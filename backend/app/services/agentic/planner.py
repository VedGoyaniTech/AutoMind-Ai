"""
AutoMind AI — Agent Planner (Part 5 Specification)
"""

import re
from typing import Dict, Any, List, Optional
from app.services.agentic.schemas import (
    AgentPlan, PlannedStep, AgentIntent, ExtractedEntities
)

class AgentPlanner:
    """
    Deterministic & rule-first planner that parses user queries, extracts entities,
    determines the exact tool execution sequence, and generates targeted follow-up questions
    when required inputs (city, variant, down payment) are missing.
    """

    INDIC_DIGITS = {
        '૦': '0', '૧': '1', '૨': '2', '૩': '3', '૪': '4', '૫': '5', '૬': '6', '૭': '7', '૮': '8', '૯': '9',
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }

    CITY_MAP = {
        "ahmedabad": ("Ahmedabad", "GJ"), "अहमदाबाद": ("Ahmedabad", "GJ"), "અમદાવાદ": ("Ahmedabad", "GJ"),
        "surat": ("Surat", "GJ"), "सूरत": ("Surat", "GJ"), "સુરત": ("Surat", "GJ"),
        "vadodara": ("Vadodara", "GJ"), "baroda": ("Vadodara", "GJ"), "વડોદરા": ("Vadodara", "GJ"),
        "rajkot": ("Rajkot", "GJ"), "રાજકોટ": ("Rajkot", "GJ"),
        "mumbai": ("Mumbai", "MH"), "मुंबई": ("Mumbai", "MH"), "મુંબઈ": ("Mumbai", "MH"),
        "pune": ("Pune", "MH"), "पुणे": ("Pune", "MH"),
        "nagpur": ("Nagpur", "MH"), "नागपुर": ("Nagpur", "MH"),
        "delhi": ("Delhi", "DL"), "दिल्ली": ("Delhi", "DL"), "new delhi": ("Delhi", "DL"),
        "bengaluru": ("Bengaluru", "KA"), "bangalore": ("Bengaluru", "KA"), "बेंगलुरु": ("Bengaluru", "KA"), "બેંગ્લોર": ("Bengaluru", "KA"),
        "chennai": ("Chennai", "TN"), "चेन्नई": ("Chennai", "TN"),
        "hyderabad": ("Hyderabad", "TS"), "हैदराबाद": ("Hyderabad", "TS"),
        "jaipur": ("Jaipur", "RJ"), "जयपुर": ("Jaipur", "RJ"),
        "lucknow": ("Lucknow", "UP"), "लखनऊ": ("Lucknow", "UP"),
        "kolkata": ("Kolkata", "WB"), "कोलकाता": ("Kolkata", "WB"),
        "chandigarh": ("Chandigarh", "CH"), "चंडीगढ़": ("Chandigarh", "CH")
    }

    KNOWN_MODELS = [
        "nexon ev", "nexon", "creta", "thar roxx", "thar", "curvv ev", "curvv", "seltos", "safari",
        "xuv700", "scorpio-n", "scorpio", "dzire", "fronx", "innova hycross", "innova crysta", "innova",
        "brezza", "punch ev", "punch", "swift", "baleno", "grand vitara", "sonet", "carens",
        "harrier", "altroz", "tiago ev", "tiago", "tigor", "venue", "verna", "i20", "alcazar",
        "tucson", "elevate", "city", "amaze", "virtus", "taigun", "slavia", "kushaq", "hector", "ev6"
    ]

    def plan(self, user_prompt: str) -> AgentPlan:
        raw_text = user_prompt.strip()
        norm_text = raw_text
        for indic_d, arabic_d in self.INDIC_DIGITS.items():
            norm_text = norm_text.replace(indic_d, arabic_d)
        p_lower = norm_text.lower()

        # 1. Detect Language
        lang = "en"
        if any("\u0900" <= c <= "\u097F" for c in user_prompt) or any(w in p_lower for w in ["batao", "kitna", "padega", "kaun", "kya", "me", "mein", "wali"]):
            lang = "hi"
        elif any("\u0A80" <= c <= "\u0AFF" for c in user_prompt) or any(w in p_lower for w in ["ketli", "batavo", "ma", "kamat", "aapse", "che"]):
            lang = "gu"

        # 2. Extract Entities
        entities = self._extract_entities(p_lower, raw_text, lang)

        # 3. Classify Intent
        intent = self._classify_intent(p_lower, entities)

        # 4. Check for Missing Required Fields -> Follow-up
        needs_follow_up = False
        follow_up_q = None
        follow_up_fields = []

        if intent in [AgentIntent.EMI, AgentIntent.PRICE_AND_EMI, AgentIntent.ON_ROAD_PRICE]:
            # For standalone "Nexon EMI batao" or "Price batao" without city
            if not entities.city and not entities.down_payment and intent == AgentIntent.EMI:
                needs_follow_up = True
                follow_up_fields = ["variant", "city", "down_payment"]
                if lang == "hi":
                    follow_up_q = f"{entities.model or 'Car'} ka kaunsa variant, kaunsi city, aur kitna down payment rakhna hai?"
                elif lang == "gu":
                    follow_up_q = f"{entities.model or 'કાર'} માટે કયો વેરિઅન્ટ, કયું શહેર અને કેટલું ડાઉન પેમેન્ટ રાખવું છે?"
                else:
                    follow_up_q = f"Which variant, city, and down payment amount would you prefer for {entities.model or 'the car'}?"

        # 5. Build Planned Steps
        steps = self._build_steps(intent, entities, raw_text)

        return AgentPlan(
            intent=intent,
            extracted_entities=entities,
            steps=steps,
            needs_follow_up=needs_follow_up,
            follow_up_question=follow_up_q,
            follow_up_fields=follow_up_fields,
            detected_language=lang,
            goal=raw_text
        )

    def _extract_entities(self, p_lower: str, raw_text: str, lang: str) -> ExtractedEntities:
        # Extract City & State
        detected_city = None
        detected_state = None
        for c_key, (c_name, s_code) in self.CITY_MAP.items():
            if re.search(r'\b' + re.escape(c_key) + r'\b', p_lower):
                detected_city = c_name
                detected_state = s_code
                break

        # Extract Model
        detected_model = None
        for m in self.KNOWN_MODELS:
            if re.search(r'\b' + re.escape(m) + r'\b', p_lower):
                detected_model = m.title()
                break

        # Extract Down Payment
        dp_val = None
        dp_match = re.search(r'(?:down\s*payment|dp|ડાઉન\s*પેમેન્ટ|डाउन\s*पेमेंट)\s*(?:of|is|₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l|lac|लाख|લાખ)', p_lower)
        if not dp_match:
            dp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l|lac|लाख|લાખ)\s*(?:down\s*payment|dp|ડાઉન\s*પેમેન્ટ|डाउन\s*पेमेंट)', p_lower)
        if dp_match:
            dp_val = float(dp_match.group(1)) * 100000.0

        # Extract Tenure
        tenure_years = [3, 5, 7]
        tenure_match = re.search(r'(\d+)\s*(?:years|year|yrs|yr|saal|साल|વર્ષ)', p_lower)
        if tenure_match:
            t = int(tenure_match.group(1))
            if 1 <= t <= 10:
                tenure_years = [t]

        # Extract Year (e.g. 2024)
        year_match = re.search(r'\b(19[89][0-9]|20[0-3][0-9])\b', p_lower)
        req_year = int(year_match.group(1)) if year_match else None

        # Extract Fuel & Body Type
        fuel = None
        if "ev" in p_lower or "electric" in p_lower or "इलेक्ट्रिक" in p_lower or "ઇલેક્ટ્રિક" in p_lower:
            fuel = "EV"
        elif "diesel" in p_lower or "डीजल" in p_lower or "ડીઝલ" in p_lower:
            fuel = "Diesel"
        elif "petrol" in p_lower or "पेट्रोल" in p_lower or "પેટ્રોલ" in p_lower:
            fuel = "Petrol"
        elif "cng" in p_lower or "सीएनजी" in p_lower or "સીએનજી" in p_lower:
            fuel = "CNG"

        body = None
        if "suv" in p_lower or "एसयूवी" in p_lower or "એસયુવી" in p_lower:
            body = "SUV"
        elif "sedan" in p_lower or "सेडान" in p_lower or "સેડાન" in p_lower:
            body = "Sedan"
        elif "hatchback" in p_lower or "हैचबैक" in p_lower or "હેચબેક" in p_lower:
            body = "Hatchback"

        # Extract Comparison targets
        comp_targets = []
        if any(w in p_lower for w in [" vs ", " versus ", " compare ", " vs. "]):
            parts = re.split(r'\s+(?:vs|versus|compare|vs\.)\s+', p_lower)
            for part in parts[:2]:
                for km in self.KNOWN_MODELS:
                    if km in part:
                        comp_targets.append(km.title())
                        break

        return ExtractedEntities(
            city=detected_city,
            state_code=detected_state,
            model=detected_model,
            down_payment=dp_val,
            tenures_years=tenure_years,
            requested_year=req_year,
            launch_year=req_year,
            fuel_type=fuel,
            body_type=body,
            comparison_targets=comp_targets,
            language=lang
        )

    def _classify_intent(self, p_lower: str, entities: ExtractedEntities) -> AgentIntent:
        # 1. Casual / Greetings
        if len(p_lower.split()) <= 4 and any(w in p_lower for w in ["hi", "hello", "hey", "namaste", "kem cho", "kaise ho", "good morning"]):
            if not any(w in p_lower for w in ["price", "emi", "car", "suv", "ev"]):
                return AgentIntent.CASUAL

        # 2. Comparison
        if entities.comparison_targets or any(w in p_lower for w in [" vs ", " versus ", "compare", "तुलना", "સરખામણી"]):
            return AgentIntent.VEHICLE_COMPARISON

        # 3. Year-wise Launches
        if entities.requested_year and any(w in p_lower for w in ["launch", "launched", "lounch", "releases", "लॉन्च", "લૉન્ચ"]):
            return AgentIntent.YEARWISE_LAUNCHES

        # 4. Price & EMI
        has_price = any(w in p_lower for w in ["price", "on-road", "on road", "cost", "कीमत", "કિંમત", "प्राइस"])
        has_emi = any(w in p_lower for w in ["emi", "installment", "loan", "किस्त", "હપ્તો"])

        if has_price and has_emi:
            return AgentIntent.PRICE_AND_EMI
        elif has_emi:
            return AgentIntent.EMI
        elif has_price:
            return AgentIntent.ON_ROAD_PRICE

        # 5. Gallery
        if any(w in p_lower for w in ["photo", "image", "gallery", "pic", "look", "exterior", "interior"]):
            return AgentIntent.GALLERY_REQUEST

        # 6. Specific vehicle details
        if entities.model:
            return AgentIntent.VEHICLE_DETAILS

        # 7. Vehicle Search / Filter
        if entities.fuel_type or entities.body_type or any(w in p_lower for w in ["under", "best", "top", "safest"]):
            return AgentIntent.VEHICLE_SEARCH

        return AgentIntent.UNSUPPORTED_OR_UNCLEAR

    def _build_steps(self, intent: AgentIntent, entities: ExtractedEntities, raw_text: str) -> List[PlannedStep]:
        steps = []
        s_id = 1

        if intent == AgentIntent.VEHICLE_COMPARISON:
            car_a = entities.comparison_targets[0] if len(entities.comparison_targets) > 0 else "Nexon"
            car_b = entities.comparison_targets[1] if len(entities.comparison_targets) > 1 else "Creta"
            steps.append(PlannedStep(
                step_id=f"step_{s_id}",
                tool_name="compare_vehicles",
                input={"car_a": car_a, "car_b": car_b},
                purpose=f"Compare specifications and pricing between {car_a} and {car_b}"
            ))
            s_id += 1

        elif intent in [AgentIntent.ON_ROAD_PRICE, AgentIntent.PRICE_AND_EMI, AgentIntent.EMI]:
            steps.append(PlannedStep(
                step_id=f"step_{s_id}",
                tool_name="calculate_pricing_quote",
                input={
                    "city": entities.city or "Ahmedabad",
                    "state_code": entities.state_code or "GJ",
                    "model": entities.model or "Nexon",
                    "variant": entities.variant,
                    "down_payment": entities.down_payment,
                    "fuel_type": entities.fuel_type or "petrol"
                },
                purpose=f"Calculate on-road price breakdown for {entities.model or 'vehicle'} in {entities.city or 'Gujarat'}"
            ))
            s_id += 1

            if intent in [AgentIntent.PRICE_AND_EMI, AgentIntent.EMI]:
                steps.append(PlannedStep(
                    step_id=f"step_{s_id}",
                    tool_name="calculate_emi",
                    input={
                        "on_road_price": 1450000.0,
                        "down_payment": entities.down_payment,
                        "tenures_years": entities.tenures_years
                    },
                    depends_on=[f"step_{s_id-1}"],
                    purpose="Calculate reducing-balance EMI options across requested tenures"
                ))
                s_id += 1

        elif intent == AgentIntent.YEARWISE_LAUNCHES:
            steps.append(PlannedStep(
                step_id=f"step_{s_id}",
                tool_name="web_research",
                input={
                    "query": raw_text,
                    "target_year": entities.requested_year
                },
                purpose=f"Retrieve verified launch citations and references for {entities.requested_year or 'recent'} vehicle releases"
            ))
            s_id += 1

        elif intent == AgentIntent.GALLERY_REQUEST:
            steps.append(PlannedStep(
                step_id=f"step_{s_id}",
                tool_name="get_vehicle_gallery",
                input={"model": entities.model or "Nexon"},
                purpose=f"Retrieve image media gallery for {entities.model or 'vehicle'}"
            ))
            s_id += 1

        elif intent == AgentIntent.VEHICLE_DETAILS:
            steps.append(PlannedStep(
                step_id=f"step_{s_id}",
                tool_name="get_vehicle_details",
                input={"model": entities.model},
                purpose=f"Fetch full specifications and safety ratings for {entities.model}"
            ))
            s_id += 1

        else:
            # General vehicle search
            steps.append(PlannedStep(
                step_id=f"step_{s_id}",
                tool_name="search_vehicles",
                input={
                    "query": raw_text,
                    "fuel_type": entities.fuel_type,
                    "body_type": entities.body_type
                },
                purpose="Search vehicle catalog for matching models"
            ))
            s_id += 1

        return steps
