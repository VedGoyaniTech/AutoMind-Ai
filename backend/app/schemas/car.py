from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class SourceResponse(BaseModel):
    id: int
    name: str
    domain: str
    base_url: str
    reliability_score: float
    source_type: str

    model_config = ConfigDict(from_attributes=True)


class CarVariantSummary(BaseModel):
    id: int
    manufacturer_name: str
    model_name: str
    variant_name: str
    model_year: int
    body_type: str
    fuel_type: str
    transmission: str
    ex_showroom_price: float
    estimated_on_road_price: float
    currency: str
    combined_mileage: Optional[float] = None
    electric_range: Optional[float] = None
    seating_capacity: int
    airbags: int
    safety_rating: Optional[float] = None
    image_url: Optional[str] = None
    is_saved: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class CarDetailResponse(BaseModel):
    id: int
    manufacturer_name: str
    model_name: str
    variant_name: str
    model_year: int
    body_type: str
    ex_showroom_price: float
    estimated_on_road_price: float
    currency: str
    country: str
    
    fuel_type: str
    transmission: str
    engine_cc: Optional[int] = None
    cylinders: Optional[int] = None
    horsepower: Optional[float] = None
    torque_nm: Optional[float] = None

    mileage_city: Optional[float] = None
    mileage_highway: Optional[float] = None
    combined_mileage: Optional[float] = None
    battery_capacity: Optional[float] = None
    electric_range: Optional[float] = None
    charging_time: Optional[float] = None

    seating_capacity: int
    airbags: int
    safety_rating: Optional[float] = None
    boot_space: Optional[int] = None
    ground_clearance: Optional[int] = None
    length: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    wheelbase: Optional[int] = None
    drive_type: str

    features: Optional[Dict[str, Any]] = None
    safety_features: Optional[Dict[str, Any]] = None
    infotainment_features: Optional[Dict[str, Any]] = None
    comfort_features: Optional[Dict[str, Any]] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    source: Optional[SourceResponse] = None
    is_saved: Optional[bool] = False
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class CarSearchFilter(BaseModel):
    query: Optional[str] = None
    manufacturer: Optional[str] = None
    body_type: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    min_mileage: Optional[float] = None
    min_airbags: Optional[int] = None
    min_safety_rating: Optional[float] = None
    seating_capacity: Optional[int] = None
    page: int = 1
    page_size: int = 12


class CarCompareRequest(BaseModel):
    variant_ids: List[int]
