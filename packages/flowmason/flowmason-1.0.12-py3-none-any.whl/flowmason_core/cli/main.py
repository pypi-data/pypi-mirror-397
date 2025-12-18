"""
FlowMason CLI main entry point.

This is the entry point for the `flowmason` command.
"""

from typing import Optional

import typer
from rich.console import Console

# Create main app
app = typer.Typer(
    name="flowmason",
    help="FlowMason - AI Pipeline Orchestration Platform",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        from flowmason_core import __version__
        console.print(f"FlowMason CLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    FlowMason - AI Pipeline Orchestration Platform.

    Build, debug, and deploy intelligent workflows.

    Use --help on any command for more information.
    """
    pass


# Import and register command groups (after app definition to avoid circular imports)
from flowmason_core.cli.commands import (  # noqa: E402
    auth,
    deploy,
    diff,
    init,
    install,
    mcp,
    nl,
    org,
    pack,
    pull,
    registry,
    run,
    studio,
    validate,
)

# Register command groups (sub-commands)
app.add_typer(studio.app, name="studio", help="Manage FlowMason Studio backend")
app.add_typer(org.app, name="org", help="Manage FlowMason org connections")
app.add_typer(auth.app, name="auth", help="Manage authentication and API keys")
app.add_typer(mcp.app, name="mcp", help="Model Context Protocol server for AI")
app.add_typer(registry.app, name="registry", help="Manage package registries")

# Register top-level commands
app.command(name="run")(run.run_pipeline)
app.command(name="validate")(validate.validate_pipeline)
app.command(name="init")(init.init_project)
app.command(name="deploy")(deploy.deploy)
app.command(name="pull")(pull.pull)
app.command(name="pack")(pack.pack)
app.command(name="install")(install.install)
app.command(name="uninstall")(install.uninstall)
app.command(name="list")(install.list_packages)
app.command(name="search")(registry.search_packages)
app.command(name="publish")(registry.publish_package)
app.command(name="diff")(diff.diff_pipelines)
app.command(name="merge")(diff.merge_pipelines)
app.command(name="diff-stats")(diff.show_diff_stats)
app.command(name="nl")(nl.run_natural)
app.command(name="nl-suggest")(nl.suggest_pipelines)


def cli():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli()
