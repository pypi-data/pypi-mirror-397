"""
SubPipeline Control Flow Component.

Calls another pipeline as a sub-routine.
This is the FlowMason equivalent of function/method calls in code.
"""

from typing import Any, Dict, Optional

from flowmason_core.core.decorators import control_flow
from flowmason_core.core.types import (
    ControlFlowDirective,
    ControlFlowInput,
    ControlFlowOutput,
    ControlFlowType,
    Field,
)


@control_flow(
    name="subpipeline",
    description="Call another pipeline as a sub-routine (function call)",
    control_flow_type="subpipeline",
    icon="box",
    color="#8B5CF6",  # Purple
    version="1.0.0",
    author="FlowMason",
    tags=["subpipeline", "call", "invoke", "function", "composition", "control-flow"],
)
class SubPipelineComponent:
    """
    Pipeline composition through sub-pipeline calls.

    This component allows a pipeline to call another pipeline,
    enabling code reuse and modular pipeline design.

    The sub-pipeline executes with its own context but can receive
    input data from the parent pipeline and return results.

    Example Pipeline Config:
        stages:
          - id: validate_customer
            type: subpipeline
            input_mapping:
              pipeline_id: "customer-validation-v2"
              input_data:
                customer: "{{input.customer}}"
                strict_mode: true
              timeout_ms: 30000

          - id: process_result
            type: processor
            depends_on: [validate_customer]
            input_mapping:
              validation_result: "{{upstream.validate_customer.result}}"

    Transpiles to:
        validation_result = customer_validation_v2(
            customer=input.customer,
            strict_mode=True
        )
        process_result(validation_result)
    """

    class Input(ControlFlowInput):
        pipeline_id: str = Field(
            description="ID of the pipeline to call",
        )
        pipeline_version: Optional[str] = Field(
            default=None,
            description="Specific version to call (latest if not specified)",
        )
        input_data: Dict[str, Any] = Field(
            default_factory=dict,
            description="Input data to pass to the sub-pipeline",
        )
        timeout_ms: int = Field(
            default=60000,
            description="Timeout for sub-pipeline execution in milliseconds",
        )
        async_execution: bool = Field(
            default=False,
            description="Whether to execute asynchronously (fire-and-forget)",
        )
        wait_for_completion: bool = Field(
            default=True,
            description="Whether to wait for sub-pipeline to complete",
        )
        inherit_context: bool = Field(
            default=True,
            description="Whether to inherit parent context (providers, variables)",
        )
        isolated: bool = Field(
            default=False,
            description="Run in isolated context (no access to parent data)",
        )
        on_error: str = Field(
            default="propagate",
            description="Error handling: 'propagate', 'ignore', or 'default'",
        )
        default_result: Optional[Any] = Field(
            default=None,
            description="Default result if on_error='default'",
        )

    class Output(ControlFlowOutput):
        pipeline_id: str = Field(
            description="ID of the called pipeline"
        )
        run_id: Optional[str] = Field(
            default=None,
            description="Run ID of the sub-pipeline execution"
        )
        status: str = Field(
            description="Execution status: 'pending', 'running', 'completed', 'failed'"
        )
        result: Any = Field(
            default=None,
            description="Result from sub-pipeline execution"
        )
        execution_time_ms: Optional[int] = Field(
            default=None,
            description="Execution time in milliseconds"
        )
        error: Optional[str] = Field(
            default=None,
            description="Error message if execution failed"
        )
        directive: ControlFlowDirective = Field(
            description="Execution directive for the executor"
        )

    class Config:
        timeout_seconds: int = 120  # 2 minutes default

    async def execute(self, input: Input, context) -> Output:
        """
        Set up sub-pipeline call and return directive.

        The actual sub-pipeline execution is handled by the executor,
        which uses the directive to load and run the specified pipeline.
        """
        # Create the directive with sub-pipeline execution info
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.SUBPIPELINE,
            execute_stages=[],  # Sub-pipeline handles its own stages
            skip_stages=[],
            continue_execution=True,
            nested_results={},  # Will be populated by executor
            metadata={
                "pipeline_id": input.pipeline_id,
                "pipeline_version": input.pipeline_version,
                "input_data": input.input_data,
                "timeout_ms": input.timeout_ms,
                "async_execution": input.async_execution,
                "wait_for_completion": input.wait_for_completion,
                "inherit_context": input.inherit_context,
                "isolated": input.isolated,
                "on_error": input.on_error,
                "default_result": input.default_result,
            },
        )

        return self.Output(
            pipeline_id=input.pipeline_id,
            run_id=None,  # Set by executor
            status="pending",
            result=None,  # Set by executor after completion
            execution_time_ms=None,
            error=None,
            directive=directive,
        )


class SubPipelineContext:
    """
    Helper class for managing sub-pipeline execution.

    Used by the executor to handle sub-pipeline calls.
    """

    def __init__(
        self,
        pipeline_id: str,
        pipeline_version: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        timeout_ms: int = 60000,
        async_execution: bool = False,
        wait_for_completion: bool = True,
        inherit_context: bool = True,
        isolated: bool = False,
        on_error: str = "propagate",
        default_result: Any = None,
        parent_run_id: Optional[str] = None,
        parent_context: Optional[Any] = None,
    ):
        self.pipeline_id = pipeline_id
        self.pipeline_version = pipeline_version
        self.input_data = input_data or {}
        self.timeout_ms = timeout_ms
        self.async_execution = async_execution
        self.wait_for_completion = wait_for_completion
        self.inherit_context = inherit_context
        self.isolated = isolated
        self.on_error = on_error
        self.default_result = default_result
        self.parent_run_id = parent_run_id
        self.parent_context = parent_context

        # Execution state
        self.run_id: Optional[str] = None
        self.status = "pending"
        self.result: Any = None
        self.error: Optional[str] = None
        self.execution_time_ms: Optional[int] = None

    def build_child_context(self) -> Dict[str, Any]:
        """
        Build context for the sub-pipeline.

        Returns:
            Context dict for sub-pipeline execution
        """
        context = {
            "parent_run_id": self.parent_run_id,
            "is_subpipeline": True,
        }

        if self.inherit_context and self.parent_context and not self.isolated:
            # Inherit providers and variables from parent
            if hasattr(self.parent_context, 'providers'):
                context["providers"] = self.parent_context.providers
            if hasattr(self.parent_context, 'variables'):
                context["variables"] = self.parent_context.variables

        return context

    def record_start(self, run_id: str) -> None:
        """Record sub-pipeline start."""
        self.run_id = run_id
        self.status = "running"

    def record_success(self, result: Any, execution_time_ms: int) -> None:
        """Record successful completion."""
        self.status = "completed"
        self.result = result
        self.execution_time_ms = execution_time_ms

    def record_failure(self, error: str, execution_time_ms: int) -> None:
        """Record execution failure."""
        self.status = "failed"
        self.error = error
        self.execution_time_ms = execution_time_ms

        # Handle error according to on_error setting
        if self.on_error == "ignore":
            self.result = None
        elif self.on_error == "default":
            self.result = self.default_result

    def get_result(self) -> Any:
        """Get the execution result."""
        if self.status == "failed" and self.on_error == "propagate":
            raise RuntimeError(f"Sub-pipeline failed: {self.error}")
        return self.result

    def should_wait(self) -> bool:
        """Check if we should wait for completion."""
        return self.wait_for_completion and not self.async_execution
