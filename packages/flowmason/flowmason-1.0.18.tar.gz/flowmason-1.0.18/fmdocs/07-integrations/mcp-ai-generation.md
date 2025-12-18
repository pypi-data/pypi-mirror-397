# MCP AI Generation Tools

FlowMason's MCP server includes AI generation tools that enable AI assistants (Claude, GPT, etc.) to create and manage pipelines programmatically.

## Overview

The MCP server exposes tools for:
- **Pipeline Creation**: Generate complete pipeline configurations
- **Stage Generation**: Create individual stage configurations
- **Validation**: Validate pipeline configs before saving
- **Suggestions**: Get pipeline structure suggestions from task descriptions

## Available Tools

### suggest_pipeline

Get AI-powered suggestions for building a pipeline.

**Parameters:**
- `task_description`: Natural language description of what you want to accomplish

**Example Usage:**
```
Tool: suggest_pipeline
Input: "I want to summarize news articles and filter out sports content"
```

**Output:**
```markdown
## Suggested Pipeline for: I want to summarize news articles...

### Recommended Components

**1. generator**
   Purpose: Generate summary
   Rationale: Use LLM to create a summary of the input

**2. filter**
   Purpose: Filter items based on criteria
   Rationale: Filter data to include only relevant items

### Example Pipeline Structure

{
  "name": "suggested-pipeline",
  "stages": [...]
}
```

### generate_stage

Generate a stage configuration for a specific component type.

**Parameters:**
- `stage_type`: Component type (e.g., "generator", "filter")
- `purpose`: What this stage should do
- `input_source`: Where to get input ("input" or "stages.<stage_id>")

**Example:**
```
Tool: generate_stage
Input: {
  "stage_type": "generator",
  "purpose": "summarize the article content",
  "input_source": "input"
}
```

**Output:**
```json
{
  "id": "generator-a1b2c3",
  "name": "summarize the article content",
  "component_type": "generator",
  "config": {
    "prompt": "Based on the following input, summarize the article content:\n\n{{input}}",
    "max_tokens": 1000,
    "temperature": 0.7
  }
}
```

### create_pipeline

Create a new pipeline from a specification.

**Parameters:**
- `name`: Pipeline name
- `description`: What the pipeline does
- `stages_json`: JSON array of stage objects
- `input_schema_json`: (optional) JSON Schema for inputs

**Example:**
```
Tool: create_pipeline
Input: {
  "name": "content-summarizer",
  "description": "Summarizes articles and extracts key points",
  "stages_json": "[{\"id\": \"summarize\", \"name\": \"Summarize\", \"component_type\": \"generator\", \"config\": {\"prompt\": \"Summarize: {{input.text}}\"}}]"
}
```

**Output:**
```
Pipeline created successfully!

**File:** /path/to/content-summarizer.pipeline.json
**Name:** content-summarizer
**Stages:** 1

Run with: `fm run /path/to/content-summarizer.pipeline.json`
```

### validate_pipeline_config

Validate a pipeline configuration before creating it.

**Parameters:**
- `pipeline_json`: Full pipeline JSON configuration

**Example:**
```
Tool: validate_pipeline_config
Input: {
  "pipeline_json": "{\"name\": \"test\", \"stages\": []}"
}
```

**Output:**
```markdown
## Validation Failed

**Errors:**
- Pipeline must have at least one stage

**Warnings:**
- Consider adding a 'description' field
- Consider adding a 'version' field
```

## Workflow Example

Here's a typical workflow for an AI assistant creating a pipeline:

### 1. Understand Available Components

```
Tool: list_components
```

### 2. Get Suggestions

```
Tool: suggest_pipeline
Input: "Create a content moderation pipeline that checks text for profanity and sentiment"
```

### 3. Generate Stage Configurations

```
Tool: generate_stage
Input: {
  "stage_type": "generator",
  "purpose": "analyze sentiment of the text",
  "input_source": "input"
}
```

### 4. Validate the Pipeline

```
Tool: validate_pipeline_config
Input: {
  "pipeline_json": "..."
}
```

### 5. Create the Pipeline

```
Tool: create_pipeline
Input: {
  "name": "content-moderation",
  "description": "Checks content for profanity and sentiment",
  "stages_json": "[...]"
}
```

## Stage Configuration Templates

### Generator Stage

```json
{
  "id": "generate-content",
  "name": "Generate Content",
  "component_type": "generator",
  "config": {
    "prompt": "Based on {{input.topic}}, write a blog post.",
    "max_tokens": 2000,
    "temperature": 0.7
  }
}
```

### Filter Stage

```json
{
  "id": "filter-results",
  "name": "Filter Results",
  "component_type": "filter",
  "config": {
    "items_path": "{{stages.fetch.output.items}}",
    "condition": "item.score > 0.5"
  },
  "depends_on": ["fetch"]
}
```

### JSON Transform Stage

```json
{
  "id": "transform-data",
  "name": "Transform Data",
  "component_type": "json_transform",
  "config": {
    "template": {
      "summary": "{{stages.summarize.output}}",
      "timestamp": "{{now()}}",
      "source": "{{input.source}}"
    }
  },
  "depends_on": ["summarize"]
}
```

### HTTP Request Stage

```json
{
  "id": "call-api",
  "name": "Call External API",
  "component_type": "http_request",
  "config": {
    "url": "https://api.example.com/analyze",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": "{{input}}"
  }
}
```

### Loop Stage

```json
{
  "id": "process-items",
  "name": "Process Each Item",
  "component_type": "loop",
  "config": {
    "items_path": "{{input.items}}",
    "max_iterations": 100,
    "body_stage": "process-single"
  }
}
```

## Best Practices for AI Generation

### 1. Use Descriptive Names

```json
{
  "id": "extract-key-points",
  "name": "Extract Key Points from Article"
}
```

### 2. Chain Stages with Dependencies

```json
{
  "id": "stage-2",
  "depends_on": ["stage-1"],
  "config": {
    "input": "{{stages.stage-1.output}}"
  }
}
```

### 3. Document Input Requirements

```json
{
  "input_schema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "The text content to process"
      }
    },
    "required": ["text"]
  }
}
```

### 4. Validate Before Creating

Always call `validate_pipeline_config` before `create_pipeline` to catch errors early.

### 5. Use Appropriate Components

| Task | Recommended Component |
|------|----------------------|
| Generate text | generator |
| Filter data | filter |
| Transform structure | json_transform |
| Make API calls | http_request |
| Iterate over items | loop |
| Evaluate content | critic |
| Select items | selector |

## Integration with AI Assistants

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "flowmason": {
      "command": "fm",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Usage in Conversation

```
User: Create a pipeline that summarizes news articles

Claude: I'll create a summarization pipeline for you.

[Uses suggest_pipeline to understand structure]
[Uses generate_stage to create each stage]
[Uses validate_pipeline_config to check]
[Uses create_pipeline to save]

I've created your pipeline at news-summarizer.pipeline.json.
You can run it with: fm run news-summarizer.pipeline.json
```

## Error Handling

The tools provide helpful error messages:

```
Tool: create_pipeline
Error: "Stage 1 missing required 'id' field"
```

```
Tool: validate_pipeline_config
Warning: "Stage 'transform': consider adding 'name' for clarity"
```

Use validation feedback to iteratively improve the pipeline configuration before saving.
