"""
FlowMason OpenTelemetry Instrumentation

Provides decorators and utilities for instrumenting pipeline components.
"""

import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from .tracer import get_tracer, SpanKind

F = TypeVar("F", bound=Callable[..., Any])


def trace_pipeline(
    pipeline_name: Optional[str] = None,
    include_input: bool = False,
    include_output: bool = False,
) -> Callable[[F], F]:
    """
    Decorator to trace a pipeline execution function.

    Usage:
        @trace_pipeline("my-pipeline")
        async def run_my_pipeline(input_data: dict) -> dict:
            # Pipeline logic
            return result
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            name = pipeline_name or func.__name__

            # Extract input if provided
            input_data = None
            if include_input and args:
                input_data = args[0] if isinstance(args[0], dict) else None

            with tracer.start_pipeline_span(
                pipeline_name=name,
                input_data=input_data,
            ) as span:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)

                    # Record output info
                    if span and include_output and isinstance(result, dict):
                        span.set_attribute(
                            "flowmason.pipeline.output_keys",
                            ",".join(result.keys()),
                        )

                    if span:
                        span.set_attribute(
                            "flowmason.pipeline.duration_ms",
                            int((time.time() - start_time) * 1000),
                        )
                        tracer.set_span_status(span, success=True)

                    return result

                except Exception as e:
                    if span:
                        tracer.record_exception(span, e)
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            name = pipeline_name or func.__name__

            input_data = None
            if include_input and args:
                input_data = args[0] if isinstance(args[0], dict) else None

            with tracer.start_pipeline_span(
                pipeline_name=name,
                input_data=input_data,
            ) as span:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)

                    if span and include_output and isinstance(result, dict):
                        span.set_attribute(
                            "flowmason.pipeline.output_keys",
                            ",".join(result.keys()),
                        )

                    if span:
                        span.set_attribute(
                            "flowmason.pipeline.duration_ms",
                            int((time.time() - start_time) * 1000),
                        )
                        tracer.set_span_status(span, success=True)

                    return result

                except Exception as e:
                    if span:
                        tracer.record_exception(span, e)
                    raise

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)

    return decorator


def trace_stage(
    stage_name: Optional[str] = None,
    component_type: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Decorator to trace a stage execution function.

    Usage:
        @trace_stage("my-stage", component_type="generator")
        async def execute_stage(input_data: dict) -> dict:
            # Stage logic
            return result
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            name = stage_name or func.__name__

            with tracer.start_stage_span(
                stage_id=name,
                stage_name=name,
                component_type=component_type,
            ) as span:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)

                    if span:
                        span.set_attribute(
                            "flowmason.stage.duration_ms",
                            int((time.time() - start_time) * 1000),
                        )
                        tracer.set_span_status(span, success=True)

                    return result

                except Exception as e:
                    if span:
                        tracer.record_exception(span, e)
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            name = stage_name or func.__name__

            with tracer.start_stage_span(
                stage_id=name,
                stage_name=name,
                component_type=component_type,
            ) as span:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)

                    if span:
                        span.set_attribute(
                            "flowmason.stage.duration_ms",
                            int((time.time() - start_time) * 1000),
                        )
                        tracer.set_span_status(span, success=True)

                    return result

                except Exception as e:
                    if span:
                        tracer.record_exception(span, e)
                    raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)

    return decorator


def instrument_pipeline(
    pipeline_id: str,
    pipeline_name: str,
    run_id: Optional[str] = None,
) -> Any:
    """
    Context manager for instrumenting a pipeline execution.

    Usage:
        with instrument_pipeline("id-123", "my-pipeline", run_id="run-456") as span:
            # Execute pipeline
            if span:
                span.set_attribute("stages.count", 5)
    """
    tracer = get_tracer()
    return tracer.start_pipeline_span(
        pipeline_name=pipeline_name,
        pipeline_id=pipeline_id,
        run_id=run_id,
    )


def instrument_stage(
    stage_id: str,
    stage_name: Optional[str] = None,
    component_type: Optional[str] = None,
) -> Any:
    """
    Context manager for instrumenting a stage execution.

    Usage:
        with instrument_stage("stage-1", "my-stage", "generator") as span:
            # Execute stage
            if span:
                span.set_attribute("output.tokens", 150)
    """
    tracer = get_tracer()
    return tracer.start_stage_span(
        stage_id=stage_id,
        stage_name=stage_name,
        component_type=component_type,
    )


class PipelineInstrumentation:
    """
    Helper class for instrumenting entire pipeline executions.

    Usage:
        instrumentation = PipelineInstrumentation(pipeline_id, pipeline_name)

        with instrumentation.pipeline_span() as pipeline_span:
            for stage in stages:
                with instrumentation.stage_span(stage.id, stage.name, stage.type) as stage_span:
                    result = await execute_stage(stage)
                    instrumentation.record_stage_metrics(stage_span, stage, result)
    """

    def __init__(
        self,
        pipeline_id: str,
        pipeline_name: str,
        run_id: Optional[str] = None,
    ):
        self.pipeline_id = pipeline_id
        self.pipeline_name = pipeline_name
        self.run_id = run_id
        self.tracer = get_tracer()
        self._stage_count = 0
        self._successful_stages = 0
        self._failed_stages = 0
        self._total_duration_ms = 0

    def pipeline_span(self) -> Any:
        """Start the pipeline span."""
        return self.tracer.start_pipeline_span(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            run_id=self.run_id,
        )

    def stage_span(
        self,
        stage_id: str,
        stage_name: Optional[str] = None,
        component_type: Optional[str] = None,
    ) -> Any:
        """Start a stage span."""
        self._stage_count += 1
        return self.tracer.start_stage_span(
            stage_id=stage_id,
            stage_name=stage_name,
            component_type=component_type,
        )

    def llm_span(
        self,
        provider: str,
        model: str,
        operation: str = "generate",
    ) -> Any:
        """Start an LLM call span."""
        return self.tracer.start_llm_span(provider, model, operation)

    def record_stage_success(
        self,
        span: Any,
        duration_ms: int,
        output_tokens: Optional[int] = None,
        cost_usd: Optional[float] = None,
    ) -> None:
        """Record successful stage execution metrics."""
        self._successful_stages += 1
        self._total_duration_ms += duration_ms

        if span is None:
            return

        span.set_attribute("flowmason.stage.duration_ms", duration_ms)
        span.set_attribute("flowmason.stage.success", True)

        if output_tokens:
            span.set_attribute("flowmason.stage.output_tokens", output_tokens)
        if cost_usd:
            span.set_attribute("flowmason.stage.cost_usd", cost_usd)

        self.tracer.set_span_status(span, success=True)

    def record_stage_failure(
        self,
        span: Any,
        exception: Exception,
        duration_ms: int,
    ) -> None:
        """Record failed stage execution."""
        self._failed_stages += 1
        self._total_duration_ms += duration_ms

        if span is None:
            return

        span.set_attribute("flowmason.stage.duration_ms", duration_ms)
        span.set_attribute("flowmason.stage.success", False)

        self.tracer.record_exception(span, exception)

    def record_pipeline_complete(
        self,
        span: Any,
        success: bool,
        total_duration_ms: int,
        total_tokens: Optional[int] = None,
        total_cost_usd: Optional[float] = None,
    ) -> None:
        """Record pipeline completion metrics."""
        if span is None:
            return

        span.set_attribute("flowmason.pipeline.duration_ms", total_duration_ms)
        span.set_attribute("flowmason.pipeline.success", success)
        span.set_attribute("flowmason.pipeline.stage_count", self._stage_count)
        span.set_attribute("flowmason.pipeline.successful_stages", self._successful_stages)
        span.set_attribute("flowmason.pipeline.failed_stages", self._failed_stages)

        if total_tokens:
            span.set_attribute("flowmason.pipeline.total_tokens", total_tokens)
        if total_cost_usd:
            span.set_attribute("flowmason.pipeline.total_cost_usd", total_cost_usd)

        self.tracer.set_span_status(span, success=success)

    def add_event(
        self,
        span: Any,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an event to a span."""
        self.tracer.add_event(span, name, attributes)
