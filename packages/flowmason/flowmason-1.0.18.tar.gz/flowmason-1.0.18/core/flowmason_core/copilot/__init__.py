"""
FlowMason AI Co-pilot Integration.

Provides AI-assisted pipeline design and development capabilities:
- Pipeline suggestions and generation
- Stage recommendations
- Error diagnosis and fixes
- Natural language pipeline explanations
- Optimization suggestions

Example:
    from flowmason_core.copilot import CopilotService, CopilotContext

    copilot = CopilotService(provider="anthropic")
    context = CopilotContext.from_pipeline(pipeline)

    # Get suggestions
    suggestions = await copilot.suggest("Add error handling to the API call")

    # Explain pipeline
    explanation = await copilot.explain(pipeline)

    # Generate pipeline from description
    pipeline = await copilot.generate("Fetch data from API and summarize it")
"""

from flowmason_core.copilot.context import CopilotContext, PipelineSnapshot
from flowmason_core.copilot.service import CopilotService, Suggestion, SuggestionType
from flowmason_core.copilot.prompts import CopilotPrompts

__all__ = [
    "CopilotService",
    "CopilotContext",
    "CopilotPrompts",
    "PipelineSnapshot",
    "Suggestion",
    "SuggestionType",
]
