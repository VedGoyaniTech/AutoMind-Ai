import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.intelligence.utils import calculate_market_statistics, normalize_vehicle_specs
from app.services.intelligence.vehicle_data_service import VehicleDataService
from app.services.intelligence.india_pricing_service import IndiaPricingService
from app.services.intelligence.vehicle_market_service import VehicleMarketService
from app.services.intelligence.weather_service import WeatherService
from app.services.intelligence.fuel_price_service import FuelPriceService
from app.services.intelligence.vehicle_news_service import VehicleNewsService
from app.services.intelligence.car_intelligence_service import CarIntelligenceService


def test_calculate_market_statistics_empty():
    stats = calculate_market_statistics([], currency="USD")
    assert stats["total_listings"] == 0
    assert stats["currency"] == "USD"
    assert stats["min_asking_price"] is None
    assert stats["max_asking_price"] is None
    assert stats["median_asking_price"] is None
    assert stats["trend_indicator"] == "insufficient_data"
    assert "asking prices" in stats["market_disclaimer"].lower()


def test_calculate_market_statistics_populated():
    listings = [
        {"price": 20000, "mileage": 30000},
        {"price": 22000, "mileage": 25000},
        {"price": 25000, "mileage": 20000},
        {"price": 30000, "mileage": 15000},
        {"price": 35000, "mileage": 10000},
    ]
    stats = calculate_market_statistics(listings, currency="USD")
    assert stats["total_listings"] == 5
    assert stats["min_asking_price"] == 20000.0
    assert stats["max_asking_price"] == 35000.0
    assert stats["median_asking_price"] == 25000.0
    assert stats["average_asking_price"] == 26400.0
    assert stats["mileage_statistics"]["average"] == 20000.0
    assert "price_distribution" in stats
    assert "asking prices" in stats["market_disclaimer"].lower()


def test_normalize_vehicle_specs():
    raw_nhtsa = {
        "Make": "Toyota",
        "Model": "Fortuner",
        "ModelYear": 2024,
        "BodyClass": "Sport Utility Vehicle (SUV)"
    }
    normalized_nhtsa = normalize_vehicle_specs(raw_nhtsa, provider="nhtsa")
    assert normalized_nhtsa["make"] == "Toyota"
    assert normalized_nhtsa["model"] == "Fortuner"
    assert normalized_nhtsa["model_year"] == 2024
    assert normalized_nhtsa["body_class"] == "Sport Utility Vehicle (SUV)"

    raw_vdev = {
        "make": "Toyota",
        "model": "Fortuner",
        "year": 2024,
        "body_type": "SUV",
        "horsepower": 201
    }
    normalized_vdev = normalize_vehicle_specs(raw_vdev, provider="vehicles_dev")
    assert normalized_vdev["make"] == "Toyota"
    assert normalized_vdev["body_type"] == "SUV"
    assert normalized_vdev["horsepower"] == 201


def test_india_pricing_service():
    async def _run():
        service = IndiaPricingService()
        res = await service.get_pricing_data(
            model="Fortuner",
            city="Ahmedabad",
            make="Toyota"
        )
        assert res["status"] == "live_statutory_engine"
        assert res["city"] == "Ahmedabad"
        assert res["state_code"] == "GJ"
        assert res["currency"] == "INR"
        assert res["price_types"]["ex_showroom"]["amount"] > 0
        assert res["price_types"]["estimated_on_road"]["amount"] > res["price_types"]["ex_showroom"]["amount"]
        assert len(res["emi_options"]) > 0
        # Audit check: IDSPay and MyNewCar marked requires_commercial_agreement
        assert res["commercial_provider_audit"]["idspay"]["status"] == "requires_commercial_agreement"
        assert res["commercial_provider_audit"]["mynewcar"]["status"] == "requires_commercial_agreement"
    asyncio.run(_run())


def test_vehicle_market_service_unconfigured():
    async def _run():
        with patch("app.services.intelligence.vehicle_market_service.settings.DATAFORCARS_API_KEY", ""):
            service = VehicleMarketService()
            res = await service.get_market_data(make="Toyota", model="RAV4", year=2022)
            assert res["status"] == "not_configured"
            assert res["provider"] == "DataForCars"
            assert res["statistics"]["currency"] == "USD"
            assert "DATAFORCARS_API_KEY" in res["note"]
    asyncio.run(_run())


def test_weather_service_mocked():
    async def _run():
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "current": {
                "temperature_2m": 32.5,
                "apparent_temperature": 34.0,
                "relative_humidity_2m": 55,
                "precipitation": 0.0,
                "wind_speed_10m": 12.0,
                "weather_code": 0,
                "time": "2026-10-01T12:00"
            }
        }
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            service = WeatherService()
            res = await service.get_city_weather("Ahmedabad")
            assert res["status"] == "live"
            assert res["temperature_celsius"] == 32.5
            assert res["weather_condition"] == "Clear Sky"
            assert "Optimal driving conditions" in res["driving_conditions"]
    asyncio.run(_run())


def test_fuel_price_service_unconfigured():
    async def _run():
        with patch("app.services.intelligence.fuel_price_service.settings.FUEL_API_KEY", ""):
            service = FuelPriceService()
            res = await service.get_fuel_prices("Ahmedabad")
            assert res["status"] == "not_configured"
            assert res["city"] == "Ahmedabad"
            assert "FUEL_API_KEY is not configured" in res["note"]
    asyncio.run(_run())


def test_news_service_unconfigured():
    async def _run():
        with patch("app.services.intelligence.vehicle_news_service.settings.NEWSAPI_KEY", ""):
            service = VehicleNewsService()
            res = await service.get_car_news("Toyota", "Fortuner")
            assert res["status"] == "not_configured"
            assert res["count"] == 0
            assert "NEWSAPI_KEY is not configured" in res["note"]
    asyncio.run(_run())


def test_car_intelligence_service_orchestrator():
    async def _run():
        service = CarIntelligenceService()
        res = await service.get_car_intelligence(
            make="Toyota",
            model="Fortuner",
            year=2024,
            city="Ahmedabad"
        )
        assert "query" in res
        assert res["query"]["make"] == "Toyota"
        assert res["query"]["model"] == "Fortuner"
        assert "specifications" in res
        assert "india_pricing" in res
        assert "market_data" in res
        assert "news" in res
        assert "weather" in res
        assert "fuel" in res
        assert "traffic" in res
        assert "ai_analysis" in res
        assert "metadata" in res
        assert res["metadata"]["is_cached"] is False
        assert len(res["ai_analysis"]["summary"]) > 50
    asyncio.run(_run())


def test_cars_intelligence_endpoint(client):
    response = client.get("/api/v1/cars/intelligence?make=Toyota&model=Fortuner&year=2024&city=Ahmedabad")
    assert response.status_code == 200
    data = response.json()
    assert data["query"]["make"] == "Toyota"
    assert data["query"]["model"] == "Fortuner"
    assert data["india_pricing"]["status"] == "live_statutory_engine"
    assert "ai_analysis" in data
    assert "metadata" in data
    assert "data_sources" in data["metadata"]
