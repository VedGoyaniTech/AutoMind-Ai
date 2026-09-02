"""
Vehicle Comparison Tool — Deterministic feature and pricing matrix builder.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.agentic.schemas import ToolExecutionResult
from app.services.pricing.engine import BASELINE_EX_SHOWROOM_PRICES

def execute_vehicle_comparison(
    car_a: str,
    car_b: str,
    db: Optional[Session] = None
) -> ToolExecutionResult:
    try:
        a_lower = car_a.lower()
        b_lower = car_b.lower()

        data_a = None
        data_b = None

        for k, v in BASELINE_EX_SHOWROOM_PRICES.items():
            if k in a_lower:
                data_a = v
            if k in b_lower:
                data_b = v

        if not data_a:
            data_a = {"mfg": "Auto A", "model": car_a, "variant": "Top", "price": 1200000.0, "fuel": "Petrol"}
        if not data_b:
            data_b = {"mfg": "Auto B", "model": car_b, "variant": "Top", "price": 1400000.0, "fuel": "Petrol"}

        matrix = {
            "car_a": data_a,
            "car_b": data_b,
            "price_difference": abs(data_a["price"] - data_b["price"]),
            "cheaper_model": data_a["model"] if data_a["price"] <= data_b["price"] else data_b["model"]
        }

        return ToolExecutionResult(
            tool_name="compare_vehicles",
            success=True,
            data=matrix
        )
    except Exception as e:
        return ToolExecutionResult(
            tool_name="compare_vehicles",
            success=False,
            error=str(e)
        )
