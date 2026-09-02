"""
Vehicle Media Tool — Structured photo gallery retriever.
"""

from typing import Dict, Any, Optional
from app.services.agentic.schemas import ToolExecutionResult
from app.services.vehicle_media import get_vehicle_media_gallery

def execute_vehicle_media(query_text: str) -> ToolExecutionResult:
    try:
        gallery = get_vehicle_media_gallery(query_text)
        return ToolExecutionResult(
            tool_name="get_vehicle_gallery",
            success=gallery is not None,
            data=gallery,
            warnings=[] if gallery else ["No dedicated photo gallery found for vehicle."]
        )
    except Exception as e:
        return ToolExecutionResult(
            tool_name="get_vehicle_gallery",
            success=False,
            error=str(e)
        )
