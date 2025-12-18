"""
Execution Recorder for FlowMason Visualization.

Records execution frames for playback and animation.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from flowmason_core.visualization.frames import (
    DataFlowFrame,
    ExecutionFrame,
    ExecutionTimeline,
    FrameType,
    StageFrame,
    StageStatus,
    TokenFrame,
)

logger = logging.getLogger(__name__)


@dataclass
class Recording:
    """
    A recorded execution for playback.

    Contains all frames and metadata needed to replay
    a pipeline execution with animation.
    """
    run_id: str
    pipeline_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    frames: List[ExecutionFrame] = field(default_factory=list)
    timeline: Optional[ExecutionTimeline] = None

    # Metadata
    total_duration_ms: int = 0
    stages: List[str] = field(default_factory=list)
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    status: str = "recording"  # recording, completed, error

    def get_frame_at(self, timestamp: float) -> Optional[ExecutionFrame]:
        """Get the frame at or before a specific timestamp."""
        for i in range(len(self.frames) - 1, -1, -1):
            if self.frames[i].timestamp <= timestamp:
                return self.frames[i]
        return self.frames[0] if self.frames else None

    def get_frames_in_range(
        self,
        start_time: float,
        end_time: float,
    ) -> List[ExecutionFrame]:
        """Get frames within a time range."""
        return [
            f for f in self.frames
            if start_time <= f.timestamp <= end_time
        ]

    def get_duration_seconds(self) -> float:
        """Get total duration in seconds."""
        return self.total_duration_ms / 1000.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "pipeline_name": self.pipeline_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "frames": [f.to_dict() for f in self.frames],
            "timeline": self.timeline.to_dict() if self.timeline else None,
            "total_duration_ms": self.total_duration_ms,
            "stages": self.stages,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recording":
        """Create from dictionary."""
        return cls(
            run_id=data["run_id"],
            pipeline_name=data["pipeline_name"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            frames=[ExecutionFrame.from_dict(f) for f in data.get("frames", [])],
            total_duration_ms=data.get("total_duration_ms", 0),
            stages=data.get("stages", []),
            input_data=data.get("input_data"),
            output_data=data.get("output_data"),
            status=data.get("status", "completed"),
        )

    def save(self, path: Path) -> None:
        """Save recording to file."""
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str))

    @classmethod
    def load(cls, path: Path) -> "Recording":
        """Load recording from file."""
        data = json.loads(path.read_text())
        return cls.from_dict(data)


class ExecutionRecorder:
    """
    Records pipeline execution for animated playback.

    Captures execution frames at regular intervals and on events.
    """

    def __init__(
        self,
        frame_interval_ms: int = 100,
        max_frames: int = 10000,
        record_tokens: bool = True,
        record_data_flow: bool = True,
    ):
        """
        Initialize the recorder.

        Args:
            frame_interval_ms: Minimum interval between frames
            max_frames: Maximum number of frames to record
            record_tokens: Whether to record token streaming
            record_data_flow: Whether to record data flow between stages
        """
        self._frame_interval_ms = frame_interval_ms
        self._max_frames = max_frames
        self._record_tokens = record_tokens
        self._record_data_flow = record_data_flow

        self._recording: Optional[Recording] = None
        self._start_time: Optional[float] = None
        self._last_frame_time: float = 0
        self._stage_states: Dict[str, StageFrame] = {}
        self._active_flows: List[DataFlowFrame] = []

        # Callbacks for real-time streaming
        self._frame_callbacks: List[Callable[[ExecutionFrame], None]] = []

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording is not None and self._recording.status == "recording"

    def start_recording(
        self,
        run_id: str,
        pipeline_name: str,
        stages: List[str],
        input_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Start recording an execution.

        Args:
            run_id: Unique run identifier
            pipeline_name: Name of the pipeline
            stages: Ordered list of stage IDs
            input_data: Pipeline input data
        """
        self._start_time = time.time()
        self._last_frame_time = 0
        self._stage_states = {}
        self._active_flows = []

        # Initialize stage states
        for stage_id in stages:
            self._stage_states[stage_id] = StageFrame(
                stage_id=stage_id,
                status=StageStatus.PENDING,
            )

        self._recording = Recording(
            run_id=run_id,
            pipeline_name=pipeline_name,
            start_time=datetime.utcnow(),
            stages=stages,
            input_data=input_data,
            timeline=ExecutionTimeline(run_id=run_id, total_duration_ms=0, stages=stages),
        )

        # Record initial frame
        self._record_frame(FrameType.EXECUTION_START, "Execution started")
        logger.info(f"Started recording execution: {run_id}")

    def stop_recording(
        self,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Recording:
        """
        Stop recording and return the recording.

        Args:
            output_data: Pipeline output data
            error: Error message if execution failed

        Returns:
            The completed Recording
        """
        if not self._recording:
            raise RuntimeError("No recording in progress")

        # Record final frame
        if error:
            self._record_frame(FrameType.EXECUTION_END, f"Execution failed: {error}")
            self._recording.status = "error"
        else:
            self._record_frame(FrameType.EXECUTION_END, "Execution completed")
            self._recording.status = "completed"

        self._recording.end_time = datetime.utcnow()
        self._recording.output_data = output_data
        self._recording.total_duration_ms = int(
            (time.time() - self._start_time) * 1000
        )

        if self._recording.timeline:
            self._recording.timeline.total_duration_ms = self._recording.total_duration_ms

        recording = self._recording
        self._recording = None
        self._start_time = None

        logger.info(f"Stopped recording: {recording.run_id}, {len(recording.frames)} frames")
        return recording

    def record_stage_start(self, stage_id: str) -> None:
        """Record a stage starting execution."""
        if not self.is_recording:
            return

        self._stage_states[stage_id] = StageFrame(
            stage_id=stage_id,
            status=StageStatus.RUNNING,
            progress=0.0,
        )

        self._record_frame(
            FrameType.STAGE_START,
            f"Stage {stage_id} started",
            current_stage_id=stage_id,
        )

        # Add timeline marker
        if self._recording and self._recording.timeline:
            self._recording.timeline.add_marker(
                timestamp=self._current_timestamp(),
                label=f"Start: {stage_id}",
                marker_type="stage",
                stage_id=stage_id,
            )

    def record_stage_progress(
        self,
        stage_id: str,
        progress: float,
        message: Optional[str] = None,
    ) -> None:
        """
        Record stage progress.

        Args:
            stage_id: Stage identifier
            progress: Progress from 0.0 to 1.0
            message: Optional progress message
        """
        if not self.is_recording:
            return

        if stage_id in self._stage_states:
            self._stage_states[stage_id].progress = progress

        # Only record if enough time has passed
        current_time = self._current_timestamp()
        if (current_time - self._last_frame_time) * 1000 < self._frame_interval_ms:
            return

        self._record_frame(
            FrameType.STAGE_PROGRESS,
            message or f"Stage {stage_id}: {progress:.0%}",
            current_stage_id=stage_id,
        )

    def record_stage_complete(
        self,
        stage_id: str,
        duration_ms: int,
        output_preview: Optional[str] = None,
    ) -> None:
        """Record a stage completing execution."""
        if not self.is_recording:
            return

        self._stage_states[stage_id] = StageFrame(
            stage_id=stage_id,
            status=StageStatus.COMPLETED,
            progress=1.0,
            duration_ms=duration_ms,
            output_preview=output_preview,
        )

        self._record_frame(
            FrameType.STAGE_COMPLETE,
            f"Stage {stage_id} completed in {duration_ms}ms",
            current_stage_id=stage_id,
        )

        # Add timeline marker
        if self._recording and self._recording.timeline:
            self._recording.timeline.add_marker(
                timestamp=self._current_timestamp(),
                label=f"Complete: {stage_id}",
                marker_type="stage",
                stage_id=stage_id,
                color="#48bb78",  # Green
            )

    def record_stage_error(
        self,
        stage_id: str,
        error: str,
        duration_ms: int = 0,
    ) -> None:
        """Record a stage error."""
        if not self.is_recording:
            return

        self._stage_states[stage_id] = StageFrame(
            stage_id=stage_id,
            status=StageStatus.FAILED,
            duration_ms=duration_ms,
            error=error,
        )

        self._record_frame(
            FrameType.STAGE_ERROR,
            f"Stage {stage_id} failed: {error}",
            current_stage_id=stage_id,
        )

        # Add timeline marker
        if self._recording and self._recording.timeline:
            self._recording.timeline.add_marker(
                timestamp=self._current_timestamp(),
                label=f"Error: {stage_id}",
                marker_type="error",
                stage_id=stage_id,
            )

    def record_data_flow(
        self,
        from_stage: str,
        to_stage: str,
        data_size_bytes: int,
        data_preview: Optional[str] = None,
        data_type: str = "unknown",
    ) -> None:
        """Record data flowing between stages."""
        if not self.is_recording or not self._record_data_flow:
            return

        flow = DataFlowFrame(
            from_stage=from_stage,
            to_stage=to_stage,
            data_size_bytes=data_size_bytes,
            data_preview=data_preview,
            data_type=data_type,
            timestamp=self._current_timestamp(),
        )

        self._active_flows.append(flow)

        self._record_frame(
            FrameType.DATA_FLOW,
            f"Data flow: {from_stage} -> {to_stage} ({data_size_bytes} bytes)",
        )

        # Add timeline marker
        if self._recording and self._recording.timeline:
            self._recording.timeline.add_marker(
                timestamp=self._current_timestamp(),
                label=f"Flow: {from_stage}→{to_stage}",
                marker_type="data_flow",
            )

        # Clean up old flows (keep last 5)
        if len(self._active_flows) > 5:
            self._active_flows = self._active_flows[-5:]

    def record_token(
        self,
        stage_id: str,
        token: str,
        token_index: int,
        cumulative_tokens: int = 0,
        estimated_total: int = 0,
    ) -> None:
        """Record a token from LLM streaming."""
        if not self.is_recording or not self._record_tokens:
            return

        # Update stage token count
        if stage_id in self._stage_states:
            self._stage_states[stage_id].tokens_generated = cumulative_tokens
            self._stage_states[stage_id].tokens_total = estimated_total
            if estimated_total > 0:
                self._stage_states[stage_id].progress = cumulative_tokens / estimated_total

        token_frame = TokenFrame(
            stage_id=stage_id,
            token=token,
            token_index=token_index,
            timestamp=self._current_timestamp(),
            cumulative_tokens=cumulative_tokens,
            estimated_total=estimated_total,
        )

        # Only record periodically for tokens (they come fast)
        current_time = self._current_timestamp()
        if (current_time - self._last_frame_time) * 1000 < self._frame_interval_ms / 2:
            return

        self._record_frame(
            FrameType.TOKEN_STREAM,
            f"Token {token_index}: {token[:20]}...",
            current_stage_id=stage_id,
            token_frame=token_frame,
        )

    def record_breakpoint(self, stage_id: str, message: str = "") -> None:
        """Record hitting a breakpoint."""
        if not self.is_recording:
            return

        if stage_id in self._stage_states:
            self._stage_states[stage_id].status = StageStatus.PAUSED

        self._record_frame(
            FrameType.BREAKPOINT_HIT,
            message or f"Breakpoint hit at {stage_id}",
            current_stage_id=stage_id,
        )

        # Add timeline marker
        if self._recording and self._recording.timeline:
            self._recording.timeline.add_marker(
                timestamp=self._current_timestamp(),
                label=f"Breakpoint: {stage_id}",
                marker_type="breakpoint",
                stage_id=stage_id,
            )

    def add_frame_callback(self, callback: Callable[[ExecutionFrame], None]) -> None:
        """Add callback for real-time frame streaming."""
        self._frame_callbacks.append(callback)

    def remove_frame_callback(self, callback: Callable[[ExecutionFrame], None]) -> None:
        """Remove a frame callback."""
        if callback in self._frame_callbacks:
            self._frame_callbacks.remove(callback)

    def _current_timestamp(self) -> float:
        """Get current timestamp relative to start."""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def _record_frame(
        self,
        frame_type: FrameType,
        message: str,
        current_stage_id: Optional[str] = None,
        token_frame: Optional[TokenFrame] = None,
    ) -> None:
        """Record a frame."""
        if not self._recording or len(self._recording.frames) >= self._max_frames:
            return

        timestamp = self._current_timestamp()
        self._last_frame_time = timestamp

        # Count completed stages
        stages_completed = sum(
            1 for s in self._stage_states.values()
            if s.status == StageStatus.COMPLETED
        )

        frame = ExecutionFrame(
            frame_type=frame_type,
            timestamp=timestamp,
            absolute_time=datetime.utcnow(),
            run_id=self._recording.run_id,
            stages=dict(self._stage_states),
            active_flows=list(self._active_flows),
            token_stream=token_frame,
            total_duration_ms=int(timestamp * 1000),
            stages_completed=stages_completed,
            stages_total=len(self._recording.stages),
            current_stage_id=current_stage_id,
            message=message,
        )

        self._recording.frames.append(frame)

        # Notify callbacks
        for callback in self._frame_callbacks:
            try:
                callback(frame)
            except Exception as e:
                logger.warning(f"Frame callback error: {e}")
