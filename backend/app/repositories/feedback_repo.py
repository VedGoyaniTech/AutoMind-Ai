"""
AutoMind AI — Message Feedback Repository Layer
Provides idempotent storage and management for user thumbs-up/down ratings.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.feedback import MessageFeedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate
from app.core.config import settings

class FeedbackRepository:
    def __init__(self, db: Session):
        self.db = db

    def submit_feedback(self, data: FeedbackCreate, user_id: Optional[int] = None) -> MessageFeedback:
        """
        Idempotently inserts or updates user feedback for a specific assistant message.
        """
        existing = (
            self.db.query(MessageFeedback)
            .filter(
                MessageFeedback.conversation_id == data.conversationId,
                MessageFeedback.message_id == data.messageId,
                MessageFeedback.user_id == user_id
            )
            .first()
        )

        if existing:
            existing.rating = data.rating
            existing.reason_code = data.reasonCode
            existing.comment = data.comment
            if data.prompt:
                existing.prompt = data.prompt
            if data.responseContent:
                existing.response_content = data.responseContent
            existing.locale = data.locale
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing

        new_fb = MessageFeedback(
            conversation_id=data.conversationId,
            message_id=data.messageId,
            parent_user_message_id=data.parentUserMessageId,
            user_id=user_id,
            prompt=data.prompt,
            response_content=data.responseContent,
            rating=data.rating,
            reason_code=data.reasonCode,
            comment=data.comment,
            model_version=settings.LLM_MODEL_ID or "qwen_lora_v4",
            locale=data.locale,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(new_fb)
        self.db.commit()
        self.db.refresh(new_fb)
        return new_fb

    def get_feedback_by_message_id(self, message_id: int, user_id: Optional[int] = None) -> Optional[MessageFeedback]:
        query = self.db.query(MessageFeedback).filter(MessageFeedback.message_id == message_id)
        if user_id:
            query = query.filter(MessageFeedback.user_id == user_id)
        return query.first()

    def get_feedback_by_id(self, feedback_id: int, user_id: Optional[int] = None) -> Optional[MessageFeedback]:
        query = self.db.query(MessageFeedback).filter(MessageFeedback.id == feedback_id)
        if user_id:
            query = query.filter(MessageFeedback.user_id == user_id)
        return query.first()

    def update_feedback(self, feedback_id: int, data: FeedbackUpdate, user_id: Optional[int] = None) -> Optional[MessageFeedback]:
        fb = self.get_feedback_by_id(feedback_id, user_id)
        if not fb:
            return None
        if data.rating is not None:
            fb.rating = data.rating
        if data.reasonCode is not None:
            fb.reason_code = data.reasonCode
        if data.comment is not None:
            fb.comment = data.comment
        fb.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(fb)
        return fb

    def delete_feedback(self, feedback_id: int, user_id: Optional[int] = None) -> bool:
        fb = self.get_feedback_by_id(feedback_id, user_id)
        if not fb:
            return False
        self.db.delete(fb)
        self.db.commit()
        return True

    def get_all_feedback_for_export(self) -> List[MessageFeedback]:
        return self.db.query(MessageFeedback).order_by(MessageFeedback.created_at.asc()).all()
