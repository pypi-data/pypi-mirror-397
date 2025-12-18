# Tutorial 3: Debugging Pipelines

This tutorial teaches you how to debug FlowMason pipelines using VSCode's native debugging features.

## What You'll Learn

- Setting breakpoints on stages
- Stepping through execution
- Inspecting variables and outputs
- Editing prompts during debug
- Using the debug console

## Prerequisites

- Completed [Tutorial 2: Building Your First Pipeline](./02-building-first-pipeline.md)
- A working pipeline to debug
- Studio running

## Understanding Debug Adapter Protocol (DAP)

FlowMason implements VSCode's Debug Adapter Protocol, giving you:

- **Breakpoints** - Pause at specific stages
- **Step controls** - Step over, step into, continue
- **Variable inspection** - See inputs, outputs, context
- **Call stack** - Navigate pipeline hierarchy
- **Debug console** - Evaluate expressions

## Step 1: Create a Debug Configuration

Create `.vscode/launch.json` in your project:

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
      "name": "Debug Content Summarizer",
      "pipeline": "pipelines/content-summarizer.pipeline.json",
      "input": {
        "url": "https://example.com/article",
        "max_length": 150
      },
      "stopOnEntry": false,
      "breakOnException": true
    }
  ]
}
```

### Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `pipeline` | string | Path to pipeline file |
| `input` | object | Input data for the pipeline |
| `inputFile` | string | Path to JSON file with input |
| `stopOnEntry` | boolean | Break on first stage |
| `breakOnException` | boolean | Break on any error |
| `breakpoints` | string[] | Pre-set breakpoint stage IDs |

## Step 2: Set Breakpoints

### Method 1: Click the Gutter

1. Open your pipeline file
2. Find a stage definition
3. Click in the gutter (left margin) next to the stage ID
4. A red dot appears indicating the breakpoint

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

### Method 2: Keyboard Shortcut

1. Place cursor on a stage
2. Press `F9` to toggle breakpoint

### Method 3: DAG Canvas

1. Open the DAG view
2. Right-click a stage node
3. Select "Toggle Breakpoint"

### Method 4: Via Debug Configuration

```json
{
  "type": "flowmason",
  "name": "Debug with Breakpoints",
  "pipeline": "pipelines/main.pipeline.json",
  "breakpoints": ["extract", "summarize"]
}
```

## Step 3: Start Debugging

### Option A: Press F5

1. Open the pipeline file
2. Press `F5`
3. Select the debug configuration if prompted

### Option B: Debug Panel

1. Click the Run and Debug icon in the Activity Bar
2. Select your configuration from the dropdown
3. Click the green play button

### Option C: CodeLens

1. Open the pipeline file
2. Click "Debug" CodeLens above the pipeline name

## Step 4: Debug Controls

When paused at a breakpoint:

| Control | Keybinding | Description |
|---------|------------|-------------|
| Continue | `F5` | Run to next breakpoint |
| Step Over | `F10` | Execute next stage |
| Step Into | `F11` | Enter sub-pipeline |
| Step Out | `Shift+F11` | Exit sub-pipeline |
| Restart | `Ctrl+Shift+F5` | Restart from beginning |
| Stop | `Shift+F5` | Stop execution |

### Debug Toolbar

```
[▶ Continue] [⏭ Step Over] [⬇ Step Into] [⬆ Step Out] [🔄 Restart] [⏹ Stop]
```

## Step 5: Inspect Variables

When paused, the Variables panel shows:

```
VARIABLES
├── Input
│   ├── url: "https://example.com/article"
│   └── max_length: 150
├── Output (after stage executes)
│   ├── body: {...}
│   └── status_code: 200
├── Context
│   ├── run_id: "run-abc123"
│   ├── stage_id: "fetch"
│   └── pipeline_name: "content-summarizer"
└── Previous Stages
    └── (outputs from completed stages)
```

### Expanding Objects

- Click the arrow to expand nested objects
- Double-click a value to copy it
- Right-click for additional options

## Step 6: Use Watch Expressions

Add expressions to monitor throughout execution:

1. In the Watch panel, click "+"
2. Enter an expression:
   - `{{fetch.output.status_code}}`
   - `{{input.url}}`
   - `{{extract.output.result.length}}`

Watch expressions update as you step through the pipeline.

## Step 7: Debug Console

Evaluate expressions in the Debug Console:

```
> {{fetch.output.body}}
{ "content": "Article text...", "meta": {...} }

> {{input.url.startsWith("https")}}
true

> {{context.run_id}}
"run-abc123"
```

### Useful Expressions

```javascript
// Check stage output
{{fetch.output}}

// Access nested properties
{{fetch.output.body.data[0].name}}

// String operations
{{input.url.replace("http:", "https:")}}

// Conditional checks
{{fetch.output.status_code == 200 ? "OK" : "FAILED"}}
```

## Step 8: Prompt Editor (AI Stages)

When paused at an AI node (generator, critic, etc.), the Prompt Editor activates:

### Viewing Prompts

```
┌─────────────────────────────────────────┐
│ PROMPT EDITOR                           │
├─────────────────────────────────────────┤
│ Stage: summarize                        │
│ Component: generator                    │
├─────────────────────────────────────────┤
│ System Prompt:                          │
│ ┌─────────────────────────────────────┐ │
│ │ You are a concise summarizer...     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ User Prompt:                            │
│ ┌─────────────────────────────────────┐ │
│ │ Summarize the following content...  │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Edit] [Re-run] [Compare]               │
└─────────────────────────────────────────┘
```

### Editing Prompts Live

1. Click "Edit" to enable editing
2. Modify the prompt text
3. Click "Re-run Stage" to execute with new prompt
4. Compare outputs side-by-side

### Prompt Iteration Workflow

1. Set breakpoint on AI stage
2. Start debugging
3. When paused, view the prompt
4. Edit and re-run until satisfied
5. Update the pipeline file with the final prompt
6. Continue execution

### Token Streaming

Watch LLM responses arrive in real-time:

```
Output (streaming):
The article discusses several key points█
```

Enable in settings: `flowmason.debugger.showTokenStream`

## Step 9: Conditional Breakpoints

Breakpoints that only trigger under certain conditions:

1. Right-click an existing breakpoint
2. Select "Edit Breakpoint..."
3. Enter a condition:

```
{{fetch.output.status_code}} != 200
```

The breakpoint only triggers when the condition is true.

### Example Conditions

```javascript
// Break on error status
{{fetch.output.status_code}} >= 400

// Break on empty result
{{extract.output.result.length}} == 0

// Break on specific input
{{input.url.includes("important")}}

// Break on iteration count (in loops)
{{_loop.index}} > 5
```

## Step 10: Exception Breakpoints

Break automatically when errors occur:

1. Open the Breakpoints panel
2. Check "Break on Exceptions"
3. Choose:
   - "All Exceptions" - Any error
   - "Uncaught Exceptions" - Unhandled errors only

### Error Types

When paused on an exception, you can see:

```
VARIABLES
└── _error
    ├── type: "CONNECTIVITY"
    ├── message: "Connection refused"
    ├── stage: "fetch"
    └── details: {...}
```

## Debugging Control Flow

### Conditional Branches

When debugging a `conditional` stage:
1. Variables show the condition value
2. Step Over shows which branch was taken
3. Skipped branches appear grayed in the DAG

### Loops (ForEach)

When debugging a `foreach` stage:
1. Variables show current item and index
2. Step through each iteration
3. Watch expressions track progress

```
VARIABLES
├── _loop
│   ├── index: 2
│   ├── total: 10
│   └── item: {...}
```

### Try/Catch

When debugging a `trycatch` stage:
1. Try stages execute normally
2. On error, catch stages execute
3. Exception breakpoints can pause on the error

## Real-World Debugging Scenarios

### Scenario 1: API Returns Unexpected Data

1. Set breakpoint on the stage using the API response
2. Inspect `{{previous_stage.output}}`
3. Check the actual data structure
4. Update your transform expression

### Scenario 2: AI Output Not As Expected

1. Set breakpoint on AI stage
2. Open Prompt Editor
3. View the actual prompt being sent
4. Edit and iterate until output improves
5. Update pipeline with final prompt

### Scenario 3: Loop Running Too Long

1. Set conditional breakpoint: `{{_loop.index}} > 100`
2. Debug to understand why loop hasn't terminated
3. Check loop exit conditions

### Scenario 4: Intermittent Failures

1. Enable "Break on Exceptions"
2. Run the pipeline multiple times
3. When it breaks, inspect the error context
4. Identify the root cause

## Debug Keyboard Shortcuts Reference

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Start Debugging | `F5` | `F5` |
| Toggle Breakpoint | `F9` | `F9` |
| Step Over | `F10` | `F10` |
| Step Into | `F11` | `F11` |
| Step Out | `Shift+F11` | `Shift+F11` |
| Continue | `F5` | `F5` |
| Stop | `Shift+F5` | `Shift+F5` |
| Restart | `Cmd+Shift+F5` | `Ctrl+Shift+F5` |

## Troubleshooting

### Breakpoints Not Working

- Ensure Studio is running
- Check breakpoint is on a valid stage ID
- Verify pipeline path in launch config
- Look for validation errors in Problems panel

### Variables Not Showing

- Wait for stage to complete before inspecting output
- Expand nested objects manually
- Check WebSocket connection in FlowMason output

### Debug Session Disconnects

- Check Studio server is running
- Increase timeout in settings
- Check for network issues

## Next Steps

- [Tutorial 4: Testing Pipelines](./04-testing-pipelines.md) - Write automated tests
- [Tutorial 5: Working with Components](./05-working-with-components.md) - Create custom components
