# Kubernetes Deployment

Deploy and manage FlowMason pipelines as Kubernetes resources using Custom Resource Definitions (CRDs).

## Overview

```yaml
apiVersion: flowmason.io/v1
kind: Pipeline
metadata:
  name: data-processor
  namespace: production
spec:
  stages:
    - id: fetch
      componentType: http_request
      config:
        url: https://api.example.com/data
    - id: process
      componentType: json_transform
      dependsOn: [fetch]
  schedule: "0 * * * *"
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
```

## Custom Resource Definitions

### Pipeline CRD

The Pipeline CRD defines a pipeline configuration that can be scheduled and managed by Kubernetes.

```python
from flowmason_core.kubernetes import Pipeline, PipelineSpec, StageSpec

# Create a Pipeline resource
pipeline = Pipeline(
    api_version="flowmason.io/v1",
    kind="Pipeline",
    metadata={
        "name": "data-processor",
        "namespace": "production"
    },
    spec=PipelineSpec(
        stages=[
            StageSpec(
                id="fetch",
                componentType="http_request",
                config={"url": "https://api.example.com"}
            ),
            StageSpec(
                id="process",
                componentType="json_transform",
                dependsOn=["fetch"]
            )
        ],
        schedule="0 * * * *",
        resources={
            "requests": {"memory": "256Mi", "cpu": "100m"},
            "limits": {"memory": "512Mi", "cpu": "500m"}
        }
    )
)
```

### PipelineRun CRD

The PipelineRun CRD represents an individual execution of a pipeline.

```python
from flowmason_core.kubernetes import PipelineRun, PipelineRunSpec

# Create a PipelineRun
run = PipelineRun(
    api_version="flowmason.io/v1",
    kind="PipelineRun",
    metadata={
        "name": "data-processor-run-001",
        "namespace": "production"
    },
    spec=PipelineRunSpec(
        pipeline_ref="data-processor",
        inputs={"date": "2025-12-14"}
    )
)
```

## Pipeline Spec Fields

| Field | Type | Description |
|-------|------|-------------|
| `stages` | `List[StageSpec]` | Pipeline stages (required) |
| `source` | `Dict` | ConfigMap reference for pipeline config |
| `schedule` | `str` | Cron expression for scheduling |
| `triggers` | `Dict` | Event triggers configuration |
| `resources` | `Dict` | Resource requests and limits |
| `env` | `List[EnvVar]` | Environment variables |
| `providers` | `Dict` | LLM provider configuration |
| `timeout` | `int` | Execution timeout in seconds |
| `retries` | `int` | Number of retry attempts |
| `parallelism` | `int` | Max parallel stage executions |

## Stage Spec Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Stage identifier (required) |
| `componentType` | `str` | Component type (required) |
| `name` | `str` | Display name |
| `dependsOn` | `List[str]` | Stage dependencies |
| `config` | `Dict` | Stage configuration |
| `inputMapping` | `Dict` | Input field mapping |

## Kubernetes Client

### FlowMasonK8sClient

```python
from flowmason_core.kubernetes import FlowMasonK8sClient

# Initialize client (uses default kubeconfig)
client = FlowMasonK8sClient()

# Or with explicit config
client = FlowMasonK8sClient(
    kubeconfig_path="/path/to/kubeconfig",
    context="my-cluster"
)

# Create pipeline
await client.create_pipeline(pipeline)

# Get pipeline
pipeline = await client.get_pipeline("data-processor", namespace="production")

# List pipelines
pipelines = await client.list_pipelines(namespace="production")

# Update pipeline
await client.update_pipeline(pipeline)

# Delete pipeline
await client.delete_pipeline("data-processor", namespace="production")

# Trigger run
run = await client.create_run("data-processor", inputs={"date": "2025-12-14"})

# Get run status
status = await client.get_run_status(run.metadata["name"])
```

## Environment Variables

Inject secrets and configuration using Kubernetes secrets:

```yaml
spec:
  env:
    - name: ANTHROPIC_API_KEY
      valueFrom:
        secretKeyRef:
          name: llm-secrets
          key: anthropic-key
    - name: DATABASE_URL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database-url
```

## Resource Management

Control resource allocation for pipeline executions:

```yaml
spec:
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
```

## Scheduling

### Cron Schedule

```yaml
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
```

### Event Triggers

```yaml
spec:
  triggers:
    webhook:
      enabled: true
      path: /webhooks/data-processor
    pubsub:
      topic: pipeline-triggers
      subscription: data-processor-sub
```

## Installation

### Install CRDs

```bash
kubectl apply -f https://flowmason.io/k8s/crds/pipeline.yaml
kubectl apply -f https://flowmason.io/k8s/crds/pipelinerun.yaml
```

### Deploy Operator

```bash
# Using Helm
helm repo add flowmason https://charts.flowmason.io
helm install flowmason-operator flowmason/operator

# Or using kubectl
kubectl apply -f https://flowmason.io/k8s/operator.yaml
```

## CLI Commands

```bash
# Deploy pipeline to Kubernetes
fm k8s deploy pipeline.json --namespace production

# List pipelines
fm k8s list --namespace production

# Get pipeline status
fm k8s status data-processor --namespace production

# Trigger run
fm k8s run data-processor --namespace production --input date=2025-12-14

# View logs
fm k8s logs data-processor-run-001 --namespace production
```

## Monitoring

### Prometheus Metrics

The operator exposes metrics at `/metrics`:

- `flowmason_pipeline_runs_total`
- `flowmason_pipeline_run_duration_seconds`
- `flowmason_pipeline_run_errors_total`
- `flowmason_stage_duration_seconds`

### Example ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: flowmason-operator
spec:
  selector:
    matchLabels:
      app: flowmason-operator
  endpoints:
    - port: metrics
```

## Best Practices

1. **Use Namespaces**: Organize pipelines by environment or team
2. **Set Resource Limits**: Always set resource limits for production
3. **Use Secrets**: Store API keys in Kubernetes secrets
4. **Monitor Runs**: Set up alerting for failed runs
5. **Version Pipelines**: Use labels for version tracking
