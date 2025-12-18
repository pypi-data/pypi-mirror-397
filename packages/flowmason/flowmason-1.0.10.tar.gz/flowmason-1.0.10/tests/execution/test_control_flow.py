"""
Tests for Control Flow Components.

Tests each control flow component individually:
- Conditional (if/else branching)
- ForEach (loop iteration)
- TryCatch (error handling)
- Router (switch/case)
- SubPipeline (nested pipeline execution)
- Return (early exit)
"""

import pytest
import asyncio
from typing import Any, Dict, List, Optional

from flowmason_core.core.types import (
    ControlFlowDirective,
    ControlFlowType,
)
from flowmason_core.config import ExecutionContext


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def execution_context():
    """Create a basic execution context for tests."""
    return ExecutionContext(
        run_id="test_control_flow_run",
        pipeline_id="test-control-flow-pipeline",
        pipeline_version="1.0.0",
        pipeline_input={}
    )


# =============================================================================
# Conditional Component Tests
# =============================================================================

class TestConditionalComponent:
    """Tests for the Conditional control flow component."""

    @pytest.mark.asyncio
    async def test_conditional_true_branch(self, execution_context):
        """Test conditional with truthy condition takes true branch."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        component = ConditionalComponent()
        input_data = component.Input(
            condition=True,
            true_branch_stages=["process_valid", "save_result"],
            false_branch_stages=["handle_error"],
            pass_data={"key": "value"}
        )

        result = await component.execute(input_data, execution_context)

        assert result.branch_taken == "true"
        assert result.condition_result is True
        assert result.data == {"key": "value"}
        assert result.directive.directive_type == ControlFlowType.CONDITIONAL
        assert set(result.directive.skip_stages) == {"handle_error"}
        assert set(result.directive.execute_stages) == {"process_valid", "save_result"}

    @pytest.mark.asyncio
    async def test_conditional_false_branch(self, execution_context):
        """Test conditional with falsy condition takes false branch."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        component = ConditionalComponent()
        input_data = component.Input(
            condition=False,
            true_branch_stages=["process_valid"],
            false_branch_stages=["handle_error", "notify_admin"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.branch_taken == "false"
        assert result.condition_result is False
        assert set(result.directive.skip_stages) == {"process_valid"}
        assert set(result.directive.execute_stages) == {"handle_error", "notify_admin"}

    @pytest.mark.asyncio
    async def test_conditional_with_expression(self, execution_context):
        """Test conditional with expression evaluation."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        component = ConditionalComponent()

        # Test with expression that evaluates to True
        input_data = component.Input(
            condition=0.9,
            condition_expression="value > 0.8",
            true_branch_stages=["high_confidence"],
            false_branch_stages=["low_confidence"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.branch_taken == "true"
        assert result.condition_result is True

    @pytest.mark.asyncio
    async def test_conditional_with_expression_false(self, execution_context):
        """Test conditional expression evaluating to False."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        component = ConditionalComponent()
        input_data = component.Input(
            condition=0.5,
            condition_expression="value > 0.8",
            true_branch_stages=["high_confidence"],
            false_branch_stages=["low_confidence"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.branch_taken == "false"
        assert result.condition_result is False

    @pytest.mark.asyncio
    async def test_conditional_empty_string_is_falsy(self, execution_context):
        """Test that empty string is falsy."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        component = ConditionalComponent()
        input_data = component.Input(
            condition="",
            true_branch_stages=["has_value"],
            false_branch_stages=["no_value"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.branch_taken == "false"

    @pytest.mark.asyncio
    async def test_conditional_empty_list_is_falsy(self, execution_context):
        """Test that empty list is falsy."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        component = ConditionalComponent()
        input_data = component.Input(
            condition=[],
            true_branch_stages=["has_items"],
            false_branch_stages=["empty"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.branch_taken == "false"

    @pytest.mark.asyncio
    async def test_conditional_non_empty_list_is_truthy(self, execution_context):
        """Test that non-empty list is truthy."""
        from flowmason_lab.operators.control_flow import ConditionalComponent

        component = ConditionalComponent()
        input_data = component.Input(
            condition=["item1", "item2"],
            true_branch_stages=["has_items"],
            false_branch_stages=["empty"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.branch_taken == "true"


# =============================================================================
# ForEach Component Tests
# =============================================================================

class TestForEachComponent:
    """Tests for the ForEach control flow component."""

    @pytest.mark.asyncio
    async def test_foreach_basic_iteration(self, execution_context):
        """Test basic foreach iteration setup."""
        from flowmason_lab.operators.control_flow import ForEachComponent

        component = ForEachComponent()
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        input_data = component.Input(
            items=items,
            loop_stages=["process_item", "save_item"],
            item_variable="customer",
            index_variable="idx",
        )

        result = await component.execute(input_data, execution_context)

        assert result.total_items == 3
        assert result.processed_items == 3
        assert result.skipped_items == 0
        assert result.current_item == {"id": 1}
        assert result.current_index == 0
        assert result.items_to_process == items
        assert result.is_complete is False
        assert result.directive.directive_type == ControlFlowType.FOREACH
        assert result.directive.loop_items == items

    @pytest.mark.asyncio
    async def test_foreach_empty_collection(self, execution_context):
        """Test foreach with empty collection marks as complete."""
        from flowmason_lab.operators.control_flow import ForEachComponent

        component = ForEachComponent()
        input_data = component.Input(
            items=[],
            loop_stages=["process"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.total_items == 0
        assert result.is_complete is True
        assert result.current_item is None
        assert result.directive.continue_execution is False

    @pytest.mark.asyncio
    async def test_foreach_with_filter_expression(self, execution_context):
        """Test foreach filtering items with expression."""
        from flowmason_lab.operators.control_flow import ForEachComponent

        component = ForEachComponent()
        items = [
            {"id": 1, "active": True},
            {"id": 2, "active": False},
            {"id": 3, "active": True},
        ]
        input_data = component.Input(
            items=items,
            loop_stages=["process"],
            filter_expression="item['active'] == True",
        )

        result = await component.execute(input_data, execution_context)

        assert result.total_items == 3
        assert result.processed_items == 2  # Only active items
        assert result.skipped_items == 1
        assert len(result.items_to_process) == 2

    @pytest.mark.asyncio
    async def test_foreach_parallel_metadata(self, execution_context):
        """Test foreach parallel execution metadata."""
        from flowmason_lab.operators.control_flow import ForEachComponent

        component = ForEachComponent()
        input_data = component.Input(
            items=[1, 2, 3, 4, 5],
            loop_stages=["process"],
            parallel=True,
            max_parallel=3,
            break_on_error=False,
        )

        result = await component.execute(input_data, execution_context)

        assert result.directive.metadata["parallel"] is True
        assert result.directive.metadata["max_parallel"] == 3
        assert result.directive.metadata["break_on_error"] is False


# =============================================================================
# TryCatch Component Tests
# =============================================================================

class TestTryCatchComponent:
    """Tests for the TryCatch control flow component."""

    @pytest.mark.asyncio
    async def test_trycatch_basic_setup(self, execution_context):
        """Test basic try-catch setup."""
        from flowmason_lab.operators.control_flow import TryCatchComponent

        component = TryCatchComponent()
        input_data = component.Input(
            try_stages=["risky_api_call", "process_response"],
            catch_stages=["log_error", "use_fallback"],
            finally_stages=["cleanup"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.status == "pending"
        assert result.error_occurred is False
        assert result.directive.directive_type == ControlFlowType.TRYCATCH
        assert set(result.directive.execute_stages) == {"risky_api_call", "process_response"}
        assert set(result.directive.skip_stages) == {"log_error", "use_fallback"}

    @pytest.mark.asyncio
    async def test_trycatch_with_retry_config(self, execution_context):
        """Test try-catch with retry configuration."""
        from flowmason_lab.operators.control_flow import TryCatchComponent

        component = TryCatchComponent()
        input_data = component.Input(
            try_stages=["api_call"],
            catch_stages=["handle_error"],
            max_retries=3,
            retry_delay_ms=1000,
        )

        result = await component.execute(input_data, execution_context)

        assert result.directive.metadata["max_retries"] == 3
        assert result.directive.metadata["retry_delay_ms"] == 1000

    @pytest.mark.asyncio
    async def test_trycatch_error_scope_propagate(self, execution_context):
        """Test try-catch with propagate error scope."""
        from flowmason_lab.operators.control_flow import TryCatchComponent, ErrorScope

        component = TryCatchComponent()
        input_data = component.Input(
            try_stages=["risky_call"],
            catch_stages=["handle_error"],
            error_scope=ErrorScope.PROPAGATE,
        )

        result = await component.execute(input_data, execution_context)

        assert result.directive.metadata["error_scope"] == "propagate"

    @pytest.mark.asyncio
    async def test_trycatch_error_scope_continue(self, execution_context):
        """Test try-catch with continue error scope."""
        from flowmason_lab.operators.control_flow import TryCatchComponent, ErrorScope

        component = TryCatchComponent()
        input_data = component.Input(
            try_stages=["risky_call"],
            catch_stages=["handle_error"],
            error_scope=ErrorScope.CONTINUE,
        )

        result = await component.execute(input_data, execution_context)

        assert result.directive.metadata["error_scope"] == "continue"

    @pytest.mark.asyncio
    async def test_trycatch_with_specific_error_types(self, execution_context):
        """Test try-catch catching specific error types."""
        from flowmason_lab.operators.control_flow import TryCatchComponent

        component = TryCatchComponent()
        input_data = component.Input(
            try_stages=["network_call"],
            catch_stages=["handle_network_error"],
            catch_error_types=["TimeoutError", "ConnectionError"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.directive.metadata["catch_error_types"] == ["TimeoutError", "ConnectionError"]


# =============================================================================
# Router Component Tests
# =============================================================================

class TestRouterComponent:
    """Tests for the Router control flow component."""

    @pytest.mark.asyncio
    async def test_router_basic_routing(self, execution_context):
        """Test basic router with route matching."""
        from flowmason_lab.operators.control_flow import RouterComponent

        component = RouterComponent()
        input_data = component.Input(
            value="billing",
            routes={
                "billing": ["billing_handler"],
                "support": ["support_handler"],
                "sales": ["sales_handler"],
            },
            default_route=["default_handler"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.route_taken == "billing"
        assert result.directive.directive_type == ControlFlowType.ROUTER
        assert "billing_handler" in result.directive.execute_stages
        assert "billing_handler" in result.stages_to_execute

    @pytest.mark.asyncio
    async def test_router_default_route(self, execution_context):
        """Test router falling back to default route."""
        from flowmason_lab.operators.control_flow import RouterComponent

        component = RouterComponent()
        input_data = component.Input(
            value="unknown_category",
            routes={
                "billing": ["billing_handler"],
                "support": ["support_handler"],
            },
            default_route=["default_handler"],
        )

        result = await component.execute(input_data, execution_context)

        assert result.route_taken == "default"
        assert "default_handler" in result.directive.execute_stages
        assert "default_handler" in result.stages_to_execute

    @pytest.mark.asyncio
    async def test_router_with_expression(self, execution_context):
        """Test router with value expression transformation."""
        from flowmason_lab.operators.control_flow import RouterComponent

        component = RouterComponent()
        input_data = component.Input(
            value={"score": 95},
            value_expression="'high' if value['score'] >= 90 else 'low'",
            routes={
                "high": ["premium_handler"],
                "low": ["standard_handler"],
            },
        )

        result = await component.execute(input_data, execution_context)

        assert result.route_taken == "high"
        assert "premium_handler" in result.directive.execute_stages

    @pytest.mark.asyncio
    async def test_router_case_insensitive(self, execution_context):
        """Test router with case-insensitive matching."""
        from flowmason_lab.operators.control_flow import RouterComponent

        component = RouterComponent()
        input_data = component.Input(
            value="BILLING",
            routes={
                "billing": ["billing_handler"],
                "support": ["support_handler"],
            },
            case_insensitive=True,
        )

        result = await component.execute(input_data, execution_context)

        assert result.route_taken == "billing"
        assert "billing_handler" in result.stages_to_execute

    @pytest.mark.asyncio
    async def test_router_skips_other_routes(self, execution_context):
        """Test that router skips stages from non-selected routes."""
        from flowmason_lab.operators.control_flow import RouterComponent

        component = RouterComponent()
        input_data = component.Input(
            value="billing",
            routes={
                "billing": ["billing_handler"],
                "support": ["support_handler", "escalate_handler"],
            },
            default_route=["default_handler"],
        )

        result = await component.execute(input_data, execution_context)

        # Should skip support and default handlers
        assert "support_handler" in result.stages_to_skip
        assert "escalate_handler" in result.stages_to_skip
        assert "default_handler" in result.stages_to_skip
        assert "billing_handler" not in result.stages_to_skip


# =============================================================================
# SubPipeline Component Tests
# =============================================================================

class TestSubPipelineComponent:
    """Tests for the SubPipeline control flow component."""

    @pytest.mark.asyncio
    async def test_subpipeline_basic_setup(self, execution_context):
        """Test basic subpipeline setup."""
        from flowmason_lab.operators.control_flow import SubPipelineComponent

        component = SubPipelineComponent()
        input_data = component.Input(
            pipeline_id="customer-validation-v2",
            input_data={"customer_id": "123", "strict_mode": True},
            timeout_ms=30000,
        )

        result = await component.execute(input_data, execution_context)

        assert result.pipeline_id == "customer-validation-v2"
        assert result.status == "pending"
        assert result.directive.directive_type == ControlFlowType.SUBPIPELINE
        assert result.directive.metadata["pipeline_id"] == "customer-validation-v2"
        assert result.directive.metadata["input_data"] == {"customer_id": "123", "strict_mode": True}

    @pytest.mark.asyncio
    async def test_subpipeline_with_version(self, execution_context):
        """Test subpipeline with specific version."""
        from flowmason_lab.operators.control_flow import SubPipelineComponent

        component = SubPipelineComponent()
        input_data = component.Input(
            pipeline_id="data-processor",
            pipeline_version="2.1.0",
            input_data={"data": [1, 2, 3]},
        )

        result = await component.execute(input_data, execution_context)

        assert result.directive.metadata["pipeline_version"] == "2.1.0"

    @pytest.mark.asyncio
    async def test_subpipeline_error_handling_options(self, execution_context):
        """Test subpipeline error handling options."""
        from flowmason_lab.operators.control_flow import SubPipelineComponent

        component = SubPipelineComponent()

        # Test with ignore error handling
        input_data = component.Input(
            pipeline_id="risky-pipeline",
            on_error="ignore",
        )
        result = await component.execute(input_data, execution_context)
        assert result.directive.metadata["on_error"] == "ignore"

        # Test with default error handling
        input_data = component.Input(
            pipeline_id="risky-pipeline",
            on_error="default",
            default_result={"status": "fallback"},
        )
        result = await component.execute(input_data, execution_context)
        assert result.directive.metadata["on_error"] == "default"
        assert result.directive.metadata["default_result"] == {"status": "fallback"}

    @pytest.mark.asyncio
    async def test_subpipeline_context_inheritance(self, execution_context):
        """Test subpipeline context inheritance options."""
        from flowmason_lab.operators.control_flow import SubPipelineComponent

        component = SubPipelineComponent()

        # Test with inherited context
        input_data = component.Input(
            pipeline_id="child-pipeline",
            inherit_context=True,
            isolated=False,
        )
        result = await component.execute(input_data, execution_context)
        assert result.directive.metadata["inherit_context"] is True
        assert result.directive.metadata["isolated"] is False

        # Test with isolated context
        input_data = component.Input(
            pipeline_id="isolated-pipeline",
            inherit_context=False,
            isolated=True,
        )
        result = await component.execute(input_data, execution_context)
        assert result.directive.metadata["isolated"] is True


# =============================================================================
# Return Component Tests
# =============================================================================

class TestReturnComponent:
    """Tests for the Return control flow component."""

    @pytest.mark.asyncio
    async def test_return_early_exit(self, execution_context):
        """Test return component for early exit."""
        from flowmason_lab.operators.control_flow import ReturnComponent

        component = ReturnComponent()
        input_data = component.Input(
            condition=True,
            return_value={"status": "early_exit", "data": [1, 2, 3]},
            message="Validation failed, exiting early",
        )

        result = await component.execute(input_data, execution_context)

        assert result.should_return is True
        assert result.return_value == {"status": "early_exit", "data": [1, 2, 3]}
        assert result.directive.directive_type == ControlFlowType.RETURN
        assert result.directive.continue_execution is False

    @pytest.mark.asyncio
    async def test_return_no_exit_when_condition_false(self, execution_context):
        """Test return does not exit when condition is false."""
        from flowmason_lab.operators.control_flow import ReturnComponent

        component = ReturnComponent()
        input_data = component.Input(
            condition=False,
            return_value={"should": "not return"},
        )

        result = await component.execute(input_data, execution_context)

        assert result.should_return is False
        assert result.directive.continue_execution is True


# =============================================================================
# Control Flow Context/State Tests
# =============================================================================

class TestLoopIterationContext:
    """Tests for LoopIterationContext helper."""

    def test_loop_context_initialization(self):
        """Test loop context initialization."""
        from flowmason_lab.operators.control_flow import LoopIterationContext

        ctx = LoopIterationContext(
            items=[1, 2, 3],
            loop_stages=["process"],
            item_variable="num",
            index_variable="i",
        )

        assert ctx.current_item == 1
        assert ctx.current_index == 0
        assert ctx.has_more is True
        assert ctx.is_complete is False

    def test_loop_context_advance(self):
        """Test loop context advancement."""
        from flowmason_lab.operators.control_flow import LoopIterationContext

        ctx = LoopIterationContext(items=[1, 2], loop_stages=["process"])

        assert ctx.current_index == 0
        assert ctx.advance() is True
        assert ctx.current_index == 1
        assert ctx.advance() is False
        assert ctx.is_complete is True

    def test_loop_context_variables(self):
        """Test loop context variable generation."""
        from flowmason_lab.operators.control_flow import LoopIterationContext

        ctx = LoopIterationContext(
            items=["a", "b", "c"],
            loop_stages=["process"],
            item_variable="letter",
            index_variable="pos",
        )

        vars = ctx.get_context_vars()
        assert vars["letter"] == "a"
        assert vars["pos"] == 0
        assert vars["loop_total"] == 3
        assert vars["loop_remaining"] == 2


class TestTryCatchContext:
    """Tests for TryCatchContext helper."""

    def test_trycatch_context_initialization(self):
        """Test try-catch context initialization."""
        from flowmason_lab.operators.control_flow import TryCatchContext

        ctx = TryCatchContext(
            try_stages=["risky"],
            catch_stages=["handle"],
            finally_stages=["cleanup"],
        )

        assert ctx.current_phase == "try"
        assert ctx.error is None
        assert ctx.get_current_stages() == ["risky"]

    def test_trycatch_context_error_recording(self):
        """Test error recording in try-catch context."""
        from flowmason_lab.operators.control_flow import TryCatchContext

        ctx = TryCatchContext(
            try_stages=["risky"],
            catch_stages=["handle"],
            finally_stages=[],
        )

        error = ValueError("Test error")
        ctx.record_error(error)

        assert ctx.error == error
        assert ctx.error_type == "ValueError"
        assert ctx.error_message == "Test error"
        assert ctx.should_catch is True

    def test_trycatch_context_phase_transitions(self):
        """Test phase transitions in try-catch context."""
        from flowmason_lab.operators.control_flow import TryCatchContext

        ctx = TryCatchContext(
            try_stages=["try1"],
            catch_stages=["catch1"],
            finally_stages=["finally1"],
        )

        assert ctx.current_phase == "try"
        ctx.transition_to_catch()
        assert ctx.current_phase == "catch"
        assert ctx.get_current_stages() == ["catch1"]
        ctx.transition_to_finally()
        assert ctx.current_phase == "finally"
        assert ctx.get_current_stages() == ["finally1"]

    def test_trycatch_context_specific_error_types(self):
        """Test catching specific error types."""
        from flowmason_lab.operators.control_flow import TryCatchContext

        ctx = TryCatchContext(
            try_stages=["risky"],
            catch_stages=["handle"],
            finally_stages=[],
            catch_error_types=["ValueError"],
        )

        # ValueError should be caught
        ctx.record_error(ValueError("test"))
        assert ctx.should_catch is True

        # Reset and test with different error type
        ctx2 = TryCatchContext(
            try_stages=["risky"],
            catch_stages=["handle"],
            finally_stages=[],
            catch_error_types=["KeyError"],
        )
        ctx2.record_error(ValueError("test"))
        assert ctx2.should_catch is False


class TestSubPipelineContext:
    """Tests for SubPipelineContext helper."""

    def test_subpipeline_context_initialization(self):
        """Test subpipeline context initialization."""
        from flowmason_lab.operators.control_flow import SubPipelineContext

        ctx = SubPipelineContext(
            pipeline_id="child-pipeline",
            input_data={"key": "value"},
            timeout_ms=30000,
        )

        assert ctx.pipeline_id == "child-pipeline"
        assert ctx.status == "pending"
        assert ctx.should_wait() is True

    def test_subpipeline_context_record_success(self):
        """Test recording successful execution."""
        from flowmason_lab.operators.control_flow import SubPipelineContext

        ctx = SubPipelineContext(
            pipeline_id="child",
            input_data={},
        )

        ctx.record_start("run-123")
        assert ctx.run_id == "run-123"
        assert ctx.status == "running"

        ctx.record_success({"result": "data"}, 500)
        assert ctx.status == "completed"
        assert ctx.result == {"result": "data"}
        assert ctx.execution_time_ms == 500

    def test_subpipeline_context_record_failure_propagate(self):
        """Test failure with propagate error handling."""
        from flowmason_lab.operators.control_flow import SubPipelineContext

        ctx = SubPipelineContext(
            pipeline_id="child",
            on_error="propagate",
        )

        ctx.record_failure("Network error", 1000)
        assert ctx.status == "failed"
        assert ctx.error == "Network error"

        with pytest.raises(RuntimeError, match="Sub-pipeline failed"):
            ctx.get_result()

    def test_subpipeline_context_record_failure_default(self):
        """Test failure with default fallback."""
        from flowmason_lab.operators.control_flow import SubPipelineContext

        ctx = SubPipelineContext(
            pipeline_id="child",
            on_error="default",
            default_result={"fallback": True},
        )

        ctx.record_failure("Error occurred", 500)
        assert ctx.status == "failed"
        assert ctx.result == {"fallback": True}
        assert ctx.get_result() == {"fallback": True}

    def test_subpipeline_context_record_failure_ignore(self):
        """Test failure with ignore error handling."""
        from flowmason_lab.operators.control_flow import SubPipelineContext

        ctx = SubPipelineContext(
            pipeline_id="child",
            on_error="ignore",
        )

        ctx.record_failure("Error", 500)
        assert ctx.status == "failed"
        assert ctx.result is None
        assert ctx.get_result() is None
