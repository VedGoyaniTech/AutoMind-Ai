"""
EMI Tool — Multi-tenure reducing balance loan calculator.
"""

from typing import Dict, Any, List, Optional
from app.services.agentic.schemas import ToolExecutionResult
from app.services.pricing.emi import calculate_multi_tenure_emi_options

def execute_emi_calculation(
    on_road_price: float,
    down_payment: Optional[float] = None,
    down_payment_pct: Optional[float] = None,
    annual_interest_rate: float = 9.25,
    tenures_years: Optional[List[int]] = None
) -> ToolExecutionResult:
    try:
        if tenures_years is None:
            tenures_years = [3, 5, 7]
        emi_res = calculate_multi_tenure_emi_options(
            on_road_price=on_road_price,
            down_payment=down_payment,
            down_payment_pct=down_payment_pct,
            annual_interest_rate=annual_interest_rate,
            tenure_years_list=tenures_years
        )
        return ToolExecutionResult(
            tool_name="calculate_emi",
            success=True,
            data=emi_res,
            source_metadata={"source": "Deterministic Reducing Balance Formula"}
        )
    except Exception as e:
        return ToolExecutionResult(
            tool_name="calculate_emi",
            success=False,
            error=str(e)
        )
