"""
AutoMind AI — Agent Execution State Management
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ConversationContextMessage(BaseModel):
    role: str # user, assistant, system
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None

class AgentState(BaseModel):
    conversation_id: Optional[str] = None
    user_id: int
    message_id: Optional[str] = None
    user_prompt: str
    locale: str = "en"
    history: List[ConversationContextMessage] = Field(default_factory=list)
    step_count: int = 0
    max_steps: int = 6
    visited_tools: List[str] = Field(default_factory=list)
    accumulated_context: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    start_time: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
