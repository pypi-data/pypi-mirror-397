"""
FlowMason Edge CLI.

Command-line interface for edge deployments.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from flowmason_edge.runtime.edge_runtime import EdgeConfig, EdgeRuntime, create_runtime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@click.group()
@click.option("--data-dir", "-d", default="/var/flowmason/edge", help="Data directory")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, data_dir: str, verbose: bool):
    """FlowMason Edge - Offline pipeline execution for edge devices."""
    ctx.ensure_object(dict)
    ctx.obj["data_dir"] = data_dir

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.argument("pipeline")
@click.option("--input", "-i", "input_file", type=click.Path(exists=True), help="Input JSON file")
@click.option("--input-json", "-j", help="Input as JSON string")
@click.option("--output", "-o", "output_file", type=click.Path(), help="Output file")
@click.option("--model", "-m", help="LLM model to use")
@click.option("--backend", "-b", default="ollama", help="LLM backend (ollama, llamacpp)")
@click.pass_context
def run(
    ctx,
    pipeline: str,
    input_file: Optional[str],
    input_json: Optional[str],
    output_file: Optional[str],
    model: Optional[str],
    backend: str,
):
    """Run a pipeline on the edge."""
    data_dir = ctx.obj["data_dir"]

    # Parse inputs
    inputs = {}
    if input_file:
        with open(input_file) as f:
            inputs = json.load(f)
    elif input_json:
        inputs = json.loads(input_json)

    async def execute():
        config = EdgeConfig(
            data_dir=data_dir,
            llm_backend=backend,
            llm_model=model,
            auto_sync=False,
        )

        runtime = EdgeRuntime(config)

        try:
            await runtime.start()

            # Check if pipeline is a file or cached name
            pipeline_path = Path(pipeline)
            if pipeline_path.exists():
                with open(pipeline_path) as f:
                    pipeline_config = json.load(f)
                result = await runtime.execute_config(pipeline_config, inputs)
            else:
                result = await runtime.execute(pipeline, inputs)

            # Output result
            output_data = {
                "run_id": result.run_id,
                "status": result.status.value,
                "duration_ms": result.duration_ms,
                "output": result.output,
            }

            if result.error:
                output_data["error"] = result.error

            if output_file:
                with open(output_file, "w") as f:
                    json.dump(output_data, f, indent=2)
                click.echo(f"Output written to {output_file}")
            else:
                click.echo(json.dumps(output_data, indent=2))

            return result.status.value == "completed"

        finally:
            await runtime.stop()

    success = asyncio.run(execute())
    sys.exit(0 if success else 1)


@cli.command()
@click.argument("pipeline_file", type=click.Path(exists=True))
@click.option("--name", "-n", help="Name for the cached pipeline")
@click.pass_context
def cache(ctx, pipeline_file: str, name: Optional[str]):
    """Cache a pipeline for offline execution."""
    data_dir = ctx.obj["data_dir"]

    with open(pipeline_file) as f:
        config = json.load(f)

    name = name or config.get("name", Path(pipeline_file).stem)

    from flowmason_edge.cache.pipeline_cache import PipelineCache

    cache_dir = str(Path(data_dir) / "pipelines")
    cache = PipelineCache(cache_dir)

    cached = cache.put(name, config, source="local")

    click.echo(f"Cached pipeline: {name}")
    click.echo(f"  Version: {cached.version}")
    click.echo(f"  Hash: {cached.hash}")
    click.echo(f"  Size: {cached.size_bytes} bytes")


@cli.command("list")
@click.option("--pipelines", "-p", is_flag=True, help="List cached pipelines")
@click.option("--models", "-m", is_flag=True, help="List cached models")
@click.option("--results", "-r", is_flag=True, help="List pending results")
@click.pass_context
def list_items(ctx, pipelines: bool, models: bool, results: bool):
    """List cached items."""
    data_dir = ctx.obj["data_dir"]

    # Default to all
    if not (pipelines or models or results):
        pipelines = models = results = True

    if pipelines:
        from flowmason_edge.cache.pipeline_cache import PipelineCache

        cache = PipelineCache(str(Path(data_dir) / "pipelines"))
        items = cache.list()

        click.echo("\nCached Pipelines:")
        if items:
            for p in items:
                click.echo(f"  {p.name} v{p.version} ({p.source})")
        else:
            click.echo("  (none)")

    if models:
        from flowmason_edge.cache.model_cache import ModelCache

        cache = ModelCache(str(Path(data_dir) / "models"))
        items = cache.list()

        click.echo("\nCached Models:")
        if items:
            for m in items:
                size_gb = m.size_bytes / 1e9
                click.echo(f"  {m.name} ({size_gb:.1f}GB) [{m.family}]")
        else:
            click.echo("  (none)")

    if results:
        from flowmason_edge.cache.result_store import ResultStore

        store = ResultStore(str(Path(data_dir) / "results"))
        stats = store.get_stats()

        click.echo("\nResults:")
        click.echo(f"  Total: {stats['total']}")
        click.echo(f"  Pending: {stats['pending']}")
        click.echo(f"  Synced: {stats['synced']}")
        click.echo(f"  Failed: {stats['failed']}")


@cli.command()
@click.option("--url", "-u", envvar="FLOWMASON_CLOUD_URL", help="Cloud URL")
@click.option("--api-key", "-k", envvar="FLOWMASON_API_KEY", help="API key")
@click.option("--pipelines", "-p", multiple=True, help="Specific pipelines to sync")
@click.pass_context
def sync(ctx, url: Optional[str], api_key: Optional[str], pipelines: tuple):
    """Sync with cloud."""
    if not url or not api_key:
        click.echo("Error: Cloud URL and API key required")
        click.echo("Set FLOWMASON_CLOUD_URL and FLOWMASON_API_KEY environment variables")
        sys.exit(1)

    data_dir = ctx.obj["data_dir"]

    async def do_sync():
        config = EdgeConfig(
            data_dir=data_dir,
            cloud_url=url,
            api_key=api_key,
            auto_sync=False,
        )

        runtime = EdgeRuntime(config)

        try:
            await runtime.start()

            # Check connectivity
            if not await runtime.check_connectivity():
                click.echo("Error: Cannot connect to cloud")
                return False

            click.echo("Connected to cloud")

            # Sync results
            click.echo("Syncing results...")
            result = await runtime.sync()

            results = result.get("results", {})
            click.echo(f"  Synced: {results.get('synced', 0)}")
            click.echo(f"  Failed: {results.get('failed', 0)}")

            # Sync pipelines
            if pipelines:
                click.echo(f"Syncing pipelines: {', '.join(pipelines)}...")
                for name, success in result.get("pipelines", {}).items():
                    status = "OK" if success else "FAILED"
                    click.echo(f"  {name}: {status}")

            return True

        finally:
            await runtime.stop()

    success = asyncio.run(do_sync())
    sys.exit(0 if success else 1)


@cli.command("download-model")
@click.argument("repo_id")
@click.argument("filename")
@click.option("--name", "-n", help="Local name for the model")
@click.pass_context
def download_model(ctx, repo_id: str, filename: str, name: Optional[str]):
    """Download a model from HuggingFace."""
    data_dir = ctx.obj["data_dir"]

    async def download():
        from flowmason_edge.cache.model_cache import ModelCache

        cache = ModelCache(str(Path(data_dir) / "models"))

        click.echo(f"Downloading {filename} from {repo_id}...")

        model = await cache.download(
            repo_id=repo_id,
            filename=filename,
            name=name,
        )

        size_gb = model.size_bytes / 1e9
        click.echo(f"Downloaded: {model.name}")
        click.echo(f"  Size: {size_gb:.1f}GB")
        click.echo(f"  Path: {model.path}")

    asyncio.run(download())


@cli.command()
@click.pass_context
def status(ctx):
    """Show edge runtime status."""
    data_dir = ctx.obj["data_dir"]

    from flowmason_edge.cache.model_cache import ModelCache
    from flowmason_edge.cache.pipeline_cache import PipelineCache
    from flowmason_edge.cache.result_store import ResultStore

    click.echo("FlowMason Edge Status")
    click.echo("=" * 40)
    click.echo(f"Data Directory: {data_dir}")

    # Pipeline cache
    pipeline_cache = PipelineCache(str(Path(data_dir) / "pipelines"))
    pipelines = pipeline_cache.list()
    click.echo(f"\nPipelines: {len(pipelines)} cached")

    # Model cache
    model_cache = ModelCache(str(Path(data_dir) / "models"))
    models = model_cache.list()
    total_size = model_cache.get_size()
    click.echo(f"Models: {len(models)} cached ({total_size / 1e9:.1f}GB)")

    # Result store
    result_store = ResultStore(str(Path(data_dir) / "results"))
    stats = result_store.get_stats()
    click.echo(f"Results: {stats['pending']} pending, {stats['synced']} synced")

    # Check Ollama
    click.echo("\nLLM Backends:")
    try:
        import requests

        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            ollama_models = resp.json().get("models", [])
            click.echo(f"  Ollama: Available ({len(ollama_models)} models)")
        else:
            click.echo("  Ollama: Not responding")
    except Exception:
        click.echo("  Ollama: Not available")

    try:
        import llama_cpp

        click.echo("  LlamaCpp: Available")
    except ImportError:
        click.echo("  LlamaCpp: Not installed")


@cli.command()
@click.option("--port", "-p", default=8080, help="Server port")
@click.option("--host", "-h", default="0.0.0.0", help="Server host")
@click.option("--model", "-m", help="LLM model to use")
@click.option("--backend", "-b", default="ollama", help="LLM backend")
@click.option("--cloud-url", envvar="FLOWMASON_CLOUD_URL", help="Cloud URL for sync")
@click.option("--api-key", envvar="FLOWMASON_API_KEY", help="API key for sync")
@click.pass_context
def serve(
    ctx,
    port: int,
    host: str,
    model: Optional[str],
    backend: str,
    cloud_url: Optional[str],
    api_key: Optional[str],
):
    """Start edge server for remote execution."""
    data_dir = ctx.obj["data_dir"]

    click.echo(f"Starting FlowMason Edge Server on {host}:{port}")

    try:
        from flowmason_edge.server import create_app, run_server

        config = EdgeConfig(
            data_dir=data_dir,
            cloud_url=cloud_url,
            api_key=api_key,
            llm_backend=backend,
            llm_model=model,
            auto_sync=bool(cloud_url and api_key),
        )

        asyncio.run(run_server(config, host=host, port=port))

    except ImportError:
        click.echo("Error: Server dependencies not installed")
        click.echo("Install with: pip install flowmason-edge[server]")
        sys.exit(1)


def main():
    """CLI entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
