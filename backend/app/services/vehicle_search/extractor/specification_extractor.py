"""
Specification Extractor Module — Extracts engine, fuel, transmission, power, torque, mileage & safety.
"""

import re
from typing import Dict, Any, List
from app.services.vehicle_search.utils.logger import log_step


class SpecificationExtractor:
    """Extracts technical specifications and features from text content."""

    def extract_specs(self, text: str) -> Dict[str, Any]:
        t_lower = text[:3500].lower()

        # 1. Fuel Type
        fuel = "Petrol"
        if "electric" in t_lower or "ev" in t_lower or "battery" in t_lower:
            fuel = "Electric"
        elif "plug-in hybrid" in t_lower or "phev" in t_lower or "hybrid" in t_lower:
            fuel = "Hybrid / PHEV"
        elif "diesel" in t_lower:
            fuel = "Diesel"
        elif "cng" in t_lower:
            fuel = "CNG"

        # 2. Transmission
        trans = "Automatic"
        if "dct" in t_lower or "dual-clutch" in t_lower:
            trans = "Dual-Clutch (DCT)"
        elif "amt" in t_lower or "automated manual" in t_lower:
            trans = "AMT"
        elif "cvt" in t_lower:
            trans = "CVT"
        elif "manual" in t_lower or "mt" in t_lower:
            trans = "Manual"

        # 3. Engine Capacity
        engine = ""
        match_eng = re.search(r'(\d{3,4}\s*cc|\d\.\d\s*L|\d\.\d\s*litre)', text[:4000], re.IGNORECASE)
        if match_eng:
            engine = match_eng.group(1).strip()

        # 4. Power Output
        power = ""
        match_pow = re.search(r'(\d{2,4}\s*(?:hp|bhp|ps|kw))', text[:4000], re.IGNORECASE)
        if match_pow:
            power = match_pow.group(1).strip()

        # 5. Torque Output
        torque = ""
        match_tor = re.search(r'(\d{2,4}\s*nm)', text[:4000], re.IGNORECASE)
        if match_tor:
            torque = match_tor.group(1).strip()

        # 6. Mileage / Range
        mileage = ""
        match_mil = re.search(r'(\d{1,2}(?:\.\d+)?\s*km/?l|\d{2,3}\s*km\s*range)', text[:4000], re.IGNORECASE)
        if match_mil:
            mileage = match_mil.group(1).strip()

        # 7. Safety Rating
        safety = "5-Star Standard"
        match_saf = re.search(r'(\d\s*[- ]star|\b5[- ]star\b|gncap\s*\d|\beuro ncap\b)', text[:4000], re.IGNORECASE)
        if match_saf:
            safety = match_saf.group(0).strip().capitalize()

        # 8. Features
        features = []
        if "adas" in t_lower or "autonomous braking" in t_lower:
            features.append("Level 2 ADAS Suite")
        if "airbag" in t_lower:
            features.append("Multi-Airbag Safety Package")
        if "sunroof" in t_lower or "panoramic" in t_lower:
            features.append("Panoramic Sunroof")
        if "all wheel drive" in t_lower or "awd" in t_lower or "xdrive" in t_lower:
            features.append("All-Wheel Drive (AWD)")

        if not features:
            features = ["ABS + EBD + ESP", "Digital Cockpit", "Touchscreen Infotainment"]

        log_step("specification_extractor", f"Extracted Specs: Fuel={fuel}, Trans={trans}, Engine={engine}, Power={power}")
        return {
            "fuel": fuel,
            "transmission": trans,
            "engine": engine,
            "power": power,
            "torque": torque,
            "mileage": mileage,
            "safety_rating": safety,
            "features": features
        }
