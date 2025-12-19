"""
Improver Node - Core FlowMason Component.

Refines content based on feedback and criteria.
Works with Critic node for iterative improvement loops.
"""

from typing import List, Optional

from flowmason_core.core.decorators import node
from flowmason_core.core.types import Field, NodeInput, NodeOutput


@node(
    name="improver",
    category="core",
    description="Refine and improve content based on feedback and criteria",
    icon="arrow-up-circle",
    color="#10B981",
    version="1.0.0",
    author="FlowMason",
    tags=["improvement", "refinement", "iteration", "core"],
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
class ImproverNode:
    """
    Refine content based on feedback.

    The Improver node takes original content and feedback (typically from
    a Critic node) and produces an improved version. It's essential for:

    - Iterative content refinement
    - Implementing feedback loops
    - Quality improvement pipelines
    - Style adjustments
    - Error correction
    """

    class Input(NodeInput):
        content: str = Field(
            description="The original content to improve",
        )
        feedback: str = Field(
            description="Feedback describing what to improve",
        )
        improvements: Optional[List[str]] = Field(
            default=None,
            description="Specific improvements to make (from Critic node)",
        )
        preserve_aspects: Optional[List[str]] = Field(
            default=None,
            description="Aspects of the original to preserve",
            examples=[["tone", "length"], ["technical accuracy", "formatting"]],
        )
        improvement_focus: Optional[str] = Field(
            default=None,
            description="Primary focus area for improvement",
            examples=["clarity", "engagement", "accuracy", "brevity"],
        )
        max_iterations: int = Field(
            default=1,
            ge=1,
            le=5,
            description="Maximum improvement passes (for internal refinement)",
        )

    class Output(NodeOutput):
        improved_content: str = Field(
            description="The improved version of the content"
        )
        changes_made: List[str] = Field(
            default_factory=list,
            description="Summary of changes made"
        )
        preserved_aspects: List[str] = Field(
            default_factory=list,
            description="Aspects that were preserved"
        )
        improvement_summary: str = Field(
            default="",
            description="Brief summary of the improvement process"
        )

    class Config:
        deterministic: bool = False
        timeout_seconds: int = 120

    async def execute(self, input: Input, context) -> Output:
        """
        Execute the improvement using the configured provider.

        Args:
            input: The validated Input model
            context: Execution context with providers and metadata

        Returns:
            Output with improved content and change summary
        """
        # Check if LLM helper is available via context.llm
        llm = getattr(context, "llm", None)

        if not llm:
            # Fallback for testing without providers
            return self.Output(
                improved_content=f"[Improved version of: {input.content[:50]}...]",
                changes_made=["Applied feedback"],
                preserved_aspects=input.preserve_aspects or [],
                improvement_summary="Content improved based on feedback",
            )

        # Build improvement instructions
        improvements_text = ""
        if input.improvements:
            improvements_text = "\n\nSpecific improvements to make:\n"
            for imp in input.improvements:
                improvements_text += f"- {imp}\n"

        preserve_text = ""
        if input.preserve_aspects:
            preserve_text = "\n\nPreserve these aspects:\n"
            for asp in input.preserve_aspects:
                preserve_text += f"- {asp}\n"

        focus_text = ""
        if input.improvement_focus:
            focus_text = f"\n\nPrimary focus: {input.improvement_focus}"

        system_prompt = """You are an expert editor and content improver. Your task is to improve the given content based on the provided feedback while maintaining the original intent and voice.

After improving the content, provide a JSON response with:
{
    "improved_content": "the improved text",
    "changes_made": ["list of changes"],
    "preserved_aspects": ["what was kept"],
    "improvement_summary": "brief summary"
}"""

        user_prompt = f"""Original content:
---
{input.content}
---

Feedback:
{input.feedback}
{improvements_text}{preserve_text}{focus_text}

Please improve the content based on this feedback."""

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
                improved_content=result.get("improved_content", response.content),
                changes_made=result.get("changes_made", []),
                preserved_aspects=result.get("preserved_aspects", []),
                improvement_summary=result.get("improvement_summary", ""),
            )
        except json.JSONDecodeError:
            # If JSON parsing fails, use raw response as improved content
            return self.Output(
                improved_content=response.content,
                changes_made=["Applied feedback"],
                preserved_aspects=input.preserve_aspects or [],
                improvement_summary="Content improved based on feedback",
            )
