# Python SDK

FlowMason provides a Python SDK for programmatic pipeline creation and execution.

## Installation

```bash
pip install flowmason
```

## Quick Start

```python
import asyncio
from flowmason_core import FlowMason

async def main():
    # Initialize with API keys from environment
    fm = FlowMason()

    # Run a pipeline from file
    result = await fm.run_pipeline_file(
        "./pipelines/my-pipeline.pipeline.json",
        {"query": "Hello, world!"}
    )

    print(result.output)

asyncio.run(main())
```

## Initialization

### Basic Setup

```python
from flowmason_core import FlowMason

# Auto-loads API keys from environment variables
fm = FlowMason()

# Or provide explicitly
fm = FlowMason(
    providers={
        "anthropic": "sk-ant-...",
        "openai": "sk-..."
    },
    default_provider="anthropic"
)
```

### Environment Variables

The SDK automatically loads from these environment variables:

| Variable | Provider |
|----------|----------|
| `ANTHROPIC_API_KEY` | Anthropic (Claude) |
| `OPENAI_API_KEY` | OpenAI (GPT) |
| `GOOGLE_API_KEY` | Google (Gemini) |
| `GROQ_API_KEY` | Groq |
| `PERPLEXITY_API_KEY` | Perplexity (Sonar) |

### Async Context Manager

```python
async with FlowMason() as fm:
    result = await fm.run_pipeline_file("./pipeline.json", {})
```

## Running Pipelines

### From File

```python
# Load and run in one step
result = await fm.run_pipeline_file(
    "./pipelines/my-pipeline.pipeline.json",
    {"topic": "AI Safety"}
)

# Or load first, run later
pipeline = fm.load_pipeline("./pipelines/my-pipeline.pipeline.json")
result = await pipeline.run({"topic": "AI Safety"})
```

### From Studio

Run pipelines stored in FlowMason Studio:

```python
result = await fm.run_from_studio(
    pipeline_id="abc123",
    input={"query": "Hello"},
    studio_url="http://localhost:8999"
)
```

### Inline Definition

Define pipelines programmatically:

```python
pipeline = fm.pipeline(
    name="Content Generator",
    stages=[
        fm.stage("generator",
            id="generate",
            config={"prompt": "Write about {{topic}}"}
        ),
        fm.stage("critic",
            id="review",
            config={"focus": "clarity"},
            depends_on=["generate"]
        ),
    ]
)

result = await pipeline.run({"topic": "Machine Learning"})
```

## Progress Callbacks

Track execution progress with async callbacks:

```python
async def on_start(stage_id, data):
    print(f"Starting: {stage_id}")

async def on_complete(stage_id, output):
    print(f"Completed: {stage_id}")
    print(f"Output: {output}")

async def on_error(stage_id, error):
    print(f"Error in {stage_id}: {error}")

result = await pipeline.run(
    {"topic": "AI"},
    on_stage_start=on_start,
    on_stage_complete=on_complete,
    on_stage_error=on_error
)
```

## Pipeline Result

```python
result = await pipeline.run({"topic": "AI"})

# Check success
if result.success:
    print(result.output)
else:
    print(f"Error: {result.error}")

# Access stage results
for stage_id, stage_result in result.stage_results.items():
    print(f"{stage_id}: {stage_result.output}")

# Usage metrics
print(f"Input tokens: {result.usage.input_tokens}")
print(f"Output tokens: {result.usage.output_tokens}")
print(f"Total cost: ${result.usage.total_cost_usd:.4f}")
```

## Components

### Loading Packages

```python
# Load all packages from a directory
fm.load_packages("./packages")

# Load a single package
fm.load_package("./packages/my-package.fmpkg")
```

### Listing Components

```python
# All components
components = fm.list_components()

# By category
ai_components = fm.list_components(category="ai")
```

### Component Info

```python
info = fm.get_component_info("generator")
print(f"Name: {info['name']}")
print(f"Description: {info['description']}")
print(f"Requires LLM: {info['requires_llm']}")
```

### Running Components Directly

```python
result = await fm.run_component(
    "generator",
    {"prompt": "Write a haiku about coding"}
)
print(result.output.content)
```

### Custom Components

Register custom components at runtime:

```python
from flowmason_core import node, NodeInput, NodeOutput, Field

@node(
    name="uppercase",
    description="Convert text to uppercase"
)
class UppercaseNode:
    class Input(NodeInput):
        text: str = Field(description="Text to convert")

    class Output(NodeOutput):
        result: str = Field(description="Uppercase text")

    async def execute(self, input, context):
        return self.Output(result=input.text.upper())

# Register with FlowMason
fm.register_component(UppercaseNode)

# Use in pipelines
result = await fm.run_component("uppercase", {"text": "hello"})
print(result.output.result)  # "HELLO"
```

## Validation

Validate pipelines before running:

```python
pipeline = fm.load_pipeline("./my-pipeline.pipeline.json")
errors = pipeline.validate()

if errors:
    for error in errors:
        print(f"Validation error: {error}")
else:
    result = await pipeline.run({})
```

## Trace IDs

For observability, pass trace IDs:

```python
import uuid

trace_id = str(uuid.uuid4())
result = await pipeline.run(
    {"query": "Hello"},
    trace_id=trace_id
)

# Use trace_id to correlate logs, metrics, etc.
```

## Error Handling

```python
try:
    result = await fm.run_pipeline_file("./pipeline.json", {})

    if not result.success:
        print(f"Pipeline failed: {result.error}")

except FileNotFoundError:
    print("Pipeline file not found")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Provider Information

```python
# Configured providers (with API keys)
print(fm.configured_providers)  # ['anthropic', 'openai']

# All available providers
print(fm.available_providers)  # ['anthropic', 'openai', 'google', 'groq', 'perplexity']
```

## Complete Example

```python
import asyncio
from flowmason_core import FlowMason, node, NodeInput, NodeOutput, Field

@node(name="formatter", category="utility")
class FormatterNode:
    class Input(NodeInput):
        text: str
        format: str = "uppercase"

    class Output(NodeOutput):
        result: str

    async def execute(self, input, context):
        if input.format == "uppercase":
            return self.Output(result=input.text.upper())
        elif input.format == "lowercase":
            return self.Output(result=input.text.lower())
        return self.Output(result=input.text)

async def main():
    async with FlowMason() as fm:
        # Register custom component
        fm.register_component(FormatterNode)

        # Define pipeline
        pipeline = fm.pipeline(
            name="Text Processor",
            stages=[
                fm.stage("generator",
                    id="generate",
                    config={"prompt": "Write a short greeting"}
                ),
                fm.stage("formatter",
                    id="format",
                    config={
                        "text": "{{stages.generate.output.content}}",
                        "format": "uppercase"
                    },
                    depends_on=["generate"]
                ),
            ]
        )

        # Run with progress tracking
        async def log_progress(stage_id, output):
            print(f"[{stage_id}] Done")

        result = await pipeline.run(
            {},
            on_stage_complete=log_progress
        )

        if result.success:
            print(f"\nFinal output: {result.output}")
        else:
            print(f"\nError: {result.error}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### FlowMason Class

| Method | Description |
|--------|-------------|
| `load_pipeline(path)` | Load pipeline from file |
| `run_pipeline_file(path, input)` | Load and run pipeline |
| `run_from_studio(id, input)` | Run pipeline from Studio |
| `pipeline(name, stages)` | Create inline pipeline |
| `stage(type, config)` | Create stage definition |
| `run_component(type, config)` | Run single component |
| `load_packages(path)` | Load component packages |
| `register_component(cls)` | Register custom component |
| `list_components(category)` | List available components |
| `get_component_info(type)` | Get component metadata |

### Pipeline Class

| Method | Description |
|--------|-------------|
| `run(input, callbacks)` | Execute the pipeline |
| `validate()` | Validate configuration |

### PipelineResult

| Property | Type | Description |
|----------|------|-------------|
| `success` | bool | Whether pipeline succeeded |
| `output` | dict | Final stage output |
| `stage_results` | dict | All stage results |
| `usage` | UsageMetrics | Token/cost metrics |
| `error` | str | Error message if failed |
| `final_output` | any | Convenience accessor |
