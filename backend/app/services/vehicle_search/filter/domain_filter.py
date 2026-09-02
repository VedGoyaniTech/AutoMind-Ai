"""
Trusted Domain Filter Module — Enforces duplicate URL removal & trusted domain whitelist filtering.

Trusted Domains:
- bmw.in
- bmwusa.com
- carwale.com
- cardekho.com
- zigwheels.com
- autocarindia.com
- caranddriver.com
- motortrend.com
- overdrive.in
- auto.ndtv.com
- drivespark.com
- Tatamotors.com
- Hyundai.com
- Mahindrascar.com
- Toyotabharat.com
- Marutisuzuki.com
"""

from typing import List, Set
from app.services.vehicle_search.models import SearchResult
from app.services.vehicle_search.utils.logger import log_step


TRUSTED_DOMAINS = {
    "bmw.in",
    "bmwusa.com",
    "carwale.com",
    "cardekho.com",
    "zigwheels.com",
    "autocarindia.com",
    "caranddriver.com",
    "motortrend.com",
    "overdrive.in",
    "auto.ndtv.com",
    "drivespark.com",
    "tatamotors.com",
    "hyundai.com",
    "mahindrasutra.com",
    "toyotabharat.com",
    "marutisuzuki.com",
    "kiaindia.net",
    "kia.com",
    "hondacarindia.com",
    "volkswagen.co.in",
    "skoda-auto.co.in",
    "audi.in",
    "mercedes-benz.co.in",
    "porsche.com",
    "ferrari.com",
    "lamborghini.com",
    "bugatti.com"
}


class TrustedDomainFilter:
    """Filters search results to only retain trusted automotive domains and unique URLs."""

    def __init__(self, allowed_domains: Set[str] = None):
        self.allowed_domains = allowed_domains if allowed_domains is not None else TRUSTED_DOMAINS

    def filter(self, search_results: List[SearchResult]) -> List[SearchResult]:
        if not search_results:
            return []

        log_step("domain_filter", f"Filtering {len(search_results)} search results against trusted domain whitelist...")
        seen_urls: Set[str] = set()
        filtered: List[SearchResult] = []

        for item in search_results:
            # 1. Normalize URL & deduplicate
            clean_url = item.url.split("#")[0].rstrip("/")
            if clean_url in seen_urls:
                log_step("domain_filter", f"Rejected Duplicate URL: {item.url}")
                continue

            # 2. Extract domain & check whitelist match
            domain = item.domain.lower().replace("www.", "")
            is_trusted = False

            for trusted in self.allowed_domains:
                if domain == trusted or domain.endswith("." + trusted):
                    is_trusted = True
                    break

            if is_trusted:
                seen_urls.add(clean_url)
                filtered.append(item)
                log_step("domain_filter", f"Accepted Trusted Domain: {domain} ({clean_url})")
            else:
                log_step("domain_filter", f"Rejected Untrusted Domain: {domain}")

        log_step("domain_filter", f"Filter complete: {len(filtered)} trusted results retained from {len(search_results)} input items")
        return filtered
