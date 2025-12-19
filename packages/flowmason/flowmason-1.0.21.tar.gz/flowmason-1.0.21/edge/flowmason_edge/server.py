"""
Edge Server for FlowMason Edge.

Provides HTTP API for remote pipeline execution.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from aiohttp import web

from flowmason_edge.runtime.edge_runtime import EdgeConfig, EdgeRuntime

logger = logging.getLogger(__name__)


class EdgeServer:
    """HTTP server for edge runtime."""

    def __init__(self, runtime: EdgeRuntime):
        self.runtime = runtime
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_get("/health", self.health_handler)
        self.app.router.add_get("/status", self.status_handler)
        self.app.router.add_post("/execute", self.execute_handler)
        self.app.router.add_post("/execute/{pipeline}", self.execute_pipeline_handler)
        self.app.router.add_get("/pipelines", self.list_pipelines_handler)
        self.app.router.add_post("/pipelines", self.cache_pipeline_handler)
        self.app.router.add_get("/models", self.list_models_handler)
        self.app.router.add_post("/sync", self.sync_handler)

    async def health_handler(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({"status": "healthy"})

    async def status_handler(self, request: web.Request) -> web.Response:
        """Get runtime status."""
        status = self.runtime.status
        return web.json_response({
            "running": status.running,
            "executor_ready": status.executor_ready,
            "llm_available": status.llm_available,
            "cached_pipelines": status.cached_pipelines,
            "cached_models": status.cached_models,
            "pending_results": status.pending_results,
            "uptime_seconds": status.uptime_seconds,
            "sync": {
                "status": status.sync_state.status.value if status.sync_state else None,
                "connection": status.sync_state.connection.value if status.sync_state else None,
            } if status.sync_state else None,
        })

    async def execute_handler(self, request: web.Request) -> web.Response:
        """Execute a pipeline configuration."""
        try:
            data = await request.json()
            pipeline = data.get("pipeline", {})
            inputs = data.get("inputs", {})

            result = await self.runtime.execute_config(pipeline, inputs)

            return web.json_response({
                "run_id": result.run_id,
                "status": result.status.value,
                "duration_ms": result.duration_ms,
                "output": result.output,
                "error": result.error,
            })

        except Exception as e:
            logger.error(f"Execute error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def execute_pipeline_handler(self, request: web.Request) -> web.Response:
        """Execute a cached pipeline."""
        try:
            pipeline_name = request.match_info["pipeline"]
            data = await request.json()
            inputs = data.get("inputs", {})

            result = await self.runtime.execute(pipeline_name, inputs)

            return web.json_response({
                "run_id": result.run_id,
                "status": result.status.value,
                "duration_ms": result.duration_ms,
                "output": result.output,
                "error": result.error,
            })

        except ValueError as e:
            return web.json_response({"error": str(e)}, status=404)
        except Exception as e:
            logger.error(f"Execute error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def list_pipelines_handler(self, request: web.Request) -> web.Response:
        """List cached pipelines."""
        pipelines = self.runtime.list_pipelines()
        return web.json_response({"pipelines": pipelines})

    async def cache_pipeline_handler(self, request: web.Request) -> web.Response:
        """Cache a pipeline."""
        try:
            data = await request.json()
            name = data.get("name")
            config = data.get("config", {})
            version = data.get("version")

            if not name:
                name = config.get("name", "unnamed")

            self.runtime.cache_pipeline(name, config, version)

            return web.json_response({"cached": name})

        except Exception as e:
            logger.error(f"Cache error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def list_models_handler(self, request: web.Request) -> web.Response:
        """List cached models."""
        models = self.runtime.list_models()
        return web.json_response({"models": models})

    async def sync_handler(self, request: web.Request) -> web.Response:
        """Trigger sync with cloud."""
        try:
            result = await self.runtime.sync()
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return web.json_response({"error": str(e)}, status=500)


def create_app(runtime: EdgeRuntime) -> web.Application:
    """Create edge server application."""
    server = EdgeServer(runtime)
    return server.app


async def run_server(
    config: EdgeConfig,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> None:
    """Run the edge server."""
    runtime = EdgeRuntime(config)

    try:
        await runtime.start()

        app = create_app(runtime)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(f"Edge server running on {host}:{port}")

        # Keep running
        while True:
            await asyncio.sleep(3600)

    except asyncio.CancelledError:
        pass
    finally:
        await runtime.stop()
