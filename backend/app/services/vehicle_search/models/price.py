"""
Vehicle Search Models — Pricing Schema Definitions
"""

from pydantic import BaseModel, Field


class PriceData(BaseModel):
    """Ex-showroom and on-road pricing structure."""
    ex_showroom: str = Field(default="", description="Ex-showroom price string e.g. ₹1.56 Crore / $79,100")
    on_road_estimate: str = Field(default="", description="Estimated on-road price in INR")
    rto_tax: str = Field(default="", description="State RTO tax estimation")
    insurance: str = Field(default="", description="Comprehensive insurance estimation")
    currency: str = Field(default="INR", description="Currency code e.g. INR, USD, EUR")
    price_lakhs: float = Field(default=0.0, description="Numerical price in Lakhs for calculation")
