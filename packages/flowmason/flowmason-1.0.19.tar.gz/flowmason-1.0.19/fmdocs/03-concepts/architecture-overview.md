# FlowMason Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        VSCode Extension                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Custom    │  │   Debug     │  │      Test Explorer      │ │
│  │   Editor    │  │   Adapter   │  │      Integration        │ │
│  │  Provider   │  │  (DAP)      │  │       (Future)          │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
│         │                │                      │               │
│         └────────────────┼──────────────────────┘               │
│                          │                                      │
│                    ┌─────▼─────┐                                │
│                    │ Extension │                                │
│                    │   Host    │                                │
│                    └─────┬─────┘                                │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTP/WebSocket
                    ┌──────▼──────┐
                    │  FlowMason  │
                    │   Studio    │
                    │  Backend    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐
        │Component │ │Execution │ │  LLM     │
        │ Registry │ │  Engine  │ │Providers │
        └──────────┘ └──────────┘ └──────────┘
```

## Layer Breakdown

### 1. VSCode Extension Layer

**Location:** `vscode-extension/`

The VSCode extension provides:
- IntelliSense and code completion for `@node`, `@operator`, `@control_flow`
- Diagnostics and linting
- CodeLens (Run/Preview buttons)
- Go to Definition for component references
- Studio lifecycle management (start/stop/restart)
- Component preview webview

**Future:**
- Custom Editor Provider for `.pipeline.json`
- Debug Adapter Protocol integration
- Test Explorer integration

### 2. Studio Layer

**Location:** `studio/flowmason_studio/`

The Studio provides both backend API and frontend UI:

**Backend (FastAPI):**
- REST API for pipelines, components, runs
- WebSocket for real-time execution updates
- ExecutionController for debug commands
- SQLite storage for pipelines and runs

**Frontend (React):**
- Pipeline Builder canvas
- Component palette
- Debug panel with breakpoints
- Stage configuration
- Execution timeline

### 3. Core Framework Layer

**Location:** `core/flowmason_core/`

The core framework provides:
- Decorators: `@node`, `@operator`, `@control_flow`
- Type system: `NodeInput`, `NodeOutput`, `ControlFlowDirective`
- Execution engine: `UniversalExecutor`, `DAGExecutor`
- Registry: Component discovery and loading
- Error handling: `ErrorType`, `FlowMasonError`

### 4. Components Layer

**Location:** `lab/flowmason_lab/`

Built-in components:
- **Control Flow:** Conditional, ForEach, TryCatch, Router, SubPipeline, Return
- **Operators:** HttpRequest, JsonTransform, Filter, SchemaValidate, VariableSet, Logger
- **Nodes:** Generator, Critic, Improver, Selector, Synthesizer

## Data Flow

### Pipeline Execution

```
User Input
    │
    ▼
┌───────────────┐
│ Pipeline      │  Parse pipeline definition
│ Definition    │  Resolve stage dependencies
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ DAGExecutor   │  Topological sort stages
│               │  Execute in dependency order
└───────┬───────┘
        │
        ▼ (for each stage)
┌───────────────┐
│ Universal     │  Resolve input mappings
│ Executor      │  Validate inputs
│               │  Execute component
│               │  Validate outputs
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Component     │  Node: LLM call
│               │  Operator: Transform
│               │  Control Flow: Directive
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Results       │  Stage outputs
│               │  Usage metrics
│               │  Trace spans
└───────────────┘
```

### WebSocket Events

```
Client                    Server
   │                         │
   │──── subscribe ─────────►│
   │                         │
   │◄─── SUBSCRIBED ─────────│
   │                         │
   │                         │ (pipeline starts)
   │◄─── RUN_STARTED ────────│
   │                         │
   │◄─── STAGE_STARTED ──────│  (for each stage)
   │◄─── STAGE_COMPLETED ────│
   │                         │
   │◄─── RUN_COMPLETED ──────│
   │                         │
   │──── unsubscribe ───────►│
```

## Key Files

### Core Framework

| File | Purpose |
|------|---------|
| `core/flowmason_core/core/decorators.py` | @node, @operator, @control_flow |
| `core/flowmason_core/core/types.py` | NodeInput, NodeOutput, ControlFlowDirective |
| `core/flowmason_core/execution/universal_executor.py` | Component execution |
| `core/flowmason_core/execution/dag_executor.py` | Pipeline execution |
| `core/flowmason_core/execution/types.py` | ErrorType, FlowMasonError, UsageMetrics |
| `core/flowmason_core/registry/extractor.py` | Metadata extraction |

### Studio

| File | Purpose |
|------|---------|
| `studio/flowmason_studio/api/app.py` | FastAPI application |
| `studio/flowmason_studio/api/routes/` | API endpoints |
| `studio/flowmason_studio/api/websocket.py` | WebSocket handler |
| `studio/flowmason_studio/services/execution_controller.py` | Debug control |
| `studio/frontend/src/pages/PipelineBuilder.tsx` | Pipeline canvas |
| `studio/frontend/src/components/debug/` | Debug UI |

### VSCode Extension

| File | Purpose |
|------|---------|
| `vscode-extension/src/extension.ts` | Extension entry point |
| `vscode-extension/src/commands/` | Command implementations |
| `vscode-extension/src/providers/` | Language providers |
| `vscode-extension/src/services/flowmasonService.ts` | API client |
