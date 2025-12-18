"""
Loop Operator - Core FlowMason Component.

Iterates over collections and manages loop state.
Essential for batch processing and iteration patterns.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput


@operator(
    name="loop",
    category="core",
    description="Iterate over collections with configurable batching and limits",
    icon="repeat",
    color="#EC4899",
    version="1.0.0",
    author="FlowMason",
    tags=["loop", "iteration", "batch", "control-flow", "core"],
)
class LoopOperator:
    """
    Iterate over collections.

    This operator enables:
    - Iterating over arrays
    - Batch processing
    - Pagination
    - Limiting iterations
    - Tracking iteration state
    """

    class Input(OperatorInput):
        items: List[Any] = Field(
            description="Collection of items to iterate over",
        )
        batch_size: int = Field(
            default=1,
            ge=1,
            le=1000,
            description="Number of items per batch",
        )
        max_iterations: Optional[int] = Field(
            default=None,
            ge=1,
            description="Maximum number of iterations (batches)",
        )
        start_index: int = Field(
            default=0,
            ge=0,
            description="Starting index in the collection",
        )
        include_metadata: bool = Field(
            default=True,
            description="Include iteration metadata in output",
        )

    class Output(OperatorOutput):
        batches: List[List[Any]] = Field(
            description="Items split into batches"
        )
        total_items: int = Field(
            description="Total number of items"
        )
        total_batches: int = Field(
            description="Total number of batches"
        )
        has_more: bool = Field(
            default=False,
            description="Whether there are more items after max_iterations"
        )
        metadata: Dict[str, Any] = Field(
            default_factory=dict,
            description="Iteration metadata"
        )

    class Config:
        deterministic: bool = True
        timeout_seconds: int = 10

    async def execute(self, input: Input, context) -> Output:
        """Execute the loop operation."""
        items = input.items
        total_items = len(items)

        # Apply start_index
        if input.start_index > 0:
            items = items[input.start_index:]

        # Split into batches
        batches = []
        for i in range(0, len(items), input.batch_size):
            batch = items[i:i + input.batch_size]
            batches.append(batch)

            # Check max_iterations
            if input.max_iterations and len(batches) >= input.max_iterations:
                break

        # Determine if there are more items
        processed_count = sum(len(b) for b in batches) + input.start_index
        has_more = processed_count < total_items

        # Build metadata
        metadata = {}
        if input.include_metadata:
            metadata = {
                "start_index": input.start_index,
                "batch_size": input.batch_size,
                "items_processed": processed_count,
                "items_remaining": total_items - processed_count,
            }

        return self.Output(
            batches=batches,
            total_items=total_items,
            total_batches=len(batches),
            has_more=has_more,
            metadata=metadata,
        )
