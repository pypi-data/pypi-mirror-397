"""
Time Travel Debugging API Routes.

Provides HTTP API for time travel debugging:
- Navigate execution history
- View state at any point
- Replay from any snapshot
- What-if analysis with modified inputs
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from flowmason_studio.models.time_travel import (
    DiffResponse,
    ExecutionSnapshot,
    ExecutionTimeline,
    JumpRequest,
    ReplayRequest,
    ReplayResult,
    SnapshotListResponse,
    SnapshotType,
    StateDiff,
    TimelineResponse,
    WhatIfRequest,
    WhatIfResult,
)
from flowmason_studio.services.time_travel_storage import get_time_travel_storage

router = APIRouter(prefix="/debug/time-travel", tags=["time-travel"])


# =============================================================================
# Response Models
# =============================================================================


class SnapshotResponse(BaseModel):
    """Response for a single snapshot."""

    snapshot: ExecutionSnapshot


class ReplayResponse(BaseModel):
    """Response for replay operations."""

    success: bool
    message: str
    result: Optional[ReplayResult] = None


class WhatIfResponse(BaseModel):
    """Response for what-if analysis."""

    success: bool
    message: str
    result: Optional[WhatIfResult] = None


# =============================================================================
# Timeline Navigation
# =============================================================================


@router.get("/runs/{run_id}/timeline", response_model=TimelineResponse)
async def get_run_timeline(run_id: str) -> TimelineResponse:
    """
    Get the execution timeline for a run.

    Returns all captured snapshots as a navigable timeline,
    showing stage progression and current position.
    """
    storage = get_time_travel_storage()
    timeline = storage.get_timeline(run_id)

    if timeline.total_snapshots == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshots found for run {run_id}"
        )

    return TimelineResponse(timeline=timeline)


@router.get("/runs/{run_id}/snapshots", response_model=SnapshotListResponse)
async def list_snapshots(
    run_id: str,
    snapshot_type: Optional[SnapshotType] = Query(
        None,
        description="Filter by snapshot type"
    ),
) -> SnapshotListResponse:
    """
    List all snapshots for a run.

    Optionally filter by snapshot type (stage_start, stage_complete, etc).
    """
    storage = get_time_travel_storage()
    snapshots = storage.get_snapshots_for_run(run_id, snapshot_type)

    return SnapshotListResponse(
        run_id=run_id,
        snapshots=snapshots,
        total=len(snapshots),
    )


@router.get("/snapshots/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot(snapshot_id: str) -> SnapshotResponse:
    """
    Get a specific snapshot by ID.

    Returns complete state at that point in execution.
    """
    storage = get_time_travel_storage()
    snapshot = storage.get_snapshot(snapshot_id)

    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    return SnapshotResponse(snapshot=snapshot)


@router.get(
    "/runs/{run_id}/stages/{stage_id}/snapshot",
    response_model=SnapshotResponse
)
async def get_stage_snapshot(
    run_id: str,
    stage_id: str,
    snapshot_type: Optional[SnapshotType] = Query(
        None,
        description="Specific snapshot type to retrieve"
    ),
) -> SnapshotResponse:
    """
    Get the snapshot at a specific stage.

    Useful for examining state before/after a particular stage.
    """
    storage = get_time_travel_storage()
    snapshot = storage.get_snapshot_at_stage(run_id, stage_id, snapshot_type)

    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot found for stage {stage_id}"
        )

    return SnapshotResponse(snapshot=snapshot)


# =============================================================================
# State Comparison
# =============================================================================


@router.get("/diff", response_model=DiffResponse)
async def get_state_diff(
    from_snapshot: str = Query(..., description="Starting snapshot ID"),
    to_snapshot: str = Query(..., description="Ending snapshot ID"),
) -> DiffResponse:
    """
    Get the difference between two snapshots.

    Shows what changed (outputs, variables, stages completed)
    between any two points in execution.
    """
    storage = get_time_travel_storage()
    diff = storage.get_diff(from_snapshot, to_snapshot)

    if not diff:
        raise HTTPException(
            status_code=404,
            detail="One or both snapshots not found"
        )

    return DiffResponse(diff=diff)


@router.get("/runs/{run_id}/diff/{stage_id}", response_model=DiffResponse)
async def get_stage_diff(
    run_id: str,
    stage_id: str,
) -> DiffResponse:
    """
    Get what changed during a specific stage execution.

    Shows the diff between stage_start and stage_complete snapshots.
    """
    storage = get_time_travel_storage()

    # Get before and after snapshots for this stage
    before = storage.get_snapshot_at_stage(
        run_id, stage_id, SnapshotType.STAGE_START
    )
    after = storage.get_snapshot_at_stage(
        run_id, stage_id, SnapshotType.STAGE_COMPLETE
    )

    if not before or not after:
        # Try to find any two consecutive snapshots
        snapshots = storage.get_snapshots_for_run(run_id)
        stage_snapshots = [s for s in snapshots if s.stage_id == stage_id]

        if len(stage_snapshots) < 2:
            raise HTTPException(
                status_code=404,
                detail=f"Need at least 2 snapshots for stage {stage_id} to compute diff"
            )

        before = stage_snapshots[0]
        after = stage_snapshots[-1]

    diff = storage.get_diff(before.id, after.id)

    if not diff:
        raise HTTPException(
            status_code=500,
            detail="Failed to compute diff"
        )

    return DiffResponse(diff=diff)


# =============================================================================
# Replay Operations
# =============================================================================


@router.post("/replay", response_model=ReplayResponse)
async def start_replay(request: ReplayRequest) -> ReplayResponse:
    """
    Start a replay from a specific snapshot.

    Allows re-executing the pipeline from any captured point,
    optionally with modified inputs for what-if analysis.
    """
    storage = get_time_travel_storage()

    # Get the snapshot
    snapshot = storage.get_snapshot(request.snapshot_id)
    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail="Snapshot not found"
        )

    # Create replay run
    result = storage.create_replay_run(
        original_run_id=snapshot.run_id,
        from_snapshot_id=request.snapshot_id,
        modifications=request.modified_inputs,
    )

    # TODO: Actually trigger the pipeline execution from this point
    # This would integrate with the execution controller

    return ReplayResponse(
        success=True,
        message=f"Replay started from snapshot {request.snapshot_id}",
        result=result,
    )


@router.get("/replay/{replay_id}", response_model=ReplayResponse)
async def get_replay_status(replay_id: str) -> ReplayResponse:
    """
    Get the status of a replay run.
    """
    storage = get_time_travel_storage()
    result = storage.get_replay_run(replay_id)

    if not result:
        raise HTTPException(status_code=404, detail="Replay run not found")

    return ReplayResponse(
        success=True,
        message=f"Replay status: {result.status}",
        result=result,
    )


# =============================================================================
# What-If Analysis
# =============================================================================


@router.post("/whatif", response_model=WhatIfResponse)
async def start_whatif_analysis(request: WhatIfRequest) -> WhatIfResponse:
    """
    Start a what-if analysis.

    Re-runs the pipeline from a snapshot with modified inputs
    and compares results to the original execution.
    """
    storage = get_time_travel_storage()

    # Get the original snapshot
    snapshot = storage.get_snapshot(request.snapshot_id)
    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail="Snapshot not found"
        )

    try:
        whatif_id, modified_snapshot = storage.create_whatif_analysis(
            original_run_id=snapshot.run_id,
            snapshot_id=request.snapshot_id,
            modifications=request.modifications,
        )

        # TODO: Actually execute the what-if run
        # This would integrate with the execution controller

        result = WhatIfResult(
            original_run_id=snapshot.run_id,
            whatif_run_id=whatif_id,
            snapshot_id=request.snapshot_id,
            modifications=request.modifications,
        )

        return WhatIfResponse(
            success=True,
            message=f"What-if analysis started with ID {whatif_id}",
            result=result,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Jump/Navigation Operations
# =============================================================================


@router.post("/jump", response_model=SnapshotResponse)
async def jump_to_snapshot(request: JumpRequest) -> SnapshotResponse:
    """
    Jump to a specific snapshot point.

    Returns the complete state at that point, which can be used
    to inspect values or start a replay.
    """
    storage = get_time_travel_storage()
    snapshot = storage.get_snapshot(request.snapshot_id)

    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    return SnapshotResponse(snapshot=snapshot)


@router.get("/runs/{run_id}/step-back", response_model=SnapshotResponse)
async def step_back(
    run_id: str,
    from_snapshot: Optional[str] = Query(
        None,
        description="Current snapshot ID (uses latest if not provided)"
    ),
) -> SnapshotResponse:
    """
    Step back to the previous snapshot.

    Navigates one step backward in the execution timeline.
    """
    storage = get_time_travel_storage()
    snapshots = storage.get_snapshots_for_run(run_id)

    if not snapshots:
        raise HTTPException(
            status_code=404,
            detail="No snapshots found for run"
        )

    # Find current position
    current_index = len(snapshots) - 1
    if from_snapshot:
        for i, snap in enumerate(snapshots):
            if snap.id == from_snapshot:
                current_index = i
                break

    # Step back
    if current_index <= 0:
        raise HTTPException(
            status_code=400,
            detail="Already at the beginning of execution"
        )

    previous_snapshot = snapshots[current_index - 1]
    return SnapshotResponse(snapshot=previous_snapshot)


@router.get("/runs/{run_id}/step-forward", response_model=SnapshotResponse)
async def step_forward(
    run_id: str,
    from_snapshot: Optional[str] = Query(
        None,
        description="Current snapshot ID (uses first if not provided)"
    ),
) -> SnapshotResponse:
    """
    Step forward to the next snapshot.

    Navigates one step forward in the execution timeline.
    """
    storage = get_time_travel_storage()
    snapshots = storage.get_snapshots_for_run(run_id)

    if not snapshots:
        raise HTTPException(
            status_code=404,
            detail="No snapshots found for run"
        )

    # Find current position
    current_index = 0
    if from_snapshot:
        for i, snap in enumerate(snapshots):
            if snap.id == from_snapshot:
                current_index = i
                break

    # Step forward
    if current_index >= len(snapshots) - 1:
        raise HTTPException(
            status_code=400,
            detail="Already at the end of execution"
        )

    next_snapshot = snapshots[current_index + 1]
    return SnapshotResponse(snapshot=next_snapshot)


# =============================================================================
# Cleanup
# =============================================================================


@router.delete("/runs/{run_id}/snapshots")
async def delete_run_snapshots(run_id: str) -> dict:
    """
    Delete all snapshots for a run.

    Frees up storage space for old runs.
    """
    storage = get_time_travel_storage()
    count = storage.delete_snapshots_for_run(run_id)

    return {
        "success": True,
        "message": f"Deleted {count} snapshots for run {run_id}",
        "deleted_count": count,
    }


@router.post("/cleanup")
async def cleanup_old_snapshots(
    days: int = Query(default=7, ge=1, le=90, description="Delete snapshots older than N days"),
) -> dict:
    """
    Clean up old snapshots.

    Removes snapshots older than the specified number of days.
    """
    storage = get_time_travel_storage()
    count = storage.cleanup_old_snapshots(days)

    return {
        "success": True,
        "message": f"Cleaned up {count} snapshots older than {days} days",
        "deleted_count": count,
    }
