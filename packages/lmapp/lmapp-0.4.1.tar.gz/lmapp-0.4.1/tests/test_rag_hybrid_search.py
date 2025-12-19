"""Unit tests for hybrid RAG search."""

import pytest

from lmapp.rag.hybrid_search import BM25Searcher, HybridSearcher, SearchRanking


class TestBM25Searcher:
    """Test BM25 keyword search."""

    def test_bm25_search_basic(self):
        """Test basic BM25 search."""
        searcher = BM25Searcher()
        documents = [
            "Python is a programming language",
            "Java is also a programming language",
            "Dogs are cute pets",
        ]

        results = searcher.search("programming language", documents, k=2)

        assert len(results) <= 2
        # Python and Java docs should rank higher than dog doc
        doc_indices = [idx for idx, _ in results]
        assert 2 not in doc_indices

    def test_bm25_empty_query(self):
        """Test BM25 with empty query."""
        searcher = BM25Searcher()
        documents = ["Test document"]

        results = searcher.search("", documents)

        assert len(results) == 0

    def test_bm25_k_parameter(self):
        """Test BM25 respects k parameter."""
        searcher = BM25Searcher()
        documents = [f"Document {i}" for i in range(10)]

        results = searcher.search("document", documents, k=3)

        assert len(results) <= 3

    def test_bm25_scoring(self):
        """Test BM25 scoring is non-negative."""
        searcher = BM25Searcher()
        documents = [
            "test document",
            "another document",
        ]

        results = searcher.search("test", documents, k=2)

        assert all(score >= 0 for _, score in results)


class TestHybridSearcher:
    """Test hybrid semantic + keyword search."""

    def test_hybrid_search_basic(self):
        """Test basic hybrid search."""
        searcher = HybridSearcher(semantic_weight=0.7, keyword_weight=0.3)

        documents = [
            "Machine learning is important",
            "Deep learning uses neural networks",
            "Cats are animals",
        ]

        # Mock semantic scores
        semantic_scores = [
            (0, 0.9),  # Machine learning doc
            (1, 0.85),  # Deep learning doc
            (2, 0.1),  # Cats doc
        ]

        results = searcher.search(
            "machine learning neural networks",
            documents,
            semantic_scores,
            k=2,
            fusion_method="weighted",
        )

        assert len(results) <= 2
        assert all(isinstance(r, SearchRanking) for r in results)

    def test_hybrid_ranking_order(self):
        """Test hybrid results are ranked by combined score."""
        searcher = HybridSearcher()

        documents = ["First", "Second", "Third"]
        semantic_scores = [(0, 0.9), (1, 0.8), (2, 0.1)]

        results = searcher.search("test", documents, semantic_scores, k=3)

        # Results should be ordered by combined score
        scores = [r.combined_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_hybrid_score_components(self):
        """Test hybrid search includes component scores."""
        searcher = HybridSearcher(semantic_weight=0.6, keyword_weight=0.4)

        documents = ["Test document one", "Test document two"]
        semantic_scores = [(0, 0.8), (1, 0.7)]

        results = searcher.search("test", documents, semantic_scores, k=2)

        for result in results:
            assert result.semantic_score >= 0
            assert result.keyword_score >= 0
            assert result.combined_score >= 0

    def test_hybrid_fusion_methods(self):
        """Test different fusion methods."""
        documents = ["First doc", "Second doc", "Third doc"]
        semantic_scores = [(0, 0.9), (1, 0.8), (2, 0.1)]

        searcher_weighted = HybridSearcher()
        results_weighted = searcher_weighted.search(
            "test",
            documents,
            semantic_scores,
            k=2,
            fusion_method="weighted",
        )

        searcher_rrf = HybridSearcher()
        results_rrf = searcher_rrf.search(
            "test",
            documents,
            semantic_scores,
            k=2,
            fusion_method="reciprocal_rank",
        )

        assert len(results_weighted) <= 2
        assert len(results_rrf) <= 2

    def test_hybrid_with_zero_scores(self):
        """Test hybrid search with zero semantic scores."""
        searcher = HybridSearcher()

        documents = ["Test one", "Test two", "Other"]
        semantic_scores = [(0, 0.0), (1, 0.0), (2, 0.0)]

        # Should still work, rely on keyword search
        results = searcher.search("test", documents, semantic_scores, k=2)

        assert len(results) > 0

    def test_search_preview_generation(self):
        """Test content preview generation."""
        searcher = HybridSearcher()

        long_doc = "This is a very long document. " * 50
        documents = [long_doc, "Short"]
        semantic_scores = [(0, 0.9), (1, 0.1)]

        results = searcher.search("test", documents, semantic_scores, k=1)

        # Preview should be truncated
        for result in results:
            assert len(result.content_preview) <= 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
