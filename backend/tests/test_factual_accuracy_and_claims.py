"""
AutoMind AI — Comprehensive Factual Accuracy, RAG, Claim Verification & Benchmark Tests
Validates all 12 core engineering scenarios mandated in Phase 12 of the Master Engineering Prompt:
1. Speed Claim Verification (Claimed vs Measured vs Official Records)
2. Speed vs Acceleration Separation
3. Deterministic Speed Unit Conversion (mph <-> km/h)
4. Indian Import Cost Breakdown (CIF, BCD, SWS, IGST/Cess, RTO, Estimated status)
5. Indian Market Availability (Dealership CBU vs Private Import)
6. Luxury Vehicle Comparison (Multi-dimensional criteria without single numeric score)
7. Brand Clarification (Bentley brand query resolves to canonical models)
8. Citation Verification & Domain Integrity
9. Verification Status Enum Coverage
10. Multilingual Request Handling (Hindi, Hinglish, Gujarati)
11. Query Analyzer Constraint Integrity (No false negative filter constraints)
12. Context Builder Structured Citation Output
"""

import pytest
from app.services.ai.claim_validator import (
    claim_validation_service,
    ClaimType,
    VerificationStatus,
    VehicleClaim,
    ImportCostBreakdown,
    MPH_TO_KMH_FACTOR,
    KMH_TO_MPH_FACTOR
)
from app.services.ai.query_analyzer import QueryAnalyzer
from app.services.ai.context_builder import ContextBuilder
from app.services.ai.vehicle_comparison_service import comparison_service, ResolutionStatus


# ---------------------------------------------------------------------------
# Test Scenario 1: Speed Claim Verification
# ---------------------------------------------------------------------------
def test_scenario_1_speed_claim_verification():
    """Koenigsegg Jesko Absolut theoretical claim vs Bugatti Chiron 300+ vs Agera RS."""
    # Jesko Absolut must be categorized as manufacturer_claim (theoretical simulation)
    jesko_claim = claim_validation_service.verify_speed_claim("Koenigsegg Jesko Absolut", 531.0, "km/h")
    assert jesko_claim.status == VerificationStatus.MANUFACTURER_CLAIM
    assert "simulation" in jesko_claim.notes.lower() or "theoretical" in jesko_claim.notes.lower()
    assert jesko_claim.normalized_value["kmh"] == 531.0

    # Bugatti Chiron Super Sport 300+ must be categorized as independently_measured (one-way Ehra-Lessien run)
    chiron_claim = claim_validation_service.verify_speed_claim("Bugatti Chiron Super Sport 300+", 490.48, "km/h")
    assert chiron_claim.status == VerificationStatus.INDEPENDENTLY_MEASURED
    assert "one-way" in chiron_claim.notes.lower() or "tüv" in chiron_claim.notes.lower()

    # Koenigsegg Agera RS must be officially_recognized_record (two-way production record)
    agera_claim = claim_validation_service.verify_speed_claim("Koenigsegg Agera RS", 447.19, "km/h")
    assert agera_claim.status == VerificationStatus.OFFICIALLY_RECOGNIZED_RECORD
    assert "guinness" in agera_claim.notes.lower() or "two-way" in agera_claim.notes.lower()


# ---------------------------------------------------------------------------
# Test Scenario 2: Speed vs Acceleration Separation
# ---------------------------------------------------------------------------
def test_scenario_2_speed_vs_acceleration_separation():
    """Top speed (gearing/aerodynamics) and 0-100 sprint (traction/torque) must never be merged."""
    table_text = claim_validation_service.generate_speed_ranking_table()
    assert "Top Speed vs Acceleration" in table_text
    assert "never combined" in table_text.lower() or "different engineering metrics" in table_text.lower()
    assert "0–100" in table_text or "0-100" in table_text


# ---------------------------------------------------------------------------
# Test Scenario 3: Deterministic Speed Unit Conversion
# ---------------------------------------------------------------------------
def test_scenario_3_deterministic_speed_unit_conversion():
    """Unit conversions must use exact 1.609344 factor without precision loss."""
    # 300 mph -> 482.80 km/h
    kmh_val = claim_validation_service.convert_speed(300.0, "mph", "km/h")
    assert kmh_val == round(300.0 * MPH_TO_KMH_FACTOR, 2)
    assert kmh_val == 482.8

    # 490.48 km/h -> 304.77 mph
    mph_val = claim_validation_service.convert_speed(490.48, "km/h", "mph")
    assert mph_val == round(490.48 * KMH_TO_MPH_FACTOR, 2)
    assert mph_val == 304.77

    # Same unit conversion
    assert claim_validation_service.convert_speed(250.0, "km/h", "km/h") == 250.0


# ---------------------------------------------------------------------------
# Test Scenario 4: Indian Import Cost Breakdown
# ---------------------------------------------------------------------------
def test_scenario_4_indian_cbu_import_cost_breakdown():
    """CBU import calculation must include CIF, BCD 100%, SWS 10%, IGST/cess ~50%, and RTO."""
    cif_usd = 200000.0  # $200k car
    breakdown = claim_validation_service.calculate_indian_cbu_import_cost(
        cif_usd=cif_usd,
        engine_cc=4000,
        fuel_type="petrol"
    )

    expected_cif_inr = 200000.0 * 84.0  # ₹1,68,00,000 (1.68 Cr)
    assert breakdown.cif_inr == expected_cif_inr
    assert breakdown.bcd_rate == 1.00  # 100% duty for >= $40k
    assert breakdown.bcd_amount_inr == expected_cif_inr
    assert breakdown.sws_rate == 0.10  # 10% on BCD
    assert breakdown.sws_amount_inr == expected_cif_inr * 0.10

    # IGST + Cess ~50% assessed on CIF + BCD + SWS
    duty_paid_val = expected_cif_inr + breakdown.bcd_amount_inr + breakdown.sws_amount_inr
    assert breakdown.igst_cess_amount_inr == duty_paid_val * 0.50

    # Total customs duty alone is 2.15x CIF (BCD 1.0 + SWS 0.1 + IGST/Cess 1.05)
    duty_multiplier = breakdown.total_customs_duty_inr / expected_cif_inr
    assert 2.10 <= duty_multiplier <= 2.20

    # Total landed cost before RTO is CIF + Customs = ~3.15x CIF
    multiplier = breakdown.landed_cost_pre_rto_inr / expected_cif_inr
    assert 3.10 <= multiplier <= 3.25
    assert breakdown.status == VerificationStatus.ESTIMATED
    assert breakdown.is_official_dealer_price is False


# ---------------------------------------------------------------------------
# Test Scenario 5: Indian Market Availability
# ---------------------------------------------------------------------------
def test_scenario_5_indian_market_availability():
    """Distinguish official dealership network from private import."""
    # Bentley has official dealerships in India
    bentley_avail = claim_validation_service.check_indian_availability("Bentley Continental GT")
    assert bentley_avail["matched"] is True
    assert "Official Dealership" in bentley_avail["availability"]
    assert "Mumbai" in bentley_avail["dealers"] or "Delhi" in bentley_avail["dealers"]

    # Koenigsegg requires private import
    jesko_avail = claim_validation_service.check_indian_availability("Koenigsegg Jesko")
    assert "Private Import" in jesko_avail["availability"]


# ---------------------------------------------------------------------------
# Test Scenario 6: Luxury Vehicle Comparison
# ---------------------------------------------------------------------------
def test_scenario_6_luxury_vehicle_comparison():
    """Luxury vehicle comparisons must present multi-dimensional criteria without single numeric score."""
    result = comparison_service.process_comparison("Bentley Continental GT vs Rolls-Royce Ghost")
    assert result.intent_detected is True
    assert result.clarification_status == "ready"
    assert "Head-to-Head Comparison" in result.response_markdown
    assert "Bentley Continental GT" in result.response_markdown
    assert "Rolls-Royce Ghost" in result.response_markdown

    # Must NOT have arbitrary score like "Bentley: 9.8/10, Rolls-Royce: 9.6/10"
    assert "9.8/10" not in result.response_markdown
    assert "Score: " not in result.response_markdown
    assert "Verified Buyer Selection Verdict" in result.response_markdown


# ---------------------------------------------------------------------------
# Test Scenario 7: Brand Clarification
# ---------------------------------------------------------------------------
def test_scenario_7_brand_clarification():
    """Brand-only queries (e.g. Bentley vs Rolls-Royce) require exact model selection."""
    result = comparison_service.process_comparison("Bentley vs Rolls-Royce")
    assert result.intent_detected is True
    assert result.clarification_status == "clarification_needed"
    assert "Model Clarification Required" in result.response_markdown
    assert "Bentley Continental GT" in result.response_markdown
    assert "Rolls-Royce Ghost" in result.response_markdown


# ---------------------------------------------------------------------------
# Test Scenario 8: Citation Verification & Domain Integrity
# ---------------------------------------------------------------------------
def test_scenario_8_citation_verification_and_domains():
    """Citations must use real publishers and URLs, never internal mock IDs."""
    chiron = claim_validation_service.verify_speed_claim("Bugatti Chiron Super Sport 300+", 490.48)
    assert chiron.source_url is not None
    assert chiron.source_url.startswith("https://")
    assert "bugatti.com" in chiron.source_url
    assert chiron.source_publisher is not None


# ---------------------------------------------------------------------------
# Test Scenario 9: Verification Status Enum Coverage
# ---------------------------------------------------------------------------
def test_scenario_9_verification_status_enums():
    """Verify all 6 standardized verification statuses are present and accessible."""
    statuses = {
        VerificationStatus.MANUFACTURER_CLAIM.value,
        VerificationStatus.INDEPENDENTLY_MEASURED.value,
        VerificationStatus.OFFICIALLY_RECOGNIZED_RECORD.value,
        VerificationStatus.ESTIMATED.value,
        VerificationStatus.UNVERIFIED.value,
        VerificationStatus.UNAVAILABLE.value
    }
    assert len(statuses) == 6
    assert "manufacturer_claim" in statuses
    assert "independently_measured" in statuses
    assert "officially_recognized_record" in statuses
    assert "estimated" in statuses
    assert "unverified" in statuses
    assert "unavailable" in statuses


# ---------------------------------------------------------------------------
# Test Scenario 10: Multilingual Request Handling
# ---------------------------------------------------------------------------
def test_scenario_10_multilingual_request_handling():
    """Gujarati and Hindi inputs should be analyzed cleanly."""
    qa = QueryAnalyzer()

    # Gujarati query: "મને બેન્ટલી કારની માહિતી આપો"
    guj_res = qa.analyze("મને બેન્ટલી કારની માહિતી આપો")
    assert guj_res["parsed_constraints"]["manufacturer"] == "Bentley"
    assert guj_res["is_luxury"] is True

    # Hindi query: "टाटा नेक्सन 15 लाख के अंदर"
    hi_res = qa.analyze("टाटा नेक्सन 15 लाख के अंदर")
    assert hi_res["parsed_constraints"]["manufacturer"] == "Tata"
    assert hi_res["parsed_constraints"]["price_max"] == 1500000.0


# ---------------------------------------------------------------------------
# Test Scenario 11: Query Analyzer Constraint Integrity
# ---------------------------------------------------------------------------
def test_scenario_11_query_analyzer_constraint_integrity():
    """Luxury brand queries should not emit false negative filter constraints."""
    qa = QueryAnalyzer()
    res = qa.analyze("bently car ki details")
    assert res["parsed_constraints"]["manufacturer"] == "Bentley"
    assert res["is_luxury"] is True
    # Should not have is_luxury: False in constraints
    assert res["parsed_constraints"]["is_luxury"] is not False


# ---------------------------------------------------------------------------
# Test Scenario 12: Context Builder Structured Output
# ---------------------------------------------------------------------------
def test_scenario_12_context_builder_structured_output():
    """ContextBuilder must format structured [SRC-N] citations and clean user constraints."""
    cb = ContextBuilder()
    mock_knowledge = [
        {
            "title": "Bentley Continental GT Engineering Overview",
            "text": "The Continental GT features a 4.0L twin-turbo V8 engine with all-wheel drive.",
            "source_name": "Bentley Media Global",
            "source_url": "https://www.bentleymedia.com/en/models/continental-gt",
            "source_type": "manufacturer"
        }
    ]
    mock_constraints = {
        "manufacturer": "Bentley",
        "price_max": 60000000.0,
        "is_luxury": True,
        "launch_status": "any",
        "market": "India"
    }

    ctx = cb.build_context(
        docs=mock_knowledge,
        parsed_constraints=mock_constraints
    )

    # Check for [SRC-1] citation formatting
    assert "[SRC-1]" in ctx
    assert "Bentley Continental GT Engineering Overview" in ctx
    assert "Publisher: Bentley Media Global" in ctx
    assert "URL: https://www.bentleymedia.com" in ctx

    # Check for clean USER SEARCH FILTERS without internal defaults
    assert "USER SEARCH FILTERS:" in ctx
    assert "Brand: Bentley" in ctx
    assert "Maximum Budget: ₹600.00 Lakh" in ctx
    assert "launch_status: any" not in ctx
    assert "market: India" not in ctx


# ---------------------------------------------------------------------------
# Test Scenario 13: 7-Gate Quality Control Review
# ---------------------------------------------------------------------------
def test_scenario_13_seven_gate_quality_control_review():
    """Validates the 7-Gate Answer Review engine: Gate A (Relevance) through Gate G (Consistency)."""
    # 1. Valid compliant response
    good_query = "What is the top speed of Koenigsegg Jesko Absolut vs Bugatti Chiron Super Sport 300+?"
    good_response = (
        "## Top Speed Comparison\n\n"
        "1. **Koenigsegg Jesko Absolut**: 531 km/h (330 mph) - `Manufacturer Claim` (CFD computer simulation projection).\n"
        "2. **Bugatti Chiron Super Sport 300+**: 490.48 km/h (304.77 mph) - `Independently Measured` (One-way certified by TÜV Rheinland).\n\n"
        "Sources:\n"
        "- [SRC-1] Bugatti Official Press Release: https://www.bugatti.com/news\n"
        "- [SRC-2] Koenigsegg Media: https://www.koenigsegg.com/model/jesko-absolut"
    )
    result = claim_validation_service.review_answer_gates(good_query, good_response)
    assert result["passed"] is True
    assert result["score"] == 1.0
    assert result["gates"]["gate_a_relevance"]["passed"] is True
    assert result["gates"]["gate_b_accuracy"]["passed"] is True
    assert result["gates"]["gate_d_sources"]["passed"] is True
    assert result["gates"]["gate_f_completeness"]["passed"] is True
    assert result["gates"]["gate_g_consistency"]["passed"] is True

    # 2. Non-compliant response with unverified simulation presented as physical record
    bad_response = (
        "The fastest car in the world is the Koenigsegg Jesko Absolut reaching 531 km/h in physical testing."
    )
    bad_result = claim_validation_service.review_answer_gates("fastest car", bad_response)
    assert bad_result["passed"] is False
    assert bad_result["gates"]["gate_b_accuracy"]["passed"] is False
    assert "Gate B" in bad_result["violations"][0]

    # 3. Non-compliant response with fake mock URL
    fake_url_response = (
        "The Bentley Continental GT is powered by a 4.0L V8 twin-turbo engine. "
        "Source: [Mock Data](mock://internal_car_id_88291)"
    )
    mock_result = claim_validation_service.review_answer_gates("Bentley Continental GT", fake_url_response)
    assert mock_result["passed"] is False
    assert mock_result["gates"]["gate_d_sources"]["passed"] is False
    assert "Gate D" in mock_result["violations"][0]

    # 4. Non-compliant response with arbitrary single-winner numeric score in luxury comparison
    arbitrary_score_response = (
        "Comparing Bentley Continental GT vs Rolls-Royce Ghost. "
        "The Bentley Continental GT is sporty, while Rolls-Royce Ghost is plush. "
        "Score: Bentley Continental GT 9.8/10, Rolls-Royce Ghost 9.6/10. Bentley wins."
    )
    score_result = claim_validation_service.review_answer_gates("Bentley vs Rolls-Royce", arbitrary_score_response)
    assert score_result["passed"] is False
    assert score_result["gates"]["gate_g_consistency"]["passed"] is False
    assert "Gate G" in score_result["violations"][0]

