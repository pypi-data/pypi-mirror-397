# Studio MCP API

FlowMason Studio exposes an HTTP API that mirrors MCP (Model Context Protocol) tools, enabling AI assistants to interact with Studio via standard HTTP requests.

## Overview

The MCP API provides:
- **Tool Discovery**: List available MCP tools
- **Tool Execution**: Execute tools via HTTP POST
- **Convenience Endpoints**: Direct access to common operations
- **Pipeline Management**: Create, validate, and query pipelines

## Base URL

```
http://localhost:8999/api/v1/mcp
```

## Endpoints

### List Available Tools

```
GET /api/v1/mcp/tools
```

Returns a list of all available MCP tools with their descriptions and parameters.

**Response:**
```json
[
  {
    "name": "list_pipelines",
    "description": "List all available pipelines in the workspace",
    "parameters": {}
  },
  {
    "name": "suggest_pipeline",
    "description": "Get AI-powered suggestions for building a pipeline",
    "parameters": {
      "task_description": {"type": "string", "required": true}
    }
  }
]
```

### Execute Tool

```
POST /api/v1/mcp/tools/call
```

Execute any MCP tool by name.

**Request:**
```json
{
  "tool_name": "suggest_pipeline",
  "arguments": {
    "task_description": "Summarize articles and filter by sentiment"
  }
}
```

**Response:**
```json
{
  "success": true,
  "content": "## Suggested Pipeline for: Summarize articles...\n\n...",
  "error": null,
  "metadata": {}
}
```

## Convenience Endpoints

### Suggest Pipeline

```
POST /api/v1/mcp/suggest
```

Get pipeline suggestions based on a task description.

**Request:**
```json
{
  "task_description": "Process customer feedback and generate reports"
}
```

**Response:**
```json
{
  "name": "suggested-pipeline",
  "description": "Process customer feedback and generate reports",
  "stages": [
    {
      "component": "generator",
      "purpose": "Generate summary",
      "rationale": "Use LLM to create a summary of the input"
    },
    {
      "component": "filter",
      "purpose": "Filter items based on criteria",
      "rationale": "Filter data to include only relevant items"
    }
  ],
  "example_pipeline": { ... }
}
```

### Generate Stage

```
POST /api/v1/mcp/generate-stage
```

Generate a stage configuration for a component type.

**Request:**
```json
{
  "stage_type": "generator",
  "purpose": "summarize the article content",
  "input_source": "input"
}
```

**Response:**
```json
{
  "id": "generator-a1b2c3",
  "name": "summarize the article content",
  "component_type": "generator",
  "config": {
    "prompt": "Based on the following input, summarize the article content:\n\n{{input}}",
    "max_tokens": 1000,
    "temperature": 0.7
  },
  "depends_on": null
}
```

### Validate Pipeline

```
POST /api/v1/mcp/validate
```

Validate a pipeline configuration.

**Request:**
```json
{
  "pipeline_json": "{\"name\": \"test\", \"stages\": []}"
}
```

**Response:**
```json
{
  "valid": false,
  "errors": ["Pipeline must have at least one stage"],
  "warnings": ["Consider adding a 'description' field"]
}
```

### Create Pipeline

```
POST /api/v1/mcp/create
```

Create a new pipeline.

**Request:**
```json
{
  "name": "my-pipeline",
  "description": "A pipeline that processes data",
  "stages": [
    {
      "id": "process",
      "name": "Process Data",
      "component_type": "generator",
      "config": {
        "prompt": "Process: {{input}}"
      }
    }
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "text": {"type": "string"}
    }
  }
}
```

**Response:**
```json
{
  "pipeline_id": "pipe_abc123",
  "name": "my-pipeline",
  "path": null,
  "message": "Pipeline created successfully"
}
```

## Available Tools

### list_pipelines
List all pipelines in the workspace.

**Parameters:** None

**Returns:** Formatted list of pipelines with name, version, status, and stage count.

### list_components
List all available FlowMason components.

**Parameters:** None

**Returns:** Components grouped by category with descriptions.

### get_component
Get detailed information about a specific component.

**Parameters:**
- `component_type` (string, required): The component type to look up

**Returns:** Component details including configuration schema.

### suggest_pipeline
Get AI-powered suggestions for building a pipeline.

**Parameters:**
- `task_description` (string, required): Natural language description of desired pipeline

**Returns:** Suggested components with rationale and example structure.

### generate_stage
Generate a stage configuration for a component type.

**Parameters:**
- `stage_type` (string, required): Component type (e.g., "generator", "filter")
- `purpose` (string, required): What the stage should accomplish
- `input_source` (string, default: "input"): Input source reference

**Returns:** Complete stage configuration ready to add to a pipeline.

### validate_pipeline_config
Validate a pipeline configuration.

**Parameters:**
- `pipeline_json` (string, required): Pipeline configuration as JSON string

**Returns:** Validation result with errors and warnings.

### create_pipeline
Create a new pipeline from a configuration.

**Parameters:**
- `name` (string, required): Pipeline name
- `description` (string, required): Pipeline description
- `stages_json` (string, required): JSON array of stage objects
- `input_schema_json` (string, optional): JSON Schema for inputs

**Returns:** Created pipeline ID and confirmation.

## Integration Examples

### Using with curl

```bash
# List available tools
curl http://localhost:8999/api/v1/mcp/tools

# Get pipeline suggestions
curl -X POST http://localhost:8999/api/v1/mcp/suggest \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Summarize articles"}'

# Execute any tool
curl -X POST http://localhost:8999/api/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "list_components", "arguments": {}}'
```

### Using with Python

```python
import requests

BASE_URL = "http://localhost:8999/api/v1/mcp"

# Get suggestions
response = requests.post(
    f"{BASE_URL}/suggest",
    json={"task_description": "Process customer feedback"}
)
suggestions = response.json()

# Generate stage
stage = requests.post(
    f"{BASE_URL}/generate-stage",
    json={
        "stage_type": "generator",
        "purpose": "summarize feedback",
        "input_source": "input"
    }
).json()

# Create pipeline
pipeline = requests.post(
    f"{BASE_URL}/create",
    json={
        "name": "feedback-processor",
        "description": "Processes customer feedback",
        "stages": [stage]
    }
).json()
```

### Using with AI Assistants

The MCP API is designed to be used by AI assistants like Claude. When integrated with an assistant, it enables natural language pipeline creation:

```
User: "Create a pipeline that summarizes articles and filters out sports content"
Assistant: [Uses suggest_pipeline to get recommendations]
         [Generates stages with generate_stage]
         [Validates with validate_pipeline_config]
         [Creates pipeline with create_pipeline]

I have created your "article-summarizer" pipeline with 2 stages:
1. generator - Summarize article content
2. filter - Filter out sports articles

You can run it with: fm run article-summarizer.pipeline.json
```

## Error Handling

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Internal server error

Error responses include a `detail` field:

```json
{
  "detail": "Invalid pipeline JSON: Expecting value: line 1 column 1"
}
```

## Authentication

When authentication is enabled in Studio, include the JWT token in requests:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8999/api/v1/mcp/tools
```

## Related Documentation

- [MCP Server (CLI)](../07-integrations/mcp.md) - MCP server for Claude Desktop
- [AI Generation Tools](../07-integrations/mcp-ai-generation.md) - Detailed MCP tool reference
- [VSCode MCP Integration](../07-integrations/vscode-mcp.md) - MCP in VSCode extension

