"""
AutoMind AI — Pydantic Validation Schemas for Provenance & Product Data Foundation
Enforces Decimal currency, mandatory source tracing, region, dates, and review statuses.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator

# Allowed Enums
ALLOWED_SOURCE_TYPES = {
    "official_oem", "government", "safety_programme", "licensed_api",
    "licensed_partner", "review", "user_contributed", "fixture"
}

ALLOWED_USES = {
    "rag", "catalogue", "analytics", "training_style_only", "not_for_training"
}

ALLOWED_REVIEW_STATUSES = {"pending", "approved", "rejected", "stale"}
ALLOWED_LIFECYCLE_STATUSES = {"active", "discontinued", "upcoming"}

class SourceCreate(BaseModel):
    source_uid: str = Field(..., description="Unique immutable source identifier")
    name: str = Field(..., min_length=2, max_length=255)
    publisher: str = Field(..., min_length=2, max_length=255)
    domain: str = Field(..., min_length=3, max_length=255)
    base_url: str = Field(..., min_length=3, max_length=500)
    source_type: str = Field(default="official_oem")
    licence: str = Field(default="OEM Public Specification Rights")
    acquisition_method: str = Field(default="authorised_download")
    reliability_score: float = Field(default=0.95, ge=0.0, le=1.0)
    allowed_use: str = Field(default="catalogue")
    region: str = Field(default="IN", max_length=20)
    published_date: Optional[datetime] = None
    fetched_date: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    active: bool = True
    revoked: bool = False
    content_hash: Optional[str] = None
    version: str = "1.0.0"
    review_status: str = "approved"
    notes: Optional[str] = None

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        if v not in ALLOWED_SOURCE_TYPES:
            raise ValueError(f"Invalid source_type '{v}'. Must be one of {ALLOWED_SOURCE_TYPES}")
        return v

    @field_validator("allowed_use")
    @classmethod
    def validate_allowed_use(cls, v: str) -> str:
        if v not in ALLOWED_USES:
            raise ValueError(f"Invalid allowed_use '{v}'. Must be one of {ALLOWED_USES}")
        return v

    @field_validator("review_status")
    @classmethod
    def validate_review_status(cls, v: str) -> str:
        if v not in ALLOWED_REVIEW_STATUSES:
            raise ValueError(f"Invalid review_status '{v}'. Must be one of {ALLOWED_REVIEW_STATUSES}")
        return v


class SourceResponse(SourceCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehicleSpecificationCreate(BaseModel):
    variant_id: int
    field_name: str = Field(..., min_length=2, max_length=100)
    value_text: Optional[str] = None
    value_numeric: Optional[Decimal] = None
    value_json: Optional[Dict[str, Any]] = None
    unit: Optional[str] = None
    source_id: int
    source_url: Optional[str] = None
    page_section: Optional[str] = None
    region: str = "IN"
    effective_date: datetime
    last_verified_at: datetime
    review_status: str = "pending"
    content_hash: Optional[str] = None

    @model_validator(mode="after")
    def validate_verified_completeness(self) -> "VehicleSpecificationCreate":
        if self.review_status == "approved":
            if not self.source_id:
                raise ValueError("Approved specification fact must have a valid source_id.")
            if not self.effective_date:
                raise ValueError("Approved specification fact must have an effective_date.")
            if not self.last_verified_at:
                raise ValueError("Approved specification fact must have a last_verified_at timestamp.")
        return self


class VehicleSpecificationResponse(VehicleSpecificationCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehiclePriceCreate(BaseModel):
    variant_id: int
    price_type: str = "ex_showroom"
    state_code: Optional[str] = None
    city: Optional[str] = None
    region: str = "IN"
    currency: str = "INR"
    amount: Decimal = Field(..., gt=0, description="Amount in fixed-point Decimal, never float")
    effective_from: datetime
    effective_to: Optional[datetime] = None
    source_id: int
    source_url: Optional[str] = None
    review_status: str = "approved"
    content_hash: Optional[str] = None

    @model_validator(mode="after")
    def validate_price_provenance(self) -> "VehiclePriceCreate":
        if self.review_status == "approved":
            if not self.source_id:
                raise ValueError("Approved vehicle price must cite a valid source_id.")
            if not self.effective_from:
                raise ValueError("Approved vehicle price must have an effective_from date.")
        return self


class VehiclePriceResponse(VehiclePriceCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RTORuleVersionCreate(BaseModel):
    state_code: str = Field(..., min_length=2, max_length=10)
    fuel_type: str = Field(..., min_length=2, max_length=50)
    vehicle_class: str = "Personal"
    min_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    max_price: Optional[Decimal] = None
    tax_rate_percent: Decimal = Field(..., ge=0, le=100)
    fixed_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    cess_percent: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    rule_expression: Optional[str] = None
    notification_ref: str = Field(..., min_length=3, max_length=255)
    source_url: Optional[str] = None
    source_id: Optional[int] = None
    effective_date: datetime
    review_date: Optional[datetime] = None
    approval_status: str = "approved"

    @model_validator(mode="after")
    def validate_rto_provenance(self) -> "RTORuleVersionCreate":
        if not self.notification_ref:
            raise ValueError("RTO rule version must cite official notification reference.")
        if not self.effective_date:
            raise ValueError("RTO rule version must specify official effective date.")
        return self


class RTORuleVersionResponse(RTORuleVersionCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SafetyRatingCreate(BaseModel):
    programme: str = Field(..., description="BNCAP, Global NCAP")
    model_id: int
    variant_applicability: str = "All Variants"
    tested_variant_name: Optional[str] = None
    test_year: int = Field(..., ge=2000, le=2030)
    adult_occupant_score: Optional[Decimal] = None
    adult_occupant_max: Optional[Decimal] = Decimal("32.00")
    child_occupant_score: Optional[Decimal] = None
    child_occupant_max: Optional[Decimal] = Decimal("49.00")
    safety_assist_score: Optional[Decimal] = None
    star_rating: Decimal = Field(..., ge=0.0, le=5.0)
    test_date: Optional[datetime] = None
    source_id: Optional[int] = None
    source_url: Optional[str] = None
    report_url: Optional[str] = None
    protocol_version: Optional[str] = None

    @model_validator(mode="after")
    def validate_applicability(self) -> "SafetyRatingCreate":
        if not self.programme:
            raise ValueError("Safety rating must specify rating programme (e.g. BNCAP, Global NCAP).")
        if not self.variant_applicability:
            raise ValueError("Safety rating must specify exact variant applicability; copying to different generations is forbidden.")
        return self


class SafetyRatingResponse(SafetyRatingCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# RAG Citation Metadata Schema
class RAGCitationMetadata(BaseModel):
    document_title: str
    publisher: str
    source_url: Optional[str] = None
    source_type: str
    published_date: Optional[str] = None
    effective_date: Optional[str] = None
    last_verified_at: Optional[str] = None
    page_section: Optional[str] = None
    review_status: str = "approved"
    is_stale: bool = False
    data_freshness_warning: Optional[str] = None
