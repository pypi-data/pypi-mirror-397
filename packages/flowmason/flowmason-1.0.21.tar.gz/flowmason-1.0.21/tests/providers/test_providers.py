"""
Tests for the provider system.

Tests cover:
- Provider registration and discovery
- ProviderResponse dataclass
- ProviderConfig serialization
- JSON parsing utilities
- Cost calculation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from flowmason_core.providers import (
    ProviderBase,
    ProviderResponse,
    ProviderConfig,
    ProviderCapability,
    register_provider,
    get_provider,
    list_providers,
    create_provider,
)


class TestProviderRegistry:
    """Tests for provider registration and discovery."""

    def test_list_providers_returns_builtin(self):
        """Built-in providers should be registered."""
        providers = list_providers()
        assert "anthropic" in providers
        assert "openai" in providers
        assert "google" in providers
        assert "groq" in providers

    def test_get_provider_returns_class(self):
        """get_provider should return the provider class."""
        provider_class = get_provider("anthropic")
        assert provider_class is not None
        assert issubclass(provider_class, ProviderBase)

    def test_get_unknown_provider_returns_none(self):
        """get_provider should return None for unknown providers."""
        provider_class = get_provider("unknown_provider")
        assert provider_class is None


class TestProviderResponse:
    """Tests for ProviderResponse dataclass."""

    def test_basic_response(self):
        """Test basic response creation."""
        response = ProviderResponse(
            content="Hello world",
            model="test-model",
        )
        assert response.content == "Hello world"
        assert response.model == "test-model"
        assert response.success is True
        assert response.error is None

    def test_text_alias(self):
        """Test .text alias for .content."""
        response = ProviderResponse(
            content="Test content",
            model="test-model",
        )
        assert response.text == response.content

    def test_token_counts_from_usage(self):
        """Test that token counts are extracted from usage dict."""
        response = ProviderResponse(
            content="Hello",
            model="test-model",
            usage={
                "input_tokens": 10,
                "output_tokens": 20,
                "cost_usd": 0.001,
            }
        )
        assert response.input_tokens == 10
        assert response.output_tokens == 20
        assert response.total_tokens == 30
        assert response.cost == 0.001

    def test_error_response(self):
        """Test error response creation."""
        response = ProviderResponse(
            content="",
            model="test-model",
            success=False,
            error="API error occurred",
        )
        assert response.success is False
        assert response.error == "API error occurred"

    def test_to_dict(self):
        """Test serialization to dict."""
        response = ProviderResponse(
            content="Hello",
            model="test-model",
            usage={"input_tokens": 5},
            duration_ms=100,
        )
        d = response.to_dict()
        assert d["content"] == "Hello"
        assert d["model"] == "test-model"
        assert d["duration_ms"] == 100
        assert d["success"] is True


class TestProviderConfig:
    """Tests for ProviderConfig dataclass."""

    def test_basic_config(self):
        """Test basic config creation."""
        config = ProviderConfig(
            provider_type="anthropic",
            api_key_env="ANTHROPIC_API_KEY",
        )
        assert config.provider_type == "anthropic"
        assert config.api_key_env == "ANTHROPIC_API_KEY"
        assert config.timeout == 120
        assert config.max_retries == 3

    def test_config_to_dict(self):
        """Test config serialization."""
        config = ProviderConfig(
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
            model="gpt-4",
            timeout=60,
        )
        d = config.to_dict()
        assert d["provider_type"] == "openai"
        assert d["model"] == "gpt-4"
        assert d["timeout"] == 60

    def test_config_from_dict(self):
        """Test config deserialization."""
        data = {
            "provider_type": "groq",
            "api_key_env": "GROQ_API_KEY",
            "model": "llama-3.3-70b-versatile",
        }
        config = ProviderConfig.from_dict(data)
        assert config.provider_type == "groq"
        assert config.model == "llama-3.3-70b-versatile"


class TestProviderCapability:
    """Tests for ProviderCapability enum."""

    def test_capability_values(self):
        """Test that all capabilities have string values."""
        assert ProviderCapability.TEXT_GENERATION.value == "text_generation"
        assert ProviderCapability.STREAMING.value == "streaming"
        assert ProviderCapability.FUNCTION_CALLING.value == "function_calling"
        assert ProviderCapability.VISION.value == "vision"
        assert ProviderCapability.EMBEDDINGS.value == "embeddings"
        assert ProviderCapability.CODE_EXECUTION.value == "code_execution"


class TestCustomProviderRegistration:
    """Tests for registering custom providers."""

    def test_register_custom_provider(self):
        """Test registering a custom provider."""
        # Create a minimal custom provider
        @register_provider
        class TestProvider(ProviderBase):
            @property
            def name(self) -> str:
                return "test_custom"

            @property
            def default_model(self) -> str:
                return "test-model"

            @property
            def available_models(self) -> list:
                return ["test-model"]

            @property
            def capabilities(self) -> list:
                return [ProviderCapability.TEXT_GENERATION]

            def call(self, prompt, **kwargs):
                return ProviderResponse(
                    content="Test response",
                    model="test-model",
                )

        # Verify it's registered
        assert "test_custom" in list_providers()
        provider_class = get_provider("test_custom")
        assert provider_class is TestProvider


class TestJSONParsing:
    """Tests for JSON parsing utilities in ProviderBase."""

    def setup_method(self):
        """Create a mock provider for testing."""
        class MockProvider(ProviderBase):
            @property
            def name(self): return "mock"
            @property
            def default_model(self): return "mock"
            @property
            def available_models(self): return ["mock"]
            @property
            def capabilities(self): return []
            def call(self, prompt, **kwargs):
                return ProviderResponse(content="", model="mock")

        self.provider = MockProvider(api_key="test")

    def test_parse_plain_json(self):
        """Test parsing plain JSON."""
        text = '{"key": "value"}'
        result = self.provider.parse_json(text)
        assert result == {"key": "value"}

    def test_parse_json_with_whitespace(self):
        """Test parsing JSON with leading/trailing whitespace."""
        text = '  \n{"key": "value"}\n  '
        result = self.provider.parse_json(text)
        assert result == {"key": "value"}

    def test_parse_json_from_markdown_block(self):
        """Test parsing JSON from markdown code block."""
        text = '''Here is the JSON:
```json
{"key": "value"}
```
'''
        result = self.provider.parse_json(text)
        assert result == {"key": "value"}

    def test_parse_json_embedded_in_text(self):
        """Test parsing JSON embedded in surrounding text."""
        text = 'The result is {"key": "value"} as shown.'
        result = self.provider.parse_json(text)
        assert result == {"key": "value"}

    def test_parse_empty_returns_empty_dict(self):
        """Test that empty string returns empty dict."""
        result = self.provider.parse_json("")
        assert result == {}


class TestCostCalculation:
    """Tests for cost calculation."""

    def setup_method(self):
        """Create a mock provider with pricing."""
        class MockProvider(ProviderBase):
            DEFAULT_PRICING = {"input": 1.0, "output": 2.0}  # per 1M tokens
            MODEL_PRICING = {
                "expensive-model": {"input": 10.0, "output": 20.0},
            }

            @property
            def name(self): return "mock"
            @property
            def default_model(self): return "mock"
            @property
            def available_models(self): return ["mock", "expensive-model"]
            @property
            def capabilities(self): return []
            def call(self, prompt, **kwargs):
                return ProviderResponse(content="", model="mock")

        self.provider = MockProvider(api_key="test")

    def test_calculate_cost_default_pricing(self):
        """Test cost calculation with default pricing."""
        # 1000 input + 500 output tokens at $1/$2 per million
        cost = self.provider.calculate_cost(1000, 500)
        expected = (1000 / 1_000_000) * 1.0 + (500 / 1_000_000) * 2.0
        assert cost == expected

    def test_calculate_cost_model_pricing(self):
        """Test cost calculation with model-specific pricing."""
        cost = self.provider.calculate_cost(1000, 500, model="expensive-model")
        expected = (1000 / 1_000_000) * 10.0 + (500 / 1_000_000) * 20.0
        assert cost == expected
