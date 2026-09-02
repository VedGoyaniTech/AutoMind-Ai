"""
AutoMind AI — On-Road Pricing & Loan EMI API Router
Exposes:
- POST /api/v1/pricing/on-road
- POST /api/v1/pricing/emi
- POST /api/v1/pricing/quote
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.pricing import (
    OnRoadPriceRequest, EMIRequest, PricingQuoteRequest, PricingQuoteResponse
)
from app.services.pricing.engine import PricingEngine
from app.services.pricing.emi import calculate_multi_tenure_emi_options

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pricing", tags=["On-Road Pricing & EMI Calculator"])

@router.post("/quote", response_model=PricingQuoteResponse)
def get_pricing_quote(
    payload: PricingQuoteRequest,
    db: Session = Depends(get_db)
):
    """
    Computes a comprehensive on-road price breakdown and multi-tenure EMI options
    for a given vehicle model and city/state.
    """
    try:
        engine = PricingEngine(db=db)
        return engine.generate_quote(payload)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err)
        )
    except Exception as err:
        logger.error(f"[PricingAPI] Quote calculation error: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute pricing quote. Please verify input parameters."
        )

@router.post("/on-road")
def get_on_road_price(
    payload: OnRoadPriceRequest,
    db: Session = Depends(get_db)
):
    """
    Computes only the on-road price breakdown (Ex-showroom, RTO, Insurance, TCS, FASTag, Cess).
    """
    try:
        engine = PricingEngine(db=db)
        quote_req = PricingQuoteRequest(
            manufacturer=payload.manufacturer,
            model=payload.model,
            variant=payload.variant,
            city=payload.city,
            stateCode=payload.stateCode,
            fuelType=payload.fuelType,
            exShowroomPrice=payload.exShowroomPrice,
            includeZeroDep=payload.includeZeroDep,
            includeDealerHandling=payload.includeDealerHandling
        )
        quote = engine.generate_quote(quote_req)
        return {
            "location": quote.location,
            "vehicle": quote.vehicle,
            "priceBreakdown": quote.priceBreakdown,
            "assumptions": quote.assumptions,
            "disclaimer": quote.disclaimer,
            "formattedSummary": quote.formattedSummary
        }
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as err:
        logger.error(f"[PricingAPI] On-road calculation error: {err}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate on-road price.")

@router.post("/emi")
def get_emi_options(payload: EMIRequest):
    """
    Computes multi-tenure reducing balance loan EMI options for a given on-road price and down payment.
    """
    try:
        return calculate_multi_tenure_emi_options(
            on_road_price=payload.onRoadPrice,
            down_payment=payload.downPayment,
            down_payment_pct=payload.downPaymentPct,
            loan_amount=payload.loanAmount,
            annual_interest_rate=payload.annualInterestRate,
            tenure_years_list=payload.tenuresYears
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as err:
        logger.error(f"[PricingAPI] EMI calculation error: {err}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate EMI.")
