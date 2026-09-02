"""
AutoMind AI — Comprehensive Motor Insurance Estimation Engine
Calculates standard comprehensive insurance packages for new private vehicles in India:
1. 1-Year Own Damage (OD) coverage (based on 95% Insured Declared Value - IDV)
2. 3-Year Mandatory Third Party (TP) liability coverage (IRDAI regulated baseline)
3. Optional Zero-Depreciation / Bumper-to-Bumper Add-on cover
"""

from typing import Dict, Any

def calculate_estimated_insurance(
    ex_showroom_price: float,
    fuel_type: str = "petrol",
    include_zero_dep: bool = True
) -> Dict[str, Any]:
    """
    Computes an estimated comprehensive insurance quote.
    """
    if ex_showroom_price <= 0:
        raise ValueError("Ex-showroom price must be greater than zero for insurance calculation.")

    # 1. Insured Declared Value (IDV) for brand-new vehicle is 95% of Ex-Showroom
    idv = round(ex_showroom_price * 0.95, 2)

    # 2. 1-Year Own Damage (OD) Tariff (approx 1.8% to 2.4% based on fuel/category)
    od_rate_pct = 2.1 if fuel_type.lower() in ["diesel", "electric"] else 1.85
    own_damage_premium = round((idv * od_rate_pct) / 100.0, 2)

    # 3. 3-Year Mandatory Third Party (TP) Premium (IRDAI statutory base)
    # <1000cc: ~₹5,286, 1000-1500cc: ~₹9,534, >1500cc/EV: ~₹24,596
    if ex_showroom_price < 800000:
        third_party_3yr = 5450.0
    elif ex_showroom_price < 1800000:
        third_party_3yr = 9850.0
    else:
        third_party_3yr = 24500.0

    # 4. Optional Zero Depreciation (Bumper-to-Bumper) Add-on Cover (~0.75% of IDV)
    zero_dep_addon = round((idv * 0.75) / 100.0, 2) if include_zero_dep else 0.0

    # 5. GST on Insurance (18% on total premium)
    subtotal = own_damage_premium + third_party_3yr + zero_dep_addon
    gst_18pct = round(subtotal * 0.18, 2)
    total_insurance = round(subtotal + gst_18pct, 2)

    return {
        "idv": idv,
        "own_damage_1yr": own_damage_premium,
        "third_party_3yr_mandatory": third_party_3yr,
        "zero_depreciation_addon": zero_dep_addon,
        "gst_18pct": gst_18pct,
        "total_insurance_estimate": total_insurance,
        "include_zero_dep": include_zero_dep,
        "assumptions": [
            f"IDV computed as 95% of Ex-Showroom (₹{idv:,.2f})",
            "Includes 1-Year Own Damage + 3-Year Mandatory Third-Party Cover (IRDAI)",
            "Includes 18% statutory GST on motor insurance",
            "Final quote varies by insurer, NCB (No Claim Bonus), and selected add-ons"
        ]
    }
