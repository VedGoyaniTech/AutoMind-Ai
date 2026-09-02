"""
AutoMind AI — Unit & Integration Test Suite for City-Wise RTO, On-Road Price & EMI Engine
"""

try:
    import pytest
except ImportError:
    pytest = None
from app.services.pricing.rto_rules import calculate_state_rto_tax, STATE_RTO_REGISTRY
from app.services.pricing.city_mapping import normalize_city_and_state, extract_city_or_state_from_text
from app.services.pricing.insurance import calculate_estimated_insurance
from app.services.pricing.fees import calculate_statutory_and_dealer_fees
from app.services.pricing.emi import calculate_single_emi, calculate_multi_tenure_emi_options
from app.services.pricing.engine import PricingEngine, format_inr
from app.schemas.pricing import PricingQuoteRequest

# ── 1. RTO Tax Calculations by State ─────────────────────────────────────────

def test_gujarat_rto_tax():
    res = calculate_state_rto_tax("GJ", 1200000.0, "petrol")
    assert res["state_code"] == "GJ"
    assert res["tax_rate_pct"] == 6.0
    assert res["base_rto_tax"] == 72000.0
    assert res["registration_fee"] == 600.0
    assert res["smart_card_fee"] == 200.0
    assert res["total_rto_tax_and_fees"] == 72800.0

def test_maharashtra_rto_progressive_slabs():
    # <= 10L is 11%
    res_low = calculate_state_rto_tax("MH", 800000.0, "petrol")
    assert res_low["tax_rate_pct"] == 11.0

    # 10L - 20L is 12%
    res_mid = calculate_state_rto_tax("MH", 1500000.0, "petrol")
    assert res_mid["tax_rate_pct"] == 12.0
    assert res_mid["base_rto_tax"] == 180000.0
    # Road safety cess in MH is 0.5%
    assert res_mid["road_safety_cess"] == 7500.0

def test_delhi_rto_slabs():
    res_petrol = calculate_state_rto_tax("DL", 1200000.0, "petrol")
    assert res_petrol["tax_rate_pct"] == 10.0
    assert res_petrol["base_rto_tax"] == 120000.0

    res_diesel = calculate_state_rto_tax("DL", 1200000.0, "diesel")
    assert res_diesel["tax_rate_pct"] == 12.5

def test_karnataka_rto_high_tax_and_cess():
    res = calculate_state_rto_tax("KA", 1500000.0, "petrol")
    assert res["tax_rate_pct"] == 17.0
    assert res["base_rto_tax"] == 255000.0
    # 11% infra cess on RTO tax amount
    expected_cess = round(255000.0 * 0.11, 2)
    assert res["road_safety_cess"] == expected_cess

def test_electric_vehicle_tax_exemption():
    res_gj_ev = calculate_state_rto_tax("GJ", 1500000.0, "electric")
    assert res_gj_ev["tax_rate_pct"] == 0.0
    assert res_gj_ev["base_rto_tax"] == 0.0

    res_dl_ev = calculate_state_rto_tax("DL", 1800000.0, "electric")
    assert res_dl_ev["tax_rate_pct"] == 0.0

# ── 2. City Mapping & Normalization ──────────────────────────────────────────

def test_city_normalization():
    city, state, scope = normalize_city_and_state("Ahmedabad")
    assert city == "Ahmedabad"
    assert state == "GJ"

    city, state, scope = normalize_city_and_state("mumbai")
    assert city == "Mumbai"
    assert state == "MH"

    city, state, scope = normalize_city_and_state("Bangalore")
    assert city == "Bangalore"
    assert state == "KA"

    city, state, scope = normalize_city_and_state("New Delhi")
    assert city == "New Delhi"
    assert state == "DL"

def test_unsupported_city_raises_error():
    try:
        normalize_city_and_state("RandomNonExistentCity123")
        assert False, "Should have raised ValueError"
    except ValueError as exc:
        assert "Could not resolve city/state" in str(exc)

def test_extract_city_from_conversational_text():
    city, state = extract_city_or_state_from_text("Nexon ka Ahmedabad me on-road price kitna hoga?")
    assert city == "Ahmedabad"
    assert state == "GJ"

    city, state = extract_city_or_state_from_text("Creta Mumbai EMI 5 years ke liye batao")
    assert city == "Mumbai"
    assert state == "MH"

    city, state = extract_city_or_state_from_text("Thar Bangalore down payment 3 lakh par monthly EMI?")
    assert city == "Bangalore"
    assert state == "KA"

# ── 3. Insurance & Statutory Fees ────────────────────────────────────────────

def test_insurance_calculation():
    ins = calculate_estimated_insurance(1000000.0, "petrol", include_zero_dep=True)
    assert ins["idv"] == 950000.0
    assert ins["total_insurance_estimate"] > 0
    assert len(ins["assumptions"]) > 0

def test_tcs_threshold():
    # Below ₹10L: TCS = 0
    fees_low = calculate_statutory_and_dealer_fees(800000.0)
    assert fees_low["tcs_applicable"] is False
    assert fees_low["tcs_amount"] == 0.0

    # Above ₹10L: TCS = 1%
    fees_high = calculate_statutory_and_dealer_fees(1500000.0)
    assert fees_high["tcs_applicable"] is True
    assert fees_high["tcs_amount"] == 15000.0
    assert fees_high["fastag_amount"] == 500.0

# ── 4. EMI Engine Calculations ───────────────────────────────────────────────

def test_standard_emi_calculation():
    # ₹10,00,000 principal at 9.25% for 5 years (60 months)
    emi_res = calculate_single_emi(1000000.0, 9.25, 5)
    assert emi_res["tenure_years"] == 5
    assert emi_res["tenure_months"] == 60
    assert 20000 < emi_res["monthly_emi"] < 22000
    assert emi_res["total_payable"] > 1000000.0
    assert emi_res["total_interest"] > 0.0

def test_zero_interest_emi_safety():
    # Zero interest: should split principal evenly without division-by-zero
    emi_res = calculate_single_emi(600000.0, 0.0, 5)
    assert emi_res["monthly_emi"] == 10000.0
    assert emi_res["total_interest"] == 0.0
    assert emi_res["total_payable"] == 600000.0

def test_multi_tenure_emi_options():
    res = calculate_multi_tenure_emi_options(
        on_road_price=1500000.0,
        down_payment=300000.0,
        annual_interest_rate=9.25,
        tenure_years_list=[3, 5, 7]
    )
    assert res["on_road_price"] == 1500000.0
    assert res["down_payment"] == 300000.0
    assert res["loan_principal"] == 1200000.0
    assert len(res["emi_options"]) == 3
    # 3-year EMI should be higher than 5-year and 7-year
    assert res["emi_options"][0]["monthly_emi"] > res["emi_options"][1]["monthly_emi"] > res["emi_options"][2]["monthly_emi"]

def test_down_payment_exceeding_on_road_price_error():
    try:
        calculate_multi_tenure_emi_options(on_road_price=1000000.0, down_payment=1500000.0)
        assert False, "Should have raised ValueError"
    except ValueError as exc:
        assert "cannot exceed" in str(exc)

# ── 5. Master Pricing Engine & Formatter ─────────────────────────────────────

def test_pricing_engine_quote_generation():
    engine = PricingEngine()
    req = PricingQuoteRequest(
        model="Nexon",
        city="Ahmedabad",
        downPayment=250000.0,
        annualInterestRate=9.25
    )
    quote = engine.generate_quote(req)
    assert quote.location.city == "Ahmedabad"
    assert quote.location.stateCode == "GJ"
    assert quote.vehicle.model == "Nexon"
    assert quote.priceBreakdown.onRoadPrice > quote.priceBreakdown.exShowroomPrice
    assert len(quote.emiOptions) == 3
    assert "## 🚗 On-Road Price & EMI Breakdown" in quote.formattedSummary
    assert "₹" in quote.formattedSummary

def test_format_inr():
    assert format_inr(1234567) == "₹12,34,567"
    assert format_inr(50000) == "₹50,000"
    assert format_inr(100) == "₹100"
