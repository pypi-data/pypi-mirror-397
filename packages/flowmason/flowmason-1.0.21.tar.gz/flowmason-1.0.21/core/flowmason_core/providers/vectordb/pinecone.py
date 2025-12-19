"""
Pinecone Vector Database Provider

Provides integration with Pinecone's managed vector database service
for RAG and semantic search applications.
"""

import os
from typing import Any, Dict, List, Optional

from .base import (
    VectorDBProvider,
    VectorDeleteResult,
    VectorRecord,
    VectorSearchResponse,
    VectorSearchResult,
    VectorUpsertResult,
    register_vectordb_provider,
)


@register_vectordb_provider
class PineconeProvider(VectorDBProvider):
    """
    Vector database provider for Pinecone.

    Pinecone is a managed vector database optimized for ML applications.
    Supports serverless and pod-based deployments.

    Features:
    - Managed infrastructure (no ops required)
    - High-performance similarity search
    - Metadata filtering
    - Namespaces for data isolation
    - Real-time index updates
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
        api_key = api_key or os.environ.get("PINECONE_API_KEY")
        if not api_key:
            raise ValueError(
                "Pinecone API key required. Set PINECONE_API_KEY env var or pass api_key."
            )

        super().__init__(
            api_key=api_key,
            index_name=index_name,
            namespace=namespace,
            host=host,
            environment=environment,
            dimensions=dimensions,
            metric=metric,
            timeout=timeout,
            **kwargs
        )
        self._client = None
        self._index = None

    @property
    def client(self):
        """Lazy-load the Pinecone client."""
        if self._client is None:
            try:
                from pinecone import Pinecone
                self._client = Pinecone(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "pinecone package required. Install with: pip install pinecone"
                )
        return self._client

    @property
    def index(self):
        """Get the current index."""
        if self._index is None and self.index_name:
            self._index = self.client.Index(self.index_name, host=self.host)
        return self._index

    @property
    def name(self) -> str:
        return "pinecone"

    def _get_index(self, index_name: Optional[str] = None):
        """Get index by name or return default."""
        name = index_name or self.index_name
        if not name:
            raise ValueError("No index name specified")
        if name == self.index_name and self._index:
            return self._index
        return self.client.Index(name, host=self.host)

    async def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None,
        batch_size: int = 100,
        **kwargs
    ) -> VectorUpsertResult:
        """
        Insert or update vectors in Pinecone.

        Args:
            records: List of VectorRecord objects to upsert
            namespace: Override default namespace
            batch_size: Batch size for upsert operations
            **kwargs: Additional Pinecone options

        Returns:
            VectorUpsertResult with count and status
        """
        ns = namespace or self.namespace or ""

        try:
            index = self._get_index()

            # Convert records to Pinecone format
            vectors = []
            for record in records:
                vector_data = {
                    "id": record.id,
                    "values": record.embedding,
                    "metadata": {
                        **record.metadata,
                        "_content": record.content,  # Store content in metadata
                    }
                }
                vectors.append(vector_data)

            # Upsert in batches
            total_upserted = 0
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                result = index.upsert(vectors=batch, namespace=ns, **kwargs)
                total_upserted += result.get("upserted_count", len(batch))

            return VectorUpsertResult(
                upserted_count=total_upserted,
                success=True,
            )

        except Exception as e:
            return VectorUpsertResult(
                upserted_count=0,
                success=False,
                error=str(e),
            )

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
        Search for similar vectors in Pinecone.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter: Pinecone metadata filter
            namespace: Override default namespace
            include_metadata: Include metadata in results
            include_vectors: Include vectors in results
            **kwargs: Additional Pinecone query options

        Returns:
            VectorSearchResponse with results

        Filter syntax example:
            {"category": {"$eq": "tech"}}
            {"price": {"$gte": 10, "$lte": 100}}
            {"$and": [{"a": {"$eq": 1}}, {"b": {"$eq": 2}}]}
        """
        ns = namespace or self.namespace or ""

        try:
            index = self._get_index()

            start_time = __import__("time").perf_counter()

            response = index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter,
                namespace=ns,
                include_metadata=include_metadata,
                include_values=include_vectors,
                **kwargs
            )

            duration_ms = int((__import__("time").perf_counter() - start_time) * 1000)

            # Convert to standard format
            results = []
            for match in response.get("matches", []):
                metadata = match.get("metadata", {})
                content = metadata.pop("_content", "")  # Extract content from metadata

                results.append(VectorSearchResult(
                    id=match["id"],
                    content=content,
                    score=match["score"],
                    metadata=metadata,
                    embedding=match.get("values"),
                ))

            return VectorSearchResponse(
                results=results,
                query_vector=query_vector if include_vectors else None,
                duration_ms=duration_ms,
                success=True,
            )

        except Exception as e:
            return VectorSearchResponse(
                results=[],
                success=False,
                error=str(e),
            )

    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        delete_all: bool = False,
        **kwargs
    ) -> VectorDeleteResult:
        """
        Delete vectors from Pinecone.

        Args:
            ids: List of vector IDs to delete
            filter: Metadata filter for deletion
            namespace: Override default namespace
            delete_all: Delete all vectors in namespace
            **kwargs: Additional Pinecone options

        Returns:
            VectorDeleteResult with count and status
        """
        ns = namespace or self.namespace or ""

        try:
            index = self._get_index()

            if delete_all:
                index.delete(delete_all=True, namespace=ns, **kwargs)
                return VectorDeleteResult(
                    deleted_count=-1,  # Pinecone doesn't return count for delete_all
                    success=True,
                )

            if ids:
                index.delete(ids=ids, namespace=ns, **kwargs)
                return VectorDeleteResult(
                    deleted_count=len(ids),
                    success=True,
                )

            if filter:
                index.delete(filter=filter, namespace=ns, **kwargs)
                return VectorDeleteResult(
                    deleted_count=-1,  # Count unknown for filter delete
                    success=True,
                )

            return VectorDeleteResult(
                deleted_count=0,
                success=False,
                error="Must specify ids, filter, or delete_all=True",
            )

        except Exception as e:
            return VectorDeleteResult(
                deleted_count=0,
                success=False,
                error=str(e),
            )

    async def list_indexes(self) -> List[str]:
        """List all Pinecone indexes."""
        try:
            indexes = self.client.list_indexes()
            return [idx.name for idx in indexes]
        except Exception as e:
            raise RuntimeError(f"Failed to list indexes: {e}")

    async def create_index(
        self,
        name: str,
        dimensions: int,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1",
        **kwargs
    ) -> bool:
        """
        Create a new Pinecone serverless index.

        Args:
            name: Index name
            dimensions: Vector dimensions
            metric: Distance metric (cosine, euclidean, dotproduct)
            cloud: Cloud provider (aws, gcp, azure)
            region: Cloud region
            **kwargs: Additional index options

        Returns:
            True if created successfully
        """
        try:
            from pinecone import ServerlessSpec

            self.client.create_index(
                name=name,
                dimension=dimensions,
                metric=metric,
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region,
                ),
                **kwargs
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create index: {e}")

    async def delete_index(self, name: str) -> bool:
        """Delete a Pinecone index."""
        try:
            self.client.delete_index(name)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete index: {e}")

    async def describe_index(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a Pinecone index."""
        try:
            index_name = name or self.index_name
            if not index_name:
                raise ValueError("No index name specified")

            description = self.client.describe_index(index_name)
            return {
                "name": description.name,
                "dimension": description.dimension,
                "metric": description.metric,
                "host": description.host,
                "status": description.status,
                "spec": str(description.spec),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to describe index: {e}")

    async def get_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            index = self._get_index()
            stats = index.describe_index_stats()

            if namespace:
                ns_stats = stats.get("namespaces", {}).get(namespace, {})
                return {
                    "namespace": namespace,
                    "vector_count": ns_stats.get("vector_count", 0),
                }

            return {
                "total_vector_count": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension"),
                "namespaces": stats.get("namespaces", {}),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get stats: {e}")
