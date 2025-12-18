"""
FlowMason OpenTelemetry Exporters

Provides configuration functions for different trace exporters.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Check for OpenTelemetry availability
try:
    from opentelemetry.sdk.trace.export import SpanExporter
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    SpanExporter = Any  # type: ignore


def configure_console_exporter() -> Optional[Any]:
    """
    Configure console exporter for development/debugging.

    Returns:
        ConsoleSpanExporter instance, or None if not available.

    Usage:
        from flowmason_core.telemetry import get_tracer, configure_console_exporter

        tracer = get_tracer()
        exporter = configure_console_exporter()
        if exporter:
            tracer.add_exporter(exporter)
    """
    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available")
        return None

    try:
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        exporter = ConsoleSpanExporter()
        logger.info("Console span exporter configured")
        return exporter

    except ImportError:
        logger.error("Console exporter not available")
        return None


def configure_otlp_exporter(
    endpoint: Optional[str] = None,
    headers: Optional[dict] = None,
    insecure: bool = False,
) -> Optional[Any]:
    """
    Configure OTLP exporter for sending traces to OpenTelemetry collectors.

    Args:
        endpoint: OTLP endpoint (default: http://localhost:4317)
        headers: Optional headers for authentication
        insecure: Use insecure connection (no TLS)

    Returns:
        OTLPSpanExporter instance, or None if not available.

    Usage:
        from flowmason_core.telemetry import get_tracer, configure_otlp_exporter

        tracer = get_tracer()
        exporter = configure_otlp_exporter(
            endpoint="http://otel-collector:4317",
            headers={"Authorization": "Bearer token"},
        )
        if exporter:
            tracer.add_exporter(exporter)
    """
    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available")
        return None

    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(
            endpoint=endpoint or "http://localhost:4317",
            headers=headers,
            insecure=insecure,
        )
        logger.info(f"OTLP span exporter configured: {endpoint or 'localhost:4317'}")
        return exporter

    except ImportError:
        logger.error(
            "OTLP exporter not available. Install with: "
            "pip install opentelemetry-exporter-otlp"
        )
        return None


def configure_otlp_http_exporter(
    endpoint: Optional[str] = None,
    headers: Optional[dict] = None,
) -> Optional[Any]:
    """
    Configure OTLP HTTP exporter for sending traces via HTTP.

    Args:
        endpoint: OTLP HTTP endpoint (default: http://localhost:4318/v1/traces)
        headers: Optional headers for authentication

    Returns:
        OTLPSpanExporter instance, or None if not available.
    """
    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available")
        return None

    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(
            endpoint=endpoint or "http://localhost:4318/v1/traces",
            headers=headers,
        )
        logger.info(
            f"OTLP HTTP span exporter configured: "
            f"{endpoint or 'localhost:4318/v1/traces'}"
        )
        return exporter

    except ImportError:
        logger.error(
            "OTLP HTTP exporter not available. Install with: "
            "pip install opentelemetry-exporter-otlp-proto-http"
        )
        return None


def configure_jaeger_exporter(
    agent_host_name: str = "localhost",
    agent_port: int = 6831,
    collector_endpoint: Optional[str] = None,
) -> Optional[Any]:
    """
    Configure Jaeger exporter for sending traces to Jaeger.

    Args:
        agent_host_name: Jaeger agent hostname
        agent_port: Jaeger agent port (UDP)
        collector_endpoint: Optional HTTP collector endpoint

    Returns:
        JaegerExporter instance, or None if not available.

    Usage:
        from flowmason_core.telemetry import get_tracer, configure_jaeger_exporter

        tracer = get_tracer()
        exporter = configure_jaeger_exporter(
            agent_host_name="jaeger",
            agent_port=6831,
        )
        if exporter:
            tracer.add_exporter(exporter)
    """
    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available")
        return None

    try:
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter

        if collector_endpoint:
            exporter = JaegerExporter(collector_endpoint=collector_endpoint)
            logger.info(f"Jaeger HTTP exporter configured: {collector_endpoint}")
        else:
            exporter = JaegerExporter(
                agent_host_name=agent_host_name,
                agent_port=agent_port,
            )
            logger.info(
                f"Jaeger UDP exporter configured: {agent_host_name}:{agent_port}"
            )

        return exporter

    except ImportError:
        logger.error(
            "Jaeger exporter not available. Install with: "
            "pip install opentelemetry-exporter-jaeger"
        )
        return None


def configure_zipkin_exporter(
    endpoint: Optional[str] = None,
) -> Optional[Any]:
    """
    Configure Zipkin exporter for sending traces to Zipkin.

    Args:
        endpoint: Zipkin endpoint (default: http://localhost:9411/api/v2/spans)

    Returns:
        ZipkinExporter instance, or None if not available.
    """
    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available")
        return None

    try:
        from opentelemetry.exporter.zipkin.json import ZipkinExporter

        exporter = ZipkinExporter(
            endpoint=endpoint or "http://localhost:9411/api/v2/spans",
        )
        logger.info(
            f"Zipkin exporter configured: "
            f"{endpoint or 'localhost:9411/api/v2/spans'}"
        )
        return exporter

    except ImportError:
        logger.error(
            "Zipkin exporter not available. Install with: "
            "pip install opentelemetry-exporter-zipkin"
        )
        return None


def configure_from_env() -> Optional[Any]:
    """
    Configure exporter based on environment variables.

    Environment variables:
        OTEL_EXPORTER_TYPE: console, otlp, jaeger, zipkin
        OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint
        OTEL_EXPORTER_JAEGER_AGENT_HOST: Jaeger agent host
        OTEL_EXPORTER_JAEGER_AGENT_PORT: Jaeger agent port
        OTEL_EXPORTER_ZIPKIN_ENDPOINT: Zipkin endpoint

    Returns:
        Configured exporter instance, or None.
    """
    import os

    exporter_type = os.environ.get("OTEL_EXPORTER_TYPE", "console").lower()

    if exporter_type == "console":
        return configure_console_exporter()

    elif exporter_type == "otlp":
        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        return configure_otlp_exporter(endpoint=endpoint)

    elif exporter_type == "otlp-http":
        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        return configure_otlp_http_exporter(endpoint=endpoint)

    elif exporter_type == "jaeger":
        host = os.environ.get("OTEL_EXPORTER_JAEGER_AGENT_HOST", "localhost")
        port = int(os.environ.get("OTEL_EXPORTER_JAEGER_AGENT_PORT", "6831"))
        return configure_jaeger_exporter(agent_host_name=host, agent_port=port)

    elif exporter_type == "zipkin":
        endpoint = os.environ.get("OTEL_EXPORTER_ZIPKIN_ENDPOINT")
        return configure_zipkin_exporter(endpoint=endpoint)

    else:
        logger.warning(f"Unknown exporter type: {exporter_type}")
        return None
