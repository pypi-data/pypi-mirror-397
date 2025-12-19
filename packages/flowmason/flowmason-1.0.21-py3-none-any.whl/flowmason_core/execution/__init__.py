"""
FlowMason Execution Engine.

Provides the universal execution system that can execute ANY component type
through a single code path.

Main Components:
- UniversalExecutor: Execute any component uniformly
- DAGExecutor: Execute pipelines as DAGs
- ExecutionTracer: Observability and tracing
- Retry logic with exponential backoff
- Error classification (MuleSoft-inspired)

The key principle: ONE code path for ALL component types.
No special cases. No hardcoded types.

Example:
    from flowmason_core.execution import UniversalExecutor, DAGExecutor
    from flowmason_core.config import ExecutionContext, ComponentConfig

    context = ExecutionContext(
        run_id="run_123",
        pipeline_id="my-pipeline",
        pipeline_version="1.0.0"
    )

    executor = UniversalExecutor(registry, context)

    # Works for ANY component type
    result = await executor.execute_component(
        ComponentConfig(type="generator", input_mapping={...}),
        upstream_outputs={}
    )
"""

from flowmason_core.execution.cancellation import (
    CancellationScope,
    CancellationToken,
    cancellable,
)
from flowmason_core.execution.retry import (
    DEFAULT_RETRYABLE_ERRORS,
    RetryContext,
    calculate_backoff,
    is_retryable,
    retry,
    with_retry,
)
from flowmason_core.execution.types import (
    CancellationError,
    ComponentExecutionError,
    ComponentResult,
    DAGResult,
    ErrorSeverity,
    # Enums
    ErrorType,
    # Error types
    ExecutionError,
    ExecutionTracer,
    # Base errors
    FlowMasonError,
    MappingExecutionError,
    ProviderError,
    RetryableError,
    RetryExhaustedError,
    RoutingError,
    TimeoutExecutionError,
    # Tracing
    TraceSpan,
    # Result types
    UsageMetrics,
    ValidationExecutionError,
)
from flowmason_core.execution.universal_executor import (
    DAGExecutor,
    UniversalExecutor,
)

__all__ = [
    # Error classification
    "ErrorType",
    "ErrorSeverity",
    # Base errors
    "FlowMasonError",
    "RetryableError",
    # Result types
    "UsageMetrics",
    "ComponentResult",
    "DAGResult",
    # Error types
    "ExecutionError",
    "ComponentExecutionError",
    "MappingExecutionError",
    "ValidationExecutionError",
    "TimeoutExecutionError",
    "RetryExhaustedError",
    "RoutingError",
    "CancellationError",
    "ProviderError",
    # Tracing
    "TraceSpan",
    "ExecutionTracer",
    # Executors
    "UniversalExecutor",
    "DAGExecutor",
    # Retry utilities
    "with_retry",
    "retry",
    "is_retryable",
    "calculate_backoff",
    "RetryContext",
    "DEFAULT_RETRYABLE_ERRORS",
    # Cancellation
    "CancellationToken",
    "CancellationScope",
    "cancellable",
]
