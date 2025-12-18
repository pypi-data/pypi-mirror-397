"""
Conditional Control Flow Component.

Executes one of two branches based on a condition.
This is the FlowMason equivalent of if/else in code.
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
    name="conditional",
    description="Execute one of two branches based on a condition (if/else)",
    control_flow_type="conditional",
    icon="git-branch",
    color="#EC4899",  # Pink
    version="1.0.0",
    author="FlowMason",
    tags=["conditional", "if-else", "branch", "control-flow"],
)
class ConditionalComponent:
    """
    Conditional branching for pipeline execution.

    This component evaluates a condition and determines which branch
    of the pipeline to execute. Stages in the non-taken branch are
    skipped via the ControlFlowDirective.

    Unlike the Filter operator which just outputs a boolean, this
    component actively controls execution flow by telling the executor
    which stages to skip.

    Example Pipeline Config:
        stages:
          - id: check_condition
            type: conditional
            input_mapping:
              condition: "{{upstream.validate.is_valid}}"
              true_branch_stages: ["process_valid", "save_result"]
              false_branch_stages: ["handle_error", "notify_admin"]

          - id: process_valid
            type: some_processor
            depends_on: [check_condition]

          - id: handle_error
            type: error_handler
            depends_on: [check_condition]

    Transpiles to:
        if validate.is_valid:
            process_valid()
            save_result()
        else:
            handle_error()
            notify_admin()
    """

    class Input(ControlFlowInput):
        condition: Any = Field(
            description="The condition to evaluate (truthy/falsy value)",
        )
        condition_expression: Optional[str] = Field(
            default=None,
            description="Python expression to evaluate (uses 'value' variable)",
            examples=[
                "value > 0.8",
                "value['status'] == 'approved'",
                "len(value) > 0",
            ],
        )
        true_branch_stages: List[str] = Field(
            default_factory=list,
            description="Stage IDs to execute if condition is true",
        )
        false_branch_stages: List[str] = Field(
            default_factory=list,
            description="Stage IDs to execute if condition is false",
        )
        pass_data: Optional[Any] = Field(
            default=None,
            description="Data to pass through to downstream stages",
        )

    class Output(ControlFlowOutput):
        branch_taken: str = Field(
            description="Which branch was taken ('true' or 'false')"
        )
        condition_value: Any = Field(
            description="The evaluated condition value"
        )
        condition_result: bool = Field(
            description="The boolean result of the condition"
        )
        data: Any = Field(
            default=None,
            description="Pass-through data for downstream stages"
        )
        directive: ControlFlowDirective = Field(
            description="Execution directive for the executor"
        )

    class Config:
        timeout_seconds: int = 5

    async def execute(self, input: Input, context) -> Output:
        """
        Execute the conditional check and return execution directive.

        The directive tells the executor which stages to skip based on
        the condition result.
        """
        # Evaluate the condition
        condition_result = self._evaluate_condition(
            input.condition,
            input.condition_expression
        )

        # Determine which branch is taken
        if condition_result:
            branch_taken = "true"
            skip_stages = input.false_branch_stages
            execute_stages = input.true_branch_stages
        else:
            branch_taken = "false"
            skip_stages = input.true_branch_stages
            execute_stages = input.false_branch_stages

        # Create the directive
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.CONDITIONAL,
            branch_taken=branch_taken,
            skip_stages=skip_stages,
            execute_stages=execute_stages,
            continue_execution=True,
            output_data=input.pass_data,
            metadata={
                "condition_value": str(input.condition)[:100],  # Truncate for safety
                "condition_result": condition_result,
            },
        )

        return self.Output(
            branch_taken=branch_taken,
            condition_value=input.condition,
            condition_result=condition_result,
            data=input.pass_data,
            directive=directive,
        )

    def _evaluate_condition(
        self,
        condition: Any,
        expression: Optional[str] = None,
    ) -> bool:
        """
        Evaluate the condition to a boolean.

        Args:
            condition: The condition value
            expression: Optional Python expression to evaluate

        Returns:
            Boolean result
        """
        if expression:
            try:
                # Safe evaluation with limited scope
                result = eval(
                    expression,
                    {"__builtins__": {}},
                    {"value": condition, "len": len, "str": str, "int": int, "float": float}
                )
                return bool(result)
            except Exception:
                # Log error and return False
                return False

        # Direct boolean evaluation
        return bool(condition)
