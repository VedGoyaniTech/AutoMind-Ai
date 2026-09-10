from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Immutable source identifier, e.g. "oem_tata_official_2026", "gov_morth_vahan_2026"
    source_uid: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False, default=lambda: f"source_{int(datetime.now(timezone.utc).timestamp())}")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher: Mapped[str] = mapped_column(String(255), nullable=False, default="Unknown Publisher")
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # official_oem, government, safety_programme, licensed_api, licensed_partner, review, user_contributed, fixture
    source_type: Mapped[str] = mapped_column(String(50), default="official_oem", index=True)
    licence: Mapped[str] = mapped_column(String(255), default="OEM Public Specification Rights")
    # manual_upload, authorised_api, authorised_download, fixture
    acquisition_method: Mapped[str] = mapped_column(String(50), default="authorised_download")
    reliability_score: Mapped[float] = mapped_column(Float, default=0.95)
    
    # rag, catalogue, analytics, training_style_only, not_for_training
    allowed_use: Mapped[str] = mapped_column(String(50), default="catalogue", index=True)
    region: Mapped[str] = mapped_column(String(20), default="IN", index=True)
    
    published_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fetched_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))
    
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    version: Mapped[str] = mapped_column(String(30), default="1.0.0")
    # pending, approved, rejected, stale
    review_status: Mapped[str] = mapped_column(String(30), default="approved", index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    variants: Mapped[List["CarVariant"]] = relationship("CarVariant", back_populates="source")
    specifications: Mapped[List["VehicleSpecification"]] = relationship("VehicleSpecification", back_populates="source")
    prices: Mapped[List["VehiclePrice"]] = relationship("VehiclePrice", back_populates="source")

