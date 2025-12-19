# Tutorial 5: Working with Components

This tutorial covers creating custom components (nodes and operators) and using built-in FlowMason components.

## What You'll Learn

- Understanding the three component types
- Creating custom AI nodes
- Creating custom operators
- Using built-in control flow components
- Registering and packaging components

## Component Types Overview

FlowMason has three component types:

| Type | Decorator | Purpose | Example |
|------|-----------|---------|---------|
| **Node** | `@node` | AI-powered operations | Text generation, analysis |
| **Operator** | `@operator` | Deterministic utilities | HTTP requests, transforms |
| **Control Flow** | `@control_flow` | Execution flow control | Conditionals, loops |

## Part 1: Creating a Custom Node

Nodes are AI-powered components that use LLM providers.

### Step 1: Create the Node File

Create `components/nodes/keyword_extractor.py`:

```python
from flowmason_core import (
    node, BaseNode, NodeInput, NodeOutput, Context
)
from pydantic import Field
from typing import List


@node(
    name="keyword-extractor",
    description="Extract keywords from text using AI",
    category="analysis",
    recommended_providers={"anthropic": ["claude-sonnet-4-20250514"]},
    timeout=60,
    max_retries=3
)
class KeywordExtractorNode(BaseNode):
    """Extracts relevant keywords from text content."""

    class Input(NodeInput):
        text: str = Field(
            description="Text to extract keywords from"
        )
        max_keywords: int = Field(
            default=10,
            ge=1,
            le=50,
            description="Maximum number of keywords to extract"
        )
        include_scores: bool = Field(
            default=False,
            description="Include relevance scores for keywords"
        )

    class Output(NodeOutput):
        keywords: List[str] = Field(
            description="Extracted keywords"
        )
        scores: List[float] = Field(
            default=[],
            description="Relevance scores (if requested)"
        )

    async def execute(self, input: Input, context: Context) -> Output:
        # Build the prompt
        prompt = f"""Extract the {input.max_keywords} most important keywords
from the following text. Return them as a JSON array.

Text:
{input.text}

{"Include a relevance score (0-1) for each keyword." if input.include_scores else ""}

Return format:
{{"keywords": ["word1", "word2"], "scores": [0.9, 0.8]}}
"""

        # Call the LLM
        response = await context.llm.generate(
            system_prompt="You are a keyword extraction expert. Always return valid JSON.",
            prompt=prompt,
            temperature=0.3,
            max_tokens=500
        )

        # Parse the response
        import json
        result = json.loads(response.content)

        return self.Output(
            keywords=result["keywords"][:input.max_keywords],
            scores=result.get("scores", []) if input.include_scores else []
        )
```

### Step 2: Node Decorator Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | Yes | Unique component name |
| `description` | str | Yes | Human-readable description |
| `category` | str | No | Category for organization |
| `recommended_providers` | dict | No | Suggested LLM providers/models |
| `timeout` | int | No | Execution timeout in seconds (default: 60) |
| `max_retries` | int | No | Maximum retry attempts (default: 3) |

### Step 3: Use the Node in a Pipeline

```json
{
  "id": "extract_keywords",
  "component_type": "keyword-extractor",
  "depends_on": ["fetch_content"],
  "config": {
    "text": "{{fetch_content.output.body}}",
    "max_keywords": 15,
    "include_scores": true
  }
}
```

## Part 2: Creating a Custom Operator

Operators are deterministic, non-AI components.

### Step 1: Create the Operator File

Create `components/operators/text_cleaner.py`:

```python
from flowmason_core import (
    operator, BaseOperator, OperatorInput, OperatorOutput, Context
)
from pydantic import Field
import re
from typing import Optional


@operator(
    name="text-cleaner",
    description="Clean and normalize text content",
    category="transform",
    timeout=30
)
class TextCleanerOperator(BaseOperator):
    """Removes HTML tags, extra whitespace, and normalizes text."""

    class Input(OperatorInput):
        text: str = Field(
            description="Text to clean"
        )
        remove_html: bool = Field(
            default=True,
            description="Remove HTML tags"
        )
        remove_urls: bool = Field(
            default=False,
            description="Remove URLs"
        )
        lowercase: bool = Field(
            default=False,
            description="Convert to lowercase"
        )
        max_length: Optional[int] = Field(
            default=None,
            description="Truncate to max length"
        )

    class Output(OperatorOutput):
        text: str = Field(
            description="Cleaned text"
        )
        original_length: int = Field(
            description="Original text length"
        )
        cleaned_length: int = Field(
            description="Cleaned text length"
        )

    async def execute(self, input: Input, context: Context) -> Output:
        text = input.text
        original_length = len(text)

        # Remove HTML tags
        if input.remove_html:
            text = re.sub(r'<[^>]+>', '', text)

        # Remove URLs
        if input.remove_urls:
            text = re.sub(r'https?://\S+', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Lowercase
        if input.lowercase:
            text = text.lower()

        # Truncate
        if input.max_length and len(text) > input.max_length:
            text = text[:input.max_length] + "..."

        return self.Output(
            text=text,
            original_length=original_length,
            cleaned_length=len(text)
        )
```

### Step 2: Operator Decorator Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | Yes | Unique component name |
| `description` | str | Yes | Human-readable description |
| `category` | str | No | Category for organization |
| `timeout` | int | No | Execution timeout in seconds (default: 30) |

### Step 3: Use the Operator in a Pipeline

```json
{
  "id": "clean_content",
  "component_type": "text-cleaner",
  "depends_on": ["fetch"],
  "config": {
    "text": "{{fetch.output.body}}",
    "remove_html": true,
    "remove_urls": true,
    "max_length": 10000
  }
}
```

## Part 3: Using Built-in Control Flow Components

FlowMason provides 6 built-in control flow components.

### Conditional (If/Else)

```json
{
  "id": "check_status",
  "component_type": "conditional",
  "depends_on": ["fetch"],
  "config": {
    "condition": "{{fetch.output.status_code}} == 200",
    "true_branch": "process_success",
    "false_branch": "handle_error"
  }
}
```

### Router (Switch/Case)

```json
{
  "id": "route_by_type",
  "component_type": "router",
  "depends_on": ["detect_type"],
  "config": {
    "value": "{{detect_type.output.content_type}}",
    "routes": {
      "text/html": "process_html",
      "application/json": "process_json",
      "text/plain": "process_text"
    },
    "default": "process_generic"
  }
}
```

### ForEach (Loop)

```json
{
  "id": "process_items",
  "component_type": "foreach",
  "depends_on": ["get_items"],
  "config": {
    "items": "{{get_items.output.items}}",
    "item_variable": "item",
    "stages": ["transform_item", "save_item"],
    "parallel": true,
    "max_concurrency": 5
  }
}
```

Inside loop stages, access the current item:
```json
{
  "id": "transform_item",
  "config": {
    "data": "{{item}}"
  }
}
```

### TryCatch (Error Handling)

```json
{
  "id": "safe_operation",
  "component_type": "trycatch",
  "config": {
    "try_stages": ["risky_fetch", "process"],
    "catch_stages": ["log_error", "use_fallback"],
    "finally_stages": ["cleanup"],
    "on_error": "continue"
  }
}
```

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

### SubPipeline (Composition)

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

### Return (Early Exit)

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

## Part 4: Built-in Operators

### HTTP Request

```json
{
  "id": "fetch_api",
  "component_type": "http-request",
  "config": {
    "url": "https://api.example.com/data",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{input.api_key}}"
    },
    "body": {
      "query": "{{input.search_term}}"
    },
    "timeout": 30
  }
}
```

### JSON Transform

```json
{
  "id": "extract_data",
  "component_type": "json-transform",
  "config": {
    "data": "{{fetch.output.body}}",
    "expression": "results[*].{name: name, id: id}"
  }
}
```

### Filter

```json
{
  "id": "filter_active",
  "component_type": "filter",
  "config": {
    "data": "{{items.output.list}}",
    "condition": "item.status == 'active'"
  }
}
```

### Schema Validate

```json
{
  "id": "validate_input",
  "component_type": "schema-validate",
  "config": {
    "data": "{{input}}",
    "schema": {
      "type": "object",
      "required": ["url"],
      "properties": {
        "url": { "type": "string", "format": "uri" }
      }
    }
  }
}
```

### Logger

```json
{
  "id": "log_progress",
  "component_type": "logger",
  "config": {
    "level": "info",
    "message": "Processing {{input.url}}",
    "data": {
      "timestamp": "{{context.timestamp}}",
      "run_id": "{{context.run_id}}"
    }
  }
}
```

## Part 5: Built-in AI Nodes

### Generator

```json
{
  "id": "generate_content",
  "component_type": "generator",
  "config": {
    "system_prompt": "You are a helpful assistant.",
    "prompt": "Write about {{input.topic}}",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

### Critic

```json
{
  "id": "evaluate_content",
  "component_type": "critic",
  "config": {
    "content": "{{generate.output.content}}",
    "criteria": ["accuracy", "clarity", "engagement"],
    "rubric": "Score each criterion 1-10 with explanation"
  }
}
```

### Improver

```json
{
  "id": "improve_content",
  "component_type": "improver",
  "config": {
    "content": "{{generate.output.content}}",
    "feedback": "{{critic.output.feedback}}",
    "instructions": "Address the feedback while maintaining the original tone"
  }
}
```

### Selector

```json
{
  "id": "select_best",
  "component_type": "selector",
  "config": {
    "options": "{{generate_variants.output.variants}}",
    "criteria": "Select the most engaging and accurate option",
    "return_reasoning": true
  }
}
```

### Synthesizer

```json
{
  "id": "combine_sources",
  "component_type": "synthesizer",
  "config": {
    "sources": [
      "{{source1.output.content}}",
      "{{source2.output.content}}"
    ],
    "instructions": "Combine into a coherent summary"
  }
}
```

## Part 6: Registering Components

### Project Configuration

In `flowmason.json`:

```json
{
  "components": {
    "include": [
      "components/**/*.py"
    ]
  }
}
```

### Verify Registration

```bash
# List all registered components
fm list --components

# Check specific component
fm validate components/nodes/keyword_extractor.py
```

### In VSCode

Components appear in the FlowMason sidebar under:
- COMPONENTS > Nodes > keyword-extractor
- COMPONENTS > Operators > text-cleaner

## Part 7: Packaging Components

### Create a Package

```bash
fm pack --output my-components-1.0.0.fmpkg
```

### Package Contents

```
my-components-1.0.0.fmpkg
├── manifest.json
├── components/
│   ├── nodes/
│   │   └── keyword_extractor.py
│   └── operators/
│       └── text_cleaner.py
└── README.md
```

### Install Package

```bash
fm install my-components-1.0.0.fmpkg
```

## Part 8: Testing Components

### Unit Test for Node

```python
import pytest
from components.nodes.keyword_extractor import KeywordExtractorNode

@pytest.mark.asyncio
async def test_keyword_extraction():
    node = KeywordExtractorNode()

    # Mock context with LLM
    context = MockContext(llm_response='{"keywords": ["test", "example"]}')

    input_data = node.Input(
        text="This is a test example text.",
        max_keywords=5
    )

    output = await node.execute(input_data, context)

    assert len(output.keywords) <= 5
    assert "test" in output.keywords
```

### Unit Test for Operator

```python
import pytest
from components.operators.text_cleaner import TextCleanerOperator

@pytest.mark.asyncio
async def test_text_cleaning():
    operator = TextCleanerOperator()

    input_data = operator.Input(
        text="<p>Hello  World</p>",
        remove_html=True
    )

    output = await operator.execute(input_data, None)

    assert output.text == "Hello World"
    assert output.cleaned_length < output.original_length
```

## Best Practices

### 1. Clear Input/Output Schemas

```python
class Input(NodeInput):
    text: str = Field(description="Input text to process")
    # Always include descriptions
```

### 2. Sensible Defaults

```python
max_keywords: int = Field(default=10, ge=1, le=50)
```

### 3. Proper Error Handling

```python
async def execute(self, input: Input, context: Context) -> Output:
    try:
        result = await self._do_work(input)
        return self.Output(result=result)
    except ValueError as e:
        raise ValidationError(f"Invalid input: {e}")
```

### 4. Logging for Debugging

```python
async def execute(self, input: Input, context: Context) -> Output:
    context.logger.info(f"Processing {len(input.text)} characters")
    # ... do work
    context.logger.debug(f"Found {len(keywords)} keywords")
```

### 5. Respect Timeouts

For long operations, check for cancellation:

```python
async def execute(self, input: Input, context: Context) -> Output:
    for item in items:
        if context.cancellation_token.is_cancelled:
            raise CancellationError("Operation cancelled")
        await self._process_item(item)
```

## Summary

You've learned to:
- Create custom AI nodes with the `@node` decorator
- Create custom operators with the `@operator` decorator
- Use built-in control flow components
- Work with built-in operators and nodes
- Register and package components
- Test components

## Next Steps

- Explore the [API Reference](../04-core-framework/decorators/node.md) for detailed decorator options
- Read about [Pipeline Patterns](../03-concepts/pipelines.md) for advanced composition
- Check [Testing Guide](./04-testing-pipelines.md) for comprehensive testing strategies
