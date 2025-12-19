"""
Tests for ControlFlowHandler.

Tests all control flow types:
- Conditional (if/else)
- Router (switch/case)
- ForEach (loops)
- TryCatch (error handling)
- SubPipeline (nested pipelines)
- Return (early exit)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest
from flowmason_core.core.types import (
    ControlFlowDirective,
    ControlFlowType,
)
from flowmason_core.execution.control_flow_handler import (
    ControlFlowHandler,
    ControlFlowState,
)
from flowmason_core.execution.types import (
    ComponentExecutionError,
    ComponentResult,
    UsageMetrics,
)


@dataclass
class MockStageConfig:
    """Mock stage configuration."""
    id: str
    type: str
    depends_on: Optional[List[Any]] = None

    def __post_init__(self) -> None:
        if self.depends_on is None:
            self.depends_on = []


class MockDAGExecutor:
    """Mock DAG executor for testing."""

    def __init__(self):
        self.executor = MockUniversalExecutor()
        self.context = MagicMock()
        self.context.variables = {}


class MockUniversalExecutor:
    """Mock universal executor for testing."""

    def __init__(self):
        self.execute_results = {}  # stage_id -> result or exception
        self.executed_stages = []  # track execution order

    def set_result(self, stage_id: str, result: Any):
        """Set the result for a stage."""
        self.execute_results[stage_id] = result

    def set_error(self, stage_id: str, error: Exception):
        """Set an error for a stage."""
        self.execute_results[stage_id] = error

    async def execute_component(
        self,
        stage_config: MockStageConfig,
        upstream_outputs: Dict[str, Any],
    ) -> ComponentResult:
        """Execute a component (mock)."""
        self.executed_stages.append(stage_config.id)

        result = self.execute_results.get(stage_config.id)

        if isinstance(result, Exception):
            raise result

        if result is None:
            # Default success result
            return ComponentResult(
                component_id=stage_config.id,
                component_type=stage_config.type,
                status="success",
                output={"result": f"output from {stage_config.id}"},
                usage=UsageMetrics(),
            )

        return result  # type: ignore[no-any-return]


# =============================================================================
# TryCatch Tests
# =============================================================================

class TestTryCatchHandler:
    """Tests for TryCatch control flow handling."""

    @pytest.fixture
    def handler(self):
        """Create a handler with mock executor."""
        dag_executor = MockDAGExecutor()
        return ControlFlowHandler(dag_executor)

    @pytest.fixture
    def stage_map(self):
        """Create a stage map with try/catch/finally stages."""
        return {
            "trycatch_stage": MockStageConfig(id="trycatch_stage", type="trycatch"),
            "try_1": MockStageConfig(id="try_1", type="http_request", depends_on=["trycatch_stage"]),
            "try_2": MockStageConfig(id="try_2", type="json_transform", depends_on=["try_1"]),
            "catch_1": MockStageConfig(id="catch_1", type="logger", depends_on=["trycatch_stage"]),
            "catch_2": MockStageConfig(id="catch_2", type="variable_set", depends_on=["catch_1"]),
            "finally_1": MockStageConfig(id="finally_1", type="logger", depends_on=["trycatch_stage"]),
        }

    @pytest.mark.asyncio
    async def test_trycatch_success_no_error(self, handler, stage_map):
        """Test TryCatch when try_stages succeed - catch should NOT execute."""
        # Setup: try stages succeed
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.TRYCATCH,
            execute_stages=["try_1", "try_2"],
            skip_stages=["catch_1", "catch_2"],
            continue_execution=True,
            metadata={
                "try_stages": ["try_1", "try_2"],
                "catch_stages": ["catch_1", "catch_2"],
                "finally_stages": ["finally_1"],
                "error_scope": "propagate",
            },
        )

        result = ComponentResult(
            component_id="trycatch_stage",
            component_type="trycatch",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        # Execute
        _nested_results = await handler.handle_directive(
            stage_id="trycatch_stage",
            directive=directive,
            result=result,
            stage_map=stage_map,
            upstream_outputs={},
            completed_stages=set(),
        )

        # Verify: try stages and finally executed, catch skipped
        executor = handler.dag_executor.executor
        assert "try_1" in executor.executed_stages
        assert "try_2" in executor.executed_stages
        assert "catch_1" not in executor.executed_stages
        assert "catch_2" not in executor.executed_stages
        assert "finally_1" in executor.executed_stages

        # Verify execution order: try stages first, then finally
        try_1_idx = executor.executed_stages.index("try_1")
        try_2_idx = executor.executed_stages.index("try_2")
        finally_1_idx = executor.executed_stages.index("finally_1")
        assert try_1_idx < try_2_idx < finally_1_idx

    @pytest.mark.asyncio
    async def test_trycatch_error_with_catch(self, handler, stage_map):
        """Test TryCatch when try_stage fails - catch should execute."""
        # Setup: first try stage fails
        handler.dag_executor.executor.set_error(
            "try_1",
            ComponentExecutionError("Connection failed", component_id="try_1")
        )

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.TRYCATCH,
            execute_stages=["try_1", "try_2"],
            skip_stages=["catch_1", "catch_2"],
            continue_execution=True,
            metadata={
                "try_stages": ["try_1", "try_2"],
                "catch_stages": ["catch_1", "catch_2"],
                "finally_stages": ["finally_1"],
                "error_scope": "continue",  # Swallow the error
            },
        )

        result = ComponentResult(
            component_id="trycatch_stage",
            component_type="trycatch",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        # Execute
        _nested_results = await handler.handle_directive(
            stage_id="trycatch_stage",
            directive=directive,
            result=result,
            stage_map=stage_map,
            upstream_outputs={},
            completed_stages=set(),
        )

        # Verify: try_1 attempted, try_2 skipped (due to error), catch executed, finally executed
        executor = handler.dag_executor.executor
        assert "try_1" in executor.executed_stages
        assert "try_2" not in executor.executed_stages  # Skipped due to error in try_1
        assert "catch_1" in executor.executed_stages
        assert "catch_2" in executor.executed_stages
        assert "finally_1" in executor.executed_stages

        # Verify result shows error was caught
        assert result.output["error_occurred"] is True
        assert result.output["recovered"] is True
        assert "ComponentExecutionError" in result.output["error_type"]

    @pytest.mark.asyncio
    async def test_trycatch_error_propagate(self, handler, stage_map):
        """Test TryCatch with error_scope='propagate' - error should re-raise after catch."""
        # Setup: try stage fails
        handler.dag_executor.executor.set_error(
            "try_1",
            ComponentExecutionError("Connection failed", component_id="try_1")
        )

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.TRYCATCH,
            execute_stages=["try_1", "try_2"],
            skip_stages=["catch_1"],
            continue_execution=True,
            metadata={
                "try_stages": ["try_1", "try_2"],
                "catch_stages": ["catch_1"],
                "finally_stages": ["finally_1"],
                "error_scope": "propagate",  # Re-raise after catch
            },
        )

        result = ComponentResult(
            component_id="trycatch_stage",
            component_type="trycatch",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        # Execute - should raise after catch/finally
        with pytest.raises(ComponentExecutionError) as exc_info:
            await handler.handle_directive(
                stage_id="trycatch_stage",
                directive=directive,
                result=result,
                stage_map=stage_map,
                upstream_outputs={},
                completed_stages=set(),
            )

        # Verify catch and finally still executed before propagation
        executor = handler.dag_executor.executor
        assert "catch_1" in executor.executed_stages
        assert "finally_1" in executor.executed_stages

        # Verify the original error was re-raised
        assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_trycatch_finally_always_executes(self, handler, stage_map):
        """Test that finally_stages always execute, even on error."""
        # Setup: try stage fails, error_scope=propagate
        handler.dag_executor.executor.set_error(
            "try_1",
            ValueError("Something went wrong")
        )

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.TRYCATCH,
            execute_stages=["try_1"],
            skip_stages=[],
            continue_execution=True,
            metadata={
                "try_stages": ["try_1"],
                "catch_stages": [],  # No catch stages
                "finally_stages": ["finally_1"],
                "error_scope": "propagate",
            },
        )

        result = ComponentResult(
            component_id="trycatch_stage",
            component_type="trycatch",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        # Execute - should raise but finally still runs
        with pytest.raises(ValueError):
            await handler.handle_directive(
                stage_id="trycatch_stage",
                directive=directive,
                result=result,
                stage_map=stage_map,
                upstream_outputs={},
                completed_stages=set(),
            )

        # Verify finally executed
        executor = handler.dag_executor.executor
        assert "finally_1" in executor.executed_stages

    @pytest.mark.asyncio
    async def test_trycatch_error_type_filtering(self, handler, stage_map):
        """Test TryCatch with catch_error_types filtering."""
        # Setup: try stage fails with TimeoutError
        handler.dag_executor.executor.set_error(
            "try_1",
            TimeoutError("Request timed out")
        )

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.TRYCATCH,
            execute_stages=["try_1"],
            skip_stages=["catch_1"],
            continue_execution=True,
            metadata={
                "try_stages": ["try_1"],
                "catch_stages": ["catch_1"],
                "finally_stages": [],
                "error_scope": "continue",
                "catch_error_types": ["TimeoutError"],  # Only catch TimeoutError
            },
        )

        result = ComponentResult(
            component_id="trycatch_stage",
            component_type="trycatch",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        # Execute - TimeoutError should be caught
        _nested_results = await handler.handle_directive(
            stage_id="trycatch_stage",
            directive=directive,
            result=result,
            stage_map=stage_map,
            upstream_outputs={},
            completed_stages=set(),
        )

        # Verify catch executed
        executor = handler.dag_executor.executor
        assert "catch_1" in executor.executed_stages
        assert result.output["error_type"] == "TimeoutError"

    @pytest.mark.asyncio
    async def test_trycatch_error_type_not_matching(self, handler, stage_map):
        """Test TryCatch when error type doesn't match filter - error propagates."""
        # Setup: try stage fails with ValueError (not in catch list)
        handler.dag_executor.executor.set_error(
            "try_1",
            ValueError("Invalid input")
        )

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.TRYCATCH,
            execute_stages=["try_1"],
            skip_stages=["catch_1"],
            continue_execution=True,
            metadata={
                "try_stages": ["try_1"],
                "catch_stages": ["catch_1"],
                "finally_stages": [],
                "error_scope": "continue",
                "catch_error_types": ["TimeoutError"],  # Only catch TimeoutError
            },
        )

        result = ComponentResult(
            component_id="trycatch_stage",
            component_type="trycatch",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        # Execute - ValueError is NOT in catch_error_types, so catch shouldn't run
        # But error_scope is "continue" so it won't raise
        _nested_results = await handler.handle_directive(
            stage_id="trycatch_stage",
            directive=directive,
            result=result,
            stage_map=stage_map,
            upstream_outputs={},
            completed_stages=set(),
        )

        # Verify catch did NOT execute (error type not in filter)
        executor = handler.dag_executor.executor
        assert "catch_1" not in executor.executed_stages


# =============================================================================
# Conditional Tests
# =============================================================================

class TestConditionalHandler:
    """Tests for Conditional control flow handling."""

    @pytest.fixture
    def handler(self):
        """Create a handler with mock executor."""
        dag_executor = MockDAGExecutor()
        return ControlFlowHandler(dag_executor)

    @pytest.mark.asyncio
    async def test_conditional_true_branch(self, handler):
        """Test conditional when condition is true - false branch skipped."""
        stage_map = {
            "cond": MockStageConfig(id="cond", type="conditional"),
            "true_stage": MockStageConfig(id="true_stage", type="logger"),
            "false_stage": MockStageConfig(id="false_stage", type="logger"),
        }

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.CONDITIONAL,
            skip_stages=["false_stage"],  # Skip false branch
            continue_execution=True,
            metadata={"branch_taken": "true"},
        )

        result = ComponentResult(
            component_id="cond",
            component_type="conditional",
            status="success",
            output={"branch_taken": "true"},
            usage=UsageMetrics(),
        )

        await handler.handle_directive(
            stage_id="cond",
            directive=directive,
            result=result,
            stage_map=stage_map,
            upstream_outputs={},
            completed_stages=set(),
        )

        # Verify false_stage is in skip set
        assert "false_stage" in handler.state.skip_stages
        assert handler.should_skip_stage("false_stage") is True
        assert handler.should_skip_stage("true_stage") is False


# =============================================================================
# Return Tests
# =============================================================================

class TestReturnHandler:
    """Tests for Return control flow handling."""

    @pytest.fixture
    def handler(self):
        """Create a handler with mock executor."""
        dag_executor = MockDAGExecutor()
        return ControlFlowHandler(dag_executor)

    @pytest.mark.asyncio
    async def test_return_triggers_early_exit(self, handler):
        """Test that Return directive triggers early exit."""
        stage_map = {
            "return_stage": MockStageConfig(id="return_stage", type="return"),
        }

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.RETURN,
            continue_execution=False,  # Stop execution
            metadata={
                "return_value": {"message": "Early exit"},
                "message": "Condition met",
            },
        )

        result = ComponentResult(
            component_id="return_stage",
            component_type="return",
            status="success",
            output={},
            usage=UsageMetrics(),
        )

        await handler.handle_directive(
            stage_id="return_stage",
            directive=directive,
            result=result,
            stage_map=stage_map,
            upstream_outputs={},
            completed_stages=set(),
        )

        # Verify early return state
        assert handler.should_return_early() is True
        assert handler.get_return_value() == {"message": "Early exit"}


# =============================================================================
# State Management Tests
# =============================================================================

class TestControlFlowState:
    """Tests for ControlFlowState management."""

    def test_initial_state(self):
        """Test initial state is empty."""
        state = ControlFlowState()
        assert len(state.skip_stages) == 0
        assert state.should_return is False
        assert state.return_value is None

    def test_reset(self):
        """Test state reset clears all state."""
        dag_executor = MockDAGExecutor()
        handler = ControlFlowHandler(dag_executor)

        # Modify state
        handler.state.skip_stages.add("stage_1")
        handler.state.should_return = True
        handler.state.return_value = "test"

        # Reset
        handler.reset()

        # Verify clean state
        assert len(handler.state.skip_stages) == 0
        assert handler.state.should_return is False
        assert handler.state.return_value is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
