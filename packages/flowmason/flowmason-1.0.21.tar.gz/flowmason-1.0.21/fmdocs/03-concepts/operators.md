# Operators

## What is an Operator?

An **Operator** is a deterministic, non-AI component for data transformation and utility tasks. Operators don't require an LLM - they perform predictable operations like HTTP calls, JSON parsing, filtering, and validation.

## Characteristics

| Property | Value |
|----------|-------|
| Decorator | `@operator` |
| Requires LLM | No |
| Default timeout | 30 seconds |
| Deterministic | Yes (same input = same output) |
| Default color | Blue (#3B82F6) |

## Creating an Operator

```python
from flowmason_core.core import operator, Field
from flowmason_core.core.types import OperatorInput, OperatorOutput
from typing import Any, List

@operator(
    name="filter-items",
    description="Filter a list based on a condition",
    category="transform",
    timeout=30
)
class FilterItemsOperator:
    """Filters items from a list based on a field value."""

    class Input(OperatorInput):
        items: List[dict] = Field(description="List of items to filter")
        field: str = Field(description="Field name to check")
        value: Any = Field(description="Value to match")
        operator: str = Field(default="eq", description="Comparison: eq, ne, gt, lt, contains")

    class Output(OperatorOutput):
        filtered: List[dict] = Field(description="Filtered items")
        count: int = Field(description="Number of items after filtering")

    async def execute(self, input: Input, context) -> Output:
        filtered = []
        for item in input.items:
            item_value = item.get(input.field)
            if self._matches(item_value, input.value, input.operator):
                filtered.append(item)

        return self.Output(filtered=filtered, count=len(filtered))

    def _matches(self, item_value, target, op):
        if op == "eq":
            return item_value == target
        elif op == "ne":
            return item_value != target
        elif op == "gt":
            return item_value > target
        elif op == "lt":
            return item_value < target
        elif op == "contains":
            return target in str(item_value)
        return False
```

## Decorator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Unique identifier (kebab-case) |
| `description` | str | Required | Human-readable description |
| `category` | str | `"general"` | Component category |
| `version` | str | `"1.0.0"` | Semantic version |
| `icon` | str | `"cog"` | Lucide icon name |
| `color` | str | `"#3B82F6"` | Hex color (blue default) |
| `timeout` | int | `30` | Execution timeout in seconds |

**Note:** Operators don't have `recommended_providers`, `max_retries`, or LLM-related parameters.

## Input/Output Classes

### OperatorInput

Base class for operator inputs:

```python
class Input(OperatorInput):
    data: dict
    expression: str = Field(min_length=1)
    timeout: int = Field(default=30, ge=1, le=300)
```

### OperatorOutput

Base class for operator outputs:

```python
class Output(OperatorOutput):
    result: Any
    success: bool
    message: str = ""
```

## Built-in Operators

### Core Operators

| Operator | Description | Use Case |
|----------|-------------|----------|
| `http-request` | Make HTTP calls | API integration |
| `json-transform` | JMESPath queries | Data extraction |
| `filter` | Filter collections | Data filtering |
| `loop` | Iterate over items | Batch processing |
| `schema-validate` | JSON Schema validation | Input validation |
| `variable-set` | Set context variables | State management |
| `logger` | Emit logs | Debugging |

### Control Flow (see [Control Flow](control-flow.md))

| Operator | Description |
|----------|-------------|
| `conditional` | If/else branching |
| `foreach` | Loop iteration |
| `trycatch` | Error handling |
| `router` | Switch/case routing |
| `subpipeline` | Pipeline composition |
| `return` | Early exit |

## Example: HTTP Request Operator

From `lab/flowmason_lab/operators/core/http_request.py`:

```python
@operator(
    name="http-request",
    description="Make HTTP requests to external APIs",
    category="integration",
    icon="globe",
    color="#3B82F6",
    timeout=30
)
class HttpRequestOperator:
    class Input(OperatorInput):
        url: str = Field(description="Request URL")
        method: str = Field(default="GET", description="HTTP method")
        headers: Dict[str, str] = Field(default_factory=dict)
        body: Optional[Dict[str, Any]] = Field(default=None)
        timeout: int = Field(default=30, ge=1, le=300)

    class Output(OperatorOutput):
        status_code: int
        headers: Dict[str, str]
        body: Any
        elapsed_ms: int
        success: bool

    async def execute(self, input: Input, context) -> Output:
        import httpx

        async with httpx.AsyncClient() as client:
            start = time.time()
            response = await client.request(
                method=input.method,
                url=input.url,
                headers=input.headers,
                json=input.body,
                timeout=input.timeout
            )
            elapsed = int((time.time() - start) * 1000)

        return self.Output(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            elapsed_ms=elapsed,
            success=response.is_success
        )
```

## Example: JSON Transform Operator

```python
@operator(
    name="json-transform",
    description="Transform JSON using JMESPath expressions",
    category="transform",
    icon="braces"
)
class JsonTransformOperator:
    class Input(OperatorInput):
        data: Any = Field(description="Input data")
        expression: str = Field(description="JMESPath expression")

    class Output(OperatorOutput):
        result: Any = Field(description="Transformed result")

    async def execute(self, input: Input, context) -> Output:
        import jmespath
        result = jmespath.search(input.expression, input.data)
        return self.Output(result=result)
```

## Operators vs Nodes

| Aspect | Operator | Node |
|--------|----------|------|
| LLM Required | No | Yes |
| Deterministic | Yes | No |
| Default Timeout | 30s | 60s |
| Retries | Not applicable | 3 by default |
| Use Case | Data transformation | AI tasks |
| Default Color | Blue | Purple |

## Best Practices

1. **Keep it simple** - Operators should do one thing well
2. **Handle errors** - Network calls can fail
3. **Validate inputs** - Use Field constraints
4. **Return useful metadata** - Include timing, counts, etc.
5. **Use async** - For I/O operations like HTTP calls
6. **Consider timeouts** - Set appropriate limits
