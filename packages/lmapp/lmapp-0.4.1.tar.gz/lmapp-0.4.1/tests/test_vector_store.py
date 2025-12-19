"""Tests for vector store backends and citation tracking."""

import asyncio
import pytest
from datetime import datetime, timezone

from src.lmapp.rag.vector_store_impl import InMemoryVectorStore, ChromaDBVectorStore
from src.lmapp.rag.vector_store import VectorDocument
from src.lmapp.rag.citation_tracker import Citation, CitationChain, CitationTracker


def run_async_test(coro):
    """Helper to run async tests."""
    return asyncio.run(coro)


# Test data
TEST_DOCS = [
    VectorDocument(
        doc_id="doc1",
        text="Machine learning is a subset of artificial intelligence.",
        vector=[0.1, 0.2, 0.3, 0.4, 0.5],
        metadata={"topic": "ai", "type": "article"},
        timestamp=datetime.now(timezone.utc),
        source="wikipedia",
    ),
    VectorDocument(
        doc_id="doc2",
        text="Deep learning uses neural networks with multiple layers.",
        vector=[0.15, 0.25, 0.35, 0.45, 0.55],
        metadata={"topic": "ai", "type": "article"},
        timestamp=datetime.now(timezone.utc),
        source="research",
    ),
    VectorDocument(
        doc_id="doc3",
        text="Natural language processing enables computers to understand text.",
        vector=[0.2, 0.3, 0.4, 0.5, 0.6],
        metadata={"topic": "nlp", "type": "article"},
        timestamp=datetime.now(timezone.utc),
        source="textbook",
    ),
]

TEST_QUERY_VECTOR = [0.12, 0.22, 0.32, 0.42, 0.52]


class TestInMemoryVectorStore:
    """Test in-memory vector store."""

    @pytest.fixture
    def store(self):
        """Create test store."""
        return InMemoryVectorStore()

    def test_add_document(self, store):
        """Test adding documents."""

        async def run_test():
            doc_id = await store.add_document(TEST_DOCS[0])
            assert doc_id == "doc1"
            retrieved = await store.get_document("doc1")
            assert retrieved is not None
            assert retrieved.text == TEST_DOCS[0].text

        run_async_test(run_test())

    def test_search(self, store):
        """Test vector search."""

        async def run_test():
            for doc in TEST_DOCS:
                await store.add_document(doc)

            results = await store.search(TEST_QUERY_VECTOR, top_k=2)

            assert len(results) <= 2
            assert all(r.similarity >= 0 for r in results)
            if len(results) > 1:
                assert results == sorted(results, key=lambda x: -x.similarity)

        run_async_test(run_test())

    def test_search_with_filter(self, store):
        """Test filtered search."""

        async def run_test():
            for doc in TEST_DOCS:
                await store.add_document(doc)

            results = await store.search(
                TEST_QUERY_VECTOR,
                top_k=5,
                filter_metadata={"topic": "ai"},
            )

            assert all(r.metadata.get("topic") == "ai" for r in results)

        run_async_test(run_test())

    def test_delete_document(self, store):
        """Test document deletion."""

        async def run_test():
            await store.add_document(TEST_DOCS[0])
            assert await store.delete_document("doc1") is True

            retrieved = await store.get_document("doc1")
            assert retrieved is None

        run_async_test(run_test())

    def test_update_document(self, store):
        """Test document update."""

        async def run_test():
            await store.add_document(TEST_DOCS[0])

            updated_doc = VectorDocument(
                doc_id="doc1",
                text="Updated text",
                vector=[0.5, 0.5, 0.5, 0.5, 0.5],
                metadata={"topic": "updated"},
                timestamp=datetime.now(timezone.utc),
                source="wikipedia",
            )

            assert await store.update_document(updated_doc) is True
            retrieved = await store.get_document("doc1")
            assert retrieved.text == "Updated text"

        run_async_test(run_test())

    def test_list_documents(self, store):
        """Test listing documents."""

        async def run_test():
            for doc in TEST_DOCS:
                await store.add_document(doc)

            all_docs = await store.list_documents(limit=10)
            assert len(all_docs) == 3

            ai_docs = await store.list_documents(source_filter="wikipedia")
            assert len(ai_docs) == 1

        run_async_test(run_test())

    def test_clear(self, store):
        """Test clearing store."""

        async def run_test():
            for doc in TEST_DOCS:
                await store.add_document(doc)

            await store.clear()
            all_docs = await store.list_documents()
            assert len(all_docs) == 0

        run_async_test(run_test())

    def test_stats(self, store):
        """Test store statistics."""

        async def run_test():
            for doc in TEST_DOCS:
                await store.add_document(doc)

            stats = await store.get_stats()
            assert stats["total_documents"] == 3
            assert stats["type"] == "memory"
            assert stats["documents_added"] == 3

        run_async_test(run_test())


class TestCitationTracker:
    """Test citation tracking."""

    @pytest.fixture
    def tracker(self):
        """Create test tracker."""
        return CitationTracker()

    def test_start_chain(self, tracker):
        """Test starting citation chain."""
        chain = tracker.start_chain()
        assert chain is not None
        assert len(chain.citations) == 0

    def test_add_citation(self, tracker):
        """Test adding citations."""
        tracker.start_chain()

        citation = Citation(
            source="test.pdf",
            doc_id="doc1",
            chunk_index=0,
            text="Test text",
            similarity=0.95,
            timestamp=datetime.now(timezone.utc),
        )

        tracker.add_citation(citation)
        chain = tracker._active_chain

        assert len(chain.citations) == 1
        assert "test.pdf" in chain.sources

    def test_finalize_chain(self, tracker):
        """Test finalizing chain."""
        tracker.start_chain()

        citation = Citation(
            source="test.pdf",
            doc_id="doc1",
            chunk_index=0,
            text="Test",
            similarity=0.9,
            timestamp=datetime.now(timezone.utc),
        )
        tracker.add_citation(citation)

        chain = tracker.finalize_chain()

        assert len(tracker._completed_chains) == 1
        assert tracker._active_chain is None
        assert len(chain.citations) == 1

    def test_citation_chain_merge(self):
        """Test merging citation chains."""
        chain1 = CitationChain()
        chain2 = CitationChain()

        citation1 = Citation(
            source="source1",
            doc_id="doc1",
            chunk_index=0,
            text="Text 1",
            similarity=0.8,
            timestamp=datetime.now(timezone.utc),
        )
        citation2 = Citation(
            source="source2",
            doc_id="doc2",
            chunk_index=0,
            text="Text 2",
            similarity=0.9,
            timestamp=datetime.now(timezone.utc),
        )

        chain1.add_citation(citation1)
        chain2.add_citation(citation2)

        merged = chain1.merge_citations(chain2)

        assert len(merged.citations) == 2
        assert len(merged.sources) == 2

    def test_format_citations_markdown(self, tracker):
        """Test markdown citation formatting."""
        tracker.start_chain()

        citation = Citation(
            source="test.pdf",
            doc_id="doc1",
            chunk_index=5,
            text="Test",
            similarity=0.87,
            timestamp=datetime.now(timezone.utc),
        )
        tracker.add_citation(citation)

        chain = tracker._active_chain
        formatted = tracker.format_citations(chain, format_type="markdown")

        assert "test.pdf" in formatted
        assert "87.00%" in formatted
        assert "doc1" in formatted

    def test_format_citations_html(self, tracker):
        """Test HTML citation formatting."""
        tracker.start_chain()

        citation = Citation(
            source="test.pdf",
            doc_id="doc1",
            chunk_index=0,
            text="Test",
            similarity=0.9,
            timestamp=datetime.now(timezone.utc),
        )
        tracker.add_citation(citation)

        chain = tracker._active_chain
        formatted = tracker.format_citations(chain, format_type="html")

        assert "<ol>" in formatted
        assert "test.pdf" in formatted

    def test_citation_stats(self, tracker):
        """Test citation statistics."""
        tracker.start_chain()

        for i, doc in enumerate(TEST_DOCS):
            citation = Citation(
                source=doc.source,
                doc_id=doc.doc_id,
                chunk_index=i,
                text=doc.text,
                similarity=0.8 + (i * 0.05),
                timestamp=datetime.now(timezone.utc),
            )
            tracker.add_citation(citation)

        chain = tracker._active_chain
        stats = chain.get_citation_stats()

        assert stats["total_citations"] == 3
        assert stats["unique_sources"] == 3
        assert stats["avg_similarity"] > 0


class TestVectorStoreSimilarity:
    """Test similarity calculations."""

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""

        async def run_test():
            store = InMemoryVectorStore()

            # Identical vectors
            sim_identical = store._cosine_similarity([1, 0, 0], [1, 0, 0])
            assert abs(sim_identical - 1.0) < 0.001

            # Orthogonal vectors
            sim_orthogonal = store._cosine_similarity([1, 0], [0, 1])
            assert abs(sim_orthogonal - 0.0) < 0.001

            # Opposite vectors
            sim_opposite = store._cosine_similarity([1, 0], [-1, 0])
            assert abs(sim_opposite - (-1.0)) < 0.001

        run_async_test(run_test())

    def test_empty_vectors(self):
        """Test with empty vectors."""

        async def run_test():
            store = InMemoryVectorStore()

            sim = store._cosine_similarity([], [1, 2, 3])
            assert sim == 0.0

            sim = store._cosine_similarity([1, 2], [3, 4, 5])
            assert sim == 0.0

        run_async_test(run_test())
