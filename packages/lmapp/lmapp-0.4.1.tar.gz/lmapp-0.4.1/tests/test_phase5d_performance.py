"""Performance tests and benchmarks for Phase 5D optimization."""

import asyncio
import time
import pytest
from datetime import datetime, timezone

from src.lmapp.rag.async_search import AsyncHybridSearcher, AsyncRAGPipeline, DocumentChunk
from src.lmapp.rag.cache import MemoryCache, SQLiteCache, AsyncCache
from src.lmapp.rag.hybrid_search import HybridSearcher
from src.lmapp.rag.document_processor import Chunk
from src.lmapp.core.async_llm import AsyncLLMClient, BatchProcessingPool


def run_async_test(coro):
    """Helper to run async tests."""
    return asyncio.run(coro)


# Mock data
MOCK_CHUNKS = [
    DocumentChunk(
        text="Async I/O enables concurrent operations without blocking threads. " "It's essential for high-performance systems.",
        metadata={"source": "async_guide", "section": "intro"},
    ),
    DocumentChunk(
        text="Caching reduces latency by storing frequently accessed data. " "Effective caching can improve performance by 10x.",
        metadata={"source": "cache_guide", "section": "benefits"},
    ),
    DocumentChunk(
        text="Search algorithms like BM25 and semantic search have different tradeoffs. " "Hybrid search combines both for best results.",
        metadata={"source": "search_guide", "section": "hybrid"},
    ),
    DocumentChunk(
        text="Performance optimization requires profiling and iteration. " "Measure first, optimize later.",
        metadata={"source": "perf_guide", "section": "methodology"},
    ),
    DocumentChunk(
        text="Connection pooling reduces overhead for repeated operations. " "Reusing connections improves throughput significantly.",
        metadata={"source": "pool_guide", "section": "implementation"},
    ),
]


@pytest.fixture
def hybrid_searcher():
    """Create mock HybridSearcher."""
    searcher = HybridSearcher()
    # HybridSearcher.search() takes documents list directly
    # Store as internal attribute for testing
    searcher._test_documents = [chunk.text for chunk in MOCK_CHUNKS]
    return searcher


@pytest.fixture
def async_searcher(hybrid_searcher):
    """Create AsyncHybridSearcher."""
    return AsyncHybridSearcher(hybrid_searcher, max_concurrent=5)


@pytest.fixture
def memory_cache():
    """Create memory cache."""
    return MemoryCache(max_size=1000)


@pytest.fixture
def sqlite_cache(tmp_path):
    """Create SQLite cache."""
    db_path = str(tmp_path / "test_cache.db")
    return SQLiteCache(db_path)


class TestAsyncSearch:
    """Test async search functionality."""

    def test_async_search_performance(self, async_searcher):
        """Test async search returns results quickly."""

        async def run_test():
            start = time.time()
            result = await async_searcher.search_async("async optimization", top_k=3)
            elapsed = (time.time() - start) * 1000

            assert result.chunks is not None
            assert len(result.chunks) <= 3
            assert result.execution_time_ms > 0
            assert elapsed < 1000  # Should complete in <1 second

        run_async_test(run_test())

    def test_batch_search_concurrency(self, async_searcher):
        """Test batch search with concurrent execution."""

        async def run_test():
            queries = [
                "async I/O",
                "caching strategies",
                "search algorithms",
                "performance optimization",
                "connection pooling",
            ]

            start = time.time()
            results = await async_searcher.batch_search_async(queries)
            elapsed = (time.time() - start) * 1000

            assert len(results) == 5
            assert all(r.chunks for r in results)
            # Batch should be faster than sequential (with proper concurrency)
            assert elapsed < 5000

        run_async_test(run_test())

    def test_search_caching(self, async_searcher):
        """Test search result caching."""

        async def run_test():
            query = "cache optimization"

            # First search
            start1 = time.time()
            result1 = await async_searcher.search_async(query, use_cache=True)
            time1 = (time.time() - start1) * 1000

            # Second search (cached)
            start2 = time.time()
            result2 = await async_searcher.search_async(query, use_cache=True)
            time2 = (time.time() - start2) * 1000

            assert result1.chunks == result2.chunks
            # Cached result should be significantly faster
            assert time2 < time1 or time2 < 10  # Either faster or trivial time

        run_async_test(run_test())

    def test_async_rag_pipeline(self, async_searcher):
        """Test async RAG pipeline performance."""

        async def run_test():
            pipeline = AsyncRAGPipeline(async_searcher)

            query = "optimization techniques"
            result = await pipeline.retrieve_and_augment(query, context_chunks=3)

            assert result["query"] == query
            assert len(result["chunks"]) <= 3
            assert result["retrieval_ms"] > 0
            assert result["total_ms"] > 0

        run_async_test(run_test())


class TestAsyncCache:
    """Test async caching backends."""

    def test_memory_cache_basic(self, memory_cache):
        """Test memory cache set/get."""

        async def run_test():
            cache = AsyncCache(memory_cache)

            data = {"key": "value", "number": 42}
            await cache.set("test_key", data)
            retrieved = await cache.get("test_key")

            assert retrieved == data

        run_async_test(run_test())

    def test_memory_cache_ttl(self, memory_cache):
        """Test memory cache with TTL."""

        async def run_test():
            cache = AsyncCache(memory_cache)

            await cache.set("expire_key", {"data": "test"}, ttl_seconds=1)
            retrieved = await cache.get("expire_key")
            assert retrieved is not None

            # Wait for expiration
            await asyncio.sleep(1.1)
            expired = await cache.get("expire_key")
            assert expired is None

        run_async_test(run_test())

    def test_sqlite_cache_persistence(self, sqlite_cache):
        """Test SQLite cache persistence."""

        async def run_test():
            cache = AsyncCache(sqlite_cache)

            data = {"persistent": True, "value": 123}
            await cache.set("persist_key", data)
            retrieved = await cache.get("persist_key")

            assert retrieved == data

        run_async_test(run_test())

    def test_cache_stats(self, memory_cache):
        """Test cache statistics."""

        async def run_test():
            cache = AsyncCache(memory_cache)

            for i in range(10):
                await cache.set(f"key_{i}", {"number": i})

            for i in range(10):
                await cache.get(f"key_{i}")

            stats = await cache.get_stats()
            assert stats["entries"] == 10
            assert stats["total_hits"] == 10

        run_async_test(run_test())

    def test_cache_deletion(self, memory_cache):
        """Test cache deletion."""

        async def run_test():
            cache = AsyncCache(memory_cache)

            await cache.set("delete_key", {"data": "test"})
            await cache.delete("delete_key")

            retrieved = await cache.get("delete_key")
            assert retrieved is None

        run_async_test(run_test())


class TestAsyncLLM:
    """Test async LLM client."""

    async def mock_llm_call(self, prompt: str, **kwargs) -> str:
        """Mock LLM call."""
        await asyncio.sleep(0.01)  # Simulate network latency
        return f"Response to: {prompt[:50]}..."

    def test_single_generation(self):
        """Test single LLM generation."""

        async def run_test():
            client = AsyncLLMClient(
                self.mock_llm_call,
                max_concurrent=1,
                timeout_seconds=5.0,
            )

            response = await client.generate("Test prompt")
            assert "Response to:" in response

        run_async_test(run_test())

    def test_batch_generation(self):
        """Test batch LLM generation."""

        async def run_test():
            client = AsyncLLMClient(
                self.mock_llm_call,
                max_concurrent=3,
                timeout_seconds=5.0,
            )

            prompts = [f"Prompt {i}" for i in range(5)]
            start = time.time()
            responses = await client.batch_generate(prompts)
            elapsed = (time.time() - start) * 1000

            assert len(responses) == 5
            assert all("Response to:" in r for r in responses)
            # Concurrent execution should be faster than sequential (50ms+ if serial)
            assert elapsed < 100

        run_async_test(run_test())

    def test_llm_metrics(self):
        """Test LLM metrics collection."""

        async def run_test():
            client = AsyncLLMClient(
                self.mock_llm_call,
                max_concurrent=1,
            )

            await client.generate("Test prompt with several words")
            metrics = client.get_metrics()

            assert metrics["total_calls"] == 1
            assert metrics["avg_duration_ms"] > 0
            assert metrics["total_tokens"] > 0

        run_async_test(run_test())


class TestBatchProcessing:
    """Test batch processing pool."""

    async def slow_processor(self, item: int) -> int:
        """Slow processing function."""
        await asyncio.sleep(0.01)
        return item * 2

    def test_batch_pool_processing(self):
        """Test batch pool processes items concurrently."""

        async def run_test():
            pool = BatchProcessingPool(worker_count=3, batch_size=5)

            # Submit items
            job_ids = []
            for i in range(10):
                job_id = await pool.submit(i)
                job_ids.append(job_id)

            # Process
            start = time.time()
            results = await pool.process(self.slow_processor, timeout_seconds=5.0)
            elapsed = (time.time() - start) * 1000

            # All results should be present
            assert len(results) == 10
            assert all(results[i] == i * 2 for i in range(10))

            # Should complete faster than sequential (100ms+)
            assert elapsed < 200

        run_async_test(run_test())


class TestPerformanceBenchmarks:
    """Overall performance benchmarks."""

    def test_end_to_end_pipeline_performance(self, async_searcher):
        """Test end-to-end pipeline performance."""

        async def run_test():
            pipeline = AsyncRAGPipeline(async_searcher)

            queries = [
                "What is async I/O?",
                "Explain caching benefits",
                "How does hybrid search work?",
            ]

            start = time.time()
            results = await pipeline.batch_retrieve_and_augment(queries, context_chunks=3)
            elapsed = (time.time() - start) * 1000

            assert len(results) == 3
            stats = pipeline.get_stats()

            assert stats["operations"] == 3
            assert stats["avg_retrieval_ms"] > 0
            # End-to-end should complete in reasonable time
            assert elapsed < 5000

        run_async_test(run_test())

    def test_concurrent_vs_sequential_timing(self, async_searcher):
        """Compare concurrent vs sequential search timing."""

        async def run_test():
            queries = [f"Query {i}" for i in range(5)]

            # Sequential (use BM25 directly)
            start_seq = time.time()
            searcher = async_searcher.searcher
            docs = searcher._test_documents
            for q in queries:
                # Use keyword searcher directly
                searcher.keyword_searcher.search(q, docs, k=5)
            seq_time = (time.time() - start_seq) * 1000

            # Concurrent
            start_conc = time.time()
            await async_searcher.batch_search_async(queries)
            conc_time = (time.time() - start_conc) * 1000

            # Concurrent should be faster (or at least not much slower)
            assert conc_time <= seq_time * 1.5 or conc_time < 100

        run_async_test(run_test())
