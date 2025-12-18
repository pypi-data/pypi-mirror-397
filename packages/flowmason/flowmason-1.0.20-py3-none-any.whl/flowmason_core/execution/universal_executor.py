"""
Universal Executor for FlowMason.

Executes ANY component type (node or operator) through a single code path.
No special cases. No hardcoded types. Everything loads from the registry.

Features:
- Timeout enforcement via asyncio.wait_for
- Retry logic with exponential backoff
- Error classification (MuleSoft-inspired)
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Type

from flowmason_core.config import (
    ComponentConfig,
    ExecutionContext,
    InputMapper,
    LLMHelper,
)
from flowmason_core.config.schema_validator import OutputValidator
from flowmason_core.execution.cancellation import CancellationToken
from flowmason_core.execution.control_flow_handler import ControlFlowHandler
from flowmason_core.execution.retry import with_retry
from flowmason_core.execution.types import (
    ComponentExecutionError,
    ComponentResult,
    ErrorType,
    ExecutionTracer,
    FlowMasonError,
    MappingExecutionError,
    RetryExhaustedError,
    TimeoutExecutionError,
    TraceSpan,
    UsageMetrics,
    ValidationExecutionError,
)
from flowmason_core.logging import MetricsCollector, StructuredLogger
from flowmason_core.registry import ComponentRegistry

# Module logger
logger = logging.getLogger(__name__)

# Default timeout in milliseconds (60 seconds for nodes, 30 seconds for operators)
DEFAULT_NODE_TIMEOUT_MS = 60000
DEFAULT_OPERATOR_TIMEOUT_MS = 30000

# Default max concurrency for parallel execution
DEFAULT_MAX_CONCURRENCY = 10


class ExecutionHooks(Protocol):
    """
    Protocol defining hooks that can be called during execution.

    Implementations can provide real-time updates for debugging,
    monitoring, or any other observability needs.
    """

    async def check_and_wait_at_stage(
        self,
        stage_id: str,
        stage_name: Optional[str] = None,
    ) -> bool:
        """
        Called BEFORE executing each stage. Return False to stop execution.

        Args:
            stage_id: The stage about to be executed
            stage_name: Display name of the stage

        Returns:
            True to continue execution, False to stop
        """
        ...

    async def on_stage_started(
        self,
        stage_id: str,
        component_type: str,
        stage_name: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Called when a stage starts execution."""
        ...

    async def on_stage_completed(
        self,
        stage_id: str,
        component_type: str,
        status: str,
        output: Any = None,
        duration_ms: Optional[int] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        stage_name: Optional[str] = None,
    ) -> None:
        """Called when a stage completes successfully."""
        ...

    async def on_stage_failed(
        self,
        stage_id: str,
        component_type: str,
        error: str,
        stage_name: Optional[str] = None,
    ) -> None:
        """Called when a stage fails."""
        ...

    async def on_run_started(
        self,
        pipeline_id: str,
        stage_ids: List[str],
        inputs: Dict[str, Any],
    ) -> None:
        """Called when a run starts."""
        ...

    async def on_run_completed(
        self,
        pipeline_id: str,
        status: str,
        output: Any = None,
        total_duration_ms: Optional[int] = None,
        total_input_tokens: Optional[int] = None,
        total_output_tokens: Optional[int] = None,
    ) -> None:
        """Called when a run completes successfully."""
        ...

    async def on_run_failed(
        self,
        pipeline_id: str,
        error: str,
        failed_stage_id: Optional[str] = None,
    ) -> None:
        """Called when a run fails."""
        ...


class UniversalExecutor:
    """
    Executes ANY component type (node or operator) uniformly.

    This is the core of FlowMason's universal architecture.
    There is ONE code path for ALL component types.

    The execution flow:
    1. Load component class from registry
    2. Map config to Input model via InputMapper
    3. Execute the component
    4. Validate output
    5. Return result with metrics

    Example:
        executor = UniversalExecutor(registry, context)

        # This works for ANY component type
        result = await executor.execute_component(
            ComponentConfig(type="generator", ...),
            upstream_outputs={}
        )

        # Same code path for custom components
        result = await executor.execute_component(
            ComponentConfig(type="support_triage", ...),
            upstream_outputs={"classify": {...}}
        )
    """

    def __init__(
        self,
        registry: ComponentRegistry,
        context: ExecutionContext,
        tracer: Optional[ExecutionTracer] = None
    ):
        """
        Initialize the executor.

        Args:
            registry: Component registry for loading components
            context: Execution context with providers and pipeline info
            tracer: Optional tracer for observability
        """
        self.registry = registry
        self.context = context
        self.mapper = InputMapper(context)
        self.output_validator = OutputValidator()
        self.tracer = tracer or ExecutionTracer(trace_id=context.trace_id)

    async def execute_component(
        self,
        component_config: ComponentConfig,
        upstream_outputs: Optional[Dict[str, Any]] = None
    ) -> ComponentResult:
        """
        Execute any component type uniformly.

        This is THE universal execution method. It works for:
        - Nodes (AI components)
        - Operators (utility components)
        - Any future component types

        Features:
        - Timeout enforcement via asyncio.wait_for
        - Retry logic with exponential backoff for recoverable errors
        - Error classification (MuleSoft-inspired)

        Args:
            component_config: Configuration for the component
            upstream_outputs: Results from previously executed stages

        Returns:
            ComponentResult with output and metrics

        Raises:
            ComponentExecutionError: If execution fails
            MappingExecutionError: If input mapping fails
            ValidationExecutionError: If output validation fails
            TimeoutExecutionError: If execution times out
            RetryExhaustedError: If all retries are exhausted
        """
        upstream_outputs = upstream_outputs or {}

        # Start trace span
        with self.tracer.span(component_config.id) as span:
            span.set_attribute("component.type", component_config.type)
            span.set_attribute("component.id", component_config.id)

            started_at = datetime.utcnow()

            try:
                # Step 1: Load component from registry
                ComponentClass = self._load_component(component_config.type, span)

                # Step 2: Get component metadata
                metadata = self.registry.get_component_metadata(component_config.type)
                span.set_attribute("component.kind", metadata.component_kind)
                span.set_attribute("component.category", metadata.category)

                # Step 3: Map config to Input model
                component_input = self._map_input(
                    component_config,
                    ComponentClass,
                    upstream_outputs,
                    span
                )

                # Step 4: Create component instance
                component_instance = ComponentClass()

                # Step 5: Set up logger and metrics for this component
                component_logger = StructuredLogger(component_config.id)
                component_metrics = MetricsCollector()
                component_logger.info(
                    "Starting execution",
                    component_type=component_config.type,
                    run_id=self.context.run_id
                )
                component_metrics.start_timer("execution")

                # Step 6: Determine timeout
                timeout_ms = self._get_timeout(component_config, metadata)
                span.set_attribute("timeout_ms", timeout_ms)

                # Step 7: Execute with context (including logger and metrics)
                stage_context = self.context.with_stage(component_config.id)
                stage_context.logger = component_logger
                stage_context.metrics = component_metrics

                # Step 8: Execute with timeout and optional retry
                result_output = await self._execute_with_timeout_and_retry(
                    component_instance=component_instance,
                    component_input=component_input,
                    stage_context=stage_context,
                    component_config=component_config,
                    timeout_ms=timeout_ms,
                    span=span,
                )

                # Step 9: Stop timer and log completion
                execution_time_ms = component_metrics.stop_timer("execution")
                component_logger.info(
                    "Execution completed",
                    duration_ms=execution_time_ms,
                    status="success"
                )

                # Step 10: Validate output
                self._validate_output(result_output, ComponentClass, span)

                # Step 11: Extract usage metrics
                usage = self._extract_usage(result_output, started_at)

                span.set_attribute("status", "success")

                return ComponentResult(
                    component_id=component_config.id,
                    component_type=component_config.type,
                    status="success",
                    output=result_output.to_dict() if hasattr(result_output, 'to_dict') else result_output,
                    usage=usage,
                    trace_id=span.trace_id,
                    span_id=span.span_id,
                    started_at=started_at,
                    completed_at=datetime.utcnow(),
                )

            except (ComponentExecutionError, MappingExecutionError, ValidationExecutionError,
                    TimeoutExecutionError, RetryExhaustedError) as e:
                span.set_attribute("status", "error")
                if isinstance(e, FlowMasonError):
                    span.set_attribute("error.type", e.error_type.value)
                logger.error(
                    f"[{component_config.id}] Execution failed: {e}",
                    exc_info=True
                )
                raise

            except asyncio.CancelledError:
                span.set_attribute("status", "cancelled")
                logger.info(f"[{component_config.id}] Execution cancelled")
                raise

            except Exception as e:
                span.set_attribute("status", "error")
                span.set_attribute("error.message", str(e))
                logger.error(
                    f"[{component_config.id}] Unexpected error: {e}",
                    exc_info=True
                )
                raise ComponentExecutionError(
                    f"Component execution failed: {e}",
                    component_id=component_config.id,
                    component_type=component_config.type,
                    cause=e
                )

    def _get_timeout(
        self,
        component_config: ComponentConfig,
        metadata: Any,
    ) -> int:
        """
        Determine the timeout for a component.

        Priority:
        1. ComponentConfig.timeout_ms (explicit config)
        2. Component metadata.timeout_seconds (decorator default)
        3. Default based on component kind (node vs operator)
        """
        # Explicit config timeout
        if component_config.timeout_ms:
            return component_config.timeout_ms

        # Metadata timeout (in seconds, convert to ms)
        if hasattr(metadata, 'timeout_seconds') and metadata.timeout_seconds:
            return int(metadata.timeout_seconds * 1000)

        # Default based on component kind
        if hasattr(metadata, 'component_kind'):
            if metadata.component_kind == "node":
                return DEFAULT_NODE_TIMEOUT_MS
            elif metadata.component_kind == "operator":
                return DEFAULT_OPERATOR_TIMEOUT_MS

        # Fallback
        return DEFAULT_NODE_TIMEOUT_MS

    async def _execute_with_timeout_and_retry(
        self,
        component_instance: Any,
        component_input: Any,
        stage_context: ExecutionContext,
        component_config: ComponentConfig,
        timeout_ms: int,
        span: TraceSpan,
    ) -> Any:
        """
        Execute a component with timeout enforcement and optional retry.

        Args:
            component_instance: The instantiated component
            component_input: Mapped input data
            stage_context: Execution context
            component_config: Component configuration
            timeout_ms: Timeout in milliseconds
            span: Trace span for observability

        Returns:
            Component output

        Raises:
            TimeoutExecutionError: If execution times out
            RetryExhaustedError: If all retries are exhausted
        """
        timeout_seconds = timeout_ms / 1000.0

        async def execute_once() -> Any:
            """Single execution attempt with timeout."""
            try:
                return await asyncio.wait_for(
                    component_instance.execute(component_input, stage_context),
                    timeout=timeout_seconds,
                )
            except asyncio.TimeoutError:
                raise TimeoutExecutionError(
                    component_id=component_config.id,
                    timeout_ms=timeout_ms,
                    component_type=component_config.type,
                )

        # Check if retry is configured
        retry_config = component_config.retry_config
        if retry_config and retry_config.max_retries > 0:
            span.set_attribute("retry.enabled", True)
            span.set_attribute("retry.max_retries", retry_config.max_retries)

            async def on_retry(attempt: int, error: Exception, delay: float) -> None:
                """Callback for retry logging."""
                span.set_attribute(f"retry.attempt_{attempt + 1}.error", str(error))
                logger.info(
                    f"[{component_config.id}] Retry {attempt + 1}/{retry_config.max_retries} "
                    f"after {delay:.2f}s: {error}"
                )

            return await with_retry(
                func=execute_once,
                config=retry_config,
                component_id=component_config.id,
                component_type=component_config.type,
                on_retry=on_retry,
            )
        else:
            # No retry configured, execute once
            return await execute_once()

    def _load_component(self, component_type: str, span: TraceSpan) -> Type:
        """Load component class from registry."""
        try:
            ComponentClass = self.registry.get_component_class(component_type)
            span.set_attribute("component.class", ComponentClass.__name__)
            return ComponentClass
        except Exception as e:
            raise ComponentExecutionError(
                f"Failed to load component '{component_type}': {e}",
                component_type=component_type,
                cause=e
            )

    def _map_input(
        self,
        component_config: ComponentConfig,
        ComponentClass: Type,
        upstream_outputs: Dict[str, Any],
        span: TraceSpan
    ) -> Any:
        """Map config to component Input."""
        try:
            # Get the Input class from the component
            if not hasattr(ComponentClass, 'Input'):
                raise MappingExecutionError(
                    f"Component {ComponentClass.__name__} has no Input class",
                    component_type=component_config.type
                )

            InputClass = ComponentClass.Input

            # Map config to Input
            component_input = self.mapper.map_config_to_input(
                component_config,
                InputClass,
                upstream_outputs
            )

            span.set_attribute("input.mapped", True)
            return component_input

        except MappingExecutionError:
            raise
        except Exception as e:
            raise MappingExecutionError(
                f"Input mapping failed: {e}",
                component_id=component_config.id,
                component_type=component_config.type,
                cause=e
            )

    def _validate_output(
        self,
        output: Any,
        ComponentClass: Type,
        span: TraceSpan
    ) -> None:
        """Validate component output."""
        if not hasattr(ComponentClass, 'Output'):
            span.set_attribute("output.validated", False)
            return

        OutputClass = ComponentClass.Output
        result = self.output_validator.validate_output(output, OutputClass)

        if not result.is_valid:
            errors = "; ".join(e.message for e in result.errors)
            raise ValidationExecutionError(
                f"Output validation failed: {errors}",
                component_type=ComponentClass.__name__
            )

        span.set_attribute("output.validated", True)

    def _extract_usage(self, output: Any, started_at: datetime) -> UsageMetrics:
        """Extract usage metrics from output."""
        duration_ms = int((datetime.utcnow() - started_at).total_seconds() * 1000)

        # Try to extract token counts from output if available
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        cost_usd = 0.0

        if hasattr(output, 'tokens_used'):
            total_tokens = output.tokens_used
        if hasattr(output, 'input_tokens'):
            input_tokens = output.input_tokens
        if hasattr(output, 'output_tokens'):
            output_tokens = output.output_tokens
        if hasattr(output, 'cost_usd'):
            cost_usd = output.cost_usd

        # Calculate total if not provided
        if total_tokens == 0 and (input_tokens > 0 or output_tokens > 0):
            total_tokens = input_tokens + output_tokens

        return UsageMetrics(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            duration_ms=duration_ms,
        )


class DAGExecutor:
    """
    Executes a complete DAG (pipeline) using the UniversalExecutor.

    Handles:
    - Topological ordering of stages
    - Wave-based parallel execution for independent stages
    - Dependency resolution
    - Error handling and partial results
    - Provider initialization and LLM helper setup
    - Execution hooks for debugging/monitoring
    - Cancellation support
    """

    def __init__(
        self,
        registry: ComponentRegistry,
        context: ExecutionContext,
        providers: Optional[Dict[str, Any]] = None,
        default_provider: Optional[str] = None,
        hooks: Optional[ExecutionHooks] = None,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        parallel_execution: bool = True,
    ):
        """
        Initialize the DAG executor.

        Args:
            registry: Component registry
            context: Execution context
            providers: Dict of provider name -> provider instance
            default_provider: Name of the default provider to use for LLMHelper
            hooks: Optional execution hooks for debugging/monitoring
            max_concurrency: Maximum number of stages to execute in parallel
            parallel_execution: Whether to enable parallel execution (default True)
        """
        self.registry = registry
        self.context = context
        self.hooks = hooks
        self.max_concurrency = max_concurrency
        self.parallel_execution = parallel_execution

        # Set up providers on context
        if providers:
            self.context.providers = providers

            # Set up LLMHelper with default provider
            default_prov_name = default_provider or next(iter(providers.keys()), None)
            if default_prov_name and default_prov_name in providers:
                self.context.llm = LLMHelper(providers[default_prov_name])

        self.tracer = ExecutionTracer(trace_id=context.trace_id)
        self.executor = UniversalExecutor(registry, context, self.tracer)
        self.control_flow_handler: Optional[ControlFlowHandler] = None

    async def execute(
        self,
        stages: list,
        pipeline_input: Dict[str, Any],
        cancellation_token: Optional[CancellationToken] = None,
    ) -> Dict[str, ComponentResult]:
        """
        Execute all stages in the DAG with parallel execution support.

        Independent stages (those with no shared dependencies) are executed
        in parallel using wave-based execution.

        Supports control flow components (conditional, router, foreach, trycatch, return).

        Args:
            stages: List of ComponentConfig stages
            pipeline_input: Original pipeline input
            cancellation_token: Optional token for cancellation support

        Returns:
            Dict mapping stage_id -> ComponentResult
        """
        # Update context with pipeline input
        self.context.pipeline_input = pipeline_input

        # Initialize control flow handler for this execution
        self.control_flow_handler = ControlFlowHandler(self)

        # Log DAG execution start
        dag_logger = StructuredLogger(f"dag:{self.context.pipeline_id}")
        dag_metrics = MetricsCollector()
        dag_metrics.start_timer("dag_execution")
        dag_logger.info(
            "Starting DAG execution",
            run_id=self.context.run_id,
            pipeline_id=self.context.pipeline_id,
            stage_count=len(stages),
            parallel_enabled=self.parallel_execution,
            max_concurrency=self.max_concurrency,
        )

        # Build stage map and dependency graph
        stage_map = {s.id: s for s in stages}
        results: Dict[str, ComponentResult] = {}
        upstream_outputs: Dict[str, Any] = {}
        completed_stages: set = set()
        failed_stage_id: Optional[str] = None

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrency)

        # Notify hooks that run has started
        if self.hooks:
            try:
                await self.hooks.on_run_started(
                    pipeline_id=self.context.pipeline_id,
                    stage_ids=[s.id for s in stages],
                    inputs=pipeline_input,
                )
            except Exception as e:
                logger.warning(f"Hook on_run_started failed: {e}")

        try:
            if self.parallel_execution:
                # Wave-based parallel execution
                await self._execute_parallel(
                    stages=stages,
                    stage_map=stage_map,
                    results=results,
                    upstream_outputs=upstream_outputs,
                    completed_stages=completed_stages,
                    semaphore=semaphore,
                    dag_logger=dag_logger,
                    dag_metrics=dag_metrics,
                    cancellation_token=cancellation_token,
                )
            else:
                # Sequential execution (backwards compatible)
                await self._execute_sequential(
                    stages=stages,
                    results=results,
                    upstream_outputs=upstream_outputs,
                    dag_logger=dag_logger,
                    dag_metrics=dag_metrics,
                    cancellation_token=cancellation_token,
                )

        except asyncio.CancelledError:
            dag_logger.info("DAG execution cancelled")
            if self.hooks:
                try:
                    await self.hooks.on_run_failed(
                        pipeline_id=self.context.pipeline_id,
                        error="Execution cancelled",
                        failed_stage_id=None,
                    )
                except Exception as hook_err:
                    logger.warning(f"Hook on_run_failed failed: {hook_err}")
            raise

        except Exception as e:
            failed_stage_id = getattr(e, 'component_id', None)
            dag_logger.error(f"DAG execution failed: {e}")
            dag_metrics.increment("stages_failed")

            if self.hooks:
                try:
                    await self.hooks.on_run_failed(
                        pipeline_id=self.context.pipeline_id,
                        error=str(e),
                        failed_stage_id=failed_stage_id,
                    )
                except Exception as hook_err:
                    logger.warning(f"Hook on_run_failed failed: {hook_err}")
            raise

        # Log completion
        dag_duration_ms = dag_metrics.stop_timer("dag_execution")
        dag_logger.info(
            "DAG execution completed",
            duration_ms=dag_duration_ms,
            stages_completed=len(results),
            parallel_enabled=self.parallel_execution,
        )

        # Notify hooks that run completed successfully
        if self.hooks and not failed_stage_id:
            try:
                total_usage = self.aggregate_usage(results)
                # Get final output from output stage or last completed stage
                final_output = self._get_final_output(stages, results)

                await self.hooks.on_run_completed(
                    pipeline_id=self.context.pipeline_id,
                    status="completed",
                    output=final_output,
                    total_duration_ms=int(dag_duration_ms),
                    total_input_tokens=total_usage.input_tokens,
                    total_output_tokens=total_usage.output_tokens,
                )
            except Exception as e:
                logger.warning(f"Hook on_run_completed failed: {e}")

        return results

    async def _execute_parallel(
        self,
        stages: list,
        stage_map: Dict[str, Any],
        results: Dict[str, ComponentResult],
        upstream_outputs: Dict[str, Any],
        completed_stages: set,
        semaphore: asyncio.Semaphore,
        dag_logger: StructuredLogger,
        dag_metrics: MetricsCollector,
        cancellation_token: Optional[CancellationToken] = None,
    ) -> None:
        """
        Execute stages in parallel waves.

        Each wave contains stages whose dependencies are satisfied.
        Within a wave, stages execute concurrently up to max_concurrency.
        Supports control flow components (conditional, router, foreach, trycatch, return).
        """
        remaining_stages = set(s.id for s in stages)
        wave_number = 0

        while remaining_stages:
            # Check for early return from control flow
            if self.control_flow_handler and self.control_flow_handler.should_return_early():
                dag_logger.info("Early return triggered, stopping execution")
                break

            # Check for cancellation
            if cancellation_token and cancellation_token.is_cancelled:
                raise asyncio.CancelledError(cancellation_token.reason)

            # Find stages ready to execute (all dependencies satisfied)
            ready_stages = self._get_ready_stages(
                remaining_stages, completed_stages, stage_map
            )

            if not ready_stages:
                # Check if remaining stages are all skipped by control flow
                skipped_remaining = all(
                    self.control_flow_handler and self.control_flow_handler.should_skip_stage(sid)
                    for sid in remaining_stages
                )
                if skipped_remaining:
                    dag_logger.info(f"All remaining stages skipped by control flow: {list(remaining_stages)}")
                    # Mark skipped stages as completed
                    for sid in list(remaining_stages):
                        skipped_result = ComponentResult(
                            component_id=sid,
                            component_type=stage_map[sid].type,
                            status="skipped",
                            output={"skipped": True, "reason": "control_flow"},
                            usage=UsageMetrics(),
                            started_at=datetime.utcnow(),
                            completed_at=datetime.utcnow(),
                        )
                        results[sid] = skipped_result
                        upstream_outputs[sid] = skipped_result.output
                        completed_stages.add(sid)
                        remaining_stages.remove(sid)
                    continue

                # No stages ready but some remaining - circular dependency
                remaining_ids = list(remaining_stages)
                raise ComponentExecutionError(
                    f"Circular dependency detected among stages: {remaining_ids}",
                    error_type=ErrorType.ROUTING,
                )

            wave_number += 1
            dag_logger.info(
                f"Executing wave {wave_number}",
                stages=list(ready_stages),
                count=len(ready_stages),
            )

            # Execute ready stages in parallel
            wave_results = await self._execute_wave(
                ready_stage_ids=ready_stages,
                stage_map=stage_map,
                upstream_outputs=upstream_outputs,
                semaphore=semaphore,
                dag_logger=dag_logger,
                dag_metrics=dag_metrics,
                cancellation_token=cancellation_token,
                completed_stages=completed_stages,
            )

            # Process wave results
            for stage_id, result in wave_results.items():
                if isinstance(result, Exception):
                    # Check if it's an early return cancellation
                    if isinstance(result, asyncio.CancelledError) and "Early return" in str(result):
                        dag_logger.info(f"Stage {stage_id} skipped due to early return")
                        continue
                    # Re-raise the first exception
                    raise result

                results[stage_id] = result
                upstream_outputs[stage_id] = result.output
                completed_stages.add(stage_id)
                remaining_stages.discard(stage_id)
                dag_metrics.increment("stages_completed")

    def _get_ready_stages(
        self,
        remaining: set,
        completed: set,
        stage_map: Dict[str, Any],
    ) -> set:
        """Get stages whose dependencies are all satisfied."""
        ready = set()
        for stage_id in remaining:
            stage = stage_map[stage_id]
            deps = set(stage.depends_on)
            if deps.issubset(completed):
                ready.add(stage_id)
        return ready

    async def _execute_wave(
        self,
        ready_stage_ids: set,
        stage_map: Dict[str, Any],
        upstream_outputs: Dict[str, Any],
        semaphore: asyncio.Semaphore,
        dag_logger: StructuredLogger,
        dag_metrics: MetricsCollector,
        cancellation_token: Optional[CancellationToken] = None,
        completed_stages: Optional[set] = None,
    ) -> Dict[str, Any]:
        """
        Execute a wave of stages in parallel.

        Supports control flow components by checking for directives after execution.

        Returns dict mapping stage_id -> ComponentResult or Exception
        """
        completed_stages = completed_stages or set()

        async def execute_with_semaphore(stage_id: str) -> tuple:
            """Execute a single stage with semaphore control."""
            stage = stage_map[stage_id]

            async with semaphore:
                # Check if stage should be skipped by control flow
                if self.control_flow_handler and self.control_flow_handler.should_skip_stage(stage_id):
                    dag_logger.info(f"Skipping stage {stage_id} (control flow)")
                    # Return a skipped result
                    skipped_result = ComponentResult(
                        component_id=stage_id,
                        component_type=stage.type,
                        status="skipped",
                        output={"skipped": True, "reason": "control_flow"},
                        usage=UsageMetrics(),
                        started_at=datetime.utcnow(),
                        completed_at=datetime.utcnow(),
                    )
                    return (stage_id, skipped_result, None)

                # Check for early return
                if self.control_flow_handler and self.control_flow_handler.should_return_early():
                    dag_logger.info(f"Early return triggered, skipping stage {stage_id}")
                    return (stage_id, asyncio.CancelledError("Early return"), None)

                # Check for cancellation before starting
                if cancellation_token and cancellation_token.is_cancelled:
                    return (stage_id, asyncio.CancelledError(cancellation_token.reason), None)

                # Check with hooks if we should continue
                if self.hooks:
                    try:
                        should_continue = await self.hooks.check_and_wait_at_stage(
                            stage_id=stage_id,
                            stage_name=getattr(stage, 'name', None) or stage_id,
                        )
                        if not should_continue:
                            dag_logger.info(f"Execution stopped at stage {stage_id} by hooks")
                            return (stage_id, asyncio.CancelledError("Stopped by hooks"), None)
                    except Exception as e:
                        logger.warning(f"Hook check_and_wait_at_stage failed: {e}")

                # Notify hooks that stage is starting
                if self.hooks:
                    try:
                        await self.hooks.on_stage_started(
                            stage_id=stage_id,
                            component_type=stage.type,
                            stage_name=getattr(stage, 'name', None) or stage_id,
                            input_data=upstream_outputs,
                        )
                    except Exception as e:
                        logger.warning(f"Hook on_stage_started failed: {e}")

                try:
                    # Track nested results from control flow directives
                    stage_nested_results = None

                    dag_logger.info(
                        "Executing stage",
                        stage_id=stage_id,
                        stage_type=stage.type,
                    )

                    result = await self.executor.execute_component(
                        stage,
                        {**upstream_outputs}
                    )

                    # Check if this is a control flow component with a directive
                    if self.control_flow_handler and self.control_flow_handler.is_control_flow_output(result.output):
                        directive = self.control_flow_handler.get_directive(result.output)
                        if directive:
                            dag_logger.info(f"Processing control flow directive from {stage_id}")
                            # Handle the directive (updates skip_stages, handles loops, etc.)
                            nested_results = await self.control_flow_handler.handle_directive(
                                stage_id=stage_id,
                                directive=directive,
                                result=result,
                                stage_map=stage_map,
                                upstream_outputs=upstream_outputs,
                                completed_stages=completed_stages,
                            )
                            # Merge nested results into upstream_outputs for template resolution
                            if nested_results:
                                for nested_id, nested_result in nested_results.items():
                                    upstream_outputs[nested_id] = nested_result.output
                            # Store nested_results to return with this stage's result
                            stage_nested_results = nested_results

                    # Notify hooks that stage completed
                    if self.hooks:
                        try:
                            await self.hooks.on_stage_completed(
                                stage_id=stage_id,
                                component_type=stage.type,
                                status="success",
                                output=result.output,
                                duration_ms=result.usage.duration_ms if result.usage else None,
                                input_tokens=result.usage.input_tokens if result.usage else None,
                                output_tokens=result.usage.output_tokens if result.usage else None,
                                stage_name=getattr(stage, 'name', None) or stage_id,
                            )
                        except Exception as e:
                            logger.warning(f"Hook on_stage_completed failed: {e}")

                    return (stage_id, result, stage_nested_results)

                except Exception as e:
                    dag_logger.error(f"Stage {stage_id} failed: {e}")

                    # Notify hooks that stage failed
                    if self.hooks:
                        try:
                            await self.hooks.on_stage_failed(
                                stage_id=stage_id,
                                component_type=stage.type,
                                error=str(e),
                                stage_name=getattr(stage, 'name', None) or stage_id,
                            )
                        except Exception as hook_err:
                            logger.warning(f"Hook on_stage_failed failed: {hook_err}")

                    # Add component_id to exception for error reporting
                    if not hasattr(e, 'component_id'):
                        setattr(e, 'component_id', stage_id)
                    return (stage_id, e, None)

        # Execute all ready stages concurrently
        tasks = [execute_with_semaphore(stage_id) for stage_id in ready_stage_ids]
        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results dict
        wave_results = {}
        for item in task_results:
            if isinstance(item, BaseException):
                # Task itself raised (shouldn't happen, but handle it)
                raise item
            stage_id, result, nested_results = item  # type: ignore[misc]
            wave_results[stage_id] = result
            # Merge nested results (from control flow stages like trycatch/foreach)
            # This marks nested stages as completed so they won't be re-executed
            if nested_results:
                wave_results.update(nested_results)

        return wave_results

    async def _execute_sequential(
        self,
        stages: list,
        results: Dict[str, ComponentResult],
        upstream_outputs: Dict[str, Any],
        dag_logger: StructuredLogger,
        dag_metrics: MetricsCollector,
        cancellation_token: Optional[CancellationToken] = None,
    ) -> None:
        """
        Execute stages sequentially (backwards compatible mode).
        Supports control flow components.
        """
        sorted_stages = self._topological_sort(stages)
        stage_map = {s.id: s for s in stages}
        completed_stages: set = set()

        for idx, stage in enumerate(sorted_stages):
            # Check for early return from control flow
            if self.control_flow_handler and self.control_flow_handler.should_return_early():
                dag_logger.info("Early return triggered, stopping execution")
                break

            # Check if stage should be skipped by control flow
            if self.control_flow_handler and self.control_flow_handler.should_skip_stage(stage.id):
                dag_logger.info(f"Skipping stage {stage.id} (control flow)")
                skipped_result = ComponentResult(
                    component_id=stage.id,
                    component_type=stage.type,
                    status="skipped",
                    output={"skipped": True, "reason": "control_flow"},
                    usage=UsageMetrics(),
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                )
                results[stage.id] = skipped_result
                upstream_outputs[stage.id] = skipped_result.output
                completed_stages.add(stage.id)
                continue

            # Check for cancellation
            if cancellation_token and cancellation_token.is_cancelled:
                raise asyncio.CancelledError(cancellation_token.reason)

            # Check with hooks if we should continue
            if self.hooks:
                try:
                    should_continue = await self.hooks.check_and_wait_at_stage(
                        stage_id=stage.id,
                        stage_name=getattr(stage, 'name', None) or stage.id,
                    )
                    if not should_continue:
                        dag_logger.info(f"Execution stopped at stage {stage.id} by hooks")
                        break
                except Exception as e:
                    logger.warning(f"Hook check_and_wait_at_stage failed: {e}")

            dag_logger.info(
                f"Executing stage {idx + 1}/{len(sorted_stages)}",
                stage_id=stage.id,
                stage_type=stage.type
            )

            # Notify hooks that stage is starting
            if self.hooks:
                try:
                    await self.hooks.on_stage_started(
                        stage_id=stage.id,
                        component_type=stage.type,
                        stage_name=getattr(stage, 'name', None) or stage.id,
                        input_data=upstream_outputs,
                    )
                except Exception as e:
                    logger.warning(f"Hook on_stage_started failed: {e}")

            try:
                result = await self.executor.execute_component(
                    stage,
                    {**upstream_outputs}
                )

                results[stage.id] = result
                upstream_outputs[stage.id] = result.output
                completed_stages.add(stage.id)
                dag_metrics.increment("stages_completed")

                # Check if this is a control flow component with a directive
                if self.control_flow_handler and self.control_flow_handler.is_control_flow_output(result.output):
                    directive = self.control_flow_handler.get_directive(result.output)
                    if directive:
                        dag_logger.info(f"Processing control flow directive from {stage.id}")
                        nested_results = await self.control_flow_handler.handle_directive(
                            stage_id=stage.id,
                            directive=directive,
                            result=result,
                            stage_map=stage_map,
                            upstream_outputs=upstream_outputs,
                            completed_stages=completed_stages,
                        )
                        # Merge nested results
                        if nested_results:
                            for nested_id, nested_result in nested_results.items():
                                results[nested_id] = nested_result
                                upstream_outputs[nested_id] = nested_result.output

                # Notify hooks that stage completed
                if self.hooks:
                    try:
                        await self.hooks.on_stage_completed(
                            stage_id=stage.id,
                            component_type=stage.type,
                            status="success",
                            output=result.output,
                            duration_ms=result.usage.duration_ms if result.usage else None,
                            input_tokens=result.usage.input_tokens if result.usage else None,
                            output_tokens=result.usage.output_tokens if result.usage else None,
                            stage_name=getattr(stage, 'name', None) or stage.id,
                        )
                    except Exception as e:
                        logger.warning(f"Hook on_stage_completed failed: {e}")

            except Exception as e:
                dag_logger.error(f"Stage {stage.id} failed: {e}")

                # Notify hooks that stage failed
                if self.hooks:
                    try:
                        await self.hooks.on_stage_failed(
                            stage_id=stage.id,
                            component_type=stage.type,
                            error=str(e),
                            stage_name=getattr(stage, 'name', None) or stage.id,
                        )
                    except Exception as hook_err:
                        logger.warning(f"Hook on_stage_failed failed: {hook_err}")

                # Add component_id to exception for error reporting
                if not hasattr(e, 'component_id'):
                    setattr(e, 'component_id', stage.id)
                raise

    def _topological_sort(self, stages: list) -> list:
        """
        Sort stages in topological order based on dependencies.
        Uses Kahn's algorithm.
        """
        in_degree = {s.id: len(s.depends_on) for s in stages}

        ready = [s for s in stages if len(s.depends_on) == 0]
        sorted_stages = []

        while ready:
            stage = ready.pop(0)
            sorted_stages.append(stage)

            for other in stages:
                if stage.id in other.depends_on:
                    in_degree[other.id] -= 1
                    if in_degree[other.id] == 0:
                        ready.append(other)

        if len(sorted_stages) != len(stages):
            return stages

        return sorted_stages

    def _get_final_output(
        self,
        stages: list,
        results: Dict[str, ComponentResult]
    ) -> Any:
        """Get the final output from the pipeline."""
        # Find terminal stages (no other stage depends on them)
        all_deps = set()
        for stage in stages:
            all_deps.update(stage.depends_on)

        terminal_stages = [s for s in stages if s.id not in all_deps]

        # If single terminal stage, return its output
        if len(terminal_stages) == 1 and terminal_stages[0].id in results:
            return results[terminal_stages[0].id].output

        # Multiple terminal stages - return dict of outputs
        if terminal_stages:
            return {
                s.id: results[s.id].output
                for s in terminal_stages
                if s.id in results
            }

        # Fallback - return last result
        if results:
            last_id = list(results.keys())[-1]
            return results[last_id].output

        return None

    def aggregate_usage(self, results: Dict[str, ComponentResult]) -> UsageMetrics:
        """Aggregate usage metrics from all stages."""
        total = UsageMetrics()
        for result in results.values():
            total = total + result.usage
        return total
