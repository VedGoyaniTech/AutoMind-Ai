"""
AutoMind AI — Production Hybrid RAG & Fine-Tuned LLM Pipeline
Architecture Flow:
  User Query
     │
     ▼
  API (FastAPI)
     │
     ▼
  Retriever (Vector DB + SQL Search + RRF)
     │
     ▼
  Top-K Context Documents
     │
     ▼
  Prompt Builder (System + Context + Query)
     │
     ▼
  Fine-Tuned Qwen2.5-1.5B (Grounded Provider)
     │
     ▼
  Post-processing & Markdown Synthesis
     │
     ▼
  Final Answer
"""

from typing import Dict, Any, Generator
from sqlalchemy.orm import Session
from app.services.ai.retriever import HybridRetriever
from app.services.ai.context_builder import ContextBuilder
from app.services.ai.llm_provider import GroundedLLMProvider, get_llm_provider
from app.services.ai.query_analyzer import QueryAnalyzer
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.core.config import settings

class ProductionRAGPipeline:
    """Production End-to-End Pipeline combining Vector/SQL RAG with Fine-Tuned LLM."""

    def __init__(self, db: Session, vector_store: LocalFAISSVectorStore):
        self.db = db
        self.vector_store = vector_store
        self.analyzer = QueryAnalyzer()
        self.retriever = HybridRetriever(db, vector_store)
        self.context_builder = ContextBuilder()
        self.llm = get_llm_provider()

    def process_query(self, user_query: str) -> Dict[str, Any]:
        # 1. Query Analysis
        analysis = self.analyzer.analyze(user_query)

        # 2. Hybrid Retrieval (SQL + Vector + DuckDuckGo Web Search)
        docs, sources, web_results = self.retriever.retrieve(
            prompt=user_query,
            filter_schema=analysis["filter_schema"]
        )

        # 3. Context Construction
        context_text = self.context_builder.build_context(
            docs=docs,
            parsed_constraints=analysis["parsed_constraints"],
            web_results=web_results
        )

        # 4. LLM Synthesis
        response_text = self.llm.generate(user_query, context_text)

        return {
            "query": user_query,
            "retrieved_documents": docs,
            "web_results": web_results,
            "sources": sources,
            "response": response_text
        }

    def stream_query(self, user_query: str) -> Generator[str, None, None]:
        analysis = self.analyzer.analyze(user_query)
        docs, _, web_results = self.retriever.retrieve(
            prompt=user_query,
            filter_schema=analysis["filter_schema"]
        )
        context_text = self.context_builder.build_context(
            docs=docs,
            parsed_constraints=analysis["parsed_constraints"],
            web_results=web_results
        )

        for token in self.llm.stream(user_query, context_text):
            yield token
