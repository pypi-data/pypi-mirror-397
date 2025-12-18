"""
Time Travel Debugging Models.

Models for capturing and navigating execution history:
- Execution snapshots at each stage
- State diffs between snapshots
- Replay points for re-execution
- Input modification for what-if analysis
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SnapshotType(str, Enum):
    """Types of execution snapshots."""

    STAGE_START = "stage_start"       # Before stage execution
    STAGE_COMPLETE = "stage_complete"  # After stage execution
    STAGE_FAILED = "stage_failed"      # Stage failed
    CHECKPOINT = "checkpoint"          # Manual checkpoint
    BRANCH_POINT = "branch_point"      # Where execution branched


class ExecutionSnapshot(BaseModel):
    """
    A snapshot of execution state at a specific point.

    Captures all information needed to replay from this point.
    """

    id: str = Field(description="Unique snapshot ID")
    run_id: str = Field(description="Run this snapshot belongs to")
    pipeline_id: str = Field(description="Pipeline being executed")

    # Position in execution
    stage_id: str = Field(description="Stage ID at this snapshot")
    stage_name: Optional[str] = Field(default=None, description="Human-readable stage name")
    stage_index: int = Field(description="Index of stage in execution order")
    snapshot_type: SnapshotType = Field(description="Type of snapshot")

    # Timing
    timestamp: str = Field(description="When this snapshot was captured")
    duration_ms: Optional[int] = Field(default=None, description="Duration to this point")

    # State
    pipeline_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original pipeline inputs"
    )
    stage_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Inputs to this stage"
    )
    stage_outputs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Outputs from this stage (if complete)"
    )
    accumulated_outputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="All outputs accumulated up to this point"
    )
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline variables at this point"
    )

    # Execution context
    completed_stages: List[str] = Field(
        default_factory=list,
        description="Stage IDs completed before this snapshot"
    )
    pending_stages: List[str] = Field(
        default_factory=list,
        description="Stage IDs remaining to execute"
    )

    # Error info (for failed snapshots)
    error: Optional[str] = Field(default=None, description="Error message if failed")
    error_type: Optional[str] = Field(default=None, description="Error classification")

    # Metadata
    component_type: Optional[str] = Field(default=None, description="Component type of stage")
    provider: Optional[str] = Field(default=None, description="LLM provider if applicable")
    model: Optional[str] = Field(default=None, description="Model used if applicable")
    token_usage: Optional[Dict[str, int]] = Field(
        default=None,
        description="Token usage at this point"
    )


class StateDiff(BaseModel):
    """
    Difference between two execution states.

    Used to show what changed between snapshots.
    """

    from_snapshot_id: str
    to_snapshot_id: str

    # Changes
    added_outputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="New outputs added"
    )
    modified_outputs: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Outputs that changed (old/new values)"
    )
    removed_outputs: List[str] = Field(
        default_factory=list,
        description="Output keys that were removed"
    )

    added_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="New variables added"
    )
    modified_variables: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Variables that changed"
    )

    stages_completed: List[str] = Field(
        default_factory=list,
        description="Stages completed between snapshots"
    )

    duration_ms: int = Field(default=0, description="Time between snapshots")
    tokens_used: int = Field(default=0, description="Tokens used between snapshots")


class ReplayRequest(BaseModel):
    """Request to replay execution from a snapshot."""

    snapshot_id: str = Field(description="Snapshot to replay from")
    modified_inputs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Modified inputs for what-if analysis"
    )
    modified_variables: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Modified variables to inject"
    )
    stop_at_stage: Optional[str] = Field(
        default=None,
        description="Stage ID to stop at (for partial replay)"
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable step-through debugging during replay"
    )


class ReplayResult(BaseModel):
    """Result of a replay operation."""

    original_run_id: str
    replay_run_id: str
    from_snapshot_id: str
    status: str  # running, completed, failed

    # What changed
    modifications_applied: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input/variable modifications that were applied"
    )

    # Comparison
    output_differences: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Differences from original run"
    )

    stages_executed: List[str] = Field(
        default_factory=list,
        description="Stages executed during replay"
    )

    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None


class TimelineEntry(BaseModel):
    """An entry in the execution timeline."""

    snapshot_id: str
    stage_id: str
    stage_name: Optional[str] = None
    component_type: Optional[str] = None
    snapshot_type: SnapshotType
    timestamp: str
    duration_ms: Optional[int] = None
    status: str  # pending, running, completed, failed
    is_current: bool = False  # Is this the current position?

    # Quick preview
    has_outputs: bool = False
    output_preview: Optional[str] = Field(
        default=None,
        description="Short preview of output"
    )
    error_preview: Optional[str] = Field(
        default=None,
        description="Short error preview if failed"
    )


class ExecutionTimeline(BaseModel):
    """Complete execution timeline for a run."""

    run_id: str
    pipeline_id: str
    total_snapshots: int
    total_duration_ms: Optional[int] = None
    status: str

    entries: List[TimelineEntry] = Field(default_factory=list)

    # Navigation
    current_index: int = 0
    can_step_back: bool = False
    can_step_forward: bool = False


class JumpRequest(BaseModel):
    """Request to jump to a specific point in execution."""

    snapshot_id: str = Field(description="Snapshot to jump to")
    restore_state: bool = Field(
        default=True,
        description="Whether to restore full state at this point"
    )


class WhatIfRequest(BaseModel):
    """Request for what-if analysis."""

    snapshot_id: str = Field(description="Snapshot to start from")
    modifications: Dict[str, Any] = Field(
        description="Input/variable modifications to apply"
    )
    compare_with_original: bool = Field(
        default=True,
        description="Compare results with original execution"
    )


class WhatIfResult(BaseModel):
    """Result of what-if analysis."""

    original_run_id: str
    whatif_run_id: str
    snapshot_id: str

    modifications: Dict[str, Any]

    # Results
    original_output: Optional[Any] = None
    modified_output: Optional[Any] = None

    # Comparison
    outputs_identical: bool = False
    differences: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of differences found"
    )

    # Performance comparison
    original_duration_ms: Optional[int] = None
    modified_duration_ms: Optional[int] = None

    # Cost comparison
    original_cost: Optional[float] = None
    modified_cost: Optional[float] = None


# API Request/Response Models

class SnapshotListResponse(BaseModel):
    """Response for listing snapshots."""

    run_id: str
    snapshots: List[ExecutionSnapshot]
    total: int


class TimelineResponse(BaseModel):
    """Response for timeline request."""

    timeline: ExecutionTimeline


class DiffResponse(BaseModel):
    """Response for diff request."""

    diff: StateDiff
