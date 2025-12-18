"""
Diff and Merge commands for FlowMason CLI.

Provides Git-style diff and merge capabilities for pipeline files.
"""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def diff_pipelines(
    file_a: Path = typer.Argument(
        ...,
        help="First pipeline file (base/old)",
    ),
    file_b: Path = typer.Argument(
        ...,
        help="Second pipeline file (target/new)",
    ),
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format: text, json, markdown, unified",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable colored output",
    ),
    ignore_position: bool = typer.Option(
        True,
        "--ignore-position/--include-position",
        help="Ignore canvas position changes",
    ),
):
    """
    Compare two pipeline files and show differences.

    Examples:
        fm diff old.pipeline.json new.pipeline.json
        fm diff base.pipeline.json feature.pipeline.json --format json
        fm diff a.pipeline.json b.pipeline.json --format markdown > diff.md
    """
    from flowmason_core.diff import DiffFormatter, PipelineDiffer
    from flowmason_core.project.loader import load_pipeline_file

    # Validate files exist
    if not file_a.exists():
        console.print(f"[red]Error:[/red] File not found: {file_a}")
        raise typer.Exit(1)
    if not file_b.exists():
        console.print(f"[red]Error:[/red] File not found: {file_b}")
        raise typer.Exit(1)

    # Load pipelines
    try:
        pipeline_a = load_pipeline_file(file_a)
        pipeline_b = load_pipeline_file(file_b)
    except Exception as e:
        console.print(f"[red]Error loading pipeline:[/red] {e}")
        raise typer.Exit(1)

    # Compute diff
    differ = PipelineDiffer()
    diff = differ.diff(pipeline_a, pipeline_b, ignore_position=ignore_position)

    # Format and output
    formatter = DiffFormatter()
    use_color = not no_color and format == "text"
    output = formatter.format_diff(diff, format=format, color=use_color)

    if format == "text":
        console.print()
        console.print(Panel(
            f"[bold]Comparing:[/bold] {file_a.name} → {file_b.name}",
            border_style="blue",
        ))
        console.print()

    # Use print for non-text formats to avoid rich formatting
    if format in ("json", "markdown", "unified"):
        print(output)
    else:
        console.print(output)

    # Exit with code 1 if there are changes (like git diff)
    if diff.has_changes:
        raise typer.Exit(1)


def merge_pipelines(
    base: Path = typer.Argument(
        ...,
        help="Base pipeline file (common ancestor)",
    ),
    ours: Path = typer.Argument(
        ...,
        help="Our pipeline file (local changes)",
    ),
    theirs: Path = typer.Argument(
        ...,
        help="Their pipeline file (remote changes)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for merged pipeline (default: stdout)",
    ),
    favor: Optional[str] = typer.Option(
        None,
        "--favor",
        help="Conflict resolution strategy: 'ours' or 'theirs'",
    ),
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format for result: text, json",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable colored output",
    ),
):
    """
    Perform a three-way merge of pipeline files.

    Three-way merge uses a common ancestor (base) to intelligently
    merge changes from two divergent versions (ours and theirs).

    Examples:
        fm merge base.pipeline.json local.pipeline.json remote.pipeline.json
        fm merge base.json ours.json theirs.json -o merged.pipeline.json
        fm merge base.json ours.json theirs.json --favor ours
    """
    from flowmason_core.diff import DiffFormatter, ThreeWayMerger
    from flowmason_core.project.loader import load_pipeline_file

    # Validate files exist
    for f, name in [(base, "base"), (ours, "ours"), (theirs, "theirs")]:
        if not f.exists():
            console.print(f"[red]Error:[/red] {name} file not found: {f}")
            raise typer.Exit(1)

    # Validate favor option
    if favor and favor not in ("ours", "theirs"):
        console.print(f"[red]Error:[/red] --favor must be 'ours' or 'theirs'")
        raise typer.Exit(1)

    # Load pipelines
    try:
        base_pipeline = load_pipeline_file(base)
        ours_pipeline = load_pipeline_file(ours)
        theirs_pipeline = load_pipeline_file(theirs)
    except Exception as e:
        console.print(f"[red]Error loading pipeline:[/red] {e}")
        raise typer.Exit(1)

    # Perform merge
    merger = ThreeWayMerger()
    result = merger.merge(base_pipeline, ours_pipeline, theirs_pipeline, favor=favor)

    # Format output
    formatter = DiffFormatter()
    use_color = not no_color and format == "text"

    console.print()
    console.print(Panel(
        f"[bold]Three-Way Merge[/bold]\n"
        f"Base: {base.name}\n"
        f"Ours: {ours.name}\n"
        f"Theirs: {theirs.name}",
        border_style="blue",
    ))
    console.print()

    # Show merge result
    result_output = formatter.format_merge_result(result, format=format, color=use_color)
    if format == "json":
        print(result_output)
    else:
        console.print(result_output)

    # Handle conflicts
    if result.has_conflicts:
        console.print()
        console.print("[yellow]Tip:[/yellow] Use --favor ours or --favor theirs to auto-resolve conflicts")
        raise typer.Exit(1)

    # Write merged output
    if result.merged:
        merged_json = json.dumps(result.merged, indent=2)

        if output:
            output.write_text(merged_json)
            console.print()
            console.print(f"[green]✓[/green] Merged pipeline written to: {output}")
        else:
            console.print()
            console.print("[bold]Merged Pipeline:[/bold]")
            print(merged_json)


def show_diff_stats(
    path: Path = typer.Argument(
        ...,
        help="Pipeline file or directory",
    ),
):
    """
    Show diff statistics for pipeline files.

    Compares against the git HEAD version if in a git repository.

    Examples:
        fm diff-stats pipelines/main.pipeline.json
        fm diff-stats pipelines/
    """
    import subprocess

    from flowmason_core.diff import DiffFormatter, PipelineDiffer
    from flowmason_core.project.loader import discover_pipelines, load_pipeline_file

    # Find pipeline files
    if path.is_file():
        files = [path]
    else:
        files = discover_pipelines(path)

    if not files:
        console.print(f"[yellow]No pipeline files found in {path}[/yellow]")
        raise typer.Exit(0)

    differ = PipelineDiffer()
    formatter = DiffFormatter()

    console.print()
    console.print(f"[bold]Diff Stats for {len(files)} pipeline(s)[/bold]")
    console.print()

    for pipeline_path in files:
        # Try to get git HEAD version
        try:
            result = subprocess.run(
                ["git", "show", f"HEAD:{pipeline_path}"],
                capture_output=True,
                text=True,
                cwd=pipeline_path.parent,
            )
            if result.returncode != 0:
                console.print(f"  {pipeline_path.name}: [dim]not in git[/dim]")
                continue

            # Parse HEAD version
            from flowmason_core.project.loader import PipelineFile
            head_pipeline = PipelineFile.from_json(result.stdout)
            current_pipeline = load_pipeline_file(pipeline_path)

            # Compute diff
            diff = differ.diff(head_pipeline, current_pipeline)

            if diff.has_changes:
                console.print(f"  {pipeline_path.name}: [yellow]{diff.summary}[/yellow]")
            else:
                console.print(f"  {pipeline_path.name}: [green]no changes[/green]")

        except Exception as e:
            console.print(f"  {pipeline_path.name}: [red]error: {e}[/red]")
