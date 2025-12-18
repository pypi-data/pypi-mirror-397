"""
Intent Parser for FlowMason.

Parses natural language commands to extract user intent.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Types of user intents."""
    RUN = "run"  # Execute a pipeline
    GENERATE = "generate"  # Create content/output
    PROCESS = "process"  # Transform data
    ANALYZE = "analyze"  # Analyze data
    SEND = "send"  # Send/deliver something
    FETCH = "fetch"  # Get data from source
    SUMMARIZE = "summarize"  # Create summary
    VALIDATE = "validate"  # Validate data
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Parsed intent from natural language."""
    type: IntentType
    action: str  # The primary action verb
    target: Optional[str] = None  # What the action applies to
    modifiers: Dict[str, str] = field(default_factory=dict)  # Additional modifiers
    entities: Dict[str, Any] = field(default_factory=dict)  # Extracted entities
    confidence: float = 0.0
    raw_text: str = ""


class IntentParser:
    """
    Parses natural language commands to extract intent.

    Uses a combination of keyword matching and pattern analysis
    to determine what the user wants to do.
    """

    # Action verb mappings to intent types
    ACTION_MAPPINGS = {
        IntentType.RUN: ["run", "execute", "start", "trigger", "launch"],
        IntentType.GENERATE: ["generate", "create", "make", "produce", "build"],
        IntentType.PROCESS: ["process", "transform", "convert", "handle"],
        IntentType.ANALYZE: ["analyze", "analyse", "examine", "inspect", "review"],
        IntentType.SEND: ["send", "deliver", "email", "post", "notify"],
        IntentType.FETCH: ["fetch", "get", "retrieve", "pull", "download"],
        IntentType.SUMMARIZE: ["summarize", "summarise", "sum up", "recap"],
        IntentType.VALIDATE: ["validate", "check", "verify", "test"],
    }

    # Common time expressions
    TIME_PATTERNS = {
        r"today": "today",
        r"yesterday": "yesterday",
        r"last\s+week": "last_week",
        r"this\s+week": "this_week",
        r"last\s+month": "last_month",
        r"this\s+month": "this_month",
        r"last\s+(\d+)\s+days?": "last_n_days",
        r"(\d{4}-\d{2}-\d{2})": "date",
        r"from\s+(\w+)\s+to\s+(\w+)": "date_range",
    }

    # Entity patterns
    ENTITY_PATTERNS = {
        "email": r"[\w\.-]+@[\w\.-]+\.\w+",
        "url": r"https?://[\w\.-/]+",
        "number": r"\b\d+(?:\.\d+)?\b",
        "filepath": r"[/\\]?(?:[\w\.-]+[/\\])+[\w\.-]+",
    }

    def parse(self, text: str) -> Intent:
        """
        Parse a natural language command into an intent.

        Args:
            text: Natural language command

        Returns:
            Parsed Intent object
        """
        # Normalize text
        normalized = text.lower().strip()

        # Extract action and intent type
        intent_type, action, confidence = self._extract_action(normalized)

        # Extract target (what the action applies to)
        target = self._extract_target(normalized, action)

        # Extract time modifiers
        modifiers = self._extract_modifiers(normalized)

        # Extract entities
        entities = self._extract_entities(text)  # Use original case

        return Intent(
            type=intent_type,
            action=action,
            target=target,
            modifiers=modifiers,
            entities=entities,
            confidence=confidence,
            raw_text=text,
        )

    def _extract_action(self, text: str) -> Tuple[IntentType, str, float]:
        """Extract the primary action verb and map to intent type."""
        words = text.split()

        # Find the first action verb
        for word in words:
            for intent_type, verbs in self.ACTION_MAPPINGS.items():
                if word in verbs:
                    return intent_type, word, 0.9

        # Check for phrase matches
        for intent_type, verbs in self.ACTION_MAPPINGS.items():
            for verb in verbs:
                if verb in text:
                    return intent_type, verb, 0.8

        # Default - try to use first verb-like word
        if words:
            return IntentType.UNKNOWN, words[0], 0.3

        return IntentType.UNKNOWN, "", 0.0

    def _extract_target(self, text: str, action: str) -> Optional[str]:
        """Extract what the action applies to."""
        # Remove the action word
        remaining = text.replace(action, "", 1).strip()

        # Common patterns: "the X", "a X", "X from/for Y"
        patterns = [
            r"(?:the|a|an)\s+(\w+(?:\s+\w+)?)",  # the report, a summary
            r"(\w+(?:\s+\w+)?)\s+(?:from|for|to)",  # data from, report for
            r"^(\w+(?:\s+\w+)?)",  # first noun phrase
        ]

        for pattern in patterns:
            match = re.search(pattern, remaining)
            if match:
                return match.group(1).strip()

        return None

    def _extract_modifiers(self, text: str) -> Dict[str, str]:
        """Extract time and other modifiers."""
        modifiers = {}

        # Time expressions
        for pattern, name in self.TIME_PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if match.groups():
                    modifiers["time"] = match.group(0)
                    modifiers["time_type"] = name
                    if len(match.groups()) > 1:
                        modifiers["time_start"] = match.group(1)
                        modifiers["time_end"] = match.group(2)
                else:
                    modifiers["time"] = name

        # Format modifiers
        format_match = re.search(r"(?:in|as|to)\s+(json|csv|pdf|excel|html)", text)
        if format_match:
            modifiers["format"] = format_match.group(1)

        # Recipient modifiers
        to_match = re.search(r"to\s+(\w+(?:\s+\w+)?)", text)
        if to_match and "time" not in to_match.group(0):
            modifiers["recipient"] = to_match.group(1)

        return modifiers

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text."""
        entities: Dict[str, Any] = {}

        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                if len(matches) == 1:
                    entities[entity_type] = matches[0]
                else:
                    entities[entity_type] = matches

        return entities

    def parse_with_llm(self, text: str, client: Any) -> Intent:
        """
        Parse intent using an LLM for better understanding.

        This provides more accurate parsing for complex commands.
        """
        prompt = f"""Parse this natural language command and extract:
1. Intent type (run, generate, process, analyze, send, fetch, summarize, validate)
2. Primary action verb
3. Target (what the action applies to)
4. Time modifiers (today, yesterday, last week, etc.)
5. Other entities (emails, URLs, numbers, file paths)

Command: "{text}"

Return as JSON:
{{
  "intent_type": "...",
  "action": "...",
  "target": "...",
  "modifiers": {{}},
  "entities": {{}}
}}"""

        try:
            response = client.messages.create(
                model="claude-haiku-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result = json.loads(response.content[0].text)

            return Intent(
                type=IntentType(result.get("intent_type", "unknown")),
                action=result.get("action", ""),
                target=result.get("target"),
                modifiers=result.get("modifiers", {}),
                entities=result.get("entities", {}),
                confidence=0.95,
                raw_text=text,
            )
        except Exception as e:
            logger.warning(f"LLM parsing failed, falling back to rule-based: {e}")
            return self.parse(text)
