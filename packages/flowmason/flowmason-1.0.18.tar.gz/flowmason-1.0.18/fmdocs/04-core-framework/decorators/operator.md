# @operator Decorator

The `@operator` decorator creates deterministic, non-AI components for data transformation and utility operations.

## Basic Usage

```python
from flowmason_core import operator, BaseOperator, OperatorInput, OperatorOutput, Context
from pydantic import Field
from typing import Any, Dict

@operator(
    name="json-transform",
    description="Transform JSON data using JMESPath expressions",
    category="transform",
)
class JsonTransformOperator(BaseOperator):
    class Input(OperatorInput):
        data: Any = Field(description="Input data to transform")
        expression: str = Field(description="JMESPath expression")

    class Output(OperatorOutput):
        result: Any

    async def execute(self, input: Input, context: Context) -> Output:
        import jmespath
        result = jmespath.search(input.expression, input.data)
        return self.Output(result=result)
```

## Decorator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | Required | Unique component name |
| `description` | `str` | Required | Human-readable description |
| `category` | `str` | `"general"` | Component category |
| `tags` | `list[str]` | `[]` | Searchable tags |
| `timeout` | `int` | `30` | Execution timeout (seconds) |
| `max_retries` | `int` | `0` | Retries (usually 0 for deterministic ops) |

## Key Differences from @node

| Aspect | @node | @operator |
|--------|-------|-----------|
| **Purpose** | AI/LLM operations | Deterministic transformations |
| **Default Timeout** | 60s | 30s |
| **Default Retries** | 3 | 0 |
| **LLM Access** | Yes | Not recommended |
| **Idempotent** | May vary | Should be |

## Full Example

```python
from flowmason_core import operator, BaseOperator, OperatorInput, OperatorOutput, Context
from pydantic import Field
from typing import Any, Dict, List, Optional
import httpx

@operator(
    name="http-request",
    description="Make HTTP requests to external APIs",
    category="http",
    tags=["http", "api", "fetch"],
    timeout=60,  # Allow longer for network ops
)
class HttpRequestOperator(BaseOperator):
    """
    Make HTTP requests with configurable method, headers, and body.

    Supports GET, POST, PUT, DELETE methods with JSON payloads.
    """

    class Input(OperatorInput):
        url: str = Field(description="Request URL")
        method: str = Field(
            default="GET",
            pattern="^(GET|POST|PUT|DELETE|PATCH)$",
            description="HTTP method"
        )
        headers: Dict[str, str] = Field(
            default_factory=dict,
            description="Request headers"
        )
        body: Optional[Any] = Field(
            default=None,
            description="Request body (JSON)"
        )
        timeout: int = Field(
            default=30,
            ge=1,
            le=300,
            description="Request timeout in seconds"
        )

    class Output(OperatorOutput):
        status_code: int
        body: Any
        headers: Dict[str, str]
        elapsed_ms: float

    async def execute(self, input: Input, context: Context) -> Output:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=input.method,
                url=input.url,
                headers=input.headers,
                json=input.body if input.body else None,
                timeout=input.timeout,
            )

            # Parse response body
            try:
                body = response.json()
            except:
                body = response.text

            return self.Output(
                status_code=response.status_code,
                body=body,
                headers=dict(response.headers),
                elapsed_ms=response.elapsed.total_seconds() * 1000,
            )
```

## Common Operator Patterns

### Data Filtering

```python
@operator(
    name="filter",
    description="Filter items based on condition",
    category="transform",
)
class FilterOperator(BaseOperator):
    class Input(OperatorInput):
        items: List[Any]
        condition: str = Field(description="Python expression using 'item'")

    class Output(OperatorOutput):
        result: List[Any]
        filtered_count: int

    async def execute(self, input: Input, context: Context) -> Output:
        result = []
        for item in input.items:
            # Safe eval with limited scope
            if eval(input.condition, {"item": item, "len": len, "str": str}):
                result.append(item)

        return self.Output(
            result=result,
            filtered_count=len(input.items) - len(result)
        )
```

### JSON Schema Validation

```python
@operator(
    name="schema-validate",
    description="Validate data against JSON Schema",
    category="validation",
)
class SchemaValidateOperator(BaseOperator):
    class Input(OperatorInput):
        data: Any
        schema: Dict[str, Any]

    class Output(OperatorOutput):
        valid: bool
        errors: List[str]

    async def execute(self, input: Input, context: Context) -> Output:
        from jsonschema import validate, ValidationError, Draft7Validator

        validator = Draft7Validator(input.schema)
        errors = []

        for error in validator.iter_errors(input.data):
            errors.append(f"{error.json_path}: {error.message}")

        return self.Output(
            valid=len(errors) == 0,
            errors=errors
        )
```

### Variable Setting

```python
@operator(
    name="variable-set",
    description="Set context variables for use in later stages",
    category="utility",
)
class VariableSetOperator(BaseOperator):
    class Input(OperatorInput):
        variables: Dict[str, Any] = Field(
            description="Variables to set in context"
        )

    class Output(OperatorOutput):
        set_variables: List[str]

    async def execute(self, input: Input, context: Context) -> Output:
        for key, value in input.variables.items():
            context.variables[key] = value

        return self.Output(set_variables=list(input.variables.keys()))
```

### Logging

```python
@operator(
    name="logger",
    description="Log messages for debugging and observability",
    category="utility",
)
class LoggerOperator(BaseOperator):
    class Input(OperatorInput):
        message: str
        level: str = Field(
            default="info",
            pattern="^(debug|info|warning|error)$"
        )
        data: Optional[Any] = None

    class Output(OperatorOutput):
        logged: bool

    async def execute(self, input: Input, context: Context) -> Output:
        context.log(input.message, level=input.level, data=input.data)
        return self.Output(logged=True)
```

## Using in Pipelines

```json
{
  "stages": [
    {
      "id": "fetch",
      "component_type": "http-request",
      "config": {
        "url": "https://api.example.com/data",
        "method": "GET",
        "headers": {
          "Authorization": "Bearer {{input.api_key}}"
        }
      }
    },
    {
      "id": "transform",
      "component_type": "json-transform",
      "depends_on": ["fetch"],
      "config": {
        "data": "{{fetch.output.body}}",
        "expression": "items[?active==`true`].{name: name, id: id}"
      }
    },
    {
      "id": "validate",
      "component_type": "schema-validate",
      "depends_on": ["transform"],
      "config": {
        "data": "{{transform.output.result}}",
        "schema": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "id"]
          }
        }
      }
    }
  ]
}
```

## Error Handling

```python
from flowmason_core import FlowMasonError, ErrorType

async def execute(self, input: Input, context: Context) -> Output:
    if not input.url.startswith(("http://", "https://")):
        raise FlowMasonError(
            error_type=ErrorType.VALIDATION,
            message="Invalid URL scheme",
            recoverable=False,
        )

    try:
        # ... operation
        pass
    except httpx.TimeoutException:
        raise FlowMasonError(
            error_type=ErrorType.CONNECTIVITY,
            message="Request timed out",
            recoverable=True,  # Can be retried
        )
```

## Best Practices

1. **Idempotency**: Operators should produce the same output for the same input
2. **No Side Effects**: Avoid modifying external state when possible
3. **Fast Execution**: Keep operators lightweight (use @node for heavy operations)
4. **Clear Errors**: Provide descriptive error messages
5. **Type Safety**: Use Pydantic validation for inputs

## See Also

- [Nodes](node.md) - AI-powered components
- [Control Flow](control-flow.md) - Flow control components
- [Concepts: Operators](../../03-concepts/operators.md) - Operator concepts
