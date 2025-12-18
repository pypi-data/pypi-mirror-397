"""
Recording Exporter for FlowMason Visualization.

Exports execution recordings to various formats.
"""

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from flowmason_core.visualization.frames import ExecutionFrame, StageStatus
from flowmason_core.visualization.recorder import Recording

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """Available export formats."""
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    MERMAID = "mermaid"
    SVG_SEQUENCE = "svg_sequence"


class RecordingExporter:
    """
    Exports recordings to various formats.

    Supports:
    - JSON: Full recording data
    - HTML: Interactive playback viewer
    - Markdown: Execution report
    - Mermaid: Sequence diagram
    - SVG: Visual timeline
    """

    def __init__(self, recording: Recording):
        """Initialize with a recording."""
        self._recording = recording

    def export(
        self,
        format: ExportFormat,
        output_path: Optional[Path] = None,
    ) -> str:
        """
        Export to specified format.

        Args:
            format: Export format
            output_path: Optional output path (returns string if None)

        Returns:
            Exported content as string
        """
        exporters = {
            ExportFormat.JSON: self._export_json,
            ExportFormat.HTML: self._export_html,
            ExportFormat.MARKDOWN: self._export_markdown,
            ExportFormat.MERMAID: self._export_mermaid,
            ExportFormat.SVG_SEQUENCE: self._export_svg_sequence,
        }

        exporter = exporters.get(format)
        if not exporter:
            raise ValueError(f"Unsupported format: {format}")

        content = exporter()

        if output_path:
            output_path.write_text(content)
            logger.info(f"Exported recording to {output_path}")

        return content

    def _export_json(self) -> str:
        """Export to JSON format."""
        return json.dumps(self._recording.to_dict(), indent=2, default=str)

    def _export_html(self) -> str:
        """Export to interactive HTML viewer."""
        recording_data = json.dumps(self._recording.to_dict(), default=str)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlowMason Execution: {self._recording.pipeline_name}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }}
        h1 {{ margin: 0; color: #4299e1; }}
        .meta {{ color: #888; font-size: 0.9em; }}
        .controls {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            padding: 15px;
            background: #16213e;
            border-radius: 8px;
        }}
        button {{
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .play-btn {{ background: #48bb78; color: white; }}
        .play-btn:hover {{ background: #38a169; }}
        .pause-btn {{ background: #ecc94b; color: #1a1a2e; }}
        .stop-btn {{ background: #f56565; color: white; }}
        button:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        .timeline {{
            height: 60px;
            background: #16213e;
            border-radius: 8px;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }}
        .timeline-progress {{
            height: 100%;
            background: linear-gradient(90deg, #4299e1, #48bb78);
            width: 0%;
            transition: width 0.1s;
        }}
        .timeline-cursor {{
            position: absolute;
            top: 0;
            width: 2px;
            height: 100%;
            background: white;
            transition: left 0.1s;
        }}
        .timeline-markers {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 100%;
        }}
        .marker {{
            position: absolute;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            top: 50%;
            transform: translateY(-50%);
        }}
        .stages-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stage {{
            padding: 15px;
            background: #16213e;
            border-radius: 8px;
            border-left: 4px solid #4299e1;
        }}
        .stage.pending {{ border-left-color: #718096; opacity: 0.6; }}
        .stage.running {{
            border-left-color: #ecc94b;
            animation: pulse 1s infinite;
        }}
        .stage.completed {{ border-left-color: #48bb78; }}
        .stage.failed {{ border-left-color: #f56565; }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        .stage-name {{ font-weight: 600; margin-bottom: 5px; }}
        .stage-status {{ font-size: 0.85em; color: #888; }}
        .progress-bar {{
            height: 4px;
            background: #333;
            border-radius: 2px;
            margin-top: 10px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: #4299e1;
            transition: width 0.1s;
        }}
        .info-panel {{
            background: #16213e;
            padding: 15px;
            border-radius: 8px;
        }}
        .time-display {{
            font-family: monospace;
            font-size: 1.2em;
            color: #4299e1;
        }}
        .speed-control {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        select {{
            padding: 8px;
            border: 1px solid #333;
            border-radius: 4px;
            background: #1a1a2e;
            color: #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>{self._recording.pipeline_name}</h1>
                <div class="meta">
                    Run ID: {self._recording.run_id} |
                    Duration: {self._recording.total_duration_ms}ms |
                    Status: {self._recording.status}
                </div>
            </div>
        </div>

        <div class="controls">
            <button class="play-btn" id="playBtn" onclick="togglePlay()">▶ Play</button>
            <button class="stop-btn" id="stopBtn" onclick="stop()">⬛ Stop</button>
            <button onclick="stepBack()">⏮</button>
            <button onclick="stepForward()">⏭</button>
            <div class="speed-control">
                <label>Speed:</label>
                <select id="speedSelect" onchange="setSpeed(this.value)">
                    <option value="0.25">0.25x</option>
                    <option value="0.5">0.5x</option>
                    <option value="1" selected>1x</option>
                    <option value="2">2x</option>
                    <option value="4">4x</option>
                </select>
            </div>
            <div class="time-display" id="timeDisplay">0:00.000 / 0:00.000</div>
        </div>

        <div class="timeline" onclick="seekTo(event)">
            <div class="timeline-progress" id="timelineProgress"></div>
            <div class="timeline-cursor" id="timelineCursor"></div>
            <div class="timeline-markers" id="timelineMarkers"></div>
        </div>

        <div class="stages-container" id="stagesContainer"></div>

        <div class="info-panel">
            <div id="frameInfo">Click Play to start visualization</div>
        </div>
    </div>

    <script>
        const recording = {recording_data};
        let currentIndex = 0;
        let isPlaying = false;
        let speed = 1.0;
        let lastTime = 0;
        let currentTimestamp = 0;

        function init() {{
            renderStages();
            renderTimeline();
            updateDisplay();
        }}

        function renderStages() {{
            const container = document.getElementById('stagesContainer');
            container.innerHTML = recording.stages.map(stageId => `
                <div class="stage pending" id="stage-${{stageId}}">
                    <div class="stage-name">${{stageId}}</div>
                    <div class="stage-status">Pending</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%"></div>
                    </div>
                </div>
            `).join('');
        }}

        function renderTimeline() {{
            const markers = document.getElementById('timelineMarkers');
            const duration = recording.total_duration_ms / 1000;

            recording.frames.forEach(frame => {{
                if (frame.current_stage_id) {{
                    const marker = document.createElement('div');
                    marker.className = 'marker';
                    marker.style.left = `${{(frame.timestamp / duration) * 100}}%`;
                    marker.style.background = getStatusColor(frame.frame_type);
                    markers.appendChild(marker);
                }}
            }});
        }}

        function getStatusColor(frameType) {{
            const colors = {{
                'stage_start': '#4299e1',
                'stage_complete': '#48bb78',
                'stage_error': '#f56565',
                'data_flow': '#9f7aea',
            }};
            return colors[frameType] || '#718096';
        }}

        function togglePlay() {{
            if (isPlaying) {{
                pause();
            }} else {{
                play();
            }}
        }}

        function play() {{
            isPlaying = true;
            document.getElementById('playBtn').textContent = '⏸ Pause';
            document.getElementById('playBtn').className = 'pause-btn';
            lastTime = performance.now();
            animate();
        }}

        function pause() {{
            isPlaying = false;
            document.getElementById('playBtn').textContent = '▶ Play';
            document.getElementById('playBtn').className = 'play-btn';
        }}

        function stop() {{
            pause();
            currentIndex = 0;
            currentTimestamp = 0;
            updateDisplay();
        }}

        function animate() {{
            if (!isPlaying) return;

            const now = performance.now();
            const elapsed = (now - lastTime) / 1000;
            lastTime = now;

            currentTimestamp += elapsed * speed;

            const duration = recording.total_duration_ms / 1000;
            if (currentTimestamp >= duration) {{
                currentTimestamp = duration;
                pause();
            }}

            // Find current frame
            while (currentIndex < recording.frames.length - 1 &&
                   recording.frames[currentIndex + 1].timestamp <= currentTimestamp) {{
                currentIndex++;
            }}

            updateDisplay();
            requestAnimationFrame(animate);
        }}

        function updateDisplay() {{
            const frame = recording.frames[currentIndex];
            if (!frame) return;

            const duration = recording.total_duration_ms / 1000;
            const progress = (currentTimestamp / duration) * 100;

            // Update timeline
            document.getElementById('timelineProgress').style.width = `${{progress}}%`;
            document.getElementById('timelineCursor').style.left = `${{progress}}%`;

            // Update time display
            document.getElementById('timeDisplay').textContent =
                `${{formatTime(currentTimestamp)}} / ${{formatTime(duration)}}`;

            // Update stages
            for (const [stageId, stageData] of Object.entries(frame.stages)) {{
                const el = document.getElementById(`stage-${{stageId}}`);
                if (el) {{
                    el.className = `stage ${{stageData.status}}`;
                    el.querySelector('.stage-status').textContent =
                        `${{stageData.status}} ${{stageData.progress ? Math.round(stageData.progress * 100) + '%' : ''}}`;
                    el.querySelector('.progress-fill').style.width = `${{(stageData.progress || 0) * 100}}%`;
                }}
            }}

            // Update info
            document.getElementById('frameInfo').textContent = frame.message;
        }}

        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60);
            const secs = (seconds % 60).toFixed(3);
            return `${{mins}}:${{secs.padStart(6, '0')}}`;
        }}

        function seekTo(event) {{
            const rect = event.target.getBoundingClientRect();
            const percent = (event.clientX - rect.left) / rect.width;
            currentTimestamp = (recording.total_duration_ms / 1000) * percent;

            // Find frame at timestamp
            currentIndex = 0;
            while (currentIndex < recording.frames.length - 1 &&
                   recording.frames[currentIndex + 1].timestamp <= currentTimestamp) {{
                currentIndex++;
            }}

            updateDisplay();
        }}

        function stepForward() {{
            if (currentIndex < recording.frames.length - 1) {{
                currentIndex++;
                currentTimestamp = recording.frames[currentIndex].timestamp;
                updateDisplay();
            }}
        }}

        function stepBack() {{
            if (currentIndex > 0) {{
                currentIndex--;
                currentTimestamp = recording.frames[currentIndex].timestamp;
                updateDisplay();
            }}
        }}

        function setSpeed(value) {{
            speed = parseFloat(value);
        }}

        init();
    </script>
</body>
</html>
"""

    def _export_markdown(self) -> str:
        """Export to Markdown report."""
        lines = [
            f"# Execution Report: {self._recording.pipeline_name}",
            "",
            f"**Run ID:** {self._recording.run_id}",
            f"**Status:** {self._recording.status}",
            f"**Duration:** {self._recording.total_duration_ms}ms",
            f"**Start Time:** {self._recording.start_time.isoformat()}",
            f"**End Time:** {self._recording.end_time.isoformat() if self._recording.end_time else 'N/A'}",
            "",
            "## Stages",
            "",
        ]

        # Get final state for each stage
        final_frame = self._recording.frames[-1] if self._recording.frames else None
        if final_frame:
            for stage_id in self._recording.stages:
                stage = final_frame.stages.get(stage_id)
                if stage:
                    status_emoji = {
                        StageStatus.COMPLETED: "✅",
                        StageStatus.FAILED: "❌",
                        StageStatus.RUNNING: "🔄",
                        StageStatus.PENDING: "⏳",
                        StageStatus.SKIPPED: "⏭️",
                        StageStatus.PAUSED: "⏸️",
                    }.get(stage.status, "❓")

                    lines.append(f"### {status_emoji} {stage_id}")
                    lines.append(f"- **Status:** {stage.status.value}")
                    lines.append(f"- **Duration:** {stage.duration_ms}ms")
                    if stage.error:
                        lines.append(f"- **Error:** {stage.error}")
                    lines.append("")

        # Timeline
        lines.append("## Timeline")
        lines.append("")
        lines.append("| Time | Event | Stage |")
        lines.append("|------|-------|-------|")

        for frame in self._recording.frames[:50]:  # Limit to first 50 events
            time_str = f"{frame.timestamp:.3f}s"
            lines.append(f"| {time_str} | {frame.message[:40]} | {frame.current_stage_id or '-'} |")

        if len(self._recording.frames) > 50:
            lines.append(f"| ... | {len(self._recording.frames) - 50} more events | ... |")

        return "\n".join(lines)

    def _export_mermaid(self) -> str:
        """Export to Mermaid sequence diagram."""
        lines = [
            "sequenceDiagram",
            f"    title Pipeline: {self._recording.pipeline_name}",
            "",
        ]

        # Define participants
        lines.append("    participant P as Pipeline")
        for stage_id in self._recording.stages:
            lines.append(f"    participant {stage_id}")

        lines.append("")

        # Add events
        current_stage = None
        for frame in self._recording.frames:
            if frame.frame_type.value == "stage_start" and frame.current_stage_id:
                if current_stage:
                    lines.append(f"    {current_stage}-->>P: complete")
                lines.append(f"    P->>+{frame.current_stage_id}: start")
                current_stage = frame.current_stage_id

            elif frame.frame_type.value == "stage_complete" and frame.current_stage_id:
                lines.append(f"    {frame.current_stage_id}->>-P: done ({frame.stages.get(frame.current_stage_id, {}).duration_ms if hasattr(frame.stages.get(frame.current_stage_id, {}), 'duration_ms') else '?'}ms)")

            elif frame.frame_type.value == "data_flow" and frame.active_flows:
                for flow in frame.active_flows[-1:]:
                    lines.append(f"    {flow.from_stage}->>{flow.to_stage}: data ({flow.data_size_bytes}b)")

        return "\n".join(lines)

    def _export_svg_sequence(self) -> str:
        """Export to SVG timeline visualization."""
        width = 1000
        height = 200 + len(self._recording.stages) * 60
        duration = self._recording.total_duration_ms / 1000

        svg_lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
            '<style>',
            '  .stage-label { font: 12px sans-serif; fill: #333; }',
            '  .time-label { font: 10px monospace; fill: #666; }',
            '  .bar { stroke: #333; stroke-width: 1; }',
            '  .completed { fill: #48bb78; }',
            '  .failed { fill: #f56565; }',
            '  .running { fill: #ecc94b; }',
            '</style>',
            '',
            f'<text x="10" y="25" class="stage-label" font-weight="bold">{self._recording.pipeline_name}</text>',
            f'<text x="10" y="45" class="time-label">Duration: {self._recording.total_duration_ms}ms</text>',
            '',
        ]

        # Draw timeline axis
        axis_y = 70
        svg_lines.append(f'<line x1="100" y1="{axis_y}" x2="900" y2="{axis_y}" stroke="#ccc" stroke-width="2"/>')

        # Time markers
        for i in range(5):
            x = 100 + (800 * i / 4)
            time_val = duration * i / 4
            svg_lines.append(f'<line x1="{x}" y1="{axis_y-5}" x2="{x}" y2="{axis_y+5}" stroke="#999"/>')
            svg_lines.append(f'<text x="{x}" y="{axis_y+20}" class="time-label" text-anchor="middle">{time_val:.2f}s</text>')

        # Draw stage bars
        y_offset = 100
        for i, stage_id in enumerate(self._recording.stages):
            y = y_offset + i * 60

            svg_lines.append(f'<text x="10" y="{y+20}" class="stage-label">{stage_id}</text>')

            # Find stage timing from frames
            start_time = None
            end_time = None
            status = "pending"

            for frame in self._recording.frames:
                stage_data = frame.stages.get(stage_id)
                if stage_data:
                    if stage_data.status == StageStatus.RUNNING and start_time is None:
                        start_time = frame.timestamp
                    elif stage_data.status in (StageStatus.COMPLETED, StageStatus.FAILED):
                        end_time = frame.timestamp
                        status = stage_data.status.value
                        break

            if start_time is not None:
                x_start = 100 + (start_time / duration) * 800
                x_end = 100 + ((end_time or duration) / duration) * 800
                bar_width = max(x_end - x_start, 5)

                svg_lines.append(
                    f'<rect x="{x_start}" y="{y+5}" width="{bar_width}" height="30" '
                    f'class="bar {status}" rx="3"/>'
                )

        svg_lines.append('</svg>')
        return '\n'.join(svg_lines)
