"""
FlowMason Vector Database Providers

Provides vector database providers for storing and searching embeddings,
used in RAG (Retrieval Augmented Generation) pipelines.

Built-in Providers:
- PineconeProvider: Managed vector database service
- ChromaDBProvider: Open-source, local/remote embedding database
- WeaviateProvider: Open-source vector search engine

Usage:
    from flowmason_core.providers.vectordb import (
        PineconeProvider,
        ChromaDBProvider,
        WeaviateProvider,
        VectorRecord,
        get_vectordb_provider,
    )

    # Use directly
    provider = PineconeProvider(index_name="my-index")

    # Upsert vectors
    records = [
        VectorRecord(id="1", embedding=[0.1, 0.2, ...], content="Hello", metadata={"type": "greeting"})
    ]
    await provider.upsert(records)

    # Search
    response = await provider.search(query_vector=[0.1, 0.2, ...], top_k=5)
    for result in response.results:
        print(f"{result.id}: {result.content} (score: {result.score})")

    # Or via registry
    ProviderClass = get_vectordb_provider("pinecone")
"""

from .base import (
    VectorDBConfig,
    VectorDBProvider,
    VectorDeleteResult,
    VectorRecord,
    VectorSearchResponse,
    VectorSearchResult,
    VectorUpsertResult,
    create_vectordb_provider,
    get_vectordb_provider,
    list_vectordb_providers,
    register_vectordb_provider,
)

# Import built-in providers to register them
from .pinecone import PineconeProvider
from .chromadb import ChromaDBProvider
from .weaviate import WeaviateProvider

__all__ = [
    # Base classes
    "VectorDBProvider",
    "VectorRecord",
    "VectorSearchResult",
    "VectorSearchResponse",
    "VectorUpsertResult",
    "VectorDeleteResult",
    "VectorDBConfig",
    # Registry functions
    "register_vectordb_provider",
    "get_vectordb_provider",
    "list_vectordb_providers",
    "create_vectordb_provider",
    # Built-in providers
    "PineconeProvider",
    "ChromaDBProvider",
    "WeaviateProvider",
]
