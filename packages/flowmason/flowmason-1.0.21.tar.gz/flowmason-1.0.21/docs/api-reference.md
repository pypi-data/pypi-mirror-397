# FlowMason API Reference

Base URL: `http://localhost:8999/api/v1`

## Authentication

All API endpoints support optional JWT authentication via Supabase.

```
Authorization: Bearer <jwt_token>
```

In development mode, authentication is optional.

---

## Registry API

Manage component packages in the registry.

### List Components

```
GET /registry/components
```

Query parameters:
- `kind` (optional): Filter by "node" or "operator"
- `category` (optional): Filter by category name

Response:
```json
{
  "components": [
    {
      "component_type": "generator",
      "component_kind": "node",
      "category": "core",
      "description": "Generate text from prompts",
      "version": "1.0.0",
      "icon": "sparkles",
      "color": "#8B5CF6",
      "author": "FlowMason",
      "tags": ["text", "generation", "llm"],
      "input_schema": { ... },
      "output_schema": { ... },
      "requires_llm": true,
      "package_name": "generator",
      "package_version": "1.0.0",
      "is_available": true
    }
  ],
  "count": 12
}
```

### Get Component Details

```
GET /registry/components/{component_type}
```

Response:
```json
{
  "component_type": "generator",
  "component_kind": "node",
  "category": "core",
  "description": "Generate text from prompts",
  "version": "1.0.0",
  "input_schema": {
    "type": "object",
    "properties": {
      "prompt": { "type": "string", "description": "The prompt" },
      "max_tokens": { "type": "integer", "default": 1000 }
    },
    "required": ["prompt"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "content": { "type": "string" },
      "tokens_used": { "type": "integer" }
    }
  },
  "recommended_providers": {
    "anthropic": { "model": "claude-3-5-sonnet-20241022" }
  }
}
```

### Deploy Package

```
POST /registry/deploy
Content-Type: multipart/form-data
```

Form data:
- `package`: The `.fmpkg` file

Response:
```json
{
  "success": true,
  "component_type": "my_component",
  "version": "1.0.0",
  "message": "Package deployed successfully"
}
```

### Unregister Component

```
DELETE /registry/components/{component_type}
```

Response:
```json
{
  "success": true,
  "message": "Component unregistered"
}
```

### Refresh Registry

```
POST /registry/refresh
```

Rescans the packages directory and reloads all packages.

Response:
```json
{
  "success": true,
  "components_loaded": 12
}
```

### Registry Statistics

```
GET /registry/stats
```

Response:
```json
{
  "total_components": 12,
  "total_packages": 12,
  "nodes": 5,
  "operators": 7,
  "categories": {
    "core": 5,
    "transform": 3,
    "control": 2,
    "data": 2
  }
}
```

---

## Pipelines API

Create and manage pipelines.

### List Pipelines

```
GET /pipelines
```

Query parameters:
- `category` (optional): Filter by category
- `search` (optional): Search in name/description
- `limit` (optional, default: 50): Max results
- `offset` (optional, default: 0): Pagination offset

Response:
```json
{
  "pipelines": [
    {
      "id": "pipeline_abc123",
      "name": "Customer Support Triage",
      "description": "Triage incoming support tickets",
      "version": "1.0.0",
      "category": "support",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### Create Pipeline

```
POST /pipelines
Content-Type: application/json
```

Request body:
```json
{
  "name": "Customer Support Triage",
  "description": "Triage incoming support tickets",
  "version": "1.0.0",
  "category": "support",
  "stages": [
    {
      "id": "classify",
      "type": "generator",
      "input_mapping": {
        "prompt": "Classify this ticket: {{input.ticket_text}}"
      },
      "depends_on": []
    },
    {
      "id": "route",
      "type": "json_transform",
      "input_mapping": {
        "data": "{{upstream.classify.content}}",
        "mappings": {"category": "$.classification"}
      },
      "depends_on": ["classify"]
    }
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "ticket_text": { "type": "string" }
    },
    "required": ["ticket_text"]
  },
  "output_stage_id": "route"
}
```

Response:
```json
{
  "id": "pipeline_abc123",
  "name": "Customer Support Triage",
  "version": "1.0.0",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Pipeline

```
GET /pipelines/{pipeline_id}
```

Response:
```json
{
  "id": "pipeline_abc123",
  "name": "Customer Support Triage",
  "description": "Triage incoming support tickets",
  "version": "1.0.0",
  "category": "support",
  "stages": [ ... ],
  "input_schema": { ... },
  "output_stage_id": "route",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Update Pipeline

```
PUT /pipelines/{pipeline_id}
Content-Type: application/json
```

Request body (partial update):
```json
{
  "name": "Updated Name",
  "stages": [ ... ]
}
```

Response:
```json
{
  "id": "pipeline_abc123",
  "name": "Updated Name",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### Delete Pipeline

```
DELETE /pipelines/{pipeline_id}
```

Response:
```json
{
  "success": true,
  "message": "Pipeline deleted"
}
```

### Clone Pipeline

```
POST /pipelines/{pipeline_id}/clone
Content-Type: application/json
```

Request body (optional):
```json
{
  "name": "Cloned Pipeline Name"
}
```

Response:
```json
{
  "id": "pipeline_xyz789",
  "name": "Cloned Pipeline Name",
  "created_at": "2024-01-15T11:00:00Z"
}
```

### Validate Pipeline

```
POST /pipelines/{pipeline_id}/validate
```

Validates the pipeline configuration without executing.

Response:
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [
    {
      "stage_id": "route",
      "field": "timeout",
      "message": "Using default timeout of 60s"
    }
  ]
}
```

### Test Pipeline

```
POST /pipelines/{pipeline_id}/test
Content-Type: application/json
```

Runs a test execution of the pipeline. A successful test is required before publishing.

Request body (optional):
```json
{
  "sample_input": {
    "ticket_text": "Test input for the pipeline"
  }
}
```

Response:
```json
{
  "success": true,
  "test_run_id": "test_abc123",
  "output": {
    "category": "support",
    "priority": "medium"
  },
  "execution_time_ms": 1234,
  "usage": {
    "total_tokens": 500,
    "total_cost": 0.005
  }
}
```

Error response (test failed):
```json
{
  "success": false,
  "test_run_id": "test_abc123",
  "error": "Stage 'classify' failed: Invalid prompt template",
  "stage_id": "classify"
}
```

### Publish Pipeline

```
POST /pipelines/{pipeline_id}/publish
Content-Type: application/json
```

Publishes a pipeline, making it available for production use. Requires a successful test run.

Request body:
```json
{
  "test_run_id": "test_abc123"
}
```

Response:
```json
{
  "success": true,
  "pipeline_id": "pipeline_abc123",
  "status": "published",
  "published_at": "2024-01-15T12:00:00Z",
  "version": "1.0.0"
}
```

Error response (no valid test):
```json
{
  "success": false,
  "error": "Pipeline must pass a test before publishing. Run POST /pipelines/{id}/test first."
}
```

### Unpublish Pipeline

```
POST /pipelines/{pipeline_id}/unpublish
```

Reverts a published pipeline to draft status.

Response:
```json
{
  "success": true,
  "pipeline_id": "pipeline_abc123",
  "status": "draft",
  "unpublished_at": "2024-01-15T13:00:00Z"
}
```

---

## Pipeline Status

Pipelines have a `status` field that follows a Salesforce Flow-like lifecycle:

| Status | Description |
|--------|-------------|
| `draft` | Pipeline is being developed. Can be edited freely. |
| `published` | Pipeline has passed testing and is production-ready. |

**Publishing Workflow:**
1. Create/edit pipeline (status: `draft`)
2. Run test via `POST /pipelines/{id}/test`
3. If test passes, publish via `POST /pipelines/{id}/publish`
4. Pipeline status changes to `published`

**Note:** Published pipelines should only execute in production environments. Draft pipelines are for development and testing.

---

## Execution API

Run pipelines and manage execution runs.

### Run Pipeline

```
POST /pipelines/{pipeline_id}/run
Content-Type: application/json
```

Request body:
```json
{
  "input": {
    "ticket_text": "My order hasn't arrived yet"
  },
  "options": {
    "timeout_seconds": 120,
    "provider_overrides": {
      "anthropic": { "model": "claude-3-opus-20240229" }
    }
  }
}
```

Response:
```json
{
  "run_id": "run_abc123",
  "pipeline_id": "pipeline_abc123",
  "status": "completed",
  "output": {
    "category": "shipping",
    "priority": "medium"
  },
  "usage": {
    "total_tokens": 1250,
    "total_cost": 0.0125,
    "execution_time_ms": 2340
  },
  "started_at": "2024-01-15T11:00:00Z",
  "completed_at": "2024-01-15T11:00:02Z"
}
```

### List Runs

```
GET /runs
```

Query parameters:
- `pipeline_id` (optional): Filter by pipeline
- `status` (optional): "running", "completed", "failed", "cancelled"
- `limit` (optional, default: 50)
- `offset` (optional, default: 0)

Response:
```json
{
  "runs": [
    {
      "run_id": "run_abc123",
      "pipeline_id": "pipeline_abc123",
      "status": "completed",
      "started_at": "2024-01-15T11:00:00Z",
      "completed_at": "2024-01-15T11:00:02Z"
    }
  ],
  "total": 1
}
```

### Get Run Status

```
GET /runs/{run_id}
```

Response:
```json
{
  "run_id": "run_abc123",
  "pipeline_id": "pipeline_abc123",
  "status": "completed",
  "input": { ... },
  "output": { ... },
  "error": null,
  "usage": {
    "total_tokens": 1250,
    "total_cost": 0.0125,
    "execution_time_ms": 2340
  },
  "started_at": "2024-01-15T11:00:00Z",
  "completed_at": "2024-01-15T11:00:02Z"
}
```

### Get Run Trace

```
GET /runs/{run_id}/trace
```

Response:
```json
{
  "run_id": "run_abc123",
  "stages": [
    {
      "stage_id": "classify",
      "component_type": "generator",
      "status": "completed",
      "input": { "prompt": "Classify this ticket: ..." },
      "output": { "content": "..." },
      "usage": {
        "input_tokens": 150,
        "output_tokens": 50,
        "duration_ms": 1200
      },
      "started_at": "2024-01-15T11:00:00Z",
      "completed_at": "2024-01-15T11:00:01Z"
    },
    {
      "stage_id": "route",
      "component_type": "json_transform",
      "status": "completed",
      "input": { ... },
      "output": { ... },
      "usage": { "duration_ms": 5 },
      "started_at": "2024-01-15T11:00:01Z",
      "completed_at": "2024-01-15T11:00:01Z"
    }
  ]
}
```

### Cancel Run

```
POST /runs/{run_id}/cancel
```

Response:
```json
{
  "success": true,
  "run_id": "run_abc123",
  "status": "cancelled"
}
```

### Delete Run

```
DELETE /runs/{run_id}
```

Response:
```json
{
  "success": true,
  "message": "Run deleted"
}
```

---

## Providers API

Manage LLM providers for pipeline execution.

### List Providers

```
GET /providers
```

Response:
```json
{
  "providers": [
    {
      "name": "anthropic",
      "display_name": "Anthropic",
      "default_model": "claude-sonnet-4-20250514",
      "available_models": [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022"
      ],
      "capabilities": ["text_generation", "streaming", "vision", "tool_use"],
      "configured": true
    },
    {
      "name": "openai",
      "display_name": "OpenAI",
      "default_model": "gpt-4o",
      "available_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
      "capabilities": ["text_generation", "streaming", "vision", "tool_use"],
      "configured": false
    }
  ],
  "count": 4
}
```

### Get Provider Models

```
GET /providers/{provider_name}/models
```

Response:
```json
{
  "provider": "anthropic",
  "models": [
    {
      "id": "claude-sonnet-4-20250514",
      "name": "Claude Sonnet 4",
      "is_default": true
    },
    {
      "id": "claude-opus-4-20250514",
      "name": "Claude Opus 4",
      "is_default": false
    }
  ],
  "default_model": "claude-sonnet-4-20250514"
}
```

### Test Provider Connection

```
POST /providers/{provider_name}/test
Content-Type: application/json
```

Request body (optional):
```json
{
  "model": "claude-sonnet-4-20250514"
}
```

Response:
```json
{
  "success": true,
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  "message": "Connection successful",
  "response_time_ms": 523
}
```

Error response (API key not configured):
```json
{
  "success": false,
  "provider": "anthropic",
  "model": null,
  "message": "API key not configured. Set ANTHROPIC_API_KEY environment variable.",
  "response_time_ms": null
}
```

### List Capabilities

```
GET /providers/capabilities
```

Response:
```json
{
  "capabilities": [
    {
      "name": "text_generation",
      "description": "Generate text from prompts"
    },
    {
      "name": "streaming",
      "description": "Stream responses token by token"
    },
    {
      "name": "vision",
      "description": "Process image inputs"
    },
    {
      "name": "tool_use",
      "description": "Call external tools/functions"
    },
    {
      "name": "embeddings",
      "description": "Generate text embeddings"
    }
  ]
}
```

---

## Templates API

Templates provide pre-built pipeline examples that users can instantiate.

### List Templates

```
GET /templates
```

Query parameters:
- `category` (optional): Filter by category (e.g., "getting-started", "salesforce")
- `difficulty` (optional): Filter by difficulty ("beginner", "intermediate", "advanced")

Response:
```json
{
  "templates": [
    {
      "id": "hello-world",
      "name": "Hello World",
      "description": "Simple text generation pipeline",
      "version": "1.0.0",
      "stage_count": 1,
      "category": "getting-started",
      "tags": ["beginner", "text"],
      "difficulty": "beginner",
      "use_cases": ["Learn basic pipeline structure"],
      "source": "builtin",
      "is_template": true
    }
  ],
  "total": 10,
  "by_category": {
    "getting-started": [...],
    "content-creation": [...],
    "salesforce": [...]
  },
  "categories": ["getting-started", "content-creation", "salesforce", "data-integration"]
}
```

### Get Template Details

```
GET /templates/{template_id}
```

Response:
```json
{
  "id": "lead-qualification",
  "name": "Lead Qualification Pipeline",
  "description": "Analyze Salesforce leads and score them for sales readiness",
  "version": "1.0.0",
  "category": "salesforce",
  "difficulty": "intermediate",
  "use_cases": [
    "Automatically score inbound leads",
    "Prioritize sales outreach"
  ],
  "stages": [
    {
      "id": "fetch-lead",
      "component_type": "http-request",
      "name": "Fetch Lead Data",
      "config": {...}
    },
    {
      "id": "analyze",
      "component_type": "generator",
      "name": "Analyze Lead",
      "depends_on": ["fetch-lead"]
    }
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "lead_id": {"type": "string", "description": "Salesforce Lead ID"}
    },
    "required": ["lead_id"]
  },
  "output_stage_id": "analyze"
}
```

### Instantiate Template

```
POST /templates/{template_id}/instantiate
```

Query parameters:
- `name` (optional): Name for the new pipeline (default: template name + timestamp)

Creates a new pipeline from the template.

Response:
```json
{
  "id": "pipeline_xyz789",
  "name": "Lead Qualification Pipeline",
  "status": "draft",
  "created_from_template": "lead-qualification",
  "created_at": "2024-01-15T12:00:00Z"
}
```

### List Template Categories

```
GET /templates/categories/list
```

Response:
```json
{
  "categories": [
    {
      "id": "getting-started",
      "name": "Getting Started",
      "icon": "rocket",
      "count": 2
    },
    {
      "id": "salesforce",
      "name": "Salesforce & CRM",
      "icon": "cloud",
      "count": 4
    }
  ],
  "total": 6
}
```

---

## Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "registry": {
    "components_loaded": 12,
    "packages_loaded": 12
  },
  "database": "connected"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid pipeline configuration",
    "details": {
      "field": "stages[0].type",
      "issue": "Unknown component type: 'unknown_component'"
    }
  }
}
```

Common error codes:
- `VALIDATION_ERROR` (400): Invalid request data
- `NOT_FOUND` (404): Resource not found
- `UNAUTHORIZED` (401): Missing or invalid authentication
- `FORBIDDEN` (403): Insufficient permissions
- `INTERNAL_ERROR` (500): Server error

---

## Rate Limits

Default rate limits:
- 100 requests/minute per IP (unauthenticated)
- 1000 requests/minute per user (authenticated)
- Pipeline execution: 10 concurrent runs per user

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705320000
```

---

## WebSocket API (Streaming)

For real-time execution updates:

```
WS /ws/runs/{run_id}
```

Messages:
```json
{"type": "stage_started", "stage_id": "classify", "timestamp": "..."}
{"type": "stage_completed", "stage_id": "classify", "output": {...}}
{"type": "run_completed", "output": {...}, "usage": {...}}
{"type": "run_failed", "error": "..."}
```
