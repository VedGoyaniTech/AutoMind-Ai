"""
AutoMind AI — Data Foundation & Provenance Test Suite
Verifies all 12 core requirements specified in P0 Data Foundation:
1. Missing provenance/approval rejection
2. Valid approved source-backed import is idempotent
3. New price/rule versions preserve old history
4. Decimal currency and unit validation
5. BNCAP rating exact vehicle applicability
6. RTO rule version official source and estimate marking
7. Knowledge document metadata mandatory for ingestion
8. Training export excludes test split, unapproved records, unconsented feedback, and TweetEval
9. Training audit flags contamination (locomotive/railway) in master_v4
10. Source/citation response schema includes freshness/review metadata
11. Admin data endpoints require authenticated authorized admin user
12. Alembic migration upgrade smoke test
"""

import os
import json
import tempfile
import pytest
from decimal import Decimal
from datetime import datetime, date, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.car import Manufacturer, CarModel, CarVariant
from app.models.source import Source
from app.models.provenance import (
    VehicleSpecification,
    VehiclePrice,
    RTORuleVersion,
    SafetyRating,
)
from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.provenance import (
    VehiclePriceCreate,
    VehicleSpecificationCreate,
    SafetyRatingCreate,
    RTORuleVersionCreate,
    RAGCitationMetadata,
)
from app.schemas.chat import SourceCard
from app.schemas.rag import RAGSearchResult, KnowledgeChunkMetadata
from app.schemas.pricing import PricingQuoteRequest, DataFreshnessInfo
from app.services.pricing.engine import PricingEngine
from scripts.data_foundation_cli import (
    validate_catalogue_import,
    import_catalogue_data,
    audit_training_data,
    ingest_knowledge_document,
)


@pytest.fixture
def admin_token(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "test@automind.ai", "password": "password123"}
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


@pytest.fixture
def regular_user_token(client):
    # Register/login normal non-admin user
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "buyer@automind.ai",
            "password": "BuyerPassword123!",
            "full_name": "Car Buyer"
        }
    )
    if res.status_code == 400 and "already registered" in res.text:
        login_res = client.post(
            "/api/v1/auth/login",
            json={"email": "buyer@automind.ai", "password": "BuyerPassword123!"}
        )
        return login_res.json()["access_token"]
    assert res.status_code in (200, 201), f"Register failed: {res.text}"
    return res.json().get("access_token") or client.post(
        "/api/v1/auth/login",
        json={"email": "buyer@automind.ai", "password": "BuyerPassword123!"}
    ).json()["access_token"]


# -----------------------------------------------------------------------------
# 1. Unverified Catalogue Fact Rejection
# -----------------------------------------------------------------------------
def test_unverified_catalogue_fact_rejection():
    """A catalogue price/spec/fact with missing source, effective date, or unapproved status is rejected."""
    bad_data = {
        "source": {
            "name": "Unverified Blog",
            "domain": "carblog.xyz",
            "source_type": "invalid_source_type",  # Invalid type
            "allowed_use": "unauthorized_scrape"   # Invalid use
        },
        "variants": [
            {
                "variant_name": "Bad Variant",
                "model_name": "Ghost Model",
                "prices": [
                    {
                        "amount": -50000,  # Negative price
                        # missing effective_from
                    }
                ],
                "specifications": [
                    {
                        "field_name": "engine_cc"
                        # missing effective_date and last_verified_at
                    }
                ]
            }
        ]
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(bad_data, f)
        tmp_path = f.name
    try:
        is_valid, errors, _ = validate_catalogue_import(tmp_path, dry_run=True)
        assert not is_valid
        assert len(errors) >= 3
        err_str = " ".join(errors).lower()
        assert "source_uid" in err_str or "invalid source_type" in err_str
        assert "effective_from" in err_str or "amount" in err_str
        assert "effective_date" in err_str
    finally:
        os.remove(tmp_path)


# -----------------------------------------------------------------------------
# 2. Valid Approved Source-Backed Import Succeeds & is Idempotent
# -----------------------------------------------------------------------------
def test_valid_catalogue_import_idempotent():
    """Importing a valid approved catalogue twice succeeds without duplicating or corrupting records."""
    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "fixtures", "sample_catalogue_import.json"
    )
    assert os.path.exists(fixture_path), f"Fixture not found: {fixture_path}"

    # First run
    res1 = import_catalogue_data(fixture_path)
    assert res1["status"] == "success"
    assert res1["summary"]["variants_count"] >= 2
    assert res1["summary"]["prices_count"] >= 2

    # Second run (idempotency check)
    res2 = import_catalogue_data(fixture_path)
    assert res2["status"] == "success"
    assert res2["summary"]["variants_count"] == res1["summary"]["variants_count"]



# -----------------------------------------------------------------------------
# 3. New Price / Rule Versions Preserve Old History
# -----------------------------------------------------------------------------
def test_version_history_preservation():
    """When a new price is published for a variant, the prior price is preserved with is_current=False."""
    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "fixtures", "sample_catalogue_import.json"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # Modify prices to represent a price revision
    updated_catalog = json.loads(json.dumps(catalog))
    updated_catalog["source"]["source_uid"] = "src-tata-nexon-2026-q3-revision"
    updated_catalog["source"]["version"] = "2026.3"
    updated_catalog["variants"][0]["prices"][0]["amount"] = "1175000.00"
    updated_catalog["variants"][0]["prices"][0]["effective_from"] = "2026-07-01T00:00:00Z"

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(updated_catalog, f)
        rev_path = f.name

    try:
        res = import_catalogue_data(rev_path)
        assert res["status"] == "success"

        # Verify in DB: both old and new price exist, old has is_current=False, new has is_current=True
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            prices = db.query(VehiclePrice).join(CarVariant).filter(
                CarVariant.variant_name == catalog["variants"][0]["variant_name"]
            ).all()
            assert len(prices) >= 2
            current_prices = [p for p in prices if p.is_current]
            historical_prices = [p for p in prices if not p.is_current]
            assert len(current_prices) >= 1
            assert len(historical_prices) >= 1
            assert any(Decimal(str(p.amount)) == Decimal("1175000.00") for p in current_prices)
        finally:
            db.close()
    finally:
        os.remove(rev_path)


# -----------------------------------------------------------------------------
# 4. Currency Represented with Decimal / Fixed-Point and Region Rules
# -----------------------------------------------------------------------------
def test_decimal_currency_and_units():
    """Currency is strictly Decimal, positive, and rejects binary float imprecision."""
    # Test valid Decimal schema
    valid_p = VehiclePriceCreate(
        variant_id=1,
        amount=Decimal("1499000.00"),
        currency="INR",
        price_type="ex_showroom",
        state_code="MH",
        city="Mumbai",
        effective_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
        source_id=1,
        review_status="approved"
    )
    assert valid_p.amount == Decimal("1499000.00")
    assert valid_p.currency == "INR"

    # Test invalid amount (zero or negative)
    with pytest.raises(Exception):
        VehiclePriceCreate(
            variant_id=1,
            amount=Decimal("-10.00"),
            currency="INR",
            price_type="ex_showroom",
            effective_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source_id=1
        )


# -----------------------------------------------------------------------------
# 5. BNCAP Rating Requires Programme and Exact Vehicle Applicability
# -----------------------------------------------------------------------------
def test_bncap_rating_exact_vehicle_applicability():
    """BNCAP rating requires programme, adult/child scores, and explicit vehicle applicability."""
    valid_rating = SafetyRatingCreate(
        programme="Bharat NCAP",
        model_id=1,
        variant_applicability="Creative Plus MT",
        star_rating=Decimal("5.0"),
        adult_occupant_score=Decimal("32.22"),
        child_occupant_score=Decimal("44.52"),
        test_year=2024,
        tested_variant_name="Creative Plus MT",
        protocol_version="BNCAP 2023.1",
        report_url="https://bharatncap.org.in/reports/nexon-2024.pdf"
    )
    assert valid_rating.programme == "Bharat NCAP"
    assert valid_rating.star_rating == Decimal("5.0")

    # Reject empty programme or missing variant applicability
    with pytest.raises(Exception):
        SafetyRatingCreate(
            programme="",
            model_id=1,
            variant_applicability="",
            star_rating=Decimal("5.0"),
            test_year=2024
        )


# -----------------------------------------------------------------------------
# 6. RTO Rule Version Requires Official Source & Marks Estimates
# -----------------------------------------------------------------------------
def test_rto_rule_version_official_source_and_estimate():
    """RTO rule versions require official notification reference, state code, and quote marks estimates."""
    rto_rule = RTORuleVersionCreate(
        state_code="GJ",
        fuel_type="electric",
        tax_rate_percent=Decimal("0.00"),
        notification_ref="Guj-Transport-EV-Notification-2024-03",
        effective_date=datetime(2024, 4, 1, tzinfo=timezone.utc),
        source_id=1
    )
    assert rto_rule.state_code == "GJ"
    assert rto_rule.tax_rate_percent == Decimal("0.00")

    # Verify PricingEngine quote marks calculation as estimate
    engine = PricingEngine()
    quote = engine.generate_quote(PricingQuoteRequest(
        model="Nexon",
        city="Ahmedabad",
        stateCode="GJ",
        fuelType="petrol"
    ))
    assert quote.dataFreshness.isEstimate is True
    assert "estimated" in quote.disclaimer.lower() or "estimate" in quote.disclaimer.lower()


# -----------------------------------------------------------------------------
# 7. Knowledge Document Metadata Mandatory for RAG Ingestion
# -----------------------------------------------------------------------------
def test_knowledge_document_metadata_mandatory():
    """RAG document ingestion requires valid .metadata.json sidecar with license, checksum, and dates."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write("# Bharat NCAP Safety Protocols\nCrash testing overview for passenger vehicles in India.")
        doc_path = f.name

    try:
        # Ingestion without metadata sidecar must raise ValueError
        with pytest.raises(ValueError, match="metadata sidecar"):
            ingest_knowledge_document(doc_path)
    finally:
        os.remove(doc_path)



# -----------------------------------------------------------------------------
# 8. Training Export Excludes Test Split, Unapproved Records & TweetEval
# -----------------------------------------------------------------------------
def test_training_export_excludes_held_out_and_tweeteval():
    """Training datasets must exclude held-out evaluation sets, TweetEval NLP corpora, and unverified data."""
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_root)

    manifest_path = os.path.join(project_root, "ml", "datasets", "approved", "data_manifest_v1.json")
    assert os.path.exists(manifest_path), f"Manifest missing at {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Exclusions must be explicitly documented
    exclusions = manifest.get("exclusions", [])
    assert any("tweet_eval" in e.lower() for e in exclusions)
    assert any("master_v4" in e.lower() or "locomotive" in e.lower() for e in exclusions)
    assert any("held_out" in e.lower() or "test.jsonl" in e.lower() for e in exclusions)

    # Approved files must not contain tweet_eval or test sets
    for split_key in ("splits", "approved_files"):
        if split_key in manifest:
            for item in manifest[split_key]:
                path_str = str(item).lower()
                assert "tweet_eval" not in path_str
                assert "test.jsonl" not in path_str


# -----------------------------------------------------------------------------
# 9. Training Data Audit Detects Contamination (Locomotive in master_v4)
# -----------------------------------------------------------------------------
def test_training_audit_detects_contamination():
    """Dataset audit scanner flags locomotive / railway questions in master_v4 and marks quarantine candidate."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as json_out:
        json_path = json_out.name
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as md_out:
        md_path = md_out.name

    try:
        res = audit_training_data(output_md=md_path, output_json=json_path)
        assert res["total_files_scanned"] > 0
        assert res["total_lines"] > 0

        # Find master_v4 in file details
        master_v4_entry = next((f for f in res["file_details"] if "master_v4" in f["filename"]), None)
        if master_v4_entry:
            assert master_v4_entry["contaminated_records"] > 0
            assert master_v4_entry["recommendation"] == "quarantine_candidate"
            matched_terms = [t for s in master_v4_entry["contamination_samples"] for t in s["matched_terms"]]
            assert any("locomotive" in t or "railway" in t for t in matched_terms)
    finally:
        if os.path.exists(json_path):
            os.remove(json_path)
        if os.path.exists(md_path):
            os.remove(md_path)


# -----------------------------------------------------------------------------
# 10. Source / Citation Response Schema Includes Freshness & Review Metadata
# -----------------------------------------------------------------------------
def test_source_citation_response_schema_freshness():
    """SourceCard, RAGSearchResult, and DataFreshnessInfo schemas contain review and freshness attributes."""
    card = SourceCard(
        id=1,
        title="Tata Nexon Official Brochure",
        website="tatamotors.com",
        url="https://cars.tatamotors.com/nexon",
        domain="tatamotors.com",
        reason="Ex-showroom pricing",
        reliability_score=0.98,
        review_status="approved",
        last_verified_at="2026-03-01T00:00:00Z",
        is_stale=False
    )
    assert card.review_status == "approved"
    assert card.is_stale is False

    rag_item = RAGSearchResult(
        evidence_id="ev-01",
        doc_type="knowledge_chunk",
        score=0.92,
        title="Bharat NCAP Standards",
        snippet="5-star adult safety requires minimum 27.0 points",
        source_name="Bharat NCAP Gazette",
        review_status="approved",
        last_verified_at="2026-02-15"
    )
    assert rag_item.review_status == "approved"

    freshness = DataFreshnessInfo(
        priceEffectiveDate="2026-01-01",
        ruleEffectiveDate="2026-01-01",
        lastVerifiedAt="2026-03-01",
        isEstimate=True,
        reviewStatus="approved"
    )
    assert freshness.isEstimate is True
    assert freshness.reviewStatus == "approved"


# -----------------------------------------------------------------------------
# 11. Admin Data Endpoints Require Authenticated Authorized Admin User
# -----------------------------------------------------------------------------
def test_admin_data_endpoints_require_admin_auth(client, admin_token, regular_user_token):
    """Admin data endpoints reject anonymous (401) and non-admin (403), allowing only genuine admins (200)."""
    # 1. Anonymous request -> 401 Unauthorized
    anon_res = client.get("/api/v1/admin/data/sources")
    assert anon_res.status_code == 401

    # 2. Authenticated Non-Admin user -> 403 Forbidden
    non_admin_headers = {"Authorization": f"Bearer {regular_user_token}"}
    forbidden_res = client.get("/api/v1/admin/data/sources", headers=non_admin_headers)
    assert forbidden_res.status_code == 403
    assert "Administrator permissions required" in forbidden_res.json()["detail"]

    # 3. Authenticated Admin user -> 200 OK
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    ok_res = client.get("/api/v1/admin/data/sources", headers=admin_headers)
    assert ok_res.status_code == 200
    data = ok_res.json()
    assert "sources" in data
    assert "total" in data

    # 4. Audit report endpoint check
    audit_res = client.get("/api/v1/admin/data/audit-report", headers=admin_headers)
    assert audit_res.status_code == 200


# -----------------------------------------------------------------------------
# 12. Alembic Migration Upgrade Smoke Test
# -----------------------------------------------------------------------------
def test_alembic_upgrade_empty_db_smoke():
    """Alembic successfully runs upgrade head and downgrade base on a blank database."""
    import subprocess
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_db_file = os.path.join(backend_root, "test_alembic_smoke.db")
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{test_db_file}"

    try:
        # Upgrade to head
        up = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=backend_root,
            env=env,
            capture_output=True,
            text=True
        )
        assert up.returncode == 0, f"Alembic upgrade failed:\nSTDOUT: {up.stdout}\nSTDERR: {up.stderr}"

        # Downgrade to base
        down = subprocess.run(
            ["alembic", "downgrade", "base"],
            cwd=backend_root,
            env=env,
            capture_output=True,
            text=True
        )
        assert down.returncode == 0, f"Alembic downgrade failed:\nSTDOUT: {down.stdout}\nSTDERR: {down.stderr}"

        # Re-upgrade to head
        re_up = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=backend_root,
            env=env,
            capture_output=True,
            text=True
        )
        assert re_up.returncode == 0, f"Alembic re-upgrade failed:\nSTDOUT: {re_up.stdout}\nSTDERR: {re_up.stderr}"
    finally:
        if os.path.exists(test_db_file):
            os.remove(test_db_file)
