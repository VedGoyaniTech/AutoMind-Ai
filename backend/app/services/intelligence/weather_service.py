import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import httpx
from app.core.config import settings

logger = logging.getLogger("automind.intelligence.weather")

WMO_WEATHER_CODES = {
    0: ("Clear Sky", "Optimal driving conditions. Full visibility."),
    1: ("Mainly Clear", "Good driving conditions. Dry roads."),
    2: ("Partly Cloudy", "Good visibility. Standard driving conditions."),
    3: ("Overcast", "Cloudy skies. Standard driving conditions."),
    45: ("Foggy", "Reduced visibility. Keep fog lights enabled and maintain braking distance."),
    48: ("Depositing Rime Fog", "Dense fog. Drive slowly with low beams."),
    51: ("Light Drizzle", "Slightly damp road surfaces. Exercise caution on turns."),
    53: ("Moderate Drizzle", "Wet road surfaces. Maintain safe following distance."),
    55: ("Dense Drizzle", "Slippery asphalt. Reduce highway cruising speeds."),
    61: ("Slight Rain", "Wet roads. Turn on wipers and test braking grip."),
    63: ("Moderate Rain", "Standing water possible. Watch for aquaplaning."),
    65: ("Heavy Rain", "Hazardous wet roads. Low visibility; keep hazard lights ready if stopped."),
    71: ("Slight Snow", "Slippery road conditions. Engage winter / snow driving mode."),
    73: ("Moderate Snow", "Challenging snow-covered roads. Low traction."),
    75: ("Heavy Snow", "Hazardous blizzard conditions. Avoid non-essential road travel."),
    80: ("Rain Showers", "Intermittent downpours. Expect sudden changes in tire grip."),
    95: ("Thunderstorm", "Severe thunderstorm. Park away from trees and waterlogged roads.")
}

class WeatherService:
    """
    Live Weather Integration via Open-Meteo:
    - Free, open public API without API key requirement
    - City geocoding + current meteorological telemetry
    - Real-time temperature (°C), precipitation, wind, humidity, and automotive driving advice.
    """

    def __init__(self):
        self.geocoding_url = settings.OPEN_METEO_GEOCODING_URL.rstrip("/")
        self.forecast_url = settings.OPEN_METEO_BASE_URL.rstrip("/")
        self.timeout = settings.PROVIDER_REQUEST_TIMEOUT_SECONDS

    async def get_city_weather(self, city: str = "Ahmedabad") -> Dict[str, Any]:
        """Fetches current weather for a city with driving implications."""
        clean_city = city.strip()
        try:
            # 1. Geocode city name to lat/lon
            coords = await self._geocode_city(clean_city)
            if not coords:
                return {
                    "status": "city_not_found",
                    "provider": "Open-Meteo",
                    "city": clean_city,
                    "error": f"Coordinates could not be resolved for city '{clean_city}'."
                }

            lat, lon, resolved_name, country = coords

            # 2. Fetch current weather from Open-Meteo
            params = {
                "latitude": str(lat),
                "longitude": str(lon),
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.forecast_url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    curr = data.get("current", {})
                    w_code = curr.get("weather_code", 0)
                    condition, driving_advice = WMO_WEATHER_CODES.get(
                        w_code, ("Normal", "Standard road conditions.")
                    )

                    return {
                        "status": "live",
                        "provider": "Open-Meteo (Open API)",
                        "city": resolved_name,
                        "country": country,
                        "coordinates": {"latitude": lat, "longitude": lon},
                        "temperature_celsius": curr.get("temperature_2m"),
                        "feels_like_celsius": curr.get("apparent_temperature"),
                        "relative_humidity_percent": curr.get("relative_humidity_2m"),
                        "precipitation_mm": curr.get("precipitation"),
                        "wind_speed_kmh": curr.get("wind_speed_10m"),
                        "weather_condition": condition,
                        "weather_code": w_code,
                        "driving_conditions": driving_advice,
                        "observation_time": curr.get("time") or datetime.now(timezone.utc).isoformat(),
                        "provenance": "https://open-meteo.com/en/docs"
                    }
                else:
                    return {
                        "status": "unavailable",
                        "provider": "Open-Meteo",
                        "city": clean_city,
                        "error": f"Open-Meteo returned status {resp.status_code}."
                    }
        except httpx.TimeoutException:
            logger.warning("[WeatherService] Open-Meteo request timed out.")
            return {
                "status": "timeout",
                "provider": "Open-Meteo",
                "city": clean_city,
                "error": f"Weather request timed out after {self.timeout}s."
            }
        except Exception as e:
            logger.error(f"[WeatherService] Weather error for {clean_city}: {e}", exc_info=True)
            return {
                "status": "unavailable",
                "provider": "Open-Meteo",
                "city": clean_city,
                "error": str(e)
            }

    async def _geocode_city(self, city: str) -> Optional[tuple[float, float, str, str]]:
        """Geocodes a city name into (lat, lon, resolved_name, country)."""
        # Hardcoded fast lookup for primary Indian hubs
        fast_coords = {
            "ahmedabad": (23.0225, 72.5714, "Ahmedabad", "India"),
            "mumbai": (19.0760, 72.8777, "Mumbai", "India"),
            "delhi": (28.6139, 77.2090, "Delhi", "India"),
            "new delhi": (28.6139, 77.2090, "New Delhi", "India"),
            "bangalore": (12.9716, 77.5946, "Bengaluru", "India"),
            "bengaluru": (12.9716, 77.5946, "Bengaluru", "India"),
            "pune": (18.5204, 73.8567, "Pune", "India"),
            "surat": (21.1702, 72.8311, "Surat", "India"),
            "vadodara": (22.3072, 73.1812, "Vadodara", "India"),
            "hyderabad": (17.3850, 78.4867, "Hyderabad", "India"),
            "chennai": (13.0827, 80.2707, "Chennai", "India"),
            "kolkata": (22.5726, 88.3639, "Kolkata", "India")
        }
        if city.lower() in fast_coords:
            return fast_coords[city.lower()]

        # Online geocoding via Open-Meteo Geocoding API
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(self.geocoding_url, params={"name": city, "count": "1"})
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    first = results[0]
                    return (
                        float(first["latitude"]),
                        float(first["longitude"]),
                        first.get("name", city),
                        first.get("country", "")
                    )
        return None

weather_service = WeatherService()
