"""
Validate command for FlowMason CLI.

Validate pipeline files and project structure.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def validate_pipeline(
    path: Path = typer.Argument(
        ...,
        help="Path to pipeline file or directory",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        "-s",
        help="Enable strict validation (fail on warnings)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation output",
    ),
    check_inheritance: bool = typer.Option(
        False,
        "--check-inheritance",
        "-i",
        help="Validate pipeline inheritance (extends, overrides, compositions)",
    ),
):
    """
    Validate pipeline files.

    Examples:
        flowmason validate pipelines/main.pipeline.json
        flowmason validate pipelines/
        flowmason validate . --strict
        flowmason validate . --check-inheritance
    """
    console.print(f"\n[bold blue]FlowMason[/bold blue] Validating: {path}\n")

    # Collect pipeline files
    pipeline_files: List[Path] = []

    if path.is_file():
        if not path.suffix == ".json" or "pipeline" not in path.stem:
            console.print(f"[yellow]Warning:[/yellow] {path} doesn't look like a pipeline file")
        pipeline_files.append(path)
    elif path.is_dir():
        # Find all .pipeline.json files
        pipeline_files = list(path.glob("**/*.pipeline.json"))
        if not pipeline_files:
            # Also look for pipelines/*.json
            pipeline_files = list(path.glob("**/pipelines/*.json"))
        if not pipeline_files:
            console.print(f"[yellow]Warning:[/yellow] No pipeline files found in {path}")
            raise typer.Exit(0)
    else:
        console.print(f"[red]Error:[/red] Path not found: {path}")
        raise typer.Exit(1)

    console.print(f"Found {len(pipeline_files)} pipeline file(s)\n")

    # Build pipeline loader for inheritance validation
    pipeline_loader: Optional[Callable] = None
    if check_inheritance:
        console.print("[dim]Inheritance validation enabled[/dim]\n")
        pipeline_loader = _create_pipeline_loader(pipeline_files)

    # Validate each file
    results = []
    for pipeline_path in pipeline_files:
        result = _validate_single_pipeline(
            pipeline_path, strict, verbose, check_inheritance, pipeline_loader
        )
        results.append(result)

    # Summary table
    table = Table(title="Validation Results")
    table.add_column("Pipeline", style="cyan")
    table.add_column("Status")
    table.add_column("Errors", style="red")
    table.add_column("Warnings", style="yellow")

    total_errors = 0
    total_warnings = 0

    for result in results:
        status = "[green]PASS[/green]" if result["valid"] else "[red]FAIL[/red]"
        table.add_row(
            result["name"],
            status,
            str(len(result["errors"])),
            str(len(result["warnings"])),
        )
        total_errors += len(result["errors"])
        total_warnings += len(result["warnings"])

    console.print(table)
    console.print()

    # Show details if verbose or errors exist
    if verbose or total_errors > 0:
        for result in results:
            if result["errors"] or (verbose and result["warnings"]):
                console.print(f"\n[bold]{result['name']}[/bold]")
                for error in result["errors"]:
                    console.print(f"  [red]ERROR:[/red] {error}")
                for warning in result["warnings"]:
                    console.print(f"  [yellow]WARN:[/yellow] {warning}")

    # Final summary
    if total_errors > 0:
        console.print(Panel(
            f"[red]Validation failed[/red]\n\n"
            f"Errors: {total_errors}\n"
            f"Warnings: {total_warnings}",
            border_style="red",
        ))
        raise typer.Exit(1)
    elif total_warnings > 0 and strict:
        console.print(Panel(
            f"[yellow]Validation failed (strict mode)[/yellow]\n\n"
            f"Warnings: {total_warnings}",
            border_style="yellow",
        ))
        raise typer.Exit(1)
    else:
        console.print(Panel(
            f"[green]All pipelines valid[/green]\n\n"
            f"Files: {len(results)}\n"
            f"Warnings: {total_warnings}",
            border_style="green",
        ))


def _create_pipeline_loader(
    pipeline_files: List[Path],
) -> Callable[[str], Optional[Any]]:
    """
    Create a pipeline loader function for inheritance validation.

    The loader builds an index of all pipelines by name and name@version,
    and returns the PipelineConfig when requested.
    """
    from flowmason_core.project.loader import load_pipeline_file

    # Build index of pipelines
    pipeline_index: Dict[str, Any] = {}

    for path in pipeline_files:
        try:
            pipeline = load_pipeline_file(path)
            # Index by name
            pipeline_index[pipeline.name] = pipeline
            # Index by name@version
            if pipeline.version:
                pipeline_index[f"{pipeline.name}@{pipeline.version}"] = pipeline
        except Exception:
            # Skip files that can't be loaded
            pass

    def loader(ref: str) -> Optional[Any]:
        """Load a pipeline by reference (name or name@version)."""
        return pipeline_index.get(ref)

    return loader


def _validate_single_pipeline(
    path: Path,
    strict: bool,
    verbose: bool,
    check_inheritance: bool = False,
    pipeline_loader: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Validate a single pipeline file."""
    from flowmason_core.project.loader import load_pipeline_file

    errors: List[str] = []
    warnings: List[str] = []
    result: Dict[str, Any] = {
        "name": path.name,
        "path": str(path),
        "valid": True,
        "errors": errors,
        "warnings": warnings,
    }

    # Check file exists and is readable
    if not path.exists():
        errors.append(f"File not found: {path}")
        result["valid"] = False
        return result

    # Try to load using PipelineFile (validates schema)
    try:
        pipeline = load_pipeline_file(path)
        result["name"] = pipeline.name or path.name
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        result["valid"] = False
        return result
    except ValidationError as e:
        # Pydantic validation errors
        for error in e.errors():
            loc = ".".join(str(x) for x in error["loc"])
            errors.append(f"{loc}: {error['msg']}")
        result["valid"] = False
        return result
    except Exception as e:
        errors.append(f"Failed to parse pipeline: {e}")
        result["valid"] = False
        return result

    # Additional validation beyond schema
    # Check recommended fields
    if not pipeline.description:
        warnings.append("Missing recommended field: description")
    if not pipeline.input_schema.properties:
        warnings.append("No input schema properties defined")
    if not pipeline.output_schema.properties:
        warnings.append("No output schema properties defined")

    # Validate stages
    stage_ids: set[str] = set()
    for idx, stage in enumerate(pipeline.stages):
        stage_result = _validate_stage_obj(stage, idx, stage_ids)
        errors.extend(stage_result["errors"])
        warnings.extend(stage_result["warnings"])
        if stage.id:
            stage_ids.add(stage.id)

    # Check output_stage_id references valid stage
    if pipeline.output_stage_id and pipeline.output_stage_id not in stage_ids:
        errors.append(f"output_stage_id '{pipeline.output_stage_id}' references non-existent stage")

    # Inheritance validation
    if check_inheritance:
        inheritance_result = _validate_inheritance(pipeline, pipeline_loader)
        errors.extend(inheritance_result["errors"])
        warnings.extend(inheritance_result["warnings"])

    if errors:
        result["valid"] = False

    return result


def _validate_inheritance(
    pipeline: Any,
    pipeline_loader: Optional[Callable],
) -> Dict[str, Any]:
    """Validate pipeline inheritance configuration."""
    from flowmason_core.inheritance import InheritanceValidator

    errors: List[str] = []
    warnings: List[str] = []
    result: Dict[str, Any] = {
        "errors": errors,
        "warnings": warnings,
    }

    # Create validator with loader
    validator = InheritanceValidator(loader=pipeline_loader)

    # Run inheritance validation
    validation_result = validator.validate(pipeline, deep=True)

    # Convert issues to error/warning strings
    for issue in validation_result.issues:
        msg = f"[{issue.code}] {issue.message}"
        if issue.stage:
            msg = f"Stage '{issue.stage}': {msg}"

        if issue.level == "error":
            errors.append(msg)
        else:
            warnings.append(msg)

    return result


def _validate_stage_obj(stage: Any, index: int, existing_ids: set[str]) -> Dict[str, Any]:
    """Validate a PipelineStage object."""
    errors: List[str] = []
    warnings: List[str] = []
    result: Dict[str, Any] = {
        "errors": errors,
        "warnings": warnings,
    }

    prefix = f"Stage {index}"
    if stage.id:
        prefix = f"Stage '{stage.id}'"

        if stage.id in existing_ids:
            errors.append(f"{prefix}: Duplicate stage ID")

    # Check component type is specified
    component_type = stage.get_component_type()
    if not component_type:
        errors.append(f"{prefix}: Missing 'component' or 'component_type'")

    # Validate depends_on references
    for dep in stage.depends_on:
        if dep not in existing_ids:
            warnings.append(
                f"{prefix}: Depends on '{dep}' which hasn't been defined yet "
                "(may be valid for topological sort)"
            )

    return result


def _validate_stage(stage: Dict[str, Any], index: int, existing_ids: set[str]) -> Dict[str, Any]:
    """Validate a single stage."""
    errors: List[str] = []
    warnings: List[str] = []
    result: Dict[str, Any] = {
        "errors": errors,
        "warnings": warnings,
        "id": None,
    }

    prefix = f"Stage {index}"

    # Required: id
    if "id" not in stage:
        errors.append(f"{prefix}: Missing required field 'id'")
    else:
        stage_id = stage["id"]
        result["id"] = stage_id
        prefix = f"Stage '{stage_id}'"

        if stage_id in existing_ids:
            errors.append(f"{prefix}: Duplicate stage ID")

    # Required: component or type
    if "component" not in stage and "type" not in stage:
        errors.append(f"{prefix}: Missing 'component' or 'type'")

    # Validate depends_on
    depends_on = stage.get("depends_on", [])
    if not isinstance(depends_on, list):
        errors.append(f"{prefix}: 'depends_on' must be an array")
    else:
        for dep in depends_on:
            if dep not in existing_ids:
                warnings.append(
                    f"{prefix}: Depends on '{dep}' which hasn't been defined yet "
                    "(may be valid for topological sort)"
                )

    # Validate config
    config = stage.get("config", {})
    if not isinstance(config, dict):
        errors.append(f"{prefix}: 'config' must be an object")

    return result
