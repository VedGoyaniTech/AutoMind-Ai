"""
AutoMind AI — Base Agent Tool Abstract Interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.services.agentic.schemas import ToolResult

class BaseAgentTool(ABC):
    """Abstract base class for all typed agent tools."""

    name: str = "base_tool"
    description: str = "Base tool description"

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with keyword arguments and return a typed ToolResult."""
        pass
