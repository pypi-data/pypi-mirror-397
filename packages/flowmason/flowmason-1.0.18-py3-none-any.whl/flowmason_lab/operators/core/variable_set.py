"""
Variable Set Operator - Core FlowMason Component.

Sets and manages context variables within pipeline execution.
Essential for state management and data passing between steps.
"""

from typing import Any, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput


@operator(
    name="variable_set",
    category="core",
    description="Set and manage context variables for pipeline state",
    icon="variable",
    color="#6366F1",
    version="1.0.0",
    author="FlowMason",
    tags=["variable", "state", "context", "data", "core"],
)
class VariableSetOperator:
    """
    Set and manage context variables.

    This operator enables:
    - Storing intermediate results
    - Passing data between pipeline branches
    - Managing pipeline state
    - Extracting values for later use
    - Conditional variable assignment
    """

    class Input(OperatorInput):
        name: str = Field(
            description="Variable name to set",
            pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
            examples=["result", "user_data", "intermediate_value"],
        )
        value: Any = Field(
            description="Value to assign to the variable",
        )
        scope: str = Field(
            default="pipeline",
            description="Variable scope: 'pipeline', 'step', or 'global'",
        )
        overwrite: bool = Field(
            default=True,
            description="Whether to overwrite if variable exists",
        )
        extract_path: Optional[str] = Field(
            default=None,
            description="Dot-path to extract from value (e.g., 'data.result.content')",
            examples=["response.content", "items[0].id"],
        )

    class Output(OperatorOutput):
        name: str = Field(description="The variable name that was set")
        value: Any = Field(description="The value that was assigned")
        previous_value: Any = Field(
            default=None,
            description="Previous value if overwritten"
        )
        was_set: bool = Field(
            default=True,
            description="Whether the variable was actually set"
        )

    class Config:
        deterministic: bool = True
        timeout_seconds: int = 5

    async def execute(self, input: Input, context) -> Output:
        """Execute variable assignment."""
        value = input.value

        # Extract nested value if path provided
        if input.extract_path:
            value = self._extract_path(value, input.extract_path)

        # Get previous value if exists
        previous_value = None
        variables = getattr(context, "variables", {})

        if input.name in variables:
            previous_value = variables[input.name]
            if not input.overwrite:
                return self.Output(
                    name=input.name,
                    value=previous_value,
                    previous_value=previous_value,
                    was_set=False,
                )

        # Set the variable (context management handled by executor)
        # This output will be used by the executor to update context
        return self.Output(
            name=input.name,
            value=value,
            previous_value=previous_value,
            was_set=True,
        )

    def _extract_path(self, data: Any, path: str) -> Any:
        """
        Extract a value from nested data using dot notation.

        Args:
            data: The data structure to extract from
            path: Dot-separated path (e.g., "data.items[0].name")

        Returns:
            The extracted value, or None if not found
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
