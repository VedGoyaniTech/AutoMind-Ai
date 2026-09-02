"""
Vehicle Entity Validator Module — Performs multi-level entity validation (Brand, Series, Model, Variant).
Uses RapidFuzz with a strict 90% minimum similarity threshold and rejects conflicting vehicle models.

Prevents mixing between different vehicles (e.g. BMW M4 vs BMW X5, Tata Nexon vs Tata Punch, Hyundai Creta vs Hyundai Venue).
"""

import re
from typing import List, Dict, Any, Tuple
from app.services.vehicle_search.models.vehicle import VehicleEntity
from app.services.vehicle_search.utils.logger import log_step

try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False


KNOWN_BRAND_ALIASES = {
    "bwm": "bmw", "farari": "ferrari", "ferari": "ferrari",
    "buggti": "bugatti", "bugati": "bugatti", "porche": "porsche",
    "porshe": "porsche", "lambo": "lamborghini", "lamborgini": "lamborghini"
}

# Explicit model conflict registry per brand to prevent cross-model leakage
BRAND_MODEL_FAMILY_MAP = {
    "bmw": ["m2", "m3", "m4", "m5", "m6", "m8", "x1", "x3", "x4", "x5", "x6", "x7", "z4", "3 series", "5 series", "7 series", "i4", "i7", "ix"],
    "tata": ["nexon", "punch", "harrier", "safari", "altroz", "tiago", "tigor", "curvv", "nano"],
    "hyundai": ["creta", "venue", "alcazar", "tucson", "exter", "verna", "i20", "i10", "ioniq 5"],
    "toyota": ["fortuner", "innova", "glanza", "urban cruiser", "camry", "hilux", "land cruiser"],
    "mahindra": ["scorpio", "xuv700", "xuv400", "xuv300", "thar", "bolero", "marazzo"],
    "kia": ["seltos", "sonet", "carens", "ev6", "carnival"],
    "honda": ["city", "amaze", "elevate", "wr-v", "civic"],
    "skoda": ["slavia", "kushaq", "kodiaq", "octavia", "superb"],
    "volkswagen": ["virtus", "taigun", "tiguan"],
    "mg": ["hector", "astor", "zs ev", "comet"],
    "porsche": ["911", "taycan", "cayenne", "macan", "panamera"],
    "ferrari": ["roma", "296", "purosangue", "sf90", "f8", "812"],
    "lamborghini": ["urus", "huracan", "revuelto", "aventador"],
    "audi": ["r8", "rs5", "q3", "q5", "q7", "q8", "a4", "a6", "e-tron"],
    "mercedes": ["c-class", "e-class", "s-class", "glc", "gle", "gls", "amg gt", "g-class"]
}


class VehicleEntityValidator:
    """Multi-level vehicle entity validator enforcing RapidFuzz >= 90% threshold and model conflict checks."""

    def __init__(self, threshold: float = 0.90):
        self.threshold = threshold

    def decompose_query(self, query: str) -> VehicleEntity:
        """Decomposes raw user query into Brand, Series, Model, Variant."""
        q_lower = query.lower().strip()
        words = q_lower.split()

        # Handle typo aliases
        for typo, real in KNOWN_BRAND_ALIASES.items():
            if typo in q_lower:
                q_lower = q_lower.replace(typo, real)
                words = q_lower.split()

        brand = ""
        model = ""
        series = ""
        variant = ""

        # Identify Brand
        for b in BRAND_MODEL_FAMILY_MAP:
            if b in q_lower:
                brand = b
                break

        if not brand and words:
            brand = words[0]

        # Identify Model
        if brand in BRAND_MODEL_FAMILY_MAP:
            for known_m in BRAND_MODEL_FAMILY_MAP[brand]:
                if known_m in q_lower:
                    model = known_m
                    break

        if not model:
            non_stop = [w for w in words if w not in ["price", "cost", "india", "specs", "specifications", "car", "give", "me"] and w != brand]
            model = non_stop[0] if non_stop else (words[1] if len(words) > 1 else brand)

        # Identify Variant if present
        variant_keywords = ["competition", "xdrive", "creativ", "empowered", "zx", "zx plus", "creative plus", "gtx", "m sport", "lxi", "vxi", "zxi"]
        for vk in variant_keywords:
            if vk in q_lower:
                variant = vk
                break

        return VehicleEntity(
            raw_query=query,
            brand=brand.upper() if len(brand) <= 4 else brand.capitalize(),
            series=series,
            model=model.upper() if len(model) <= 4 else model.capitalize(),
            variant=variant.title()
        )

    def validate_items(self, query: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items or not query:
            return []

        entity = self.decompose_query(query)
        log_step("entity_validation", f"Validating entity match for requested vehicle: {entity.brand} {entity.model} (Threshold: {int(self.threshold*100)}%)...")

        valid_items = []

        for item in items:
            text_to_check = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
            is_valid, score, reason = self._validate_single_text(entity, text_to_check)

            if is_valid:
                valid_items.append(item)
                log_step("entity_validation", f"ACCEPTED Entity Match: '{item.get('title', '')}' (Score: {score:.2f})")
            else:
                log_step("entity_validation", f"REJECTED Entity Match: '{item.get('title', '')}' ({reason})")

        log_step("entity_validation", f"Entity validation complete: {len(valid_items)} items passed out of {len(items)}")
        return valid_items

    def _validate_single_text(self, entity: VehicleEntity, page_text: str) -> Tuple[bool, float, str]:
        brand_lower = entity.brand.lower()
        model_lower = entity.model.lower()

        # 1. Model Conflict Check — Check if page references a DIFFERENT model of the same brand
        if brand_lower in BRAND_MODEL_FAMILY_MAP:
            all_brand_models = BRAND_MODEL_FAMILY_MAP[brand_lower]
            for other_model in all_brand_models:
                # If page contains other_model but requested query DOES NOT contain other_model -> Conflict!
                if other_model != model_lower and self._token_in_text(other_model, page_text) and not self._token_in_text(other_model, entity.raw_query.lower()):
                    return False, 0.0, f"Model conflict: page references '{other_model}', requested '{model_lower}'"

        # 2. Token inclusion check for brand & model
        if model_lower and not self._token_in_text(model_lower, page_text):
            return False, 0.0, f"Model '{model_lower}' not found in target text"

        # 3. RapidFuzz similarity ratio against requested model token
        if HAS_RAPIDFUZZ:
            similarity = fuzz.token_set_ratio(f"{brand_lower} {model_lower}", page_text) / 100.0
        else:
            similarity = 0.95 if model_lower in page_text else 0.50

        if similarity < self.threshold:
            return False, similarity, f"Below threshold ({similarity:.2f})"

        return True, similarity, "PASSED"

    def _token_in_text(self, token: str, text: str) -> bool:
        pattern = r'\b' + re.escape(token) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
