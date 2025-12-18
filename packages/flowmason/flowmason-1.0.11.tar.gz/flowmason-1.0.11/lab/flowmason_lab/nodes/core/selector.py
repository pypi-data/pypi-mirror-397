"""
Selector Node - Core FlowMason Component.

Chooses the best option from a set of candidates.
Essential for A/B testing, quality selection, and decision-making pipelines.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="selector",
    category="core",
    description="Choose the best option from a set of candidates based on criteria",
    icon="check-circle",
    color="#F97316",
    version="1.0.0",
    author="FlowMason",
    tags=["selection", "choice", "ranking", "decision", "core"],
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.2,
            "max_tokens": 2048,
        },
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.2,
            "max_tokens": 2048,
        },
    },
    default_provider="anthropic",
)
class SelectorNode:
    """
    Choose the best option from a set of candidates.

    The Selector node evaluates multiple options and selects the best one
    based on specified criteria. Essential for:

    - A/B testing content variations
    - Quality-based selection
    - Multi-path pipeline decisions
    - Choosing optimal responses
    - Filtering to top N results
    """

    class Input(NodeInput):
        candidates: List[str] = Field(
            description="List of candidate options to choose from",
            min_length=2,
        )
        criteria: Optional[List[str]] = Field(
            default=None,
            description="Criteria to evaluate candidates against",
            examples=[
                ["clarity", "accuracy", "engagement"],
                ["relevance", "completeness"],
            ],
        )
        context: Optional[str] = Field(
            default=None,
            description="Context for the selection (e.g., purpose, audience)",
        )
        selection_mode: str = Field(
            default="best",
            description="How to select: 'best' (single), 'top_n', or 'rank_all'",
        )
        top_n: int = Field(
            default=1,
            ge=1,
            le=10,
            description="Number of top candidates to return (for top_n mode)",
        )
        explain_choice: bool = Field(
            default=True,
            description="Include explanation for why the selection was made",
        )

    class Output(NodeOutput):
        selected: str = Field(
            description="The selected/best candidate"
        )
        selected_index: int = Field(
            description="Index of the selected candidate (0-based)"
        )
        explanation: str = Field(
            default="",
            description="Explanation for the selection"
        )
        rankings: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Full rankings with scores (for rank_all mode)"
        )
        confidence: float = Field(
            default=0.0,
            ge=0.0,
            le=1.0,
            description="Confidence in the selection (0-1)"
        )

    class Config:
        deterministic: bool = False
        timeout_seconds: int = 60

    async def execute(self, input: Input, context) -> Output:
        """
        Execute the selection using the configured provider.

        Args:
            input: The validated Input model
            context: Execution context with providers and metadata

        Returns:
            Output with selected candidate and explanation
        """
        # Check if LLM helper is available via context.llm
        llm = getattr(context, "llm", None)

        if not llm:
            # Fallback for testing without providers
            return self.Output(
                selected=input.candidates[0],
                selected_index=0,
                explanation="[Selection made without provider - defaulted to first]",
                rankings=[],
                confidence=0.5,
            )

        # Format candidates for the prompt
        candidates_text = ""
        for i, candidate in enumerate(input.candidates):
            candidates_text += f"\n[Option {i + 1}]:\n{candidate}\n"

        criteria_text = ""
        if input.criteria:
            criteria_text = "\nEvaluate based on these criteria:\n"
            for c in input.criteria:
                criteria_text += f"- {c}\n"

        context_text = f"\nContext: {input.context}" if input.context else ""

        mode_instruction = self._get_mode_instruction(input.selection_mode, input.top_n)

        system_prompt = f"""You are an expert evaluator tasked with selecting the best option(s) from a set of candidates.

{mode_instruction}

Respond in JSON format:
{{
    "selected_index": 0,  // 0-based index of the best option
    "explanation": "why this was selected",
    "rankings": [
        {{"index": 0, "score": 0.95, "strengths": ["..."], "weaknesses": ["..."]}},
        ...
    ],
    "confidence": 0.85  // 0-1 confidence in the selection
}}"""

        user_prompt = f"""Select the best option from these {len(input.candidates)} candidates:
{candidates_text}
{criteria_text}{context_text}

Evaluate each option and select the best one."""

        # Call LLM via context.llm.generate_async()
        response = await llm.generate_async(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=2048,
        )

        # Parse JSON response
        import json
        try:
            result = json.loads(response.content)
            selected_idx = result.get("selected_index", 0)

            # Validate index
            if selected_idx < 0 or selected_idx >= len(input.candidates):
                selected_idx = 0

            return self.Output(
                selected=input.candidates[selected_idx],
                selected_index=selected_idx,
                explanation=result.get("explanation", ""),
                rankings=result.get("rankings", []),
                confidence=float(result.get("confidence", 0.5)),
            )
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract selection from response
            return self.Output(
                selected=input.candidates[0],
                selected_index=0,
                explanation=response.content,
                rankings=[],
                confidence=0.5,
            )

    def _get_mode_instruction(self, mode: str, top_n: int) -> str:
        """Get instructions based on selection mode."""
        if mode == "best":
            return "Select the single best option from the candidates."
        elif mode == "top_n":
            return f"Select the top {top_n} options, ranked from best to worst."
        elif mode == "rank_all":
            return "Rank all options from best to worst with scores."
        else:
            return "Select the single best option from the candidates."
