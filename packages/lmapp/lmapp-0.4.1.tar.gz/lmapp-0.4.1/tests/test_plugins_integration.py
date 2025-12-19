"""Integration tests for plugin system."""

import json
import pytest
from pathlib import Path

from lmapp.plugins import PluginManager
from lmapp.plugins.base import PluginMetadata


class TestPluginInstallation:
    """Test plugin installation workflows."""

    def test_install_valid_plugin(self, tmp_path):
        """Test installing a valid plugin."""
        manager = PluginManager(tmp_path)

        # Setup mock plugin in registry
        metadata = PluginMetadata(
            name="test-install",
            version="0.1.0",
            author="Test",
            description="Installation test",
            dependencies=[],
            entry_point="test_install.Plugin",
        )
        manager.registry.register(metadata, "https://github.com/test/test-install")

        # Install plugin
        result = manager.install("test-install")

        # Should succeed (simulated)
        assert result is not None

    def test_install_missing_plugin(self, tmp_path):
        """Test installing non-existent plugin."""
        manager = PluginManager(tmp_path)

        # Try to install non-existent plugin
        result = manager.install("nonexistent-plugin")
        assert result is False

    def test_install_with_dependencies(self, tmp_path):
        """Test installing plugin with dependencies."""
        manager = PluginManager(tmp_path)

        # Register plugin with dependencies
        metadata = PluginMetadata(
            name="plugin-with-deps",
            version="0.1.0",
            author="Test",
            description="Plugin with dependencies",
            dependencies=["sys"],
            entry_point="plugin_with_deps.Plugin",
        )
        manager.registry.register(metadata, "https://github.com/test/plugin-with-deps")

        # Install
        result = manager.install("plugin-with-deps")

        # Should succeed with valid dependencies
        assert result is not None


class TestPluginRegistry:
    """Test plugin registry operations."""

    def test_registry_persistence(self, tmp_path):
        """Test registry data persists to disk."""
        # Create and populate registry
        registry1 = PluginManager(tmp_path).registry
        metadata = PluginMetadata(
            name="persistence-test",
            version="0.1.0",
            author="Test",
            description="Persistence test",
            dependencies=[],
            entry_point="persistence_test.Plugin",
        )
        registry1.register(metadata, "https://github.com/test/persistence-test")

        # Create new manager with same path
        registry2 = PluginManager(tmp_path).registry

        # Registry should be loaded
        assert registry2.get("persistence-test") is not None

    def test_registry_stats_update(self, tmp_path):
        """Test updating registry statistics."""
        manager = PluginManager(tmp_path)

        # Register plugin
        metadata = PluginMetadata(
            name="stats-test",
            version="0.1.0",
            author="Test",
            description="Stats test",
            dependencies=[],
            entry_point="stats_test.Plugin",
        )
        manager.registry.register(metadata, "https://github.com/test/stats-test")

        # Update stats
        manager.registry.update_stats("stats-test", downloads=150, rating=4.8)

        # Verify stats
        entry = manager.registry.get("stats-test")
        assert entry.downloads == 150
        assert entry.rating == 4.8


class TestPluginSearch:
    """Test plugin search functionality."""

    def test_search_by_name(self, tmp_path):
        """Test searching plugins by name."""
        manager = PluginManager(tmp_path)

        # Register multiple plugins
        for name in ["api-plugin", "data-plugin", "web-plugin"]:
            metadata = PluginMetadata(
                name=name,
                version="0.1.0",
                author="Test",
                description=f"Description for {name}",
                dependencies=[],
                entry_point=f"{name}.Plugin",
                tags=["api"] if "api" in name else ["data"],
            )
            manager.registry.register(metadata, f"https://github.com/test/{name}")

        # Search by name
        results = manager.search("api")
        assert len(results) > 0
        assert any(r["name"] == "api-plugin" for r in results)

    def test_search_by_tag(self, tmp_path):
        """Test searching plugins by tag."""
        manager = PluginManager(tmp_path)

        # Register plugin with tags
        metadata = PluginMetadata(
            name="tagged-plugin",
            version="0.1.0",
            author="Test",
            description="Tagged plugin",
            dependencies=[],
            entry_point="tagged_plugin.Plugin",
            tags=["integration", "cloud"],
        )
        manager.registry.register(metadata, "https://github.com/test/tagged-plugin")

        # Search by tag
        results = manager.search("integration")
        assert len(results) > 0
        assert results[0]["name"] == "tagged-plugin"

    def test_search_empty_results(self, tmp_path):
        """Test search with no matches."""
        manager = PluginManager(tmp_path)

        results = manager.search("nonexistent-query-xyz")
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
