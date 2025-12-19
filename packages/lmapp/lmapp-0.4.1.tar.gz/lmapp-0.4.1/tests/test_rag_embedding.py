"""Unit tests for RAG embedding service."""

import pytest

from lmapp.rag.embedding import EmbeddingService, MockEmbeddingModel, OllamaEmbeddingModel


class TestMockEmbeddingModel:
    """Test mock embedding model."""

    def test_embed_single_text(self):
        """Test embedding a single text."""
        model = MockEmbeddingModel(dim=384)
        embedding = model.embed(["Hello world"])

        assert len(embedding) == 1
        assert len(embedding[0]) == 384
        assert all(isinstance(x, float) for x in embedding[0])
        assert all(-1.0 <= x <= 1.0 for x in embedding[0])

    def test_embed_multiple_texts(self):
        """Test embedding multiple texts."""
        model = MockEmbeddingModel(dim=256)
        texts = ["First text", "Second text", "Third text"]

        embeddings = model.embed(texts)

        assert len(embeddings) == 3
        assert all(len(e) == 256 for e in embeddings)

    def test_embed_query(self):
        """Test embedding a query."""
        model = MockEmbeddingModel(dim=384)
        query_embedding = model.embed_query("test query")

        assert len(query_embedding) == 384
        assert all(isinstance(x, float) for x in query_embedding)

    def test_deterministic_embedding(self):
        """Test that same text produces same embedding."""
        model = MockEmbeddingModel(dim=384)
        text = "Deterministic test"

        emb1 = model.embed([text])[0]
        emb2 = model.embed([text])[0]

        assert emb1 == emb2

    def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings."""
        model = MockEmbeddingModel(dim=384)

        emb1 = model.embed(["Text A"])[0]
        emb2 = model.embed(["Text B"])[0]

        assert emb1 != emb2

    def test_model_dimension(self):
        """Test model dimension property."""
        model = MockEmbeddingModel(dim=512)
        assert model.dimension == 512


class TestEmbeddingService:
    """Test embedding service with caching."""

    def test_embedding_cache(self):
        """Test that embeddings are cached."""
        service = EmbeddingService()

        text = "Cache test"
        emb1 = service.embed_texts([text])[0]
        emb2 = service.embed_texts([text])[0]

        # Should be identical from cache
        assert emb1 == emb2

    def test_multiple_embeddings(self):
        """Test embedding multiple texts."""
        service = EmbeddingService()
        texts = ["Text one", "Text two", "Text three"]

        embeddings = service.embed_texts(texts)

        assert len(embeddings) == 3
        assert all(isinstance(e, list) for e in embeddings)

    def test_query_embedding(self):
        """Test query embedding."""
        service = EmbeddingService()
        query = "What is this?"

        embedding = service.embed_query(query)

        assert isinstance(embedding, list)
        assert len(embedding) > 0

    def test_clear_cache(self):
        """Test clearing the cache."""
        service = EmbeddingService()

        text = "Cache clear test"
        _ = service.embed_texts([text])
        service.clear_cache()

        # Cache should be empty
        assert len(service._cache) == 0

    def test_partial_cache_hit(self):
        """Test mixed cached and uncached texts."""
        service = EmbeddingService()

        text1 = "Cached text"
        text2 = "New text"

        # First call - caches text1
        _ = service.embed_texts([text1])

        # Second call - uses cache for text1, computes text2
        embeddings = service.embed_texts([text1, text2])

        assert len(embeddings) == 2


class TestOllamaEmbeddingModel:
    """Test Ollama embedding model."""

    def test_model_properties(self):
        """Test Ollama model properties."""
        model = OllamaEmbeddingModel(model_name="test-model", base_url="http://localhost:11434")

        assert model.model_name == "test-model"
        assert model.base_url == "http://localhost:11434"
        assert model.dimension > 0

    def test_fallback_to_mock(self):
        """Test fallback to mock when Ollama unavailable."""
        model = OllamaEmbeddingModel(base_url="http://invalid-url:0000")

        # Should fall back to mock and still work
        embeddings = model.embed(["Test"])

        assert len(embeddings) == 1
        assert len(embeddings[0]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
