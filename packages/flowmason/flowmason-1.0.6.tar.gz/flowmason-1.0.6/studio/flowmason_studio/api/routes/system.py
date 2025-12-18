"""
System Diagnostics API Routes.

Endpoints for system health, diagnostics, and admin operations:
- Detailed health checks
- System information
- Database status
- Provider connectivity
- Resource usage
"""

import os
import platform
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...services.storage import get_pipeline_storage, get_run_storage
from ..routes.registry import get_registry

router = APIRouter(prefix="/system", tags=["system"])


# ==================== Response Models ====================

class HealthStatus(BaseModel):
    """Component health status."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: Optional[str] = None
    latency_ms: Optional[float] = None


class SystemHealth(BaseModel):
    """Overall system health."""
    status: str  # "healthy", "degraded", "unhealthy"
    version: str
    uptime_seconds: Optional[float] = None
    components: List[HealthStatus]
    timestamp: str


class SystemInfo(BaseModel):
    """System information."""
    version: str
    python_version: str
    platform: str
    platform_version: str
    hostname: str
    working_directory: str
    environment: str  # "development", "staging", "production"


class DatabaseStatus(BaseModel):
    """Database status."""
    type: str  # "sqlite", "postgresql"
    connected: bool
    pipeline_count: int
    run_count: int
    size_bytes: Optional[int] = None


class ProviderStatus(BaseModel):
    """LLM provider status."""
    name: str
    configured: bool
    available: bool
    default: bool


class ResourceUsage(BaseModel):
    """Resource usage metrics."""
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    disk_usage_percent: Optional[float] = None
    open_file_count: Optional[int] = None


class DiagnosticsReport(BaseModel):
    """Complete diagnostics report."""
    health: SystemHealth
    system: SystemInfo
    database: DatabaseStatus
    providers: List[ProviderStatus]
    resources: ResourceUsage
    registry: Dict[str, Any]


# ==================== Helper Functions ====================

_start_time = datetime.utcnow()


def _get_uptime_seconds() -> float:
    """Get server uptime in seconds."""
    return (datetime.utcnow() - _start_time).total_seconds()


def _check_database_health() -> HealthStatus:
    """Check database connectivity."""
    try:
        import time
        start = time.time()

        storage = get_pipeline_storage()
        pipelines, _ = storage.list()  # type: ignore[misc]

        latency = (time.time() - start) * 1000

        return HealthStatus(
            name="database",
            status="healthy",
            message=f"{len(pipelines)} pipelines",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        return HealthStatus(
            name="database",
            status="unhealthy",
            message=str(e),
        )


def _check_registry_health() -> HealthStatus:
    """Check component registry."""
    try:
        registry = get_registry()
        components = registry.list_components()

        return HealthStatus(
            name="registry",
            status="healthy",
            message=f"{len(components)} components",
        )
    except Exception as e:
        return HealthStatus(
            name="registry",
            status="unhealthy",
            message=str(e),
        )


def _check_providers_health() -> HealthStatus:
    """Check LLM provider configuration."""
    try:
        from flowmason_core.providers import list_providers

        configured = 0
        for provider in list_providers():
            env_var = f"{provider.upper()}_API_KEY"
            if os.environ.get(env_var):
                configured += 1

        if configured == 0:
            return HealthStatus(
                name="providers",
                status="degraded",
                message="No providers configured",
            )

        return HealthStatus(
            name="providers",
            status="healthy",
            message=f"{configured} providers configured",
        )
    except Exception as e:
        return HealthStatus(
            name="providers",
            status="unhealthy",
            message=str(e),
        )


def _get_environment() -> str:
    """Determine running environment."""
    env = os.environ.get("FLOWMASON_ENV", "").lower()
    if env in ("production", "prod"):
        return "production"
    elif env in ("staging", "stage"):
        return "staging"
    return "development"


# ==================== Endpoints ====================

@router.get("/health", response_model=SystemHealth)
async def get_health():
    """
    Get detailed system health.

    Returns health status for all system components.
    """
    from ...api.app import API_VERSION

    components = [
        _check_database_health(),
        _check_registry_health(),
        _check_providers_health(),
    ]

    # Determine overall status
    if any(c.status == "unhealthy" for c in components):
        overall_status = "unhealthy"
    elif any(c.status == "degraded" for c in components):
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return SystemHealth(
        status=overall_status,
        version=API_VERSION,
        uptime_seconds=round(_get_uptime_seconds(), 1),
        components=components,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/info", response_model=SystemInfo)
async def get_system_info():
    """
    Get system information.

    Returns version, platform, and environment details.
    """
    from ...api.app import API_VERSION

    return SystemInfo(
        version=API_VERSION,
        python_version=platform.python_version(),
        platform=platform.system(),
        platform_version=platform.release(),
        hostname=platform.node(),
        working_directory=os.getcwd(),
        environment=_get_environment(),
    )


@router.get("/database", response_model=DatabaseStatus)
async def get_database_status():
    """
    Get database status.

    Returns database type, connection status, and statistics.
    """
    try:
        pipeline_storage = get_pipeline_storage()
        run_storage = get_run_storage()

        pipelines = pipeline_storage.list_pipelines()
        runs = run_storage.list_runs(limit=10000)

        # Check if PostgreSQL or SQLite
        db_url = os.environ.get("DATABASE_URL", "")
        db_type = "postgresql" if "postgresql" in db_url else "sqlite"

        # Get database size for SQLite
        size_bytes = None
        if db_type == "sqlite":
            db_path = os.path.join(os.getcwd(), ".flowmason", "flowmason.db")
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)

        return DatabaseStatus(
            type=db_type,
            connected=True,
            pipeline_count=len(pipelines),
            run_count=len(runs),
            size_bytes=size_bytes,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=List[ProviderStatus])
async def get_provider_status():
    """
    Get LLM provider status.

    Returns configuration and availability for each provider.
    """
    from flowmason_core.providers import list_providers

    provider_env_vars = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
    }

    default_provider = os.environ.get("FLOWMASON_DEFAULT_PROVIDER", "anthropic")

    results = []
    for provider in list_providers():
        env_var = provider_env_vars.get(provider, f"{provider.upper()}_API_KEY")
        api_key = os.environ.get(env_var)

        results.append(ProviderStatus(
            name=provider,
            configured=bool(api_key),
            available=bool(api_key),  # In future, could do actual connectivity check
            default=provider == default_provider,
        ))

    return results


@router.get("/resources", response_model=ResourceUsage)
async def get_resource_usage():
    """
    Get resource usage metrics.

    Returns memory, CPU, and disk usage if available.
    """
    try:
        import psutil

        process = psutil.Process()

        return ResourceUsage(
            memory_mb=round(process.memory_info().rss / 1024 / 1024, 2),
            cpu_percent=process.cpu_percent(interval=0.1),
            disk_usage_percent=psutil.disk_usage("/").percent,
            open_file_count=len(process.open_files()),
        )
    except ImportError:
        # psutil not installed
        return ResourceUsage()
    except Exception:
        return ResourceUsage()


@router.get("/diagnostics", response_model=DiagnosticsReport)
async def get_diagnostics():
    """
    Get complete diagnostics report.

    Returns comprehensive system information for troubleshooting.
    """
    health = await get_health()
    system = await get_system_info()
    database = await get_database_status()
    providers = await get_provider_status()
    resources = await get_resource_usage()

    # Registry info
    try:
        registry = get_registry()
        components = registry.list_components()

        categories = {}
        for comp in components:
            cat = comp.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1

        registry_info = {
            "total_components": len(components),
            "categories": categories,
        }
    except Exception:
        registry_info = {"error": "Unable to load registry"}

    return DiagnosticsReport(
        health=health,
        system=system,
        database=database,
        providers=providers,
        resources=resources,
        registry=registry_info,
    )


@router.get("/config")
async def get_config():
    """
    Get non-sensitive configuration.

    Returns environment configuration (no secrets).
    """
    return {
        "environment": _get_environment(),
        "default_provider": os.environ.get("FLOWMASON_DEFAULT_PROVIDER", "anthropic"),
        "scheduler_enabled": os.environ.get("FLOWMASON_SCHEDULER_ENABLED", "true").lower() == "true",
        "debug_mode": os.environ.get("FLOWMASON_DEBUG", "false").lower() == "true",
        "cors_origins": os.environ.get("FLOWMASON_CORS_ORIGINS", "*"),
        "log_level": os.environ.get("FLOWMASON_LOG_LEVEL", "INFO"),
    }


@router.post("/gc")
async def trigger_garbage_collection():
    """
    Trigger garbage collection.

    Forces Python garbage collection for memory cleanup.
    """
    import gc

    before = gc.get_count()
    collected = gc.collect()
    after = gc.get_count()

    return {
        "message": "Garbage collection completed",
        "objects_collected": collected,
        "generation_counts_before": before,
        "generation_counts_after": after,
    }


@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = 100,
    level: Optional[str] = None,
):
    """
    Get recent log entries.

    Returns recent log entries from the in-memory buffer.
    """
    try:
        from ...services.logging_service import get_logging_service

        service = get_logging_service()
        logs = service.get_recent_logs(limit=limit)  # type: ignore[attr-defined]

        if level:
            logs = [log for log in logs if log.get("level", "").upper() == level.upper()]

        return {
            "count": len(logs),
            "logs": logs,
        }
    except Exception as e:
        return {
            "error": str(e),
            "logs": [],
        }
