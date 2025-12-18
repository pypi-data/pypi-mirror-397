"""
Router Control Flow Component.

Routes execution to one of multiple branches based on a value.
This is the FlowMason equivalent of switch/case in code.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import control_flow
from flowmason_core.core.types import (
    ControlFlowDirective,
    ControlFlowInput,
    ControlFlowOutput,
    ControlFlowType,
    Field,
)


@control_flow(
    name="router",
    description="Route execution to one of multiple branches based on a value (switch/case)",
    control_flow_type="router",
    icon="git-merge",
    color="#F59E0B",  # Amber
    version="1.0.0",
    author="FlowMason",
    tags=["router", "switch", "case", "branch", "control-flow"],
)
class RouterComponent:
    """
    Multi-way branching for pipeline execution.

    This component evaluates a value and routes execution to one of
    multiple branches. Stages in non-selected branches are skipped
    via the ControlFlowDirective.

    Unlike Conditional which is binary (if/else), Router supports
    multiple branches (switch/case).

    Example Pipeline Config:
        stages:
          - id: route_by_type
            type: router
            input_mapping:
              value: "{{upstream.classify.category}}"
              routes:
                "urgent": ["process_urgent", "notify_oncall"]
                "normal": ["process_normal", "log_result"]
                "low": ["queue_for_later"]
              default_route: ["handle_unknown"]

          - id: process_urgent
            type: urgent_processor
            depends_on: [route_by_type]

          - id: process_normal
            type: normal_processor
            depends_on: [route_by_type]

    Transpiles to:
        match classify.category:
            case "urgent":
                process_urgent()
                notify_oncall()
            case "normal":
                process_normal()
                log_result()
            case "low":
                queue_for_later()
            case _:
                handle_unknown()
    """

    class Input(ControlFlowInput):
        value: Any = Field(
            description="The value to route on",
        )
        routes: Dict[str, List[str]] = Field(
            description="Map of value -> list of stage IDs to execute",
            examples=[
                {
                    "approved": ["process_approved"],
                    "rejected": ["process_rejected", "notify_user"],
                    "pending": ["queue_for_review"],
                }
            ],
        )
        default_route: List[str] = Field(
            default_factory=list,
            description="Stage IDs to execute if no route matches",
        )
        value_expression: Optional[str] = Field(
            default=None,
            description="Expression to transform value before routing",
            examples=["value.lower()", "value['type']", "str(value)"],
        )
        case_insensitive: bool = Field(
            default=False,
            description="Whether to do case-insensitive string matching",
        )
        pass_data: Optional[Any] = Field(
            default=None,
            description="Data to pass through to downstream stages",
        )

    class Output(ControlFlowOutput):
        route_taken: str = Field(
            description="Which route was taken (key from routes dict or 'default')"
        )
        original_value: Any = Field(
            description="The original routing value"
        )
        matched_value: Any = Field(
            description="The value after any transformation"
        )
        stages_to_execute: List[str] = Field(
            description="List of stage IDs that will be executed"
        )
        stages_to_skip: List[str] = Field(
            description="List of stage IDs that will be skipped"
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
        Execute the routing decision and return execution directive.

        The directive tells the executor which stages to skip based on
        the routing result.
        """
        # Transform value if expression provided
        matched_value = self._transform_value(
            input.value,
            input.value_expression,
            input.case_insensitive,
        )

        # Find matching route
        route_taken, stages_to_execute = self._find_route(
            matched_value,
            input.routes,
            input.default_route,
            input.case_insensitive,
        )

        # Calculate stages to skip (all other routes)
        all_route_stages = set()
        for route_stages in input.routes.values():
            all_route_stages.update(route_stages)
        all_route_stages.update(input.default_route)

        stages_to_skip = list(all_route_stages - set(stages_to_execute))

        # Create the directive
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.ROUTER,
            branch_taken=route_taken,
            skip_stages=stages_to_skip,
            execute_stages=stages_to_execute,
            continue_execution=True,
            output_data=input.pass_data,
            metadata={
                "original_value": str(input.value)[:100],
                "matched_value": str(matched_value)[:100],
                "available_routes": list(input.routes.keys()),
            },
        )

        return self.Output(
            route_taken=route_taken,
            original_value=input.value,
            matched_value=matched_value,
            stages_to_execute=stages_to_execute,
            stages_to_skip=stages_to_skip,
            data=input.pass_data,
            directive=directive,
        )

    def _transform_value(
        self,
        value: Any,
        expression: Optional[str],
        case_insensitive: bool,
    ) -> Any:
        """
        Transform the routing value.

        Args:
            value: Original value
            expression: Optional transformation expression
            case_insensitive: Whether to lowercase strings

        Returns:
            Transformed value
        """
        result = value

        # Apply expression if provided
        if expression:
            try:
                result = eval(
                    expression,
                    {"__builtins__": {}},
                    {"value": value, "str": str, "int": int, "float": float, "len": len}
                )
            except Exception:
                pass  # Keep original value on error

        # Apply case insensitivity
        if case_insensitive and isinstance(result, str):
            result = result.lower()

        return result

    def _find_route(
        self,
        value: Any,
        routes: Dict[str, List[str]],
        default_route: List[str],
        case_insensitive: bool,
    ) -> tuple:
        """
        Find the matching route for a value.

        Args:
            value: The value to match
            routes: Route definitions
            default_route: Default if no match
            case_insensitive: Whether to do case-insensitive matching

        Returns:
            Tuple of (route_name, stages_to_execute)
        """
        # Build lookup dict (possibly case-insensitive)
        if case_insensitive:
            lookup = {
                k.lower() if isinstance(k, str) else k: (k, v)
                for k, v in routes.items()
            }
            search_value = value.lower() if isinstance(value, str) else value
        else:
            lookup = {k: (k, v) for k, v in routes.items()}
            search_value = value

        # Find match
        if search_value in lookup:
            route_name, stages = lookup[search_value]
            return route_name, stages

        # String conversion fallback
        str_value = str(search_value)
        if str_value in lookup:
            route_name, stages = lookup[str_value]
            return route_name, stages

        # Default route
        return "default", default_route
