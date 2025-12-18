"""
Org commands for FlowMason CLI.

Manage FlowMason org connections (similar to Salesforce DX org management).
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    help="Manage FlowMason org connections",
    no_args_is_help=True,
)

console = Console()

# Config file locations
FLOWMASON_DIR = Path.home() / ".flowmason"
ORGS_FILE = FLOWMASON_DIR / "orgs.json"


def _ensure_config_dir():
    """Ensure the .flowmason config directory exists."""
    FLOWMASON_DIR.mkdir(parents=True, exist_ok=True)


def _load_orgs() -> Dict[Any, Any]:
    """Load orgs configuration."""
    _ensure_config_dir()
    if ORGS_FILE.exists():
        try:
            result = json.loads(ORGS_FILE.read_text())
            return dict(result) if isinstance(result, dict) else {"orgs": {}, "default": None}
        except json.JSONDecodeError:
            return {"orgs": {}, "default": None}
    return {"orgs": {}, "default": None}


def _save_orgs(config: dict):
    """Save orgs configuration."""
    _ensure_config_dir()
    ORGS_FILE.write_text(json.dumps(config, indent=2))


@app.command("login")
def org_login(
    alias: str = typer.Option(
        ...,
        "--alias",
        "-a",
        help="Alias for this org connection",
    ),
    instance_url: str = typer.Option(
        ...,
        "--instance-url",
        "-u",
        help="URL of the FlowMason org (e.g., https://staging.flowmason.io)",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="API key for authentication (or use FLOWMASON_API_KEY env var)",
    ),
    set_default: bool = typer.Option(
        False,
        "--default",
        "-d",
        help="Set this org as the default",
    ),
):
    """
    Authorize a FlowMason org connection.

    Similar to 'sf org login' in Salesforce DX.

    Examples:
        flowmason org login --alias staging --instance-url https://staging.flowmason.io
        flowmason org login -a prod -u https://prod.flowmason.io --default
        flowmason org login -a dev -u http://localhost:8999 -k my-api-key
    """
    console.print(f"\n[bold blue]FlowMason[/bold blue] Connecting to org: {alias}\n")

    # Get API key from option or environment
    api_key = api_key or os.environ.get("FLOWMASON_API_KEY")

    # Normalize instance URL
    instance_url = instance_url.rstrip("/")

    # Test connection
    console.print(f"Testing connection to {instance_url}...")
    try:
        import httpx
        response = httpx.get(f"{instance_url}/health", timeout=10)
        if response.status_code == 200:
            console.print("[green]Connection successful![/green]")
        else:
            console.print(f"[yellow]Warning:[/yellow] Server returned status {response.status_code}")
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Could not connect: {e}")
        console.print("Saving connection anyway. The server may be offline.")

    # Save org configuration
    config = _load_orgs()
    config["orgs"][alias] = {
        "instance_url": instance_url,
        "api_key": api_key,
        "created_at": datetime.utcnow().isoformat(),
        "last_used": None,
    }

    if set_default or not config.get("default"):
        config["default"] = alias

    _save_orgs(config)

    console.print(Panel(
        f"[green]Org connected successfully![/green]\n\n"
        f"Alias: {alias}\n"
        f"URL: {instance_url}\n"
        f"Default: {'Yes' if config['default'] == alias else 'No'}",
        title="FlowMason Org",
        border_style="green",
    ))


@app.command("logout")
def org_logout(
    alias: str = typer.Option(
        None,
        "--alias",
        "-a",
        help="Alias of the org to disconnect",
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Alias of the org to disconnect (alias for --alias)",
    ),
    all_orgs: bool = typer.Option(
        False,
        "--all",
        help="Disconnect from all orgs",
    ),
):
    """
    Disconnect from a FlowMason org.

    Examples:
        flowmason org logout --alias staging
        flowmason org logout --target prod
        flowmason org logout --all
    """
    config = _load_orgs()

    if all_orgs:
        config["orgs"] = {}
        config["default"] = None
        _save_orgs(config)
        console.print("[green]Disconnected from all orgs[/green]")
        return

    # Use alias or target
    org_alias = alias or target
    if not org_alias:
        console.print("[red]Error:[/red] Specify an org with --alias or --target")
        raise typer.Exit(1)

    if org_alias not in config["orgs"]:
        console.print(f"[yellow]Warning:[/yellow] Org '{org_alias}' not found")
        raise typer.Exit(0)

    del config["orgs"][org_alias]

    # Clear default if it was this org
    if config["default"] == org_alias:
        config["default"] = next(iter(config["orgs"].keys()), None)

    _save_orgs(config)
    console.print(f"[green]Disconnected from org '{org_alias}'[/green]")


@app.command("list")
def org_list():
    """
    List all connected FlowMason orgs.

    Examples:
        flowmason org list
    """
    config = _load_orgs()

    if not config["orgs"]:
        console.print("[yellow]No orgs connected.[/yellow]")
        console.print("Use 'flowmason org login' to connect to an org.")
        return

    table = Table(title="Connected Orgs")
    table.add_column("Alias", style="cyan")
    table.add_column("Instance URL")
    table.add_column("Default")
    table.add_column("Last Used")

    for alias, org in config["orgs"].items():
        is_default = "✓" if config["default"] == alias else ""
        last_used = org.get("last_used", "Never")
        if last_used and last_used != "Never":
            # Format the date nicely
            try:
                dt = datetime.fromisoformat(last_used)
                last_used = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass

        table.add_row(
            alias,
            org["instance_url"],
            is_default,
            last_used or "Never",
        )

    console.print(table)


@app.command("default")
def org_default(
    alias: str = typer.Argument(
        ...,
        help="Alias of the org to set as default",
    ),
):
    """
    Set the default FlowMason org.

    Examples:
        flowmason org default staging
        flowmason org default production
    """
    config = _load_orgs()

    if alias not in config["orgs"]:
        console.print(f"[red]Error:[/red] Org '{alias}' not found")
        console.print("Use 'flowmason org list' to see available orgs")
        raise typer.Exit(1)

    config["default"] = alias
    _save_orgs(config)
    console.print(f"[green]Default org set to '{alias}'[/green]")


@app.command("display")
def org_display(
    alias: str = typer.Option(
        None,
        "--alias",
        "-a",
        help="Alias of the org to display",
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Alias of the org to display (alias for --alias)",
    ),
):
    """
    Display details for a FlowMason org.

    Examples:
        flowmason org display
        flowmason org display --alias staging
        flowmason org display --target production
    """
    config = _load_orgs()

    # Determine which org to display
    org_alias = alias or target or config.get("default")
    if not org_alias:
        console.print("[red]Error:[/red] No org specified and no default set")
        console.print("Use --alias to specify an org, or 'flowmason org default' to set a default")
        raise typer.Exit(1)

    if org_alias not in config["orgs"]:
        console.print(f"[red]Error:[/red] Org '{org_alias}' not found")
        raise typer.Exit(1)

    org = config["orgs"][org_alias]
    is_default = config["default"] == org_alias

    # Try to get health info from the org
    status = "[yellow]Unknown[/yellow]"
    version = "Unknown"
    try:
        import httpx
        response = httpx.get(f"{org['instance_url']}/health", timeout=5)
        if response.status_code == 200:
            status = "[green]Connected[/green]"
            data = response.json()
            version = data.get("version", "Unknown")
        else:
            status = f"[red]Error ({response.status_code})[/red]"
    except Exception:
        status = "[red]Unreachable[/red]"

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")
    table.add_row("Alias", org_alias)
    table.add_row("Instance URL", org["instance_url"])
    table.add_row("Status", status)
    table.add_row("Version", version)
    table.add_row("Default", "Yes" if is_default else "No")
    table.add_row("API Key", "[dim]" + ("Configured" if org.get("api_key") else "Not set") + "[/dim]")
    table.add_row("Created", org.get("created_at", "Unknown"))
    table.add_row("Last Used", org.get("last_used", "Never"))

    console.print(Panel(table, title=f"Org: {org_alias}", border_style="blue"))


def get_default_org() -> Optional[dict]:
    """Get the default org configuration."""
    config = _load_orgs()
    default_alias = config.get("default")
    if default_alias and default_alias in config["orgs"]:
        org = config["orgs"][default_alias]
        org["alias"] = default_alias
        return dict(org) if isinstance(org, dict) else None
    return None


def get_org(alias: str) -> Optional[Dict[Any, Any]]:
    """Get an org configuration by alias."""
    config = _load_orgs()
    if alias in config["orgs"]:
        org = config["orgs"][alias]
        org["alias"] = alias
        return dict(org) if isinstance(org, dict) else None
    return None


def update_last_used(alias: str):
    """Update the last_used timestamp for an org."""
    config = _load_orgs()
    if alias in config["orgs"]:
        config["orgs"][alias]["last_used"] = datetime.utcnow().isoformat()
        _save_orgs(config)
