"""
FlowMason Trace Export

Export execution traces to various formats for debugging and analysis:
- JSON file export
- OpenTelemetry compatible format
- OTLP JSON format

Usage:
    from flowmason_studio.tracing import TraceExporter, export_trace_to_json

    exporter = TraceExporter(output_dir="./traces")
    exporter.export(trace)

    # Or use convenience functions
    json_str = export_trace_to_json(trace)
    export_trace_to_file(trace, "./my_trace.json")
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .tracer import ExecutionTrace, Span


@dataclass
class ExportConfig:
    """Configuration for trace export."""

    output_dir: str = "./traces"
    include_raw_content: bool = True
    max_content_size: int = 10000  # Max chars for raw prompt/response
    indent: int = 2
    timestamp_format: str = "%Y%m%d_%H%M%S"


class TraceExporter:
    """
    Export execution traces to files.

    Handles batching, formatting, and file management for trace exports.
    """

    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialize exporter.

        Args:
            config: Export configuration
        """
        self.config = config or ExportConfig()
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

    def export(self, trace: ExecutionTrace) -> str:
        """
        Export a trace to a JSON file.

        Args:
            trace: Execution trace to export

        Returns:
            Path to the exported file
        """
        timestamp = datetime.now().strftime(self.config.timestamp_format)
        filename = f"trace_{trace.run_id}_{timestamp}.json"
        filepath = os.path.join(self.config.output_dir, filename)

        trace_dict = self._prepare_trace(trace)

        with open(filepath, "w") as f:
            json.dump(trace_dict, f, indent=self.config.indent, default=str)

        return filepath

    def export_batch(self, traces: List[ExecutionTrace]) -> List[str]:
        """
        Export multiple traces.

        Args:
            traces: List of traces to export

        Returns:
            List of exported file paths
        """
        return [self.export(trace) for trace in traces]

    def _prepare_trace(self, trace: ExecutionTrace) -> Dict[str, Any]:
        """Prepare trace for export, applying content limits."""
        trace_dict = trace.to_dict()

        if not self.config.include_raw_content:
            # Remove raw content from spans
            for span in trace_dict.get("spans", []):
                span.pop("raw_prompt", None)
                span.pop("raw_response", None)
        else:
            # Truncate raw content if too large
            for span in trace_dict.get("spans", []):
                if "raw_prompt" in span and len(span["raw_prompt"]) > self.config.max_content_size:
                    span["raw_prompt"] = span["raw_prompt"][:self.config.max_content_size] + "..."
                if "raw_response" in span and len(span["raw_response"]) > self.config.max_content_size:
                    span["raw_response"] = span["raw_response"][:self.config.max_content_size] + "..."

        return trace_dict


def export_trace_to_json(trace: ExecutionTrace, indent: int = 2) -> str:
    """
    Export trace to JSON string.

    Args:
        trace: Execution trace
        indent: JSON indentation

    Returns:
        JSON string
    """
    return trace.to_json(indent=indent)


def export_trace_to_file(trace: ExecutionTrace, filepath: str, indent: int = 2) -> None:
    """
    Export trace to a specific file path.

    Args:
        trace: Execution trace
        filepath: Output file path
        indent: JSON indentation
    """
    with open(filepath, "w") as f:
        json.dump(trace.to_dict(), f, indent=indent, default=str)


def load_trace_from_file(filepath: str) -> Dict[str, Any]:
    """
    Load a trace from a JSON file.

    Args:
        filepath: Path to trace file

    Returns:
        Trace data as dictionary
    """
    with open(filepath, "r") as f:
        result = json.load(f)
        return dict(result) if isinstance(result, dict) else {}


def convert_to_opentelemetry(trace: ExecutionTrace) -> Dict[str, Any]:
    """
    Convert trace to OpenTelemetry-compatible format.

    Args:
        trace: Execution trace

    Returns:
        OpenTelemetry formatted trace
    """
    resource_spans = []

    for span in trace.spans:
        otel_span = {
            "traceId": trace.trace_id,
            "spanId": span.span_id,
            "parentSpanId": span.parent_span_id,
            "name": span.name,
            "kind": "SPAN_KIND_INTERNAL",
            "startTimeUnixNano": _datetime_to_nanos(span.start_time) if span.start_time else 0,
            "endTimeUnixNano": _datetime_to_nanos(span.end_time) if span.end_time else 0,
            "attributes": _convert_attributes(span),
            "status": {
                "code": "STATUS_CODE_OK" if span.status.value == "success" else "STATUS_CODE_ERROR",
                "message": span.error or "",
            },
        }

        # Add events
        if span.events:
            otel_span["events"] = [
                {
                    "name": event.name,
                    "timeUnixNano": _datetime_to_nanos(event.timestamp),
                    "attributes": [
                        {"key": k, "value": {"stringValue": str(v)}}
                        for k, v in event.attributes.items()
                    ],
                }
                for event in span.events
            ]

        resource_spans.append(otel_span)

    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "flowmason"}},
                        {"key": "pipeline.id", "value": {"stringValue": trace.pipeline_id}},
                        {"key": "run.id", "value": {"stringValue": trace.run_id}},
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {"name": "flowmason.tracer"},
                        "spans": resource_spans,
                    }
                ],
            }
        ]
    }


def export_trace_to_otlp_json(trace: ExecutionTrace, filepath: str) -> None:
    """
    Export trace in OTLP JSON format.

    Args:
        trace: Execution trace
        filepath: Output file path
    """
    otel_trace = convert_to_opentelemetry(trace)
    with open(filepath, "w") as f:
        json.dump(otel_trace, f, indent=2)


def _datetime_to_nanos(dt: datetime) -> int:
    """Convert datetime to nanoseconds since epoch."""
    return int(dt.timestamp() * 1_000_000_000)


def _convert_attributes(span: Span) -> List[Dict[str, Any]]:
    """Convert span attributes to OpenTelemetry format."""
    attributes = []

    # Add standard attributes
    if span.node_id:
        attributes.append({"key": "node.id", "value": {"stringValue": span.node_id}})
    if span.node_type:
        attributes.append({"key": "node.type", "value": {"stringValue": span.node_type}})
    if span.provider:
        attributes.append({"key": "llm.provider", "value": {"stringValue": span.provider}})
    if span.model:
        attributes.append({"key": "llm.model", "value": {"stringValue": span.model}})

    # Add token usage
    if span.total_tokens > 0:
        attributes.extend([
            {"key": "llm.input_tokens", "value": {"intValue": span.input_tokens}},
            {"key": "llm.output_tokens", "value": {"intValue": span.output_tokens}},
            {"key": "llm.total_tokens", "value": {"intValue": span.total_tokens}},
            {"key": "llm.cost_usd", "value": {"doubleValue": span.cost_usd}},
        ])

    # Add duration
    attributes.append({"key": "duration_ms", "value": {"intValue": span.duration_ms}})

    # Add custom attributes
    for key, value in span.attributes.items():
        if isinstance(value, bool):
            attributes.append({"key": key, "value": {"boolValue": value}})
        elif isinstance(value, int):
            attributes.append({"key": key, "value": {"intValue": value}})
        elif isinstance(value, float):
            attributes.append({"key": key, "value": {"doubleValue": value}})
        else:
            attributes.append({"key": key, "value": {"stringValue": str(value)}})

    return attributes
