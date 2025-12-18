"""
Visualization API Routes for FlowMason Studio.

Provides endpoints for execution visualization and animation.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/visualization", tags=["visualization"])


# Storage for recordings (in production, use proper storage)
_recordings: Dict[str, Any] = {}


# Request/Response Models

class RecordingInfo(BaseModel):
    """Information about a recording."""
    run_id: str
    pipeline_name: str
    status: str
    total_duration_ms: int
    frame_count: int
    start_time: str


class FrameData(BaseModel):
    """A single execution frame."""
    frame_type: str
    timestamp: float
    run_id: str
    stages: Dict[str, Any]
    active_flows: List[Dict[str, Any]] = []
    current_stage_id: Optional[str] = None
    message: str = ""


class TimelineData(BaseModel):
    """Timeline data for visualization."""
    run_id: str
    total_duration_ms: int
    stages: List[str]
    markers: List[Dict[str, Any]]


class ExportRequest(BaseModel):
    """Request to export a recording."""
    format: str = Field(description="Export format: json, html, markdown, mermaid, svg_sequence")


# Endpoints

@router.get("/recordings", response_model=List[RecordingInfo])
async def list_recordings():
    """List all available recordings."""
    return [
        RecordingInfo(
            run_id=run_id,
            pipeline_name=rec.get("pipeline_name", "unknown"),
            status=rec.get("status", "unknown"),
            total_duration_ms=rec.get("total_duration_ms", 0),
            frame_count=len(rec.get("frames", [])),
            start_time=rec.get("start_time", ""),
        )
        for run_id, rec in _recordings.items()
    ]


@router.get("/recordings/{run_id}")
async def get_recording(run_id: str):
    """Get a full recording."""
    recording = _recordings.get(run_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


@router.get("/recordings/{run_id}/frames")
async def get_frames(
    run_id: str,
    start: float = 0.0,
    end: Optional[float] = None,
    limit: int = 100,
):
    """
    Get frames for a recording.

    Args:
        run_id: Recording ID
        start: Start timestamp (seconds)
        end: End timestamp (seconds, defaults to end of recording)
        limit: Maximum frames to return
    """
    recording = _recordings.get(run_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    frames = recording.get("frames", [])

    # Filter by timestamp
    if end is None:
        end = recording.get("total_duration_ms", 0) / 1000.0

    filtered = [
        f for f in frames
        if start <= f.get("timestamp", 0) <= end
    ]

    return filtered[:limit]


@router.get("/recordings/{run_id}/timeline", response_model=TimelineData)
async def get_timeline(run_id: str):
    """Get the timeline for a recording."""
    recording = _recordings.get(run_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    timeline = recording.get("timeline")
    if timeline:
        return TimelineData(**timeline)

    # Build timeline from frames
    markers = []
    for frame in recording.get("frames", []):
        if frame.get("current_stage_id"):
            markers.append({
                "timestamp": frame.get("timestamp", 0),
                "label": frame.get("message", "")[:30],
                "marker_type": frame.get("frame_type", ""),
                "stage_id": frame.get("current_stage_id"),
            })

    return TimelineData(
        run_id=run_id,
        total_duration_ms=recording.get("total_duration_ms", 0),
        stages=recording.get("stages", []),
        markers=markers,
    )


@router.post("/recordings/{run_id}/export")
async def export_recording(run_id: str, request: ExportRequest):
    """
    Export a recording to various formats.

    Supported formats: json, html, markdown, mermaid, svg_sequence
    """
    from flowmason_core.visualization import ExportFormat, Recording, RecordingExporter

    recording_data = _recordings.get(run_id)
    if not recording_data:
        raise HTTPException(status_code=404, detail="Recording not found")

    try:
        # Convert to Recording object
        recording = Recording.from_dict(recording_data)
        exporter = RecordingExporter(recording)

        format_map = {
            "json": ExportFormat.JSON,
            "html": ExportFormat.HTML,
            "markdown": ExportFormat.MARKDOWN,
            "mermaid": ExportFormat.MERMAID,
            "svg_sequence": ExportFormat.SVG_SEQUENCE,
        }

        export_format = format_map.get(request.format.lower())
        if not export_format:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {request.format}",
            )

        content = exporter.export(export_format)

        # Return appropriate content type
        if request.format.lower() == "html":
            return HTMLResponse(content=content)
        elif request.format.lower() == "svg_sequence":
            return HTMLResponse(content=content, media_type="image/svg+xml")

        return {"content": content, "format": request.format}

    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/recordings/{run_id}")
async def delete_recording(run_id: str):
    """Delete a recording."""
    if run_id not in _recordings:
        raise HTTPException(status_code=404, detail="Recording not found")

    del _recordings[run_id]
    return {"status": "deleted", "run_id": run_id}


@router.get("/recordings/{run_id}/viewer", response_class=HTMLResponse)
async def get_viewer(run_id: str):
    """Get the HTML viewer for a recording."""
    from flowmason_core.visualization import ExportFormat, Recording, RecordingExporter

    recording_data = _recordings.get(run_id)
    if not recording_data:
        raise HTTPException(status_code=404, detail="Recording not found")

    recording = Recording.from_dict(recording_data)
    exporter = RecordingExporter(recording)
    return exporter.export(ExportFormat.HTML)


# WebSocket for live visualization

class LiveVisualizationManager:
    """Manages live visualization WebSocket connections."""

    def __init__(self):
        self._connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, run_id: str, websocket: WebSocket):
        """Connect a client to live visualization."""
        await websocket.accept()
        if run_id not in self._connections:
            self._connections[run_id] = []
        self._connections[run_id].append(websocket)
        logger.info(f"Live visualization client connected: {run_id}")

    def disconnect(self, run_id: str, websocket: WebSocket):
        """Disconnect a client."""
        if run_id in self._connections:
            if websocket in self._connections[run_id]:
                self._connections[run_id].remove(websocket)
            if not self._connections[run_id]:
                del self._connections[run_id]
        logger.info(f"Live visualization client disconnected: {run_id}")

    async def broadcast_frame(self, run_id: str, frame: Dict[str, Any]):
        """Broadcast a frame to all connected clients."""
        if run_id not in self._connections:
            return

        disconnected = []
        for websocket in self._connections[run_id]:
            try:
                await websocket.send_json({"type": "frame", "data": frame})
            except Exception:
                disconnected.append(websocket)

        for ws in disconnected:
            self.disconnect(run_id, ws)


_live_manager = LiveVisualizationManager()


def get_live_manager() -> LiveVisualizationManager:
    """Get the live visualization manager."""
    return _live_manager


@router.websocket("/live/{run_id}")
async def live_visualization(websocket: WebSocket, run_id: str):
    """
    WebSocket for live execution visualization.

    Receives real-time execution frames as they happen.
    """
    await _live_manager.connect(run_id, websocket)

    try:
        while True:
            # Wait for client messages (ping/pong, commands)
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            elif message.get("type") == "subscribe":
                # Already subscribed by connecting
                await websocket.send_json({
                    "type": "subscribed",
                    "run_id": run_id,
                })

    except WebSocketDisconnect:
        _live_manager.disconnect(run_id, websocket)


# Helper functions for integration with execution

def store_recording(recording_data: Dict[str, Any]) -> None:
    """Store a recording (called after execution completes)."""
    run_id = recording_data.get("run_id")
    if run_id:
        _recordings[run_id] = recording_data
        logger.info(f"Stored recording: {run_id}")


async def broadcast_live_frame(run_id: str, frame: Dict[str, Any]) -> None:
    """Broadcast a frame for live visualization."""
    await _live_manager.broadcast_frame(run_id, frame)
