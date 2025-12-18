"""
Edge Runtime for FlowMason Edge.

Main runtime class that orchestrates edge execution.
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from flowmason_edge.adapters.base import LocalLLMAdapter
from flowmason_edge.cache.model_cache import ModelCache
from flowmason_edge.cache.pipeline_cache import PipelineCache
from flowmason_edge.cache.result_store import ResultStore
from flowmason_edge.runtime.edge_executor import EdgeExecutor, ExecutionResult
from flowmason_edge.runtime.sync_manager import SyncManager, SyncState

logger = logging.getLogger(__name__)


@dataclass
class EdgeConfig:
    """Configuration for edge runtime."""
    # Storage paths
    data_dir: str = "/var/flowmason/edge"
    pipeline_cache_dir: Optional[str] = None
    model_cache_dir: Optional[str] = None
    result_store_dir: Optional[str] = None

    # Cloud connection
    cloud_url: Optional[str] = None
    api_key: Optional[str] = None

    # Execution settings
    max_concurrent: int = 2
    execution_timeout: int = 300

    # Cache settings
    pipeline_cache_size_mb: int = 100
    pipeline_ttl_days: int = 30
    model_cache_size_gb: int = 50
    result_retention_days: int = 30

    # Sync settings
    sync_interval: int = 60
    auto_sync: bool = True

    # LLM settings
    llm_backend: str = "ollama"  # ollama, llamacpp
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None

    @classmethod
    def from_env(cls) -> "EdgeConfig":
        """Create config from environment variables."""
        return cls(
            data_dir=os.environ.get("FLOWMASON_EDGE_DATA_DIR", "/var/flowmason/edge"),
            cloud_url=os.environ.get("FLOWMASON_CLOUD_URL"),
            api_key=os.environ.get("FLOWMASON_API_KEY"),
            max_concurrent=int(os.environ.get("FLOWMASON_MAX_CONCURRENT", "2")),
            llm_backend=os.environ.get("FLOWMASON_LLM_BACKEND", "ollama"),
            llm_model=os.environ.get("FLOWMASON_LLM_MODEL"),
            llm_base_url=os.environ.get("FLOWMASON_LLM_BASE_URL"),
            auto_sync=os.environ.get("FLOWMASON_AUTO_SYNC", "true").lower() == "true",
        )


@dataclass
class RuntimeStatus:
    """Runtime status information."""
    running: bool
    executor_ready: bool
    llm_available: bool
    sync_state: Optional[SyncState]
    cached_pipelines: int
    cached_models: int
    pending_results: int
    uptime_seconds: int


class EdgeRuntime:
    """
    Main runtime for FlowMason Edge.

    Provides a complete edge execution environment with:
    - Local LLM execution
    - Pipeline caching
    - Result store-and-forward
    - Cloud synchronization

    Example:
        config = EdgeConfig.from_env()
        runtime = EdgeRuntime(config)

        await runtime.start()

        # Execute a pipeline
        result = await runtime.execute("my-pipeline", {"input": "data"})

        # Sync with cloud
        await runtime.sync()

        await runtime.stop()
    """

    def __init__(self, config: EdgeConfig):
        """
        Initialize the edge runtime.

        Args:
            config: Edge configuration
        """
        self.config = config
        self._started_at: Optional[datetime] = None
        self._running = False

        # Initialize paths
        self._data_dir = Path(config.data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components (lazy)
        self._pipeline_cache: Optional[PipelineCache] = None
        self._model_cache: Optional[ModelCache] = None
        self._result_store: Optional[ResultStore] = None
        self._llm_adapter: Optional[LocalLLMAdapter] = None
        self._executor: Optional[EdgeExecutor] = None
        self._sync_manager: Optional[SyncManager] = None

        self._progress_callbacks: List[Callable] = []

    @property
    def pipeline_cache(self) -> PipelineCache:
        """Get pipeline cache."""
        if self._pipeline_cache is None:
            cache_dir = self.config.pipeline_cache_dir or str(
                self._data_dir / "pipelines"
            )
            self._pipeline_cache = PipelineCache(
                cache_dir=cache_dir,
                max_size_mb=self.config.pipeline_cache_size_mb,
                ttl_days=self.config.pipeline_ttl_days,
            )
        return self._pipeline_cache

    @property
    def model_cache(self) -> ModelCache:
        """Get model cache."""
        if self._model_cache is None:
            cache_dir = self.config.model_cache_dir or str(self._data_dir / "models")
            self._model_cache = ModelCache(
                cache_dir=cache_dir,
                max_size_gb=self.config.model_cache_size_gb,
            )
        return self._model_cache

    @property
    def result_store(self) -> ResultStore:
        """Get result store."""
        if self._result_store is None:
            store_dir = self.config.result_store_dir or str(self._data_dir / "results")
            self._result_store = ResultStore(
                store_dir=store_dir,
                retention_days=self.config.result_retention_days,
            )
        return self._result_store

    @property
    def llm_adapter(self) -> Optional[LocalLLMAdapter]:
        """Get LLM adapter."""
        return self._llm_adapter

    @property
    def sync_manager(self) -> Optional[SyncManager]:
        """Get sync manager."""
        return self._sync_manager

    @property
    def status(self) -> RuntimeStatus:
        """Get runtime status."""
        sync_state = self._sync_manager.state if self._sync_manager else None

        cached_pipelines = len(self.pipeline_cache.list())
        cached_models = len(self.model_cache.list())

        stats = self.result_store.get_stats()
        pending_results = stats.get("pending", 0) + stats.get("failed", 0)

        uptime = 0
        if self._started_at:
            uptime = int((datetime.utcnow() - self._started_at).total_seconds())

        return RuntimeStatus(
            running=self._running,
            executor_ready=self._executor is not None,
            llm_available=self._llm_adapter is not None,
            sync_state=sync_state,
            cached_pipelines=cached_pipelines,
            cached_models=cached_models,
            pending_results=pending_results,
            uptime_seconds=uptime,
        )

    async def start(self) -> None:
        """Start the edge runtime."""
        if self._running:
            return

        logger.info("Starting FlowMason Edge Runtime...")
        self._started_at = datetime.utcnow()

        # Initialize LLM adapter
        await self._init_llm_adapter()

        # Initialize executor
        self._executor = EdgeExecutor(
            llm_adapter=self._llm_adapter,
            max_concurrent=self.config.max_concurrent,
            timeout_seconds=self.config.execution_timeout,
            progress_callback=self._on_progress,
        )

        # Initialize sync manager
        if self.config.cloud_url and self.config.api_key:
            self._sync_manager = SyncManager(
                cloud_url=self.config.cloud_url,
                api_key=self.config.api_key,
                result_store=self.result_store,
                pipeline_cache=self.pipeline_cache,
                sync_interval=self.config.sync_interval,
                on_status_change=self._on_sync_status_change,
            )

            if self.config.auto_sync:
                await self._sync_manager.start()

        self._running = True
        logger.info("FlowMason Edge Runtime started")

    async def stop(self) -> None:
        """Stop the edge runtime."""
        if not self._running:
            return

        logger.info("Stopping FlowMason Edge Runtime...")

        # Stop sync manager
        if self._sync_manager:
            await self._sync_manager.stop()

        # Unload LLM
        if self._llm_adapter:
            await self._llm_adapter.unload_model()

        self._running = False
        logger.info("FlowMason Edge Runtime stopped")

    async def execute(
        self,
        pipeline_name: str,
        inputs: Dict[str, Any],
        run_id: Optional[str] = None,
        store_result: bool = True,
    ) -> ExecutionResult:
        """
        Execute a pipeline.

        Args:
            pipeline_name: Name of pipeline to execute
            inputs: Input data
            run_id: Optional run identifier
            store_result: Store result for sync

        Returns:
            ExecutionResult
        """
        if not self._executor:
            raise RuntimeError("Runtime not started")

        # Get pipeline from cache
        pipeline = self.pipeline_cache.get(pipeline_name)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_name}")

        # Execute
        result = await self._executor.execute(
            pipeline=pipeline,
            inputs=inputs,
            run_id=run_id,
        )

        # Store result for sync
        if store_result and result.status.value == "completed":
            self.result_store.store(
                run_id=result.run_id,
                pipeline_name=pipeline_name,
                output=result.output,
                metadata={
                    "started_at": result.started_at.isoformat(),
                    "duration_ms": result.duration_ms,
                },
            )

        return result

    async def execute_config(
        self,
        pipeline: Dict[str, Any],
        inputs: Dict[str, Any],
        run_id: Optional[str] = None,
    ) -> ExecutionResult:
        """
        Execute a pipeline configuration directly.

        Args:
            pipeline: Pipeline configuration
            inputs: Input data
            run_id: Optional run identifier

        Returns:
            ExecutionResult
        """
        if not self._executor:
            raise RuntimeError("Runtime not started")

        return await self._executor.execute(
            pipeline=pipeline,
            inputs=inputs,
            run_id=run_id,
        )

    def cache_pipeline(
        self,
        name: str,
        config: Dict[str, Any],
        version: Optional[str] = None,
    ) -> None:
        """Cache a pipeline for offline execution."""
        self.pipeline_cache.put(name, config, version=version, source="local")
        logger.info(f"Cached pipeline: {name}")

    def list_pipelines(self) -> List[Dict[str, Any]]:
        """List cached pipelines."""
        return [
            {
                "name": p.name,
                "version": p.version,
                "cached_at": p.cached_at.isoformat(),
                "source": p.source,
            }
            for p in self.pipeline_cache.list()
        ]

    def list_models(self) -> List[Dict[str, Any]]:
        """List cached models."""
        return [
            {
                "name": m.name,
                "filename": m.filename,
                "size_gb": m.size_bytes / 1e9,
                "quantization": m.quantization,
                "family": m.family,
            }
            for m in self.model_cache.list()
        ]

    async def download_model(
        self,
        repo_id: str,
        filename: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Download a model from HuggingFace."""
        model = await self.model_cache.download(
            repo_id=repo_id,
            filename=filename,
            name=name,
        )
        return {
            "name": model.name,
            "size_gb": model.size_bytes / 1e9,
            "path": str(model.path),
        }

    async def sync(self) -> Dict[str, Any]:
        """Manually trigger sync with cloud."""
        if not self._sync_manager:
            return {"error": "Sync not configured"}

        results = await self._sync_manager.sync_results()
        pipelines = await self._sync_manager.sync_pipelines()

        return {
            "results": results,
            "pipelines": pipelines,
        }

    async def check_connectivity(self) -> bool:
        """Check cloud connectivity."""
        if not self._sync_manager:
            return False
        return await self._sync_manager.check_connectivity()

    def on_progress(self, callback: Callable) -> None:
        """Register progress callback."""
        self._progress_callbacks.append(callback)

    async def _init_llm_adapter(self) -> None:
        """Initialize LLM adapter."""
        backend = self.config.llm_backend

        if backend == "ollama":
            from flowmason_edge.adapters.ollama import OllamaAdapter

            model = self.config.llm_model or "llama2"
            base_url = self.config.llm_base_url or "http://localhost:11434"

            self._llm_adapter = OllamaAdapter(
                model=model,
                base_url=base_url,
            )

            # Check availability
            if await self._llm_adapter.check_availability():
                logger.info(f"Ollama adapter ready with model: {model}")
            else:
                logger.warning("Ollama not available")
                self._llm_adapter = None

        elif backend == "llamacpp":
            from flowmason_edge.adapters.llamacpp import LlamaCppAdapter

            model = self.config.llm_model
            if not model:
                # Try to find a model in cache
                models = self.model_cache.list()
                if models:
                    model = str(models[0].path)

            if model:
                self._llm_adapter = LlamaCppAdapter(
                    model=model,
                    n_gpu_layers=0,  # CPU only by default
                )

                if await self._llm_adapter.check_availability():
                    logger.info(f"LlamaCpp adapter ready with model: {model}")
                else:
                    logger.warning("LlamaCpp model not available")
                    self._llm_adapter = None
            else:
                logger.warning("No model configured for llamacpp backend")

        else:
            logger.warning(f"Unknown LLM backend: {backend}")

    def _on_progress(
        self,
        run_id: str,
        stage_id: str,
        status: str,
        progress: int,
    ) -> None:
        """Handle progress updates."""
        for callback in self._progress_callbacks:
            try:
                callback(run_id, stage_id, status, progress)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

    def _on_sync_status_change(self, state: SyncState) -> None:
        """Handle sync status changes."""
        logger.debug(f"Sync status: {state.status.value}, connection: {state.connection.value}")


async def create_runtime(
    data_dir: Optional[str] = None,
    cloud_url: Optional[str] = None,
    api_key: Optional[str] = None,
    llm_backend: str = "ollama",
    llm_model: Optional[str] = None,
    auto_start: bool = True,
) -> EdgeRuntime:
    """
    Create and optionally start an edge runtime.

    Args:
        data_dir: Data directory path
        cloud_url: Cloud Studio URL
        api_key: API key
        llm_backend: LLM backend to use
        llm_model: Model to use
        auto_start: Start runtime automatically

    Returns:
        EdgeRuntime instance
    """
    config = EdgeConfig(
        data_dir=data_dir or "/var/flowmason/edge",
        cloud_url=cloud_url,
        api_key=api_key,
        llm_backend=llm_backend,
        llm_model=llm_model,
    )

    runtime = EdgeRuntime(config)

    if auto_start:
        await runtime.start()

    return runtime
