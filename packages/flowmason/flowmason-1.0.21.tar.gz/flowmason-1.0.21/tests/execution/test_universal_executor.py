"""
Tests for the Universal Executor.

Tests that ANY component type can be executed through a single code path.
"""

import pytest

from flowmason_core.config import ComponentConfig, ExecutionContext
from flowmason_core.execution import (
    UniversalExecutor,
    DAGExecutor,
    ComponentResult,
    UsageMetrics,
    ComponentExecutionError,
)
from flowmason_core.registry import ComponentRegistry


# Uses fixtures from conftest.py: temp_packages_dir, sample_node_package, sample_operator_package


@pytest.fixture
def registry_with_packages(temp_packages_dir, sample_node_package, sample_operator_package):
    """Create a registry with test packages loaded."""
    registry = ComponentRegistry(temp_packages_dir, auto_scan=False)
    registry.register_package(sample_node_package)
    registry.register_package(sample_operator_package)
    return registry


@pytest.fixture
def execution_context():
    """Create a basic execution context."""
    return ExecutionContext(
        run_id="test_run_123",
        pipeline_id="test-pipeline",
        pipeline_version="1.0.0",
        pipeline_input={"prompt": "Hello", "max_tokens": 500}
    )


class TestUniversalExecutorBasics:
    """Basic executor tests."""

    @pytest.mark.asyncio
    async def test_execute_node_component(self, registry_with_packages, execution_context):
        """Test executing a node component."""
        executor = UniversalExecutor(registry_with_packages, execution_context)

        config = ComponentConfig(
            id="test_stage",
            type="test_generator",  # From conftest sample_node_package
            input_mapping={
                "prompt": "{{input.prompt}}",
                "max_tokens": "{{input.max_tokens}}"
            }
        )

        result = await executor.execute_component(config)

        assert isinstance(result, ComponentResult)
        assert result.status == "success"
        assert result.component_id == "test_stage"
        assert result.component_type == "test_generator"
        assert "Generated from:" in result.output["content"]

    @pytest.mark.asyncio
    async def test_execute_operator_component(self, registry_with_packages, execution_context):
        """Test executing an operator component."""
        execution_context.pipeline_input = {"data": "hello", "uppercase": True}
        executor = UniversalExecutor(registry_with_packages, execution_context)

        config = ComponentConfig(
            id="op_stage",
            type="test_transform",  # From conftest sample_operator_package
            input_mapping={
                "data": "{{input.data}}",
                "uppercase": "{{input.uppercase}}"
            }
        )

        result = await executor.execute_component(config)

        assert result.status == "success"
        assert result.output["result"] == "HELLO"

    @pytest.mark.asyncio
    async def test_execute_with_static_values(self, registry_with_packages, execution_context):
        """Test executing with static (non-template) values."""
        executor = UniversalExecutor(registry_with_packages, execution_context)

        config = ComponentConfig(
            id="static_stage",
            type="test_generator",
            input_mapping={
                "prompt": "Static prompt",
                "max_tokens": 100
            }
        )

        result = await executor.execute_component(config)

        assert result.status == "success"
        assert "Static prompt" in result.output["content"]

    @pytest.mark.asyncio
    async def test_execute_with_defaults(self, registry_with_packages, execution_context):
        """Test executing with default values."""
        executor = UniversalExecutor(registry_with_packages, execution_context)

        config = ComponentConfig(
            id="default_stage",
            type="test_generator",
            input_mapping={
                "prompt": "Just prompt"
                # max_tokens will use default of 1000
            }
        )

        result = await executor.execute_component(config)

        assert result.status == "success"
        assert "Just prompt" in result.output["content"]


class TestUniversalExecutorUpstream:
    """Tests for upstream data handling."""

    @pytest.mark.asyncio
    async def test_execute_with_upstream_data(self, registry_with_packages, execution_context):
        """Test using upstream stage output."""
        executor = UniversalExecutor(registry_with_packages, execution_context)

        config = ComponentConfig(
            id="downstream_stage",
            type="test_transform",
            input_mapping={
                "data": "{{upstream.previous.content}}",
                "uppercase": True
            }
        )

        upstream_outputs = {
            "previous": {"content": "upstream_data"}
        }

        result = await executor.execute_component(config, upstream_outputs)

        assert result.status == "success"
        assert result.output["result"] == "UPSTREAM_DATA"


class TestUniversalExecutorMetrics:
    """Tests for execution metrics."""

    @pytest.mark.asyncio
    async def test_result_has_usage_metrics(self, registry_with_packages, execution_context):
        """Test that result includes usage metrics."""
        executor = UniversalExecutor(registry_with_packages, execution_context)

        config = ComponentConfig(
            id="test_stage",
            type="test_generator",
            input_mapping={"prompt": "test"}
        )

        result = await executor.execute_component(config)

        assert isinstance(result.usage, UsageMetrics)
        assert result.usage.duration_ms >= 0
        assert result.usage.total_tokens == 100  # From conftest test node (tokens_used=100)

    @pytest.mark.asyncio
    async def test_result_has_timing(self, registry_with_packages, execution_context):
        """Test that result includes timing information."""
        executor = UniversalExecutor(registry_with_packages, execution_context)

        config = ComponentConfig(
            id="test_stage",
            type="test_generator",
            input_mapping={"prompt": "test"}
        )

        result = await executor.execute_component(config)

        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.completed_at >= result.started_at

    @pytest.mark.asyncio
    async def test_result_has_trace_info(self, registry_with_packages, execution_context):
        """Test that result includes trace information."""
        executor = UniversalExecutor(registry_with_packages, execution_context)

        config = ComponentConfig(
            id="test_stage",
            type="test_generator",
            input_mapping={"prompt": "test"}
        )

        result = await executor.execute_component(config)

        assert result.trace_id is not None
        assert result.span_id is not None


class TestUniversalExecutorErrors:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_unknown_component_error(self, registry_with_packages, execution_context):
        """Test error for unknown component type."""
        executor = UniversalExecutor(registry_with_packages, execution_context)

        config = ComponentConfig(
            id="test_stage",
            type="nonexistent_component",
            input_mapping={}
        )

        with pytest.raises(ComponentExecutionError) as exc_info:
            await executor.execute_component(config)

        assert "nonexistent_component" in str(exc_info.value)


class TestDAGExecutor:
    """Tests for the DAG executor."""

    @pytest.mark.asyncio
    async def test_execute_single_stage(self, registry_with_packages, execution_context):
        """Test executing a single-stage DAG."""
        dag_executor = DAGExecutor(registry_with_packages, execution_context)

        stages = [
            ComponentConfig(
                id="only_stage",
                type="test_generator",
                input_mapping={"prompt": "{{input.prompt}}"}
            )
        ]

        results = await dag_executor.execute(stages, {"prompt": "DAG test"})

        assert "only_stage" in results
        assert results["only_stage"].status == "success"

    @pytest.mark.asyncio
    async def test_execute_multi_stage(self, registry_with_packages, execution_context):
        """Test executing a multi-stage DAG."""
        dag_executor = DAGExecutor(registry_with_packages, execution_context)

        stages = [
            ComponentConfig(
                id="stage1",
                type="test_generator",
                input_mapping={"prompt": "{{input.prompt}}"},
                depends_on=[]
            ),
            ComponentConfig(
                id="stage2",
                type="test_transform",
                input_mapping={
                    "data": "{{upstream.stage1.content}}",
                    "uppercase": True
                },
                depends_on=["stage1"]
            )
        ]

        results = await dag_executor.execute(stages, {"prompt": "Multi"})

        assert "stage1" in results
        assert "stage2" in results
        assert results["stage1"].status == "success"
        assert results["stage2"].status == "success"
        # stage2 should have uppercase content from stage1
        assert results["stage2"].output["result"].isupper()

    @pytest.mark.asyncio
    async def test_aggregate_usage(self, registry_with_packages, execution_context):
        """Test aggregating usage across stages."""
        dag_executor = DAGExecutor(registry_with_packages, execution_context)

        stages = [
            ComponentConfig(
                id="stage1",
                type="test_generator",
                input_mapping={"prompt": "test1"},
                depends_on=[]
            ),
            ComponentConfig(
                id="stage2",
                type="test_generator",
                input_mapping={"prompt": "test2"},
                depends_on=[]
            )
        ]

        results = await dag_executor.execute(stages, {})

        total_usage = dag_executor.aggregate_usage(results)

        # Each stage uses 100 tokens (from test node)
        assert total_usage.total_tokens == 200


class TestUsageMetricsAggregation:
    """Tests for usage metrics."""

    def test_usage_metrics_addition(self):
        """Test adding usage metrics together."""
        m1 = UsageMetrics(input_tokens=100, output_tokens=50, total_tokens=150, duration_ms=100)
        m2 = UsageMetrics(input_tokens=200, output_tokens=100, total_tokens=300, duration_ms=200)

        result = m1 + m2

        assert result.input_tokens == 300
        assert result.output_tokens == 150
        assert result.total_tokens == 450
        assert result.duration_ms == 300
