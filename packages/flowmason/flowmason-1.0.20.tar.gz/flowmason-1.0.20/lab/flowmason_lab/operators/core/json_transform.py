"""
JSON Transform Operator - Core FlowMason Component.

Transforms JSON data using JMESPath expressions or simple mappings.
Essential for data reshaping between pipeline stages.
"""

import json
from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput


@operator(
    name="json_transform",
    category="core",
    description="Transform JSON data using mappings or JMESPath expressions",
    icon="code",
    color="#F59E0B",
    version="1.0.0",
    author="FlowMason",
    tags=["json", "transform", "data", "mapping", "core"],
)
class JsonTransformOperator:
    """
    Transform JSON data structures.

    This operator enables:
    - Reshaping data between stages
    - Extracting nested values
    - Combining fields
    - Filtering arrays
    - Type conversions

    Supports:
    - Simple field mappings: {"output_field": "input.nested.field"}
    - JMESPath expressions for complex queries
    - Template strings with {{field}} syntax
    """

    class Input(OperatorInput):
        data: Any = Field(
            description="Input data to transform (JSON object or array)",
            examples=[
                {"user": {"name": "John", "email": "john@example.com"}},
                [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
            ],
        )
        mapping: Optional[Dict[str, str]] = Field(
            default=None,
            description="Field mapping (output_field -> input path or expression)",
            examples=[{
                "name": "user.full_name",
                "email": "user.contact.email",
                "id": "user.id",
            }],
        )
        jmespath_expression: Optional[str] = Field(
            default=None,
            description="JMESPath expression for complex transformations",
            examples=[
                "users[?age > `18`].name",
                "{name: user.name, emails: user.contacts[*].email}",
            ],
        )
        defaults: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Default values for missing fields",
        )
        flatten: bool = Field(
            default=False,
            description="Flatten nested structures to single level",
        )
        exclude_fields: Optional[List[str]] = Field(
            default=None,
            description="Fields to exclude from output",
        )
        parse_json_strings: bool = Field(
            default=True,
            description="Automatically parse JSON strings before transformation",
        )

    class Output(OperatorOutput):
        result: Any = Field(description="Transformed data")
        fields_mapped: int = Field(
            default=0,
            description="Number of fields successfully mapped"
        )
        fields_missing: List[str] = Field(
            default_factory=list,
            description="Fields that were missing (used defaults)"
        )

    class Config:
        deterministic: bool = True
        timeout_seconds: int = 10

    async def execute(self, input: Input, context) -> Output:
        """Execute the JSON transformation."""
        data = input.data
        fields_missing = []

        # Auto-parse JSON strings if enabled
        if input.parse_json_strings and isinstance(data, str):
            data = self._try_parse_json(data)

        # If JMESPath expression provided, use that
        if input.jmespath_expression:
            try:
                import jmespath
                result = jmespath.search(input.jmespath_expression, data)
                return self.Output(
                    result=result,
                    fields_mapped=1,
                    fields_missing=[],
                )
            except ImportError:
                raise RuntimeError(
                    "jmespath is required for JMESPath expressions. "
                    "Install with: pip install jmespath"
                )
            except Exception as e:
                raise ValueError(f"JMESPath expression error: {e}")

        # Apply field mapping
        if input.mapping:
            result = {}
            for output_field, input_path in input.mapping.items():
                value = self._get_nested_value(data, input_path)
                if value is None and input.defaults and output_field in input.defaults:
                    value = input.defaults[output_field]
                    fields_missing.append(output_field)
                result[output_field] = value

            # Exclude fields if specified
            if input.exclude_fields:
                for field in input.exclude_fields:
                    result.pop(field, None)

            return self.Output(
                result=result,
                fields_mapped=len(input.mapping),
                fields_missing=fields_missing,
            )

        # If flatten requested, flatten the structure
        if input.flatten:
            result = self._flatten_dict(data)
            return self.Output(
                result=result,
                fields_mapped=len(result) if isinstance(result, dict) else 0,
                fields_missing=[],
            )

        # No transformation specified, return data as-is
        return self.Output(
            result=data,
            fields_mapped=0,
            fields_missing=[],
        )

    def _get_nested_value(self, data: Any, path: str) -> Any:
        """
        Get a nested value from data using dot notation.

        Args:
            data: The data structure to query
            path: Dot-separated path (e.g., "user.name" or "items[0].id")

        Returns:
            The value at the path, or None if not found
        """
        if data is None:
            return None

        parts = path.replace("[", ".[").split(".")
        current = data

        for part in parts:
            if not part:
                continue

            # Handle array index notation [0], [1], etc.
            if part.startswith("[") and part.endswith("]"):
                try:
                    index = int(part[1:-1])
                    if isinstance(current, (list, tuple)) and len(current) > index:
                        current = current[index]
                    else:
                        return None
                except (ValueError, TypeError):
                    return None
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                return None

            if current is None:
                return None

        return current

    def _flatten_dict(
        self,
        data: Any,
        parent_key: str = "",
        separator: str = ".",
    ) -> Dict[str, Any]:
        """
        Flatten a nested dictionary to single level.

        Args:
            data: The nested data structure
            parent_key: Key prefix for recursion
            separator: Separator between nested keys

        Returns:
            Flattened dictionary
        """
        items = {}

        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                if isinstance(value, dict):
                    items.update(self._flatten_dict(value, new_key, separator))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            items.update(
                                self._flatten_dict(item, f"{new_key}[{i}]", separator)
                            )
                        else:
                            items[f"{new_key}[{i}]"] = item
                else:
                    items[new_key] = value
        else:
            items[parent_key or "value"] = data

        return items

    def _try_parse_json(self, data: str) -> Any:
        """
        Try to parse a string as JSON.

        Handles common cases:
        - Pure JSON strings
        - JSON with markdown code blocks (```json ... ```)
        - JSON embedded in text (extracts first {...} or [...])
        - Returns original string if not valid JSON
        """
        if not data or not isinstance(data, str):
            return data

        text = data.strip()

        # Handle markdown code blocks
        if "```" in text:
            # Find content between ``` markers
            import re
            code_block = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
            if code_block:
                text = code_block.group(1).strip()

        # Try to parse as JSON directly
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            pass

        # Try to extract JSON object or array from text
        # Find first { or [ and match to closing } or ]
        for start_char, end_char in [('{', '}'), ('[', ']')]:
            start_idx = text.find(start_char)
            if start_idx != -1:
                # Find matching closing bracket
                depth = 0
                in_string = False
                escape_next = False
                for i, char in enumerate(text[start_idx:], start_idx):
                    if escape_next:
                        escape_next = False
                        continue
                    if char == '\\' and in_string:
                        escape_next = True
                        continue
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    if in_string:
                        continue
                    if char == start_char:
                        depth += 1
                    elif char == end_char:
                        depth -= 1
                        if depth == 0:
                            # Found matching bracket
                            json_str = text[start_idx:i + 1]
                            try:
                                return json.loads(json_str)
                            except (json.JSONDecodeError, TypeError):
                                break

        # Could not parse, return original
        return data
