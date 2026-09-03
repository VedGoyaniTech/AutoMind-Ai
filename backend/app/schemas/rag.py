from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class VehicleRecordMetadata(BaseModel):
    """Structured vehicle specification metadata schema."""
    vehicle_id: int
    manufacturer: str
    model: str
    variant: str
    body_type: Optional[str] = None
    ex_showroom_price: float
    estimated_on_road_price: Optional[float] = None
    currency: str = "INR"
    fuel_type: str
    transmission: str
    seating_capacity: int
    airbags: int
    safety_rating: Optional[float] = None
    combined_mileage: Optional[float] = None
    electric_range: Optional[float] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    domain: Optional[str] = None
    reliability_score: float = 0.95
    updated_at: Optional[str] = None
    doc_type: str = "vehicle_record"

class KnowledgeChunkMetadata(BaseModel):
    """Unstructured knowledge document chunk schema (brochures, manuals, FAQs, articles)."""
    chunk_id: str
    document_id: str
    doc_hash: str
    title: str
    text: str
    source_url: Optional[str] = None
    source_name: str
    domain: Optional[str] = None
    document_type: str = Field(default="article", description="brochure, manual, article, faq, guide, policy")
    manufacturer_tags: List[str] = Field(default_factory=list)
    model_tags: List[str] = Field(default_factory=list)
    language: str = "en"
    publication_date: Optional[str] = None
    updated_at: Optional[str] = None
    reliability_score: float = 0.90
    doc_type: str = "knowledge_chunk"

class RAGSearchResult(BaseModel):
    """Unified retrieval result item with explicit score, type, and source provenance."""
    evidence_id: str
    doc_type: str # "vehicle_record", "knowledge_chunk", "web_snippet"
    score: float
    title: str
    snippet: str
    source_name: str
    source_url: Optional[str] = None
    domain: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RAGMetadata(BaseModel):
    """Payload passed along with chat SSE stream for transparent citation inspection."""
    total_retrieved: int
    vehicle_records_count: int
    knowledge_chunks_count: int
    web_sources_count: int
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    results: List[RAGSearchResult] = Field(default_factory=list)
