"""
FlowMason OpenTelemetry Tracer

Provides distributed tracing for pipeline executions.
"""

import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Union

logger = logging.getLogger(__name__)

# OpenTelemetry is an optional dependency
try:
    from opentelemetry import trace
    from opentelemetry.trace import (
        Span,
        SpanKind as OTelSpanKind,
        Status,
        StatusCode,
        Tracer,
    )
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from opentelemetry.context import Context
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    Span = Any  # type: ignore
    Tracer = Any  # type: ignore
    Context = Any  # type: ignore


class SpanKind(str, Enum):
    """Types of spans in FlowMason tracing."""
    PIPELINE = "pipeline"
    STAGE = "stage"
    LLM_CALL = "llm_call"
    HTTP_REQUEST = "http_request"
    DATABASE = "database"
    CONTROL_FLOW = "control_flow"


@dataclass
class TracingConfig:
    """Configuration for OpenTelemetry tracing."""
    # Service identification
    service_name: str = "flowmason"
    service_version: str = "1.0.0"
    environment: str = "development"

    # Exporter configuration
    exporter_type: str = "console"  # console, otlp, jaeger
    endpoint: Optional[str] = None  # OTLP/Jaeger endpoint

    # Sampling
    sampling_ratio: float = 1.0  # 1.0 = trace everything

    # Feature flags
    enabled: bool = True
    trace_llm_calls: bool = True
    trace_http_requests: bool = True
    include_input_output: bool = False  # May contain sensitive data

    # Additional resource attributes
    resource_attributes: Dict[str, str] = field(default_factory=dict)


class FlowMasonTracer:
    """
    OpenTelemetry tracer for FlowMason pipelines.

    Usage:
        tracer = FlowMasonTracer(TracingConfig(service_name="my-service"))

        with tracer.start_pipeline_span("my-pipeline", pipeline_id="123") as span:
            with tracer.start_stage_span("stage-1", component_type="generator") as stage_span:
                # Execute stage
                stage_span.set_attribute("output.length", len(result))
    """

    def __init__(self, config: Optional[TracingConfig] = None):
        """Initialize the tracer with configuration."""
        self.config = config or TracingConfig()
        self._tracer: Optional[Tracer] = None
        self._provider: Optional[Any] = None
        self._propagator = None

        if not OTEL_AVAILABLE:
            logger.warning(
                "OpenTelemetry not available. Install with: "
                "pip install opentelemetry-api opentelemetry-sdk"
            )
            return

        if not self.config.enabled:
            logger.info("OpenTelemetry tracing is disabled")
            return

        self._initialize_tracer()

    def _initialize_tracer(self) -> None:
        """Initialize the OpenTelemetry tracer."""
        if not OTEL_AVAILABLE:
            return

        # Create resource with service info
        resource_attrs = {
            SERVICE_NAME: self.config.service_name,
            "service.version": self.config.service_version,
            "deployment.environment": self.config.environment,
            "telemetry.sdk.name": "flowmason",
            **self.config.resource_attributes,
        }

        resource = Resource.create(resource_attrs)

        # Create tracer provider
        self._provider = TracerProvider(resource=resource)

        # Set as global provider
        trace.set_tracer_provider(self._provider)

        # Get tracer
        self._tracer = trace.get_tracer(
            "flowmason",
            self.config.service_version,
        )

        # Initialize propagator for distributed tracing
        self._propagator = TraceContextTextMapPropagator()

        logger.info(
            f"OpenTelemetry tracer initialized for service: {self.config.service_name}"
        )

    @property
    def is_enabled(self) -> bool:
        """Check if tracing is enabled and available."""
        return OTEL_AVAILABLE and self.config.enabled and self._tracer is not None

    def add_exporter(self, exporter: Any) -> None:
        """Add a span exporter to the tracer provider."""
        if not OTEL_AVAILABLE or not self._provider:
            return

        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        processor = BatchSpanProcessor(exporter)
        self._provider.add_span_processor(processor)

    @contextmanager
    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.STAGE,
        attributes: Optional[Dict[str, Any]] = None,
        parent: Optional[Context] = None,
    ) -> Generator[Optional[Span], None, None]:
        """Start a new span."""
        if not self.is_enabled:
            yield None
            return

        span_kind_map = {
            SpanKind.PIPELINE: OTelSpanKind.SERVER,
            SpanKind.STAGE: OTelSpanKind.INTERNAL,
            SpanKind.LLM_CALL: OTelSpanKind.CLIENT,
            SpanKind.HTTP_REQUEST: OTelSpanKind.CLIENT,
            SpanKind.DATABASE: OTelSpanKind.CLIENT,
            SpanKind.CONTROL_FLOW: OTelSpanKind.INTERNAL,
        }

        otel_kind = span_kind_map.get(kind, OTelSpanKind.INTERNAL)

        assert self._tracer is not None
        with self._tracer.start_as_current_span(
            name,
            kind=otel_kind,
            attributes=attributes or {},
            context=parent,
        ) as span:
            span.set_attribute("flowmason.span_kind", kind.value)
            yield span

    @contextmanager
    def start_pipeline_span(
        self,
        pipeline_name: str,
        pipeline_id: Optional[str] = None,
        run_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> Generator[Optional[Span], None, None]:
        """Start a span for a pipeline execution."""
        attributes = {
            "flowmason.pipeline.name": pipeline_name,
            "flowmason.span_type": "pipeline",
        }

        if pipeline_id:
            attributes["flowmason.pipeline.id"] = pipeline_id
        if run_id:
            attributes["flowmason.run.id"] = run_id
        if input_data and self.config.include_input_output:
            attributes["flowmason.pipeline.input_keys"] = ",".join(input_data.keys())

        with self.start_span(
            f"pipeline:{pipeline_name}",
            kind=SpanKind.PIPELINE,
            attributes=attributes,
        ) as span:
            yield span

    @contextmanager
    def start_stage_span(
        self,
        stage_id: str,
        stage_name: Optional[str] = None,
        component_type: Optional[str] = None,
        parent: Optional[Context] = None,
    ) -> Generator[Optional[Span], None, None]:
        """Start a span for a stage execution."""
        display_name = stage_name or stage_id
        attributes = {
            "flowmason.stage.id": stage_id,
            "flowmason.span_type": "stage",
        }

        if stage_name:
            attributes["flowmason.stage.name"] = stage_name
        if component_type:
            attributes["flowmason.stage.component_type"] = component_type

        with self.start_span(
            f"stage:{display_name}",
            kind=SpanKind.STAGE,
            attributes=attributes,
            parent=parent,
        ) as span:
            yield span

    @contextmanager
    def start_llm_span(
        self,
        provider: str,
        model: str,
        operation: str = "generate",
    ) -> Generator[Optional[Span], None, None]:
        """Start a span for an LLM call."""
        if not self.config.trace_llm_calls:
            yield None
            return

        attributes = {
            "flowmason.llm.provider": provider,
            "flowmason.llm.model": model,
            "flowmason.llm.operation": operation,
            "flowmason.span_type": "llm_call",
        }

        with self.start_span(
            f"llm:{provider}/{model}",
            kind=SpanKind.LLM_CALL,
            attributes=attributes,
        ) as span:
            yield span

    @contextmanager
    def start_http_span(
        self,
        method: str,
        url: str,
    ) -> Generator[Optional[Span], None, None]:
        """Start a span for an HTTP request."""
        if not self.config.trace_http_requests:
            yield None
            return

        attributes = {
            "http.method": method,
            "http.url": url,
            "flowmason.span_type": "http_request",
        }

        with self.start_span(
            f"{method} {url}",
            kind=SpanKind.HTTP_REQUEST,
            attributes=attributes,
        ) as span:
            yield span

    @contextmanager
    def start_control_flow_span(
        self,
        control_type: str,
        stage_id: str,
    ) -> Generator[Optional[Span], None, None]:
        """Start a span for a control flow operation."""
        attributes = {
            "flowmason.control_flow.type": control_type,
            "flowmason.control_flow.stage_id": stage_id,
            "flowmason.span_type": "control_flow",
        }

        with self.start_span(
            f"control:{control_type}",
            kind=SpanKind.CONTROL_FLOW,
            attributes=attributes,
        ) as span:
            yield span

    def record_exception(self, span: Optional[Span], exception: Exception) -> None:
        """Record an exception on a span."""
        if not self.is_enabled or span is None:
            return

        span.record_exception(exception)
        span.set_status(Status(StatusCode.ERROR, str(exception)))

    def set_span_status(
        self,
        span: Optional[Span],
        success: bool,
        message: Optional[str] = None,
    ) -> None:
        """Set the status of a span."""
        if not self.is_enabled or span is None:
            return

        if success:
            span.set_status(Status(StatusCode.OK, message))
        else:
            span.set_status(Status(StatusCode.ERROR, message))

    def add_event(
        self,
        span: Optional[Span],
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an event to a span."""
        if not self.is_enabled or span is None:
            return

        span.add_event(name, attributes=attributes or {})

    def inject_context(self, carrier: Dict[str, str]) -> None:
        """Inject trace context into a carrier for distributed tracing."""
        if not self.is_enabled or not self._propagator:
            return

        self._propagator.inject(carrier)

    def extract_context(self, carrier: Dict[str, str]) -> Optional[Context]:
        """Extract trace context from a carrier."""
        if not self.is_enabled or not self._propagator:
            return None

        return self._propagator.extract(carrier)

    def get_current_span(self) -> Optional[Span]:
        """Get the current active span."""
        if not self.is_enabled:
            return None
        return trace.get_current_span()

    def get_current_trace_id(self) -> Optional[str]:
        """Get the current trace ID as a hex string."""
        span = self.get_current_span()
        if span is None:
            return None

        context = span.get_span_context()
        if context.trace_id == 0:
            return None

        return format(context.trace_id, "032x")

    def shutdown(self) -> None:
        """Shutdown the tracer and flush pending spans."""
        if self._provider:
            self._provider.shutdown()


# Global tracer instance
_global_tracer: Optional[FlowMasonTracer] = None


def configure_tracing(config: Optional[TracingConfig] = None) -> FlowMasonTracer:
    """Configure global tracing with the given configuration."""
    global _global_tracer

    # Allow configuration from environment variables
    if config is None:
        config = TracingConfig(
            service_name=os.environ.get("OTEL_SERVICE_NAME", "flowmason"),
            environment=os.environ.get("OTEL_ENVIRONMENT", "development"),
            exporter_type=os.environ.get("OTEL_EXPORTER_TYPE", "console"),
            endpoint=os.environ.get("OTEL_EXPORTER_ENDPOINT"),
            enabled=os.environ.get("OTEL_TRACING_ENABLED", "true").lower() == "true",
        )

    _global_tracer = FlowMasonTracer(config)
    return _global_tracer


def get_tracer() -> FlowMasonTracer:
    """Get the global tracer instance."""
    global _global_tracer

    if _global_tracer is None:
        _global_tracer = FlowMasonTracer()

    return _global_tracer
