"""
Deploy command for FlowMason CLI.

Deploy pipelines and components from local files to an org.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def deploy(
    path: Optional[Path] = typer.Argument(
        None,
        help="Path to pipeline file or directory (default: all pipelines in project)",
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target org alias (default: default org)",
    ),
    local: bool = typer.Option(
        False,
        "--local",
        "-l",
        help="Deploy to local SQLite database",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview what would be deployed without making changes",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing pipelines",
    ),
):
    """
    Deploy pipelines from local files to an org.

    Similar to 'sf project deploy' in Salesforce DX.

    Examples:
        flowmason deploy                              # Deploy all to default org
        flowmason deploy pipelines/main.pipeline.json # Deploy specific pipeline
        flowmason deploy --target production          # Deploy to specific org
        flowmason deploy --local                      # Deploy to local SQLite
        flowmason deploy --dry-run                    # Preview deployment
    """
    from flowmason_core.cli.commands.org import get_default_org, get_org, update_last_used
    from flowmason_core.project.loader import ProjectLoader, discover_pipelines, load_pipeline_file

    console.print("\n[bold blue]FlowMason[/bold blue] Deploy\n")

    # Determine target
    if local:
        target_name = "local"
        target_url = "Local SQLite Database"
    else:
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
                console.print("Or use --local to deploy to local database")
                raise typer.Exit(1)
        target_name = org["alias"]
        target_url = org["instance_url"]

    console.print(f"Target: [cyan]{target_name}[/cyan] ({target_url})")

    # Collect pipelines to deploy
    pipelines_to_deploy: List[Path] = []

    if path:
        path = Path(path).resolve()
        if path.is_file():
            pipelines_to_deploy.append(path)
        elif path.is_dir():
            pipelines_to_deploy.extend(discover_pipelines(path))
        else:
            console.print(f"[red]Error:[/red] Path not found: {path}")
            raise typer.Exit(1)
    else:
        # Try to load from project
        project_loader = ProjectLoader(Path.cwd())
        if project_loader.has_manifest:
            pipelines_to_deploy.extend(project_loader.discover_pipelines())
        else:
            # Look for pipelines directory
            pipelines_dir = Path.cwd() / "pipelines"
            if pipelines_dir.is_dir():
                pipelines_to_deploy.extend(discover_pipelines(pipelines_dir))
            else:
                console.print("[yellow]Warning:[/yellow] No pipelines found")
                console.print("Specify a path or run from a FlowMason project directory")
                raise typer.Exit(1)

    if not pipelines_to_deploy:
        console.print("[yellow]Warning:[/yellow] No pipelines found to deploy")
        raise typer.Exit(0)

    console.print(f"Found {len(pipelines_to_deploy)} pipeline(s) to deploy\n")

    # Validate and prepare pipelines
    deploy_items: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for pipeline_path in pipelines_to_deploy:
        try:
            pipeline = load_pipeline_file(pipeline_path)
            deploy_items.append({
                "path": pipeline_path,
                "pipeline": pipeline,
                "name": pipeline.name,
                "version": pipeline.version,
            })
        except Exception as e:
            errors.append({
                "path": pipeline_path,
                "error": str(e),
            })

    # Show validation errors
    if errors:
        console.print("[red]Validation errors:[/red]")
        for error in errors:
            console.print(f"  {error['path'].name}: {error['error']}")
        console.print()

    if not deploy_items:
        console.print("[red]Error:[/red] No valid pipelines to deploy")
        raise typer.Exit(1)

    # Display what will be deployed
    table = Table(title="Pipelines to Deploy")
    table.add_column("Name", style="cyan")
    table.add_column("Version")
    table.add_column("Stages")
    table.add_column("File")

    for item in deploy_items:
        table.add_row(
            item["name"],
            item["version"],
            str(len(item["pipeline"].stages)),
            item["path"].name,
        )

    console.print(table)
    console.print()

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] No changes made")
        return

    # Deploy to target
    if local:
        _deploy_local(deploy_items, force)
    else:
        if not org:
            console.print("[red]Error:[/red] No org configuration found")
            raise typer.Exit(1)
        _deploy_remote(deploy_items, org, force)
        update_last_used(target_name)

    console.print(Panel(
        f"[green]Deployment complete![/green]\n\n"
        f"Target: {target_name}\n"
        f"Pipelines deployed: {len(deploy_items)}",
        title="FlowMason Deploy",
        border_style="green",
    ))


def _deploy_local(deploy_items: List[dict], force: bool):
    """Deploy pipelines to local SQLite database."""
    try:
        from flowmason_studio.db.connection import get_session
        from flowmason_studio.db.models import Pipeline, json_serialize
        from sqlalchemy import select
    except ImportError:
        console.print("[red]Error:[/red] flowmason-studio not installed")
        console.print("Install with: pip install flowmason-studio")
        raise typer.Exit(1)

    with get_session() as session:
        for item in deploy_items:
            pipeline = item["pipeline"]

            # Check if pipeline exists
            existing = session.execute(
                select(Pipeline).where(Pipeline.name == pipeline.name)
            ).scalar_one_or_none()

            if existing and not force:
                console.print(f"[yellow]Skip:[/yellow] {pipeline.name} already exists (use --force to overwrite)")
                continue

            # Prepare pipeline data
            stages_data = [
                {
                    "id": s.id,
                    "component_type": s.get_component_type(),
                    "name": s.name,
                    "config": s.config,
                    "input_mapping": s.input_mapping,
                    "depends_on": s.depends_on,
                    "position": s.position.model_dump() if s.position else None,
                    "llm_settings": s.llm_settings.model_dump() if s.llm_settings else None,
                    "timeout_ms": s.timeout_ms,
                }
                for s in pipeline.stages
            ]

            if existing:
                # Update existing
                existing.name = pipeline.name  # type: ignore[assignment]
                existing.description = pipeline.description  # type: ignore[assignment]
                existing.version = pipeline.version  # type: ignore[assignment]
                existing.config = json_serialize({"stages": stages_data})  # type: ignore[assignment]
                existing.input_schema = json_serialize(pipeline.input_schema.model_dump())  # type: ignore[assignment]
                existing.output_schema = json_serialize(pipeline.output_schema.model_dump())  # type: ignore[assignment]
                existing.output_stage_id = pipeline.output_stage_id  # type: ignore[assignment]
                existing.category = pipeline.category  # type: ignore[assignment]
                existing.tags = json_serialize(pipeline.tags)  # type: ignore[assignment]
                console.print(f"[green]Updated:[/green] {pipeline.name}")
            else:
                # Create new
                import uuid
                db_pipeline = Pipeline(
                    id=str(uuid.uuid4()),
                    name=pipeline.name,
                    description=pipeline.description,
                    version=pipeline.version,
                    config=json_serialize({"stages": stages_data}),
                    input_schema=json_serialize(pipeline.input_schema.model_dump()),
                    output_schema=json_serialize(pipeline.output_schema.model_dump()),
                    output_stage_id=pipeline.output_stage_id,
                    category=pipeline.category,
                    tags=json_serialize(pipeline.tags),
                )
                session.add(db_pipeline)
                console.print(f"[green]Created:[/green] {pipeline.name}")

        session.commit()


def _deploy_remote(deploy_items: List[dict], org: dict, force: bool):
    """Deploy pipelines to remote org via API."""
    import httpx

    base_url = org["instance_url"]
    headers = {}
    if org.get("api_key"):
        headers["Authorization"] = f"Bearer {org['api_key']}"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for item in deploy_items:
            pipeline = item["pipeline"]
            task = progress.add_task(f"Deploying {pipeline.name}...", total=None)

            try:
                # Prepare pipeline data for API
                stages_data = [
                    {
                        "id": s.id,
                        "component_type": s.get_component_type(),
                        "name": s.name,
                        "config": s.config,
                        "input_mapping": s.input_mapping,
                        "depends_on": s.depends_on,
                        "position": s.position.model_dump() if s.position else None,
                        "llm_settings": s.llm_settings.model_dump() if s.llm_settings else None,
                        "timeout_ms": s.timeout_ms,
                    }
                    for s in pipeline.stages
                ]

                payload = {
                    "name": pipeline.name,
                    "description": pipeline.description,
                    "version": pipeline.version,
                    "input_schema": pipeline.input_schema.model_dump(),
                    "output_schema": pipeline.output_schema.model_dump(),
                    "stages": stages_data,
                    "output_stage_id": pipeline.output_stage_id,
                    "category": pipeline.category,
                    "tags": pipeline.tags,
                    "sample_input": pipeline.sample_input,
                }

                # Check if pipeline exists
                response = httpx.get(
                    f"{base_url}/api/v1/pipelines/by-name/{pipeline.name}",
                    headers=headers,
                    timeout=30,
                )

                if response.status_code == 200:
                    if not force:
                        progress.update(task, description=f"[yellow]Skip:[/yellow] {pipeline.name} exists")
                        continue
                    # Update existing
                    existing = response.json()
                    response = httpx.put(
                        f"{base_url}/api/v1/pipelines/{existing['id']}",
                        json=payload,
                        headers=headers,
                        timeout=30,
                    )
                else:
                    # Create new
                    response = httpx.post(
                        f"{base_url}/api/v1/pipelines",
                        json=payload,
                        headers=headers,
                        timeout=30,
                    )

                if response.status_code in (200, 201):
                    progress.update(task, description=f"[green]Deployed:[/green] {pipeline.name}")
                else:
                    progress.update(task, description=f"[red]Failed:[/red] {pipeline.name} ({response.status_code})")

            except Exception as e:
                progress.update(task, description=f"[red]Error:[/red] {pipeline.name}: {e}")
