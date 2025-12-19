# Template Gallery

FlowMason Studio includes a built-in template gallery with starter pipelines for common use cases. Templates provide a quick way to get started with new pipelines.

## Overview

Templates are pre-built pipeline configurations that you can:
- Browse by category or search by keyword
- Preview to understand the pipeline structure
- Create new pipelines from with one click
- Customize after creation

## Browsing Templates

### List All Templates

```bash
curl http://localhost:8999/api/v1/gallery/templates
```

Response:
```json
[
  {
    "id": "blog-post-generator",
    "name": "Blog Post Generator",
    "description": "Generate well-structured blog posts on any topic",
    "category": "content",
    "tags": ["writing", "blog", "content-generation"],
    "difficulty": "beginner",
    "estimated_time": "5 minutes",
    "use_case": "Creating blog posts, articles, or long-form content"
  }
]
```

### Filter by Category

```bash
curl "http://localhost:8999/api/v1/gallery/templates?category=content"
```

### Filter by Difficulty

```bash
curl "http://localhost:8999/api/v1/gallery/templates?difficulty=beginner"
```

### Search Templates

```bash
curl "http://localhost:8999/api/v1/gallery/templates?search=code"
```

## Template Categories

### List Categories

```bash
curl http://localhost:8999/api/v1/gallery/templates/categories
```

Response:
```json
[
  {"name": "analysis", "count": 2},
  {"name": "automation", "count": 2},
  {"name": "content", "count": 2},
  {"name": "data", "count": 2},
  {"name": "development", "count": 2}
]
```

### Available Categories

| Category | Description |
|----------|-------------|
| `content` | Content generation (blog posts, emails) |
| `data` | Data processing and transformation |
| `analysis` | Text analysis (sentiment, summarization) |
| `automation` | API chains and webhook processing |
| `development` | Code review and explanation |

## Template Tags

List all available tags for filtering:

```bash
curl http://localhost:8999/api/v1/gallery/templates/tags
```

## Getting Template Details

### Full Template

```bash
curl http://localhost:8999/api/v1/gallery/templates/blog-post-generator
```

Response includes:
- Full pipeline definition with all stages
- Sample input for testing
- Documentation and prerequisites

### Preview Only

Get a simplified view of the pipeline structure:

```bash
curl http://localhost:8999/api/v1/gallery/templates/blog-post-generator/preview
```

Response:
```json
{
  "name": "Blog Post Generator",
  "description": "Generate a blog post with outline, draft, and review",
  "stages": [
    {"id": "outline", "component_type": "generator", "depends_on": []},
    {"id": "draft", "component_type": "generator", "depends_on": ["outline"]},
    {"id": "review", "component_type": "critic", "depends_on": ["draft"]}
  ],
  "input_schema": {...},
  "sample_input": {...}
}
```

## Creating Pipelines from Templates

Create a new pipeline from a template:

```bash
curl -X POST http://localhost:8999/api/v1/gallery/templates/blog-post-generator/create-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Blog Pipeline",
    "description": "Custom blog post generator"
  }'
```

Response:
```json
{
  "pipeline_id": "abc123...",
  "name": "My Blog Pipeline",
  "message": "Pipeline created from template 'Blog Post Generator'"
}
```

The created pipeline is fully editable in Studio.

## Built-in Templates

### Content Templates

#### Blog Post Generator
- **ID**: `blog-post-generator`
- **Difficulty**: Beginner
- **Stages**: outline → draft → review
- **Use case**: Creating blog posts, articles, or long-form content

#### Professional Email Writer
- **ID**: `email-writer`
- **Difficulty**: Beginner
- **Stages**: write-email
- **Use case**: Writing business emails, follow-ups, or formal communications

### Data Templates

#### Document Data Extractor
- **ID**: `data-extractor`
- **Difficulty**: Intermediate
- **Stages**: extract → parse → validate
- **Use case**: Extracting specific information from documents, emails, or reports

#### CSV Data Transformer
- **ID**: `csv-transformer`
- **Difficulty**: Intermediate
- **Stages**: load → transform (foreach) → enrich-row
- **Use case**: Processing CSV files, adding computed fields, or enriching data

### Analysis Templates

#### Sentiment Analyzer
- **ID**: `sentiment-analyzer`
- **Difficulty**: Beginner
- **Stages**: analyze → parse
- **Use case**: Analyzing customer feedback, reviews, or social media posts

#### Smart Text Summarizer
- **ID**: `text-summarizer`
- **Difficulty**: Beginner
- **Stages**: summarize
- **Use case**: Summarizing articles, documents, or meeting notes

### Automation Templates

#### API Data Chain
- **ID**: `api-chain`
- **Difficulty**: Intermediate
- **Stages**: fetch-primary → transform → fetch-secondary
- **Use case**: Integrating multiple APIs in a single workflow

#### Webhook Processor
- **ID**: `webhook-processor`
- **Difficulty**: Intermediate
- **Stages**: validate → route → (process-order | process-support | log-unknown)
- **Use case**: Processing webhooks from external services

### Development Templates

#### AI Code Reviewer
- **ID**: `code-reviewer`
- **Difficulty**: Intermediate
- **Stages**: analyze → summarize
- **Use case**: Automated code review for PRs or code audits

#### Code Explainer
- **ID**: `code-explainer`
- **Difficulty**: Beginner
- **Stages**: explain
- **Use case**: Understanding unfamiliar code or creating documentation

## Difficulty Levels

| Level | Description |
|-------|-------------|
| `beginner` | Simple pipelines, easy to understand and modify |
| `intermediate` | Multiple stages with dependencies, some configuration needed |
| `advanced` | Complex workflows, requires understanding of advanced features |

## Template Structure

Each template includes:

| Field | Description |
|-------|-------------|
| `id` | Unique identifier |
| `name` | Display name |
| `description` | Short description |
| `category` | Category for organization |
| `tags` | Keywords for search |
| `difficulty` | beginner/intermediate/advanced |
| `estimated_time` | Approximate setup time |
| `use_case` | When to use this template |
| `pipeline` | Full pipeline definition |
| `sample_input` | Example input for testing |
| `documentation` | Detailed usage instructions |
| `prerequisites` | Required API keys or setup |

## Best Practices

1. **Start Simple**: Begin with beginner templates to learn the patterns
2. **Use Sample Input**: Test templates with provided sample input first
3. **Customize Gradually**: Make small changes and test after each modification
4. **Check Prerequisites**: Ensure you have required API keys configured
5. **Read Documentation**: Each template includes usage documentation
