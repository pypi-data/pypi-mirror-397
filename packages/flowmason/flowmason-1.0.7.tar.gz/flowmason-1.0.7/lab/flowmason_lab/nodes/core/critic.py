"""
Critic Node - Core FlowMason Component.

Evaluates content and provides structured feedback.
Essential for quality control and iterative improvement pipelines.
"""

from enum import Enum
from typing import Dict, List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


class Rating(str, Enum):
    """Quality rating scale."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


@node(
    name="critic",
    category="core",
    description="Evaluate content and provide structured feedback with ratings",
    icon="clipboard-check",
    color="#EF4444",
    version="1.0.0",
    author="FlowMason",
    tags=["evaluation", "feedback", "quality", "core"],
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.3,
            "max_tokens": 2048,
        },
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.3,
            "max_tokens": 2048,
        },
    },
    default_provider="anthropic",
)
class CriticNode:
    """
    Evaluate content and provide structured feedback.

    The Critic node analyzes content against specified criteria and returns
    detailed feedback with ratings. It's essential for:

    - Quality assurance in content pipelines
    - Iterative improvement loops (with Improver node)
    - A/B testing content variations
    - Compliance checking
    - Style guide enforcement
    """

    class Input(NodeInput):
        content: str = Field(
            description="The content to evaluate",
        )
        criteria: Optional[List[str]] = Field(
            default=None,
            description="Specific criteria to evaluate against",
            examples=[
                ["clarity", "accuracy", "engagement"],
                ["grammar", "tone", "completeness"],
            ],
        )
        context: Optional[str] = Field(
            default=None,
            description="Additional context for evaluation (target audience, purpose, etc.)",
        )
        rubric: Optional[Dict[str, str]] = Field(
            default=None,
            description="Detailed rubric for each criterion",
            examples=[{
                "clarity": "Content should be easy to understand for a general audience",
                "accuracy": "All facts should be verifiable and up-to-date",
            }],
        )
        strict_mode: bool = Field(
            default=False,
            description="If true, apply stricter evaluation standards",
        )

    class Output(NodeOutput):
        overall_rating: str = Field(
            description="Overall quality rating (excellent/good/acceptable/needs_improvement/poor)"
        )
        score: float = Field(
            description="Numerical score from 0.0 to 1.0"
        )
        feedback: str = Field(
            description="Detailed feedback explaining the evaluation"
        )
        strengths: List[str] = Field(
            default_factory=list,
            description="List of identified strengths"
        )
        improvements: List[str] = Field(
            default_factory=list,
            description="List of suggested improvements"
        )
        criterion_scores: Dict[str, float] = Field(
            default_factory=dict,
            description="Individual scores per criterion (0.0-1.0)"
        )
        passes_threshold: bool = Field(
            default=True,
            description="Whether content meets minimum quality threshold"
        )

    class Config:
        deterministic: bool = False
        timeout_seconds: int = 60

    async def execute(self, input: Input, context) -> Output:
        """
        Execute the evaluation using the configured provider.

        Args:
            input: The validated Input model
            context: Execution context with providers and metadata

        Returns:
            Output with evaluation results and feedback
        """
        # Check if LLM helper is available via context.llm
        llm = getattr(context, "llm", None)

        if not llm:
            # Fallback for testing without providers
            return self.Output(
                overall_rating="good",
                score=0.75,
                feedback=f"[Evaluation of content: {input.content[:50]}...]",
                strengths=["Clear structure"],
                improvements=["Could add more examples"],
                criterion_scores={},
                passes_threshold=True,
            )

        # Build evaluation prompt
        criteria_text = ""
        if input.criteria:
            criteria_text = "\n\nEvaluate against these criteria:\n"
            for c in input.criteria:
                rubric_desc = input.rubric.get(c, "") if input.rubric else ""
                criteria_text += f"- {c}"
                if rubric_desc:
                    criteria_text += f": {rubric_desc}"
                criteria_text += "\n"

        context_text = f"\n\nContext: {input.context}" if input.context else ""
        strictness = "Apply strict evaluation standards." if input.strict_mode else ""

        system_prompt = f"""You are an expert content evaluator. Analyze the provided content and give structured feedback.

{strictness}

Respond in JSON format with:
{{
    "overall_rating": "excellent|good|acceptable|needs_improvement|poor",
    "score": 0.0-1.0,
    "feedback": "detailed explanation",
    "strengths": ["list of strengths"],
    "improvements": ["list of improvements"],
    "criterion_scores": {{"criterion": score}},
    "passes_threshold": true/false
}}"""

        user_prompt = f"""Evaluate this content:

---
{input.content}
---
{criteria_text}{context_text}"""

        # Call LLM via context.llm.generate_async()
        response = await llm.generate_async(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=2048,
        )

        # Parse JSON response
        import json
        try:
            result = json.loads(response.content)
            return self.Output(
                overall_rating=result.get("overall_rating", "acceptable"),
                score=float(result.get("score", 0.5)),
                feedback=result.get("feedback", ""),
                strengths=result.get("strengths", []),
                improvements=result.get("improvements", []),
                criterion_scores=result.get("criterion_scores", {}),
                passes_threshold=result.get("passes_threshold", True),
            )
        except json.JSONDecodeError:
            # If JSON parsing fails, return basic evaluation
            return self.Output(
                overall_rating="acceptable",
                score=0.5,
                feedback=response.content,
                strengths=[],
                improvements=[],
                criterion_scores={},
                passes_threshold=True,
            )
