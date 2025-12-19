"""
Built-in Provider Implementations

These are the standard providers that come with FlowMason.
They can serve as examples for creating custom providers.
"""

import os
from typing import AsyncIterator, Dict, List, Optional

from .base import (
    ProviderBase,
    ProviderCapability,
    ProviderResponse,
    register_provider,
)


@register_provider
class AnthropicProvider(ProviderBase):
    """
    Provider for Anthropic's Claude models.

    Supports Claude 3/3.5/4 family including Opus, Sonnet, and Haiku.
    """

    DEFAULT_PRICING = {"input": 3.0, "output": 15.0}

    MODEL_PRICING = {
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
        "claude-opus-4-5-20251101": {"input": 15.0, "output": 75.0},
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        pricing: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY env var or pass api_key."
            )

        model = model or "claude-sonnet-4-20250514"
        pricing = pricing or self.MODEL_PRICING.get(model, self.DEFAULT_PRICING)

        super().__init__(
            api_key=api_key,
            model=model,
            timeout=timeout,
            max_retries=max_retries,
            pricing=pricing,
            **kwargs
        )
        self._client = None
        self._async_client = None

    @property
    def client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                )
            except ImportError:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
        return self._client

    @property
    def async_client(self):
        """Lazy-load the async Anthropic client."""
        if self._async_client is None:
            try:
                import anthropic
                self._async_client = anthropic.AsyncAnthropic(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                )
            except ImportError:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
        return self._async_client

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return "claude-sonnet-4-20250514"

    @property
    def available_models(self) -> List[str]:
        return list(self.MODEL_PRICING.keys())

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.TEXT_GENERATION,
            ProviderCapability.STREAMING,
            ProviderCapability.VISION,
        ]

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        model = model or self.model or self.default_model

        try:
            messages = [{"role": "user", "content": prompt}]

            def _call():
                return self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system or "You are a helpful assistant.",
                    messages=messages,
                    **kwargs
                )

            response, duration_ms = self._time_call(_call)

            content = ""
            if response.content:
                content = response.content[0].text

            usage = self._build_usage_dict(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=model,
                stop_reason=response.stop_reason,
            )

            return ProviderResponse(
                content=content,
                model=model,
                usage=usage,
                duration_ms=duration_ms,
                metadata={"stop_reason": response.stop_reason, "id": response.id}
            )

        except Exception as e:
            return ProviderResponse(
                content="",
                model=model,
                success=False,
                error=str(e),
            )

    async def call_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        import time
        model = model or self.model or self.default_model

        try:
            messages = [{"role": "user", "content": prompt}]

            start = time.perf_counter()
            response = await self.async_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "You are a helpful assistant.",
                messages=messages,
                **kwargs
            )
            duration_ms = int((time.perf_counter() - start) * 1000)

            content = ""
            if response.content:
                content = response.content[0].text

            usage = self._build_usage_dict(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=model,
                stop_reason=response.stop_reason,
            )

            return ProviderResponse(
                content=content,
                model=model,
                usage=usage,
                duration_ms=duration_ms,
                metadata={"stop_reason": response.stop_reason, "id": response.id}
            )

        except Exception as e:
            return ProviderResponse(
                content="",
                model=model,
                success=False,
                error=str(e),
            )

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

        Yields:
            Token chunks as they arrive from the API
        """
        model = model or self.model or self.default_model

        try:
            messages = [{"role": "user", "content": prompt}]

            async with self.async_client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "You are a helpful assistant.",
                messages=messages,
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            yield f"[Error: {str(e)}]"


@register_provider
class OpenAIProvider(ProviderBase):
    """Provider for OpenAI's GPT models."""

    DEFAULT_PRICING = {"input": 2.5, "output": 10.0}

    MODEL_PRICING = {
        "gpt-4o": {"input": 2.5, "output": 10.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "o1-preview": {"input": 15.0, "output": 60.0},
        "o1-mini": {"input": 3.0, "output": 12.0},
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        pricing: Optional[Dict[str, float]] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key."
            )

        model = model or "gpt-4o"
        pricing = pricing or self.MODEL_PRICING.get(model, self.DEFAULT_PRICING)

        super().__init__(
            api_key=api_key,
            model=model,
            timeout=timeout,
            max_retries=max_retries,
            pricing=pricing,
            **kwargs
        )
        self.base_url = base_url
        self._client = None
        self._async_client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                    base_url=self.base_url,
                )
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._client

    @property
    def async_client(self):
        if self._async_client is None:
            try:
                from openai import AsyncOpenAI
                self._async_client = AsyncOpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                    base_url=self.base_url,
                )
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._async_client

    @property
    def name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return "gpt-4o"

    @property
    def available_models(self) -> List[str]:
        return list(self.MODEL_PRICING.keys())

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.TEXT_GENERATION,
            ProviderCapability.STREAMING,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.VISION,
        ]

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        model = model or self.model or self.default_model

        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            def _call():
                return self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

            response, duration_ms = self._time_call(_call)

            content = response.choices[0].message.content or ""

            usage = self._build_usage_dict(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                model=model,
                finish_reason=response.choices[0].finish_reason,
            )

            return ProviderResponse(
                content=content,
                model=model,
                usage=usage,
                duration_ms=duration_ms,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id,
                }
            )

        except Exception as e:
            return ProviderResponse(
                content="",
                model=model,
                success=False,
                error=str(e),
            )

    async def call_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        import time
        model = model or self.model or self.default_model

        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            start = time.perf_counter()
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            duration_ms = int((time.perf_counter() - start) * 1000)

            content = response.choices[0].message.content or ""

            usage = self._build_usage_dict(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                model=model,
                finish_reason=response.choices[0].finish_reason,
            )

            return ProviderResponse(
                content=content,
                model=model,
                usage=usage,
                duration_ms=duration_ms,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id,
                }
            )

        except Exception as e:
            return ProviderResponse(
                content="",
                model=model,
                success=False,
                error=str(e),
            )

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

        Yields:
            Token chunks as they arrive from the API
        """
        model = model or self.model or self.default_model

        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            stream = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"[Error: {str(e)}]"


@register_provider
class GoogleProvider(ProviderBase):
    """Provider for Google's Gemini models."""

    DEFAULT_PRICING = {"input": 1.25, "output": 5.0}

    MODEL_PRICING = {
        "gemini-1.5-pro": {"input": 1.25, "output": 5.0},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.3},
        "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.3},
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        pricing: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY env var or pass api_key."
            )

        model = model or "gemini-1.5-pro"
        pricing = pricing or self.MODEL_PRICING.get(model, self.DEFAULT_PRICING)

        super().__init__(
            api_key=api_key,
            model=model,
            timeout=timeout,
            max_retries=max_retries,
            pricing=pricing,
            **kwargs
        )

    @property
    def name(self) -> str:
        return "google"

    @property
    def default_model(self) -> str:
        return "gemini-1.5-pro"

    @property
    def available_models(self) -> List[str]:
        return list(self.MODEL_PRICING.keys())

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.TEXT_GENERATION,
            ProviderCapability.STREAMING,
            ProviderCapability.VISION,
        ]

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        model = model or self.model or self.default_model

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            client = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config,  # type: ignore[arg-type]
                system_instruction=system,
            )

            def _call():
                return client.generate_content(prompt)

            response, duration_ms = self._time_call(_call)

            content = response.text if response.text else ""

            # Estimate tokens (Gemini doesn't always provide exact counts)
            input_tokens = len(prompt.split()) * 1.3
            output_tokens = len(content.split()) * 1.3

            usage = self._build_usage_dict(
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
                model=model,
            )

            return ProviderResponse(
                content=content,
                model=model,
                usage=usage,
                duration_ms=duration_ms,
            )

        except ImportError:
            raise ImportError(
                "google-generativeai package required. Install with: pip install google-generativeai"
            )
        except Exception as e:
            return ProviderResponse(
                content="",
                model=model,
                success=False,
                error=str(e),
            )


@register_provider
class GroqProvider(ProviderBase):
    """Provider for Groq's fast inference models."""

    DEFAULT_PRICING = {"input": 0.59, "output": 0.79}

    MODEL_PRICING = {
        "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
        "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
        "mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
        "gemma2-9b-it": {"input": 0.20, "output": 0.20},
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        pricing: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "Groq API key required. Set GROQ_API_KEY env var or pass api_key."
            )

        model = model or "llama-3.3-70b-versatile"
        pricing = pricing or self.MODEL_PRICING.get(model, self.DEFAULT_PRICING)

        super().__init__(
            api_key=api_key,
            model=model,
            timeout=timeout,
            max_retries=max_retries,
            pricing=pricing,
            **kwargs
        )
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError("groq package required. Install with: pip install groq")
        return self._client

    @property
    def name(self) -> str:
        return "groq"

    @property
    def default_model(self) -> str:
        return "llama-3.3-70b-versatile"

    @property
    def available_models(self) -> List[str]:
        return list(self.MODEL_PRICING.keys())

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.TEXT_GENERATION,
            ProviderCapability.STREAMING,
        ]

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        model = model or self.model or self.default_model

        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            def _call():
                return self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

            response, duration_ms = self._time_call(_call)

            content = response.choices[0].message.content or ""

            usage = self._build_usage_dict(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                model=model,
                finish_reason=response.choices[0].finish_reason,
            )

            return ProviderResponse(
                content=content,
                model=model,
                usage=usage,
                duration_ms=duration_ms,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id,
                }
            )

        except Exception as e:
            return ProviderResponse(
                content="",
                model=model,
                success=False,
                error=str(e),
            )


@register_provider
class PerplexityProvider(ProviderBase):
    """
    Provider for Perplexity AI models with real-time internet search.

    Perplexity's "online" models can search the web in real-time, making them
    ideal for research, fact-checking, and up-to-date information retrieval.
    Uses OpenAI-compatible API format.
    """

    DEFAULT_PRICING = {"input": 0.2, "output": 0.2}

    # Pricing per 1M tokens (as of Dec 2024)
    MODEL_PRICING = {
        # Sonar models with online search
        "sonar": {"input": 1.0, "output": 1.0},
        "sonar-pro": {"input": 3.0, "output": 15.0},
        "sonar-reasoning": {"input": 1.0, "output": 5.0},
        # Legacy models
        "sonar-small-online": {"input": 0.2, "output": 0.2},
        "sonar-medium-online": {"input": 0.6, "output": 0.6},
        "sonar-small-chat": {"input": 0.2, "output": 0.2},
        "sonar-medium-chat": {"input": 0.6, "output": 0.6},
        # Llama-based models
        "llama-3.1-sonar-small-128k-online": {"input": 0.2, "output": 0.2},
        "llama-3.1-sonar-large-128k-online": {"input": 1.0, "output": 1.0},
        "llama-3.1-sonar-huge-128k-online": {"input": 5.0, "output": 5.0},
    }

    BASE_URL = "https://api.perplexity.ai"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        pricing: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        api_key = api_key or os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError(
                "Perplexity API key required. Set PERPLEXITY_API_KEY env var or pass api_key."
            )

        model = model or "sonar-pro"
        pricing = pricing or self.MODEL_PRICING.get(model, self.DEFAULT_PRICING)

        super().__init__(
            api_key=api_key,
            model=model,
            timeout=timeout,
            max_retries=max_retries,
            pricing=pricing,
            **kwargs
        )
        self._client = None
        self._async_client = None

    @property
    def client(self):
        """Lazy-load the Perplexity client (OpenAI-compatible)."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.BASE_URL,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                )
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._client

    @property
    def async_client(self):
        """Lazy-load the async Perplexity client."""
        if self._async_client is None:
            try:
                from openai import AsyncOpenAI
                self._async_client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.BASE_URL,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                )
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._async_client

    @property
    def name(self) -> str:
        return "perplexity"

    @property
    def default_model(self) -> str:
        return "sonar-pro"

    @property
    def available_models(self) -> List[str]:
        return list(self.MODEL_PRICING.keys())

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.TEXT_GENERATION,
            ProviderCapability.STREAMING,
        ]

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        model = model or self.model or self.default_model

        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            def _call():
                return self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

            response, duration_ms = self._time_call(_call)

            content = response.choices[0].message.content or ""

            # Extract citations if available (Perplexity includes sources)
            citations = []
            if hasattr(response, 'citations'):
                citations = response.citations

            usage = self._build_usage_dict(
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                model=model,
                finish_reason=response.choices[0].finish_reason,
            )

            return ProviderResponse(
                content=content,
                model=model,
                usage=usage,
                duration_ms=duration_ms,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id,
                    "citations": citations,
                }
            )

        except Exception as e:
            return ProviderResponse(
                content="",
                model=model,
                success=False,
                error=str(e),
            )

    async def call_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        import time
        model = model or self.model or self.default_model

        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            start = time.perf_counter()
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            duration_ms = int((time.perf_counter() - start) * 1000)

            content = response.choices[0].message.content or ""

            # Extract citations if available
            citations = []
            if hasattr(response, 'citations'):
                citations = response.citations

            usage = self._build_usage_dict(
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                model=model,
                finish_reason=response.choices[0].finish_reason,
            )

            return ProviderResponse(
                content=content,
                model=model,
                usage=usage,
                duration_ms=duration_ms,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id,
                    "citations": citations,
                }
            )

        except Exception as e:
            return ProviderResponse(
                content="",
                model=model,
                success=False,
                error=str(e),
            )

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

        Yields:
            Token chunks as they arrive from the API
        """
        model = model or self.model or self.default_model

        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            stream = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"[Error: {str(e)}]"
