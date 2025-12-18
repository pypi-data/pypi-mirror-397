# AI Co-pilot

The FlowMason AI Co-pilot provides intelligent assistance for designing, debugging, and optimizing pipelines using large language models.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  AI Co-pilot                                              [Ask] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User: "Add error handling to the API call stage"               │
│                                                                 │
│  Co-pilot: I'll wrap the http-request stage in a trycatch       │
│  with retry logic. Here's my suggestion:                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ + trycatch: api-with-retry                               │   │
│  │   ├── try: http-request (existing)                       │   │
│  │   ├── catch: error-handler (new)                         │   │
│  │   └── retry: 3 attempts, exponential backoff             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Apply Changes]  [Modify]  [Explain]  [Reject]                │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### 1. Pipeline Suggestions

Get AI-powered suggestions for improving your pipelines.

```python
from flowmason_core.copilot import CopilotService, CopilotContext

# Initialize service
copilot = CopilotService(api_key="your-anthropic-key")

# Create context from your pipeline
context = CopilotContext.from_pipeline(pipeline)

# Get suggestions
suggestion = await copilot.suggest(
    context=context,
    request="Add error handling to the API call"
)

print(f"Suggestion: {suggestion.description}")
print(f"Changes: {suggestion.config}")
print(f"Reasoning: {suggestion.reasoning}")
```

### 2. Pipeline Explanation

Understand complex pipelines with AI-generated explanations.

```python
explanation = await copilot.explain(
    context=context,
    target="process-data"  # Specific stage or None for whole pipeline
)

print(explanation.summary)
print(explanation.details)
```

### 3. Pipeline Generation

Generate entire pipelines from natural language descriptions.

```python
pipeline = await copilot.generate(
    description="Create a pipeline that fetches user data from an API, "
                "validates the schema, transforms it to our format, "
                "and saves to the database"
)
```

### 4. Optimization Suggestions

Get recommendations for improving pipeline performance.

```python
optimizations = await copilot.optimize(context=context)

for opt in optimizations:
    print(f"- {opt.description}")
    print(f"  Impact: {opt.impact}")
    print(f"  Effort: {opt.effort}")
```

### 5. Debug Assistance

Get help debugging pipeline issues.

```python
debug_help = await copilot.debug(
    context=context,
    error_message="Stage 'transform' failed: KeyError 'user_id'",
    execution_logs=logs
)

print(f"Root cause: {debug_help.root_cause}")
print(f"Suggested fix: {debug_help.suggestion}")
```

## API Endpoints

The Studio backend provides REST endpoints for co-pilot functionality:

### POST /api/v1/copilot/suggest
```json
{
  "pipeline_id": "my-pipeline",
  "request": "Add validation before the transform stage"
}
```

### POST /api/v1/copilot/explain
```json
{
  "pipeline_id": "my-pipeline",
  "stage_id": "transform"  // optional
}
```

### POST /api/v1/copilot/generate
```json
{
  "description": "Pipeline that processes customer feedback"
}
```

### POST /api/v1/copilot/optimize
```json
{
  "pipeline_id": "my-pipeline"
}
```

### POST /api/v1/copilot/debug
```json
{
  "pipeline_id": "my-pipeline",
  "run_id": "run-123",
  "error": "KeyError: 'user_id'"
}
```

## Context Serialization

The co-pilot uses a structured context to understand your pipeline:

```python
from flowmason_core.copilot import (
    CopilotContext, PipelineSnapshot, StageSnapshot, RegistrySnapshot
)

# Manual context creation
context = CopilotContext(
    pipeline=PipelineSnapshot(
        id="my-pipeline",
        name="My Pipeline",
        stages=[
            StageSnapshot(
                id="fetch",
                component_type="http_request",
                config={"url": "https://api.example.com"}
            )
        ]
    ),
    registry=RegistrySnapshot(
        available_components=["http_request", "json_transform", "logger"]
    )
)
```

## VSCode Integration

Access the AI Co-pilot directly from VSCode:

### Sidebar Panel
1. Open the FlowMason sidebar
2. Click on "AI Co-pilot" tab
3. Type your request and press Enter

### Inline Suggestions
- Hover over a stage and click "Ask AI"
- Use `Cmd+K` (Mac) or `Ctrl+K` (Windows) for quick actions

### Commands
- `FlowMason: Ask AI Co-pilot`
- `FlowMason: Explain Pipeline`
- `FlowMason: Optimize Pipeline`
- `FlowMason: Generate Pipeline from Description`

## Configuration

Configure the co-pilot in your settings:

```json
{
  "flowmason.copilot.enabled": true,
  "flowmason.copilot.model": "claude-3-opus",
  "flowmason.copilot.maxTokens": 4096,
  "flowmason.copilot.temperature": 0.7
}
```

Environment variables:
```bash
ANTHROPIC_API_KEY=your-api-key
FLOWMASON_COPILOT_MODEL=claude-3-opus
```

## Best Practices

1. **Be Specific**: Provide clear, specific requests for better suggestions
2. **Review Changes**: Always review AI suggestions before applying
3. **Iterate**: Use "Modify" to refine suggestions that are close but not perfect
4. **Provide Context**: Include relevant information about your use case
5. **Use Explain**: Use the explain feature to understand complex pipelines
