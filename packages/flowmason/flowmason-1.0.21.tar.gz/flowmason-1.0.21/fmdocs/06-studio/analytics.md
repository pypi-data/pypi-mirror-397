# Analytics API

FlowMason Studio provides an analytics API for dashboard metrics and statistics. These endpoints power the Operations Dashboard and provide insights into pipeline execution.

## Overview

The analytics API provides:
- Execution metrics and success rates
- Per-pipeline statistics
- Daily and hourly trends
- Recent activity feed
- Usage summaries

## Dashboard Overview

Get a complete dashboard overview in a single call:

```bash
curl "http://localhost:8999/api/v1/analytics/overview?days=7&limit=5"
```

Response:
```json
{
  "metrics": {
    "total_runs": 150,
    "successful_runs": 135,
    "failed_runs": 12,
    "cancelled_runs": 2,
    "running_runs": 1,
    "success_rate": 0.9,
    "avg_duration_seconds": 45.2
  },
  "top_pipelines": [
    {
      "pipeline_id": "pipe_abc123",
      "pipeline_name": "Data ETL",
      "total_runs": 50,
      "successful_runs": 48,
      "failed_runs": 2,
      "success_rate": 0.96,
      "avg_duration_seconds": 30.5,
      "last_run_at": "2024-01-15T10:30:00Z"
    }
  ],
  "daily_stats": [
    {
      "date": "2024-01-15",
      "total_runs": 25,
      "successful_runs": 23,
      "failed_runs": 2
    }
  ],
  "recent_activity": [
    {
      "run_id": "run_xyz789",
      "pipeline_id": "pipe_abc123",
      "pipeline_name": "Data ETL",
      "status": "completed",
      "started_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:30:45Z",
      "duration_seconds": 45.0
    }
  ]
}
```

## Execution Metrics

Get aggregate execution metrics:

```bash
curl "http://localhost:8999/api/v1/analytics/metrics?days=7"
```

Filter by pipeline:
```bash
curl "http://localhost:8999/api/v1/analytics/metrics?days=7&pipeline_id=pipe_abc123"
```

Response:
```json
{
  "total_runs": 150,
  "successful_runs": 135,
  "failed_runs": 12,
  "cancelled_runs": 2,
  "running_runs": 1,
  "success_rate": 0.9,
  "avg_duration_seconds": 45.2
}
```

## Pipeline Metrics

Get per-pipeline statistics:

```bash
curl "http://localhost:8999/api/v1/analytics/pipelines?days=7&limit=20&sort_by=runs"
```

Sort options:
- `runs` - Most runs first (default)
- `success_rate` - Highest success rate first
- `name` - Alphabetical

Response:
```json
[
  {
    "pipeline_id": "pipe_abc123",
    "pipeline_name": "Data ETL",
    "total_runs": 50,
    "successful_runs": 48,
    "failed_runs": 2,
    "success_rate": 0.96,
    "avg_duration_seconds": 30.5,
    "last_run_at": "2024-01-15T10:30:00Z"
  },
  {
    "pipeline_id": "pipe_def456",
    "pipeline_name": "Content Generator",
    "total_runs": 35,
    "successful_runs": 30,
    "failed_runs": 5,
    "success_rate": 0.857,
    "avg_duration_seconds": 120.3,
    "last_run_at": "2024-01-15T09:00:00Z"
  }
]
```

## Daily Statistics

Get daily run counts for charting:

```bash
curl "http://localhost:8999/api/v1/analytics/daily?days=30"
```

Filter by pipeline:
```bash
curl "http://localhost:8999/api/v1/analytics/daily?days=30&pipeline_id=pipe_abc123"
```

Response:
```json
[
  {
    "date": "2024-01-01",
    "total_runs": 15,
    "successful_runs": 14,
    "failed_runs": 1
  },
  {
    "date": "2024-01-02",
    "total_runs": 20,
    "successful_runs": 18,
    "failed_runs": 2
  }
]
```

## Hourly Distribution

Get aggregated hourly distribution:

```bash
curl "http://localhost:8999/api/v1/analytics/hourly?days=7"
```

Response:
```json
[
  {"hour": 0, "total_runs": 5, "successful_runs": 5, "failed_runs": 0},
  {"hour": 1, "total_runs": 3, "successful_runs": 3, "failed_runs": 0},
  {"hour": 9, "total_runs": 25, "successful_runs": 23, "failed_runs": 2},
  {"hour": 10, "total_runs": 30, "successful_runs": 28, "failed_runs": 2}
]
```

This is useful for understanding when pipelines are most active.

## Recent Activity

Get recent execution activity:

```bash
curl "http://localhost:8999/api/v1/analytics/recent?limit=20"
```

Filter by status:
```bash
curl "http://localhost:8999/api/v1/analytics/recent?limit=20&status=failed"
```

Response:
```json
[
  {
    "run_id": "run_xyz789",
    "pipeline_id": "pipe_abc123",
    "pipeline_name": "Data ETL",
    "status": "completed",
    "started_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:30:45Z",
    "duration_seconds": 45.0
  },
  {
    "run_id": "run_abc123",
    "pipeline_id": "pipe_def456",
    "pipeline_name": "Content Generator",
    "status": "failed",
    "started_at": "2024-01-15T10:25:00Z",
    "completed_at": "2024-01-15T10:25:30Z",
    "duration_seconds": 30.0
  }
]
```

## Usage Summary

Get overall usage summary:

```bash
curl "http://localhost:8999/api/v1/analytics/usage?days=30"
```

Response:
```json
{
  "period": "last_30_days",
  "total_pipelines": 25,
  "active_pipelines": 15,
  "total_runs": 450,
  "total_stages_executed": 1800,
  "avg_stages_per_run": 4.0
}
```

## Query Parameters

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | int | 7 | Number of days to include (1-90) |
| `limit` | int | varies | Maximum items to return |
| `pipeline_id` | string | - | Filter by pipeline |

### Sort Options (Pipeline Metrics)

| Value | Description |
|-------|-------------|
| `runs` | Sort by total run count (default) |
| `success_rate` | Sort by success rate |
| `name` | Sort alphabetically |

## Use Cases

### Operations Dashboard

```javascript
// Fetch complete dashboard data
const response = await fetch('/api/v1/analytics/overview?days=7&limit=5');
const data = await response.json();

// Display metrics
console.log(`Success Rate: ${(data.metrics.success_rate * 100).toFixed(1)}%`);
console.log(`Total Runs: ${data.metrics.total_runs}`);
console.log(`Average Duration: ${data.metrics.avg_duration_seconds?.toFixed(1)}s`);
```

### Chart Data

```javascript
// Get daily stats for line chart
const daily = await fetch('/api/v1/analytics/daily?days=30');
const dailyData = await daily.json();

// Format for chart library
const chartData = dailyData.map(d => ({
  date: d.date,
  success: d.successful_runs,
  failed: d.failed_runs
}));
```

### Pipeline Health Monitoring

```javascript
// Get pipelines sorted by success rate
const pipelines = await fetch('/api/v1/analytics/pipelines?sort_by=success_rate&limit=10');
const data = await pipelines.json();

// Find low-performing pipelines
const troubled = data.filter(p => p.success_rate < 0.9);
console.log('Pipelines needing attention:', troubled);
```

### Real-time Activity Feed

```javascript
// Poll for recent activity
async function pollActivity() {
  const response = await fetch('/api/v1/analytics/recent?limit=10');
  const activity = await response.json();
  updateActivityFeed(activity);
}

setInterval(pollActivity, 5000); // Every 5 seconds
```

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Invalid parameters (e.g., days > 90) |
| 500 | Server error |

## Performance Notes

- Data is calculated in real-time from stored runs
- For large datasets, consider using smaller `days` values
- The `/overview` endpoint combines multiple queries for efficiency
- Use specific endpoints when you only need partial data
