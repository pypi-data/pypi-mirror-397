# Federated Execution

Distribute pipeline execution across multiple clouds and regions for improved performance, data locality, and resilience.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Pipeline: global-data-processor                                │
│                                                                 │
│  ┌─────────┐     ┌─────────────────────────────────┐           │
│  │ ingest  │────▶│     PARALLEL FEDERATION         │           │
│  │ (local) │     │  ┌───────┐ ┌───────┐ ┌───────┐ │           │
│  └─────────┘     │  │US-EAST│ │EU-WEST│ │AP-EAST│ │           │
│                  │  │process│ │process│ │process│ │           │
│                  │  └───┬───┘ └───┬───┘ └───┬───┘ │           │
│                  └──────┼─────────┼─────────┼─────┘           │
│                         └─────────┼─────────┘                  │
│                                   ▼                            │
│                            ┌───────────┐                       │
│                            │  aggregate │                       │
│                            │  (local)   │                       │
│                            └───────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration

### Region Configuration

```python
from flowmason_core.federation import (
    FederationConfig, RegionConfig, FederatedStageConfig,
    FederationStrategy, AggregationStrategy
)

# Define regions
us_east = RegionConfig(
    name="us-east-1",
    endpoint="https://us-east.flowmason.io",
    api_key="us-east-key",
    priority=1,
    weight=1.0,
    max_concurrent=10,
    timeout_seconds=300,
    tags=["gpu", "high-memory"],
    latitude=37.7749,
    longitude=-122.4194,
    cost_per_execution=0.01,
    cost_per_token=0.00001
)

eu_west = RegionConfig(
    name="eu-west-1",
    endpoint="https://eu-west.flowmason.io",
    api_key="eu-west-key",
    priority=2,
    latitude=51.5074,
    longitude=-0.1278
)

# Create federation config
config = FederationConfig(
    regions=[us_east, eu_west],
    default_strategy=FederationStrategy.NEAREST
)
```

### Federated Stage Configuration

Configure federation at the stage level in your pipeline:

```json
{
  "stages": [
    {
      "id": "process-data",
      "type": "transformer",
      "federation": {
        "strategy": "parallel",
        "regions": ["us-east-1", "eu-west-1", "ap-northeast-1"],
        "data_locality": true,
        "aggregation": "merge"
      }
    }
  ]
}
```

## Federation Strategies

### FederationStrategy

| Strategy | Description |
|----------|-------------|
| `PARALLEL` | Execute on all regions simultaneously |
| `SEQUENTIAL` | Execute on regions in order |
| `NEAREST` | Execute on geographically nearest region |
| `ROUND_ROBIN` | Distribute across regions evenly |
| `LEAST_LOADED` | Route to region with lowest load |
| `COST_OPTIMIZED` | Route to cheapest available region |

### Python API

```python
from flowmason_core.federation import FederatedStageConfig, FederationStrategy

stage_config = FederatedStageConfig(
    strategy=FederationStrategy.PARALLEL,
    regions=["us-east-1", "eu-west-1"],
    data_locality=True,
    aggregation=AggregationStrategy.MERGE,
    timeout_seconds=300,
    retry_on_failure=True,
    fallback_region="us-east-1"
)
```

## Aggregation Strategies

When executing in parallel, results must be aggregated:

| Strategy | Description |
|----------|-------------|
| `MERGE` | Merge all results into one object |
| `REDUCE` | Apply reduce function to results |
| `FIRST` | Return first successful result |
| `ALL` | Return array of all results |
| `MAJORITY` | Return most common result |

## FederationCoordinator

The coordinator orchestrates federated execution.

```python
from flowmason_core.federation import FederationCoordinator

coordinator = FederationCoordinator(config)

# Execute federated stage
result = await coordinator.execute_federated(
    stage_id="process-data",
    stage_config=stage_config,
    inputs={"data": large_dataset}
)

print(f"Results from {len(result.region_results)} regions")
print(f"Aggregated output: {result.aggregated}")
```

## RemoteExecutor

Executes stages on remote regions.

```python
from flowmason_core.federation import RemoteExecutor

executor = RemoteExecutor(config)

# Execute on specific region
result = await executor.execute(
    region="us-east-1",
    stage_id="process",
    inputs={"data": data}
)

# Execute on multiple regions
results = await executor.execute_parallel(
    regions=["us-east-1", "eu-west-1"],
    stage_id="process",
    inputs={"data": data}
)
```

## DataRouter

Routes data to optimal regions based on locality.

```python
from flowmason_core.federation import DataRouter

router = DataRouter(config)

# Get optimal region for data source
region = router.get_optimal_region(
    data_location={"lat": 40.7128, "lon": -74.0060}  # New York
)
print(f"Optimal region: {region}")  # us-east-1

# Route data to regions
routing = router.route_data(
    data=large_dataset,
    strategy=FederationStrategy.NEAREST,
    source_location={"lat": 40.7128, "lon": -74.0060}
)
```

## Pipeline Configuration

Enable federation in your pipeline.json:

```json
{
  "id": "global-analytics",
  "name": "Global Analytics Pipeline",
  "federation": {
    "enabled": true,
    "default_strategy": "nearest"
  },
  "stages": [
    {
      "id": "collect",
      "type": "http_request",
      "config": { "url": "{{input.data_url}}" }
    },
    {
      "id": "process",
      "type": "json_transform",
      "depends_on": ["collect"],
      "federation": {
        "strategy": "parallel",
        "regions": ["us-east-1", "eu-west-1", "ap-northeast-1"],
        "aggregation": "merge"
      }
    },
    {
      "id": "store",
      "type": "database_write",
      "depends_on": ["process"]
    }
  ]
}
```

## Monitoring

### Federation Metrics

```python
# Get federation statistics
stats = coordinator.get_stats()

print(f"Total executions: {stats.total_executions}")
print(f"Success rate: {stats.success_rate}%")
print(f"Average latency: {stats.avg_latency_ms}ms")

# Per-region stats
for region, region_stats in stats.by_region.items():
    print(f"{region}: {region_stats.success_rate}% success")
```

### Health Checks

```python
# Check region health
health = await coordinator.check_health()

for region, status in health.items():
    print(f"{region}: {'healthy' if status.healthy else 'unhealthy'}")
    print(f"  Latency: {status.latency_ms}ms")
    print(f"  Load: {status.current_load}/{status.max_concurrent}")
```

## Error Handling

### Failover

```python
stage_config = FederatedStageConfig(
    strategy=FederationStrategy.NEAREST,
    regions=["us-east-1", "eu-west-1"],
    retry_on_failure=True,
    max_retries=3,
    fallback_region="eu-west-1"
)
```

### Partial Failures

```python
result = await coordinator.execute_federated(...)

if result.has_partial_failure:
    print(f"Failed regions: {result.failed_regions}")
    print(f"Successful regions: {result.successful_regions}")
```

## Best Practices

1. **Use Data Locality**: Enable `data_locality` to reduce data transfer
2. **Set Timeouts**: Configure appropriate timeouts per region
3. **Monitor Costs**: Track cost_per_execution for optimization
4. **Configure Fallbacks**: Always set fallback regions
5. **Test Failover**: Regularly test region failover scenarios
6. **Balance Load**: Use ROUND_ROBIN or LEAST_LOADED for even distribution
