import os
import json
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorStore(ABC):
    """Abstract VectorStore interface for pluggable vector search engines."""

    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray) -> None:
        """Add documents and corresponding pre-computed embeddings to the index."""
        pass

    @abstractmethod
    def search(self, query_embedding: np.ndarray, top_k: int = 20) -> List[Dict[str, Any]]:
        """Search nearest vector neighbors for a query embedding."""
        pass

    @abstractmethod
    def delete(self, doc_ids: List[int]) -> None:
        """Remove document vectors by ID."""
        pass

    @abstractmethod
    def rebuild_index(self) -> None:
        """Re-index and clean up vector storage."""
        pass

    @abstractmethod
    def save(self, directory: str) -> None:
        """Persist index and metadata to disk."""
        pass

    @abstractmethod
    def load(self, directory: str) -> bool:
        """Load index and metadata from disk."""
        pass


class LocalFAISSVectorStore(VectorStore):
    """
    High-performance vector store abstraction supporting FAISS index when available,
    with an automatic fallback to normalized Cosine Similarity NumPy search.
    """

    def __init__(self, index_path: str = "./vector_index"):
        self.index_path = index_path
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.use_faiss = False
        self.faiss_index = None

        # Check for faiss
        try:
            import faiss
            self.use_faiss = True
        except ImportError:
            self.use_faiss = False

        if os.path.exists(index_path):
            self.load(index_path)

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray) -> None:
        if len(documents) == 0:
            return

        # Ensure 2D float32 array
        embeddings = np.ascontiguousarray(embeddings.astype("float32"))
        
        # Normalize for Cosine Similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized_embeddings = embeddings / norms

        if self.embeddings is None or len(self.embeddings) == 0:
            self.embeddings = normalized_embeddings
            self.documents = list(documents)
        else:
            self.embeddings = np.vstack([self.embeddings, normalized_embeddings])
            self.documents.extend(documents)

        if self.use_faiss and self.embeddings is not None:
            import faiss
            dimension = self.embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension) # Inner Product on normalized vectors = Cosine Similarity
            self.faiss_index.add(self.embeddings)

        self.save(self.index_path)

    def search(self, query_embedding: np.ndarray, top_k: int = 20) -> List[Dict[str, Any]]:
        if self.embeddings is None or len(self.documents) == 0:
            return []

        # Prepare query vector
        q = np.ascontiguousarray(query_embedding.astype("float32")).reshape(1, -1)
        norm = np.linalg.norm(q)
        if norm > 0:
            q = q / norm

        actual_k = min(top_k, len(self.documents))

        if self.use_faiss and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(q, actual_k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.documents):
                    doc = dict(self.documents[idx])
                    doc["similarity_score"] = float(score)
                    results.append(doc)
            return results

        # Fallback NumPy Cosine Similarity
        scores = np.dot(self.embeddings, q.T).flatten()
        top_indices = np.argsort(scores)[::-1][:actual_k]

        results = []
        for idx in top_indices:
            doc = dict(self.documents[idx])
            doc["similarity_score"] = float(scores[idx])
            results.append(doc)
        return results

    def delete(self, doc_ids: List[int]) -> None:
        if self.embeddings is None or len(self.documents) == 0:
            return
        
        keep_indices = [i for i, doc in enumerate(self.documents) if doc.get("car_variant_id") not in doc_ids]
        if len(keep_indices) == len(self.documents):
            return

        self.documents = [self.documents[i] for i in keep_indices]
        if len(keep_indices) > 0:
            self.embeddings = self.embeddings[keep_indices]
            if self.use_faiss:
                import faiss
                dimension = self.embeddings.shape[1]
                self.faiss_index = faiss.IndexFlatIP(dimension)
                self.faiss_index.add(self.embeddings)
        else:
            self.embeddings = None
            self.faiss_index = None

        self.save(self.index_path)

    def rebuild_index(self) -> None:
        if self.embeddings is not None and self.use_faiss:
            import faiss
            dimension = self.embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)
            self.faiss_index.add(self.embeddings)
        self.save(self.index_path)

    def save(self, directory: str) -> None:
        os.makedirs(directory, exist_ok=True)
        docs_file = os.path.join(directory, "documents.json")
        embeddings_file = os.path.join(directory, "embeddings.npy")

        with open(docs_file, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=2)

        if self.embeddings is not None:
            np.save(embeddings_file, self.embeddings)

    def load(self, directory: str) -> bool:
        docs_file = os.path.join(directory, "documents.json")
        embeddings_file = os.path.join(directory, "embeddings.npy")

        if not os.path.exists(docs_file) or not os.path.exists(embeddings_file):
            return False

        try:
            with open(docs_file, "r", encoding="utf-8") as f:
                self.documents = json.load(f)

            self.embeddings = np.load(embeddings_file)

            if self.use_faiss and self.embeddings is not None and len(self.embeddings) > 0:
                import faiss
                dimension = self.embeddings.shape[1]
                self.faiss_index = faiss.IndexFlatIP(dimension)
                self.faiss_index.add(self.embeddings)
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Global singleton vector store — imported by chat.py and retriever.py
# Loads existing index from disk on startup; starts empty if no index yet.
# ---------------------------------------------------------------------------
from app.core.config import settings

global_vector_store = LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
