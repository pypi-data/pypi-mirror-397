"""
OpenAI Embedding Provider

Supports OpenAI's text-embedding-3-small, text-embedding-3-large,
and text-embedding-ada-002 models.
"""

import os
from typing import Dict, List, Optional

from .base import (
    EmbeddingProvider,
    EmbeddingResponse,
    register_embedding_provider,
)


@register_embedding_provider
class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    Embedding provider for OpenAI's embedding models.

    Models:
    - text-embedding-3-small: Fast, cost-effective (1536 dims, can reduce to 512)
    - text-embedding-3-large: High performance (3072 dims, can reduce)
    - text-embedding-ada-002: Legacy model (1536 dims fixed)

    Supports dimension reduction for text-embedding-3 models.
    """

    # Pricing per 1M tokens
    DEFAULT_PRICING = {"input": 0.02}

    MODEL_PRICING = {
        "text-embedding-3-small": {"input": 0.02},
        "text-embedding-3-large": {"input": 0.13},
        "text-embedding-ada-002": {"input": 0.10},
    }

    # Default dimensions per model
    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
        timeout: int = 60,
        max_retries: int = 3,
        batch_size: int = 100,
        pricing: Optional[Dict[str, float]] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key."
            )

        model = model or "text-embedding-3-small"
        pricing = pricing or self.MODEL_PRICING.get(model, self.DEFAULT_PRICING)

        super().__init__(
            api_key=api_key,
            model=model,
            dimensions=dimensions,
            timeout=timeout,
            max_retries=max_retries,
            batch_size=batch_size,
            pricing=pricing,
            **kwargs
        )
        self.base_url = base_url
        self._client = None
        self._async_client = None

    @property
    def client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                    base_url=self.base_url,
                )
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._client

    @property
    def async_client(self):
        """Lazy-load the async OpenAI client."""
        if self._async_client is None:
            try:
                from openai import AsyncOpenAI
                self._async_client = AsyncOpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                    base_url=self.base_url,
                )
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._async_client

    @property
    def name(self) -> str:
        return "openai_embeddings"

    @property
    def default_model(self) -> str:
        return "text-embedding-3-small"

    @property
    def available_models(self) -> List[str]:
        return list(self.MODEL_PRICING.keys())

    @property
    def default_dimensions(self) -> int:
        model = self.model or self.default_model
        return self.MODEL_DIMENSIONS.get(model, 1536)

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
            dimensions: Override dimensions (only for text-embedding-3-*)
            **kwargs: Additional options

        Returns:
            EmbeddingResponse with embedding vectors
        """
        model = model or self.model or self.default_model
        dims = dimensions or self.dimensions

        try:
            def _call():
                # Build request parameters
                params = {
                    "model": model,
                    "input": texts,
                }

                # Only text-embedding-3-* models support dimension reduction
                if dims and model.startswith("text-embedding-3"):
                    params["dimensions"] = dims

                return self.client.embeddings.create(**params)

            response, duration_ms = self._time_call(_call)

            # Extract embeddings
            embeddings = [item.embedding for item in response.data]

            # Determine actual dimensions
            actual_dims = len(embeddings[0]) if embeddings else (dims or self.default_dimensions)

            usage = self._build_usage_dict(
                total_tokens=response.usage.total_tokens,
                model=model,
            )

            return EmbeddingResponse(
                embeddings=embeddings,
                model=model,
                dimensions=actual_dims,
                usage=usage,
                duration_ms=duration_ms,
            )

        except Exception as e:
            return EmbeddingResponse(
                embeddings=[],
                model=model,
                dimensions=dims or self.default_dimensions,
                success=False,
                error=str(e),
            )

    async def embed_async(
        self,
        texts: List[str],
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """
        Generate embeddings asynchronously.

        Args:
            texts: List of texts to embed
            model: Override default model
            dimensions: Override dimensions (only for text-embedding-3-*)
            **kwargs: Additional options

        Returns:
            EmbeddingResponse with embedding vectors
        """
        import time
        model = model or self.model or self.default_model
        dims = dimensions or self.dimensions

        try:
            # Build request parameters
            params = {
                "model": model,
                "input": texts,
            }

            if dims and model.startswith("text-embedding-3"):
                params["dimensions"] = dims

            start = time.perf_counter()
            response = await self.async_client.embeddings.create(**params)
            duration_ms = int((time.perf_counter() - start) * 1000)

            embeddings = [item.embedding for item in response.data]
            actual_dims = len(embeddings[0]) if embeddings else (dims or self.default_dimensions)

            usage = self._build_usage_dict(
                total_tokens=response.usage.total_tokens,
                model=model,
            )

            return EmbeddingResponse(
                embeddings=embeddings,
                model=model,
                dimensions=actual_dims,
                usage=usage,
                duration_ms=duration_ms,
            )

        except Exception as e:
            return EmbeddingResponse(
                embeddings=[],
                model=model,
                dimensions=dims or self.default_dimensions,
                success=False,
                error=str(e),
            )
