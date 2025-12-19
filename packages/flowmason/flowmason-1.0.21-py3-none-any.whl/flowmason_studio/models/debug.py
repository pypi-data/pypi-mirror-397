"""
Debug State Models for FlowMason Studio.

Models for managing debug execution state including:
- Debug mode (running, paused, stepping, stopped)
- Breakpoints
- Current execution position
- Auto-resume timeout
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DebugMode(str, Enum):
    """Execution debug mode states."""
    RUNNING = "running"      # Normal execution
    PAUSED = "paused"        # Paused by user or breakpoint
    STEPPING = "stepping"    # Step-through mode (pause after each stage)
    STOPPED = "stopped"      # Execution stopped/cancelled


class ExceptionBreakpointFilter(str, Enum):
    """Exception filter types for pause-on-exception."""
    ALL = "all"                    # Pause on all errors
    UNCAUGHT = "uncaught"          # Pause on uncaught/unhandled errors
    ERROR = "error"                # Pause on ERROR severity
    WARNING = "warning"            # Pause on WARNING severity
    TIMEOUT = "timeout"            # Pause on timeout errors
    VALIDATION = "validation"      # Pause on validation errors
    CONNECTIVITY = "connectivity"  # Pause on connectivity/network errors


class DebugState(BaseModel):
    """
    Current debug state for a run.

    Tracks the debug mode, breakpoints, and current position.
    """
    run_id: str = Field(description="Run ID this state belongs to")
    mode: DebugMode = Field(default=DebugMode.RUNNING, description="Current debug mode")
    breakpoints: List[str] = Field(
        default_factory=list,
        description="List of stage IDs with breakpoints set"
    )
    exception_breakpoints: List[str] = Field(
        default_factory=list,
        description="List of exception filters to pause on (e.g., 'all', 'error', 'timeout')"
    )
    current_stage_id: Optional[str] = Field(
        default=None,
        description="Stage ID currently being executed or paused at"
    )
    paused_at: Optional[datetime] = Field(
        default=None,
        description="When execution was paused"
    )
    timeout_at: Optional[datetime] = Field(
        default=None,
        description="When to auto-resume (5 minute timeout)"
    )
    pause_reason: Optional[str] = Field(
        default=None,
        description="Reason for pause (breakpoint, user_requested, exception, etc.)"
    )
    current_exception: Optional["ExceptionInfo"] = Field(
        default=None,
        description="Current exception info if paused due to exception"
    )

    model_config = ConfigDict(use_enum_values=True)


class DebugCommand(str, Enum):
    """Debug commands that can be sent."""
    PAUSE = "pause"
    RESUME = "resume"
    STEP = "step"           # Execute one stage then pause
    STOP = "stop"           # Stop execution entirely
    SET_BREAKPOINT = "set_breakpoint"
    REMOVE_BREAKPOINT = "remove_breakpoint"


class DebugCommandRequest(BaseModel):
    """Request to send a debug command."""
    command: DebugCommand = Field(description="The debug command to execute")
    stage_id: Optional[str] = Field(
        default=None,
        description="Stage ID for breakpoint commands"
    )


class DebugCommandResponse(BaseModel):
    """Response from a debug command."""
    run_id: str
    success: bool
    mode: DebugMode
    message: str
    current_stage_id: Optional[str] = None
    breakpoints: List[str] = Field(default_factory=list)


class SetBreakpointsRequest(BaseModel):
    """Request to set breakpoints for a run."""
    stage_ids: List[str] = Field(
        description="Stage IDs to set breakpoints on. Replaces existing breakpoints."
    )


class BreakpointInfo(BaseModel):
    """Information about a breakpoint."""
    stage_id: str
    enabled: bool = True
    hit_count: int = 0
    condition: Optional[str] = None  # Future: conditional breakpoints


class StageExecutionEvent(BaseModel):
    """
    Event emitted during stage execution.

    Used for WebSocket broadcasts to provide real-time updates.
    """
    run_id: str
    stage_id: str
    stage_name: Optional[str] = None
    component_type: str
    event_type: str  # started, completed, failed
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # For completed/failed events
    status: Optional[str] = None
    duration_ms: Optional[int] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # Usage info (for LLM calls)
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class RunExecutionEvent(BaseModel):
    """
    Event emitted for run-level execution updates.

    Used for WebSocket broadcasts for run lifecycle events.
    """
    run_id: str
    pipeline_id: str
    event_type: str  # started, completed, failed
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # For started event
    stage_ids: Optional[List[str]] = None
    inputs: Optional[Dict[str, Any]] = None

    # For completed event
    status: Optional[str] = None
    output: Optional[Any] = None
    total_duration_ms: Optional[int] = None

    # For failed event
    error: Optional[str] = None
    failed_stage_id: Optional[str] = None

    # Aggregated usage
    total_input_tokens: Optional[int] = None
    total_output_tokens: Optional[int] = None


class DebugPauseEvent(BaseModel):
    """
    Event emitted when execution is paused.

    Sent via WebSocket when hitting a breakpoint or user pauses.
    """
    run_id: str
    stage_id: str
    stage_name: Optional[str] = None
    reason: str  # breakpoint, user_requested, step_mode, exception
    timeout_seconds: int = 300  # 5 minutes default
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Current state when paused
    completed_stages: List[str] = Field(default_factory=list)
    pending_stages: List[str] = Field(default_factory=list)

    # Exception info (if paused due to exception)
    exception_info: Optional["ExceptionInfo"] = None


class SetExceptionBreakpointsRequest(BaseModel):
    """Request to set exception breakpoints for a run."""
    filters: List[str] = Field(
        description="Exception filter IDs to break on (e.g., 'all', 'error', 'timeout'). Replaces existing."
    )


class ExceptionInfo(BaseModel):
    """
    Information about an exception that caused a pause.

    Provides detailed error information for the debug panel.
    """
    exception_id: str = Field(description="Unique identifier for this exception")
    description: str = Field(description="Human-readable error description")
    break_mode: str = Field(
        default="always",
        description="Break mode: 'always', 'never', 'unhandled'"
    )

    # FlowMason error classification
    error_type: Optional[str] = Field(
        default=None,
        description="FlowMason ErrorType (e.g., TIMEOUT, VALIDATION, CONNECTIVITY)"
    )
    severity: Optional[str] = Field(
        default=None,
        description="Error severity (CRITICAL, ERROR, WARNING, INFO)"
    )

    # Stage context
    stage_id: Optional[str] = Field(default=None, description="Stage where error occurred")
    stage_name: Optional[str] = Field(default=None, description="Human-readable stage name")
    component_type: Optional[str] = Field(default=None, description="Component type that failed")

    # Additional details
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details and context"
    )
    stack_trace: Optional[str] = Field(
        default=None,
        description="Stack trace if available"
    )
    recoverable: bool = Field(
        default=False,
        description="Whether the error is potentially recoverable"
    )

    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Update forward references
DebugState.model_rebuild()
DebugPauseEvent.model_rebuild()
