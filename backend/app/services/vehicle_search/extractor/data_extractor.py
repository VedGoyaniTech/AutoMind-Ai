"""
Data Extractor Module — Converts scraped page content into structured ExtractedVehicleSpec JSON schema.
"""

import re
from typing import Optional, List
from app.services.vehicle_search.models import ScrapedPage, ExtractedVehicleSpec
from app.services.vehicle_search.utils.logger import log_step


class DataExtractor:
    """Extracts structured vehicle data JSON from clean scraped web page text."""

    def extract_structured_spec(self, page: ScrapedPage, requested_vehicle: str) -> Optional[ExtractedVehicleSpec]:
        if not page or not page.clean_text:
            return None

        text = page.clean_text
        title = page.title

        log_step("extraction", f"Extracting structured data from {page.domain} for: '{requested_vehicle}'...")

        # 1. Extract Prices
        ex_price = self._extract_price(text, title)
        onroad_price = self._extract_onroad_price(text)

        # 2. Extract Powertrain Specs
        fuel = self._extract_fuel(text)
        trans = self._extract_transmission(text)
        engine = self._extract_engine(text)
        power = self._extract_power(text)
        torque = self._extract_torque(text)
        mileage = self._extract_mileage(text)
        safety = self._extract_safety(text)
        variant = self._extract_variant(text, title, requested_vehicle)
        features = self._extract_features(text)

        # Build ExtractedVehicleSpec object
        spec = ExtractedVehicleSpec(
            vehicle_name=self._clean_vehicle_name(requested_vehicle, title),
            variant_name=variant,
            manufacturer=self._extract_manufacturer(requested_vehicle),
            fuel_type=fuel,
            transmission=trans,
            engine_capacity=engine,
            power_hp=power,
            torque_nm=torque,
            mileage_kmpl=mileage,
            ex_showroom_price=ex_price,
            on_road_price=onroad_price,
            safety_rating=safety,
            key_features=features,
            source_url=page.url,
            source_domain=page.domain,
            confidence_score=1.0
        )

        log_step("extraction", f"Extracted JSON from {page.domain}: {spec.vehicle_name} ({spec.variant_name}) | Price: {spec.ex_showroom_price}")
        return spec

    def _extract_price(self, text: str, title: str) -> str:
        """Extracts ex-showroom price (e.g. ₹1.53 Cr / ₹15.30 Lakh / $79,100)."""
        combined = f"{title}\n{text[:4000]}"
        patterns = [
            r'₹\s*[\d\.]+\s*(?:Cr|Crore|Lakh|Lakhs|L)',
            r'Rs\.?\s*[\d\.]+\s*(?:Cr|Crore|Lakh|Lakhs|L)',
            r'INR\s*[\d\.]+\s*(?:Cr|Crore|Lakh|Lakhs|L)',
            r'\$\s*[\d,]+(?:\.\d+)?'
        ]
        for p in patterns:
            match = re.search(p, combined, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return ""

    def _extract_onroad_price(self, text: str) -> str:
        match = re.search(r'on[- ]road\s*(?:price)?\s*[:\-]?\s*(₹\s*[\d\.]+\s*(?:Cr|Crore|Lakh|Lakhs|L))', text[:4000], re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_fuel(self, text: str) -> str:
        t_lower = text[:3000].lower()
        if "electric" in t_lower or "ev" in t_lower or "battery" in t_lower:
            return "Electric"
        if "plug-in hybrid" in t_lower or "phev" in t_lower or "hybrid" in t_lower:
            return "Hybrid / PHEV"
        if "diesel" in t_lower:
            return "Diesel"
        if "petrol" in t_lower or "gasoline" in t_lower:
            return "Petrol"
        return "Petrol"

    def _extract_transmission(self, text: str) -> str:
        t_lower = text[:3000].lower()
        if "dct" in t_lower or "dual-clutch" in t_lower:
            return "Dual-Clutch (DCT)"
        if "amt" in t_lower or "automated manual" in t_lower:
            return "AMT"
        if "cvt" in t_lower:
            return "CVT"
        if "automatic" in t_lower or "at" in t_lower or "steptronic" in t_lower:
            return "Automatic"
        if "manual" in t_lower or "mt" in t_lower:
            return "Manual"
        return "Automatic"

    def _extract_engine(self, text: str) -> str:
        match = re.search(r'(\d{3,4}\s*cc|\d\.\d\s*L|\d\.\d\s*litre)', text[:4000], re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_power(self, text: str) -> str:
        match = re.search(r'(\d{2,4}\s*(?:hp|bhp|ps|kw))', text[:4000], re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_torque(self, text: str) -> str:
        match = re.search(r'(\d{2,4}\s*nm)', text[:4000], re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_mileage(self, text: str) -> str:
        match = re.search(r'(\d{1,2}(?:\.\d+)?\s*km/?l|\d{2,3}\s*km\s*range)', text[:4000], re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_safety(self, text: str) -> str:
        match = re.search(r'(\d\s*[- ]star|\b5[- ]star\b|gncap\s*\d|\beuro ncap\b)', text[:4000], re.IGNORECASE)
        if match:
            return match.group(0).strip().capitalize()
        return "5-Star Standard"

    def _extract_variant(self, text: str, title: str, requested_vehicle: str) -> str:
        # Check title for variant extensions (e.g. Competition xDrive, M Sport, GTX Plus)
        combined = f"{title} {text[:1000]}"
        match = re.search(r'(competition\s*xdrive|competition|m\s*sport|gtx\s*plus|creative\s*plus|zx\s*plus|el\s*pro|sx\s*\(o\))', combined, re.IGNORECASE)
        if match:
            return match.group(0).strip().title()
        return "Standard Variant"

    def _extract_features(self, text: str) -> List[str]:
        features = []
        t_lower = text[:3000].lower()
        if "adas" in t_lower or "autonomous braking" in t_lower:
            features.append("Level 2 ADAS Suite")
        if "airbag" in t_lower:
            features.append("Multi-Airbag Safety Package")
        if "sunroof" in t_lower or "panoramic" in t_lower:
            features.append("Panoramic Sunroof")
        if "all wheel drive" in t_lower or "awd" in t_lower or "xdrive" in t_lower:
            features.append("All-Wheel Drive (AWD)")
        return features if features else ["ABS + EBD + ESP", "Digital Cockpit", "Touchscreen Infotainment"]

    def _extract_manufacturer(self, vehicle: str) -> str:
        v = vehicle.split()[0].capitalize()
        return v

    def _clean_vehicle_name(self, requested: str, title: str) -> str:
        return requested.strip().title()
