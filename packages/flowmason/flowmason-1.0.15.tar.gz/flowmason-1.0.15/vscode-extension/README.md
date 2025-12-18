# FlowMason VSCode Extension

The official VSCode extension for FlowMason - Universal AI Workflow Infrastructure.

Build, debug, and deploy AI pipelines directly in VSCode with a Salesforce DX-style workflow.

## What's New in v0.9.3

- **Fixed Lab Component Registration** - Critical bug fix
  - Studio now properly auto-discovers built-in lab components
  - Fixed issue where old cached packages would override updated components
  - `json_transform` now correctly parses JSON strings with `parse_json_strings=True`

## What's New in v0.9.2

- **Fixed Pipeline Execution from VSCode** - Critical bug fix
  - Pipelines with template variables (e.g., `{{upstream.stage.field}}`) now work correctly
  - Fixed field mapping in Studio API that was causing template resolution errors
  - CLI and VSCode/Studio now use consistent execution paths

## What's New in v0.9.1

- **Fixed Studio Startup** - Now uses `fm studio start` CLI command
  - Works correctly with pip-installed FlowMason
  - No longer requires source code or npm
  - Studio management is simpler and more reliable

## What's New in v0.9.0

- **Control Flow Components Now Fully Working**
  - **ForEach Loops** - Iterate over collections with `{{context.item_variable}}` and `{{context.index_variable}}`
  - **TryCatch Error Handling** - Try/catch blocks with proper nested result propagation
  - **Conditional Branching** - Route execution based on conditions
  - **Router (Switch/Case)** - Multi-branch routing based on values
  - All control flow components properly integrate with the DAG executor

- **Loop Variable Injection** - Access current item and index in foreach loops:
  ```json
  {
    "id": "transform-item",
    "config": {
      "data": {
        "item": "{{context.current_item}}",
        "index": "{{context.item_index}}"
      }
    },
    "depends_on": ["foreach-stage"]
  }
  ```

- **Nested Result Propagation** - Access results from try/catch nested stages:
  ```json
  {
    "id": "process-result",
    "config": {
      "data": {
        "api_result": "{{upstream.fetch-api}}",
        "status": "{{upstream.trycatch-stage.status}}"
      }
    },
    "depends_on": ["trycatch-stage"]
  }
  ```

## What's New in v0.8.0

- **Visual-First Configuration Editor** (Salesforce Flow-style)
  - **No more typing `{{...}}` syntax** - everything through dropdowns
  - **Source Picker**: Dropdown to select data sources (Pipeline Input, upstream stages)
  - **Visual Field Mapper**: Table UI to map input fields to output fields for json_transform
  - **Prompt Editor**: Click variable pills to insert references into prompts
  - **Generated JSON View**: Read-only, collapsible section showing the actual config
  - Configuration is 100% visual - JSON is just output for CI/CD

## What's New in v0.7.1

- **Smart Data Source Awareness** - Configuration editor now understands data flow
  - Shows available Pipeline Input fields from `input_schema`
  - Shows upstream stages with their output fields
  - Click field chips to insert correct variable syntax automatically
  - Visual field picker for `{{input.field}}` and `{{stage.result.field}}` references

## What's New in v0.7.0

- **Enhanced Configuration Editor** - Beautiful full-panel editor for stage configuration
  - Opens on the right side with more space
  - Shows all available fields for each component with descriptions
  - Dropdowns for enum fields, checkboxes for booleans
  - Number inputs with min/max/step validation
  - JSON editors for complex objects
  - Built-in schemas for all core components (generator, json_transform, http_request, etc.)
  - Tips section showing variable syntax
  - Category badges and icons for visual clarity
- **Fix** - Circular dependency prevention - cannot create cycles in DAG
- **Fix** - Stage Config panel context now properly set

## What's New in v0.6.11

- **Fix** - Stage Config panel now shows when DAG canvas is open
- **Fix** - Circular dependency prevention - cannot create connections that would form cycles
- **Improved** - Warning message when attempting to create invalid circular connection

## What's New in v0.6.10

- **Fix** - "Edit Configuration" now works from DAG canvas right-click menu (opens Stage Config panel)
- **Fix** - Keyboard shortcuts (A, F, Delete, etc.) now work in DAG canvas
- **Improved** - Stage Config panel automatically focuses when editing configuration

## What's New in v0.6.9

- **Fix** - Fixed node dragging not working (positions now update correctly during drag)
- **Fix** - Fixed connection ports not responding to clicks
- **Improved** - Input ports now visible when connecting for easier drop targets

## What's New in v0.6.8

- **Enhanced DAG Canvas** - React Flow-style pipeline editor
  - Right-click context menus on nodes, edges, and canvas
  - Drag nodes to reposition (positions saved to pipeline)
  - Visual connection ports (drag from output to input)
  - Multi-select with Shift+Click or drag selection box
  - Keyboard shortcuts: Delete, Ctrl+D (duplicate), A (add), F (fit), Ctrl+A (select all)
  - Mouse wheel zoom (zoom towards cursor)
  - Minimap overview
  - Double-click node to edit config

## What's New in v0.6.7

- **Development Webhook Server** - Built-in webhook server for testing output_config
  - Start with: `FlowMason: Start Webhook Server` (port 9999)
  - View received payloads in Output panel (FlowMason Webhook)
  - Configurable port via `flowmason.webhookPort` setting
- **Fix** - Add Stage command now works in DAG canvas view

## What's New in v0.6.3

- **Fix** - Fixed pipeline template to use correct `jmespath_expression` field
- **Fix** - Fixed upstream reference format (`upstream.stage.result.field`)
- **Fix** - Added `auto_discover()` method to ComponentRegistry for CLI support

## What's New in v0.6.2

- **Fix** - Fixed template type coercion error in generated pipeline (max_tokens)

## What's New in v0.6.1

- **Improved New Project Template** - Creates Input → Generate → Output pipeline demonstrating full workflow
- **Output Routing Example** - New projects include `output_config` with webhook destination template
- **Updated Dependencies** - Requires FlowMason 0.5.0+

## What's New in v0.6.0

- **Input/Output Architecture** - New `output_config` support in pipelines for automatic result routing
- **Output Destinations** - Configure webhook, email, database, and message queue destinations
- **Schema Updates** - Pipeline schema now supports output routing configuration
- **Named Pipeline Invocation** - Run pipelines by name via the API (`POST /run`)

## What's New in v0.5.0

- **New Project Command** - Create complete FlowMason projects with `flowmason.json`, example components, and pipelines
- **Updated Project Format** - Uses modern `flowmason.json` manifest and `.pipeline.json` pipeline files
- **Studio Management** - Start, stop, and restart FlowMason Studio directly from VSCode
- **Enhanced Debugging** - Full debugging support with breakpoints (F9), step-through (F10), and run (F5)
- **Improved Code Generation** - Generated components use current API (`async def execute`)

## Quick Start

1. **Install FlowMason CLI**: `pip install flowmason`
2. **Create a Project**: `Cmd+Shift+P` → "FlowMason: New Project"
3. **Start Studio**: `Cmd+Shift+P` → "FlowMason: Start Studio"
4. **Run Pipeline**: Press `F5` with a `.pipeline.json` file open

## Features

### Project Management

Create and manage FlowMason projects with proper structure:

- **New Project** (`FlowMason: New Project`) - Interactive wizard creates:
  - `flowmason.json` - Project manifest
  - `components/` - Example node and operator
  - `pipelines/` - Example pipeline
  - Proper `.gitignore` and `README.md`

### Component Development

Create nodes and operators with interactive wizards:

- **New Node** (`FlowMason: New Node`) - AI-powered components with LLM calls
- **New Operator** (`FlowMason: New Operator`) - Deterministic data transformations

### Studio Integration

Control FlowMason Studio backend directly from VSCode:

- **Start Studio** - Launch the backend server (port 8999)
- **Stop Studio** - Gracefully stop the server
- **Restart Studio** - Restart with fresh state
- **Status Bar** - Shows connection status (Connected/Disconnected)

### Development Webhook Server

Built-in webhook server for testing pipeline output routing:

- **Start Webhook Server** - Launch local webhook receiver (default port 9999)
- **Stop Webhook Server** - Stop the webhook server
- **Copy Webhook URL** - Copy `http://localhost:9999/webhook` to clipboard
- **Output Panel** - View received webhook payloads in real-time

Configure your pipeline's `output_config` to use `http://localhost:9999/webhook` during development. All received payloads are displayed in the "FlowMason Webhook" output panel with full request details.

### Debugging

Full debugging support for pipelines:

| Shortcut | Action |
|----------|--------|
| `F5` | Run/Debug pipeline |
| `F9` | Toggle breakpoint on stage |
| `F10` | Step over (next stage) |
| `F11` | Step into (sub-pipeline) |
| `Shift+F5` | Stop execution |

### IntelliSense & Auto-completion

Intelligent code completion for:
- `@node`, `@operator`, and `@control_flow` decorators
- Decorator parameters (name, description, category, etc.)
- Input/Output field definitions
- FlowMason imports

### Diagnostics & Linting

Real-time validation for:
- Missing decorator parameters
- Non-kebab-case naming
- Missing Input/Output classes
- Hardcoded secrets detection
- Execute method signatures

### Code Snippets

| Prefix | Description |
|--------|-------------|
| `fmnode` | Full node component |
| `fmoperator` | Full operator component |
| `fminput` | Input class |
| `fmoutput` | Output class |
| `fmfield` | Field definition |
| `fmgenerate` | LLM generate call |
| `fmupstream` | Upstream access |

### Sidebar Views

The FlowMason activity bar provides:

1. **Components** - Browse registered components by category
2. **Pipelines** - View and manage pipelines
3. **Runs** - Execution history

### CodeLens

Clickable actions above components:
- **Run** - Execute the component
- **Preview** - View component schema
- **Open in Studio** - View in browser

## Commands

| Command | Description |
|---------|-------------|
| `FlowMason: New Project` | Create a new FlowMason project |
| `FlowMason: New Node` | Create a new node component |
| `FlowMason: New Operator` | Create a new operator component |
| `FlowMason: Start Studio` | Start the FlowMason backend |
| `FlowMason: Stop Studio` | Stop the FlowMason backend |
| `FlowMason: Restart Studio` | Restart the backend |
| `FlowMason: Open Studio` | Open Studio in browser |
| `FlowMason: Preview Component` | Preview component schema |
| `FlowMason: Refresh Registry` | Refresh component list |
| `FlowMason: Open DAG View` | Visual pipeline editor |
| `FlowMason: Start Webhook Server` | Start dev webhook receiver |
| `FlowMason: Stop Webhook Server` | Stop dev webhook receiver |
| `FlowMason: Copy Webhook URL` | Copy webhook URL to clipboard |

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `flowmason.studioUrl` | `http://localhost:8999` | Studio backend URL |
| `flowmason.pythonPath` | `python` | Python executable |
| `flowmason.showDiagnostics` | `true` | Show diagnostics |
| `flowmason.defaultProvider` | `anthropic` | Default LLM provider |
| `flowmason.defaultModel` | `claude-sonnet-4-20250514` | Default model |
| `flowmason.webhookPort` | `9999` | Dev webhook server port |

## Requirements

- **VSCode** 1.85.0 or higher
- **Python** 3.11 or higher
- **FlowMason CLI** (`pip install flowmason`)

## Installation

### From VSIX

```bash
code --install-extension flowmason-0.9.3.vsix
```

### From Source

```bash
cd vscode-extension
npm install
npm run compile
# Press F5 to launch extension development host
```

## Project Structure

A FlowMason project created by this extension:

```
my-project/
├── flowmason.json           # Project manifest
├── components/
│   ├── __init__.py
│   ├── example_node.py      # AI node example
│   └── example_operator.py  # Operator example
├── pipelines/
│   └── main.pipeline.json   # Pipeline definition
├── requirements.txt
├── .gitignore
└── README.md
```

## Links

- **Documentation**: https://flowmason.com/docs
- **PyPI**: https://pypi.org/project/flowmason/
- **Support**: support@flowmason.com

## License

Proprietary - FlowMason
