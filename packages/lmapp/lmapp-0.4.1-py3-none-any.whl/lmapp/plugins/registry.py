"""Plugin registry for centralized plugin discovery and management."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
import requests

from .base import PluginMetadata


@dataclass
class PluginEntry:
    """Entry in the plugin registry."""

    name: str
    version: str
    author: str
    description: str
    dependencies: List[str]
    entry_point: str
    repository: str
    license: str
    downloads: int = 0
    rating: float = 0.0
    tags: List[str] = field(default_factory=list)
    published_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PluginRegistry:
    """Centralized plugin registry for discovery and metadata."""

    REGISTRY_URL = "https://api.github.com/repos/lmapp-ai/plugin-registry/contents"

    def __init__(self, local_registry_path: Optional[Path] = None):
        """Initialize plugin registry.

        Args:
            local_registry_path: Optional path to local registry cache
        """
        self.local_registry_path = local_registry_path or Path.home() / ".lmapp" / "registry"
        self.local_registry_path.mkdir(parents=True, exist_ok=True)
        self._registry: Dict[str, PluginEntry] = {}
        self._load_local_registry()

    def _load_local_registry(self) -> None:
        """Load registry from local cache."""
        registry_file = self.local_registry_path / "registry.json"
        if registry_file.exists():
            with open(registry_file) as f:
                data = json.load(f)
                self._registry = {name: PluginEntry(**entry) for name, entry in data.items()}

    async def _save_local_registry(self) -> None:
        """Save registry to local cache."""
        registry_file = self.local_registry_path / "registry.json"
        async with aiofiles.open(registry_file, "w") as f:
            await f.write(json.dumps(
                {name: asdict(entry) for name, entry in self._registry.items()},
                indent=2,
            ))

    def refresh(self) -> None:
        """Refresh registry from remote source."""
        try:
            # TODO: Implement remote registry fetch from GitHub
            # For now, registry is managed locally
            pass
        except requests.RequestException as e:
            print(f"Failed to refresh registry: {e}")

    def search(self, query: str) -> List[PluginEntry]:
        """Search for plugins by name, description, or tags.

        Args:
            query: Search query

        Returns:
            List of matching plugin entries
        """
        query = query.lower()
        matches = []

        for entry in self._registry.values():
            if query in entry.name.lower() or query in entry.description.lower() or any(query in tag.lower() for tag in entry.tags):
                matches.append(entry)

        # Sort by rating and downloads
        return sorted(matches, key=lambda x: (-x.rating, -x.downloads))

    def get(self, name: str) -> Optional[PluginEntry]:
        """Get plugin entry by name.

        Args:
            name: Plugin name

        Returns:
            Plugin entry or None if not found
        """
        return self._registry.get(name)

    def list_all(self) -> List[PluginEntry]:
        """List all plugins in registry.

        Returns:
            List of all plugin entries
        """
        return sorted(self._registry.values(), key=lambda x: -x.rating)

    async def register(self, metadata: PluginMetadata, repository: str) -> None:
        """Register a new plugin in the registry.

        Args:
            metadata: Plugin metadata
            repository: Plugin repository URL
        """
        entry = PluginEntry(
            name=metadata.name,
            version=metadata.version,
            author=metadata.author,
            description=metadata.description,
            dependencies=metadata.dependencies,
            entry_point=metadata.entry_point,
            repository=repository,
            license=metadata.license,
            tags=metadata.tags or [],
        )
        self._registry[metadata.name] = entry
        await self._save_local_registry()

    async def update_stats(self, name: str, downloads: int = 0, rating: float = 0.0) -> None:
        """Update plugin statistics.

        Args:
            name: Plugin name
            downloads: Number of downloads
            rating: Plugin rating (0.0-5.0)
        """
        if name in self._registry:
            if downloads > 0:
                self._registry[name].downloads = downloads
            if rating > 0.0:
                self._registry[name].rating = min(rating, 5.0)
            await self._save_local_registry()
