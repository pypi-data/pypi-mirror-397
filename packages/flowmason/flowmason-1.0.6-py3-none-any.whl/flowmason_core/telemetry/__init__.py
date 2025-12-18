"""
FlowMason OpenTelemetry Integration

Provides distributed tracing for pipeline executions using OpenTelemetry.
"""

from .tracer import (
    FlowMasonTracer,
    get_tracer,
    configure_tracing,
    TracingConfig,
    SpanKind,
)
from .instrumentation import (
    instrument_pipeline,
    instrument_stage,
    trace_stage,
    trace_pipeline,
)
from .exporters import (
    configure_jaeger_exporter,
    configure_otlp_exporter,
    configure_console_exporter,
)

__all__ = [
    # Tracer
    "FlowMasonTracer",
    "get_tracer",
    "configure_tracing",
    "TracingConfig",
    "SpanKind",
    # Instrumentation
    "instrument_pipeline",
    "instrument_stage",
    "trace_stage",
    "trace_pipeline",
    # Exporters
    "configure_jaeger_exporter",
    "configure_otlp_exporter",
    "configure_console_exporter",
]
