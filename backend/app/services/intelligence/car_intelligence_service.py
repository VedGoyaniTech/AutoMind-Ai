import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.intelligence import (
    CarIntelligenceCache,
    MarketListingSnapshot,
    MarketStatisticsSnapshot
)
from app.services.intelligence.vehicle_data_service import VehicleDataService
from app.services.intelligence.india_pricing_service import IndiaPricingService
from app.services.intelligence.vehicle_market_service import VehicleMarketService
from app.services.intelligence.vehicle_news_service import VehicleNewsService
from app.services.intelligence.weather_service import WeatherService
from app.services.intelligence.fuel_price_service import FuelPriceService
from app.services.intelligence.traffic_service import TrafficService
from app.services.ai.llm_provider import get_llm_provider

logger = logging.getLogger("automind.intelligence.master")


class CarIntelligenceService:
    """
    Unified Master Orchestrator for Real-Time AI Car Intelligence.
    Executes parallel federated lookups across all external providers:
    1. Vehicle Specifications & VIN Decoding (Vehicles.dev / NHTSA vPIC)
    2. Indian New-Car Statutory Pricing (AutoMind Deterministic Engine + IDSPay/MyNewCar audit)
    3. Used-Car Listings & Market Snapshots (DataForCars / India Partner Interface)
    4. Automotive News (NewsAPI)
    5. Live Weather & Driving Conditions (Open-Meteo)
    6. Indian Fuel Prices (IndianAPI / APIMitra)
    7. Traffic & Road Incidents (INRIX)
    8. Grounded AI Synthesis (AutoMind LLM Provider)
    """

    def __init__(self):
        self.vehicle_data_service = VehicleDataService()
        self.india_pricing_service = IndiaPricingService()
        self.market_service = VehicleMarketService()
        self.news_service = VehicleNewsService()
        self.weather_service = WeatherService()
        self.fuel_service = FuelPriceService()
        self.traffic_service = TrafficService()

    async def get_car_intelligence(
        self,
        make: str,
        model: str,
        year: Optional[int] = None,
        city: str = "Ahmedabad",
        vin: Optional[str] = None,
        db: Optional[Session] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Federates data collection from all providers, generates grounded AI synthesis,
        and caches results.
        """
        make_clean = make.strip().title()
        model_clean = model.strip()
        city_clean = city.strip().title() if city else "Ahmedabad"
        now_utc = datetime.now(timezone.utc)

        # 1. Check persistent database cache
        if db is not None and not force_refresh:
            cached_entry = self._check_cache(db, make_clean, model_clean, year, city_clean)
            if cached_entry:
                logger.info(f"[CarIntelligence] Cache hit for {make_clean} {model_clean} ({city_clean})")
                cached_data = cached_entry.payload.copy() if isinstance(cached_entry.payload, dict) else json.loads(cached_entry.payload)
                cached_data["metadata"]["is_cached"] = True
                cached_data["metadata"]["cached_at"] = cached_entry.created_at.isoformat() if cached_entry.created_at else now_utc.isoformat()
                cached_data["metadata"]["expires_at"] = cached_entry.expires_at.isoformat() if cached_entry.expires_at else None
                return cached_data

        # 2. Fire concurrent external provider requests with individual timeouts
        tasks = [
            self.vehicle_data_service.get_vehicle_specs(make=make_clean, model=model_clean, year=year, vin=vin),
            self.india_pricing_service.get_pricing_data(model=model_clean, city=city_clean, make=make_clean, year=year),
            self.market_service.get_market_data(make=make_clean, model=model_clean, year=year, city=city_clean),
            self.news_service.get_car_news(make=make_clean, model=model_clean),
            self.weather_service.get_city_weather(city=city_clean),
            self.fuel_service.get_fuel_prices(city=city_clean),
            self.traffic_service.get_city_traffic(city=city_clean)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        specs_res = self._format_result(results[0], "Vehicle Specifications", "NHTSA / Vehicles.dev")
        pricing_res = self._format_result(results[1], "Indian Pricing", "AutoMind Statutory Engine")
        market_res = self._format_result(results[2], "Used Car Market", "DataForCars")
        news_res = self._format_result(results[3], "Automotive News", "NewsAPI")
        weather_res = self._format_result(results[4], "Live Weather", "Open-Meteo")
        fuel_res = self._format_result(results[5], "Fuel Prices", "IndianAPI / APIMitra")
        traffic_res = self._format_result(results[6], "Traffic Conditions", "INRIX")

        # 3. Generate Grounded AI Synthesis
        ai_analysis = await self._generate_grounded_summary(
            make=make_clean,
            model=model_clean,
            year=year,
            city=city_clean,
            specs=specs_res,
            pricing=pricing_res,
            market=market_res,
            news=news_res,
            weather=weather_res,
            fuel=fuel_res,
            traffic=traffic_res
        )

        # 4. Construct unified payload
        payload = {
            "query": {
                "make": make_clean,
                "model": model_clean,
                "year": year,
                "city": city_clean,
                "vin": vin
            },
            "specifications": specs_res,
            "india_pricing": pricing_res,
            "market_data": market_res,
            "news": news_res,
            "weather": weather_res,
            "fuel": fuel_res,
            "traffic": traffic_res,
            "ai_analysis": ai_analysis,
            "metadata": {
                "is_cached": False,
                "fetched_at": now_utc.isoformat(),
                "data_sources": {
                    "specifications": {
                        "provider": specs_res.get("provider", "NHTSA / Vehicles.dev"),
                        "status": specs_res.get("status"),
                        "last_updated": specs_res.get("last_updated") or specs_res.get("fetched_at")
                    },
                    "pricing": {
                        "provider": pricing_res.get("provider", "AutoMind Statutory Pricing Engine"),
                        "status": pricing_res.get("status"),
                        "last_updated": pricing_res.get("last_updated")
                    },
                    "market": {
                        "provider": market_res.get("provider", "DataForCars"),
                        "status": market_res.get("status"),
                        "currency": market_res.get("currency", "USD"),
                        "last_updated": market_res.get("last_updated")
                    },
                    "news": {
                        "provider": news_res.get("provider", "NewsAPI"),
                        "status": news_res.get("status"),
                        "article_count": len(news_res.get("articles", [])),
                        "last_updated": news_res.get("last_updated")
                    },
                    "weather": {
                        "provider": weather_res.get("provider", "Open-Meteo"),
                        "status": weather_res.get("status"),
                        "last_updated": weather_res.get("last_updated")
                    },
                    "fuel": {
                        "provider": fuel_res.get("provider", "IndianAPI / APIMitra"),
                        "status": fuel_res.get("status"),
                        "last_updated": fuel_res.get("last_updated")
                    },
                    "traffic": {
                        "provider": traffic_res.get("provider", "INRIX"),
                        "status": traffic_res.get("status"),
                        "last_updated": traffic_res.get("last_updated")
                    }
                }
            }
        }

        # 5. Persist to cache and snapshot tables
        if db is not None:
            try:
                self._save_cache(db, make_clean, model_clean, year, city_clean, payload)
                self._save_market_snapshots(db, make_clean, model_clean, year, market_res)
            except Exception as e:
                logger.warning(f"[CarIntelligence] Database persistence error: {e}")

        return payload

    def _format_result(self, result: Any, section_name: str, fallback_provider: str) -> Dict[str, Any]:
        """Ensures that any failed or unhandled task produces a safe, structured dictionary."""
        if isinstance(result, Exception):
            logger.error(f"[CarIntelligence] Error in {section_name}: {result}")
            return {
                "status": "error",
                "provider": fallback_provider,
                "error": str(result),
                "data": None,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        if isinstance(result, dict):
            return result
        return {
            "status": "unavailable",
            "provider": fallback_provider,
            "data": None,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

    async def _generate_grounded_summary(
        self,
        make: str,
        model: str,
        year: Optional[int],
        city: str,
        specs: Dict[str, Any],
        pricing: Dict[str, Any],
        market: Dict[str, Any],
        news: Dict[str, Any],
        weather: Dict[str, Any],
        fuel: Dict[str, Any],
        traffic: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Uses the existing AutoMind Grounded LLM provider to synthesize an executive
        intelligence briefing. STRICTLY grounded in verified data: no hallucinated specs or prices.
        """
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Extract verified facts
        specs_data = specs.get("specs") or specs.get("data") or {}
        specs_status = specs.get("status")
        
        price_types = pricing.get("price_types") or {}
        breakdown = pricing.get("breakdown") or {}
        ex_showroom_inr = price_types.get("ex_showroom", {}).get("amount") or breakdown.get("exShowroomPrice")
        on_road_inr = price_types.get("estimated_on_road", {}).get("amount") or breakdown.get("onRoadPrice")
        emi_options = pricing.get("emi_options") or []
        emi_inr = emi_options[0].get("monthlyEMI") if emi_options else None
        
        market_stats = market.get("statistics") or {}
        market_count = market_stats.get("listing_count", 0)
        market_currency = market_stats.get("currency", "USD")
        market_median = market_stats.get("median_price")

        temp_c = weather.get("temperature_celsius")
        weather_cond = weather.get("weather_condition")
        driving_advice = weather.get("driving_conditions", "")

        fuel_prices = fuel.get("prices") or {}
        petrol_price = fuel_prices.get("petrol", {}).get("price")
        diesel_price = fuel_prices.get("diesel", {}).get("price")

        news_articles = news.get("articles") or []
        top_headlines = [a.get("title") for a in news_articles[:3] if a.get("title")]

        traffic_status = traffic.get("status")

        # Build context block
        context_lines = [
            f"TARGET VEHICLE: {year or ''} {make} {model}".strip(),
            f"CITY/LOCATION: {city}",
            f"REPORT TIMESTAMP: {now_str}",
            "",
            "--- VERIFIED DATA SOURCES ---",
            f"1. SPECIFICATIONS (Provider: {specs.get('provider')}, Status: {specs_status}):",
            f"   Details: {json.dumps(specs_data) if specs_data else 'No specific dimensional data available.'}",
            "",
            f"2. INDIAN STATUTORY PRICING (City: {city}, Status: {pricing.get('status')}):",
            f"   Ex-Showroom: ₹{ex_showroom_inr:,.2f}" if ex_showroom_inr else "   Ex-Showroom: Data pending",
            f"   Estimated On-Road ({city}): ₹{on_road_inr:,.2f}" if on_road_inr else "   Estimated On-Road: Data pending",
            f"   Indicative Monthly EMI: ₹{emi_inr:,.2f}/mo (5yr @ 9.25%)" if emi_inr else "   Indicative EMI: N/A",
            "",
            f"3. MARKET LISTINGS & STATISTICS (Provider: {market.get('provider')}, Coverage: {market.get('geographic_coverage')}):",
            f"   Listing Count: {market_count} active listings found",
            f"   Median Asking Price: {market_currency} {market_median:,.2f}" if market_median else f"   Median Asking Price: None ({market.get('note', 'No active listings')})",
            "   CRITICAL NOTE: DataForCars covers North America (USD). Do NOT mix USD asking prices with Indian INR prices.",
            "",
            f"4. LOCAL WEATHER IN {city.upper()} (Provider: Open-Meteo, Status: {weather.get('status')}):",
            f"   Temperature: {temp_c}°C, Condition: {weather_cond}" if temp_c is not None else "   Weather: Live observation unavailable",
            f"   Driving Condition Advice: {driving_advice}",
            "",
            f"5. FUEL PRICES IN {city.upper()} (Provider: IndianAPI, Status: {fuel.get('status')}):",
            f"   Petrol: ₹{petrol_price}/L" if petrol_price else "   Petrol: Live rate unconfigured/unavailable",
            f"   Diesel: ₹{diesel_price}/L" if diesel_price else "   Diesel: Live rate unconfigured/unavailable",
            "",
            f"6. TRAFFIC STATUS (Provider: INRIX, Status: {traffic_status}):",
            f"   {traffic.get('note', 'Traffic telemetry not configured.')}",
            "",
            f"7. LATEST CAR NEWS (Provider: NewsAPI, Status: {news.get('status')}):",
            f"   Headlines: {'; '.join(top_headlines) if top_headlines else 'No recent articles found.'}"
        ]

        context_str = "\n".join(context_lines)

        prompt = (
            "You are AutoMind Car Intelligence AI. Summarize the real-world status of the requested vehicle based ONLY on the provided verified data.\n"
            "STRICT RULES:\n"
            "1. NEVER invent, guess, or extrapolate car prices, used listings, fuel prices, or news if they are unavailable or unconfigured.\n"
            "2. If an external API is not configured or unavailable, state that fact clearly.\n"
            "3. Clearly distinguish Indian new car on-road prices (INR) from US used car market stats (USD).\n"
            "4. Provide a structured 3-paragraph executive briefing: (1) Vehicle & Indian Pricing Snapshot, (2) Market & Environmental Readiness in the selected city, and (3) Strategic Buyer Takeaway."
        )

        try:
            llm = get_llm_provider()
            generated_text = llm.generate(prompt=prompt, context=context_str)
            summary_content = generated_text.strip() if generated_text else self._deterministic_fallback_summary(
                make, model, year, city, ex_showroom_inr, on_road_inr, emi_inr, temp_c, weather_cond, driving_advice, petrol_price
            )
        except Exception as e:
            logger.warning(f"[CarIntelligence] LLM generation fallback triggered: {e}")
            summary_content = self._deterministic_fallback_summary(
                make, model, year, city, ex_showroom_inr, on_road_inr, emi_inr, temp_c, weather_cond, driving_advice, petrol_price
            )

        return {
            "summary": summary_content,
            "provider": "AutoMind Grounded LLM",
            "grounded_facts_count": 7,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def _deterministic_fallback_summary(
        self,
        make: str,
        model: str,
        year: Optional[int],
        city: str,
        ex_showroom: Optional[float],
        on_road: Optional[float],
        emi: Optional[float],
        temp: Optional[float],
        weather: Optional[str],
        advice: str,
        petrol: Optional[float]
    ) -> str:
        """Reliable, factual fallback summary when LLM generation is unavailable."""
        car_name = f"{year or ''} {make} {model}".strip()
        p1 = f"The **{car_name}** has been analyzed with AutoMind's verified intelligence telemetry for **{city}**."
        if on_road and ex_showroom:
            p1 += f" Based on official statutory tax calculations for your region, the ex-showroom price is estimated at **₹{ex_showroom:,.2f}**, resulting in an estimated on-road price of **₹{on_road:,.2f}** (with an estimated 5-year EMI of **₹{emi:,.2f}/month**)."
        else:
            p1 += " Specific on-road tax calculations are currently being finalized for this configuration."

        p2 = f"Local conditions in **{city}** currently report "
        if temp is not None:
            p2 += f"a temperature of **{temp}°C** ({weather or 'Fair'}). {advice} "
        else:
            p2 += "weather telemetry as pending. "

        if petrol:
            p2 += f"Current verified petrol rates in the city stand at **₹{petrol}/L**."
        else:
            p2 += "Live city fuel rate feeds are currently unconfigured or pending provider confirmation."

        p3 = "Buyer Takeaway: North American used market data via DataForCars is segregated in USD and not mixed with domestic Indian figures. Please review the official specification sheets and dealer quotes before making financial commitments."

        return f"{p1}\n\n{p2}\n\n{p3}"

    def _check_cache(
        self,
        db: Session,
        make: str,
        model: str,
        year: Optional[int],
        city: str
    ) -> Optional[CarIntelligenceCache]:
        """Checks if valid unexpired cached intelligence exists in DB."""
        cache_key = f"all:{make.lower()}:{model.lower()}:{year or ''}:{city.lower()}"
        now = datetime.now(timezone.utc)
        return db.query(CarIntelligenceCache).filter(
            CarIntelligenceCache.cache_key == cache_key,
            CarIntelligenceCache.expires_at > now
        ).order_by(CarIntelligenceCache.created_at.desc()).first()

    def _save_cache(
        self,
        db: Session,
        make: str,
        model: str,
        year: Optional[int],
        city: str,
        payload: Dict[str, Any]
    ) -> None:
        """Stores or updates the intelligence cache record."""
        cache_key = f"all:{make.lower()}:{model.lower()}:{year or ''}:{city.lower()}"
        ttl_seconds = settings.INTELLIGENCE_CACHE_TTL_SECONDS
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)

        cache_entry = db.query(CarIntelligenceCache).filter(
            CarIntelligenceCache.cache_key == cache_key
        ).first()

        if cache_entry:
            cache_entry.payload = payload
            cache_entry.expires_at = expires_at
            cache_entry.updated_at = now
        else:
            cache_entry = CarIntelligenceCache(
                cache_key=cache_key,
                provider="all",
                payload=payload,
                expires_at=expires_at,
                created_at=now,
                updated_at=now
            )
            db.add(cache_entry)
        db.commit()

    def _save_market_snapshots(
        self,
        db: Session,
        make: str,
        model: str,
        year: Optional[int],
        market_res: Dict[str, Any]
    ) -> None:
        """Stores historical market listings and statistical aggregates when listings are present."""
        listings = market_res.get("listings") or []
        stats = market_res.get("statistics") or {}
        now = datetime.now(timezone.utc)

        if stats and stats.get("listing_count", 0) > 0:
            stat_snapshot = MarketStatisticsSnapshot(
                make=make,
                model=model,
                year=year,
                currency=stats.get("currency", "USD"),
                total_listings=stats.get("listing_count", 0),
                min_price=stats.get("min_price"),
                max_price=stats.get("max_price"),
                average_price=stats.get("average_price"),
                median_price=stats.get("median_price"),
                average_mileage=stats.get("avg_mileage"),
                price_distribution=stats.get("price_distribution"),
                observation_date=now,
                created_at=now
            )
            db.add(stat_snapshot)

        for l in listings[:20]:  # Limit top 20 snapshots per query
            listing_snapshot = MarketListingSnapshot(
                make=make,
                model=model,
                year=l.get("year") or year,
                price=l.get("price", 0.0),
                currency=l.get("currency", "USD"),
                is_asking_price=True,
                mileage=l.get("mileage"),
                mileage_unit=l.get("mileage_unit", "miles"),
                listing_url=l.get("url"),
                source_provider=market_res.get("provider", "DataForCars"),
                created_at=now
            )
            db.add(listing_snapshot)

        db.commit()
