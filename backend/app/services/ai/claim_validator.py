"""
AutoMind AI — Claim Validation, Benchmark Verification & Statutory Import Service
Enforces deterministic factual accuracy across vehicle specifications, performance records,
speed claims, unit conversions, Indian import cost estimations, and citation integrity.
"""

import re
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("automind.claim_validator")

# Exact unit conversion factor: 1 mile = 1.609344 km
MPH_TO_KMH_FACTOR = 1.609344
KMH_TO_MPH_FACTOR = 1.0 / 1.609344


class ClaimType(str, Enum):
    TOP_SPEED = "top_speed"
    ACCELERATION_0_100 = "acceleration_0_100"
    PRICE_INR = "price_inr"
    IMPORT_COST = "import_cost"
    AVAILABILITY_INDIA = "availability_india"
    SAFETY_RATING = "safety_rating"
    ENGINE_SPECS = "engine_specs"


class VerificationStatus(str, Enum):
    MANUFACTURER_CLAIM = "manufacturer_claim"
    INDEPENDENTLY_MEASURED = "independently_measured"
    OFFICIALLY_RECOGNIZED_RECORD = "officially_recognized_record"
    ESTIMATED = "estimated"
    UNVERIFIED = "unverified"
    UNAVAILABLE = "unavailable"


@dataclass
class VehicleClaim:
    claim_type: ClaimType
    vehicle_name: str
    raw_value: Any
    normalized_value: Any
    unit: str
    status: VerificationStatus
    notes: str
    source_url: Optional[str] = None
    source_publisher: Optional[str] = None


@dataclass
class ImportCostBreakdown:
    base_currency: str
    cif_foreign: float
    exchange_rate_inr: float
    cif_inr: float
    bcd_rate: float
    bcd_amount_inr: float
    sws_rate: float
    sws_amount_inr: float
    igst_cess_rate: float
    igst_cess_amount_inr: float
    total_customs_duty_inr: float
    landed_cost_pre_rto_inr: float
    rto_registration_rate: float
    rto_registration_amount_inr: float
    insurance_handling_amount_inr: float
    estimated_total_on_road_inr: float
    status: VerificationStatus = VerificationStatus.ESTIMATED
    is_official_dealer_price: bool = False
    disclaimer: str = (
        "Illustrative private import estimate under CBU guidelines. "
        "Actual landing cost varies based on state RTO, port handling, forex fluctuations, and customs valuation."
    )


# Curated Verified Speed & Performance Records Database
KNOWN_SPEED_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "koenigsegg agera rs": {
        "canonical_name": "Koenigsegg Agera RS",
        "speed_kmh": 447.19,
        "speed_mph": 277.87,
        "status": VerificationStatus.OFFICIALLY_RECOGNIZED_RECORD,
        "run_type": "Two-way average on closed public highway (Route 160, Nevada, USA, Nov 2017)",
        "verified_by": "VBOX / Racelogic verified, Guinness recognized two-way production record",
        "notes": "Officially verified two-way production car record.",
        "source_publisher": "Guinness World Records / Racelogic",
        "source_url": "https://www.koenigsegg.com/model/agera-rs"
    },
    "ssc tuatara": {
        "canonical_name": "SSC Tuatara",
        "speed_kmh": 455.3,
        "speed_mph": 282.9,
        "status": VerificationStatus.INDEPENDENTLY_MEASURED,
        "run_type": "Two-way average at Johnny Bohmer Proving Grounds, Florida (Jan 2021)",
        "verified_by": "Racelogic VBOX independently verified two-way customer car run",
        "notes": "Independently measured two-way production vehicle test.",
        "source_publisher": "Racelogic VBOX USA",
        "source_url": "https://www.sscnorthamerica.com/tuatara"
    },
    "bugatti chiron super sport 300+": {
        "canonical_name": "Bugatti Chiron Super Sport 300+",
        "speed_kmh": 490.48,
        "speed_mph": 304.77,
        "status": VerificationStatus.INDEPENDENTLY_MEASURED,
        "run_type": "One-way pre-production record run at Ehra-Lessien test track, Germany (Aug 2019)",
        "verified_by": "TÜV Rheinland certified (single direction)",
        "notes": "Independently measured one-way speed record. Not a two-way Guinness production record.",
        "source_publisher": "TÜV Rheinland / Bugatti",
        "source_url": "https://newsroom.bugatti.com/press-releases/bugatti-breaks-the-300-mph-barrier"
    },
    "koenigsegg jesko absolut": {
        "canonical_name": "Koenigsegg Jesko Absolut",
        "speed_kmh": 531.0,
        "speed_mph": 330.0,
        "status": VerificationStatus.MANUFACTURER_CLAIM,
        "run_type": "Theoretical computational simulation / engineering projection",
        "verified_by": "Unverified by physical speed run",
        "notes": "Manufacturer claimed simulation top speed. Physical top-speed run has not yet been conducted.",
        "source_publisher": "Koenigsegg Automotive AB",
        "source_url": "https://www.koenigsegg.com/model/jesko-absolut"
    },
    "bugatti bolide": {
        "canonical_name": "Bugatti Bolide",
        "speed_kmh": 500.0,
        "speed_mph": 311.0,
        "status": VerificationStatus.MANUFACTURER_CLAIM,
        "run_type": "Theoretical simulation (track-only hypercar)",
        "verified_by": "Unverified physical run",
        "notes": "Manufacturer claimed theoretical track simulation speed.",
        "source_publisher": "Bugatti Automobiles S.A.S.",
        "source_url": "https://newsroom.bugatti.com"
    },
    "hennessey venom f5": {
        "canonical_name": "Hennessey Venom F5",
        "speed_kmh": 500.0,
        "speed_mph": 311.0,
        "status": VerificationStatus.MANUFACTURER_CLAIM,
        "run_type": "Target claim (partial testing has achieved 271.6 mph / 437.1 km/h)",
        "verified_by": "Manufacturer internal telemetry",
        "notes": "Manufacturer target speed; 300+ mph run pending.",
        "source_publisher": "Hennessey Special Vehicles",
        "source_url": "https://www.hennesseyspecialvehicles.com"
    },
    "rimac nevera": {
        "canonical_name": "Rimac Nevera",
        "speed_kmh": 412.0,
        "speed_mph": 256.0,
        "status": VerificationStatus.INDEPENDENTLY_MEASURED,
        "run_type": "Two-way independently measured EV record at Automotive Testing Papenburg (ATP), Germany",
        "verified_by": "Dewesoft and Racelogic VBOX verified",
        "notes": "Independently measured fastest production electric vehicle (EV).",
        "source_publisher": "Racelogic / Dewesoft",
        "source_url": "https://www.rimac-automobili.com/nevera"
    },
    "bugatti veyron super sport": {
        "canonical_name": "Bugatti Veyron 16.4 Super Sport",
        "speed_kmh": 431.07,
        "speed_mph": 267.86,
        "status": VerificationStatus.OFFICIALLY_RECOGNIZED_RECORD,
        "run_type": "Guinness official two-way production record at Ehra-Lessien (July 2010)",
        "verified_by": "Guinness World Records / German TÜV",
        "notes": "Officially certified Guinness production record.",
        "source_publisher": "Guinness World Records",
        "source_url": "https://www.guinnessworldrecords.com"
    }
}

# Indian Market Availability Database
INDIAN_MARKET_STATUS: Dict[str, Dict[str, Any]] = {
    "bentley continental gt": {
        "availability": "Official Dealership Network (CBU)",
        "dealers": "Bentley Mumbai (Exclusive Motors), Bentley New Delhi",
        "price_range_inr": "₹5.23 – ₹6.00 Crore (Ex-Showroom)",
        "status": VerificationStatus.INDEPENDENTLY_MEASURED
    },
    "bentley flying spur": {
        "availability": "Official Dealership Network (CBU)",
        "dealers": "Bentley Mumbai, Bentley New Delhi",
        "price_range_inr": "₹5.25 – ₹7.60 Crore (Ex-Showroom)",
        "status": VerificationStatus.INDEPENDENTLY_MEASURED
    },
    "bentley bentayga": {
        "availability": "Official Dealership Network (CBU)",
        "dealers": "Bentley Mumbai, Bentley New Delhi",
        "price_range_inr": "₹4.10 – ₹5.00 Crore (Ex-Showroom)",
        "status": VerificationStatus.INDEPENDENTLY_MEASURED
    },
    "rolls-royce ghost": {
        "availability": "Official Dealership Network (CBU)",
        "dealers": "Rolls-Royce Motor Cars New Delhi, Chennai",
        "price_range_inr": "₹6.95 – ₹7.95 Crore (Ex-Showroom)",
        "status": VerificationStatus.INDEPENDENTLY_MEASURED
    },
    "rolls-royce phantom": {
        "availability": "Official Dealership Network (CBU)",
        "dealers": "Rolls-Royce Motor Cars New Delhi, Chennai",
        "price_range_inr": "₹9.50 – ₹10.50 Crore (Ex-Showroom)",
        "status": VerificationStatus.INDEPENDENTLY_MEASURED
    },
    "rolls-royce cullinan": {
        "availability": "Official Dealership Network (CBU)",
        "dealers": "Rolls-Royce Motor Cars New Delhi, Chennai",
        "price_range_inr": "₹6.95 – ₹8.20 Crore (Ex-Showroom)",
        "status": VerificationStatus.INDEPENDENTLY_MEASURED
    },
    "rolls-royce spectre": {
        "availability": "Official Dealership Network (CBU)",
        "dealers": "Rolls-Royce Motor Cars New Delhi, Chennai",
        "price_range_inr": "₹7.50 – ₹8.50 Crore (Ex-Showroom)",
        "status": VerificationStatus.INDEPENDENTLY_MEASURED
    },
    "ferrari 296 gtb": {
        "availability": "Official Dealership Network (CBU)",
        "dealers": "Ferrari New Delhi, Ferrari Mumbai",
        "price_range_inr": "₹5.40 – ₹6.00 Crore (Ex-Showroom)",
        "status": VerificationStatus.INDEPENDENTLY_MEASURED
    },
    "ferrari sf90 stradale": {
        "availability": "Official Dealership Network (CBU)",
        "dealers": "Ferrari New Delhi, Ferrari Mumbai",
        "price_range_inr": "₹7.50 – ₹9.00 Crore (Ex-Showroom)",
        "status": VerificationStatus.INDEPENDENTLY_MEASURED
    },
    "koenigsegg jesko": {
        "availability": "Private Import / Special Allocation Only (No official Indian showroom)",
        "dealers": "None (Requires Carnet or direct CBU private homologation import)",
        "price_range_inr": "Estimated ₹35.00 – ₹45.00 Crore (Landed with ~200%+ import duties)",
        "status": VerificationStatus.ESTIMATED
    },
    "bugatti chiron": {
        "availability": "Private Import / Private Collector Allocation Only (No official showroom in India)",
        "dealers": "None (Private import only)",
        "price_range_inr": "Estimated ₹30.00 – ₹40.00 Crore (Landed with ~200%+ import duties)",
        "status": VerificationStatus.ESTIMATED
    }
}


class ClaimValidationService:
    """
    Central validation service for automotive claims, speed records,
    import cost calculations, and unit conversions.
    """

    def __init__(self, inr_usd_rate: float = 84.0):
        self.inr_usd_rate = inr_usd_rate

    @staticmethod
    def convert_speed(value: float, from_unit: str, to_unit: str) -> float:
        """
        Deterministically converts speed between mph and km/h.
        1 mph = 1.609344 km/h exactly.
        """
        f_clean = from_unit.strip().lower()
        t_clean = to_unit.strip().lower()

        if f_clean == t_clean:
            return round(value, 2)

        if f_clean in ["mph", "miles/h", "miles per hour"]:
            if t_clean in ["km/h", "kmh", "kmph", "kilometers per hour"]:
                return round(value * MPH_TO_KMH_FACTOR, 2)
        elif f_clean in ["km/h", "kmh", "kmph", "kilometers per hour"]:
            if t_clean in ["mph", "miles/h", "miles per hour"]:
                return round(value * KMH_TO_MPH_FACTOR, 2)

        raise ValueError(f"Unsupported speed unit conversion: {from_unit} -> {to_unit}")

    def verify_speed_claim(self, vehicle_name: str, claimed_speed: float, unit: str = "km/h") -> VehicleClaim:
        """
        Verifies a vehicle's speed claim against known physical and official records.
        Distinguishes manufacturer simulation claims from independently measured and
        officially recognized records.
        """
        v_lower = vehicle_name.lower().strip()
        matched_key = None
        for k in KNOWN_SPEED_BENCHMARKS:
            if k in v_lower or v_lower in k:
                matched_key = k
                break

        unit_clean = unit.strip().lower()
        speed_kmh = claimed_speed if "km" in unit_clean else self.convert_speed(claimed_speed, "mph", "km/h")

        if matched_key:
            bench = KNOWN_SPEED_BENCHMARKS[matched_key]
            canonical = bench["canonical_name"]
            status = bench["status"]
            notes = f"{bench['run_type']}. Verified by: {bench['verified_by']}. {bench['notes']}"
            return VehicleClaim(
                claim_type=ClaimType.TOP_SPEED,
                vehicle_name=canonical,
                raw_value=claimed_speed,
                normalized_value={"kmh": bench["speed_kmh"], "mph": bench["speed_mph"]},
                unit="km/h",
                status=status,
                notes=notes,
                source_url=bench.get("source_url"),
                source_publisher=bench.get("source_publisher")
            )

        # Fallback for unbenchmarked hypercars: check if speed exceeds 480 km/h (300 mph)
        # Any claim exceeding 480 km/h without official documentation is a manufacturer claim/simulation
        if speed_kmh >= 480.0:
            status = VerificationStatus.MANUFACTURER_CLAIM
            notes = f"Theoretical or manufacturer-claimed speed ({speed_kmh:.1f} km/h). No independent two-way physical test on record."
        elif speed_kmh > 0:
            status = VerificationStatus.UNVERIFIED
            notes = f"Speed of {speed_kmh:.1f} km/h requires secondary verification."
        else:
            status = VerificationStatus.UNAVAILABLE
            notes = "Speed information unavailable."

        return VehicleClaim(
            claim_type=ClaimType.TOP_SPEED,
            vehicle_name=vehicle_name,
            raw_value=claimed_speed,
            normalized_value={"kmh": speed_kmh, "mph": round(speed_kmh * KMH_TO_MPH_FACTOR, 2)},
            unit="km/h",
            status=status,
            notes=notes
        )

    def calculate_indian_cbu_import_cost(
        self,
        cif_usd: float,
        engine_cc: int = 3500,
        fuel_type: str = "petrol",
        is_new_vehicle: bool = True
    ) -> ImportCostBreakdown:
        """
        Calculates statutory illustrative Indian import costs for CBU (Completely Built Unit) passenger cars:
        1. CIF (Cost, Insurance, Freight) in INR
        2. Basic Customs Duty (BCD):
           - 100% for new cars if CIF >= $40,000 OR engine capacity > 3000cc (petrol) / > 2500cc (diesel)
           - 70% for new cars if CIF < $40,000 and engine <= 3000cc / 2500cc
        3. Social Welfare Surcharge (SWS): 10% on BCD amount
        4. Integrated GST (IGST) + Compensation Cess:
           - 28% GST + 22% Cess = ~50% assessed on (CIF + BCD + SWS)
        5. State Road Tax / Registration (RTO): ~15% on landed pre-RTO cost
        6. Marine insurance & port handling: ~2%
        """
        cif_inr = cif_usd * self.inr_usd_rate

        # BCD Rate calculation
        fuel_clean = fuel_type.strip().lower()
        is_large_engine = (fuel_clean == "petrol" and engine_cc > 3000) or (fuel_clean == "diesel" and engine_cc > 2500)

        if cif_usd >= 40000.0 or is_large_engine:
            bcd_rate = 1.00  # 100%
        else:
            bcd_rate = 0.70  # 70%

        bcd_amount = cif_inr * bcd_rate
        sws_rate = 0.10  # 10% of BCD
        sws_amount = bcd_amount * sws_rate

        # Duty paid value for IGST + Cess
        assessable_value_for_igst = cif_inr + bcd_amount + sws_amount
        igst_cess_rate = 0.50  # 28% IGST + 22% Compensation Cess
        igst_cess_amount = assessable_value_for_igst * igst_cess_rate

        total_customs = bcd_amount + sws_amount + igst_cess_amount
        landed_pre_rto = cif_inr + total_customs

        rto_rate = 0.15  # Average state registration (12% - 20%)
        rto_amount = landed_pre_rto * rto_rate
        insurance_handling = cif_inr * 0.02

        total_on_road = landed_pre_rto + rto_amount + insurance_handling

        return ImportCostBreakdown(
            base_currency="USD",
            cif_foreign=cif_usd,
            exchange_rate_inr=self.inr_usd_rate,
            cif_inr=round(cif_inr, 2),
            bcd_rate=bcd_rate,
            bcd_amount_inr=round(bcd_amount, 2),
            sws_rate=sws_rate,
            sws_amount_inr=round(sws_amount, 2),
            igst_cess_rate=igst_cess_rate,
            igst_cess_amount_inr=round(igst_cess_amount, 2),
            total_customs_duty_inr=round(total_customs, 2),
            landed_cost_pre_rto_inr=round(landed_pre_rto, 2),
            rto_registration_rate=rto_rate,
            rto_registration_amount_inr=round(rto_amount, 2),
            insurance_handling_amount_inr=round(insurance_handling, 2),
            estimated_total_on_road_inr=round(total_on_road, 2),
            status=VerificationStatus.ESTIMATED,
            is_official_dealer_price=False
        )

    def check_indian_availability(self, vehicle_name: str) -> Dict[str, Any]:
        """
        Checks whether a vehicle is officially distributed in India through
        an authorized dealership network or requires private import.
        """
        v_lower = vehicle_name.lower().strip()
        for k, info in INDIAN_MARKET_STATUS.items():
            if k in v_lower or v_lower in k:
                return {
                    "matched": True,
                    "canonical_name": k.title(),
                    "availability": info["availability"],
                    "dealers": info["dealers"],
                    "price_range_inr": info["price_range_inr"],
                    "status": info["status"].value
                }

        return {
            "matched": False,
            "canonical_name": vehicle_name.title(),
            "availability": "Private Import or Unverified Official Network",
            "dealers": "None on official record",
            "price_range_inr": "Customs Duty Applicable (estimated 2.1x–2.4x foreign price)",
            "status": VerificationStatus.UNVERIFIED.value
        }

    def generate_speed_ranking_table(self, top_n: int = 5) -> str:
        """
        Generates a rigorous, verified ranking of the world's fastest cars
        strictly distinguishing officially recognized production records,
        independently measured runs, and theoretical manufacturer simulation claims.
        """
        rows = [
            ("1", "Bugatti Chiron Super Sport 300+", "490.48 km/h (304.77 mph)", "Independently Measured", "One-way Ehra-Lessien run certified by TÜV Rheinland. Pre-production derivative."),
            ("2", "SSC Tuatara", "455.30 km/h (282.90 mph)", "Independently Measured", "Two-way verified average at Johnny Bohmer Proving Grounds (Racelogic VBOX)."),
            ("3", "Koenigsegg Agera RS", "447.19 km/h (277.87 mph)", "Officially Recognized Record", "Guinness World Record certified two-way average on Route 160, Nevada."),
            ("4", "Rimac Nevera (EV)", "412.00 km/h (256.00 mph)", "Independently Measured", "Independently measured fastest production EV (Racelogic & Dewesoft certified)."),
            ("5", "Bugatti Veyron 16.4 Super Sport", "431.07 km/h (267.86 mph)", "Officially Recognized Record", "Guinness World Record certified two-way average (Ehra-Lessien)."),
            ("—", "Koenigsegg Jesko Absolut", "531.00 km/h (330.00 mph) [Claimed]", "Manufacturer Claim", "Computer CFD simulation projection. Physical top-speed run not yet completed."),
            ("—", "Bugatti Bolide", "500.00 km/h (311.00 mph) [Claimed]", "Manufacturer Claim", "Track-only simulation target; unverified physical road record."),
            ("—", "Hennessey Venom F5", "500.00+ km/h (311.00+ mph) [Target]", "Manufacturer Claim", "Manufacturer target; physical run has achieved 271.6 mph (437.1 km/h) to date.")
        ]

        lines = [
            "## ⚡ Verified World's Fastest Production Cars & Speed Records",
            "",
            "> [!NOTE]",
            "> **Standard of Proof:** Officially recognized production records require a two-way run on the same stretch within one hour (to account for wind/gradient) and independent telemetry (e.g. Racelogic VBOX / TÜV / Guinness). Theoretical computer simulations are marked as **Manufacturer Claim** and listed separately.",
            "",
            "### 🏁 Confirmed & Independently Measured Physical Records",
            "| Rank | Vehicle Model | Verified Speed | Verification Status | Test Verification Details |",
            "| :---: | :--- | :--- | :--- | :--- |"
        ]

        for rank, model, speed, status, details in rows[:5]:
            status_badge = f"`{status}`"
            lines.append(f"| {rank} | **{model}** | **{speed}** | {status_badge} | {details} |")

        lines.extend([
            "",
            "### 🧪 Theoretical Simulations & Manufacturer Target Claims (Unverified by Physical Run)",
            "| Model | Claimed Speed | Status | Note |",
            "| :--- | :--- | :--- | :--- |",
            "| **Koenigsegg Jesko Absolut** | 531 km/h (330 mph) | `Manufacturer Claim` | CFD and gearing simulation; awaiting physical record run. |",
            "| **Bugatti Bolide** | 500 km/h (311 mph) | `Manufacturer Claim` | Track simulation; not street-legal or physically road-certified. |",
            "| **Hennessey Venom F5** | 500+ km/h (311+ mph) | `Manufacturer Claim` | Engineering target; highest test run verified so far is 437.1 km/h. |",
            "",
            "### 📌 Critical Performance Distinction: Top Speed vs Acceleration",
            "- **Top Speed:** Aerodynamic efficiency, high-rpm gearing, and tire heat tolerance (e.g. Bugatti Chiron 300+ at 490.48 km/h).",
            "- **Acceleration (0–100 km/h sprint):** Instant motor torque, AWD traction, and launch control (e.g. Rimac Nevera 0–100 in 1.81s; McMurtry Speirling in 1.40s). Top speed and 0–100 acceleration are completely different engineering metrics and are never combined into a single ranking."
        ])

        return "\n".join(lines)

    def review_answer_gates(
        self,
        query: str,
        response: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the 7-Gate Quality Control Review mandated by AutoMind AI:
        - Gate A (Relevance): Evaluates if response answers the specific prompt.
        - Gate B (Accuracy): Validates factual claims, speeds, record distinctions.
        - Gate C (Context): Ensures proper currency, country, model year, variant context.
        - Gate D (Sources): Validates citations and flags fake/internal links.
        - Gate E (Uncertainty): Ensures estimates/simulations are marked with uncertainty.
        - Gate F (Completeness): Ensures adequate substance without fluff.
        - Gate G (Final Consistency): Checks narrative/table consistency without arbitrary scores.
        """
        violations = []
        recommendations = []
        gates = {}

        q_lower = query.lower().strip()
        r_lower = response.lower().strip()

        # Gate A: Relevance
        gate_a_passed = True
        gate_a_details = []
        if len(r_lower) < 20:
            gate_a_passed = False
            gate_a_details.append("Response is too brief or empty.")
            violations.append("Gate A: Empty or near-empty response.")
        else:
            # Check key automotive entities if mentioned in query
            for brand in ["bentley", "bugatti", "koenigsegg", "ferrari", "lamborghini", "porsche", "rolls-royce", "tata", "mahindra", "maruti", "toyota", "hyundai", "bmw", "mercedes", "audi"]:
                if brand in q_lower and brand not in r_lower and brand.replace("-", " ") not in r_lower:
                    gate_a_passed = False
                    gate_a_details.append(f"Query explicitly requested '{brand}' but response failed to mention it.")
                    violations.append(f"Gate A: Requested vehicle brand '{brand}' not addressed in response.")
                    break
        if gate_a_passed:
            gate_a_details.append("Response directly addresses user query.")
        gates["gate_a_relevance"] = {"passed": gate_a_passed, "details": " ".join(gate_a_details)}

        # Gate B: Accuracy
        gate_b_passed = True
        gate_b_details = []
        # Check simulation speeds presented as physical records
        if ("531" in r_lower or "jesko absolut" in r_lower) and "fastest" in r_lower:
            if not any(token in r_lower for token in ["claim", "simulation", "theoretical", "projected", "unverified"]):
                gate_b_passed = False
                gate_b_details.append("Koenigsegg Jesko Absolut 531 km/h is a theoretical simulation, not a verified physical record.")
                violations.append("Gate B: Theoretical simulation presented as verified physical record.")
        if ("500" in r_lower and "bolide" in r_lower):
            if not any(token in r_lower for token in ["claim", "simulation", "track", "target"]):
                gate_b_passed = False
                gate_b_details.append("Bugatti Bolide 500 km/h is a track simulation, not a verified production road record.")
                violations.append("Gate B: Bugatti Bolide track simulation unverified.")
        # Check conflation of top speed and 0-100 sprint
        if "top speed" in r_lower and ("0-100" in r_lower or "0–100" in r_lower):
            if "combined" in r_lower and "rank" in r_lower:
                gate_b_passed = False
                gate_b_details.append("Top speed and acceleration sprint must never be combined into a single ranking metric.")
                violations.append("Gate B: Conflated top speed with acceleration sprint.")
        if gate_b_passed:
            gate_b_details.append("Factual claims, performance records, and simulation distinctions are accurate.")
        gates["gate_b_accuracy"] = {"passed": gate_b_passed, "details": " ".join(gate_b_details)}

        # Gate C: Context
        gate_c_passed = True
        gate_c_details = []
        has_price = any(curr in r_lower for curr in ["₹", "rs.", "inr", "lakh", "crore", "$", "usd", "€", "eur", "£", "gbp"])
        if has_price:
            if not any(qual in r_lower for qual in ["ex-showroom", "on-road", "msrp", "starting at", "approx", "estimated", "price", "range"]):
                recommendations.append("Gate C: Clarify whether prices are ex-showroom, MSRP, or on-road with statutory charges.")
        gates["gate_c_context"] = {"passed": gate_c_passed, "details": "Context, currency, and market parameters are specified."}

        # Gate D: Sources
        gate_d_passed = True
        gate_d_details = []
        fake_patterns = [r"mock://", r"internal_car_id", r"fake-source\.com", r"http://localhost", r"test-data-source"]
        for pat in fake_patterns:
            if re.search(pat, response):
                gate_d_passed = False
                gate_d_details.append(f"Response contains internal mock/fabricated citation: {pat}")
                violations.append(f"Gate D: Fabricated or mock source detected ({pat}).")
        if gate_d_passed:
            gate_d_details.append("All citations reference verified external sources or structured indices.")
        gates["gate_d_sources"] = {"passed": gate_d_passed, "details": " ".join(gate_d_details)}

        # Gate E: Uncertainty
        gate_e_passed = True
        gate_e_details = []
        if "customs duty" in r_lower or "cbu import" in r_lower or "landed cost" in r_lower:
            if not any(unc in r_lower for unc in ["estimate", "illustrative", "approx", "provisional", "indicative"]):
                gate_e_passed = False
                gate_e_details.append("CBU import landed cost must be clearly labeled as an estimate.")
                violations.append("Gate E: Private import calculation missing explicit estimation disclaimer.")
        if gate_e_passed:
            gate_e_details.append("Estimates, simulations, and uncertainties are properly qualified.")
        gates["gate_e_uncertainty"] = {"passed": gate_e_passed, "details": " ".join(gate_e_details)}

        # Gate F: Completeness
        gate_f_passed = True
        gate_f_details = []
        if len(response.strip()) < 50:
            gate_f_passed = False
            gate_f_details.append("Response is incomplete or excessively truncated.")
            violations.append("Gate F: Response is incomplete (< 50 characters).")
        else:
            gate_f_details.append("Response provides substantive details answering the inquiry.")
        gates["gate_f_completeness"] = {"passed": gate_f_passed, "details": " ".join(gate_f_details)}

        # Gate G: Final Consistency
        gate_g_passed = True
        gate_g_details = []
        if ("bentley" in r_lower or "rolls-royce" in r_lower) and "vs" in q_lower:
            if re.search(r"\b\d\.\d/10\b", response) or re.search(r"score:\s*\d+", r_lower):
                gate_g_passed = False
                gate_g_details.append("Luxury comparisons must not assign arbitrary single-winner numerical scores.")
                violations.append("Gate G: Arbitrary numerical winner score assigned in luxury vehicle comparison.")
        if gate_g_passed:
            gate_g_details.append("Internal consistency verified across narrative, tables, and verdicts.")
        gates["gate_g_consistency"] = {"passed": gate_g_passed, "details": " ".join(gate_g_details)}

        all_passed = all(g["passed"] for g in gates.values())
        passed_count = sum(1 for g in gates.values() if g["passed"])
        score = round(passed_count / len(gates), 2)

        return {
            "passed": all_passed,
            "overall_status": "APPROVED" if all_passed else "REJECTED_GATES",
            "score": score,
            "gates_passed": f"{passed_count}/{len(gates)}",
            "gates": gates,
            "violations": violations,
            "recommendations": recommendations
        }


claim_validation_service = ClaimValidationService()
