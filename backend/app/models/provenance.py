"""
AutoMind AI — Provenance & Product Data Foundation Models
Enforces source traceability, versioning, validity intervals, and review statuses.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, DateTime, Integer, Numeric, Text, JSON, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class VehicleSpecification(Base):
    """
    Normalized per-fact specification table with source traceability.
    A single car variant can have multiple source-backed, verified facts.
    """
    __tablename__ = "vehicle_specifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    variant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("car_variants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Typed value storage
    value_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    value_numeric: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    value_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # mm, liters, km/l, kWh, bhp, Nm, etc.

    # Provenance metadata
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    page_section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[str] = mapped_column(String(20), default="IN", nullable=False)
    
    effective_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # pending, approved, rejected, stale
    review_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    variant: Mapped["CarVariant"] = relationship("CarVariant", back_populates="specifications")
    source: Mapped["Source"] = relationship("Source", back_populates="specifications")

    __table_args__ = (
        UniqueConstraint("variant_id", "field_name", "source_id", "effective_date", name="uq_variant_spec_provenance"),
    )


class VehiclePrice(Base):
    """
    Versioned financial price history.
    Uses Numeric(12, 2) (fixed-point Decimal) for accurate currency calculations.
    """
    __tablename__ = "vehicle_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    variant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("car_variants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # ex_showroom, on_road_estimate
    price_type: Mapped[str] = mapped_column(String(50), default="ex_showroom", index=True, nullable=False)
    state_code: Mapped[Optional[str]] = mapped_column(String(10), index=True, nullable=True)  # GJ, MH, DL, KA, etc.
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    region: Mapped[str] = mapped_column(String(20), default="IN", nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    
    # Financial amount (Fixed-point Decimal)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    effective_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    review_status: Mapped[str] = mapped_column(String(30), default="approved", index=True, nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    variant: Mapped["CarVariant"] = relationship("CarVariant", back_populates="prices")
    source: Mapped["Source"] = relationship("Source", back_populates="prices")

    @property
    def is_current(self) -> bool:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (self.effective_from <= now) and (self.effective_to is None or self.effective_to > now)

    __table_args__ = (
        UniqueConstraint("variant_id", "price_type", "state_code", "city", "effective_from", name="uq_variant_price_version"),
    )


class RTORuleVersion(Base):
    """
    Statutory RTO road tax and fee schedule versioned by state and notification.
    """
    __tablename__ = "rto_rule_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    state_code: Mapped[str] = mapped_column(String(10), index=True, nullable=False)  # GJ, MH, DL, KA, BH, etc.
    fuel_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)   # Petrol, Diesel, EV, CNG, Hybrid, All
    vehicle_class: Mapped[str] = mapped_column(String(50), default="Personal", nullable=False)
    
    min_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    max_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    tax_rate_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    fixed_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    cess_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    rule_expression: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    notification_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    
    effective_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    review_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approval_status: Mapped[str] = mapped_column(String(30), default="approved", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


class SafetyRating(Base):
    """
    Official crash-test ratings (Bharat NCAP / Global NCAP) with strict vehicle applicability.
    """
    __tablename__ = "safety_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    programme: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # BNCAP, Global NCAP
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("car_models.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_applicability: Mapped[str] = mapped_column(String(255), default="All Variants", nullable=False)
    tested_variant_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    test_year: Mapped[int] = mapped_column(Integer, nullable=False)

    adult_occupant_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    adult_occupant_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), default=Decimal("32.00"), nullable=True)
    child_occupant_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    child_occupant_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), default=Decimal("49.00"), nullable=True)
    safety_assist_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    star_rating: Mapped[Decimal] = mapped_column(Numeric(2, 1), nullable=False)  # e.g. 5.0
    
    test_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    report_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    protocol_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


class InsuranceAssumption(Base):
    """
    Transparent regulatory assumptions for estimating comprehensive motor insurance.
    """
    __tablename__ = "insurance_assumptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    state_code: Mapped[str] = mapped_column(String(10), default="All", nullable=False)
    segment: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(50), default="All", nullable=False)
    coverage_type: Mapped[str] = mapped_column(String(50), default="1yr_OD_3yr_TP", nullable=False)
    
    od_rate_percent: Mapped[Decimal] = mapped_column(Numeric(5, 3), nullable=False)
    tp_fixed_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    addon_rates_percent: Mapped[Decimal] = mapped_column(Numeric(5, 3), default=Decimal("0.500"), nullable=False)
    
    insurer_source: Mapped[str] = mapped_column(String(255), nullable=False)
    effective_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    review_status: Mapped[str] = mapped_column(String(30), default="approved", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class RecallCampaign(Base):
    """
    Official vehicle recall and service campaign registry.
    Only aggregated statistical unit counts and ranges; NO individual owner PII or VINs.
    """
    __tablename__ = "recalls_and_service_campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    manufacturer_id: Mapped[int] = mapped_column(Integer, ForeignKey("manufacturers.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("car_models.id", ondelete="SET NULL"), nullable=True, index=True)
    campaign_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False, unique=True)
    issue_description: Mapped[str] = mapped_column(Text, nullable=False)
    remedy: Mapped[str] = mapped_column(Text, nullable=False)
    affected_vin_range: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    affected_units_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recall_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    official_notice_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class EVChargingStation(Base):
    """
    Licensed public EV charging station infrastructure with connector types and power ratings.
    """
    __tablename__ = "ev_charging_stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    network_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    station_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    state_code: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    connector_types: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["CCS2", "Type 2"]
    max_power_kw: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    access_type: Mapped[str] = mapped_column(String(50), default="Public", nullable=False)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class OwnershipCostAssumption(Base):
    """
    TCO calculation parameters (fuel/electricity price, service cost, tyre/battery assumptions).
    """
    __tablename__ = "ownership_cost_assumptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("car_models.id", ondelete="SET NULL"), nullable=True, index=True)
    segment: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    annual_km_assumed: Mapped[int] = mapped_column(Integer, default=12000, nullable=False)
    fuel_or_energy_rate: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)  # per liter or per kWh
    annual_maintenance_est: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tyre_battery_replacement_est: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    effective_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
