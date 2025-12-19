"""Async caching layer for RAG operations."""

import asyncio
import json
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Generic, TypeVar
from pathlib import Path

T = TypeVar("T")


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: str
    timestamp: datetime
    ttl_seconds: Optional[int]
    hits: int = 0

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl_seconds is None:
            return False
        return (datetime.now(timezone.utc) - self.timestamp).total_seconds() > self.ttl_seconds


class CacheBackend(ABC):
    """Abstract cache backend."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear entire cache."""
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache backend."""

    def __init__(self, max_size: int = 1000):
        """Initialize memory cache.

        Args:
            max_size: Maximum entries to store
        """
        self.max_size = max_size
        self.store: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        async with self._lock:
            entry = self.store.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                del self.store[key]
                return None

            entry.hits += 1
            return entry.value

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Set value in cache."""
        async with self._lock:
            if len(self.store) >= self.max_size:
                # Remove least recently used entry
                least_used = min(
                    self.store.items(),
                    key=lambda x: x[1].hits,
                )[0]
                del self.store[least_used]

            self.store[key] = CacheEntry(
                key=key,
                value=value,
                timestamp=datetime.now(timezone.utc),
                ttl_seconds=ttl_seconds,
            )

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        async with self._lock:
            self.store.pop(key, None)

    async def clear(self) -> None:
        """Clear entire cache."""
        async with self._lock:
            self.store.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            total_hits = sum(e.hits for e in self.store.values())
            return {
                "type": "memory",
                "entries": len(self.store),
                "max_size": self.max_size,
                "total_hits": total_hits,
                "avg_ttl": sum(e.ttl_seconds or 0 for e in self.store.values()) / max(len(self.store), 1),
            }


class SQLiteCache(CacheBackend):
    """SQLite-backed persistent cache."""

    def __init__(self, db_path: str = ".cache/lmapp_cache.db"):
        """Initialize SQLite cache.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                timestamp REAL NOT NULL,
                ttl_seconds INTEGER,
                hits INTEGER DEFAULT 0
            )
        """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON cache(timestamp)")
        conn.commit()
        conn.close()

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        async with self._lock:
            loop = asyncio.get_event_loop()
            executor = None  # Use default executor
            return await loop.run_in_executor(executor, self._get_sync, key)

    def _get_sync(self, key: str) -> Optional[str]:
        """Synchronous get operation."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT value, timestamp, ttl_seconds FROM cache WHERE key = ?",
            (key,),
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        value, timestamp, ttl_seconds = row
        if ttl_seconds is not None:
            if (datetime.now(timezone.utc).timestamp() - timestamp) > ttl_seconds:
                asyncio.create_task(self.delete(key))
                return None

        return value

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Set value in cache."""
        async with self._lock:
            loop = asyncio.get_event_loop()
            executor = None  # Use default executor
            await loop.run_in_executor(
                executor,
                self._set_sync,
                key,
                value,
                ttl_seconds,
            )

    def _set_sync(
        self,
        key: str,
        value: str,
        ttl_seconds: Optional[int],
    ) -> None:
        """Synchronous set operation."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO cache
            (key, value, timestamp, ttl_seconds, hits)
            VALUES (?, ?, ?, ?, COALESCE((
                SELECT hits FROM cache WHERE key = ?
            ), 0))
            """,
            (key, value, datetime.now(timezone.utc).timestamp(), ttl_seconds, key),
        )
        conn.commit()
        conn.close()

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        async with self._lock:
            loop = asyncio.get_event_loop()
            executor = None  # Use default executor
            await loop.run_in_executor(executor, self._delete_sync, key)

    def _delete_sync(self, key: str) -> None:
        """Synchronous delete operation."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()
        conn.close()

    async def clear(self) -> None:
        """Clear entire cache."""
        async with self._lock:
            loop = asyncio.get_event_loop()
            executor = None  # Use default executor
            await loop.run_in_executor(executor, self._clear_sync)

    def _clear_sync(self) -> None:
        """Synchronous clear operation."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache")
        conn.commit()
        conn.close()

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            loop = asyncio.get_event_loop()
            executor = None  # Use default executor
            return await loop.run_in_executor(executor, self._get_stats_sync)

    def _get_stats_sync(self) -> dict[str, Any]:
        """Synchronous stats operation."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*), SUM(hits) FROM cache")
        count, total_hits = cursor.fetchone()

        cursor.execute("SELECT SUM(length(value)) FROM cache")
        size_bytes = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "type": "sqlite",
            "entries": count or 0,
            "db_path": str(self.db_path),
            "size_bytes": size_bytes,
            "total_hits": total_hits or 0,
        }


class AsyncCache(Generic[T]):
    """Async cache wrapper with automatic serialization."""

    def __init__(self, backend: CacheBackend):
        """Initialize async cache.

        Args:
            backend: Cache backend (Memory or SQLite)
        """
        self.backend = backend

    async def get(self, key: str) -> Optional[T]:
        """Get value from cache."""
        value_str = await self.backend.get(key)
        if value_str is None:
            return None
        try:
            return json.loads(value_str)
        except json.JSONDecodeError:
            return None

    async def set(
        self,
        key: str,
        value: T,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Set value in cache."""
        value_str = json.dumps(value, default=str)
        await self.backend.set(key, value_str, ttl_seconds)

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        await self.backend.delete(key)

    async def clear(self) -> None:
        """Clear entire cache."""
        await self.backend.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return await self.backend.get_stats()
