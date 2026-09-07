"""
AutoMind AI — Web Research Agent Tool
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.services.agentic.tools.base import BaseAgentTool
from app.services.agentic.schemas import ToolResult, SourceReference, SourceType, ConfidenceLevel
from app.services.ai.duckduckgo_search import duckduckgo_search_service
from app.core.config import settings

logger = logging.getLogger("automind.agentic.web_research")

TRUSTED_DOMAINS = [
    "autocarindia.com", "carwale.com", "cardekho.com", "zigwheels.com",
    "overdrive.in", "auto.hindustantimes.com", "timesdrive.in",
    "tatamotors.com", "hyundai.com", "marutisuzuki.com", "mahindra.com", "toyotabharat.com",
    "morth.nic.in", "parivahan.gov.in"
]

class WebResearchTool(BaseAgentTool):
    name = "web_research"
    description = "Searches trusted automotive web index via DuckDuckGo for vehicle launches, historical facts, and missing specs."

    def execute(self, query: str, target_year: Optional[int] = None, max_results: int = 5) -> ToolResult:
        try:
            raw_results = duckduckgo_search_service.search(query=query, max_results=max_results)
            validated_sources: List[SourceReference] = []
            valid_results: List[Dict[str, Any]] = []
            warnings: List[str] = []

            for r in raw_results:
                url = r.get("url", "").strip()
                title = r.get("title", "Automotive Research Article").strip()
                snippet = r.get("snippet", "").strip()

                # Filter out raw search engine urls
                if not url.startswith("http") or "duckduckgo.com" in url or "google.com" in url:
                    continue

                domain = ""
                try:
                    domain = url.split("//")[1].split("/")[0].lower()
                except Exception:
                    domain = "automotive.org"

                is_trusted = any(td in domain for td in TRUSTED_DOMAINS)
                confidence = ConfidenceLevel.HIGH if is_trusted else ConfidenceLevel.MEDIUM

                ref = SourceReference(
                    title=title,
                    url=url,
                    domain=domain,
                    source_type=SourceType.WEB_RESEARCH if not is_trusted else SourceType.TRUSTED_AUTOMOTIVE_PUBLICATION,
                    retrieved_at=datetime.now(timezone.utc).isoformat(),
                    confidence=confidence
                )
                validated_sources.append(ref)
                valid_results.append({
                    "title": title,
                    "url": url,
                    "domain": domain,
                    "snippet": snippet,
                    "is_trusted": is_trusted
                })

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={"results": valid_results, "query": query, "target_year": target_year},
                sources=validated_sources,
                warnings=warnings,
                source_metadata={"source": "duckduckgo_web_grounding", "count": len(valid_results)}
            )
        except Exception as e:
            logger.warning(f"[WebResearchTool] Error searching web: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                data={"results": [], "query": query},
                error=str(e),
                user_safe_error="Web research search unavailable."
            )

def execute_web_research(query: str, target_year: Optional[int] = None, max_results: int = 5) -> ToolResult:
    tool = WebResearchTool()
    return tool.execute(query=query, target_year=target_year, max_results=max_results)
