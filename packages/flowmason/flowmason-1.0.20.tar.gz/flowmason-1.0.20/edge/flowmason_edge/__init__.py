"""
FlowMason Edge - Lightweight Edge Runtime.

Run FlowMason pipelines on edge devices with:
- Offline-first execution
- Local LLM support (Ollama, llama.cpp)
- Pipeline and model caching
- Store-and-forward for results
- Cloud sync when online

Example:
    from flowmason_edge import EdgeRuntime

    # Initialize edge runtime
    runtime = EdgeRuntime(
        cache_dir="/var/flowmason/cache",
        cloud_url="https://studio.flowmason.io",
    )

    # Run a pipeline (works offline)
    result = await runtime.run("my-pipeline", inputs={"key": "value"})

    # Sync results when online
    await runtime.sync()
"""

__version__ = "0.1.0"

from flowmason_edge.runtime.edge_executor import EdgeExecutor, ExecutionResult
from flowmason_edge.runtime.edge_runtime import EdgeRuntime, EdgeConfig, create_runtime
from flowmason_edge.runtime.sync_manager import SyncManager, SyncStatus
from flowmason_edge.cache.pipeline_cache import PipelineCache
from flowmason_edge.cache.model_cache import ModelCache
from flowmason_edge.cache.result_store import ResultStore
from flowmason_edge.adapters.base import LocalLLMAdapter, GenerationConfig, GenerationResult
from flowmason_edge.adapters.ollama import OllamaAdapter
from flowmason_edge.adapters.llamacpp import LlamaCppAdapter

__all__ = [
    # Runtime
    "EdgeRuntime",
    "EdgeConfig",
    "EdgeExecutor",
    "ExecutionResult",
    "create_runtime",
    # Cache
    "PipelineCache",
    "ModelCache",
    "ResultStore",
    # Sync
    "SyncManager",
    "SyncStatus",
    # Adapters
    "LocalLLMAdapter",
    "OllamaAdapter",
    "LlamaCppAdapter",
    "GenerationConfig",
    "GenerationResult",
]
