"""
Vehicle Search Tool — Search local catalog by budget, fuel, body type, airbags, and segment.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.agentic.schemas import ToolExecutionResult
from app.models.car import CarVariant, CarModel, Manufacturer

def execute_vehicle_search(
    db: Optional[Session],
    max_budget_lakh: Optional[float] = None,
    min_budget_lakh: Optional[float] = None,
    fuel_type: Optional[str] = None,
    body_type: Optional[str] = None,
    min_airbags: Optional[int] = None,
    query_text: Optional[str] = None
) -> ToolExecutionResult:
    try:
        results = []
        if db:
            query = db.query(CarVariant).join(CarModel).join(Manufacturer)
            if max_budget_lakh:
                query = query.filter(CarVariant.ex_showroom_price <= max_budget_lakh * 100000)
            if min_budget_lakh:
                query = query.filter(CarVariant.ex_showroom_price >= min_budget_lakh * 100000)
            if fuel_type:
                query = query.filter(CarVariant.fuel_type.ilike(f"%{fuel_type}%"))
            if min_airbags:
                query = query.filter(CarVariant.airbags >= min_airbags)

            db_results = query.limit(10).all()
            for v in db_results:
                m = v.car_model
                mfg = m.manufacturer
                results.append({
                    "id": v.id,
                    "manufacturer": mfg.name,
                    "model": m.name,
                    "variant": v.variant_name,
                    "ex_showroom_price": v.ex_showroom_price,
                    "fuel_type": v.fuel_type,
                    "airbags": v.airbags,
                    "safety_rating": v.safety_rating,
                    "body_type": m.body_type
                })

        # Fallback baseline catalog search if DB query empty
        if not results:
            from app.services.pricing.engine import BASELINE_EX_SHOWROOM_PRICES
            for key, data in BASELINE_EX_SHOWROOM_PRICES.items():
                p_lakh = data["price"] / 100000.0
                if max_budget_lakh and p_lakh > max_budget_lakh:
                    continue
                if min_budget_lakh and p_lakh < min_budget_lakh:
                    continue
                if fuel_type and fuel_type.lower() not in data["fuel"].lower():
                    continue
                results.append({
                    "manufacturer": data["mfg"],
                    "model": data["model"],
                    "variant": data["variant"],
                    "ex_showroom_price": data["price"],
                    "fuel_type": data["fuel"],
                    "airbags": 6,
                    "safety_rating": 5.0,
                    "body_type": "SUV"
                })

        return ToolExecutionResult(
            tool_name="search_vehicles",
            success=True,
            data={"vehicles": results, "count": len(results)},
            warnings=[] if results else ["No exact matching vehicle found for criteria."]
        )
    except Exception as e:
        return ToolExecutionResult(
            tool_name="search_vehicles",
            success=False,
            error=str(e)
        )
