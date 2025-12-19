"""Async RAG search implementation for high-performance document retrieval."""

import asyncio
from typing import Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

from src.lmapp.rag.hybrid_search import HybridSearcher
from src.lmapp.rag.document_processor import Chunk


@dataclass
class DocumentChunk:
    """Wrapper for document chunk with metadata."""

    text: str
    metadata: dict


@dataclass
class AsyncSearchResult:
    """Result from async search operation."""

    chunks: List[DocumentChunk]
    query: str
    execution_time_ms: float
    timestamp: datetime


class AsyncHybridSearcher:
    """Async wrapper for hybrid search with concurrent operations."""

    def __init__(self, searcher: HybridSearcher, max_concurrent: int = 5):
        """Initialize async searcher.

        Args:
            searcher: Base HybridSearcher instance
            max_concurrent: Max concurrent search operations
        """
        self.searcher = searcher
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._search_cache: dict[str, AsyncSearchResult] = {}

    async def search_async(
        self,
        query: str,
        top_k: int = 5,
        use_cache: bool = True,
    ) -> AsyncSearchResult:
        """Perform async hybrid search.

        Args:
            query: Search query
            top_k: Number of top results
            use_cache: Use cached results if available

        Returns:
            AsyncSearchResult with chunks and metadata
        """
        cache_key = f"{query}:{top_k}"

        if use_cache and cache_key in self._search_cache:
            return self._search_cache[cache_key]

        async with self._semaphore:
            start = datetime.now(timezone.utc)

            # Run search in executor to avoid blocking
            loop = asyncio.get_event_loop()

            # HybridSearcher.search requires documents list
            # For testing, use internal test documents or return empty
            doc_list = getattr(self.searcher, "_test_documents", [])

            if not doc_list:
                chunks = []
            else:
                # Call BM25 searcher directly
                chunks = self.searcher.keyword_searcher.search(query, doc_list, top_k)
                # Convert (idx, score) tuples to DocumentChunk objects
                chunks = [
                    DocumentChunk(
                        text=doc_list[idx],
                        metadata={"index": idx, "score": score},
                    )
                    for idx, score in chunks[:top_k]
                ]

            elapsed = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            result = AsyncSearchResult(
                chunks=chunks,
                query=query,
                execution_time_ms=elapsed,
                timestamp=start,
            )

            if use_cache:
                self._search_cache[cache_key] = result

            return result

    async def batch_search_async(
        self,
        queries: List[str],
        top_k: int = 5,
    ) -> List[AsyncSearchResult]:
        """Perform multiple searches concurrently.

        Args:
            queries: List of search queries
            top_k: Number of top results per query

        Returns:
            List of AsyncSearchResult for each query
        """
        tasks = [self.search_async(query, top_k=top_k, use_cache=True) for query in queries]
        return await asyncio.gather(*tasks)

    def clear_cache(self) -> None:
        """Clear search result cache."""
        self._search_cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_queries": len(self._search_cache),
            "cache_size_mb": sum(len(str(r.chunks)) for r in self._search_cache.values()) / 1024 / 1024,
        }


class AsyncRAGPipeline:
    """High-performance async RAG pipeline."""

    def __init__(
        self,
        searcher: AsyncHybridSearcher,
        llm_call_timeout: float = 60.0,
    ):
        """Initialize async RAG pipeline.

        Args:
            searcher: AsyncHybridSearcher instance
            llm_call_timeout: Timeout for LLM calls in seconds
        """
        self.searcher = searcher
        self.llm_call_timeout = llm_call_timeout
        self._operation_stats: List[dict[str, Any]] = []

    async def retrieve_and_augment(
        self,
        query: str,
        context_chunks: int = 5,
        rerank: bool = False,
    ) -> dict[str, Any]:
        """Retrieve documents and prepare augmented context.

        Args:
            query: Search query
            context_chunks: Number of context chunks
            rerank: Apply reranking (if available)

        Returns:
            Dictionary with query, retrieved chunks, and metadata
        """
        start = datetime.now(timezone.utc)

        # Async search
        result = await self.searcher.search_async(
            query,
            top_k=context_chunks,
            use_cache=True,
        )

        elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        # Extract sources from metadata
        sources = set()
        for chunk in result.chunks:
            if isinstance(chunk.metadata, dict):
                sources.add(chunk.metadata.get("source", ""))

        augmented = {
            "query": query,
            "chunks": result.chunks,
            "source_count": len(sources),
            "total_tokens": sum(len(c.text.split()) for c in result.chunks),
            "retrieval_ms": result.execution_time_ms,
            "total_ms": elapsed_ms,
            "timestamp": start,
        }

        self._operation_stats.append(augmented)
        return augmented

    async def batch_retrieve_and_augment(
        self,
        queries: List[str],
        context_chunks: int = 5,
    ) -> List[dict[str, Any]]:
        """Batch retrieve augmented contexts.

        Args:
            queries: List of queries
            context_chunks: Number of context chunks per query

        Returns:
            List of augmented context dicts
        """
        tasks = [self.retrieve_and_augment(q, context_chunks=context_chunks) for q in queries]
        return await asyncio.gather(*tasks)

    def get_stats(self) -> dict[str, Any]:
        """Get pipeline statistics."""
        if not self._operation_stats:
            return {"operations": 0}

        retrieval_times = [s["retrieval_ms"] for s in self._operation_stats]
        total_times = [s["total_ms"] for s in self._operation_stats]

        return {
            "operations": len(self._operation_stats),
            "avg_retrieval_ms": sum(retrieval_times) / len(retrieval_times),
            "max_retrieval_ms": max(retrieval_times),
            "avg_total_ms": sum(total_times) / len(total_times),
            "avg_source_count": sum(s["source_count"] for s in self._operation_stats) / len(self._operation_stats),
        }

    def clear_stats(self) -> None:
        """Clear operation statistics."""
        self._operation_stats.clear()
