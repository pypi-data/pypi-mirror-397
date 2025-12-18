"""
Init command for FlowMason CLI.

Initialize a new FlowMason project with standard structure.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

console = Console()


def init_project(
    path: Optional[Path] = typer.Argument(
        None,
        help="Path to initialize project in (default: current directory)",
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Project name (default: directory name)",
    ),
    template: Optional[str] = typer.Option(
        None,
        "--template",
        "-t",
        help="Template to use (basic, ai-pipeline, etl)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing flowmason.json",
    ),
):
    """
    Initialize a new FlowMason project.

    Creates the standard project structure with flowmason.json manifest,
    directories for pipelines and components, and optionally starter files.

    Examples:
        flowmason init
        flowmason init my-project
        flowmason init --name my-ai-pipeline --template ai-pipeline
    """
    # Determine project path
    project_path = Path(path) if path else Path.cwd()
    project_path = project_path.resolve()

    # Determine project name
    project_name = name or project_path.name

    console.print(f"\n[bold blue]FlowMason[/bold blue] Initializing project: {project_name}\n")

    # Check if manifest already exists
    manifest_path = project_path / "flowmason.json"
    if manifest_path.exists() and not force:
        console.print("[yellow]Warning:[/yellow] flowmason.json already exists")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)

    # Create project directory if needed
    project_path.mkdir(parents=True, exist_ok=True)

    # Create directory structure
    directories = [
        "pipelines",
        "components/nodes",
        "components/operators",
        ".flowmason",
    ]

    for dir_name in directories:
        (project_path / dir_name).mkdir(parents=True, exist_ok=True)

    # Create flowmason.json
    manifest = _create_manifest(project_name, template)
    manifest_path.write_text(json.dumps(manifest, indent=2))

    # Create starter files based on template
    _create_starter_files(project_path, template)

    # Create .gitignore for FlowMason
    _create_gitignore(project_path)

    # Show success message
    tree = Tree(f"[bold]{project_name}[/bold]")
    tree.add("[dim]flowmason.json[/dim] - Project manifest")
    tree.add("[dim]pipelines/[/dim] - Pipeline definitions")
    tree.add("[dim]components/[/dim] - Custom components")
    tree.add("[dim].flowmason/[/dim] - Local state & cache")

    console.print(Panel(
        "[green]Project initialized successfully![/green]\n\n"
        "Next steps:\n"
        "  1. Edit [cyan]flowmason.json[/cyan] to configure providers\n"
        "  2. Create pipelines in [cyan]pipelines/[/cyan]\n"
        "  3. Run [cyan]flowmason run pipelines/main.pipeline.json[/cyan]",
        title="FlowMason",
        border_style="green",
    ))
    console.print()
    console.print(tree)
    console.print()


def _create_manifest(name: str, template: Optional[str]) -> Dict[str, Any]:
    """Create the flowmason.json manifest content."""
    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": f"{name} - FlowMason AI Pipeline Project",
        "main": "pipelines/main.pipeline.json",
        "components": {
            "include": ["components/**/*.py"]
        },
        "providers": {
            "default": "anthropic",
            "anthropic": {
                "model": "claude-sonnet-4-20250514"
            }
        },
        "testing": {
            "timeout": 30000,
            "retries": 2
        },
        "pipeline_dirs": ["pipelines"]
    }

    # Adjust based on template
    if template == "etl":
        manifest["description"] = f"{name} - Data ETL Pipeline"
        providers = manifest["providers"]
        if isinstance(providers, dict):
            providers["default"] = "none"
            if "anthropic" in providers:
                del providers["anthropic"]

    return manifest


def _create_starter_files(project_path: Path, template: Optional[str]):
    """Create starter pipeline files based on template."""
    pipelines_dir = project_path / "pipelines"

    if template == "ai-pipeline":
        # Create an AI-focused starter pipeline
        pipeline = {
            "$schema": "https://flowmason.dev/schemas/pipeline.schema.json",
            "name": "ai-content-pipeline",
            "version": "1.0.0",
            "description": "Generate and refine AI content",
            "input_schema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to write about"},
                    "style": {"type": "string", "description": "Writing style"}
                },
                "required": ["topic"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "word_count": {"type": "integer"}
                }
            },
            "stages": [
                {
                    "id": "generate",
                    "component": "generator",
                    "config": {
                        "prompt": "Write a short article about {{input.topic}} in a {{input.style}} style.",
                        "max_tokens": 500
                    }
                },
                {
                    "id": "improve",
                    "component": "improver",
                    "depends_on": ["generate"],
                    "config": {
                        "content": "{{generate.output.content}}",
                        "criteria": ["clarity", "engagement", "accuracy"]
                    }
                }
            ],
            "output_stage_id": "improve",
            "sample_input": {
                "topic": "artificial intelligence",
                "style": "informative"
            }
        }
    elif template == "etl":
        # Create a data ETL starter pipeline
        pipeline = {
            "$schema": "https://flowmason.dev/schemas/pipeline.schema.json",
            "name": "data-etl-pipeline",
            "version": "1.0.0",
            "description": "Extract, transform, and load data",
            "input_schema": {
                "type": "object",
                "properties": {
                    "source_url": {"type": "string", "description": "Data source URL"}
                },
                "required": ["source_url"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "records_processed": {"type": "integer"},
                    "result": {"type": "object"}
                }
            },
            "stages": [
                {
                    "id": "fetch",
                    "component": "http-request",
                    "config": {
                        "url": "{{input.source_url}}",
                        "method": "GET"
                    }
                },
                {
                    "id": "transform",
                    "component": "json-transform",
                    "depends_on": ["fetch"],
                    "config": {
                        "data": "{{fetch.output.body}}",
                        "expression": "items[*].{id: id, name: name}"
                    }
                },
                {
                    "id": "validate",
                    "component": "schema-validate",
                    "depends_on": ["transform"],
                    "config": {
                        "data": "{{transform.output.result}}",
                        "schema": {
                            "type": "array",
                            "items": {"type": "object"}
                        }
                    }
                }
            ],
            "output_stage_id": "validate",
            "sample_input": {
                "source_url": "https://api.example.com/data"
            }
        }
    else:
        # Default basic template
        pipeline = {
            "$schema": "https://flowmason.dev/schemas/pipeline.schema.json",
            "name": "main",
            "version": "1.0.0",
            "description": "Main pipeline",
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Input message"}
                },
                "required": ["message"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "result": {"type": "string"}
                }
            },
            "stages": [
                {
                    "id": "process",
                    "component": "generator",
                    "config": {
                        "prompt": "Process this message: {{input.message}}"
                    }
                }
            ],
            "output_stage_id": "process",
            "sample_input": {
                "message": "Hello, FlowMason!"
            }
        }

    # Write the pipeline file
    pipeline_file = pipelines_dir / "main.pipeline.json"
    pipeline_file.write_text(json.dumps(pipeline, indent=2))


def _create_gitignore(project_path: Path):
    """Create .gitignore for FlowMason projects."""
    gitignore_path = project_path / ".gitignore"

    # Append to existing or create new
    gitignore_content = """
# FlowMason
.flowmason/
*.fmpkg

# Python
__pycache__/
*.py[cod]
*$py.class
.env
.venv/
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""

    if gitignore_path.exists():
        existing = gitignore_path.read_text()
        if "# FlowMason" not in existing:
            gitignore_path.write_text(existing + gitignore_content)
    else:
        gitignore_path.write_text(gitignore_content.strip())
