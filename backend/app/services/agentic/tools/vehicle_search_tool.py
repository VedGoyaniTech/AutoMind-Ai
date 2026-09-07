"""
AutoMind AI — Vehicle Search Agent Tool
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.services.agentic.tools.base import BaseAgentTool
from app.services.agentic.schemas import ToolResult, SourceReference, SourceType
from app.repositories.car_repo import CarRepository
from app.schemas.car import CarSearchFilter

class VehicleSearchTool(BaseAgentTool):
    name = "search_vehicles"
    description = "Searches structured database catalog for vehicles matching budget, fuel, body type, airbags, and manufacturer."

    def execute(
        self,
        db: Optional[Session] = None,
        query: Optional[str] = None,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        fuel_type: Optional[str] = None,
        body_type: Optional[str] = None,
        price_max: Optional[float] = None,
        price_min: Optional[float] = None,
        min_airbags: Optional[int] = None,
        seating_capacity: Optional[int] = None,
        **kwargs
    ) -> ToolResult:
        try:
            if db is not None:
                car_repo = CarRepository(db)
                filters = CarSearchFilter(
                    query=query or model,
                    manufacturer=manufacturer,
                    fuel_type=fuel_type,
                    body_type=body_type,
                    price_max=price_max,
                    price_min=price_min,
                    min_airbags=min_airbags,
                    seating_capacity=seating_capacity,
                    page=1,
                    page_size=8
                )
                variants, total = car_repo.search_variants(filters)
                vehicles_data = []
                sources = []
                for v in variants:
                    m_name = v.car_model.manufacturer.name if v.car_model and v.car_model.manufacturer else ""
                    mod_name = v.car_model.name if v.car_model else ""
                    vehicles_data.append({
                        "id": v.id,
                        "manufacturer": m_name,
                        "model": mod_name,
                        "variant": v.variant_name,
                        "price": v.ex_showroom_price,
                        "fuel_type": v.fuel_type,
                        "body_type": v.car_model.body_type if v.car_model else "",
                        "airbags": v.airbags,
                        "safety_rating": v.safety_rating,
                        "mileage": v.combined_mileage,
                        "electric_range": v.electric_range
                    })
                    if v.source:
                        sources.append(SourceReference(
                            title=f"{m_name} {mod_name} Official Catalog",
                            url=v.source.base_url or "https://automind.ai",
                            domain=v.source.domain or "automind.ai",
                            source_type=SourceType.LOCAL_DATABASE
                        ))

                exact_match = len(vehicles_data) == 1
                ambiguous = len(vehicles_data) > 1 and bool(model and not any(v.get("variant") == (kwargs.get("variant") or "") for v in vehicles_data))

                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={
                        "vehicles": vehicles_data,
                        "total_matches": total,
                        "exact_match": exact_match,
                        "ambiguous": ambiguous,
                        "suggested_choices": [f"{v['model']} {v['variant']}" for v in vehicles_data[:4]]
                    },
                    sources=sources[:4],
                    source_metadata={"source": "AutoMind Structured SQL Vehicle Catalog"}
                )
            else:
                # Fallback to Curated Baseline Models
                from app.services.pricing.engine import BASELINE_EX_SHOWROOM_PRICES
                matched = []
                for k, p in BASELINE_EX_SHOWROOM_PRICES.items():
                    if not query or query.lower() in k:
                        matched.append({"name": k.title(), "price": p, "manufacturer": k.title().split()[0]})

                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    data={"vehicles": matched[:6], "total_matches": len(matched)},
                    source_metadata={"source": "Curated Automotive Catalog"}
                )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e),
                user_safe_error=f"Vehicle search failed: {str(e)}"
            )

def execute_vehicle_search(
    db: Optional[Session] = None,
    query: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    fuel_type: Optional[str] = None,
    body_type: Optional[str] = None,
    price_max: Optional[float] = None,
    price_min: Optional[float] = None,
    min_airbags: Optional[int] = None,
    seating_capacity: Optional[int] = None,
    **kwargs
) -> ToolResult:
    tool = VehicleSearchTool()
    return tool.execute(
        db=db,
        query=query,
        manufacturer=manufacturer,
        model=model,
        fuel_type=fuel_type,
        body_type=body_type,
        price_max=price_max,
        price_min=price_min,
        min_airbags=min_airbags,
        seating_capacity=seating_capacity,
        **kwargs
    )
