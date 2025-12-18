"""
Control Flow Handler for FlowMason.

Handles execution of control flow directives returned by control flow components.
Supports: conditional, router, foreach, trycatch, subpipeline, return.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Set

from flowmason_core.core.types import (
    ControlFlowDirective,
    ControlFlowType,
)
from flowmason_core.execution.types import (
    ComponentExecutionError,
    ComponentResult,
    ErrorType,
)

if TYPE_CHECKING:
    from flowmason_core.execution.universal_executor import DAGExecutor

logger = logging.getLogger(__name__)


@dataclass
class ControlFlowState:
    """Tracks control flow execution state within a pipeline run."""

    # Stages to skip (populated by conditional/router)
    skip_stages: Set[str] = field(default_factory=set)

    # Early return flag
    should_return: bool = False
    return_value: Any = None
    return_message: Optional[str] = None

    # Loop state (for foreach)
    loop_contexts: Dict[str, "LoopContext"] = field(default_factory=dict)

    # Try-catch state
    trycatch_contexts: Dict[str, "TryCatchState"] = field(default_factory=dict)

    # Subpipeline results
    subpipeline_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoopContext:
    """Tracks state for a foreach loop."""
    loop_stage_id: str
    items: List[Any]
    current_index: int = 0
    results: List[Any] = field(default_factory=list)
    loop_stages: List[str] = field(default_factory=list)
    item_variable: str = "item"
    index_variable: str = "index"
    parallel: bool = False
    max_parallel: int = 5
    break_on_error: bool = True
    is_complete: bool = False
    errors: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def current_item(self) -> Any:
        if self.current_index < len(self.items):
            return self.items[self.current_index]
        return None

    @property
    def has_more(self) -> bool:
        return self.current_index < len(self.items)

    def advance(self) -> bool:
        self.current_index += 1
        if self.current_index >= len(self.items):
            self.is_complete = True
            return False
        return True

    def get_loop_variables(self) -> Dict[str, Any]:
        """Get variables to inject for current iteration."""
        return {
            self.item_variable: self.current_item,
            self.index_variable: self.current_index,
            "loop_total": len(self.items),
            "loop_remaining": len(self.items) - self.current_index - 1,
            "loop_results": self.results,
        }


@dataclass
class TryCatchState:
    """Tracks state for a try-catch block."""
    trycatch_stage_id: str
    try_stages: List[str]
    catch_stages: List[str]
    finally_stages: List[str]
    error_scope: str = "propagate"  # "propagate" or "continue"
    current_phase: str = "try"  # "try", "catch", "finally"
    error: Optional[Exception] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    try_results: Dict[str, Any] = field(default_factory=dict)
    catch_results: Dict[str, Any] = field(default_factory=dict)
    finally_results: Dict[str, Any] = field(default_factory=dict)


# Type for subpipeline executor callback
SubPipelineExecutor = Callable[[str, Dict[str, Any], Optional[int]], Awaitable[Dict[str, Any]]]


class ControlFlowHandler:
    """
    Handles control flow directives during pipeline execution.

    This class is used by DAGExecutor to process control flow components
    and modify execution flow accordingly.
    """

    def __init__(
        self,
        dag_executor: "DAGExecutor",
        subpipeline_executor: Optional[SubPipelineExecutor] = None,
    ):
        """
        Initialize the control flow handler.

        Args:
            dag_executor: The DAG executor instance (for executing nested stages)
            subpipeline_executor: Optional callback to execute sub-pipelines.
                                  Signature: (pipeline_id, input_data, timeout_ms) -> result
        """
        self.dag_executor = dag_executor
        self.subpipeline_executor = subpipeline_executor
        self.state = ControlFlowState()

    def is_control_flow_output(self, output: Any) -> bool:
        """Check if output contains a control flow directive."""
        if output is None:
            return False

        # Check for directive in output dict
        if isinstance(output, dict):
            directive = output.get("directive")
            if directive and isinstance(directive, dict):
                return "directive_type" in directive

        # Check for directive attribute on output object
        if hasattr(output, "directive"):
            directive = output.directive
            if hasattr(directive, "directive_type"):
                return True
            if isinstance(directive, dict) and "directive_type" in directive:
                return True

        return False

    def get_directive(self, output: Any) -> Optional[ControlFlowDirective]:
        """Extract control flow directive from component output."""
        if output is None:
            return None

        directive_data = None

        # Extract from dict
        if isinstance(output, dict):
            directive_data = output.get("directive")
        # Extract from object attribute
        elif hasattr(output, "directive"):
            directive_data = output.directive

        if directive_data is None:
            return None

        # If already a ControlFlowDirective, return it
        if isinstance(directive_data, ControlFlowDirective):
            return directive_data

        # Convert dict to ControlFlowDirective
        if isinstance(directive_data, dict):
            try:
                return ControlFlowDirective(**directive_data)
            except Exception as e:
                logger.warning(f"Failed to parse control flow directive: {e}")
                return None

        return None

    def should_skip_stage(self, stage_id: str) -> bool:
        """Check if a stage should be skipped."""
        return stage_id in self.state.skip_stages

    def should_return_early(self) -> bool:
        """Check if pipeline should return early."""
        return self.state.should_return

    def get_return_value(self) -> Any:
        """Get the early return value."""
        return self.state.return_value

    async def handle_directive(
        self,
        stage_id: str,
        directive: ControlFlowDirective,
        result: ComponentResult,
        stage_map: Dict[str, Any],
        upstream_outputs: Dict[str, Any],
        completed_stages: Set[str],
    ) -> Dict[str, ComponentResult]:
        """
        Handle a control flow directive and return any additional results.

        Args:
            stage_id: The stage that produced the directive
            directive: The control flow directive
            result: The component result
            stage_map: Map of stage_id -> stage config
            upstream_outputs: Current upstream outputs
            completed_stages: Set of completed stage IDs

        Returns:
            Dict of additional stage results from nested execution
        """
        directive_type = directive.directive_type

        if isinstance(directive_type, str):
            directive_type = ControlFlowType(directive_type)

        logger.info(f"Handling control flow directive: {directive_type.value} from {stage_id}")

        if directive_type == ControlFlowType.CONDITIONAL:
            return await self._handle_conditional(stage_id, directive, stage_map)

        elif directive_type == ControlFlowType.ROUTER:
            return await self._handle_router(stage_id, directive, stage_map)

        elif directive_type == ControlFlowType.FOREACH:
            return await self._handle_foreach(
                stage_id, directive, result, stage_map, upstream_outputs, completed_stages
            )

        elif directive_type == ControlFlowType.TRYCATCH:
            return await self._handle_trycatch(
                stage_id, directive, result, stage_map, upstream_outputs, completed_stages
            )

        elif directive_type == ControlFlowType.SUBPIPELINE:
            return await self._handle_subpipeline(stage_id, directive, upstream_outputs)

        elif directive_type == ControlFlowType.RETURN:
            return self._handle_return(stage_id, directive, result)

        else:
            logger.warning(f"Unknown control flow directive type: {directive_type}")
            return {}

    async def _handle_conditional(
        self,
        stage_id: str,
        directive: ControlFlowDirective,
        stage_map: Dict[str, Any],
    ) -> Dict[str, ComponentResult]:
        """Handle conditional (if/else) directive."""
        # Add skip_stages to the state
        for skip_id in directive.skip_stages:
            self.state.skip_stages.add(skip_id)
            logger.debug(f"Conditional {stage_id}: skipping stage {skip_id}")

        return {}

    async def _handle_router(
        self,
        stage_id: str,
        directive: ControlFlowDirective,
        stage_map: Dict[str, Any],
    ) -> Dict[str, ComponentResult]:
        """Handle router (switch/case) directive."""
        # Add skip_stages to the state
        for skip_id in directive.skip_stages:
            self.state.skip_stages.add(skip_id)
            logger.debug(f"Router {stage_id}: skipping stage {skip_id}")

        return {}

    async def _handle_foreach(
        self,
        stage_id: str,
        directive: ControlFlowDirective,
        result: ComponentResult,
        stage_map: Dict[str, Any],
        upstream_outputs: Dict[str, Any],
        completed_stages: Set[str],
    ) -> Dict[str, ComponentResult]:
        """
        Handle foreach (loop) directive.

        Executes loop_stages for each item in loop_items.
        """
        items = directive.loop_items or []
        if not items:
            logger.info(f"ForEach {stage_id}: no items to iterate")
            return {}

        metadata = directive.metadata or {}
        loop_stages = metadata.get("loop_stages", directive.execute_stages) or []
        item_variable = metadata.get("item_variable", "item")
        index_variable = metadata.get("index_variable", "index")
        parallel = metadata.get("parallel", False)
        max_parallel = metadata.get("max_parallel", 5)
        break_on_error = metadata.get("break_on_error", True)
        collect_results = metadata.get("collect_results", True)

        logger.info(f"ForEach {stage_id}: iterating over {len(items)} items, stages={loop_stages}")

        # Skip loop stages in main DAG - they'll be executed inline by this handler
        for skip_id in loop_stages:
            self.state.skip_stages.add(skip_id)

        # Get loop stage configs
        loop_stage_configs = [stage_map[sid] for sid in loop_stages if sid in stage_map]
        if not loop_stage_configs:
            logger.warning(f"ForEach {stage_id}: no valid loop stages found")
            return {}

        all_results: Dict[str, ComponentResult] = {}
        iteration_outputs: List[Any] = []

        if parallel:
            # Parallel execution with semaphore
            semaphore = asyncio.Semaphore(max_parallel)

            async def process_item(idx: int, item: Any) -> Dict[str, Any]:
                async with semaphore:
                    return await self._execute_loop_iteration(
                        loop_stage_id=stage_id,
                        iteration_index=idx,
                        item=item,
                        item_variable=item_variable,
                        index_variable=index_variable,
                        loop_stage_configs=loop_stage_configs,
                        upstream_outputs=upstream_outputs,
                        completed_stages=completed_stages,
                    )

            tasks = [process_item(idx, item) for idx, item in enumerate(items)]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)

            for idx, iter_result in enumerate(results_list):
                if isinstance(iter_result, BaseException):
                    if break_on_error:
                        raise iter_result
                    logger.error(f"ForEach {stage_id} iteration {idx} failed: {iter_result}")
                else:
                    all_results.update(iter_result.get("results", {}))
                    if collect_results:
                        iteration_outputs.append(iter_result.get("output"))
        else:
            # Sequential execution
            for idx, item in enumerate(items):
                try:
                    iter_result = await self._execute_loop_iteration(
                        loop_stage_id=stage_id,
                        iteration_index=idx,
                        item=item,
                        item_variable=item_variable,
                        index_variable=index_variable,
                        loop_stage_configs=loop_stage_configs,
                        upstream_outputs=upstream_outputs,
                        completed_stages=completed_stages,
                    )
                    all_results.update(iter_result.get("results", {}))
                    if collect_results:
                        iteration_outputs.append(iter_result.get("output"))
                except Exception as e:
                    if break_on_error:
                        raise
                    logger.error(f"ForEach {stage_id} iteration {idx} failed: {e}")

        # Update the original foreach stage result with collected outputs
        if result.output and isinstance(result.output, dict):
            result.output["results"] = iteration_outputs
            result.output["is_complete"] = True
            result.output["processed_items"] = len(items)

        return all_results

    async def _execute_loop_iteration(
        self,
        loop_stage_id: str,
        iteration_index: int,
        item: Any,
        item_variable: str,
        index_variable: str,
        loop_stage_configs: List[Any],
        upstream_outputs: Dict[str, Any],
        completed_stages: Set[str],
    ) -> Dict[str, Any]:
        """Execute a single loop iteration."""
        # Create iteration-specific upstream outputs with loop variables
        iter_upstream = {
            **upstream_outputs,
            # Add loop variables accessible via upstream.{foreach_stage_id}
            loop_stage_id: {
                **upstream_outputs.get(loop_stage_id, {}),
                "current_item": item,
                "current_index": iteration_index,
                item_variable: item,
                index_variable: iteration_index,
            }
        }

        # Also add loop variables at the context level
        self.dag_executor.context.variables = {
            **getattr(self.dag_executor.context, "variables", {}),
            item_variable: item,
            index_variable: iteration_index,
            "loop_item": item,
            "loop_index": iteration_index,
        }

        iter_results: Dict[str, ComponentResult] = {}
        last_output = None

        for stage_config in loop_stage_configs:
            iter_stage_id = f"{stage_config.id}_iter_{iteration_index}"

            result = await self.dag_executor.executor.execute_component(
                stage_config,
                iter_upstream,
            )

            iter_results[iter_stage_id] = result
            iter_upstream[stage_config.id] = result.output
            last_output = result.output

        return {
            "results": iter_results,
            "output": last_output,
        }

    async def _handle_trycatch(
        self,
        stage_id: str,
        directive: ControlFlowDirective,
        result: ComponentResult,
        stage_map: Dict[str, Any],
        upstream_outputs: Dict[str, Any],
        completed_stages: Set[str],
    ) -> Dict[str, ComponentResult]:
        """
        Handle try-catch directive.

        Executes try_stages, and if any fails, executes catch_stages.
        Always executes finally_stages at the end.

        Inspired by MuleSoft's error handling:
        - on-error-propagate: Execute catch, then re-raise
        - on-error-continue: Execute catch, then continue (swallow error)
        """
        metadata = directive.metadata or {}
        try_stages = metadata.get("try_stages", directive.execute_stages) or []
        catch_stages = metadata.get("catch_stages", directive.skip_stages) or []
        finally_stages = metadata.get("finally_stages", [])
        error_scope = metadata.get("error_scope", "propagate")
        catch_error_types = metadata.get("catch_error_types", [])

        logger.info(f"TryCatch {stage_id}: try={try_stages}, catch={catch_stages}, finally={finally_stages}")

        all_results: Dict[str, ComponentResult] = {}
        caught_error: Optional[Exception] = None
        caught_error_type: Optional[str] = None
        caught_error_message: Optional[str] = None

        # Skip all try/catch/finally stages in the main DAG execution
        # We'll execute them inline here
        for skip_id in try_stages + catch_stages + finally_stages:
            self.state.skip_stages.add(skip_id)

        # Get stage configs
        try_stage_configs = [stage_map[sid] for sid in try_stages if sid in stage_map]
        catch_stage_configs = [stage_map[sid] for sid in catch_stages if sid in stage_map]
        finally_stage_configs = [stage_map[sid] for sid in finally_stages if sid in stage_map]

        # Create a working copy of upstream outputs
        try_upstream = {**upstream_outputs}

        # === PHASE 1: Execute try_stages ===
        try:
            for stage_config in try_stage_configs:
                logger.debug(f"TryCatch {stage_id}: executing try stage {stage_config.id}")

                try_result = await self.dag_executor.executor.execute_component(
                    stage_config,
                    try_upstream,
                )

                all_results[stage_config.id] = try_result
                try_upstream[stage_config.id] = try_result.output
                completed_stages.add(stage_config.id)

        except Exception as e:
            # Capture error details
            caught_error = e
            caught_error_type = type(e).__name__
            caught_error_message = str(e)
            logger.info(f"TryCatch {stage_id}: caught error in try block - {caught_error_type}: {caught_error_message}")

            # Check if we should catch this error type
            should_catch = True
            if catch_error_types:
                should_catch = caught_error_type in catch_error_types
                if not should_catch:
                    logger.info(f"TryCatch {stage_id}: error type {caught_error_type} not in catch list, will propagate")

        # === PHASE 2: Execute catch_stages (if error occurred and should be caught) ===
        if caught_error and catch_stage_configs:
            should_catch = True
            if catch_error_types:
                should_catch = caught_error_type in catch_error_types

            if should_catch:
                logger.info(f"TryCatch {stage_id}: executing catch stages")

                # Add error context to upstream outputs
                catch_upstream = {
                    **try_upstream,
                    stage_id: {
                        **upstream_outputs.get(stage_id, {}),
                        "error": caught_error_message,
                        "error_type": caught_error_type,
                        "error_occurred": True,
                    }
                }

                for stage_config in catch_stage_configs:
                    try:
                        logger.debug(f"TryCatch {stage_id}: executing catch stage {stage_config.id}")

                        catch_result = await self.dag_executor.executor.execute_component(
                            stage_config,
                            catch_upstream,
                        )

                        all_results[stage_config.id] = catch_result
                        catch_upstream[stage_config.id] = catch_result.output
                        completed_stages.add(stage_config.id)

                    except Exception as catch_err:
                        logger.error(f"TryCatch {stage_id}: catch stage {stage_config.id} failed: {catch_err}")
                        # Error in catch block is always propagated
                        raise

        # === PHASE 3: Execute finally_stages (always) ===
        if finally_stage_configs:
            logger.info(f"TryCatch {stage_id}: executing finally stages")

            # Use the latest upstream outputs
            finally_upstream = {**try_upstream}
            if caught_error:
                finally_upstream[stage_id] = {
                    **upstream_outputs.get(stage_id, {}),
                    "error": caught_error_message,
                    "error_type": caught_error_type,
                    "error_occurred": True,
                }

            for stage_config in finally_stage_configs:
                try:
                    logger.debug(f"TryCatch {stage_id}: executing finally stage {stage_config.id}")

                    finally_result = await self.dag_executor.executor.execute_component(
                        stage_config,
                        finally_upstream,
                    )

                    all_results[stage_config.id] = finally_result
                    finally_upstream[stage_config.id] = finally_result.output
                    completed_stages.add(stage_config.id)

                except Exception as finally_err:
                    logger.error(f"TryCatch {stage_id}: finally stage {stage_config.id} failed: {finally_err}")
                    # Error in finally block is always propagated
                    raise

        # === PHASE 4: Handle error propagation ===
        if caught_error:
            if error_scope == "propagate":
                # Re-raise the original error after catch/finally
                logger.info(f"TryCatch {stage_id}: propagating error after catch/finally")
                raise caught_error
            else:
                # error_scope == "continue" - swallow the error
                logger.info(f"TryCatch {stage_id}: continuing execution after catching error")

        # Update the original trycatch stage result
        if result.output is not None and isinstance(result.output, dict):
            result.output["status"] = "caught" if caught_error else "success"
            result.output["error_occurred"] = caught_error is not None
            result.output["error_message"] = caught_error_message
            result.output["error_type"] = caught_error_type
            result.output["recovered"] = caught_error is not None and error_scope == "continue"

        return all_results

    async def _handle_subpipeline(
        self,
        stage_id: str,
        directive: ControlFlowDirective,
        upstream_outputs: Dict[str, Any],
    ) -> Dict[str, ComponentResult]:
        """
        Handle subpipeline directive.

        Loads and executes another pipeline as a sub-routine.
        """
        metadata = directive.metadata or {}
        pipeline_id = metadata.get("pipeline_id")
        input_data = metadata.get("input_data", {})
        timeout_ms = metadata.get("timeout_ms", 60000)
        on_error = metadata.get("on_error", "propagate")
        default_result = metadata.get("default_result")

        if not pipeline_id:
            raise ComponentExecutionError(
                f"SubPipeline {stage_id}: pipeline_id is required",
                component_id=stage_id,
                error_type=ErrorType.VALIDATION,
            )

        logger.info(f"SubPipeline {stage_id}: executing pipeline {pipeline_id}")

        # Check if we have a subpipeline executor
        if not self.subpipeline_executor:
            logger.warning(f"SubPipeline {stage_id}: no subpipeline executor configured")
            self.state.subpipeline_results[stage_id] = {
                "pipeline_id": pipeline_id,
                "input_data": input_data,
                "status": "skipped",
                "message": "SubPipeline executor not configured",
            }
            return {}

        try:
            # Execute the sub-pipeline
            start_time = datetime.utcnow()
            result = await self.subpipeline_executor(pipeline_id, input_data, timeout_ms)
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Store the result
            self.state.subpipeline_results[stage_id] = {
                "pipeline_id": pipeline_id,
                "input_data": input_data,
                "status": "completed",
                "result": result,
                "execution_time_ms": execution_time_ms,
            }

            logger.info(f"SubPipeline {stage_id}: completed in {execution_time_ms}ms")

        except asyncio.TimeoutError:
            error_msg = f"SubPipeline {pipeline_id} timed out after {timeout_ms}ms"
            logger.error(f"SubPipeline {stage_id}: {error_msg}")

            if on_error == "propagate":
                raise ComponentExecutionError(
                    error_msg,
                    component_id=stage_id,
                    error_type=ErrorType.TIMEOUT,
                )
            elif on_error == "default":
                self.state.subpipeline_results[stage_id] = {
                    "pipeline_id": pipeline_id,
                    "status": "timeout",
                    "result": default_result,
                    "error": error_msg,
                }
            else:  # ignore
                self.state.subpipeline_results[stage_id] = {
                    "pipeline_id": pipeline_id,
                    "status": "timeout",
                    "result": None,
                    "error": error_msg,
                }

        except Exception as e:
            error_msg = f"SubPipeline {pipeline_id} failed: {str(e)}"
            logger.error(f"SubPipeline {stage_id}: {error_msg}")

            if on_error == "propagate":
                raise ComponentExecutionError(
                    error_msg,
                    component_id=stage_id,
                    error_type=ErrorType.EXECUTION,
                    cause=e,
                )
            elif on_error == "default":
                self.state.subpipeline_results[stage_id] = {
                    "pipeline_id": pipeline_id,
                    "status": "failed",
                    "result": default_result,
                    "error": error_msg,
                }
            else:  # ignore
                self.state.subpipeline_results[stage_id] = {
                    "pipeline_id": pipeline_id,
                    "status": "failed",
                    "result": None,
                    "error": error_msg,
                }

        return {}

    def _handle_return(
        self,
        stage_id: str,
        directive: ControlFlowDirective,
        result: ComponentResult,
    ) -> Dict[str, ComponentResult]:
        """Handle return (early exit) directive."""
        # Check if return was triggered
        if not directive.continue_execution:
            metadata = directive.metadata or {}
            self.state.should_return = True
            self.state.return_value = metadata.get("return_value")
            self.state.return_message = metadata.get("message")

            logger.info(f"Return {stage_id}: early exit triggered, value={self.state.return_value}")

        return {}

    def get_loop_variables(self, stage_id: str) -> Dict[str, Any]:
        """Get current loop variables for a stage within a loop."""
        for loop_id, ctx in self.state.loop_contexts.items():
            if stage_id in ctx.loop_stages:
                return ctx.get_loop_variables()
        return {}

    def reset(self) -> None:
        """Reset control flow state for a new execution."""
        self.state = ControlFlowState()
