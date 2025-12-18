# System Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                        │
├─────────────────────────────┬───────────────────────────────────────┤
│     VSCode Extension        │         Studio Frontend               │
│  ┌───────────────────────┐  │  ┌─────────────────────────────────┐  │
│  │ - IntelliSense        │  │  │ - Pipeline Builder (React)      │  │
│  │ - Diagnostics         │  │  │ - Component Palette             │  │
│  │ - CodeLens            │  │  │ - Debug Panel                   │  │
│  │ - Preview Webview     │  │  │ - Execution Timeline            │  │
│  │ - Studio Management   │  │  │ - Stage Configuration           │  │
│  └───────────────────────┘  │  └─────────────────────────────────┘  │
└─────────────────────────────┴───────────────────────────────────────┘
                                       │
                              HTTP/WebSocket
                                       │
┌──────────────────────────────────────▼──────────────────────────────┐
│                         API Layer (FastAPI)                         │
├─────────────────────────────────────────────────────────────────────┤
│  Routes:                                                            │
│  ├── /api/v1/registry     - Component management                    │
│  ├── /api/v1/pipelines    - Pipeline CRUD                           │
│  ├── /api/v1/runs         - Execution management                    │
│  ├── /api/v1/providers    - LLM provider config                     │
│  ├── /api/v1/settings     - App settings                            │
│  ├── /api/v1/logs         - Logging                                 │
│  └── /api/v1/ws/runs      - WebSocket for real-time updates         │
├─────────────────────────────────────────────────────────────────────┤
│  Services:                                                          │
│  ├── ExecutionController  - Debug commands (pause/resume/step)      │
│  ├── PipelineStorage      - Pipeline persistence                    │
│  └── RunStorage           - Execution history                       │
└─────────────────────────────────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────┐
│                        Core Framework Layer                         │
├─────────────────────────────────────────────────────────────────────┤
│  Execution:                                                         │
│  ├── DAGExecutor          - Pipeline execution (topological sort)   │
│  ├── UniversalExecutor    - Component execution                     │
│  ├── ControlFlowHandler   - Process directives                      │
│  ├── ExecutionHooks       - Callbacks for observability             │
│  └── ExecutionTracer      - Span tracking                           │
├─────────────────────────────────────────────────────────────────────┤
│  Types:                                                             │
│  ├── NodeInput/Output     - Node type bases                         │
│  ├── OperatorInput/Output - Operator type bases                     │
│  ├── ControlFlowDirective - Flow control instructions               │
│  ├── FlowMasonError       - Error hierarchy                         │
│  └── UsageMetrics         - Token/cost tracking                     │
├─────────────────────────────────────────────────────────────────────┤
│  Registry:                                                          │
│  ├── ComponentRegistry    - Component discovery                     │
│  ├── MetadataExtractor    - Schema extraction                       │
│  └── PackageLoader        - .fmpkg loading                          │
└─────────────────────────────────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────┐
│                         Component Layer                             │
├─────────────────────────────────────────────────────────────────────┤
│  Control Flow (6):        Operators (7):         Nodes (5):         │
│  ├── Conditional          ├── HttpRequest        ├── Generator      │
│  ├── ForEach              ├── JsonTransform      ├── Critic         │
│  ├── TryCatch             ├── Filter             ├── Improver       │
│  ├── Router               ├── SchemaValidate     ├── Selector       │
│  ├── SubPipeline          ├── VariableSet        └── Synthesizer    │
│  └── Return               └── Logger                                │
└─────────────────────────────────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────┐
│                       External Services                             │
├─────────────────────────────────────────────────────────────────────┤
│  LLM Providers:           Storage:              External APIs:      │
│  ├── Anthropic            ├── SQLite            ├── HTTP endpoints  │
│  ├── OpenAI               └── File system       └── Webhooks        │
│  ├── Google                                                         │
│  └── Groq                                                           │
└─────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
flowmason/
├── core/                           # Core framework
│   └── flowmason_core/
│       ├── core/                   # Decorators, types
│       │   ├── decorators.py       # @node, @operator, @control_flow
│       │   └── types.py            # NodeInput, NodeOutput, etc.
│       ├── execution/              # Execution engine
│       │   ├── universal_executor.py
│       │   ├── dag_executor.py
│       │   ├── control_flow_handler.py
│       │   ├── types.py            # FlowMasonError, UsageMetrics
│       │   ├── retry.py            # Retry logic (not integrated)
│       │   └── cancellation.py     # Cancellation (not integrated)
│       └── registry/               # Component discovery
│           ├── extractor.py
│           └── types.py
│
├── studio/                         # Studio application
│   └── flowmason_studio/
│       ├── api/                    # FastAPI backend
│       │   ├── app.py
│       │   ├── routes/
│       │   │   ├── registry.py
│       │   │   ├── pipelines.py
│       │   │   └── execution.py
│       │   └── websocket.py
│       ├── services/
│       │   └── execution_controller.py
│       └── models/
│           └── api.py
│   └── frontend/                   # React frontend
│       └── src/
│           ├── pages/
│           │   └── PipelineBuilder.tsx
│           ├── components/
│           │   ├── PipelineCanvas.tsx
│           │   └── debug/
│           └── services/
│               ├── api.ts
│               └── websocket.ts
│
├── lab/                            # Built-in components
│   └── flowmason_lab/
│       ├── nodes/
│       │   └── core/               # Generator, Critic, etc.
│       └── operators/
│           ├── core/               # HttpRequest, JsonTransform, etc.
│           └── control_flow/       # Conditional, ForEach, etc.
│
├── vscode-extension/               # VSCode extension
│   └── src/
│       ├── extension.ts
│       ├── commands/
│       ├── providers/
│       └── services/
│
└── fmdocs/                         # Documentation
```

## Key Components

### 1. Decorators

Three decorators mark classes as FlowMason components:

```python
# Node - AI-powered, requires LLM
@node(name="generator", ...)
class GeneratorNode: ...

# Operator - Deterministic, no LLM
@operator(name="http-request", ...)
class HttpRequestOperator: ...

# Control Flow - Modifies execution
@control_flow(name="conditional", control_flow_type="conditional", ...)
class ConditionalComponent: ...
```

### 2. Execution Engine

**DAGExecutor** - Orchestrates pipeline execution:
- Topological sort of stages
- Dependency resolution
- Sequential execution (parallel planned)

**UniversalExecutor** - Executes individual components:
- Input mapping and validation
- Component instantiation
- Output validation
- Tracing

### 3. WebSocket Real-Time

Events flow from executor → API → WebSocket → clients:

```
DAGExecutor.execute()
    │
    ├── hooks.on_stage_started(stage_id)
    │       │
    │       └── ExecutionController.on_stage_started()
    │               │
    │               └── WebSocket.broadcast("STAGE_STARTED")
    │                       │
    │                       └── Frontend receives event
    │
    └── hooks.on_stage_completed(stage_id, result)
```

### 4. Registry System

Components are discovered via:
1. Package scan (`~/.flowmason/packages/`)
2. Metadata extraction from decorated classes
3. Schema generation from Input/Output classes

## Data Models

### Pipeline

```python
class PipelineDetail(BaseModel):
    id: str
    name: str
    description: str
    version: str
    status: PipelineStatus  # DRAFT, PUBLISHED
    stages: List[PipelineStage]
    input_schema: Dict
    output_schema: Dict
```

### Stage

```python
class PipelineStage(BaseModel):
    id: str
    component: str
    depends_on: List[str] = []
    config: Dict[str, Any]
    llm_settings: Optional[LLMSettings]
```

### Component

```python
class ComponentInfo(BaseModel):
    component_type: str
    component_kind: str  # node, operator, control_flow
    category: str
    description: str
    input_schema: Dict
    output_schema: Dict
    requires_llm: bool
    timeout_seconds: int
```

## Current Limitations

| Area | Limitation | Status |
|------|------------|--------|
| Execution | Sequential only | Parallel planned |
| Timeout | Not enforced | Defined, not wired |
| Retry | Not integrated | Logic exists |
| Cancellation | Not integrated | Token exists |
| Storage | SQLite database | File-based planned |
| VSCode | Opens browser | Custom editor planned |
