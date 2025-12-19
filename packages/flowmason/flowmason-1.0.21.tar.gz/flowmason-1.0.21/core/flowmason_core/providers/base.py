"""
Provider Plugin System for FlowMason

This module provides the base infrastructure for creating custom AI providers
that can be used within FlowMason pipelines. Providers handle communication
with LLM APIs and can be easily plugged into any pipeline.

The system is designed to be:
- Extensible: Easy to add new providers
- Consistent: Common interface for all providers
- Portable: Providers can be packaged and shared
"""

import asyncio
import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Dict, Generator, List, Optional


class ProviderCapability(str, Enum):
    """Capabilities that a provider can support."""
    TEXT_GENERATION = "text_generation"
    STREAMING = "streaming"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    EMBEDDINGS = "embeddings"
    CODE_EXECUTION = "code_execution"
    # RAG capabilities
    VECTOR_SEARCH = "vector_search"
    DOCUMENT_INGEST = "document_ingest"
    # Audio capabilities
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    VOICE_CLONING = "voice_cloning"
    # Document processing capabilities
    OCR = "ocr"
    LAYOUT_ANALYSIS = "layout_analysis"
    ENTITY_EXTRACTION = "entity_extraction"
    DOCUMENT_CLASSIFICATION = "document_classification"
    INTELLIGENT_EXTRACTION = "intelligent_extraction"


@dataclass
class ProviderResponse:
    """
    Standardized response from any provider call.

    NOTE: Includes compatibility fields (`text`, `input_tokens`, `output_tokens`, `cost`)
    so existing nodes written against Iterate/Forge style responses keep working.
    """
    content: str
    model: str
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0

    def __post_init__(self) -> None:
        # Populate token/cost fields from usage if not explicitly set.
        self.input_tokens = self.input_tokens or self.usage.get("input_tokens", 0)
        self.output_tokens = self.output_tokens or self.usage.get("output_tokens", 0)
        self.cost = self.cost or self.usage.get("cost_usd", 0.0)

    @property
    def text(self) -> str:
        """Alias for legacy code that expects `.text` instead of `.content`."""
        return self.content

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "metadata": self.metadata,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
        }


@dataclass
class ProviderConfig:
    """
    Configuration for a provider instance.

    Used when serializing/deserializing provider configurations
    for storage or transmission.
    """
    provider_type: str
    api_key_env: str  # Environment variable name (never store actual keys)
    model: Optional[str] = None
    timeout: int = 120
    max_retries: int = 3
    custom_pricing: Optional[Dict[str, float]] = None
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider_type": self.provider_type,
            "api_key_env": self.api_key_env,
            "model": self.model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "custom_pricing": self.custom_pricing,
            "extra_config": self.extra_config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderConfig":
        """Create from dictionary."""
        return cls(**data)


class ProviderBase(ABC):
    """
    Abstract base class for AI providers in FlowMason.

    All providers must implement:
    - name: Provider identifier
    - default_model: Default model to use
    - call(): Synchronous API call
    - available_models: List of supported models
    - capabilities: List of supported capabilities

    The base class provides:
    - JSON parsing utilities
    - Cost calculation
    - Timing utilities
    - Async wrapper (can be overridden for native async)

    Example implementation:

        class MyCustomProvider(ProviderBase):
            DEFAULT_PRICING = {"input": 1.0, "output": 2.0}

            @property
            def name(self) -> str:
                return "my_custom"

            @property
            def default_model(self) -> str:
                return "my-model-v1"

            @property
            def available_models(self) -> List[str]:
                return ["my-model-v1", "my-model-v2"]

            @property
            def capabilities(self) -> List[ProviderCapability]:
                return [ProviderCapability.TEXT_GENERATION]

            def call(self, prompt, system=None, model=None,
                     temperature=0.7, max_tokens=4096, **kwargs) -> ProviderResponse:
                # Your API call logic here
                pass
    """

    # Default pricing per 1M tokens (override in subclasses)
    DEFAULT_PRICING = {"input": 0.0, "output": 0.0}

    # Model-specific pricing (override in subclasses)
    MODEL_PRICING: Dict[str, Dict[str, float]] = {}

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        pricing: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """
        Initialize the provider.

        Args:
            api_key: API key (or use environment variable)
            model: Default model to use
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            pricing: Custom pricing per 1M tokens {"input": X, "output": Y}
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.pricing = pricing or self.DEFAULT_PRICING
        self.extra_config = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier (e.g., 'anthropic', 'openai')."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model for this provider."""
        pass

    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """List of available models for this provider."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[ProviderCapability]:
        """List of capabilities this provider supports."""
        pass

    @abstractmethod
    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        """
        Execute a prompt and return the response.

        Args:
            prompt: User prompt to execute
            system: Optional system prompt
            model: Override default model
            temperature: Generation temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific options

        Returns:
            ProviderResponse with content and metadata
        """
        pass

    def supports(self, capability: ProviderCapability) -> bool:
        """Check if provider supports a capability."""
        return capability in self.capabilities

    def get_model_pricing(self, model: Optional[str] = None) -> Dict[str, float]:
        """Get pricing for a specific model."""
        model = model or self.model or self.default_model
        return self.MODEL_PRICING.get(model, self.DEFAULT_PRICING)

    def parse_json(self, text: str) -> Any:
        """
        Parse JSON from response text.

        Handles various formats:
        - Plain JSON
        - Markdown code blocks
        - JSON with surrounding text

        Args:
            text: Response text containing JSON

        Returns:
            Parsed JSON (dict, list, or primitive)

        Raises:
            ValueError: If JSON cannot be parsed
        """
        if not text:
            return {}

        text = text.strip()

        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        patterns = [
            r'```(?:json)?\s*\n?([\s\S]*?)\n?```',
            r'```\s*([\s\S]*?)\s*```',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue

        # Try finding JSON object in text (try multiple possible matches)
        # Use finditer to find all potential JSON objects and try each
        for json_match in re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text):
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                continue

        # Fallback: try non-greedy match for nested objects
        object_match = re.search(r'(\{[\s\S]*?\})', text)
        if object_match:
            # Try progressively larger matches until valid JSON
            start_pos = object_match.start()
            for end_pos in range(object_match.end(), len(text) + 1):
                candidate = text[start_pos:end_pos]
                if candidate.count('{') == candidate.count('}'):
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        continue

        # Try finding JSON array in text
        for array_match in re.finditer(r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]', text):
            try:
                return json.loads(array_match.group(0))
            except json.JSONDecodeError:
                continue

        # Fallback: try non-greedy match for nested arrays
        list_match = re.search(r'(\[[\s\S]*?\])', text)
        if list_match:
            start_pos = list_match.start()
            for end_pos in range(list_match.end(), len(text) + 1):
                candidate = text[start_pos:end_pos]
                if candidate.count('[') == candidate.count(']'):
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        continue

        raise ValueError(f"Could not parse JSON from response: {text[:200]}...")

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """
        Calculate cost for a request.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model used (for model-specific pricing)

        Returns:
            Estimated cost in USD
        """
        pricing = self.get_model_pricing(model)
        input_cost = (input_tokens / 1_000_000) * pricing.get("input", 0)
        output_cost = (output_tokens / 1_000_000) * pricing.get("output", 0)
        return input_cost + output_cost

    def _time_call(self, func, *args, **kwargs) -> tuple:
        """
        Time a function call.

        Args:
            func: Function to call
            *args, **kwargs: Arguments to pass

        Returns:
            Tuple of (result, duration_ms)
        """
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms

    def _build_usage_dict(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        model: Optional[str] = None,
        **extra
    ) -> Dict[str, Any]:
        """
        Build a standardized usage dictionary.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model used
            **extra: Additional usage data

        Returns:
            Usage dictionary
        """
        total_tokens = input_tokens + output_tokens
        cost = self.calculate_cost(input_tokens, output_tokens, model)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost,
            "model": model or self.model or self.default_model,
            "provider": self.name,
            **extra
        }

    async def call_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        """
        Async version of call().

        Default implementation wraps the sync call in a thread executor.
        Override in subclasses for native async support.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.call(
                prompt=prompt,
                system=system,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        )

    async def _time_call_async(self, coro) -> tuple:
        """Time an async coroutine."""
        start = time.perf_counter()
        result = await coro
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms

    def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream response chunks.

        Default implementation yields the full response at once.
        Override for true streaming support.
        """
        response = self.call(prompt, system, model, temperature, max_tokens, **kwargs)
        yield response.content

    async def stream_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream response chunks asynchronously.

        Default implementation yields the full response at once.
        Override for true streaming support.

        Yields:
            Token chunks as they arrive from the API
        """
        response = await self.call_async(prompt, system, model, temperature, max_tokens, **kwargs)
        yield response.content

    def get_config(self) -> ProviderConfig:
        """Get the configuration for this provider instance."""
        return ProviderConfig(
            provider_type=self.name,
            api_key_env=f"{self.name.upper()}_API_KEY",
            model=self.model,
            timeout=self.timeout,
            max_retries=self.max_retries,
            custom_pricing=self.pricing if self.pricing != self.DEFAULT_PRICING else None,
            extra_config=self.extra_config,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model or self.default_model})"


# Provider Registry
_PROVIDER_REGISTRY: Dict[str, type] = {}


def register_provider(provider_class: type) -> type:
    """
    Register a provider class in the global registry.

    Can be used as a decorator:

        @register_provider
        class MyProvider(ProviderBase):
            ...
    """
    if not issubclass(provider_class, ProviderBase):
        raise ValueError(f"{provider_class.__name__} must extend ProviderBase")

    # Create temporary instance to get name
    # This requires the class to have reasonable defaults
    try:
        temp = object.__new__(provider_class)
        temp.api_key = "temp"
        temp.model = None
        temp.timeout = 120
        temp.max_retries = 3
        temp.pricing = provider_class.DEFAULT_PRICING
        temp.extra_config = {}
        name = temp.name
    except Exception:
        # Fallback to class name
        name = provider_class.__name__.lower().replace("provider", "")

    _PROVIDER_REGISTRY[name] = provider_class
    return provider_class


def get_provider(name: str) -> Optional[type]:
    """Get a provider class by name."""
    return _PROVIDER_REGISTRY.get(name)


def list_providers() -> List[str]:
    """List all registered provider names."""
    return list(_PROVIDER_REGISTRY.keys())


def create_provider(config: ProviderConfig) -> ProviderBase:
    """
    Create a provider instance from configuration.

    Args:
        config: Provider configuration

    Returns:
        Configured provider instance

    Raises:
        ValueError: If provider type is unknown
    """
    import os

    provider_class = get_provider(config.provider_type)
    if not provider_class:
        raise ValueError(f"Unknown provider type: {config.provider_type}")

    # Get API key from environment
    api_key = os.environ.get(config.api_key_env)

    provider: ProviderBase = provider_class(
        api_key=api_key,
        model=config.model,
        timeout=config.timeout,
        max_retries=config.max_retries,
        pricing=config.custom_pricing,
        **config.extra_config
    )
    return provider
