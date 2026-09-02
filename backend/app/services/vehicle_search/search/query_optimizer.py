"""
Query Optimizer Module — Transforms raw user queries into targeted automotive search strings.
Examples:
- "BMW M4" -> "BMW M4 Competition price specifications India"
- "Audi RS5" -> "Audi RS5 price specifications India"
- "Toyota Fortuner" -> "Toyota Fortuner on road price specifications"
- "Hyundai Creta" -> "Hyundai Creta price mileage engine specifications"
"""

import re
from app.services.vehicle_search.utils.logger import log_step


class QueryOptimizer:
    """Optimizes raw vehicle queries into targeted, unambiguous search engine strings."""

    GENERIC_STOP_WORDS = {"give", "me", "what", "is", "the", "tell", "show", "details", "how", "much", "please", "car"}

    def optimize(self, user_query: str) -> str:
        if not user_query:
            return ""

        raw = user_query.strip()
        words = [w for w in raw.split() if w.lower() not in self.GENERIC_STOP_WORDS]
        base_query = " ".join(words) if words else raw
        q_lower = base_query.lower()

        additions = []

        if not any(w in q_lower for w in ["price", "cost", "on-road", "ex-showroom"]):
            additions.append("price")

        if not any(w in q_lower for w in ["spec", "specs", "specification", "specifications", "engine", "mileage"]):
            additions.append("specifications")

        if not any(w in q_lower for w in ["india", "inr", "lakh", "crore", "usd", "usa"]):
            additions.append("India")

        optimized = f"{base_query} {' '.join(additions)}".strip()
        log_step("query_optimization", f"Transformed query: '{user_query}' -> '{optimized}'")
        return optimized
