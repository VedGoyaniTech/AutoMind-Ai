import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import httpx
from app.core.config import settings

logger = logging.getLogger("automind.intelligence.fuel")

class FuelPriceService:
    """
    Indian City Fuel Price Integration (API Mitra / Indian API):
    - Fetches daily revised petrol and diesel prices per liter (₹/L)
    - Validates city coverage and genuine responses
    - Strictly flags unconfigured status if FUEL_API_KEY is not set (never labels hardcoded data as live).
    """

    def __init__(self):
        self.api_key = settings.FUEL_API_KEY
        self.base_url = settings.INDIAN_API_BASE_URL.rstrip("/")
        self.timeout = settings.PROVIDER_REQUEST_TIMEOUT_SECONDS

    async def get_fuel_prices(self, city: str = "Ahmedabad") -> Dict[str, Any]:
        """Fetches current petrol and diesel prices for an Indian city."""
        clean_city = city.strip().title()

        # If key is missing, mark as not_configured
        if not self.api_key:
            return {
                "status": "not_configured",
                "provider": "Indian API / API Mitra",
                "city": clean_city,
                "currency": "INR",
                "petrol": None,
                "diesel": None,
                "note": "FUEL_API_KEY is not configured in .env. Configure an API key from IndianAPI (https://indianapi.in/) or APIMitra (https://apimitra.com/) to receive daily live pump prices.",
                "provenance": "https://indianapi.in/"
            }

        url = f"{self.base_url}/fuel/price"
        params = {"city": clean_city}
        headers = {"X-Api-Key": self.api_key, "Accept": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    petrol = data.get("petrol") or data.get("petrol_price")
                    diesel = data.get("diesel") or data.get("diesel_price")
                    last_updated = data.get("updated_at") or data.get("date") or datetime.now(timezone.utc).isoformat()

                    if petrol is not None and diesel is not None:
                        return {
                            "status": "live",
                            "provider": "Indian API (Live OMC Feed)",
                            "city": clean_city,
                            "currency": "INR",
                            "petrol_per_liter": float(petrol),
                            "diesel_per_liter": float(diesel),
                            "cng_per_kg": float(data["cng"]) if "cng" in data and data["cng"] else None,
                            "last_updated": last_updated,
                            "provenance": "Indian Oil Corporation / BPCL / HPCL Daily Pricing Matrix",
                            "unit": "₹/Litre"
                        }
                    else:
                        return {
                            "status": "empty_results",
                            "provider": "Indian API",
                            "city": clean_city,
                            "error": f"City '{clean_city}' fuel prices not found in provider registry."
                        }
                elif resp.status_code in (401, 403):
                    return {
                        "status": "auth_failed",
                        "provider": "Indian API",
                        "city": clean_city,
                        "error": "FUEL_API_KEY is unauthorized or expired."
                    }
                else:
                    return {
                        "status": "unavailable",
                        "provider": "Indian API",
                        "city": clean_city,
                        "error": f"Fuel API returned status {resp.status_code}."
                    }
        except httpx.TimeoutException:
            logger.warning("[FuelPriceService] Fuel API request timed out.")
            return {
                "status": "timeout",
                "provider": "Indian API",
                "city": clean_city,
                "error": f"Request to Fuel API timed out after {self.timeout}s."
            }
        except Exception as e:
            logger.error(f"[FuelPriceService] Fuel API error: {e}", exc_info=True)
            return {
                "status": "unavailable",
                "provider": "Indian API",
                "city": clean_city,
                "error": str(e)
            }

fuel_price_service = FuelPriceService()
