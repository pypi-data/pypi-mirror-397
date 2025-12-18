# MCP AI Assistant

FlowMason Studio includes an AI-powered MCP Assistant that helps discover, understand, and use MCP tools effectively.

## Overview

The MCP Assistant provides:

- **Tool Discovery**: Find the right tools for any task
- **Smart Recommendations**: AI-analyzed tool suggestions with relevance scoring
- **Tool Explanations**: Detailed explanations of tool capabilities and usage
- **Tool Chains**: Automated multi-step workflows
- **Smart Invocation**: AI-assisted parameter resolution
- **Autocomplete**: Intelligent parameter suggestions
- **Conversations**: Multi-turn AI-assisted interactions

## Quick Start

### Analyze a Task

```http
POST /api/v1/mcp-assistant/analyze
Content-Type: application/json

{
  "task": "I need to create a pipeline that processes customer feedback",
  "available_data": {"source": "database"},
  "constraints": ["must handle large volumes"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Task analyzed successfully",
  "analysis": {
    "task": "I need to create a pipeline that processes customer feedback",
    "intent": "Create automated workflow for customer feedback processing",
    "required_capabilities": ["pipeline_management", "data_processing"],
    "data_requirements": ["customer feedback data", "processing rules"],
    "suggested_workflow": [
      "Create a new pipeline for feedback processing",
      "Configure data input source",
      "Add processing stages",
      "Set up output handling"
    ],
    "tool_recommendations": [
      {
        "tool_name": "create_pipeline",
        "relevance_score": 0.95,
        "reason": "Primary tool for creating new pipelines",
        "suggested_params": {
          "name": "customer-feedback-processor"
        }
      },
      {
        "tool_name": "add_stage",
        "relevance_score": 0.85,
        "reason": "Needed to add processing stages"
      }
    ]
  }
}
```

### Get Tool Recommendations

Quick recommendations without full analysis:

```http
GET /api/v1/mcp-assistant/recommend?task=summarize%20documents&limit=3
```

**Response:**
```json
{
  "task": "summarize documents",
  "recommendations": [
    {
      "tool_name": "run_pipeline",
      "relevance_score": 0.9,
      "reason": "Execute a summarization pipeline"
    },
    {
      "tool_name": "create_pipeline",
      "relevance_score": 0.7,
      "reason": "Create a new summarization pipeline"
    }
  ]
}
```

## Tool Discovery

### List All Tools

```http
GET /api/v1/mcp-assistant/tools
```

Returns enhanced tool information with AI-generated metadata:

```json
[
  {
    "name": "create_pipeline",
    "description": "Create a new pipeline configuration",
    "category": "pipeline",
    "capabilities": [
      {
        "name": "Pipeline Creation",
        "description": "Create new pipeline definitions",
        "examples": ["Create a summarization pipeline"]
      }
    ],
    "when_to_use": [
      "Starting a new workflow",
      "Setting up data processing"
    ],
    "prerequisites": [
      "Know the components you want to use"
    ],
    "related_tools": ["add_stage", "run_pipeline"],
    "usage_examples": [
      {
        "description": "Create a simple pipeline",
        "inputs": {"name": "my-pipeline", "description": "Process data"},
        "output": {"id": "pipe_123", "name": "my-pipeline"}
      }
    ]
  }
]
```

### Filter by Category

```http
GET /api/v1/mcp-assistant/tools?category=pipeline
```

Categories:
- `pipeline` - Pipeline management tools
- `component` - Component operations
- `data` - Data manipulation
- `integration` - External integrations
- `utility` - General utilities

### Search Tools

```http
GET /api/v1/mcp-assistant/tools/search?q=pipeline&limit=5
```

## Tool Explanations

### Get Detailed Explanation

```http
POST /api/v1/mcp-assistant/explain
Content-Type: application/json

{
  "tool_name": "run_pipeline",
  "context": "I'm building a batch processing system",
  "detail_level": "detailed"
}
```

**Response:**
```json
{
  "tool_name": "run_pipeline",
  "summary": "Execute a pipeline with given inputs",
  "detailed_description": "The run_pipeline tool executes a configured pipeline...",
  "parameter_explanations": {
    "pipeline_id": "The unique identifier of the pipeline to run",
    "inputs": "JSON object containing the input data for the pipeline"
  },
  "common_use_cases": [
    "Execute pipelines on demand",
    "Process batch data",
    "Test pipeline configurations"
  ],
  "tips": [
    "Use async execution for long-running pipelines",
    "Monitor execution via WebSocket for real-time updates"
  ],
  "warnings": [
    "Ensure inputs match the pipeline's expected schema"
  ],
  "see_also": ["create_pipeline", "get_pipeline_status"]
}
```

### Quick Explanation

```http
GET /api/v1/mcp-assistant/explain/run_pipeline?detail_level=brief
```

## Tool Chains

Create automated multi-step workflows:

### Create a Chain

```http
POST /api/v1/mcp-assistant/chains
Content-Type: application/json

{
  "goal": "Set up a new content moderation pipeline and run it",
  "max_steps": 5
}
```

**Response:**
```json
{
  "id": "chain_abc123",
  "name": "Content Moderation Setup",
  "description": "Set up a new content moderation pipeline and run it",
  "steps": [
    {
      "order": 1,
      "tool_name": "create_pipeline",
      "description": "Create the content moderation pipeline",
      "parameters": {
        "name": "content-moderation",
        "description": "Moderate user content"
      },
      "output_key": "pipeline"
    },
    {
      "order": 2,
      "tool_name": "add_stage",
      "description": "Add moderation component",
      "input_mapping": {
        "pipeline_id": "pipeline.id"
      },
      "parameters": {
        "component_type": "classifier"
      }
    },
    {
      "order": 3,
      "tool_name": "run_pipeline",
      "description": "Execute the pipeline",
      "input_mapping": {
        "pipeline_id": "pipeline.id"
      }
    }
  ],
  "estimated_duration": "~2 minutes"
}
```

### List Chains

```http
GET /api/v1/mcp-assistant/chains
```

### Get Chain Details

```http
GET /api/v1/mcp-assistant/chains/chain_abc123
```

## Smart Invocation

Let the AI resolve parameters from natural language:

```http
POST /api/v1/mcp-assistant/invoke
Content-Type: application/json

{
  "tool_name": "create_pipeline",
  "natural_language_params": "create a pipeline called news-summarizer for processing RSS feeds",
  "partial_params": {"version": "1.0.0"},
  "context": {"available_components": ["generator", "filter"]}
}
```

**Response:**
```json
{
  "success": true,
  "resolved_params": {
    "name": "news-summarizer",
    "description": "Pipeline for processing RSS feeds",
    "version": "1.0.0"
  },
  "confidence": 0.85,
  "explanations": {
    "name": "Extracted from 'called news-summarizer'",
    "description": "Inferred from 'processing RSS feeds'"
  },
  "warnings": []
}
```

## Autocomplete

Get intelligent parameter suggestions:

```http
POST /api/v1/mcp-assistant/autocomplete
Content-Type: application/json

{
  "tool_name": "run_pipeline",
  "parameter": "pipeline_id",
  "partial_value": "news",
  "context": {"recent_pipelines": ["news-summarizer", "news-classifier"]}
}
```

**Response:**
```json
{
  "parameter": "pipeline_id",
  "suggestions": [
    {
      "value": "news-summarizer",
      "label": "news-summarizer",
      "description": "Recently used pipeline",
      "source": "history"
    },
    {
      "value": "news-classifier",
      "label": "news-classifier",
      "description": "Recently used pipeline",
      "source": "history"
    }
  ]
}
```

## Conversations

For complex multi-step interactions:

### Start a Conversation

```http
POST /api/v1/mcp-assistant/conversations
Content-Type: application/json

{
  "initial_task": "Help me set up a document processing workflow"
}
```

**Response:**
```json
{
  "context": {
    "id": "conv_xyz789",
    "started_at": "2024-01-15T10:30:00Z",
    "messages": [],
    "tools_used": [],
    "current_task": "Help me set up a document processing workflow",
    "accumulated_data": {}
  },
  "assistant_response": "I'll help you with: Help me set up a document processing workflow. Let me analyze what tools we'll need."
}
```

### Continue the Conversation

```http
POST /api/v1/mcp-assistant/conversations/conv_xyz789/messages
Content-Type: application/json

{
  "message": "I want to extract text and summarize it"
}
```

### Get Conversation State

```http
GET /api/v1/mcp-assistant/conversations/conv_xyz789
```

### End Conversation

```http
DELETE /api/v1/mcp-assistant/conversations/conv_xyz789
```

## Categories

List all tool categories:

```http
GET /api/v1/mcp-assistant/categories
```

**Response:**
```json
[
  {
    "category": "pipeline",
    "description": "Tools for creating and managing pipelines",
    "tool_count": 5,
    "example_tools": ["create_pipeline", "run_pipeline", "list_pipelines"]
  },
  {
    "category": "component",
    "description": "Tools for working with components",
    "tool_count": 3,
    "example_tools": ["list_components", "get_component"]
  }
]
```

## Python Integration

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8999/api/v1") as client:
        # Analyze a task
        response = await client.post("/mcp-assistant/analyze", json={
            "task": "Build a sentiment analysis pipeline",
        })
        analysis = response.json()
        print(f"Intent: {analysis['analysis']['intent']}")

        for rec in analysis['analysis']['tool_recommendations']:
            print(f"  - {rec['tool_name']}: {rec['reason']}")

        # Get tool explanation
        response = await client.post("/mcp-assistant/explain", json={
            "tool_name": "create_pipeline",
            "detail_level": "detailed",
        })
        explanation = response.json()
        print(f"\nTool: {explanation['tool_name']}")
        print(f"Summary: {explanation['summary']}")

        # Create a tool chain
        response = await client.post("/mcp-assistant/chains", json={
            "goal": "Create and run a summarization pipeline",
        })
        chain = response.json()
        print(f"\nChain: {chain['name']}")
        for step in chain['steps']:
            print(f"  {step['order']}. {step['tool_name']}: {step['description']}")

asyncio.run(main())
```

## Best Practices

1. **Be Specific**: Provide detailed task descriptions for better recommendations
2. **Include Context**: Pass available data and constraints for accurate analysis
3. **Use Conversations**: For complex multi-step workflows, use the conversation API
4. **Leverage Autocomplete**: Use autocomplete for faster parameter entry
5. **Review Chains**: Always review generated tool chains before execution

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp-assistant/tools` | GET | List all enhanced tools |
| `/mcp-assistant/tools/{name}` | GET | Get specific tool details |
| `/mcp-assistant/tools/search` | GET | Search tools by keyword |
| `/mcp-assistant/analyze` | POST | Analyze task and get recommendations |
| `/mcp-assistant/recommend` | GET | Quick tool recommendations |
| `/mcp-assistant/explain` | POST | Get detailed tool explanation |
| `/mcp-assistant/explain/{name}` | GET | Quick tool explanation |
| `/mcp-assistant/chains` | POST | Create a tool chain |
| `/mcp-assistant/chains` | GET | List all chains |
| `/mcp-assistant/chains/{id}` | GET | Get specific chain |
| `/mcp-assistant/invoke` | POST | Smart tool invocation |
| `/mcp-assistant/autocomplete` | POST | Get parameter suggestions |
| `/mcp-assistant/conversations` | POST | Start conversation |
| `/mcp-assistant/conversations/{id}/messages` | POST | Send message |
| `/mcp-assistant/conversations/{id}` | GET | Get conversation state |
| `/mcp-assistant/conversations/{id}` | DELETE | End conversation |
| `/mcp-assistant/categories` | GET | List tool categories |
