"""
AutoMind AI — Typed Agentic Tool & Plan Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    source_metadata: Dict[str, Any] = Field(default_factory=lambda: {"source": "local_deterministic_engine"})
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AgentPlanStep(BaseModel):
    step_id: int
    tool_name: str
    description: str
    arguments: Dict[str, Any]
    status: str = "pending" # pending, running, completed, failed

class AgentPlan(BaseModel):
    goal: str
    detected_language: str = "en" # hi, gu, en, hinglish
    steps: List[AgentPlanStep]
    estimated_steps: int

class VerificationReport(BaseModel):
    is_valid: bool
    financial_values_verified: bool
    budget_constraints_satisfied: bool
    no_unsupported_live_claims: bool
    language_preserved: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class AgentResponse(BaseModel):
    content: str
    plan: AgentPlan
    tool_results: List[ToolExecutionResult]
    verification: VerificationReport
    pricing_quote: Optional[Dict[str, Any]] = None
    vehicle_gallery: Optional[Dict[str, Any]] = None
    comparison_matrix: Optional[Dict[str, Any]] = None
