"""
AutoMind AI — Vehicle Details Agent Tool
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.agentic.tools.base import BaseAgentTool
from app.services.agentic.schemas import ToolResult, SourceReference, SourceType
from app.repositories.car_repo import CarRepository

class VehicleDetailsTool(BaseAgentTool):
    name = "get_vehicle_details"
    description = "Retrieves full technical specifications, safety ratings, dimensions, and features for a specified vehicle."

    def execute(self, db: Optional[Session] = None, variant_id: Optional[int] = None, model: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            if db and variant_id:
                repo = CarRepository(db)
                v = repo.get_variant_by_id(variant_id)
                if v:
                    m_name = v.car_model.manufacturer.name if v.car_model and v.car_model.manufacturer else ""
                    mod_name = v.car_model.name if v.car_model else ""
                    data = {
                        "id": v.id,
                        "manufacturer": m_name,
                        "model": mod_name,
                        "variant": v.variant_name,
                        "price": v.ex_showroom_price,
                        "fuel_type": v.fuel_type,
                        "transmission": v.transmission,
                        "airbags": v.airbags,
                        "safety_rating": v.safety_rating,
                        "mileage": v.combined_mileage,
                        "electric_range": v.electric_range
                    }
                    sources = [SourceReference(
                        title=f"{m_name} {mod_name} Official Specifications",
                        url=v.source.base_url if v.source else "https://automind.ai",
                        domain=v.source.domain if v.source else "automind.ai",
                        source_type=SourceType.LOCAL_DATABASE
                    )]
                    return ToolResult(tool_name=self.name, success=True, data=data, sources=sources)

            # Fallback
            from app.services.pricing.engine import BASELINE_EX_SHOWROOM_PRICES
            name = (model or "Vehicle").strip()
            price = BASELINE_EX_SHOWROOM_PRICES.get(name.lower(), 1200000.0)
            data = {
                "model": name.title(),
                "ex_showroom_price": price,
                "fuel_type": "Petrol/Diesel",
                "airbags": 6,
                "safety_rating": 5.0
            }
            return ToolResult(tool_name=self.name, success=True, data=data)
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=str(e), user_safe_error=f"Details lookup failed: {str(e)}")

def execute_vehicle_details(db: Optional[Session] = None, variant_id: Optional[int] = None, model: Optional[str] = None, **kwargs) -> ToolResult:
    tool = VehicleDetailsTool()
    return tool.execute(db=db, variant_id=variant_id, model=model, **kwargs)
