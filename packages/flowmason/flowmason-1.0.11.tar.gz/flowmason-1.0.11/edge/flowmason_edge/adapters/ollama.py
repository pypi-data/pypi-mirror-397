"""
Ollama Adapter for FlowMason Edge.

Provides integration with Ollama for running local LLMs.
"""

import asyncio
import json
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from flowmason_edge.adapters.base import (
    GenerationConfig,
    GenerationResult,
    LocalLLMAdapter,
    ModelInfo,
)

logger = logging.getLogger(__name__)


class OllamaAdapter(LocalLLMAdapter):
    """
    Adapter for Ollama local LLM server.

    Ollama provides easy-to-use local LLM inference with support
    for many popular models like Llama, Mistral, etc.

    Example:
        adapter = OllamaAdapter(model="llama2")

        # Check if Ollama is running
        if await adapter.check_availability():
            result = await adapter.generate("What is the capital of France?")
            print(result.text)
    """

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(
        self,
        model: str = "llama2",
        base_url: Optional[str] = None,
        timeout: int = 120,
    ):
        """
        Initialize Ollama adapter.

        Args:
            model: Model name (e.g., "llama2", "mistral", "codellama")
            base_url: Ollama server URL (default: http://localhost:11434)
            timeout: Request timeout in seconds
        """
        super().__init__(
            model=model,
            base_url=base_url or self.DEFAULT_BASE_URL,
            timeout=timeout,
        )
        self._http_client = None

    async def _get_client(self):
        """Get or create HTTP client."""
        if self._http_client is None:
            try:
                import httpx
                self._http_client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout,
                )
            except ImportError:
                raise ImportError("httpx required for Ollama. Run: pip install httpx")
        return self._http_client

    async def check_availability(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            self._is_available = response.status_code == 200
            return self._is_available
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            self._is_available = False
            return False

    async def list_models(self) -> List[ModelInfo]:
        """List models available in Ollama."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")

            if response.status_code != 200:
                return []

            data = response.json()
            models = []

            for model_data in data.get("models", []):
                name = model_data.get("name", "")
                details = model_data.get("details", {})

                models.append(ModelInfo(
                    name=name,
                    size_bytes=model_data.get("size", 0),
                    quantization=details.get("quantization_level"),
                    parameters=details.get("parameter_size", ""),
                    family=details.get("family", ""),
                    loaded=False,  # Ollama loads on demand
                ))

            return models

        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []

    async def load_model(self, model: Optional[str] = None) -> bool:
        """
        Load a model in Ollama.

        Ollama loads models on demand, so this just verifies
        the model is available or pulls it.
        """
        model = model or self.model

        try:
            client = await self._get_client()

            # Check if model exists
            response = await client.post(
                "/api/show",
                json={"name": model},
            )

            if response.status_code == 200:
                logger.info(f"Model {model} is available")
                return True

            # Try to pull the model
            logger.info(f"Pulling model {model}...")
            response = await client.post(
                "/api/pull",
                json={"name": model},
                timeout=600,  # Pulling can take a while
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Error loading model {model}: {e}")
            return False

    async def unload_model(self, model: Optional[str] = None) -> bool:
        """
        Unload a model from Ollama.

        Note: Ollama manages model loading/unloading automatically.
        """
        # Ollama handles this automatically
        return True

    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None,
    ) -> GenerationResult:
        """Generate text using Ollama."""
        config = config or GenerationConfig()
        start_time = time.time()

        try:
            client = await self._get_client()

            # Build request
            request_data: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": config.max_tokens,
                    "temperature": config.temperature,
                    "top_p": config.top_p,
                    "top_k": config.top_k,
                },
            }

            if system_prompt:
                request_data["system"] = system_prompt

            if config.stop_sequences:
                request_data["options"]["stop"] = config.stop_sequences

            response = await client.post(
                "/api/generate",
                json=request_data,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama error: {response.text}")

            data = response.json()
            latency_ms = int((time.time() - start_time) * 1000)

            return GenerationResult(
                text=data.get("response", ""),
                tokens_generated=data.get("eval_count", 0),
                tokens_prompt=data.get("prompt_eval_count", 0),
                model=self.model,
                finish_reason="stop" if data.get("done") else "length",
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Generate text with streaming."""
        config = config or GenerationConfig()

        try:
            client = await self._get_client()

            request_data: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "num_predict": config.max_tokens,
                    "temperature": config.temperature,
                    "top_p": config.top_p,
                    "top_k": config.top_k,
                },
            }

            if system_prompt:
                request_data["system"] = system_prompt

            if config.stop_sequences:
                request_data["options"]["stop"] = config.stop_sequences

            async with client.stream(
                "POST",
                "/api/generate",
                json=request_data,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """Chat completion using Ollama's chat endpoint."""
        config = config or GenerationConfig()
        start_time = time.time()

        try:
            client = await self._get_client()

            request_data: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": config.max_tokens,
                    "temperature": config.temperature,
                    "top_p": config.top_p,
                    "top_k": config.top_k,
                },
            }

            if config.stop_sequences:
                request_data["options"]["stop"] = config.stop_sequences

            response = await client.post(
                "/api/chat",
                json=request_data,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama chat error: {response.text}")

            data = response.json()
            latency_ms = int((time.time() - start_time) * 1000)

            message = data.get("message", {})

            return GenerationResult(
                text=message.get("content", ""),
                tokens_generated=data.get("eval_count", 0),
                tokens_prompt=data.get("prompt_eval_count", 0),
                model=self.model,
                finish_reason="stop" if data.get("done") else "length",
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using Ollama."""
        try:
            client = await self._get_client()

            response = await client.post(
                "/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama embeddings error: {response.text}")

            data = response.json()
            return data.get("embedding", [])

        except Exception as e:
            logger.error(f"Ollama embeddings error: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
