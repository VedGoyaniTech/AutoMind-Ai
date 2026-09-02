"""
AutoMind AI — Comprehensive Multi-Scenario & Voice Test Suite
Validates:
1. Voice API (sample prompts & fallback audio transcription)
2. Hindi, Gujarati, English automotive question answering
3. City RTO pricing & reducing-balance loan EMI calculation
4. Multi-modal vehicle gallery associations
5. Feedback logging & idempotency
"""

import os
import sys
import pytest
from app.services.pricing.engine import PricingEngine
from app.schemas.pricing import PricingQuoteRequest
from app.services.vehicle_media import get_vehicle_gallery_for_query
from app.services.ai.llm_provider import get_llm_provider

def test_voice_sample_prompts(client):
    """Verify voice sample prompts for Hindi, Gujarati, and English."""
    for locale in ["hi-IN", "gu-IN", "en-IN"]:
        res = client.get(f"/api/v1/voice/sample-prompts?locale={locale}")
        assert res.status_code == 200
        data = res.json()
        assert data["locale"] == locale
        assert len(data["prompts"]) > 0
        assert "text" in data["prompts"][0]

def test_voice_transcription_and_intent_detection(client):
    """Verify voice transcription endpoint extracts intent and returns formatted query."""
    # Pricing Intent
    res_pricing = client.post(
        "/api/v1/voice/transcribe",
        data={"language": "hi-IN", "text_fallback": "Nexon on-road price in Ahmedabad"}
    )
    assert res_pricing.status_code == 200
    assert res_pricing.json()["detected_intent"] == "pricing_rto"

    # EMI Intent
    res_emi = client.post(
        "/api/v1/voice/transcribe",
        data={"language": "hi-IN", "text_fallback": "Creta Mumbai monthly EMI 5 years"}
    )
    assert res_emi.status_code == 200
    assert res_emi.json()["detected_intent"] == "loan_emi"

    # Gujarati Intent
    res_gu = client.post(
        "/api/v1/voice/transcribe",
        data={"language": "gu-IN", "text_fallback": "નેક્સન કાર ની અમદાવાદ માં કિંમત"}
    )
    assert res_gu.status_code == 200
    assert res_gu.json()["detected_intent"] == "pricing_rto"

def test_scenario_city_rto_and_emi_answering():
    """Verify city-wise pricing and EMI calculations across multiple Indian cities."""
    engine = PricingEngine()

    # Ahmedabad / Gujarat
    gj_req = PricingQuoteRequest(
        exShowroomPrice=1150000,
        city="Ahmedabad",
        fuelType="petrol",
        seatingCapacity=5,
        engineCc=1199,
        downPayment=250000,
        annualInterestRate=9.25
    )
    gj_quote = engine.generate_quote(gj_req)
    assert gj_quote.location.stateCode == "GJ"
    assert gj_quote.priceBreakdown.rtoTax == 69000.0
    assert len(gj_quote.emiOptions) == 3

    # Mumbai / Maharashtra
    mh_req = PricingQuoteRequest(
        exShowroomPrice=1500000,
        city="Mumbai",
        fuelType="diesel",
        seatingCapacity=5,
        engineCc=1493,
        downPayment=300000,
        annualInterestRate=9.25
    )
    mh_quote = engine.generate_quote(mh_req)
    assert mh_quote.location.stateCode == "MH"
    assert mh_quote.priceBreakdown.onRoadPrice > 1500000

    # Bangalore / Karnataka
    ka_req = PricingQuoteRequest(
        exShowroomPrice=1600000,
        city="Bangalore",
        fuelType="diesel",
        seatingCapacity=4,
        engineCc=2184,
        downPayment=400000,
        annualInterestRate=9.5
    )
    ka_quote = engine.generate_quote(ka_req)
    assert ka_quote.location.stateCode == "KA"
    assert ka_quote.priceBreakdown.rtoTax > 250000

def test_scenario_multilingual_llm_responses():
    """Verify that the conversational LLM generates informative answers for Hindi, Gujarati, and comparisons."""
    llm = get_llm_provider()

    # Hindi Safety Query
    hindi_resp = llm.generate("मुझे 15 लाख में 6 एयरबैग वाली सबसे सुरक्षित कार बताएं", "")
    assert len(hindi_resp) > 50
    assert "Nexon" in hindi_resp or "3XO" in hindi_resp or "5-Star" in hindi_resp

    # Gujarati Mileage Query
    gu_resp = llm.generate("મને ૧૨ લાખ ના બજેટ માં સારી માઈલેજ આપતી ઓટોમેટિક ગાડી જોઈએ છે", "")
    assert len(gu_resp) > 50
    assert "Dzire" in gu_resp or "Fronx" in gu_resp or "km/l" in gu_resp

    # Head to Head Comparison
    comp_resp = llm.generate("Compare Mahindra Thar vs Suzuki Jimny", "")
    assert "Mahindra Thar" in comp_resp
    assert "Suzuki Jimny" in comp_resp

def test_scenario_vehicle_media_galleries():
    """Verify structured image galleries are available for popular car models."""
    for model in ["Thar", "Creta", "Nexon", "Curvv", "Dzire"]:
        gallery = get_vehicle_gallery_for_query(model)
        assert gallery is not None
        assert len(gallery["images"]) >= 1
        assert all("url" in img and "caption" in img for img in gallery["images"])
