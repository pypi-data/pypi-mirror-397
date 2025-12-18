"""
Test actual pipeline execution with demo scenarios.

This tests the full execution path including:
- Component loading from registry
- Input mapping and template resolution
- Control flow directive processing
- DAG execution with dependencies
"""

import asyncio
import pytest
import json
import zipfile
from pathlib import Path
from typing import Any, Dict

from flowmason_core.registry import ComponentRegistry
from flowmason_core.config import ComponentConfig, ExecutionContext
from flowmason_core.execution import DAGExecutor


# =============================================================================
# Component Source Code (for creating test packages)
# =============================================================================

# Control Flow Components
CONDITIONAL_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/control_flow/conditional.py").read()
ROUTER_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/control_flow/router.py").read()
FOREACH_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/control_flow/foreach.py").read()
TRYCATCH_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/control_flow/trycatch.py").read()
SUBPIPELINE_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/control_flow/subpipeline.py").read()
RETURN_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/control_flow/return_early.py").read()

# Core Operators
LOGGER_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/core/logger.py").read()
JSON_TRANSFORM_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/core/json_transform.py").read()
FILTER_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/core/filter.py").read()
SCHEMA_VALIDATE_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/core/schema_validate.py").read()
VARIABLE_SET_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/operators/core/variable_set.py").read()

# Core Nodes
GENERATOR_SOURCE = open(Path(__file__).parent.parent / "lab/flowmason_lab/nodes/core/generator.py").read()


def create_test_package(output_dir: Path, name: str, source: str, comp_type: str = "node") -> Path:
    """Create a test package."""
    pkg_path = output_dir / f"{name}-1.0.0.fmpkg"
    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": f"Test package: {name}",
        "type": comp_type,
        "author": {"name": "Test", "email": "test@test.com"},
        "license": "MIT",
        "category": "testing",
        "entry_point": "index.py",
        "requires_llm": comp_type == "node",
        "dependencies": []
    }
    with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("flowmason-package.json", json.dumps(manifest, indent=2))
        zf.writestr("index.py", source)
    return pkg_path


def create_all_packages(pkg_dir: Path):
    """Create all test packages."""
    # Control flow
    create_test_package(pkg_dir, "conditional", CONDITIONAL_SOURCE, "control_flow")
    create_test_package(pkg_dir, "router", ROUTER_SOURCE, "control_flow")
    create_test_package(pkg_dir, "foreach", FOREACH_SOURCE, "control_flow")
    create_test_package(pkg_dir, "trycatch", TRYCATCH_SOURCE, "control_flow")
    create_test_package(pkg_dir, "subpipeline", SUBPIPELINE_SOURCE, "control_flow")
    create_test_package(pkg_dir, "return", RETURN_SOURCE, "control_flow")

    # Core operators
    create_test_package(pkg_dir, "logger", LOGGER_SOURCE, "operator")
    create_test_package(pkg_dir, "json_transform", JSON_TRANSFORM_SOURCE, "operator")
    create_test_package(pkg_dir, "filter", FILTER_SOURCE, "operator")
    create_test_package(pkg_dir, "schema_validate", SCHEMA_VALIDATE_SOURCE, "operator")
    create_test_package(pkg_dir, "variable_set", VARIABLE_SET_SOURCE, "operator")

    # Core nodes
    create_test_package(pkg_dir, "generator", GENERATOR_SOURCE, "node")


# =============================================================================
# Test Scenarios
# =============================================================================

class TestControlFlowExecution:
    """Test control flow execution in real pipelines."""

    @pytest.fixture
    def packages_dir(self, tmp_path):
        """Create directory with test packages."""
        pkg_dir = tmp_path / "packages"
        pkg_dir.mkdir()
        create_all_packages(pkg_dir)
        return pkg_dir

    @pytest.fixture
    def registry(self, packages_dir):
        """Create registry with test packages."""
        return ComponentRegistry(packages_dir, auto_scan=True)

    @pytest.fixture
    def context(self):
        """Create execution context."""
        return ExecutionContext(
            run_id="test-execution-001",
            pipeline_id="test-pipeline",
            pipeline_version="1.0.0",
            pipeline_input={}
        )

    @pytest.mark.asyncio
    async def test_conditional_branching(self, registry, context):
        """Test conditional branching with true/false paths."""
        context.pipeline_input = {"should_process": True}

        stages = [
            # Conditional check
            ComponentConfig(
                id="check_condition",
                type="conditional",
                input_mapping={
                    "condition": True,  # Hardcoded for test
                    "true_branch_stages": ["process_true"],
                    "false_branch_stages": ["process_false"]
                },
                depends_on=[]
            ),
            # True branch
            ComponentConfig(
                id="process_true",
                type="logger",
                input_mapping={
                    "message": "True branch executed",
                    "level": "info"
                },
                depends_on=["check_condition"]
            ),
            # False branch
            ComponentConfig(
                id="process_false",
                type="logger",
                input_mapping={
                    "message": "False branch executed",
                    "level": "info"
                },
                depends_on=["check_condition"]
            )
        ]

        dag = DAGExecutor(registry, context)
        results = await dag.execute(stages, context.pipeline_input)

        assert "check_condition" in results
        assert results["check_condition"].status == "success"
        # True branch should execute, false should be skipped
        assert results["check_condition"].output["branch_taken"] == "true"

    @pytest.mark.asyncio
    async def test_router_multi_way(self, registry, context):
        """Test router with multiple routes."""
        stages = [
            ComponentConfig(
                id="route_request",
                type="router",
                input_mapping={
                    "value": "billing",
                    "routes": {
                        "billing": ["handle_billing"],
                        "support": ["handle_support"],
                        "general": ["handle_general"]
                    },
                    "default_route": ["handle_default"]
                },
                depends_on=[]
            ),
            ComponentConfig(
                id="handle_billing",
                type="logger",
                input_mapping={"message": "Billing handler", "level": "info"},
                depends_on=["route_request"]
            ),
            ComponentConfig(
                id="handle_support",
                type="logger",
                input_mapping={"message": "Support handler", "level": "info"},
                depends_on=["route_request"]
            ),
            ComponentConfig(
                id="handle_general",
                type="logger",
                input_mapping={"message": "General handler", "level": "info"},
                depends_on=["route_request"]
            ),
            ComponentConfig(
                id="handle_default",
                type="logger",
                input_mapping={"message": "Default handler", "level": "info"},
                depends_on=["route_request"]
            )
        ]

        dag = DAGExecutor(registry, context)
        results = await dag.execute(stages, context.pipeline_input)

        assert results["route_request"].output["route_taken"] == "billing"
        # Billing should execute, others should be skipped

    @pytest.mark.asyncio
    async def test_foreach_iteration(self, registry, context):
        """Test foreach loop setup."""
        stages = [
            ComponentConfig(
                id="loop_setup",
                type="foreach",
                input_mapping={
                    "items": [{"id": 1}, {"id": 2}, {"id": 3}],
                    "loop_stages": ["process_item"],
                    "item_variable": "item",
                    "index_variable": "idx"
                },
                depends_on=[]
            ),
            ComponentConfig(
                id="process_item",
                type="logger",
                input_mapping={
                    "message": "Processing item",
                    "level": "info"
                },
                depends_on=["loop_setup"]
            )
        ]

        dag = DAGExecutor(registry, context)
        results = await dag.execute(stages, context.pipeline_input)

        assert results["loop_setup"].output["total_items"] == 3
        # Loop setup provides items_to_process for the executor to iterate
        assert "items_to_process" in results["loop_setup"].output

    @pytest.mark.asyncio
    async def test_trycatch_setup(self, registry, context):
        """Test try-catch error boundary setup."""
        stages = [
            ComponentConfig(
                id="error_boundary",
                type="trycatch",
                input_mapping={
                    "try_stages": ["risky_op"],
                    "catch_stages": ["handle_error"],
                    "finally_stages": ["cleanup"],
                    "max_retries": 2
                },
                depends_on=[]
            ),
            ComponentConfig(
                id="risky_op",
                type="logger",
                input_mapping={"message": "Risky operation", "level": "info"},
                depends_on=["error_boundary"]
            ),
            ComponentConfig(
                id="handle_error",
                type="logger",
                input_mapping={"message": "Error handled", "level": "warning"},
                depends_on=["error_boundary"]
            ),
            ComponentConfig(
                id="cleanup",
                type="logger",
                input_mapping={"message": "Cleanup", "level": "info"},
                depends_on=["risky_op", "handle_error"]
            )
        ]

        dag = DAGExecutor(registry, context)
        results = await dag.execute(stages, context.pipeline_input)

        assert results["error_boundary"].output["status"] == "pending"
        assert results["error_boundary"].output["directive"]["metadata"]["max_retries"] == 2

    @pytest.mark.asyncio
    async def test_subpipeline_setup(self, registry, context):
        """Test subpipeline component setup."""
        stages = [
            ComponentConfig(
                id="call_subpipeline",
                type="subpipeline",
                input_mapping={
                    "pipeline_id": "validation-pipeline",
                    "input_data": {"user_id": "123", "validate": True},
                    "timeout_ms": 30000,
                    "on_error": "default",
                    "default_result": {"validated": False}
                },
                depends_on=[]
            )
        ]

        dag = DAGExecutor(registry, context)
        results = await dag.execute(stages, context.pipeline_input)

        assert results["call_subpipeline"].output["pipeline_id"] == "validation-pipeline"
        assert results["call_subpipeline"].output["status"] == "pending"

    @pytest.mark.asyncio
    async def test_return_early_exit(self, registry, context):
        """Test early return component."""
        stages = [
            ComponentConfig(
                id="check_guard",
                type="return",
                input_mapping={
                    "condition": True,
                    "return_value": {"status": "early_exit", "reason": "guard triggered"},
                    "message": "Guard condition met"
                },
                depends_on=[]
            ),
            ComponentConfig(
                id="should_not_run",
                type="logger",
                input_mapping={"message": "This should be skipped", "level": "info"},
                depends_on=["check_guard"]
            )
        ]

        dag = DAGExecutor(registry, context)
        results = await dag.execute(stages, context.pipeline_input)

        assert results["check_guard"].output["should_return"] == True
        assert results["check_guard"].output["return_value"]["status"] == "early_exit"

    @pytest.mark.asyncio
    async def test_combined_operators(self, registry, context):
        """Test combining multiple operators in a pipeline."""
        context.pipeline_input = {
            "data": {"name": "John", "score": 85, "active": True}
        }

        stages = [
            # Log start
            ComponentConfig(
                id="log_start",
                type="logger",
                input_mapping={
                    "message": "Processing started",
                    "level": "info",
                    "data": {"received": True}
                },
                depends_on=[]
            ),
            # Transform data
            ComponentConfig(
                id="transform",
                type="json_transform",
                input_mapping={
                    "data": {"name": "John", "score": 85},
                    "mapping": {
                        "user_name": "name",
                        "user_score": "score"
                    }
                },
                depends_on=["log_start"]
            ),
            # Filter based on condition
            ComponentConfig(
                id="filter_check",
                type="filter",
                input_mapping={
                    "data": {"score": 85},
                    "condition": "data['score'] >= 80",
                    "filter_mode": "pass_fail"
                },
                depends_on=["transform"]
            ),
            # Validate output
            ComponentConfig(
                id="validate",
                type="schema_validate",
                input_mapping={
                    "data": {"user_name": "John", "user_score": 85},
                    "json_schema": {
                        "type": "object",
                        "required": ["user_name"],
                        "properties": {
                            "user_name": {"type": "string"},
                            "user_score": {"type": "integer"}
                        }
                    }
                },
                depends_on=["filter_check"]
            ),
            # Log completion
            ComponentConfig(
                id="log_complete",
                type="logger",
                input_mapping={
                    "message": "Processing complete",
                    "level": "info"
                },
                depends_on=["validate"]
            )
        ]

        dag = DAGExecutor(registry, context)
        results = await dag.execute(stages, context.pipeline_input)

        # All stages should complete
        assert len(results) == 5
        assert all(r.status in ("success", "skipped") for r in results.values())

        # Check specific results
        assert results["transform"].output["result"]["user_name"] == "John"
        assert results["filter_check"].output["passed"] == True
        assert results["validate"].output["valid"] == True


class TestComplexPipelines:
    """Test complex pipeline scenarios."""

    @pytest.fixture
    def packages_dir(self, tmp_path):
        pkg_dir = tmp_path / "packages"
        pkg_dir.mkdir()
        create_all_packages(pkg_dir)
        return pkg_dir

    @pytest.fixture
    def registry(self, packages_dir):
        return ComponentRegistry(packages_dir, auto_scan=True)

    @pytest.fixture
    def context(self):
        return ExecutionContext(
            run_id="complex-test-001",
            pipeline_id="complex-pipeline",
            pipeline_version="1.0.0",
            pipeline_input={}
        )

    @pytest.mark.asyncio
    async def test_nested_conditionals(self, registry, context):
        """Test nested conditional logic."""
        stages = [
            # First level check
            ComponentConfig(
                id="level1_check",
                type="conditional",
                input_mapping={
                    "condition": True,
                    "true_branch_stages": ["level2_check"],
                    "false_branch_stages": ["level1_false"]
                },
                depends_on=[]
            ),
            # Second level check (only runs if level1 is true)
            ComponentConfig(
                id="level2_check",
                type="conditional",
                input_mapping={
                    "condition": False,
                    "true_branch_stages": ["deep_true"],
                    "false_branch_stages": ["deep_false"]
                },
                depends_on=["level1_check"]
            ),
            ComponentConfig(
                id="level1_false",
                type="logger",
                input_mapping={"message": "Level 1 false", "level": "info"},
                depends_on=["level1_check"]
            ),
            ComponentConfig(
                id="deep_true",
                type="logger",
                input_mapping={"message": "Deep true", "level": "info"},
                depends_on=["level2_check"]
            ),
            ComponentConfig(
                id="deep_false",
                type="logger",
                input_mapping={"message": "Deep false", "level": "info"},
                depends_on=["level2_check"]
            )
        ]

        dag = DAGExecutor(registry, context)
        results = await dag.execute(stages, context.pipeline_input)

        # Level 1 should take true branch
        assert results["level1_check"].output["branch_taken"] == "true"
        # Level 2 should take false branch
        assert results["level2_check"].output["branch_taken"] == "false"

    @pytest.mark.asyncio
    async def test_parallel_execution(self, registry, context):
        """Test parallel stage execution."""
        stages = [
            # Three parallel stages
            ComponentConfig(
                id="parallel_a",
                type="logger",
                input_mapping={"message": "Parallel A", "level": "info"},
                depends_on=[]
            ),
            ComponentConfig(
                id="parallel_b",
                type="logger",
                input_mapping={"message": "Parallel B", "level": "info"},
                depends_on=[]
            ),
            ComponentConfig(
                id="parallel_c",
                type="logger",
                input_mapping={"message": "Parallel C", "level": "info"},
                depends_on=[]
            ),
            # Merge point
            ComponentConfig(
                id="merge",
                type="logger",
                input_mapping={"message": "Merge point", "level": "info"},
                depends_on=["parallel_a", "parallel_b", "parallel_c"]
            )
        ]

        dag = DAGExecutor(registry, context)
        results = await dag.execute(stages, context.pipeline_input)

        assert len(results) == 4
        assert all(r.status == "success" for r in results.values())


# =============================================================================
# Main runner
# =============================================================================

async def run_all_tests():
    """Run all demo execution tests."""
    import sys
    import tempfile

    print("\n" + "="*60)
    print("  Demo Pipeline Execution Tests")
    print("="*60 + "\n")

    # Create temp directory for packages
    with tempfile.TemporaryDirectory() as tmp_dir:
        pkg_dir = Path(tmp_dir) / "packages"
        pkg_dir.mkdir()

        # Create all component packages
        print("  Creating component packages...")
        create_all_packages(pkg_dir)
        print(f"  Created packages in {pkg_dir}")

        registry = ComponentRegistry(pkg_dir, auto_scan=True)
        print(f"  Loaded {len(registry.list_components())} components")

        context = ExecutionContext(
            run_id="demo-test-001",
            pipeline_id="demo-test",
            pipeline_version="1.0.0",
            pipeline_input={}
        )

        tests = [
            ("Conditional Branching", test_conditional),
            ("Router Multi-way", test_router),
            ("ForEach Loop", test_foreach),
            ("TryCatch Error Handling", test_trycatch),
            ("SubPipeline Setup", test_subpipeline),
            ("Return Early Exit", test_return),
            ("Combined Operators", test_combined),
        ]

        passed = 0
        failed = 0

        for name, test_func in tests:
            try:
                await test_func(registry, context)
                print(f"  [PASS] {name}")
                passed += 1
            except Exception as e:
                print(f"  [FAIL] {name}: {e}")
                failed += 1

        print(f"\n  Results: {passed} passed, {failed} failed\n")
        return passed, failed


async def test_conditional(registry, context):
    stages = [
        ComponentConfig(
            id="check",
            type="conditional",
            input_mapping={
                "condition": True,
                "true_branch_stages": ["t"],
                "false_branch_stages": ["f"]
            },
            depends_on=[]
        )
    ]
    dag = DAGExecutor(registry, context)
    results = await dag.execute(stages, {})
    assert results["check"].output["branch_taken"] == "true"


async def test_router(registry, context):
    stages = [
        ComponentConfig(
            id="route",
            type="router",
            input_mapping={
                "value": "billing",
                "routes": {"billing": ["b"], "support": ["s"]},
                "default_route": ["d"]
            },
            depends_on=[]
        )
    ]
    dag = DAGExecutor(registry, context)
    results = await dag.execute(stages, {})
    assert results["route"].output["route_taken"] == "billing"


async def test_foreach(registry, context):
    stages = [
        ComponentConfig(
            id="loop",
            type="foreach",
            input_mapping={
                "items": [1, 2, 3],
                "loop_stages": ["process"],
                "item_variable": "item"
            },
            depends_on=[]
        )
    ]
    dag = DAGExecutor(registry, context)
    results = await dag.execute(stages, {})
    assert results["loop"].output["total_items"] == 3


async def test_trycatch(registry, context):
    stages = [
        ComponentConfig(
            id="tc",
            type="trycatch",
            input_mapping={
                "try_stages": ["risky"],
                "catch_stages": ["handle"],
                "finally_stages": [],
                "max_retries": 2
            },
            depends_on=[]
        )
    ]
    dag = DAGExecutor(registry, context)
    results = await dag.execute(stages, {})
    assert results["tc"].output["status"] == "pending"


async def test_subpipeline(registry, context):
    stages = [
        ComponentConfig(
            id="sp",
            type="subpipeline",
            input_mapping={
                "pipeline_id": "child",
                "input_data": {"x": 1}
            },
            depends_on=[]
        )
    ]
    dag = DAGExecutor(registry, context)
    results = await dag.execute(stages, {})
    assert results["sp"].output["pipeline_id"] == "child"


async def test_return(registry, context):
    stages = [
        ComponentConfig(
            id="ret",
            type="return",
            input_mapping={
                "condition": True,
                "return_value": {"done": True}
            },
            depends_on=[]
        )
    ]
    dag = DAGExecutor(registry, context)
    results = await dag.execute(stages, {})
    assert results["ret"].output["should_return"] == True


async def test_combined(registry, context):
    stages = [
        ComponentConfig(
            id="log1",
            type="logger",
            input_mapping={"message": "Start", "level": "info"},
            depends_on=[]
        ),
        ComponentConfig(
            id="transform",
            type="json_transform",
            input_mapping={
                "data": {"a": 1, "b": 2},
                "mapping": {"x": "a", "y": "b"}
            },
            depends_on=["log1"]
        ),
        ComponentConfig(
            id="filter",
            type="filter",
            input_mapping={
                "data": {"score": 85},
                "condition": "data['score'] >= 80"
            },
            depends_on=["transform"]
        ),
        ComponentConfig(
            id="log2",
            type="logger",
            input_mapping={"message": "Done", "level": "info"},
            depends_on=["filter"]
        )
    ]
    dag = DAGExecutor(registry, context)
    results = await dag.execute(stages, {})
    assert len(results) == 4
    assert results["transform"].output["result"]["x"] == 1
    assert results["filter"].output["passed"] == True


if __name__ == "__main__":
    asyncio.run(run_all_tests())
