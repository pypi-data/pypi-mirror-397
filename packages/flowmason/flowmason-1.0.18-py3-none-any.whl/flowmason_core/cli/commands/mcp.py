"""
MCP Server command for FlowMason CLI.

Expose FlowMason pipelines to AI assistants via Model Context Protocol.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    help="Model Context Protocol (MCP) server for AI integration",
    no_args_is_help=True,
)

console = Console()


@app.command()
def serve(
    pipelines_dir: Optional[Path] = typer.Option(
        None,
        "--pipelines",
        "-p",
        help="Directory containing pipeline files",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
    studio_url: str = typer.Option(
        "http://localhost:8999",
        "--studio-url",
        "-s",
        help="FlowMason Studio API URL",
    ),
    transport: str = typer.Option(
        "stdio",
        "--transport",
        "-t",
        help="Transport type (stdio or sse)",
    ),
):
    """
    Start the FlowMason MCP server.

    This exposes FlowMason pipelines as MCP tools that AI assistants
    (like Claude) can use to discover and run pipelines.

    Examples:
        flowmason mcp serve
        flowmason mcp serve --pipelines ./pipelines
        flowmason mcp serve --studio-url http://localhost:8999
    """
    try:
        from flowmason_core.mcp import run_mcp_server
    except ImportError:
        console.print(Panel(
            "[red]MCP SDK not installed[/red]\n\n"
            "Install with: pip install flowmason[mcp]\n"
            "Or: pip install mcp",
            title="Missing Dependency",
            border_style="red",
        ))
        raise typer.Exit(1)

    console.print(Panel(
        "[bold blue]FlowMason MCP Server[/bold blue]\n\n"
        f"Pipelines: {pipelines_dir or 'auto-detect'}\n"
        f"Studio: {studio_url}\n"
        f"Transport: {transport}\n\n"
        "[dim]Press Ctrl+C to stop[/dim]",
        border_style="blue",
    ))

    try:
        run_mcp_server(
            pipelines_dir=pipelines_dir,
            studio_url=studio_url,
            transport=transport,
        )
    except KeyboardInterrupt:
        console.print("\n[dim]Server stopped[/dim]")


@app.command()
def config():
    """
    Show MCP server configuration for Claude Desktop.

    Prints the configuration to add to Claude Desktop's config file.
    """
    import json
    import sys

    # Find python executable
    python_path = sys.executable

    config = {
        "mcpServers": {
            "flowmason": {
                "command": python_path,
                "args": ["-m", "flowmason_core.cli.main", "mcp", "serve"],
                "env": {
                    "PYTHONUNBUFFERED": "1"
                }
            }
        }
    }

    console.print(Panel(
        "[bold]Add this to your Claude Desktop config[/bold]\n\n"
        f"Config file location:\n"
        f"  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json\n"
        f"  Windows: %APPDATA%/Claude/claude_desktop_config.json\n\n"
        f"Configuration:\n"
        f"[green]{json.dumps(config, indent=2)}[/green]",
        title="MCP Server Configuration",
        border_style="blue",
    ))


@app.command()
def test():
    """
    Test the MCP server by listing available tools.
    """
    try:
        from flowmason_core.mcp import create_mcp_server
    except ImportError:
        console.print(Panel(
            "[red]MCP SDK not installed[/red]\n\n"
            "Install with: pip install flowmason[mcp]\n"
            "Or: pip install mcp",
            title="Missing Dependency",
            border_style="red",
        ))
        raise typer.Exit(1)

    console.print("[bold blue]FlowMason MCP Server Test[/bold blue]\n")

    try:
        mcp = create_mcp_server()
        console.print("[green]Server created successfully[/green]\n")

        # List registered tools
        console.print("[bold]Available Tools:[/bold]")
        if hasattr(mcp, '_tools'):
            for tool_name in mcp._tools:
                console.print(f"  - {tool_name}")
        else:
            console.print("  - list_pipelines")
            console.print("  - get_pipeline")
            console.print("  - run_pipeline")
            console.print("  - list_components")
            console.print("  - get_component")

        console.print("\n[green]MCP server is ready to use![/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
