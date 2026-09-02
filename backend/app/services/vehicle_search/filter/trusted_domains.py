"""
Trusted Domain Filter Module — Enforces domain whitelist filtering against trusted automotive sources.
"""

from typing import List, Dict, Any, Set
from app.services.vehicle_search.utils.logger import log_step

TRUSTED_DOMAINS: Set[str] = {
    "bmw.in",
    "bmwusa.com",
    "carwale.com",
    "cardekho.com",
    "zigwheels.com",
    "autocarindia.com",
    "caranddriver.com",
    "motortrend.com",
    "topgear.com",
    "autoexpress.co.uk",
    "edmunds.com",
    "kbb.com",
    "overdrive.in",
    "auto.ndtv.com",
    "drivespark.com",
    "tatamotors.com",
    "hyundai.com",
    "toyotabharat.com",
    "marutisuzuki.com",
    "kia.com",
    "hondacarindia.com",
    "volkswagen.co.in",
    "skoda-auto.co.in",
    "audi.in",
    "mercedes-benz.co.in",
    "porsche.com",
    "ferrari.com",
    "lamborghini.com",
    "bugatti.com",
    "bentleymotors.com",
    "rolls-roycemotorcars.com",
    "mgmotor.co.in",
    "nissan.in",
    "renault.co.in",
    "jeep-india.com",
    "volvocars.com",
    "lexusindia.co.in",
    "byd.com"
}


class TrustedDomainFilter:
    """Filters raw search results to retain only trusted automotive domains."""

    def __init__(self, whitelist: Set[str] = None):
        self.whitelist = whitelist if whitelist is not None else TRUSTED_DOMAINS

    def filter(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return []

        log_step("trusted_domains", f"Filtering {len(items)} items against trusted whitelist...")
        trusted = []

        for item in items:
            domain = item.get("domain", "").lower().replace("www.", "")
            is_trusted = False
            for allowed in self.whitelist:
                if domain == allowed or domain.endswith("." + allowed):
                    is_trusted = True
                    break

            if is_trusted:
                trusted.append(item)
                log_step("trusted_domains", f"ACCEPTED Trusted Domain: {domain}")
            else:
                log_step("trusted_domains", f"REJECTED Untrusted Domain: {domain}")

        log_step("trusted_domains", f"Domain filtering complete: {len(trusted)} retained out of {len(items)}")
        return trusted
