import sys
import os
try:
    import pytest
except ImportError:
    pytest = None

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

# Mock pydantic if C-extensions are missing
class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def mock_config_dict(*args, **kwargs):
    return {}

sys.modules["pydantic"] = type("module", (), {"BaseModel": MockBaseModel, "ConfigDict": mock_config_dict})()

# Mock config module before importing app services
class MockSettings:
    VECTOR_INDEX_PATH = "backend/vector_index"
    ENABLE_DUCKDUCKGO_SEARCH = True
    DUCKDUCKGO_MAX_RESULTS = 5
    LLM_PROVIDER = "local"
    LLM_MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
    RETRIEVAL_TOP_K = 10
    RERANK_TOP_K = 10

import types
config_mod = types.ModuleType("app.core.config")
config_mod.settings = MockSettings()
sys.modules["app.core.config"] = config_mod

from app.services.ai.query_analyzer import QueryAnalyzer
from app.services.ai.dataset_store import CarDatasetStore
from app.services.ai.llm_provider import GroundedLLMProvider

def test_case_1_2005_launches():
    """Case 1: 'mujhe 2005 me kaunsi car launch hui list chahiye' -> Only 2005 records, no Curvv/Thar Roxx/XUV3XO/Punch EV."""
    analyzer = QueryAnalyzer()
    analysis = analyzer.analyze("mujhe 2005 me kaunsi car launch hui list chahiye")

    assert analysis["requested_year"] == 2005, f"Expected 2005 year, got {analysis['requested_year']}"

    records = CarDatasetStore.query(launch_year=2005, market="India")
    assert len(records) > 0, "Expected 2005 dataset records"

    car_names = [r["car_name"].lower() for r in records]
    assert any("swift" in c for c in car_names) or any("innova" in c for c in car_names) or any("city" in c for c in car_names)

    # Verify NO 2024 mass-market cars present
    forbidden = ["curvv", "thar roxx", "xuv3xo", "punch ev"]
    for f in forbidden:
        assert not any(f in c for c in car_names), f"Forbidden 2024 car '{f}' found in 2005 results!"

    # Test LLM Provider Output
    llm = GroundedLLMProvider()
    resp = llm._generate_dynamic_car_launches_response(
        prompt="mujhe 2005 me kaunsi car launch hui list chahiye",
        target_year=2005,
        is_luxury=False,
        candidates=records,
        web_results=[]
    )
    assert "2005" in resp
    assert "Swift (1st Gen)" in resp or "Innova (1st Gen)" in resp
    for f in forbidden:
        assert f not in resp.lower(), f"Forbidden 2024 car '{f}' present in 2005 LLM response!"


def test_case_2_2026_luxury_launches():
    """Case 2: '2026 me luxury car kaunsi launch hui hai' -> Only 2026 luxury records, no Nexon/Brezza/XUV400/Seltos."""
    analyzer = QueryAnalyzer()
    analysis = analyzer.analyze("2026 me luxury car kaunsi launch hui hai")

    assert analysis["requested_year"] == 2026
    assert analysis["is_luxury"] is True

    records = CarDatasetStore.query(launch_year=2026, category="luxury", market="India")
    assert len(records) > 0, "Expected 2026 luxury dataset records"

    car_names = [r["car_name"].lower() for r in records]

    # Verify NO budget sub-4m cars present in 2026 luxury
    forbidden = ["nexon", "brezza", "xuv400", "seltos", "swift", "punch"]
    for f in forbidden:
        assert not any(f in c for c in car_names), f"Mass-market car '{f}' found in 2026 luxury results!"

    # Test LLM Provider Output
    llm = GroundedLLMProvider()
    resp = llm._generate_dynamic_car_launches_response(
        prompt="2026 me luxury car kaunsi launch hui hai",
        target_year=2026,
        is_luxury=True,
        candidates=records,
        web_results=[]
    )
    assert "Luxury" in resp or "2026" in resp
    for f in forbidden:
        assert f not in resp.lower(), f"Mass-market car '{f}' present in 2026 luxury LLM response!"


def test_case_3_2024_ev_launches():
    """Case 3: '2024 EV launches India' -> Only 2024 EV records."""
    analyzer = QueryAnalyzer()
    analysis = analyzer.analyze("2024 EV launches India")

    assert analysis["requested_year"] == 2024

    records = CarDatasetStore.query(launch_year=2024, fuel_type="EV", market="India")
    assert len(records) > 0, "Expected 2024 EV records"

    for r in records:
        assert r["fuel_type"].lower() in ["ev", "electric"], f"Non-EV record '{r['car_name']}' found in 2024 EV query!"
        assert r["launch_year"] == 2024, f"Non-2024 record '{r['car_name']}' found in 2024 EV query!"


def test_case_4_no_dataset_match():
    """Case 4: Query with no dataset match -> Transparent no-data message, NEVER a generic default list."""
    llm = GroundedLLMProvider()
    resp = llm._generate_dynamic_car_launches_response(
        prompt="1990 luxury EV launches India",
        target_year=1990,
        is_luxury=True,
        candidates=[],
        web_results=[]
    )

    assert "Dataset mein India ke" in resp or "verified record available nahi hai" in resp
    assert "Curvv" not in resp
    assert "Thar Roxx" not in resp
    assert "Nexon" not in resp

if __name__ == "__main__":
    print("Running automated dataset retrieval tests...")
    test_case_1_2005_launches()
    print("✔ Test Case 1 PASSED: 2005 Launches strictly isolated")
    test_case_2_2026_luxury_launches()
    print("✔ Test Case 2 PASSED: 2026 Luxury Launches strictly isolated")
    test_case_3_2024_ev_launches()
    print("✔ Test Case 3 PASSED: 2024 EV Launches strictly isolated")
    test_case_4_no_dataset_match()
    print("✔ Test Case 4 PASSED: Transparent No-Data Message verified")
    print("\nALL 4 AUTOMATED TEST CASES PASSED CLEANLY!")
