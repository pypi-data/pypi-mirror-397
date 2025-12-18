# @control_flow Decorator

The `@control_flow` decorator creates components that control pipeline execution flow.

## Basic Usage

```python
from flowmason_core import (
    control_flow, BaseControlFlow, ControlFlowInput, ControlFlowOutput,
    ControlFlowDirective, ControlFlowType, Context
)
from pydantic import Field
from typing import Optional

@control_flow(
    name="conditional",
    description="Execute branches based on condition",
    control_flow_type="conditional",
)
class ConditionalComponent(BaseControlFlow):
    class Input(ControlFlowInput):
        condition: bool = Field(description="Condition to evaluate")
        true_branch: str = Field(description="Stage to execute if true")
        false_branch: Optional[str] = Field(default=None, description="Stage if false")

    class Output(ControlFlowOutput):
        branch_taken: str
        directive: ControlFlowDirective

    async def execute(self, input: Input, context: Context) -> Output:
        branch = input.true_branch if input.condition else input.false_branch

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.CONDITIONAL,
            skip_stages=[
                input.false_branch if input.condition else input.true_branch
            ] if (input.true_branch and input.false_branch) else [],
            branch_taken=branch,
        )

        return self.Output(branch_taken=branch, directive=directive)
```

## Decorator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | Required | Unique component name |
| `description` | `str` | Required | Human-readable description |
| `control_flow_type` | `str` | Required | Type: conditional, router, foreach, trycatch, subpipeline, return |
| `category` | `str` | `"control-flow"` | Component category |

## Control Flow Types

### conditional

If/else branching based on a condition.

```python
@control_flow(name="conditional", control_flow_type="conditional")
class ConditionalComponent(BaseControlFlow):
    ...
```

**Pipeline Usage:**
```json
{
  "id": "check_status",
  "component_type": "conditional",
  "config": {
    "condition": "{{fetch.output.status_code}} == 200",
    "true_branch": "process_data",
    "false_branch": "handle_error"
  }
}
```

### router

Multi-branch routing (switch/case).

```python
@control_flow(name="router", control_flow_type="router")
class RouterComponent(BaseControlFlow):
    class Input(ControlFlowInput):
        value: str
        routes: dict  # {"case1": "stage1", "case2": "stage2"}
        default: Optional[str] = None

    async def execute(self, input: Input, context: Context) -> Output:
        branch = input.routes.get(input.value, input.default)
        skip = [s for k, s in input.routes.items() if k != input.value]

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.ROUTER,
            skip_stages=skip,
            branch_taken=branch,
        )
        return self.Output(branch_taken=branch, directive=directive)
```

**Pipeline Usage:**
```json
{
  "id": "route_by_type",
  "component_type": "router",
  "config": {
    "value": "{{input.content_type}}",
    "routes": {
      "article": "process_article",
      "video": "process_video",
      "image": "process_image"
    },
    "default": "process_generic"
  }
}
```

### foreach

Loop over collections.

```python
@control_flow(name="foreach", control_flow_type="foreach")
class ForEachComponent(BaseControlFlow):
    class Input(ControlFlowInput):
        items: list
        item_variable: str = "item"
        stages: list[str]  # Stages to execute per item
        parallel: bool = False
        max_concurrency: int = 5

    async def execute(self, input: Input, context: Context) -> Output:
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.FOREACH,
            loop_items=input.items,
            loop_variable=input.item_variable,
            loop_stages=input.stages,
            parallel=input.parallel,
            max_concurrency=input.max_concurrency,
        )
        return self.Output(directive=directive)
```

**Pipeline Usage:**
```json
{
  "id": "process_urls",
  "component_type": "foreach",
  "config": {
    "items": "{{input.urls}}",
    "item_variable": "url",
    "stages": ["fetch_url", "parse_content"],
    "parallel": true,
    "max_concurrency": 10
  }
}
```

### trycatch

Error handling with try/catch semantics.

```python
@control_flow(name="trycatch", control_flow_type="trycatch")
class TryCatchComponent(BaseControlFlow):
    class Input(ControlFlowInput):
        try_stages: list[str]
        catch_stages: list[str]
        finally_stages: Optional[list[str]] = None
        on_error: str = "continue"  # continue or propagate

    async def execute(self, input: Input, context: Context) -> Output:
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.TRYCATCH,
            try_stages=input.try_stages,
            catch_stages=input.catch_stages,
            finally_stages=input.finally_stages or [],
            on_error=input.on_error,
        )
        return self.Output(directive=directive)
```

**Pipeline Usage:**
```json
{
  "id": "safe_operation",
  "component_type": "trycatch",
  "config": {
    "try_stages": ["risky_fetch", "process"],
    "catch_stages": ["log_error", "fallback"],
    "finally_stages": ["cleanup"],
    "on_error": "continue"
  }
}
```

### subpipeline

Execute another pipeline.

```python
@control_flow(name="subpipeline", control_flow_type="subpipeline")
class SubPipelineComponent(BaseControlFlow):
    class Input(ControlFlowInput):
        pipeline: str  # Pipeline name or path
        input: dict    # Input to pass

    async def execute(self, input: Input, context: Context) -> Output:
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.SUBPIPELINE,
            subpipeline_name=input.pipeline,
            subpipeline_input=input.input,
        )
        return self.Output(directive=directive)
```

**Pipeline Usage:**
```json
{
  "id": "run_etl",
  "component_type": "subpipeline",
  "config": {
    "pipeline": "pipelines/etl.pipeline.json",
    "input": {
      "source": "{{input.data_source}}",
      "destination": "{{input.output_path}}"
    }
  }
}
```

### return

Early exit with a value.

```python
@control_flow(name="return", control_flow_type="return")
class ReturnComponent(BaseControlFlow):
    class Input(ControlFlowInput):
        value: Any
        condition: Optional[bool] = True

    async def execute(self, input: Input, context: Context) -> Output:
        if not input.condition:
            directive = ControlFlowDirective(
                directive_type=ControlFlowType.RETURN,
                should_return=False,
            )
        else:
            directive = ControlFlowDirective(
                directive_type=ControlFlowType.RETURN,
                should_return=True,
                return_value=input.value,
            )
        return self.Output(directive=directive)
```

**Pipeline Usage:**
```json
{
  "id": "early_exit",
  "component_type": "return",
  "depends_on": ["validate"],
  "config": {
    "condition": "{{validate.output.valid}} == false",
    "value": {
      "error": "Validation failed",
      "details": "{{validate.output.errors}}"
    }
  }
}
```

## ControlFlowDirective

The directive tells the executor how to modify execution:

```python
@dataclass
class ControlFlowDirective:
    directive_type: ControlFlowType

    # Conditional/Router
    skip_stages: list[str] = field(default_factory=list)
    branch_taken: Optional[str] = None

    # ForEach
    loop_items: list = field(default_factory=list)
    loop_variable: str = "item"
    loop_stages: list[str] = field(default_factory=list)
    parallel: bool = False
    max_concurrency: int = 10

    # TryCatch
    try_stages: list[str] = field(default_factory=list)
    catch_stages: list[str] = field(default_factory=list)
    finally_stages: list[str] = field(default_factory=list)
    on_error: str = "continue"

    # SubPipeline
    subpipeline_name: Optional[str] = None
    subpipeline_input: dict = field(default_factory=dict)

    # Return
    should_return: bool = False
    return_value: Any = None
```

## Built-in Control Flow Components

FlowMason Lab provides these ready-to-use components:

| Component | Type | Description |
|-----------|------|-------------|
| `conditional` | conditional | If/else branching |
| `router` | router | Multi-branch routing |
| `foreach` | foreach | Collection iteration |
| `trycatch` | trycatch | Error handling |
| `subpipeline` | subpipeline | Pipeline composition |
| `return` | return | Early exit |

## Error Handling in Control Flow

### TryCatch Behavior

```
on_error: "continue"
- Catch stages execute on error
- Pipeline continues after catch

on_error: "propagate"
- Catch stages execute on error
- Error re-thrown after catch
```

### Error Context

In catch stages, access error info:

```json
{
  "id": "log_error",
  "component_type": "logger",
  "config": {
    "message": "Error: {{_error.message}}",
    "data": {
      "type": "{{_error.type}}",
      "stage": "{{_error.stage}}"
    }
  }
}
```

## Best Practices

1. **Keep It Simple**: Avoid deeply nested control flow
2. **Use TryCatch**: Wrap risky operations
3. **Parallel When Possible**: Use `parallel: true` for independent iterations
4. **Clear Branch Names**: Use descriptive stage IDs for branches
5. **Limit Concurrency**: Don't overwhelm external services

## See Also

- [Nodes](node.md) - AI components
- [Operators](operator.md) - Utility components
- [Concepts: Control Flow](../../03-concepts/control-flow.md)
