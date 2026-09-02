"""
AutoMind AI — Comprehensive Controlled Agentic AI Test Suite
Verifies all 10 Phase 5.5 Agentic Scenarios:
1. "Best EV under ₹15 lakh in Ahmedabad, EMI under ₹20,000"
2. "Nexon vs Creta in Mumbai with 20% down payment"
3. Unknown city fallback
4. Unknown variant fallback
5. Missing ex-showroom price handling
6. Hindi conversational request
7. Gujarati conversational request
8. Tool failure isolation
9. Conflicting vehicle search handling
10. Loop-prevention and step limit adherence
"""

import pytest
from app.services.agentic.orchestrator import AgentOrchestrator
from app.services.agentic.planner import AgentPlanner
from app.services.agentic.verifier import AgentVerifier
from app.services.agentic.tools.pricing_quote import execute_pricing_quote
from app.services.agentic.tools.emi import execute_emi_calculation
from app.services.agentic.tools.comparison import execute_vehicle_comparison
from app.services.agentic.tools.vehicle_search import execute_vehicle_search

def test_scenario_1_best_ev_under_15_lakh_ahmedabad():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Best EV under 15 lakh in Ahmedabad EMI under 20000")
    assert res.verification.is_valid
    assert len(res.tool_results) >= 1
    assert any(r.tool_name in ["search_vehicles", "calculate_pricing_quote"] for r in res.tool_results)

def test_scenario_2_nexon_vs_creta_mumbai_down_payment():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Nexon vs Creta in Mumbai with 20% down payment")
    assert res.verification.is_valid
    assert res.comparison_matrix is not None
    assert "car_a" in res.comparison_matrix and "car_b" in res.comparison_matrix

def test_scenario_3_unknown_city():
    # Should fall back cleanly or calculate state estimate without crashing
    res = execute_pricing_quote(db=None, city="Atlantis", model="Nexon")
    # Even if unsupported, returns clean failure result with clear warning
    assert res.tool_name == "calculate_pricing_quote"
    assert res.success is False or "state" in res.source_metadata

def test_scenario_4_unknown_variant_fallback():
    res = execute_pricing_quote(db=None, city="Ahmedabad", model="Thar", variant="XYZ_NonExistent_Variant")
    # Uses model baseline ex-showroom price
    assert res.success is True
    assert res.data["priceBreakdown"]["onRoadPrice"] > 0

def test_scenario_5_missing_ex_showroom_price():
    res = execute_pricing_quote(db=None, city="Ahmedabad", model="UnknownMysteryCar123")
    assert res.success is False
    assert "Ex-showroom price is required" in (res.error or "")

def test_scenario_6_hindi_request():
    planner = AgentPlanner()
    plan = planner.plan("नेक्सॉन कार का अहमदाबाद में ऑन-रोड प्राइस कितना होगा?")
    assert plan.detected_language == "hi"
    assert any(s.tool_name == "calculate_pricing_quote" for s in plan.steps)

def test_scenario_7_gujarati_request():
    planner = AgentPlanner()
    plan = planner.plan("અમદાવાદમાં નેક્સન કાર ની કિંમત અને EMI કેટલી થશે?")
    assert plan.detected_language == "gu"
    assert any(s.tool_name == "calculate_pricing_quote" for s in plan.steps)

def test_scenario_8_tool_failure_isolation():
    verifier = AgentVerifier()
    # If a tool fails, verifier catches warning without crashing system
    report = verifier.verify(
        user_prompt="Nexon price",
        detected_language="en",
        tool_results=[]
    )
    assert report.is_valid is True

def test_scenario_9_comparison_tool():
    res = execute_vehicle_comparison(car_a="Nexon", car_b="Creta")
    assert res.success is True
    assert res.data["price_difference"] > 0
    assert res.data["cheaper_model"] == "Nexon"

def test_scenario_10_step_limit_and_loop_prevention():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run("Nexon on-road price Ahmedabad", max_steps=2)
    assert len(res.tool_results) <= 2
