# Edge Deployment

Run FlowMason pipelines on edge devices with offline-first execution and local LLM support.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLOUD                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FlowMason Studio (Central)                              │   │
│  │  - Pipeline registry                                     │   │
│  │  - Execution history sync                                │   │
│  │  - Edge device management                                │   │
│  └────────────────────────┬────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │ Sync (when connected)
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Edge Node 1  │   │  Edge Node 2  │   │  Edge Node 3  │
│  (Raspberry)  │   │  (Jetson)     │   │  (Industrial) │
│  ┌─────────┐  │   │  ┌─────────┐  │   │  ┌─────────┐  │
│  │Pipeline │  │   │  │Pipeline │  │   │  │Pipeline │  │
│  │Cache    │  │   │  │Cache    │  │   │  │Cache    │  │
│  └─────────┘  │   │  └─────────┘  │   │  └─────────┘  │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Installation

### Python Package

```bash
pip install flowmason-edge
```

### Docker (ARM64)

```bash
docker pull flowmason/edge:latest-arm64
docker run -d --name flowmason-edge \
  -v /var/flowmason:/var/flowmason \
  -e CLOUD_URL=https://studio.flowmason.io \
  -e API_KEY=your-api-key \
  flowmason/edge:latest-arm64
```

## Configuration

### EdgeConfig

```python
from flowmason_edge import EdgeConfig, create_runtime

config = EdgeConfig(
    # Storage directories
    data_dir="/var/flowmason/edge",
    pipeline_cache_dir="/var/flowmason/pipelines",
    model_cache_dir="/var/flowmason/models",
    result_store_dir="/var/flowmason/results",

    # Cloud connection
    cloud_url="https://studio.flowmason.io",
    api_key="your-api-key",

    # Execution limits
    max_concurrent=2,
    execution_timeout=300,

    # Cache settings
    pipeline_cache_size_mb=100,
    pipeline_ttl_days=30,
    model_cache_size_gb=50,
    result_retention_days=30,

    # Sync settings
    sync_interval=60,
    auto_sync=True,

    # LLM settings
    llm_backend="ollama",  # or "llamacpp"
    llm_model="llama2",
    llm_base_url="http://localhost:11434"
)

# Create runtime
runtime = await create_runtime(config)
```

## Edge Executor

The `EdgeExecutor` runs pipelines locally with offline support.

```python
from flowmason_edge import EdgeExecutor, EdgeConfig

config = EdgeConfig(data_dir="/var/flowmason/edge")
executor = EdgeExecutor(config)

# Execute a pipeline
result = await executor.execute(
    pipeline_id="data-processor",
    inputs={"sensor_data": [1, 2, 3]}
)

print(f"Status: {result.status}")
print(f"Output: {result.output}")
print(f"Duration: {result.duration_ms}ms")
```

## Local LLM Support

### Ollama Adapter

```python
from flowmason_edge.adapters import OllamaAdapter

adapter = OllamaAdapter(
    base_url="http://localhost:11434",
    model="llama2"
)

# Generate text
response = await adapter.generate(
    prompt="Summarize: ...",
    temperature=0.7,
    max_tokens=500
)
```

### LlamaCpp Adapter

```python
from flowmason_edge.adapters import LlamaCppAdapter

adapter = LlamaCppAdapter(
    model_path="/models/llama-2-7b.gguf",
    n_ctx=2048,
    n_threads=4
)

response = await adapter.generate(prompt="...")
```

## Caching

### Pipeline Cache

Pipelines are cached locally for offline execution.

```python
from flowmason_edge.cache import PipelineCache

cache = PipelineCache(
    cache_dir="/var/flowmason/pipelines",
    max_size_mb=100,
    ttl_days=30
)

# Cache a pipeline
await cache.store("my-pipeline", pipeline_config)

# Retrieve cached pipeline
pipeline = await cache.get("my-pipeline")

# Check if cached
exists = await cache.exists("my-pipeline")

# Clear old entries
await cache.cleanup()
```

### Model Cache

LLM models are cached locally.

```python
from flowmason_edge.cache import ModelCache

cache = ModelCache(
    cache_dir="/var/flowmason/models",
    max_size_gb=50
)

# Download and cache model
await cache.ensure_model("llama2")

# Get model path
path = cache.get_model_path("llama2")
```

### Result Store

Execution results are stored for sync.

```python
from flowmason_edge.cache import ResultStore

store = ResultStore(
    store_dir="/var/flowmason/results",
    retention_days=30
)

# Store result
await store.save(run_id, result)

# Get pending results (not yet synced)
pending = await store.get_pending()

# Mark as synced
await store.mark_synced(run_id)
```

## Cloud Sync

### SyncManager

Synchronizes with the cloud when connectivity is available.

```python
from flowmason_edge import SyncManager

sync = SyncManager(
    cloud_url="https://studio.flowmason.io",
    api_key="your-api-key",
    sync_interval=60,
    ping_interval=30
)

# Check connection status
status = sync.status  # SyncStatus.ONLINE or SyncStatus.OFFLINE

# Manual sync
await sync.sync_results()
await sync.sync_pipelines()

# Set status callback
sync.on_status_change = lambda status: print(f"Status: {status}")

# Start background sync
await sync.start()

# Stop sync
await sync.stop()
```

## CLI Commands

```bash
# Start edge runtime
fm-edge start

# Check status
fm-edge status

# Run pipeline locally
fm-edge run my-pipeline --input data.json

# Sync with cloud
fm-edge sync

# List cached pipelines
fm-edge list

# Clear cache
fm-edge clear-cache --pipelines --models

# Configure
fm-edge config set cloud_url https://studio.flowmason.io
fm-edge config set api_key your-key
```

## HTTP API

The edge runtime exposes a local HTTP API:

```bash
# Start server
fm-edge serve --port 8080
```

### Endpoints

```
POST /run/{pipeline_id}     # Execute pipeline
GET  /status/{run_id}       # Get run status
GET  /pipelines             # List cached pipelines
GET  /health                # Health check
POST /sync                  # Trigger sync
```

## Environment Variables

```bash
FLOWMASON_EDGE_DATA_DIR=/var/flowmason/edge
FLOWMASON_CLOUD_URL=https://studio.flowmason.io
FLOWMASON_API_KEY=your-api-key
FLOWMASON_LLM_BACKEND=ollama
FLOWMASON_LLM_MODEL=llama2
OLLAMA_HOST=http://localhost:11434
```

## Resource Constraints

For resource-constrained devices:

```python
config = EdgeConfig(
    max_concurrent=1,           # Single execution
    execution_timeout=120,      # 2 minute timeout
    pipeline_cache_size_mb=50,  # Smaller cache
    model_cache_size_gb=10,     # Smaller model cache
)
```

## Best Practices

1. **Pre-cache Pipelines**: Download pipelines before going offline
2. **Use Quantized Models**: Use GGUF quantized models for smaller footprint
3. **Set Retention Limits**: Configure result retention to prevent disk fill
4. **Monitor Sync Status**: Alert on extended offline periods
5. **Test Offline**: Verify pipelines work without cloud connectivity
