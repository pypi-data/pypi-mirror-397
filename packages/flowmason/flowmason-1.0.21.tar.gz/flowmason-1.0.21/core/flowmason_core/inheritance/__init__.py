"""
Pipeline Inheritance & Composition Module.

Provides support for:
- Pipeline inheritance (extends) - child pipelines inherit stages from parents
- Stage overrides - child pipelines can override inherited stage configs
- Abstract pipelines - base pipelines that cannot be executed directly
- Pipeline composition - embed sub-pipelines as stages
"""

from flowmason_core.inheritance.merger import PipelineMerger
from flowmason_core.inheritance.resolver import InheritanceResolver
from flowmason_core.inheritance.validator import InheritanceValidator

__all__ = [
    "InheritanceResolver",
    "PipelineMerger",
    "InheritanceValidator",
]
