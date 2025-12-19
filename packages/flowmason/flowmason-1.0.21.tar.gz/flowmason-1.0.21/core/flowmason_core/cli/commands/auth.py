"""
Auth commands for FlowMason CLI.

Manage authentication: bootstrap, API keys, whoami.
"""

from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .org import get_default_org, get_org, update_last_used

app = typer.Typer(
    help="Manage FlowMason authentication",
    no_args_is_help=True,
)

console = Console()


def _get_client(org_alias: Optional[str] = None):
    """Get HTTP client for the specified or default org."""
    import httpx

    if org_alias:
        org = get_org(org_alias)
    else:
        org = get_default_org()

    if not org:
        console.print("[red]Error:[/red] No org specified and no default org set")
        console.print("Use 'fm org login' to connect to an org first")
        raise typer.Exit(1)

    headers = {}
    if org.get("api_key"):
        headers["Authorization"] = f"Bearer {org['api_key']}"

    client = httpx.Client(
        base_url=org["instance_url"],
        headers=headers,
        timeout=30,
    )

    return client, org


@app.command("bootstrap")
def bootstrap(
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target org alias (uses default if not specified)",
    ),
    org_name: str = typer.Option(
        "Default Organization",
        "--org-name",
        help="Name for the new organization",
    ),
    org_slug: str = typer.Option(
        "default",
        "--org-slug",
        help="URL-friendly slug for the organization",
    ),
    user_email: str = typer.Option(
        "admin@flowmason.local",
        "--email",
        help="Admin user email",
    ),
    user_name: str = typer.Option(
        "Admin",
        "--name",
        help="Admin user name",
    ),
):
    """
    Bootstrap a new FlowMason instance.

    Creates an organization, admin user, and initial API key.
    Run this once when setting up a new FlowMason server.

    Examples:
        fm auth bootstrap --target local
        fm auth bootstrap --org-name "My Company" --org-slug my-company
    """
    console.print("\n[bold blue]FlowMason[/bold blue] Bootstrap\n")

    client, org = _get_client(target)

    console.print(f"Bootstrapping {org['instance_url']}...")

    try:
        response = client.post(
            "/api/v1/auth/bootstrap",
            params={
                "org_name": org_name,
                "org_slug": org_slug,
                "user_email": user_email,
                "user_name": user_name,
            },
        )

        if response.status_code == 200:
            data = response.json()

            # Display success
            console.print(Panel(
                f"[green]Bootstrap successful![/green]\n\n"
                f"[bold]Organization:[/bold]\n"
                f"  ID: {data['org']['id']}\n"
                f"  Name: {data['org']['name']}\n"
                f"  Slug: {data['org']['slug']}\n\n"
                f"[bold]Admin User:[/bold]\n"
                f"  ID: {data['user']['id']}\n"
                f"  Email: {data['user']['email']}\n"
                f"  Name: {data['user']['name']}\n\n"
                f"[bold]API Key:[/bold]\n"
                f"  ID: {data['api_key']['id']}\n"
                f"  Name: {data['api_key']['name']}\n"
                f"  [yellow]Key: {data['api_key']['key']}[/yellow]\n\n"
                f"[red bold]IMPORTANT:[/red bold] Save the API key now!\n"
                f"It will not be shown again.",
                title="FlowMason Bootstrap",
                border_style="green",
            ))

            # Offer to save the key
            save_key = typer.confirm("\nSave API key to org configuration?")
            if save_key:
                from .org import _load_orgs, _save_orgs
                config = _load_orgs()
                alias = org.get("alias") or target or config.get("default")
                if alias and alias in config["orgs"]:
                    config["orgs"][alias]["api_key"] = data["api_key"]["key"]
                    _save_orgs(config)
                    console.print(f"[green]API key saved to org '{alias}'[/green]")

        elif response.status_code == 400:
            error = response.json().get("detail", "Unknown error")
            console.print(f"[yellow]Already bootstrapped:[/yellow] {error}")
            raise typer.Exit(0)
        else:
            console.print(f"[red]Error ({response.status_code}):[/red] {response.text}")
            raise typer.Exit(1)

    except Exception as e:
        if "Connection refused" in str(e):
            console.print(f"[red]Error:[/red] Could not connect to {org['instance_url']}")
            console.print("Make sure the FlowMason server is running.")
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    finally:
        client.close()


@app.command("whoami")
def whoami(
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target org alias (uses default if not specified)",
    ),
):
    """
    Display current authentication info.

    Shows the organization, user, and API key associated with
    the current credentials.

    Examples:
        fm auth whoami
        fm auth whoami --target production
    """
    console.print("\n[bold blue]FlowMason[/bold blue] Authentication Info\n")

    client, org = _get_client(target)
    update_last_used(org.get("alias", target))

    try:
        response = client.get("/api/v1/auth/whoami")

        if response.status_code == 200:
            data = response.json()

            # Organization info
            org_info = data.get("org", {})
            console.print(f"[bold]Organization:[/bold] {org_info.get('name')}")
            console.print(f"  ID: {org_info.get('id')}")
            console.print(f"  Slug: {org_info.get('slug')}")
            console.print(f"  Plan: {org_info.get('plan')}")

            # User info (if any)
            user_info = data.get("user")
            if user_info:
                console.print(f"\n[bold]User:[/bold] {user_info.get('name')}")
                console.print(f"  Email: {user_info.get('email')}")

            # API key info
            key_info = data.get("api_key")
            if key_info:
                console.print(f"\n[bold]API Key:[/bold] {key_info.get('name')}")
                console.print(f"  Prefix: {key_info.get('key_prefix')}...")
                console.print(f"  Scopes: {', '.join(data.get('scopes', []))}")

        elif response.status_code == 401:
            console.print("[red]Error:[/red] Invalid or missing API key")
            console.print("Use 'fm auth bootstrap' to create credentials, or")
            console.print("'fm org login --api-key <key>' to configure an existing key")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Error ({response.status_code}):[/red] {response.text}")
            raise typer.Exit(1)

    except Exception as e:
        if "Connection refused" in str(e):
            console.print(f"[red]Error:[/red] Could not connect to {org['instance_url']}")
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    finally:
        client.close()


# API Key subcommands
api_key_app = typer.Typer(
    help="Manage API keys",
    no_args_is_help=True,
)
app.add_typer(api_key_app, name="api-key")


@api_key_app.command("create")
def api_key_create(
    name: str = typer.Argument(
        ...,
        help="Name for the API key",
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target org alias",
    ),
    scopes: str = typer.Option(
        "full",
        "--scopes",
        "-s",
        help="Comma-separated scopes: full, read, execute, deploy",
    ),
):
    """
    Create a new API key.

    Examples:
        fm auth api-key create "CI/CD Key"
        fm auth api-key create "Read-Only Key" --scopes read
        fm auth api-key create "Deploy Key" --scopes deploy,execute
    """
    console.print("\n[bold blue]FlowMason[/bold blue] Create API Key\n")

    client, org = _get_client(target)

    scope_list = [s.strip() for s in scopes.split(",")]

    try:
        response = client.post(
            "/api/v1/auth/api-keys",
            json={
                "name": name,
                "scopes": scope_list,
            },
        )

        if response.status_code == 200:
            data = response.json()
            key_info = data.get("api_key", {})
            raw_key = data.get("raw_key")

            console.print(Panel(
                f"[green]API key created![/green]\n\n"
                f"[bold]Name:[/bold] {key_info.get('name')}\n"
                f"[bold]ID:[/bold] {key_info.get('id')}\n"
                f"[bold]Scopes:[/bold] {', '.join(key_info.get('scopes', []))}\n\n"
                f"[yellow bold]Key: {raw_key}[/yellow bold]\n\n"
                f"[red]IMPORTANT:[/red] Copy this key now!\n"
                f"It will not be shown again.",
                title="New API Key",
                border_style="green",
            ))

        elif response.status_code == 401:
            console.print("[red]Error:[/red] Authentication required")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Error ({response.status_code}):[/red] {response.text}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    finally:
        client.close()


@api_key_app.command("list")
def api_key_list(
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target org alias",
    ),
):
    """
    List all API keys for the organization.

    Examples:
        fm auth api-key list
        fm auth api-key list --target production
    """
    console.print("\n[bold blue]FlowMason[/bold blue] API Keys\n")

    client, org = _get_client(target)

    try:
        response = client.get("/api/v1/auth/api-keys")

        if response.status_code == 200:
            keys = response.json()

            if not keys:
                console.print("[yellow]No API keys found.[/yellow]")
                return

            table = Table(title=f"API Keys ({org.get('alias', 'default')})")
            table.add_column("Name", style="cyan")
            table.add_column("Prefix")
            table.add_column("Scopes")
            table.add_column("Active")
            table.add_column("Last Used")

            for key in keys:
                active = "[green]Yes[/green]" if key.get("is_active") else "[red]No[/red]"
                last_used = key.get("last_used_at", "Never")
                if last_used and last_used != "Never":
                    # Format nicely
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(last_used.replace("Z", "+00:00"))
                        last_used = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        pass

                table.add_row(
                    key.get("name"),
                    key.get("key_prefix") + "...",
                    ", ".join(key.get("scopes", [])),
                    active,
                    last_used or "Never",
                )

            console.print(table)

        elif response.status_code == 401:
            console.print("[red]Error:[/red] Authentication required")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Error ({response.status_code}):[/red] {response.text}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    finally:
        client.close()


@api_key_app.command("revoke")
def api_key_revoke(
    key_id: str = typer.Argument(
        ...,
        help="ID of the API key to revoke",
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target org alias",
    ),
    reason: str = typer.Option(
        "Manually revoked via CLI",
        "--reason",
        "-r",
        help="Reason for revocation",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation",
    ),
):
    """
    Revoke an API key.

    Examples:
        fm auth api-key revoke key_abc123
        fm auth api-key revoke key_abc123 --reason "Compromised"
    """
    if not force:
        confirm = typer.confirm(f"Are you sure you want to revoke key {key_id}?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    console.print("\n[bold blue]FlowMason[/bold blue] Revoke API Key\n")

    client, org = _get_client(target)

    try:
        response = client.delete(
            f"/api/v1/auth/api-keys/{key_id}",
            params={"reason": reason},
        )

        if response.status_code == 200:
            console.print(f"[green]API key {key_id} has been revoked.[/green]")

        elif response.status_code == 404:
            console.print(f"[red]Error:[/red] API key not found: {key_id}")
            raise typer.Exit(1)
        elif response.status_code == 401:
            console.print("[red]Error:[/red] Authentication required")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Error ({response.status_code}):[/red] {response.text}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    finally:
        client.close()


@app.command("audit-log")
def audit_log(
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target org alias",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-l",
        help="Number of entries to show",
    ),
    action: Optional[str] = typer.Option(
        None,
        "--action",
        "-a",
        help="Filter by action (e.g., pipeline.create)",
    ),
):
    """
    View audit log entries.

    Examples:
        fm auth audit-log
        fm auth audit-log --limit 50
        fm auth audit-log --action pipeline.create
    """
    console.print("\n[bold blue]FlowMason[/bold blue] Audit Log\n")

    client, org = _get_client(target)

    try:
        params: Dict[str, Any] = {"limit": limit}
        if action:
            params["action"] = action

        response = client.get("/api/v1/auth/audit-log", params=params)

        if response.status_code == 200:
            entries = response.json()

            if not entries:
                console.print("[yellow]No audit log entries found.[/yellow]")
                return

            table = Table(title=f"Audit Log ({org.get('alias', 'default')})")
            table.add_column("Timestamp", style="dim")
            table.add_column("Action", style="cyan")
            table.add_column("Resource")
            table.add_column("Status")

            for entry in entries:
                timestamp = entry.get("timestamp", "")
                if timestamp:
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass

                status = "[green]OK[/green]" if entry.get("success") else "[red]FAIL[/red]"
                resource = f"{entry.get('resource_type', '')}"
                if entry.get("resource_id"):
                    resource += f" ({entry.get('resource_id')[:12]}...)"

                table.add_row(
                    timestamp,
                    entry.get("action", ""),
                    resource,
                    status,
                )

            console.print(table)

        elif response.status_code == 401:
            console.print("[red]Error:[/red] Authentication required")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Error ({response.status_code}):[/red] {response.text}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    finally:
        client.close()
