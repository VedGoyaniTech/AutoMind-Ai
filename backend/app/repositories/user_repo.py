from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.models.user import User, UserPreference
from app.core.security import get_password_hash

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).options(joinedload(User.preference)).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).options(joinedload(User.preference)).filter(User.id == user_id).first()

    def create(self, full_name: str, email: str, password: str, is_admin: bool = False) -> User:
        hashed_password = get_password_hash(password)
        user = User(
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Create default preferences
        pref = UserPreference(user_id=user.id)
        self.db.add(pref)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_preference(self, user_id: int, answer_detail: str = "Balanced", units: str = "Metric", currency: str = "INR") -> UserPreference:
        pref = self.db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        if not pref:
            pref = UserPreference(user_id=user_id, answer_detail=answer_detail, units=units, currency=currency)
            self.db.add(pref)
        else:
            pref.answer_detail = answer_detail
            pref.units = units
            pref.currency = currency
        self.db.commit()
        self.db.refresh(pref)
        return pref
