"""
Plugin system for lmapp.

Provides plugin registry, discovery, installation, and management.
"""

__all__ = [
    "PluginRegistry",
    "PluginManager",
    "Plugin",
]

from .registry import PluginRegistry
from .manager import PluginManager
from .base import Plugin
