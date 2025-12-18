"""
FlowMason Natural Language Processing Module.

Provides natural language understanding for pipeline triggers:
- Intent parsing from natural language commands
- Pipeline matching based on semantic similarity
- Entity extraction for pipeline inputs

Example:
    from flowmason_core.nlp import NLPTriggerService

    service = NLPTriggerService(pipelines)

    # Parse natural language command
    result = await service.parse("generate a sales report for last week")

    # Returns matched pipeline and extracted inputs
    print(result.pipeline_name)  # "sales-report"
    print(result.inputs)  # {"date_range": "last week"}
"""

from flowmason_core.nlp.input_extractor import (
    ExtractionResult,
    InputExtractor,
    InputSchema,
)
from flowmason_core.nlp.intent_parser import Intent, IntentParser, IntentType
from flowmason_core.nlp.pipeline_matcher import (
    MatchResult,
    PipelineMatcher,
    PipelineTriggerConfig,
)
from flowmason_core.nlp.service import NLPTriggerService, TriggerResult

__all__ = [
    # Main service
    "NLPTriggerService",
    "TriggerResult",
    # Intent parsing
    "IntentParser",
    "Intent",
    "IntentType",
    # Pipeline matching
    "PipelineMatcher",
    "MatchResult",
    "PipelineTriggerConfig",
    # Input extraction
    "InputExtractor",
    "InputSchema",
    "ExtractionResult",
]
