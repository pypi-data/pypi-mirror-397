"""Base plugin interface and abstract class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PluginMetadata:
    """Plugin metadata information."""

    name: str
    version: str
    author: str
    description: str
    dependencies: List[str]
    entry_point: str
    min_lmapp_version: str = "0.3.5"
    max_lmapp_version: Optional[str] = None
    tags: Optional[List[str]] = None
    repository: Optional[str] = None
    license: str = "MIT"


class Plugin(ABC):
    """Abstract base class for lmapp plugins."""

    metadata: PluginMetadata

    @abstractmethod
    def initialize(self) -> None:
        """Initialize plugin on load."""
        pass

    @abstractmethod
    def execute(self, command: str, args: Dict[str, Any]) -> Any:
        """Execute plugin command.

        Args:
            command: Command name within plugin
            args: Command arguments

        Returns:
            Command result
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Clean up plugin resources on unload."""
        pass

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self.metadata
