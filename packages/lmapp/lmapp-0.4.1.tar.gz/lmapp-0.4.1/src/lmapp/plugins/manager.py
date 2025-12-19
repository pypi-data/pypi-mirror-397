"""Plugin manager for installation, loading, and lifecycle management."""

import importlib
import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Plugin, PluginMetadata
from .registry import PluginRegistry


@dataclass
class InstalledPlugin:
    """Information about an installed plugin."""

    name: str
    version: str
    path: Path
    instance: Optional[Plugin] = None


class DependencyResolver:
    """Resolves and validates plugin dependencies."""

    def __init__(self):
        """Initialize dependency resolver."""
        self.resolved: Dict[str, str] = {}

    def resolve(self, dependencies: List[str]) -> Dict[str, str]:
        """Resolve dependencies to versions.

        Args:
            dependencies: List of dependency specifiers (name or name==version)

        Returns:
            Dictionary of resolved dependencies and versions
        """
        resolved = {}

        for dep in dependencies:
            if "==" in dep:
                name, version = dep.split("==", 1)
                resolved[name.strip()] = version.strip()
            else:
                # For unversioned, try to detect installed version
                try:
                    mod = importlib.import_module(dep)
                    resolved[dep] = getattr(mod, "__version__", "unknown")
                except ImportError:
                    resolved[dep] = "not-installed"

        self.resolved = resolved
        return resolved

    def validate(self, dependencies: Dict[str, str]) -> bool:
        """Validate that all dependencies are installed.

        Args:
            dependencies: Dictionary of dependencies and required versions

        Returns:
            True if all dependencies valid
        """
        for name, required_version in dependencies.items():
            try:
                mod = importlib.import_module(name)
                installed_version = getattr(mod, "__version__", "unknown")

                if required_version != "unknown" and installed_version != required_version:
                    print(f"Version mismatch for {name}: " f"required {required_version}, have {installed_version}")
                    return False
            except ImportError:
                print(f"Required dependency not installed: {name}")
                return False

        return True


class PluginManager:
    """Manages plugin lifecycle: discovery, installation, loading, execution."""

    def __init__(self, plugins_path: Optional[Path] = None):
        """Initialize plugin manager.

        Args:
            plugins_path: Path to installed plugins directory
        """
        self.plugins_path = plugins_path or Path.home() / ".lmapp" / "plugins"
        self.plugins_path.mkdir(parents=True, exist_ok=True)

        self.registry = PluginRegistry()
        self.dependency_resolver = DependencyResolver()
        self.installed_plugins: Dict[str, InstalledPlugin] = {}

        self._discover_installed()

    def _discover_installed(self) -> None:
        """Discover and load installed plugins."""
        for plugin_dir in self.plugins_path.iterdir():
            if not plugin_dir.is_dir():
                continue

            # Look for plugin.py or __init__.py
            plugin_file = plugin_dir / "plugin.py"
            if not plugin_file.exists():
                plugin_file = plugin_dir / "__init__.py"

            if plugin_file.exists():
                try:
                    self._load_plugin(plugin_dir.name, plugin_dir)
                except Exception as e:
                    print(f"Failed to load plugin {plugin_dir.name}: {e}")

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for plugins in registry.

        Args:
            query: Search query

        Returns:
            List of plugin information
        """
        results = self.registry.search(query)
        return [
            {
                "name": entry.name,
                "version": entry.version,
                "author": entry.author,
                "description": entry.description,
                "rating": entry.rating,
                "downloads": entry.downloads,
                "tags": entry.tags,
            }
            for entry in results
        ]

    def install(self, plugin_name: str, version: Optional[str] = None) -> bool:
        """Install a plugin from registry.

        Args:
            plugin_name: Plugin name
            version: Optional specific version

        Returns:
            True if installation successful
        """
        entry = self.registry.get(plugin_name)
        if not entry:
            print(f"Plugin not found in registry: {plugin_name}")
            return False

        # Resolve and validate dependencies
        deps = self.dependency_resolver.resolve(entry.dependencies)
        if not self.dependency_resolver.validate(deps):
            print(f"Failed to resolve dependencies for {plugin_name}")
            return False

        # Clone/download plugin
        plugin_path = self.plugins_path / plugin_name
        try:
            # TODO: Implement actual download/clone from repository
            print(f"Installing {plugin_name} from {entry.repository}")

            # For now, simulate installation
            plugin_path.mkdir(parents=True, exist_ok=True)

            # Load the plugin
            if self._load_plugin(plugin_name, plugin_path):
                print(f"Successfully installed {plugin_name}")
                return True
        except Exception as e:
            print(f"Installation failed: {e}")
            # Cleanup on failure
            if plugin_path.exists():
                import shutil

                shutil.rmtree(plugin_path)
            return False

        return False

    def _load_plugin(self, name: str, path: Path) -> bool:
        """Load a plugin from disk.

        Args:
            name: Plugin name
            path: Path to plugin directory

        Returns:
            True if plugin loaded successfully
        """
        try:
            spec = importlib.util.spec_from_file_location(name, path / "plugin.py" if (path / "plugin.py").exists() else path / "__init__.py")
            if not spec or not spec.loader:
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get plugin class (should be named Plugin or derive from base.Plugin)
            if hasattr(module, "Plugin"):
                plugin_class = module.Plugin
                instance = plugin_class()
                instance.initialize()

                installed = InstalledPlugin(
                    name=name,
                    version=instance.metadata.version,
                    path=path,
                    instance=instance,
                )
                self.installed_plugins[name] = installed
                return True
        except Exception as e:
            print(f"Failed to load plugin {name}: {e}")
            return False

        return False

    def uninstall(self, plugin_name: str) -> bool:
        """Uninstall a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            True if uninstallation successful
        """
        if plugin_name not in self.installed_plugins:
            print(f"Plugin not installed: {plugin_name}")
            return False

        try:
            plugin = self.installed_plugins[plugin_name]

            # Shutdown plugin
            if plugin.instance:
                plugin.instance.shutdown()

            # Remove files
            import shutil

            if plugin.path.exists():
                shutil.rmtree(plugin.path)

            del self.installed_plugins[plugin_name]
            print(f"Successfully uninstalled {plugin_name}")
            return True
        except Exception as e:
            print(f"Uninstallation failed: {e}")
            return False

    def list_installed(self) -> List[Dict[str, Any]]:
        """List all installed plugins.

        Returns:
            List of installed plugin information
        """
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "path": str(plugin.path),
            }
            for plugin in self.installed_plugins.values()
        ]

    def execute(self, plugin_name: str, command: str, args: Dict[str, Any]) -> Any:
        """Execute a command in a plugin.

        Args:
            plugin_name: Plugin name
            command: Command name
            args: Command arguments

        Returns:
            Command result
        """
        if plugin_name not in self.installed_plugins:
            raise ValueError(f"Plugin not installed: {plugin_name}")

        plugin = self.installed_plugins[plugin_name]
        if not plugin.instance:
            raise RuntimeError(f"Plugin not loaded: {plugin_name}")

        return plugin.instance.execute(command, args)

    def update(self, plugin_name: str) -> bool:
        """Update a plugin to latest version.

        Args:
            plugin_name: Plugin name

        Returns:
            True if update successful
        """
        if plugin_name not in self.installed_plugins:
            print(f"Plugin not installed: {plugin_name}")
            return False

        # Uninstall old version
        if not self.uninstall(plugin_name):
            return False

        # Install latest version
        return self.install(plugin_name)

    def update_all(self) -> Dict[str, bool]:
        """Update all installed plugins.

        Returns:
            Dictionary of plugin names and update status
        """
        results = {}
        for plugin_name in list(self.installed_plugins.keys()):
            results[plugin_name] = self.update(plugin_name)
        return results
