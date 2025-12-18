"""
FlowMason Provider Plugin System

This module provides the infrastructure for creating and using AI providers
within FlowMason pipelines.

Built-in Providers:
- AnthropicProvider: Claude models (3, 3.5, 4)
- OpenAIProvider: GPT-4, GPT-4o, o1 models
- GoogleProvider: Gemini models
- GroqProvider: Fast Llama/Mixtral inference

Creating Custom Providers:
    from flowmason_core.providers import ProviderBase, register_provider

    @register_provider
    class MyProvider(ProviderBase):
        @property
        def name(self) -> str:
            return "my_provider"

        @property
        def default_model(self) -> str:
            return "my-model-v1"

        # ... implement required methods

Usage:
    from flowmason_core.providers import get_provider, list_providers

    # List available providers
    providers = list_providers()  # ['anthropic', 'openai', 'google', 'groq']

    # Get a provider class
    AnthropicProvider = get_provider('anthropic')
    provider = AnthropicProvider(api_key='...')

    # Call the provider
    response = provider.call("Hello, world!")
    print(response.content)
"""

from .base import (
    ProviderBase,
    ProviderCapability,
    ProviderConfig,
    ProviderResponse,
    create_provider,
    get_provider,
    list_providers,
    register_provider,
)

# Import built-in providers to register them
from .builtin import (
    AnthropicProvider,
    GoogleProvider,
    GroqProvider,
    OpenAIProvider,
    PerplexityProvider,
)

__all__ = [
    # Base classes
    "ProviderBase",
    "ProviderResponse",
    "ProviderConfig",
    "ProviderCapability",
    # Registry functions
    "register_provider",
    "get_provider",
    "list_providers",
    "create_provider",
    # Built-in providers
    "AnthropicProvider",
    "OpenAIProvider",
    "GoogleProvider",
    "GroqProvider",
    "PerplexityProvider",
]
