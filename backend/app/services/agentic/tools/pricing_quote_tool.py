"""
AutoMind AI — Pricing Quote Agent Tool
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.agentic.tools.base import BaseAgentTool
from app.services.agentic.schemas import ToolResult, SourceReference, SourceType
from app.services.pricing.engine import PricingEngine
from app.schemas.pricing import PricingQuoteRequest

class PricingQuoteTool(BaseAgentTool):
    name = "calculate_pricing_quote"
    description = "Calculates itemized on-road price, RTO taxes, insurance, fees, and multi-tenure EMI options deterministically."

    def execute(
        self,
        db: Optional[Session] = None,
        city: Optional[str] = None,
        state_code: Optional[str] = None,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        variant: Optional[str] = None,
        fuel_type: str = "petrol",
        ex_showroom_price: Optional[float] = None,
        down_payment: Optional[float] = None,
        annual_interest_rate: float = 9.25,
        **kwargs
    ) -> ToolResult:
        try:
            engine = PricingEngine(db=db)
            req = PricingQuoteRequest(
                city=city,
                stateCode=state_code,
                manufacturer=manufacturer,
                model=model,
                variant=variant,
                fuelType=fuel_type,
                exShowroomPrice=ex_showroom_price,
                downPayment=down_payment,
                annualInterestRate=annual_interest_rate
            )
            quote = engine.generate_quote(req)
            data = quote.model_dump()

            source_ref = SourceReference(
                title=f"State RTO Slabs & Motor Vehicle Act ({quote.location.stateName})",
                url="https://parivahan.gov.in",
                domain="parivahan.gov.in",
                source_type=SourceType.LOCAL_RULE
            )

            return ToolResult(
                tool_name=self.name,
                success=True,
                data=data,
                sources=[source_ref],
                source_metadata={
                    "source": "AutoMind Local RTO & Pricing Rules Engine",
                    "rules_version": "2026.1",
                    "state": quote.location.stateCode
                }
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e),
                user_safe_error=f"Could not calculate quote: {str(e)}",
                warnings=["Unable to calculate pricing quote. Please check city and model parameters."]
            )

def execute_pricing_quote(
    db: Optional[Session] = None,
    city: Optional[str] = None,
    state_code: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    variant: Optional[str] = None,
    fuel_type: str = "petrol",
    ex_showroom_price: Optional[float] = None,
    down_payment: Optional[float] = None,
    annual_interest_rate: float = 9.25,
    **kwargs
) -> ToolResult:
    tool = PricingQuoteTool()
    return tool.execute(
        db=db,
        city=city,
        state_code=state_code,
        manufacturer=manufacturer,
        model=model,
        variant=variant,
        fuel_type=fuel_type,
        ex_showroom_price=ex_showroom_price,
        down_payment=down_payment,
        annual_interest_rate=annual_interest_rate,
        **kwargs
    )
