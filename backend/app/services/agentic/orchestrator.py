"""
Agent Orchestrator — Central execution controller coordinating Planner, Typed Tools, Verifier, and Response Builder.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.services.agentic.schemas import AgentPlan, AgentResponse, ToolExecutionResult
from app.services.agentic.planner import AgentPlanner
from app.services.agentic.verifier import AgentVerifier
from app.services.agentic.response_builder import ResponseBuilder

# Import tools
from app.services.agentic.tools.vehicle_search import execute_vehicle_search
from app.services.agentic.tools.pricing_quote import execute_pricing_quote
from app.services.agentic.tools.emi import execute_emi_calculation
from app.services.agentic.tools.comparison import execute_vehicle_comparison
from app.services.agentic.tools.vehicle_media import execute_vehicle_media
from app.services.agentic.tools.vehicle_details import execute_vehicle_details

logger = logging.getLogger("automind.agentic")

class AgentOrchestrator:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.planner = AgentPlanner()
        self.verifier = AgentVerifier()
        self.response_builder = ResponseBuilder()

    def run(self, user_prompt: str, max_steps: int = 5) -> AgentResponse:
        logger.info(f"Agent Orchestrator starting for goal: {user_prompt}")
        plan = self.planner.plan(user_prompt)
        tool_results: List[ToolExecutionResult] = []

        pricing_quote_data = None
        gallery_data = None
        comp_matrix_data = None

        # Execute planned steps with loop boundary safety
        for step in plan.steps[:max_steps]:
            step.status = "running"
            result = None

            if step.tool_name == "calculate_pricing_quote":
                result = execute_pricing_quote(db=self.db, **step.arguments)
                if result.success and result.data:
                    pricing_quote_data = result.data

            elif step.tool_name == "search_vehicles":
                result = execute_vehicle_search(db=self.db, **step.arguments)

            elif step.tool_name == "calculate_emi":
                result = execute_emi_calculation(**step.arguments)

            elif step.tool_name == "compare_vehicles":
                result = execute_vehicle_comparison(db=self.db, **step.arguments)
                if result.success and result.data:
                    comp_matrix_data = result.data

            elif step.tool_name == "get_vehicle_gallery":
                result = execute_vehicle_media(**step.arguments)
                if result.success and result.data:
                    gallery_data = result.data

            elif step.tool_name == "get_vehicle_details":
                result = execute_vehicle_details(db=self.db, **step.arguments)

            if result:
                step.status = "completed" if result.success else "failed"
                tool_results.append(result)

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

        return AgentResponse(
            content=content,
            plan=plan,
            tool_results=tool_results,
            verification=verification,
            pricing_quote=pricing_quote_data,
            vehicle_gallery=gallery_data,
            comparison_matrix=comp_matrix_data
        )

# Global singleton
agent_orchestrator = AgentOrchestrator()
