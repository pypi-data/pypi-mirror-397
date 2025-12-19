"""
Schedule API Routes.

Manage scheduled pipeline runs with cron expressions.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

from flowmason_studio.services.schedule_storage import (
    ScheduledPipeline,
    get_schedule_storage,
)

router = APIRouter(prefix="/schedules", tags=["schedules"])


# Request/Response Models
class CreateScheduleRequest(BaseModel):
    """Request to create a new schedule."""

    name: str = Field(..., description="Schedule name")
    pipeline_id: str = Field(..., description="Pipeline to run")
    pipeline_name: str = Field(..., description="Pipeline name for display")
    cron_expression: str = Field(
        ...,
        description="Cron expression (e.g., '0 9 * * *' for daily at 9am)",
        examples=["0 9 * * *", "*/15 * * * *", "0 0 * * 0"],
    )
    inputs: Optional[Dict[str, Any]] = Field(
        default=None, description="Inputs to pass to pipeline"
    )
    timezone: str = Field(default="UTC", description="Timezone for schedule")
    description: str = Field(default="", description="Schedule description")
    enabled: bool = Field(default=True, description="Whether schedule is active")


class UpdateScheduleRequest(BaseModel):
    """Request to update a schedule."""

    name: Optional[str] = None
    cron_expression: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None


class ScheduleResponse(BaseModel):
    """Schedule response."""

    id: str
    name: str
    pipeline_id: str
    pipeline_name: str
    org_id: str
    cron_expression: str
    inputs: Dict[str, Any]
    enabled: bool
    timezone: str
    description: str
    created_at: str
    updated_at: str
    next_run_at: Optional[str]
    last_run_at: Optional[str]
    last_run_id: Optional[str]
    last_run_status: Optional[str]
    run_count: int
    failure_count: int

    @classmethod
    def from_schedule(cls, schedule: ScheduledPipeline) -> "ScheduleResponse":
        return cls(
            id=schedule.id,
            name=schedule.name,
            pipeline_id=schedule.pipeline_id,
            pipeline_name=schedule.pipeline_name,
            org_id=schedule.org_id,
            cron_expression=schedule.cron_expression,
            inputs=schedule.inputs,
            enabled=schedule.enabled,
            timezone=schedule.timezone,
            description=schedule.description,
            created_at=schedule.created_at,
            updated_at=schedule.updated_at,
            next_run_at=schedule.next_run_at,
            last_run_at=schedule.last_run_at,
            last_run_id=schedule.last_run_id,
            last_run_status=schedule.last_run_status,
            run_count=schedule.run_count,
            failure_count=schedule.failure_count,
        )


class ScheduleListResponse(BaseModel):
    """List schedules response."""

    schedules: List[ScheduleResponse]
    total: int
    limit: int
    offset: int


class ScheduleRunResponse(BaseModel):
    """Schedule run history item."""

    id: str
    schedule_id: str
    run_id: str
    scheduled_at: str
    started_at: str
    status: str
    error_message: Optional[str]


class TriggerScheduleResponse(BaseModel):
    """Response when manually triggering a schedule."""

    run_id: str
    schedule_id: str
    message: str


# Routes
@router.post("", response_model=ScheduleResponse)
async def create_schedule(
    request: CreateScheduleRequest,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """
    Create a new scheduled pipeline run.

    Schedules are defined using cron expressions:
    - `0 9 * * *` - Daily at 9:00 AM
    - `*/15 * * * *` - Every 15 minutes
    - `0 0 * * 0` - Weekly on Sunday at midnight
    - `0 0 1 * *` - Monthly on the 1st at midnight
    """
    storage = get_schedule_storage()

    schedule = storage.create(
        name=request.name,
        pipeline_id=request.pipeline_id,
        pipeline_name=request.pipeline_name,
        org_id=org_id,
        cron_expression=request.cron_expression,
        inputs=request.inputs,
        timezone=request.timezone,
        description=request.description,
        enabled=request.enabled,
    )

    return ScheduleResponse.from_schedule(schedule)


@router.get("", response_model=ScheduleListResponse)
async def list_schedules(
    org_id: str = Query(default="default", description="Organization ID"),
    pipeline_id: Optional[str] = Query(default=None, description="Filter by pipeline"),
    enabled_only: bool = Query(default=False, description="Only show enabled schedules"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """List all schedules for an organization."""
    storage = get_schedule_storage()

    schedules, total = storage.list(
        org_id=org_id,
        pipeline_id=pipeline_id,
        enabled_only=enabled_only,
        limit=limit,
        offset=offset,
    )

    return ScheduleListResponse(
        schedules=[ScheduleResponse.from_schedule(s) for s in schedules],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Get a schedule by ID."""
    storage = get_schedule_storage()

    schedule = storage.get(schedule_id, org_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return ScheduleResponse.from_schedule(schedule)


@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    request: UpdateScheduleRequest,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Update a schedule."""
    storage = get_schedule_storage()

    # Check exists
    existing = storage.get(schedule_id, org_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule = storage.update(
        schedule_id=schedule_id,
        org_id=org_id,
        name=request.name,
        cron_expression=request.cron_expression,
        inputs=request.inputs,
        enabled=request.enabled,
        timezone=request.timezone,
        description=request.description,
    )

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return ScheduleResponse.from_schedule(schedule)


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Delete a schedule."""
    storage = get_schedule_storage()

    deleted = storage.delete(schedule_id, org_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return {"deleted": True, "schedule_id": schedule_id}


@router.post("/{schedule_id}/enable", response_model=ScheduleResponse)
async def enable_schedule(
    schedule_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Enable a schedule."""
    storage = get_schedule_storage()

    schedule = storage.update(schedule_id=schedule_id, org_id=org_id, enabled=True)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return ScheduleResponse.from_schedule(schedule)


@router.post("/{schedule_id}/disable", response_model=ScheduleResponse)
async def disable_schedule(
    schedule_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Disable a schedule."""
    storage = get_schedule_storage()

    schedule = storage.update(schedule_id=schedule_id, org_id=org_id, enabled=False)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return ScheduleResponse.from_schedule(schedule)


@router.post("/{schedule_id}/trigger", response_model=TriggerScheduleResponse)
async def trigger_schedule(
    schedule_id: str,
    background_tasks: BackgroundTasks,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """
    Manually trigger a scheduled pipeline run.

    This runs the pipeline immediately, regardless of the schedule.
    The next scheduled run time is not affected.
    """
    from datetime import datetime

    storage = get_schedule_storage()

    schedule = storage.get(schedule_id, org_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Execute the pipeline
    from flowmason_studio.services.execution_controller import create_controller
    from flowmason_studio.services.storage import get_pipeline_storage

    # Load pipeline
    pipeline_storage = get_pipeline_storage()
    pipeline = pipeline_storage.get(schedule.pipeline_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline {schedule.pipeline_id} not found",
        )

    # Create run
    import uuid

    run_id = str(uuid.uuid4())

    # Record the run
    scheduled_at = datetime.utcnow().isoformat()
    storage.record_run(
        schedule_id=schedule_id,
        run_id=run_id,
        scheduled_at=scheduled_at,
        status="running",
    )

    # Execute in background
    async def execute_scheduled_run():
        try:
            controller = await create_controller(
                run_id=run_id,
                pipeline_id=schedule.pipeline_id,
                org_id=org_id,
            )

            await controller.execute_pipeline(
                pipeline_config=pipeline,
                inputs=schedule.inputs,
            )

            storage.update_run_status(
                schedule_id=schedule_id,
                run_id=run_id,
                status="completed",
            )
        except Exception as e:
            storage.update_run_status(
                schedule_id=schedule_id,
                run_id=run_id,
                status="failed",
                error_message=str(e),
            )

    background_tasks.add_task(execute_scheduled_run)

    return TriggerScheduleResponse(
        run_id=run_id,
        schedule_id=schedule_id,
        message="Pipeline execution started",
    )


@router.get("/{schedule_id}/history", response_model=List[ScheduleRunResponse])
async def get_schedule_history(
    schedule_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
    limit: int = Query(default=50, ge=1, le=500),
):
    """Get run history for a schedule."""
    storage = get_schedule_storage()

    # Verify schedule exists and belongs to org
    schedule = storage.get(schedule_id, org_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    runs = storage.get_run_history(schedule_id, limit)

    return [
        ScheduleRunResponse(
            id=run.id,
            schedule_id=run.schedule_id,
            run_id=run.run_id,
            scheduled_at=run.scheduled_at,
            started_at=run.started_at,
            status=run.status,
            error_message=run.error_message,
        )
        for run in runs
    ]


@router.get("/cron/validate")
async def validate_cron(
    expression: str = Query(..., description="Cron expression to validate"),
    timezone: str = Query(default="UTC", description="Timezone"),
):
    """
    Validate a cron expression and show next run times.

    Returns the next 5 scheduled run times.
    """
    try:
        from croniter import croniter  # type: ignore[import-untyped]
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="croniter package not installed. Install with: pip install croniter",
        )

    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo

        try:
            tz = ZoneInfo(timezone)
            now = datetime.now(tz)
        except Exception:
            now = datetime.utcnow()

        cron = croniter(expression, now)

        next_runs = []
        for _ in range(5):
            next_run = cron.get_next(datetime)
            next_runs.append(next_run.isoformat())

        return {
            "valid": True,
            "expression": expression,
            "timezone": timezone,
            "next_runs": next_runs,
        }

    except Exception as e:
        return {
            "valid": False,
            "expression": expression,
            "error": str(e),
        }
