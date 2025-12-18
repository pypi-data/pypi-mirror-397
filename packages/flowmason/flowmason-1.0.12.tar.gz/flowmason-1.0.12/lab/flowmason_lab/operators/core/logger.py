"""
Logger Operator - Core FlowMason Component.

Emits structured logs during pipeline execution.
Essential for debugging, monitoring, and auditing.
"""

import logging
from typing import Any, Dict, Literal, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput

pipeline_logger = logging.getLogger("flowmason.pipeline")


@operator(
    name="logger",
    category="core",
    description="Emit structured logs during pipeline execution",
    icon="file-text",
    color="#78716C",
    version="1.0.0",
    author="FlowMason",
    tags=["logging", "debug", "monitoring", "audit", "core"],
)
class LoggerOperator:
    """
    Emit structured logs during pipeline execution.

    This operator enables:
    - Debug logging during development
    - Audit trails for compliance
    - Performance monitoring
    - Error tracking
    - Pipeline observability
    """

    class Input(OperatorInput):
        message: str = Field(
            description="Log message",
            examples=["Processing complete", "User data received"],
        )
        level: Literal["debug", "info", "warning", "error"] = Field(
            default="info",
            description="Log level",
        )
        data: Optional[Any] = Field(
            default=None,
            description="Additional data to include in log",
        )
        tags: Optional[Dict[str, str]] = Field(
            default=None,
            description="Structured tags for log filtering",
            examples=[{"component": "auth", "action": "login"}],
        )
        emit_to_trace: bool = Field(
            default=True,
            description="Include in execution trace",
        )
        passthrough: Optional[Any] = Field(
            default=None,
            description="Data to pass through unchanged (for chaining)",
        )

    class Output(OperatorOutput):
        logged: bool = Field(
            default=True,
            description="Whether the log was emitted"
        )
        log_id: str = Field(
            default="",
            description="Unique identifier for this log entry"
        )
        passthrough: Any = Field(
            default=None,
            description="Passthrough data unchanged"
        )

    class Config:
        deterministic: bool = True
        timeout_seconds: int = 5

    async def execute(self, input: Input, context) -> Output:
        """Execute logging."""
        import uuid
        from datetime import datetime

        log_id = str(uuid.uuid4())[:8]

        # Build structured log entry
        log_entry: Dict[str, Any] = {
            "log_id": log_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": input.level,
            "message": input.message,
        }

        if input.data is not None:
            log_entry["data"] = input.data

        if input.tags:
            log_entry["tags"] = input.tags

        # Add execution context if available
        if hasattr(context, "run_id"):
            log_entry["run_id"] = context.run_id
        if hasattr(context, "step_id"):
            log_entry["step_id"] = context.step_id
        if hasattr(context, "pipeline_id"):
            log_entry["pipeline_id"] = context.pipeline_id

        # Emit to Python logger
        log_method = getattr(pipeline_logger, input.level, pipeline_logger.info)
        log_method(
            f"[{log_id}] {input.message}",
            extra={"structured": log_entry}
        )

        # Emit to execution trace if requested
        if input.emit_to_trace and hasattr(context, "trace"):
            context.trace.add_log(log_entry)

        return self.Output(
            logged=True,
            log_id=log_id,
            passthrough=input.passthrough,
        )
