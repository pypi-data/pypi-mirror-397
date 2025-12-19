"""Unit tests for plugin system."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from lmapp.plugins import Plugin, PluginManager, PluginRegistry
from lmapp.plugins.base import PluginMetadata
from lmapp.plugins.manager import DependencyResolver, InstalledPlugin


class TestDependencyResolver:
    """Test dependency resolution."""

    def test_resolve_versioned_dependency(self):
        """Test resolving versioned dependency specifiers."""
        resolver = DependencyResolver()
        deps = resolver.resolve(["requests==2.28.0"])

        assert "requests" in deps
        assert deps["requests"] == "2.28.0"

    def test_resolve_unversioned_dependency(self):
        """Test resolving unversioned dependency."""
        resolver = DependencyResolver()
        deps = resolver.resolve(["sys"])

        assert "sys" in deps

    def test_resolve_multiple_dependencies(self):
        """Test resolving multiple dependencies."""
        resolver = DependencyResolver()
        deps = resolver.resolve(["requests==2.28.0", "click==8.0.0"])

        assert "requests" in deps
        assert "click" in deps
        assert deps["requests"] == "2.28.0"
        assert deps["click"] == "8.0.0"

    def test_validate_installed_dependencies(self):
        """Test validation of installed dependencies."""
        resolver = DependencyResolver()
        resolved = {"sys": "unknown", "os": "unknown"}

        assert resolver.validate(resolved) is True

    def test_validate_missing_dependencies(self):
        """Test validation fails for missing dependencies."""
        resolver = DependencyResolver()
        resolved = {"nonexistent_module_xyz": "1.0.0"}

        assert resolver.validate(resolved) is False


class MockPlugin(Plugin):
    """Mock plugin for testing."""

    def __init__(self):
        self.metadata = PluginMetadata(
            name="test-plugin",
            version="0.1.0",
            author="Test Author",
            description="Test plugin",
            dependencies=[],
            entry_point="mock_plugin.Plugin",
        )
        self.initialized = False
        self.shutdown_called = False

    def initialize(self) -> None:
        self.initialized = True

    def execute(self, command: str, args):
        if command == "test":
            return f"Executed test with args: {args}"
        return None

    def shutdown(self) -> None:
        self.shutdown_called = True


class TestPluginRegistry:
    """Test plugin registry."""

    def test_registry_initialization(self, tmp_path):
        """Test registry initializes correctly."""
        registry = PluginRegistry(tmp_path)
        assert registry.local_registry_path == tmp_path
        assert len(registry.list_all()) == 0

    def test_register_plugin(self, tmp_path):
        """Test registering a new plugin."""
        registry = PluginRegistry(tmp_path)
        metadata = PluginMetadata(
            name="test-plugin",
            version="0.1.0",
            author="Test Author",
            description="Test plugin",
            dependencies=[],
            entry_point="test_plugin.Plugin",
        )

        registry.register(metadata, "https://github.com/test/test-plugin")

        assert registry.get("test-plugin") is not None
        plugin_entry = registry.get("test-plugin")
        assert plugin_entry.name == "test-plugin"
        assert plugin_entry.version == "0.1.0"

    def test_search_plugins(self, tmp_path):
        """Test searching for plugins."""
        registry = PluginRegistry(tmp_path)

        # Register test plugins
        for i in range(3):
            metadata = PluginMetadata(
                name=f"plugin-{i}",
                version="0.1.0",
                author="Test",
                description=f"Test plugin {i}",
                dependencies=[],
                entry_point=f"plugin_{i}.Plugin",
                tags=["test"],
            )
            registry.register(metadata, "https://github.com/test/plugin")

        # Search
        results = registry.search("plugin")
        assert len(results) == 3

        results = registry.search("plugin-1")
        assert len(results) == 1
        assert results[0].name == "plugin-1"

    def test_list_all_plugins(self, tmp_path):
        """Test listing all plugins."""
        registry = PluginRegistry(tmp_path)

        # Register plugins
        for i in range(3):
            metadata = PluginMetadata(
                name=f"plugin-{i}",
                version="0.1.0",
                author="Test",
                description=f"Plugin {i}",
                dependencies=[],
                entry_point=f"plugin_{i}.Plugin",
            )
            registry.register(metadata, "https://github.com/test/plugin")

        plugins = registry.list_all()
        assert len(plugins) == 3

    def test_update_plugin_stats(self, tmp_path):
        """Test updating plugin statistics."""
        registry = PluginRegistry(tmp_path)
        metadata = PluginMetadata(
            name="test-plugin",
            version="0.1.0",
            author="Test",
            description="Test",
            dependencies=[],
            entry_point="test.Plugin",
        )
        registry.register(metadata, "https://github.com/test/test")

        registry.update_stats("test-plugin", downloads=100, rating=4.5)

        plugin = registry.get("test-plugin")
        assert plugin.downloads == 100
        assert plugin.rating == 4.5


class TestPluginManager:
    """Test plugin manager."""

    def test_manager_initialization(self, tmp_path):
        """Test manager initializes correctly."""
        manager = PluginManager(tmp_path)
        assert manager.plugins_path == tmp_path

    def test_search_plugins(self, tmp_path):
        """Test searching for plugins through manager."""
        manager = PluginManager(tmp_path)

        # Add plugin to registry
        metadata = PluginMetadata(
            name="search-test",
            version="0.1.0",
            author="Test",
            description="Search test plugin",
            dependencies=[],
            entry_point="search_test.Plugin",
            tags=["search", "test"],
        )
        manager.registry.register(metadata, "https://github.com/test/search-test")

        # Search
        results = manager.search("search")
        assert len(results) > 0
        assert results[0]["name"] == "search-test"

    def test_list_installed_plugins(self, tmp_path):
        """Test listing installed plugins."""
        manager = PluginManager(tmp_path)

        # Initially empty
        assert len(manager.list_installed()) == 0

    def test_execute_plugin_command(self, tmp_path):
        """Test executing plugin command."""
        manager = PluginManager(tmp_path)

        # Manually add plugin to manager
        mock_plugin = MockPlugin()
        installed = InstalledPlugin(
            name="mock-plugin",
            version="0.1.0",
            path=tmp_path / "mock-plugin",
            instance=mock_plugin,
        )
        manager.installed_plugins["mock-plugin"] = installed

        # Execute command
        result = manager.execute("mock-plugin", "test", {"key": "value"})
        assert "Executed test" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
