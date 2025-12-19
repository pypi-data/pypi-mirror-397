"""Async I/O optimization for LLM operations."""

import asyncio
from typing import Any, Optional, Callable, Awaitable
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class LLMCallMetrics:
    """Metrics for LLM calls."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_ms: float
    cached: bool


class AsyncLLMClient:
    """Async wrapper for LLM operations."""

    def __init__(
        self,
        call_fn: Callable[..., Awaitable[str]],
        max_concurrent: int = 3,
        timeout_seconds: float = 60.0,
    ):
        """Initialize async LLM client.

        Args:
            call_fn: Async function to call LLM
            max_concurrent: Max concurrent LLM calls
            timeout_seconds: Timeout per call
        """
        self.call_fn = call_fn
        self.max_concurrent = max_concurrent
        self.timeout_seconds = timeout_seconds
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._metrics: list[LLMCallMetrics] = []

    async def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """Generate response from LLM asynchronously.

        Args:
            prompt: Input prompt
            **kwargs: Additional LLM parameters

        Returns:
            Generated response
        """
        async with self._semaphore:
            start = datetime.now(timezone.utc)

            try:
                response = await asyncio.wait_for(
                    self.call_fn(prompt, **kwargs),
                    timeout=self.timeout_seconds,
                )
            except asyncio.TimeoutError:
                raise RuntimeError(f"LLM call timed out after {self.timeout_seconds}s")

            elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            # Estimate tokens (rough approximation)
            prompt_tokens = len(prompt.split()) // 4
            completion_tokens = len(response.split()) // 4

            metrics = LLMCallMetrics(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                duration_ms=elapsed_ms,
                cached=False,
            )
            self._metrics.append(metrics)

            return response

    async def batch_generate(
        self,
        prompts: list[str],
        **kwargs: Any,
    ) -> list[str]:
        """Generate responses for multiple prompts concurrently.

        Args:
            prompts: List of prompts
            **kwargs: Additional LLM parameters

        Returns:
            List of responses
        """
        tasks = [self.generate(p, **kwargs) for p in prompts]
        return await asyncio.gather(*tasks)

    def get_metrics(self) -> dict[str, Any]:
        """Get LLM call metrics."""
        if not self._metrics:
            return {"calls": 0}

        durations = [m.duration_ms for m in self._metrics]
        tokens = [m.total_tokens for m in self._metrics]

        return {
            "total_calls": len(self._metrics),
            "avg_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "total_tokens": sum(tokens),
            "avg_tokens_per_call": sum(tokens) / len(tokens),
        }

    def clear_metrics(self) -> None:
        """Clear metrics."""
        self._metrics.clear()


class BatchProcessingPool:
    """Async batch processing with concurrency control."""

    def __init__(self, worker_count: int = 4, batch_size: int = 10):
        """Initialize batch pool.

        Args:
            worker_count: Number of workers
            batch_size: Items per batch
        """
        self.worker_count = worker_count
        self.batch_size = batch_size
        self._queue: asyncio.Queue = asyncio.Queue()
        self._results: dict[int, Any] = {}
        self._counter = 0

    async def submit(self, item: Any) -> int:
        """Submit item for processing.

        Args:
            item: Item to process

        Returns:
            Job ID
        """
        job_id = self._counter
        self._counter += 1
        await self._queue.put((job_id, item))
        return job_id

    async def process_queue(
        self,
        processor: Callable[[Any], Awaitable[Any]],
        timeout_seconds: float = 300.0,
    ) -> dict[int, Any]:
        """Process all queued items.

        Args:
            processor: Async function to process items
            timeout_seconds: Overall timeout

        Returns:
            Dict mapping job IDs to results
        """
        workers = [asyncio.create_task(self._worker(processor, timeout_seconds)) for _ in range(self.worker_count)]

        try:
            await asyncio.wait_for(
                asyncio.gather(*workers),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            for w in workers:
                w.cancel()
            raise

        return self._results

    async def _worker(
        self,
        processor: Callable[[Any], Awaitable[Any]],
        timeout_seconds: float,
    ) -> None:
        """Worker coroutine."""
        start = datetime.now(timezone.utc)

        while True:
            try:
                job_id, item = self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            elapsed = (datetime.now(timezone.utc) - start).total_seconds()
            if elapsed > timeout_seconds:
                break

            try:
                result = await processor(item)
                self._results[job_id] = result
            except Exception as e:
                self._results[job_id] = {"error": str(e)}
            finally:
                self._queue.task_done()
