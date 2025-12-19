# Control Flow

## What is Control Flow?

**Control Flow** components modify pipeline execution - they enable branching, looping, error handling, and early returns. Unlike nodes and operators that process data, control flow components return **directives** that tell the executor how to proceed.

## Characteristics

| Property | Value |
|----------|-------|
| Decorator | `@control_flow` |
| Requires LLM | No |
| Default timeout | 30 seconds |
| Default color | Pink (#EC4899) |
| Returns | `ControlFlowDirective` |

## Control Flow Types

| Type | Component | Description |
|------|-----------|-------------|
| `conditional` | ConditionalComponent | If/else branching |
| `foreach` | ForEachComponent | Loop over collections |
| `trycatch` | TryCatchComponent | Error handling |
| `router` | RouterComponent | Switch/case routing |
| `subpipeline` | SubPipelineComponent | Call another pipeline |
| `return` | ReturnComponent | Early exit |

## ControlFlowDirective

Control flow components return a `ControlFlowDirective` that modifies execution:

```python
class ControlFlowDirective(BaseModel):
    directive_type: ControlFlowType      # conditional, foreach, etc.
    skip_stages: List[str] = []          # Stages to skip
    execute_stages: List[str] = []       # Stages that were executed
    loop_items: Optional[List[Any]]      # For foreach
    loop_results: Optional[List[Any]]
    current_item: Optional[Any]
    current_index: Optional[int]
    nested_results: Dict[str, Any] = {}  # Sub-execution results
    error: Optional[str]                 # For trycatch
    error_type: Optional[str]
    recovered: bool = False              # Whether error was recovered
    continue_execution: bool = True      # Whether to continue pipeline
    branch_taken: Optional[str]          # For conditional/router
    output_data: Optional[Any]           # Output from control flow
    metadata: Dict[str, Any] = {}
```

## Components

### Conditional (If/Else)

Branch execution based on a boolean condition.

```python
@control_flow(
    name="conditional",
    description="If/else branching",
    category="control-flow",
    control_flow_type="conditional",
    icon="git-branch",
    color="#EC4899"
)
class ConditionalComponent:
    class Input(ControlFlowInput):
        condition: bool = Field(description="Condition to evaluate")
        true_branch: str = Field(description="Stage ID for true path")
        false_branch: Optional[str] = Field(default=None, description="Stage ID for false path")

    class Output(ControlFlowOutput):
        branch_taken: str
        directive: ControlFlowDirective
```

**Usage in pipeline:**
```json
{
  "id": "check-length",
  "component": "conditional",
  "config": {
    "condition": "{{len(input.text) > 1000}}",
    "true_branch": "summarize-long",
    "false_branch": "summarize-short"
  }
}
```

### ForEach (Loop)

Iterate over a collection, executing stages for each item.

```python
@control_flow(
    name="foreach",
    description="Loop over collections",
    category="control-flow",
    control_flow_type="foreach",
    icon="repeat",
    color="#10B981"
)
class ForEachComponent:
    class Input(ControlFlowInput):
        items: List[Any] = Field(description="Items to iterate over")
        loop_stages: List[str] = Field(description="Stages to execute per item")
        parallel: bool = Field(default=False, description="Execute items in parallel")
        max_parallel: int = Field(default=5, description="Max parallel executions")
        break_on_error: bool = Field(default=True, description="Stop on first error")

    class Output(ControlFlowOutput):
        results: List[Any]
        directive: ControlFlowDirective
```

**Usage:**
```json
{
  "id": "process-items",
  "component": "foreach",
  "config": {
    "items": "{{input.documents}}",
    "loop_stages": ["extract", "summarize"],
    "item_variable": "current_doc",
    "index_variable": "doc_index",
    "parallel": true,
    "max_parallel": 3
  }
}
```

**Accessing Loop Variables:**

Inside loop stages, access the current item and index via `{{context.variable_name}}`:

```json
{
  "id": "extract",
  "component_type": "json_transform",
  "depends_on": ["process-items"],
  "config": {
    "data": {
      "item": "{{context.current_doc}}",
      "index": "{{context.doc_index}}"
    },
    "jmespath_expression": "{ content: item.text, position: index }"
  }
}
```

> **Important:** Loop stages must have `depends_on: ["foreach_stage_id"]` to ensure they execute within the foreach context.

### TryCatch (Error Handling)

Handle errors with recovery paths (MuleSoft-inspired).

```python
@control_flow(
    name="trycatch",
    description="Error handling with recovery",
    category="control-flow",
    control_flow_type="trycatch",
    icon="shield",
    color="#EF4444"
)
class TryCatchComponent:
    class Input(ControlFlowInput):
        try_stages: List[str] = Field(description="Stages to try")
        catch_stages: List[str] = Field(default=[], description="Stages on error")
        finally_stages: List[str] = Field(default=[], description="Always execute")
        error_scope: str = Field(default="propagate", description="propagate or continue")
        catch_error_types: List[str] = Field(default=[], description="Specific errors to catch")

    class Output(ControlFlowOutput):
        error: Optional[str]
        error_type: Optional[str]
        recovered: bool
        directive: ControlFlowDirective
```

**Error scopes:**
- `propagate` - Re-raise error after catch (like `on-error-propagate`)
- `continue` - Swallow error, continue pipeline (like `on-error-continue`)

**Usage:**
```json
{
  "id": "safe-api-call",
  "component": "trycatch",
  "config": {
    "try_stages": ["fetch-data"],
    "catch_stages": ["use-fallback"],
    "finally_stages": ["cleanup"],
    "error_scope": "continue"
  }
}
```

**Accessing Results from Try/Catch Stages:**

Downstream stages can access results from nested stages via `{{upstream.nested_stage_id}}`:

```json
{
  "id": "process-result",
  "component_type": "json_transform",
  "depends_on": ["safe-api-call"],
  "config": {
    "data": {
      "api_result": "{{upstream.fetch-data}}",
      "trycatch_info": "{{upstream.safe-api-call}}"
    },
    "jmespath_expression": "{ data: api_result.body, status: trycatch_info.status }"
  }
}
```

> **Note:** Try and catch stages must have `depends_on: ["trycatch_stage_id"]` for proper execution order.

### Router (Switch/Case)

Route to different branches based on a value.

```python
@control_flow(
    name="router",
    description="Switch/case routing",
    category="control-flow",
    control_flow_type="router",
    icon="git-merge",
    color="#F59E0B"
)
class RouterComponent:
    class Input(ControlFlowInput):
        value: Any = Field(description="Value to route on")
        routes: Dict[str, str] = Field(description="Value → stage ID mapping")
        default: Optional[str] = Field(default=None, description="Default stage")

    class Output(ControlFlowOutput):
        route_taken: str
        directive: ControlFlowDirective
```

**Usage:**
```json
{
  "id": "route-by-type",
  "component": "router",
  "config": {
    "value": "{{input.document_type}}",
    "routes": {
      "pdf": "process-pdf",
      "doc": "process-doc",
      "txt": "process-text"
    },
    "default": "process-generic"
  }
}
```

### SubPipeline (Composition)

Call another pipeline as a sub-routine.

```python
@control_flow(
    name="subpipeline",
    description="Call another pipeline",
    category="control-flow",
    control_flow_type="subpipeline",
    icon="workflow",
    color="#6366F1"
)
class SubPipelineComponent:
    class Input(ControlFlowInput):
        pipeline_id: str = Field(description="Pipeline to call")
        pipeline_version: Optional[str] = Field(default=None)
        input_data: Dict[str, Any] = Field(description="Input for sub-pipeline")
        timeout_ms: int = Field(default=60000)

    class Output(ControlFlowOutput):
        pipeline_id: str
        result: Any
        directive: ControlFlowDirective
```

**Usage:**
```json
{
  "id": "run-preprocessing",
  "component": "subpipeline",
  "config": {
    "pipeline_id": "preprocessing-pipeline",
    "input_data": {
      "documents": "{{input.raw_documents}}"
    }
  }
}
```

### Return (Early Exit)

Exit the pipeline early with a return value.

```python
@control_flow(
    name="return",
    description="Early exit from pipeline",
    category="control-flow",
    control_flow_type="return",
    icon="corner-down-left",
    color="#8B5CF6"
)
class ReturnComponent:
    class Input(ControlFlowInput):
        condition: bool = Field(default=True, description="Return if true")
        return_value: Any = Field(description="Value to return")
        message: str = Field(default="", description="Return reason")

    class Output(ControlFlowOutput):
        should_return: bool
        return_value: Any
        directive: ControlFlowDirective
```

**Usage (guard clause):**
```json
{
  "id": "check-input",
  "component": "return",
  "config": {
    "condition": "{{not input.text}}",
    "return_value": {"error": "No input provided"},
    "message": "Empty input"
  }
}
```

## Creating Custom Control Flow

```python
from flowmason_core.core import control_flow, Field
from flowmason_core.core.types import (
    ControlFlowInput,
    ControlFlowOutput,
    ControlFlowDirective,
    ControlFlowType
)

@control_flow(
    name="retry-on-fail",
    description="Retry stages on failure",
    category="control-flow",
    control_flow_type="trycatch"  # Use existing type or define new
)
class RetryOnFailComponent:
    class Input(ControlFlowInput):
        stages: List[str]
        max_retries: int = 3
        delay_ms: int = 1000

    class Output(ControlFlowOutput):
        attempts: int
        success: bool
        directive: ControlFlowDirective

    async def execute(self, input: Input, context) -> Output:
        # Custom retry logic
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.TRYCATCH,
            execute_stages=input.stages,
            metadata={"max_retries": input.max_retries}
        )
        return self.Output(
            attempts=1,
            success=True,
            directive=directive
        )
```

## Best Practices

1. **Keep control flow simple** - Complex logic belongs in operators
2. **Use meaningful stage IDs** - Makes pipelines readable
3. **Handle edge cases** - Empty lists in foreach, missing routes
4. **Consider error handling** - Wrap risky operations in trycatch
5. **Use guard clauses** - Return early for invalid inputs
6. **Avoid deep nesting** - Flatten when possible
