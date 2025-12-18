"""
Generator Node - Core FlowMason Component.

Creates content from prompts using LLM providers.
This is the foundation node for text generation in pipelines.
"""

from typing import List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="generator",
    category="core",
    description="Generate text content from a prompt using an LLM provider",
    icon="sparkles",
    color="#8B5CF6",
    version="1.0.0",
    author="FlowMason",
    tags=["generation", "text", "llm", "core"],
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.7,
            "max_tokens": 4096,
        },
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 4096,
        },
    },
    default_provider="anthropic",
)
class GeneratorNode:
    """
    Generate text content from a prompt.

    The Generator is the most fundamental node in FlowMason. It takes a prompt
    and produces text output using the configured LLM provider.

    Use cases:
    - Content creation (blog posts, marketing copy, documentation)
    - Code generation
    - Translation
    - Summarization
    - Question answering
    - Creative writing
    """

    class Input(NodeInput):
        prompt: str = Field(
            description="The prompt to generate content from",
            examples=[
                "Write a blog post about AI safety",
                "Explain quantum computing to a 10-year-old",
            ],
        )
        system_prompt: Optional[str] = Field(
            default=None,
            description="System prompt to set context and behavior",
            examples=[
                "You are a helpful technical writer.",
                "You are a creative storyteller.",
            ],
        )
        max_tokens: int = Field(
            default=4096,
            ge=1,
            le=128000,
            description="Maximum tokens to generate",
        )
        temperature: float = Field(
            default=0.7,
            ge=0.0,
            le=2.0,
            description="Sampling temperature (0=deterministic, higher=more creative)",
        )
        stop_sequences: Optional[List[str]] = Field(
            default=None,
            description="Sequences that stop generation when encountered",
        )
        output_format: Optional[str] = Field(
            default=None,
            description="Expected output format hint (e.g., 'json', 'markdown', 'code')",
        )

    class Output(NodeOutput):
        content: str = Field(description="Generated text content")
        tokens_used: int = Field(default=0, description="Total tokens used")
        finish_reason: str = Field(
            default="stop",
            description="Why generation stopped (stop, length, content_filter)",
        )
        model: str = Field(default="", description="Model used for generation")

    class Config:
        deterministic: bool = False
        timeout_seconds: int = 120

    async def execute(self, input: Input, context) -> Output:
        """
        Execute the generation using the configured provider.

        Args:
            input: The validated Input model
            context: Execution context with providers and metadata

        Returns:
            Output with generated content and usage metrics
        """
        # Check if LLM helper is available via context.llm
        llm = getattr(context, "llm", None)

        if not llm:
            # Fallback: return placeholder for testing without providers
            return self.Output(
                content=f"[Generated from: {input.prompt[:100]}...]",
                tokens_used=0,
                finish_reason="stop",
                model="mock",
            )

        # Call LLM via context.llm.generate_async()
        response = await llm.generate_async(
            prompt=input.prompt,
            system_prompt=input.system_prompt,
            temperature=input.temperature,
            max_tokens=input.max_tokens,
        )

        # Extract token usage from response
        # ProviderResponse has total_tokens as a property
        tokens = response.total_tokens if hasattr(response, 'total_tokens') else 0

        # Extract finish reason - may be in metadata or as stop_reason
        finish_reason = "stop"
        if hasattr(response, 'metadata') and response.metadata:
            finish_reason = response.metadata.get('stop_reason') or response.metadata.get('finish_reason') or "stop"

        return self.Output(
            content=response.content,
            tokens_used=tokens,
            finish_reason=finish_reason,
            model=response.model or llm.provider_name,
        )
