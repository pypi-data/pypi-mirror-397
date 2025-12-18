# Visual Debugging (Animated Execution)

FlowMason provides animated visualization of pipeline execution, allowing you to watch data flow through stages in real-time or replay recorded executions.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Execution Visualization                          [▶ Play] [⏸] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐  ═══▶  ┌─────────┐  ───▶  ┌─────────┐            │
│  │ fetch   │  data  │ process │        │ output  │            │
│  │ ✓ 1.2s  │  ════▶ │ ⟳ 45%   │        │ ○ wait  │            │
│  └─────────┘        └─────────┘        └─────────┘            │
│                          │                                      │
│                     ┌────┴────┐                                │
│                     │ Tokens: 234/1000                         │
│                     │ "Processing customer..."                  │
│                     └─────────┘                                │
│                                                                 │
│  Timeline: ═══════════════●═══════════════════════════════     │
│            0s            2.5s                           10s     │
└─────────────────────────────────────────────────────────────────┘
```

## Recording Executions

### Python API

```python
from flowmason_core.visualization import ExecutionRecorder

# Create recorder
recorder = ExecutionRecorder()

# Start recording
recorder.start_recording(
    run_id="run-123",
    pipeline_name="my-pipeline",
    stages=["fetch", "process", "output"]
)

# Record stage events (normally done automatically by executor)
recorder.record_stage_start("fetch")
recorder.record_stage_progress("fetch", 50)  # 50% complete
recorder.record_stage_complete("fetch", duration_ms=1200, output_preview='{"data": [...]}')

recorder.record_stage_start("process")
recorder.record_stage_progress("process", 25)
recorder.record_stage_progress("process", 50)
recorder.record_stage_progress("process", 75)
recorder.record_stage_complete("process", duration_ms=3500)

# Stop and get recording
recording = recorder.stop_recording()

print(f"Recorded {len(recording.frames)} frames")
print(f"Total duration: {recording.duration_ms}ms")
```

## Playback Controls

### ExecutionAnimator

```python
from flowmason_core.visualization import ExecutionAnimator

# Create animator from recording
animator = ExecutionAnimator(recording)

# Playback controls
animator.play()           # Start playback
animator.pause()          # Pause playback
animator.stop()           # Stop and reset
animator.seek(2500)       # Seek to 2.5 seconds
animator.seek_percent(50) # Seek to 50% of duration

# Speed control
animator.speed = 2.0      # 2x speed
animator.speed = 0.5      # Half speed

# Available speeds
print(animator.SPEED_OPTIONS)  # [0.5, 1.0, 2.0, 4.0]

# Navigation
animator.step_forward()       # Next frame
animator.step_backward()      # Previous frame
animator.skip_to_stage("process")  # Jump to stage
animator.skip_to_next_stage()
animator.skip_to_previous_stage()
```

### Callbacks

```python
# Set callbacks for UI updates
animator.set_frame_callback(lambda frame: update_ui(frame))
animator.set_position_callback(lambda pos: update_timeline(pos))

# Frame contains stage states
def update_ui(frame):
    for stage_id, stage_state in frame.stages.items():
        print(f"{stage_id}: {stage_state.status} ({stage_state.progress}%)")
```

## Export Formats

### RecordingExporter

```python
from flowmason_core.visualization import RecordingExporter
from flowmason_core.visualization.exporter import ExportFormat

exporter = RecordingExporter(recording)

# Export to JSON
json_data = exporter.export(ExportFormat.JSON)

# Export to HTML (interactive player)
html_page = exporter.export(ExportFormat.HTML)

# Export to Markdown (static report)
markdown = exporter.export(ExportFormat.MARKDOWN)

# Export to Mermaid diagram
mermaid = exporter.export(ExportFormat.MERMAID)

# Export to SVG sequence diagram
svg = exporter.export(ExportFormat.SVG_SEQUENCE)

# Save to file
exporter.export(ExportFormat.HTML, output_path=Path("execution.html"))
```

### Export Format Details

| Format | Description | Use Case |
|--------|-------------|----------|
| `JSON` | Raw recording data | API responses, storage |
| `HTML` | Interactive player | Sharing, documentation |
| `MARKDOWN` | Text report | README files, tickets |
| `MERMAID` | Mermaid.js diagram | Documentation |
| `SVG_SEQUENCE` | SVG sequence diagram | Presentations |

## Frame Types

```python
from flowmason_core.visualization import FrameType

# Available frame types
FrameType.STAGE_START      # Stage began execution
FrameType.STAGE_PROGRESS   # Progress update (0-100)
FrameType.STAGE_COMPLETE   # Stage finished successfully
FrameType.STAGE_ERROR      # Stage failed with error
FrameType.DATA_FLOW        # Data passed between stages
FrameType.TOKEN_STREAM     # LLM token streaming update
```

## VSCode Integration

### Opening Visual Debugger

1. Run a pipeline with debugging enabled
2. Click "Open Visual Debugger" in the debug toolbar
3. Or use Command Palette: `FlowMason: Open Visual Debugger`

### Features

- **Real-time Animation**: Watch execution as it happens
- **Timeline Scrubbing**: Drag to any point in time
- **Stage Details**: Click stages to see inputs/outputs
- **Token Streaming**: Watch LLM responses generate
- **Data Flow Arrows**: Animated data flow between stages

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `←` | Step backward |
| `→` | Step forward |
| `[` | Previous stage |
| `]` | Next stage |
| `1-4` | Set speed (1x, 2x, 3x, 4x) |

## CLI Commands

```bash
# Record execution to file
fm run pipeline.json --record execution.json

# Play back recording
fm playback execution.json

# Export recording
fm export-recording execution.json --format html --output report.html
```

## Best Practices

1. **Record Important Runs**: Enable recording for debugging sessions
2. **Use Speed Controls**: Speed up long executions, slow down complex parts
3. **Export for Documentation**: Export HTML for sharing with team
4. **Monitor Token Usage**: Watch token streaming for LLM optimization
