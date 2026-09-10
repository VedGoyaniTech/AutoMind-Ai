from app.db.session import Base
from app.models.user import User, UserPreference
from app.models.source import Source
from app.models.car import Manufacturer, CarModel, CarVariant, SavedCar
from app.models.chat import Conversation, Message
from app.models.ingestion import IngestionJob
from app.models.feedback import MessageFeedback

__all__ = [
    "Base",
    "User",
    "UserPreference",
    "Source",
    "Manufacturer",
    "CarModel",
    "CarVariant",
    "SavedCar",
    "Conversation",
    "Message",
    "IngestionJob",
    "MessageFeedback"
]

