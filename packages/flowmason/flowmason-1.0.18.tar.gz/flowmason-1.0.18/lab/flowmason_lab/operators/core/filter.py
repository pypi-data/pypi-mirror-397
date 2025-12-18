"""
Filter Operator - Core FlowMason Component.

Conditionally passes or blocks data based on conditions.
Essential for branching logic in pipelines.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput

logger = logging.getLogger(__name__)


@operator(
    name="filter",
    category="core",
    description="Conditionally filter data based on expressions or conditions",
    icon="filter",
    color="#8B5CF6",
    version="1.1.0",
    author="FlowMason",
    tags=["filter", "condition", "branch", "control-flow", "core"],
)
class FilterOperator:
    """
    Conditionally filter data based on conditions.

    This operator enables:
    - Conditional pipeline branching
    - Data filtering based on values
    - Guard conditions before expensive operations
    - Array filtering
    - Schema-based filtering

    **Important:** In `filter_array` mode, use `item` to reference each element.
    In `pass_fail` mode, use `data` to reference the full dataset.
    """

    class Input(OperatorInput):
        data: Any = Field(
            description="The data to evaluate or filter",
        )
        condition: Optional[str] = Field(
            default=None,
            description=(
                "Python expression to evaluate. "
                "In pass_fail mode: use 'data' variable. "
                "In filter_array mode: use 'item' variable for each element."
            ),
            examples=[
                "data['score'] > 0.8",  # pass_fail mode
                "item.get('status') == 'active'",  # filter_array mode
                "len(data) > 0",  # pass_fail mode
            ],
        )
        field_conditions: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Field-based conditions: {field: expected_value}",
            examples=[{"status": "active", "approved": True}],
        )
        pass_if_missing: bool = Field(
            default=False,
            description="If True, pass data when condition fields are missing",
        )
        filter_mode: str = Field(
            default="pass_fail",
            description="Mode: 'pass_fail' (boolean), 'filter_array' (filter list items)",
        )
        invert: bool = Field(
            default=False,
            description="Invert the condition result",
        )

    class Output(OperatorOutput):
        passed: bool = Field(description="Whether the data passed the filter")
        data: Any = Field(description="Original or filtered data")
        filtered_count: int = Field(
            default=0,
            description="Number of items filtered (for array mode)"
        )
        reason: str = Field(
            default="",
            description="Reason for pass/fail"
        )

    class Config:
        deterministic: bool = True
        timeout_seconds: int = 5

    async def execute(self, input: Input, context) -> Output:
        """Execute the filter operation."""
        data = input.data

        # Array filtering mode
        if input.filter_mode == "filter_array" and isinstance(data, list):
            # Validate condition before processing
            if input.condition:
                self._validate_condition(input.condition, input.filter_mode)
            return self._filter_array(input, data)

        # Standard pass/fail mode
        passed, reason = self._evaluate_condition(input, data)

        if input.invert:
            passed = not passed
            reason = f"(inverted) {reason}"

        return self.Output(
            passed=passed,
            data=data if passed else None,
            filtered_count=0,
            reason=reason,
        )

    def _validate_condition(self, condition: str, mode: str) -> None:
        """
        Validate condition syntax and warn about common mistakes.

        Raises:
            ValueError: If condition uses incorrect syntax for the mode.
        """
        if mode == "filter_array":
            # Detect list comprehension pattern (common mistake)
            if re.search(r'\[.+for.+in\s+data\s+if', condition):
                logger.warning(
                    f"DEPRECATION: List comprehension in filter_array mode is not supported. "
                    f"Condition: '{condition}'"
                )
                raise ValueError(
                    f"Invalid condition for filter_array mode: '{condition}'. "
                    f"Use per-item syntax like 'item.get(\"status\") == \"active\"' "
                    f"instead of list comprehension."
                )

            # Detect 'data' variable usage (should use 'item')
            if re.search(r'\bdata\b', condition):
                logger.warning(
                    f"DEPRECATION: Using 'data' variable in filter_array mode. "
                    f"Use 'item' instead. Condition: '{condition}'"
                )
                raise ValueError(
                    f"Invalid condition for filter_array mode: '{condition}'. "
                    f"Use 'item' to reference each element (e.g., item.get('field') == 'value'). "
                    f"'data' is only available in pass_fail mode for full dataset evaluation."
                )

    def _filter_array(self, input: Input, data: List[Any]) -> "FilterOperator.Output":
        """Filter array items based on conditions."""
        passed_items = []
        filtered_count = 0

        for item in data:
            item_passed, reason = self._evaluate_item_condition(input, item)
            if input.invert:
                item_passed = not item_passed

            if item_passed:
                passed_items.append(item)
            else:
                filtered_count += 1

        return self.Output(
            passed=len(passed_items) > 0,
            data=passed_items,
            filtered_count=filtered_count,
            reason=f"Filtered {filtered_count} items, {len(passed_items)} passed",
        )

    def _evaluate_item_condition(self, input: Input, item: Any) -> tuple[bool, str]:
        """
        Evaluate condition against a single item (for filter_array mode).

        Uses 'item' variable, consistent with foreach operator.

        Args:
            input: Operator input configuration
            item: Single item from the array

        Returns:
            Tuple of (passed, reason)
        """
        # If expression provided, evaluate it
        if input.condition:
            try:
                # Safe evaluation with limited scope - uses 'item' variable
                result = eval(
                    input.condition,
                    {"__builtins__": {}},
                    {
                        "item": item,
                        "len": len,
                        "str": str,
                        "int": int,
                        "float": float,
                        "bool": bool,
                        "isinstance": isinstance,
                        "type": type,
                    }
                )
                return bool(result), f"Expression evaluated to {result}"
            except NameError as e:
                error_msg = f"Filter condition error: {e}"
                if "'data'" in str(e):
                    error_msg += (
                        ". Hint: In filter_array mode, use 'item' to reference each element "
                        "(e.g., item.get('field') == 'value')"
                    )
                if input.pass_if_missing:
                    return True, f"Expression error (pass_if_missing): {error_msg}"
                return False, error_msg
            except Exception as e:
                if input.pass_if_missing:
                    return True, f"Expression error (pass_if_missing): {e}"
                return False, f"Expression error: {e}"

        # If field conditions provided, check each
        if input.field_conditions:
            if not isinstance(item, dict):
                return False, "Field conditions require dict data"

            for field, expected in input.field_conditions.items():
                if field not in item:
                    if input.pass_if_missing:
                        continue
                    return False, f"Missing field: {field}"

                actual = item[field]
                if actual != expected:
                    return False, f"Field '{field}': expected {expected}, got {actual}"

            return True, "All field conditions matched"

        # No conditions specified, pass everything
        return True, "No conditions specified"

    def _evaluate_condition(self, input: Input, data: Any) -> tuple[bool, str]:
        """
        Evaluate conditions against data (for pass_fail mode).

        Uses 'data' variable for full dataset evaluation.

        Returns:
            Tuple of (passed, reason)
        """
        # If expression provided, evaluate it
        if input.condition:
            try:
                # Safe evaluation with limited scope
                result = eval(
                    input.condition,
                    {"__builtins__": {}},
                    {
                        "data": data,
                        "len": len,
                        "str": str,
                        "int": int,
                        "float": float,
                        "bool": bool,
                        "isinstance": isinstance,
                        "type": type,
                    }
                )
                return bool(result), f"Expression '{input.condition}' = {result}"
            except Exception as e:
                if input.pass_if_missing:
                    return True, f"Expression error (pass_if_missing): {e}"
                return False, f"Expression error: {e}"

        # If field conditions provided, check each
        if input.field_conditions:
            if not isinstance(data, dict):
                return False, "Field conditions require dict data"

            for field, expected in input.field_conditions.items():
                if field not in data:
                    if input.pass_if_missing:
                        continue
                    return False, f"Missing field: {field}"

                actual = data[field]
                if actual != expected:
                    return False, f"Field '{field}': expected {expected}, got {actual}"

            return True, "All field conditions matched"

        # No conditions specified, pass everything
        return True, "No conditions specified"
