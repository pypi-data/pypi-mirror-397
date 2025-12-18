"""
Synthesizer Node - Core FlowMason Component.

Combines multiple inputs into a unified output.
Essential for merging parallel pipeline branches.
"""

from typing import List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="synthesizer",
    category="core",
    description="Combine multiple inputs into a unified, coherent output",
    icon="git-merge",
    color="#06B6D4",
    version="1.0.0",
    author="FlowMason",
    tags=["synthesis", "combine", "merge", "aggregation", "core"],
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.5,
            "max_tokens": 4096,
        },
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.5,
            "max_tokens": 4096,
        },
    },
    default_provider="anthropic",
)
class SynthesizerNode:
    """
    Combine multiple inputs into a unified output.

    The Synthesizer node takes multiple pieces of content (from parallel
    pipeline branches or multiple sources) and combines them into a single
    coherent output. Essential for:

    - Merging parallel processing results
    - Combining multiple perspectives
    - Aggregating information from different sources
    - Creating summaries from multiple documents
    - Resolving conflicting viewpoints
    """

    class Input(NodeInput):
        inputs: List[str] = Field(
            description="List of content pieces to synthesize",
            min_length=2,
        )
        synthesis_strategy: str = Field(
            default="integrate",
            description="How to combine inputs",
            examples=["integrate", "summarize", "compare", "consensus", "best_of"],
        )
        context: Optional[str] = Field(
            default=None,
            description="Additional context to guide synthesis",
        )
        output_format: Optional[str] = Field(
            default=None,
            description="Desired format for synthesized output",
            examples=["paragraph", "bullet_points", "structured"],
        )
        preserve_sources: bool = Field(
            default=False,
            description="Include source attribution in output",
        )
        max_length: Optional[int] = Field(
            default=None,
            description="Maximum length of synthesized output (in words)",
            ge=10,
            le=10000,
        )

    class Output(NodeOutput):
        synthesized: str = Field(
            description="The synthesized output combining all inputs"
        )
        sources_used: int = Field(
            default=0,
            description="Number of input sources used"
        )
        strategy_applied: str = Field(
            default="",
            description="The synthesis strategy that was applied"
        )
        key_themes: List[str] = Field(
            default_factory=list,
            description="Common themes identified across inputs"
        )

    class Config:
        deterministic: bool = False
        timeout_seconds: int = 120

    async def execute(self, input: Input, context) -> Output:
        """
        Execute the synthesis using the configured provider.

        Args:
            input: The validated Input model
            context: Execution context with providers and metadata

        Returns:
            Output with synthesized content
        """
        # Check if LLM helper is available via context.llm
        llm = getattr(context, "llm", None)

        if not llm:
            # Fallback for testing without providers
            combined = "\n\n---\n\n".join(input.inputs)
            return self.Output(
                synthesized=f"[Synthesized from {len(input.inputs)} inputs]:\n{combined[:500]}...",
                sources_used=len(input.inputs),
                strategy_applied=input.synthesis_strategy,
                key_themes=["theme1", "theme2"],
            )

        # Build synthesis prompt based on strategy
        strategy_instructions = self._get_strategy_instructions(input.synthesis_strategy)

        # Format inputs for the prompt
        inputs_text = ""
        for i, inp in enumerate(input.inputs, 1):
            inputs_text += f"\n[Source {i}]:\n{inp}\n"

        context_text = f"\nContext: {input.context}" if input.context else ""
        format_text = f"\nOutput format: {input.output_format}" if input.output_format else ""
        length_text = f"\nTarget length: approximately {input.max_length} words" if input.max_length else ""
        source_text = "\nInclude source attribution (e.g., 'According to Source 1...')" if input.preserve_sources else ""

        system_prompt = f"""You are an expert at synthesizing information from multiple sources.

{strategy_instructions}

After synthesizing, provide a JSON response with:
{{
    "synthesized": "the synthesized content",
    "key_themes": ["list of common themes"],
    "strategy_applied": "{input.synthesis_strategy}"
}}"""

        user_prompt = f"""Synthesize the following {len(input.inputs)} inputs:
{inputs_text}
{context_text}{format_text}{length_text}{source_text}

Apply the '{input.synthesis_strategy}' strategy to combine these inputs into a unified output."""

        # Call LLM via context.llm.generate_async()
        response = await llm.generate_async(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=4096,
        )

        # Parse JSON response
        import json
        try:
            result = json.loads(response.content)
            return self.Output(
                synthesized=result.get("synthesized", response.content),
                sources_used=len(input.inputs),
                strategy_applied=result.get("strategy_applied", input.synthesis_strategy),
                key_themes=result.get("key_themes", []),
            )
        except json.JSONDecodeError:
            return self.Output(
                synthesized=response.content,
                sources_used=len(input.inputs),
                strategy_applied=input.synthesis_strategy,
                key_themes=[],
            )

    def _get_strategy_instructions(self, strategy: str) -> str:
        """Get instructions for the synthesis strategy."""
        strategies = {
            "integrate": (
                "Integration Strategy: Combine all inputs into a single coherent narrative. "
                "Weave together the information smoothly, eliminating redundancy while "
                "preserving all unique insights."
            ),
            "summarize": (
                "Summarization Strategy: Create a concise summary that captures the key "
                "points from all inputs. Focus on the most important information and "
                "common themes."
            ),
            "compare": (
                "Comparison Strategy: Analyze the inputs and highlight similarities and "
                "differences. Present a balanced view of how the sources agree or disagree."
            ),
            "consensus": (
                "Consensus Strategy: Identify areas of agreement across all inputs. "
                "Focus on common ground and shared conclusions."
            ),
            "best_of": (
                "Best-of Strategy: Evaluate each input and select the highest quality "
                "content. Combine the strongest elements from each source."
            ),
        }
        return strategies.get(strategy, strategies["integrate"])
