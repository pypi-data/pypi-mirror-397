# Execution Engine

## Overview

The FlowMason execution engine consists of two main executors:

1. **DAGExecutor** - Orchestrates pipeline execution with parallel wave-based processing
2. **UniversalExecutor** - Executes individual components with timeout and retry support

**Location:** `core/flowmason_core/execution/universal_executor.py`

## DAGExecutor

The DAGExecutor runs complete pipelines with support for:
- Wave-based parallel execution of independent stages
- Sequential execution mode (backwards compatible)
- Control flow handling (conditional, foreach, trycatch, router, return)
- Cancellation support via CancellationToken
- ExecutionHooks for debugging and monitoring

```python
class DAGExecutor:
    def __init__(
        self,
        registry: ComponentRegistry,
        context: ExecutionContext,
        providers: Optional[Dict[str, Any]] = None,
        default_provider: Optional[str] = None,
        hooks: Optional[ExecutionHooks] = None,
        max_concurrency: int = 10,      # Max parallel stages
        parallel_execution: bool = True  # Enable parallel mode
    ):
        self.executor = UniversalExecutor(registry, context)
        self.control_flow_handler = ControlFlowHandler(self)

    async def execute(
        self,
        stages: list,
        pipeline_input: Dict[str, Any],
        cancellation_token: Optional[CancellationToken] = None,
    ) -> Dict[str, ComponentResult]:
        # Parallel wave execution or sequential
        if self.parallel_execution:
            await self._execute_parallel(...)
        else:
            await self._execute_sequential(...)
```

### Wave-Based Parallel Execution

Independent stages execute concurrently in waves:

```
Input
  │
  ▼
Wave 1: [Stage A, Stage B]  ← Execute in parallel
              │
              ▼
Wave 2: [Stage C]  ← Depends on A and B
              │
              ▼
Wave 3: [Stage D, Stage E, Stage F]  ← All depend on C
```

Features:
- **Semaphore-controlled concurrency** - max_concurrency limits parallel tasks
- **Dependency-aware** - Stages wait for all dependencies
- **Control flow aware** - Respects skip_stages and early return

### Topological Sort

Uses Kahn's algorithm to order stages by dependencies:

```python
def _topological_sort(self, stages: list) -> list:
    stage_map = {s.id: s for s in stages}
    in_degree = {s.id: len(s.depends_on) for s in stages}

    ready = [s for s in stages if len(s.depends_on) == 0]
    sorted_stages = []

    while ready:
        stage = ready.pop(0)
        sorted_stages.append(stage)

        for other in stages:
            if stage.id in other.depends_on:
                in_degree[other.id] -= 1
                if in_degree[other.id] == 0:
                    ready.append(other)

    return sorted_stages
```

## UniversalExecutor

Executes ANY component type (node, operator, control_flow) uniformly.

Features:
- **Timeout enforcement** via `asyncio.wait_for()`
- **Retry logic** with exponential backoff
- **Error classification** (MuleSoft-inspired error types)
- **Tracing** with span attributes

```python
class UniversalExecutor:
    async def execute_component(
        self,
        component_config: ComponentConfig,
        upstream_outputs: Optional[Dict[str, Any]] = None
    ) -> ComponentResult:
        # 1. Load component from registry
        ComponentClass = self.registry.get_component_class(component_config.type)

        # 2. Get metadata (timeout, retry config)
        metadata = self.registry.get_component_metadata(component_config.type)

        # 3. Map config to Input model
        component_input = self.mapper.map_config_to_input(
            component_config,
            ComponentClass.Input,
            upstream_outputs
        )

        # 4. Determine timeout
        timeout_ms = self._get_timeout(component_config, metadata)

        # 5. Execute with timeout and retry
        result = await self._execute_with_timeout_and_retry(
            component_instance,
            component_input,
            context,
            component_config,
            timeout_ms
        )

        # 6. Validate output
        self._validate_output(result, ComponentClass)

        return ComponentResult(...)
```

### Timeout Enforcement

Timeouts are enforced at execution time:

```python
async def _execute_with_timeout_and_retry(self, ...):
    timeout_seconds = timeout_ms / 1000.0

    async def execute_once():
        try:
            return await asyncio.wait_for(
                component.execute(input, context),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            raise TimeoutExecutionError(
                component_id=component_config.id,
                timeout_ms=timeout_ms,
            )

    # Execute with retry if configured
    if retry_config and retry_config.max_retries > 0:
        return await with_retry(execute_once, retry_config, ...)
    else:
        return await execute_once()
```

**Timeout Priority:**
1. `ComponentConfig.timeout_ms` (explicit config)
2. `metadata.timeout_seconds` (from decorator)
3. Default: 60s for nodes, 30s for operators

### Retry Logic

Integrated retry with exponential backoff:

```python
# In retry.py
async def with_retry(
    func: Callable,
    config: RetryConfig,
    component_id: str,
    component_type: str,
    on_retry: Optional[Callable] = None,
) -> Any:
    for attempt in range(config.max_retries + 1):
        try:
            return await func()
        except Exception as e:
            if not is_retryable(e, config):
                raise

            if attempt == config.max_retries:
                raise RetryExhaustedError(...)

            delay = calculate_backoff(attempt, config)
            if on_retry:
                await on_retry(attempt, e, delay)
            await asyncio.sleep(delay / 1000)
```

### Input Mapping

Resolves template references like `{{fetch.output.body}}`:

```python
# In config/input_mapper.py
def map_config_to_input(self, config, InputClass, upstream_outputs):
    def resolve_template(value):
        if isinstance(value, str) and "{{" in value:
            # Handle input.* references
            if value.startswith("{{input."):
                return get_nested(pipeline_input, path)

            # Handle stage.* references
            stage_id, field_path = parse_template(value)
            return get_nested(upstream_outputs[stage_id], field_path)

        return value

    return InputClass(**{k: resolve_template(v) for k, v in config.items()})
```

## ControlFlowHandler

**Location:** `core/flowmason_core/execution/control_flow_handler.py`

Processes ControlFlowDirective from control flow components.

### Supported Control Flow Types

| Type | Description | Implementation |
|------|-------------|----------------|
| **CONDITIONAL** | If/else branching | Adds branches to `skip_stages` |
| **ROUTER** | Switch/case routing | Adds non-matching routes to `skip_stages` |
| **FOREACH** | Loop iteration | Executes loop_stages inline for each item |
| **TRYCATCH** | Error handling | Executes try/catch/finally inline |
| **SUBPIPELINE** | Nested pipeline | Calls subpipeline_executor callback |
| **RETURN** | Early exit | Sets `should_return` flag |

### TryCatch Handling

Executes try_stages, catches errors, runs catch_stages and finally_stages:

```python
async def _handle_trycatch(self, ...):
    # Skip all stages in main DAG (execute inline)
    for skip_id in try_stages + catch_stages + finally_stages:
        self.state.skip_stages.add(skip_id)

    # PHASE 1: Execute try_stages
    try:
        for stage in try_stages:
            result = await self.executor.execute_component(stage, upstream)
            all_results[stage.id] = result
    except Exception as e:
        caught_error = e

    # PHASE 2: Execute catch_stages (if error)
    if caught_error and catch_stages:
        for stage in catch_stages:
            result = await self.executor.execute_component(stage, upstream)
            # Error context available via upstream[trycatch_id].error

    # PHASE 3: Execute finally_stages (always)
    for stage in finally_stages:
        result = await self.executor.execute_component(stage, upstream)

    # PHASE 4: Propagate or continue based on error_scope
    if caught_error and error_scope == "propagate":
        raise caught_error  # MuleSoft on-error-propagate
    # else: continue (on-error-continue)
```

### ForEach Handling

Supports sequential and parallel iteration:

```python
async def _handle_foreach(self, ...):
    items = directive.loop_items
    loop_stages = metadata.get("loop_stages", [])
    parallel = metadata.get("parallel", False)
    max_parallel = metadata.get("max_parallel", 5)

    if parallel:
        # Parallel with semaphore
        semaphore = asyncio.Semaphore(max_parallel)
        tasks = [process_item(idx, item) for idx, item in enumerate(items)]
        results = await asyncio.gather(*tasks)
    else:
        # Sequential
        for idx, item in enumerate(items):
            await process_item(idx, item)
```

### ControlFlowState

Tracks execution state modifications:

```python
@dataclass
class ControlFlowState:
    skip_stages: Set[str] = field(default_factory=set)
    should_return: bool = False
    return_value: Any = None
    return_message: Optional[str] = None
    loop_contexts: Dict[str, LoopContext] = field(default_factory=dict)
    trycatch_contexts: Dict[str, TryCatchState] = field(default_factory=dict)
    subpipeline_results: Dict[str, Any] = field(default_factory=dict)
```

## ExecutionHooks

Protocol for observability and debug control:

```python
class ExecutionHooks(Protocol):
    async def check_and_wait_at_stage(
        self,
        stage_id: str,
        stage_name: Optional[str] = None,
    ) -> bool:
        """Called BEFORE executing each stage. Return False to stop."""
        ...

    async def on_stage_started(
        self,
        stage_id: str,
        component_type: str,
        stage_name: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Called when a stage starts execution."""
        ...

    async def on_stage_completed(
        self,
        stage_id: str,
        component_type: str,
        status: str,
        output: Any = None,
        duration_ms: Optional[int] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
    ) -> None:
        """Called when a stage completes successfully."""
        ...

    async def on_stage_failed(
        self,
        stage_id: str,
        component_type: str,
        error: str,
    ) -> None:
        """Called when a stage fails."""
        ...

    async def on_run_started(
        self,
        pipeline_id: str,
        stage_ids: List[str],
        inputs: Dict[str, Any],
    ) -> None:
        """Called when a run starts."""
        ...

    async def on_run_completed(
        self,
        pipeline_id: str,
        status: str,
        output: Any = None,
        total_duration_ms: Optional[int] = None,
    ) -> None:
        """Called when a run completes."""
        ...

    async def on_run_failed(
        self,
        pipeline_id: str,
        error: str,
        failed_stage_id: Optional[str] = None,
    ) -> None:
        """Called when a run fails."""
        ...
```

## Cancellation

Pass a CancellationToken to support graceful cancellation:

```python
# Create token
token = CancellationToken()

# Pass to executor
result = await dag_executor.execute(stages, input, cancellation_token=token)

# Cancel from another task
token.cancel("User requested stop")
```

The executor checks `token.is_cancelled` before each stage.

## Result Types

### ComponentResult

```python
@dataclass
class ComponentResult:
    component_id: str
    component_type: str
    status: str = "success"  # success, error, skipped
    error: Optional[str] = None
    output: Any = None
    usage: UsageMetrics = field(default_factory=UsageMetrics)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
```

### UsageMetrics

```python
@dataclass
class UsageMetrics:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    provider: Optional[str] = None
    model: Optional[str] = None

    def __add__(self, other: "UsageMetrics") -> "UsageMetrics":
        """Supports aggregation across stages."""
        return UsageMetrics(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            cost_usd=self.cost_usd + other.cost_usd,
            duration_ms=self.duration_ms + other.duration_ms
        )
```

## Error Types (MuleSoft-Inspired)

```python
class ErrorType(Enum):
    """Classification of errors for routing and handling."""
    CONNECTIVITY = "CONNECTIVITY"      # Network/connection issues
    TIMEOUT = "TIMEOUT"                # Operation timed out
    VALIDATION = "VALIDATION"          # Input/output validation
    TRANSFORMATION = "TRANSFORMATION"  # Data transformation failed
    EXPRESSION = "EXPRESSION"          # Expression evaluation failed
    ROUTING = "ROUTING"                # Pipeline routing issue
    SECURITY = "SECURITY"              # Auth/permission issues
    EXECUTION = "EXECUTION"            # General execution error
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"
    CANCELLATION = "CANCELLATION"
    UNKNOWN = "UNKNOWN"
```

## Future Improvements

1. **Streaming** - Stream LLM responses to client
2. **Checkpointing** - Save execution state for resume
3. **Distributed execution** - Execute stages across workers
