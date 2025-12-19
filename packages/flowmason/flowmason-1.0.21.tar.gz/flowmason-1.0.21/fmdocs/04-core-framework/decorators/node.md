# @node Decorator

The `@node` decorator creates AI-powered components that require LLM providers.

## Basic Usage

```python
from flowmason_core import node, BaseNode, NodeInput, NodeOutput, Context
from pydantic import Field
from typing import Optional, Dict

@node(
    name="summarizer",
    description="Summarize text content",
    category="text",
)
class SummarizerNode(BaseNode):
    class Input(NodeInput):
        text: str = Field(description="Text to summarize")
        max_length: int = Field(default=200, description="Maximum summary length")
        style: str = Field(default="concise", description="Summary style")

    class Output(NodeOutput):
        summary: str
        word_count: int

    async def execute(self, input: Input, context: Context) -> Output:
        response = await context.llm.generate(
            prompt=f"Summarize the following text in {input.max_length} words or less. Style: {input.style}\n\n{input.text}",
            system="You are a professional summarizer.",
            temperature=0.3,
        )
        summary = response.text
        return self.Output(
            summary=summary,
            word_count=len(summary.split())
        )
```

## Decorator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | Required | Unique component name |
| `description` | `str` | Required | Human-readable description |
| `category` | `str` | `"general"` | Component category for organization |
| `tags` | `list[str]` | `[]` | Searchable tags |
| `timeout` | `int` | `60` | Execution timeout in seconds |
| `max_retries` | `int` | `3` | Maximum retry attempts |
| `retry_delay` | `float` | `1.0` | Initial delay between retries |
| `retry_backoff` | `float` | `2.0` | Backoff multiplier for retries |
| `retryable_errors` | `list[ErrorType]` | `[TIMEOUT, PROVIDER]` | Errors that trigger retry |
| `recommended_providers` | `dict` | `{}` | Recommended LLM providers and models |

## Full Example with All Options

```python
from flowmason_core import (
    node, BaseNode, NodeInput, NodeOutput, Context, ErrorType
)
from pydantic import Field
from typing import Optional, Dict, List

@node(
    name="content-generator",
    description="Generate content based on prompts with quality controls",
    category="generation",
    tags=["content", "llm", "creative"],
    timeout=120,  # 2 minutes
    max_retries=3,
    retry_delay=2.0,
    retry_backoff=2.0,
    retryable_errors=[ErrorType.TIMEOUT, ErrorType.PROVIDER],
    recommended_providers={
        "anthropic": ["claude-sonnet-4-20250514", "claude-3-haiku-20240307"],
        "openai": ["gpt-4o", "gpt-4o-mini"],
    }
)
class ContentGeneratorNode(BaseNode):
    """
    Generates content with configurable creativity and length.

    Supports multiple content types and quality validation.
    """

    class Input(NodeInput):
        prompt: str = Field(
            description="The content generation prompt"
        )
        content_type: str = Field(
            default="article",
            description="Type of content to generate"
        )
        tone: str = Field(
            default="professional",
            description="Writing tone"
        )
        max_tokens: int = Field(
            default=1024,
            ge=1,
            le=4096,
            description="Maximum output tokens"
        )
        temperature: float = Field(
            default=0.7,
            ge=0.0,
            le=2.0,
            description="Creativity level (0=deterministic, 2=creative)"
        )
        system_prompt: Optional[str] = Field(
            default=None,
            description="Custom system prompt override"
        )

    class Output(NodeOutput):
        content: str
        token_count: int
        model_used: str
        metadata: Dict[str, any]

    async def execute(self, input: Input, context: Context) -> Output:
        # Build system prompt
        system = input.system_prompt or f"""You are a {input.tone} content writer.
Generate {input.content_type} content based on the user's prompt.
Be engaging and well-structured."""

        # Generate content
        response = await context.llm.generate(
            prompt=input.prompt,
            system=system,
            temperature=input.temperature,
            max_tokens=input.max_tokens,
        )

        return self.Output(
            content=response.text,
            token_count=response.usage.get("output_tokens", 0),
            model_used=response.model,
            metadata={
                "content_type": input.content_type,
                "tone": input.tone,
                "finish_reason": response.finish_reason,
            }
        )
```

## The Context Object

The `context` parameter provides access to runtime services:

```python
async def execute(self, input: Input, context: Context) -> Output:
    # LLM access
    response = await context.llm.generate(prompt="...", system="...")

    # Streaming (if supported)
    async for chunk in context.llm.stream_async(prompt="..."):
        # Process streaming tokens
        pass

    # Run ID for tracking
    run_id = context.run_id

    # Stage ID
    stage_id = context.stage_id

    # Access variables from previous stages
    previous_output = context.variables.get("previous_stage.output")

    # Custom logging
    context.log("Processing started", level="info")
```

## LLM Provider Interface

The `context.llm` provides these methods:

### generate()

```python
response = await context.llm.generate(
    prompt="User message",
    system="System instructions",
    model="claude-sonnet-4-20250514",  # Optional, uses default
    temperature=0.7,
    max_tokens=1024,
    stop_sequences=["END"],  # Optional
)

# Response object
response.text        # Generated text
response.model       # Model used
response.usage       # {"input_tokens": N, "output_tokens": N}
response.finish_reason  # "end_turn", "max_tokens", etc.
```

### stream_async()

```python
full_response = ""
async for chunk in context.llm.stream_async(
    prompt="User message",
    system="System instructions",
    temperature=0.7,
):
    full_response += chunk
    # Process each token as it arrives
```

## Input/Output Types

### Built-in Field Types

```python
from pydantic import Field
from typing import Optional, List, Dict, Any, Union

class Input(NodeInput):
    # Required string
    text: str

    # Optional with default
    language: str = "en"

    # With description and validation
    count: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of items"
    )

    # Optional field
    metadata: Optional[Dict[str, Any]] = None

    # List of items
    tags: List[str] = Field(default_factory=list)

    # Union types
    source: Union[str, List[str]] = Field(description="Single URL or list of URLs")
```

### Output Types

```python
class Output(NodeOutput):
    # Simple types
    result: str
    count: int
    score: float
    success: bool

    # Complex types
    items: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    # Optional
    error: Optional[str] = None
```

## Error Handling

```python
from flowmason_core import FlowMasonError, ErrorType

async def execute(self, input: Input, context: Context) -> Output:
    try:
        response = await context.llm.generate(prompt=input.prompt)
        return self.Output(content=response.text)
    except Exception as e:
        # Raise typed error for flow control
        raise FlowMasonError(
            error_type=ErrorType.COMPONENT,
            message=f"Generation failed: {str(e)}",
            recoverable=True,
            details={"prompt_length": len(input.prompt)}
        )
```

### Error Types

| Type | When to Use |
|------|------------|
| `VALIDATION` | Input validation failures |
| `COMPONENT` | Component-specific errors |
| `PROVIDER` | LLM provider errors (retryable) |
| `TIMEOUT` | Execution timeout (retryable) |
| `CONFIGURATION` | Configuration errors |
| `CONNECTIVITY` | Network errors |

## Using in Pipelines

```json
{
  "id": "generate_content",
  "component_type": "content-generator",
  "config": {
    "prompt": "Write about {{input.topic}}",
    "content_type": "blog_post",
    "tone": "casual",
    "temperature": 0.8,
    "max_tokens": 2000
  }
}
```

## Best Practices

1. **Clear Descriptions**: Document inputs/outputs thoroughly for IDE support
2. **Sensible Defaults**: Provide defaults that work for common cases
3. **Validation**: Use Pydantic constraints (`ge`, `le`, `regex`, etc.)
4. **Error Handling**: Catch and wrap errors with appropriate types
5. **Timeouts**: Set realistic timeouts for LLM operations
6. **Temperature**: Match temperature to task (low for facts, high for creativity)

## See Also

- [Operators](operator.md) - Non-AI components
- [Control Flow](control-flow.md) - Flow control components
- [Concepts: Nodes](../../03-concepts/nodes.md) - Node concepts
