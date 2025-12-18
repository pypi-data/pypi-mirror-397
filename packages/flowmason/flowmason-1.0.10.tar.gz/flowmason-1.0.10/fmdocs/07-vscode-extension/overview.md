# VSCode Extension Overview

**Version 0.10.0** | **All Features Complete**

The FlowMason VSCode extension provides a native IDE experience for building, debugging, and testing AI pipelines.

## Installation

```bash
# From VSIX file
code --install-extension flowmason-0.10.0.vsix

# Or from source
cd vscode-extension
npm install && npm run compile && npm run package
code --install-extension flowmason-0.10.0.vsix
```

## Features Overview

### Language Support

| Feature | Description |
|---------|-------------|
| **IntelliSense** | Autocomplete for decorators, components, configs |
| **Diagnostics** | Real-time validation and error highlighting |
| **Hover** | Documentation on hover for components |
| **CodeLens** | Run/Preview buttons above decorators |
| **Go to Definition** | Jump to component definitions (F12) |
| **Find References** | Find all usages of components |
| **Document Symbols** | Outline view for pipeline structure |

### Pipeline Editing

| Feature | Description |
|---------|-------------|
| **DAG Canvas** | Visual editor for pipeline stages |
| **Stage Tree** | Tree view of pipeline stages |
| **Config Panel** | Edit stage configuration in sidebar |
| **React Config Editor** | Rich React-based stage configuration |
| **Validation** | Real-time pipeline validation |

### Debugging (DAP)

| Feature | Description |
|---------|-------------|
| **Breakpoints** | Set breakpoints on stages (F9) |
| **Conditional Breakpoints** | Break on expression conditions |
| **Hit Count Breakpoints** | Break after N hits |
| **Watch Expressions** | Evaluate expressions during debug |
| **Step Through** | Step over stages (F10), step into (F11) |
| **Variables** | Inspect inputs/outputs in panel |
| **Call Stack** | Pipeline → stage hierarchy |
| **Exception Breakpoints** | Break on errors |
| **Prompt Editor** | Edit prompts during debug |
| **Token Streaming** | See LLM tokens in real-time |

### Time Travel Debugging

| Feature | Description |
|---------|-------------|
| **Execution Snapshots** | Capture state at each stage |
| **Timeline Navigation** | Step back and forward through history |
| **State Comparison** | Diff view between snapshots |
| **Replay** | Re-execute from any snapshot |
| **What-If Analysis** | Run with modified inputs |

### Marketplace

| Feature | Description |
|---------|-------------|
| **Browse** | Featured, trending, and new pipelines |
| **Search** | Search and filter by category |
| **Install** | Install pipelines directly to workspace |
| **Publishers** | View publisher profiles |
| **Favorites** | Save favorite pipelines |

### Testing

| Feature | Description |
|---------|-------------|
| **Test Explorer** | VSCode Test Explorer integration |
| **Test Discovery** | Auto-discover `.test.json` files |
| **Coverage** | Code coverage reporting |
| **Coverage Gutters** | Visual coverage in editor |

## Getting Started

### 1. Open a FlowMason Project

```bash
cd my-flowmason-project
code .
```

The extension activates automatically when it detects `flowmason.json`.

### 2. Start Studio

Use Command Palette (Cmd+Shift+P):
- "FlowMason: Start Studio" - Start the backend server
- "FlowMason: Stop Studio" - Stop the server
- "FlowMason: Restart Studio" - Restart the server

Or use the status bar button.

### 3. Create a Pipeline

1. Right-click in Explorer > "New FlowMason Pipeline"
2. Enter pipeline name
3. Opens in DAG Canvas editor

Or create manually:
```json
// pipelines/my-pipeline.pipeline.json
{
  "name": "my-pipeline",
  "version": "1.0.0",
  "stages": []
}
```

### 4. Add Stages

In the DAG Canvas:
1. Click "Add Stage" or use Cmd+Shift+A
2. Select component from QuickPick
3. Configure in the sidebar panel

### 5. Run Pipeline

- Press `F5` to run with debugging
- Press `Ctrl+F5` to run without debugging
- Click the "Run" CodeLens above the pipeline

### 6. Debug Pipeline

1. Set breakpoints (F9 on a stage)
2. Press F5 to start debugging
3. Use F10 to step through
4. Inspect variables in the Debug panel
5. Edit prompts in the Prompt Editor panel

## Views

### Activity Bar

The FlowMason activity bar icon reveals:

```
FLOWMASON
├── Components
│   ├── Nodes
│   │   ├── generator
│   │   ├── critic
│   │   └── ...
│   ├── Operators
│   │   ├── http-request
│   │   └── ...
│   └── Control Flow
│       ├── conditional
│       └── ...
├── Pipelines
│   ├── main.pipeline.json
│   └── etl.pipeline.json
├── Runs
│   ├── run-abc123 (completed)
│   └── run-def456 (running)
├── Tests
│   └── main.test.json
├── Marketplace
│   ├── Featured
│   ├── Trending
│   ├── New
│   ├── Categories
│   │   ├── AI/ML
│   │   ├── Data Processing
│   │   └── ...
│   └── Your Library
└── Time Travel
    └── (During debug session)
        ├── Stage: fetch (snapshot)
        ├── Stage: process (snapshot)
        └── Stage: generate (current)
```

### Pipeline Stages View

When a `.pipeline.json` file is open:

```
PIPELINE STAGES
├── fetch (http-request)
├── process (json-transform)
├── generate (generator)
└── output (logger)
```

Click a stage to:
- Select it in the DAG Canvas
- Open configuration in sidebar

### Stage Config View

Sidebar panel showing:
- Stage ID and component type
- Input configuration fields
- Dependencies
- Apply/Reset buttons

## Commands

### Studio Management
| Command | Keybinding | Description |
|---------|------------|-------------|
| FlowMason: Start Studio | - | Start backend server |
| FlowMason: Stop Studio | - | Stop backend server |
| FlowMason: Restart Studio | - | Restart backend server |
| FlowMason: Open Studio | - | Open Studio in browser |

### Pipeline Execution
| Command | Keybinding | Description |
|---------|------------|-------------|
| FlowMason: Run Pipeline | F5 | Run current pipeline |
| FlowMason: Debug Pipeline | Ctrl+F5 | Debug with breakpoints |
| FlowMason: Toggle Breakpoint | F9 | Add/remove stage breakpoint |
| FlowMason: Step Over | F10 | Step to next stage |
| FlowMason: Step Into | F11 | Step into sub-pipeline |
| FlowMason: Continue | F5 | Continue to next breakpoint |
| FlowMason: Stop | Shift+F5 | Stop execution |

### Pipeline Editing
| Command | Keybinding | Description |
|---------|------------|-------------|
| FlowMason: Add Stage | Cmd+Shift+A | Add stage to pipeline |
| FlowMason: Open DAG View | - | Open visual editor |
| FlowMason: Preview Component | - | Preview component output |
| FlowMason: New Node | - | Scaffold new node |
| FlowMason: New Operator | - | Scaffold new operator |
| FlowMason: New Pipeline | - | Create new pipeline |

### Testing
| Command | Keybinding | Description |
|---------|------------|-------------|
| FlowMason: Run Tests | Cmd+; A | Run all tests |
| FlowMason: Run Test File | - | Run tests in current file |

### Marketplace
| Command | Description |
|---------|-------------|
| FlowMason: Search Marketplace | Search for pipelines and components |
| FlowMason: Install from Marketplace | Install selected listing |
| FlowMason: View Listing | View listing details |
| FlowMason: View Publisher | View publisher profile |
| FlowMason: Add to Favorites | Save to favorites |
| FlowMason: Remove from Favorites | Remove from favorites |
| FlowMason: Refresh Marketplace | Refresh marketplace listings |

### Time Travel Debugging
| Command | Description |
|---------|-------------|
| FlowMason: Step Back | Go to previous snapshot |
| FlowMason: Step Forward | Go to next snapshot |
| FlowMason: View Snapshot | View snapshot details |
| FlowMason: Compare Snapshots | Diff two snapshots |
| FlowMason: Replay from Snapshot | Re-execute from snapshot |
| FlowMason: What-If Analysis | Run with modified inputs |
| FlowMason: Refresh Timeline | Refresh time travel timeline |

## Settings

Configure in VSCode Settings (Cmd+,):

```json
{
  "flowmason.studioHost": "localhost",
  "flowmason.studioPort": 8999,
  "flowmason.autoStartStudio": true,
  "flowmason.showCodeLens": true,
  "flowmason.diagnostics.enabled": true,
  "flowmason.debugger.showTokenStream": true
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `studioHost` | `localhost` | Studio server host |
| `studioPort` | `8999` | Studio server port |
| `autoStartStudio` | `true` | Auto-start Studio on activation |
| `showCodeLens` | `true` | Show Run/Preview buttons |
| `diagnostics.enabled` | `true` | Enable validation diagnostics |
| `debugger.showTokenStream` | `true` | Show tokens during debug |

## Debug Configuration

Create `.vscode/launch.json`:

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
        "name": "test"
      },
      "stopOnEntry": false,
      "breakOnException": true
    }
  ]
}
```

| Property | Description |
|----------|-------------|
| `pipeline` | Pipeline file path |
| `input` | Input data for pipeline |
| `inputFile` | JSON file with input data |
| `stopOnEntry` | Break on first stage |
| `breakOnException` | Break on errors |

## Test Explorer

### Test File Format

Create `.test.json` files:

```json
{
  "name": "Pipeline Tests",
  "pipeline": "pipelines/main.pipeline.json",
  "tests": [
    {
      "name": "happy path",
      "input": { "url": "https://example.com" },
      "assertions": [
        { "path": "output.status", "equals": "success" }
      ]
    }
  ]
}
```

### Running Tests

- Click "Run" button in Test Explorer
- Use Cmd+; A to run all tests
- Right-click test > "Run Test"

### Coverage

Coverage reports appear in:
- Test Explorer (per-file coverage)
- Editor gutters (line coverage)
- Coverage panel (summary)

## Prompt Editor

During debugging, the Prompt Editor panel shows:

1. **Current Prompt**: System and user prompts being sent
2. **Edit Mode**: Modify prompts live
3. **Re-run**: Execute stage with modified prompt
4. **Compare**: Side-by-side output comparison
5. **History**: Previous prompt versions
6. **Streaming**: Watch tokens arrive in real-time

### Workflow

1. Set breakpoint on LLM stage
2. Start debugging (F5)
3. When paused, open Prompt Editor
4. Edit the prompt
5. Click "Re-run Stage"
6. Compare outputs
7. Save successful prompt as new version

## Status Bar

The status bar shows:
- Studio connection status (green/red dot)
- Current pipeline name
- Run status (Ready/Running/Paused)
- Click to access quick actions

## Troubleshooting

### Studio Won't Start

```bash
# Check if port is in use
lsof -i :8999

# Start manually
fm studio start --port 8999
```

### Extension Not Activating

- Ensure `flowmason.json` exists in workspace
- Check Output panel > "FlowMason" for errors
- Reload window (Cmd+Shift+P > "Reload Window")

### Debug Session Fails

- Ensure Studio is running
- Check pipeline is valid (`fm validate`)
- Check API keys are set

## See Also

- [Debugging Guide](../09-debugging-testing/debugging/current-debugging.md)
- [Testing Guide](../09-debugging-testing/testing/pipeline-testing.md)
- [Getting Started](../02-getting-started/quickstart.md)
