"""
Embedding Provider Base Classes

Provides the base infrastructure for embedding providers that convert
text into vector representations for semantic search and RAG.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EmbeddingResponse:
    """
    Standardized response from an embedding provider.
    """
    embeddings: List[List[float]]  # List of embedding vectors
    model: str
    dimensions: int
    usage: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "embeddings": self.embeddings,
            "model": self.model,
            "dimensions": self.dimensions,
            "usage": self.usage,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class EmbeddingConfig:
    """Configuration for an embedding provider instance."""
    provider_type: str
    api_key_env: str
    model: Optional[str] = None
    dimensions: Optional[int] = None
    timeout: int = 60
    max_retries: int = 3
    batch_size: int = 100  # Max texts per batch
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_type": self.provider_type,
            "api_key_env": self.api_key_env,
            "model": self.model,
            "dimensions": self.dimensions,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "batch_size": self.batch_size,
            "extra_config": self.extra_config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmbeddingConfig":
        return cls(**data)


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.

    All embedding providers must implement:
    - name: Provider identifier
    - default_model: Default embedding model
    - embed(): Generate embeddings for text(s)
    - available_models: List of supported models
    - default_dimensions: Default vector dimensions

    Example implementation:

        class MyEmbeddingProvider(EmbeddingProvider):
            @property
            def name(self) -> str:
                return "my_embeddings"

            @property
            def default_model(self) -> str:
                return "my-embed-v1"

            @property
            def available_models(self) -> List[str]:
                return ["my-embed-v1", "my-embed-v2"]

            @property
            def default_dimensions(self) -> int:
                return 1536

            def embed(self, texts, model=None, dimensions=None) -> EmbeddingResponse:
                # Your embedding logic here
                pass
    """

    # Default pricing per 1M tokens (override in subclasses)
    DEFAULT_PRICING = {"input": 0.0}

    # Model-specific pricing
    MODEL_PRICING: Dict[str, Dict[str, float]] = {}

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
        timeout: int = 60,
        max_retries: int = 3,
        batch_size: int = 100,
        pricing: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """
        Initialize the embedding provider.

        Args:
            api_key: API key (or use environment variable)
            model: Default model to use
            dimensions: Override default dimensions
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            batch_size: Maximum texts per batch request
            pricing: Custom pricing per 1M tokens {"input": X}
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        self.timeout = timeout
        self.max_retries = max_retries
        self.batch_size = batch_size
        self.pricing = pricing or self.DEFAULT_PRICING
        self.extra_config = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier (e.g., 'openai_embeddings')."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default embedding model for this provider."""
        pass

    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """List of available embedding models."""
        pass

    @property
    @abstractmethod
    def default_dimensions(self) -> int:
        """Default embedding dimensions."""
        pass

    @abstractmethod
    def embed(
        self,
        texts: List[str],
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to embed
            model: Override default model
            dimensions: Override default dimensions (if supported)
            **kwargs: Provider-specific options

        Returns:
            EmbeddingResponse with embedding vectors
        """
        pass

    async def embed_async(
        self,
        texts: List[str],
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """
        Async version of embed().

        Default implementation wraps sync call.
        Override for native async support.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.embed(texts=texts, model=model, dimensions=dimensions, **kwargs)
        )

    def embed_single(
        self,
        text: str,
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
        **kwargs
    ) -> List[float]:
        """
        Convenience method to embed a single text.

        Args:
            text: Text to embed
            model: Override default model
            dimensions: Override default dimensions

        Returns:
            Single embedding vector
        """
        response = self.embed([text], model=model, dimensions=dimensions, **kwargs)
        if response.success and response.embeddings:
            return response.embeddings[0]
        raise ValueError(response.error or "Failed to generate embedding")

    async def embed_single_async(
        self,
        text: str,
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
        **kwargs
    ) -> List[float]:
        """Async version of embed_single()."""
        response = await self.embed_async([text], model=model, dimensions=dimensions, **kwargs)
        if response.success and response.embeddings:
            return response.embeddings[0]
        raise ValueError(response.error or "Failed to generate embedding")

    def embed_batched(
        self,
        texts: List[str],
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """
        Embed texts in batches to handle large inputs.

        Args:
            texts: List of texts to embed
            model: Override default model
            dimensions: Override default dimensions

        Returns:
            Combined EmbeddingResponse with all embeddings
        """
        all_embeddings: List[List[float]] = []
        total_tokens = 0
        total_duration = 0

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            response = self.embed(batch, model=model, dimensions=dimensions, **kwargs)

            if not response.success:
                return response  # Return error immediately

            all_embeddings.extend(response.embeddings)
            total_tokens += response.usage.get("total_tokens", 0)
            total_duration += response.duration_ms

        model = model or self.model or self.default_model
        dims = dimensions or self.dimensions or self.default_dimensions

        return EmbeddingResponse(
            embeddings=all_embeddings,
            model=model,
            dimensions=dims,
            usage={"total_tokens": total_tokens},
            duration_ms=total_duration,
        )

    def get_model_pricing(self, model: Optional[str] = None) -> Dict[str, float]:
        """Get pricing for a specific model."""
        model = model or self.model or self.default_model
        return self.MODEL_PRICING.get(model, self.DEFAULT_PRICING)

    def calculate_cost(self, tokens: int, model: Optional[str] = None) -> float:
        """Calculate cost for a request."""
        pricing = self.get_model_pricing(model)
        return (tokens / 1_000_000) * pricing.get("input", 0)

    def _time_call(self, func, *args, **kwargs) -> tuple:
        """Time a function call."""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms

    def _build_usage_dict(
        self,
        total_tokens: int = 0,
        model: Optional[str] = None,
        **extra
    ) -> Dict[str, Any]:
        """Build a standardized usage dictionary."""
        model = model or self.model or self.default_model
        cost = self.calculate_cost(total_tokens, model)

        return {
            "total_tokens": total_tokens,
            "cost_usd": cost,
            "model": model,
            "provider": self.name,
            **extra
        }

    def get_config(self) -> EmbeddingConfig:
        """Get the configuration for this provider instance."""
        return EmbeddingConfig(
            provider_type=self.name,
            api_key_env=f"{self.name.upper()}_API_KEY",
            model=self.model,
            dimensions=self.dimensions,
            timeout=self.timeout,
            max_retries=self.max_retries,
            batch_size=self.batch_size,
            extra_config=self.extra_config,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model or self.default_model})"


# Embedding Provider Registry
_EMBEDDING_REGISTRY: Dict[str, type] = {}


def register_embedding_provider(provider_class: type) -> type:
    """
    Register an embedding provider class.

    Can be used as a decorator:

        @register_embedding_provider
        class MyEmbeddingProvider(EmbeddingProvider):
            ...
    """
    if not issubclass(provider_class, EmbeddingProvider):
        raise ValueError(f"{provider_class.__name__} must extend EmbeddingProvider")

    try:
        temp = object.__new__(provider_class)
        temp.api_key = "temp"
        temp.model = None
        temp.dimensions = None
        temp.timeout = 60
        temp.max_retries = 3
        temp.batch_size = 100
        temp.pricing = provider_class.DEFAULT_PRICING
        temp.extra_config = {}
        name = temp.name
    except Exception:
        name = provider_class.__name__.lower().replace("provider", "").replace("embedding", "")

    _EMBEDDING_REGISTRY[name] = provider_class
    return provider_class


def get_embedding_provider(name: str) -> Optional[type]:
    """Get an embedding provider class by name."""
    return _EMBEDDING_REGISTRY.get(name)


def list_embedding_providers() -> List[str]:
    """List all registered embedding provider names."""
    return list(_EMBEDDING_REGISTRY.keys())


def create_embedding_provider(config: EmbeddingConfig) -> EmbeddingProvider:
    """Create an embedding provider instance from configuration."""
    import os

    provider_class = get_embedding_provider(config.provider_type)
    if not provider_class:
        raise ValueError(f"Unknown embedding provider type: {config.provider_type}")

    api_key = os.environ.get(config.api_key_env)

    provider: EmbeddingProvider = provider_class(
        api_key=api_key,
        model=config.model,
        dimensions=config.dimensions,
        timeout=config.timeout,
        max_retries=config.max_retries,
        batch_size=config.batch_size,
        **config.extra_config
    )
    return provider
