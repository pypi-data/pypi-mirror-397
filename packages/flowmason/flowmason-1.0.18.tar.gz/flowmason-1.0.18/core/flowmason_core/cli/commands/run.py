"""
Run command for FlowMason CLI.

Execute pipelines from file or from an org.
"""

import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

import typer

if TYPE_CHECKING:
    from flowmason_core.project.loader import PipelineFile
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def run_pipeline(
    pipeline_path: Path = typer.Argument(
        ...,
        help="Path to pipeline file (.pipeline.json)",
        exists=True,
        readable=True,
    ),
    input_data: Optional[str] = typer.Option(
        None,
        "--input",
        "-i",
        help="Input data as JSON string",
    ),
    input_file: Optional[Path] = typer.Option(
        None,
        "--input-file",
        "-f",
        help="Path to input JSON file",
        exists=True,
        readable=True,
    ),
    use_sample: bool = typer.Option(
        False,
        "--sample",
        "-s",
        help="Use sample_input from pipeline file",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug mode (starts debug server)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
    timeout: Optional[int] = typer.Option(
        None,
        "--timeout",
        "-t",
        help="Execution timeout in seconds",
    ),
):
    """
    Run a pipeline from a file.

    Examples:
        flowmason run pipelines/main.pipeline.json
        flowmason run pipelines/main.pipeline.json --input '{"url": "https://..."}'
        flowmason run pipelines/main.pipeline.json --input-file test-input.json
        flowmason run pipelines/main.pipeline.json --sample
        flowmason run pipelines/main.pipeline.json --debug
    """
    # Load pipeline using the project loader
    from flowmason_core.project.loader import load_pipeline_file

    console.print(f"\n[bold blue]FlowMason[/bold blue] Running pipeline: {pipeline_path}\n")

    try:
        pipeline = load_pipeline_file(pipeline_path)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid pipeline JSON: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load pipeline: {e}")
        raise typer.Exit(1)

    # Determine input data (priority: --input > --input-file > --sample > empty)
    pipeline_input = {}
    if input_data:
        try:
            pipeline_input = json.loads(input_data)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error:[/red] Invalid JSON input: {e}")
            raise typer.Exit(1)
    elif input_file:
        try:
            pipeline_input = json.loads(input_file.read_text())
        except json.JSONDecodeError as e:
            console.print(f"[red]Error:[/red] Invalid JSON in {input_file}: {e}")
            raise typer.Exit(1)
    elif use_sample and pipeline.sample_input:
        pipeline_input = pipeline.sample_input
        console.print("[dim]Using sample_input from pipeline file[/dim]\n")
    elif not input_data and not input_file and pipeline.sample_input:
        # Auto-use sample input if no input provided and sample exists
        pipeline_input = pipeline.sample_input
        console.print("[dim]No input provided, using sample_input from pipeline file[/dim]\n")

    pipeline_name = pipeline.name
    stage_count = len(pipeline.stages)

    # Display pipeline info
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="dim")
    info_table.add_column("Value")
    info_table.add_row("Pipeline", pipeline_name)
    info_table.add_row("Stages", str(stage_count))
    info_table.add_row("Input", json.dumps(pipeline_input)[:50] + "..." if len(json.dumps(pipeline_input)) > 50 else json.dumps(pipeline_input))
    console.print(info_table)
    console.print()

    if debug:
        console.print("[yellow]Debug mode:[/yellow] Starting debug server...")
        console.print("  Connect VSCode debugger to start execution")
        console.print("  Or use flowmason studio for visual debugging\n")

    # Execute pipeline
    try:
        result = asyncio.run(_execute_pipeline(
            pipeline,
            pipeline_input,
            verbose=verbose,
            timeout=timeout,
        ))

        # Display results
        console.print()
        if result.get("status") == "success":
            console.print(Panel(
                f"[green]Pipeline completed successfully[/green]\n\n"
                f"Duration: {result.get('duration_ms', 0)}ms\n"
                f"Stages executed: {result.get('stages_completed', 0)}",
                title="Result",
                border_style="green",
            ))

            if verbose and result.get("output"):
                console.print("\n[bold]Output:[/bold]")
                console.print_json(data=result["output"])
        else:
            console.print(Panel(
                f"[red]Pipeline failed[/red]\n\n"
                f"Error: {result.get('error', 'Unknown error')}\n"
                f"Failed at: {result.get('failed_stage', 'Unknown')}",
                title="Error",
                border_style="red",
            ))
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1)


async def _execute_pipeline(
    pipeline: "PipelineFile",
    pipeline_input: dict,
    verbose: bool = False,
    timeout: Optional[int] = None,
) -> dict:
    """Execute a pipeline and return results."""
    from datetime import datetime


    # Import execution components
    try:
        from flowmason_core.config import ComponentConfig, ExecutionContext
        from flowmason_core.execution.universal_executor import DAGExecutor
        from flowmason_core.providers import AnthropicProvider, OpenAIProvider
        from flowmason_core.registry import ComponentRegistry
    except ImportError as e:
        return {
            "status": "error",
            "error": f"Failed to import execution components: {e}",
        }

    start_time = datetime.utcnow()

    # Create registry and load components
    registry = ComponentRegistry()
    registry.auto_discover()

    # Load project config to get providers
    providers: Dict[str, Any] = {}
    default_provider: Optional[str] = None
    try:
        import os

        # Find project root by looking for flowmason.json
        project_root = Path(pipeline.file_path).parent if pipeline.file_path else Path.cwd()
        while project_root != project_root.parent:
            if (project_root / "flowmason.json").exists():
                break
            project_root = project_root.parent
        else:
            project_root = Path.cwd()

        manifest_path = project_root / "flowmason.json"
        if manifest_path.exists():
            manifest_data = json.loads(manifest_path.read_text())
            prov_config = manifest_data.get("providers", {})

            if prov_config:
                default_provider = prov_config.get("default")

                # Create provider instances
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
        # Continue without providers - generator will use fallback
        if verbose:
            console.print(f"[dim]Warning: Could not load providers: {e}[/dim]")

    # Create execution context
    context = ExecutionContext(
        pipeline_id=pipeline.name,
        pipeline_version=pipeline.version,
        run_id=f"cli-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        trace_id=f"trace-{datetime.utcnow().timestamp()}",
    )

    # Convert PipelineFile stages to ComponentConfig
    stages = []
    for stage in pipeline.stages:
        component_config = ComponentConfig(
            id=stage.id,
            type=stage.get_component_type(),
            depends_on=stage.depends_on,
            input_mapping=stage.config,
        )
        stages.append(component_config)

    # Create executor with providers
    executor = DAGExecutor(
        registry=registry,
        context=context,
        parallel_execution=True,
        providers=providers if providers else None,
        default_provider=default_provider,
    )

    # Execute
    try:
        results = await executor.execute(stages, pipeline_input)

        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Get final output
        final_output = None
        if results:
            # Use output_stage_id if specified, otherwise use last stage
            output_stage_id = pipeline.output_stage_id or list(results.keys())[-1]
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
            "failed_stage": getattr(e, "component_id", None),
            "duration_ms": duration_ms,
        }
