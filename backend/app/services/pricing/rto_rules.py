"""
AutoMind AI — Configurable RTO Tax Rules Service Layer
Version: 1.0.0 (Effective: 2025-2026 Fiscal Year)

IMPORTANT NOTE:
RTO tax rules and motor vehicle tax slabs change frequently across Indian states
and municipal jurisdictions. All calculations produced by this module represent
standard estimated baseline calculations based on state motor vehicle acts and
must be verified with local RTO offices or official Vahan portal for statutory exactness.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class RTOTaxSlab(BaseModel):
    min_price: float = 0.0
    max_price: float = float("inf")
    rate_percentage: float
    flat_cess: float = 0.0
    description: str = ""

class StateRTORule(BaseModel):
    state_code: str
    state_name: str
    version: str = "2025.1"
    effective_date: str = "2025-04-01"
    # Fuel types: petrol, diesel, cng, electric, hybrid
    fuel_slabs: Dict[str, List[RTOTaxSlab]]
    registration_fee: float = 600.0
    smart_card_fee: float = 200.0
    road_safety_cess_pct: float = 0.0
    notes: str = ""

# ── State-specific RTO Tax Rule Registry ──────────────────────────────────────
STATE_RTO_REGISTRY: Dict[str, StateRTORule] = {
    "GJ": StateRTORule(
        state_code="GJ",
        state_name="Gujarat",
        fuel_slabs={
            "petrol": [
                RTOTaxSlab(min_price=0, max_price=600000, rate_percentage=6.0, description="Up to ₹6 Lakh: 6% RTO Tax"),
                RTOTaxSlab(min_price=600000, max_price=1500000, rate_percentage=6.0, description="₹6L - ₹15L: 6% RTO Tax"),
                RTOTaxSlab(min_price=1500000, max_price=float("inf"), rate_percentage=6.0, description="Above ₹15L: 6% RTO Tax"),
            ],
            "diesel": [
                RTOTaxSlab(min_price=0, max_price=float("inf"), rate_percentage=6.0, description="Diesel Vehicles: 6% Flat RTO Tax"),
            ],
            "cng": [
                RTOTaxSlab(min_price=0, max_price=float("inf"), rate_percentage=6.0, description="Factory Fitted CNG: 6% RTO Tax"),
            ],
            "electric": [
                RTOTaxSlab(min_price=0, max_price=float("inf"), rate_percentage=0.0, description="Electric Vehicles: 100% RTO Tax Exemption"),
            ],
            "hybrid": [
                RTOTaxSlab(min_price=0, max_price=float("inf"), rate_percentage=6.0, description="Strong Hybrid: 6% RTO Tax"),
            ]
        },
        registration_fee=600.0,
        smart_card_fee=200.0,
        road_safety_cess_pct=0.0,
        notes="Gujarat levies standard 6% individual road tax on private non-transport 4-wheelers."
    ),
    "MH": StateRTORule(
        state_code="MH",
        state_name="Maharashtra",
        fuel_slabs={
            "petrol": [
                RTOTaxSlab(min_price=0, max_price=1000000, rate_percentage=11.0, description="Up to ₹10 Lakh: 11% RTO Tax"),
                RTOTaxSlab(min_price=1000000, max_price=2000000, rate_percentage=12.0, description="₹10L - ₹20L: 12% RTO Tax"),
                RTOTaxSlab(min_price=2000000, max_price=float("inf"), rate_percentage=13.0, description="Above ₹20L: 13% RTO Tax"),
            ],
            "diesel": [
                RTOTaxSlab(min_price=0, max_price=1000000, rate_percentage=13.0, description="Diesel Up to ₹10 Lakh: 13% RTO Tax"),
                RTOTaxSlab(min_price=1000000, max_price=2000000, rate_percentage=14.0, description="Diesel ₹10L - ₹20L: 14% RTO Tax"),
                RTOTaxSlab(min_price=2000000, max_price=float("inf"), rate_percentage=15.0, description="Diesel Above ₹20L: 15% RTO Tax"),
            ],
            "cng": [
                RTOTaxSlab(min_price=0, max_price=float("inf"), rate_percentage=7.0, description="CNG Vehicles: 7% Concessional RTO Tax"),
            ],
            "electric": [
                RTOTaxSlab(min_price=0, max_price=float("inf"), rate_percentage=0.0, description="Electric Vehicles: 0% Road Tax (EV Policy Subsidy)"),
            ],
            "hybrid": [
                RTOTaxSlab(min_price=0, max_price=1000000, rate_percentage=11.0, description="Hybrid Up to ₹10L: 11%"),
                RTOTaxSlab(min_price=1000000, max_price=float("inf"), rate_percentage=12.0, description="Hybrid Above ₹10L: 12%"),
            ]
        },
        registration_fee=600.0,
        smart_card_fee=200.0,
        road_safety_cess_pct=0.5,
        notes="Maharashtra applies progressive slabs for Petrol/Diesel + 0.5% Road Safety Cess."
    ),
    "DL": StateRTORule(
        state_code="DL",
        state_name="Delhi",
        fuel_slabs={
            "petrol": [
                RTOTaxSlab(min_price=0, max_price=600000, rate_percentage=4.0, description="Up to ₹6 Lakh: 4% RTO Tax"),
                RTOTaxSlab(min_price=600000, max_price=1000000, rate_percentage=7.0, description="₹6L - ₹10L: 7% RTO Tax"),
                RTOTaxSlab(min_price=1000000, max_price=float("inf"), rate_percentage=10.0, description="Above ₹10L: 10% RTO Tax"),
            ],
            "diesel": [
                RTOTaxSlab(min_price=0, max_price=600000, rate_percentage=5.0, description="Diesel Up to ₹6 Lakh: 5% RTO Tax"),
                RTOTaxSlab(min_price=600000, max_price=1000000, rate_percentage=8.75, description="Diesel ₹6L - ₹10L: 8.75% RTO Tax"),
                RTOTaxSlab(min_price=1000000, max_price=float("inf"), rate_percentage=12.5, description="Diesel Above ₹10L: 12.5% RTO Tax"),
            ],
            "cng": [
                RTOTaxSlab(min_price=0, max_price=600000, rate_percentage=4.0, description="CNG Up to ₹6L: 4%"),
                RTOTaxSlab(min_price=600000, max_price=float("inf"), rate_percentage=7.0, description="CNG Above ₹6L: 7%"),
            ],
            "electric": [
                RTOTaxSlab(min_price=0, max_price=float("inf"), rate_percentage=0.0, description="EV: 0% Road Tax under Delhi EV Policy"),
            ],
            "hybrid": [
                RTOTaxSlab(min_price=0, max_price=1000000, rate_percentage=7.0, description="Hybrid Up to ₹10L: 7%"),
                RTOTaxSlab(min_price=1000000, max_price=float("inf"), rate_percentage=10.0, description="Hybrid Above ₹10L: 10%"),
            ]
        },
        registration_fee=600.0,
        smart_card_fee=200.0,
        road_safety_cess_pct=0.0,
        notes="Delhi applies tiered taxation with total EV tax waiver."
    ),
    "KA": StateRTORule(
        state_code="KA",
        state_name="Karnataka",
        fuel_slabs={
            "petrol": [
                RTOTaxSlab(min_price=0, max_price=500000, rate_percentage=13.0, description="Up to ₹5 Lakh: 13% RTO Tax"),
                RTOTaxSlab(min_price=500000, max_price=1000000, rate_percentage=14.0, description="₹5L - ₹10L: 14% RTO Tax"),
                RTOTaxSlab(min_price=1000000, max_price=2000000, rate_percentage=17.0, description="₹10L - ₹20L: 17% RTO Tax"),
                RTOTaxSlab(min_price=2000000, max_price=float("inf"), rate_percentage=18.0, description="Above ₹20L: 18% RTO Tax"),
            ],
            "diesel": [
                RTOTaxSlab(min_price=0, max_price=500000, rate_percentage=13.0, description="Diesel Up to ₹5 Lakh: 13% RTO Tax"),
                RTOTaxSlab(min_price=500000, max_price=1000000, rate_percentage=14.0, description="Diesel ₹5L - ₹10L: 14% RTO Tax"),
                RTOTaxSlab(min_price=1000000, max_price=2000000, rate_percentage=17.0, description="Diesel ₹10L - ₹20L: 17% RTO Tax"),
                RTOTaxSlab(min_price=2000000, max_price=float("inf"), rate_percentage=18.0, description="Diesel Above ₹20L: 18% RTO Tax"),
            ],
            "cng": [
                RTOTaxSlab(min_price=0, max_price=1000000, rate_percentage=14.0, description="CNG Up to ₹10L: 14%"),
                RTOTaxSlab(min_price=1000000, max_price=float("inf"), rate_percentage=17.0, description="CNG Above ₹10L: 17%"),
            ],
            "electric": [
                RTOTaxSlab(min_price=0, max_price=2500000, rate_percentage=0.0, description="EVs up to ₹25 Lakh: 0% Road Tax"),
                RTOTaxSlab(min_price=2500000, max_price=float("inf"), rate_percentage=10.0, description="Luxury EVs above ₹25 Lakh: 10% Road Tax"),
            ],
            "hybrid": [
                RTOTaxSlab(min_price=0, max_price=1000000, rate_percentage=14.0, description="Hybrid Up to ₹10L: 14%"),
                RTOTaxSlab(min_price=1000000, max_price=float("inf"), rate_percentage=17.0, description="Hybrid Above ₹10L: 17%"),
            ]
        },
        registration_fee=600.0,
        smart_card_fee=200.0,
        road_safety_cess_pct=11.0,  # 11% cess on RTO tax amount in Karnataka
        notes="Karnataka levies highest RTO rates in India plus 11% Infrastructure/Road Safety Cess on the tax amount."
    )
}

def calculate_state_rto_tax(
    state_code: str,
    ex_showroom_price: float,
    fuel_type: str = "petrol"
) -> Dict[str, Any]:
    """
    Calculates detailed RTO tax, cess, and registration fees for a given state.
    """
    code = state_code.upper().strip()
    if code not in STATE_RTO_REGISTRY:
        raise ValueError(f"Unsupported state code '{state_code}'. Supported states: {list(STATE_RTO_REGISTRY.keys())}")

    rule = STATE_RTO_REGISTRY[code]
    fuel = fuel_type.lower().strip()
    if fuel not in rule.fuel_slabs:
        fuel = "petrol"  # Fallback to petrol baseline

    slabs = rule.fuel_slabs[fuel]
    matched_slab = None
    for s in slabs:
        if s.min_price <= ex_showroom_price < s.max_price:
            matched_slab = s
            break
    if not matched_slab and slabs:
        matched_slab = slabs[-1]

    base_rto_tax = round((ex_showroom_price * matched_slab.rate_percentage) / 100.0, 2)
    
    # State Cess Calculation
    cess_amount = 0.0
    if code == "KA":
        # Karnataka: 11% cess ON the RTO tax amount
        cess_amount = round((base_rto_tax * rule.road_safety_cess_pct) / 100.0, 2)
    elif rule.road_safety_cess_pct > 0:
        # Maharashtra: 0.5% on ex-showroom
        cess_amount = round((ex_showroom_price * rule.road_safety_cess_pct) / 100.0, 2)

    total_rto_payable = round(base_rto_tax + cess_amount + rule.registration_fee + rule.smart_card_fee, 2)

    return {
        "state_code": code,
        "state_name": rule.state_name,
        "fuel_type": fuel,
        "ex_showroom_price": ex_showroom_price,
        "tax_rate_pct": matched_slab.rate_percentage,
        "base_rto_tax": base_rto_tax,
        "road_safety_cess": cess_amount,
        "registration_fee": rule.registration_fee,
        "smart_card_fee": rule.smart_card_fee,
        "total_rto_tax_and_fees": total_rto_payable,
        "slab_description": matched_slab.description,
        "version": rule.version,
        "effective_date": rule.effective_date,
        "notes": rule.notes
    }
