"""Core types and decorators for FlowMason components."""

from flowmason_core.core.decorators import (
    control_flow,
    get_component_type,
    get_control_flow_type,
    is_control_flow_component,
    is_flowmason_component,
    node,
    operator,
)
from flowmason_core.core.types import (
    ControlFlowDirective,
    # Control flow types
    ControlFlowInput,
    ControlFlowOutput,
    ControlFlowResult,
    ControlFlowType,
    # Field helper
    Field,
    # Node types
    NodeInput,
    NodeOutput,
    # Operator types
    OperatorInput,
    OperatorOutput,
)

__all__ = [
    # Node types
    "NodeInput",
    "NodeOutput",
    # Operator types
    "OperatorInput",
    "OperatorOutput",
    # Control flow types
    "ControlFlowInput",
    "ControlFlowOutput",
    "ControlFlowDirective",
    "ControlFlowResult",
    "ControlFlowType",
    # Field helper
    "Field",
    # Decorators
    "node",
    "operator",
    "control_flow",
    # Utilities
    "is_flowmason_component",
    "is_control_flow_component",
    "get_component_type",
    "get_control_flow_type",
]
