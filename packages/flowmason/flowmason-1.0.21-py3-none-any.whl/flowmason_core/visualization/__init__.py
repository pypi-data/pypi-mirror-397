"""
FlowMason Visualization Module.

Provides animated execution visualization and debugging:
- Execution frames for real-time animation
- Data flow visualization
- Token streaming overlays
- Timeline playback controls
- Recording and export

Example:
    from flowmason_core.visualization import ExecutionRecorder, ExecutionAnimator

    # Record an execution
    recorder = ExecutionRecorder()
    recorder.start_recording(run_id)

    # ... execute pipeline ...

    recording = recorder.stop_recording()

    # Play back with animator
    animator = ExecutionAnimator(recording)
    animator.play(speed=1.0)
"""

from flowmason_core.visualization.frames import (
    DataFlowFrame,
    ExecutionFrame,
    ExecutionTimeline,
    FrameType,
    StageFrame,
    StageStatus,
    TimelineMarker,
    TokenFrame,
)
from flowmason_core.visualization.recorder import ExecutionRecorder, Recording
from flowmason_core.visualization.animator import ExecutionAnimator, PlaybackState
from flowmason_core.visualization.exporter import RecordingExporter, ExportFormat

__all__ = [
    # Frame types
    "FrameType",
    "ExecutionFrame",
    "StageFrame",
    "StageStatus",
    "DataFlowFrame",
    "TokenFrame",
    "ExecutionTimeline",
    "TimelineMarker",
    # Recording
    "ExecutionRecorder",
    "Recording",
    # Animation
    "ExecutionAnimator",
    "PlaybackState",
    # Export
    "RecordingExporter",
    "ExportFormat",
]
