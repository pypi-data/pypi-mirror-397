# FlowMason Component Communication Deep Dive

## Executive Summary

This document analyzes FlowMason's component input/output system, pipeline communication patterns, and execution architecture. The analysis reveals a **well-designed foundation with significant gaps** in parallel execution, timeout/retry enforcement, and advanced data transformation capabilities.

---

## 1. Current Architecture Analysis

### 1.1 Input/Output Type System

**Location:** `core/flowmason_core/core/types.py`, `core/flowmason_core/core/decorators.py`

**Base Classes:**
```
NodeInput      → extra="forbid" (strict)
NodeOutput     → extra="allow" (flexible for LLM responses)
OperatorInput  → extra="forbid" (strict)
OperatorOutput → extra="allow" (flexible)
```

**Schema Generation:**
- Extracted at decoration time via `model_json_schema()`
- Stored in `_flowmason_metadata` on the class
- Supports: primitives, list, dict, datetime, date, enums

**Type Coercion (`type_coercion.py`):**
- String → int/float/bool/datetime/date
- JSON string → dict/list
- Enum by name or value
- Union types (tries each variant)

### 1.2 Component Communication (Input Mapping)

**Location:** `core/flowmason_core/config/input_mapper.py`, `template_resolver.py`

**Template Syntax:**
```
{{input.field}}              - Pipeline input
{{input.nested.field}}       - Nested access (dot notation)
{{upstream.stage_id.field}}  - Upstream stage output
{{env.VAR_NAME}}             - Environment variable
{{context.run_id}}           - Execution context
```

**Type Preservation:**
- Single template (`"{{input.data}}"`) preserves original type
- Mixed text (`"Hello {{input.name}}"`) returns string

**Mapping Flow:**
```
Pipeline Config → Template Resolution → Type Coercion → Pydantic Validation → Input Instance
```

### 1.3 Pipeline Execution

**Location:** `core/flowmason_core/execution/universal_executor.py`

**DAG Execution:**
- Topological sort using Kahn's algorithm
- Cycle detection with fallback to original order
- **SEQUENTIAL execution** - stages run one at a time
- Outputs accumulated in `upstream_outputs` dict

---

## 2. Critical Gaps Identified

### 2.1 PARALLEL EXECUTION NOT IMPLEMENTED

**Current Code (universal_executor.py:386-417):**
```python
for idx, stage in enumerate(sorted_stages):
    result = await self.executor.execute_component(stage, all_upstream)
    upstream_outputs[stage.id] = result.output
```

**Impact:**
- Independent stages (no shared dependencies) still run sequentially
- Pipeline time = sum of ALL stage times (not max of parallel paths)
- Example: A→C, B→C where A=5s, B=5s, C=2s
  - Current: 12s (5+5+2)
  - With parallel: 7s (max(5,5)+2)

### 2.2 TIMEOUT NOT ENFORCED

**Defined but unused:**
- `ComponentConfig.timeout_ms` - Field exists
- `metadata.timeout_seconds` - Set by decorators (60s nodes, 30s operators)
- **No `asyncio.wait_for()` in execution code**

**Risk:** Runaway components never terminate

### 2.3 RETRY NOT IMPLEMENTED

**Defined but unused:**
- `RetryConfig` class with max_retries, backoff settings
- `ComponentConfig.retry_config` field
- **No retry loop in executor**

**Risk:** Transient failures (rate limits, network) fail permanently

### 2.4 LIMITED TEMPLATE CAPABILITIES

**Not Supported:**
| Feature | Example | Status |
|---------|---------|--------|
| Conditionals | `{{x ? a : b}}` | Missing |
| Transformations | `{{text \| uppercase}}` | Missing |
| Array indexing | `{{items[0]}}` | Missing |
| Default values | `{{field ?? 'default'}}` | Missing |
| Aggregation | `{{stages \| concat}}` | Missing |
| Object construction | `{{'key': value}}` | Missing |

### 2.5 TYPE SYSTEM LIMITATIONS

**Missing Types:**
- UUID
- Decimal (financial precision)
- Path
- Nested Pydantic models
- Tuple, Set

**Missing Validation:**
- Cross-field constraints
- Custom validators (@field_validator)
- Email/URL format validation
- Schema versioning

### 2.6 ERROR HANDLING GAPS

- Template errors don't show available keys
- Coercion errors lack constraint details
- No fallback templates
- No error-based routing

---

## 3. Data Flow Bottlenecks

### 3.1 All Upstream in Context
Every stage receives ALL previous outputs:
```python
all_upstream = {**upstream_outputs}  # Everything
```
- Large early outputs bloat context for all subsequent stages
- No selective filtering

### 3.2 Output Structure Assumptions
- Templates assume dict-like access
- Custom objects may not traverse correctly
- No explicit serialization format

### 3.3 Provider Sharing
- Single provider instance shared across stages
- No isolation, no load balancing
- Rate limit state shared

---

## 4. Potential Improvements

### Priority 1: Critical (Execution Correctness)

#### 4.1 Implement Parallel Execution
```python
# Group independent stages
async def execute_parallel(stages, upstream):
    independent = find_stages_with_satisfied_deps(stages, upstream)
    results = await asyncio.gather(*[
        executor.execute_component(s, upstream) for s in independent
    ])
    return results
```

#### 4.2 Implement Timeout Enforcement
```python
timeout = config.timeout_ms or (metadata.timeout_seconds * 1000)
result = await asyncio.wait_for(
    component.execute(input, context),
    timeout=timeout/1000
)
```

#### 4.3 Implement Retry Logic
```python
for attempt in range(retry_config.max_retries + 1):
    try:
        return await execute()
    except RetryableError:
        if attempt == max_retries: raise
        await asyncio.sleep(backoff_delay(attempt))
```

### Priority 2: Enhanced Communication

#### 4.4 Template Transformations
Add Jinja2-style filters:
```
{{input.text | uppercase}}
{{input.items | first}}
{{input.count | default(0)}}
{{upstream.results | pluck('status') | join(',')}}
```

#### 4.5 Conditional Mapping
```json
{
  "priority": {
    "$if": "{{input.urgent}}",
    "then": "high",
    "else": "normal"
  }
}
```

#### 4.6 Array Operations
```
{{input.items[0]}}
{{upstream.results[-1]}}
{{input.data.*.name}}  // pluck from array of objects
```

### Priority 3: Type System Enhancements

#### 4.7 Additional Types
- UUID with validation
- Decimal for financial data
- Path with existence checking
- Nested Pydantic model support

#### 4.8 Cross-Field Validation
```python
@model_validator(mode='after')
def check_range(self):
    if self.min > self.max:
        raise ValueError("min must be <= max")
```

#### 4.9 Schema Versioning
Track input/output schema changes for compatibility checking.

### Priority 4: Execution Features

#### 4.10 Conditional Stage Execution
```json
{
  "id": "send_alert",
  "condition": "{{upstream.classify.severity}} == 'critical'"
}
```

#### 4.11 Streaming Results
WebSocket endpoint for real-time stage completion updates.

#### 4.12 Run Cancellation
Proper task handle management for CancelledError propagation.

---

## 5. Key Files to Modify

| Area | File | Changes |
|------|------|---------|
| Parallel Exec | `execution/universal_executor.py` | Add parallel group execution |
| Timeouts | `execution/universal_executor.py` | Add asyncio.wait_for |
| Retries | `execution/universal_executor.py` | Add retry loop |
| Templates | `config/template_resolver.py` | Add filters, conditionals |
| Types | `core/types.py` | Add UUID, Decimal, nested models |
| Coercion | `config/type_coercion.py` | Add new type handlers |
| Validation | `registry/extractor.py` | Add cross-field support |

---

---

## 6. Operators Deep Dive

### 6.1 Operator vs Node

| Aspect | Operators | Nodes |
|--------|-----------|-------|
| **Purpose** | Utility, data transformation | AI-powered components |
| **LLM Required** | No (`requires_llm=False`) | Yes (`requires_llm=True`) |
| **Deterministic** | Yes (default) | No (LLM randomness) |
| **Default Timeout** | 30 seconds | 60 seconds |
| **Token/Cost Tracking** | No | Yes |
| **Decorator** | `@operator` | `@node` |

### 6.2 Built-in Core Operators

Located in `lab/flowmason_lab/operators/core/`:

| Operator | Purpose | Key Features |
|----------|---------|--------------|
| `variable_set` | Manage pipeline state | Dot-path extraction, scoped variables |
| `http_request` | External API calls | All HTTP methods, auth, JSON handling |
| `json_transform` | Transform data | JMESPath, field mapping, flattening |
| `filter` | Conditional filtering | Python expressions, field conditions |
| `logger` | Structured logging | Tags, passthrough for chaining |
| `schema_validate` | JSON Schema validation | Type coercion, error collection |
| `loop` | Batch iteration | Pagination, max_iterations |

### 6.3 Operator Input Pattern

Operators use `data: Any` for flexible payload while maintaining typed config:

```python
class Input(OperatorInput):
    data: Any = Field(description="The data to transform")  # Flexible
    mapping: Dict[str, str] = Field(...)  # Typed config
    jmespath_expression: Optional[str] = Field(...)  # Typed config
```

---

## 7. Pipeline as Code (Transpilation Model)

### 7.1 Mental Model

```
Pipeline     = Class (accepts input, returns output)
├── Node     = Method that calls LLM API
├── Operator = Pure method (deterministic)
└── ???      = Control flow primitives (MISSING)
```

### 7.2 Target: Transpilable to Apex/Python

```python
class CustomerAnalysisPipeline:
    def execute(self, input: PipelineInput) -> PipelineOutput:
        validated = self.validate_schema(input.data)        # Operator

        if not validated.is_valid:                          # Conditional - MISSING
            return self.handle_error(validated.errors)

        for customer in input.customers:                    # For-each - MISSING
            enriched = self.fetch_crm(customer.id)          # Operator
            analysis = self.analyze(enriched, llm=claude)   # Node
            results.append(analysis)

        return PipelineOutput(results=results)
```

### 7.3 What EXISTS vs What's MISSING

| Category | Exists | Missing |
|----------|--------|---------|
| **Computation** | Node (LLM), Operator (utility) | ✓ Complete |
| **Data Transform** | json_transform, filter, variable_set | ✓ Good |
| **I/O** | http_request | File read/write, Database |
| **Control Flow** | Loop (batching only) | For-each (nested execution), While loop |
| **Branching** | Filter (boolean) | Conditional execution (if/else), Switch/router |
| **Error Handling** | Retry config | Try-catch, Error recovery paths |
| **Composition** | None | Call sub-pipeline, Return early |
| **Events** | None | Triggers, Scheduled, Webhooks |

---

## 8. Missing Component Types (CRITICAL)

### 8.1 New `@control_flow` Decorator

Distinct from `@node` and `@operator`:

```python
@control_flow(
    name="conditional",
    category="control_flow",
    icon="git-branch",
    color="#F59E0B"
)
class ConditionalOperator:
    class Input(ControlFlowInput): ...
    class Output(ControlFlowOutput): ...
```

### 8.2 Control Flow Directive Pattern

Control flow components return execution directives, not just data:

```python
class ControlFlowDirective(BaseModel):
    directive_type: Literal["conditional", "foreach", "trycatch", "router", "subpipeline"]
    skip_stages: List[str] = []      # Stages to skip
    execute_stages: List[str] = []   # Stages that were executed
    nested_results: Dict[str, ComponentResult] = {}
```

### 8.3 Five New Component Types

| Component | Input Fields | Behavior | Canvas Shape |
|-----------|--------------|----------|--------------|
| **Conditional** | `condition: bool`, `true_branch: str`, `false_branch: str` | Execute ONE branch | Diamond |
| **ForEach** | `items: List`, `loop_stages: List[str]`, `parallel: bool` | Sub-executor per item | Container |
| **TryCatch** | `try_stages: List[str]`, `catch_stages: List[str]` | Error boundary | Container |
| **Router** | `value: Any`, `routes: Dict[str, str]` | Switch/case to N branches | Diamond + N outputs |
| **SubPipeline** | `pipeline_id: str`, `input_mapping: Dict` | Call another pipeline | Nested icon |

### 8.4 Example: Conditional

```json
{
  "id": "branch_decision",
  "type": "conditional",
  "depends_on": ["check_score"],
  "input_mapping": {
    "condition": "{{upstream.check_score.passed}}",
    "true_branch": "high_score_path",
    "false_branch": "low_score_path"
  }
}
```

### 8.5 Example: ForEach

```json
{
  "id": "process_each",
  "type": "foreach",
  "input_mapping": {
    "items": "{{upstream.get_items.body.data}}",
    "loop_stages": ["enrich_item", "validate_item"],
    "parallel": true,
    "max_parallel": 10
  }
}
```

---

## 9. Execution Gap Fixes (Detailed Design)

### 9.1 Parallel Execution (Wave-Based)

Replace sequential loop with parallel wave execution:

```python
async def execute(self, stages, pipeline_input):
    while remaining:
        ready = self._get_ready_stages(remaining, completed)  # Deps satisfied
        wave_results = await self._execute_wave(ready)        # asyncio.gather
        # Update completed, remaining
```

**Key Considerations:**
- Provider pooling for thread safety
- Semaphore for max concurrency
- Partial failure handling

### 9.2 Timeout Enforcement

```python
async def execute_component(self, config, upstream):
    timeout = config.timeout_ms or metadata.timeout_seconds * 1000

    try:
        result = await asyncio.wait_for(
            component.execute(input, context),
            timeout=timeout/1000
        )
    except asyncio.TimeoutError:
        raise TimeoutExecutionError(config.id, timeout)
```

### 9.3 Retry Logic

New file `execution/retry.py`:

```python
async def with_retry(func, config: RetryConfig, retryable_errors):
    for attempt in range(config.max_retries + 1):
        try:
            return await func()
        except tuple(retryable_errors) as e:
            if attempt == config.max_retries:
                raise
            delay = calculate_backoff(attempt, config)
            await asyncio.sleep(delay)
```

**Retryable by default:** ConnectionError, TimeoutError, RateLimitError

### 9.4 Conditional Stage Execution

Add to `ComponentConfig`:

```python
condition: Optional[str]     # "{{upstream.check.passed}}"
skip_if: Optional[str]       # "{{input.skip_validation}}"
skip_output: Optional[Dict]  # Default output when skipped
```

### 9.5 Run Cancellation

New `CancellationToken`:

```python
token = CancellationToken()
task = asyncio.create_task(executor.execute(stages, input, token))

# Later:
token.cancel("User requested")

# Executor checks token between stages, cancels active tasks
```

---

## 10. Implementation Priority

| Phase | Items | Rationale |
|-------|-------|-----------|
| **Phase 1** | Timeout + Retry | Safety, resilience (low risk) |
| **Phase 2** | Conditional Execution + Cancellation | Control (medium risk) |
| **Phase 3** | Parallel Execution | Performance (higher risk) |
| **Phase 4** | Conditional + Router | Basic control flow |
| **Phase 5** | ForEach + TryCatch | Nested execution |
| **Phase 6** | SubPipeline | Composition |

---

## 11. Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `core/flowmason_core/execution/retry.py` | Retry logic with backoff |
| `core/flowmason_core/execution/cancellation.py` | CancellationToken |
| `lab/flowmason_lab/operators/control_flow/__init__.py` | Control flow package |
| `lab/flowmason_lab/operators/control_flow/conditional.py` | Conditional component |
| `lab/flowmason_lab/operators/control_flow/foreach.py` | ForEach component |
| `lab/flowmason_lab/operators/control_flow/trycatch.py` | TryCatch component |
| `lab/flowmason_lab/operators/control_flow/router.py` | Router component |
| `lab/flowmason_lab/operators/control_flow/subpipeline.py` | SubPipeline component |

### Modified Files

| File | Changes |
|------|---------|
| `core/flowmason_core/core/decorators.py` | Add `@control_flow` decorator |
| `core/flowmason_core/core/types.py` | Add `ControlFlowInput`, `ControlFlowOutput` |
| `core/flowmason_core/config/types.py` | Add `condition`, `skip_if` fields |
| `core/flowmason_core/execution/universal_executor.py` | Parallel, timeout, retry, directives |
| `core/flowmason_core/execution/types.py` | New error types |
| `studio/frontend/src/components/PipelineCanvas.tsx` | New node shapes |

---

## 12. Summary Table

| Category | Current State | Gap Severity | Recommended Action |
|----------|--------------|--------------|-------------------|
| **Missing Component Types** |
| Conditional (if/else) | Only Filter (boolean output) | **CRITICAL** | New `@control_flow` component |
| ForEach (nested exec) | Loop batches only | **CRITICAL** | New component with sub-executor |
| TryCatch | None (failure stops) | **HIGH** | New error boundary component |
| Router/Switch | None | **HIGH** | New multi-branch component |
| SubPipeline | None | **MEDIUM** | New composition component |
| **Execution Gaps** |
| Parallel Execution | Not implemented | **HIGH** | Wave-based asyncio.gather |
| Timeouts | Defined, not enforced | **HIGH** | Add wait_for wrapper |
| Retries | Defined, not implemented | **HIGH** | Add retry loop with backoff |
| Cancellation | Not implemented | **HIGH** | CancellationToken pattern |
| **Template Enhancements** |
| Template Transforms | Not supported | MEDIUM | Add filter syntax |
| Array Access | Not supported | MEDIUM | Add index syntax |
| **Type System** |
| Type Coverage | Limited | LOW | Add UUID, Decimal |
| Schema Versioning | Not supported | LOW | Add version tracking |

---

## 13. Testing Patterns (Salesforce @isTest / MuleSoft MUnit Style)

### 13.1 Current Test Infrastructure

```
tests/
├── conftest.py              # Shared fixtures (@TestSetup equivalent)
├── registry/                # Registry unit tests
├── execution/               # Executor tests
├── integration/             # Full pipeline tests (Test.startTest/stopTest)
├── config/                  # Mapping, coercion tests
└── providers/               # Provider mock tests
```

**Key Pattern:** Fixture-based architecture with `@pytest.fixture` (like Apex `@TestSetup`)

### 13.2 Async Test Pattern

```python
@pytest.mark.asyncio
async def test_execute_node_component(registry, execution_context):
    executor = UniversalExecutor(registry, execution_context)
    config = ComponentConfig(id="test", type="generator", ...)
    result = await executor.execute_component(config)
    assert result.status == "success"
```

### 13.3 Mock Patterns for LLM Providers

```python
from unittest.mock import Mock, patch

@pytest.fixture
def mock_llm_provider():
    provider = Mock()
    provider.complete.return_value = ProviderResponse(
        content="Mocked response",
        model="mock-model",
        usage={"input_tokens": 10, "output_tokens": 20}
    )
    return provider
```

### 13.4 Control Flow Test Strategy

```python
# Test Conditional branches
@pytest.mark.parametrize("condition,expected_branch", [
    (True, "true_path"),
    (False, "false_path"),
])
@pytest.mark.asyncio
async def test_conditional_branches(condition, expected_branch):
    config = ComponentConfig(
        id="branch",
        type="conditional",
        input_mapping={
            "condition": condition,
            "true_branch": "success_stage",
            "false_branch": "failure_stage"
        }
    )
    result = await executor.execute_component(config)
    assert result.output["branch_taken"] == expected_branch
```

---

## 14. Registry Integration

### 14.1 Zero Hardcoded Components

The registry dynamically loads ALL components from `.fmpkg` packages:

```python
class ComponentRegistry:
    def scan_packages(self, packages_dir):
        fmpkg_files = list(scan_dir.glob("**/*.fmpkg"))
        for fmpkg_path in fmpkg_files:
            self.register_package(str(fmpkg_path))
```

### 14.2 Decorator Stores Metadata (No Auto-Register)

```python
@node(name="generator", category="nlp", ...)
class GeneratorNode:
    ...

# After decoration:
cls._flowmason_metadata = {
    "name": "generator",
    "category": "nlp",
    "component_kind": "node",
    "input_schema": {...},
    "output_schema": {...},
}
```

### 14.3 @control_flow Integration

New decorator follows same pattern - categories auto-detected:

```python
@control_flow(
    name="conditional",
    category="control_flow",  # Auto-added to registry categories
    icon="git-branch",
    color="#EC4899"
)
class ConditionalComponent:
    class Input(ControlFlowInput): ...
    class Output(ControlFlowOutput): ...
```

**No code changes needed** - registry discovers "control_flow" category automatically.

---

## 15. Error Handling (MuleSoft Pattern)

### 15.1 Current Error Hierarchy

```
ExecutionError (base)
├── ComponentExecutionError (stage failures)
├── MappingExecutionError (input mapping)
├── ValidationExecutionError (output validation)
└── ProviderError (LLM provider issues)
```

### 15.2 Gap: No MuleSoft-Style Error Types

**MuleSoft has:** CONNECTIVITY, EXPRESSION, ROUTING, SECURITY, VALIDATION, TIMEOUT

**FlowMason needs:**

```python
class ErrorType(str, Enum):
    CONNECTIVITY = "CONNECTIVITY"     # Network, provider down
    EXPRESSION = "EXPRESSION"         # Template resolution
    ROUTING = "ROUTING"               # Invalid dependencies
    SECURITY = "SECURITY"             # Auth, API key
    VALIDATION = "VALIDATION"         # Schema mismatch
    EXECUTION = "EXECUTION"           # Component logic
    TIMEOUT = "TIMEOUT"               # Time limit exceeded
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"
```

### 15.3 Gap: No on-error-propagate/continue

**MuleSoft has:**
- `on-error-propagate` - Re-throws after handling
- `on-error-continue` - Handles error, continues flow

**FlowMason needs ErrorScope:**

```python
class ErrorScope:
    def __init__(self, on_error: str = "propagate"):  # "propagate" | "continue"
        self.on_error = on_error

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.on_error == "continue":
            return True  # Suppress exception, continue flow
        raise  # Propagate
```

### 15.4 Gap: Retry Not Implemented

`RetryConfig` exists but is **never used**:

```python
# Exists in config/types.py but NOT enforced:
class RetryConfig(BaseModel):
    max_retries: int = 3
    initial_delay_ms: int = 1000
    backoff_multiplier: float = 2.0
```

### 15.5 Recommended Error Handler Chain

```python
class ErrorHandlerChain:
    def add_handler(self, predicate, handler):
        """if predicate(error) is True, call handler"""

    async def handle(self, error) -> bool:
        for predicate, handler in self.handlers:
            if predicate(error):
                await handler(error)
                return True
        return False

# Usage:
chain.add_handler(
    lambda e: e.error_type == ErrorType.TIMEOUT,
    async_retry_handler
)
chain.add_handler(
    lambda e: e.error_type == ErrorType.RETRY_EXHAUSTED,
    async_alert_oncall
)
```

---

## 16. Execution Tracking (Salesforce Flow Style)

### 16.1 Current State Management

**Frontend (PipelineCanvas.tsx):**
- Per-stage status: `idle | pending | running | completed | success | failed`
- Visual indicators: spinner, checkmark, X icons
- Data flow animation on edges
- Breakpoint indicators

**Backend:**
- WebSocket real-time updates (`/api/v1/ws/runs`)
- Debug control: pause/resume/step/breakpoints
- Span-based tracing with parent-child hierarchy

### 16.2 WebSocket Events

```python
class WebSocketEventType(str, Enum):
    RUN_STARTED = "run_started"
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    STAGE_FAILED = "stage_failed"
    RUN_COMPLETED = "run_completed"
    EXECUTION_PAUSED = "execution_paused"
    BREAKPOINT_HIT = "breakpoint_hit"
```

### 16.3 Gap: No Salesforce-Style Flow Interviews

**Salesforce has:**
- Flow interviews track execution state
- Paused flows can resume
- Element-by-element debug logs

**FlowMason needs ExecutionSession:**

```python
class ExecutionSession(Base):
    id: str                      # session_123abc
    run_id: str
    status: str                  # active, paused, completed, abandoned
    current_stage_id: str
    paused_at_stage_id: str
    session_variables: Dict      # Mutable state across pauses
    resume_token: str            # For API resumption
    last_checkpoint: Dict        # State to resume from
```

### 16.4 Gap: No Loop Iteration Tracking

**For ForEach control flow, need:**

```python
class LoopExecution:
    loop_id: str
    stage_id: str               # Stage with ForEach
    items_total: int
    items_completed: int
    items_failed: int
    iterations: List[StageExecution]  # One per iteration
```

### 16.5 Gap: No Fault Flow Tracking

**Need fault_flow flag:**

```python
class ControlFlowExecution:
    execution_id: str
    stage_id: str
    loop_iteration: Optional[int]
    fault_flow: bool = False     # Is this a fault path?
    condition_result: Optional[bool]
    checkpoint_data: Optional[Dict]  # For resumption
```

### 16.6 New WebSocket Events Needed

```python
# Control flow events
LOOP_STARTED = "loop_started"
LOOP_ITERATION_START = "loop_iteration_start"
LOOP_ITERATION_END = "loop_iteration_end"
LOOP_COMPLETED = "loop_completed"
FAULT_FLOW_ENTERED = "fault_flow_entered"
SESSION_CHECKPOINT = "session_checkpoint"
```

---

## 17. Salesforce/MuleSoft Feature Mapping

| Salesforce/MuleSoft | FlowMason Current | FlowMason Needed |
|---------------------|-------------------|------------------|
| **Apex @isTest** | pytest fixtures | ✓ Good |
| **MUnit mocks** | unittest.mock | ✓ Good |
| **Flow Interviews** | None | ExecutionSession |
| **Debug Logs** | Partial (spans) | ControlFlowExecution |
| **Element States** | Basic status | Status timeline |
| **Subflows** | None | SubPipeline tracking |
| **Loop Tracking** | None | LoopExecution model |
| **Fault Paths** | Stage failure only | fault_flow flag |
| **on-error-continue** | None | ErrorScope |
| **Error Types** | Implicit | ErrorType enum |
| **Retry Strategy** | Config exists, unused | Implement retry loop |

---

## 18. Implementation Roadmap

**Note:** No backward compatibility required - early development stage allows breaking changes for optimal architecture.

### Phase 1: Foundation (Safety & Resilience)
1. Implement ErrorType enum and FlowMasonError
2. Add timeout enforcement (asyncio.wait_for)
3. Implement retry logic with backoff
4. Add error classification

### Phase 2: Error Control (MuleSoft Style)
5. Implement ErrorScope (on-error-propagate/continue)
6. Add error handler chains
7. Add TryCatch control flow component

### Phase 3: Execution Tracking (Salesforce Style)
8. Add ControlFlowExecution model
9. Implement ExecutionSession for pause/resume
10. Add loop iteration tracking
11. Add fault flow detection

### Phase 4: Control Flow Components
12. Conditional component
13. Router component
14. ForEach component (with iteration tracking)
15. SubPipeline component

### Phase 5: Frontend
16. Timeline visualization
17. Loop iteration inspector
18. Fault flow visualization
19. Resume workflow UI
