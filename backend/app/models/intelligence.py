from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, Float, Integer, Text, JSON, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class CarIntelligenceCache(Base):
    """
    Cache table to store normalized external API responses and computed intelligence.
    Enforces per-provider TTLs and prevents API rate-limit exhaustion.
    """
    __tablename__ = "car_intelligence_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cache_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # 'all', 'weather', 'fuel', 'news', 'listings', 'specs', 'pricing'
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_intel_cache_key_exp", "cache_key", "expires_at"),
    )


class MarketListingSnapshot(Base):
    """
    Stores observed vehicle market listings from verified providers (e.g. DataForCars, future Indian feeds).
    Preserves currency, market geography, mileage, and asking price indicators.
    """
    __tablename__ = "market_listing_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    make: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    variant: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    country: Mapped[str] = mapped_column(String(50), default="US")  # "US", "IN", etc.
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")  # "USD", "INR"
    is_asking_price: Mapped[bool] = mapped_column(Boolean, default=True)  # True = dealer/seller asking, False = verified transaction
    mileage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mileage_unit: Mapped[str] = mapped_column(String(10), default="miles")  # "miles", "km"
    dealer_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    listing_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_provider: Mapped[str] = mapped_column(String(100), nullable=False)  # "DataForCars", "PartnerFeed"
    listed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_listing_search", "make", "model", "year", "country"),
    )


class MarketStatisticsSnapshot(Base):
    """
    Historical aggregated market statistics per vehicle and region.
    Allows genuine trend calculation over multiple dated observation points.
    """
    __tablename__ = "market_statistics_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    make: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(50), default="US")
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    total_listings: Mapped[int] = mapped_column(Integer, default=0)
    min_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_mileage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_distribution: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    observation_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
