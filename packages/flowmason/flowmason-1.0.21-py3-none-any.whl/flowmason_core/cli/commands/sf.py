"""
Salesforce integration commands for FlowMason CLI.
Adds native Salesforce org support to fm CLI.
"""

import json
import subprocess
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(
    help="Salesforce integration commands",
    no_args_is_help=True,
)

console = Console()


def _get_sf_org_info(org_alias: Optional[str] = None):
    """Get Salesforce org information using sf CLI."""
    cmd = ["sf", "org", "display", "--json"]
    if org_alias:
        cmd.extend(["--target-org", org_alias])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return data.get("result", {})
    except subprocess.CalledProcessError:
        return None
    except json.JSONDecodeError:
        return None


def _list_sf_orgs():
    """List Salesforce orgs using sf CLI."""
    try:
        result = subprocess.run(
            ["sf", "org", "list", "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return data.get("result", {})
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def _configure_fm_org_from_sf(sf_alias: Optional[str] = None, fm_alias: Optional[str] = None):
    """Configure fm org using Salesforce org credentials."""
    from .org import _load_orgs, _save_orgs
    from datetime import datetime
    
    # Get Salesforce org info
    sf_info = _get_sf_org_info(sf_alias)
    if not sf_info:
        console.print(f"[red]Error:[/red] Could not get Salesforce org info")
        if sf_alias:
            console.print(f"Org: {sf_alias}")
        console.print("Make sure you're logged in: sf org login web")
        raise typer.Exit(1)
    
    access_token = sf_info.get("accessToken")
    instance_url = sf_info.get("instanceUrl")
    username = sf_info.get("username")
    
    if not access_token or not instance_url:
        console.print("[red]Error:[/red] Missing access token or instance URL")
        raise typer.Exit(1)
    
    # Use sf alias as fm alias if not specified
    if not fm_alias:
        fm_alias = sf_alias or username or "salesforce"
    
    # Save to fm org config
    config = _load_orgs()
    config["orgs"][fm_alias] = {
        "instance_url": instance_url,
        "api_key": access_token,
        "org_type": "salesforce",
        "sf_alias": sf_alias,
        "sf_username": username,
        "created_at": datetime.utcnow().isoformat(),
        "last_used": None,
    }
    
    _save_orgs(config)
    return fm_alias, instance_url, username


@app.command("connect")
def sf_connect(
    sf_org: Optional[str] = typer.Option(
        None,
        "--sf-org",
        "-s",
        help="Salesforce org alias (from sf org list)",
    ),
    alias: Optional[str] = typer.Option(
        None,
        "--alias",
        "-a",
        help="FlowMason alias for this connection (defaults to sf org alias)",
    ),
    set_default: bool = typer.Option(
        False,
        "--default",
        "-d",
        help="Set this as the default fm org",
    ),
):
    """
    Connect to a Salesforce org for fm deployment.
    
    This command configures fm to use your Salesforce org's REST API endpoint.
    It automatically fetches a fresh access token from the Salesforce CLI.
    
    Examples:
        fm sf connect --sf-org Flowmason
        fm sf connect --sf-org myorg --alias production --default
        fm sf connect  # Uses default Salesforce org
    """
    from .org import _load_orgs, _save_orgs
    
    console.print("\n[bold blue]FlowMason[/bold blue] → Salesforce Integration\n")
    
    # Configure fm org from Salesforce
    fm_alias, instance_url, username = _configure_fm_org_from_sf(sf_org, alias)
    
    console.print(f"✅ Connected to Salesforce")
    console.print(f"   FM Alias: [cyan]{fm_alias}[/cyan]")
    console.print(f"   SF Org: {sf_org or '(default)'}")
    console.print(f"   Username: {username}")
    console.print(f"   Instance: {instance_url}")
    
    # Set as default if requested
    if set_default:
        config = _load_orgs()
        config["default"] = fm_alias
        _save_orgs(config)
        console.print(f"\n[green]Set as default org[/green]")
    
    console.print(f"\n[green]Ready to deploy![/green]")
    console.print(f"Usage: fm deploy --target {fm_alias}")


@app.command("refresh")
def sf_refresh(
    alias: str = typer.Argument(
        ...,
        help="FlowMason org alias to refresh",
    ),
):
    """
    Refresh Salesforce access token for an fm org.
    
    Salesforce tokens expire periodically. Use this command to fetch
    a fresh token from the Salesforce CLI and update the fm org configuration.
    
    Examples:
        fm sf refresh salesforce
        fm sf refresh Flowmason
    """
    from .org import _load_orgs, _save_orgs, get_org
    
    console.print(f"\n[bold blue]FlowMason[/bold blue] Refreshing Salesforce token\n")
    
    # Get org configuration
    org = get_org(alias)
    if not org:
        console.print(f"[red]Error:[/red] Org '{alias}' not found")
        raise typer.Exit(1)
    
    if org.get("org_type") != "salesforce":
        console.print(f"[yellow]Warning:[/yellow] Org '{alias}' is not a Salesforce org")
        console.print("This command only works with Salesforce orgs")
        raise typer.Exit(1)
    
    sf_alias = org.get("sf_alias")
    
    # Get fresh token
    sf_info = _get_sf_org_info(sf_alias)
    if not sf_info:
        console.print(f"[red]Error:[/red] Could not get Salesforce org info")
        if sf_alias:
            console.print(f"SF Org: {sf_alias}")
        raise typer.Exit(1)
    
    # Update org config with fresh token
    config = _load_orgs()
    config["orgs"][alias]["api_key"] = sf_info.get("accessToken")
    config["orgs"][alias]["instance_url"] = sf_info.get("instanceUrl")
    _save_orgs(config)
    
    console.print(f"✅ Refreshed token for [cyan]{alias}[/cyan]")
    console.print(f"   SF Org: {sf_alias or '(default)'}")
    console.print(f"   Username: {sf_info.get('username')}")


@app.command("list")
def sf_list():
    """
    List available Salesforce orgs from sf CLI.
    
    Shows all Salesforce orgs you're connected to via the Salesforce CLI.
    """
    console.print("\n[bold blue]Salesforce Orgs[/bold blue]\n")
    
    orgs_data = _list_sf_orgs()
    if not orgs_data:
        console.print("[yellow]No Salesforce orgs found[/yellow]")
        console.print("Login to Salesforce: sf org login web")
        return
    
    from rich.table import Table
    
    table = Table()
    table.add_column("Alias", style="cyan")
    table.add_column("Username")
    table.add_column("Org ID")
    table.add_column("Status")
    
    # Add non-scratch orgs
    for org in orgs_data.get("nonScratchOrgs", []):
        table.add_row(
            org.get("alias") or "",
            org.get("username") or "",
            org.get("orgId") or "",
            "Active"
        )
    
    # Add scratch orgs
    for org in orgs_data.get("scratchOrgs", []):
        table.add_row(
            org.get("alias") or "",
            org.get("username") or "",
            org.get("orgId") or "",
            "Scratch Org"
        )
    
    console.print(table)
    console.print("\n[dim]Use 'fm sf connect --sf-org <alias>' to connect[/dim]")
