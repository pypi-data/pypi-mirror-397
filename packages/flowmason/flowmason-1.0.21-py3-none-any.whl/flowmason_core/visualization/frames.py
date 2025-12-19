"""
Execution Frame Types for FlowMason Visualization.

Defines the data structures for animated execution visualization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FrameType(str, Enum):
    """Types of execution frames."""
    EXECUTION_START = "execution_start"
    EXECUTION_END = "execution_end"
    STAGE_START = "stage_start"
    STAGE_PROGRESS = "stage_progress"
    STAGE_COMPLETE = "stage_complete"
    STAGE_ERROR = "stage_error"
    DATA_FLOW = "data_flow"
    TOKEN_STREAM = "token_stream"
    BREAKPOINT_HIT = "breakpoint_hit"
    VARIABLE_UPDATE = "variable_update"


class StageStatus(str, Enum):
    """Status of a stage in a frame."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"


@dataclass
class StageFrame:
    """State of a single stage at a point in time."""
    stage_id: str
    status: StageStatus
    progress: float = 0.0  # 0.0 to 1.0
    duration_ms: int = 0
    output_preview: Optional[str] = None
    error: Optional[str] = None
    tokens_generated: int = 0
    tokens_total: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataFlowFrame:
    """Data flowing between stages."""
    from_stage: str
    to_stage: str
    data_size_bytes: int = 0
    data_preview: Optional[str] = None
    data_type: str = "unknown"
    timestamp: float = 0.0  # Relative to execution start


@dataclass
class TokenFrame:
    """Token streaming from an LLM stage."""
    stage_id: str
    token: str
    token_index: int
    timestamp: float  # Relative to execution start
    cumulative_tokens: int = 0
    estimated_total: int = 0


@dataclass
class ExecutionFrame:
    """
    A snapshot of execution state at a point in time.

    Used for animated playback of pipeline execution.
    """
    frame_type: FrameType
    timestamp: float  # Seconds from start
    absolute_time: datetime
    run_id: str

    # Stage states
    stages: Dict[str, StageFrame] = field(default_factory=dict)

    # Active data flows (for animation)
    active_flows: List[DataFlowFrame] = field(default_factory=list)

    # Token stream (for LLM stages)
    token_stream: Optional[TokenFrame] = None

    # Execution metadata
    total_duration_ms: int = 0
    stages_completed: int = 0
    stages_total: int = 0

    # Current stage being animated
    current_stage_id: Optional[str] = None

    # Additional context
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "frame_type": self.frame_type.value,
            "timestamp": self.timestamp,
            "absolute_time": self.absolute_time.isoformat(),
            "run_id": self.run_id,
            "stages": {
                sid: {
                    "stage_id": s.stage_id,
                    "status": s.status.value,
                    "progress": s.progress,
                    "duration_ms": s.duration_ms,
                    "output_preview": s.output_preview,
                    "error": s.error,
                    "tokens_generated": s.tokens_generated,
                    "tokens_total": s.tokens_total,
                }
                for sid, s in self.stages.items()
            },
            "active_flows": [
                {
                    "from_stage": f.from_stage,
                    "to_stage": f.to_stage,
                    "data_size_bytes": f.data_size_bytes,
                    "data_preview": f.data_preview,
                    "data_type": f.data_type,
                }
                for f in self.active_flows
            ],
            "token_stream": {
                "stage_id": self.token_stream.stage_id,
                "token": self.token_stream.token,
                "token_index": self.token_stream.token_index,
                "cumulative_tokens": self.token_stream.cumulative_tokens,
            } if self.token_stream else None,
            "total_duration_ms": self.total_duration_ms,
            "stages_completed": self.stages_completed,
            "stages_total": self.stages_total,
            "current_stage_id": self.current_stage_id,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionFrame":
        """Create from dictionary."""
        stages = {}
        for sid, s in data.get("stages", {}).items():
            stages[sid] = StageFrame(
                stage_id=s["stage_id"],
                status=StageStatus(s["status"]),
                progress=s.get("progress", 0.0),
                duration_ms=s.get("duration_ms", 0),
                output_preview=s.get("output_preview"),
                error=s.get("error"),
                tokens_generated=s.get("tokens_generated", 0),
                tokens_total=s.get("tokens_total", 0),
            )

        active_flows = []
        for f in data.get("active_flows", []):
            active_flows.append(DataFlowFrame(
                from_stage=f["from_stage"],
                to_stage=f["to_stage"],
                data_size_bytes=f.get("data_size_bytes", 0),
                data_preview=f.get("data_preview"),
                data_type=f.get("data_type", "unknown"),
            ))

        token_stream = None
        if data.get("token_stream"):
            ts = data["token_stream"]
            token_stream = TokenFrame(
                stage_id=ts["stage_id"],
                token=ts["token"],
                token_index=ts["token_index"],
                timestamp=data["timestamp"],
                cumulative_tokens=ts.get("cumulative_tokens", 0),
            )

        return cls(
            frame_type=FrameType(data["frame_type"]),
            timestamp=data["timestamp"],
            absolute_time=datetime.fromisoformat(data["absolute_time"]),
            run_id=data["run_id"],
            stages=stages,
            active_flows=active_flows,
            token_stream=token_stream,
            total_duration_ms=data.get("total_duration_ms", 0),
            stages_completed=data.get("stages_completed", 0),
            stages_total=data.get("stages_total", 0),
            current_stage_id=data.get("current_stage_id"),
            message=data.get("message", ""),
        )


@dataclass
class TimelineMarker:
    """A marker on the execution timeline."""
    timestamp: float
    label: str
    marker_type: str = "stage"  # stage, error, breakpoint, data_flow
    stage_id: Optional[str] = None
    color: str = "#4299e1"  # Default blue


@dataclass
class ExecutionTimeline:
    """Timeline of an execution for visualization."""
    run_id: str
    total_duration_ms: int
    markers: List[TimelineMarker] = field(default_factory=list)
    stages: List[str] = field(default_factory=list)  # Ordered stage IDs

    def add_marker(
        self,
        timestamp: float,
        label: str,
        marker_type: str = "stage",
        stage_id: Optional[str] = None,
        color: Optional[str] = None,
    ) -> None:
        """Add a marker to the timeline."""
        self.markers.append(TimelineMarker(
            timestamp=timestamp,
            label=label,
            marker_type=marker_type,
            stage_id=stage_id,
            color=color or self._default_color(marker_type),
        ))

    def _default_color(self, marker_type: str) -> str:
        """Get default color for marker type."""
        colors = {
            "stage": "#4299e1",      # Blue
            "error": "#f56565",       # Red
            "breakpoint": "#ecc94b",  # Yellow
            "data_flow": "#48bb78",   # Green
            "token": "#9f7aea",       # Purple
        }
        return colors.get(marker_type, "#4299e1")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "total_duration_ms": self.total_duration_ms,
            "markers": [
                {
                    "timestamp": m.timestamp,
                    "label": m.label,
                    "marker_type": m.marker_type,
                    "stage_id": m.stage_id,
                    "color": m.color,
                }
                for m in self.markers
            ],
            "stages": self.stages,
        }
