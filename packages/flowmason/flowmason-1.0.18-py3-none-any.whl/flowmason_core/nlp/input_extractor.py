"""
Input Extractor for FlowMason.

Extracts pipeline input values from natural language commands.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of extracting inputs from natural language."""
    inputs: Dict[str, Any] = field(default_factory=dict)
    missing_required: List[str] = field(default_factory=list)
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)


@dataclass
class InputSchema:
    """Schema for a pipeline input."""
    name: str
    type: str  # string, number, boolean, date, array, object
    required: bool = False
    default: Any = None
    description: str = ""
    enum: Optional[List[Any]] = None
    patterns: List[str] = field(default_factory=list)  # NL patterns to extract this input


class InputExtractor:
    """
    Extracts pipeline inputs from natural language.

    Uses a combination of:
    - Schema-based extraction (matching input names/patterns)
    - Entity recognition (dates, numbers, emails, etc.)
    - Context inference (defaults, implied values)
    """

    # Date expressions to parse
    DATE_EXPRESSIONS = {
        "today": lambda: datetime.now().strftime("%Y-%m-%d"),
        "yesterday": lambda: (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "tomorrow": lambda: (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "last week": lambda: (datetime.now() - timedelta(weeks=1)).strftime("%Y-%m-%d"),
        "this week": lambda: datetime.now().strftime("%Y-%m-%d"),
        "last month": lambda: (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d"),
        "this month": lambda: datetime.now().replace(day=1).strftime("%Y-%m-%d"),
    }

    # Patterns for common input types
    TYPE_PATTERNS = {
        "email": r"[\w\.-]+@[\w\.-]+\.\w+",
        "url": r"https?://[\w\.-/]+",
        "date": r"\d{4}-\d{2}-\d{2}",
        "number": r"\b\d+(?:\.\d+)?\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "filepath": r"[/\\]?(?:[\w\.-]+[/\\])+[\w\.-]+",
    }

    def __init__(self, input_schemas: Optional[List[InputSchema]] = None):
        """
        Initialize the extractor.

        Args:
            input_schemas: List of input schemas for the target pipeline
        """
        self._schemas = {s.name: s for s in (input_schemas or [])}

    def set_schemas(self, schemas: List[InputSchema]) -> None:
        """Set input schemas for extraction."""
        self._schemas = {s.name: s for s in schemas}

    def set_schemas_from_pipeline(self, pipeline: Any) -> None:
        """Extract input schemas from pipeline configuration."""
        input_schema = {}
        if isinstance(pipeline, dict):
            input_schema = pipeline.get("input_schema", {})
        elif hasattr(pipeline, "input_schema"):
            input_schema = pipeline.input_schema or {}

        schemas = []
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])

        for name, prop in properties.items():
            schemas.append(InputSchema(
                name=name,
                type=prop.get("type", "string"),
                required=name in required,
                default=prop.get("default"),
                description=prop.get("description", ""),
                enum=prop.get("enum"),
                patterns=prop.get("nl_patterns", []),
            ))

        self._schemas = {s.name: s for s in schemas}

    def extract(
        self,
        text: str,
        entities: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """
        Extract inputs from natural language text.

        Args:
            text: Natural language command
            entities: Pre-extracted entities from intent parser
            context: Additional context (previous values, defaults)

        Returns:
            ExtractionResult with extracted inputs
        """
        inputs: Dict[str, Any] = {}
        missing_required: List[str] = []
        warnings: List[str] = []
        confidence_scores: List[float] = []

        # Merge pre-extracted entities
        if entities:
            for key, value in entities.items():
                inputs[key] = value
                confidence_scores.append(0.8)

        # Extract based on schemas
        for name, schema in self._schemas.items():
            if name in inputs:
                continue

            value, conf = self._extract_for_schema(text, schema)
            if value is not None:
                inputs[name] = value
                confidence_scores.append(conf)
            elif schema.default is not None:
                inputs[name] = schema.default
                confidence_scores.append(0.5)
            elif schema.required:
                missing_required.append(name)

        # Apply context defaults
        if context:
            for name, value in context.items():
                if name not in inputs and name in self._schemas:
                    inputs[name] = value
                    confidence_scores.append(0.6)

        # Extract any remaining typed values
        self._extract_typed_values(text, inputs, confidence_scores)

        # Calculate overall confidence
        confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return ExtractionResult(
            inputs=inputs,
            missing_required=missing_required,
            confidence=confidence,
            warnings=warnings,
        )

    def _extract_for_schema(
        self,
        text: str,
        schema: InputSchema,
    ) -> Tuple[Any, float]:
        """Extract value for a specific schema."""
        text_lower = text.lower()

        # Try custom patterns first
        for pattern in schema.patterns:
            value, conf = self._match_pattern(pattern, text)
            if value is not None:
                return self._coerce_type(value, schema.type), conf

        # Try to find by name mention
        name_pattern = rf"(?:{schema.name}|{schema.name.replace('_', ' ')})\s*(?:is|=|:)?\s*['\"]?([^'\"]+)['\"]?"
        match = re.search(name_pattern, text_lower)
        if match:
            return self._coerce_type(match.group(1).strip(), schema.type), 0.85

        # Try enum matching
        if schema.enum:
            for enum_val in schema.enum:
                if str(enum_val).lower() in text_lower:
                    return enum_val, 0.8

        # Try type-based extraction
        if schema.type == "date":
            value = self._extract_date(text)
            if value:
                return value, 0.75

        if schema.type in ("number", "integer"):
            value = self._extract_number(text, schema.name)
            if value is not None:
                return value, 0.7

        if schema.type == "boolean":
            value = self._extract_boolean(text, schema.name)
            if value is not None:
                return value, 0.7

        # Try description-based extraction
        if schema.description:
            value = self._extract_by_description(text, schema.description, schema.type)
            if value is not None:
                return value, 0.6

        return None, 0.0

    def _match_pattern(self, pattern: str, text: str) -> Tuple[Any, float]:
        """Match a pattern and extract value."""
        # Pattern format: "for {value}" or "date: {value}"
        placeholders = re.findall(r"\{(\w+)\}", pattern)
        if not placeholders:
            return None, 0.0

        # Convert to regex
        regex = pattern.lower()
        for ph in placeholders:
            regex = regex.replace(f"{{{ph}}}", f"(?P<{ph}>.+?)")

        try:
            match = re.search(regex, text.lower())
            if match:
                # Return first captured group
                groups = match.groupdict()
                if groups:
                    return list(groups.values())[0].strip(), 0.9
        except re.error:
            pass

        return None, 0.0

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text."""
        text_lower = text.lower()

        # Check date expressions
        for expr, date_fn in self.DATE_EXPRESSIONS.items():
            if expr in text_lower:
                return date_fn()

        # Check for relative days
        match = re.search(r"last\s+(\d+)\s+days?", text_lower)
        if match:
            days = int(match.group(1))
            return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Check for explicit date
        match = re.search(r"\d{4}-\d{2}-\d{2}", text)
        if match:
            return match.group(0)

        return None

    def _extract_number(self, text: str, name: str) -> Optional[float]:
        """Extract number associated with a name."""
        # Try to find number near the name
        name_pattern = rf"(?:{name}|{name.replace('_', ' ')})\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)"
        match = re.search(name_pattern, text.lower())
        if match:
            return float(match.group(1))

        # Extract first number if there's only one
        numbers = re.findall(r"\b(\d+(?:\.\d+)?)\b", text)
        if len(numbers) == 1:
            return float(numbers[0])

        return None

    def _extract_boolean(self, text: str, name: str) -> Optional[bool]:
        """Extract boolean value."""
        text_lower = text.lower()

        # Check for explicit true/false near name
        if re.search(rf"{name}\s*(?:is|=|:)?\s*(?:true|yes|on|enabled)", text_lower):
            return True
        if re.search(rf"{name}\s*(?:is|=|:)?\s*(?:false|no|off|disabled)", text_lower):
            return False

        # Check for negation
        if re.search(rf"(?:no|without|disable|don't)\s+{name}", text_lower):
            return False
        if re.search(rf"(?:with|enable|do)\s+{name}", text_lower):
            return True

        return None

    def _extract_by_description(
        self,
        text: str,
        description: str,
        expected_type: str,
    ) -> Any:
        """Try to extract based on description hints."""
        text_lower = text.lower()
        desc_lower = description.lower()

        # Extract keywords from description
        keywords = re.findall(r"\b\w+\b", desc_lower)
        keywords = [k for k in keywords if len(k) > 3]

        for keyword in keywords:
            # Look for value after keyword
            pattern = rf"{keyword}\s*(?:is|=|:)?\s*['\"]?([^'\"]+)['\"]?"
            match = re.search(pattern, text_lower)
            if match:
                return self._coerce_type(match.group(1).strip(), expected_type)

        return None

    def _extract_typed_values(
        self,
        text: str,
        inputs: Dict[str, Any],
        confidence_scores: List[float],
    ) -> None:
        """Extract typed values not yet captured."""
        # Extract emails
        if "email" not in inputs:
            emails = re.findall(self.TYPE_PATTERNS["email"], text)
            if emails:
                inputs["email"] = emails[0] if len(emails) == 1 else emails
                confidence_scores.append(0.9)

        # Extract URLs
        if "url" not in inputs:
            urls = re.findall(self.TYPE_PATTERNS["url"], text)
            if urls:
                inputs["url"] = urls[0] if len(urls) == 1 else urls
                confidence_scores.append(0.9)

    def _coerce_type(self, value: Any, target_type: str) -> Any:
        """Coerce value to target type."""
        if value is None:
            return None

        try:
            if target_type == "string":
                return str(value)
            elif target_type in ("number", "integer"):
                return float(value) if "." in str(value) else int(value)
            elif target_type == "boolean":
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ("true", "yes", "on", "1")
            elif target_type == "array":
                if isinstance(value, list):
                    return value
                return [v.strip() for v in str(value).split(",")]
            elif target_type == "date":
                # Try to parse as date
                if isinstance(value, str):
                    return value  # Already string format
                return str(value)
        except (ValueError, TypeError):
            pass

        return value

    async def extract_with_llm(
        self,
        text: str,
        client: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """
        Extract inputs using LLM for better accuracy.

        Args:
            text: Natural language command
            client: LLM client
            context: Additional context

        Returns:
            ExtractionResult with extracted inputs
        """
        if not self._schemas:
            return self.extract(text, context=context)

        # Build schema description for LLM
        schema_desc = []
        for name, schema in self._schemas.items():
            req = "(required)" if schema.required else "(optional)"
            default = f" [default: {schema.default}]" if schema.default else ""
            schema_desc.append(f"- {name}: {schema.type} {req}{default} - {schema.description}")

        prompt = f"""Extract input values from this natural language command.

Command: "{text}"

Expected inputs:
{chr(10).join(schema_desc)}

Return a JSON object with the extracted values. Use null for missing optional values.
For dates, use YYYY-MM-DD format. Convert relative dates (today, yesterday, last week) to actual dates.

JSON output:"""

        try:
            response = client.messages.create(
                model="claude-haiku-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result_text = response.content[0].text

            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                inputs = json.loads(json_match.group(0))

                # Check for missing required
                missing = []
                for name, schema in self._schemas.items():
                    if schema.required and inputs.get(name) is None:
                        missing.append(name)

                return ExtractionResult(
                    inputs={k: v for k, v in inputs.items() if v is not None},
                    missing_required=missing,
                    confidence=0.95,
                )
        except Exception as e:
            logger.warning(f"LLM extraction failed, using rule-based: {e}")

        # Fall back to rule-based extraction
        return self.extract(text, context=context)
