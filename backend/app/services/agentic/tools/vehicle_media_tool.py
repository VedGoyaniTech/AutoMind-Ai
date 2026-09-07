"""
AutoMind AI — Vehicle Media & Gallery Agent Tool
"""

from typing import Dict, Any, Optional
from app.services.agentic.tools.base import BaseAgentTool
from app.services.agentic.schemas import ToolResult
from app.services.vehicle_media import get_vehicle_gallery_for_query

class VehicleMediaTool(BaseAgentTool):
    name = "get_vehicle_gallery"
    description = "Retrieves high-resolution curated image media gallery and 360 viewer assets for a vehicle."

    def execute(self, model: Optional[str] = None, query_text: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            name = (model or query_text or kwargs.get("car_name") or "Thar").strip()
            gallery = get_vehicle_gallery_for_query(name)
            if gallery and gallery.get("images"):
                return ToolResult(tool_name=self.name, success=True, data=gallery)
            return ToolResult(tool_name=self.name, success=False, error="No media found", warnings=["No gallery assets available."])
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=str(e), user_safe_error="Media service error.")

def execute_vehicle_media(model: Optional[str] = None, query_text: Optional[str] = None, **kwargs) -> ToolResult:
    tool = VehicleMediaTool()
    return tool.execute(model=model, query_text=query_text, **kwargs)
