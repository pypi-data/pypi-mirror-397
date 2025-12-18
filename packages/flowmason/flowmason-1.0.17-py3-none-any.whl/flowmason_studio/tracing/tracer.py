"""
FlowMason Execution Tracer

Captures detailed execution traces for debugging and observability:
- Per-node input/output capture
- Prompt/response logging with token counts
- Timing spans with parent-child relationships
- Error and retry tracking
- Export to JSON and OpenTelemetry format

Usage:
    from flowmason_studio.tracing import ExecutionTracer, Span

    tracer = ExecutionTracer(run_id="run-123", pipeline_id="pipeline-1")

    with tracer.span("node_execution", node_id="generator-1") as span:
        span.set_input({"prompt": "..."})
        result = await execute_node(...)
        span.set_output(result)
        span.set_usage(tokens=100, cost=0.001)
"""

import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SpanStatus(str, Enum):
    """Status of a trace span."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class SpanEvent:
    """An event within a span (e.g., retry, log message)."""
    name: str
    timestamp: datetime
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "attributes": self.attributes,
        }


@dataclass
class Span:
    """
    A trace span representing a unit of work.

    Spans can be nested to represent parent-child relationships
    (e.g., pipeline -> batch -> node -> provider call).
    """
    span_id: str
    name: str
    trace_id: str
    parent_span_id: Optional[str] = None

    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: int = 0

    # Status
    status: SpanStatus = SpanStatus.PENDING

    # Context
    node_id: Optional[str] = None
    node_type: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None

    # Input/Output
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    raw_prompt: Optional[str] = None
    raw_response: Optional[str] = None

    # Usage
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    # Error
    error: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0

    # Events
    events: List[SpanEvent] = field(default_factory=list)

    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)

    def start(self) -> "Span":
        """Mark span as started."""
        self.start_time = datetime.now(timezone.utc)
        self.status = SpanStatus.RUNNING
        return self

    def end(self, status: Optional[SpanStatus] = None) -> "Span":
        """Mark span as ended."""
        self.end_time = datetime.now(timezone.utc)
        if status:
            self.status = status
        elif self.status == SpanStatus.RUNNING:
            self.status = SpanStatus.SUCCESS

        if self.start_time and self.end_time:
            self.duration_ms = int(
                (self.end_time - self.start_time).total_seconds() * 1000
            )
        return self

    def set_input(self, data: Dict[str, Any]) -> "Span":
        """Set input data for this span."""
        self.input_data = data
        return self

    def set_output(self, data: Dict[str, Any]) -> "Span":
        """Set output data for this span."""
        self.output_data = data
        return self

    def set_prompt(self, prompt: str) -> "Span":
        """Set raw prompt text."""
        self.raw_prompt = prompt
        return self

    def set_response(self, response: str) -> "Span":
        """Set raw response text."""
        self.raw_response = response
        return self

    def set_usage(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> "Span":
        """Set token usage and cost."""
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens
        self.cost_usd = cost_usd
        return self

    def set_error(self, error: str, error_type: Optional[str] = None) -> "Span":
        """Set error information."""
        self.error = error
        self.error_type = error_type
        self.status = SpanStatus.ERROR
        return self

    def add_event(self, name: str, **attributes) -> "Span":
        """Add an event to this span."""
        self.events.append(SpanEvent(
            name=name,
            timestamp=datetime.now(timezone.utc),
            attributes=attributes,
        ))
        return self

    def set_attribute(self, key: str, value: Any) -> "Span":
        """Set a custom attribute."""
        self.attributes[key] = value
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary for serialization."""
        result: Dict[str, Any] = {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
        }

        # Context
        if self.node_id:
            result["node_id"] = self.node_id
        if self.node_type:
            result["node_type"] = self.node_type
        if self.provider:
            result["provider"] = self.provider
        if self.model:
            result["model"] = self.model

        # Input/Output (truncate large values for storage)
        if self.input_data:
            result["input"] = self._truncate_data(self.input_data)
        if self.output_data:
            result["output"] = self._truncate_data(self.output_data)
        if self.raw_prompt:
            result["raw_prompt"] = self._truncate_string(self.raw_prompt, 10000)
        if self.raw_response:
            result["raw_response"] = self._truncate_string(self.raw_response, 10000)

        # Usage
        if self.total_tokens > 0:
            result["usage"] = {
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "total_tokens": self.total_tokens,
                "cost_usd": self.cost_usd,
            }

        # Error
        if self.error:
            result["error"] = {
                "message": self.error,
                "type": self.error_type,
            }
            result["retry_count"] = self.retry_count

        # Events
        if self.events:
            result["events"] = [e.to_dict() for e in self.events]

        # Attributes
        if self.attributes:
            result["attributes"] = self.attributes

        return result

    def _truncate_data(self, data: Dict[str, Any], max_depth: int = 3) -> Dict[str, Any]:
        """Truncate nested data for storage."""
        result = self._truncate_value(data, max_depth, 0)
        return result if isinstance(result, dict) else {}

    def _truncate_value(self, value: Any, max_depth: int, current_depth: int) -> Any:
        """Recursively truncate values."""
        if current_depth >= max_depth:
            if isinstance(value, (dict, list)):
                return f"<{type(value).__name__} with {len(value)} items>"
            return value

        if isinstance(value, dict):
            return {
                k: self._truncate_value(v, max_depth, current_depth + 1)
                for k, v in value.items()
            }
        elif isinstance(value, list):
            if len(value) > 10:
                return [
                    self._truncate_value(v, max_depth, current_depth + 1)
                    for v in value[:10]
                ] + [f"... and {len(value) - 10} more items"]
            return [
                self._truncate_value(v, max_depth, current_depth + 1)
                for v in value
            ]
        elif isinstance(value, str) and len(value) > 1000:
            return value[:1000] + f"... ({len(value)} chars total)"
        return value

    def _truncate_string(self, s: str, max_length: int) -> str:
        """Truncate a string to max length."""
        if len(s) > max_length:
            return s[:max_length] + f"... ({len(s)} chars total)"
        return s


@dataclass
class ExecutionTrace:
    """
    Complete execution trace for a pipeline run.

    Contains all spans with timing, input/output, and usage information.
    """
    trace_id: str
    run_id: str
    pipeline_id: str
    pipeline_name: Optional[str] = None

    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: int = 0

    # Status
    success: bool = False
    error: Optional[str] = None

    # Spans
    spans: List[Span] = field(default_factory=list)

    # Aggregated usage
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_span(self, span: Span) -> None:
        """Add a span to the trace."""
        self.spans.append(span)

    def finalize(self) -> "ExecutionTrace":
        """Finalize trace by aggregating usage and setting end time."""
        self.end_time = datetime.now(timezone.utc)
        if self.start_time and self.end_time:
            self.duration_ms = int(
                (self.end_time - self.start_time).total_seconds() * 1000
            )

        # Aggregate usage from all spans
        for span in self.spans:
            self.total_input_tokens += span.input_tokens
            self.total_output_tokens += span.output_tokens
            self.total_tokens += span.total_tokens
            self.total_cost_usd += span.cost_usd

        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "pipeline_id": self.pipeline_id,
            "pipeline_name": self.pipeline_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "spans": [s.to_dict() for s in self.spans],
            "usage": {
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_tokens": self.total_tokens,
                "total_cost_usd": self.total_cost_usd,
            },
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Export trace as JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


class ExecutionTracer:
    """
    Tracer for capturing execution details.

    Creates and manages spans for a pipeline execution,
    building a complete trace that can be exported.
    """

    def __init__(
        self,
        run_id: str,
        pipeline_id: str,
        pipeline_name: Optional[str] = None,
    ):
        """
        Initialize tracer.

        Args:
            run_id: Unique run identifier
            pipeline_id: Pipeline identifier
            pipeline_name: Optional pipeline name
        """
        self.trace_id = str(uuid.uuid4())
        self.run_id = run_id
        self.pipeline_id = pipeline_id
        self.pipeline_name = pipeline_name

        self._trace = ExecutionTrace(
            trace_id=self.trace_id,
            run_id=run_id,
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            start_time=datetime.now(timezone.utc),
        )

        self._span_stack: List[Span] = []
        self._current_span: Optional[Span] = None

    def create_span(
        self,
        name: str,
        node_id: Optional[str] = None,
        node_type: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Span:
        """
        Create a new span.

        Args:
            name: Span name
            node_id: Optional node ID
            node_type: Optional node type
            provider: Optional provider name
            model: Optional model name

        Returns:
            New Span instance
        """
        parent_id = self._current_span.span_id if self._current_span else None

        span = Span(
            span_id=str(uuid.uuid4()),
            name=name,
            trace_id=self.trace_id,
            parent_span_id=parent_id,
            node_id=node_id,
            node_type=node_type,
            provider=provider,
            model=model,
        )

        return span

    @contextmanager
    def span(
        self,
        name: str,
        node_id: Optional[str] = None,
        node_type: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Context manager for creating and tracking a span.

        Usage:
            with tracer.span("node_execution", node_id="gen-1") as span:
                span.set_input(inputs)
                result = await execute(...)
                span.set_output(result)

        Args:
            name: Span name
            node_id: Optional node ID
            node_type: Optional node type
            provider: Optional provider name
            model: Optional model name

        Yields:
            Span instance
        """
        span = self.create_span(
            name=name,
            node_id=node_id,
            node_type=node_type,
            provider=provider,
            model=model,
        )

        # Push to stack
        if self._current_span:
            self._span_stack.append(self._current_span)
        self._current_span = span

        span.start()

        try:
            yield span
            if span.status == SpanStatus.RUNNING:
                span.end(SpanStatus.SUCCESS)
        except Exception as e:
            span.set_error(str(e), type(e).__name__)
            span.end(SpanStatus.ERROR)
            raise
        finally:
            # Add to trace
            self._trace.add_span(span)

            # Pop from stack
            if self._span_stack:
                self._current_span = self._span_stack.pop()
            else:
                self._current_span = None

    def record_span(self, span: Span) -> None:
        """Record a completed span directly."""
        self._trace.add_span(span)

    def set_success(self, success: bool) -> None:
        """Set overall trace success status."""
        self._trace.success = success

    def set_error(self, error: str) -> None:
        """Set overall trace error."""
        self._trace.error = error
        self._trace.success = False

    def set_metadata(self, key: str, value: Any) -> None:
        """Set trace metadata."""
        self._trace.metadata[key] = value

    def finalize(self) -> ExecutionTrace:
        """Finalize and return the complete trace."""
        return self._trace.finalize()

    def get_trace(self) -> ExecutionTrace:
        """Get the current trace (may not be finalized)."""
        return self._trace


def create_tracer_from_context(
    run_id: str,
    pipeline_id: str,
    pipeline_name: Optional[str] = None,
) -> ExecutionTracer:
    """
    Factory function to create a tracer.

    Args:
        run_id: Unique run identifier
        pipeline_id: Pipeline identifier
        pipeline_name: Optional pipeline name

    Returns:
        ExecutionTracer instance
    """
    return ExecutionTracer(
        run_id=run_id,
        pipeline_id=pipeline_id,
        pipeline_name=pipeline_name,
    )
