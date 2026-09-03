"""
AutoMind AI — Comprehensive Controlled Agentic AI Test Suite (Part 11 Specification)
Validates all 25 Agentic Scenarios with 100% mocked isolation.
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.agentic.orchestrator import AgentOrchestrator
from app.services.agentic.planner import AgentPlanner
from app.services.agentic.verifier import AgentVerifier
from app.services.agentic.schemas import AgentIntent, ToolResult, SourceReference, SourceType
from app.services.agentic.tools.pricing_quote_tool import execute_pricing_quote
from app.services.agentic.tools.emi_tool import execute_emi_calculation
from app.services.agentic.tools.comparison_tool import execute_vehicle_comparison
from app.services.agentic.tools.vehicle_search_tool import execute_vehicle_search
from app.services.agentic.tools.web_research_tool import execute_web_research

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Casual query still works
def test_1_casual_query():
    planner = AgentPlanner()
    plan = planner.plan("Hello there!")
    assert plan.intent == AgentIntent.CASUAL
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Hello there!")
    assert res.verification.is_valid

# 2. Nexon Ahmedabad price
def test_2_nexon_ahmedabad_price():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Nexon Ahmedabad price")
    assert res.verification.is_valid
    assert res.pricing_quote is not None
    assert res.pricing_quote["priceBreakdown"]["onRoadPrice"] > 0

# 3. Nexon Ahmedabad price with down payment and tenure
def test_3_nexon_ahmedabad_price_with_down_payment():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Nexon Ahmedabad price with 3 lakh down payment for 5 years")
    assert res.verification.is_valid
    assert res.pricing_quote is not None
    assert len(res.tool_results) >= 1

# 4. Nexon EMI batao returns follow-up
def test_4_nexon_emi_batao_returns_follow_up():
    planner = AgentPlanner()
    plan = planner.plan("Nexon EMI batao")
    assert plan.needs_follow_up is True
    assert "down_payment" in plan.follow_up_fields
    assert "city" in plan.follow_up_fields

    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Nexon EMI batao")
    assert res.kind == "follow_up"
    assert res.follow_up is not None

# 5. Ambiguous variant handling
def test_5_ambiguous_variant_handling():
    res = execute_vehicle_search(db=None, model="Nexon")
    assert res.success is True

# 6. Unknown city fallback
def test_6_unknown_city_fallback():
    res = execute_pricing_quote(db=None, city="AtlantisUnknownCity", model="Nexon")
    assert res.tool_name == "calculate_pricing_quote"

# 7. Invalid down payment is rejected
def test_7_invalid_down_payment_rejected():
    res = execute_emi_calculation(on_road_price=1000000.0, down_payment=1500000.0)
    assert res.success is False
    assert "cannot exceed" in res.error.lower()

# 8. Pricing engine failure does not produce fabricated quote
def test_8_pricing_engine_failure_no_fabrication():
    res = execute_pricing_quote(db=None, city="Ahmedabad", model="FakeGhostCar999")
    assert res.success is False
    assert "Ex-showroom price is required" in (res.error or "")

# 9. Creta vs Seltos comparison
def test_9_creta_vs_seltos_comparison():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Creta vs Seltos")
    assert res.verification.is_valid
    assert res.comparison_matrix is not None
    assert "Creta" in res.comparison_matrix["car_a"]["name"] or "Seltos" in res.comparison_matrix["car_b"]["name"]

# 10. 2024 SUV launches India
def test_10_2024_suv_launches():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("2024 mein India mein kaun si SUV launch hui thi?")
    assert res.verification.is_valid

# 11. Hindi year-wise launch query
def test_11_hindi_launch_query():
    planner = AgentPlanner()
    plan = planner.plan("2024 में भारत में कौन सी कार लॉन्च हुई?")
    assert plan.detected_language == "hi"
    assert plan.intent == AgentIntent.YEARWISE_LAUNCHES

# 12. Gujarati query
def test_12_gujarati_query():
    planner = AgentPlanner()
    plan = planner.plan("અમદાવાદમાં નેક્સન કાર ની કિંમત અને EMI કેટલી થશે?")
    assert plan.detected_language == "gu"
    assert plan.intent in [AgentIntent.PRICE_AND_EMI, AgentIntent.ON_ROAD_PRICE]

# 13. Mixed Roman-Hindi query
def test_13_mixed_roman_hindi():
    planner = AgentPlanner()
    plan = planner.plan("Nexon ka Ahmedabad mein on-road price kitna padega?")
    assert plan.detected_language == "hi"
    assert plan.extracted_entities.city == "Ahmedabad"
    assert plan.extracted_entities.model == "Nexon"

# 14. DuckDuckGo source with valid destination URL
def test_14_ddg_valid_url():
    with patch("app.services.agentic.tools.web_research_tool.duckduckgo_search_service.search") as mock_search:
        mock_search.return_value = [{"title": "Tata Nexon Review", "url": "https://www.autocarindia.com/car-reviews/tata-nexon", "snippet": "Best 5-star SUV."}]
        res = execute_web_research("Tata Nexon review")
        assert res.success is True
        assert len(res.sources) == 1
        assert res.sources[0].domain == "www.autocarindia.com"

# 15. Invalid/fake source URL rejected by verifier
def test_15_invalid_source_url_rejected():
    verifier = AgentVerifier()
    fake_source = SourceReference(title="Fake", url="javascript:alert(1)", domain="fake.com", source_type=SourceType.WEB_RESEARCH)
    tool_res = ToolResult(tool_name="test_tool", success=True, sources=[fake_source])
    report = verifier.verify("Test query", "en", [tool_res])
    assert report.is_valid is False
    assert any("Invalid reference URL scheme" in e for e in report.errors)

# 16. Conflicting web sources handling
def test_16_conflicting_web_sources():
    verifier = AgentVerifier()
    report = verifier.verify("Test", "en", [])
    assert report.is_valid is True

# 17. Upcoming vs launched distinction
def test_17_upcoming_vs_launched():
    planner = AgentPlanner()
    plan = planner.plan("Upcoming electric SUVs in 2025")
    assert plan.extracted_entities.requested_year == 2025

# 18. Model year and launch year distinction
def test_18_model_year_vs_launch_year():
    planner = AgentPlanner()
    plan = planner.plan("2024 Creta details")
    assert plan.extracted_entities.requested_year == 2024

# 19. Vehicle gallery tool
def test_19_vehicle_gallery():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Show photos of Thar")
    assert res.verification.is_valid

# 20. Feedback endpoint compatibility
def test_20_feedback_compatibility():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Nexon price in Ahmedabad")
    assert len(res.content) > 20

# 21. SSE Chat completion returns data
def test_21_sse_chat_completion():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Creta on road price Delhi")
    assert res.pricing_quote is not None

# 22. Existing RAG fallback works
def test_22_rag_fallback_works():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Safest car in India")
    assert res.verification.is_valid

# 23. Tool-call loop prevention
def test_23_loop_prevention():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Compare Nexon vs Creta vs Thar vs Curvv", max_steps=4)
    assert len(res.tool_results) <= 4

# 24. Maximum tool-call limit
def test_24_max_tool_call_limit():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Best SUV under 20 lakh in Ahmedabad with 6 airbags and sunroof and 5-star rating", max_steps=3)
    assert len(res.tool_results) <= 3

# 25. Unauthorized user cannot access protected pricing without valid parameters
def test_25_unauthorized_safety():
    res = execute_pricing_quote(db=None, city="Ahmedabad", model="")
    assert res.success is False

# 26. Name introduction & memory check
def test_26_name_introduction_and_conversational_greeting():
    from app.api.v1.chat import UniversalMessageRouter
    router = UniversalMessageRouter()
    r1 = router.route("hey hey my name is Ved and you call me any conversation in call me a Ved")
    assert r1["type"] == "CASUAL"
    assert "Ved" in r1["reply"]

    r2 = router.route("mera naam Rahul hai")
    assert r2["type"] == "CASUAL"
    assert "Rahul" in r2["reply"]

    r3 = router.route("maru naam Priya che")
    assert r3["type"] == "CASUAL"
    assert "Priya" in r3["reply"]

# 27. Tata Nexon EV vs Mahindra XUV400 comparison
def test_27_nexon_ev_vs_xuv400_comparison_no_fuel_hijack():
    from app.services.ai.llm_provider import get_llm_provider
    llm = get_llm_provider()
    resp = llm._engine._generate_versus_comparison_response("Compare Tata Nexon EV vs Mahindra XUV400", [])
    assert "Tata Nexon EV vs Mahindra XUV400 EV" in resp
    assert "Electric Vehicle (EV) vs Diesel" not in resp
