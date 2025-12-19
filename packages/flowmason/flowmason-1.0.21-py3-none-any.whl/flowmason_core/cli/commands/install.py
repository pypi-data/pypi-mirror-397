"""
Install command for FlowMason CLI.

Install .fmpkg packages locally.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def install(
    package_path: Path = typer.Argument(
        ...,
        help="Path to .fmpkg package file",
        exists=True,
        readable=True,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing installation",
    ),
):
    """
    Install a .fmpkg package locally.

    Examples:
        flowmason install my-package-1.0.0.fmpkg
        flowmason install ./packages/my-package-1.0.0.fmpkg --force
    """
    from flowmason_core.packaging.installer import PackageInstaller

    console.print("\n[bold blue]FlowMason[/bold blue] Install\n")
    console.print(f"Package: {package_path}")

    installer = PackageInstaller()

    try:
        manifest = installer.install(package_path, force=force)

        console.print(Panel(
            f"[green]Package installed successfully![/green]\n\n"
            f"Name: {manifest.name}\n"
            f"Version: {manifest.version}\n"
            f"Description: {manifest.description}\n"
            f"Pipelines: {len(manifest.pipelines)}\n"
            f"Components: {len(manifest.components)}",
            title="FlowMason Install",
            border_style="green",
        ))

    except ValueError as e:
        console.print(f"[yellow]Warning:[/yellow] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def uninstall(
    name: str = typer.Argument(
        ...,
        help="Package name to uninstall",
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        "-v",
        help="Specific version to uninstall (default: all versions)",
    ),
):
    """
    Uninstall a FlowMason package.

    Examples:
        flowmason uninstall my-package
        flowmason uninstall my-package --version 1.0.0
    """
    from flowmason_core.packaging.installer import PackageInstaller

    console.print("\n[bold blue]FlowMason[/bold blue] Uninstall\n")

    installer = PackageInstaller()

    if installer.uninstall(name, version):
        if version:
            console.print(f"[green]Uninstalled {name}@{version}[/green]")
        else:
            console.print(f"[green]Uninstalled all versions of {name}[/green]")
    else:
        console.print(f"[yellow]Warning:[/yellow] Package '{name}' not found")


def list_packages():
    """
    List installed FlowMason packages.

    Examples:
        flowmason list
    """
    from flowmason_core.packaging.installer import PackageInstaller

    console.print("\n[bold blue]FlowMason[/bold blue] Installed Packages\n")

    installer = PackageInstaller()
    packages = installer.list_installed()

    if not packages:
        console.print("[dim]No packages installed[/dim]")
        console.print("Use 'flowmason install <package.fmpkg>' to install packages")
        return

    table = Table(title="Installed Packages")
    table.add_column("Name", style="cyan")
    table.add_column("Version")
    table.add_column("Description")

    for pkg in packages:
        table.add_row(
            pkg["name"],
            pkg["version"],
            pkg["description"][:50] + "..." if len(pkg["description"]) > 50 else pkg["description"],
        )

    console.print(table)
