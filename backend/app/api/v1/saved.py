from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.car_repo import CarRepository
from app.schemas.car import CarVariantSummary
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/saved", tags=["Saved Cars"])

@router.get("", response_model=List[CarVariantSummary])
def get_saved_cars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = CarRepository(db)
    variants = repo.get_saved_cars_for_user(current_user.id)
    res = []
    for v in variants:
        res.append(
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
                image_url=v.image_url,
                is_saved=True
            )
        )
    return res

@router.post("/{variant_id}", status_code=status.HTTP_201_CREATED)
def save_car(
    variant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = CarRepository(db)
    variant = repo.get_variant_by_id(variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Car variant not found")

    repo.save_car(current_user.id, variant_id)
    return {"message": "Car saved successfully", "variant_id": variant_id}

@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_car(
    variant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = CarRepository(db)
    repo.unsave_car(current_user.id, variant_id)
    return None
