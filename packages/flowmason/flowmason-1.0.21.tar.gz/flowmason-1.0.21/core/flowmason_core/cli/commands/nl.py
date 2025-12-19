"""
Natural Language command for FlowMason CLI.

Trigger pipelines using natural language commands.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def run_natural(
    command: str = typer.Argument(
        ...,
        help="Natural language command (e.g., 'generate a sales report for yesterday')",
    ),
    project_dir: Optional[Path] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project directory (defaults to current directory)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show matched pipeline without executing",
    ),
    threshold: float = typer.Option(
        0.5,
        "--threshold",
        "-t",
        help="Minimum confidence threshold for matching (0.0-1.0)",
    ),
    use_llm: bool = typer.Option(
        False,
        "--llm",
        help="Use LLM for better accuracy (requires API key)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed matching information",
    ),
    extra_input: Optional[str] = typer.Option(
        None,
        "--input",
        "-i",
        help="Additional input as JSON (merged with extracted inputs)",
    ),
):
    """
    Run a pipeline using natural language.

    Examples:
        fm nl "generate a sales report for last week"
        fm nl "process the customer data from yesterday" --verbose
        fm nl "send daily summary to team@example.com" --dry-run
        fm nl "run the ETL pipeline" --threshold 0.7
    """
    console.print(f"\n[bold blue]FlowMason[/bold blue] Natural Language Trigger\n")
    console.print(f"[dim]Command:[/dim] \"{command}\"\n")

    # Find project directory
    project_path = project_dir or Path.cwd()

    # Find project root by looking for flowmason.json
    while project_path != project_path.parent:
        if (project_path / "flowmason.json").exists():
            break
        project_path = project_path.parent
    else:
        project_path = project_dir or Path.cwd()

    # Load pipelines from project
    pipelines = _load_project_pipelines(project_path)

    if not pipelines:
        console.print("[yellow]Warning:[/yellow] No pipelines found in project")
        console.print(f"[dim]Searched in: {project_path}[/dim]")
        raise typer.Exit(1)

    console.print(f"[dim]Found {len(pipelines)} pipeline(s) in project[/dim]\n")

    # Create NLP service
    from flowmason_core.nlp import NLPTriggerService

    llm_client = None
    if use_llm:
        llm_client = _get_llm_client()
        if not llm_client:
            console.print("[yellow]Warning:[/yellow] Could not initialize LLM client, using rule-based matching")
            use_llm = False

    service = NLPTriggerService(
        pipelines=pipelines,
        use_llm=use_llm,
        llm_client=llm_client,
    )

    # Parse the command
    result = service.parse_sync(command, threshold=threshold)

    # Display matching results
    if verbose:
        console.print(Panel(
            service.explain_match(result),
            title="Match Analysis",
            border_style="cyan",
        ))
        console.print()

    if not result.success:
        console.print(f"[red]Error:[/red] {result.error}")

        if result.alternatives:
            console.print("\n[yellow]Did you mean one of these?[/yellow]")
            for alt in result.alternatives[:3]:
                console.print(f"  - {alt.pipeline_name} ({alt.confidence:.0%})")

        raise typer.Exit(1)

    # Display matched pipeline
    match_table = Table(show_header=False, box=None, padding=(0, 2))
    match_table.add_column("Key", style="dim")
    match_table.add_column("Value")
    match_table.add_row("Pipeline", result.pipeline_name)
    match_table.add_row("Confidence", f"{result.confidence:.0%}")

    if result.intent:
        match_table.add_row("Intent", f"{result.intent.type.value} - {result.intent.action}")

    console.print(match_table)
    console.print()

    # Show extracted inputs
    if result.inputs:
        console.print("[bold]Extracted Inputs:[/bold]")
        for key, value in result.inputs.items():
            console.print(f"  {key}: {value}")
        console.print()

    # Merge extra input
    final_inputs = result.inputs.copy()
    if extra_input:
        try:
            extra = json.loads(extra_input)
            final_inputs.update(extra)
            console.print("[dim]Merged additional input[/dim]\n")
        except json.JSONDecodeError as e:
            console.print(f"[yellow]Warning:[/yellow] Invalid JSON in --input: {e}")

    if dry_run:
        console.print(Panel(
            f"[cyan]Dry run - would execute:[/cyan]\n\n"
            f"Pipeline: {result.pipeline_name}\n"
            f"Inputs: {json.dumps(final_inputs, indent=2)}",
            title="Dry Run",
            border_style="cyan",
        ))
        return

    # Execute the pipeline
    console.print("[bold]Executing pipeline...[/bold]\n")

    try:
        exec_result = asyncio.run(_execute_matched_pipeline(
            pipeline_name=result.pipeline_name,
            pipelines=pipelines,
            inputs=final_inputs,
            project_path=project_path,
            verbose=verbose,
        ))

        # Display results
        if exec_result.get("status") == "success":
            console.print(Panel(
                f"[green]Pipeline completed successfully[/green]\n\n"
                f"Duration: {exec_result.get('duration_ms', 0)}ms\n"
                f"Stages executed: {exec_result.get('stages_completed', 0)}",
                title="Result",
                border_style="green",
            ))

            if verbose and exec_result.get("output"):
                console.print("\n[bold]Output:[/bold]")
                console.print_json(data=exec_result["output"])
        else:
            console.print(Panel(
                f"[red]Pipeline failed[/red]\n\n"
                f"Error: {exec_result.get('error', 'Unknown error')}",
                title="Error",
                border_style="red",
            ))
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1)


def suggest_pipelines(
    query: str = typer.Argument(
        ...,
        help="Partial command or query for suggestions",
    ),
    project_dir: Optional[Path] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project directory",
    ),
    max_suggestions: int = typer.Option(
        5,
        "--max",
        "-m",
        help="Maximum suggestions to show",
    ),
):
    """
    Get pipeline suggestions based on a query.

    Useful for autocomplete or exploring available pipelines.

    Examples:
        fm nl-suggest "sales"
        fm nl-suggest "generate report" --max 3
    """
    console.print(f"\n[bold blue]FlowMason[/bold blue] Pipeline Suggestions\n")

    # Find project directory
    project_path = project_dir or Path.cwd()
    while project_path != project_path.parent:
        if (project_path / "flowmason.json").exists():
            break
        project_path = project_path.parent
    else:
        project_path = project_dir or Path.cwd()

    pipelines = _load_project_pipelines(project_path)

    if not pipelines:
        console.print("[yellow]No pipelines found[/yellow]")
        raise typer.Exit(1)

    from flowmason_core.nlp import NLPTriggerService

    service = NLPTriggerService(pipelines=pipelines)
    suggestions = service.suggest_pipelines(query, max_suggestions=max_suggestions)

    if not suggestions:
        console.print("[dim]No matching pipelines found[/dim]")
        return

    table = Table(title=f"Suggestions for: \"{query}\"")
    table.add_column("Pipeline", style="cyan")
    table.add_column("Confidence", justify="right")
    table.add_column("Description")

    for s in suggestions:
        table.add_row(
            s["name"],
            f"{s['confidence']:.0%}",
            s.get("description", "")[:50] + "..." if len(s.get("description", "")) > 50 else s.get("description", ""),
        )

    console.print(table)


def _load_project_pipelines(project_path: Path) -> Dict[str, Any]:
    """Load all pipelines from a project directory."""
    pipelines: Dict[str, Any] = {}

    # Look for pipeline files
    pipeline_patterns = [
        "*.pipeline.json",
        "pipelines/*.pipeline.json",
        "**/*.pipeline.json",
    ]

    pipeline_files = []
    for pattern in pipeline_patterns:
        pipeline_files.extend(project_path.glob(pattern))

    # Remove duplicates
    pipeline_files = list(set(pipeline_files))

    for pf in pipeline_files:
        try:
            data = json.loads(pf.read_text())
            name = data.get("name", pf.stem.replace(".pipeline", ""))
            pipelines[name] = data
        except Exception:
            continue

    return pipelines


def _get_llm_client() -> Optional[Any]:
    """Get LLM client for enhanced matching."""
    import os

    # Try Anthropic first
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            return anthropic.Anthropic(api_key=api_key)
        except ImportError:
            pass

    # Try OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            return openai.OpenAI(api_key=api_key)
        except ImportError:
            pass

    return None


async def _execute_matched_pipeline(
    pipeline_name: str,
    pipelines: Dict[str, Any],
    inputs: Dict[str, Any],
    project_path: Path,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Execute a matched pipeline."""
    from datetime import datetime
    from pathlib import Path as P

    from flowmason_core.config import ComponentConfig, ExecutionContext
    from flowmason_core.execution.universal_executor import DAGExecutor
    from flowmason_core.registry import ComponentRegistry

    pipeline_data = pipelines.get(pipeline_name)
    if not pipeline_data:
        return {
            "status": "error",
            "error": f"Pipeline '{pipeline_name}' not found",
        }

    start_time = datetime.utcnow()

    # Create registry
    registry = ComponentRegistry()
    registry.auto_discover()

    # Load providers
    providers: Dict[str, Any] = {}
    default_provider: Optional[str] = None

    try:
        import os
        from flowmason_core.providers import AnthropicProvider, OpenAIProvider

        manifest_path = project_path / "flowmason.json"
        if manifest_path.exists():
            manifest_data = json.loads(manifest_path.read_text())
            prov_config = manifest_data.get("providers", {})

            if prov_config:
                default_provider = prov_config.get("default")

                for prov_name, prov_settings in prov_config.items():
                    if prov_name == "default":
                        continue

                    if prov_name == "anthropic":
                        api_key = os.environ.get("ANTHROPIC_API_KEY")
                        if api_key:
                            model = prov_settings.get("model", "claude-sonnet-4-20250514") if isinstance(prov_settings, dict) else "claude-sonnet-4-20250514"
                            providers["anthropic"] = AnthropicProvider(api_key=api_key, model=model)
                            if not default_provider:
                                default_provider = "anthropic"

                    elif prov_name == "openai":
                        api_key = os.environ.get("OPENAI_API_KEY")
                        if api_key:
                            model = prov_settings.get("model", "gpt-4o") if isinstance(prov_settings, dict) else "gpt-4o"
                            providers["openai"] = OpenAIProvider(api_key=api_key, model=model)
                            if not default_provider:
                                default_provider = "openai"
    except Exception as e:
        if verbose:
            console.print(f"[dim]Warning: Could not load providers: {e}[/dim]")

    # Create execution context
    context = ExecutionContext(
        pipeline_id=pipeline_name,
        pipeline_version=pipeline_data.get("version", "1.0.0"),
        run_id=f"nl-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        trace_id=f"trace-{datetime.utcnow().timestamp()}",
    )

    # Convert stages to ComponentConfig
    stages = []
    for stage in pipeline_data.get("stages", []):
        component_type = stage.get("component_type") or stage.get("component", "unknown")
        stages.append(ComponentConfig(
            id=stage.get("id", ""),
            type=component_type,
            depends_on=stage.get("depends_on", []),
            input_mapping=stage.get("config", {}),
        ))

    # Create executor
    executor = DAGExecutor(
        registry=registry,
        context=context,
        parallel_execution=True,
        providers=providers if providers else None,
        default_provider=default_provider,
    )

    # Execute
    try:
        results = await executor.execute(stages, inputs)

        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Get final output
        final_output = None
        if results:
            output_stage_id = pipeline_data.get("output_stage_id") or list(results.keys())[-1]
            if output_stage_id in results:
                final_output = results[output_stage_id].output
            else:
                final_output = results[list(results.keys())[-1]].output

        return {
            "status": "success",
            "duration_ms": duration_ms,
            "stages_completed": len(results),
            "output": final_output,
        }

    except Exception as e:
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return {
            "status": "error",
            "error": str(e),
            "duration_ms": duration_ms,
        }
