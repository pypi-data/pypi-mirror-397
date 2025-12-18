# Pipeline Debugging

FlowMason provides a full-featured debugger for stepping through pipeline execution, setting breakpoints, and inspecting stage inputs/outputs.

## Overview

The debugger supports:
- **Breakpoints** - Pause execution before specific stages
- **Stepping** - Execute one stage at a time
- **Pause/Resume** - Stop and continue execution on demand
- **Variable Inspection** - View stage inputs, outputs, and config
- **Exception Breakpoints** - Pause on specific error types
- **WebSocket Events** - Real-time debug updates

## VSCode Integration

The FlowMason VSCode extension provides a native debugging experience using the Debug Adapter Protocol (DAP).

### Starting a Debug Session

1. Open a `.pipeline.json` file
2. Set breakpoints by clicking in the gutter (left margin)
3. Press `F5` or use `Run > Start Debugging`
4. Select "FlowMason" as the debugger

### Debug Controls

| Action | Shortcut | Description |
|--------|----------|-------------|
| Continue | F5 | Resume execution until next breakpoint |
| Step Over | F10 | Execute one stage then pause |
| Pause | F6 | Pause running execution |
| Stop | Shift+F5 | Stop execution entirely |

### Setting Breakpoints

Click in the gutter next to any stage's `"id"` line to set a breakpoint. When execution reaches that stage, it will pause.

```json
{
  "stages": [
    {
      "id": "fetch-data",  // ← Click here to set breakpoint
      "component_type": "http_request",
      "config": { ... }
    }
  ]
}
```

### Viewing Variables

When paused, the Variables pane shows:
- **Input** - Data passed to the current stage
- **Output** - Result from the stage (after completion)
- **Config** - Stage configuration

### Call Stack

The Call Stack shows:
- Current stage at the top
- Completed stages below (execution history)

## Debug Launch Configuration

Create a `.vscode/launch.json` file for custom debug configurations:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "flowmason",
      "request": "launch",
      "name": "Debug Pipeline",
      "pipeline": "${file}",
      "input": {
        "query": "test input"
      },
      "stopOnEntry": false
    },
    {
      "type": "flowmason",
      "request": "launch",
      "name": "Debug with Input File",
      "pipeline": "${workspaceFolder}/pipelines/my-pipeline.pipeline.json",
      "inputFile": "${workspaceFolder}/inputs/test-input.json",
      "stopOnEntry": true
    }
  ]
}
```

### Launch Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `pipeline` | string | Path to pipeline file (required) |
| `input` | object | Input data for the pipeline |
| `inputFile` | string | Path to JSON file with input data |
| `stopOnEntry` | boolean | Pause before first stage (default: false) |

## Exception Breakpoints

Configure the debugger to pause on specific error types:

1. Open the Breakpoints pane in VSCode
2. Enable exception filters:
   - **All Errors** - Pause on any error
   - **Uncaught Errors** - Pause on unhandled errors
   - **Error Severity** - Pause on ERROR level
   - **Timeout Errors** - Pause on timeouts
   - **Validation Errors** - Pause on validation failures
   - **Connectivity Errors** - Pause on network errors

When an exception is caught, the debugger shows:
- Error description
- Error type and severity
- Stack trace (if available)
- Stage context

## API Debugging

You can also control debugging via the REST API:

### Start Debug Run

```bash
curl -X POST http://localhost:8999/api/v1/debug/run \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline": {
      "name": "test-pipeline",
      "stages": [...]
    },
    "inputs": {"key": "value"},
    "breakpoints": ["stage-1", "stage-3"],
    "stop_on_entry": false
  }'
```

### Pause Execution

```bash
curl -X POST http://localhost:8999/api/v1/runs/{run_id}/debug/pause
```

### Resume Execution

```bash
curl -X POST http://localhost:8999/api/v1/runs/{run_id}/debug/resume
```

### Step to Next Stage

```bash
curl -X POST http://localhost:8999/api/v1/runs/{run_id}/debug/step
```

### Stop Execution

```bash
curl -X POST http://localhost:8999/api/v1/runs/{run_id}/debug/stop
```

### Set Breakpoints

```bash
curl -X PUT http://localhost:8999/api/v1/runs/{run_id}/debug/breakpoints \
  -H "Content-Type: application/json" \
  -d '{"stage_ids": ["stage-1", "stage-3"]}'
```

### Set Exception Breakpoints

```bash
curl -X PUT http://localhost:8999/api/v1/runs/{run_id}/debug/exception-breakpoints \
  -H "Content-Type: application/json" \
  -d '{"filters": ["all", "timeout"]}'
```

### Get Debug State

```bash
curl http://localhost:8999/api/v1/runs/{run_id}/debug/state
```

Response:
```json
{
  "run_id": "abc123",
  "mode": "paused",
  "breakpoints": ["stage-1", "stage-3"],
  "exception_breakpoints": ["all"],
  "current_stage_id": "stage-1",
  "paused_at": "2024-01-15T10:30:00Z",
  "timeout_at": "2024-01-15T10:35:00Z",
  "pause_reason": "breakpoint"
}
```

### Get Exception Info

```bash
curl http://localhost:8999/api/v1/runs/{run_id}/debug/exception-info
```

## WebSocket Debug Events

Connect to the WebSocket endpoint for real-time debug events:

```javascript
const ws = new WebSocket('ws://localhost:8999/api/v1/ws/runs');

// Subscribe to run updates
ws.send(JSON.stringify({
  type: 'subscribe',
  run_id: 'your-run-id'
}));

// Debug commands via WebSocket
ws.send(JSON.stringify({ type: 'pause', run_id: 'your-run-id' }));
ws.send(JSON.stringify({ type: 'resume', run_id: 'your-run-id' }));
ws.send(JSON.stringify({ type: 'step', run_id: 'your-run-id' }));
ws.send(JSON.stringify({ type: 'stop', run_id: 'your-run-id' }));
```

### Event Types

| Event | Description |
|-------|-------------|
| `run_started` | Pipeline execution started |
| `stage_started` | Stage execution began |
| `stage_completed` | Stage finished successfully |
| `stage_failed` | Stage encountered an error |
| `execution_paused` | Execution paused (breakpoint or manual) |
| `execution_resumed` | Execution resumed |
| `run_completed` | Pipeline finished successfully |
| `run_failed` | Pipeline failed |
| `stream_start` | LLM streaming started |
| `token_chunk` | LLM token received |
| `stream_end` | LLM streaming completed |

## Debug Modes

| Mode | Description |
|------|-------------|
| `running` | Normal execution |
| `paused` | Execution paused (breakpoint, manual, or exception) |
| `stepping` | Step mode - pause after each stage |
| `stopped` | Execution terminated |

## Auto-Resume Timeout

To prevent indefinite pauses, the debugger automatically resumes after 5 minutes (configurable). This prevents resource leaks if a debug session is abandoned.

## Advanced: Prompt Editing

During a pause, you can modify LLM prompts before execution:

```bash
# Get current prompt
curl http://localhost:8999/api/v1/runs/{run_id}/debug/stage/{stage_id}/prompt

# Update prompt and rerun
curl -X POST http://localhost:8999/api/v1/runs/{run_id}/debug/stage/{stage_id}/rerun \
  -H "Content-Type: application/json" \
  -d '{"modified_prompt": "Updated prompt text..."}'
```

This is useful for iteratively testing LLM prompts without restarting the entire pipeline.

## Best Practices

1. **Use breakpoints strategically** - Set them before stages you want to inspect
2. **Check stage outputs** - Verify data is being transformed correctly
3. **Watch for exceptions** - Enable exception breakpoints during development
4. **Use step mode for complex flows** - Step through conditional logic
5. **Don't forget to resume** - The auto-timeout prevents runaway pauses

---

# Time Travel Debugging

FlowMason Studio provides time travel debugging capabilities that let you navigate through execution history, inspect state at any point, and replay with modified inputs.

## Time Travel Overview

Time travel debugging enables:

- **Execution Timeline**: Navigate through every stage of a pipeline run
- **State Inspection**: View inputs, outputs, and variables at any point
- **Step Back/Forward**: Move through execution history like a debugger
- **Replay**: Re-run from any snapshot with original or modified inputs
- **What-If Analysis**: Test alternative inputs without restarting from scratch
- **State Diffs**: See exactly what changed between any two points

## Execution Timeline

Get the complete execution timeline for a run:

```http
GET /api/v1/debug/time-travel/runs/{run_id}/timeline
```

**Response:**
```json
{
  "timeline": {
    "run_id": "run_abc123",
    "pipeline_id": "pipe_xyz",
    "total_snapshots": 8,
    "total_duration_ms": 4500,
    "status": "completed",
    "entries": [
      {
        "snapshot_id": "snap_001",
        "stage_id": "stage_input",
        "stage_name": "Parse Input",
        "component_type": "json_transform",
        "snapshot_type": "stage_complete",
        "timestamp": "2024-01-15T10:30:00Z",
        "duration_ms": 150,
        "status": "completed",
        "is_current": false,
        "has_outputs": true,
        "output_preview": "{\"parsed\": true, \"data\": ...}"
      }
    ],
    "current_index": 1,
    "can_step_back": true,
    "can_step_forward": false
  }
}
```

## Viewing Snapshots

### Get Snapshot Details

```http
GET /api/v1/debug/time-travel/snapshots/{snapshot_id}
```

Returns complete state including:
- `pipeline_inputs` - Original pipeline inputs
- `stage_inputs` - Inputs passed to this stage
- `stage_outputs` - Outputs from this stage
- `accumulated_outputs` - All outputs up to this point
- `variables` - Pipeline variables
- `completed_stages` - Stages executed so far
- `pending_stages` - Stages remaining

### Snapshot Types

| Type | Description |
|------|-------------|
| `stage_start` | Captured before a stage executes |
| `stage_complete` | Captured after successful execution |
| `stage_failed` | Captured when a stage fails |
| `checkpoint` | Manual checkpoint |
| `branch_point` | Where execution branched |

## Navigation Commands

### Step Back

```http
GET /api/v1/debug/time-travel/runs/{run_id}/step-back?from_snapshot={snapshot_id}
```

### Step Forward

```http
GET /api/v1/debug/time-travel/runs/{run_id}/step-forward?from_snapshot={snapshot_id}
```

### Jump to Snapshot

```http
POST /api/v1/debug/time-travel/jump
Content-Type: application/json

{
  "snapshot_id": "snap_003",
  "restore_state": true
}
```

## State Comparison

### Compare Any Two Points

```http
GET /api/v1/debug/time-travel/diff?from_snapshot=snap_001&to_snapshot=snap_003
```

**Response:**
```json
{
  "diff": {
    "from_snapshot_id": "snap_001",
    "to_snapshot_id": "snap_003",
    "added_outputs": {
      "stage_llm": {"summary": "This is a greeting..."}
    },
    "modified_outputs": {},
    "removed_outputs": [],
    "added_variables": {"iteration_count": 1},
    "modified_variables": {},
    "stages_completed": ["stage_llm"],
    "duration_ms": 2100,
    "tokens_used": 450
  }
}
```

### See What a Stage Changed

```http
GET /api/v1/debug/time-travel/runs/{run_id}/diff/{stage_id}
```

## Replay Execution

### Replay from a Point

Re-execute the pipeline from any snapshot:

```http
POST /api/v1/debug/time-travel/replay
Content-Type: application/json

{
  "snapshot_id": "snap_002",
  "modified_inputs": null,
  "debug_mode": false
}
```

### Replay with Modified Inputs

```http
POST /api/v1/debug/time-travel/replay
Content-Type: application/json

{
  "snapshot_id": "snap_002",
  "modified_inputs": {
    "text": "Different input"
  },
  "debug_mode": true
}
```

## What-If Analysis

Test alternative scenarios without starting from scratch:

```http
POST /api/v1/debug/time-travel/whatif
Content-Type: application/json

{
  "snapshot_id": "snap_001",
  "modifications": {
    "text": "Different input text",
    "var:temperature": 0.8
  },
  "compare_with_original": true
}
```

### Modification Syntax

- Regular keys modify pipeline inputs: `"input_key": "new_value"`
- Variables use `var:` prefix: `"var:my_variable": "new_value"`

## Python Integration

```python
from flowmason_studio.services.time_travel_storage import get_time_travel_storage

storage = get_time_travel_storage()

# Get execution timeline
timeline = storage.get_timeline("run_abc123")
print(f"Total snapshots: {timeline.total_snapshots}")

# Get specific snapshot
snapshot = storage.get_snapshot("snap_001")
print(f"Inputs: {snapshot.stage_inputs}")
print(f"Outputs: {snapshot.stage_outputs}")

# Compare two points
diff = storage.get_diff("snap_001", "snap_003")
print(f"Added outputs: {list(diff.added_outputs.keys())}")

# Create replay
result = storage.create_replay_run(
    original_run_id="run_abc123",
    from_snapshot_id="snap_002",
    modifications={"input_text": "Modified input"},
)
print(f"Replay started: {result.replay_run_id}")
```

## Cleanup

### Delete Snapshots for a Run

```http
DELETE /api/v1/debug/time-travel/runs/{run_id}/snapshots
```

### Clean Up Old Snapshots

```http
POST /api/v1/debug/time-travel/cleanup?days=7
```

## Time Travel API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/debug/time-travel/runs/{run_id}/timeline` | GET | Get execution timeline |
| `/debug/time-travel/runs/{run_id}/snapshots` | GET | List all snapshots |
| `/debug/time-travel/snapshots/{snapshot_id}` | GET | Get specific snapshot |
| `/debug/time-travel/runs/{run_id}/stages/{stage_id}/snapshot` | GET | Get stage snapshot |
| `/debug/time-travel/diff` | GET | Compare two snapshots |
| `/debug/time-travel/runs/{run_id}/diff/{stage_id}` | GET | Get stage diff |
| `/debug/time-travel/replay` | POST | Start replay |
| `/debug/time-travel/replay/{replay_id}` | GET | Get replay status |
| `/debug/time-travel/whatif` | POST | Start what-if analysis |
| `/debug/time-travel/jump` | POST | Jump to snapshot |
| `/debug/time-travel/runs/{run_id}/step-back` | GET | Step back |
| `/debug/time-travel/runs/{run_id}/step-forward` | GET | Step forward |
| `/debug/time-travel/runs/{run_id}/snapshots` | DELETE | Delete run snapshots |
| `/debug/time-travel/cleanup` | POST | Clean old snapshots |
