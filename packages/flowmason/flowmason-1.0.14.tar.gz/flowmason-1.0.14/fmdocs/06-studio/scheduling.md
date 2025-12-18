# Pipeline Scheduling

FlowMason Studio includes a built-in scheduler for running pipelines automatically based on cron expressions.

## Overview

The scheduler allows you to:
- Schedule pipelines to run at specific times
- Use cron expressions for flexible scheduling
- Pass inputs to scheduled runs
- Track run history and status
- Manually trigger scheduled runs

## Creating a Schedule

### Via API

```bash
curl -X POST http://localhost:8999/api/v1/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Report",
    "pipeline_id": "abc123",
    "pipeline_name": "generate-report",
    "cron_expression": "0 9 * * *",
    "timezone": "America/New_York",
    "inputs": {
      "format": "pdf",
      "recipients": ["team@example.com"]
    },
    "description": "Generate daily report at 9am ET"
  }'
```

### Schedule Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name for the schedule |
| `pipeline_id` | string | Yes | ID of the pipeline to run |
| `pipeline_name` | string | Yes | Pipeline name for display |
| `cron_expression` | string | Yes | Cron schedule expression |
| `timezone` | string | No | Timezone (default: "UTC") |
| `inputs` | object | No | Inputs to pass to the pipeline |
| `description` | string | No | Schedule description |
| `enabled` | boolean | No | Whether schedule is active (default: true) |

## Cron Expressions

Cron expressions follow the standard 5-field format:

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

### Common Examples

| Expression | Description |
|------------|-------------|
| `0 9 * * *` | Daily at 9:00 AM |
| `0 9 * * 1-5` | Weekdays at 9:00 AM |
| `*/15 * * * *` | Every 15 minutes |
| `0 */2 * * *` | Every 2 hours |
| `0 0 * * 0` | Weekly on Sunday at midnight |
| `0 0 1 * *` | Monthly on the 1st at midnight |
| `0 6,12,18 * * *` | At 6am, 12pm, and 6pm daily |
| `30 4 1,15 * *` | At 4:30 AM on the 1st and 15th |

### Validate Expression

Check if a cron expression is valid and see upcoming run times:

```bash
curl "http://localhost:8999/api/v1/schedules/cron/validate?expression=0%209%20*%20*%20*&timezone=America/New_York"
```

Response:
```json
{
  "valid": true,
  "expression": "0 9 * * *",
  "timezone": "America/New_York",
  "next_runs": [
    "2024-01-15T09:00:00-05:00",
    "2024-01-16T09:00:00-05:00",
    "2024-01-17T09:00:00-05:00",
    "2024-01-18T09:00:00-05:00",
    "2024-01-19T09:00:00-05:00"
  ]
}
```

## Managing Schedules

### List Schedules

```bash
# List all schedules
curl http://localhost:8999/api/v1/schedules

# Filter by pipeline
curl "http://localhost:8999/api/v1/schedules?pipeline_id=abc123"

# Only enabled schedules
curl "http://localhost:8999/api/v1/schedules?enabled_only=true"
```

### Get Schedule

```bash
curl http://localhost:8999/api/v1/schedules/{schedule_id}
```

### Update Schedule

```bash
curl -X PATCH http://localhost:8999/api/v1/schedules/{schedule_id} \
  -H "Content-Type: application/json" \
  -d '{
    "cron_expression": "0 10 * * *",
    "inputs": {"format": "csv"}
  }'
```

### Enable/Disable Schedule

```bash
# Disable
curl -X POST http://localhost:8999/api/v1/schedules/{schedule_id}/disable

# Enable
curl -X POST http://localhost:8999/api/v1/schedules/{schedule_id}/enable
```

### Delete Schedule

```bash
curl -X DELETE http://localhost:8999/api/v1/schedules/{schedule_id}
```

## Manual Triggers

Run a scheduled pipeline immediately:

```bash
curl -X POST http://localhost:8999/api/v1/schedules/{schedule_id}/trigger
```

Response:
```json
{
  "run_id": "run-xyz789",
  "schedule_id": "sched-abc123",
  "message": "Pipeline execution started"
}
```

This doesn't affect the next scheduled run time.

## Run History

View execution history for a schedule:

```bash
curl http://localhost:8999/api/v1/schedules/{schedule_id}/history
```

Response:
```json
[
  {
    "id": "record-1",
    "schedule_id": "sched-abc123",
    "run_id": "run-xyz789",
    "scheduled_at": "2024-01-15T09:00:00Z",
    "started_at": "2024-01-15T09:00:02Z",
    "status": "completed",
    "error_message": null
  },
  {
    "id": "record-2",
    "schedule_id": "sched-abc123",
    "run_id": "run-xyz456",
    "scheduled_at": "2024-01-14T09:00:00Z",
    "started_at": "2024-01-14T09:00:01Z",
    "status": "failed",
    "error_message": "Connection timeout"
  }
]
```

## Schedule Response

Full schedule response includes:

```json
{
  "id": "sched-abc123",
  "name": "Daily Report",
  "pipeline_id": "abc123",
  "pipeline_name": "generate-report",
  "org_id": "default",
  "cron_expression": "0 9 * * *",
  "inputs": {"format": "pdf"},
  "enabled": true,
  "timezone": "America/New_York",
  "description": "Generate daily report at 9am ET",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-10T12:00:00Z",
  "next_run_at": "2024-01-16T09:00:00-05:00",
  "last_run_at": "2024-01-15T09:00:02Z",
  "last_run_id": "run-xyz789",
  "last_run_status": "completed",
  "run_count": 15,
  "failure_count": 1
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWMASON_SCHEDULER_ENABLED` | `true` | Enable/disable the scheduler |
| `FLOWMASON_SCHEDULER_POLL_INTERVAL` | `60` | Seconds between schedule checks |
| `FLOWMASON_SCHEDULER_MAX_CONCURRENT` | `5` | Max concurrent scheduled runs |

### Disable Scheduler

To disable the scheduler (useful for worker nodes in a cluster):

```bash
FLOWMASON_SCHEDULER_ENABLED=false fm studio
```

## Timezones

Schedules support IANA timezone names:

```json
{
  "timezone": "America/New_York"
}
```

Common timezones:
- `UTC` - Coordinated Universal Time
- `America/New_York` - Eastern Time
- `America/Chicago` - Central Time
- `America/Denver` - Mountain Time
- `America/Los_Angeles` - Pacific Time
- `Europe/London` - British Time
- `Europe/Paris` - Central European Time
- `Asia/Tokyo` - Japan Standard Time
- `Australia/Sydney` - Australian Eastern Time

## Best Practices

1. **Use descriptive names**: Make it clear what the schedule does
2. **Set appropriate timezones**: Use the timezone where the schedule makes sense
3. **Monitor failures**: Check `failure_count` and review run history
4. **Test with manual triggers**: Verify pipeline works before scheduling
5. **Stagger schedules**: Avoid scheduling many pipelines at the same time
6. **Use specific times**: Prefer `0 9 * * *` over `* 9 * * *`

## Dependencies

The scheduler requires the `croniter` package:

```bash
pip install croniter
# or
pip install flowmason[scheduling]
```

## Database Storage

Schedules are stored in SQLite (development) or PostgreSQL (production):

- `schedules` table: Schedule configurations
- `schedule_runs` table: Run history

The scheduler uses the same database as other Studio services.
