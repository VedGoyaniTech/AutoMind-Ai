from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Float, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="Global")
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    models: Mapped[list["CarModel"]] = relationship("CarModel", back_populates="manufacturer", cascade="all, delete-orphan")


class CarModel(Base):
    __tablename__ = "car_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    manufacturer_id: Mapped[int] = mapped_column(Integer, ForeignKey("manufacturers.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    body_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # SUV, Sedan, Hatchback, MUV, EV, Hybrid
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    manufacturer: Mapped["Manufacturer"] = relationship("Manufacturer", back_populates="models")
    variants: Mapped[list["CarVariant"]] = relationship("CarVariant", back_populates="car_model", cascade="all, delete-orphan")


class CarVariant(Base):
    __tablename__ = "car_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("car_models.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)

    variant_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    model_year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    # Financial & Availability
    ex_showroom_price: Mapped[float] = mapped_column(Float, index=True, nullable=False) # In INR (e.g. 1500000)
    estimated_on_road_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    country: Mapped[str] = mapped_column(String(50), default="India")

    # Powertrain & Performance
    fuel_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False) # Petrol, Diesel, EV, Hybrid, CNG
    transmission: Mapped[str] = mapped_column(String(50), index=True, nullable=False) # Manual, Automatic, DCT, CVT, AMT
    engine_cc: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cylinders: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    horsepower: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # bhp
    torque_nm: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # Nm
    
    # Fuel Efficiency / EV Spec
    mileage_city: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # km/l
    mileage_highway: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # km/l
    combined_mileage: Mapped[Optional[float]] = mapped_column(Float, index=True, nullable=True) # km/l or km/kWh
    battery_capacity: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # kWh
    electric_range: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # km
    charging_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # hours

    # Capacity, Safety & Dimensions
    seating_capacity: Mapped[int] = mapped_column(Integer, index=True, default=5)
    airbags: Mapped[int] = mapped_column(Integer, index=True, default=2)
    safety_rating: Mapped[Optional[float]] = mapped_column(Float, index=True, nullable=True) # 0 to 5 stars
    boot_space: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # liters
    ground_clearance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # mm
    length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # mm
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # mm
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # mm
    wheelbase: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # mm
    drive_type: Mapped[str] = mapped_column(String(50), default="FWD") # FWD, RWD, AWD, 4WD

    # Detailed Content & Features (Stored as JSON lists or dicts)
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    safety_features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    infotainment_features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    comfort_features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    pros: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    cons: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    car_model: Mapped["CarModel"] = relationship("CarModel", back_populates="variants")
    source: Mapped[Optional["Source"]] = relationship("Source", back_populates="variants")
    saved_by: Mapped[list["SavedCar"]] = relationship("SavedCar", back_populates="variant", cascade="all, delete-orphan")


class SavedCar(Base):
    __tablename__ = "saved_cars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("car_variants.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="saved_cars")
    variant: Mapped["CarVariant"] = relationship("CarVariant", back_populates="saved_by")
