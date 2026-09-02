from typing import Dict, Any

class DataNormalizer:
    """Normalizes automotive dataset values (strings, prices, fuel types, transmissions)."""

    FUEL_MAP = {
        "petrol": "Petrol",
        "gasoline": "Petrol",
        "diesel": "Diesel",
        "ev": "EV",
        "electric": "EV",
        "bev": "EV",
        "hybrid": "Hybrid",
        "phev": "Hybrid",
        "cng": "CNG"
    }

    TRANSMISSION_MAP = {
        "manual": "Manual",
        "mt": "Manual",
        "automatic": "Automatic",
        "auto": "Automatic",
        "at": "Automatic",
        "dct": "DCT",
        "cvt": "CVT",
        "amt": "AMT"
    }

    @classmethod
    def normalize_record(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        norm = dict(raw)

        # Title Case names
        norm["manufacturer"] = str(raw.get("manufacturer", "Generic")).strip().title()
        norm["model"] = str(raw.get("model", "Model")).strip().title()
        norm["variant"] = str(raw.get("variant", "Standard")).strip()
        norm["body_type"] = str(raw.get("body_type", "SUV")).strip().upper()

        # Fuel Normalization
        raw_fuel = str(raw.get("fuel_type", "Petrol")).strip().lower()
        norm["fuel_type"] = cls.FUEL_MAP.get(raw_fuel, "Petrol")

        # Transmission Normalization
        raw_trans = str(raw.get("transmission", "Manual")).strip().lower()
        norm["transmission"] = cls.TRANSMISSION_MAP.get(raw_trans, "Manual")

        # Price parsing
        price = float(raw.get("ex_showroom_price", 1000000))
        norm["ex_showroom_price"] = price
        norm["estimated_on_road_price"] = float(raw.get("estimated_on_road_price", price * 1.15))

        # Year
        norm["model_year"] = int(raw.get("model_year", 2024))

        # Integers & Floats
        norm["seating_capacity"] = int(raw.get("seating_capacity", 5))
        norm["airbags"] = int(raw.get("airbags", 2))
        
        if raw.get("combined_mileage"):
            norm["combined_mileage"] = float(raw.get("combined_mileage"))
        if raw.get("safety_rating"):
            norm["safety_rating"] = float(raw.get("safety_rating"))

        return norm
