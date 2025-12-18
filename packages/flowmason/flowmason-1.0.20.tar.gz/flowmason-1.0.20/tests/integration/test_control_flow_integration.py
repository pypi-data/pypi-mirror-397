"""
Integration Tests for Control Flow Components.

Tests complete pipeline execution with control flow components:
- Conditional branching in real pipelines
- ForEach loop iteration
- TryCatch error handling
- Router multi-way branching
- SubPipeline nested execution
- Return early exit

These tests verify that control flow directives are correctly
processed by the DAGExecutor and that execution flow is properly
controlled.
"""

import json
import zipfile
import pytest
from pathlib import Path
from typing import Any, Dict, List, Optional

from flowmason_core.registry import ComponentRegistry
from flowmason_core.config import (
    ComponentConfig,
    ExecutionContext,
)
from flowmason_core.execution import (
    UniversalExecutor,
    DAGExecutor,
    UsageMetrics,
)


# =============================================================================
# Test Component Source Code
# =============================================================================

# Simple processor that transforms data
PROCESSOR_NODE_SOURCE = '''
"""Processor Node - transforms input data."""

from typing import Any
from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node


@node(
    name="processor",
    category="testing",
    description="Process and transform data",
    version="1.0.0",
)
class ProcessorNode:
    """Processes input data."""

    class Input(NodeInput):
        data: Any = Field(description="Data to process")
        operation: str = Field(default="passthrough", description="Operation to perform")

    class Output(NodeOutput):
        result: Any
        operation_performed: str = ""

    async def execute(self, input: "ProcessorNode.Input", context) -> "ProcessorNode.Output":
        data = input.data
        operation = input.operation

        if operation == "uppercase" and isinstance(data, str):
            result = data.upper()
        elif operation == "lowercase" and isinstance(data, str):
            result = data.lower()
        elif operation == "double" and isinstance(data, (int, float)):
            result = data * 2
        elif operation == "increment":
            result = {"count": data.get("count", 0) + 1} if isinstance(data, dict) else data + 1
        elif operation == "fail":
            raise ValueError("Intentional failure for testing")
        else:
            result = data

        return self.Output(result=result, operation_performed=operation)
'''

# Validator that checks conditions
VALIDATOR_NODE_SOURCE = '''
"""Validator Node - validates input and returns status."""

from typing import Any, List
from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node


@node(
    name="validator",
    category="testing",
    description="Validate input data",
    version="1.0.0",
)
class ValidatorNode:
    """Validates input data."""

    class Input(NodeInput):
        data: Any = Field(description="Data to validate")
        rules: List[str] = Field(default_factory=list, description="Validation rules")

    class Output(NodeOutput):
        is_valid: bool = True
        errors: List[str] = []
        data: Any = None

    async def execute(self, input: "ValidatorNode.Input", context) -> "ValidatorNode.Output":
        errors = []
        data = input.data

        for rule in input.rules:
            if rule == "not_empty":
                if not data:
                    errors.append("Data is empty")
            elif rule == "is_string":
                if not isinstance(data, str):
                    errors.append("Data must be a string")
            elif rule == "min_length_3":
                if isinstance(data, str) and len(data) < 3:
                    errors.append("Data must be at least 3 characters")
            elif rule == "is_positive":
                if isinstance(data, (int, float)) and data <= 0:
                    errors.append("Data must be positive")

        return self.Output(
            is_valid=len(errors) == 0,
            errors=errors,
            data=data
        )
'''

# Aggregator that combines multiple inputs
AGGREGATOR_OPERATOR_SOURCE = '''
"""Aggregator Operator - combines multiple inputs."""

from typing import Any, List, Dict
from flowmason_core.core.types import OperatorInput, OperatorOutput, Field
from flowmason_core.core.decorators import operator


@operator(
    name="aggregator",
    category="testing",
    description="Aggregate multiple inputs",
    version="1.0.0",
)
class AggregatorOperator:
    """Aggregates multiple inputs."""

    class Input(OperatorInput):
        items: List[Any] = Field(description="Items to aggregate")
        operation: str = Field(default="list", description="Aggregation operation")

    class Output(OperatorOutput):
        result: Any
        count: int = 0

    async def execute(self, input: "AggregatorOperator.Input", context) -> "AggregatorOperator.Output":
        items = input.items or []
        operation = input.operation

        if operation == "sum" and all(isinstance(i, (int, float)) for i in items):
            result = sum(items)
        elif operation == "concat" and all(isinstance(i, str) for i in items):
            result = "".join(items)
        elif operation == "flatten":
            result = []
            for item in items:
                if isinstance(item, list):
                    result.extend(item)
                else:
                    result.append(item)
        else:
            result = items

        return self.Output(result=result, count=len(items))
'''

# Logger operator for testing
LOGGER_OPERATOR_SOURCE = '''
"""Logger Operator - logs messages for testing."""

from typing import Any, Optional
from flowmason_core.core.types import OperatorInput, OperatorOutput, Field
from flowmason_core.core.decorators import operator


@operator(
    name="test_logger",
    category="testing",
    description="Log messages for testing",
    version="1.0.0",
)
class TestLoggerOperator:
    """Logs messages and passes data through."""

    class Input(OperatorInput):
        message: str = Field(description="Message to log")
        data: Any = Field(default=None, description="Data to pass through")
        level: str = Field(default="info", description="Log level")

    class Output(OperatorOutput):
        logged: bool = True
        message: str = ""
        data: Any = None

    async def execute(self, input: "TestLoggerOperator.Input", context) -> "TestLoggerOperator.Output":
        # In real implementation, would log to a logging system
        return self.Output(
            logged=True,
            message=f"[{input.level.upper()}] {input.message}",
            data=input.data
        )
'''


# =============================================================================
# Fixtures
# =============================================================================

def create_package(output_dir: Path, name: str, source: str, comp_type: str = "node") -> Path:
    """Create a .fmpkg package file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    pkg_path = output_dir / f"{name}-1.0.0.fmpkg"

    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": f"Test package: {name}",
        "type": comp_type,
        "author": {"name": "Test", "email": "test@test.com"},
        "license": "MIT",
        "category": "testing",
        "tags": ["test"],
        "entry_point": "index.py",
        "requires_llm": comp_type == "node",
        "dependencies": []
    }

    with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("flowmason-package.json", json.dumps(manifest, indent=2))
        zf.writestr("index.py", source)

    return pkg_path


@pytest.fixture
def integration_packages_dir(tmp_path):
    """Create a directory with all integration test packages."""
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir()

    # Create test packages
    create_package(packages_dir, "processor", PROCESSOR_NODE_SOURCE, "node")
    create_package(packages_dir, "validator", VALIDATOR_NODE_SOURCE, "node")
    create_package(packages_dir, "aggregator", AGGREGATOR_OPERATOR_SOURCE, "operator")
    create_package(packages_dir, "test_logger", LOGGER_OPERATOR_SOURCE, "operator")

    return packages_dir


@pytest.fixture
def registry(integration_packages_dir):
    """Create a registry with all integration test packages."""
    reg = ComponentRegistry(integration_packages_dir, auto_scan=True)
    return reg


@pytest.fixture
def execution_context():
    """Create a standard execution context."""
    return ExecutionContext(
        run_id="integration_test_run",
        pipeline_id="integration-test-pipeline",
        pipeline_version="1.0.0",
        pipeline_input={}
    )


# =============================================================================
# Test: Basic DAG Execution (Nodes and Operators)
# =============================================================================

class TestBasicDAGExecution:
    """Tests for basic DAG execution with nodes and operators."""

    @pytest.mark.asyncio
    async def test_single_node_execution(self, registry, execution_context):
        """Test executing a single node."""
        execution_context.pipeline_input = {"data": "hello", "operation": "uppercase"}
        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="process",
                type="processor",
                input_mapping={
                    "data": "{{input.data}}",
                    "operation": "{{input.operation}}"
                },
                depends_on=[]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        assert "process" in results
        assert results["process"].status == "success"
        assert results["process"].output["result"] == "HELLO"

    @pytest.mark.asyncio
    async def test_node_to_operator_chain(self, registry, execution_context):
        """Test node followed by operator."""
        execution_context.pipeline_input = {"data": "test"}
        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="validate",
                type="validator",
                input_mapping={
                    "data": "{{input.data}}",
                    "rules": ["not_empty", "is_string"]
                },
                depends_on=[]
            ),
            ComponentConfig(
                id="log_result",
                type="test_logger",
                input_mapping={
                    "message": "Validation complete",
                    "data": "{{upstream.validate.is_valid}}"
                },
                depends_on=["validate"]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        assert results["validate"].status == "success"
        assert results["validate"].output["is_valid"] is True
        assert results["log_result"].status == "success"

    @pytest.mark.asyncio
    async def test_parallel_then_aggregate(self, registry, execution_context):
        """Test parallel execution followed by aggregation."""
        execution_context.pipeline_input = {
            "data1": "hello",
            "data2": "world"
        }
        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            # Parallel processing
            ComponentConfig(
                id="process1",
                type="processor",
                input_mapping={"data": "{{input.data1}}", "operation": "uppercase"},
                depends_on=[]
            ),
            ComponentConfig(
                id="process2",
                type="processor",
                input_mapping={"data": "{{input.data2}}", "operation": "uppercase"},
                depends_on=[]
            ),
            # Aggregate results
            ComponentConfig(
                id="aggregate",
                type="aggregator",
                input_mapping={
                    "items": ["{{upstream.process1.result}}", "{{upstream.process2.result}}"],
                    "operation": "concat"
                },
                depends_on=["process1", "process2"]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        assert results["process1"].output["result"] == "HELLO"
        assert results["process2"].output["result"] == "WORLD"
        assert results["aggregate"].output["result"] == "HELLOWORLD"
        assert results["aggregate"].output["count"] == 2


# =============================================================================
# Test: Conditional Control Flow
# =============================================================================

class TestConditionalIntegration:
    """Integration tests for Conditional control flow."""

    @pytest.mark.asyncio
    async def test_conditional_true_branch_execution(self, registry, execution_context):
        """Test that true branch executes when condition is true."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        # Register conditional component
        # Note: In production, this would be loaded from a package
        # For testing, we'll execute the conditional directly and verify directive

        execution_context.pipeline_input = {"data": "valid_input"}

        # First, test the conditional component output
        conditional = ConditionalComponent()
        cond_input = conditional.Input(
            condition=True,
            true_branch_stages=["process_valid"],
            false_branch_stages=["handle_error"],
        )
        cond_result = await conditional.execute(cond_input, execution_context)

        assert cond_result.branch_taken == "true"
        assert "handle_error" in cond_result.directive.skip_stages
        assert "process_valid" in cond_result.directive.execute_stages

    @pytest.mark.asyncio
    async def test_conditional_false_branch_execution(self, registry, execution_context):
        """Test that false branch executes when condition is false."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        conditional = ConditionalComponent()
        cond_input = conditional.Input(
            condition=False,
            true_branch_stages=["process_valid"],
            false_branch_stages=["handle_error", "notify_admin"],
        )
        cond_result = await conditional.execute(cond_input, execution_context)

        assert cond_result.branch_taken == "false"
        assert "process_valid" in cond_result.directive.skip_stages
        assert "handle_error" in cond_result.directive.execute_stages
        assert "notify_admin" in cond_result.directive.execute_stages

    @pytest.mark.asyncio
    async def test_conditional_with_validation_result(self, registry, execution_context):
        """Test conditional based on validation result."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        execution_context.pipeline_input = {"data": "ab"}  # Too short
        dag_executor = DAGExecutor(registry, execution_context)

        # First validate the data
        stages = [
            ComponentConfig(
                id="validate",
                type="validator",
                input_mapping={
                    "data": "{{input.data}}",
                    "rules": ["min_length_3"]
                },
                depends_on=[]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)
        is_valid = results["validate"].output["is_valid"]

        # Now test conditional with the validation result
        conditional = ConditionalComponent()
        cond_input = conditional.Input(
            condition=is_valid,
            true_branch_stages=["process"],
            false_branch_stages=["reject"],
        )
        cond_result = await conditional.execute(cond_input, execution_context)

        # Should take false branch since validation failed
        assert cond_result.branch_taken == "false"
        assert is_valid is False


# =============================================================================
# Test: ForEach Control Flow
# =============================================================================

class TestForEachIntegration:
    """Integration tests for ForEach control flow."""

    @pytest.mark.asyncio
    async def test_foreach_basic_iteration(self, registry, execution_context):
        """Test basic foreach iteration setup."""
        from flowmason_lab.operators.control_flow import ForEachComponent

        foreach = ForEachComponent()
        foreach_input = foreach.Input(
            items=[{"id": 1}, {"id": 2}, {"id": 3}],
            loop_stages=["process_item"],
            item_variable="item",
        )
        result = await foreach.execute(foreach_input, execution_context)

        assert result.total_items == 3
        assert result.current_index == 0
        assert result.current_item == {"id": 1}
        assert result.directive.loop_items == [{"id": 1}, {"id": 2}, {"id": 3}]

    @pytest.mark.asyncio
    async def test_foreach_with_filter(self, registry, execution_context):
        """Test foreach with filter expression."""
        from flowmason_lab.operators.control_flow import ForEachComponent

        foreach = ForEachComponent()
        foreach_input = foreach.Input(
            items=[
                {"id": 1, "active": True},
                {"id": 2, "active": False},
                {"id": 3, "active": True},
                {"id": 4, "active": False},
            ],
            loop_stages=["process_active"],
            filter_expression="item['active'] == True",
        )
        result = await foreach.execute(foreach_input, execution_context)

        assert result.total_items == 4
        assert result.processed_items == 2  # Only active items
        assert result.skipped_items == 2
        assert len(result.items_to_process) == 2

    @pytest.mark.asyncio
    async def test_foreach_empty_collection(self, registry, execution_context):
        """Test foreach with empty collection."""
        from flowmason_lab.operators.control_flow import ForEachComponent

        foreach = ForEachComponent()
        foreach_input = foreach.Input(
            items=[],
            loop_stages=["process_item"],
        )
        result = await foreach.execute(foreach_input, execution_context)

        assert result.total_items == 0
        assert result.is_complete is True
        assert result.directive.continue_execution is False


# =============================================================================
# Test: TryCatch Control Flow
# =============================================================================

class TestTryCatchIntegration:
    """Integration tests for TryCatch control flow."""

    @pytest.mark.asyncio
    async def test_trycatch_setup(self, registry, execution_context):
        """Test try-catch directive setup."""
        from flowmason_lab.operators.control_flow import TryCatchComponent

        trycatch = TryCatchComponent()
        tc_input = trycatch.Input(
            try_stages=["risky_operation"],
            catch_stages=["handle_error"],
            finally_stages=["cleanup"],
        )
        result = await trycatch.execute(tc_input, execution_context)

        assert result.status == "pending"
        assert "risky_operation" in result.directive.execute_stages
        assert "handle_error" in result.directive.skip_stages

    @pytest.mark.asyncio
    async def test_trycatch_with_retry_config(self, registry, execution_context):
        """Test try-catch with retry configuration."""
        from flowmason_lab.operators.control_flow import TryCatchComponent

        trycatch = TryCatchComponent()
        tc_input = trycatch.Input(
            try_stages=["api_call"],
            catch_stages=["fallback"],
            max_retries=3,
            retry_delay_ms=500,
        )
        result = await trycatch.execute(tc_input, execution_context)

        assert result.directive.metadata["max_retries"] == 3
        assert result.directive.metadata["retry_delay_ms"] == 500

    @pytest.mark.asyncio
    async def test_trycatch_context_error_handling(self, registry, execution_context):
        """Test TryCatchContext error handling."""
        from flowmason_lab.operators.control_flow import TryCatchContext, ErrorScope

        ctx = TryCatchContext(
            try_stages=["risky"],
            catch_stages=["handle"],
            finally_stages=["cleanup"],
            error_scope=ErrorScope.CONTINUE,
        )

        # Simulate error
        ctx.record_error(ValueError("Test error"))
        assert ctx.should_catch is True
        assert ctx.error_type == "ValueError"

        # Transition to catch
        ctx.transition_to_catch()
        assert ctx.current_phase == "catch"
        assert ctx.get_current_stages() == ["handle"]

        # Final status
        assert ctx.get_final_status() == "caught"


# =============================================================================
# Test: Router Control Flow
# =============================================================================

class TestRouterIntegration:
    """Integration tests for Router control flow."""

    @pytest.mark.asyncio
    async def test_router_basic_routing(self, registry, execution_context):
        """Test basic router routing."""
        from flowmason_lab.operators.control_flow import RouterComponent

        router = RouterComponent()
        router_input = router.Input(
            value="billing",
            routes={
                "billing": ["billing_handler"],
                "support": ["support_handler"],
                "sales": ["sales_handler"],
            },
            default_route=["default_handler"],
        )
        result = await router.execute(router_input, execution_context)

        assert result.route_taken == "billing"
        assert "billing_handler" in result.stages_to_execute
        assert "support_handler" in result.stages_to_skip
        assert "sales_handler" in result.stages_to_skip
        assert "default_handler" in result.stages_to_skip

    @pytest.mark.asyncio
    async def test_router_default_route(self, registry, execution_context):
        """Test router falling back to default route."""
        from flowmason_lab.operators.control_flow import RouterComponent

        router = RouterComponent()
        router_input = router.Input(
            value="unknown",
            routes={
                "billing": ["billing_handler"],
                "support": ["support_handler"],
            },
            default_route=["default_handler"],
        )
        result = await router.execute(router_input, execution_context)

        assert result.route_taken == "default"
        assert "default_handler" in result.stages_to_execute

    @pytest.mark.asyncio
    async def test_router_case_insensitive(self, registry, execution_context):
        """Test router with case-insensitive matching."""
        from flowmason_lab.operators.control_flow import RouterComponent

        router = RouterComponent()
        router_input = router.Input(
            value="BILLING",
            routes={
                "billing": ["billing_handler"],
            },
            case_insensitive=True,
        )
        result = await router.execute(router_input, execution_context)

        assert result.route_taken == "billing"


# =============================================================================
# Test: SubPipeline Control Flow
# =============================================================================

class TestSubPipelineIntegration:
    """Integration tests for SubPipeline control flow."""

    @pytest.mark.asyncio
    async def test_subpipeline_setup(self, registry, execution_context):
        """Test subpipeline directive setup."""
        from flowmason_lab.operators.control_flow import SubPipelineComponent

        subpipeline = SubPipelineComponent()
        sp_input = subpipeline.Input(
            pipeline_id="validation-pipeline",
            input_data={"user_id": "123"},
            timeout_ms=30000,
        )
        result = await subpipeline.execute(sp_input, execution_context)

        assert result.pipeline_id == "validation-pipeline"
        assert result.status == "pending"
        assert result.directive.metadata["pipeline_id"] == "validation-pipeline"
        assert result.directive.metadata["input_data"] == {"user_id": "123"}

    @pytest.mark.asyncio
    async def test_subpipeline_context_success(self, registry, execution_context):
        """Test SubPipelineContext successful execution."""
        from flowmason_lab.operators.control_flow import SubPipelineContext

        ctx = SubPipelineContext(
            pipeline_id="test-pipeline",
            input_data={"key": "value"},
        )

        ctx.record_start("run-123")
        assert ctx.status == "running"

        ctx.record_success({"output": "data"}, 500)
        assert ctx.status == "completed"
        assert ctx.result == {"output": "data"}
        assert ctx.execution_time_ms == 500

    @pytest.mark.asyncio
    async def test_subpipeline_context_failure_default(self, registry, execution_context):
        """Test SubPipelineContext failure with default fallback."""
        from flowmason_lab.operators.control_flow import SubPipelineContext

        ctx = SubPipelineContext(
            pipeline_id="test-pipeline",
            on_error="default",
            default_result={"fallback": True},
        )

        ctx.record_failure("Network error", 1000)
        assert ctx.status == "failed"
        assert ctx.result == {"fallback": True}


# =============================================================================
# Test: Return Control Flow
# =============================================================================

class TestReturnIntegration:
    """Integration tests for Return control flow."""

    @pytest.mark.asyncio
    async def test_return_early_exit(self, registry, execution_context):
        """Test return early exit."""
        from flowmason_lab.operators.control_flow import ReturnComponent

        return_comp = ReturnComponent()
        ret_input = return_comp.Input(
            condition=True,
            return_value={"status": "early_exit"},
            message="Exiting early due to condition",
        )
        result = await return_comp.execute(ret_input, execution_context)

        assert result.should_return is True
        assert result.return_value == {"status": "early_exit"}
        assert result.directive.continue_execution is False

    @pytest.mark.asyncio
    async def test_return_no_exit_when_false(self, registry, execution_context):
        """Test return does not exit when condition is false."""
        from flowmason_lab.operators.control_flow import ReturnComponent

        return_comp = ReturnComponent()
        ret_input = return_comp.Input(
            condition=False,
            return_value={"should": "not return"},
        )
        result = await return_comp.execute(ret_input, execution_context)

        assert result.should_return is False
        assert result.directive.continue_execution is True


# =============================================================================
# Test: Complex Pipeline Scenarios
# =============================================================================

class TestComplexPipelineScenarios:
    """Tests for complex pipeline scenarios combining multiple control flows."""

    @pytest.mark.asyncio
    async def test_validation_then_conditional_processing(self, registry, execution_context):
        """Test validation followed by conditional processing."""
        execution_context.pipeline_input = {"data": "hello world"}
        dag_executor = DAGExecutor(registry, execution_context)

        # Execute validation
        stages = [
            ComponentConfig(
                id="validate",
                type="validator",
                input_mapping={
                    "data": "{{input.data}}",
                    "rules": ["not_empty", "is_string", "min_length_3"]
                },
                depends_on=[]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        # Validation should pass
        assert results["validate"].output["is_valid"] is True

        # Now we can use the result in a conditional
        from flowmason_lab.operators.control_flow import ConditionalComponent
        conditional = ConditionalComponent()
        cond_input = conditional.Input(
            condition=results["validate"].output["is_valid"],
            true_branch_stages=["process"],
            false_branch_stages=["reject"],
        )
        cond_result = await conditional.execute(cond_input, execution_context)

        assert cond_result.branch_taken == "true"

    @pytest.mark.asyncio
    async def test_loop_with_aggregation(self, registry, execution_context):
        """Test foreach loop followed by aggregation."""
        from flowmason_lab.operators.control_flow import ForEachComponent

        # Set up foreach
        foreach = ForEachComponent()
        foreach_input = foreach.Input(
            items=[1, 2, 3, 4, 5],
            loop_stages=["double_item"],
            item_variable="num",
        )
        foreach_result = await foreach.execute(foreach_input, execution_context)

        assert foreach_result.total_items == 5
        assert len(foreach_result.items_to_process) == 5

        # The actual loop execution would be handled by the DAGExecutor
        # Here we verify the directive is correctly set up
        assert foreach_result.directive.loop_items == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_router_with_multiple_handlers(self, registry, execution_context):
        """Test router directing to different handlers."""
        from flowmason_lab.operators.control_flow import RouterComponent

        test_cases = [
            ("billing", "billing"),
            ("support", "support"),
            ("sales", "sales"),
            ("unknown", "default"),
        ]

        router = RouterComponent()

        for input_value, expected_route in test_cases:
            router_input = router.Input(
                value=input_value,
                routes={
                    "billing": ["billing_handler"],
                    "support": ["support_handler"],
                    "sales": ["sales_handler"],
                },
                default_route=["default_handler"],
            )
            result = await router.execute(router_input, execution_context)

            assert result.route_taken == expected_route, f"Failed for input: {input_value}"


# =============================================================================
# Test: Error Scenarios
# =============================================================================

class TestErrorScenarios:
    """Tests for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_component_execution_error(self, registry, execution_context):
        """Test handling component execution errors."""
        execution_context.pipeline_input = {"data": "test", "operation": "fail"}
        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="failing_stage",
                type="processor",
                input_mapping={
                    "data": "{{input.data}}",
                    "operation": "{{input.operation}}"
                },
                depends_on=[]
            )
        ]

        with pytest.raises(Exception) as exc_info:
            await dag_executor.execute(stages, execution_context.pipeline_input)

        assert "Intentional failure" in str(exc_info.value) or "execution failed" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_validation_failure_propagation(self, registry, execution_context):
        """Test that validation failures are properly reported."""
        execution_context.pipeline_input = {"data": ""}  # Empty data
        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="validate",
                type="validator",
                input_mapping={
                    "data": "{{input.data}}",
                    "rules": ["not_empty"]
                },
                depends_on=[]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        assert results["validate"].output["is_valid"] is False
        assert "Data is empty" in results["validate"].output["errors"]


# =============================================================================
# Test: Usage Metrics Aggregation
# =============================================================================

class TestUsageMetrics:
    """Tests for usage metrics tracking and aggregation."""

    @pytest.mark.asyncio
    async def test_usage_metrics_tracked(self, registry, execution_context):
        """Test that usage metrics are tracked for each stage."""
        execution_context.pipeline_input = {"data": "test"}
        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="process",
                type="processor",
                input_mapping={"data": "{{input.data}}"},
                depends_on=[]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        assert results["process"].usage is not None
        assert results["process"].usage.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_usage_metrics_aggregation(self, registry, execution_context):
        """Test aggregating usage metrics across stages."""
        execution_context.pipeline_input = {"data": "test"}
        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="stage1",
                type="processor",
                input_mapping={"data": "{{input.data}}"},
                depends_on=[]
            ),
            ComponentConfig(
                id="stage2",
                type="processor",
                input_mapping={"data": "{{upstream.stage1.result}}"},
                depends_on=["stage1"]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)
        total_usage = dag_executor.aggregate_usage(results)

        assert isinstance(total_usage, UsageMetrics)
        assert total_usage.duration_ms >= 0
