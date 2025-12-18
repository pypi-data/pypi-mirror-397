# Natural Language Pipeline Builder

FlowMason Studio includes an AI-powered Natural Language Builder that generates complete pipelines from plain English descriptions.

## Overview

The Natural Language Builder enables:

- **Pipeline Generation**: Describe what you want, get a working pipeline
- **Intent Analysis**: Understand how your request is interpreted
- **Component Matching**: Find the right components for any task
- **Iterative Refinement**: Improve generated pipelines with feedback
- **Templates**: Start from common patterns

## Quick Start

### Generate a Pipeline

```http
POST /api/v1/nl-builder/generate
Content-Type: application/json

{
  "description": "Summarize a long article, then translate the summary to Spanish",
  "mode": "detailed"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Pipeline generated successfully",
  "result": {
    "id": "gen_abc123",
    "status": "completed",
    "analysis": {
      "intent": "summarization",
      "actions": ["summarize", "translate"],
      "entities": [],
      "data_sources": ["user_input"],
      "outputs": ["text"],
      "constraints": [],
      "ambiguities": []
    },
    "suggestions": [
      {
        "component_type": "generator",
        "name": "Generator",
        "purpose": "Generate summary from input",
        "rationale": "Matches intent: summarization",
        "confidence": 0.9
      },
      {
        "component_type": "generator",
        "name": "Generator",
        "purpose": "Translate content",
        "rationale": "Required for action: translate",
        "confidence": 0.85
      }
    ],
    "pipeline": {
      "name": "Summarization Pipeline",
      "description": "Summarize a long article, then translate the summary to Spanish",
      "version": "1.0.0",
      "stages": [
        {
          "id": "generator_1",
          "name": "Generate summary from input",
          "component_type": "generator",
          "config": {
            "prompt": "Based on the following input, generate summary from input:\n\n{{input}}",
            "max_tokens": 1000,
            "temperature": 0.7
          },
          "depends_on": []
        },
        {
          "id": "generator_2",
          "name": "Translate content",
          "component_type": "generator",
          "config": {
            "prompt": "Based on the following input, translate content:\n\n{{stages.generator_1.output}}",
            "max_tokens": 1000,
            "temperature": 0.7
          },
          "depends_on": ["generator_1"]
        }
      ],
      "input_schema": {
        "type": "object",
        "properties": {
          "text": {
            "type": "string",
            "description": "Input text to process"
          }
        },
        "required": ["text"]
      }
    }
  }
}
```

### Quick Generation

For simple pipelines, use the quick endpoint:

```http
POST /api/v1/nl-builder/quick?description=Filter%20products%20by%20price%20and%20sort%20by%20rating
```

Returns just the generated pipeline without detailed analysis.

## Generation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `quick` | Fast generation with basic structure | Simple pipelines |
| `detailed` | Full generation with configs and analysis | Production pipelines |
| `interactive` | Step-by-step with user feedback | Complex requirements |

## Analyzing Requests

Before generating, you can analyze how your description will be interpreted:

```http
POST /api/v1/nl-builder/analyze?description=Fetch%20data%20from%20API%20and%20summarize%20it
```

**Response:**
```json
{
  "analysis": {
    "intent": "summarization",
    "entities": [],
    "actions": ["summarize", "call"],
    "data_sources": ["external_api"],
    "outputs": [],
    "constraints": [],
    "ambiguities": ["Output format not specified"]
  },
  "suggested_approach": "fetch data from external_api → perform call, summarize",
  "estimated_complexity": "moderate",
  "estimated_stages": 3
}
```

## Finding Components

Search for components that match a task:

```http
POST /api/v1/nl-builder/match-components
Content-Type: application/json

{
  "task": "filter a list of products by price",
  "limit": 3
}
```

**Response:**
```json
{
  "task": "filter a list of products by price",
  "matches": [
    {
      "component_type": "filter",
      "name": "Filter",
      "description": "Filter items based on conditions",
      "match_score": 0.4,
      "match_reason": "matches use case 'filter'"
    },
    {
      "component_type": "json_transform",
      "name": "JSON Transform",
      "description": "Transform and restructure JSON data",
      "match_score": 0.2,
      "match_reason": "contains 'data'"
    }
  ]
}
```

## Refining Pipelines

Improve a generated pipeline with feedback:

```http
POST /api/v1/nl-builder/refine
Content-Type: application/json

{
  "generation_id": "gen_abc123",
  "feedback": "Add error handling and make the output more structured as JSON"
}
```

**Response:**
```json
{
  "original_id": "gen_abc123",
  "refined_id": "gen_def456",
  "changes_made": [
    "Added stages: schema_validate_1",
    "Modified stage configurations"
  ],
  "pipeline": { ... }
}
```

## Templates

Start from predefined templates for common patterns:

### List Templates

```http
GET /api/v1/nl-builder/templates
```

**Response:**
```json
[
  {
    "id": "summarization",
    "name": "Text Summarization",
    "description": "Summarize long text into concise points",
    "category": "ai",
    "example_prompt": "Summarize this article into 3 key points",
    "stages": 1
  },
  {
    "id": "content-review",
    "name": "Content Review",
    "description": "Generate content and have it reviewed for quality",
    "category": "ai",
    "example_prompt": "Generate a product description and review it for accuracy",
    "stages": 2
  }
]
```

### Generate from Template

```http
POST /api/v1/nl-builder/from-template/content-review?customization=Focus%20on%20technical%20products
```

## Advanced Options

### Preferred/Avoided Components

Control which components are used:

```json
{
  "description": "Process and validate user data",
  "preferred_components": ["schema_validate", "json_transform"],
  "avoid_components": ["http_request"]
}
```

### Context and Examples

Provide additional context:

```json
{
  "description": "Generate a report from sales data",
  "context": {
    "available_fields": ["date", "amount", "product", "region"],
    "output_format": "markdown"
  },
  "examples": [
    {
      "input": {"sales": [{"amount": 100}]},
      "output": {"total": 100, "count": 1}
    }
  ]
}
```

## Intent Recognition

The builder recognizes these primary intents:

| Intent | Trigger Words |
|--------|---------------|
| `summarization` | summarize, summary |
| `translation` | translate, translation |
| `classification` | classify, categorize |
| `extraction` | extract, parse |
| `generation` | generate, create, write |
| `transformation` | transform, convert |
| `validation` | validate, check, verify |
| `analysis` | analyze, evaluate |

## Component Selection

Components are matched based on:

1. **Use case keywords** - Direct matches with component capabilities
2. **Description similarity** - Words found in component descriptions
3. **Name matching** - Component names in the request
4. **Action mapping** - Actions mapped to appropriate components

### Action to Component Mapping

| Action | Component |
|--------|-----------|
| filter | filter |
| transform | json_transform |
| validate | schema_validate |
| send/call | http_request |
| summarize/generate | generator |
| review/evaluate | critic |
| improve | improver |

## Python Integration

```python
from flowmason_studio.services.nl_builder_service import get_nl_builder_service
import asyncio

service = get_nl_builder_service()

async def generate():
    # Generate pipeline
    result = await service.generate_pipeline(
        description="Fetch news articles and summarize the top 5",
        mode=GenerationMode.DETAILED,
    )

    if result.pipeline:
        print(f"Generated: {result.pipeline.name}")
        for stage in result.pipeline.stages:
            print(f"  - {stage.id}: {stage.component_type}")

    # Find components
    matches = await service.find_components("filter by date", limit=3)
    for match in matches:
        print(f"{match.component_type}: {match.match_score:.2f}")

    # Analyze request
    analysis = await service.analyze_request("Process customer feedback")
    print(f"Intent: {analysis.intent}")
    print(f"Actions: {analysis.actions}")

asyncio.run(generate())
```

## Best Practices

1. **Be Specific**: Include details about inputs, outputs, and processing steps
2. **Use Action Words**: Start with verbs like "summarize", "filter", "transform"
3. **Mention Data Sources**: Specify if data comes from API, file, or user input
4. **Describe Output Format**: Mention if you need JSON, text, email, etc.
5. **Iterate with Refinement**: Use the refine endpoint to improve results

## Tips for Better Results

### Good Descriptions

- "Fetch product data from API, filter by price under $100, and generate a summary report"
- "Validate JSON input against a schema, transform to new format, and send to webhook"
- "Take a list of articles, summarize each one, then combine into a newsletter"

### Less Effective Descriptions

- "Process data" (too vague)
- "Make it work" (no specific intent)
- "Do the thing with the stuff" (unclear)

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/nl-builder/generate` | POST | Generate pipeline from description |
| `/nl-builder/quick` | POST | Quick generation (returns pipeline only) |
| `/nl-builder/generations/{id}` | GET | Get generation result |
| `/nl-builder/refine` | POST | Refine a generated pipeline |
| `/nl-builder/analyze` | POST | Analyze request without generating |
| `/nl-builder/match-components` | POST | Find matching components |
| `/nl-builder/components/search` | GET | Quick component search |
| `/nl-builder/templates` | GET | List available templates |
| `/nl-builder/from-template/{id}` | POST | Generate from template |
