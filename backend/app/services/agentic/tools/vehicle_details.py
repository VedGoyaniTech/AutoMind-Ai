"""
Vehicle Details Tool — Retrieve detailed technical specifications.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.agentic.schemas import ToolExecutionResult
from app.models.car import CarVariant, CarModel, Manufacturer

def execute_vehicle_details(
    model_name: str,
    db: Optional[Session] = None
) -> ToolExecutionResult:
    try:
        if db:
            m = db.query(CarModel).filter(CarModel.name.ilike(f"%{model_name}%")).first()
            if m and m.variants:
                v = m.variants[0]
                return ToolExecutionResult(
                    tool_name="get_vehicle_details",
                    success=True,
                    data={
                        "model": m.name,
                        "manufacturer": m.manufacturer.name if m.manufacturer else "Unknown",
                        "segment": m.segment,
                        "body_type": m.body_type,
                        "ex_showroom_price": v.ex_showroom_price,
                        "fuel_type": v.fuel_type,
                        "engine_cc": v.engine_cc,
                        "airbags": v.airbags,
                        "safety_rating": v.safety_rating
                    }
                )
        return ToolExecutionResult(
            tool_name="get_vehicle_details",
            success=True,
            data={
                "model": model_name,
                "specs": "Standard local catalog specifications available."
            }
        )
    except Exception as e:
        return ToolExecutionResult(
            tool_name="get_vehicle_details",
            success=False,
            error=str(e)
        )
