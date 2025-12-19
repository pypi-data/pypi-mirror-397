"""
NLP Trigger Service for FlowMason.

Main service for natural language pipeline triggers.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from flowmason_core.nlp.input_extractor import InputExtractor, ExtractionResult
from flowmason_core.nlp.intent_parser import Intent, IntentParser
from flowmason_core.nlp.pipeline_matcher import MatchResult, PipelineMatcher

logger = logging.getLogger(__name__)


@dataclass
class TriggerResult:
    """Result of processing a natural language trigger."""
    success: bool
    pipeline_name: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    intent: Optional[Intent] = None
    match: Optional[MatchResult] = None
    extraction: Optional[ExtractionResult] = None
    error: Optional[str] = None
    alternatives: List[MatchResult] = field(default_factory=list)


class NLPTriggerService:
    """
    Natural Language Pipeline Trigger Service.

    Provides a complete pipeline for:
    1. Parsing natural language commands to extract intent
    2. Matching intents to available pipelines
    3. Extracting input values from the command
    4. Returning a ready-to-execute pipeline configuration

    Example:
        service = NLPTriggerService(pipelines)
        result = await service.parse("generate a sales report for last week")

        if result.success:
            print(f"Running {result.pipeline_name} with {result.inputs}")
    """

    def __init__(
        self,
        pipelines: Optional[Dict[str, Any]] = None,
        pipeline_loader: Optional[Callable[[str], Any]] = None,
        use_llm: bool = False,
        llm_client: Any = None,
    ):
        """
        Initialize the NLP trigger service.

        Args:
            pipelines: Dictionary of pipeline name -> pipeline config
            pipeline_loader: Function to load pipeline by name
            use_llm: Whether to use LLM for better accuracy
            llm_client: LLM client (Anthropic/OpenAI)
        """
        self._pipelines = pipelines or {}
        self._pipeline_loader = pipeline_loader
        self._use_llm = use_llm
        self._llm_client = llm_client

        self._intent_parser = IntentParser()
        self._pipeline_matcher = PipelineMatcher(
            pipelines=pipelines,
            pipeline_loader=pipeline_loader,
        )
        self._input_extractor = InputExtractor()

    def register_pipeline(self, name: str, pipeline: Any) -> None:
        """
        Register a pipeline for natural language matching.

        Args:
            name: Pipeline name
            pipeline: Pipeline configuration
        """
        self._pipelines[name] = pipeline
        self._pipeline_matcher.register_pipeline(name, pipeline)

    def register_pipelines(self, pipelines: Dict[str, Any]) -> None:
        """Register multiple pipelines."""
        for name, pipeline in pipelines.items():
            self.register_pipeline(name, pipeline)

    async def parse(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
        threshold: float = 0.5,
    ) -> TriggerResult:
        """
        Parse a natural language command and match to a pipeline.

        Args:
            command: Natural language command (e.g., "run sales report for yesterday")
            context: Optional context (user preferences, previous values)
            threshold: Minimum confidence threshold for matching

        Returns:
            TriggerResult with matched pipeline and extracted inputs
        """
        try:
            # Step 1: Parse intent
            if self._use_llm and self._llm_client:
                intent = self._intent_parser.parse_with_llm(command, self._llm_client)
            else:
                intent = self._intent_parser.parse(command)

            logger.debug(f"Parsed intent: {intent.type.value} - {intent.action}")

            # Step 2: Match to pipeline
            if self._use_llm and self._llm_client:
                matches = await self._pipeline_matcher.match_with_llm(
                    intent,
                    self._llm_client,
                    threshold=threshold,
                )
            else:
                matches = self._pipeline_matcher.match(intent, threshold=threshold)

            if not matches:
                return TriggerResult(
                    success=False,
                    intent=intent,
                    error="No matching pipeline found for command",
                )

            best_match = matches[0]
            alternatives = matches[1:] if len(matches) > 1 else []

            logger.debug(f"Matched pipeline: {best_match.pipeline_name} (confidence: {best_match.confidence})")

            # Step 3: Get pipeline for input extraction
            pipeline = self._pipelines.get(best_match.pipeline_name)
            if not pipeline and self._pipeline_loader:
                pipeline = self._pipeline_loader(best_match.pipeline_name)

            if pipeline:
                self._input_extractor.set_schemas_from_pipeline(pipeline)

            # Step 4: Extract inputs
            merged_entities = {**intent.entities, **best_match.extracted_entities}
            merged_context = context or {}

            # Add modifiers to context
            if intent.modifiers:
                merged_context.update(intent.modifiers)

            if self._use_llm and self._llm_client:
                extraction = await self._input_extractor.extract_with_llm(
                    command,
                    self._llm_client,
                    context=merged_context,
                )
            else:
                extraction = self._input_extractor.extract(
                    command,
                    entities=merged_entities,
                    context=merged_context,
                )

            logger.debug(f"Extracted inputs: {extraction.inputs}")

            # Check for missing required inputs
            if extraction.missing_required:
                return TriggerResult(
                    success=False,
                    pipeline_name=best_match.pipeline_name,
                    inputs=extraction.inputs,
                    confidence=best_match.confidence,
                    intent=intent,
                    match=best_match,
                    extraction=extraction,
                    error=f"Missing required inputs: {', '.join(extraction.missing_required)}",
                    alternatives=alternatives,
                )

            # Calculate overall confidence
            overall_confidence = (
                intent.confidence * 0.3 +
                best_match.confidence * 0.5 +
                extraction.confidence * 0.2
            )

            return TriggerResult(
                success=True,
                pipeline_name=best_match.pipeline_name,
                inputs=extraction.inputs,
                confidence=overall_confidence,
                intent=intent,
                match=best_match,
                extraction=extraction,
                alternatives=alternatives,
            )

        except Exception as e:
            logger.error(f"Error parsing command: {e}")
            return TriggerResult(
                success=False,
                error=str(e),
            )

    def parse_sync(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
        threshold: float = 0.5,
    ) -> TriggerResult:
        """
        Synchronous version of parse for CLI usage.

        Args:
            command: Natural language command
            context: Optional context
            threshold: Minimum confidence threshold

        Returns:
            TriggerResult with matched pipeline and extracted inputs
        """
        try:
            # Parse intent (always synchronous)
            intent = self._intent_parser.parse(command)

            # Match to pipeline (synchronous)
            matches = self._pipeline_matcher.match(intent, threshold=threshold)

            if not matches:
                return TriggerResult(
                    success=False,
                    intent=intent,
                    error="No matching pipeline found for command",
                )

            best_match = matches[0]
            alternatives = matches[1:] if len(matches) > 1 else []

            # Get pipeline for input extraction
            pipeline = self._pipelines.get(best_match.pipeline_name)
            if not pipeline and self._pipeline_loader:
                pipeline = self._pipeline_loader(best_match.pipeline_name)

            if pipeline:
                self._input_extractor.set_schemas_from_pipeline(pipeline)

            # Extract inputs
            merged_entities = {**intent.entities, **best_match.extracted_entities}
            merged_context = context or {}
            if intent.modifiers:
                merged_context.update(intent.modifiers)

            extraction = self._input_extractor.extract(
                command,
                entities=merged_entities,
                context=merged_context,
            )

            # Check for missing required inputs
            if extraction.missing_required:
                return TriggerResult(
                    success=False,
                    pipeline_name=best_match.pipeline_name,
                    inputs=extraction.inputs,
                    confidence=best_match.confidence,
                    intent=intent,
                    match=best_match,
                    extraction=extraction,
                    error=f"Missing required inputs: {', '.join(extraction.missing_required)}",
                    alternatives=alternatives,
                )

            # Calculate overall confidence
            overall_confidence = (
                intent.confidence * 0.3 +
                best_match.confidence * 0.5 +
                extraction.confidence * 0.2
            )

            return TriggerResult(
                success=True,
                pipeline_name=best_match.pipeline_name,
                inputs=extraction.inputs,
                confidence=overall_confidence,
                intent=intent,
                match=best_match,
                extraction=extraction,
                alternatives=alternatives,
            )

        except Exception as e:
            logger.error(f"Error parsing command: {e}")
            return TriggerResult(
                success=False,
                error=str(e),
            )

    def explain_match(self, result: TriggerResult) -> str:
        """
        Generate a human-readable explanation of the match.

        Args:
            result: TriggerResult from parse()

        Returns:
            Explanation string
        """
        if not result.success:
            return f"Failed to match: {result.error}"

        lines = [
            f"Matched pipeline: {result.pipeline_name}",
            f"Confidence: {result.confidence:.0%}",
            "",
            "Intent Analysis:",
            f"  Type: {result.intent.type.value if result.intent else 'unknown'}",
            f"  Action: {result.intent.action if result.intent else 'unknown'}",
            f"  Target: {result.intent.target if result.intent else 'unknown'}",
        ]

        if result.match:
            lines.extend([
                "",
                "Match Details:",
                f"  Reasoning: {result.match.reasoning}",
            ])
            if result.match.matched_pattern:
                lines.append(f"  Pattern: {result.match.matched_pattern}")

        if result.inputs:
            lines.extend([
                "",
                "Extracted Inputs:",
            ])
            for key, value in result.inputs.items():
                lines.append(f"  {key}: {value}")

        if result.alternatives:
            lines.extend([
                "",
                "Alternative Matches:",
            ])
            for alt in result.alternatives[:3]:
                lines.append(f"  - {alt.pipeline_name} ({alt.confidence:.0%})")

        return "\n".join(lines)

    def suggest_pipelines(
        self,
        partial_command: str,
        max_suggestions: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Suggest pipelines based on partial command (for autocomplete).

        Args:
            partial_command: Partial natural language command
            max_suggestions: Maximum suggestions to return

        Returns:
            List of pipeline suggestions with metadata
        """
        intent = self._intent_parser.parse(partial_command)
        matches = self._pipeline_matcher.match(intent, threshold=0.2, max_results=max_suggestions)

        suggestions = []
        for match in matches:
            pipeline = self._pipelines.get(match.pipeline_name, {})
            desc = ""
            if isinstance(pipeline, dict):
                desc = pipeline.get("description", "")
            elif hasattr(pipeline, "description"):
                desc = pipeline.description or ""

            suggestions.append({
                "name": match.pipeline_name,
                "description": desc,
                "confidence": match.confidence,
                "reasoning": match.reasoning,
            })

        return suggestions
