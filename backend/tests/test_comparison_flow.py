"""
AutoMind AI — Comprehensive Vehicle Comparison Flow Test Suite
Tests:
- Multi-lingual comparison intent detection (English, Hindi, Hinglish, Gujarati)
- Clean vehicle entity extraction without conversational fillers
- Case A: Brand-only clarification (Rolls Royce vs BMW 5)
- Case B: Two valid luxury models (BMW 5 Series vs Mercedes E-Class)
- Case C: Two valid mainstream SUVs (Creta vs Seltos)
- Case D: Valid model vs unknown car (Tata Nexon vs unknowncar)
- Case E: Full-size 4x4 SUVs (Fortuner vs Endeavour)
- Case F: Typo tolerance & brand-only (Rolls Royals vs BMW 5)
- Zero hallucination validation: no fake comparison tables for unverified or brand-only queries
- Logging trace presence
"""

import pytest
import logging
from app.services.ai.vehicle_comparison_service import (
    comparison_service,
    ResolutionStatus,
    VehicleComparisonService
)
from app.services.ai.llm_provider import get_llm_provider

@pytest.fixture
def service():
    return comparison_service

@pytest.fixture
def llm():
    return get_llm_provider()

# --------------------------------------------------------------------------
# 1. Multi-Lingual Intent Detection Tests
# --------------------------------------------------------------------------
def test_intent_detection_english(service):
    assert service.detect_comparison_intent("compare BMW 5 Series and Mercedes E-Class") is True
    assert service.detect_comparison_intent("BMW 5 vs Mercedes E-Class") is True
    assert service.detect_comparison_intent("difference between Creta and Seltos") is True
    assert service.detect_comparison_intent("which is better Fortuner or Endeavour") is True

def test_intent_detection_hindi_hinglish(service):
    assert service.detect_comparison_intent("Creta aur Seltos ka comparison") is True
    assert service.detect_comparison_intent("mujhe Rolls Royce and BMW 5 ki comparison kro") is True
    assert service.detect_comparison_intent("BMW 5 Series vs Mercedes E-Class compare karo") is True
    assert service.detect_comparison_intent("Creta better hai ya Seltos") is True
    assert service.detect_comparison_intent("Fortuner ke against Endeavour") is True
    assert service.detect_comparison_intent("mujhe Fortuner aur Endeavour compare karna hai") is True
    assert service.detect_comparison_intent("Creta aur Seltos me se konsi achi hai") is True

def test_intent_detection_gujarati(service):
    assert service.detect_comparison_intent("Fortuner ane Endeavour ni tulna") is True
    assert service.detect_comparison_intent("Creta ane Seltos ni sarxamni karo") is True
    assert service.detect_comparison_intent("Fortuner ane Endeavour ma thi kai sari che") is True

def test_intent_detection_negative(service):
    assert service.detect_comparison_intent("show images of fortuner") is False
    assert service.detect_comparison_intent("what is the price of nexon in ahmedabad") is False
    assert service.detect_comparison_intent("explain ADAS level 2 technology") is False

# --------------------------------------------------------------------------
# 2. Entity Extraction & Filler Removal Tests
# --------------------------------------------------------------------------
def test_candidate_extraction_cleanliness(service):
    # Query with leading and trailing fillers
    cand_a, cand_b = service.extract_candidates("mujhe Rolls Royce and BMW 5 ki comparison kro")
    assert cand_a == "Rolls Royce"
    assert cand_b == "BMW 5"
    assert "mujhe" not in cand_a.lower()
    assert "comparison" not in cand_b.lower()
    assert "kro" not in cand_b.lower()

    # Query with 'compare' prefix and trailing 'karo'
    cand_a, cand_b = service.extract_candidates("BMW 5 Series vs Mercedes E-Class compare karo")
    assert cand_a == "BMW 5 Series"
    assert cand_b == "Mercedes E-Class"

    # Query with Gujarati 'ane' and 'ni tulna'
    cand_a, cand_b = service.extract_candidates("Fortuner ane Endeavour ni tulna")
    assert cand_a == "Fortuner"
    assert cand_b == "Endeavour"

# --------------------------------------------------------------------------
# 3. Specific Required Test Cases (A - F)
# --------------------------------------------------------------------------
def test_case_a_brand_only_clarification(service, llm):
    """
    Case A: 'mujhe Rolls Royce and BMW 5 ki comparison kro'
    Must NOT treat full user sentence as car names.
    Must detect Rolls-Royce as brand-only and BMW 5 as exact model.
    Must ask user to choose Rolls-Royce model (Ghost, Cullinan, Phantom, Spectre).
    Must NOT output a comparison table or hallucinate specifications.
    """
    query = "mujhe Rolls Royce and BMW 5 ki comparison kro"
    res = service.process_comparison(query)

    assert res.intent_detected is True
    assert res.clarification_status == "clarification_needed"
    assert res.candidate_a == "Rolls Royce"
    assert res.candidate_b == "BMW 5"
    assert res.resolution_a.status == ResolutionStatus.BRAND_ONLY
    assert res.resolution_a.brand_name == "Rolls-Royce"
    assert res.resolution_b.status == ResolutionStatus.EXACT_MODEL
    assert "BMW 5 Series" in res.resolution_b.model_name

    # Clarification must list exact 4 models
    assert "Ghost" in res.response_markdown
    assert "Cullinan" in res.response_markdown
    assert "Phantom" in res.response_markdown
    assert "Spectre" in res.response_markdown

    # Must NOT contain a comparison table
    assert "| Parameter / Feature |" not in res.response_markdown
    assert "Muje Rolls Royals" not in res.response_markdown
    assert "Bmw 5 Ki Comparison Kro" not in res.response_markdown

    # End-to-end LLM Provider generation check
    llm_resp = llm.generate(query, "")
    assert "Ghost" in llm_resp
    assert "Cullinan" in llm_resp
    assert "| Parameter / Feature |" not in llm_resp

def test_case_b_two_valid_luxury_models(service, llm):
    """
    Case B: 'BMW 5 Series vs Mercedes E-Class compare karo'
    Both are valid luxury models.
    Must generate a verified comparison table using dataset values.
    """
    query = "BMW 5 Series vs Mercedes E-Class compare karo"
    res = service.process_comparison(query)

    assert res.intent_detected is True
    assert res.clarification_status == "ready"
    assert res.resolution_a.status == ResolutionStatus.EXACT_MODEL
    assert res.resolution_b.status == ResolutionStatus.EXACT_MODEL

    # Must contain verified table
    assert "| Parameter / Feature |" in res.response_markdown
    assert "BMW 5 Series" in res.response_markdown
    assert "Mercedes-Benz E-Class" in res.response_markdown
    assert "72.90" in res.response_markdown  # BMW 5 price
    assert "76.05" in res.response_markdown  # Mercedes E price

    # LLM Provider check
    llm_resp = llm.generate(query, "")
    assert "BMW 5 Series" in llm_resp
    assert "Mercedes-Benz E-Class" in llm_resp
    assert "| Parameter / Feature |" in llm_resp

def test_case_c_creta_and_seltos(service, llm):
    """
    Case C: 'Compare Creta and Seltos'
    Both are valid midsize SUVs.
    Must generate verified comparison table.
    """
    query = "Compare Creta and Seltos"
    res = service.process_comparison(query)

    assert res.intent_detected is True
    assert res.clarification_status == "ready"
    assert "Hyundai Creta" in res.response_markdown
    assert "Kia Seltos" in res.response_markdown
    assert "| Parameter / Feature |" in res.response_markdown

    # LLM check
    llm_resp = llm.generate(query, "")
    assert "Hyundai Creta" in llm_resp
    assert "Kia Seltos" in llm_resp

def test_case_d_valid_vs_unknown_car(service, llm):
    """
    Case D: 'Compare Tata Nexon vs unknowncar'
    Tata Nexon is identified.
    unknowncar is recognized as missing from dataset.
    Must state unknowncar is not in dataset; must NOT fabricate data or table.
    """
    query = "Compare Tata Nexon vs unknowncar"
    res = service.process_comparison(query)

    assert res.intent_detected is True
    assert res.clarification_status == "car_not_found"
    assert res.resolution_a.status == ResolutionStatus.EXACT_MODEL
    assert "Tata Nexon" in res.resolution_a.model_name
    assert res.resolution_b.status == ResolutionStatus.NOT_FOUND

    # Must inform about unknowncar and NOT generate comparison table
    assert "unknowncar" in res.response_markdown
    assert "| Parameter / Feature |" not in res.response_markdown
    assert "Tata Nexon" in res.response_markdown

    # LLM check
    llm_resp = llm.generate(query, "")
    assert "unknowncar" in llm_resp
    assert "| Parameter / Feature |" not in llm_resp

def test_case_e_fortuner_vs_endeavour(service, llm):
    """
    Case E: 'compare Fortuner vs Endeavour'
    Must match Toyota Fortuner and Ford Endeavour.
    Must show verified comparison table.
    """
    query = "compare Fortuner vs Endeavour"
    res = service.process_comparison(query)

    assert res.intent_detected is True
    assert res.clarification_status == "ready"
    assert "Toyota Fortuner" in res.response_markdown
    assert "Ford Endeavour" in res.response_markdown
    assert "| Parameter / Feature |" in res.response_markdown

    # LLM check
    llm_resp = llm.generate(query, "")
    assert "Toyota Fortuner" in llm_resp
    assert "Ford Endeavour" in llm_resp

def test_case_f_typo_brand_only(service, llm):
    """
    Case F: 'Rolls Royals vs BMW 5'
    Must correct typo 'Rolls Royals' -> Rolls-Royce.
    Must detect Rolls-Royce as brand-only and ask for model clarification.
    Must NOT generate a comparison table.
    """
    query = "Rolls Royals vs BMW 5"
    res = service.process_comparison(query)

    assert res.intent_detected is True
    assert res.clarification_status == "clarification_needed"
    assert res.resolution_a.status == ResolutionStatus.BRAND_ONLY
    assert res.resolution_a.brand_name == "Rolls-Royce"
    assert res.resolution_b.status == ResolutionStatus.EXACT_MODEL

    # Must list Rolls-Royce models
    assert "Ghost" in res.response_markdown
    assert "Cullinan" in res.response_markdown
    assert "| Parameter / Feature |" not in res.response_markdown

    # LLM check
    llm_resp = llm.generate(query, "")
    assert "Ghost" in llm_resp
    assert "Cullinan" in llm_resp
    assert "| Parameter / Feature |" not in llm_resp

# --------------------------------------------------------------------------
# 4. Developer Logging Trace Verification (Requirement 11)
# --------------------------------------------------------------------------
def test_developer_trace_logging(service, caplog):
    with caplog.at_level(logging.INFO, logger="automind.comparison"):
        query = "mujhe Rolls Royce and BMW 5 ki comparison kro"
        service.process_comparison(query)

        # Verify trace log contents
        assert any(
            "Vehicle Comparison Flow Trace:" in record.message
            and "raw_query='mujhe Rolls Royce and BMW 5 ki comparison kro'" in record.message
            and "detected_intent=True" in record.message
            and "clarification_status='clarification_needed'" in record.message
            for record in caplog.records
        )
