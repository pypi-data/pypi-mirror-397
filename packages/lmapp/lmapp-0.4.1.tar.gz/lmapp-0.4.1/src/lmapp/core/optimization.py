"""Lazy loading and startup optimization for lmapp."""

import importlib
import sys
from typing import Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ImportMetrics:
    """Metrics for lazy import operations."""

    module_name: str
    import_time_ms: float
    timestamp: datetime


class LazyModule:
    """Lazy-loaded module wrapper."""

    def __init__(self, module_name: str, import_fn: Optional[Callable] = None):
        """Initialize lazy module.

        Args:
            module_name: Full module name (e.g., 'src.lmapp.rag.embedding')
            import_fn: Optional function to call on first import
        """
        self.module_name = module_name
        self.import_fn = import_fn
        self._module: Optional[Any] = None
        self._imported = False

    def __getattr__(self, name: str) -> Any:
        """Lazy load module on attribute access."""
        if not self._imported:
            start = datetime.now(timezone.utc)

            try:
                self._module = importlib.import_module(self.module_name)
                if self.import_fn:
                    self.import_fn(self._module)
                self._imported = True

                elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            except ImportError as e:
                raise ImportError(f"Failed to load {self.module_name}: {e}")

        return getattr(self._module, name)

    def is_loaded(self) -> bool:
        """Check if module is loaded."""
        return self._imported


class StartupOptimizer:
    """Manages startup time optimization through lazy loading."""

    def __init__(self):
        """Initialize startup optimizer."""
        self._lazy_modules: dict[str, LazyModule] = {}
        self._import_metrics: list[ImportMetrics] = []
        self._critical_modules: list[str] = [
            "src.lmapp.cli",
            "src.lmapp.core",
            "src.lmapp.backend",
        ]
        self._optional_modules: list[str] = [
            "src.lmapp.rag.embedding",
            "src.lmapp.rag.hybrid_search",
            "src.lmapp.plugins.registry",
            "src.lmapp.workflows.engine",
        ]

    def register_lazy_module(
        self,
        module_name: str,
        import_fn: Optional[Callable] = None,
    ) -> LazyModule:
        """Register module for lazy loading.

        Args:
            module_name: Full module name
            import_fn: Optional initialization function

        Returns:
            LazyModule wrapper
        """
        lazy = LazyModule(module_name, import_fn)
        self._lazy_modules[module_name] = lazy
        return lazy

    def load_critical_modules(self) -> dict[str, float]:
        """Load critical modules synchronously.

        Returns:
            Dict mapping module names to load times in ms
        """
        load_times = {}

        for module_name in self._critical_modules:
            start = datetime.now(timezone.utc)

            try:
                importlib.import_module(module_name)
                elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
                load_times[module_name] = elapsed_ms

                self._import_metrics.append(
                    ImportMetrics(
                        module_name=module_name,
                        import_time_ms=elapsed_ms,
                        timestamp=start,
                    )
                )
            except ImportError:
                load_times[module_name] = 0.0  # Skip if not available

        return load_times

    def precompile_patterns(self) -> dict[str, int]:
        """Precompile regex patterns for faster matching.

        Returns:
            Dict mapping pattern names to compiled count
        """
        import re

        patterns = {
            "code_identifier": r"[a-zA-Z_][a-zA-Z0-9_]*",
            "import_statement": r"^(?:from|import)\s+[\w.]+",
            "function_def": r"^(?:async\s+)?def\s+\w+\(",
            "class_def": r"^class\s+\w+",
            "docstring": r'""".*?"""',
        }

        compiled = {}
        for name, pattern in patterns.items():
            try:
                re.compile(pattern)
                compiled[name] = 1
            except re.error:
                compiled[name] = 0

        return compiled

    def get_module_load_metrics(self) -> dict[str, Any]:
        """Get module loading metrics.

        Returns:
            Dict with load statistics
        """
        if not self._import_metrics:
            return {"total_metrics": 0}

        times = [m.import_time_ms for m in self._import_metrics]
        return {
            "total_modules": len(self._import_metrics),
            "total_time_ms": sum(times),
            "avg_time_ms": sum(times) / len(times),
            "max_time_ms": max(times),
            "lazy_modules_registered": len(self._lazy_modules),
        }

    def optimize_startup(self) -> dict[str, Any]:
        """Run full startup optimization.

        Returns:
            Dict with optimization results
        """
        start = datetime.now(timezone.utc)

        # Load critical modules
        load_times = self.load_critical_modules()

        # Precompile patterns
        patterns = self.precompile_patterns()

        total_time = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        return {
            "startup_time_ms": total_time,
            "critical_modules_loaded": sum(1 for t in load_times.values() if t > 0),
            "patterns_compiled": sum(patterns.values()),
            "lazy_modules_available": len(self._optional_modules),
            "module_load_times": load_times,
        }


class ResourcePool:
    """Manages shared resource pooling for connection reuse."""

    def __init__(self, max_size: int = 10):
        """Initialize resource pool.

        Args:
            max_size: Maximum pool size
        """
        self.max_size = max_size
        self._available: list[Any] = []
        self._in_use: set[int] = set()
        self._factories: dict[str, Callable] = {}

    def register_factory(self, resource_type: str, factory: Callable) -> None:
        """Register resource factory.

        Args:
            resource_type: Type identifier (e.g., 'db_connection')
            factory: Factory function to create resources
        """
        self._factories[resource_type] = factory

    def acquire(self, resource_type: str) -> Any:
        """Acquire resource from pool.

        Args:
            resource_type: Type of resource

        Returns:
            Resource instance
        """
        if self._available and len(self._available) > 0:
            resource = self._available.pop()
        else:
            factory = self._factories.get(resource_type)
            if not factory:
                raise ValueError(f"No factory for {resource_type}")
            resource = factory()

        self._in_use.add(id(resource))
        return resource

    def release(self, resource: Any) -> None:
        """Release resource back to pool.

        Args:
            resource: Resource to release
        """
        self._in_use.discard(id(resource))
        if len(self._available) < self.max_size:
            self._available.append(resource)

    def get_stats(self) -> dict[str, Any]:
        """Get pool statistics."""
        return {
            "available": len(self._available),
            "in_use": len(self._in_use),
            "max_size": self.max_size,
            "utilization": len(self._in_use) / self.max_size if self.max_size > 0 else 0,
        }


class MemoryOptimizer:
    """Optimizes memory usage through object pooling and deduplication."""

    def __init__(self):
        """Initialize memory optimizer."""
        self._string_cache: dict[str, str] = {}
        self._object_pools: dict[str, list[Any]] = {}

    def intern_string(self, string: str) -> str:
        """Intern string to reduce memory duplication.

        Args:
            string: String to intern

        Returns:
            Interned string reference
        """
        if string not in self._string_cache:
            self._string_cache[string] = string
        return self._string_cache[string]

    def register_object_pool(self, object_type: str, max_size: int) -> None:
        """Register object pool for reuse.

        Args:
            object_type: Type identifier
            max_size: Maximum pool size
        """
        self._object_pools[object_type] = []

    def get_stats(self) -> dict[str, Any]:
        """Get memory optimization statistics."""
        cached_size = sum(len(s) for s in self._string_cache.values())

        return {
            "interned_strings": len(self._string_cache),
            "cached_string_size_bytes": cached_size,
            "object_pools": len(self._object_pools),
            "pool_sizes": {t: len(objs) for t, objs in self._object_pools.items()},
        }
