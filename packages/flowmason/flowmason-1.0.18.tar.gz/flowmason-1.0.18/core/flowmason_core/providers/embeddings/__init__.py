"""
FlowMason Embedding Providers

Provides embedding providers for converting text to vectors,
used in RAG (Retrieval Augmented Generation) pipelines.

Built-in Providers:
- OpenAIEmbeddingProvider: text-embedding-3-small/large, ada-002

Usage:
    from flowmason_core.providers.embeddings import (
        OpenAIEmbeddingProvider,
        get_embedding_provider,
        list_embedding_providers,
    )

    # Use directly
    provider = OpenAIEmbeddingProvider()
    response = provider.embed(["Hello, world!"])
    embedding = response.embeddings[0]  # List[float]

    # Or via registry
    ProviderClass = get_embedding_provider("openai_embeddings")
    provider = ProviderClass(api_key="...")
"""

from .base import (
    EmbeddingConfig,
    EmbeddingProvider,
    EmbeddingResponse,
    create_embedding_provider,
    get_embedding_provider,
    list_embedding_providers,
    register_embedding_provider,
)

# Import built-in providers to register them
from .openai import OpenAIEmbeddingProvider

__all__ = [
    # Base classes
    "EmbeddingProvider",
    "EmbeddingResponse",
    "EmbeddingConfig",
    # Registry functions
    "register_embedding_provider",
    "get_embedding_provider",
    "list_embedding_providers",
    "create_embedding_provider",
    # Built-in providers
    "OpenAIEmbeddingProvider",
]
