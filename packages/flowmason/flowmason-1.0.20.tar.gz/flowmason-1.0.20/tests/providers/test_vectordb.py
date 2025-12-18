"""
Tests for vector database providers.

Tests cover:
- VectorDBProvider base class
- VectorRecord and VectorSearchResult dataclasses
- Pinecone provider
- ChromaDB provider
- Weaviate provider
- Registry functions
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from flowmason_core.providers.vectordb import (
    VectorDBProvider,
    VectorRecord,
    VectorSearchResult,
    VectorSearchResponse,
    VectorDBConfig,
    PineconeProvider,
    ChromaDBProvider,
    WeaviateProvider,
    register_vectordb_provider,
    get_vectordb_provider,
    list_vectordb_providers,
)


class TestVectorRecord:
    """Tests for VectorRecord dataclass."""

    def test_basic_record(self):
        """Test basic record creation."""
        record = VectorRecord(
            id="doc-1",
            vector=[0.1, 0.2, 0.3],
        )
        assert record.id == "doc-1"
        assert len(record.vector) == 3
        assert record.metadata is None

    def test_record_with_metadata(self):
        """Test record with metadata."""
        record = VectorRecord(
            id="doc-1",
            vector=[0.1, 0.2],
            metadata={"source": "test", "page": 1},
        )
        assert record.metadata["source"] == "test"
        assert record.metadata["page"] == 1

    def test_to_dict(self):
        """Test serialization."""
        record = VectorRecord(
            id="doc-1",
            vector=[0.1, 0.2],
            metadata={"key": "value"},
        )
        d = record.to_dict()
        assert d["id"] == "doc-1"
        assert d["vector"] == [0.1, 0.2]
        assert d["metadata"]["key"] == "value"


class TestVectorSearchResult:
    """Tests for VectorSearchResult dataclass."""

    def test_basic_result(self):
        """Test basic search result."""
        result = VectorSearchResult(
            id="doc-1",
            score=0.95,
        )
        assert result.id == "doc-1"
        assert result.score == 0.95

    def test_result_with_metadata(self):
        """Test result with metadata."""
        result = VectorSearchResult(
            id="doc-1",
            score=0.95,
            metadata={"content": "test content"},
            vector=[0.1, 0.2],
        )
        assert result.metadata["content"] == "test content"
        assert result.vector == [0.1, 0.2]


class TestVectorSearchResponse:
    """Tests for VectorSearchResponse."""

    def test_basic_response(self):
        """Test basic response."""
        response = VectorSearchResponse(
            results=[
                VectorSearchResult(id="1", score=0.9),
                VectorSearchResult(id="2", score=0.8),
            ],
            total_results=2,
        )
        assert len(response.results) == 2
        assert response.total_results == 2
        assert response.success is True

    def test_error_response(self):
        """Test error response."""
        response = VectorSearchResponse(
            results=[],
            success=False,
            error="Index not found",
        )
        assert response.success is False
        assert response.error == "Index not found"


class TestVectorDBConfig:
    """Tests for VectorDBConfig."""

    def test_basic_config(self):
        """Test basic config."""
        config = VectorDBConfig(
            provider_type="pinecone",
            api_key_env="PINECONE_API_KEY",
        )
        assert config.provider_type == "pinecone"

    def test_config_with_options(self):
        """Test config with extra options."""
        config = VectorDBConfig(
            provider_type="pinecone",
            extra_config={"metric": "cosine"},
        )
        assert config.extra_config["metric"] == "cosine"


class TestVectorDBRegistry:
    """Tests for vectordb provider registry."""

    def test_list_providers(self):
        """Test listing providers."""
        providers = list_vectordb_providers()
        assert "pinecone" in providers
        assert "chromadb" in providers
        assert "weaviate" in providers

    def test_get_provider(self):
        """Test getting a provider class."""
        provider_class = get_vectordb_provider("pinecone")
        assert provider_class is not None
        assert issubclass(provider_class, VectorDBProvider)

    def test_get_unknown_provider(self):
        """Test getting unknown provider."""
        provider_class = get_vectordb_provider("unknown")
        assert provider_class is None


class TestPineconeProvider:
    """Tests for Pinecone provider."""

    def test_init_requires_api_key(self):
        """Test init requires API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                PineconeProvider()

    def test_init_with_api_key(self):
        """Test init with explicit API key."""
        provider = PineconeProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.name == "pinecone"

    def test_capabilities(self):
        """Test capabilities list."""
        provider = PineconeProvider(api_key="test-key")
        caps = provider.capabilities
        assert "vector_search" in caps
        assert "metadata_filtering" in caps
        assert "namespaces" in caps

    @pytest.mark.asyncio
    async def test_upsert_mock(self):
        """Test upsert with mocked client."""
        provider = PineconeProvider(api_key="test-key")

        # Mock the index
        mock_index = MagicMock()
        mock_index.upsert.return_value = {"upserted_count": 2}
        provider._get_index = MagicMock(return_value=mock_index)

        records = [
            VectorRecord(id="1", vector=[0.1, 0.2]),
            VectorRecord(id="2", vector=[0.3, 0.4]),
        ]

        count = await provider.upsert("test-index", records)
        assert count == 2

    @pytest.mark.asyncio
    async def test_search_mock(self):
        """Test search with mocked client."""
        provider = PineconeProvider(api_key="test-key")

        # Mock the index
        mock_match = MagicMock()
        mock_match.id = "doc-1"
        mock_match.score = 0.95
        mock_match.metadata = {"content": "test"}

        mock_result = MagicMock()
        mock_result.matches = [mock_match]

        mock_index = MagicMock()
        mock_index.query.return_value = mock_result
        provider._get_index = MagicMock(return_value=mock_index)

        response = await provider.search(
            index_name="test-index",
            query_vector=[0.1, 0.2],
            top_k=5,
        )

        assert response.success is True
        assert len(response.results) == 1
        assert response.results[0].id == "doc-1"
        assert response.results[0].score == 0.95


class TestChromaDBProvider:
    """Tests for ChromaDB provider."""

    def test_init_default(self):
        """Test default init (in-memory)."""
        provider = ChromaDBProvider()
        assert provider.name == "chromadb"

    def test_init_persistent(self):
        """Test init with persistent path."""
        provider = ChromaDBProvider(persist_directory="/tmp/chroma")
        assert provider.persist_directory == "/tmp/chroma"

    def test_capabilities(self):
        """Test capabilities."""
        provider = ChromaDBProvider()
        caps = provider.capabilities
        assert "vector_search" in caps
        assert "metadata_filtering" in caps

    @pytest.mark.asyncio
    async def test_upsert_mock(self):
        """Test upsert with mocked client."""
        provider = ChromaDBProvider()

        # Mock the collection
        mock_collection = MagicMock()
        mock_collection.upsert.return_value = None

        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        provider._client = mock_client

        records = [
            VectorRecord(id="1", vector=[0.1, 0.2], metadata={"text": "test"}),
        ]

        count = await provider.upsert("test-collection", records)
        assert count == 1

    @pytest.mark.asyncio
    async def test_search_mock(self):
        """Test search with mocked client."""
        provider = ChromaDBProvider()

        # Mock the collection
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc-1", "doc-2"]],
            "distances": [[0.1, 0.2]],
            "metadatas": [[{"text": "a"}, {"text": "b"}]],
        }

        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        provider._client = mock_client

        response = await provider.search(
            index_name="test-collection",
            query_vector=[0.1, 0.2],
            top_k=5,
        )

        assert response.success is True
        assert len(response.results) == 2


class TestWeaviateProvider:
    """Tests for Weaviate provider."""

    def test_init_requires_url(self):
        """Test init requires URL."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="URL required"):
                WeaviateProvider()

    def test_init_with_url(self):
        """Test init with URL."""
        provider = WeaviateProvider(url="http://localhost:8080")
        assert provider.url == "http://localhost:8080"
        assert provider.name == "weaviate"

    def test_capabilities(self):
        """Test capabilities."""
        provider = WeaviateProvider(url="http://localhost:8080")
        caps = provider.capabilities
        assert "vector_search" in caps
        assert "metadata_filtering" in caps
        assert "hybrid_search" in caps
