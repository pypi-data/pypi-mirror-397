# Pipeline Definition

Complete reference for the Flowmason pipeline JSON structure.

## Pipeline Structure

```json
{
  "name": "Pipeline Name",
  "version": "1.0.0",
  "description": "What this pipeline does",
  "input_schema": { ... },
  "output_schema": { ... },
  "stages": [ ... ],
  "output_stage_id": "final-stage-id"
}
```

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable pipeline name |
| `version` | string | No | Semantic version (e.g., "1.0.0") |
| `description` | string | No | Pipeline description |
| `input_schema` | object | No | JSON Schema for input validation |
| `output_schema` | object | No | JSON Schema for output validation |
| `stages` | array | Yes | Array of stage definitions |
| `output_stage_id` | string | Yes | ID of the stage that produces final output |

## Stage Structure

```json
{
  "id": "unique-stage-id",
  "name": "Human Readable Name",
  "component_type": "generator",
  "config": { ... },
  "depends_on": ["previous-stage-id"],
  "position": { "x": 100, "y": 200 }
}
```

### Stage Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (alphanumeric + hyphens) |
| `name` | string | No | Display name for debugging |
| `component_type` | string | Yes | Component type to execute |
| `config` | object | Yes | Component-specific configuration |
| `depends_on` | array | Yes | Array of stage IDs this stage depends on |
| `position` | object | No | Visual position for Studio (x, y coordinates) |

## Template Syntax

Templates use `{{...}}` syntax to reference data:

### Input References

Access pipeline input values:

```
{{input.field}}           # Direct field access
{{input.nested.field}}    # Nested field access
{{input.array[0]}}        # Array index access
```

### Upstream References

Access results from completed stages:

```
{{upstream.stage-id.result}}      # Stage result
{{upstream.stage-id.content}}     # Generator content
{{upstream.stage-id.body}}        # HTTP response body
{{upstream.stage-id.status_code}} # HTTP status code
```

### Context References

Access loop context variables (in foreach):

```
{{context.current_item}}   # Current iteration item
{{context.item_index}}     # Current iteration index
```

### Template Examples

```json
{
  "config": {
    "prompt": "Summarize: {{input.article_text}}",
    "data": {
      "user": "{{input.user_name}}",
      "classification": "{{upstream.classify.content}}",
      "processed": "{{upstream.transform.result}}"
    }
  }
}
```

## Input Schema

Define expected input structure using JSON Schema:

```json
{
  "input_schema": {
    "type": "object",
    "properties": {
      "subject": {
        "type": "string",
        "description": "Ticket subject line"
      },
      "description": {
        "type": "string",
        "description": "Ticket description"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "default": "medium"
      }
    },
    "required": ["subject", "description"]
  }
}
```

## Output Schema

Define expected output structure:

```json
{
  "output_schema": {
    "type": "object",
    "properties": {
      "category": {
        "type": "string",
        "enum": ["billing", "technical", "account", "other"]
      },
      "priority": {
        "type": "string"
      },
      "response": {
        "type": "string"
      }
    }
  }
}
```

## Dependencies and Execution Order

### Sequential Execution

Stages execute in dependency order:

```json
{
  "stages": [
    { "id": "A", "depends_on": [] },
    { "id": "B", "depends_on": ["A"] },
    { "id": "C", "depends_on": ["B"] }
  ]
}
```

Execution order: A → B → C

### Parallel Execution

Stages without dependencies can run in parallel:

```json
{
  "stages": [
    { "id": "A", "depends_on": [] },
    { "id": "B", "depends_on": [] },
    { "id": "C", "depends_on": [] },
    { "id": "D", "depends_on": ["A", "B", "C"] }
  ]
}
```

Execution: A, B, C (parallel) → D

### Diamond Dependencies

```json
{
  "stages": [
    { "id": "start", "depends_on": [] },
    { "id": "path-a", "depends_on": ["start"] },
    { "id": "path-b", "depends_on": ["start"] },
    { "id": "merge", "depends_on": ["path-a", "path-b"] }
  ]
}
```

```
       ┌─→ path-a ─┐
start ─┤           ├─→ merge
       └─→ path-b ─┘
```

## Complete Example

```json
{
  "name": "Customer Support Triage",
  "version": "1.0.0",
  "description": "Classify and respond to support tickets",
  "input_schema": {
    "type": "object",
    "properties": {
      "subject": { "type": "string" },
      "description": { "type": "string" },
      "customer_id": { "type": "string" }
    },
    "required": ["subject", "description"]
  },
  "stages": [
    {
      "id": "classify",
      "name": "Classify Ticket",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a support ticket classifier. Output JSON with category and priority.",
        "prompt": "Classify:\nSubject: {{input.subject}}\nDescription: {{input.description}}",
        "max_tokens": 100,
        "temperature": 0.1
      },
      "depends_on": []
    },
    {
      "id": "parse-classification",
      "name": "Parse Classification",
      "component_type": "json_transform",
      "config": {
        "data": "{{upstream.classify.content}}",
        "jmespath_expression": "@"
      },
      "depends_on": ["classify"]
    },
    {
      "id": "generate-response",
      "name": "Generate Response",
      "component_type": "generator",
      "config": {
        "system_prompt": "You are a helpful support agent. Write a professional response.",
        "prompt": "Write a response for this {{upstream.parse-classification.result.category}} ticket (priority: {{upstream.parse-classification.result.priority}}):\n\n{{input.description}}",
        "max_tokens": 300,
        "temperature": 0.7
      },
      "depends_on": ["parse-classification"]
    },
    {
      "id": "output",
      "name": "Format Output",
      "component_type": "json_transform",
      "config": {
        "data": {
          "category": "{{upstream.parse-classification.result.category}}",
          "priority": "{{upstream.parse-classification.result.priority}}",
          "response": "{{upstream.generate-response.content}}",
          "customer_id": "{{input.customer_id}}"
        },
        "jmespath_expression": "@"
      },
      "depends_on": ["generate-response"]
    }
  ],
  "output_stage_id": "output"
}
```

## Next Steps

- [Components](05-components.md) - Available component types
- [Execution](06-execution.md) - Sync and async execution
- [Examples](09-examples.md) - Complete pipeline examples
