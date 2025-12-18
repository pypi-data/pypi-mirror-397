"""
TryCatch Control Flow Component.

Handles errors in pipeline execution with recovery options.
This is the FlowMason equivalent of try/except in code.
"""

from typing import Any, Dict, List, Optional

from flowmason_core.core.decorators import control_flow
from flowmason_core.core.types import (
    ControlFlowDirective,
    ControlFlowInput,
    ControlFlowOutput,
    ControlFlowType,
    Field,
)


class ErrorScope:
    """Error handling scope options (MuleSoft-inspired)."""
    PROPAGATE = "propagate"  # Re-raise error after catch (on-error-propagate)
    CONTINUE = "continue"    # Continue execution after catch (on-error-continue)


@control_flow(
    name="trycatch",
    description="Handle errors with recovery paths (try/except)",
    control_flow_type="trycatch",
    icon="shield",
    color="#EF4444",  # Red
    version="1.0.0",
    author="FlowMason",
    tags=["trycatch", "error", "exception", "recovery", "control-flow"],
)
class TryCatchComponent:
    """
    Error handling for pipeline execution.

    This component wraps stages in error handling, allowing pipelines
    to recover from errors or execute alternative paths.

    Inspired by MuleSoft's error handling:
    - on-error-propagate: Execute catch, then re-raise
    - on-error-continue: Execute catch, then continue

    Example Pipeline Config:
        stages:
          - id: safe_operation
            type: trycatch
            input_mapping:
              try_stages: ["risky_api_call", "process_response"]
              catch_stages: ["log_error", "use_fallback"]
              finally_stages: ["cleanup"]
              error_scope: "continue"  # Don't fail pipeline

          - id: risky_api_call
            type: http_request
            depends_on: [safe_operation]

          - id: log_error
            type: logger
            depends_on: [safe_operation]
            # Only runs if try_stages fail

    Transpiles to:
        try:
            risky_api_call()
            process_response()
        except Exception as e:
            log_error(e)
            use_fallback()
        finally:
            cleanup()
    """

    class Input(ControlFlowInput):
        try_stages: List[str] = Field(
            description="Stage IDs to execute in try block",
        )
        catch_stages: List[str] = Field(
            default_factory=list,
            description="Stage IDs to execute if error occurs",
        )
        finally_stages: List[str] = Field(
            default_factory=list,
            description="Stage IDs to execute regardless of outcome",
        )
        error_scope: str = Field(
            default=ErrorScope.PROPAGATE,
            description="'propagate' (re-raise after catch) or 'continue' (swallow error)",
        )
        catch_error_types: List[str] = Field(
            default_factory=list,
            description="Specific error types to catch (empty = catch all)",
            examples=[["TimeoutError", "ConnectionError"]],
        )
        max_retries: int = Field(
            default=0,
            description="Number of retries before executing catch",
        )
        retry_delay_ms: int = Field(
            default=1000,
            description="Delay between retries in milliseconds",
        )
        pass_data: Optional[Any] = Field(
            default=None,
            description="Data to pass through to try/catch stages",
        )

    class Output(ControlFlowOutput):
        status: str = Field(
            description="'success', 'caught', or 'error'"
        )
        error_occurred: bool = Field(
            description="Whether an error occurred in try block"
        )
        error_message: Optional[str] = Field(
            default=None,
            description="Error message if error occurred"
        )
        error_type: Optional[str] = Field(
            default=None,
            description="Type of error that occurred"
        )
        recovered: bool = Field(
            default=False,
            description="Whether error was recovered (catch executed)"
        )
        try_result: Any = Field(
            default=None,
            description="Result from try block (if successful)"
        )
        catch_result: Any = Field(
            default=None,
            description="Result from catch block (if executed)"
        )
        data: Any = Field(
            default=None,
            description="Pass-through data"
        )
        directive: ControlFlowDirective = Field(
            description="Execution directive for the executor"
        )

    class Config:
        timeout_seconds: int = 120  # 2 minutes for try/catch blocks

    async def execute(self, input: Input, context) -> Output:
        """
        Set up try/catch execution and return directive.

        This component sets up the error handling context. The executor
        uses the directive to wrap stage execution in error handling.
        """
        # Initial state - try block will be executed
        # Catch/finally are initially skipped (unless error occurs)

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.TRYCATCH,
            execute_stages=input.try_stages,  # Start with try
            skip_stages=input.catch_stages,   # Skip catch initially
            continue_execution=True,
            error=None,
            error_type=None,
            recovered=False,
            metadata={
                "try_stages": input.try_stages,
                "catch_stages": input.catch_stages,
                "finally_stages": input.finally_stages,
                "error_scope": input.error_scope,
                "catch_error_types": input.catch_error_types,
                "max_retries": input.max_retries,
                "retry_delay_ms": input.retry_delay_ms,
            },
        )

        return self.Output(
            status="pending",  # Will be updated by executor
            error_occurred=False,
            error_message=None,
            error_type=None,
            recovered=False,
            try_result=None,
            catch_result=None,
            data=input.pass_data,
            directive=directive,
        )


class TryCatchContext:
    """
    Helper class for tracking try/catch execution state.

    Used by the executor to manage error handling.
    """

    def __init__(
        self,
        try_stages: List[str],
        catch_stages: List[str],
        finally_stages: List[str],
        error_scope: str = ErrorScope.PROPAGATE,
        catch_error_types: Optional[List[str]] = None,
        max_retries: int = 0,
        retry_delay_ms: int = 1000,
    ):
        self.try_stages = try_stages
        self.catch_stages = catch_stages
        self.finally_stages = finally_stages
        self.error_scope = error_scope
        self.catch_error_types = catch_error_types or []
        self.max_retries = max_retries
        self.retry_delay_ms = retry_delay_ms

        self.current_phase = "try"  # try, catch, finally
        self.retry_count = 0
        self.error: Optional[Exception] = None
        self.error_type: Optional[str] = None
        self.error_message: Optional[str] = None
        self.try_results: Dict[str, Any] = {}
        self.catch_results: Dict[str, Any] = {}
        self.finally_results: Dict[str, Any] = {}

    @property
    def should_catch(self) -> bool:
        """Check if error should be caught."""
        if self.error is None:
            return False

        # If no specific types, catch all
        if not self.catch_error_types:
            return True

        # Check if error type matches
        error_type_name = type(self.error).__name__
        return error_type_name in self.catch_error_types

    @property
    def can_retry(self) -> bool:
        """Check if retry is possible."""
        return self.retry_count < self.max_retries

    def record_error(self, error: Exception) -> None:
        """Record an error from try block."""
        self.error = error
        self.error_type = type(error).__name__
        self.error_message = str(error)

    def increment_retry(self) -> None:
        """Increment retry counter."""
        self.retry_count += 1

    def transition_to_catch(self) -> None:
        """Transition to catch phase."""
        self.current_phase = "catch"

    def transition_to_finally(self) -> None:
        """Transition to finally phase."""
        self.current_phase = "finally"

    def get_current_stages(self) -> List[str]:
        """Get stages for current phase."""
        if self.current_phase == "try":
            return self.try_stages
        elif self.current_phase == "catch":
            return self.catch_stages
        elif self.current_phase == "finally":
            return self.finally_stages
        return []

    def add_result(self, stage_id: str, result: Any) -> None:
        """Add result for current phase."""
        if self.current_phase == "try":
            self.try_results[stage_id] = result
        elif self.current_phase == "catch":
            self.catch_results[stage_id] = result
        elif self.current_phase == "finally":
            self.finally_results[stage_id] = result

    def get_error_context(self) -> Dict[str, Any]:
        """Get error information for catch stages."""
        return {
            "error": self.error,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
        }

    def should_propagate(self) -> bool:
        """Check if error should be propagated after catch."""
        return (
            self.error is not None and
            self.error_scope == ErrorScope.PROPAGATE
        )

    def get_final_status(self) -> str:
        """Get final execution status."""
        if self.error is None:
            return "success"
        elif self.should_catch and self.catch_stages:
            return "caught"
        else:
            return "error"
