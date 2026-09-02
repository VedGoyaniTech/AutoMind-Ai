from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.car import CarVariantSummary

class SourceCard(BaseModel):
    id: int
    title: str
    website: str
    url: str
    domain: str
    reason: str
    reliability_score: float

class ChatMessageSend(BaseModel):
    conversation_id: Optional[int] = None
    message: str

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class ChatStreamEvent(BaseModel):
    event_type: str # 'progress', 'token', 'sources', 'cars', 'complete', 'error'
    stage: Optional[str] = None # 'understanding', 'searching', 'comparing', 'checking', 'ranking', 'generating'
    message: Optional[str] = None
    token: Optional[str] = None
    sources: Optional[List[SourceCard]] = None
    cars: Optional[List[CarVariantSummary]] = None
    conversation_id: Optional[int] = None
