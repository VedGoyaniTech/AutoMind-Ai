# Test completed
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.config import settings
from app.services.ai.llm_provider import get_llm_provider, NvidiaNIMLLMProvider

print("LLM Provider in settings:", settings.LLM_PROVIDER)
print("NVIDIA Model ID:", settings.NVIDIA_MODEL_ID)

provider = get_llm_provider()
print("Instantiated Provider Class:", provider.__class__.__name__)

test_prompt = "What is the engine spec of BMW M4?"
test_context = "[Web 1] BMW M4 Competition Coupe comes with 3.0L Twin-Turbo Inline-6 (503 HP)"

print("\n--- Testing Live NVIDIA NIM LLM API Call ---")
result = provider.generate(test_prompt, test_context)
print("\nGenerated Response:\n", result[:400])
