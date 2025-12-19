"""
Logs API Routes.

Provides endpoints for viewing and configuring application logs.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from flowmason_studio.services.logging_service import (
    LogCategory,
    LogLevel,
    get_logging_service,
)

router = APIRouter(prefix="/logs", tags=["Logs"])


# Request/Response Models
class LogEntryResponse(BaseModel):
    """Response model for a log entry."""
    id: str
    timestamp: str
    level: str
    category: str
    message: str
    logger_name: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None


class LogListResponse(BaseModel):
    """Response model for list of logs."""
    entries: List[LogEntryResponse]
    total: int
    limit: int
    offset: int


class LogConfigResponse(BaseModel):
    """Response model for log configuration."""
    global_level: str
    category_levels: Dict[str, str]
    max_entries: int
    enabled: bool
    categories: List[str]  # Available categories


class LogConfigUpdateRequest(BaseModel):
    """Request to update log configuration."""
    global_level: Optional[str] = Field(None, description="Global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    category_levels: Optional[Dict[str, str]] = Field(None, description="Per-category log levels")
    max_entries: Optional[int] = Field(None, ge=100, le=10000, description="Max entries to retain")
    enabled: Optional[bool] = Field(None, description="Enable/disable logging")


class LogStatsResponse(BaseModel):
    """Response with logging statistics."""
    total_entries: int
    entries_by_level: Dict[str, int]
    entries_by_category: Dict[str, int]


# Routes

@router.get("", response_model=LogListResponse)
def get_logs(
    limit: int = Query(100, ge=1, le=500, description="Maximum entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    level: Optional[str] = Query(None, description="Minimum log level filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    search: Optional[str] = Query(None, description="Search string in message"),
    since: Optional[str] = Query(None, description="Only entries after this ISO timestamp"),
):
    """
    Get log entries with optional filtering.

    Returns logs in reverse chronological order (most recent first).
    """
    service = get_logging_service()

    # Convert level string to enum if provided
    level_enum = None
    if level:
        try:
            level_enum = LogLevel(level.upper())
        except ValueError:
            pass

    entries = service.get_entries(
        limit=limit,
        offset=offset,
        level=level_enum,
        category=category,
        search=search,
        since=since,
    )

    return LogListResponse(
        entries=[LogEntryResponse(**e.to_dict()) for e in entries],
        total=service.get_entry_count(),
        limit=limit,
        offset=offset,
    )


@router.get("/config", response_model=LogConfigResponse)
def get_log_config():
    """Get current log configuration."""
    service = get_logging_service()
    config = service.config

    return LogConfigResponse(
        global_level=config.global_level.value,
        category_levels={k: v.value for k, v in config.category_levels.items()},
        max_entries=config.max_entries,
        enabled=config.enabled,
        categories=[c.value for c in LogCategory],
    )


@router.put("/config", response_model=LogConfigResponse)
def update_log_config(request: LogConfigUpdateRequest):
    """
    Update log configuration.

    Changes take effect immediately for new log entries.
    """
    service = get_logging_service()
    config = service.config

    if request.global_level is not None:
        try:
            config.global_level = LogLevel(request.global_level.upper())
        except ValueError:
            pass

    if request.category_levels is not None:
        for cat, level in request.category_levels.items():
            try:
                config.category_levels[cat] = LogLevel(level.upper())
            except ValueError:
                pass

    if request.max_entries is not None:
        config.max_entries = request.max_entries

    if request.enabled is not None:
        config.enabled = request.enabled

    service.set_config(config)

    return get_log_config()


@router.delete("")
def clear_logs():
    """Clear all log entries."""
    service = get_logging_service()
    service.clear()
    return {"message": "Logs cleared", "cleared": True}


@router.get("/stats", response_model=LogStatsResponse)
def get_log_stats():
    """Get logging statistics."""
    service = get_logging_service()
    entries = service.get_entries(limit=service.get_entry_count())

    # Count by level
    by_level: Dict[str, int] = {}
    by_category: Dict[str, int] = {}

    for entry in entries:
        by_level[entry.level] = by_level.get(entry.level, 0) + 1
        by_category[entry.category] = by_category.get(entry.category, 0) + 1

    return LogStatsResponse(
        total_entries=service.get_entry_count(),
        entries_by_level=by_level,
        entries_by_category=by_category,
    )


@router.get("/levels")
def get_available_levels():
    """Get available log levels."""
    return {
        "levels": [level.value for level in LogLevel],
        "categories": [cat.value for cat in LogCategory],
    }
