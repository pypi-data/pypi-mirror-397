# FlowMason Package Format Specification

**Version:** 1.0.0

This document specifies the format for FlowMason component packages (`.fmpkg` files).

## Overview

FlowMason packages are ZIP archives with the `.fmpkg` extension. Each package contains a single component (node or operator) along with its metadata and dependencies.

## File Structure

```
my-component-1.0.0.fmpkg
├── flowmason-package.json    # Required: Package manifest
├── index.py                  # Required: Component entry point
├── requirements.txt          # Optional: Python dependencies
└── assets/                   # Optional: Additional files
    ├── prompts/
    └── schemas/
```

## Package Manifest (`flowmason-package.json`)

The manifest file contains all metadata about the package.

### Required Fields

```json
{
  "name": "my-component",
  "version": "1.0.0",
  "description": "A brief description of what this component does",
  "type": "node",
  "entry_point": "index.py",
  "author": {
    "name": "Author Name",
    "email": "author@example.com"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique component identifier (lowercase, hyphens allowed) |
| `version` | string | Semantic version (e.g., "1.0.0", "2.1.3") |
| `description` | string | Human-readable description |
| `type` | string | Either "node" or "operator" |
| `entry_point` | string | Path to the Python file containing the component |
| `author` | object | Author information |

### Optional Fields

```json
{
  "name": "my-component",
  "version": "1.0.0",
  "description": "Description",
  "type": "node",
  "entry_point": "index.py",
  "author": {
    "name": "Author Name",
    "email": "author@example.com"
  },
  "license": "MIT",
  "category": "nlp",
  "tags": ["text", "generation", "ai"],
  "requires_llm": true,
  "timeout_seconds": 120,
  "dependencies": ["numpy>=1.20.0", "requests>=2.25.0"],
  "flowmason_version": ">=0.1.0"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `license` | string | "MIT" | License identifier |
| `category` | string | "uncategorized" | Component category for UI grouping |
| `tags` | string[] | [] | Tags for search/filtering |
| `requires_llm` | boolean | false (operators), true (nodes) | Whether component needs LLM access |
| `timeout_seconds` | integer | 60 | Maximum execution time |
| `dependencies` | string[] | [] | Python package requirements |
| `flowmason_version` | string | "*" | Compatible FlowMason versions |

## Component Entry Point

The entry point file must contain a class decorated with `@node` or `@operator`.

### Node Component Example

```python
"""Generator Node - generates text from prompts."""

from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node


@node(
    name="generator",
    category="core",
    description="Generate text from a prompt using an LLM",
    icon="sparkles",
    color="#8B5CF6",
    version="1.0.0",
    author="FlowMason",
    tags=["text", "generation", "llm"],
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.7,
        },
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.7,
        }
    },
    default_provider="anthropic",
)
class GeneratorNode:
    """Generates text content from prompts."""

    class Input(NodeInput):
        prompt: str = Field(description="The prompt to generate from")
        system_prompt: str = Field(default="", description="Optional system prompt")
        max_tokens: int = Field(default=1000, ge=1, le=100000, description="Max tokens")
        temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")

    class Output(NodeOutput):
        content: str = Field(description="Generated content")
        tokens_used: int = Field(default=0, description="Tokens consumed")
        model: str = Field(default="", description="Model used")

    async def execute(self, input: Input, context) -> Output:
        # Implementation here
        response = await context.llm.generate(
            prompt=input.prompt,
            system_prompt=input.system_prompt,
            max_tokens=input.max_tokens,
            temperature=input.temperature,
        )

        return self.Output(
            content=response.content,
            tokens_used=response.usage.total_tokens,
            model=response.model,
        )
```

### Operator Component Example

```python
"""JSON Transform Operator - transforms JSON data."""

from typing import Any, Dict, List, Optional
from flowmason_core.core.types import OperatorInput, OperatorOutput, Field
from flowmason_core.core.decorators import operator


@operator(
    name="json_transform",
    category="transform",
    description="Transform JSON data using field mappings",
    icon="braces",
    color="#3B82F6",
    version="1.0.0",
    author="FlowMason",
    tags=["json", "transform", "data"],
)
class JsonTransformOperator:
    """Transforms JSON data structures."""

    class Input(OperatorInput):
        data: Any = Field(description="Input data to transform")
        mappings: Dict[str, str] = Field(
            default_factory=dict,
            description="Field mappings: {output_field: input_path}"
        )

    class Output(OperatorOutput):
        result: Any = Field(description="Transformed data")

    async def execute(self, input: Input, context) -> Output:
        result = {}
        for output_key, input_path in input.mappings.items():
            value = self._get_nested(input.data, input_path)
            result[output_key] = value

        return self.Output(result=result)

    def _get_nested(self, data: Any, path: str) -> Any:
        """Get value at nested path like 'user.profile.name'."""
        parts = path.split('.')
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current
```

## Decorator Parameters

### `@node` Decorator

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | Yes | Unique component type identifier |
| `category` | str | Yes | Category for grouping |
| `description` | str | Yes | Human-readable description |
| `version` | str | Yes | Component version |
| `author` | str | Yes | Author name |
| `icon` | str | No | Lucide icon name |
| `color` | str | No | Hex color for UI |
| `tags` | list | No | Search tags |
| `recommended_providers` | dict | No | LLM provider configs |
| `default_provider` | str | No | Default LLM provider |
| `required_capabilities` | list | No | Required LLM capabilities |
| `timeout_seconds` | int | No | Execution timeout |

### `@operator` Decorator

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | Yes | Unique component type identifier |
| `category` | str | Yes | Category for grouping |
| `description` | str | Yes | Human-readable description |
| `version` | str | Yes | Component version |
| `author` | str | Yes | Author name |
| `icon` | str | No | Lucide icon name |
| `color` | str | No | Hex color for UI |
| `tags` | list | No | Search tags |
| `timeout_seconds` | int | No | Execution timeout |

## Input/Output Schema

Input and Output classes define the component's interface using Pydantic models.

### Field Types

```python
from typing import Any, Dict, List, Optional
from flowmason_core.core.types import Field

class Input(NodeInput):
    # Basic types
    text: str = Field(description="Text input")
    count: int = Field(default=10, description="Number of items")
    rate: float = Field(default=0.5, ge=0.0, le=1.0, description="Rate value")
    enabled: bool = Field(default=True, description="Feature flag")

    # Complex types
    items: List[str] = Field(default_factory=list, description="List of items")
    config: Dict[str, Any] = Field(default_factory=dict, description="Config dict")

    # Optional types
    override: Optional[str] = Field(default=None, description="Optional override")

    # Enums
    mode: str = Field(default="fast", description="Mode: fast or slow")
```

### Field Constraints

```python
# String constraints
name: str = Field(min_length=1, max_length=100, description="Name")

# Numeric constraints
temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
max_tokens: int = Field(default=1000, ge=1, le=100000, description="Max tokens")

# Enum constraint
status: str = Field(description="Status", json_schema_extra={"enum": ["active", "inactive"]})
```

## Execution Context

The `context` parameter provides runtime services:

```python
async def execute(self, input: Input, context) -> Output:
    # Access run information
    run_id = context.run_id
    pipeline_id = context.pipeline_id

    # For nodes: access LLM
    if context.llm:
        response = await context.llm.generate(prompt=input.prompt)

    # Access environment variables
    api_key = context.get_env("API_KEY")

    # Logging
    context.log.info("Processing input")

    return self.Output(...)
```

## Building Packages

Use the package builder script:

```bash
# Build a single package
PYTHONPATH=core:lab python scripts/package_builder.py path/to/component.py

# Build all core packages
PYTHONPATH=core:lab python scripts/package_builder.py all
```

Output packages are placed in `dist/packages/`.

## Installing Packages

Packages are installed by copying to the packages directory and registering:

```python
from flowmason_core.registry import ComponentRegistry

registry = ComponentRegistry("/path/to/packages")
registry.register_package("/path/to/my-component-1.0.0.fmpkg")
```

Or via the Studio API:

```bash
curl -X POST http://localhost:8999/api/v1/registry/deploy \
  -F "package=@my-component-1.0.0.fmpkg"
```

## Version Compatibility

Package versions follow semantic versioning:

- **MAJOR**: Breaking changes to Input/Output schemas
- **MINOR**: New optional fields or features
- **PATCH**: Bug fixes without schema changes

When a pipeline references a component, it should specify version constraints:

```json
{
  "stages": [
    {
      "id": "gen",
      "type": "generator@^1.0.0",
      "input_mapping": {}
    }
  ]
}
```

## Best Practices

1. **Keep components focused** - One component, one purpose
2. **Document all fields** - Use `description` on every Field
3. **Provide defaults** - Make optional fields have sensible defaults
4. **Handle errors gracefully** - Raise descriptive exceptions
5. **Test independently** - Components should be testable in isolation
6. **Version appropriately** - Follow semver for schema changes
