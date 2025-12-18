# Nodes

## What is a Node?

A **Node** is an AI-powered component that requires an LLM (Large Language Model) to execute. Nodes perform intelligent tasks like text generation, summarization, analysis, and decision-making.

## Characteristics

| Property | Value |
|----------|-------|
| Decorator | `@node` |
| Requires LLM | Yes |
| Default timeout | 60 seconds |
| Default retries | 3 |
| Deterministic | No (LLM responses vary) |

## Creating a Node

```python
from flowmason_core.core import node, Field
from flowmason_core.core.types import NodeInput, NodeOutput

@node(
    name="summarize-text",
    description="Summarize text using an LLM",
    category="text",
    recommended_providers={"anthropic": ["claude-sonnet-4-20250514"]},
    timeout=60,
    max_retries=3
)
class SummarizeTextNode:
    """Summarizes input text to a specified length."""

    class Input(NodeInput):
        text: str = Field(description="Text to summarize")
        max_length: int = Field(default=100, description="Maximum words in summary")
        style: str = Field(default="concise", description="Summary style")

    class Output(NodeOutput):
        summary: str = Field(description="Generated summary")
        word_count: int = Field(description="Number of words in summary")

    async def execute(self, input: Input, context) -> Output:
        prompt = f"""Summarize the following text in {input.max_length} words or less.
Style: {input.style}

Text:
{input.text}

Summary:"""

        response = await context.llm.generate(
            prompt=prompt,
            max_tokens=input.max_length * 2
        )

        summary = response.text.strip()
        word_count = len(summary.split())

        return self.Output(summary=summary, word_count=word_count)
```

## Decorator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Unique identifier (kebab-case) |
| `description` | str | Required | Human-readable description |
| `category` | str | `"general"` | Component category |
| `version` | str | `"1.0.0"` | Semantic version |
| `icon` | str | `"cpu"` | Lucide icon name |
| `color` | str | `"#8B5CF6"` | Hex color (purple default) |
| `timeout` | int | `60` | Execution timeout in seconds |
| `max_retries` | int | `3` | Maximum retry attempts |
| `recommended_providers` | dict | `{}` | Provider → models mapping |
| `default_provider` | str | `None` | Default LLM provider |
| `required_capabilities` | list | `[]` | Required LLM capabilities |

## Input/Output Classes

### NodeInput

Base class for node inputs:

```python
class Input(NodeInput):
    # Required field
    text: str

    # Optional with default
    max_length: int = 100

    # With Field metadata
    temperature: float = Field(
        default=0.7,
        ge=0,
        le=2,
        description="LLM temperature"
    )
```

**Validation:**
- `extra="forbid"` - No extra fields allowed
- Validates on assignment
- Strips whitespace from strings

### NodeOutput

Base class for node outputs:

```python
class Output(NodeOutput):
    summary: str
    confidence: float
    metadata: dict = {}
```

**Validation:**
- `extra="allow"` - Extra fields allowed (flexible for LLM responses)

## Context Object

The `context` parameter provides:

```python
async def execute(self, input: Input, context) -> Output:
    # LLM access
    response = await context.llm.generate(prompt="...")
    response = await context.llm.stream(prompt="...")

    # Run metadata
    run_id = context.run_id
    stage_id = context.stage_id

    # Upstream outputs (in pipeline)
    prev_output = context.upstream_outputs.get("previous_stage")
```

## Built-in Nodes

| Node | Description |
|------|-------------|
| `generator` | Create content from prompts |
| `critic` | Evaluate and provide feedback |
| `improver` | Refine content based on criteria |
| `selector` | Choose best option from set |
| `synthesizer` | Combine multiple inputs |

## Best Practices

1. **Clear descriptions** - Help users understand what the node does
2. **Sensible defaults** - Make common cases easy
3. **Input validation** - Use Field constraints
4. **Meaningful outputs** - Include metadata when useful
5. **Handle errors** - LLM calls can fail
6. **Consider tokens** - Estimate token usage for cost

## Example: Generator Node

From `lab/flowmason_lab/nodes/core/generator.py`:

```python
@node(
    name="generator",
    description="Generate content using an LLM provider",
    category="core",
    icon="sparkles",
    color="#8B5CF6",
    recommended_providers={
        "anthropic": ["claude-sonnet-4-20250514"],
        "openai": ["gpt-4o"]
    },
    default_provider="anthropic"
)
class GeneratorNode:
    class Input(NodeInput):
        prompt: str = Field(description="The prompt to send to the LLM")
        system_prompt: Optional[str] = Field(default=None)
        temperature: float = Field(default=0.7, ge=0, le=2)
        max_tokens: int = Field(default=1024, ge=1)

    class Output(NodeOutput):
        content: str = Field(description="Generated content")
        usage: Dict[str, int] = Field(description="Token usage")

    async def execute(self, input: Input, context) -> Output:
        response = await context.llm.generate(
            prompt=input.prompt,
            system_prompt=input.system_prompt,
            temperature=input.temperature,
            max_tokens=input.max_tokens
        )
        return self.Output(
            content=response.text,
            usage=response.usage
        )
```
