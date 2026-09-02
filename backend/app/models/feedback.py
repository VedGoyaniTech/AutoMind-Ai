"""
AutoMind AI — User Message Feedback Database Model
Stores thumbs-up / thumbs-down ratings, reason codes, and feedback for DPO curation.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.db.session import Base

class MessageFeedback(Base):
    __tablename__ = "message_feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, index=True, nullable=False)
    message_id = Column(Integer, index=True, nullable=False)
    parent_user_message_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True, index=True)
    
    prompt = Column(Text, nullable=True)
    response_content = Column(Text, nullable=True)
    rating = Column(String(10), nullable=False)  # "up" | "down"
    reason_code = Column(String(50), nullable=True)  # "incorrect_price", "not_relevant", etc.
    comment = Column(String(500), nullable=True)
    
    model_version = Column(String(50), default="qwen_lora_v4")
    locale = Column(String(20), default="en-IN")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
