"""
Event Trigger API Routes.

Provides HTTP API for managing event-driven pipeline triggers.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from flowmason_studio.models.triggers import (
    CreateTriggerRequest,
    EventTrigger,
    TriggerEvent,
    TriggerEventListResponse,
    TriggerListResponse,
    TriggerStatsResponse,
    TriggerStatus,
    TriggerType,
    UpdateTriggerRequest,
)
from flowmason_studio.services.trigger_service import get_trigger_service
from flowmason_studio.services.trigger_storage import get_trigger_storage

router = APIRouter(prefix="/triggers", tags=["triggers"])


# =============================================================================
# Response Models
# =============================================================================


class TriggerResponse(BaseModel):
    """Response for trigger operations."""

    success: bool
    message: str
    trigger: Optional[EventTrigger] = None


class EmitEventRequest(BaseModel):
    """Request to emit a custom event."""

    endpoint: str
    data: Dict[str, Any]


class EmitEventResponse(BaseModel):
    """Response from emitting an event."""

    triggered_count: int
    events: List[TriggerEvent]


# =============================================================================
# Trigger CRUD Endpoints
# =============================================================================


@router.get("", response_model=TriggerListResponse)
async def list_triggers(
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
    trigger_type: Optional[TriggerType] = Query(None, description="Filter by type"),
    enabled_only: bool = Query(False, description="Only show enabled triggers"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Results per page"),
) -> TriggerListResponse:
    """List all event triggers with optional filtering."""
    storage = get_trigger_storage()

    triggers, total = storage.list_triggers(
        pipeline_id=pipeline_id,
        trigger_type=trigger_type,
        enabled_only=enabled_only,
        page=page,
        page_size=page_size,
    )

    return TriggerListResponse(
        triggers=triggers,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=EventTrigger)
async def create_trigger(request: CreateTriggerRequest) -> EventTrigger:
    """Create a new event trigger."""
    storage = get_trigger_storage()
    service = get_trigger_service()

    # Validate config based on type
    try:
        trigger = storage.create_trigger(
            name=request.name,
            description=request.description,
            pipeline_id=request.pipeline_id,
            trigger_type=request.trigger_type,
            config=request.config,
            enabled=request.enabled,
            max_concurrent=request.max_concurrent,
            cooldown_seconds=request.cooldown_seconds,
            default_inputs=request.default_inputs,
        )

        # Start the trigger if enabled
        if trigger.enabled:
            await service.add_trigger(trigger)

        return trigger
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{trigger_id}", response_model=EventTrigger)
async def get_trigger(trigger_id: str) -> EventTrigger:
    """Get a specific trigger by ID."""
    storage = get_trigger_storage()

    trigger = storage.get_trigger(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    return trigger


@router.put("/{trigger_id}", response_model=EventTrigger)
async def update_trigger(
    trigger_id: str,
    request: UpdateTriggerRequest,
) -> EventTrigger:
    """Update an existing trigger."""
    storage = get_trigger_storage()
    service = get_trigger_service()

    # Get existing trigger
    existing = storage.get_trigger(trigger_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Trigger not found")

    # Check if we need to restart the trigger
    needs_restart = (
        request.config is not None or
        request.enabled is not None
    )

    # Stop if needs restart
    if needs_restart and existing.enabled:
        await service.remove_trigger(trigger_id)

    # Update
    updated = storage.update_trigger(
        trigger_id,
        name=request.name,
        description=request.description,
        config=request.config,
        enabled=request.enabled,
        max_concurrent=request.max_concurrent,
        cooldown_seconds=request.cooldown_seconds,
        default_inputs=request.default_inputs,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Trigger not found")

    # Restart if needed and enabled
    if needs_restart and updated.enabled:
        await service.add_trigger(updated)

    return updated


@router.delete("/{trigger_id}", response_model=TriggerResponse)
async def delete_trigger(trigger_id: str) -> TriggerResponse:
    """Delete a trigger."""
    storage = get_trigger_storage()
    service = get_trigger_service()

    # Stop the trigger first
    await service.remove_trigger(trigger_id)

    # Delete from storage
    success = storage.delete_trigger(trigger_id)

    if not success:
        raise HTTPException(status_code=404, detail="Trigger not found")

    return TriggerResponse(
        success=True,
        message=f"Trigger {trigger_id} deleted",
    )


# =============================================================================
# Trigger Control Endpoints
# =============================================================================


@router.post("/{trigger_id}/pause", response_model=TriggerResponse)
async def pause_trigger(trigger_id: str) -> TriggerResponse:
    """Pause a trigger (stop watching but keep configuration)."""
    service = get_trigger_service()
    storage = get_trigger_storage()

    trigger = storage.get_trigger(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    await service.pause_trigger(trigger_id)

    return TriggerResponse(
        success=True,
        message=f"Trigger {trigger_id} paused",
        trigger=storage.get_trigger(trigger_id),
    )


@router.post("/{trigger_id}/resume", response_model=TriggerResponse)
async def resume_trigger(trigger_id: str) -> TriggerResponse:
    """Resume a paused trigger."""
    service = get_trigger_service()
    storage = get_trigger_storage()

    trigger = storage.get_trigger(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    await service.resume_trigger(trigger_id)

    return TriggerResponse(
        success=True,
        message=f"Trigger {trigger_id} resumed",
        trigger=storage.get_trigger(trigger_id),
    )


@router.post("/{trigger_id}/test", response_model=TriggerEvent)
async def test_trigger(
    trigger_id: str,
    test_data: Optional[Dict[str, Any]] = None,
) -> TriggerEvent:
    """Test a trigger by simulating an event."""
    storage = get_trigger_storage()
    service = get_trigger_service()

    trigger = storage.get_trigger(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    # Create test event data
    event_data = test_data or {}
    event_data["_test"] = True

    # Fire the trigger
    event = await service._fire_trigger(
        trigger_id,
        "test",
        event_data
    )

    if not event:
        raise HTTPException(
            status_code=400,
            detail="Trigger could not be fired (disabled or in cooldown)"
        )

    return event


# =============================================================================
# Trigger Events Endpoints
# =============================================================================


@router.get("/{trigger_id}/events", response_model=TriggerEventListResponse)
async def list_trigger_events(
    trigger_id: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> TriggerEventListResponse:
    """List events for a specific trigger."""
    storage = get_trigger_storage()

    # Verify trigger exists
    trigger = storage.get_trigger(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    events, total = storage.list_events(
        trigger_id=trigger_id,
        status=status,
        page=page,
        page_size=page_size,
    )

    return TriggerEventListResponse(
        events=events,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/events", response_model=TriggerEventListResponse)
async def list_all_events(
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
    status: Optional[str] = Query(None, description="Filter by status"),
    since: Optional[datetime] = Query(None, description="Events since this time"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> TriggerEventListResponse:
    """List all trigger events across all triggers."""
    storage = get_trigger_storage()

    events, total = storage.list_events(
        pipeline_id=pipeline_id,
        status=status,
        since=since,
        page=page,
        page_size=page_size,
    )

    return TriggerEventListResponse(
        events=events,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/events/{event_id}", response_model=TriggerEvent)
async def get_event(event_id: str) -> TriggerEvent:
    """Get a specific trigger event."""
    storage = get_trigger_storage()

    event = storage.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


# =============================================================================
# Custom Event Emission
# =============================================================================


@router.post("/emit", response_model=EmitEventResponse)
async def emit_custom_event(request: EmitEventRequest) -> EmitEventResponse:
    """Emit a custom event to trigger matching listeners."""
    service = get_trigger_service()

    events = await service.emit_custom_event(
        endpoint=request.endpoint,
        event_data=request.data,
    )

    return EmitEventResponse(
        triggered_count=len(events),
        events=events,
    )


@router.post("/emit/mcp", response_model=EmitEventResponse)
async def emit_mcp_event(
    server_name: str,
    event_type: str,
    event_data: Dict[str, Any],
) -> EmitEventResponse:
    """Emit an MCP event to trigger matching listeners."""
    service = get_trigger_service()
    storage = get_trigger_storage()

    # Get matching triggers
    triggers = storage.get_active_triggers_by_type(TriggerType.MCP_EVENT)
    events: List[TriggerEvent] = []

    await service.emit_mcp_event(server_name, event_type, event_data)

    # Note: The actual events are created inside emit_mcp_event
    # For now, return empty events list as they're async

    return EmitEventResponse(
        triggered_count=0,  # Will be updated asynchronously
        events=events,
    )


# =============================================================================
# Statistics
# =============================================================================


@router.get("/stats", response_model=TriggerStatsResponse)
async def get_trigger_stats() -> TriggerStatsResponse:
    """Get trigger statistics."""
    storage = get_trigger_storage()
    stats = storage.get_stats()

    return TriggerStatsResponse(
        total_triggers=stats["total_triggers"],
        active_triggers=stats["active_triggers"],
        paused_triggers=stats["paused_triggers"],
        error_triggers=stats["error_triggers"],
        total_events_24h=stats["total_events_24h"],
        successful_events_24h=stats["successful_events_24h"],
        failed_events_24h=stats["failed_events_24h"],
        triggers_by_type=stats["triggers_by_type"],
    )


# =============================================================================
# Pipeline Triggers Convenience
# =============================================================================


@router.get("/pipeline/{pipeline_id}", response_model=TriggerListResponse)
async def get_pipeline_triggers(
    pipeline_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> TriggerListResponse:
    """Get all triggers for a specific pipeline."""
    storage = get_trigger_storage()

    triggers, total = storage.list_triggers(
        pipeline_id=pipeline_id,
        page=page,
        page_size=page_size,
    )

    return TriggerListResponse(
        triggers=triggers,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/type/{trigger_type}", response_model=TriggerListResponse)
async def get_triggers_by_type(
    trigger_type: TriggerType,
    enabled_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> TriggerListResponse:
    """Get all triggers of a specific type."""
    storage = get_trigger_storage()

    triggers, total = storage.list_triggers(
        trigger_type=trigger_type,
        enabled_only=enabled_only,
        page=page,
        page_size=page_size,
    )

    return TriggerListResponse(
        triggers=triggers,
        total=total,
        page=page,
        page_size=page_size,
    )
