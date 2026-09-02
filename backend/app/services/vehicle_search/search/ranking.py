"""
Search Ranking Module — Ranks search items based on domain authority, title relevance, and spec keywords.
"""

from typing import List, Dict, Any
from app.services.vehicle_search.utils.logger import log_step


class SearchRanker:
    """Ranks and sorts search engine results to select top priority pages for scraping."""

    HIGH_AUTHORITY_DOMAINS = {
        "carwale.com": 1.5,
        "cardekho.com": 1.5,
        "bmw.in": 2.0,
        "autocarindia.com": 1.4,
        "zigwheels.com": 1.3,
        "caranddriver.com": 1.3,
        "motortrend.com": 1.3
    }

    def rank_results(self, items: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        if not items:
            return []

        q_words = set(query.lower().split())

        def score_item(item: Dict[str, Any]) -> float:
            score = 1.0
            domain = item.get("domain", "").lower()
            title = item.get("title", "").lower()

            # Domain authority boost
            for dom, weight in self.HIGH_AUTHORITY_DOMAINS.items():
                if dom in domain:
                    score *= weight
                    break

            # Keyword match boost
            t_words = set(title.split())
            overlap = q_words.intersection(t_words)
            score += len(overlap) * 0.5

            if "price" in title:
                score += 0.5
            if "spec" in title or "specs" in title:
                score += 0.4

            return score

        ranked = sorted(items, key=score_item, reverse=True)
        log_step("ranking", f"Ranked {len(ranked)} search items based on authority and query relevance")
        return ranked
