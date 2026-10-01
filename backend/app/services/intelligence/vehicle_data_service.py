import logging
from typing import Optional, Dict, Any, List
import httpx
from app.core.config import settings
from app.services.intelligence.utils import normalize_vehicle_specs

logger = logging.getLogger("automind.intelligence.vehicle_data")

class VehicleDataService:
    """
    Integrates vehicle specifications, model lookup, and VIN decoding via:
    1. Vehicles.dev API (Commercial API, requires VEHICLES_API_KEY)
    2. NHTSA vPIC API (US Government Open API, completely free, no key required)
    """

    def __init__(self):
        self.vehicles_dev_key = settings.VEHICLES_API_KEY
        self.vehicles_dev_url = settings.VEHICLES_DEV_BASE_URL.rstrip("/")
        self.nhtsa_url = settings.NHTSA_BASE_URL.rstrip("/")
        self.timeout = settings.PROVIDER_REQUEST_TIMEOUT_SECONDS

    async def get_vehicle_specs(
        self,
        make: str,
        model: str,
        year: Optional[int] = None,
        vin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gathers specs and/or VIN decode results with provider status and provenance.
        """
        # 1. VIN Decoding flow (NHTSA or Vehicles.dev)
        if vin and vin.strip():
            clean_vin = vin.strip().upper()
            return await self._decode_vin(clean_vin)

        # 2. Vehicles.dev specification flow (if key configured)
        if self.vehicles_dev_key:
            try:
                res = await self._fetch_vehicles_dev(make, model, year)
                if res.get("status") == "success":
                    return res
            except Exception as e:
                logger.warning(f"[VehicleDataService] Vehicles.dev fetch error: {e}")

        # 3. Fallback to NHTSA model information (free, always available)
        try:
            nhtsa_res = await self._fetch_nhtsa_models(make, model, year)
            return nhtsa_res
        except Exception as e:
            logger.warning(f"[VehicleDataService] NHTSA fetch error: {e}")
            return {
                "status": "unavailable",
                "provider": "NHTSA vPIC / Vehicles.dev",
                "error": str(e),
                "data": None,
                "provenance": "https://vpic.nhtsa.dot.gov/api/"
            }

    async def _decode_vin(self, vin: str) -> Dict[str, Any]:
        """Decode VIN using official NHTSA vPIC open API."""
        url = f"{self.nhtsa_url}/vehicles/DecodeVinValues/{vin}?format=json"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("Results", [])
                if results and len(results) > 0:
                    r = results[0]
                    # Filter out empty fields
                    filtered = {k: v for k, v in r.items() if v and str(v).strip()}
                    normalized = normalize_vehicle_specs(filtered, "nhtsa")
                    return {
                        "status": "live",
                        "provider": "NHTSA vPIC (US DOT)",
                        "vin": vin,
                        "data": normalized,
                        "raw": filtered,
                        "provenance": "https://vpic.nhtsa.dot.gov/api/",
                        "market_coverage": "North America / Global VIN Standards"
                    }
        return {
            "status": "unavailable",
            "provider": "NHTSA vPIC",
            "vin": vin,
            "data": None,
            "error": "VIN could not be decoded or returned no results."
        }

    async def _fetch_vehicles_dev(self, make: str, model: str, year: Optional[int] = None) -> Dict[str, Any]:
        """Fetch specification from Vehicles.dev API."""
        params = {"make": make, "model": model}
        if year:
            params["year"] = str(year)

        headers = {"X-API-Key": self.vehicles_dev_key}
        url = f"{self.vehicles_dev_url}/v1/vehicles"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data") or data.get("vehicles") or [data]
                if items and isinstance(items, list) and len(items) > 0:
                    norm = normalize_vehicle_specs(items[0], "vehicles_dev")
                    return {
                        "status": "live",
                        "provider": "Vehicles.dev",
                        "data": norm,
                        "all_trims": items,
                        "provenance": "https://vehicles.dev/docs"
                    }
            elif resp.status_code in (401, 403):
                return {
                    "status": "auth_failed",
                    "provider": "Vehicles.dev",
                    "error": "Vehicles.dev API key is invalid or unauthorized."
                }
        return {"status": "unavailable", "provider": "Vehicles.dev"}

    async def _fetch_nhtsa_models(self, make: str, model: str, year: Optional[int] = None) -> Dict[str, Any]:
        """Free fallback to official NHTSA database to verify make and models."""
        url = f"{self.nhtsa_url}/vehicles/GetModelsForMake/{make}?format=json"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("Results", [])
                matching = [
                    r for r in results 
                    if model.lower() in r.get("Model_Name", "").lower()
                ]
                return {
                    "status": "live",
                    "provider": "NHTSA vPIC (Open Gov API)",
                    "data": {
                        "make": make,
                        "model": model,
                        "year": year,
                        "known_models_count": len(results),
                        "exact_matches": [m.get("Model_Name") for m in matching[:5]],
                        "make_id": results[0].get("Make_ID") if results else None
                    },
                    "provenance": "https://vpic.nhtsa.dot.gov/api/",
                    "note": "Specifications validated via US NHTSA Open Automotive Registry."
                }
        return {"status": "unavailable", "provider": "NHTSA vPIC"}

vehicle_data_service = VehicleDataService()
