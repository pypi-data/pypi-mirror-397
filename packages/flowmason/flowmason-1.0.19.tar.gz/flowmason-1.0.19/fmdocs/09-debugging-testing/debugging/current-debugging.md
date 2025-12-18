# Debugging Pipelines

FlowMason provides comprehensive debugging capabilities through VSCode's Debug Adapter Protocol (DAP).

## Quick Start

1. Open a `.pipeline.json` file
2. Set breakpoints (F9 on a stage in the JSON or DAG view)
3. Press F5 to start debugging
4. Step through with F10

## Debug Adapter Protocol (DAP)

FlowMason implements VSCode's standard Debug Adapter Protocol, providing:

- Breakpoints on pipeline stages
- Step over (next stage)
- Step into (sub-pipelines)
- Variables inspection
- Watch expressions
- Call stack view
- Exception breakpoints

## Setting Breakpoints

### In JSON Editor

Click in the gutter next to a stage definition:

```json
{
  "stages": [
    {
      "id": "fetch",        // ← Click gutter here
      "component_type": "http-request",
      ...
    }
  ]
}
```

### In DAG Canvas

Right-click a stage node > "Toggle Breakpoint"

Or click the breakpoint indicator on the node.

### Via Keyboard

1. Place cursor on stage
2. Press F9

### Conditional Breakpoints

Right-click breakpoint > "Edit Breakpoint":

```
Condition: {{fetch.output.status_code}} != 200
```

The breakpoint only triggers when the condition is true.

### Exception Breakpoints

Enable in the Breakpoints panel:
- Break on all exceptions
- Break on uncaught exceptions
- Break on specific error types (VALIDATION, TIMEOUT, etc.)

## Debug Controls

| Control | Keybinding | Description |
|---------|------------|-------------|
| Continue | F5 | Run to next breakpoint |
| Step Over | F10 | Execute next stage |
| Step Into | F11 | Enter sub-pipeline |
| Step Out | Shift+F11 | Exit sub-pipeline |
| Restart | Ctrl+Shift+F5 | Restart from beginning |
| Stop | Shift+F5 | Stop execution |

## Variables Panel

When paused, the Variables panel shows:

```
VARIABLES
├── Input
│   ├── url: "https://api.example.com"
│   └── method: "GET"
├── Output (after execution)
│   ├── body: {...}
│   └── status_code: 200
├── Context
│   ├── run_id: "run-abc123"
│   └── stage_id: "fetch"
└── Previous Stages
    └── setup
        └── output: {...}
```

### Inspecting Objects

Click to expand objects and arrays. Double-click to copy values.

## Watch Expressions

Add expressions to monitor:

```
{{fetch.output.body.data.length}}
{{process.output.items[0].name}}
{{context.run_id}}
```

## Call Stack

Shows the execution hierarchy:

```
CALL STACK
├── main-pipeline
│   ├── fetch (current) ●
│   ├── process
│   └── output
└── sub-pipeline (if entered)
    ├── step1
    └── step2
```

Click a frame to view its variables.

## Prompt Editor

During debugging of LLM stages, the Prompt Editor panel activates:

### Viewing Prompts

When paused at a @node stage:

```
┌─────────────────────────────────────────┐
│ PROMPT EDITOR                           │
├─────────────────────────────────────────┤
│ Stage: generate_content                 │
│ Component: generator                    │
├─────────────────────────────────────────┤
│ System Prompt:                          │
│ ┌─────────────────────────────────────┐ │
│ │ You are a helpful assistant...      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ User Prompt:                            │
│ ┌─────────────────────────────────────┐ │
│ │ Summarize the following text:       │ │
│ │ {{input.text}}                      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Edit] [Re-run] [Compare]               │
└─────────────────────────────────────────┘
```

### Editing Prompts

1. Click "Edit" to enable editing
2. Modify the prompt text
3. Click "Re-run Stage" to execute with new prompt
4. View output in the comparison panel

### Side-by-Side Comparison

Compare outputs from different prompt versions:

```
┌─────────────────┬─────────────────┐
│ Version 1       │ Version 2       │
├─────────────────┼─────────────────┤
│ Output:         │ Output:         │
│ The text talks  │ Key points:     │
│ about several   │ 1. Topic A      │
│ important...    │ 2. Topic B...   │
├─────────────────┼─────────────────┤
│ Tokens: 245     │ Tokens: 189     │
│ Time: 1.2s      │ Time: 0.9s      │
└─────────────────┴─────────────────┘
```

### Token Streaming

Watch LLM responses arrive in real-time:

```
Output (streaming):
The article discusses█
```

Enable in settings: `flowmason.debugger.showTokenStream`

## Debug Console

View execution logs and evaluate expressions:

```
> {{fetch.output.body}}
{ "data": [...], "meta": {...} }

> {{input.url.startsWith("https")}}
true
```

## Launch Configurations

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "flowmason",
      "request": "launch",
      "name": "Debug Current Pipeline",
      "pipeline": "${file}",
      "stopOnEntry": true
    },
    {
      "type": "flowmason",
      "request": "launch",
      "name": "Debug with Test Input",
      "pipeline": "pipelines/main.pipeline.json",
      "inputFile": "tests/input.json"
    },
    {
      "type": "flowmason",
      "request": "launch",
      "name": "Debug Specific Stage",
      "pipeline": "pipelines/main.pipeline.json",
      "input": { "url": "https://example.com" },
      "breakpoints": ["process", "output"]
    }
  ]
}
```

### Configuration Options

| Property | Type | Description |
|----------|------|-------------|
| `pipeline` | string | Pipeline file path |
| `input` | object | Input data |
| `inputFile` | string | Path to JSON input file |
| `stopOnEntry` | boolean | Break on first stage |
| `breakOnException` | boolean | Break on any error |
| `breakpoints` | string[] | Pre-set breakpoint stage IDs |
| `env` | object | Environment variables |

## WebSocket Events

The debug session communicates via WebSocket:

```
ws://localhost:8999/api/v1/ws/runs
```

Events received during debugging:

| Event | Description |
|-------|-------------|
| `stage_started` | Stage began execution |
| `stage_completed` | Stage finished successfully |
| `stage_failed` | Stage encountered error |
| `execution_paused` | Hit breakpoint |
| `token_chunk` | LLM token received |
| `stream_start` | LLM streaming began |
| `stream_end` | LLM streaming ended |

## Debugging Control Flow

### Conditional Branches

When debugging a `conditional` stage:
1. Variables panel shows the condition value
2. Step over shows which branch was taken
3. Skipped branches are grayed in DAG

### Loops (ForEach)

When debugging a `foreach` stage:
1. Variables panel shows current item and index
2. Step through each iteration
3. Watch expression shows iteration progress

### Error Handling (TryCatch)

When debugging a `trycatch` stage:
1. Try stages execute normally
2. On error, catch stages execute
3. Exception breakpoints can pause on error
4. Variables show error details

## Troubleshooting

### Breakpoints Not Hit

- Ensure Studio is running
- Check breakpoint is on valid stage ID
- Verify pipeline path in launch config

### Variables Not Showing

- Wait for stage to complete
- Expand nested objects manually
- Check WebSocket connection

### Prompt Editor Empty

- Only available for @node components
- Stage must use LLM (context.llm)
- Wait for stage to pause (not complete)

### Debug Session Disconnects

- Check Studio server is running
- Check WebSocket connection
- Increase timeout in settings

## Best Practices

1. **Start Simple**: Debug one stage at a time
2. **Use Conditional Breakpoints**: Skip iterations in loops
3. **Watch Key Values**: Monitor important outputs
4. **Save Prompt Versions**: Keep successful prompt iterations
5. **Check Error Details**: Expand exception info in Variables

## See Also

- [VSCode Extension](../07-vscode-extension/overview.md)
- [Testing](./testing/pipeline-testing.md)
- [Control Flow](../03-concepts/control-flow.md)
