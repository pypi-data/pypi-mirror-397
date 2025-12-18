"""
ChromaDB Vector Database Provider

Provides integration with ChromaDB, an open-source embedding database
that can run locally or in the cloud.
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
class ChromaDBProvider(VectorDBProvider):
    """
    Vector database provider for ChromaDB.

    ChromaDB is an open-source embedding database that can:
    - Run in-memory (ephemeral)
    - Run persistently (local file storage)
    - Connect to a ChromaDB server (remote)

    Features:
    - Simple API
    - Built-in embedding functions
    - Metadata filtering with WHERE clauses
    - Document storage alongside embeddings
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,  # Called 'collection' in ChromaDB
        namespace: Optional[str] = None,
        host: Optional[str] = None,
        port: int = 8000,
        persist_directory: Optional[str] = None,
        dimensions: Optional[int] = None,
        metric: str = "cosine",  # cosine, l2, ip (inner product)
        timeout: int = 30,
        in_memory: bool = False,
        **kwargs
    ):
        """
        Initialize ChromaDB provider.

        Args:
            api_key: API key for ChromaDB Cloud (if using)
            index_name: Collection name
            namespace: Not used in ChromaDB (collections serve this purpose)
            host: ChromaDB server host (for client mode)
            port: ChromaDB server port
            persist_directory: Directory for persistent storage
            dimensions: Vector dimensions (not required, auto-detected)
            metric: Distance metric (cosine, l2, ip)
            timeout: Request timeout
            in_memory: Use ephemeral in-memory storage
            **kwargs: Additional options
        """
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
        self.port = port
        self.persist_directory = persist_directory
        self.in_memory = in_memory
        self._client = None
        self._collection = None

    @property
    def client(self):
        """Lazy-load the ChromaDB client."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings

                if self.host:
                    # Connect to remote ChromaDB server
                    self._client = chromadb.HttpClient(
                        host=self.host,
                        port=self.port,
                        settings=Settings(
                            chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                            chroma_client_auth_credentials=self.api_key,
                        ) if self.api_key else None,
                    )
                elif self.persist_directory:
                    # Persistent local storage
                    self._client = chromadb.PersistentClient(
                        path=self.persist_directory
                    )
                elif self.in_memory:
                    # Ephemeral in-memory storage
                    self._client = chromadb.EphemeralClient()
                else:
                    # Default to in-memory
                    self._client = chromadb.EphemeralClient()

            except ImportError:
                raise ImportError(
                    "chromadb package required. Install with: pip install chromadb"
                )
        return self._client

    @property
    def collection(self):
        """Get the current collection."""
        if self._collection is None and self.index_name:
            # Map our metric names to ChromaDB's
            metric_map = {
                "cosine": "cosine",
                "euclidean": "l2",
                "l2": "l2",
                "dotproduct": "ip",
                "ip": "ip",
            }
            hnsw_space = metric_map.get(self.metric, "cosine")

            self._collection = self.client.get_or_create_collection(
                name=self.index_name,
                metadata={"hnsw:space": hnsw_space}
            )
        return self._collection

    @property
    def name(self) -> str:
        return "chromadb"

    def _get_collection(self, collection_name: Optional[str] = None):
        """Get collection by name or return default."""
        name = collection_name or self.index_name
        if not name:
            raise ValueError("No collection name specified")
        if name == self.index_name and self._collection:
            return self._collection
        return self.client.get_collection(name)

    async def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None,
        **kwargs
    ) -> VectorUpsertResult:
        """
        Insert or update vectors in ChromaDB.

        Note: ChromaDB doesn't have namespaces; use different collections instead.

        Args:
            records: List of VectorRecord objects to upsert
            namespace: If provided, uses as collection name
            **kwargs: Additional ChromaDB options

        Returns:
            VectorUpsertResult with count and status
        """
        try:
            collection = self._get_collection(namespace)

            ids = [r.id for r in records]
            embeddings = [r.embedding for r in records]
            documents = [r.content for r in records]
            metadatas = [r.metadata for r in records]

            # ChromaDB upsert
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
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
        **kwargs
    ) -> VectorSearchResponse:
        """
        Search for similar vectors in ChromaDB.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter: ChromaDB where clause filter
            namespace: Collection name override
            include_metadata: Include metadata in results
            include_vectors: Include vectors in results
            **kwargs: Additional ChromaDB query options

        Returns:
            VectorSearchResponse with results

        Filter syntax (ChromaDB where clause):
            {"field": "value"}  # Exact match
            {"field": {"$eq": "value"}}  # Equals
            {"field": {"$ne": "value"}}  # Not equals
            {"field": {"$gt": 5}}  # Greater than
            {"field": {"$gte": 5}}  # Greater than or equal
            {"field": {"$lt": 5}}  # Less than
            {"field": {"$lte": 5}}  # Less than or equal
            {"field": {"$in": ["a", "b"]}}  # In list
            {"field": {"$nin": ["a", "b"]}}  # Not in list
            {"$and": [...]}  # AND
            {"$or": [...]}  # OR
        """
        try:
            collection = self._get_collection(namespace)

            start_time = __import__("time").perf_counter()

            # Build include list
            include = ["documents"]
            if include_metadata:
                include.append("metadatas")
            if include_vectors:
                include.append("embeddings")
            include.append("distances")

            response = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=filter,
                include=include,
            )

            duration_ms = int((__import__("time").perf_counter() - start_time) * 1000)

            # Convert to standard format
            results = []
            if response and response.get("ids"):
                ids = response["ids"][0]  # First (only) query result
                distances = response.get("distances", [[]])[0]
                documents = response.get("documents", [[]])[0]
                metadatas = response.get("metadatas", [[]])[0]
                embeddings = response.get("embeddings", [[]])[0] if include_vectors else [None] * len(ids)

                for i, id_ in enumerate(ids):
                    # ChromaDB returns distances, we need to convert to scores
                    # For cosine: score = 1 - distance
                    # For l2: score = 1 / (1 + distance)
                    distance = distances[i] if distances else 0
                    if self.metric in ["cosine", "ip"]:
                        score = 1 - distance
                    else:  # l2/euclidean
                        score = 1 / (1 + distance)

                    results.append(VectorSearchResult(
                        id=id_,
                        content=documents[i] if documents else "",
                        score=score,
                        metadata=metadatas[i] if metadatas else {},
                        embedding=embeddings[i] if include_vectors else None,
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
        Delete vectors from ChromaDB.

        Args:
            ids: List of vector IDs to delete
            filter: Where clause filter for deletion
            namespace: Collection name override
            delete_all: Delete all vectors (deletes and recreates collection)
            **kwargs: Additional options

        Returns:
            VectorDeleteResult with count and status
        """
        try:
            collection = self._get_collection(namespace)

            if delete_all:
                # Get collection count before delete
                count = collection.count()
                # Delete by re-creating (ChromaDB doesn't have delete_all)
                coll_name = namespace or self.index_name
                self.client.delete_collection(coll_name)
                self._collection = None  # Reset cached collection
                return VectorDeleteResult(
                    deleted_count=count,
                    success=True,
                )

            if ids:
                collection.delete(ids=ids)
                return VectorDeleteResult(
                    deleted_count=len(ids),
                    success=True,
                )

            if filter:
                collection.delete(where=filter)
                return VectorDeleteResult(
                    deleted_count=-1,  # Unknown count for filter delete
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
        """List all ChromaDB collections."""
        try:
            collections = self.client.list_collections()
            return [c.name for c in collections]
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
        Create a new ChromaDB collection.

        Args:
            name: Collection name
            dimensions: Not enforced in ChromaDB (auto-detected)
            metric: Distance metric (cosine, l2, ip)
            **kwargs: Additional collection metadata

        Returns:
            True if created successfully
        """
        try:
            metric_map = {
                "cosine": "cosine",
                "euclidean": "l2",
                "l2": "l2",
                "dotproduct": "ip",
                "ip": "ip",
            }
            hnsw_space = metric_map.get(metric, "cosine")

            self.client.create_collection(
                name=name,
                metadata={"hnsw:space": hnsw_space, **kwargs}
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create collection: {e}")

    async def delete_index(self, name: str) -> bool:
        """Delete a ChromaDB collection."""
        try:
            self.client.delete_collection(name)
            if name == self.index_name:
                self._collection = None
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete collection: {e}")

    async def describe_index(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a ChromaDB collection."""
        try:
            collection = self._get_collection(name)
            return {
                "name": collection.name,
                "count": collection.count(),
                "metadata": collection.metadata,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to describe collection: {e}")
