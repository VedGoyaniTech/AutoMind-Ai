import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import httpx
from app.core.config import settings
from app.services.intelligence.utils import calculate_market_statistics

logger = logging.getLogger("automind.intelligence.market")

class VehicleMarketService:
    """
    Integrates used-car listings and market statistics via:
    1. DataForCars API (US-focused vehicle listings and market snapshots)
    2. India Market Feed Provider Interface (for future licensed Indian listing APIs)

    CRITICAL RULES:
    - Never display US market values as Indian prices.
    - Always state currency (USD vs INR) and geographic coverage.
    - Distinguish asking prices from completed sales.
    """

    def __init__(self):
        self.api_key = settings.DATAFORCARS_API_KEY
        self.base_url = settings.DATAFORCARS_BASE_URL.rstrip("/")
        self.timeout = settings.PROVIDER_REQUEST_TIMEOUT_SECONDS

    async def get_market_data(
        self,
        make: str,
        model: str,
        year: Optional[int] = None,
        city: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves active listings, computes market statistics, and reports geographic alignment.
        """
        # 1. If key is missing, report not_configured
        if not self.api_key:
            return {
                "status": "not_configured",
                "provider": "DataForCars",
                "listings": [],
                "statistics": calculate_market_statistics([], "USD"),
                "geographic_coverage": "United States (USD)",
                "india_feed_status": "partner_interface_ready",
                "note": "DATAFORCARS_API_KEY is not configured. Configure credentials in .env to enable live North American used-car market snapshots.",
                "provenance": "https://dataforcars.com/docs"
            }

        # 2. Fetch live listings from DataForCars API
        try:
            listings, raw_snapshot = await self._fetch_dataforcars_listings(make, model, year)
            stats = calculate_market_statistics(listings, currency="USD")
            return {
                "status": "live" if listings else "empty_results",
                "provider": "DataForCars",
                "geographic_coverage": "United States (USD)",
                "currency": "USD",
                "listings": listings,
                "statistics": stats,
                "raw_snapshot": raw_snapshot,
                "india_feed_status": "partner_interface_ready",
                "market_scope_notice": "Market data originates from North American dealer listings (in USD). For Indian vehicle purchases, refer to our verified on-road pricing section.",
                "provenance": "https://dataforcars.com/docs/vehicle-listings",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except httpx.TimeoutException:
            logger.warning("[VehicleMarketService] DataForCars request timed out.")
            return {
                "status": "timeout",
                "provider": "DataForCars",
                "listings": [],
                "statistics": calculate_market_statistics([], "USD"),
                "error": f"Request to DataForCars timed out after {self.timeout}s."
            }
        except Exception as e:
            logger.error(f"[VehicleMarketService] DataForCars error: {e}", exc_info=True)
            return {
                "status": "unavailable",
                "provider": "DataForCars",
                "listings": [],
                "statistics": calculate_market_statistics([], "USD"),
                "error": str(e)
            }

    async def _fetch_dataforcars_listings(
        self,
        make: str,
        model: str,
        year: Optional[int] = None
    ) -> tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Call DataForCars vehicle listings and market snapshot endpoints."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Api-Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "AutoMindAI/1.0"
        }
        params = {"make": make, "model": model}
        if year:
            params["year"] = str(year)

        listings_url = f"{self.base_url}/v1/listings"
        snapshot_url = f"{self.base_url}/v1/market-snapshot"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # 1. Fetch listings
            listings_resp = await client.get(listings_url, params=params, headers=headers)
            normalized_listings = []
            if listings_resp.status_code == 200:
                body = listings_resp.json()
                raw_items = body.get("data") or body.get("listings") or []
                for item in raw_items:
                    retail = item.get("retail") or {}
                    veh = item.get("vehicle") or {}
                    ident = veh.get("identity") or {}
                    dealer = item.get("dealer") or {}

                    l_price = retail.get("price") if retail.get("price") is not None else item.get("price", 0.0)
                    l_miles = retail.get("miles") if retail.get("miles") is not None else item.get("mileage")
                    l_year = ident.get("year") or item.get("year") or year
                    l_url = retail.get("vdp") or item.get("url") or item.get("listing_url")
                    l_dealer = dealer.get("name") or item.get("dealer_name") or item.get("seller_name")
                    l_state = dealer.get("state") or item.get("state")

                    normalized_listings.append({
                        "id": str(item.get("vin") or item.get("id") or ""),
                        "title": item.get("title") or f"{l_year or ''} {make} {model}".strip(),
                        "make": make,
                        "model": model,
                        "year": l_year,
                        "price": float(l_price) if l_price else 0.0,
                        "currency": item.get("currency", "USD"),
                        "mileage": float(l_miles) if l_miles is not None else None,
                        "mileage_unit": item.get("mileage_unit", "miles"),
                        "city": item.get("city"),
                        "state": l_state,
                        "country": "US",
                        "dealer_name": l_dealer,
                        "listing_url": l_url,
                        "url": l_url,
                        "is_asking_price": True,
                        "listed_at": item.get("listed_at") or item.get("created_at")
                    })

            # 2. Fetch market snapshot if available
            snapshot_data = None
            try:
                snap_resp = await client.get(snapshot_url, params=params, headers=headers)
                if snap_resp.status_code == 200:
                    snapshot_data = snap_resp.json()
            except Exception:
                pass

            return normalized_listings, snapshot_data

vehicle_market_service = VehicleMarketService()
