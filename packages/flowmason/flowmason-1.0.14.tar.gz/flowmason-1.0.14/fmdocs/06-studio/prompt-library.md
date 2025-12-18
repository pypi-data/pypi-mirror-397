# Prompt Library

FlowMason Studio includes a prompt library for managing reusable prompt templates that can be shared across stages and pipelines.

## Overview

The prompt library allows you to:
- Create and manage reusable prompt templates
- Use variables for dynamic content
- Share prompts across your organization
- Track usage and versioning
- Set recommended model parameters

## Creating Prompts

### Basic Template

```bash
curl -X POST http://localhost:8999/api/v1/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "summarizer",
    "content": "Summarize the following {{content_type}} in {{language}}:\n\n{{content}}",
    "description": "Summarize any content type",
    "category": "summarization",
    "tags": ["summary", "content"],
    "default_values": {
      "language": "English",
      "content_type": "text"
    }
  }'
```

### With System Prompt

```bash
curl -X POST http://localhost:8999/api/v1/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "code-reviewer",
    "system_prompt": "You are an expert code reviewer with deep knowledge of {{language}} best practices.",
    "content": "Review the following code for bugs, security issues, and improvements:\n\n```{{language}}\n{{code}}\n```",
    "category": "code-review",
    "recommended_model": "claude-3-5-sonnet-latest",
    "temperature": 0.3
  }'
```

## Variable Syntax

Use `{{variable_name}}` for dynamic content:

```
Extract {{entity_type}} entities from the following text:

{{input_text}}

Return the results as {{output_format}}.
```

Variables are automatically detected and listed in the `variables` field.

## Rendering Prompts

Substitute variables to get the final prompt:

```bash
curl -X POST http://localhost:8999/api/v1/prompts/{prompt_id}/render \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "content_type": "article",
      "language": "French",
      "content": "The quick brown fox..."
    }
  }'
```

Response:
```json
{
  "content": "Summarize the following article in French:\n\nThe quick brown fox...",
  "system_prompt": null
}
```

## Using in Pipelines

Reference prompts in your pipeline stages:

```json
{
  "id": "summarize",
  "component_type": "generator",
  "config": {
    "prompt_template_id": "prompt-abc123",
    "variables": {
      "content": "{{stages.fetch-data.output.text}}",
      "language": "Spanish"
    }
  }
}
```

Or by name:
```json
{
  "config": {
    "prompt_template_name": "summarizer",
    "variables": { ... }
  }
}
```

## Listing Prompts

### All Prompts

```bash
curl http://localhost:8999/api/v1/prompts
```

### By Category

```bash
curl "http://localhost:8999/api/v1/prompts?category=summarization"
```

### Search

```bash
curl "http://localhost:8999/api/v1/prompts?search=code"
```

### List Categories

```bash
curl http://localhost:8999/api/v1/prompts/categories
```

## Getting Prompts

### By ID

```bash
curl http://localhost:8999/api/v1/prompts/{prompt_id}
```

### By Name

```bash
curl http://localhost:8999/api/v1/prompts/by-name/summarizer
```

## Updating Prompts

```bash
curl -X PATCH http://localhost:8999/api/v1/prompts/{prompt_id} \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated prompt content with {{new_variable}}",
    "temperature": 0.7
  }'
```

Updates automatically increment the version number.

## Duplicating Prompts

Copy a prompt (including public prompts from other orgs):

```bash
curl -X POST "http://localhost:8999/api/v1/prompts/{prompt_id}/duplicate?name=my-copy"
```

## Deleting Prompts

```bash
curl -X DELETE http://localhost:8999/api/v1/prompts/{prompt_id}
```

## Prompt Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `name` | string | Template name |
| `content` | string | Prompt text with `{{variables}}` |
| `system_prompt` | string | Optional system prompt |
| `description` | string | Human-readable description |
| `category` | string | Category for organization |
| `tags` | array | Tags for filtering |
| `variables` | array | Auto-extracted variable names |
| `default_values` | object | Default variable values |
| `recommended_model` | string | Suggested model ID |
| `temperature` | number | Suggested temperature (0-2) |
| `max_tokens` | number | Suggested max tokens |
| `version` | string | Semantic version |
| `usage_count` | number | Times rendered |
| `is_public` | boolean | Visible to all organizations |
| `is_featured` | boolean | Featured in gallery |

## Categories

Common prompt categories:
- `extraction` - Extract structured data
- `generation` - Generate content
- `summarization` - Summarize content
- `translation` - Translate text
- `analysis` - Analyze data/text
- `code-review` - Review code
- `code-generation` - Generate code
- `classification` - Classify content
- `qa` - Question answering
- `chat` - Conversational prompts

## Sharing Prompts

### Public Prompts

Make a prompt available to all organizations:

```bash
curl -X PATCH http://localhost:8999/api/v1/prompts/{prompt_id} \
  -H "Content-Type: application/json" \
  -d '{"is_public": true}'
```

Public prompts:
- Are visible to all organizations
- Can be duplicated by anyone
- Cannot be modified by other organizations

### Private Prompts

By default, prompts are private to your organization.

## Best Practices

1. **Use descriptive names**: `extract-customer-info` > `prompt1`
2. **Document variables**: Include examples in the description
3. **Set sensible defaults**: Provide default_values where possible
4. **Choose appropriate categories**: Makes browsing easier
5. **Include model recommendations**: Help users get best results
6. **Version your changes**: The system auto-versions on update

## Example Prompts

### Entity Extraction

```json
{
  "name": "extract-entities",
  "content": "Extract all {{entity_types}} from the following text. Return as JSON array.\n\nText: {{text}}\n\nEntities:",
  "category": "extraction",
  "default_values": {
    "entity_types": "person names, organizations, and locations"
  },
  "recommended_model": "claude-3-5-sonnet-latest",
  "temperature": 0
}
```

### Code Explanation

```json
{
  "name": "explain-code",
  "system_prompt": "You are a patient teacher who explains code clearly.",
  "content": "Explain what this {{language}} code does, step by step:\n\n```{{language}}\n{{code}}\n```",
  "category": "code-review",
  "default_values": {
    "language": "Python"
  }
}
```

### Translation

```json
{
  "name": "translator",
  "content": "Translate the following text from {{source_language}} to {{target_language}}. Preserve formatting.\n\nText: {{text}}\n\nTranslation:",
  "category": "translation",
  "default_values": {
    "source_language": "English"
  }
}
```

## Database Storage

Prompts are stored in the `prompt_templates` table with support for both SQLite (development) and PostgreSQL (production). Variables are automatically extracted and stored for quick reference.
