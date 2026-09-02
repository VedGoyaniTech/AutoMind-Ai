"""
Pricing Quote Tool — Deterministic local On-Road Price & EMI calculation.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.agentic.schemas import ToolExecutionResult
from app.services.pricing.engine import PricingEngine
from app.schemas.pricing import PricingQuoteRequest

def execute_pricing_quote(
    db: Optional[Session],
    city: Optional[str] = None,
    state_code: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    variant: Optional[str] = None,
    fuel_type: str = "petrol",
    ex_showroom_price: Optional[float] = None,
    down_payment: Optional[float] = None,
    annual_interest_rate: float = 9.25
) -> ToolExecutionResult:
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
        return ToolExecutionResult(
            tool_name="calculate_pricing_quote",
            success=True,
            data=quote.model_dump(),
            source_metadata={
                "source": "AutoMind Local RTO & Pricing Rules Engine",
                "rules_version": "2026.1",
                "state": quote.location.stateCode
            }
        )
    except Exception as e:
        return ToolExecutionResult(
            tool_name="calculate_pricing_quote",
            success=False,
            error=str(e),
            warnings=["Unable to calculate pricing quote. Please check city and model parameters."]
        )
