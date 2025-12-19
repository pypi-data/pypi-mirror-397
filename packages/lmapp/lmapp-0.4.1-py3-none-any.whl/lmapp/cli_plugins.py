import click
import sys
import urllib.request
from pathlib import Path
from rich.console import Console
from rich.table import Table
from lmapp.plugins.plugin_marketplace import PluginRegistry
from lmapp.utils.logging import logger

console = Console()

# Default Registry URL (Placeholder)
DEFAULT_REGISTRY_URL = "https://raw.githubusercontent.com/nabaznyl/lmapp-plugins/main/registry.json"


@click.group()
def plugins():
    """Manage plugins (search, install, list)"""
    pass


@plugins.command()
@click.argument("query", required=False)
def search(query):
    """Search for plugins in the marketplace"""
    logger.debug(f"Searching plugins with query: {query}")

    registry = PluginRegistry(name="official", url=DEFAULT_REGISTRY_URL, description="Official LMAPP Plugin Registry")

    with console.status("[bold green]Fetching registry..."):
        if not registry.fetch_remote():
            console.print("[yellow]Warning: Could not fetch remote registry. Showing local cache if available.[/yellow]")
            # In a real implementation, we would load from cache here

    results = registry.search(query) if query else list(registry.plugins.values())

    if not results:
        console.print(f"[yellow]No plugins found matching '{query}'[/yellow]")
        return

    table = Table(title=f"Plugin Search Results ({len(results)})")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Verified", justify="center")

    for p in results:
        verified_mark = "✓" if p.verified else ""
        table.add_row(p.name, p.name, p.description, verified_mark)  # Using name as ID for now if ID missing

    console.print(table)


@plugins.command()
@click.argument("plugin_name")
def install(plugin_name):
    """Install a plugin by Name"""
    logger.debug(f"Installing plugin: {plugin_name}")

    registry = PluginRegistry(name="official", url=DEFAULT_REGISTRY_URL, description="Official LMAPP Plugin Registry")

    with console.status("[bold green]Fetching registry..."):
        registry.fetch_remote()

    plugin = registry.get_by_name(plugin_name)
    if not plugin:
        console.print(f"[red]Plugin '{plugin_name}' not found.[/red]")
        sys.exit(1)

    console.print(f"Installing [bold cyan]{plugin.name}[/bold cyan] v{plugin.version}...")

    # Determine install path
    safe_name = plugin.name.replace(" ", "_").lower()
    install_dir = Path.home() / ".lmapp" / "plugins"
    install_dir.mkdir(parents=True, exist_ok=True)
    install_path = install_dir / f"{safe_name}.py"

    if install_path.exists():
        console.print(f"[yellow]Plugin already exists at {install_path}. Overwriting...[/yellow]")

    with console.status(f"Downloading to {install_path}..."):
        try:
            # Check if install_url is valid
            if not plugin.install_url.startswith("http"):
                console.print(f"[red]Invalid install URL: {plugin.install_url}[/red]")
                sys.exit(1)

            urllib.request.urlretrieve(plugin.install_url, install_path)
            console.print(f"[green]Successfully installed {plugin.name} to {install_path}![/green]")
        except Exception as e:
            console.print(f"[red]Failed to download plugin: {e}[/red]")
            sys.exit(1)
