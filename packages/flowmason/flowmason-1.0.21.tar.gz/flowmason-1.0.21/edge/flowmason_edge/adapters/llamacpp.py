"""
Llama.cpp Adapter for FlowMason Edge.

Provides integration with llama-cpp-python for direct GGUF model loading.
"""

import logging
import time
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

from flowmason_edge.adapters.base import (
    GenerationConfig,
    GenerationResult,
    LocalLLMAdapter,
    ModelInfo,
)

logger = logging.getLogger(__name__)


class LlamaCppAdapter(LocalLLMAdapter):
    """
    Adapter for llama-cpp-python.

    Directly loads GGUF models without requiring a server.
    Ideal for embedded/edge deployments with limited resources.

    Example:
        adapter = LlamaCppAdapter(
            model="/models/llama-2-7b-chat.Q4_K_M.gguf",
            n_ctx=2048,
            n_gpu_layers=20,  # Use GPU if available
        )

        result = await adapter.generate("Explain quantum computing")
        print(result.text)
    """

    def __init__(
        self,
        model: str,
        n_ctx: int = 2048,
        n_gpu_layers: int = 0,
        n_threads: Optional[int] = None,
        verbose: bool = False,
        **kwargs,
    ):
        """
        Initialize llama.cpp adapter.

        Args:
            model: Path to GGUF model file
            n_ctx: Context window size
            n_gpu_layers: Number of layers to offload to GPU
            n_threads: Number of CPU threads (None = auto)
            verbose: Enable verbose logging
            **kwargs: Additional llama-cpp-python parameters
        """
        super().__init__(model=model, base_url=None)
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.n_threads = n_threads
        self.verbose = verbose
        self.extra_params = kwargs
        self._llm = None
        self._model_info: Optional[ModelInfo] = None

    async def check_availability(self) -> bool:
        """Check if llama-cpp-python is available."""
        try:
            import llama_cpp
            self._is_available = True

            # Check if model file exists
            if Path(self.model).exists():
                return True
            else:
                logger.warning(f"Model file not found: {self.model}")
                return False

        except ImportError:
            logger.warning("llama-cpp-python not installed")
            self._is_available = False
            return False

    async def list_models(self) -> List[ModelInfo]:
        """
        List available models.

        For llama.cpp, this scans a models directory for GGUF files.
        """
        models = []
        model_path = Path(self.model)

        # If model is a directory, scan for GGUF files
        if model_path.is_dir():
            for gguf_file in model_path.glob("**/*.gguf"):
                models.append(ModelInfo(
                    name=gguf_file.stem,
                    size_bytes=gguf_file.stat().st_size,
                    quantization=self._extract_quantization(gguf_file.name),
                ))
        elif model_path.exists():
            models.append(ModelInfo(
                name=model_path.stem,
                size_bytes=model_path.stat().st_size,
                quantization=self._extract_quantization(model_path.name),
                loaded=self._llm is not None,
            ))

        return models

    def _extract_quantization(self, filename: str) -> Optional[str]:
        """Extract quantization from filename."""
        # Common patterns: Q4_K_M, Q5_K_S, Q8_0, etc.
        import re
        match = re.search(r'Q\d+[_\w]*', filename, re.IGNORECASE)
        return match.group(0) if match else None

    async def load_model(self, model: Optional[str] = None) -> bool:
        """Load a GGUF model."""
        model_path = model or self.model

        if self._llm is not None:
            logger.info("Model already loaded")
            return True

        try:
            from llama_cpp import Llama

            logger.info(f"Loading model: {model_path}")
            start_time = time.time()

            self._llm = Llama(
                model_path=model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                n_threads=self.n_threads,
                verbose=self.verbose,
                **self.extra_params,
            )

            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.2f}s")

            # Update model info
            model_file = Path(model_path)
            self._model_info = ModelInfo(
                name=model_file.stem,
                size_bytes=model_file.stat().st_size,
                quantization=self._extract_quantization(model_file.name),
                context_length=self.n_ctx,
                loaded=True,
            )

            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    async def unload_model(self, model: Optional[str] = None) -> bool:
        """Unload the model from memory."""
        if self._llm is not None:
            del self._llm
            self._llm = None
            self._model_info = None
            logger.info("Model unloaded")
        return True

    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None,
    ) -> GenerationResult:
        """Generate text using llama.cpp."""
        if self._llm is None:
            await self.load_model()

        if self._llm is None:
            raise RuntimeError("Model not loaded")

        config = config or GenerationConfig()
        start_time = time.time()

        # Build full prompt with system prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"<<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt}"

        try:
            # Run in thread pool to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()

            output = await loop.run_in_executor(
                None,
                lambda: self._llm(
                    full_prompt,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    top_k=config.top_k,
                    stop=config.stop_sequences or None,
                    echo=False,
                )
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Extract result
            choice = output.get("choices", [{}])[0]
            text = choice.get("text", "")
            finish_reason = choice.get("finish_reason", "stop")

            usage = output.get("usage", {})

            return GenerationResult(
                text=text,
                tokens_generated=usage.get("completion_tokens", 0),
                tokens_prompt=usage.get("prompt_tokens", 0),
                model=self.model,
                finish_reason=finish_reason,
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Generate text with streaming."""
        if self._llm is None:
            await self.load_model()

        if self._llm is None:
            raise RuntimeError("Model not loaded")

        config = config or GenerationConfig()

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"<<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt}"

        try:
            import asyncio

            # Create streaming generator
            stream = self._llm(
                full_prompt,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                stop=config.stop_sequences or None,
                stream=True,
            )

            # Yield tokens
            for output in stream:
                choice = output.get("choices", [{}])[0]
                token = choice.get("text", "")
                if token:
                    yield token

                # Allow other tasks to run
                await asyncio.sleep(0)

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """Chat completion using llama.cpp."""
        if self._llm is None:
            await self.load_model()

        if self._llm is None:
            raise RuntimeError("Model not loaded")

        config = config or GenerationConfig()
        start_time = time.time()

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            output = await loop.run_in_executor(
                None,
                lambda: self._llm.create_chat_completion(
                    messages=messages,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    top_k=config.top_k,
                    stop=config.stop_sequences or None,
                )
            )

            latency_ms = int((time.time() - start_time) * 1000)

            choice = output.get("choices", [{}])[0]
            message = choice.get("message", {})
            usage = output.get("usage", {})

            return GenerationResult(
                text=message.get("content", ""),
                tokens_generated=usage.get("completion_tokens", 0),
                tokens_prompt=usage.get("prompt_tokens", 0),
                model=self.model,
                finish_reason=choice.get("finish_reason", "stop"),
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings."""
        if self._llm is None:
            await self.load_model()

        if self._llm is None:
            raise RuntimeError("Model not loaded")

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            embedding = await loop.run_in_executor(
                None,
                lambda: self._llm.embed(text)
            )

            return embedding

        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    def get_model_info(self) -> Optional[ModelInfo]:
        """Get info about the loaded model."""
        return self._model_info
