"""
AutoMind AI — Reducing-Balance EMI & Auto-Loan Calculation Module
Implements standard banking reducing balance EMI equation:
  EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
"""

from typing import List, Dict, Any, Optional

def calculate_single_emi(
    principal: float,
    annual_interest_rate: float,
    tenure_years: int
) -> Dict[str, Any]:
    """
    Calculates EMI for a single tenure with zero-division safety.
    """
    if principal <= 0:
        return {
            "tenure_years": tenure_years,
            "tenure_months": tenure_years * 12,
            "monthly_emi": 0.0,
            "loan_principal": 0.0,
            "total_interest": 0.0,
            "total_payable": 0.0
        }

    n_months = tenure_years * 12

    # Zero-interest financing safety
    if annual_interest_rate <= 0:
        monthly_emi = round(principal / n_months, 2)
        return {
            "tenure_years": tenure_years,
            "tenure_months": n_months,
            "monthly_emi": monthly_emi,
            "loan_principal": round(principal, 2),
            "total_interest": 0.0,
            "total_payable": round(principal, 2)
        }

    r_monthly = (annual_interest_rate / 12.0) / 100.0
    factor = (1.0 + r_monthly) ** n_months
    monthly_emi = round((principal * r_monthly * factor) / (factor - 1.0), 2)
    total_payable = round(monthly_emi * n_months, 2)
    total_interest = round(total_payable - principal, 2)

    return {
        "tenure_years": tenure_years,
        "tenure_months": n_months,
        "monthly_emi": monthly_emi,
        "loan_principal": round(principal, 2),
        "total_interest": total_interest,
        "total_payable": total_payable
    }

def calculate_multi_tenure_emi_options(
    on_road_price: float,
    down_payment: Optional[float] = None,
    down_payment_pct: Optional[float] = None,
    loan_amount: Optional[float] = None,
    annual_interest_rate: float = 9.25,
    tenure_years_list: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Computes multi-tenure EMI comparison (defaults to 3, 5, and 7 years).
    """
    if on_road_price <= 0:
        raise ValueError("On-road price must be positive for loan financing.")

    # 1. Determine Down Payment and Loan Principal
    if loan_amount is not None and loan_amount > 0:
        if loan_amount > on_road_price:
            raise ValueError(f"Loan amount (₹{loan_amount:,.2f}) cannot exceed on-road price (₹{on_road_price:,.2f}).")
        principal = loan_amount
        actual_down_payment = on_road_price - loan_amount
    elif down_payment is not None:
        if down_payment < 0:
            raise ValueError("Down payment cannot be negative.")
        if down_payment > on_road_price:
            raise ValueError(f"Down payment (₹{down_payment:,.2f}) cannot exceed total on-road price (₹{on_road_price:,.2f}).")
        actual_down_payment = down_payment
        principal = on_road_price - down_payment
    elif down_payment_pct is not None:
        if not (0 <= down_payment_pct <= 100):
            raise ValueError("Down payment percentage must be between 0% and 100%.")
        actual_down_payment = round((on_road_price * down_payment_pct) / 100.0, 2)
        principal = on_road_price - actual_down_payment
    else:
        # Default to standard 20% down payment
        actual_down_payment = round(on_road_price * 0.20, 2)
        principal = on_road_price - actual_down_payment

    if tenure_years_list is None or not tenure_years_list:
        tenure_years_list = [3, 5, 7]

    emi_results = []
    for t in tenure_years_list:
        if t <= 0:
            continue
        opt = calculate_single_emi(
            principal=principal,
            annual_interest_rate=annual_interest_rate,
            tenure_years=t
        )
        emi_results.append(opt)

    down_payment_pct_val = round((actual_down_payment / on_road_price) * 100.0, 1) if on_road_price > 0 else 0.0

    return {
        "on_road_price": round(on_road_price, 2),
        "down_payment": round(actual_down_payment, 2),
        "down_payment_pct": down_payment_pct_val,
        "loan_principal": round(principal, 2),
        "annual_interest_rate": annual_interest_rate,
        "emi_options": emi_results
    }
