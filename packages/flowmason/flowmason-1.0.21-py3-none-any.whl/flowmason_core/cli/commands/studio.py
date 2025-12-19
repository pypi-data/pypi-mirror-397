"""
Studio command for FlowMason CLI.

Manage FlowMason Studio backend server.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from flowmason_core.resources.bootstrap import ensure_extra_assets
app = typer.Typer(
    help="Manage FlowMason Studio backend",
    no_args_is_help=True,
)

console = Console()

# PID file location
PID_FILE = Path.home() / ".flowmason" / "studio.pid"


@app.command()
def start(
    port: int = typer.Option(
        8999,
        "--port",
        "-p",
        help="Port to run the server on",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        "-h",
        help="Host to bind to",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        "-r",
        help="Enable auto-reload for development",
    ),
    background: bool = typer.Option(
        False,
        "--background",
        "-b",
        help="Run in background",
    ),
):
    """
    Start FlowMason Studio backend server.

    Examples:
        flowmason studio start
        flowmason studio start --port 8080
        flowmason studio start --background
        flowmason studio start --reload
    """
    # Check if already running
    if _is_running():
        pid = _get_pid()
        console.print(f"[yellow]Warning:[/yellow] Studio already running (PID: {pid})")
        console.print("Use 'flowmason studio stop' to stop it first")
        raise typer.Exit(1)

    console.print("\n[bold blue]FlowMason Studio[/bold blue] Starting...\n")

    # Ensure extra assets (frontend, demos, etc.) are available locally.
    # This may download a tar.gz from the FlowMason website on first run.
    ensure_extra_assets(console)

    # Try to find the studio module
    try:
        import flowmason_studio  # noqa: F401
        del flowmason_studio  # Only needed to verify import works
    except ImportError:
        console.print("[red]Error:[/red] flowmason-studio not installed")
        console.print("Install with: pip install flowmason-studio")
        raise typer.Exit(1)

    # Build uvicorn command
    cmd = [
        sys.executable, "-m", "uvicorn",
        "flowmason_studio.api.app:app",
        "--host", host,
        "--port", str(port),
    ]

    if reload:
        cmd.append("--reload")

    console.print(f"  Host: {host}")
    console.print(f"  Port: {port}")
    console.print(f"  Reload: {reload}")
    console.print()

    if background:
        # Run in background
        console.print("Starting in background...")

        # Ensure PID directory exists
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        # Save PID
        PID_FILE.write_text(str(process.pid))

        # Wait a moment to check if it started
        time.sleep(1)

        if process.poll() is None:
            console.print(Panel(
                f"[green]Studio started[/green]\n\n"
                f"URL: http://{host}:{port}\n"
                f"PID: {process.pid}",
                title="FlowMason Studio",
                border_style="green",
            ))
        else:
            console.print("[red]Error:[/red] Studio failed to start")
            raise typer.Exit(1)
    else:
        # Run in foreground
        console.print(f"Starting Studio at http://{host}:{port}")
        console.print("Press Ctrl+C to stop\n")

        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            console.print("\n\nStopping Studio...")


@app.command()
def stop():
    """
    Stop FlowMason Studio backend server.

    Examples:
        flowmason studio stop
    """
    if not _is_running():
        console.print("[yellow]Warning:[/yellow] Studio is not running")
        raise typer.Exit(0)

    pid = _get_pid()
    console.print(f"Stopping Studio (PID: {pid})...")

    try:
        os.kill(pid, signal.SIGTERM)

        # Wait for process to stop
        for _ in range(10):
            time.sleep(0.5)
            try:
                os.kill(pid, 0)  # Check if process exists
            except ProcessLookupError:
                break

        # Force kill if still running
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

        # Remove PID file
        if PID_FILE.exists():
            PID_FILE.unlink()

        console.print("[green]Studio stopped[/green]")

    except ProcessLookupError:
        console.print("[yellow]Warning:[/yellow] Process not found")
        if PID_FILE.exists():
            PID_FILE.unlink()
    except PermissionError:
        console.print("[red]Error:[/red] Permission denied. Try running as root.")
        raise typer.Exit(1)


@app.command()
def status():
    """
    Check FlowMason Studio status.

    Examples:
        flowmason studio status
    """
    if _is_running():
        pid = _get_pid()
        console.print(Panel(
            f"[green]Studio is running[/green]\n\n"
            f"PID: {pid}",
            title="FlowMason Studio",
            border_style="green",
        ))

        # Try to get more info
        try:
            import requests  # type: ignore[import-untyped]
            response = requests.get("http://127.0.0.1:8999/health", timeout=2)
            if response.status_code == 200:
                console.print("\nHealth check: [green]OK[/green]")
        except Exception:
            console.print("\nHealth check: [yellow]Unable to connect[/yellow]")
    else:
        console.print(Panel(
            "[yellow]Studio is not running[/yellow]",
            title="FlowMason Studio",
            border_style="yellow",
        ))


@app.command()
def restart(
    port: int = typer.Option(
        8999,
        "--port",
        "-p",
        help="Port to run the server on",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        "-h",
        help="Host to bind to",
    ),
):
    """
    Restart FlowMason Studio backend server.

    Examples:
        flowmason studio restart
    """
    if _is_running():
        stop()
        time.sleep(1)

    start(port=port, host=host, background=True)


def _is_running() -> bool:
    """Check if Studio is running."""
    if not PID_FILE.exists():
        return False

    pid = _get_pid()
    if pid is None:
        return False

    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        # Clean up stale PID file
        PID_FILE.unlink()
        return False


def _get_pid() -> Optional[int]:
    """Get Studio PID from file."""
    if not PID_FILE.exists():
        return None

    try:
        return int(PID_FILE.read_text().strip())
    except (ValueError, FileNotFoundError):
        return None
