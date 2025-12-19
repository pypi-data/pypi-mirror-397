"""
Tests for ForEach control flow handling.

Tests sequential and parallel loop execution.
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
    LoopContext,
)
from flowmason_core.execution.types import (
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
        self.execute_results = {}
        self.executed_stages = []
        self.execution_inputs = {}  # Track inputs for verification

    def set_result(self, stage_id: str, result: Any):
        self.execute_results[stage_id] = result

    async def execute_component(
        self,
        stage_config: MockStageConfig,
        upstream_outputs: Dict[str, Any],
    ) -> ComponentResult:
        self.executed_stages.append(stage_config.id)
        self.execution_inputs[stage_config.id] = upstream_outputs.copy()

        result = self.execute_results.get(stage_config.id)
        if isinstance(result, Exception):
            raise result

        if result is None:
            return ComponentResult(
                component_id=stage_config.id,
                component_type=stage_config.type,
                status="success",
                output={"result": f"output from {stage_config.id}"},
                usage=UsageMetrics(),
            )
        return result  # type: ignore[no-any-return]


class TestForEachHandler:
    """Tests for ForEach control flow handling."""

    @pytest.fixture
    def handler(self):
        dag_executor = MockDAGExecutor()
        return ControlFlowHandler(dag_executor)

    @pytest.fixture
    def stage_map(self):
        return {
            "foreach_stage": MockStageConfig(id="foreach_stage", type="foreach"),
            "process_item": MockStageConfig(id="process_item", type="json_transform"),
            "save_item": MockStageConfig(id="save_item", type="variable_set"),
        }

    @pytest.mark.asyncio
    async def test_foreach_sequential_execution(self, handler, stage_map):
        """Test ForEach executes loop_stages for each item sequentially."""
        items = ["a", "b", "c"]

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.FOREACH,
            loop_items=items,
            continue_execution=True,
            metadata={
                "loop_stages": ["process_item", "save_item"],
                "item_variable": "item",
                "index_variable": "index",
                "parallel": False,
                "collect_results": True,
            },
        )

        result = ComponentResult(
            component_id="foreach_stage",
            component_type="foreach",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        _nested_results = await handler.handle_directive(
            stage_id="foreach_stage",
            directive=directive,
            result=result,
            stage_map=stage_map,
            upstream_outputs={},
            completed_stages=set(),
        )

        # Should execute loop_stages for each item
        executor = handler.dag_executor.executor
        # 3 items x 2 stages = 6 executions (with iteration suffix)
        assert len(executor.executed_stages) == 6

        # Check iteration naming: stage_id_iter_N
        assert "process_item" in executor.executed_stages[0]
        assert "save_item" in executor.executed_stages[1]

    @pytest.mark.asyncio
    async def test_foreach_empty_items(self, handler, stage_map):
        """Test ForEach with empty items list."""
        directive = ControlFlowDirective(
            directive_type=ControlFlowType.FOREACH,
            loop_items=[],
            continue_execution=True,
            metadata={
                "loop_stages": ["process_item"],
                "parallel": False,
            },
        )

        result = ComponentResult(
            component_id="foreach_stage",
            component_type="foreach",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        _nested_results = await handler.handle_directive(
            stage_id="foreach_stage",
            directive=directive,
            result=result,
            stage_map=stage_map,
            upstream_outputs={},
            completed_stages=set(),
        )

        # No executions for empty list
        assert len(handler.dag_executor.executor.executed_stages) == 0
        assert _nested_results == {}

    @pytest.mark.asyncio
    async def test_foreach_parallel_execution(self, handler, stage_map):
        """Test ForEach parallel execution with semaphore."""
        items = [1, 2, 3, 4, 5]

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.FOREACH,
            loop_items=items,
            continue_execution=True,
            metadata={
                "loop_stages": ["process_item"],
                "parallel": True,
                "max_parallel": 2,  # Only 2 at a time
            },
        )

        result = ComponentResult(
            component_id="foreach_stage",
            component_type="foreach",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        _nested_results = await handler.handle_directive(
            stage_id="foreach_stage",
            directive=directive,
            result=result,
            stage_map=stage_map,
            upstream_outputs={},
            completed_stages=set(),
        )

        # All items processed
        executor = handler.dag_executor.executor
        assert len(executor.executed_stages) == 5

    @pytest.mark.asyncio
    async def test_foreach_break_on_error(self, handler, stage_map):
        """Test ForEach stops on error when break_on_error=True."""
        handler.dag_executor.executor.set_result(
            "process_item",
            Exception("Processing failed")
        )

        directive = ControlFlowDirective(
            directive_type=ControlFlowType.FOREACH,
            loop_items=[1, 2, 3],
            continue_execution=True,
            metadata={
                "loop_stages": ["process_item"],
                "parallel": False,
                "break_on_error": True,
            },
        )

        result = ComponentResult(
            component_id="foreach_stage",
            component_type="foreach",
            status="pending",
            output={},
            usage=UsageMetrics(),
        )

        with pytest.raises(Exception) as exc_info:
            await handler.handle_directive(
                stage_id="foreach_stage",
                directive=directive,
                result=result,
                stage_map=stage_map,
                upstream_outputs={},
                completed_stages=set(),
            )

        assert "Processing failed" in str(exc_info.value)
        # Should stop after first error
        assert len(handler.dag_executor.executor.executed_stages) == 1


class TestLoopContext:
    """Tests for LoopContext helper class."""

    def test_loop_context_properties(self):
        """Test LoopContext properties."""
        ctx = LoopContext(
            loop_stage_id="foreach_1",
            items=[1, 2, 3],
            item_variable="num",
            index_variable="idx",
        )

        assert ctx.current_item == 1
        assert ctx.has_more is True
        assert ctx.is_complete is False

    def test_loop_context_advance(self):
        """Test advancing through loop items."""
        ctx = LoopContext(
            loop_stage_id="foreach_1",
            items=["a", "b"],
        )

        assert ctx.current_item == "a"
        assert ctx.advance() is True
        assert ctx.current_item == "b"
        assert ctx.advance() is False
        assert ctx.is_complete is True

    def test_loop_context_variables(self):
        """Test loop variable injection."""
        ctx = LoopContext(
            loop_stage_id="foreach_1",
            items=["x", "y", "z"],
            item_variable="letter",
            index_variable="pos",
        )
        ctx.advance()  # Move to index 1

        vars = ctx.get_loop_variables()
        assert vars["letter"] == "y"
        assert vars["pos"] == 1
        assert vars["loop_total"] == 3
        assert vars["loop_remaining"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
