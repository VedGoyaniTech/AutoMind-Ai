"""
Vehicle Extractor Module — Extracts vehicle brand, model, series, and variant names.
"""

import re
from typing import Dict, Any
from app.services.vehicle_search.utils.logger import log_step


class VehicleExtractor:
    """Extracts vehicle brand, model, series, and variant name from text content."""

    def extract_vehicle_info(self, text: str, title: str, query: str) -> Dict[str, str]:
        q_words = query.strip().split()
        brand = q_words[0].capitalize() if q_words else "Automotive"
        model = q_words[1].capitalize() if len(q_words) > 1 else brand

        # Check for variant name in title/text
        combined = f"{title}\n{text[:1500]}"
        variant = ""

        variant_patterns = [
            r'(competition\s*xdrive|competition|m\s*sport|gtx\s*plus|creative\s*plus|zx\s*plus|el\s*pro|sx\s*\(o\)|xline|tech\s*line|easy\s*shift|cummins)',
            r'(coupe|convertible|spider|gtb|gts|purosangue|stradale|pur\s*sport|tourbillon)'
        ]

        for p in variant_patterns:
            match = re.search(p, combined, re.IGNORECASE)
            if match:
                variant = match.group(0).strip().title()
                break

        if not variant:
            variant = "Standard Variant"

        log_step("vehicle_extractor", f"Extracted Vehicle Info: Brand={brand}, Model={model}, Variant={variant}")
        return {
            "brand": brand,
            "model": model,
            "series": "",
            "variant": variant
        }
