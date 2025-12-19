"""
Pack command for FlowMason CLI.

Build .fmpkg packages from FlowMason projects.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def pack(
    path: Optional[Path] = typer.Argument(
        None,
        help="Path to project directory (default: current directory)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path",
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        "-v",
        help="Override package version",
    ),
):
    """
    Build a .fmpkg package from a FlowMason project.

    Examples:
        flowmason pack
        flowmason pack --version 1.2.0
        flowmason pack --output my-package.fmpkg
        flowmason pack /path/to/project
    """
    from flowmason_core.packaging.builder import PackageBuilder

    project_path = Path(path) if path else Path.cwd()
    project_path = project_path.resolve()

    console.print("\n[bold blue]FlowMason[/bold blue] Pack\n")
    console.print(f"Project: {project_path}")

    # Check for project manifest
    manifest_path = project_path / "flowmason.json"
    if not manifest_path.exists():
        console.print("[red]Error:[/red] No flowmason.json found")
        console.print("Run 'flowmason init' to create a project")
        raise typer.Exit(1)

    # Create builder
    builder = PackageBuilder(project_path)

    # Discover files
    files = builder.discover_files()
    total_files = sum(len(f) for f in files.values())

    console.print(f"\nDiscovered {total_files} files:\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Type")
    table.add_column("Count")
    table.add_column("Files")

    for file_type, file_list in files.items():
        if file_list:
            file_names = ", ".join(str(f.name) for f in file_list[:3])
            if len(file_list) > 3:
                file_names += f", ... (+{len(file_list) - 3} more)"
            table.add_row(file_type.capitalize(), str(len(file_list)), file_names)

    console.print(table)
    console.print()

    if total_files == 0:
        console.print("[yellow]Warning:[/yellow] No files found to package")
        console.print("Add pipelines to pipelines/ or components to components/")
        raise typer.Exit(1)

    # Build package
    try:
        package_path = builder.build(output_path=output, version=version)
        manifest = builder.manifest

        manifest_name = manifest.name if manifest else "unknown"
        manifest_version = manifest.version if manifest else "unknown"

        console.print(Panel(
            f"[green]Package built successfully![/green]\n\n"
            f"Name: {manifest_name}\n"
            f"Version: {manifest_version}\n"
            f"Output: {package_path}\n"
            f"Size: {package_path.stat().st_size / 1024:.1f} KB",
            title="FlowMason Pack",
            border_style="green",
        ))

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
