"""
Price Extractor Module — Extracts ex-showroom and on-road price strings and numeric values.
"""

import re
from typing import Dict, Any
from app.services.vehicle_search.utils.logger import log_step


class PriceExtractor:
    """Extracts ex-showroom and on-road prices from text content."""

    PRICE_PATTERNS = [
        r'₹\s*[\d\.]+\s*(?:Cr|Crore|Lakh|Lakhs|L)',
        r'Rs\.?\s*[\d\.]+\s*(?:Cr|Crore|Lakh|Lakhs|L)',
        r'INR\s*[\d\.]+\s*(?:Cr|Crore|Lakh|Lakhs|L)',
        r'\$\s*[\d,]+(?:\.\d+)?\s*(?:Million|M)?'
    ]

    def extract_prices(self, text: str, title: str) -> Dict[str, str]:
        combined = f"{title}\n{text[:4000]}"
        ex_showroom = ""
        on_road = ""

        # Extract Ex-Showroom Price
        for p in self.PRICE_PATTERNS:
            match = re.search(p, combined, re.IGNORECASE)
            if match:
                ex_showroom = match.group(0).strip()
                break

        # Extract On-Road Price if explicitly mentioned
        match_onroad = re.search(r'on[- ]road\s*(?:price)?\s*[:\-]?\s*(₹\s*[\d\.]+\s*(?:Cr|Crore|Lakh|Lakhs|L))', combined, re.IGNORECASE)
        if match_onroad:
            on_road = match_onroad.group(1).strip()

        log_step("price_extractor", f"Extracted Price Info: Ex-Showroom={ex_showroom}, On-Road={on_road}")
        return {
            "ex_showroom": ex_showroom,
            "on_road": on_road
        }
