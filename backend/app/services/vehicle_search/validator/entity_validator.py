"""
Entity Validator Module — Validates requested vehicle entity against page title/URL using 90% threshold.

Example:
Requested: "BMW M4" -> Page: "BMW X5" -> REJECT
Requested: "BMW M4 Competition" -> Page: "BMW M4 Competition xDrive" -> ACCEPT
"""

from typing import List
from app.services.vehicle_search.models import SearchResult
from app.services.vehicle_search.utils.fuzzy import is_entity_match
from app.services.vehicle_search.utils.logger import log_step


class EntityValidator:
    """Validates search result pages against requested vehicle entity using a strict 90% similarity threshold."""

    def __init__(self, threshold: float = 0.90):
        self.threshold = threshold

    def validate_results(self, requested_vehicle: str, search_results: List[SearchResult]) -> List[SearchResult]:
        if not requested_vehicle or not search_results:
            return []

        log_step("entity_validation", f"Validating entity matching for '{requested_vehicle}' (Threshold: {int(self.threshold*100)}%)...")
        valid_results: List[SearchResult] = []

        for item in search_results:
            # Check title + snippet against requested vehicle name
            text_to_check = f"{item.title} {item.snippet}"
            is_match, score = is_entity_match(requested_vehicle, text_to_check, threshold=self.threshold)

            # Check for conflicting car model names in title (e.g. user asked for M4, title says X5 or M3)
            has_conflict = self._check_model_conflict(requested_vehicle, item.title)

            if is_match and not has_conflict:
                valid_results.append(item)
                log_step("entity_validation", f"ACCEPTED Entity Match: '{item.title}' (Score: {score:.2f})")
            else:
                reason = "Conflicting vehicle model" if has_conflict else f"Below threshold ({score:.2f})"
                log_step("entity_validation", f"REJECTED Entity Match: '{item.title}' ({reason})")

        log_step("entity_validation", f"Entity validation complete: {len(valid_results)} pages validated out of {len(search_results)}")
        return valid_results

    def _check_model_conflict(self, requested_vehicle: str, page_title: str) -> bool:
        """
        Detects if the page title explicitly references a DIFFERENT vehicle model of the same brand.
        Example: requested "BMW M4", title mentions "BMW X5" or "BMW M3" -> Conflict = True.
        """
        req_lower = requested_vehicle.lower()
        title_lower = page_title.lower()

        # Specific model codes for BMW, Audi, Mercedes, Mahindra, Tata, Hyundai, etc.
        model_codes = ["m2", "m3", "m4", "m5", "m6", "m8", "x1", "x3", "x5", "x6", "x7", "z4", "q3", "q5", "q7", "r8", "c-class", "e-class", "s-class", "creta", "seltos", "nexon", "harrier", "safari", "scorpio", "thar", "fortuner"]

        for code in model_codes:
            # If code is in title but NOT in requested_vehicle name -> model conflict!
            if re_token_match(code, title_lower) and not re_token_match(code, req_lower):
                return True

        return False


def re_token_match(token: str, text: str) -> bool:
    """Exact word boundary match for model code tokens."""
    import re
    pattern = r'\b' + re.escape(token) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))
