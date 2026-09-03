"""
AutoMind AI — Reducing-Balance EMI Agent Tool
"""

from typing import Dict, Any, Optional, List
from app.services.agentic.tools.base import BaseAgentTool
from app.services.agentic.schemas import ToolResult
from app.services.pricing.emi import calculate_multi_tenure_emi_options

class EMITool(BaseAgentTool):
    name = "calculate_emi"
    description = "Calculates reducing-balance monthly loan installments, principal, interest, and multi-tenure tables."

    def execute(
        self,
        on_road_price: float,
        down_payment: Optional[float] = None,
        down_payment_percent: Optional[float] = None,
        annual_interest_rate: float = 9.25,
        tenures_years: Optional[List[int]] = None,
        **kwargs
    ) -> ToolResult:
        try:
            if tenures_years is None:
                tenures_years = [3, 5, 7]

            res = calculate_multi_tenure_emi_options(
                on_road_price=on_road_price,
                down_payment=down_payment,
                down_payment_pct=down_payment_percent,
                annual_interest_rate=annual_interest_rate,
                tenure_years_list=tenures_years
            )

            return ToolResult(
                tool_name=self.name,
                success=True,
                data=res,
                source_metadata={"source": "AutoMind Reducing-Balance EMI Formula"}
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e),
                user_safe_error=f"Could not calculate EMI: {str(e)}",
                warnings=["Unable to calculate EMI due to parameter constraints."]
            )

def execute_emi_calculation(
    on_road_price: float,
    down_payment: Optional[float] = None,
    down_payment_percent: Optional[float] = None,
    annual_interest_rate: float = 9.25,
    tenures_years: Optional[List[int]] = None,
    **kwargs
) -> ToolResult:
    tool = EMITool()
    return tool.execute(
        on_road_price=on_road_price,
        down_payment=down_payment,
        down_payment_percent=down_payment_percent,
        annual_interest_rate=annual_interest_rate,
        tenures_years=tenures_years,
        **kwargs
    )
