from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.car_repo import CarRepository
from app.schemas.car import CarVariantSummary, CarDetailResponse, CarSearchFilter, CarCompareRequest
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/cars", tags=["Cars"])

@router.get("", response_model=dict)
def search_cars(
    query: Optional[str] = Query(None),
    manufacturer: Optional[str] = Query(None),
    body_type: Optional[str] = Query(None),
    fuel_type: Optional[str] = Query(None),
    transmission: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    min_mileage: Optional[float] = Query(None),
    min_airbags: Optional[int] = Query(None),
    min_safety_rating: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db)
):
    repo = CarRepository(db)
    filter_params = CarSearchFilter(
        query=query,
        manufacturer=manufacturer,
        body_type=body_type,
        fuel_type=fuel_type,
        transmission=transmission,
        price_min=price_min,
        price_max=price_max,
        min_mileage=min_mileage,
        min_airbags=min_airbags,
        min_safety_rating=min_safety_rating,
        page=page,
        page_size=page_size
    )

    variants, total = repo.search_variants(filter_params)
    
    summaries = []
    for v in variants:
        summaries.append(
            CarVariantSummary(
                id=v.id,
                manufacturer_name=v.car_model.manufacturer.name,
                model_name=v.car_model.name,
                variant_name=v.variant_name,
                model_year=v.model_year,
                body_type=v.car_model.body_type,
                fuel_type=v.fuel_type,
                transmission=v.transmission,
                ex_showroom_price=v.ex_showroom_price,
                estimated_on_road_price=v.estimated_on_road_price,
                currency=v.currency,
                combined_mileage=v.combined_mileage,
                electric_range=v.electric_range,
                seating_capacity=v.seating_capacity,
                airbags=v.airbags,
                safety_rating=v.safety_rating,
                image_url=v.image_url
            )
        )

    return {
        "items": summaries,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    }


@router.get("/{id}", response_model=CarDetailResponse)
def get_car_detail(id: int, db: Session = Depends(get_db)):
    repo = CarRepository(db)
    variant = repo.get_variant_by_id(id)
    if not variant:
        raise HTTPException(status_code=404, detail="Vehicle model not found")

    return CarDetailResponse(
        id=variant.id,
        manufacturer_name=variant.car_model.manufacturer.name,
        model_name=variant.car_model.name,
        variant_name=variant.variant_name,
        model_year=variant.model_year,
        body_type=variant.car_model.body_type,
        ex_showroom_price=variant.ex_showroom_price,
        estimated_on_road_price=variant.estimated_on_road_price,
        currency=variant.currency,
        country=variant.country,
        fuel_type=variant.fuel_type,
        transmission=variant.transmission,
        engine_cc=variant.engine_cc,
        cylinders=variant.cylinders,
        horsepower=variant.horsepower,
        torque_nm=variant.torque_nm,
        mileage_city=variant.mileage_city,
        mileage_highway=variant.mileage_highway,
        combined_mileage=variant.combined_mileage,
        battery_capacity=variant.battery_capacity,
        electric_range=variant.electric_range,
        charging_time=variant.charging_time,
        seating_capacity=variant.seating_capacity,
        airbags=variant.airbags,
        safety_rating=variant.safety_rating,
        boot_space=variant.boot_space,
        ground_clearance=variant.ground_clearance,
        length=variant.length,
        width=variant.width,
        height=variant.height,
        wheelbase=variant.wheelbase,
        drive_type=variant.drive_type,
        features=variant.features,
        safety_features=variant.safety_features,
        infotainment_features=variant.infotainment_features,
        comfort_features=variant.comfort_features,
        pros=variant.pros,
        cons=variant.cons,
        description=variant.description,
        image_url=variant.image_url,
        source_url=variant.source_url,
        source=variant.source,
        last_updated=variant.last_updated
    )


@router.post("/compare", response_model=List[CarDetailResponse])
def compare_cars(payload: CarCompareRequest, db: Session = Depends(get_db)):
    if not payload.variant_ids or len(payload.variant_ids) > 4:
        raise HTTPException(status_code=400, detail="Please select between 1 and 4 car models to compare.")

    repo = CarRepository(db)
    variants = repo.get_variants_by_ids(payload.variant_ids)
    
    res = []
    for variant in variants:
        res.append(
            CarDetailResponse(
                id=variant.id,
                manufacturer_name=variant.car_model.manufacturer.name,
                model_name=variant.car_model.name,
                variant_name=variant.variant_name,
                model_year=variant.model_year,
                body_type=variant.car_model.body_type,
                ex_showroom_price=variant.ex_showroom_price,
                estimated_on_road_price=variant.estimated_on_road_price,
                currency=variant.currency,
                country=variant.country,
                fuel_type=variant.fuel_type,
                transmission=variant.transmission,
                engine_cc=variant.engine_cc,
                cylinders=variant.cylinders,
                horsepower=variant.horsepower,
                torque_nm=variant.torque_nm,
                mileage_city=variant.mileage_city,
                mileage_highway=variant.mileage_highway,
                combined_mileage=variant.combined_mileage,
                battery_capacity=variant.battery_capacity,
                electric_range=variant.electric_range,
                charging_time=variant.charging_time,
                seating_capacity=variant.seating_capacity,
                airbags=variant.airbags,
                safety_rating=variant.safety_rating,
                boot_space=variant.boot_space,
                ground_clearance=variant.ground_clearance,
                length=variant.length,
                width=variant.width,
                height=variant.height,
                wheelbase=variant.wheelbase,
                drive_type=variant.drive_type,
                features=variant.features,
                safety_features=variant.safety_features,
                infotainment_features=variant.infotainment_features,
                comfort_features=variant.comfort_features,
                pros=variant.pros,
                cons=variant.cons,
                description=variant.description,
                image_url=variant.image_url,
                source_url=variant.source_url,
                source=variant.source,
                last_updated=variant.last_updated
            )
        )
    return res
