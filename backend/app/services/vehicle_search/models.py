"""
Vehicle Search Pipeline — Pydantic Data Models & Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Raw search result item from search engine."""
    title: str
    url: str
    snippet: str
    domain: str = ""


class ScrapedPage(BaseModel):
    """Clean scraped content from a trusted web page."""
    url: str
    domain: str
    title: str
    clean_text: str
    raw_html: Optional[str] = None


class ExtractedVehicleSpec(BaseModel):
    """Structured vehicle data extracted from a scraped web page."""
    vehicle_name: str = Field(description="Full vehicle name e.g. BMW M4 Competition")
    variant_name: str = Field(default="", description="Specific variant e.g. xDrive Coupe")
    manufacturer: str = Field(default="", description="Manufacturer e.g. BMW")
    body_type: str = Field(default="", description="Body type e.g. Coupe, SUV, Sedan")
    fuel_type: str = Field(default="", description="Fuel type e.g. Petrol, Diesel, EV, Hybrid")
    transmission: str = Field(default="", description="Transmission e.g. Automatic, Manual, DCT")
    engine_capacity: str = Field(default="", description="Engine size e.g. 2993 cc / 3.0L")
    power_hp: str = Field(default="", description="Power output e.g. 523 hp / 503 bhp")
    torque_nm: str = Field(default="", description="Torque e.g. 650 Nm")
    mileage_kmpl: str = Field(default="", description="Fuel efficiency / range e.g. 10.75 kmpl / 450 km")
    ex_showroom_price: str = Field(default="", description="Ex-showroom price e.g. ₹1.53 Crore / $79,100")
    on_road_price: str = Field(default="", description="Estimated on-road price in INR")
    safety_rating: str = Field(default="", description="Safety rating e.g. 5-Star GNCAP / Euro NCAP")
    key_features: List[str] = Field(default_factory=list, description="Key features list")
    source_url: str = Field(default="", description="Source URL")
    source_domain: str = Field(default="", description="Source domain name e.g. carwale.com")
    confidence_score: float = Field(default=1.0, description="Extraction confidence score")


class MergedVehicleResult(BaseModel):
    """Consensus vehicle data merged from multiple trusted sources."""
    query: str
    vehicle: str
    variant: str
    manufacturer: str
    fuel: str
    transmission: str
    engine: str
    power: str
    torque: str
    mileage: str
    price_ex_showroom: str
    price_on_road: str
    safety_rating: str
    features: List[str] = Field(default_factory=list)
    consensus_sources: List[str] = Field(default_factory=list)
    confidence: float = 1.0


class PipelineLogEvent(BaseModel):
    """Structured log event for pipeline execution stages."""
    stage: str
    message: str
    details: Optional[Dict[str, Any]] = None
