"""
Pull command for FlowMason CLI.

Pull pipelines and components from an org to local files.
"""

import json
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def pull(
    pipeline: Optional[str] = typer.Option(
        None,
        "--pipeline",
        "-p",
        help="Name of specific pipeline to pull",
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target org alias (default: default org)",
    ),
    output_dir: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for pipeline files (default: ./pipelines)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview what would be pulled without making changes",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing local files",
    ),
):
    """
    Pull pipelines from an org to local files.

    Similar to 'sf project retrieve' in Salesforce DX.

    Examples:
        flowmason pull                           # Pull all from default org
        flowmason pull --pipeline main           # Pull specific pipeline
        flowmason pull --target production       # Pull from specific org
        flowmason pull --output ./my-pipelines   # Pull to custom directory
        flowmason pull --dry-run                 # Preview what would be pulled
    """
    from flowmason_core.cli.commands.org import get_default_org, get_org, update_last_used

    console.print("\n[bold blue]FlowMason[/bold blue] Pull\n")

    # Get org configuration
    if target:
        org = get_org(target)
        if not org:
            console.print(f"[red]Error:[/red] Org '{target}' not found")
            console.print("Use 'flowmason org list' to see available orgs")
            raise typer.Exit(1)
    else:
        org = get_default_org()
        if not org:
            console.print("[red]Error:[/red] No default org set")
            console.print("Use 'flowmason org default <alias>' to set a default org")
            console.print("Or use --target to specify an org")
            raise typer.Exit(1)

    target_name = org["alias"]
    target_url = org["instance_url"]

    console.print(f"Source: [cyan]{target_name}[/cyan] ({target_url})")

    # Determine output directory
    if not output_dir:
        output_dir = Path.cwd() / "pipelines"
    output_dir = output_dir.resolve()

    console.print(f"Output: {output_dir}\n")

    # Fetch pipelines from org
    pipelines = _fetch_pipelines(org, pipeline)

    if not pipelines:
        console.print("[yellow]No pipelines found in org[/yellow]")
        raise typer.Exit(0)

    # Display what will be pulled
    table = Table(title="Pipelines to Pull")
    table.add_column("Name", style="cyan")
    table.add_column("Version")
    table.add_column("Stages")
    table.add_column("Status")

    for p in pipelines:
        local_path = output_dir / f"{_sanitize_filename(p['name'])}.pipeline.json"
        status = "[yellow]Overwrite[/yellow]" if local_path.exists() else "[green]New[/green]"
        if local_path.exists() and not force and not dry_run:
            status = "[dim]Skip (exists)[/dim]"

        table.add_row(
            p["name"],
            p.get("version", "1.0.0"),
            str(len(p.get("stages", []))),
            status,
        )

    console.print(table)
    console.print()

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] No changes made")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write pipeline files
    pulled_count = 0
    skipped_count = 0

    for p in pipelines:
        local_path = output_dir / f"{_sanitize_filename(p['name'])}.pipeline.json"

        if local_path.exists() and not force:
            console.print(f"[yellow]Skip:[/yellow] {p['name']} (file exists, use --force to overwrite)")
            skipped_count += 1
            continue

        # Convert to file format
        file_content = _convert_to_file_format(p)
        local_path.write_text(json.dumps(file_content, indent=2))
        console.print(f"[green]Pulled:[/green] {p['name']} -> {local_path.name}")
        pulled_count += 1

    update_last_used(target_name)

    console.print(Panel(
        f"[green]Pull complete![/green]\n\n"
        f"Source: {target_name}\n"
        f"Pulled: {pulled_count}\n"
        f"Skipped: {skipped_count}",
        title="FlowMason Pull",
        border_style="green",
    ))


def _fetch_pipelines(org: dict, pipeline_name: Optional[str]) -> List[dict]:
    """Fetch pipelines from remote org via API."""
    import httpx

    base_url = org["instance_url"]
    headers = {}
    if org.get("api_key"):
        headers["Authorization"] = f"Bearer {org['api_key']}"

    try:
        if pipeline_name:
            # Fetch specific pipeline
            response = httpx.get(
                f"{base_url}/api/v1/pipelines/by-name/{pipeline_name}",
                headers=headers,
                timeout=30,
            )
            if response.status_code == 200:
                return [response.json()]
            elif response.status_code == 404:
                console.print(f"[yellow]Warning:[/yellow] Pipeline '{pipeline_name}' not found in org")
                return []
            else:
                console.print(f"[red]Error:[/red] Failed to fetch pipeline: {response.status_code}")
                return []
        else:
            # Fetch all pipelines
            response = httpx.get(
                f"{base_url}/api/v1/pipelines",
                headers=headers,
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                # Handle both list and paginated response
                if isinstance(data, list):
                    return list(data)
                result = data.get("items", data.get("pipelines", []))
                return list(result) if isinstance(result, list) else []
            else:
                console.print(f"[red]Error:[/red] Failed to fetch pipelines: {response.status_code}")
                return []

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to connect to org: {e}")
        return []


def _convert_to_file_format(pipeline_data: dict) -> dict:
    """Convert API pipeline format to file format."""
    # Extract stages from config if nested
    stages = pipeline_data.get("stages", [])
    if not stages and "config" in pipeline_data:
        config = pipeline_data["config"]
        if isinstance(config, str):
            config = json.loads(config)
        stages = config.get("stages", [])

    # Convert stages to file format
    file_stages = []
    for stage in stages:
        file_stage = {
            "id": stage.get("id"),
            "component": stage.get("component_type") or stage.get("component"),
        }
        if stage.get("name"):
            file_stage["name"] = stage["name"]
        if stage.get("config"):
            file_stage["config"] = stage["config"]
        if stage.get("depends_on"):
            file_stage["depends_on"] = stage["depends_on"]
        if stage.get("position"):
            file_stage["position"] = stage["position"]
        if stage.get("llm_settings"):
            file_stage["llm_settings"] = stage["llm_settings"]
        if stage.get("timeout_ms"):
            file_stage["timeout_ms"] = stage["timeout_ms"]

        file_stages.append(file_stage)

    # Build file format
    file_format = {
        "$schema": "https://flowmason.dev/schemas/pipeline.schema.json",
        "name": pipeline_data.get("name"),
        "version": pipeline_data.get("version", "1.0.0"),
        "description": pipeline_data.get("description", ""),
    }

    # Add schemas
    input_schema = pipeline_data.get("input_schema", {})
    if isinstance(input_schema, str):
        input_schema = json.loads(input_schema)
    file_format["input_schema"] = input_schema or {"type": "object", "properties": {}}

    output_schema = pipeline_data.get("output_schema", {})
    if isinstance(output_schema, str):
        output_schema = json.loads(output_schema)
    file_format["output_schema"] = output_schema or {"type": "object", "properties": {}}

    file_format["stages"] = file_stages

    if pipeline_data.get("output_stage_id"):
        file_format["output_stage_id"] = pipeline_data["output_stage_id"]

    if pipeline_data.get("category"):
        file_format["category"] = pipeline_data["category"]

    tags = pipeline_data.get("tags", [])
    if isinstance(tags, str):
        tags = json.loads(tags)
    if tags:
        file_format["tags"] = tags

    if pipeline_data.get("sample_input"):
        sample_input = pipeline_data["sample_input"]
        if isinstance(sample_input, str):
            sample_input = json.loads(sample_input)
        file_format["sample_input"] = sample_input

    return file_format


def _sanitize_filename(name: str) -> str:
    """Sanitize pipeline name for use as filename."""
    # Replace spaces and special chars with hyphens
    import re
    sanitized = re.sub(r'[^\w\-]', '-', name.lower())
    sanitized = re.sub(r'-+', '-', sanitized)  # Collapse multiple hyphens
    return sanitized.strip('-')
