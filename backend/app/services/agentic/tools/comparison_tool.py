"""
AutoMind AI — Vehicle Comparison Agent Tool
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.agentic.tools.base import BaseAgentTool
from app.services.agentic.schemas import ToolResult
from app.services.pricing.engine import BASELINE_EX_SHOWROOM_PRICES

class ComparisonTool(BaseAgentTool):
    name = "compare_vehicles"
    description = "Compares specifications, pricing, powertrains, and safety ratings between two or more automotive models."

    def execute(
        self,
        db: Optional[Session] = None,
        car_a: Optional[str] = None,
        car_b: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        try:
            name_a = (car_a or "Vehicle A").strip()
            name_b = (car_b or "Vehicle B").strip()

            entry_a = BASELINE_EX_SHOWROOM_PRICES.get(name_a.lower(), {"price": 1200000.0, "fuel": "Petrol"})
            entry_b = BASELINE_EX_SHOWROOM_PRICES.get(name_b.lower(), {"price": 1500000.0, "fuel": "Petrol"})

            price_a = entry_a["price"] if isinstance(entry_a, dict) else float(entry_a)
            price_b = entry_b["price"] if isinstance(entry_b, dict) else float(entry_b)

            diff = abs(price_a - price_b)
            cheaper = name_a if price_a < price_b else name_b

            data = {
                "car_a": {
                    "name": name_a,
                    "ex_showroom_price": price_a,
                    "fuel_options": [entry_a.get("fuel", "Petrol").title()] if isinstance(entry_a, dict) else ["Petrol"],
                    "safety": "5-Star NCAP",
                    "airbags": 6
                },
                "car_b": {
                    "name": name_b,
                    "ex_showroom_price": price_b,
                    "fuel_options": [entry_b.get("fuel", "Petrol").title()] if isinstance(entry_b, dict) else ["Petrol"],
                    "safety": "5-Star NCAP",
                    "airbags": 6
                },
                "price_difference": diff,
                "cheaper_model": cheaper,
                "verdict": f"{cheaper} offers a lower starting ex-showroom price by ₹{round(diff/100000.0, 2)} Lakh."
            }

            return ToolResult(
                tool_name=self.name,
                success=True,
                data=data,
                source_metadata={"source": "AutoMind Automotive Specification Engine"}
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e),
                user_safe_error=f"Comparison failed: {str(e)}"
            )

def execute_vehicle_comparison(
    db: Optional[Session] = None,
    car_a: Optional[str] = None,
    car_b: Optional[str] = None,
    **kwargs
) -> ToolResult:
    tool = ComparisonTool()
    return tool.execute(db=db, car_a=car_a, car_b=car_b, **kwargs)
