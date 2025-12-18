"""
Return Control Flow Component.

Enables early exit from pipeline execution with a return value.
This is the FlowMason equivalent of return statements in code.
"""

from typing import Any, List, Optional

from flowmason_core.core.decorators import control_flow
from flowmason_core.core.types import (
    ControlFlowDirective,
    ControlFlowInput,
    ControlFlowOutput,
    ControlFlowType,
    Field,
)


@control_flow(
    name="return",
    description="Exit pipeline early with a return value",
    control_flow_type="return",
    icon="corner-down-left",
    color="#6366F1",  # Indigo
    version="1.0.0",
    author="FlowMason",
    tags=["return", "exit", "early", "terminate", "control-flow"],
)
class ReturnComponent:
    """
    Early exit from pipeline execution.

    This component terminates pipeline execution and returns
    a specified value. Useful for:
    - Short-circuit evaluation
    - Error handling without exceptions
    - Guard clauses
    - Conditional early termination

    Example Pipeline Config:
        stages:
          - id: validate_input
            type: processor
            input_mapping:
              data: "{{input.data}}"

          - id: early_exit_if_invalid
            type: return
            depends_on: [validate_input]
            input_mapping:
              condition: "{{upstream.validate_input.is_valid == false}}"
              return_value:
                success: false
                error: "{{upstream.validate_input.error_message}}"
              message: "Validation failed, returning early"

          - id: process_data
            type: processor
            depends_on: [early_exit_if_invalid]
            # This stage only runs if early_exit_if_invalid doesn't return

    Transpiles to:
        validation_result = validate_input(data)
        if not validation_result.is_valid:
            return {"success": False, "error": validation_result.error_message}
        process_data(...)
    """

    class Input(ControlFlowInput):
        condition: bool = Field(
            default=True,
            description="Whether to execute the return (always returns if True)",
        )
        condition_expression: Optional[str] = Field(
            default=None,
            description="Optional expression to evaluate (overrides condition)",
            examples=["{{upstream.check.passed}} == false", "len({{input.items}}) == 0"],
        )
        return_value: Any = Field(
            default=None,
            description="Value to return from the pipeline",
        )
        message: Optional[str] = Field(
            default=None,
            description="Optional message explaining the early return",
        )
        status: str = Field(
            default="completed",
            description="Pipeline status on return: 'completed', 'cancelled', or 'failed'",
        )

    class Output(ControlFlowOutput):
        should_return: bool = Field(
            description="Whether the return was triggered"
        )
        return_value: Any = Field(
            default=None,
            description="The value to return from pipeline"
        )
        message: Optional[str] = Field(
            default=None,
            description="Message explaining the return"
        )
        status: str = Field(
            description="Pipeline status"
        )
        remaining_stages: List[str] = Field(
            default_factory=list,
            description="Stages that will be skipped"
        )
        directive: ControlFlowDirective = Field(
            description="Execution directive for the executor"
        )

    class Config:
        timeout_seconds: int = 5  # Returns should be instant

    async def execute(self, input: Input, context) -> Output:
        """
        Evaluate return condition and create directive.

        If the condition is true, creates a directive that stops
        pipeline execution and returns the specified value.
        """
        # Evaluate condition
        should_return = input.condition

        if input.condition_expression:
            # Expression takes precedence
            should_return = self._evaluate_expression(
                input.condition_expression, context
            )

        if should_return:
            # Create directive to stop execution
            directive = ControlFlowDirective(
                directive_type=ControlFlowType.RETURN,
                execute_stages=[],  # No more stages
                skip_stages=[],  # Will be populated by executor with remaining stages
                continue_execution=False,  # Stop pipeline
                metadata={
                    "return_value": input.return_value,
                    "message": input.message,
                    "status": input.status,
                    "triggered": True,
                },
            )

            return self.Output(
                should_return=True,
                return_value=input.return_value,
                message=input.message,
                status=input.status,
                remaining_stages=[],  # Executor fills this
                directive=directive,
            )
        else:
            # Continue execution normally
            directive = ControlFlowDirective(
                directive_type=ControlFlowType.RETURN,
                execute_stages=[],
                skip_stages=[],
                continue_execution=True,  # Continue pipeline
                metadata={
                    "return_value": None,
                    "message": None,
                    "status": "running",
                    "triggered": False,
                },
            )

            return self.Output(
                should_return=False,
                return_value=None,
                message=None,
                status="running",
                remaining_stages=[],
                directive=directive,
            )

    def _evaluate_expression(self, expression: str, context) -> bool:
        """
        Evaluate a condition expression.

        Args:
            expression: Python expression to evaluate
            context: Execution context with variables

        Returns:
            Boolean result of expression
        """
        try:
            # Build evaluation context
            eval_context = {
                "__builtins__": {},
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "True": True,
                "False": False,
                "None": None,
            }

            # Add context variables if available
            if hasattr(context, 'variables'):
                eval_context.update(context.variables)

            result = eval(expression, eval_context)
            return bool(result)
        except Exception:
            # On error, don't return (safe default)
            return False


class GuardClause:
    """
    Helper for creating guard clause patterns.

    Guard clauses are early returns that handle edge cases
    at the start of a pipeline, keeping the main logic clean.

    Usage in pipeline config:
        stages:
          # Guard clause 1: Check input exists
          - id: guard_empty_input
            type: return
            input_mapping:
              condition: "{{len(input.items) == 0}}"
              return_value: {"items": [], "message": "No items to process"}

          # Guard clause 2: Check authorization
          - id: guard_unauthorized
            type: return
            depends_on: [guard_empty_input]
            input_mapping:
              condition: "{{input.user.role != 'admin'}}"
              return_value: {"error": "Unauthorized"}
              status: "failed"

          # Main logic (only runs if guards pass)
          - id: process_items
            type: processor
            depends_on: [guard_unauthorized]
    """

    @staticmethod
    def empty_check(
        field: str,
        return_value: Any = None,
        message: str = "Input is empty",
    ) -> dict:
        """Create guard for empty input."""
        return {
            "type": "return",
            "input_mapping": {
                "condition_expression": f"len({{{{{field}}}}}) == 0",
                "return_value": return_value or {"error": message},
                "message": message,
            },
        }

    @staticmethod
    def null_check(
        field: str,
        return_value: Any = None,
        message: str = "Required field is null",
    ) -> dict:
        """Create guard for null/None field."""
        return {
            "type": "return",
            "input_mapping": {
                "condition_expression": f"{{{{{field}}}}} is None",
                "return_value": return_value or {"error": message},
                "message": message,
            },
        }

    @staticmethod
    def auth_check(
        role_field: str = "input.user.role",
        required_role: str = "admin",
        return_value: Any = None,
    ) -> dict:
        """Create guard for authorization check."""
        return {
            "type": "return",
            "input_mapping": {
                "condition_expression": f"{{{{{role_field}}}}} != '{required_role}'",
                "return_value": return_value or {"error": "Unauthorized"},
                "status": "failed",
                "message": f"Required role: {required_role}",
            },
        }


class EarlyExitPatterns:
    """
    Common early exit patterns for pipelines.

    These patterns represent common scenarios where you want
    to exit a pipeline early based on certain conditions.
    """

    @staticmethod
    def on_validation_failure(
        validation_stage: str,
        error_field: str = "errors",
    ) -> dict:
        """Exit early if validation fails."""
        return {
            "type": "return",
            "input_mapping": {
                "condition": f"{{{{upstream.{validation_stage}.is_valid}}}} == false",
                "return_value": {
                    "success": False,
                    "errors": f"{{{{upstream.{validation_stage}.{error_field}}}}}",
                },
                "status": "completed",
                "message": "Validation failed",
            },
        }

    @staticmethod
    def on_empty_result(
        query_stage: str,
        result_field: str = "results",
    ) -> dict:
        """Exit early if query returns no results."""
        return {
            "type": "return",
            "input_mapping": {
                "condition_expression": f"len({{{{upstream.{query_stage}.{result_field}}}}}) == 0",
                "return_value": {
                    "found": False,
                    "results": [],
                },
                "status": "completed",
                "message": "No results found",
            },
        }

    @staticmethod
    def on_cache_hit(
        cache_stage: str,
    ) -> dict:
        """Exit early if cache hit (return cached value)."""
        return {
            "type": "return",
            "input_mapping": {
                "condition": f"{{{{upstream.{cache_stage}.hit}}}} == true",
                "return_value": f"{{{{upstream.{cache_stage}.value}}}}",
                "status": "completed",
                "message": "Cache hit - returning cached value",
            },
        }

    @staticmethod
    def on_rate_limit(
        rate_limit_stage: str,
    ) -> dict:
        """Exit early if rate limited."""
        return {
            "type": "return",
            "input_mapping": {
                "condition": f"{{{{upstream.{rate_limit_stage}.limited}}}} == true",
                "return_value": {
                    "error": "Rate limited",
                    "retry_after": f"{{{{upstream.{rate_limit_stage}.retry_after}}}}",
                },
                "status": "failed",
                "message": "Rate limit exceeded",
            },
        }
