"""
AutoMind AI — Master On-Road Pricing & Loan EMI Orchestration Engine
Combines:
- Vehicle DB / Catalog pricing lookup
- City-to-state RTO tax calculation
- IRDAI-based comprehensive motor insurance
- 1% TCS, FASTag, HSRP & statutory cess
- Reducing-balance EMI calculation across 3, 5, and 7-year tenures
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.services.pricing.rto_rules import calculate_state_rto_tax, STATE_RTO_REGISTRY
from app.services.pricing.city_mapping import normalize_city_and_state
from app.services.pricing.insurance import calculate_estimated_insurance
from app.services.pricing.fees import calculate_statutory_and_dealer_fees
from app.services.pricing.emi import calculate_multi_tenure_emi_options
from app.schemas.pricing import (
    PricingQuoteRequest, PricingQuoteResponse,
    LocationInfo, VehicleInfo, PriceBreakdown, EMIOptionItem
)

# Standard Ex-Showroom Baseline Registry for popular models when not in DB
BASELINE_EX_SHOWROOM_PRICES: Dict[str, Dict[str, Any]] = {
    # Mainstream Compact & Midsize SUVs
    "nexon": {"mfg": "Tata", "model": "Nexon", "variant": "Creative Plus 1.2 MT", "price": 1150000.0, "fuel": "petrol"},
    "creta": {"mfg": "Hyundai", "model": "Creta", "variant": "SX (O) 1.5 IVT", "price": 1860000.0, "fuel": "petrol"},
    "thar": {"mfg": "Mahindra", "model": "Thar", "variant": "LX 4WD Hard Top", "price": 1540000.0, "fuel": "diesel"},
    "curvv": {"mfg": "Tata", "model": "Curvv", "variant": "Accomplished Plus 1.5 DCA", "price": 1749000.0, "fuel": "diesel"},
    "seltos": {"mfg": "Kia", "model": "Seltos", "variant": "GTX Plus 1.5 AT", "price": 1890000.0, "fuel": "petrol"},
    "safari": {"mfg": "Tata", "model": "Safari", "variant": "Accomplished Plus 2.0 AT", "price": 2450000.0, "fuel": "diesel"},
    "harrier": {"mfg": "Tata", "model": "Harrier", "variant": "Fearless Plus Dark AT", "price": 2350000.0, "fuel": "diesel"},
    "xuv700": {"mfg": "Mahindra", "model": "XUV700", "variant": "AX7 L AWD Diesel AT", "price": 2499000.0, "fuel": "diesel"},
    "scorpio": {"mfg": "Mahindra", "model": "Scorpio-N", "variant": "Z8 L 4x4 AT", "price": 2250000.0, "fuel": "diesel"},
    "brezza": {"mfg": "Maruti Suzuki", "model": "Brezza", "variant": "ZXi Plus AT", "price": 1250000.0, "fuel": "petrol"},
    "punch": {"mfg": "Tata", "model": "Punch", "variant": "Creative Flagship", "price": 950000.0, "fuel": "petrol"},
    "exter": {"mfg": "Hyundai", "model": "Exter", "variant": "SX (O) Connect AMT", "price": 980000.0, "fuel": "petrol"},
    "fronx": {"mfg": "Maruti Suzuki", "model": "Fronx", "variant": "Alpha 1.0 Turbo AT", "price": 1185000.0, "fuel": "petrol"},
    "jimny": {"mfg": "Maruti Suzuki", "model": "Jimny", "variant": "Alpha 4x4 AT", "price": 1479000.0, "fuel": "petrol"},
    "kushaq": {"mfg": "Skoda", "model": "Kushaq", "variant": "Monte Carlo 1.5 TSI DSG", "price": 1850000.0, "fuel": "petrol"},
    "taigun": {"mfg": "Volkswagen", "model": "Taigun", "variant": "GT Plus 1.5 TSI DSG", "price": 1890000.0, "fuel": "petrol"},
    "elevate": {"mfg": "Honda", "model": "Elevate", "variant": "ZX CVT", "price": 1590000.0, "fuel": "petrol"},
    "sonet": {"mfg": "Kia", "model": "Sonet", "variant": "GTX Plus 1.5 AT", "price": 1450000.0, "fuel": "diesel"},
    "xuv3xo": {"mfg": "Mahindra", "model": "XUV 3XO", "variant": "AX7 L Turbo AT", "price": 1399000.0, "fuel": "petrol"},
    "3xo": {"mfg": "Mahindra", "model": "XUV 3XO", "variant": "AX7 L Turbo AT", "price": 1399000.0, "fuel": "petrol"},

    # Premium MPVs & Full-Size SUVs
    "innova": {"mfg": "Toyota", "model": "Innova Hycross", "variant": "ZX (O) Hybrid", "price": 3098000.0, "fuel": "hybrid"},
    "fortuner": {"mfg": "Toyota", "model": "Fortuner", "variant": "4x4 AT GR-S Diesel", "price": 4350000.0, "fuel": "diesel"},

    # Sedans & Hatchbacks
    "dzire": {"mfg": "Maruti Suzuki", "model": "Dzire", "variant": "ZXi Plus AGS", "price": 1014000.0, "fuel": "petrol"},
    "swift": {"mfg": "Maruti Suzuki", "model": "Swift", "variant": "ZXi Plus AMT", "price": 895000.0, "fuel": "petrol"},
    "city": {"mfg": "Honda", "model": "City", "variant": "ZX CVT", "price": 1620000.0, "fuel": "petrol"},
    "verna": {"mfg": "Hyundai", "model": "Verna", "variant": "SX (O) 1.5 Turbo DCT", "price": 1740000.0, "fuel": "petrol"},
    "slavia": {"mfg": "Skoda", "model": "Slavia", "variant": "Style 1.5 TSI DSG", "price": 1750000.0, "fuel": "petrol"},
    "virtus": {"mfg": "Volkswagen", "model": "Virtus", "variant": "GT Plus 1.5 TSI DSG", "price": 1780000.0, "fuel": "petrol"},
    "baleno": {"mfg": "Maruti Suzuki", "model": "Baleno", "variant": "Alpha AGS", "price": 980000.0, "fuel": "petrol"},
    "i20": {"mfg": "Hyundai", "model": "i20", "variant": "Asta (O) IVT", "price": 1080000.0, "fuel": "petrol"},
    "tiago": {"mfg": "Tata", "model": "Tiago", "variant": "XZ Plus Dual Tone", "price": 750000.0, "fuel": "petrol"},

    # Electric Vehicles
    "nexon ev": {"mfg": "Tata", "model": "Nexon EV", "variant": "Empowered Plus LR", "price": 1699000.0, "fuel": "electric"},
    "punch ev": {"mfg": "Tata", "model": "Punch EV", "variant": "Empowered Plus S LR", "price": 1429000.0, "fuel": "electric"},
    "curvv ev": {"mfg": "Tata", "model": "Curvv EV", "variant": "Empowered Plus 55", "price": 2199000.0, "fuel": "electric"},
    "windsor": {"mfg": "MG", "model": "Windsor EV", "variant": "Essence Pro", "price": 1550000.0, "fuel": "electric"},
    "windsor ev": {"mfg": "MG", "model": "Windsor EV", "variant": "Essence Pro", "price": 1550000.0, "fuel": "electric"},
    "zs ev": {"mfg": "MG", "model": "ZS EV", "variant": "Exclusive Plus", "price": 2490000.0, "fuel": "electric"},

    # Luxury & Executive Segment
    "bmw 3": {"mfg": "BMW", "model": "3 Series Gran Limousine", "variant": "330Li M Sport", "price": 6060000.0, "fuel": "petrol"},
    "bmw3": {"mfg": "BMW", "model": "3 Series Gran Limousine", "variant": "330Li M Sport", "price": 6060000.0, "fuel": "petrol"},
    "3 series": {"mfg": "BMW", "model": "3 Series Gran Limousine", "variant": "330Li M Sport", "price": 6060000.0, "fuel": "petrol"},
    "bmw x1": {"mfg": "BMW", "model": "X1", "variant": "sDrive18d M Sport", "price": 5250000.0, "fuel": "diesel"},
    "bmw": {"mfg": "BMW", "model": "3 Series Gran Limousine", "variant": "330Li M Sport", "price": 6060000.0, "fuel": "petrol"},
    "mercedes c class": {"mfg": "Mercedes-Benz", "model": "C-Class", "variant": "C 200", "price": 6185000.0, "fuel": "petrol"},
    "c class": {"mfg": "Mercedes-Benz", "model": "C-Class", "variant": "C 200", "price": 6185000.0, "fuel": "petrol"},
    "mercedes": {"mfg": "Mercedes-Benz", "model": "C-Class", "variant": "C 200", "price": 6185000.0, "fuel": "petrol"},
    "audi a4": {"mfg": "Audi", "model": "A4", "variant": "Technology 40 TFSI", "price": 5185000.0, "fuel": "petrol"},
    "audi": {"mfg": "Audi", "model": "A4", "variant": "Technology 40 TFSI", "price": 5185000.0, "fuel": "petrol"},
    "audi q3": {"mfg": "Audi", "model": "Q3", "variant": "Technology 40 TFSI Quattro", "price": 5300000.0, "fuel": "petrol"},
    "volvo xc60": {"mfg": "Volvo", "model": "XC60", "variant": "B5 Ultimate", "price": 6890000.0, "fuel": "petrol"}
}

def format_inr(amount: float) -> str:
    """Formats float into standard Indian Rupee notation e.g. ₹12,34,567."""
    s = f"{int(round(amount))}"
    if len(s) <= 3:
        return f"₹{s}"
    last_three = s[-3:]
    other_digits = s[:-3]
    chunks = []
    while len(other_digits) > 2:
        chunks.insert(0, other_digits[-2:])
        other_digits = other_digits[:-2]
    if other_digits:
        chunks.insert(0, other_digits)
    return f"₹{','.join(chunks)},{last_three}"

class PricingEngine:
    """Production Pricing & Loan Quotation Service."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def generate_quote(self, req: PricingQuoteRequest) -> PricingQuoteResponse:
        # 1. Resolve Location (City & State)
        city_name, state_code, scope_desc = normalize_city_and_state(req.city, req.stateCode)

        # 2. Resolve Vehicle & Ex-Showroom Price
        ex_price = req.exShowroomPrice
        mfg = req.manufacturer or "Automobile"
        model_name = req.model or "Vehicle"
        variant_name = req.variant or "Standard Variant"
        fuel = (req.fuelType or "petrol").lower()
        is_estimated = False

        # Attempt to lookup in baseline catalog if price is missing
        if ex_price is None or ex_price <= 0:
            query_key = (req.model or "").lower().strip()
            matched = False
            for k, data in BASELINE_EX_SHOWROOM_PRICES.items():
                if k in query_key or k in (req.variant or "").lower():
                    mfg = data["mfg"]
                    model_name = data["model"]
                    variant_name = data["variant"]
                    ex_price = data["price"]
                    fuel = data["fuel"]
                    is_estimated = True
                    matched = True
                    break
            
            if not matched:
                raise ValueError(
                    f"Ex-showroom price is required for vehicle '{model_name}'. "
                    f"Please provide an exShowroomPrice or choose from known catalog models: {list(BASELINE_EX_SHOWROOM_PRICES.keys())}."
                )

        # 3. Calculate RTO Tax & Cess
        rto_res = calculate_state_rto_tax(
            state_code=state_code,
            ex_showroom_price=ex_price,
            fuel_type=fuel
        )

        # 4. Calculate Insurance
        ins_res = calculate_estimated_insurance(
            ex_showroom_price=ex_price,
            fuel_type=fuel,
            include_zero_dep=req.includeZeroDep
        )

        # 5. Calculate Fees & TCS
        fees_res = calculate_statutory_and_dealer_fees(
            ex_showroom_price=ex_price,
            include_dealer_handling=req.includeDealerHandling
        )

        # 6. Sum On-Road Price
        on_road_total = round(
            ex_price +
            rto_res["total_rto_tax_and_fees"] +
            ins_res["total_insurance_estimate"] +
            fees_res["total_other_charges"],
            2
        )

        # 7. Calculate Multi-Tenure EMI (3, 5, 7 Years)
        emi_calc = calculate_multi_tenure_emi_options(
            on_road_price=on_road_total,
            down_payment=req.downPayment,
            down_payment_pct=req.downPaymentPct,
            annual_interest_rate=req.annualInterestRate,
            tenure_years_list=req.tenuresYears
        )

        emi_items = [
            EMIOptionItem(
                tenureYears=e["tenure_years"],
                tenureMonths=e["tenure_months"],
                monthlyEmi=e["monthly_emi"],
                loanPrincipal=e["loan_principal"],
                totalInterest=e["total_interest"],
                totalPayable=e["total_payable"]
            )
            for e in emi_calc["emi_options"]
        ]

        # 8. Build Assumptions & Disclaimers
        assumptions = [
            f"State RTO tax calculated at {rto_res['tax_rate_pct']}% under {rto_res['state_name']} Motor Vehicle Rules ({rto_res['slab_description']}).",
            f"Comprehensive insurance includes 1-Year Own Damage + 3-Year Third Party liability (Zero Dep: {'Yes' if req.includeZeroDep else 'No'}).",
            f"TCS @ 1% applied: {'Yes (₹' + str(fees_res['tcs_amount']) + ')' if fees_res['tcs_applicable'] else 'No (Ex-showroom <= ₹10 Lakh)'}.",
            f"EMI loan calculation based on {req.annualInterestRate}% annual interest rate and down payment of {format_inr(emi_calc['down_payment'])} ({emi_calc['down_payment_pct']}%)."
        ]

        disclaimer = (
            f"All prices and EMI amounts shown are estimated calculations for {city_name}, {rto_res['state_name']}. "
            "Actual on-road price may vary depending on exact dealer delivery charges, optional accessories, "
            "municipal entry taxes, and prevailing bank interest rates."
        )

        # 9. Formatted Markdown Summary Table
        summary_md = f"""## 🚗 On-Road Price & EMI Breakdown: {mfg} {model_name} ({variant_name})
**Location:** {city_name}, {rto_res['state_name']} (State Code: `{state_code}`) | **Fuel Type:** {fuel.title()}

### 💰 Itemized Price Breakdown
| Component | Amount (INR) | Mandatory / Details |
| :--- | :---: | :--- |
| **Ex-Showroom Price** | **{format_inr(ex_price)}** | Base Vehicle Price |
| **State RTO Tax** | {format_inr(rto_res['base_rto_tax'])} | {rto_res['slab_description']} |
| **Road Safety Cess & Reg Fee** | {format_inr(rto_res['road_safety_cess'] + rto_res['registration_fee'] + rto_res['smart_card_fee'])} | State Cess + Smart Card |
| **Comprehensive Insurance (1+3 Yr)** | {format_inr(ins_res['total_insurance_estimate'])} | IDV: {format_inr(ins_res['idv'])} (18% GST Incl.) |
| **TCS (Tax Collected at Source)** | {format_inr(fees_res['tcs_amount'])} | {'1% under Sec 206C(1F)' if fees_res['tcs_applicable'] else '₹0 (Price <= ₹10L)'} |
| **FASTag Issuance** | {format_inr(fees_res['fastag_amount'])} | Security Deposit + Tag Fee |
| **HSRP & Portal Charges** | {format_inr(fees_res['hsrp_and_portal_fees'])} | Laser Security Number Plate |
| **Total Estimated On-Road Price** | **{format_inr(on_road_total)}** | **Estimated On-Road in {city_name}** |

### 💳 Loan Financing & Monthly EMI Options (Bank Interest: {req.annualInterestRate}%)
*Down Payment:* **{format_inr(emi_calc['down_payment'])}** ({emi_calc['down_payment_pct']}%) | *Loan Principal:* **{format_inr(emi_calc['loan_principal'])}**

| Loan Tenure | Monthly EMI | Total Interest Payable | Total Amount Paid |
| :---: | :---: | :---: | :---: |
"""
        for opt in emi_items:
            summary_md += f"| **{opt.tenureYears} Years ({opt.tenureMonths} Mos)** | **{format_inr(opt.monthlyEmi)}/mo** | {format_inr(opt.totalInterest)} | {format_inr(opt.totalPayable)} |\n"

        summary_md += f"\n> ℹ️ *Disclaimer: {disclaimer}*"

        return PricingQuoteResponse(
            location=LocationInfo(
                city=city_name,
                stateCode=state_code,
                stateName=rto_res["state_name"],
                calculationScope=scope_desc
            ),
            vehicle=VehicleInfo(
                manufacturer=mfg,
                model=model_name,
                variant=variant_name,
                fuelType=fuel,
                isEstimatedPrice=is_estimated
            ),
            priceBreakdown=PriceBreakdown(
                exShowroomPrice=ex_price,
                rtoTax=rto_res["base_rto_tax"],
                rtoRoadSafetyCess=rto_res["road_safety_cess"],
                registrationAndSmartCardFee=rto_res["registration_fee"] + rto_res["smart_card_fee"],
                insurance=ins_res["total_insurance_estimate"],
                tcs=fees_res["tcs_amount"],
                fastag=fees_res["fastag_amount"],
                hsrpAndPortalFees=fees_res["hsrp_and_portal_fees"],
                dealerHandlingCharges=fees_res["dealer_handling_charges"],
                hsrpOrRegistration=rto_res["registration_fee"] + rto_res["smart_card_fee"] + fees_res["hsrp_and_portal_fees"],
                cessAndOtherFees=rto_res["road_safety_cess"],
                dealerHandling=fees_res["dealer_handling_charges"],
                onRoadPrice=on_road_total
            ),
            emiOptions=emi_items,
            assumptions=assumptions,
            disclaimer=disclaimer,
            formattedSummary=summary_md
        )
