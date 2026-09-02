"""
AutoMind AI — Unit Test Suite for User Message Feedback & DPO Pipeline
"""

import os
import sys

from app.db.session import SessionLocal, engine, Base
from app.models.user import User
from app.models.feedback import MessageFeedback
from app.repositories.feedback_repo import FeedbackRepository
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate
from app.core.security import get_password_hash

def test_feedback_submission_and_idempotence():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        repo = FeedbackRepository(db)

        # 1. Submit initial thumbs up
        fb_req = FeedbackCreate(
            conversationId=1,
            messageId=101,
            parentUserMessageId=100,
            rating="up",
            prompt="What is Nexon price in Ahmedabad?",
            responseContent="Nexon on-road price is ₹12.77 Lakh...",
            locale="en-IN"
        )
        fb1 = repo.submit_feedback(fb_req, user_id=1)
        assert fb1.id is not None
        assert fb1.rating == "up"

        # 2. Idempotent update to thumbs down with reason
        fb_update_req = FeedbackCreate(
            conversationId=1,
            messageId=101,
            parentUserMessageId=100,
            rating="down",
            reasonCode="incorrect_price",
            comment="RTO tax should be 6%",
            prompt="What is Nexon price in Ahmedabad?",
            responseContent="Nexon on-road price is ₹12.77 Lakh...",
            locale="en-IN"
        )
        fb2 = repo.submit_feedback(fb_update_req, user_id=1)
        # Should update same record, not duplicate
        assert fb2.id == fb1.id
        assert fb2.rating == "down"
        assert fb2.reason_code == "incorrect_price"
        assert fb2.comment == "RTO tax should be 6%"

        # 3. Retrieve status
        status_fb = repo.get_feedback_by_message_id(101, user_id=1)
        assert status_fb is not None
        assert status_fb.rating == "down"

        # 4. Withdraw / Delete feedback
        deleted = repo.delete_feedback(fb1.id, user_id=1)
        assert deleted is True

        post_delete = repo.get_feedback_by_message_id(101, user_id=1)
        assert post_delete is None

    finally:
        db.close()
