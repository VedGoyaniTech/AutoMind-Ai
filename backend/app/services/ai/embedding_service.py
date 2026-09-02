import numpy as np
import logging
from typing import List, Union
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_ID):
        self.model_name = model_name
        self._model = None
        self._fallback_dim = 384
        self.device = "cpu"

    @property
    def dimension(self) -> int:
        return self._fallback_dim

    @property
    def model(self):
        if self._model is None:
            try:
                import torch
                from sentence_transformers import SentenceTransformer
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Loading SentenceTransformer '{self.model_name}' on device: {self.device.upper()}")
                self._model = SentenceTransformer(self.model_name, device=self.device)
            except Exception as e:
                logger.warning(f"SentenceTransformer init notice ({e}). Using CPU fallback.")
                self._model = False
        return self._model if self._model is not False else None

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, self._fallback_dim), dtype=np.float32)

        mdl = self.model
        if mdl is not None:
            try:
                embeddings = mdl.encode(texts, convert_to_numpy=True, show_progress_bar=False, device=self.device)
                return embeddings.astype(np.float32)
            except Exception as e:
                logger.warning(f"Error during GPU encoding ({e}). Using CPU encoding.")
                pass

        # Fallback hashing vectorizer if model is loading
        embeddings = []
        for text in texts:
            vec = np.zeros(self._fallback_dim, dtype=np.float32)
            words = text.lower().split()
            for w in words:
                idx = abs(hash(w)) % self._fallback_dim
                vec[idx] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            embeddings.append(vec)
        return np.array(embeddings, dtype=np.float32)

# Global singleton
embedding_service = EmbeddingService()
