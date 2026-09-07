"""
AutoMind AI — Typed Agentic Schemas (Part 3 Specification)
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class AgentIntent(str, Enum):
    CASUAL = "casual"
    VEHICLE_SEARCH = "vehicle_search"
    VEHICLE_DETAILS = "vehicle_details"
    YEARWISE_LAUNCHES = "yearwise_launches"
    VEHICLE_CATEGORY = "vehicle_category"
    VEHICLE_COMPARISON = "vehicle_comparison"
    ON_ROAD_PRICE = "on_road_price"
    EMI = "emi"
    PRICE_AND_EMI = "price_and_emi"
    UPCOMING_VEHICLES = "upcoming_vehicles"
    HISTORICAL_VEHICLE_LOOKUP = "historical_vehicle_lookup"
    GALLERY_REQUEST = "gallery_request"
    SOURCES_INQUIRY = "sources_inquiry"
    UNSUPPORTED_OR_UNCLEAR = "unsupported_or_unclear"

class SourceType(str, Enum):
    LOCAL_DATABASE = "local_database"
    LOCAL_RULE = "local_rule"
    OFFICIAL_MANUFACTURER = "official_manufacturer"
    TRUSTED_AUTOMOTIVE_PUBLICATION = "trusted_automotive_publication"
    WEB_RESEARCH = "web_research"

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DataStatus(str, Enum):
    LOCAL = "local"
    WEB_RESEARCHED = "web_researched"
    MIXED = "mixed"
    INCOMPLETE = "incomplete"

class ResponseKind(str, Enum):
    TEXT = "text"
    FOLLOW_UP = "follow_up"
    PRICING_QUOTE = "pricing_quote"
    COMPARISON = "comparison"
    VEHICLE_DETAILS = "vehicle_details"
    VEHICLE_LAUNCHES = "vehicle_launches"
    GALLERY = "gallery"
    ERROR = "error"

class SourceReference(BaseModel):
    title: str
    url: str
    domain: str
    source_type: SourceType = SourceType.LOCAL_DATABASE
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    published_at: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH

class ExtractedEntities(BaseModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    fuel_type: Optional[str] = None
    body_type: Optional[str] = None
    launch_year: Optional[int] = None
    requested_year: Optional[int] = None
    down_payment: Optional[float] = None
    down_payment_percent: Optional[float] = None
    loan_amount: Optional[float] = None
    annual_interest_rate: Optional[float] = None
    tenures_years: List[int] = Field(default_factory=lambda: [3, 5, 7])
    budget: Optional[float] = None
    comparison_targets: List[str] = Field(default_factory=list)
    language: str = "en" # en, hi, gu, hinglish

class PlannedStep(BaseModel):
    step_id: str
    tool_name: str
    input: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    purpose: str
    status: str = "pending" # pending, running, completed, failed

class AgentPlan(BaseModel):
    intent: AgentIntent
    extracted_entities: ExtractedEntities
    steps: List[PlannedStep]
    needs_follow_up: bool = False
    follow_up_question: Optional[str] = None
    follow_up_fields: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    detected_language: str = "en"
    goal: str = ""

# Backward compatibility alias
AgentPlanStep = PlannedStep

class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)
    sources: List[SourceReference] = Field(default_factory=list)
    error_code: Optional[str] = None
    user_safe_error: Optional[str] = None
    error: Optional[str] = None # For compatibility
    source_metadata: Dict[str, Any] = Field(default_factory=dict)
    executed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Backward compatibility alias
ToolExecutionResult = ToolResult

class VerificationReport(BaseModel):
    is_valid: bool
    financial_values_verified: bool = True
    budget_constraints_satisfied: bool = True
    no_unsupported_live_claims: bool = True
    language_preserved: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class AgentRequest(BaseModel):
    conversation_id: Optional[str] = None
    user_id: int
    message_id: Optional[str] = None
    message: str
    locale: Optional[str] = "en"
    conversation_context: List[Dict[str, Any]] = Field(default_factory=list)

class AgentResponse(BaseModel):
    kind: ResponseKind = ResponseKind.TEXT
    content: str = "" # user-facing explanation / markdown text
    answer_text: Optional[str] = None
    plan: Optional[AgentPlan] = None
    tool_results: List[ToolResult] = Field(default_factory=list)
    verification: Optional[VerificationReport] = None
    pricing_quote: Optional[Dict[str, Any]] = None
    emi_options: Optional[List[Dict[str, Any]]] = None
    comparison: Optional[Dict[str, Any]] = None
    comparison_matrix: Optional[Dict[str, Any]] = None # alias
    vehicles: List[Dict[str, Any]] = Field(default_factory=list)
    gallery: Optional[Dict[str, Any]] = None
    vehicle_gallery: Optional[Dict[str, Any]] = None # alias
    sources: List[SourceReference] = Field(default_factory=list)
    follow_up: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)
    data_status: DataStatus = DataStatus.LOCAL
    action_summary: List[str] = Field(default_factory=list)
