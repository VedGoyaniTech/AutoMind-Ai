import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import httpx
from app.core.config import settings

logger = logging.getLogger("automind.intelligence.traffic")

class TrafficService:
    """
    Traffic Intelligence Integration via INRIX:
    - INRIX Developer Portal: https://developer.inrix.com/
    - Covers traffic incidents, segment speeds, congestion index, and travel times.
    - Indian market notice: INRIX primarily services North America, Europe, and select international corridors.
      India coverage requires specific enterprise licensing.
    - If unconfigured, marks status as 'not_configured' without failing the overall car intelligence payload.
    """

    def __init__(self):
        self.api_key = settings.TRAFFIC_API_KEY
        self.base_url = settings.INRIX_BASE_URL.rstrip("/")
        self.timeout = settings.PROVIDER_REQUEST_TIMEOUT_SECONDS

    async def get_city_traffic(self, city: str = "Ahmedabad") -> Dict[str, Any]:
        """Fetches traffic and congestion index for a target metropolitan area."""
        clean_city = city.strip().title()

        if not self.api_key:
            return {
                "status": "not_configured",
                "provider": "INRIX Traffic",
                "city": clean_city,
                "congestion_level": None,
                "incidents_count": 0,
                "note": "TRAFFIC_API_KEY is not configured in .env. INRIX enterprise credentials required for live urban corridor congestion data.",
                "provenance": "https://developer.inrix.com/",
                "market_coverage": "North America / Europe primary; Indian urban hubs require enterprise data contract"
            }

        url = f"{self.base_url}/v1/traffic/congestion"
        params = {"city": clean_city}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "status": "live",
                        "provider": "INRIX",
                        "city": clean_city,
                        "congestion_index": data.get("congestion_index"),
                        "average_speed_kmh": data.get("average_speed_kmh"),
                        "incident_summary": data.get("incidents", []),
                        "provenance": "https://inrix.com/",
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        "status": "unavailable",
                        "provider": "INRIX",
                        "city": clean_city,
                        "error": f"INRIX API returned status {resp.status_code}."
                    }
        except httpx.TimeoutException:
            logger.warning("[TrafficService] INRIX request timed out.")
            return {
                "status": "timeout",
                "provider": "INRIX",
                "city": clean_city,
                "error": f"Request to INRIX timed out after {self.timeout}s."
            }
        except Exception as e:
            logger.error(f"[TrafficService] INRIX error: {e}", exc_info=True)
            return {
                "status": "unavailable",
                "provider": "INRIX",
                "city": clean_city,
                "error": str(e)
            }

traffic_service = TrafficService()
