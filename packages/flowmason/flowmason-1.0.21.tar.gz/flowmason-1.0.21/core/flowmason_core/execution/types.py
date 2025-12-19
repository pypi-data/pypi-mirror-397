"""
Execution Types for FlowMason.

Data structures for execution results, tracing, usage tracking, and error handling.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Error Types (MuleSoft-inspired classification)
# =============================================================================

class ErrorType(str, Enum):
    """
    Classification of error types for structured error handling.

    Inspired by MuleSoft's error types for consistent error handling
    and routing in pipelines.
    """
    # Connection and Network
    CONNECTIVITY = "CONNECTIVITY"       # Network issues, provider unavailable
    TIMEOUT = "TIMEOUT"                 # Execution time limit exceeded

    # Data and Validation
    VALIDATION = "VALIDATION"           # Schema mismatch, invalid data
    EXPRESSION = "EXPRESSION"           # Template resolution, JMESPath errors
    TRANSFORMATION = "TRANSFORMATION"   # Data transformation failures

    # Execution
    EXECUTION = "EXECUTION"             # Generic component execution error
    ROUTING = "ROUTING"                 # Invalid dependencies, missing stages

    # Security
    SECURITY = "SECURITY"               # Auth failures, API key issues

    # Retry
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED" # All retries failed

    # Control Flow
    CONTROL_FLOW = "CONTROL_FLOW"       # Conditional/loop/branch errors

    # Unknown
    UNKNOWN = "UNKNOWN"                 # Unclassified errors


class ErrorSeverity(str, Enum):
    """Severity level for errors."""
    CRITICAL = "critical"   # Pipeline must stop
    ERROR = "error"         # Stage failed, may continue with on-error-continue
    WARNING = "warning"     # Non-fatal issue
    INFO = "info"           # Informational


class RetryableError(Exception):
    """Marker interface for errors that can be retried."""
    pass


# =============================================================================
# Base Error Classes
# =============================================================================

class FlowMasonError(Exception):
    """
    Base class for all FlowMason errors.

    Provides structured error information for error handling,
    routing, and observability.
    """

    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        component_id: Optional[str] = None,
        component_type: Optional[str] = None,
        cause: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
    ):
        self.error_type = error_type
        self.severity = severity
        self.component_id = component_id
        self.component_type = component_type
        self.cause = cause
        self.details = details or {}
        self.recoverable = recoverable
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "message": str(self),
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "component_id": self.component_id,
            "component_type": self.component_type,
            "cause": str(self.cause) if self.cause else None,
            "details": self.details,
            "recoverable": self.recoverable,
        }

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        component_id: Optional[str] = None,
        component_type: Optional[str] = None,
    ) -> "FlowMasonError":
        """Create a FlowMasonError from a generic exception."""
        # Try to classify the error
        error_type = cls._classify_exception(exc)
        recoverable = cls._is_recoverable(exc, error_type)

        return cls(
            message=str(exc),
            error_type=error_type,
            component_id=component_id,
            component_type=component_type,
            cause=exc,
            recoverable=recoverable,
        )

    @staticmethod
    def _classify_exception(exc: Exception) -> ErrorType:
        """Classify an exception into an ErrorType."""
        exc_type = type(exc).__name__.lower()
        exc_msg = str(exc).lower()

        # Connection errors
        if any(x in exc_type for x in ["connection", "network", "socket", "http"]):
            return ErrorType.CONNECTIVITY

        # Timeout errors
        if "timeout" in exc_type or "timeout" in exc_msg:
            return ErrorType.TIMEOUT

        # Validation errors
        if any(x in exc_type for x in ["validation", "schema", "type"]):
            return ErrorType.VALIDATION

        # Auth errors
        if any(x in exc_type for x in ["auth", "permission", "forbidden", "unauthorized"]):
            return ErrorType.SECURITY

        # Rate limits (common provider error)
        if "rate" in exc_msg and "limit" in exc_msg:
            return ErrorType.CONNECTIVITY  # Treat as retryable connectivity

        return ErrorType.EXECUTION

    @staticmethod
    def _is_recoverable(exc: Exception, error_type: ErrorType) -> bool:
        """Determine if an error is recoverable (retryable)."""
        # Explicitly retryable
        if isinstance(exc, RetryableError):
            return True

        # Connectivity and timeout are typically retryable
        if error_type in (ErrorType.CONNECTIVITY, ErrorType.TIMEOUT):
            return True

        return False


class UsageMetrics(BaseModel):
    """Token and cost usage from execution."""

    model_config = ConfigDict(extra="allow")

    # Token counts
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)

    # Cost
    cost_usd: float = Field(default=0.0, ge=0.0)

    # Timing
    duration_ms: int = Field(default=0, ge=0)

    # Provider info
    provider: Optional[str] = None
    model: Optional[str] = None

    def __add__(self, other: "UsageMetrics") -> "UsageMetrics":
        """Combine usage metrics."""
        return UsageMetrics(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            cost_usd=self.cost_usd + other.cost_usd,
            duration_ms=self.duration_ms + other.duration_ms,
        )


class ComponentResult(BaseModel):
    """Result from executing a single component."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    # Component identification
    component_id: str = Field(description="Stage ID in the pipeline")
    component_type: str = Field(description="Component type name")

    # Status
    status: str = Field(default="success", description="Execution status")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    # Output
    output: Any = Field(default=None, description="Component output data")

    # Usage metrics
    usage: UsageMetrics = Field(default_factory=UsageMetrics)

    # Tracing
    trace_id: Optional[str] = Field(default=None)
    span_id: Optional[str] = Field(default=None)

    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class DAGResult(BaseModel):
    """Result from executing a complete DAG/pipeline."""

    model_config = ConfigDict(extra="allow")

    # Identification
    run_id: str
    pipeline_id: str
    pipeline_version: str

    # Status
    status: str = Field(default="success")
    error: Optional[str] = None

    # Stage results
    stage_results: Dict[str, ComponentResult] = Field(default_factory=dict)

    # Final output (from output stage)
    final_output: Any = None

    # Aggregated usage
    usage: UsageMetrics = Field(default_factory=UsageMetrics)

    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Tracing
    trace_id: Optional[str] = None

    def get_stage_result(self, stage_id: str) -> Optional[ComponentResult]:
        """Get result for a specific stage."""
        return self.stage_results.get(stage_id)

    def get_stage_output(self, stage_id: str) -> Any:
        """Get output from a specific stage."""
        result = self.stage_results.get(stage_id)
        return result.output if result else None


# =============================================================================
# Specific Error Classes (inherit from FlowMasonError)
# =============================================================================

class ExecutionError(FlowMasonError):
    """Base class for execution errors (for backwards compatibility)."""

    def __init__(
        self,
        message: str,
        component_id: Optional[str] = None,
        component_type: Optional[str] = None,
        cause: Optional[Exception] = None,
        error_type: ErrorType = ErrorType.EXECUTION,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_type=error_type,
            component_id=component_id,
            component_type=component_type,
            cause=cause,
            **kwargs
        )


class ComponentExecutionError(ExecutionError):
    """Error during component execution."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_type=ErrorType.EXECUTION, **kwargs)


class MappingExecutionError(ExecutionError):
    """Error during input mapping."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_type=ErrorType.EXPRESSION, **kwargs)


class ValidationExecutionError(ExecutionError):
    """Error during output validation."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_type=ErrorType.VALIDATION, **kwargs)


class TimeoutExecutionError(ExecutionError, RetryableError):
    """Error when execution times out."""

    def __init__(
        self,
        component_id: str,
        timeout_ms: int,
        component_type: Optional[str] = None,
        **kwargs
    ):
        self.timeout_ms = timeout_ms
        message = f"Component '{component_id}' timed out after {timeout_ms}ms"
        super().__init__(
            message=message,
            error_type=ErrorType.TIMEOUT,
            component_id=component_id,
            component_type=component_type,
            recoverable=True,
            details={"timeout_ms": timeout_ms},
            **kwargs
        )


class RetryExhaustedError(ExecutionError):
    """Error when all retries have been exhausted."""

    def __init__(
        self,
        component_id: str,
        attempts: int,
        last_error: Optional[Exception] = None,
        component_type: Optional[str] = None,
        **kwargs
    ):
        self.attempts = attempts
        self.last_error = last_error
        message = f"Component '{component_id}' failed after {attempts} attempts"
        if last_error:
            message += f": {last_error}"
        super().__init__(
            message=message,
            error_type=ErrorType.RETRY_EXHAUSTED,
            component_id=component_id,
            component_type=component_type,
            cause=last_error,
            recoverable=False,
            details={"attempts": attempts},
            **kwargs
        )


class RoutingError(ExecutionError):
    """Error in pipeline routing/dependencies."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_type=ErrorType.ROUTING, **kwargs)


class ProviderError(ExecutionError, RetryableError):
    """Error from LLM provider."""

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: Optional[int] = None,
        **kwargs
    ):
        self.provider = provider
        self.status_code = status_code

        # Classify based on status code
        error_type = ErrorType.EXECUTION
        recoverable = False
        if status_code:
            if status_code == 401:
                error_type = ErrorType.SECURITY
            elif status_code == 429:
                error_type = ErrorType.CONNECTIVITY  # Rate limit
                recoverable = True
            elif status_code >= 500:
                error_type = ErrorType.CONNECTIVITY  # Server error
                recoverable = True

        super().__init__(
            message=message,
            error_type=error_type,
            recoverable=recoverable,
            details={"provider": provider, "status_code": status_code},
            **kwargs
        )


class CancellationError(ExecutionError):
    """Error when execution is cancelled."""

    def __init__(
        self,
        message: str = "Execution was cancelled",
        component_id: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        self.reason = reason
        if reason:
            message = f"{message}: {reason}"
        super().__init__(
            message=message,
            error_type=ErrorType.EXECUTION,
            component_id=component_id,
            recoverable=False,
            severity=ErrorSeverity.INFO,
            details={"reason": reason},
            **kwargs
        )


class TraceSpan:
    """
    Simple tracing span for execution observability.

    This is a minimal implementation - can be extended to support
    OpenTelemetry or other tracing systems.
    """

    def __init__(self, name: str, trace_id: Optional[str] = None):
        import uuid
        self.name = name
        self.trace_id = trace_id or str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        self.attributes: Dict[str, Any] = {}
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.status = "unknown"

    def __enter__(self) -> "TraceSpan":
        self.started_at = datetime.utcnow()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.completed_at = datetime.utcnow()
        if exc_type is not None:
            self.status = "error"
            self.attributes["error.type"] = exc_type.__name__
            self.attributes["error.message"] = str(exc_val)
        else:
            self.status = "success"

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    @property
    def duration_ms(self) -> int:
        """Get duration in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return 0


class ExecutionTracer:
    """
    Simple execution tracer for observability.

    Tracks spans for each component execution and builds
    a trace tree.
    """

    def __init__(self, trace_id: Optional[str] = None):
        import uuid
        self.trace_id = trace_id or str(uuid.uuid4())
        self.spans: List[TraceSpan] = []

    def span(self, name: str) -> TraceSpan:
        """Create a new span."""
        span = TraceSpan(name, trace_id=self.trace_id)
        self.spans.append(span)
        return span

    def get_spans(self) -> List[Dict[str, Any]]:
        """Get all spans as dictionaries."""
        return [
            {
                "name": span.name,
                "trace_id": span.trace_id,
                "span_id": span.span_id,
                "status": span.status,
                "started_at": span.started_at.isoformat() if span.started_at else None,
                "completed_at": span.completed_at.isoformat() if span.completed_at else None,
                "duration_ms": span.duration_ms,
                "attributes": span.attributes,
            }
            for span in self.spans
        ]
