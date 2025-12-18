"""
Execution Controller for FlowMason Studio.

Manages debug execution control including:
- Pause/resume/step execution
- Breakpoint handling
- Timeout management
- Integration with DAGExecutor via hooks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from flowmason_studio.api.websocket import (
    ConnectionManager,
    WebSocketEventType,
    get_connection_manager,
)
from flowmason_studio.models.debug import (
    DebugMode,
    DebugPauseEvent,
    DebugState,
    ExceptionBreakpointFilter,
    ExceptionInfo,
    RunExecutionEvent,
    StageExecutionEvent,
)

logger = logging.getLogger(__name__)


# Default pause timeout in seconds (5 minutes)
DEFAULT_PAUSE_TIMEOUT = 300


class ExecutionController:
    """
    Controls execution flow for debugging.

    Features:
    - Pause execution before/after any stage
    - Step through stages one at a time
    - Breakpoint support
    - Auto-resume after timeout
    - WebSocket event broadcasting
    """

    def __init__(
        self,
        run_id: str,
        ws_manager: Optional[ConnectionManager] = None,
        pause_timeout: int = DEFAULT_PAUSE_TIMEOUT,
        org_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
    ):
        """
        Initialize execution controller for a run.

        Args:
            run_id: The run ID this controller manages
            ws_manager: WebSocket manager for broadcasting events
            pause_timeout: Seconds to wait before auto-resume (default 5 min)
            org_id: Organization ID for usage tracking
            pipeline_id: Pipeline ID for usage tracking
        """
        self.run_id = run_id
        self.ws_manager = ws_manager or get_connection_manager()
        self.pause_timeout = pause_timeout
        self.org_id = org_id
        self.pipeline_id = pipeline_id

        # Debug state
        self._state = DebugState(run_id=run_id)
        self._resume_event = asyncio.Event()
        self._resume_event.set()  # Start in running state
        self._lock = asyncio.Lock()

        # Track execution progress
        self._completed_stages: List[str] = []
        self._pending_stages: List[str] = []
        self._current_stage_id: Optional[str] = None

    @property
    def mode(self) -> DebugMode:
        """Get current debug mode."""
        return self._state.mode

    @property
    def breakpoints(self) -> List[str]:
        """Get list of breakpoint stage IDs."""
        return list(self._state.breakpoints)

    @property
    def exception_breakpoints(self) -> List[str]:
        """Get list of exception breakpoint filters."""
        return list(self._state.exception_breakpoints)

    @property
    def current_stage_id(self) -> Optional[str]:
        """Get current stage being executed."""
        return self._current_stage_id

    async def _track_usage(
        self,
        stage_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: Optional[float] = None,
        duration_ms: int = 0,
    ):
        """
        Track LLM usage for a stage.

        Args:
            stage_id: The stage ID
            provider: LLM provider name
            model: Model name
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            cost_usd: Cost in USD (auto-calculated if None)
            duration_ms: Execution duration in milliseconds
        """
        if not self.org_id:
            # Skip tracking if no org_id (e.g., unauthenticated)
            return

        try:
            from flowmason_studio.services.usage_storage import get_usage_storage

            usage_storage = get_usage_storage()
            usage_storage.record_usage(
                org_id=self.org_id,
                run_id=self.run_id,
                pipeline_id=self.pipeline_id or "",
                stage_id=stage_id,
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd,
                duration_ms=duration_ms,
            )
            logger.debug(f"Tracked usage: {provider}/{model} - {input_tokens}+{output_tokens} tokens")
        except Exception as e:
            logger.warning(f"Failed to track usage: {e}")

    async def set_mode(self, mode: DebugMode, reason: Optional[str] = None):
        """
        Set the debug mode.

        Args:
            mode: New debug mode
            reason: Reason for mode change
        """
        async with self._lock:
            old_mode = self._state.mode
            self._state.mode = mode
            self._state.pause_reason = reason

            if mode == DebugMode.PAUSED:
                self._state.paused_at = datetime.utcnow()
                self._state.timeout_at = datetime.utcnow() + timedelta(seconds=self.pause_timeout)
                self._resume_event.clear()
            elif mode in [DebugMode.RUNNING, DebugMode.STEPPING]:
                self._state.paused_at = None
                self._state.timeout_at = None
                self._resume_event.set()
            elif mode == DebugMode.STOPPED:
                self._resume_event.set()  # Unblock any waiters

            logger.info(f"Run {self.run_id}: mode changed from {old_mode} to {mode} (reason: {reason})")

    async def set_breakpoints(self, stage_ids: List[str]):
        """
        Set breakpoints for the run.

        Args:
            stage_ids: List of stage IDs to break at
        """
        async with self._lock:
            self._state.breakpoints = list(stage_ids)
            logger.debug(f"Run {self.run_id}: breakpoints set to {stage_ids}")

    async def add_breakpoint(self, stage_id: str):
        """Add a breakpoint for a stage."""
        async with self._lock:
            if stage_id not in self._state.breakpoints:
                self._state.breakpoints.append(stage_id)
                logger.debug(f"Run {self.run_id}: breakpoint added at {stage_id}")

    async def remove_breakpoint(self, stage_id: str):
        """Remove a breakpoint for a stage."""
        async with self._lock:
            if stage_id in self._state.breakpoints:
                self._state.breakpoints.remove(stage_id)
                logger.debug(f"Run {self.run_id}: breakpoint removed from {stage_id}")

    async def set_exception_breakpoints(self, filters: List[str]):
        """
        Set exception breakpoints for the run.

        Args:
            filters: List of exception filter IDs (e.g., 'all', 'error', 'timeout')
        """
        async with self._lock:
            self._state.exception_breakpoints = list(filters)
            logger.debug(f"Run {self.run_id}: exception breakpoints set to {filters}")

    def should_pause_on_exception(
        self,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> bool:
        """
        Check if execution should pause based on exception breakpoint filters.

        Args:
            error_type: The FlowMason ErrorType (e.g., 'TIMEOUT', 'VALIDATION')
            severity: The error severity (e.g., 'ERROR', 'WARNING')

        Returns:
            True if execution should pause, False otherwise
        """
        if not self._state.exception_breakpoints:
            return False

        filters = self._state.exception_breakpoints

        # Check 'all' filter - pause on any error
        if ExceptionBreakpointFilter.ALL.value in filters:
            return True

        # Check severity-based filters
        if severity:
            severity_lower = severity.lower()
            if severity_lower == "error" and ExceptionBreakpointFilter.ERROR.value in filters:
                return True
            if severity_lower == "warning" and ExceptionBreakpointFilter.WARNING.value in filters:
                return True

        # Check error type-based filters
        if error_type:
            error_type_lower = error_type.lower()
            if error_type_lower == "timeout" and ExceptionBreakpointFilter.TIMEOUT.value in filters:
                return True
            if error_type_lower == "validation" and ExceptionBreakpointFilter.VALIDATION.value in filters:
                return True
            if error_type_lower == "connectivity" and ExceptionBreakpointFilter.CONNECTIVITY.value in filters:
                return True

        # Check 'uncaught' filter - treat all errors as uncaught for now
        if ExceptionBreakpointFilter.UNCAUGHT.value in filters:
            return True

        return False

    async def pause(self) -> bool:
        """
        Pause execution.

        Returns:
            True if pause was applied, False if already paused or stopped
        """
        if self._state.mode in [DebugMode.PAUSED, DebugMode.STOPPED]:
            return False

        await self.set_mode(DebugMode.PAUSED, reason="user_requested")
        await self._broadcast_pause_event()
        return True

    async def resume(self) -> bool:
        """
        Resume execution.

        Returns:
            True if resume was applied, False if not paused
        """
        if self._state.mode != DebugMode.PAUSED:
            return False

        await self.set_mode(DebugMode.RUNNING, reason="user_resumed")

        # Broadcast resume event
        await self.ws_manager.broadcast_run_event(
            self.run_id,
            WebSocketEventType.EXECUTION_RESUMED,
            {
                "stage_id": self._current_stage_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        return True

    async def step(self) -> bool:
        """
        Step to next stage (execute one stage then pause).

        Returns:
            True if step was applied
        """
        await self.set_mode(DebugMode.STEPPING, reason="step_mode")
        return True

    async def stop(self) -> bool:
        """
        Stop execution entirely.

        Returns:
            True if stop was applied
        """
        if self._state.mode == DebugMode.STOPPED:
            return False

        await self.set_mode(DebugMode.STOPPED, reason="user_stopped")
        return True

    async def check_and_wait_at_stage(
        self,
        stage_id: str,
        stage_name: Optional[str] = None,
    ) -> bool:
        """
        Check if execution should pause/continue at this stage.

        Called BEFORE executing each stage. If a breakpoint is set or
        we're in step mode, this will pause execution and wait for
        resume/step/stop.

        Args:
            stage_id: The stage about to be executed
            stage_name: Display name of the stage

        Returns:
            True if execution should continue, False if stopped
        """
        self._current_stage_id = stage_id
        self._state.current_stage_id = stage_id

        # Check if stopped
        if self._state.mode == DebugMode.STOPPED:
            logger.info(f"Run {self.run_id}: execution stopped before {stage_id}")
            return False

        # Check for breakpoint hit
        should_pause = False
        pause_reason = None

        if stage_id in self._state.breakpoints:
            should_pause = True
            pause_reason = "breakpoint"
            logger.info(f"Run {self.run_id}: breakpoint hit at {stage_id}")

        elif self._state.mode == DebugMode.STEPPING:
            should_pause = True
            pause_reason = "step_mode"
            logger.info(f"Run {self.run_id}: step mode pause at {stage_id}")

        elif self._state.mode == DebugMode.PAUSED:
            should_pause = True
            pause_reason = self._state.pause_reason or "paused"

        if should_pause:
            await self.set_mode(DebugMode.PAUSED, reason=pause_reason)
            await self._broadcast_pause_event(stage_name)

            # Wait for resume with timeout
            try:
                await asyncio.wait_for(
                    self._wait_for_resume(),
                    timeout=self.pause_timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Run {self.run_id}: pause timeout at {stage_id}, auto-resuming")
                await self.set_mode(DebugMode.RUNNING, reason="timeout_auto_resume")

        # Check if stopped while waiting
        if self._state.mode == DebugMode.STOPPED:
            return False

        return True

    async def _wait_for_resume(self):
        """Wait for the resume event to be set."""
        while not self._resume_event.is_set():
            await asyncio.sleep(0.1)
            # Check periodically if state changed
            if self._state.mode in [DebugMode.RUNNING, DebugMode.STEPPING, DebugMode.STOPPED]:
                return

    async def _broadcast_pause_event(self, stage_name: Optional[str] = None):
        """Broadcast pause event to WebSocket subscribers."""
        event = DebugPauseEvent(
            run_id=self.run_id,
            stage_id=self._current_stage_id or "",
            stage_name=stage_name,
            reason=self._state.pause_reason or "paused",
            timeout_seconds=self.pause_timeout,
            completed_stages=self._completed_stages.copy(),
            pending_stages=self._pending_stages.copy(),
        )

        await self.ws_manager.broadcast_run_event(
            self.run_id,
            WebSocketEventType.EXECUTION_PAUSED,
            event.model_dump(mode='json'),
        )

    async def on_stage_started(
        self,
        stage_id: str,
        component_type: str,
        stage_name: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Called when a stage starts execution.

        Args:
            stage_id: The stage ID
            component_type: Type of component being executed
            stage_name: Display name of the stage
            input_data: Input data passed to the stage
        """
        self._current_stage_id = stage_id

        event = StageExecutionEvent(
            run_id=self.run_id,
            stage_id=stage_id,
            stage_name=stage_name,
            component_type=component_type,
            event_type="started",
        )

        await self.ws_manager.broadcast_run_event(
            self.run_id,
            WebSocketEventType.STAGE_STARTED,
            {
                **event.model_dump(mode='json'),
                "input": input_data,
            },
        )

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
        provider: Optional[str] = None,
        model: Optional[str] = None,
        cost_usd: Optional[float] = None,
    ):
        """
        Called when a stage completes execution.

        Args:
            stage_id: The stage ID
            component_type: Type of component executed
            status: Completion status
            output: Output data from the stage
            duration_ms: Execution duration in milliseconds
            input_tokens: Input tokens used (for LLM calls)
            output_tokens: Output tokens used (for LLM calls)
            stage_name: Display name of the stage
            provider: LLM provider name (e.g., 'anthropic', 'openai')
            model: Model name (e.g., 'claude-3-5-sonnet-20241022')
            cost_usd: Cost in USD (calculated if not provided)
        """
        self._completed_stages.append(stage_id)
        if stage_id in self._pending_stages:
            self._pending_stages.remove(stage_id)

        # Track LLM usage if token info is available
        if input_tokens is not None and output_tokens is not None and provider:
            await self._track_usage(
                stage_id=stage_id,
                provider=provider,
                model=model or "unknown",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd,
                duration_ms=duration_ms or 0,
            )

        event = StageExecutionEvent(
            run_id=self.run_id,
            stage_id=stage_id,
            stage_name=stage_name,
            component_type=component_type,
            event_type="completed",
            status=status,
            duration_ms=duration_ms,
            output=output,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        await self.ws_manager.broadcast_run_event(
            self.run_id,
            WebSocketEventType.STAGE_COMPLETED,
            event.model_dump(mode='json'),
        )

    async def on_stage_failed(
        self,
        stage_id: str,
        component_type: str,
        error: str,
        stage_name: Optional[str] = None,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
    ) -> bool:
        """
        Called when a stage fails.

        Args:
            stage_id: The stage ID
            component_type: Type of component that failed
            error: Error message
            stage_name: Display name of the stage
            error_type: FlowMason ErrorType (e.g., 'TIMEOUT', 'VALIDATION')
            severity: Error severity (e.g., 'ERROR', 'WARNING')
            details: Additional error details
            stack_trace: Stack trace if available

        Returns:
            True if execution should continue, False if stopped
        """
        event = StageExecutionEvent(
            run_id=self.run_id,
            stage_id=stage_id,
            stage_name=stage_name,
            component_type=component_type,
            event_type="failed",
            status="failed",
            error=error,
        )

        await self.ws_manager.broadcast_run_event(
            self.run_id,
            WebSocketEventType.STAGE_FAILED,
            event.model_dump(mode='json'),
        )

        # Check if we should pause on this exception
        if self.should_pause_on_exception(error_type=error_type, severity=severity):
            import uuid

            # Create exception info
            exception_info = ExceptionInfo(
                exception_id=str(uuid.uuid4()),
                description=error,
                break_mode="always",
                error_type=error_type,
                severity=severity or "ERROR",
                stage_id=stage_id,
                stage_name=stage_name,
                component_type=component_type,
                details=details,
                stack_trace=stack_trace,
                recoverable=False,
            )

            # Store exception in state
            self._state.current_exception = exception_info
            self._current_stage_id = stage_id
            self._state.current_stage_id = stage_id

            # Pause execution
            await self.set_mode(DebugMode.PAUSED, reason="exception")

            # Broadcast pause event with exception info
            pause_event = DebugPauseEvent(
                run_id=self.run_id,
                stage_id=stage_id,
                stage_name=stage_name,
                reason="exception",
                timeout_seconds=self.pause_timeout,
                completed_stages=self._completed_stages.copy(),
                pending_stages=self._pending_stages.copy(),
                exception_info=exception_info,
            )

            await self.ws_manager.broadcast_run_event(
                self.run_id,
                WebSocketEventType.EXECUTION_PAUSED,
                pause_event.model_dump(mode='json'),
            )

            logger.info(f"Run {self.run_id}: paused on exception at {stage_id}: {error}")

            # Wait for resume with timeout
            try:
                await asyncio.wait_for(
                    self._wait_for_resume(),
                    timeout=self.pause_timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Run {self.run_id}: exception pause timeout at {stage_id}, auto-resuming")
                await self.set_mode(DebugMode.RUNNING, reason="timeout_auto_resume")

            # Clear exception info after resume
            self._state.current_exception = None

        # Check if stopped while waiting
        if self._state.mode == DebugMode.STOPPED:
            return False

        return True

    def get_exception_info(self) -> Optional[ExceptionInfo]:
        """Get information about the current exception (if paused due to exception)."""
        return self._state.current_exception

    async def on_run_started(
        self,
        pipeline_id: str,
        stage_ids: List[str],
        inputs: Dict[str, Any],
    ):
        """
        Called when a run starts.

        Args:
            pipeline_id: The pipeline being run
            stage_ids: List of stage IDs in execution order
            inputs: Pipeline input data
        """
        self._pending_stages = list(stage_ids)
        self._completed_stages = []

        event = RunExecutionEvent(
            run_id=self.run_id,
            pipeline_id=pipeline_id,
            event_type="started",
            stage_ids=stage_ids,
            inputs=inputs,
        )

        await self.ws_manager.broadcast_run_event(
            self.run_id,
            WebSocketEventType.RUN_STARTED,
            event.model_dump(mode='json'),
        )

    async def on_run_completed(
        self,
        pipeline_id: str,
        status: str,
        output: Any = None,
        total_duration_ms: Optional[int] = None,
        total_input_tokens: Optional[int] = None,
        total_output_tokens: Optional[int] = None,
    ):
        """
        Called when a run completes successfully.

        Args:
            pipeline_id: The pipeline that ran
            status: Final status
            output: Final output
            total_duration_ms: Total execution time
            total_input_tokens: Total input tokens used
            total_output_tokens: Total output tokens used
        """
        event = RunExecutionEvent(
            run_id=self.run_id,
            pipeline_id=pipeline_id,
            event_type="completed",
            status=status,
            output=output,
            total_duration_ms=total_duration_ms,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
        )

        await self.ws_manager.broadcast_run_event(
            self.run_id,
            WebSocketEventType.RUN_COMPLETED,
            event.model_dump(mode='json'),
        )

    async def on_run_failed(
        self,
        pipeline_id: str,
        error: str,
        failed_stage_id: Optional[str] = None,
    ):
        """
        Called when a run fails.

        Args:
            pipeline_id: The pipeline that failed
            error: Error message
            failed_stage_id: Stage ID where failure occurred
        """
        event = RunExecutionEvent(
            run_id=self.run_id,
            pipeline_id=pipeline_id,
            event_type="failed",
            status="failed",
            error=error,
            failed_stage_id=failed_stage_id,
        )

        await self.ws_manager.broadcast_run_event(
            self.run_id,
            WebSocketEventType.RUN_FAILED,
            event.model_dump(mode='json'),
        )

    def get_state(self) -> DebugState:
        """Get the current debug state."""
        return self._state.model_copy()

    # ==========================================================================
    # Stage information and prompt editing support
    # ==========================================================================

    def __init_stage_store(self):
        """Initialize stage info storage if not present."""
        if not hasattr(self, '_stage_info'):
            self._stage_info: Dict[str, Dict[str, Any]] = {}

    def store_stage_info(
        self,
        stage_id: str,
        component_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
    ):
        """
        Store stage information for debugging.

        Args:
            stage_id: The stage ID
            component_type: Type of component
            input_data: Input data for the stage
            config: Stage configuration
            name: Display name of the stage
        """
        self.__init_stage_store()
        self._stage_info[stage_id] = {
            "name": name or stage_id,
            "component_type": component_type,
            "input": input_data or {},
            "config": config or {},
            "system_prompt": config.get("system_prompt", "") if config else "",
            "user_prompt": config.get("prompt", "") if config else "",
            "variables": {},
            "output": None,
        }

    def update_stage_output(self, stage_id: str, output: Any, tokens: Optional[Dict[str, int]] = None):
        """
        Update stage output after execution.

        Args:
            stage_id: The stage ID
            output: Output from the stage
            tokens: Token usage information
        """
        self.__init_stage_store()
        if stage_id in self._stage_info:
            self._stage_info[stage_id]["output"] = output
            if tokens:
                self._stage_info[stage_id]["tokens"] = tokens

    def get_stage_info(self, stage_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a stage.

        Args:
            stage_id: The stage ID

        Returns:
            Stage information dictionary or None if not found
        """
        self.__init_stage_store()
        return self._stage_info.get(stage_id)

    async def rerun_stage(
        self,
        stage_id: str,
        registry: Any,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Re-execute a single stage with optionally modified prompts.

        Args:
            stage_id: The stage to re-run
            registry: Component registry
            system_prompt: Modified system prompt (optional)
            user_prompt: Modified user prompt (optional)

        Returns:
            Dict with output, tokens, duration_ms
        """
        import time

        from flowmason_core.config import ExecutionContext
        from flowmason_core.execution import UniversalExecutor

        self.__init_stage_store()
        stage_info = self._stage_info.get(stage_id)
        if not stage_info:
            raise ValueError(f"Stage {stage_id} not found in execution context")

        # Get the component
        component_type = stage_info["component_type"]
        component_info = registry.get_component(component_type)
        if not component_info:
            raise ValueError(f"Component {component_type} not found in registry")

        # Build the modified config
        config = dict(stage_info.get("config", {}))
        if system_prompt is not None:
            config["system_prompt"] = system_prompt
        if user_prompt is not None:
            config["prompt"] = user_prompt

        # Get the input data
        input_data = stage_info.get("input", {})

        # Create execution context
        context = ExecutionContext(
            run_id=self.run_id,
            pipeline_id="rerun",
            pipeline_version="1.0.0",
            pipeline_input=input_data,
            providers=getattr(self, '_providers', {}),
        )

        # Execute the component
        start_time = time.time()
        try:
            executor = UniversalExecutor(  # type: ignore[call-arg]
                registry=registry,
                context=context,
                providers=getattr(self, '_providers', {}),
                default_provider=getattr(self, '_default_provider', None),
            )

            result = await executor.execute_component(  # type: ignore[call-arg, arg-type, misc]
                component_info=component_info,
                component_config=config,  # type: ignore[arg-type]
                input_data=input_data,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Update stored stage info
            self._stage_info[stage_id]["output"] = result.output

            return {
                "output": result.output,
                "tokens": {
                    "input": getattr(result, 'input_tokens', 0),
                    "output": getattr(result, 'output_tokens', 0),
                },
                "duration_ms": duration_ms,
            }

        except Exception as e:
            logger.error(f"Failed to re-run stage {stage_id}: {e}")
            raise

    def set_providers(self, providers: Dict[str, Any], default_provider: Optional[str] = None):
        """
        Set providers for stage re-execution.

        Args:
            providers: Dictionary of provider instances
            default_provider: Default provider name
        """
        self._providers = providers
        self._default_provider = default_provider


# Global registry of active controllers
_active_controllers: Dict[str, ExecutionController] = {}
_controllers_lock = asyncio.Lock()


async def get_controller(run_id: str) -> Optional[ExecutionController]:
    """Get the execution controller for a run."""
    async with _controllers_lock:
        return _active_controllers.get(run_id)


async def create_controller(
    run_id: str,
    ws_manager: Optional[ConnectionManager] = None,
    breakpoints: Optional[List[str]] = None,
    org_id: Optional[str] = None,
    pipeline_id: Optional[str] = None,
) -> ExecutionController:
    """
    Create and register an execution controller for a run.

    Args:
        run_id: The run ID
        ws_manager: Optional WebSocket manager
        breakpoints: Initial breakpoints to set
        org_id: Organization ID for usage tracking
        pipeline_id: Pipeline ID for usage tracking

    Returns:
        The created ExecutionController
    """
    controller = ExecutionController(
        run_id,
        ws_manager,
        org_id=org_id,
        pipeline_id=pipeline_id,
    )
    if breakpoints:
        await controller.set_breakpoints(breakpoints)

    async with _controllers_lock:
        _active_controllers[run_id] = controller

    logger.info(f"Created execution controller for run {run_id}")
    return controller


async def remove_controller(run_id: str):
    """Remove an execution controller for a run."""
    async with _controllers_lock:
        if run_id in _active_controllers:
            del _active_controllers[run_id]
            logger.info(f"Removed execution controller for run {run_id}")
