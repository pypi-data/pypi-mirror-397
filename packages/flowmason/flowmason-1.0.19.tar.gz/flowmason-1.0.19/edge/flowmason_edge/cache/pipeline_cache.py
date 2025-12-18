"""
Pipeline Cache for FlowMason Edge.

Caches pipeline configurations for offline execution.
"""

import hashlib
import json
import logging
import shutil
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CachedPipeline:
    """Metadata about a cached pipeline."""
    name: str
    version: str
    hash: str
    cached_at: datetime
    last_accessed: datetime
    size_bytes: int
    source: str  # "cloud", "local"
    path: Path


class PipelineCache:
    """
    Cache for pipeline configurations.

    Stores pipeline definitions locally for offline execution.
    Supports automatic sync with cloud when online.

    Example:
        cache = PipelineCache("/var/flowmason/cache/pipelines")

        # Cache a pipeline
        cache.put("my-pipeline", pipeline_config)

        # Get cached pipeline
        pipeline = cache.get("my-pipeline")

        # Check if available offline
        if cache.has("my-pipeline"):
            print("Pipeline available offline")
    """

    METADATA_FILE = "cache_metadata.json"
    PIPELINES_DIR = "pipelines"

    def __init__(
        self,
        cache_dir: str,
        max_size_mb: int = 100,
        ttl_days: int = 30,
    ):
        """
        Initialize the pipeline cache.

        Args:
            cache_dir: Directory for cache storage
            max_size_mb: Maximum cache size in MB
            ttl_days: Time-to-live for cached items
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_days * 24 * 60 * 60
        self._metadata: Dict[str, CachedPipeline] = {}

        self._ensure_dirs()
        self._load_metadata()

    def _ensure_dirs(self) -> None:
        """Ensure cache directories exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / self.PIPELINES_DIR).mkdir(exist_ok=True)

    def _load_metadata(self) -> None:
        """Load cache metadata from disk."""
        metadata_path = self.cache_dir / self.METADATA_FILE
        if metadata_path.exists():
            try:
                data = json.loads(metadata_path.read_text())
                for name, item in data.get("pipelines", {}).items():
                    self._metadata[name] = CachedPipeline(
                        name=item["name"],
                        version=item["version"],
                        hash=item["hash"],
                        cached_at=datetime.fromisoformat(item["cached_at"]),
                        last_accessed=datetime.fromisoformat(item["last_accessed"]),
                        size_bytes=item["size_bytes"],
                        source=item["source"],
                        path=Path(item["path"]),
                    )
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        metadata_path = self.cache_dir / self.METADATA_FILE
        data = {
            "version": "1.0",
            "updated_at": datetime.utcnow().isoformat(),
            "pipelines": {
                name: {
                    "name": item.name,
                    "version": item.version,
                    "hash": item.hash,
                    "cached_at": item.cached_at.isoformat(),
                    "last_accessed": item.last_accessed.isoformat(),
                    "size_bytes": item.size_bytes,
                    "source": item.source,
                    "path": str(item.path),
                }
                for name, item in self._metadata.items()
            },
        }
        metadata_path.write_text(json.dumps(data, indent=2))

    def _compute_hash(self, config: Dict[str, Any]) -> str:
        """Compute hash of pipeline configuration."""
        content = json.dumps(config, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def has(self, name: str, version: Optional[str] = None) -> bool:
        """
        Check if a pipeline is cached.

        Args:
            name: Pipeline name
            version: Optional version (matches any if None)

        Returns:
            True if cached and valid
        """
        key = f"{name}@{version}" if version else name

        # Check simple name first
        if name in self._metadata:
            item = self._metadata[name]
            if version and item.version != version:
                return False
            # Check if file still exists
            if not item.path.exists():
                return False
            # Check TTL
            age = (datetime.utcnow() - item.cached_at).total_seconds()
            if age > self.ttl_seconds:
                return False
            return True

        return key in self._metadata

    def get(self, name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a cached pipeline configuration.

        Args:
            name: Pipeline name
            version: Optional version

        Returns:
            Pipeline configuration or None if not cached
        """
        if not self.has(name, version):
            return None

        item = self._metadata.get(name)
        if not item:
            return None

        try:
            config = json.loads(item.path.read_text())

            # Update last accessed
            item.last_accessed = datetime.utcnow()
            self._save_metadata()

            return config

        except Exception as e:
            logger.error(f"Failed to read cached pipeline: {e}")
            return None

    def put(
        self,
        name: str,
        config: Dict[str, Any],
        version: Optional[str] = None,
        source: str = "local",
    ) -> CachedPipeline:
        """
        Cache a pipeline configuration.

        Args:
            name: Pipeline name
            config: Pipeline configuration
            version: Pipeline version
            source: Where the pipeline came from

        Returns:
            CachedPipeline metadata
        """
        # Compute hash
        config_hash = self._compute_hash(config)

        # Check if already cached with same hash
        if name in self._metadata:
            existing = self._metadata[name]
            if existing.hash == config_hash:
                existing.last_accessed = datetime.utcnow()
                self._save_metadata()
                return existing

        # Ensure space available
        self._enforce_size_limit()

        # Save pipeline
        version = version or config.get("version", "1.0.0")
        filename = f"{name}_{version}_{config_hash}.json"
        path = self.cache_dir / self.PIPELINES_DIR / filename

        path.write_text(json.dumps(config, indent=2))

        # Update metadata
        now = datetime.utcnow()
        cached = CachedPipeline(
            name=name,
            version=version,
            hash=config_hash,
            cached_at=now,
            last_accessed=now,
            size_bytes=path.stat().st_size,
            source=source,
            path=path,
        )

        self._metadata[name] = cached
        self._save_metadata()

        logger.info(f"Cached pipeline: {name} v{version}")
        return cached

    def remove(self, name: str) -> bool:
        """
        Remove a pipeline from cache.

        Args:
            name: Pipeline name

        Returns:
            True if removed
        """
        if name not in self._metadata:
            return False

        item = self._metadata[name]
        try:
            if item.path.exists():
                item.path.unlink()
            del self._metadata[name]
            self._save_metadata()
            logger.info(f"Removed cached pipeline: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove cached pipeline: {e}")
            return False

    def list(self) -> List[CachedPipeline]:
        """List all cached pipelines."""
        return list(self._metadata.values())

    def clear(self) -> None:
        """Clear all cached pipelines."""
        pipelines_dir = self.cache_dir / self.PIPELINES_DIR
        if pipelines_dir.exists():
            shutil.rmtree(pipelines_dir)
            pipelines_dir.mkdir()

        self._metadata.clear()
        self._save_metadata()
        logger.info("Pipeline cache cleared")

    def get_size(self) -> int:
        """Get total cache size in bytes."""
        return sum(item.size_bytes for item in self._metadata.values())

    def _enforce_size_limit(self) -> None:
        """Enforce cache size limit by removing old items."""
        current_size = self.get_size()

        if current_size <= self.max_size_bytes:
            return

        # Sort by last accessed (oldest first)
        items = sorted(
            self._metadata.items(),
            key=lambda x: x[1].last_accessed,
        )

        # Remove until under limit
        for name, item in items:
            if current_size <= self.max_size_bytes * 0.8:  # Keep 20% headroom
                break

            self.remove(name)
            current_size -= item.size_bytes

    def sync_from_cloud(
        self,
        pipeline_names: List[str],
        fetch_func,
    ) -> Dict[str, bool]:
        """
        Sync pipelines from cloud.

        Args:
            pipeline_names: Pipelines to sync
            fetch_func: Async function to fetch pipeline config

        Returns:
            Dict of pipeline name -> success
        """
        import asyncio

        results = {}

        async def sync_pipeline(name: str) -> bool:
            try:
                config = await fetch_func(name)
                if config:
                    self.put(name, config, source="cloud")
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to sync {name}: {e}")
                return False

        async def sync_all():
            tasks = [sync_pipeline(name) for name in pipeline_names]
            return await asyncio.gather(*tasks)

        loop = asyncio.get_event_loop()
        sync_results = loop.run_until_complete(sync_all())

        for name, success in zip(pipeline_names, sync_results):
            results[name] = success

        return results
