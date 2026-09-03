"""
AutoMind AI — Agent Orchestrator (Part 6 Specification)
"""

import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
from sqlalchemy.orm import Session

from app.services.agentic.schemas import (
    AgentPlan, AgentResponse, ToolResult, SourceReference, ResponseKind, DataStatus
)
from app.services.agentic.planner import AgentPlanner
from app.services.agentic.verifier import AgentVerifier
from app.services.agentic.response_builder import ResponseBuilder

# Import tools
from app.services.agentic.tools.vehicle_search_tool import execute_vehicle_search
from app.services.agentic.tools.pricing_quote_tool import execute_pricing_quote
from app.services.agentic.tools.emi_tool import execute_emi_calculation
from app.services.agentic.tools.comparison_tool import execute_vehicle_comparison
from app.services.agentic.tools.vehicle_media_tool import execute_vehicle_media
from app.services.agentic.tools.vehicle_details_tool import execute_vehicle_details
from app.services.agentic.tools.web_research_tool import execute_web_research

logger = logging.getLogger("automind.agentic.orchestrator")

class AgentOrchestrator:
    """
    Central controller executing planned tool steps, verifying data integrity,
    and building safe user-visible responses.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.planner = AgentPlanner()
        self.verifier = AgentVerifier()
        self.response_builder = ResponseBuilder()

    def run(self, user_prompt: str, max_steps: int = 5) -> AgentResponse:
        logger.info(f"[AgentOrchestrator] Processing: {user_prompt[:50]}")
        plan = self.planner.plan(user_prompt)
        tool_results: List[ToolResult] = []

        # If planner detected required missing fields, immediately return follow-up response
        if plan.needs_follow_up:
            verification = self.verifier.verify(user_prompt, plan.detected_language, [])
            content = self.response_builder.build_response(plan, [], verification)
            return AgentResponse(
                kind=ResponseKind.FOLLOW_UP,
                content=content,
                answer_text=content,
                plan=plan,
                tool_results=[],
                verification=verification,
                follow_up={"fields": plan.follow_up_fields, "question": plan.follow_up_question}
            )

        pricing_quote_data = None
        emi_options_data = None
        gallery_data = None
        comp_matrix_data = None
        all_sources: List[SourceReference] = []

        # Execute planned steps with loop boundary safety
        for step in plan.steps[:max_steps]:
            step.status = "running"
            result: Optional[ToolResult] = None

            try:
                if step.tool_name == "calculate_pricing_quote":
                    result = execute_pricing_quote(db=self.db, **step.input)
                    if result.success and result.data:
                        pricing_quote_data = result.data

                elif step.tool_name == "calculate_emi":
                    result = execute_emi_calculation(**step.input)
                    if result.success and result.data:
                        emi_options_data = result.data.get("tenure_options")

                elif step.tool_name == "search_vehicles":
                    result = execute_vehicle_search(db=self.db, **step.input)

                elif step.tool_name == "compare_vehicles":
                    result = execute_vehicle_comparison(db=self.db, **step.input)
                    if result.success and result.data:
                        comp_matrix_data = result.data

                elif step.tool_name == "get_vehicle_gallery":
                    result = execute_vehicle_media(**step.input)
                    if result.success and result.data:
                        gallery_data = result.data

                elif step.tool_name == "get_vehicle_details":
                    result = execute_vehicle_details(db=self.db, **step.input)

                elif step.tool_name == "web_research":
                    result = execute_web_research(**step.input)

                if result:
                    step.status = "completed" if result.success else "failed"
                    tool_results.append(result)
                    if result.sources:
                        all_sources.extend(result.sources)
            except Exception as step_err:
                logger.error(f"[AgentOrchestrator] Step {step.step_id} failed: {step_err}")
                step.status = "failed"
                tool_results.append(ToolResult(
                    tool_name=step.tool_name,
                    success=False,
                    error=str(step_err),
                    user_safe_error="Tool step failed safely."
                ))

        # Verification Stage
        verification = self.verifier.verify(
            user_prompt=user_prompt,
            detected_language=plan.detected_language,
            tool_results=tool_results
        )

        # Build Response
        content = self.response_builder.build_response(
            plan=plan,
            tool_results=tool_results,
            verification=verification
        )

        # Determine response kind
        kind = ResponseKind.TEXT
        if pricing_quote_data:
            kind = ResponseKind.PRICING_QUOTE
        elif comp_matrix_data:
            kind = ResponseKind.COMPARISON
        elif gallery_data:
            kind = ResponseKind.GALLERY

        return AgentResponse(
            kind=kind,
            content=content,
            answer_text=content,
            plan=plan,
            tool_results=tool_results,
            verification=verification,
            pricing_quote=pricing_quote_data,
            emi_options=emi_options_data,
            comparison=comp_matrix_data,
            comparison_matrix=comp_matrix_data,
            gallery=gallery_data,
            vehicle_gallery=gallery_data,
            sources=all_sources
        )

# Global singleton
agent_orchestrator = AgentOrchestrator()
