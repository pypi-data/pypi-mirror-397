"""
FlowMason Studio FastAPI Application.

Main entry point for the Studio API server.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from flowmason_core.config.installation import get_installation_config
from flowmason_core.registry import ComponentRegistry

from flowmason_studio.api.routes import (
    allowlist,
    analytics,
    auth,
    codegen,
    collaboration,
    component_visual,
    copilot,
    diff,
    execution,
    experiments,
    gallery,
    generate,
    inheritance,
    kubernetes,
    logs,
    marketplace,
    mcp,
    mcp_assistant,
    multi_region,
    natural,
    nl_builder,
    oauth,
    packages,
    permissions,
    pipelines,
    private_registry,
    prompts,
    providers,
    registry,
    saml,
    schedules,
    secrets,
    settings,
    system,
    templates,
    tests,
    time_travel,
    tokens,
    triggers,
    usage,
    versions,
    visualization,
    webhooks,
)
from flowmason_studio.api.routes.registry import set_registry
from flowmason_studio.api.websocket import get_connection_manager, websocket_handler
from flowmason_studio.services.logging_service import LogCategory, get_logging_service, log_info
from flowmason_studio.services.storage import (
    PipelineStorage,
    RunStorage,
    set_pipeline_storage,
    set_run_storage,
)

# Application metadata
API_TITLE = "FlowMason Studio API"
API_DESCRIPTION = """
FlowMason Studio provides an HTTP API for managing AI workflow pipelines.

## Features

- **Component Registry**: Browse and manage available components
- **Pipeline Management**: Create, edit, and version pipelines
- **Execution**: Run pipelines and monitor execution
- **Observability**: View execution traces and metrics
"""
API_VERSION = "1.0.11"


def create_app(
    component_registry: Optional[ComponentRegistry] = None,
    package_dirs: Optional[list[Path]] = None,
    enable_cors: bool = True,
    cors_origins: Optional[list[str]] = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        component_registry: Pre-configured registry (creates new if None)
        package_dirs: Directories to scan for .fmpkg packages
        enable_cors: Whether to enable CORS middleware
        cors_origins: Allowed CORS origins (defaults to ["*"])

    Returns:
        Configured FastAPI application
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan handler for startup/shutdown."""
        # Startup
        nonlocal component_registry

        # Create registry if not provided
        if component_registry is None:
            component_registry = ComponentRegistry()

            # Auto-discover built-in lab components
            component_registry.auto_discover()

            # Scan package directories if provided
            if package_dirs:
                for pkg_dir in package_dirs:
                    if pkg_dir.exists():
                        component_registry.scan_packages(pkg_dir)

        # Set global registry
        set_registry(component_registry)

        # Initialize database and storage (SQLite for dev, can switch to PostgreSQL)
        from flowmason_studio.services.database import close_connection, get_connection
        get_connection()  # This initializes the database schema
        set_pipeline_storage(PipelineStorage())
        set_run_storage(RunStorage())

        # Initialize logging service
        get_logging_service()
        log_info(LogCategory.SYSTEM, f"FlowMason Studio API v{API_VERSION} started")

        # Initialize auth service (creates tables)
        from flowmason_studio.auth import get_auth_service
        get_auth_service()
        log_info(LogCategory.SYSTEM, "Authentication service initialized")

        # Register installation state (port/host from env vars if available)
        import os
        install_config = get_installation_config()
        install_config.register_installation(version=API_VERSION)
        install_config.update_studio_state(
            running=True,
            port=int(os.environ.get("FLOWMASON_PORT", 8999)),
            host=os.environ.get("FLOWMASON_HOST", "127.0.0.1"),
        )
        log_info(LogCategory.SYSTEM, "Installation state registered")

        # Start background scheduler for cron-scheduled pipelines
        from flowmason_studio.services.scheduler import start_scheduler, stop_scheduler
        scheduler_enabled = os.environ.get("FLOWMASON_SCHEDULER_ENABLED", "true").lower() == "true"
        if scheduler_enabled:
            await start_scheduler()
            log_info(LogCategory.SYSTEM, "Pipeline scheduler started")

        # Start event trigger service
        from flowmason_studio.services.trigger_service import start_trigger_service, stop_trigger_service
        triggers_enabled = os.environ.get("FLOWMASON_TRIGGERS_ENABLED", "true").lower() == "true"
        if triggers_enabled:
            await start_trigger_service()
            log_info(LogCategory.SYSTEM, "Event trigger service started")

        yield

        # Shutdown trigger service
        if triggers_enabled:
            await stop_trigger_service()
            log_info(LogCategory.SYSTEM, "Event trigger service stopped")

        # Shutdown scheduler
        if scheduler_enabled:
            await stop_scheduler()
            log_info(LogCategory.SYSTEM, "Pipeline scheduler stopped")

        # Shutdown - clear server state and cleanup database connection
        install_config.update_studio_state(running=False)
        close_connection()

    # Create app
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        lifespan=lifespan,
    )

    # Add CORS middleware
    if enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins or ["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include routers
    app.include_router(auth.router, prefix="/api/v1")  # Auth first for bootstrap
    app.include_router(saml.router, prefix="/api/v1")  # SAML/SSO authentication
    app.include_router(registry.router, prefix="/api/v1")
    app.include_router(pipelines.router, prefix="/api/v1")
    app.include_router(execution.router, prefix="/api/v1")
    app.include_router(providers.router, prefix="/api/v1")
    app.include_router(settings.router, prefix="/api/v1")
    app.include_router(logs.router, prefix="/api/v1")
    app.include_router(templates.router, prefix="/api/v1")
    app.include_router(tests.router, prefix="/api/v1")
    app.include_router(allowlist.router, prefix="/api/v1")
    app.include_router(allowlist.connections_router, prefix="/api/v1")
    app.include_router(allowlist.deliveries_router, prefix="/api/v1")
    app.include_router(secrets.router, prefix="/api/v1")
    app.include_router(webhooks.router, prefix="/api/v1")
    app.include_router(webhooks.trigger_router, prefix="/api/v1")
    app.include_router(usage.router, prefix="/api/v1")
    app.include_router(schedules.router, prefix="/api/v1")
    app.include_router(versions.router, prefix="/api/v1")
    app.include_router(prompts.router, prefix="/api/v1")
    app.include_router(gallery.router, prefix="/api/v1")
    app.include_router(oauth.router, prefix="/api/v1")
    app.include_router(tokens.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1")
    app.include_router(system.router, prefix="/api/v1")
    app.include_router(component_visual.router, prefix="/api/v1")
    app.include_router(collaboration.router, prefix="/api/v1")
    app.include_router(marketplace.router, prefix="/api/v1")
    app.include_router(multi_region.router, prefix="/api/v1")
    app.include_router(mcp.router, prefix="/api/v1")
    app.include_router(mcp_assistant.router, prefix="/api/v1")
    app.include_router(packages.router, prefix="/api/v1")
    app.include_router(private_registry.router, prefix="/api/v1")
    app.include_router(permissions.router, prefix="/api/v1")
    app.include_router(triggers.router, prefix="/api/v1")
    app.include_router(experiments.router, prefix="/api/v1")
    app.include_router(time_travel.router, prefix="/api/v1")
    app.include_router(nl_builder.router, prefix="/api/v1")
    app.include_router(natural.router, prefix="/api/v1")
    app.include_router(generate.router, prefix="/api/v1")
    app.include_router(visualization.router, prefix="/api/v1")
    app.include_router(codegen.router, prefix="/api/v1")
    app.include_router(inheritance.router, prefix="/api/v1")
    app.include_router(diff.router, prefix="/api/v1")
    app.include_router(kubernetes.router, prefix="/api/v1")
    app.include_router(copilot.router, prefix="/api/v1")  # P5.3 AI Copilot

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": API_VERSION}

    # WebSocket endpoint for real-time execution updates
    @app.websocket("/api/v1/ws/runs")
    async def websocket_runs_endpoint(websocket: WebSocket):
        """
        WebSocket endpoint for real-time execution updates.

        Protocol:
        - Send {"type": "subscribe", "run_id": "..."} to subscribe to run updates
        - Send {"type": "unsubscribe", "run_id": "..."} to unsubscribe
        - Send {"type": "ping"} for keepalive (receives pong response)
        - Send {"type": "pause", "run_id": "..."} to pause execution
        - Send {"type": "resume", "run_id": "..."} to resume execution
        - Send {"type": "step", "run_id": "..."} to step to next stage

        Events received:
        - connected: Connection established with client_id
        - subscribed: Successfully subscribed to a run
        - run_started: Pipeline execution started
        - stage_started: Stage execution started
        - stage_completed: Stage execution completed
        - stage_failed: Stage execution failed
        - execution_paused: Execution paused at breakpoint or by command
        - run_completed: Pipeline execution completed
        - run_failed: Pipeline execution failed
        """
        manager = get_connection_manager()
        await websocket_handler(websocket, manager)

    # Serve built frontend static files
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        # Mount static assets (CSS, JS)
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        # Serve index.html for root
        @app.get("/", include_in_schema=False)
        async def serve_spa_root():
            """Serve the frontend SPA."""
            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/docs")

        # Catch-all route for SPA client-side routing
        # Must be last to not interfere with API routes
        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa_fallback(full_path: str):
            """Serve index.html for all non-API routes (SPA fallback)."""
            # Don't serve SPA for API routes or docs
            if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "health")):
                from fastapi.responses import JSONResponse
                return JSONResponse({"error": "Not found"}, status_code=404)

            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            from fastapi.responses import JSONResponse
            return JSONResponse({"error": "Frontend not found"}, status_code=404)
    else:
        # Fallback when no frontend is built - redirect to API docs
        @app.get("/", include_in_schema=False)
        async def root():
            """Redirect root to API documentation."""
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/docs")

    return app


# Default app instance for uvicorn
app = create_app()


def run_server(
    host: str = "127.0.0.1",
    port: int = 8999,
    reload: bool = False,
    package_dirs: Optional[list[Path]] = None,
):
    """
    Run the Studio API server.

    Args:
        host: Host to bind to
        port: Port to listen on
        reload: Enable auto-reload for development
        package_dirs: Directories to scan for packages
    """
    import os

    import uvicorn

    # Set environment variables for the lifespan handler to pick up
    os.environ["FLOWMASON_HOST"] = host
    os.environ["FLOWMASON_PORT"] = str(port)

    # Note: When using reload, we can't pass custom app instance
    # Package dirs would need to be configured via environment
    uvicorn.run(
        "flowmason_studio.api.app:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    import os
    host = os.environ.get("FLOWMASON_HOST", "127.0.0.1")
    port = int(os.environ.get("FLOWMASON_PORT", "8999"))
    run_server(host=host, port=port)
