"""
Registry CLI Commands

Commands for managing remote registries and packages.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Manage package registries")
console = Console()


@app.command("list")
def list_registries(
    include_disabled: bool = typer.Option(False, "--all", "-a", help="Include disabled registries"),
):
    """List configured registries."""
    from flowmason_core.registry.remote import get_remote_registry

    client = get_remote_registry()
    registries = client.list_registries(include_disabled=include_disabled)

    if not registries:
        console.print("No registries configured.")
        console.print("\nAdd a registry with: [bold]fm registry add <name> <url>[/bold]")
        return

    table = Table(title="Configured Registries")
    table.add_column("Name", style="cyan")
    table.add_column("URL")
    table.add_column("Status")
    table.add_column("Priority", justify="right")
    table.add_column("Default")

    for reg in registries:
        status = "[green]enabled[/green]" if reg.enabled else "[red]disabled[/red]"
        default = "[yellow]Yes[/yellow]" if reg.is_default else ""
        name = f"{reg.name}" + (" [dim](publish)[/dim]" if reg.can_publish else "")

        table.add_row(name, reg.url, status, str(reg.priority), default)

    console.print(table)


@app.command("add")
def add_registry(
    name: str = typer.Argument(..., help="Unique name for the registry"),
    url: str = typer.Argument(..., help="Base URL of the registry"),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="Authentication token"),
    priority: int = typer.Option(100, "--priority", "-p", help="Priority (lower = higher)"),
    set_default: bool = typer.Option(False, "--default", help="Set as default registry"),
):
    """Add a new registry."""
    from flowmason_core.registry.remote import get_remote_registry

    client = get_remote_registry()

    try:
        config = client.add_registry(
            name=name,
            url=url,
            auth_token=token,
            priority=priority,
            set_default=set_default,
        )

        if config.enabled:
            console.print(f"[green]Added registry '{name}'[/green]")
        else:
            console.print(f"[yellow]Added registry '{name}' (could not connect)[/yellow]")

        if set_default:
            console.print(f"Set as default registry")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("remove")
def remove_registry(
    name: str = typer.Argument(..., help="Registry name to remove"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Remove a registry."""
    from flowmason_core.registry.remote import get_remote_registry

    if not yes:
        confirm = typer.confirm(f"Remove registry '{name}'?")
        if not confirm:
            raise typer.Abort()

    client = get_remote_registry()

    if client.remove_registry(name):
        console.print(f"[green]Removed registry '{name}'[/green]")
    else:
        console.print(f"[red]Registry '{name}' not found[/red]")
        raise typer.Exit(1)


@app.command("set-default")
def set_default_registry(
    name: str = typer.Argument(..., help="Registry name to set as default"),
):
    """Set a registry as the default."""
    from flowmason_core.registry.remote import get_remote_registry

    client = get_remote_registry()

    if client.set_default_registry(name):
        console.print(f"[green]Set '{name}' as default registry[/green]")
    else:
        console.print(f"[red]Registry '{name}' not found[/red]")
        raise typer.Exit(1)


@app.command("cache")
def cache_command(
    clear: bool = typer.Option(False, "--clear", help="Clear the package cache"),
    older_than: Optional[int] = typer.Option(None, "--older-than", help="Clear packages older than N days"),
):
    """Manage the package cache."""
    from flowmason_core.registry.remote import get_remote_registry

    client = get_remote_registry()

    if clear:
        removed = client.clear_cache(older_than_days=older_than)
        console.print(f"[green]Removed {removed} cached package(s)[/green]")
    else:
        stats = client.get_cache_stats()

        table = Table(title="Package Cache")
        table.add_column("Property")
        table.add_column("Value")

        table.add_row("Location", stats["cache_dir"])
        table.add_row("Packages", str(stats["packages"]))
        table.add_row("Size", f"{stats['total_size_bytes'] / 1024 / 1024:.2f} MB")

        console.print(table)


# Top-level commands (added to main CLI, not under 'registry' group)


def search_packages(
    query: str = typer.Argument(..., help="Search query"),
    registry: Optional[str] = typer.Option(None, "--registry", "-r", help="Search specific registry"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Search for packages in registries."""
    from flowmason_core.registry.remote import get_remote_registry

    client = get_remote_registry()

    try:
        result = client.search(
            query=query,
            registry_name=registry,
            category=category,
        )

        if as_json:
            output = {
                "query": result.query,
                "total_count": result.total_count,
                "packages": [
                    {
                        "name": p.name,
                        "version": p.version,
                        "description": p.description,
                        "registry": p.registry_name,
                        "components": p.components,
                    }
                    for p in result.packages
                ]
            }
            console.print_json(data=output)
            return

        if not result.packages:
            console.print(f"[yellow]No packages found for '{query}'[/yellow]")
            return

        table = Table(title=f"Search Results for '{query}'")
        table.add_column("Package", style="cyan")
        table.add_column("Version")
        table.add_column("Description")
        table.add_column("Registry")
        table.add_column("Components")

        for pkg in result.packages:
            table.add_row(
                pkg.name,
                pkg.version,
                (pkg.description or "")[:50] + ("..." if len(pkg.description or "") > 50 else ""),
                pkg.registry_name,
                str(pkg.component_count),
            )

        console.print(table)
        console.print(f"\n[dim]Found {result.total_count} package(s)[/dim]")

    except Exception as e:
        console.print(f"[red]Search failed: {e}[/red]")
        raise typer.Exit(1)


def install_package(
    name: str = typer.Argument(..., help="Package name to install"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Specific version (default: latest)"),
    registry: Optional[str] = typer.Option(None, "--registry", "-r", help="From specific registry"),
    packages_dir: Optional[str] = typer.Option(None, "--dir", "-d", help="Install directory"),
):
    """Install a package from a registry."""
    from flowmason_core.registry.remote import (
        PackageNotFoundError,
        get_remote_registry,
    )

    client = get_remote_registry()

    try:
        dest = Path(packages_dir) if packages_dir else None
        version_str = f"@{version}" if version else ""

        with console.status(f"Installing {name}{version_str}..."):
            install_path = client.install(
                name=name,
                version=version,
                registry_name=registry,
                packages_dir=dest,
            )

        console.print(f"[green]Installed to: {install_path}[/green]")

        # Refresh local registry
        from flowmason_core.registry import get_registry

        local_registry = get_registry()
        local_registry.register_package(install_path)
        console.print("[dim]Package registered in local registry[/dim]")

    except PackageNotFoundError:
        console.print(f"[red]Package '{name}' not found[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Installation failed: {e}[/red]")
        raise typer.Exit(1)


def publish_package(
    package_path: str = typer.Argument(..., help="Path to .fmpkg file"),
    registry: Optional[str] = typer.Option(None, "--registry", "-r", help="Publish to specific registry"),
):
    """Publish a package to a registry."""
    from flowmason_core.registry.remote import (
        AuthenticationError,
        PackagePublishError,
        get_remote_registry,
    )

    path = Path(package_path)
    if not path.exists():
        console.print(f"[red]File not found: {package_path}[/red]")
        raise typer.Exit(1)

    if not path.suffix == ".fmpkg":
        console.print("[red]Package must be a .fmpkg file[/red]")
        raise typer.Exit(1)

    client = get_remote_registry()

    try:
        with console.status(f"Publishing {path.name}..."):
            pkg_info = client.publish(path, registry_name=registry)

        console.print(f"[green]Published {pkg_info.name}@{pkg_info.version}[/green]")
        console.print(f"Registry: {pkg_info.registry_name}")
        console.print(f"Download URL: {pkg_info.download_url}")

    except AuthenticationError:
        console.print("[red]Authentication required.[/red]")
        console.print("Add a token with: [bold]fm registry add <name> <url> --token <token>[/bold]")
        raise typer.Exit(1)
    except PackagePublishError as e:
        console.print(f"[red]Publish failed: {e}[/red]")
        raise typer.Exit(1)
