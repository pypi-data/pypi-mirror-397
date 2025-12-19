"""
Model Cache for FlowMason Edge.

Manages local LLM models for offline execution.
"""

import hashlib
import json
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CachedModel:
    """Metadata about a cached model."""
    name: str
    filename: str
    size_bytes: int
    quantization: Optional[str]
    family: str
    cached_at: datetime
    last_used: datetime
    source_url: Optional[str]
    checksum: Optional[str]
    path: Path


class ModelCache:
    """
    Cache for local LLM models.

    Manages GGUF and other model files for offline execution.
    Supports downloading from HuggingFace and other sources.

    Example:
        cache = ModelCache("/var/flowmason/models")

        # Download and cache a model
        model = await cache.download("TheBloke/Llama-2-7B-Chat-GGUF", "llama-2-7b-chat.Q4_K_M.gguf")

        # Get path to cached model
        path = cache.get_path("llama-2-7b-chat")

        # List available models
        for model in cache.list():
            print(f"{model.name}: {model.size_bytes / 1e9:.1f}GB")
    """

    METADATA_FILE = "models_metadata.json"
    DEFAULT_CACHE_SIZE_GB = 50

    def __init__(
        self,
        cache_dir: str,
        max_size_gb: int = DEFAULT_CACHE_SIZE_GB,
    ):
        """
        Initialize the model cache.

        Args:
            cache_dir: Directory for model storage
            max_size_gb: Maximum cache size in GB
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self._metadata: Dict[str, CachedModel] = {}

        self._ensure_dirs()
        self._load_metadata()

    def _ensure_dirs(self) -> None:
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _load_metadata(self) -> None:
        """Load cache metadata from disk."""
        metadata_path = self.cache_dir / self.METADATA_FILE
        if metadata_path.exists():
            try:
                data = json.loads(metadata_path.read_text())
                for name, item in data.get("models", {}).items():
                    self._metadata[name] = CachedModel(
                        name=item["name"],
                        filename=item["filename"],
                        size_bytes=item["size_bytes"],
                        quantization=item.get("quantization"),
                        family=item.get("family", ""),
                        cached_at=datetime.fromisoformat(item["cached_at"]),
                        last_used=datetime.fromisoformat(item["last_used"]),
                        source_url=item.get("source_url"),
                        checksum=item.get("checksum"),
                        path=Path(item["path"]),
                    )
            except Exception as e:
                logger.warning(f"Failed to load model cache metadata: {e}")

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        metadata_path = self.cache_dir / self.METADATA_FILE
        data = {
            "version": "1.0",
            "updated_at": datetime.utcnow().isoformat(),
            "models": {
                name: {
                    "name": item.name,
                    "filename": item.filename,
                    "size_bytes": item.size_bytes,
                    "quantization": item.quantization,
                    "family": item.family,
                    "cached_at": item.cached_at.isoformat(),
                    "last_used": item.last_used.isoformat(),
                    "source_url": item.source_url,
                    "checksum": item.checksum,
                    "path": str(item.path),
                }
                for name, item in self._metadata.items()
            },
        }
        metadata_path.write_text(json.dumps(data, indent=2))

    def has(self, name: str) -> bool:
        """Check if a model is cached."""
        if name not in self._metadata:
            return False
        return self._metadata[name].path.exists()

    def get_path(self, name: str) -> Optional[Path]:
        """Get path to a cached model."""
        if not self.has(name):
            return None

        item = self._metadata[name]
        item.last_used = datetime.utcnow()
        self._save_metadata()

        return item.path

    def list(self) -> List[CachedModel]:
        """List all cached models."""
        return list(self._metadata.values())

    def get_info(self, name: str) -> Optional[CachedModel]:
        """Get info about a cached model."""
        return self._metadata.get(name)

    def get_size(self) -> int:
        """Get total cache size in bytes."""
        return sum(item.size_bytes for item in self._metadata.values())

    def add_local(
        self,
        model_path: str,
        name: Optional[str] = None,
        copy: bool = False,
    ) -> CachedModel:
        """
        Add a local model file to the cache.

        Args:
            model_path: Path to model file
            name: Name for the model (defaults to filename)
            copy: Copy file to cache dir (vs symlink)

        Returns:
            CachedModel metadata
        """
        source_path = Path(model_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        name = name or source_path.stem
        filename = source_path.name

        # Determine target path
        if copy:
            target_path = self.cache_dir / filename
            if not target_path.exists():
                shutil.copy2(source_path, target_path)
        else:
            target_path = source_path

        # Extract info from filename
        quantization = self._extract_quantization(filename)
        family = self._extract_family(filename)

        now = datetime.utcnow()
        cached = CachedModel(
            name=name,
            filename=filename,
            size_bytes=target_path.stat().st_size,
            quantization=quantization,
            family=family,
            cached_at=now,
            last_used=now,
            source_url=None,
            checksum=None,
            path=target_path,
        )

        self._metadata[name] = cached
        self._save_metadata()

        logger.info(f"Added model to cache: {name}")
        return cached

    async def download(
        self,
        repo_id: str,
        filename: str,
        name: Optional[str] = None,
        revision: str = "main",
        progress_callback=None,
    ) -> CachedModel:
        """
        Download a model from HuggingFace.

        Args:
            repo_id: HuggingFace repo (e.g., "TheBloke/Llama-2-7B-Chat-GGUF")
            filename: Model filename
            name: Local name for the model
            revision: Git revision
            progress_callback: Callback for download progress

        Returns:
            CachedModel metadata
        """
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            raise ImportError("huggingface_hub required. Run: pip install huggingface_hub")

        name = name or Path(filename).stem

        # Check if already cached
        if self.has(name):
            logger.info(f"Model already cached: {name}")
            return self._metadata[name]

        # Ensure space
        await self._enforce_size_limit_async()

        logger.info(f"Downloading {filename} from {repo_id}...")

        # Download
        try:
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                revision=revision,
                cache_dir=str(self.cache_dir / "hf_cache"),
            )

            # Copy to our cache structure
            target_path = self.cache_dir / filename
            shutil.copy2(local_path, target_path)

            # Compute checksum
            checksum = self._compute_checksum(target_path)

            # Extract info
            quantization = self._extract_quantization(filename)
            family = self._extract_family(filename)

            now = datetime.utcnow()
            cached = CachedModel(
                name=name,
                filename=filename,
                size_bytes=target_path.stat().st_size,
                quantization=quantization,
                family=family,
                cached_at=now,
                last_used=now,
                source_url=f"https://huggingface.co/{repo_id}",
                checksum=checksum,
                path=target_path,
            )

            self._metadata[name] = cached
            self._save_metadata()

            logger.info(f"Downloaded and cached: {name}")
            return cached

        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise

    def remove(self, name: str, delete_file: bool = True) -> bool:
        """
        Remove a model from cache.

        Args:
            name: Model name
            delete_file: Also delete the model file

        Returns:
            True if removed
        """
        if name not in self._metadata:
            return False

        item = self._metadata[name]

        if delete_file and item.path.exists():
            try:
                item.path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete model file: {e}")

        del self._metadata[name]
        self._save_metadata()

        logger.info(f"Removed model from cache: {name}")
        return True

    def clear(self, delete_files: bool = True) -> None:
        """Clear all cached models."""
        if delete_files:
            for item in self._metadata.values():
                try:
                    if item.path.exists():
                        item.path.unlink()
                except Exception:
                    pass

        self._metadata.clear()
        self._save_metadata()
        logger.info("Model cache cleared")

    def _extract_quantization(self, filename: str) -> Optional[str]:
        """Extract quantization from filename."""
        import re
        match = re.search(r'Q\d+[_\w]*', filename, re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_family(self, filename: str) -> str:
        """Extract model family from filename."""
        lower = filename.lower()
        families = ["llama", "mistral", "mixtral", "phi", "gemma", "qwen", "yi", "falcon"]
        for family in families:
            if family in lower:
                return family
        return "unknown"

    def _compute_checksum(self, path: Path) -> str:
        """Compute SHA256 checksum of file."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    async def _enforce_size_limit_async(self) -> None:
        """Enforce cache size limit."""
        current_size = self.get_size()

        if current_size <= self.max_size_bytes:
            return

        # Sort by last used (oldest first)
        items = sorted(
            self._metadata.items(),
            key=lambda x: x[1].last_used,
        )

        for name, item in items:
            if current_size <= self.max_size_bytes * 0.8:
                break

            self.remove(name)
            current_size -= item.size_bytes
