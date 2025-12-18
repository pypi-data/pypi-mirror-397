"""
Base Local LLM Adapter for FlowMason Edge.

Abstract base class for local LLM providers.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    stop_sequences: List[str] = field(default_factory=list)
    stream: bool = False


@dataclass
class GenerationResult:
    """Result from text generation."""
    text: str
    tokens_generated: int = 0
    tokens_prompt: int = 0
    model: str = ""
    finish_reason: str = "stop"
    latency_ms: int = 0


@dataclass
class ModelInfo:
    """Information about a local model."""
    name: str
    size_bytes: int = 0
    quantization: Optional[str] = None
    context_length: int = 4096
    parameters: str = ""  # e.g., "7B", "13B"
    family: str = ""  # e.g., "llama", "mistral"
    loaded: bool = False


class LocalLLMAdapter(ABC):
    """
    Abstract base class for local LLM adapters.

    Provides a common interface for different local LLM backends
    like Ollama, llama.cpp, etc.
    """

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        timeout: int = 120,
    ):
        """
        Initialize the adapter.

        Args:
            model: Model name/path
            base_url: Base URL for API (if applicable)
            timeout: Request timeout in seconds
        """
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self._is_available = False

    @property
    def name(self) -> str:
        """Get adapter name."""
        return self.__class__.__name__

    @abstractmethod
    async def check_availability(self) -> bool:
        """
        Check if the LLM backend is available.

        Returns:
            True if available and ready
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """
        List available models.

        Returns:
            List of ModelInfo for available models
        """
        pass

    @abstractmethod
    async def load_model(self, model: Optional[str] = None) -> bool:
        """
        Load a model into memory.

        Args:
            model: Model name (uses default if None)

        Returns:
            True if loaded successfully
        """
        pass

    @abstractmethod
    async def unload_model(self, model: Optional[str] = None) -> bool:
        """
        Unload a model from memory.

        Args:
            model: Model name (uses default if None)

        Returns:
            True if unloaded successfully
        """
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate text from a prompt.

        Args:
            prompt: Input prompt
            config: Generation configuration
            system_prompt: Optional system prompt

        Returns:
            GenerationResult with generated text
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Generate text with streaming.

        Args:
            prompt: Input prompt
            config: Generation configuration
            system_prompt: Optional system prompt

        Yields:
            Generated tokens as they're produced
        """
        pass

    async def chat(
        self,
        messages: List[Dict[str, str]],
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Chat completion interface.

        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            config: Generation configuration

        Returns:
            GenerationResult with response
        """
        # Default implementation converts to prompt
        prompt_parts = []
        system_prompt = None

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_prompt = content
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt = "\n".join(prompt_parts) + "\nAssistant:"
        return await self.generate(prompt, config, system_prompt)

    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text.

        Args:
            text: Input text

        Returns:
            Embedding vector

        Raises:
            NotImplementedError if adapter doesn't support embeddings
        """
        raise NotImplementedError(f"{self.name} does not support embeddings")

    def get_model_info(self) -> Optional[ModelInfo]:
        """Get info about the current model."""
        return None

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.

        Returns:
            Health status dictionary
        """
        is_available = await self.check_availability()
        return {
            "adapter": self.name,
            "model": self.model,
            "available": is_available,
            "base_url": self.base_url,
        }
