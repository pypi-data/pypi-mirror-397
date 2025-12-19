"""CLI commands for plugin management."""

import click
from typing import Optional

from lmapp.plugins import PluginManager


@click.group()
def plugin():
    """Manage lmapp plugins."""
    pass


@plugin.command()
@click.argument("query")
def search(query: str):
    """Search for plugins in the registry."""
    manager = PluginManager()
    results = manager.search(query)

    if not results:
        click.echo(f"No plugins found matching: {query}")
        return

    click.echo(f"\nFound {len(results)} plugins:\n")
    for plugin in results:
        click.echo(f"  {plugin['name']} v{plugin['version']}")
        click.echo(f"    Author: {plugin['author']}")
        click.echo(f"    Description: {plugin['description']}")
        click.echo(f"    Rating: {plugin['rating']:.1f}/5.0 ({plugin['downloads']} downloads)")
        if plugin["tags"]:
            click.echo(f"    Tags: {', '.join(plugin['tags'])}")
        click.echo()


@plugin.command()
@click.argument("plugin_name")
@click.option("--version", default=None, help="Specific version to install")
def install(plugin_name: str, version: Optional[str]):
    """Install a plugin."""
    manager = PluginManager()
    click.echo(f"Installing {plugin_name}...")

    if manager.install(plugin_name, version):
        click.echo(f"✓ Successfully installed {plugin_name}")
    else:
        click.echo(f"✗ Failed to install {plugin_name}", err=True)


@plugin.command()
def list():
    """List installed plugins."""
    manager = PluginManager()
    plugins = manager.list_installed()

    if not plugins:
        click.echo("No plugins installed")
        return

    click.echo(f"Installed plugins ({len(plugins)}):\n")
    for plugin in plugins:
        click.echo(f"  {plugin['name']} v{plugin['version']}")
        click.echo(f"    Path: {plugin['path']}")


@plugin.command()
@click.argument("plugin_name")
def uninstall(plugin_name: str):
    """Uninstall a plugin."""
    manager = PluginManager()

    if click.confirm(f"Uninstall {plugin_name}?"):
        if manager.uninstall(plugin_name):
            click.echo(f"✓ Successfully uninstalled {plugin_name}")
        else:
            click.echo(f"✗ Failed to uninstall {plugin_name}", err=True)


@plugin.command()
@click.argument("plugin_name")
def update(plugin_name: str):
    """Update a plugin."""
    manager = PluginManager()
    click.echo(f"Updating {plugin_name}...")

    if manager.update(plugin_name):
        click.echo(f"✓ Successfully updated {plugin_name}")
    else:
        click.echo(f"✗ Failed to update {plugin_name}", err=True)


@plugin.command()
def update_all():
    """Update all installed plugins."""
    manager = PluginManager()
    click.echo("Updating all plugins...")

    results = manager.update_all()
    success = sum(1 for v in results.values() if v)

    click.echo(f"\nUpdated {success}/{len(results)} plugins")
    for plugin_name, success in results.items():
        status = "✓" if success else "✗"
        click.echo(f"  {status} {plugin_name}")
