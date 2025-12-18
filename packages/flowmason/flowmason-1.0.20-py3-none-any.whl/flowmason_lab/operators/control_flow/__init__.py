"""
Control Flow Components for FlowMason.

These components manage pipeline execution flow:
- Conditional: If/else branching
- Router: Switch/case routing
- ForEach: Loop over items
- TryCatch: Error handling with recovery
- SubPipeline: Call another pipeline
- Return: Early exit with value
"""

from flowmason_lab.operators.control_flow.conditional import ConditionalComponent
from flowmason_lab.operators.control_flow.foreach import (
    ForEachComponent,
    LoopIterationContext,
)
from flowmason_lab.operators.control_flow.return_early import (
    EarlyExitPatterns,
    GuardClause,
    ReturnComponent,
)
from flowmason_lab.operators.control_flow.router import RouterComponent
from flowmason_lab.operators.control_flow.subpipeline import (
    SubPipelineComponent,
    SubPipelineContext,
)
from flowmason_lab.operators.control_flow.trycatch import (
    ErrorScope,
    TryCatchComponent,
    TryCatchContext,
)

__all__ = [
    # Basic control flow
    "ConditionalComponent",
    "RouterComponent",
    # Advanced control flow
    "ForEachComponent",
    "LoopIterationContext",
    "TryCatchComponent",
    "TryCatchContext",
    "ErrorScope",
    # Composition control flow
    "SubPipelineComponent",
    "SubPipelineContext",
    "ReturnComponent",
    "GuardClause",
    "EarlyExitPatterns",
]
