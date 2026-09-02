"""
AutoMind AI — On-Road Pricing & EMI Calculator Pydantic Schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class OnRoadPriceRequest(BaseModel):
    manufacturer: Optional[str] = Field(None, description="Automotive manufacturer name, e.g. Tata, Mahindra, Hyundai")
    model: Optional[str] = Field(None, description="Vehicle model name, e.g. Nexon, Creta, Thar")
    variant: Optional[str] = Field(None, description="Specific variant name")
    city: Optional[str] = Field(None, description="City name, e.g. Ahmedabad, Mumbai, Delhi, Bengaluru")
    stateCode: Optional[str] = Field(None, description="2-letter state code, e.g. GJ, MH, DL, KA")
    fuelType: str = Field("petrol", description="Fuel type: petrol, diesel, cng, electric, hybrid")
    exShowroomPrice: Optional[float] = Field(None, description="Ex-showroom price in INR (if known/custom)")
    includeZeroDep: bool = Field(True, description="Include zero-depreciation insurance add-on")
    includeDealerHandling: bool = Field(False, description="Include optional dealer logistics/handling fee")

class EMIRequest(BaseModel):
    onRoadPrice: float = Field(..., description="Total on-road price in INR")
    downPayment: Optional[float] = Field(None, description="Down payment amount in INR")
    downPaymentPct: Optional[float] = Field(None, description="Down payment percentage (0-100)")
    loanAmount: Optional[float] = Field(None, description="Direct loan amount in INR")
    annualInterestRate: float = Field(9.25, description="Annual bank interest rate in percent (e.g. 8.75 - 9.5%)")
    tenuresYears: List[int] = Field(default_factory=lambda: [3, 5, 7], description="List of loan tenures in years")

class PricingQuoteRequest(BaseModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    city: Optional[str] = None
    stateCode: Optional[str] = None
    fuelType: str = "petrol"
    exShowroomPrice: Optional[float] = None
    includeZeroDep: bool = True
    includeDealerHandling: bool = False
    downPayment: Optional[float] = None
    downPaymentPct: Optional[float] = None
    annualInterestRate: float = 9.25
    tenuresYears: List[int] = Field(default_factory=lambda: [3, 5, 7])

class EMIOptionItem(BaseModel):
    tenureYears: int
    tenureMonths: int
    monthlyEmi: float
    loanPrincipal: float
    totalInterest: float
    totalPayable: float

class PriceBreakdown(BaseModel):
    exShowroomPrice: float
    rtoTax: float
    rtoRoadSafetyCess: float = 0.0
    registrationAndSmartCardFee: float = 0.0
    insurance: float
    tcs: float = 0.0
    fastag: float = 0.0
    hsrpAndPortalFees: float = 0.0
    dealerHandlingCharges: float = 0.0
    hsrpOrRegistration: float = 0.0
    cessAndOtherFees: float = 0.0
    dealerHandling: float = 0.0
    onRoadPrice: float

class LocationInfo(BaseModel):
    city: str
    stateCode: str
    stateName: str
    calculationScope: str = "city_estimate"

class VehicleInfo(BaseModel):
    manufacturer: str
    model: str
    variant: str
    fuelType: str
    isEstimatedPrice: bool = False

class DataFreshnessInfo(BaseModel):
    priceEffectiveDate: Optional[str] = "2026-01-01"
    ruleEffectiveDate: Optional[str] = "2026-01-01"
    lastVerifiedAt: Optional[str] = "2026-03-01"
    isEstimate: bool = True
    dataSourceLabel: str = "local_rto_registry"

class PricingQuoteResponse(BaseModel):
    location: LocationInfo
    vehicle: VehicleInfo
    priceBreakdown: PriceBreakdown
    emiOptions: List[EMIOptionItem]
    dataFreshness: DataFreshnessInfo = Field(default_factory=DataFreshnessInfo)
    assumptions: List[str]
    disclaimer: str
    formattedSummary: Optional[str] = None
