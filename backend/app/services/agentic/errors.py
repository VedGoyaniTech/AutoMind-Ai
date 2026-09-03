"""
AutoMind AI — Agentic Exception & Error Definitions
"""

class AgenticError(Exception):
    """Base exception for all agentic layer failures."""
    def __init__(self, message: str, code: str = "AGENTIC_ERROR", user_safe_message: str = "An error occurred while processing your request."):
        super().__init__(message)
        self.code = code
        self.user_safe_message = user_safe_message

class PlanningError(AgenticError):
    """Raised when query intent or entity extraction fails."""
    def __init__(self, message: str, user_safe_message: str = "Could not create an execution plan for your request."):
        super().__init__(message, code="PLANNING_ERROR", user_safe_message=user_safe_message)

class ToolExecutionError(AgenticError):
    """Raised when a specific tool fails execution."""
    def __init__(self, tool_name: str, message: str, user_safe_message: str = "A tool failed to execute."):
        super().__init__(f"Tool '{tool_name}' failed: {message}", code="TOOL_EXECUTION_ERROR", user_safe_message=user_safe_message)
        self.tool_name = tool_name

class VerificationError(AgenticError):
    """Raised when verifier detects contradictory, fabricated, or invalid output."""
    def __init__(self, message: str, user_safe_message: str = "Generated response failed verification safety checks."):
        super().__init__(message, code="VERIFICATION_ERROR", user_safe_message=user_safe_message)
