# Input/Output Architecture

FlowMason supports flexible input and output routing for pipelines, enabling:
- Named pipeline invocation (call by name, not ID)
- Declarative output routing (designer defaults + caller overrides)
- Multiple destination types (webhook, email, database, message queue)
- Per-org security via allowlists

## Named Pipeline Invocation

Pipelines can be invoked by name with optional version pinning:

```bash
POST /api/v1/run
{
  "pipeline": "customer-support-triage",       # Latest version
  "input": { "ticket_id": "T-123", "message": "..." }
}

# Or with version pinning:
POST /api/v1/run
{
  "pipeline": "customer-support-triage@1.0.0", # Specific version
  "input": { "ticket_id": "T-123", "message": "..." }
}
```

### RunPipelineRequest

| Field | Type | Description |
|-------|------|-------------|
| `pipeline` | string | Pipeline name with optional version: `"my-pipeline"` or `"my-pipeline@1.0.0"` |
| `input` | object | Pipeline input data |
| `output_config` | PipelineOutputConfig | Optional caller-specified output configuration |
| `async_mode` | boolean | If true (default), returns immediately with run_id |
| `callback_url` | string | Shorthand for adding a webhook destination |

### RunPipelineResponse

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | Unique run identifier |
| `pipeline_id` | string | Resolved pipeline ID |
| `pipeline_name` | string | Pipeline name |
| `pipeline_version` | string | Pipeline version |
| `status` | RunStatus | Current run status |
| `result` | any | Pipeline result (only if async_mode=false) |
| `delivery_report` | OutputDeliveryReport | Delivery results (only if async_mode=false) |

## Output Destinations

### Destination Types

FlowMason supports four output destination types:

#### Webhook

Send results via HTTP POST/PUT:

```json
{
  "id": "crm-webhook",
  "type": "webhook",
  "name": "Update CRM",
  "config": {
    "url": "https://api.salesforce.com/webhook",
    "method": "POST",
    "headers": { "Authorization": "Bearer {{env.SF_TOKEN}}" },
    "timeout_ms": 30000,
    "retry_count": 3
  },
  "on_success": true,
  "on_error": false
}
```

#### Email

Send notifications via email:

```json
{
  "id": "ops-email",
  "type": "email",
  "name": "Alert Ops Team",
  "config": {
    "to": ["ops@company.com"],
    "cc": ["manager@company.com"],
    "subject_template": "Pipeline {{pipeline_name}} completed",
    "body_template": "Result: {{result | tojson}}",
    "is_html": false
  },
  "on_success": false,
  "on_error": true
}
```

#### Database

Store results in a database:

```json
{
  "id": "results-db",
  "type": "database",
  "name": "Store in Analytics DB",
  "config": {
    "connection_id": "conn_abc123",
    "table": "pipeline_results",
    "operation": "insert",
    "column_mapping": {
      "run_id": "run_id",
      "output": "result_json",
      "completed_at": "timestamp"
    }
  },
  "on_success": true
}
```

#### Message Queue

Publish to a message queue:

```json
{
  "id": "kafka-events",
  "type": "message_queue",
  "name": "Publish to Kafka",
  "config": {
    "connection_id": "conn_kafka_prod",
    "queue_name": "pipeline-events",
    "message_template": "{{ result | tojson }}"
  },
  "on_success": true
}
```

### OutputDestination Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique destination identifier |
| `type` | enum | `webhook`, `email`, `database`, `message_queue` |
| `name` | string | Human-readable name |
| `enabled` | boolean | Whether destination is active (default: true) |
| `config` | object | Type-specific configuration |
| `on_success` | boolean | Deliver on successful completion (default: true) |
| `on_error` | boolean | Deliver on pipeline error (default: false) |
| `error_types` | string[] | Filter error delivery to specific types |
| `payload_template` | string | Jinja2 template to transform output |

## Pipeline Output Configuration

Pipelines can define default output destinations that run automatically:

```json
{
  "name": "customer-support-triage",
  "version": "1.0.0",
  "output_config": {
    "destinations": [
      {
        "id": "webhook-crm",
        "type": "webhook",
        "name": "Update CRM",
        "on_success": true,
        "config": { "url": "https://api.salesforce.com/webhook" }
      },
      {
        "id": "email-ops",
        "type": "email",
        "name": "Alert Ops Team",
        "on_error": true,
        "error_types": ["TIMEOUT", "CONNECTIVITY"],
        "config": { "to": ["ops@company.com"] }
      }
    ],
    "allow_caller_destinations": true,
    "allow_caller_override": false
  },
  "stages": [...]
}
```

### Config Merging

| Pipeline Config | Caller Behavior |
|-----------------|-----------------|
| `allow_caller_destinations: true` | Caller destinations are added to designer defaults |
| `allow_caller_destinations: false` | Caller destinations are ignored |
| `allow_caller_override: true` | Caller can replace all designer defaults |
| `allow_caller_override: false` | Designer defaults always run |

## Security: Allowlist System

All output destinations must be pre-approved in the organization's allowlist.

### Allowlist Entry Types

| Type | Pattern Example | Description |
|------|-----------------|-------------|
| `webhook_domain` | `*.salesforce.com` | Allow any subdomain |
| `webhook_url` | `https://api.example.com/webhook` | Exact URL match |
| `email_domain` | `@company.com` | Allow emails to domain |
| `database_connection` | `conn_abc123` | Reference stored connection |
| `message_queue_connection` | `conn_kafka_prod` | Reference stored connection |

### Allowlist API

```bash
# Create allowlist entry
POST /api/v1/allowlist
{
  "entry_type": "webhook_domain",
  "pattern": "*.salesforce.com",
  "description": "Salesforce webhooks"
}

# List entries
GET /api/v1/allowlist

# Validate a destination
POST /api/v1/allowlist/validate
{
  "destination_type": "webhook",
  "config": { "url": "https://api.salesforce.com/webhook" }
}
# Response: { "is_allowed": true, "matched_entry": "allow_xxx" }

# Delete entry
DELETE /api/v1/allowlist/{id}
```

## Stored Connections

Database and message queue destinations use stored connections for secure credential management.

### Connection Types

- `postgresql`, `mysql`, `mongodb` - Database connections
- `kafka`, `rabbitmq`, `sqs`, `redis` - Message queue connections

### Connections API

```bash
# Create stored connection
POST /api/v1/connections
{
  "name": "Production PostgreSQL",
  "connection_type": "postgresql",
  "host": "db.example.com",
  "port": 5432,
  "database": "analytics",
  "username": "pipeline_user",
  "password": "secret123",
  "ssl_enabled": true
}

# List connections (credentials hidden)
GET /api/v1/connections

# Test connection
POST /api/v1/connections/{id}/test

# Delete connection
DELETE /api/v1/connections/{id}
```

## Delivery Logging

All output deliveries are logged for observability:

```bash
# Get delivery log for a run
GET /api/v1/deliveries/{run_id}

# Response:
{
  "run_id": "run_abc123",
  "deliveries": [
    {
      "destination_id": "webhook-crm",
      "destination_type": "webhook",
      "status": "success",
      "response_code": 200,
      "started_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:30:01Z",
      "retry_count": 0
    },
    {
      "destination_id": "email-ops",
      "destination_type": "email",
      "status": "skipped",
      "error": "on_error=true but pipeline succeeded"
    }
  ]
}
```

## OutputRouterOperator

For routing within pipelines, use the `OutputRouterOperator`:

```python
from flowmason_lab.operators import OutputRouterOperator

# In a pipeline stage:
{
  "id": "send-results",
  "component_type": "output_router",
  "config": {
    "data": "{{previous_stage.output}}",
    "destinations": [
      {
        "id": "webhook-1",
        "type": "webhook",
        "name": "CRM Webhook",
        "config": { "url": "https://api.example.com/webhook" }
      }
    ],
    "parallel": true,
    "fail_on_error": false
  }
}
```

## ErrorRouterOperator

For error notifications in TryCatch handlers:

```python
from flowmason_lab.operators import ErrorRouterOperator

# In a TryCatch error handler:
{
  "id": "notify-error",
  "component_type": "error_router",
  "config": {
    "error_type": "{{error.type}}",
    "error_message": "{{error.message}}",
    "stage_id": "{{error.stage_id}}",
    "severity": "critical",
    "destinations": [
      {
        "id": "pagerduty",
        "type": "webhook",
        "name": "PagerDuty Alert",
        "config": { "url": "https://events.pagerduty.com/v2/enqueue" }
      }
    ]
  }
}
```

## Complete Example

```bash
# 1. Set up allowlist (admin)
POST /api/v1/allowlist
{ "entry_type": "webhook_domain", "pattern": "*.myapp.com" }

# 2. Create pipeline with output config (designer)
POST /api/v1/pipelines
{
  "name": "order-processor",
  "output_config": {
    "destinations": [
      { "id": "default-webhook", "type": "webhook", "config": {"url": "https://api.myapp.com/orders"} }
    ],
    "allow_caller_destinations": true
  },
  "stages": [...]
}

# 3. Run pipeline with caller webhook (caller)
POST /api/v1/run
{
  "pipeline": "order-processor",
  "input": { "order_id": "ORD-123" },
  "output_config": {
    "destinations": [
      { "id": "my-callback", "type": "webhook", "config": {"url": "https://callback.myapp.com/done"} }
    ]
  }
}
# Both default-webhook AND my-callback will receive the result
```
