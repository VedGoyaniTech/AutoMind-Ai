import os
import sys
import time
import torch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.services.ai.query_analyzer import QueryAnalyzer
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.services.ai.retriever import HybridRetriever
from app.services.ai.context_builder import ContextBuilder
from app.services.ai.llm_provider import GroundedLLMProvider
from app.core.config import settings

def main():
    print("=" * 70)
    print("      AUTOMIND AI — INTERACTIVE TERMINAL RAG & MODEL CHAT")
    print("=" * 70)

    # Hardware Info Check
    gpu_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_available else "CPU Mode (PyTorch CPU Engine Active)"
    vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2) if gpu_available else 0

    print(f"  [Hardware Info] CUDA Acceleration: {'ENABLED 🚀' if gpu_available else 'DISABLED (CPU Mode)'}")
    print(f"  [Hardware Info] Active Device    : {gpu_name}")
    if gpu_available:
        print(f"  [Hardware Info] Total GPU vRAM   : {vram_gb} GB")
    else:
        print("  [Notice] To enable GPU acceleration, install CUDA-enabled PyTorch:")
        print("           pip install torch --index-url https://download.pytorch.org/whl/cu121")
    print("=" * 70)
    print("\nType your car question below (or type 'exit' or 'quit' to stop).\n")

    db = SessionLocal()
    vector_store = LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
    analyzer = QueryAnalyzer()
    retriever = HybridRetriever(db, vector_store)
    context_builder = ContextBuilder()
    llm = GroundedLLMProvider()

    try:
        while True:
            try:
                user_input = input("\n[User Prompt] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting interactive chat...")
                break

            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break

            t0 = time.time()
            print("\n  ⚙ Analyzing query & extracting constraints...")
            analysis = analyzer.analyze(user_input)
            print(f"  ✔ Intent Detected : {analysis['intent']}")
            print(f"  ✔ Filter Schema   : {analysis['parsed_constraints']}")

            print("  🔍 Querying MySQL & FAISS Vector Index...")
            docs, sources = retriever.retrieve(user_input, analysis["filter_schema"])
            print(f"  ✔ Matches Found   : {len(docs)} car models, {len(sources)} verified sources")

            context_text = context_builder.build_context(docs, analysis["parsed_constraints"])

            print("\n  🤖 AutoMind AI Response (Streaming):\n" + "-" * 50)
            t_stream_start = time.time()
            
            for token in llm.stream(user_input, context_text):
                print(token, end="", flush=True)
            
            t_stream_end = time.time()
            print("\n" + "-" * 50)
            print(f"  [Performance] Total turn latency: {round(t_stream_end - t0, 3)}s (Streaming: {round(t_stream_end - t_stream_start, 3)}s)")

            if sources:
                sources_str = ", ".join([f"{s.title} ({s.domain})" for s in sources])
                print(f"  [Verified Sources Cited]: {sources_str}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
