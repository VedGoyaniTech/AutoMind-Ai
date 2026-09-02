import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai.vector_store import LocalFAISSVectorStore
from app.core.config import settings

def rebuild_index():
    print(f"Rebuilding vector index at '{settings.VECTOR_INDEX_PATH}'...")
    vector_store = LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
    vector_store.rebuild_index()
    print("Vector index rebuild complete!")

if __name__ == "__main__":
    rebuild_index()
