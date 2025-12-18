"""
Execution Animator for FlowMason Visualization.

Provides playback control for recorded executions.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from flowmason_core.visualization.frames import ExecutionFrame, ExecutionTimeline
from flowmason_core.visualization.recorder import Recording

logger = logging.getLogger(__name__)


class PlaybackState(str, Enum):
    """State of the animator."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    SEEKING = "seeking"


@dataclass
class PlaybackPosition:
    """Current playback position."""
    timestamp: float  # Seconds from start
    frame_index: int
    progress: float  # 0.0 to 1.0


class ExecutionAnimator:
    """
    Animates recorded pipeline executions.

    Provides playback controls like play, pause, seek,
    and speed adjustment for visualizing execution.
    """

    SPEED_OPTIONS = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0]

    def __init__(
        self,
        recording: Recording,
        frame_callback: Optional[Callable[[ExecutionFrame], None]] = None,
        position_callback: Optional[Callable[[PlaybackPosition], None]] = None,
    ):
        """
        Initialize the animator.

        Args:
            recording: The recording to animate
            frame_callback: Called when a new frame should be displayed
            position_callback: Called when playback position changes
        """
        self._recording = recording
        self._frame_callback = frame_callback
        self._position_callback = position_callback

        self._state = PlaybackState.STOPPED
        self._current_index = 0
        self._current_timestamp = 0.0
        self._speed = 1.0

        self._playback_task: Optional[asyncio.Task] = None
        self._last_update_time: float = 0.0

        # For smooth interpolation
        self._interpolate = True

    @property
    def state(self) -> PlaybackState:
        """Get current playback state."""
        return self._state

    @property
    def current_frame(self) -> Optional[ExecutionFrame]:
        """Get the current frame."""
        if 0 <= self._current_index < len(self._recording.frames):
            return self._recording.frames[self._current_index]
        return None

    @property
    def current_position(self) -> PlaybackPosition:
        """Get current playback position."""
        duration = self._recording.get_duration_seconds()
        progress = self._current_timestamp / duration if duration > 0 else 0.0
        return PlaybackPosition(
            timestamp=self._current_timestamp,
            frame_index=self._current_index,
            progress=progress,
        )

    @property
    def duration(self) -> float:
        """Get total duration in seconds."""
        return self._recording.get_duration_seconds()

    @property
    def speed(self) -> float:
        """Get current playback speed."""
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        """Set playback speed."""
        if value in self.SPEED_OPTIONS or 0.1 <= value <= 16.0:
            self._speed = value
            logger.debug(f"Playback speed set to {value}x")

    def set_frame_callback(
        self,
        callback: Callable[[ExecutionFrame], None],
    ) -> None:
        """Set the frame callback."""
        self._frame_callback = callback

    def set_position_callback(
        self,
        callback: Callable[[PlaybackPosition], None],
    ) -> None:
        """Set the position callback."""
        self._position_callback = callback

    async def play(self) -> None:
        """Start or resume playback."""
        if self._state == PlaybackState.PLAYING:
            return

        self._state = PlaybackState.PLAYING
        self._last_update_time = time.time()

        # Start playback loop
        self._playback_task = asyncio.create_task(self._playback_loop())
        logger.debug("Playback started")

    async def pause(self) -> None:
        """Pause playback."""
        if self._state != PlaybackState.PLAYING:
            return

        self._state = PlaybackState.PAUSED
        if self._playback_task:
            self._playback_task.cancel()
            try:
                await self._playback_task
            except asyncio.CancelledError:
                pass
            self._playback_task = None

        logger.debug("Playback paused")

    async def stop(self) -> None:
        """Stop playback and reset to beginning."""
        await self.pause()
        self._state = PlaybackState.STOPPED
        self._current_index = 0
        self._current_timestamp = 0.0

        # Emit initial frame
        self._emit_current_frame()
        logger.debug("Playback stopped")

    async def seek(self, timestamp: float) -> None:
        """
        Seek to a specific timestamp.

        Args:
            timestamp: Target timestamp in seconds
        """
        was_playing = self._state == PlaybackState.PLAYING
        if was_playing:
            await self.pause()

        self._state = PlaybackState.SEEKING

        # Clamp timestamp
        duration = self._recording.get_duration_seconds()
        timestamp = max(0.0, min(timestamp, duration))
        self._current_timestamp = timestamp

        # Find the frame at or before this timestamp
        self._current_index = self._find_frame_index(timestamp)

        # Emit frame
        self._emit_current_frame()

        if was_playing:
            await self.play()
        else:
            self._state = PlaybackState.PAUSED

        logger.debug(f"Seeked to {timestamp:.2f}s")

    async def seek_percent(self, percent: float) -> None:
        """Seek to a percentage of total duration."""
        percent = max(0.0, min(100.0, percent))
        timestamp = (percent / 100.0) * self._recording.get_duration_seconds()
        await self.seek(timestamp)

    async def step_forward(self) -> None:
        """Step forward one frame."""
        if self._current_index < len(self._recording.frames) - 1:
            self._current_index += 1
            self._current_timestamp = self._recording.frames[self._current_index].timestamp
            self._emit_current_frame()

    async def step_backward(self) -> None:
        """Step backward one frame."""
        if self._current_index > 0:
            self._current_index -= 1
            self._current_timestamp = self._recording.frames[self._current_index].timestamp
            self._emit_current_frame()

    async def skip_to_stage(self, stage_id: str) -> None:
        """Skip to when a specific stage starts."""
        for i, frame in enumerate(self._recording.frames):
            if frame.current_stage_id == stage_id:
                await self.seek(frame.timestamp)
                return

    async def skip_to_next_stage(self) -> None:
        """Skip to the next stage change."""
        current_stage = self.current_frame.current_stage_id if self.current_frame else None

        for i in range(self._current_index + 1, len(self._recording.frames)):
            frame = self._recording.frames[i]
            if frame.current_stage_id != current_stage and frame.current_stage_id:
                await self.seek(frame.timestamp)
                return

    async def skip_to_previous_stage(self) -> None:
        """Skip to the previous stage change."""
        current_stage = self.current_frame.current_stage_id if self.current_frame else None

        for i in range(self._current_index - 1, -1, -1):
            frame = self._recording.frames[i]
            if frame.current_stage_id != current_stage and frame.current_stage_id:
                await self.seek(frame.timestamp)
                return

    def get_timeline(self) -> ExecutionTimeline:
        """Get the execution timeline."""
        if self._recording.timeline:
            return self._recording.timeline

        # Build timeline from frames
        timeline = ExecutionTimeline(
            run_id=self._recording.run_id,
            total_duration_ms=self._recording.total_duration_ms,
            stages=self._recording.stages,
        )

        for frame in self._recording.frames:
            if frame.current_stage_id:
                timeline.add_marker(
                    timestamp=frame.timestamp,
                    label=frame.message[:30],
                    marker_type=frame.frame_type.value,
                    stage_id=frame.current_stage_id,
                )

        return timeline

    def get_frame_at(self, timestamp: float) -> Optional[ExecutionFrame]:
        """Get the frame at a specific timestamp."""
        return self._recording.get_frame_at(timestamp)

    async def _playback_loop(self) -> None:
        """Main playback loop."""
        try:
            while self._state == PlaybackState.PLAYING:
                current_time = time.time()
                elapsed = current_time - self._last_update_time
                self._last_update_time = current_time

                # Advance timestamp by elapsed * speed
                self._current_timestamp += elapsed * self._speed

                # Check if we've reached the end
                duration = self._recording.get_duration_seconds()
                if self._current_timestamp >= duration:
                    self._current_timestamp = duration
                    self._current_index = len(self._recording.frames) - 1
                    self._emit_current_frame()
                    self._state = PlaybackState.STOPPED
                    logger.debug("Playback reached end")
                    return

                # Find current frame
                self._current_index = self._find_frame_index(self._current_timestamp)

                # Emit frame
                self._emit_current_frame()

                # Sleep for smooth playback (target ~60fps)
                await asyncio.sleep(1 / 60)

        except asyncio.CancelledError:
            pass

    def _find_frame_index(self, timestamp: float) -> int:
        """Find the frame index at or before a timestamp."""
        # Binary search for efficiency
        frames = self._recording.frames
        left, right = 0, len(frames) - 1

        while left < right:
            mid = (left + right + 1) // 2
            if frames[mid].timestamp <= timestamp:
                left = mid
            else:
                right = mid - 1

        return left

    def _emit_current_frame(self) -> None:
        """Emit the current frame to callbacks."""
        frame = self.current_frame
        if frame and self._frame_callback:
            try:
                self._frame_callback(frame)
            except Exception as e:
                logger.warning(f"Frame callback error: {e}")

        if self._position_callback:
            try:
                self._position_callback(self.current_position)
            except Exception as e:
                logger.warning(f"Position callback error: {e}")


class LiveAnimator:
    """
    Handles live animation during execution.

    Receives frames in real-time and animates the visualization.
    """

    def __init__(
        self,
        frame_callback: Callable[[ExecutionFrame], None],
        buffer_size: int = 100,
    ):
        """
        Initialize live animator.

        Args:
            frame_callback: Called for each frame to display
            buffer_size: Number of frames to buffer
        """
        self._frame_callback = frame_callback
        self._buffer_size = buffer_size
        self._frame_buffer: List[ExecutionFrame] = []
        self._is_running = False

    def start(self) -> None:
        """Start the live animator."""
        self._is_running = True
        self._frame_buffer = []

    def stop(self) -> None:
        """Stop the live animator."""
        self._is_running = False

    def receive_frame(self, frame: ExecutionFrame) -> None:
        """
        Receive a frame from the recorder.

        Args:
            frame: The execution frame to display
        """
        if not self._is_running:
            return

        # Add to buffer
        self._frame_buffer.append(frame)
        if len(self._frame_buffer) > self._buffer_size:
            self._frame_buffer.pop(0)

        # Display frame
        try:
            self._frame_callback(frame)
        except Exception as e:
            logger.warning(f"Live frame callback error: {e}")

    def get_recent_frames(self, count: int = 10) -> List[ExecutionFrame]:
        """Get recent frames from buffer."""
        return self._frame_buffer[-count:]
