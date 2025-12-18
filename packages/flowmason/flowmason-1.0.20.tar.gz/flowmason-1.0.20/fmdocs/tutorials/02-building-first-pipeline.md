# Tutorial 2: Building Your First Pipeline

This tutorial guides you through creating a complete AI pipeline that fetches content from a URL and generates a summary.

## What We'll Build

A 3-stage pipeline:
1. **fetch** - Retrieve content from a URL
2. **extract** - Extract the main text content
3. **summarize** - Generate an AI summary

```
[fetch] ──► [extract] ──► [summarize]
```

## Prerequisites

- Completed [Tutorial 1: Getting Started](./01-getting-started.md)
- Studio running (`fm studio start`)
- API key configured for your LLM provider

## Step 1: Create the Pipeline File

### Option A: Using Command Palette

1. Press `Cmd+Shift+P`
2. Type "FlowMason: New Pipeline"
3. Enter name: `content-summarizer`
4. A new file opens: `pipelines/content-summarizer.pipeline.json`

### Option B: Manual Creation

Create `pipelines/content-summarizer.pipeline.json`:

```json
{
  "$schema": "../.flowmason/schemas/pipeline.schema.json",
  "name": "content-summarizer",
  "version": "1.0.0",
  "description": "Fetches content from a URL and generates a summary",
  "input_schema": {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "URL to fetch and summarize"
      },
      "max_length": {
        "type": "integer",
        "default": 200,
        "description": "Maximum summary length in words"
      }
    },
    "required": ["url"]
  },
  "stages": []
}
```

## Step 2: Add the Fetch Stage

The first stage fetches content from the provided URL.

### Using the Visual Editor

1. Click "Open DAG View" button in the editor toolbar
2. Click "Add Stage" or press `Cmd+Shift+A`
3. Select "Operators" → "http-request"
4. Enter stage ID: `fetch`

### JSON Configuration

Add to the `stages` array:

```json
{
  "id": "fetch",
  "component_type": "http-request",
  "description": "Fetch content from URL",
  "config": {
    "url": "{{input.url}}",
    "method": "GET",
    "timeout": 30
  }
}
```

### Understanding Template Syntax

- `{{input.url}}` - References the pipeline input
- `{{input.max_length}}` - Would reference max_length input
- Template expressions are evaluated at runtime

## Step 3: Add the Extract Stage

This stage extracts clean text from the HTML response.

Add to `stages`:

```json
{
  "id": "extract",
  "component_type": "json-transform",
  "description": "Extract text content",
  "depends_on": ["fetch"],
  "config": {
    "data": "{{fetch.output.body}}",
    "expression": "content || text || body"
  }
}
```

### Key Concepts

- `depends_on: ["fetch"]` - This stage runs after `fetch` completes
- `{{fetch.output.body}}` - References the output of the `fetch` stage
- The JMESPath expression extracts text content

## Step 4: Add the Summarize Stage

This AI stage generates the summary using an LLM.

Add to `stages`:

```json
{
  "id": "summarize",
  "component_type": "generator",
  "description": "Generate AI summary",
  "depends_on": ["extract"],
  "config": {
    "system_prompt": "You are a concise summarizer. Extract key points and present them clearly.",
    "prompt": "Summarize the following content in {{input.max_length}} words or less:\n\n{{extract.output.result}}",
    "temperature": 0.3,
    "max_tokens": 500
  }
}
```

### AI Node Configuration

| Field | Description |
|-------|-------------|
| `system_prompt` | Sets the AI's behavior/persona |
| `prompt` | The user message with template variables |
| `temperature` | Creativity level (0.0-2.0, lower = more focused) |
| `max_tokens` | Maximum response length |

## Step 5: Complete Pipeline

Your complete `content-summarizer.pipeline.json`:

```json
{
  "$schema": "../.flowmason/schemas/pipeline.schema.json",
  "name": "content-summarizer",
  "version": "1.0.0",
  "description": "Fetches content from a URL and generates a summary",
  "input_schema": {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "URL to fetch and summarize"
      },
      "max_length": {
        "type": "integer",
        "default": 200,
        "description": "Maximum summary length in words"
      }
    },
    "required": ["url"]
  },
  "stages": [
    {
      "id": "fetch",
      "component_type": "http-request",
      "description": "Fetch content from URL",
      "config": {
        "url": "{{input.url}}",
        "method": "GET",
        "timeout": 30
      }
    },
    {
      "id": "extract",
      "component_type": "json-transform",
      "description": "Extract text content",
      "depends_on": ["fetch"],
      "config": {
        "data": "{{fetch.output.body}}",
        "expression": "content || text || body"
      }
    },
    {
      "id": "summarize",
      "component_type": "generator",
      "description": "Generate AI summary",
      "depends_on": ["extract"],
      "config": {
        "system_prompt": "You are a concise summarizer. Extract key points and present them clearly.",
        "prompt": "Summarize the following content in {{input.max_length}} words or less:\n\n{{extract.output.result}}",
        "temperature": 0.3,
        "max_tokens": 500
      }
    }
  ],
  "output": {
    "summary": "{{summarize.output.content}}",
    "source_url": "{{input.url}}"
  }
}
```

## Step 6: Validate the Pipeline

### Automatic Validation

The extension validates in real-time. Check the Problems panel (`Cmd+Shift+M`) for errors:

- Missing dependencies
- Unknown component types
- Invalid configuration
- Circular dependencies

### Manual Validation

```bash
fm validate pipelines/content-summarizer.pipeline.json
```

## Step 7: Run the Pipeline

### From VSCode

1. Open the pipeline file
2. Click the "Run" CodeLens above the pipeline name
3. Enter input when prompted:
   ```json
   {
     "url": "https://example.com/article",
     "max_length": 150
   }
   ```
4. View results in the Output panel

### From Command Line

```bash
fm run pipelines/content-summarizer.pipeline.json \
  --input '{"url": "https://example.com/article", "max_length": 150}'
```

### From API

```bash
curl -X POST http://localhost:8999/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline": "content-summarizer",
    "input": {
      "url": "https://example.com/article",
      "max_length": 150
    }
  }'
```

## Step 8: View the DAG Visualization

1. Open the pipeline file
2. Click "Open DAG View" in the toolbar
3. See your pipeline as a visual graph:

```
┌─────────┐     ┌─────────┐     ┌───────────┐
│  fetch  │────►│ extract │────►│ summarize │
└─────────┘     └─────────┘     └───────────┘
```

### DAG Interactions

- **Click** a stage to select it
- **Double-click** to edit configuration
- **Right-click** for context menu
- **Drag** to reposition nodes

## Adding Error Handling

Wrap risky operations with TryCatch:

```json
{
  "id": "safe_fetch",
  "component_type": "trycatch",
  "config": {
    "try_stages": ["fetch", "extract"],
    "catch_stages": ["handle_error"],
    "on_error": "continue"
  }
}
```

Add an error handler:

```json
{
  "id": "handle_error",
  "component_type": "logger",
  "config": {
    "level": "error",
    "message": "Failed to fetch: {{_error.message}}"
  }
}
```

## Adding Conditional Logic

Process different content types differently:

```json
{
  "id": "route_content",
  "component_type": "router",
  "depends_on": ["fetch"],
  "config": {
    "value": "{{fetch.output.content_type}}",
    "routes": {
      "text/html": "extract_html",
      "application/json": "extract_json",
      "text/plain": "extract_text"
    },
    "default": "extract_text"
  }
}
```

## Exercise: Extend the Pipeline

Try adding these features:

1. **Language Detection** - Add a stage to detect the content language
2. **Translation** - If not English, translate before summarizing
3. **Keywords** - Extract keywords from the summary
4. **Output Formatting** - Format the final output as Markdown

## Common Patterns

### Sequential Processing

```
[A] ──► [B] ──► [C]
```

```json
{ "id": "A" },
{ "id": "B", "depends_on": ["A"] },
{ "id": "C", "depends_on": ["B"] }
```

### Parallel Processing

```
      ┌──► [B] ──┐
[A] ──┤          ├──► [D]
      └──► [C] ──┘
```

```json
{ "id": "A" },
{ "id": "B", "depends_on": ["A"] },
{ "id": "C", "depends_on": ["A"] },
{ "id": "D", "depends_on": ["B", "C"] }
```

### Conditional Branching

```
        ┌──► [B] (if true)
[A] ──► │
        └──► [C] (if false)
```

```json
{
  "id": "branch",
  "component_type": "conditional",
  "depends_on": ["A"],
  "config": {
    "condition": "{{A.output.valid}}",
    "true_branch": "B",
    "false_branch": "C"
  }
}
```

## Next Steps

- [Tutorial 3: Debugging Pipelines](./03-debugging-pipelines.md) - Learn to debug with breakpoints
- [Tutorial 4: Testing Pipelines](./04-testing-pipelines.md) - Write tests for your pipeline
- [Tutorial 5: Working with Components](./05-working-with-components.md) - Create custom nodes
