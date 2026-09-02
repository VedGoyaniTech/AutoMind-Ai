import re
from typing import Dict, Any, List, Optional
from app.schemas.car import CarSearchFilter

class QueryAnalyzer:
    """Parses natural language car questions into structured constraints and search intents."""

    MANUFACTURERS = [
        "Tata", "Hyundai", "Kia", "Mahindra", "Maruti", "Toyota", 
        "Honda", "Volkswagen", "Skoda", "BMW", "Mercedes-Benz", "Audi", "MG"
    ]
    
    BODY_TYPES = ["SUV", "Sedan", "Hatchback", "MUV", "Coupe", "EV", "Cross-over"]
    FUEL_TYPES = ["Petrol", "Diesel", "EV", "Electric", "Hybrid", "CNG"]
    TRANSMISSIONS = ["Automatic", "Manual", "DCT", "CVT", "AMT"]

    def analyze(self, prompt: str) -> Dict[str, Any]:
        text = prompt.strip()
        lower = text.lower()

        # 1. Price constraint parsing
        price_max: Optional[float] = None
        price_min: Optional[float] = None

        lakh_match = re.search(r'(?:under|below|less than|within|upto|up to)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l)', lower)
        if lakh_match:
            price_max = float(lakh_match.group(1)) * 100000.0

        num_price_match = re.search(r'(?:under|below)\s*(?:₹|rs\.?|inr)?\s*(\d{6,8})', lower)
        if num_price_match:
            price_max = float(num_price_match.group(1))

        # 2. Airbags parsing
        airbags_min: Optional[int] = None
        airbag_match = re.search(r'(\d+)\s*airbags', lower)
        if airbag_match:
            airbags_min = int(airbag_match.group(1))

        # 3. Mileage parsing
        min_mileage: Optional[float] = None
        mileage_match = re.search(r'(?:mileage|fuel efficiency)\s*(?:above|greater than|>|more than)\s*(\d+(?:\.\d+)?)', lower)
        if not mileage_match:
            mileage_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:km/l|kmpl|kmpl)', lower)
        if mileage_match:
            min_mileage = float(mileage_match.group(1))

        # 4. Seating capacity
        seating_min: Optional[int] = None
        seater_match = re.search(r'(\d+)\s*seat', lower)
        if seater_match:
            seating_min = int(seater_match.group(1))
        elif "family of 5" in lower or "5 people" in lower:
            seating_min = 5
        elif "family of 7" in lower or "7 people" in lower:
            seating_min = 7

        # 5. Safety rating
        min_safety_rating: Optional[float] = None
        safety_match = re.search(r'(\d+)\s*star', lower)
        if safety_match:
            min_safety_rating = float(safety_match.group(1))
        elif "safest" in lower:
            min_safety_rating = 4.5

        # 6. Extract Manufacturer
        detected_manufacturer: Optional[str] = None
        for m in self.MANUFACTURERS:
            if m.lower() in lower:
                detected_manufacturer = m
                break

        # 7. Extract Body Type
        detected_body_type: Optional[str] = None
        for b in self.BODY_TYPES:
            if b.lower() in lower:
                detected_body_type = b
                break

        # 8. Extract Fuel Type
        detected_fuel: Optional[str] = None
        for f in self.FUEL_TYPES:
            if f.lower() in lower:
                if f.lower() in ["electric", "ev"]:
                    detected_fuel = "EV"
                else:
                    detected_fuel = f
                break

        # 9. Luxury & Supercar detection
        is_luxury = any(w in lower for w in ["luxury", "luxry", "luxurious", "premium", "exotic", "supercar", "expensive", "sports car"])
        if is_luxury and not price_min:
            price_min = 2500000.0

        # 10. Year Extraction (e.g. 2005, 2024, 2026, or "is saal" / "abhi")
        requested_year: Optional[int] = None
        year_match = re.search(r'\b(19[89][0-9]|20[0-3][0-9])\b', lower)
        if year_match:
            requested_year = int(year_match.group(1))
        elif any(phrase in lower for phrase in ["is saal", "this year", "abhi", "now", "recent"]):
            requested_year = 2024

        # 11. Launch Status (launched vs upcoming)
        launch_status = "any"
        if any(w in lower for w in ["upcoming", "announced", "future", "aane wali", "aage"]):
            launch_status = "upcoming"
        elif any(w in lower for w in ["launched", "lounch", "lunched", "release", "released", "aayi", "aagayi"]):
            launch_status = "launched"

        # 12. Market Extraction (default India)
        market = "India"
        if "usa" in lower or "us market" in lower or "america" in lower:
            market = "USA"
        elif "uk" in lower or "britain" in lower:
            market = "UK"
        elif "germany" in lower:
            market = "Germany"

        # 13. Category Normalization
        category_name = "all"
        if is_luxury:
            category_name = "luxury"
        elif detected_body_type:
            category_name = detected_body_type
        elif detected_fuel == "EV":
            category_name = "EV"

        is_launch = any(w in lower for w in ["launch", "lounch", "launched", "lunched", "upcoming", "release", "releases", "new car", "new cars"]) or requested_year is not None
        is_compare = any(word in lower for word in ["compare", "vs", "versus", "difference", "better than", "or"])
        is_websites_request = any(word in lower for word in ["websites", "sources", "check before buying", "links", "where to read"])

        intent_type = "vehicle_search"
        if is_compare:
            intent_type = "comparison"
        elif is_launch:
            intent_type = "car_launches"
        elif is_websites_request:
            intent_type = "sources_inquiry"

        filter_schema = CarSearchFilter(
            query=prompt,
            manufacturer=detected_manufacturer,
            body_type=detected_body_type,
            fuel_type=detected_fuel,
            price_max=price_max,
            price_min=price_min,
            min_mileage=min_mileage,
            min_airbags=airbags_min,
            min_safety_rating=min_safety_rating
        )

        return {
            "prompt": prompt,
            "intent": intent_type,
            "requested_year": requested_year,
            "launch_status": launch_status,
            "market": market,
            "category": category_name,
            "is_compare": is_compare,
            "is_luxury": is_luxury,
            "is_launch": is_launch,
            "is_websites_request": is_websites_request,
            "filter_schema": filter_schema,
            "parsed_constraints": {
                "manufacturer": detected_manufacturer,
                "body_type": detected_body_type,
                "fuel_type": detected_fuel,
                "price_max": price_max,
                "price_min": price_min,
                "min_airbags": airbags_min,
                "min_mileage": min_mileage,
                "seating_min": seating_min,
                "min_safety_rating": min_safety_rating,
                "is_luxury": is_luxury,
                "requested_year": requested_year,
                "market": market,
                "category": category_name,
                "launch_status": launch_status
            }
        }
