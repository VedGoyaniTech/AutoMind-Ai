from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc
from app.models.car import CarVariant, CarModel, Manufacturer, SavedCar
from app.models.source import Source
from app.schemas.car import CarSearchFilter

class CarRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_variant_by_id(self, variant_id: int) -> Optional[CarVariant]:
        return (
            self.db.query(CarVariant)
            .options(
                joinedload(CarVariant.car_model).joinedload(CarModel.manufacturer),
                joinedload(CarVariant.source)
            )
            .filter(CarVariant.id == variant_id)
            .first()
        )

    def search_variants(self, filters: CarSearchFilter) -> Tuple[List[CarVariant], int]:
        query = self.db.query(CarVariant).join(CarModel).join(Manufacturer)

        if filters.query:
            q = f"%{filters.query.strip()}%"
            query = query.filter(
                or_(
                    Manufacturer.name.ilike(q),
                    CarModel.name.ilike(q),
                    CarVariant.variant_name.ilike(q),
                    CarVariant.description.ilike(q)
                )
            )

        if filters.manufacturer:
            query = query.filter(Manufacturer.name.ilike(f"%{filters.manufacturer}%"))

        if filters.body_type:
            query = query.filter(CarModel.body_type.ilike(f"%{filters.body_type}%"))

        if filters.fuel_type:
            query = query.filter(CarVariant.fuel_type.ilike(f"%{filters.fuel_type}%"))

        if filters.transmission:
            query = query.filter(CarVariant.transmission.ilike(f"%{filters.transmission}%"))

        if filters.price_min is not None:
            query = query.filter(CarVariant.ex_showroom_price >= filters.price_min)

        if filters.price_max is not None:
            query = query.filter(CarVariant.ex_showroom_price <= filters.price_max)

        if filters.min_mileage is not None:
            query = query.filter(CarVariant.combined_mileage >= filters.min_mileage)

        if filters.min_airbags is not None:
            query = query.filter(CarVariant.airbags >= filters.min_airbags)

        if filters.min_safety_rating is not None:
            query = query.filter(CarVariant.safety_rating >= filters.min_safety_rating)

        total = query.count()

        offset = (filters.page - 1) * filters.page_size
        results = (
            query.options(
                joinedload(CarVariant.car_model).joinedload(CarModel.manufacturer),
                joinedload(CarVariant.source)
            )
            .order_by(desc(CarVariant.last_updated))
            .offset(offset)
            .limit(filters.page_size)
            .all()
        )

        return results, total

    def get_variants_by_ids(self, variant_ids: List[int]) -> List[CarVariant]:
        return (
            self.db.query(CarVariant)
            .options(
                joinedload(CarVariant.car_model).joinedload(CarModel.manufacturer),
                joinedload(CarVariant.source)
            )
            .filter(CarVariant.id.in_(variant_ids))
            .all()
        )

    def is_car_saved(self, user_id: int, variant_id: int) -> bool:
        return (
            self.db.query(SavedCar)
            .filter(SavedCar.user_id == user_id, SavedCar.variant_id == variant_id)
            .first()
            is not None
        )

    def save_car(self, user_id: int, variant_id: int) -> SavedCar:
        saved = self.db.query(SavedCar).filter(SavedCar.user_id == user_id, SavedCar.variant_id == variant_id).first()
        if not saved:
            saved = SavedCar(user_id=user_id, variant_id=variant_id)
            self.db.add(saved)
            self.db.commit()
            self.db.refresh(saved)
        return saved

    def unsave_car(self, user_id: int, variant_id: int) -> bool:
        saved = self.db.query(SavedCar).filter(SavedCar.user_id == user_id, SavedCar.variant_id == variant_id).first()
        if saved:
            self.db.delete(saved)
            self.db.commit()
            return True
        return False

    def get_saved_cars_for_user(self, user_id: int) -> List[CarVariant]:
        saved_list = (
            self.db.query(SavedCar)
            .options(
                joinedload(SavedCar.variant).joinedload(CarVariant.car_model).joinedload(CarModel.manufacturer)
            )
            .filter(SavedCar.user_id == user_id)
            .order_by(desc(SavedCar.created_at))
            .all()
        )
        return [item.variant for item in saved_list if item.variant]
