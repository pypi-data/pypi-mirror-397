"""
ForEach Control Flow Component.

Iterates over a collection and executes stages for each item.
This is the FlowMason equivalent of for loops in code.
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
    name="foreach",
    description="Iterate over items and execute stages for each (for loop)",
    control_flow_type="foreach",
    icon="repeat",
    color="#10B981",  # Emerald green
    version="1.0.0",
    author="FlowMason",
    tags=["foreach", "loop", "iterate", "collection", "control-flow"],
)
class ForEachComponent:
    """
    Loop iteration for pipeline execution.

    This component iterates over a collection and provides each item
    to downstream stages. The directive includes loop state that the
    executor uses to repeat stage execution.

    There are two modes:
    1. BATCH mode (default): All items are processed, results collected
    2. STREAMING mode: Items processed one at a time (for large collections)

    Example Pipeline Config:
        stages:
          - id: process_customers
            type: foreach
            input_mapping:
              items: "{{input.customers}}"
              item_variable: "customer"
              loop_stages: ["enrich_customer", "analyze_customer"]
              collect_results: true

          - id: enrich_customer
            type: crm_lookup
            depends_on: [process_customers]
            input_mapping:
              customer_id: "{{upstream.process_customers.current_item.id}}"

          - id: analyze_customer
            type: ai_analyzer
            depends_on: [enrich_customer]

    Transpiles to:
        results = []
        for customer in input.customers:
            enriched = crm_lookup(customer.id)
            analysis = ai_analyzer(enriched)
            results.append(analysis)
    """

    class Input(ControlFlowInput):
        items: List[Any] = Field(
            description="Collection of items to iterate over",
        )
        loop_stages: List[str] = Field(
            default_factory=list,
            description="Stage IDs to execute for each item",
        )
        item_variable: str = Field(
            default="item",
            description="Variable name for current item in context",
        )
        index_variable: str = Field(
            default="index",
            description="Variable name for current index in context",
        )
        collect_results: bool = Field(
            default=True,
            description="Whether to collect results from each iteration",
        )
        parallel: bool = Field(
            default=False,
            description="Whether to process items in parallel",
        )
        max_parallel: int = Field(
            default=5,
            description="Maximum parallel iterations (if parallel=True)",
        )
        break_on_error: bool = Field(
            default=True,
            description="Whether to stop iteration on first error",
        )
        filter_expression: Optional[str] = Field(
            default=None,
            description="Optional filter expression (uses 'item' variable)",
            examples=["item['active'] == True", "len(item) > 0"],
        )

    class Output(ControlFlowOutput):
        total_items: int = Field(
            description="Total number of items in collection"
        )
        processed_items: int = Field(
            description="Number of items processed"
        )
        skipped_items: int = Field(
            description="Number of items skipped (by filter)"
        )
        current_item: Any = Field(
            default=None,
            description="Current item being processed (for executor)"
        )
        current_index: int = Field(
            default=0,
            description="Current index (0-based)"
        )
        items_to_process: List[Any] = Field(
            default_factory=list,
            description="Items that will be processed (after filtering)"
        )
        results: List[Any] = Field(
            default_factory=list,
            description="Collected results from iterations"
        )
        is_complete: bool = Field(
            default=False,
            description="Whether all iterations are complete"
        )
        directive: ControlFlowDirective = Field(
            description="Execution directive for the executor"
        )

    class Config:
        timeout_seconds: int = 300  # 5 minutes for loops

    async def execute(self, input: Input, context) -> Output:
        """
        Execute the foreach loop setup and return execution directive.

        This component sets up the loop state. The executor uses the
        directive to actually iterate and execute stages multiple times.
        """
        items = input.items or []

        # Apply filter if provided
        if input.filter_expression:
            items_to_process = self._filter_items(items, input.filter_expression)
            skipped_items = len(items) - len(items_to_process)
        else:
            items_to_process = items
            skipped_items = 0

        total_items = len(items)
        processed_items = len(items_to_process)

        # Determine if loop is complete (empty collection)
        is_complete = len(items_to_process) == 0

        # Set up first item if available
        current_item = items_to_process[0] if items_to_process else None
        current_index = 0

        # Create the directive
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.FOREACH,
            execute_stages=input.loop_stages,
            skip_stages=[],  # ForEach doesn't skip, it repeats
            loop_items=items_to_process,
            loop_results=[],  # Will be populated by executor
            current_item=current_item,
            current_index=current_index,
            continue_execution=not is_complete,
            metadata={
                "item_variable": input.item_variable,
                "index_variable": input.index_variable,
                "collect_results": input.collect_results,
                "parallel": input.parallel,
                "max_parallel": input.max_parallel,
                "break_on_error": input.break_on_error,
                "total_items": total_items,
                "processed_items": processed_items,
            },
        )

        return self.Output(
            total_items=total_items,
            processed_items=processed_items,
            skipped_items=skipped_items,
            current_item=current_item,
            current_index=current_index,
            items_to_process=items_to_process,
            results=[],
            is_complete=is_complete,
            directive=directive,
        )

    def _filter_items(
        self,
        items: List[Any],
        expression: str,
    ) -> List[Any]:
        """
        Filter items based on expression.

        Args:
            items: Items to filter
            expression: Python expression using 'item' variable

        Returns:
            Filtered list of items
        """
        result = []
        for item in items:
            try:
                passed = eval(
                    expression,
                    {"__builtins__": {}},
                    {"item": item, "len": len, "str": str, "int": int, "float": float}
                )
                if passed:
                    result.append(item)
            except Exception:
                # Skip items that cause evaluation errors
                pass
        return result


class LoopIterationContext:
    """
    Helper class for tracking loop iteration state.

    Used by the executor to manage loop execution.
    """

    def __init__(
        self,
        items: List[Any],
        loop_stages: List[str],
        item_variable: str = "item",
        index_variable: str = "index",
        parallel: bool = False,
        max_parallel: int = 5,
        break_on_error: bool = True,
    ):
        self.items = items
        self.loop_stages = loop_stages
        self.item_variable = item_variable
        self.index_variable = index_variable
        self.parallel = parallel
        self.max_parallel = max_parallel
        self.break_on_error = break_on_error

        self.current_index = 0
        self.results: List[Any] = []
        self.errors: List[Dict[str, Any]] = []
        self.is_complete = False

    @property
    def current_item(self) -> Any:
        """Get current item."""
        if self.current_index < len(self.items):
            return self.items[self.current_index]
        return None

    @property
    def has_more(self) -> bool:
        """Check if there are more items."""
        return self.current_index < len(self.items)

    def advance(self) -> bool:
        """
        Advance to next item.

        Returns:
            True if advanced, False if complete
        """
        self.current_index += 1
        if self.current_index >= len(self.items):
            self.is_complete = True
            return False
        return True

    def add_result(self, result: Any) -> None:
        """Add result from current iteration."""
        self.results.append(result)

    def add_error(self, error: Exception, item: Any, index: int) -> None:
        """Record an error."""
        self.errors.append({
            "index": index,
            "item": str(item)[:100],
            "error": str(error),
            "error_type": type(error).__name__,
        })

    def get_context_vars(self) -> Dict[str, Any]:
        """Get variables to inject into execution context."""
        return {
            self.item_variable: self.current_item,
            self.index_variable: self.current_index,
            "loop_total": len(self.items),
            "loop_remaining": len(self.items) - self.current_index - 1,
            "loop_results": self.results,
        }
