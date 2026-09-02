"""
Vehicle Search Models — Vehicle Schema & Entity Definitions
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class VehicleEntity(BaseModel):
    """Decomposed vehicle entity representation."""
    raw_query: str
    brand: str = Field(description="Manufacturer/Brand e.g. BMW, Tata, Hyundai")
    series: str = Field(default="", description="Series e.g. M Series, X Series, GenX")
    model: str = Field(description="Model name e.g. M4, Nexon, Creta")
    variant: str = Field(default="", description="Specific variant e.g. Competition xDrive, Creative Plus")


class VehicleSpec(BaseModel):
    """Engine, powertrain, and vehicle specifications."""
    fuel: str = Field(default="Petrol")
    transmission: str = Field(default="Automatic")
    engine: str = Field(default="")
    power: str = Field(default="")
    torque: str = Field(default="")
    mileage: str = Field(default="")
    top_speed: str = Field(default="")
    acceleration_0_100: str = Field(default="")
    safety_rating: str = Field(default="5-Star Standard")
    ncap_agency: str = Field(default="GNCAP / Euro NCAP")
    features: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)
    launch_date: str = Field(default="")
    warranty: str = Field(default="")


class ExtractedVehicleData(BaseModel):
    """Structured vehicle data extracted from a single web source."""
    brand: str
    model: str
    series: str = ""
    variant: str = ""
    fuel: str = "Petrol"
    transmission: str = "Automatic"
    engine: str = ""
    power: str = ""
    torque: str = ""
    mileage: str = ""
    top_speed: str = ""
    acceleration_0_100: str = ""
    price_ex_showroom: str = ""
    price_on_road: str = ""
    safety_rating: str = "5-Star Standard"
    features: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    source_url: str = ""
    source_domain: str = ""
    confidence_score: float = 1.0


class ConsensusVehicleData(BaseModel):
    """Consensus vehicle data verified across multiple trusted sources."""
    brand: str
    model: str
    series: str = ""
    variant: str = ""
    fuel: str = "Petrol"
    transmission: str = "Automatic"
    engine: str = ""
    power: str = ""
    torque: str = ""
    mileage: str = ""
    price_ex_showroom: str = ""
    price_on_road: str = ""
    safety_rating: str = "5-Star Standard"
    features: List[str] = Field(default_factory=list)
    consensus_sources: List[str] = Field(default_factory=list)
    confidence: float = 1.0
