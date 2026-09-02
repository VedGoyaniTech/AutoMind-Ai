"""
Agent Planner — Analyzes user goal and constructs a verified sequence of typed tool steps.
"""

import re
from typing import Dict, Any, List
from app.services.agentic.schemas import AgentPlan, AgentPlanStep

class AgentPlanner:
    def plan(self, user_prompt: str) -> AgentPlan:
        p_lower = user_prompt.lower()
        steps: List[AgentPlanStep] = []
        step_id = 1

        # Detect language
        lang = "en"
        if any("\u0900" <= c <= "\u097F" for c in user_prompt) or any(w in p_lower for w in ["batao", "kitna", "padega", "kaun", "kya", "me"]):
            lang = "hi"
        elif any("\u0A80" <= c <= "\u0AFF" for c in user_prompt) or any(w in p_lower for w in ["ketli", "batavo", "ma", "kamat", "aapse"]):
            lang = "gu"

        # 1. Check for Vehicle Comparison
        if any(w in p_lower for w in ["vs", "compare", "versus", "comparison"]):
            cars = re.findall(r"([a-zA-Z0-9]+)\s+(?:vs|versus|compare)\s+([a-zA-Z0-9]+)", user_prompt, re.I)
            car_a = cars[0][0] if cars else "Car A"
            car_b = cars[0][1] if cars else "Car B"
            steps.append(AgentPlanStep(
                step_id=step_id,
                tool_name="compare_vehicles",
                description=f"Compare {car_a} and {car_b} features and pricing",
                arguments={"car_a": car_a, "car_b": car_b}
            ))
            step_id += 1

        # 2. Check for On-Road Price / RTO / EMI
        has_price_intent = any(w in p_lower for w in [
            "on-road", "on road", "price", "rto", "tax", "emi", "down payment", "cost",
            "kitna", "keemat", "કિંમત", "प्राइस", "ऑन-रोड", "ऑन रोड", "कीमत", "કેટલી"
        ])
        if has_price_intent:
            # Extract city if present
            city = None
            city_map = {
                "ahmedabad": "Ahmedabad", "अहमदाबाद": "Ahmedabad", "અમદાવાદ": "Ahmedabad",
                "surat": "Surat", "सूरत": "Surat", "સુરત": "Surat",
                "mumbai": "Mumbai", "मुंबई": "Mumbai", "મુંબઈ": "Mumbai",
                "pune": "Pune", "पुणे": "Pune",
                "delhi": "Delhi", "दिल्ली": "Delhi",
                "bengaluru": "Bengaluru", "bangalore": "Bengaluru", "बेंगलुरु": "Bengaluru"
            }
            for c_key, c_val in city_map.items():
                if c_key in p_lower:
                    city = c_val
                    break

            # Extract model
            model = None
            model_map = {
                "nexon": "Nexon", "नेक्सॉन": "Nexon", "નેક્સન": "Nexon",
                "creta": "Creta", "क्रेटा": "Creta",
                "thar": "Thar", "थार": "Thar",
                "curvv": "Curvv", "कर्व": "Curvv",
                "seltos": "Seltos", "सेल्टोस": "Seltos",
                "safari": "Safari", "सफारी": "Safari",
                "xuv700": "XUV700", "dzire": "Dzire", "fronx": "Fronx",
                "innova": "Innova", "brezza": "Brezza", "punch": "Punch", "swift": "Swift"
            }
            for m_key, m_val in model_map.items():
                if m_key in p_lower:
                    model = m_val
                    break

            # Extract down payment if present
            dp = None
            dp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)", p_lower)
            if dp_match and ("down" in p_lower or "dp" in p_lower):
                dp = float(dp_match.group(1)) * 100000.0

            steps.append(AgentPlanStep(
                step_id=step_id,
                tool_name="calculate_pricing_quote",
                description=f"Calculate deterministic on-road price and EMI for {model or 'vehicle'} in {city or 'city'}",
                arguments={
                    "city": city or "Ahmedabad",
                    "model": model or "Nexon",
                    "down_payment": dp,
                    "fuel_type": "petrol"
                }
            ))
            step_id += 1

        # 3. Check for Photo / Media Gallery Intent
        has_media_intent = any(w in p_lower for w in ["photo", "image", "gallery", "pic", "look", "exterior", "interior"])
        if has_media_intent or any(m in p_lower for m in ["thar", "creta", "nexon", "curvv", "xuv700", "dzire"]):
            steps.append(AgentPlanStep(
                step_id=step_id,
                tool_name="get_vehicle_gallery",
                description="Retrieve structured multi-modal vehicle photo gallery",
                arguments={"query_text": user_prompt}
            ))
            step_id += 1

        # 4. Check for Budget / Search Intent
        if not steps or any(w in p_lower for w in ["best", "under", "budget", "top", "recommend", "suv", "ev"]):
            steps.append(AgentPlanStep(
                step_id=step_id,
                tool_name="search_vehicles",
                description="Search local vehicle catalog matching budget and fuel constraints",
                arguments={"query_text": user_prompt}
            ))
            step_id += 1

        return AgentPlan(
            goal=user_prompt,
            detected_language=lang,
            steps=steps,
            estimated_steps=len(steps)
        )
