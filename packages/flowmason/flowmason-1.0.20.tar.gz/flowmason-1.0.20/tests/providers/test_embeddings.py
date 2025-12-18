"""
Tests for embedding providers.

Tests cover:
- EmbeddingProvider base class
- OpenAI embedding provider
- Registry functions
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from flowmason_core.providers.embeddings import (
    EmbeddingProvider,
    EmbeddingResponse,
    EmbeddingConfig,
    OpenAIEmbeddingProvider,
    register_embedding_provider,
    get_embedding_provider,
    list_embedding_providers,
    create_embedding_provider,
)


class TestEmbeddingResponse:
    """Tests for EmbeddingResponse dataclass."""

    def test_basic_response(self):
        """Test basic response creation."""
        response = EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3]],
            model="text-embedding-3-small",
            dimensions=3,
        )
        assert len(response.embeddings) == 1
        assert response.dimensions == 3
        assert response.model == "text-embedding-3-small"
        assert response.success is True

    def test_multiple_embeddings(self):
        """Test response with multiple embeddings."""
        response = EmbeddingResponse(
            embeddings=[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]],
            model="text-embedding-3-small",
            dimensions=2,
            total_tokens=30,
        )
        assert len(response.embeddings) == 3
        assert response.total_tokens == 30

    def test_error_response(self):
        """Test error response."""
        response = EmbeddingResponse(
            embeddings=[],
            model="",
            success=False,
            error="API rate limit exceeded",
        )
        assert response.success is False
        assert response.error == "API rate limit exceeded"

    def test_to_dict(self):
        """Test serialization to dict."""
        response = EmbeddingResponse(
            embeddings=[[0.1, 0.2]],
            model="test-model",
            dimensions=2,
            total_tokens=10,
            duration_ms=50,
        )
        d = response.to_dict()
        assert d["model"] == "test-model"
        assert d["dimensions"] == 2
        assert d["total_tokens"] == 10
        assert d["duration_ms"] == 50


class TestEmbeddingConfig:
    """Tests for EmbeddingConfig."""

    def test_basic_config(self):
        """Test basic config creation."""
        config = EmbeddingConfig(
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
        )
        assert config.provider_type == "openai"
        assert config.model is None

    def test_config_with_model(self):
        """Test config with specific model."""
        config = EmbeddingConfig(
            provider_type="openai",
            model="text-embedding-3-large",
            dimensions=1024,
        )
        assert config.model == "text-embedding-3-large"
        assert config.dimensions == 1024

    def test_config_to_dict(self):
        """Test config serialization."""
        config = EmbeddingConfig(
            provider_type="openai",
            model="text-embedding-3-small",
        )
        d = config.to_dict()
        assert d["provider_type"] == "openai"
        assert d["model"] == "text-embedding-3-small"

    def test_config_from_dict(self):
        """Test config deserialization."""
        data = {
            "provider_type": "openai",
            "model": "text-embedding-3-small",
            "dimensions": 512,
        }
        config = EmbeddingConfig.from_dict(data)
        assert config.provider_type == "openai"
        assert config.dimensions == 512


class TestEmbeddingRegistry:
    """Tests for embedding provider registry."""

    def test_list_providers(self):
        """Test listing registered providers."""
        providers = list_embedding_providers()
        assert "openai" in providers

    def test_get_provider(self):
        """Test getting a provider class."""
        provider_class = get_embedding_provider("openai")
        assert provider_class is not None
        assert issubclass(provider_class, EmbeddingProvider)

    def test_get_unknown_provider(self):
        """Test getting unknown provider returns None."""
        provider_class = get_embedding_provider("unknown_provider")
        assert provider_class is None


class TestOpenAIEmbeddingProvider:
    """Tests for OpenAI embedding provider."""

    def test_init_requires_api_key(self):
        """Test that init requires API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                OpenAIEmbeddingProvider()

    def test_init_with_api_key(self):
        """Test init with explicit API key."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.name == "openai"

    def test_init_with_env_var(self):
        """Test init with environment variable."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"}):
            provider = OpenAIEmbeddingProvider()
            assert provider.api_key == "env-key"

    def test_default_model(self):
        """Test default model is set."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        assert provider.default_model == "text-embedding-3-small"

    def test_available_models(self):
        """Test available models list."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        models = provider.available_models
        assert "text-embedding-3-small" in models
        assert "text-embedding-3-large" in models
        assert "text-embedding-ada-002" in models

    def test_dimensions_property(self):
        """Test dimensions for models."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        # Default for text-embedding-3-small
        assert provider.dimensions == 1536

    @pytest.mark.asyncio
    async def test_embed_async_mock(self):
        """Test async embedding with mocked client."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")

        # Mock the client
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3]),
        ]
        mock_response.model = "text-embedding-3-small"
        mock_response.usage = MagicMock(total_tokens=10)

        mock_client = MagicMock()
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        provider._async_client = mock_client

        result = await provider.embed_async("test text")

        assert result.success is True
        assert len(result.embeddings) == 1
        assert result.embeddings[0] == [0.1, 0.2, 0.3]

    def test_embed_sync_mock(self):
        """Test sync embedding with mocked client."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")

        # Mock the client
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3]),
        ]
        mock_response.model = "text-embedding-3-small"
        mock_response.usage = MagicMock(total_tokens=10)

        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_response
        provider._client = mock_client

        result = provider.embed("test text")

        assert result.success is True
        assert len(result.embeddings) == 1

    @pytest.mark.asyncio
    async def test_embed_batched(self):
        """Test batched embedding."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")

        # Mock the client
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2]),
            MagicMock(embedding=[0.3, 0.4]),
        ]
        mock_response.model = "text-embedding-3-small"
        mock_response.usage = MagicMock(total_tokens=20)

        mock_client = MagicMock()
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        provider._async_client = mock_client

        result = await provider.embed_batched(["text1", "text2"])

        assert result.success is True
        assert len(result.embeddings) == 2
