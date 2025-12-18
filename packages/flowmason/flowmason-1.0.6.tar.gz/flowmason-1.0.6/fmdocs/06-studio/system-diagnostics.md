# System Diagnostics API

FlowMason Studio provides a system diagnostics API for health monitoring, troubleshooting, and admin operations.

## Overview

The system API provides:
- Detailed health checks for all components
- System and platform information
- Database status and statistics
- LLM provider connectivity status
- Resource usage metrics
- Recent log access

## Health Check

Get detailed health status:

```bash
curl http://localhost:8999/api/v1/system/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "components": [
    {
      "name": "database",
      "status": "healthy",
      "message": "25 pipelines",
      "latency_ms": 2.5
    },
    {
      "name": "registry",
      "status": "healthy",
      "message": "15 components"
    },
    {
      "name": "providers",
      "status": "healthy",
      "message": "2 providers configured"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Health Statuses

| Status | Description |
|--------|-------------|
| `healthy` | All components functioning normally |
| `degraded` | Some components have issues but system is operational |
| `unhealthy` | Critical components are failing |

## System Information

Get platform and environment details:

```bash
curl http://localhost:8999/api/v1/system/info
```

Response:
```json
{
  "version": "1.0.0",
  "python_version": "3.11.4",
  "platform": "Darwin",
  "platform_version": "23.0.0",
  "hostname": "macbook-pro",
  "working_directory": "/Users/dev/flowmason-project",
  "environment": "development"
}
```

### Environments

| Environment | Description |
|-------------|-------------|
| `development` | Local development (default) |
| `staging` | Staging/test environment |
| `production` | Production deployment |

Set via `FLOWMASON_ENV` environment variable.

## Database Status

Get database status and statistics:

```bash
curl http://localhost:8999/api/v1/system/database
```

Response:
```json
{
  "type": "sqlite",
  "connected": true,
  "pipeline_count": 25,
  "run_count": 150,
  "size_bytes": 1048576
}
```

## Provider Status

Get LLM provider configuration status:

```bash
curl http://localhost:8999/api/v1/system/providers
```

Response:
```json
[
  {
    "name": "anthropic",
    "configured": true,
    "available": true,
    "default": true
  },
  {
    "name": "openai",
    "configured": true,
    "available": true,
    "default": false
  },
  {
    "name": "google",
    "configured": false,
    "available": false,
    "default": false
  }
]
```

## Resource Usage

Get memory and CPU usage (requires `psutil`):

```bash
curl http://localhost:8999/api/v1/system/resources
```

Response:
```json
{
  "memory_mb": 256.5,
  "cpu_percent": 5.2,
  "disk_usage_percent": 45.0,
  "open_file_count": 12
}
```

Note: Metrics may be empty if `psutil` is not installed.

## Complete Diagnostics

Get a complete diagnostics report:

```bash
curl http://localhost:8999/api/v1/system/diagnostics
```

Response:
```json
{
  "health": { ... },
  "system": { ... },
  "database": { ... },
  "providers": [ ... ],
  "resources": { ... },
  "registry": {
    "total_components": 15,
    "categories": {
      "core": 5,
      "control_flow": 3,
      "ai": 4,
      "http": 1,
      "utility": 2
    }
  }
}
```

## Configuration

Get non-sensitive configuration:

```bash
curl http://localhost:8999/api/v1/system/config
```

Response:
```json
{
  "environment": "development",
  "default_provider": "anthropic",
  "scheduler_enabled": true,
  "debug_mode": false,
  "cors_origins": "*",
  "log_level": "INFO"
}
```

## Recent Logs

Get recent log entries:

```bash
curl "http://localhost:8999/api/v1/system/logs/recent?limit=50"
```

Filter by level:
```bash
curl "http://localhost:8999/api/v1/system/logs/recent?limit=50&level=ERROR"
```

Response:
```json
{
  "count": 50,
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "INFO",
      "category": "execution",
      "message": "Pipeline run_abc123 completed"
    }
  ]
}
```

## Garbage Collection

Trigger Python garbage collection:

```bash
curl -X POST http://localhost:8999/api/v1/system/gc
```

Response:
```json
{
  "message": "Garbage collection completed",
  "objects_collected": 1500,
  "generation_counts_before": [100, 50, 25],
  "generation_counts_after": [10, 5, 2]
}
```

## Use Cases

### Health Monitoring

```python
import httpx

async def check_health():
    response = await httpx.get("http://localhost:8999/api/v1/system/health")
    data = response.json()

    if data["status"] != "healthy":
        print(f"System is {data['status']}")
        for component in data["components"]:
            if component["status"] != "healthy":
                print(f"  - {component['name']}: {component['message']}")
```

### Kubernetes Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/system/health
    port: 8999
  initialDelaySeconds: 10
  periodSeconds: 30
```

### Admin Dashboard Integration

```javascript
async function loadDiagnostics() {
  const response = await fetch('/api/v1/system/diagnostics');
  const data = await response.json();

  // Update dashboard
  updateHealthIndicator(data.health.status);
  updateResourceGauges(data.resources);
  updateProviderList(data.providers);
}
```

### Troubleshooting Script

```bash
#!/bin/bash
echo "=== FlowMason Diagnostics ==="

# Health
echo "\nHealth Status:"
curl -s http://localhost:8999/api/v1/system/health | jq '.status, .components'

# Database
echo "\nDatabase:"
curl -s http://localhost:8999/api/v1/system/database | jq '.'

# Providers
echo "\nProviders:"
curl -s http://localhost:8999/api/v1/system/providers | jq '.[] | select(.configured == true)'

# Recent errors
echo "\nRecent Errors:"
curl -s "http://localhost:8999/api/v1/system/logs/recent?level=ERROR&limit=5" | jq '.logs'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLOWMASON_ENV` | Environment (development/staging/production) | development |
| `FLOWMASON_DEFAULT_PROVIDER` | Default LLM provider | anthropic |
| `FLOWMASON_SCHEDULER_ENABLED` | Enable cron scheduler | true |
| `FLOWMASON_DEBUG` | Enable debug mode | false |
| `FLOWMASON_LOG_LEVEL` | Log level | INFO |
| `FLOWMASON_CORS_ORIGINS` | CORS allowed origins | * |
