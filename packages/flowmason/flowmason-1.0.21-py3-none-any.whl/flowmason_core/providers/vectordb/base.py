"""
Vector Database Provider Base Classes

Provides the base infrastructure for vector database providers used in
RAG (Retrieval Augmented Generation) pipelines for semantic search.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VectorSearchResult:
    """A single search result from a vector database."""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
            "embedding": self.embedding,
        }


@dataclass
class VectorUpsertResult:
    """Result of an upsert operation."""
    upserted_count: int
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "upserted_count": self.upserted_count,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class VectorDeleteResult:
    """Result of a delete operation."""
    deleted_count: int
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deleted_count": self.deleted_count,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class VectorSearchResponse:
    """Response from a vector search operation."""
    results: List[VectorSearchResult]
    query_vector: Optional[List[float]] = None
    duration_ms: int = 0
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "results": [r.to_dict() for r in self.results],
            "query_vector": self.query_vector,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class VectorDBConfig:
    """Configuration for a vector database provider instance."""
    provider_type: str
    api_key_env: Optional[str] = None
    index_name: Optional[str] = None
    namespace: Optional[str] = None
    host: Optional[str] = None
    environment: Optional[str] = None
    dimensions: Optional[int] = None
    metric: str = "cosine"  # cosine, euclidean, dotproduct
    timeout: int = 30
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_type": self.provider_type,
            "api_key_env": self.api_key_env,
            "index_name": self.index_name,
            "namespace": self.namespace,
            "host": self.host,
            "environment": self.environment,
            "dimensions": self.dimensions,
            "metric": self.metric,
            "timeout": self.timeout,
            "extra_config": self.extra_config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorDBConfig":
        return cls(**data)


@dataclass
class VectorRecord:
    """A record to upsert into the vector database."""
    id: str
    embedding: List[float]
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "embedding": self.embedding,
            "content": self.content,
            "metadata": self.metadata,
        }


class VectorDBProvider(ABC):
    """
    Abstract base class for vector database providers.

    All vector DB providers must implement:
    - name: Provider identifier
    - upsert(): Insert or update vectors
    - search(): Search for similar vectors
    - delete(): Delete vectors
    - list_indexes(): List available indexes

    Example implementation:

        class MyVectorDB(VectorDBProvider):
            @property
            def name(self) -> str:
                return "my_vectordb"

            async def upsert(self, records, namespace=None) -> VectorUpsertResult:
                # Your upsert logic here
                pass

            async def search(self, query_vector, top_k=10, filter=None, namespace=None) -> VectorSearchResponse:
                # Your search logic here
                pass

            async def delete(self, ids=None, filter=None, namespace=None) -> VectorDeleteResult:
                # Your delete logic here
                pass
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        namespace: Optional[str] = None,
        host: Optional[str] = None,
        environment: Optional[str] = None,
        dimensions: Optional[int] = None,
        metric: str = "cosine",
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize the vector database provider.

        Args:
            api_key: API key for the provider
            index_name: Default index/collection name
            namespace: Default namespace for operations
            host: Host URL (for self-hosted solutions)
            environment: Environment/region (e.g., 'us-west1-gcp')
            dimensions: Vector dimensions
            metric: Distance metric (cosine, euclidean, dotproduct)
            timeout: Request timeout in seconds
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self.index_name = index_name
        self.namespace = namespace
        self.host = host
        self.environment = environment
        self.dimensions = dimensions
        self.metric = metric
        self.timeout = timeout
        self.extra_config = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier (e.g., 'pinecone', 'chromadb')."""
        pass

    @abstractmethod
    async def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None,
        **kwargs
    ) -> VectorUpsertResult:
        """
        Insert or update vectors in the database.

        Args:
            records: List of VectorRecord objects to upsert
            namespace: Override default namespace
            **kwargs: Provider-specific options

        Returns:
            VectorUpsertResult with count and status
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        include_metadata: bool = True,
        include_vectors: bool = False,
        **kwargs
    ) -> VectorSearchResponse:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter: Metadata filter (provider-specific syntax)
            namespace: Override default namespace
            include_metadata: Include metadata in results
            include_vectors: Include vectors in results
            **kwargs: Provider-specific options

        Returns:
            VectorSearchResponse with results
        """
        pass

    @abstractmethod
    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        delete_all: bool = False,
        **kwargs
    ) -> VectorDeleteResult:
        """
        Delete vectors from the database.

        Args:
            ids: List of vector IDs to delete
            filter: Metadata filter for deletion
            namespace: Override default namespace
            delete_all: Delete all vectors in namespace
            **kwargs: Provider-specific options

        Returns:
            VectorDeleteResult with count and status
        """
        pass

    async def search_with_embedding(
        self,
        embedding_provider,
        query_text: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        **kwargs
    ) -> VectorSearchResponse:
        """
        Convenience method to search using text query.

        Embeds the query text and then searches.

        Args:
            embedding_provider: An EmbeddingProvider instance
            query_text: Text to embed and search
            top_k: Number of results
            filter: Metadata filter
            namespace: Override default namespace

        Returns:
            VectorSearchResponse with results
        """
        # Get embedding for query
        query_vector = await embedding_provider.embed_single_async(query_text)

        # Search with embedded vector
        response = await self.search(
            query_vector=query_vector,
            top_k=top_k,
            filter=filter,
            namespace=namespace,
            **kwargs
        )

        # Include the query vector in response
        response.query_vector = query_vector
        return response

    async def upsert_texts(
        self,
        embedding_provider,
        texts: List[str],
        ids: Optional[List[str]] = None,
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        namespace: Optional[str] = None,
        **kwargs
    ) -> VectorUpsertResult:
        """
        Convenience method to upsert texts with automatic embedding.

        Args:
            embedding_provider: An EmbeddingProvider instance
            texts: List of texts to embed and upsert
            ids: List of IDs (auto-generated if not provided)
            metadata_list: List of metadata dicts per text
            namespace: Override default namespace

        Returns:
            VectorUpsertResult with count and status
        """
        import uuid

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]

        # Generate metadata if not provided
        if metadata_list is None:
            metadata_list = [{} for _ in texts]

        # Get embeddings
        response = await embedding_provider.embed_async(texts)
        if not response.success:
            return VectorUpsertResult(
                upserted_count=0,
                success=False,
                error=response.error
            )

        # Build records
        records = [
            VectorRecord(
                id=id_,
                embedding=emb,
                content=text,
                metadata=meta
            )
            for id_, emb, text, meta in zip(ids, response.embeddings, texts, metadata_list)
        ]

        # Upsert
        return await self.upsert(records, namespace=namespace, **kwargs)

    @abstractmethod
    async def list_indexes(self) -> List[str]:
        """List available indexes/collections."""
        pass

    async def create_index(
        self,
        name: str,
        dimensions: int,
        metric: str = "cosine",
        **kwargs
    ) -> bool:
        """
        Create a new index/collection.

        Default implementation raises NotImplementedError.
        Override in subclasses that support index creation.
        """
        raise NotImplementedError(f"{self.name} does not support create_index")

    async def delete_index(self, name: str) -> bool:
        """
        Delete an index/collection.

        Default implementation raises NotImplementedError.
        Override in subclasses that support index deletion.
        """
        raise NotImplementedError(f"{self.name} does not support delete_index")

    async def describe_index(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about an index.

        Default implementation raises NotImplementedError.
        Override in subclasses that support index description.
        """
        raise NotImplementedError(f"{self.name} does not support describe_index")

    def _time_call(self, func, *args, **kwargs) -> tuple:
        """Time a function call."""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms

    async def _time_call_async(self, coro) -> tuple:
        """Time an async coroutine."""
        start = time.perf_counter()
        result = await coro
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms

    def get_config(self) -> VectorDBConfig:
        """Get the configuration for this provider instance."""
        return VectorDBConfig(
            provider_type=self.name,
            api_key_env=f"{self.name.upper()}_API_KEY",
            index_name=self.index_name,
            namespace=self.namespace,
            host=self.host,
            environment=self.environment,
            dimensions=self.dimensions,
            metric=self.metric,
            timeout=self.timeout,
            extra_config=self.extra_config,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(index={self.index_name})"


# Vector DB Provider Registry
_VECTORDB_REGISTRY: Dict[str, type] = {}


def register_vectordb_provider(provider_class: type) -> type:
    """
    Register a vector database provider class.

    Can be used as a decorator:

        @register_vectordb_provider
        class MyVectorDB(VectorDBProvider):
            ...
    """
    if not issubclass(provider_class, VectorDBProvider):
        raise ValueError(f"{provider_class.__name__} must extend VectorDBProvider")

    try:
        temp = object.__new__(provider_class)
        temp.api_key = "temp"
        temp.index_name = None
        temp.namespace = None
        temp.host = None
        temp.environment = None
        temp.dimensions = None
        temp.metric = "cosine"
        temp.timeout = 30
        temp.extra_config = {}
        name = temp.name
    except Exception:
        name = provider_class.__name__.lower().replace("provider", "").replace("vectordb", "")

    _VECTORDB_REGISTRY[name] = provider_class
    return provider_class


def get_vectordb_provider(name: str) -> Optional[type]:
    """Get a vector database provider class by name."""
    return _VECTORDB_REGISTRY.get(name)


def list_vectordb_providers() -> List[str]:
    """List all registered vector database provider names."""
    return list(_VECTORDB_REGISTRY.keys())


def create_vectordb_provider(config: VectorDBConfig) -> VectorDBProvider:
    """Create a vector database provider instance from configuration."""
    import os

    provider_class = get_vectordb_provider(config.provider_type)
    if not provider_class:
        raise ValueError(f"Unknown vector database provider type: {config.provider_type}")

    api_key = os.environ.get(config.api_key_env) if config.api_key_env else None

    provider: VectorDBProvider = provider_class(
        api_key=api_key,
        index_name=config.index_name,
        namespace=config.namespace,
        host=config.host,
        environment=config.environment,
        dimensions=config.dimensions,
        metric=config.metric,
        timeout=config.timeout,
        **config.extra_config
    )
    return provider
