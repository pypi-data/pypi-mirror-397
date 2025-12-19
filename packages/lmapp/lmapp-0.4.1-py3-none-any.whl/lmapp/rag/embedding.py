"""Embedding service for RAG."""

from abc import ABC, abstractmethod
from typing import List, Optional
import hashlib


class EmbeddingModel(ABC):
    """Abstract embedding model."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for query.

        Args:
            query: Query text

        Returns:
            Embedding vector
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding dimension."""
        pass


class MockEmbeddingModel(EmbeddingModel):
    """Mock embedding for testing/development.

    Generates deterministic fake embeddings based on text content.
    """

    def __init__(self, dim: int = 384):
        self._dim = dim

    @property
    def dimension(self) -> int:
        return self._dim

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings."""
        return [self._mock_embed(text) for text in texts]

    def embed_query(self, query: str) -> List[float]:
        """Generate mock query embedding."""
        return self._mock_embed(query)

    def _mock_embed(self, text: str) -> List[float]:
        """Generate deterministic mock embedding from text."""
        # Use hash of text to seed deterministic random values
        hash_obj = hashlib.sha256(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)

        # Generate embedding values deterministically
        embedding = []
        for i in range(self._dim):
            # Use different seed for each dimension
            val = ((hash_int + i * 31) % 10000) / 10000.0
            embedding.append(val * 2.0 - 1.0)  # Scale to [-1, 1]

        return embedding


class OllamaEmbeddingModel(EmbeddingModel):
    """Ollama embedding model."""

    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self._dim = 384  # Default for nomic-embed-text

    @property
    def dimension(self) -> int:
        return self._dim

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings via Ollama."""
        try:
            import requests

            results = []
            for text in texts:
                response = requests.post(
                    f"{self.base_url}/api/embed",
                    json={"model": self.model_name, "input": text},
                )
                if response.status_code == 200:
                    embedding = response.json().get("embedding", [])
                    results.append(embedding)
                else:
                    print(f"Failed to embed text: {response.status_code}")
                    results.append([0.0] * self._dim)

            return results
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            # Fall back to mock
            return MockEmbeddingModel(self._dim).embed(texts)

    def embed_query(self, query: str) -> List[float]:
        """Generate query embedding via Ollama."""
        return self.embed([query])[0]


class EmbeddingService:
    """Service for managing embeddings."""

    def __init__(self, model: Optional[EmbeddingModel] = None):
        self.model = model or MockEmbeddingModel()
        self._cache = {}

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with caching.

        Args:
            texts: Texts to embed

        Returns:
            Embedding vectors
        """
        uncached = []
        uncached_indices = []

        # Check cache
        for i, text in enumerate(texts):
            if text in self._cache:
                continue
            uncached.append(text)
            uncached_indices.append(i)

        # Embed uncached texts
        if uncached:
            embeddings = self.model.embed(uncached)
            for text, emb in zip(uncached, embeddings):
                self._cache[text] = emb

        # Assemble results in original order
        results = [None] * len(texts)
        for idx, text in enumerate(texts):
            results[idx] = self._cache[text]

        return results

    def embed_query(self, query: str) -> List[float]:
        """Embed a query with caching."""
        if query in self._cache:
            return self._cache[query]

        embedding = self.model.embed_query(query)
        self._cache[query] = embedding
        return embedding

    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self._cache.clear()
