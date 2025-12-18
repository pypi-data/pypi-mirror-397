# Multi-Region Deployment

FlowMason Studio supports deploying pipelines across multiple geographic regions for improved reliability, latency, and compliance.

## Overview

Multi-Region Deployment provides:

- **Geographic Distribution**: Deploy to regions worldwide
- **Traffic Routing**: Smart routing based on latency, location, or rules
- **Automatic Failover**: Seamless failover when regions become unhealthy
- **Health Monitoring**: Continuous health checks across regions
- **Scaling**: Independent scaling per region
- **Metrics**: Region-specific and global metrics

## Quick Start

### List Available Regions

```http
GET /api/v1/multi-region/regions
```

**Response:**
```json
{
  "regions": [
    {
      "id": "us-east-1",
      "name": "US East (Virginia)",
      "code": "us-east-1",
      "location": "Virginia, USA",
      "status": "active",
      "supports_gpu": true,
      "max_concurrent_runs": 500,
      "available_providers": ["openai", "anthropic", "google"],
      "current_load": 0.45,
      "average_latency_ms": 25.5,
      "uptime_percentage": 99.95
    },
    {
      "id": "eu-west-1",
      "name": "Europe (Ireland)",
      "code": "eu-west-1",
      "location": "Dublin, Ireland",
      "status": "active",
      "supports_gpu": true
    }
  ],
  "total": 6
}
```

### Create a Deployment

```http
POST /api/v1/multi-region/deployments
Content-Type: application/json

{
  "pipeline_id": "my-pipeline",
  "pipeline_version": "1.0.0",
  "name": "production-deployment",
  "config": {
    "primary_region": "us-east-1",
    "replica_regions": ["eu-west-1", "ap-northeast-1"],
    "routing_strategy": "latency",
    "auto_failover_enabled": true,
    "health_check": {
      "type": "http",
      "interval_seconds": 30,
      "timeout_seconds": 10
    },
    "min_replicas_per_region": 2,
    "max_replicas_per_region": 10,
    "auto_scaling_enabled": true
  }
}
```

**Response:**
```json
{
  "id": "deploy_abc123",
  "pipeline_id": "my-pipeline",
  "pipeline_version": "1.0.0",
  "name": "production-deployment",
  "status": "active",
  "config": {...},
  "regions": [
    {
      "region_id": "us-east-1",
      "status": "active",
      "version": "1.0.0",
      "replicas": 2,
      "healthy_replicas": 2,
      "health_check_status": "healthy"
    },
    {
      "region_id": "eu-west-1",
      "status": "active",
      "replicas": 2,
      "healthy_replicas": 2
    },
    {
      "region_id": "ap-northeast-1",
      "status": "active",
      "replicas": 2,
      "healthy_replicas": 2
    }
  ]
}
```

## Regions

### Available Regions

| Region | Location | GPU | Providers |
|--------|----------|-----|-----------|
| `us-east-1` | Virginia, USA | Yes | OpenAI, Anthropic, Google |
| `us-west-2` | Oregon, USA | Yes | OpenAI, Anthropic |
| `eu-west-1` | Dublin, Ireland | Yes | OpenAI, Anthropic, Google |
| `eu-central-1` | Frankfurt, Germany | No | OpenAI, Anthropic |
| `ap-northeast-1` | Tokyo, Japan | Yes | OpenAI, Anthropic |
| `ap-southeast-1` | Singapore | No | OpenAI, Anthropic |

### Get Region Details

```http
GET /api/v1/multi-region/regions/us-east-1
```

### Get Region Endpoint

```http
GET /api/v1/multi-region/regions/us-east-1/endpoint
```

**Response:**
```json
{
  "region_id": "us-east-1",
  "api_url": "https://us-east-1.api.flowmason.io",
  "ws_url": "wss://us-east-1.api.flowmason.io/ws",
  "health_check_url": "https://us-east-1.api.flowmason.io/health"
}
```

### Find Nearest Region

```http
GET /api/v1/multi-region/regions/nearest?latitude=40.7128&longitude=-74.0060
```

## Routing Strategies

### Latency-Based (Default)

Routes requests to the region with the lowest latency.

```json
{
  "routing_strategy": "latency"
}
```

### Geolocation

Routes requests based on the user's geographic location.

```json
{
  "routing_strategy": "geolocation"
}
```

### Weighted

Distributes traffic by configured weights.

```json
{
  "routing_strategy": "weighted",
  "routing_rules": [
    {
      "id": "rule_1",
      "name": "Production weights",
      "target_regions": ["us-east-1", "eu-west-1"],
      "weights": {
        "us-east-1": 70,
        "eu-west-1": 30
      }
    }
  ]
}
```

### Failover

Uses primary region with automatic failover to replicas.

```json
{
  "routing_strategy": "failover"
}
```

### Round Robin

Equal distribution across all healthy regions.

```json
{
  "routing_strategy": "round_robin"
}
```

## Routing Rules

Custom rules for advanced routing logic:

```json
{
  "routing_rules": [
    {
      "id": "eu_users",
      "name": "Route EU users to EU region",
      "priority": 10,
      "enabled": true,
      "source_countries": ["DE", "FR", "GB", "IT", "ES"],
      "target_regions": ["eu-west-1", "eu-central-1"],
      "fallback_regions": ["us-east-1"]
    },
    {
      "id": "api_header",
      "name": "Route by API header",
      "priority": 5,
      "header_conditions": {
        "X-Preferred-Region": "asia"
      },
      "target_regions": ["ap-northeast-1", "ap-southeast-1"]
    }
  ]
}
```

### Resolve Route

```http
GET /api/v1/multi-region/deployments/{id}/route?latitude=51.5074&longitude=-0.1278&source_country=GB
```

**Response:**
```json
{
  "region_id": "eu-west-1",
  "endpoint": {
    "api_url": "https://eu-west-1.api.flowmason.io",
    "ws_url": "wss://eu-west-1.api.flowmason.io/ws"
  }
}
```

## Scaling

### Scale a Region

```http
PUT /api/v1/multi-region/deployments/{id}/regions/us-east-1/scale
Content-Type: application/json

{
  "replicas": 5
}
```

### Auto-Scaling Configuration

```json
{
  "auto_scaling_enabled": true,
  "min_replicas_per_region": 2,
  "max_replicas_per_region": 20,
  "scale_up_threshold": 0.7,
  "scale_down_threshold": 0.3
}
```

## Failover

### Automatic Failover

```json
{
  "auto_failover_enabled": true,
  "failover_threshold": 3,
  "failover_cooldown_seconds": 300
}
```

### Manual Failover

```http
POST /api/v1/multi-region/deployments/{id}/failover
Content-Type: application/json

{
  "from_region": "us-east-1",
  "to_region": "us-west-2",
  "reason": "Scheduled maintenance"
}
```

### Get Failover History

```http
GET /api/v1/multi-region/deployments/{id}/failover-events
```

**Response:**
```json
[
  {
    "id": "event_xyz",
    "from_region": "us-east-1",
    "to_region": "us-west-2",
    "reason": "Health check failures exceeded threshold",
    "triggered_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:30:05Z",
    "success": true,
    "affected_requests": 12
  }
]
```

## Health Checks

### Configuration

```json
{
  "health_check": {
    "type": "http",
    "interval_seconds": 30,
    "timeout_seconds": 10,
    "healthy_threshold": 2,
    "unhealthy_threshold": 3,
    "path": "/health",
    "expected_status": 200
  }
}
```

### Health Check Types

| Type | Description |
|------|-------------|
| `http` | HTTP endpoint check |
| `tcp` | TCP connection check |
| `pipeline` | Run a test pipeline |

### Run Manual Health Check

```http
POST /api/v1/multi-region/deployments/{id}/regions/us-east-1/health-check
```

## Metrics

### Global Metrics

```http
GET /api/v1/multi-region/deployments/{id}/metrics
```

**Response:**
```json
{
  "timestamp": "2024-01-15T12:00:00Z",
  "total_requests": 10000,
  "total_errors": 15,
  "global_latency_p50_ms": 85.5,
  "global_latency_p95_ms": 250.0,
  "regions": {
    "us-east-1": {
      "requests": 5000,
      "errors": 8,
      "latency_p50_ms": 50.0,
      "latency_p95_ms": 150.0,
      "cpu_usage": 0.45,
      "memory_usage": 0.55
    },
    "eu-west-1": {
      "requests": 3000,
      "errors": 5,
      "latency_p50_ms": 75.0
    }
  },
  "routing_distribution": {
    "us-east-1": 5000,
    "eu-west-1": 3000,
    "ap-northeast-1": 2000
  }
}
```

### Region Metrics

```http
GET /api/v1/multi-region/deployments/{id}/regions/us-east-1/metrics
```

## Region Management

### Add Region

```http
POST /api/v1/multi-region/deployments/{id}/regions
Content-Type: application/json

{
  "region_id": "ap-southeast-1",
  "replicas": 2,
  "weight": 10
}
```

### Remove Region

```http
DELETE /api/v1/multi-region/deployments/{id}/regions/ap-southeast-1
```

## Deployment Lifecycle

### Update Deployment

```http
PATCH /api/v1/multi-region/deployments/{id}
Content-Type: application/json

{
  "pipeline_version": "1.1.0",
  "config": {
    "routing_strategy": "weighted"
  }
}
```

### Stop Deployment

```http
POST /api/v1/multi-region/deployments/{id}/stop
```

### Delete Deployment

```http
DELETE /api/v1/multi-region/deployments/{id}
```

## Configuration Reference

```json
{
  "config": {
    "primary_region": "us-east-1",
    "replica_regions": ["eu-west-1", "ap-northeast-1"],
    "excluded_regions": [],

    "routing_strategy": "latency",
    "routing_rules": [],

    "health_check": {
      "type": "http",
      "interval_seconds": 30,
      "timeout_seconds": 10,
      "healthy_threshold": 2,
      "unhealthy_threshold": 3,
      "path": "/health",
      "expected_status": 200
    },

    "min_replicas_per_region": 1,
    "max_replicas_per_region": 10,
    "auto_scaling_enabled": true,
    "scale_up_threshold": 0.7,
    "scale_down_threshold": 0.3,

    "auto_failover_enabled": true,
    "failover_threshold": 3,
    "failover_cooldown_seconds": 300,

    "sync_state": true,
    "sync_interval_seconds": 5
  }
}
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/multi-region/regions` | GET | List regions |
| `/multi-region/regions/{id}` | GET | Get region |
| `/multi-region/regions/{id}/endpoint` | GET | Get endpoint |
| `/multi-region/regions/nearest` | GET | Find nearest |
| `/multi-region/deployments` | GET | List deployments |
| `/multi-region/deployments` | POST | Create deployment |
| `/multi-region/deployments/{id}` | GET | Get deployment |
| `/multi-region/deployments/{id}` | PATCH | Update deployment |
| `/multi-region/deployments/{id}/stop` | POST | Stop deployment |
| `/multi-region/deployments/{id}` | DELETE | Delete deployment |
| `/multi-region/deployments/{id}/regions` | POST | Add region |
| `/multi-region/deployments/{id}/regions/{rid}` | DELETE | Remove region |
| `/multi-region/deployments/{id}/regions/{rid}/scale` | PUT | Scale region |
| `/multi-region/deployments/{id}/failover` | POST | Trigger failover |
| `/multi-region/deployments/{id}/failover-events` | GET | Failover history |
| `/multi-region/deployments/{id}/route` | GET | Resolve route |
| `/multi-region/deployments/{id}/metrics` | GET | Global metrics |
| `/multi-region/deployments/{id}/regions/{rid}/metrics` | GET | Region metrics |
| `/multi-region/deployments/{id}/regions/{rid}/health-check` | POST | Run health check |
