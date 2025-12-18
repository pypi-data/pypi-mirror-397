# Event-Driven Triggers

FlowMason supports event-driven pipeline triggers that automatically execute pipelines in response to various events.

## Overview

Event triggers enable automated pipeline execution based on:
- **File System Events**: Watch for file changes
- **Pipeline Completion**: Chain pipelines together
- **MCP Events**: React to MCP server events
- **Message Queues**: Consume from Redis, RabbitMQ, Kafka, SQS
- **Custom Events**: Internal event emission

## Trigger Types

### File Watch Triggers

Monitor file system changes and trigger pipelines when files are created, modified, or deleted.

```json
{
  "name": "Process New CSV Files",
  "pipeline_id": "pipe_data_import",
  "trigger_type": "file_watch",
  "config": {
    "path": "/data/incoming/*.csv",
    "events": ["created", "modified"],
    "recursive": true,
    "debounce_seconds": 5,
    "ignore_patterns": ["*.tmp", "*.part"]
  },
  "default_inputs": {
    "mode": "batch"
  }
}
```

**Configuration Options:**

| Option | Type | Description |
|--------|------|-------------|
| `path` | string | Glob pattern for files to watch |
| `events` | array | Events to trigger on: `created`, `modified`, `deleted`, `moved` |
| `recursive` | boolean | Watch subdirectories (default: true) |
| `debounce_seconds` | number | Debounce rapid file changes |
| `ignore_patterns` | array | Glob patterns to ignore |

**Input Mapping:**
```json
{
  "input_mapping": {
    "file_path": "$.path",
    "event_type": "$.event"
  }
}
```

### Pipeline Completion Triggers

Chain pipelines by triggering one pipeline when another completes.

```json
{
  "name": "Post-Process Data",
  "pipeline_id": "pipe_post_process",
  "trigger_type": "pipeline_completed",
  "config": {
    "source_pipeline_id": "pipe_data_fetch",
    "status": "success",
    "pass_outputs": true,
    "output_mapping": {
      "raw_data": "processed_data"
    }
  }
}
```

**Configuration Options:**

| Option | Type | Description |
|--------|------|-------------|
| `source_pipeline_id` | string | Pipeline to watch |
| `status` | string | Trigger on: `success`, `failed`, `any` |
| `pass_outputs` | boolean | Pass source outputs as inputs |
| `output_mapping` | object | Map source outputs to target inputs |

### MCP Event Triggers

React to events from MCP servers.

```json
{
  "name": "Process New Orders",
  "pipeline_id": "pipe_order_processor",
  "trigger_type": "mcp_event",
  "config": {
    "server_name": "database",
    "event_type": "row_inserted",
    "filter": {
      "table": "orders",
      "status": "pending"
    },
    "input_mapping": {
      "order_id": "$.id",
      "customer": "$.customer_id"
    }
  }
}
```

**Configuration Options:**

| Option | Type | Description |
|--------|------|-------------|
| `server_name` | string | MCP server name |
| `event_type` | string | Event type to listen for |
| `filter` | object | Filter criteria for events |
| `input_mapping` | object | Map event data to inputs |

### Message Queue Triggers

Consume messages from external queues.

```json
{
  "name": "Process Queue Messages",
  "pipeline_id": "pipe_message_handler",
  "trigger_type": "message_queue",
  "config": {
    "queue_type": "redis",
    "connection_url": "redis://localhost:6379",
    "queue_name": "jobs:pending",
    "ack_mode": "auto",
    "batch_size": 1,
    "input_mapping": {
      "payload": "$.body"
    }
  }
}
```

**Supported Queue Types:**
- `redis`: Redis pub/sub and lists
- `rabbitmq`: RabbitMQ AMQP
- `kafka`: Apache Kafka
- `sqs`: AWS SQS

### Custom Event Triggers

React to internal events emitted via API.

```json
{
  "name": "Handle User Events",
  "pipeline_id": "pipe_user_handler",
  "trigger_type": "custom",
  "config": {
    "endpoint": "user_events",
    "filter": {
      "action": "signup"
    },
    "input_mapping": {
      "user_id": "$.user.id",
      "email": "$.user.email"
    }
  }
}
```

## API Reference

### List Triggers

```http
GET /api/v1/triggers
GET /api/v1/triggers?pipeline_id=pipe_abc&enabled_only=true
GET /api/v1/triggers/pipeline/{pipeline_id}
GET /api/v1/triggers/type/{trigger_type}
```

### Create Trigger

```http
POST /api/v1/triggers
Content-Type: application/json

{
  "name": "My Trigger",
  "pipeline_id": "pipe_abc123",
  "trigger_type": "file_watch",
  "config": {
    "path": "/data/*.json",
    "events": ["created"]
  },
  "enabled": true,
  "max_concurrent": 3,
  "cooldown_seconds": 10,
  "default_inputs": {}
}
```

### Update Trigger

```http
PUT /api/v1/triggers/{trigger_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "enabled": false
}
```

### Delete Trigger

```http
DELETE /api/v1/triggers/{trigger_id}
```

### Control Triggers

```http
POST /api/v1/triggers/{trigger_id}/pause
POST /api/v1/triggers/{trigger_id}/resume
POST /api/v1/triggers/{trigger_id}/test
```

### List Events

```http
GET /api/v1/triggers/events
GET /api/v1/triggers/{trigger_id}/events
GET /api/v1/triggers/events?status=completed&since=2024-01-01T00:00:00Z
```

### Emit Custom Events

```http
POST /api/v1/triggers/emit
Content-Type: application/json

{
  "endpoint": "user_events",
  "data": {
    "action": "signup",
    "user": {
      "id": "user_123",
      "email": "user@example.com"
    }
  }
}
```

### Get Statistics

```http
GET /api/v1/triggers/stats
```

**Response:**
```json
{
  "total_triggers": 15,
  "active_triggers": 12,
  "paused_triggers": 2,
  "error_triggers": 1,
  "total_events_24h": 1547,
  "successful_events_24h": 1520,
  "failed_events_24h": 27,
  "triggers_by_type": {
    "file_watch": 5,
    "pipeline_completed": 7,
    "custom": 3
  }
}
```

## Trigger Settings

### Concurrency Control

```json
{
  "max_concurrent": 5
}
```

Limits how many executions can run simultaneously from this trigger.

### Cooldown

```json
{
  "cooldown_seconds": 30
}
```

Minimum time between trigger fires. Prevents rapid-fire executions.

### Default Inputs

```json
{
  "default_inputs": {
    "mode": "production",
    "retry_count": 3
  }
}
```

Default inputs merged with event-resolved inputs.

## Input Resolution

Inputs are resolved in order of priority:
1. Event data via `input_mapping`
2. Default inputs from trigger config
3. Trigger metadata (`_trigger_event`)

### Path Expressions

Input mapping uses JSONPath-like expressions:

```json
{
  "input_mapping": {
    "user_id": "$.data.user.id",
    "items": "$.data.order.items",
    "first_item": "$.data.order.items.0"
  }
}
```

### Trigger Metadata

Every triggered execution receives:

```json
{
  "_trigger_event": {
    "trigger_id": "trig_abc123",
    "event_type": "file_created",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Python Integration

### Direct Service Usage

```python
from flowmason_studio.services.trigger_service import get_trigger_service
from flowmason_studio.services.trigger_storage import get_trigger_storage
from flowmason_studio.models.triggers import TriggerType

# Create trigger
storage = get_trigger_storage()
trigger = storage.create_trigger(
    name="Process Files",
    pipeline_id="pipe_processor",
    trigger_type=TriggerType.FILE_WATCH,
    config={
        "path": "/data/*.json",
        "events": ["created"],
    },
)

# Emit custom event
service = get_trigger_service()
await service.emit_custom_event(
    endpoint="my_events",
    event_data={"action": "test", "value": 42},
)

# Notify pipeline completion
await service.notify_pipeline_completed(
    pipeline_id="pipe_source",
    run_id="run_123",
    status="success",
    outputs={"result": "data"},
)
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWMASON_TRIGGERS_ENABLED` | `true` | Enable trigger service |

## Error Handling

When a trigger encounters an error:
1. Trigger status changes to `error`
2. Error message is recorded
3. Events continue to be logged

To recover:
```http
POST /api/v1/triggers/{trigger_id}/resume
```

## Best Practices

1. **Use Debouncing**: For file watchers, set appropriate debounce times
2. **Set Cooldowns**: Prevent runaway trigger loops
3. **Limit Concurrency**: Control resource usage with `max_concurrent`
4. **Use Filters**: Filter MCP and custom events to reduce noise
5. **Monitor Events**: Regularly review trigger events for failures
6. **Test Triggers**: Use the test endpoint before enabling

## Troubleshooting

### Trigger Not Firing

1. Check trigger is enabled: `GET /api/v1/triggers/{id}`
2. Verify status is `active`
3. Check cooldown hasn't been triggered
4. Review event filter criteria

### High Event Volume

1. Increase debounce time
2. Add more specific filters
3. Increase cooldown period
4. Review file watch patterns

### Pipeline Not Executing

1. Verify pipeline exists
2. Check trigger events: `GET /api/v1/triggers/{id}/events`
3. Review resolved inputs
4. Check pipeline execution logs
