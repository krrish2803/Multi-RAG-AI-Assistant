"""Embedding service using NVIDIA NIM API."""

from typing import Optional

from app.config import Settings


class EmbeddingService:
    """Service for generating text embeddings using NVIDIA NIM."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.dimension = settings.qdrant_vector_size
        self._model = None

    @property
    def model(self):
        """Lazy-load the NVIDIA embeddings model."""
        if self._model is None:
            try:
                from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
                self._model = NVIDIAEmbeddings(
                    model=self.settings.nvidia_embed_model,
                    api_key=self.settings.nvidia_api_key,
                    base_url=self.settings.nvidia_base_url,
                )
            except Exception:
                self._model = None
        return self._model

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        if self.model is None:
            return self._fallback_embedding(text)

        try:
            result = await self.model.ainvoke(text)
            return result
        except Exception:
            return self._fallback_embedding(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        if self.model is None:
            return [self._fallback_embedding(t) for t in texts]

        try:
            results = await self.model.abatch_invoke(texts)
            return results
        except Exception:
            return [self._fallback_embedding(t) for t in texts]

    def _fallback_embedding(self, text: str) -> list[float]:
        """Generate a simple fallback embedding using hash-based approach."""
        import hashlib
        hash_bytes = hashlib.sha512(text.encode()).digest()
        # Create deterministic vector from hash
        vector = []
        for i in range(self.dimension):
            byte_idx = i % len(hash_bytes)
            vector.append((hash_bytes[byte_idx] - 128) / 128.0)
        return vector
