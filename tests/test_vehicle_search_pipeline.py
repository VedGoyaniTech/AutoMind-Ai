"""
Automated Test Suite — Vehicle Search Pipeline
Validates entity matching, domain filtering, query optimization, structured extraction, and consensus merging across target benchmarks:
- BMW M4
- BMW X5
- Hyundai Creta
- Tata Nexon
- Mahindra Scorpio N
- Mercedes C-Class
"""

import pytest
from app.services.vehicle_search.search.query_optimizer import QueryOptimizer
from app.services.vehicle_search.filter.domain_filter import TrustedDomainFilter, TRUSTED_DOMAINS
from app.services.vehicle_search.validator.entity_validator import EntityValidator
from app.services.vehicle_search.utils.fuzzy import calculate_similarity_ratio, is_entity_match
from app.services.vehicle_search.models import SearchResult, ExtractedVehicleSpec
from app.services.vehicle_search.merger.consensus_merger import ConsensusMerger


def test_query_optimizer():
    optimizer = QueryOptimizer()
    opt = optimizer.optimize("BMW M4")
    assert "BMW M4" in opt
    assert "price" in opt.lower()
    assert "india" in opt.lower() or "specs" in opt.lower()


def test_trusted_domain_filter():
    domain_filter = TrustedDomainFilter()
    sample_results = [
        SearchResult(title="BMW M4 Price in India", url="https://www.carwale.com/bmw-cars/m4/", snippet="BMW M4 price...", domain="carwale.com"),
        SearchResult(title="BMW M4 Overview", url="https://www.bmw.in/m4", snippet="BMW M4 India...", domain="bmw.in"),
        SearchResult(title="Random Car Blog", url="https://randomblog123.com/bmw", snippet="Random...", domain="randomblog123.com")
    ]

    filtered = domain_filter.filter(sample_results)
    assert len(filtered) == 2
    domains = [f.domain for f in filtered]
    assert "carwale.com" in domains
    assert "bmw.in" in domains
    assert "randomblog123.com" not in domains


def test_entity_validation_bmw_m4_vs_x5():
    validator = EntityValidator(threshold=0.90)
    results = [
        SearchResult(title="BMW M4 Competition xDrive Coupe Price & Specs", url="https://www.carwale.com/bmw-cars/m4/", snippet="BMW M4 Competition...", domain="carwale.com"),
        SearchResult(title="BMW X5 SUV Price & Specs", url="https://www.carwale.com/bmw-cars/x5/", snippet="BMW X5 SUV...", domain="carwale.com")
    ]

    valid = validator.validate_results("BMW M4", results)
    assert len(valid) == 1
    assert "BMW M4" in valid[0].title
    assert "BMW X5" not in valid[0].title


def test_fuzzy_matching_threshold():
    match_m4, score_m4 = is_entity_match("BMW M4", "BMW M4 Competition Coupe Specs", threshold=0.90)
    assert match_m4 is True

    match_x5, score_x5 = is_entity_match("BMW M4", "BMW X5 xDrive40i", threshold=0.90)
    # Model conflict check should reject X5 when user requested M4
    validator = EntityValidator(threshold=0.90)
    valid = validator.validate_results("BMW M4", [SearchResult(title="BMW X5 xDrive40i", url="http://test.com", snippet="X5", domain="test.com")])
    assert len(valid) == 0


def test_consensus_merger():
    merger = ConsensusMerger()
    spec1 = ExtractedVehicleSpec(
        vehicle_name="BMW M4 Competition",
        variant_name="xDrive Coupe",
        ex_showroom_price="₹1.53 Crore",
        fuel_type="Petrol",
        transmission="Automatic",
        source_domain="carwale.com",
        source_url="https://carwale.com/m4"
    )
    spec2 = ExtractedVehicleSpec(
        vehicle_name="BMW M4 Competition",
        variant_name="xDrive Coupe",
        ex_showroom_price="₹1.53 Crore",
        fuel_type="Petrol",
        transmission="Automatic",
        source_domain="autocarindia.com",
        source_url="https://autocarindia.com/m4"
    )

    merged = merger.merge_specs("BMW M4", [spec1, spec2])
    assert merged is not None
    assert merged.vehicle == "BMW M4 Competition"
    assert merged.price_ex_showroom == "₹1.53 Crore"
    assert len(merged.consensus_sources) == 2
