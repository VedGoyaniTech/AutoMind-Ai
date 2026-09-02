"""
Duplicate URL Remover Module — Normalizes and deduplicates URLs.
"""

from typing import List, Dict, Any, Set
from app.services.vehicle_search.utils.logger import log_step


class DuplicateRemover:
    """Normalizes URLs and removes duplicate web pages."""

    def remove_duplicates(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return []

        seen: Set[str] = set()
        unique_items = []

        for item in items:
            raw_url = item.get("url", "")
            if not raw_url:
                continue

            # Normalize URL
            clean_url = raw_url.split("#")[0].rstrip("/").lower()
            if clean_url.startswith("https://"):
                clean_url = clean_url[8:]
            elif clean_url.startswith("http://"):
                clean_url = clean_url[7:]

            if clean_url in seen:
                log_step("duplicate_remover", f"Removed Duplicate URL: {raw_url}")
                continue

            seen.add(clean_url)
            unique_items.append(item)

        log_step("duplicate_remover", f"Deduplication complete: {len(unique_items)} unique items retained out of {len(items)}")
        return unique_items
