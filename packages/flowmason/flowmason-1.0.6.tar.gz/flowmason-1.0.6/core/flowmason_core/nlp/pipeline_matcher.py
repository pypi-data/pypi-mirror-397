"""
Pipeline Matcher for FlowMason.

Matches parsed intents to available pipelines using semantic similarity
and pattern matching.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from flowmason_core.nlp.intent_parser import Intent, IntentType

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of matching an intent to a pipeline."""
    pipeline_name: str
    confidence: float
    matched_pattern: Optional[str] = None
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""


@dataclass
class PipelineTriggerConfig:
    """Natural language trigger configuration for a pipeline."""
    patterns: List[str] = field(default_factory=list)
    entities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    description: str = ""


class PipelineMatcher:
    """
    Matches natural language intents to pipelines.

    Uses a combination of:
    - Exact pattern matching
    - Keyword matching
    - Semantic similarity (if LLM available)
    """

    def __init__(
        self,
        pipelines: Optional[Dict[str, Any]] = None,
        pipeline_loader: Optional[Callable[[str], Any]] = None,
    ):
        """
        Initialize the matcher.

        Args:
            pipelines: Dictionary of pipeline name -> pipeline config
            pipeline_loader: Function to load pipeline by name
        """
        self._pipelines = pipelines or {}
        self._pipeline_loader = pipeline_loader
        self._trigger_configs: Dict[str, PipelineTriggerConfig] = {}
        self._build_trigger_index()

    def _build_trigger_index(self) -> None:
        """Build index of trigger configurations from pipelines."""
        for name, pipeline in self._pipelines.items():
            config = self._extract_trigger_config(pipeline)
            if config:
                self._trigger_configs[name] = config

    def _extract_trigger_config(self, pipeline: Any) -> Optional[PipelineTriggerConfig]:
        """Extract trigger configuration from pipeline."""
        # Handle dict format
        if isinstance(pipeline, dict):
            triggers = pipeline.get("triggers", {})
            nl_config = triggers.get("natural_language", {})
            if nl_config:
                return PipelineTriggerConfig(
                    patterns=nl_config.get("patterns", []),
                    entities=nl_config.get("entities", {}),
                    keywords=nl_config.get("keywords", []),
                    description=pipeline.get("description", ""),
                )
            # Fall back to description-based matching
            return PipelineTriggerConfig(
                description=pipeline.get("description", ""),
                keywords=self._extract_keywords(pipeline.get("name", "")),
            )

        # Handle object format
        if hasattr(pipeline, "triggers"):
            triggers = pipeline.triggers or {}
            nl_config = triggers.get("natural_language", {})
            if nl_config:
                return PipelineTriggerConfig(
                    patterns=nl_config.get("patterns", []),
                    entities=nl_config.get("entities", {}),
                    keywords=nl_config.get("keywords", []),
                    description=getattr(pipeline, "description", ""),
                )

        # Fall back to description
        if hasattr(pipeline, "description"):
            return PipelineTriggerConfig(
                description=pipeline.description or "",
                keywords=self._extract_keywords(getattr(pipeline, "name", "")),
            )

        return None

    def _extract_keywords(self, name: str) -> List[str]:
        """Extract keywords from pipeline name."""
        # Split on common separators
        words = re.split(r"[-_\s]+", name.lower())
        return [w for w in words if len(w) > 2]

    def register_pipeline(
        self,
        name: str,
        pipeline: Any,
        trigger_config: Optional[PipelineTriggerConfig] = None,
    ) -> None:
        """
        Register a pipeline for matching.

        Args:
            name: Pipeline name
            pipeline: Pipeline configuration
            trigger_config: Optional explicit trigger config
        """
        self._pipelines[name] = pipeline
        if trigger_config:
            self._trigger_configs[name] = trigger_config
        else:
            config = self._extract_trigger_config(pipeline)
            if config:
                self._trigger_configs[name] = config

    def match(
        self,
        intent: Intent,
        threshold: float = 0.5,
        max_results: int = 3,
    ) -> List[MatchResult]:
        """
        Match an intent to available pipelines.

        Args:
            intent: Parsed intent from natural language
            threshold: Minimum confidence threshold
            max_results: Maximum number of results to return

        Returns:
            List of MatchResult sorted by confidence
        """
        results: List[MatchResult] = []

        for name, config in self._trigger_configs.items():
            match_result = self._score_pipeline(name, config, intent)
            if match_result and match_result.confidence >= threshold:
                results.append(match_result)

        # Sort by confidence
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results[:max_results]

    def _score_pipeline(
        self,
        name: str,
        config: PipelineTriggerConfig,
        intent: Intent,
    ) -> Optional[MatchResult]:
        """Score how well a pipeline matches the intent."""
        scores: List[Tuple[float, str, Optional[str]]] = []

        # Pattern matching (highest priority)
        for pattern in config.patterns:
            score, entities = self._match_pattern(pattern, intent.raw_text)
            if score > 0:
                scores.append((score * 1.0, "pattern_match", pattern))

        # Keyword matching
        keyword_score = self._match_keywords(config.keywords, intent)
        if keyword_score > 0:
            scores.append((keyword_score * 0.7, "keyword_match", None))

        # Description similarity
        if config.description:
            desc_score = self._match_description(config.description, intent)
            if desc_score > 0:
                scores.append((desc_score * 0.5, "description_match", None))

        # Intent type matching (if pipeline has stage types that match)
        intent_score = self._match_intent_type(name, intent)
        if intent_score > 0:
            scores.append((intent_score * 0.3, "intent_type_match", None))

        if not scores:
            return None

        # Take best score
        best_score, reasoning, matched_pattern = max(scores, key=lambda x: x[0])

        return MatchResult(
            pipeline_name=name,
            confidence=min(best_score, 1.0),
            matched_pattern=matched_pattern,
            extracted_entities=intent.entities,
            reasoning=reasoning,
        )

    def _match_pattern(
        self,
        pattern: str,
        text: str,
    ) -> Tuple[float, Dict[str, str]]:
        """
        Match a pattern against text.

        Patterns can include placeholders like {date}, {name}.
        """
        # Convert pattern to regex
        # {placeholder} -> named capture group
        regex_pattern = pattern.lower()
        entities: Dict[str, str] = {}

        # Find all placeholders
        placeholders = re.findall(r"\{(\w+)\}", pattern)

        # Replace placeholders with capture groups
        for placeholder in placeholders:
            regex_pattern = regex_pattern.replace(
                f"{{{placeholder}}}",
                f"(?P<{placeholder}>.+?)"
            )

        # Escape special characters (except our capture groups)
        regex_pattern = re.sub(r"([.^$*+?()[\]{}|\\])", r"\\\1", regex_pattern)
        # Restore capture groups
        for placeholder in placeholders:
            regex_pattern = regex_pattern.replace(
                f"\\(\\?P\\<{placeholder}\\>\\.\\+\\?\\)",
                f"(?P<{placeholder}>.+?)"
            )

        try:
            match = re.search(regex_pattern, text.lower())
            if match:
                entities = match.groupdict()
                return 0.95, entities
        except re.error:
            pass

        # Partial match - check if pattern words are in text
        pattern_words = set(re.findall(r"\w+", pattern.lower()))
        pattern_words -= {p.lower() for p in placeholders}
        text_words = set(re.findall(r"\w+", text.lower()))

        if pattern_words and pattern_words.issubset(text_words):
            return 0.7, entities

        overlap = pattern_words & text_words
        if overlap and len(overlap) >= len(pattern_words) * 0.5:
            return 0.5, entities

        return 0.0, entities

    def _match_keywords(self, keywords: List[str], intent: Intent) -> float:
        """Match keywords against intent."""
        if not keywords:
            return 0.0

        text_lower = intent.raw_text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)

        if matches == 0:
            return 0.0

        return matches / len(keywords)

    def _match_description(self, description: str, intent: Intent) -> float:
        """Match description against intent using word overlap."""
        desc_words = set(re.findall(r"\w+", description.lower()))
        text_words = set(re.findall(r"\w+", intent.raw_text.lower()))

        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "to", "for", "of", "in", "on"}
        desc_words -= stop_words
        text_words -= stop_words

        if not desc_words:
            return 0.0

        overlap = desc_words & text_words
        return len(overlap) / len(desc_words)

    def _match_intent_type(self, pipeline_name: str, intent: Intent) -> float:
        """Match based on intent type and pipeline characteristics."""
        pipeline = self._pipelines.get(pipeline_name)
        if not pipeline:
            return 0.0

        # Get stages
        stages = []
        if isinstance(pipeline, dict):
            stages = pipeline.get("stages", [])
        elif hasattr(pipeline, "stages"):
            stages = pipeline.stages or []

        # Check if any stage matches the intent type
        intent_to_components = {
            IntentType.GENERATE: ["generator", "llm", "ai"],
            IntentType.FETCH: ["http_request", "fetch", "api"],
            IntentType.PROCESS: ["json_transform", "transform", "filter"],
            IntentType.VALIDATE: ["schema_validate", "validator"],
            IntentType.SEND: ["http_request", "email", "notify"],
            IntentType.SUMMARIZE: ["generator", "summarizer", "llm"],
            IntentType.ANALYZE: ["generator", "analyzer", "llm"],
        }

        components = intent_to_components.get(intent.type, [])
        if not components:
            return 0.0

        for stage in stages:
            stage_type = ""
            if isinstance(stage, dict):
                stage_type = stage.get("component_type", "") or stage.get("component", "")
            elif hasattr(stage, "component_type"):
                stage_type = stage.component_type or ""

            if any(comp in stage_type.lower() for comp in components):
                return 0.6

        return 0.0

    async def match_with_llm(
        self,
        intent: Intent,
        client: Any,
        threshold: float = 0.5,
        max_results: int = 3,
    ) -> List[MatchResult]:
        """
        Match intent to pipelines using LLM for better accuracy.

        Args:
            intent: Parsed intent
            client: LLM client (Anthropic/OpenAI)
            threshold: Minimum confidence
            max_results: Maximum results

        Returns:
            List of MatchResult
        """
        # First do rule-based matching
        rule_results = self.match(intent, threshold=0.3, max_results=10)

        if not rule_results:
            return []

        # Prepare pipeline summaries for LLM
        pipeline_summaries = []
        for result in rule_results:
            pipeline = self._pipelines.get(result.pipeline_name)
            if pipeline:
                desc = ""
                if isinstance(pipeline, dict):
                    desc = pipeline.get("description", "")
                elif hasattr(pipeline, "description"):
                    desc = pipeline.description or ""
                pipeline_summaries.append(f"- {result.pipeline_name}: {desc}")

        prompt = f"""Given the user's command and available pipelines, rank which pipeline(s) best match.

User command: "{intent.raw_text}"
Extracted intent: {intent.type.value} - {intent.action}

Available pipelines:
{chr(10).join(pipeline_summaries)}

Return a JSON array of matches with confidence scores (0-1):
[{{"name": "pipeline-name", "confidence": 0.9, "reasoning": "why it matches"}}]

Only include pipelines with confidence >= {threshold}. Return empty array if no good match."""

        try:
            response = client.messages.create(
                model="claude-haiku-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result_text = response.content[0].text

            # Extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', result_text)
            if json_match:
                matches = json.loads(json_match.group(0))
                return [
                    MatchResult(
                        pipeline_name=m["name"],
                        confidence=m["confidence"],
                        reasoning=m.get("reasoning", ""),
                    )
                    for m in matches[:max_results]
                    if m["confidence"] >= threshold
                ]
        except Exception as e:
            logger.warning(f"LLM matching failed, using rule-based: {e}")

        # Fall back to rule-based results
        return [r for r in rule_results if r.confidence >= threshold][:max_results]
