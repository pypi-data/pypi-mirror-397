"""
Weaviate Vector Database Provider

Provides integration with Weaviate, an open-source vector search engine
with a GraphQL API and powerful filtering capabilities.
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
class WeaviateProvider(VectorDBProvider):
    """
    Vector database provider for Weaviate.

    Weaviate is an open-source vector search engine that supports:
    - Self-hosted or Weaviate Cloud Services (WCS)
    - GraphQL API
    - Hybrid search (vector + keyword)
    - Multi-tenancy
    - Built-in vectorization modules

    Features:
    - Powerful GraphQL filtering
    - Schema-based collections (Classes)
    - Real-time updates
    - Horizontal scaling
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,  # Called 'class' in Weaviate
        namespace: Optional[str] = None,  # Tenant ID for multi-tenancy
        host: Optional[str] = None,
        cluster_url: Optional[str] = None,  # WCS cluster URL
        dimensions: Optional[int] = None,
        metric: str = "cosine",  # cosine, l2, dot
        timeout: int = 30,
        grpc_port: int = 50051,
        http_port: int = 8080,
        **kwargs
    ):
        """
        Initialize Weaviate provider.

        Args:
            api_key: Weaviate API key (for WCS or authentication)
            index_name: Class name (collection)
            namespace: Tenant ID for multi-tenancy
            host: Weaviate host URL (for self-hosted)
            cluster_url: WCS cluster URL
            dimensions: Vector dimensions
            metric: Distance metric (cosine, l2, dot)
            timeout: Request timeout
            grpc_port: gRPC port
            http_port: HTTP port
            **kwargs: Additional options
        """
        api_key = api_key or os.environ.get("WEAVIATE_API_KEY")

        # Get cluster URL from env if not provided
        cluster_url = cluster_url or os.environ.get("WEAVIATE_CLUSTER_URL")

        super().__init__(
            api_key=api_key,
            index_name=index_name,
            namespace=namespace,
            host=host,
            dimensions=dimensions,
            metric=metric,
            timeout=timeout,
            **kwargs
        )
        self.cluster_url = cluster_url
        self.grpc_port = grpc_port
        self.http_port = http_port
        self._client = None

    @property
    def client(self):
        """Lazy-load the Weaviate client."""
        if self._client is None:
            try:
                import weaviate
                from weaviate.auth import AuthApiKey

                if self.cluster_url:
                    # Connect to Weaviate Cloud Services
                    self._client = weaviate.connect_to_wcs(
                        cluster_url=self.cluster_url,
                        auth_credentials=AuthApiKey(self.api_key) if self.api_key else None,
                    )
                elif self.host:
                    # Connect to self-hosted Weaviate
                    self._client = weaviate.connect_to_custom(
                        http_host=self.host,
                        http_port=self.http_port,
                        grpc_host=self.host,
                        grpc_port=self.grpc_port,
                        http_secure=self.host.startswith("https"),
                        grpc_secure=self.host.startswith("https"),
                        auth_credentials=AuthApiKey(self.api_key) if self.api_key else None,
                    )
                else:
                    # Connect to local Weaviate
                    self._client = weaviate.connect_to_local()

            except ImportError:
                raise ImportError(
                    "weaviate-client package required. Install with: pip install weaviate-client"
                )
        return self._client

    @property
    def name(self) -> str:
        return "weaviate"

    def _get_collection(self, collection_name: Optional[str] = None):
        """Get collection by name or return default."""
        name = collection_name or self.index_name
        if not name:
            raise ValueError("No collection/class name specified")
        return self.client.collections.get(name)

    def _map_metric(self, metric: str) -> str:
        """Map metric names to Weaviate format."""
        metric_map = {
            "cosine": "cosine",
            "euclidean": "l2-squared",
            "l2": "l2-squared",
            "dotproduct": "dot",
            "dot": "dot",
        }
        return metric_map.get(metric, "cosine")

    async def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None,
        **kwargs
    ) -> VectorUpsertResult:
        """
        Insert or update vectors in Weaviate.

        Args:
            records: List of VectorRecord objects to upsert
            namespace: Tenant ID for multi-tenancy
            **kwargs: Additional Weaviate options

        Returns:
            VectorUpsertResult with count and status
        """
        try:
            collection = self._get_collection()

            # Weaviate v4 uses batch context manager
            with collection.batch.dynamic() as batch:
                for record in records:
                    properties = {
                        **record.metadata,
                        "_content": record.content,
                    }

                    batch.add_object(
                        uuid=record.id,
                        properties=properties,
                        vector=record.embedding,
                        tenant=namespace or self.namespace,
                    )

            return VectorUpsertResult(
                upserted_count=len(records),
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
        alpha: float = 1.0,  # Hybrid search: 1.0 = pure vector, 0.0 = pure keyword
        **kwargs
    ) -> VectorSearchResponse:
        """
        Search for similar vectors in Weaviate.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter: Weaviate filter (see Weaviate docs for syntax)
            namespace: Tenant ID for multi-tenancy
            include_metadata: Include properties in results
            include_vectors: Include vectors in results
            alpha: Hybrid search weight (1.0 = pure vector)
            **kwargs: Additional Weaviate query options

        Returns:
            VectorSearchResponse with results

        Filter syntax example:
            {"path": ["field"], "operator": "Equal", "valueText": "value"}
            {"operator": "And", "operands": [...]}
        """
        try:
            collection = self._get_collection()

            start_time = __import__("time").perf_counter()

            # Build query
            query = collection.query.near_vector(
                near_vector=query_vector,
                limit=top_k,
                tenant=namespace or self.namespace,
                return_metadata=["distance", "certainty"] if include_metadata else None,
                include_vector=include_vectors,
            )

            # Add filter if provided
            if filter:
                from weaviate.classes.query import Filter
                query = query.with_where(filter)

            response = query.do()

            duration_ms = int((__import__("time").perf_counter() - start_time) * 1000)

            # Convert to standard format
            results = []
            for obj in response.objects:
                properties = dict(obj.properties) if obj.properties else {}
                content = properties.pop("_content", "")

                # Calculate score from distance/certainty
                score = obj.metadata.certainty if hasattr(obj.metadata, 'certainty') else 0.0
                if score == 0.0 and hasattr(obj.metadata, 'distance'):
                    # Convert distance to score (assuming cosine)
                    score = 1.0 - obj.metadata.distance

                results.append(VectorSearchResult(
                    id=str(obj.uuid),
                    content=content,
                    score=score,
                    metadata=properties,
                    embedding=obj.vector if include_vectors else None,
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
        Delete vectors from Weaviate.

        Args:
            ids: List of object UUIDs to delete
            filter: Where filter for batch deletion
            namespace: Tenant ID for multi-tenancy
            delete_all: Delete all objects in collection
            **kwargs: Additional options

        Returns:
            VectorDeleteResult with count and status
        """
        try:
            collection = self._get_collection()

            if delete_all:
                # Delete collection and recreate
                coll_name = self.index_name
                count = collection.aggregate.over_all(total_count=True).total_count
                self.client.collections.delete(coll_name)
                return VectorDeleteResult(
                    deleted_count=count,
                    success=True,
                )

            if ids:
                deleted = 0
                for obj_id in ids:
                    try:
                        collection.data.delete_by_id(
                            uuid=obj_id,
                            tenant=namespace or self.namespace,
                        )
                        deleted += 1
                    except Exception:
                        pass  # Object might not exist
                return VectorDeleteResult(
                    deleted_count=deleted,
                    success=True,
                )

            if filter:
                result = collection.data.delete_many(
                    where=filter,
                    tenant=namespace or self.namespace,
                )
                return VectorDeleteResult(
                    deleted_count=result.matches,
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
        """List all Weaviate collections/classes."""
        try:
            collections = self.client.collections.list_all()
            return list(collections.keys())
        except Exception as e:
            raise RuntimeError(f"Failed to list collections: {e}")

    async def create_index(
        self,
        name: str,
        dimensions: int,
        metric: str = "cosine",
        **kwargs
    ) -> bool:
        """
        Create a new Weaviate collection/class.

        Args:
            name: Collection name
            dimensions: Vector dimensions
            metric: Distance metric (cosine, l2, dot)
            **kwargs: Additional collection properties

        Returns:
            True if created successfully
        """
        try:
            from weaviate.classes.config import Configure, Property, DataType

            # Map metric
            distance_metric = self._map_metric(metric)

            # Build properties from kwargs
            properties = kwargs.pop("properties", [])
            if not properties:
                # Default property for content
                properties = [
                    Property(name="_content", data_type=DataType.TEXT)
                ]

            self.client.collections.create(
                name=name,
                vectorizer_config=Configure.Vectorizer.none(),  # We provide vectors
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=distance_metric,
                ),
                properties=properties,
                **kwargs
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create collection: {e}")

    async def delete_index(self, name: str) -> bool:
        """Delete a Weaviate collection/class."""
        try:
            self.client.collections.delete(name)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete collection: {e}")

    async def describe_index(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a Weaviate collection."""
        try:
            coll_name = name or self.index_name
            if not coll_name:
                raise ValueError("No collection name specified")

            collection = self.client.collections.get(coll_name)
            config = collection.config.get()

            # Get count
            agg = collection.aggregate.over_all(total_count=True)

            return {
                "name": coll_name,
                "count": agg.total_count,
                "vectorizer": str(config.vectorizer),
                "properties": [p.name for p in config.properties],
            }
        except Exception as e:
            raise RuntimeError(f"Failed to describe collection: {e}")

    def close(self):
        """Close the Weaviate client connection."""
        if hasattr(self, '_client') and self._client:
            self._client.close()
            self._client = None

    def __del__(self):
        """Ensure client is closed on deletion."""
        self.close()
