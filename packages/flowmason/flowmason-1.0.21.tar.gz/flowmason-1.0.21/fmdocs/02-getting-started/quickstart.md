# Quick Start Guide

Build and run your first FlowMason pipeline in 5 minutes.

## Prerequisites

- FlowMason installed ([Installation Guide](installation.md))
- An LLM API key (Anthropic or OpenAI)

## Step 1: Initialize a Project

```bash
mkdir my-first-pipeline && cd my-first-pipeline
fm init
```

This creates:
```
my-first-pipeline/
├── flowmason.json          # Project configuration
├── pipelines/              # Pipeline definitions
├── components/             # Custom components
└── .flowmason/            # State and cache
```

## Step 2: Set Your API Key

```bash
# Choose one or more providers
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
export GROQ_API_KEY="your-key-here"
export PERPLEXITY_API_KEY="your-key-here"
```

## Step 3: Create a Pipeline

Create `pipelines/hello.pipeline.json`:

```json
{
  "name": "hello-pipeline",
  "description": "My first FlowMason pipeline",
  "version": "1.0.0",
  "stages": [
    {
      "id": "greet",
      "component_type": "generator",
      "config": {
        "prompt": "Say hello to {{input.name}} in a creative way. Keep it under 50 words.",
        "temperature": 0.8
      }
    }
  ]
}
```

## Step 4: Run the Pipeline

```bash
fm run pipelines/hello.pipeline.json --input '{"name": "World"}'
```

Output:
```
FlowMason Pipeline Runner
Pipeline: hello-pipeline
─────────────────────────
[1/1] Running stage: greet (generator)
✓ Stage completed in 1.2s

Result:
{
  "content": "Hello there, magnificent World! May your day sparkle with unexpected joys..."
}
```

## Step 5: Add More Stages

Update `pipelines/hello.pipeline.json` to add processing:

```json
{
  "name": "hello-pipeline",
  "description": "My first FlowMason pipeline",
  "version": "1.0.0",
  "stages": [
    {
      "id": "greet",
      "component_type": "generator",
      "config": {
        "prompt": "Say hello to {{input.name}} in a creative way. Keep it under 50 words.",
        "temperature": 0.8
      }
    },
    {
      "id": "analyze",
      "component_type": "critic",
      "depends_on": ["greet"],
      "config": {
        "content": "{{greet.output.content}}",
        "criteria": ["creativity", "friendliness", "brevity"],
        "scoring_scale": 10
      }
    }
  ]
}
```

Run again:
```bash
fm run pipelines/hello.pipeline.json --input '{"name": "World"}'
```

## Step 6: Debug in VSCode

1. Open the project in VSCode
2. Open `pipelines/hello.pipeline.json`
3. Press `F5` to start debugging
4. Set breakpoints by clicking the gutter or pressing `F9`
5. Step through with `F10`

## Using the Visual Editor

1. Open a `.pipeline.json` file in VSCode
2. Click "Open DAG View" in the editor toolbar
3. Drag and drop to connect stages
4. Configure stages in the sidebar panel

## Common Patterns

### Conditional Branching

```json
{
  "id": "check",
  "component_type": "conditional",
  "depends_on": ["analyze"],
  "config": {
    "condition": "{{analyze.output.overall_score}} >= 7",
    "true_branch": "publish",
    "false_branch": "improve"
  }
}
```

### Error Handling

```json
{
  "id": "safe_fetch",
  "component_type": "trycatch",
  "config": {
    "try_stages": ["fetch_data"],
    "catch_stages": ["fallback"],
    "on_error": "continue"
  }
}
```

### Looping

```json
{
  "id": "process_all",
  "component_type": "foreach",
  "config": {
    "items": "{{input.urls}}",
    "item_variable": "url",
    "stages": ["fetch", "process"],
    "parallel": true,
    "max_concurrency": 5
  }
}
```

## Next Steps

- [Core Concepts](../03-concepts/architecture-overview.md) - Deeper understanding
- [Building Nodes](../04-core-framework/decorators/node.md) - Create custom AI components
- [Building Operators](../04-core-framework/decorators/operator.md) - Create utility components
- [Debugging](../09-debugging-testing/debugging/current-debugging.md) - Debug pipeline execution
- [VSCode Extension](../07-vscode-extension/overview.md) - Full extension guide
