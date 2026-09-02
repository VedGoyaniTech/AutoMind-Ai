"""
AutoMind AI — User Message Feedback API Router
Provides endpoints for user thumbs up/down feedback on assistant responses.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.schemas.feedback import (
    FeedbackCreate, FeedbackUpdate, FeedbackResponse, FeedbackStatusResponse
)
from app.repositories.feedback_repo import FeedbackRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat/feedback", tags=["Chat Message Feedback"])

@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits or updates a user rating (thumbs up / thumbs down) for an assistant message.
    """
    try:
        repo = FeedbackRepository(db)
        return repo.submit_feedback(payload, user_id=current_user.id)
    except Exception as err:
        logger.error(f"[FeedbackAPI] Error submitting feedback: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record message feedback."
        )

@router.patch("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    payload: FeedbackUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates an existing feedback entry (e.g. changing rating or updating comment).
    """
    repo = FeedbackRepository(db)
    updated = repo.update_feedback(feedback_id, payload, user_id=current_user.id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback ID {feedback_id} not found."
        )
    return updated

@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revokes or deletes user feedback for a message.
    """
    repo = FeedbackRepository(db)
    deleted = repo.delete_feedback(feedback_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback ID {feedback_id} not found."
        )
    return None

@router.get("/status", response_model=FeedbackStatusResponse)
def get_feedback_status(
    message_id: int = Query(..., description="ID of the assistant message"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the current user's feedback status for a given message.
    """
    repo = FeedbackRepository(db)
    fb = repo.get_feedback_by_message_id(message_id, user_id=current_user.id)
    if fb:
        return FeedbackStatusResponse(hasFeedback=True, feedback=FeedbackResponse.model_validate(fb))
    return FeedbackStatusResponse(hasFeedback=False, feedback=None)
