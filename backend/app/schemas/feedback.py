"""
AutoMind AI — Message Feedback Pydantic Schemas
"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

ReasonCodeType = Literal[
    "incorrect_price",
    "not_relevant",
    "incomplete_answer",
    "language_issue",
    "unsafe_inappropriate",
    "other"
]

class FeedbackCreate(BaseModel):
    conversationId: int = Field(..., description="ID of the conversation")
    messageId: int = Field(..., description="ID of the assistant message")
    parentUserMessageId: Optional[int] = Field(None, description="ID of the preceding user message")
    rating: Literal["up", "down"] = Field(..., description="'up' for helpful, 'down' for unhelpful")
    reasonCode: Optional[ReasonCodeType] = Field(None, description="Reason category for thumbs down")
    comment: Optional[str] = Field(None, max_length=500, description="Optional user comment (max 500 characters)")
    prompt: Optional[str] = Field(None, description="Prompt text for reference")
    responseContent: Optional[str] = Field(None, description="Assistant response text for reference")
    locale: str = Field("en-IN", description="User interface locale e.g. hi-IN, gu-IN, en-IN")

class FeedbackUpdate(BaseModel):
    rating: Optional[Literal["up", "down"]] = None
    reasonCode: Optional[ReasonCodeType] = None
    comment: Optional[str] = Field(None, max_length=500)

class FeedbackResponse(BaseModel):
    id: int
    conversation_id: int = Field(..., alias="conversationId")
    message_id: int = Field(..., alias="messageId")
    parent_user_message_id: Optional[int] = Field(None, alias="parentUserMessageId")
    rating: str
    reason_code: Optional[str] = Field(None, alias="reasonCode")
    comment: Optional[str] = None
    model_version: str = Field(..., alias="modelVersion")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True

class FeedbackStatusResponse(BaseModel):
    hasFeedback: bool
    feedback: Optional[FeedbackResponse] = None
