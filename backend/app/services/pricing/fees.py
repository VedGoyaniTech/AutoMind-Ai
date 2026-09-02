"""
AutoMind AI — Statutory Fees, TCS & FASTag Estimation Module
Calculates:
1. Tax Collected at Source (TCS) @ 1% under Section 206C(1F) for cars > ₹10 Lakh
2. Mandatory FASTag issuance fee
3. High Security Registration Plate (HSRP) & Municipal green cess
4. Optional dealer logistics/handling charges (transparently separated)
"""

from typing import Dict, Any

def calculate_statutory_and_dealer_fees(
    ex_showroom_price: float,
    include_dealer_handling: bool = False
) -> Dict[str, Any]:
    """
    Computes TCS, FASTag, and registration cess items.
    """
    if ex_showroom_price <= 0:
        raise ValueError("Ex-showroom price must be greater than zero.")

    # 1. TCS: 1.0% for vehicles whose ex-showroom price exceeds ₹10,00,000
    tcs_applicable = ex_showroom_price > 1000000.0
    tcs_amount = round(ex_showroom_price * 0.01, 2) if tcs_applicable else 0.0

    # 2. FASTag standard issuance & security deposit
    fastag_amount = 500.0

    # 3. High Security Registration Plates (HSRP) & Government Portal Fee
    hsrp_and_portal_fees = 850.0

    # 4. Optional Dealer Logistics / PDI Handling (Transparently labelled)
    dealer_handling = 15000.0 if include_dealer_handling else 0.0

    return {
        "tcs_amount": tcs_amount,
        "tcs_applicable": tcs_applicable,
        "fastag_amount": fastag_amount,
        "hsrp_and_portal_fees": hsrp_and_portal_fees,
        "dealer_handling_charges": dealer_handling,
        "include_dealer_handling": include_dealer_handling,
        "total_other_charges": round(tcs_amount + fastag_amount + hsrp_and_portal_fees + dealer_handling, 2),
        "notes": [
            "TCS (1%) is mandatory under Income Tax Sec 206C(1F) for cars above ₹10 Lakh (Adjustable against annual income tax return).",
            "FASTag includes ₹200 tag cost + ₹200 security deposit + ₹100 pre-loaded toll balance.",
            "HSRP includes High Security Number Plates with laser tamper-proof color-coded stickers."
        ]
    }
