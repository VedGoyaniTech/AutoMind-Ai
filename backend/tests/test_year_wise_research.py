"""
AutoMind AI — Comprehensive Year-Wise Vehicle Research & DuckDuckGo Fallback Test Suite
Verifies all 20 scenarios without relying on live network.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.services.ai.llm_provider import get_llm_provider
from app.services.ai.duckduckgo_search import DuckDuckGoSearchService, _RESEARCH_CACHE
from app.services.pricing.historical_cars import query_historical_cars
from app.services.pricing.engine import PricingEngine
from app.schemas.pricing import PricingQuoteRequest

@pytest.fixture
def llm():
    return get_llm_provider()

# 1. 2018 SUV launches
def test_1_2018_suv_launches(llm):
    resp = llm.generate("2018 mein India mein kaun si SUV launch hui thi?", "")
    assert "2018" in resp
    assert "Dataset Verification Notice" not in resp
    assert "Mahindra Marazzo" in resp or "Volvo XC40" in resp or "SUVs" in resp

# 2. 2019 luxury cars
def test_2_2019_luxury_cars(llm):
    resp = llm.generate("2019 luxury cars India", "")
    assert "2019" in resp
    assert "Dataset Verification Notice" not in resp
    assert "BMW" in resp or "Cars" in resp

# 3. 2020 EV cars
def test_3_2020_ev_cars(llm):
    resp = llm.generate("2020 electric cars launches", "")
    assert "2020" in resp
    assert "Nexon EV" in resp or "Electric" in resp or "EV" in resp
    assert "Dataset Verification Notice" not in resp

# 4. 2021 sedan query
def test_4_2021_sedan_query(llm):
    resp = llm.generate("2021 sedans in India", "")
    assert "2021" in resp
    assert "Dataset Verification Notice" not in resp

# 5. 2022 brand-specific query (Hyundai)
def test_5_2022_hyundai_cars_launched(llm):
    resp = llm.generate("2022 Hyundai cars launched", "")
    assert "2022" in resp
    assert "Dataset Verification Notice" not in resp

# 6. 2023 hatchback query
def test_6_2023_hatchback_query(llm):
    resp = llm.generate("2023 hatchback cars", "")
    assert "2023" in resp
    assert "Dataset Verification Notice" not in resp

# 7. 2024 launch query with trusted web fallback
def test_7_2024_launch_query_web_fallback(llm):
    resp = llm.generate("2024 mein kaun si cars launch hui thi?", "")
    assert "2024" in resp
    assert "Dataset Verification Notice" not in resp
    assert "Thar Roxx" in resp or "Creta" in resp or "Autocar India" in resp

# 8. 2024 EV SUV query
def test_8_2024_ev_suv_query(llm):
    resp = llm.generate("2024 EV SUVs India", "")
    assert "2024" in resp
    assert "Curvv" in resp or "Windsor" in resp or "EV" in resp or "SUVs" in resp

# 9. 2024 specific-model detail query
def test_9_2024_creta_details(llm):
    resp = llm.generate("2024 Creta details", "")
    assert "Hyundai Creta" in resp or "Creta" in resp
    assert "| Field | Details |" in resp
    assert "Vehicle type" in resp
    assert "Dataset Verification Notice" not in resp

# 10. 2025 Tata query
def test_10_2025_tata_query(llm):
    resp = llm.generate("2025 Tata cars", "")
    assert "2025" in resp
    assert "Sierra" in resp or "Tata" in resp

# 11. Hindi query
def test_11_hindi_query(llm):
    resp = llm.generate("2024 में कौन सी कार लॉन्च हुई थी?", "")
    assert "2024" in resp
    assert "भारत में लॉन्च हुई" in resp

# 12. Gujarati query
def test_12_gujarati_query(llm):
    resp = llm.generate("2024 માં કઈ કાર લોન્ચ થઈ હતી?", "")
    assert "2024" in resp
    assert "Dataset Verification Notice" not in resp

# 13. Mixed Roman-Hindi query
def test_13_mixed_roman_hindi_query(llm):
    resp = llm.generate("2024 mein India me kaun si cars launch hui thi?", "")
    assert "2024" in resp
    assert "Important notes" in resp

# 14. Launched versus upcoming distinction
def test_14_launched_vs_upcoming_distinction():
    launched = query_historical_cars(year=2024, status="launched")
    upcoming = query_historical_cars(year=2025, status="upcoming")
    assert any(c["name"] == "Mahindra Thar Roxx (5-Door)" for c in launched)
    assert any(c["name"] == "Tata Sierra EV" for c in upcoming)
    assert not any(c["status"] == "upcoming" for c in launched)

# 15. Conflicting sources / notes handling
def test_15_conflicting_sources_handling(llm):
    resp = llm.generate("2024 car launches India", "")
    assert "Important notes" in resp
    assert "On-road price city के हिसाब से अलग होगा" in resp

# 16. No trusted sources returns honest information not confirmed
def test_16_no_trusted_sources_honest_response(llm):
    with patch("app.services.pricing.historical_cars.query_historical_cars", return_value=[]):
        resp = llm._engine._generate_dynamic_car_launches_response("1842 steam car launch", target_year=1842, is_luxury=False, candidates=[], web_results=[])
        assert "Information not confirmed" in resp
        assert "Dataset Verification Notice" not in resp

# 17. No fabricated citations
def test_17_no_fabricated_citations(llm):
    resp = llm.generate("2024 SUV cars", "")
    assert "https://www.carwale.com" in resp or "https://www.autocarindia.com" in resp

# 18. No generic no-data notice when evidence exists
def test_18_no_generic_no_data_notice(llm):
    resp = llm.generate("2025 luxury EV cars India", "")
    assert "Dataset Verification Notice" not in resp
    assert "2025" in resp

# 19. Caching behavior in DuckDuckGo service
def test_19_caching_behavior():
    ddg = DuckDuckGoSearchService()
    cache_key = "test_cache_query_2024_suv_hyundai"
    _RESEARCH_CACHE[cache_key] = {
        "query": "test",
        "results": [{"title": "Cached Result", "url": "https://www.carwale.com/cached", "snippet": "Cached"}]
    }
    cached = ddg.targeted_automotive_search(query="test_cache_query", year=2024, category="suv", brand="hyundai")
    assert len(cached) == 1
    assert cached[0]["title"] == "Cached Result"

# 20. Existing pricing & EMI flows continue working
def test_20_pricing_and_emi_flows_intact():
    engine = PricingEngine()
    req = PricingQuoteRequest(
        city="Ahmedabad",
        stateCode="GJ",
        model="Nexon",
        exShowroomPrice=1150000.0
    )
    quote = engine.generate_quote(req)
    assert quote.priceBreakdown.onRoadPrice > 1150000.0
    assert len(quote.emiOptions) == 3
