# OpenTelemetry Integration

FlowMason provides native OpenTelemetry integration for distributed tracing of pipeline executions.

## Overview

The telemetry module enables:
- **Distributed Tracing**: Track pipeline executions across services
- **Stage-Level Visibility**: See timing and status of each stage
- **LLM Call Tracking**: Monitor LLM API calls with token counts
- **Multiple Exporters**: Send traces to Jaeger, Zipkin, OTLP, or console

## Installation

Install OpenTelemetry dependencies:

```bash
# Core SDK
pip install opentelemetry-api opentelemetry-sdk

# Exporters (install as needed)
pip install opentelemetry-exporter-otlp          # OTLP/gRPC
pip install opentelemetry-exporter-otlp-proto-http  # OTLP/HTTP
pip install opentelemetry-exporter-jaeger        # Jaeger
pip install opentelemetry-exporter-zipkin        # Zipkin
```

## Quick Start

```python
from flowmason_core.telemetry import (
    configure_tracing,
    get_tracer,
    TracingConfig,
    configure_console_exporter,
)

# Configure tracing
config = TracingConfig(
    service_name="my-pipeline-service",
    environment="production",
)
tracer = configure_tracing(config)

# Add console exporter for development
exporter = configure_console_exporter()
if exporter:
    tracer.add_exporter(exporter)

# Trace a pipeline execution
with tracer.start_pipeline_span("my-pipeline", pipeline_id="123") as span:
    # Execute stages
    with tracer.start_stage_span("stage-1", component_type="generator") as stage_span:
        result = execute_stage()
        if stage_span:
            stage_span.set_attribute("output.tokens", 150)
```

## Configuration

### TracingConfig Options

```python
from flowmason_core.telemetry import TracingConfig

config = TracingConfig(
    # Service identification
    service_name="flowmason",           # Service name in traces
    service_version="1.0.0",            # Service version
    environment="production",           # deployment environment

    # Feature flags
    enabled=True,                       # Enable/disable tracing
    trace_llm_calls=True,               # Trace LLM API calls
    trace_http_requests=True,           # Trace HTTP requests
    include_input_output=False,         # Include I/O in traces (may be sensitive)

    # Additional attributes
    resource_attributes={
        "team": "ml-platform",
        "region": "us-west-2",
    },
)
```

### Environment Variables

Configure via environment variables:

```bash
# Service info
export OTEL_SERVICE_NAME="my-service"
export OTEL_ENVIRONMENT="production"

# Enable/disable
export OTEL_TRACING_ENABLED="true"

# Exporter configuration
export OTEL_EXPORTER_TYPE="otlp"  # console, otlp, jaeger, zipkin
export OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-collector:4317"
```

## Exporters

### Console Exporter (Development)

```python
from flowmason_core.telemetry import get_tracer, configure_console_exporter

tracer = get_tracer()
exporter = configure_console_exporter()
if exporter:
    tracer.add_exporter(exporter)
```

### OTLP Exporter (Production)

Send traces to OpenTelemetry Collector:

```python
from flowmason_core.telemetry import get_tracer, configure_otlp_exporter

tracer = get_tracer()
exporter = configure_otlp_exporter(
    endpoint="http://otel-collector:4317",
    headers={"Authorization": "Bearer token"},
    insecure=False,
)
if exporter:
    tracer.add_exporter(exporter)
```

### Jaeger Exporter

Send traces directly to Jaeger:

```python
from flowmason_core.telemetry import get_tracer, configure_jaeger_exporter

tracer = get_tracer()
exporter = configure_jaeger_exporter(
    agent_host_name="jaeger",
    agent_port=6831,
    # Or use HTTP collector
    # collector_endpoint="http://jaeger:14268/api/traces",
)
if exporter:
    tracer.add_exporter(exporter)
```

### Auto-Configure from Environment

```python
from flowmason_core.telemetry.exporters import configure_from_env

exporter = configure_from_env()
if exporter:
    get_tracer().add_exporter(exporter)
```

## Instrumentation

### Using Decorators

```python
from flowmason_core.telemetry import trace_pipeline, trace_stage

@trace_pipeline("content-generator")
async def run_content_pipeline(input_data: dict) -> dict:
    result = await generate_content(input_data)
    return result

@trace_stage("generate", component_type="generator")
async def generate_content(input_data: dict) -> str:
    # LLM call here
    return content
```

### Using Context Managers

```python
from flowmason_core.telemetry import instrument_pipeline, instrument_stage

with instrument_pipeline("pipeline-123", "my-pipeline", run_id="run-456") as span:
    if span:
        span.set_attribute("custom.attribute", "value")

    with instrument_stage("stage-1", "extract", "extractor") as stage_span:
        result = await execute_stage()
        if stage_span:
            stage_span.set_attribute("records.count", len(result))
```

### Using PipelineInstrumentation Class

```python
from flowmason_core.telemetry import PipelineInstrumentation

instrumentation = PipelineInstrumentation(
    pipeline_id="123",
    pipeline_name="my-pipeline",
    run_id="run-456",
)

with instrumentation.pipeline_span() as pipeline_span:
    for stage in stages:
        with instrumentation.stage_span(
            stage.id, stage.name, stage.component_type
        ) as stage_span:
            try:
                start = time.time()
                result = await execute_stage(stage)
                duration = int((time.time() - start) * 1000)

                instrumentation.record_stage_success(
                    stage_span,
                    duration_ms=duration,
                    output_tokens=result.tokens,
                )
            except Exception as e:
                instrumentation.record_stage_failure(
                    stage_span, e, duration_ms=duration
                )
                raise

    instrumentation.record_pipeline_complete(
        pipeline_span,
        success=True,
        total_duration_ms=total_duration,
        total_tokens=total_tokens,
    )
```

## Span Attributes

### Pipeline Spans

| Attribute | Type | Description |
|-----------|------|-------------|
| `flowmason.pipeline.name` | string | Pipeline name |
| `flowmason.pipeline.id` | string | Pipeline ID |
| `flowmason.run.id` | string | Run ID |
| `flowmason.pipeline.duration_ms` | int | Total duration |
| `flowmason.pipeline.success` | bool | Success status |
| `flowmason.pipeline.stage_count` | int | Number of stages |
| `flowmason.pipeline.total_tokens` | int | Total tokens used |
| `flowmason.pipeline.total_cost_usd` | float | Total cost |

### Stage Spans

| Attribute | Type | Description |
|-----------|------|-------------|
| `flowmason.stage.id` | string | Stage ID |
| `flowmason.stage.name` | string | Stage name |
| `flowmason.stage.component_type` | string | Component type |
| `flowmason.stage.duration_ms` | int | Stage duration |
| `flowmason.stage.success` | bool | Success status |
| `flowmason.stage.output_tokens` | int | Output tokens |
| `flowmason.stage.cost_usd` | float | Stage cost |

### LLM Call Spans

| Attribute | Type | Description |
|-----------|------|-------------|
| `flowmason.llm.provider` | string | Provider name |
| `flowmason.llm.model` | string | Model name |
| `flowmason.llm.operation` | string | Operation type |
| `flowmason.llm.input_tokens` | int | Input tokens |
| `flowmason.llm.output_tokens` | int | Output tokens |

## LLM Call Tracing

```python
tracer = get_tracer()

with tracer.start_pipeline_span("my-pipeline") as pipeline_span:
    with tracer.start_stage_span("generate") as stage_span:
        # Trace the LLM call
        with tracer.start_llm_span(
            provider="openai",
            model="gpt-4",
            operation="generate",
        ) as llm_span:
            response = await openai.chat.completions.create(...)

            if llm_span:
                llm_span.set_attribute("llm.input_tokens", response.usage.prompt_tokens)
                llm_span.set_attribute("llm.output_tokens", response.usage.completion_tokens)
```

## Distributed Tracing

### Propagating Context

```python
tracer = get_tracer()

# Inject context into headers for outgoing requests
headers = {}
tracer.inject_context(headers)
# headers now contains 'traceparent' and 'tracestate'

# Make HTTP request with propagated context
response = await httpx.post(url, headers=headers)
```

### Extracting Context

```python
from fastapi import Request

@app.post("/run")
async def run_pipeline(request: Request):
    tracer = get_tracer()

    # Extract context from incoming request headers
    context = tracer.extract_context(dict(request.headers))

    # Continue trace with extracted context
    with tracer.start_pipeline_span(
        "my-pipeline",
        parent=context,  # Link to parent span
    ) as span:
        # Execute pipeline
        pass
```

## Docker Compose with Jaeger

```yaml
version: '3.8'

services:
  flowmason:
    build: .
    environment:
      - OTEL_SERVICE_NAME=flowmason
      - OTEL_EXPORTER_TYPE=jaeger
      - OTEL_EXPORTER_JAEGER_AGENT_HOST=jaeger
      - OTEL_EXPORTER_JAEGER_AGENT_PORT=6831

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "6831:6831/udp"  # Jaeger agent
```

Access Jaeger UI at http://localhost:16686

## Best Practices

1. **Use Meaningful Span Names**: Include pipeline/stage names for easy identification

2. **Add Custom Attributes**: Include business-relevant data like user IDs, request IDs

3. **Handle Errors Properly**: Always record exceptions for debugging

4. **Use Sampling in Production**: Reduce overhead with sampling:
   ```python
   config = TracingConfig(sampling_ratio=0.1)  # Sample 10%
   ```

5. **Protect Sensitive Data**: Disable `include_input_output` for sensitive pipelines

6. **Set Up Alerts**: Configure alerts in your observability platform for:
   - High latency pipelines
   - Frequent stage failures
   - LLM API errors
