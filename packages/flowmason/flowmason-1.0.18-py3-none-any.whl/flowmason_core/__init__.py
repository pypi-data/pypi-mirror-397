"""
FlowMason Core - Universal AI Workflow Infrastructure

This package provides the core functionality for FlowMason:
- Type system for nodes and operators (Input/Output schemas)
- Decorators for defining components (@node, @operator)
- Universal Component Registry for dynamic loading
- Package format for component distribution
- High-level API for running pipelines

Quick Start:
    from flowmason_core import FlowMason

    fm = FlowMason()
    fm.load_packages("./packages")

    result = await fm.run_component("generator", {"prompt": "Hello"})
    print(result.output)
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("flowmason")
except PackageNotFoundError:
    __version__ = "0.0.0"  # Development fallback

from flowmason_core.api import FlowMason, Pipeline, PipelineResult, StageDefinition
from flowmason_core.core.decorators import control_flow, node, operator
from flowmason_core.core.types import (
    Field,
    NodeInput,
    NodeOutput,
    OperatorInput,
    OperatorOutput,
)
from flowmason_core.inheritance import (
    InheritanceResolver,
    InheritanceValidator,
    PipelineMerger,
)

__all__ = [
    # High-level API
    "FlowMason",
    "Pipeline",
    "PipelineResult",
    "StageDefinition",
    # Type system
    "NodeInput",
    "NodeOutput",
    "OperatorInput",
    "OperatorOutput",
    "Field",
    # Decorators
    "node",
    "operator",
    "control_flow",
    # Inheritance
    "InheritanceResolver",
    "InheritanceValidator",
    "PipelineMerger",
]
