"""
FlowMason Demo Runner with Statistics Collection

Runs all demo pipelines and collects comprehensive statistics about:
- Execution times
- Stage completion rates
- Control flow paths taken
- Component usage
- Error handling effectiveness
"""

import asyncio
import json
import time
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List
from dataclasses import dataclass, field, asdict
from collections import defaultdict

from flowmason_core.registry import ComponentRegistry
from flowmason_core.config import ComponentConfig, ExecutionContext
from flowmason_core.execution import DAGExecutor


# =============================================================================
# Statistics Data Classes
# =============================================================================

@dataclass
class StageStats:
    """Statistics for a single stage execution."""
    stage_id: str
    component_type: str
    status: str
    duration_ms: float = 0.0
    output_keys: List[str] = field(default_factory=list)
    error: str = None


@dataclass
class PipelineRunStats:
    """Statistics for a single pipeline run."""
    pipeline_name: str
    test_case: str
    status: str
    total_duration_ms: float
    stages_executed: int
    stages_skipped: int
    stages_failed: int
    stage_stats: List[StageStats] = field(default_factory=list)
    control_flow_decisions: Dict[str, Any] = field(default_factory=dict)
    error: str = None


@dataclass
class DemoStatistics:
    """Aggregate statistics for all demo runs."""
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_stages_executed: int = 0
    total_stages_skipped: int = 0
    total_execution_time_ms: float = 0.0
    component_usage: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    control_flow_stats: Dict[str, Dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))
    pipeline_runs: List[PipelineRunStats] = field(default_factory=list)

    def add_run(self, run_stats: PipelineRunStats):
        self.total_runs += 1
        if run_stats.status == "success":
            self.successful_runs += 1
        else:
            self.failed_runs += 1
        self.total_stages_executed += run_stats.stages_executed
        self.total_stages_skipped += run_stats.stages_skipped
        self.total_execution_time_ms += run_stats.total_duration_ms
        self.pipeline_runs.append(run_stats)

        # Track component usage
        for stage_stat in run_stats.stage_stats:
            self.component_usage[stage_stat.component_type] += 1

        # Track control flow decisions
        for cf_type, decision in run_stats.control_flow_decisions.items():
            if isinstance(decision, str):
                self.control_flow_stats[cf_type][decision] += 1


# =============================================================================
# Component Source Loading
# =============================================================================

def load_component_sources():
    """Load all component source files."""
    base_path = Path(__file__).parent.parent

    sources = {
        # Control flow
        "conditional": (base_path / "lab/flowmason_lab/operators/control_flow/conditional.py").read_text(),
        "router": (base_path / "lab/flowmason_lab/operators/control_flow/router.py").read_text(),
        "foreach": (base_path / "lab/flowmason_lab/operators/control_flow/foreach.py").read_text(),
        "trycatch": (base_path / "lab/flowmason_lab/operators/control_flow/trycatch.py").read_text(),
        "subpipeline": (base_path / "lab/flowmason_lab/operators/control_flow/subpipeline.py").read_text(),
        "return": (base_path / "lab/flowmason_lab/operators/control_flow/return_early.py").read_text(),
        # Core operators
        "logger": (base_path / "lab/flowmason_lab/operators/core/logger.py").read_text(),
        "json_transform": (base_path / "lab/flowmason_lab/operators/core/json_transform.py").read_text(),
        "filter": (base_path / "lab/flowmason_lab/operators/core/filter.py").read_text(),
        "schema_validate": (base_path / "lab/flowmason_lab/operators/core/schema_validate.py").read_text(),
        "variable_set": (base_path / "lab/flowmason_lab/operators/core/variable_set.py").read_text(),
        # Core nodes
        "generator": (base_path / "lab/flowmason_lab/nodes/core/generator.py").read_text(),
    }
    return sources


def create_package(output_dir: Path, name: str, source: str, comp_type: str) -> Path:
    """Create a .fmpkg package file."""
    pkg_path = output_dir / f"{name}-1.0.0.fmpkg"
    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": f"Package: {name}",
        "type": comp_type,
        "author": {"name": "FlowMason", "email": "demo@flowmason.dev"},
        "license": "MIT",
        "category": "demo",
        "entry_point": "index.py",
        "requires_llm": comp_type == "node",
        "dependencies": []
    }
    with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("flowmason-package.json", json.dumps(manifest, indent=2))
        zf.writestr("index.py", source)
    return pkg_path


def setup_registry(pkg_dir: Path) -> ComponentRegistry:
    """Set up registry with all components."""
    sources = load_component_sources()

    # Create packages
    type_map = {
        "conditional": "control_flow",
        "router": "control_flow",
        "foreach": "control_flow",
        "trycatch": "control_flow",
        "subpipeline": "control_flow",
        "return": "control_flow",
        "logger": "operator",
        "json_transform": "operator",
        "filter": "operator",
        "schema_validate": "operator",
        "variable_set": "operator",
        "generator": "node",
    }

    for name, source in sources.items():
        create_package(pkg_dir, name, source, type_map[name])

    return ComponentRegistry(pkg_dir, auto_scan=True)


# =============================================================================
# Demo Test Cases
# =============================================================================

CONDITIONAL_TESTS = [
    {
        "name": "Conditional - True Branch",
        "stages": [
            {"id": "check", "type": "conditional", "input_mapping": {
                "condition": True,
                "true_branch_stages": ["true_path"],
                "false_branch_stages": ["false_path"]
            }, "depends_on": []},
            {"id": "true_path", "type": "logger", "input_mapping": {
                "message": "True branch taken", "level": "info"
            }, "depends_on": ["check"]},
            {"id": "false_path", "type": "logger", "input_mapping": {
                "message": "False branch taken", "level": "info"
            }, "depends_on": ["check"]}
        ],
        "input": {}
    },
    {
        "name": "Conditional - False Branch",
        "stages": [
            {"id": "check", "type": "conditional", "input_mapping": {
                "condition": False,
                "true_branch_stages": ["true_path"],
                "false_branch_stages": ["false_path"]
            }, "depends_on": []},
            {"id": "true_path", "type": "logger", "input_mapping": {
                "message": "True branch taken", "level": "info"
            }, "depends_on": ["check"]},
            {"id": "false_path", "type": "logger", "input_mapping": {
                "message": "False branch taken", "level": "info"
            }, "depends_on": ["check"]}
        ],
        "input": {}
    },
    {
        "name": "Conditional - With Expression (score > 80)",
        "stages": [
            {"id": "check", "type": "conditional", "input_mapping": {
                "condition": 95,
                "condition_expression": "value > 80",
                "true_branch_stages": ["pass"],
                "false_branch_stages": ["fail"]
            }, "depends_on": []},
        ],
        "input": {}
    },
    {
        "name": "Conditional - With Expression (score < 80)",
        "stages": [
            {"id": "check", "type": "conditional", "input_mapping": {
                "condition": 65,
                "condition_expression": "value > 80",
                "true_branch_stages": ["pass"],
                "false_branch_stages": ["fail"]
            }, "depends_on": []},
        ],
        "input": {}
    }
]

ROUTER_TESTS = [
    {
        "name": "Router - Billing Route",
        "stages": [
            {"id": "route", "type": "router", "input_mapping": {
                "value": "billing",
                "routes": {
                    "billing": ["billing_handler"],
                    "support": ["support_handler"],
                    "sales": ["sales_handler"]
                },
                "default_route": ["default_handler"]
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "Router - Support Route",
        "stages": [
            {"id": "route", "type": "router", "input_mapping": {
                "value": "support",
                "routes": {
                    "billing": ["billing_handler"],
                    "support": ["support_handler"],
                    "sales": ["sales_handler"]
                },
                "default_route": ["default_handler"]
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "Router - Default Route (unknown)",
        "stages": [
            {"id": "route", "type": "router", "input_mapping": {
                "value": "unknown_category",
                "routes": {
                    "billing": ["billing_handler"],
                    "support": ["support_handler"]
                },
                "default_route": ["default_handler"]
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "Router - Case Insensitive",
        "stages": [
            {"id": "route", "type": "router", "input_mapping": {
                "value": "BILLING",
                "routes": {"billing": ["handler"]},
                "case_insensitive": True
            }, "depends_on": []}
        ],
        "input": {}
    }
]

FOREACH_TESTS = [
    {
        "name": "ForEach - 5 Items",
        "stages": [
            {"id": "loop", "type": "foreach", "input_mapping": {
                "items": [1, 2, 3, 4, 5],
                "loop_stages": ["process"],
                "item_variable": "item"
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "ForEach - Empty Collection",
        "stages": [
            {"id": "loop", "type": "foreach", "input_mapping": {
                "items": [],
                "loop_stages": ["process"],
                "item_variable": "item"
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "ForEach - With Filter (active only)",
        "stages": [
            {"id": "loop", "type": "foreach", "input_mapping": {
                "items": [
                    {"id": 1, "active": True},
                    {"id": 2, "active": False},
                    {"id": 3, "active": True},
                    {"id": 4, "active": False},
                    {"id": 5, "active": True}
                ],
                "loop_stages": ["process"],
                "filter_expression": "item['active'] == True"
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "ForEach - 10 Items Parallel",
        "stages": [
            {"id": "loop", "type": "foreach", "input_mapping": {
                "items": list(range(10)),
                "loop_stages": ["process"],
                "parallel": True,
                "max_parallel": 3
            }, "depends_on": []}
        ],
        "input": {}
    }
]

TRYCATCH_TESTS = [
    {
        "name": "TryCatch - Basic Setup",
        "stages": [
            {"id": "tc", "type": "trycatch", "input_mapping": {
                "try_stages": ["risky_op"],
                "catch_stages": ["handle_error"],
                "finally_stages": ["cleanup"]
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "TryCatch - With Retries",
        "stages": [
            {"id": "tc", "type": "trycatch", "input_mapping": {
                "try_stages": ["api_call"],
                "catch_stages": ["fallback"],
                "max_retries": 3,
                "retry_delay_ms": 500
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "TryCatch - Propagate Error Scope",
        "stages": [
            {"id": "tc", "type": "trycatch", "input_mapping": {
                "try_stages": ["dangerous"],
                "catch_stages": ["recover"],
                "error_scope": "propagate"
            }, "depends_on": []}
        ],
        "input": {}
    }
]

SUBPIPELINE_TESTS = [
    {
        "name": "SubPipeline - Basic Call",
        "stages": [
            {"id": "sp", "type": "subpipeline", "input_mapping": {
                "pipeline_id": "validation-pipeline",
                "input_data": {"user_id": "123"}
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "SubPipeline - With Timeout",
        "stages": [
            {"id": "sp", "type": "subpipeline", "input_mapping": {
                "pipeline_id": "slow-pipeline",
                "input_data": {},
                "timeout_ms": 5000
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "SubPipeline - With Default Fallback",
        "stages": [
            {"id": "sp", "type": "subpipeline", "input_mapping": {
                "pipeline_id": "risky-pipeline",
                "on_error": "default",
                "default_result": {"fallback": True}
            }, "depends_on": []}
        ],
        "input": {}
    }
]

RETURN_TESTS = [
    {
        "name": "Return - Early Exit (condition true)",
        "stages": [
            {"id": "guard", "type": "return", "input_mapping": {
                "condition": True,
                "return_value": {"status": "early_exit"},
                "message": "Guard triggered"
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "Return - No Exit (condition false)",
        "stages": [
            {"id": "guard", "type": "return", "input_mapping": {
                "condition": False,
                "return_value": {"should": "not_return"}
            }, "depends_on": []}
        ],
        "input": {}
    }
]

OPERATOR_TESTS = [
    {
        "name": "Logger - Info Level",
        "stages": [
            {"id": "log", "type": "logger", "input_mapping": {
                "message": "Test log message",
                "level": "info",
                "data": {"key": "value"}
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "JSON Transform - Field Mapping",
        "stages": [
            {"id": "transform", "type": "json_transform", "input_mapping": {
                "data": {"user": {"name": "John", "email": "john@example.com"}},
                "mapping": {"username": "user.name", "contact": "user.email"}
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "Filter - Pass Condition",
        "stages": [
            {"id": "filter", "type": "filter", "input_mapping": {
                "data": {"score": 85},
                "condition": "data['score'] >= 80"
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "Filter - Fail Condition",
        "stages": [
            {"id": "filter", "type": "filter", "input_mapping": {
                "data": {"score": 65},
                "condition": "data['score'] >= 80"
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "Schema Validate - Valid Data",
        "stages": [
            {"id": "validate", "type": "schema_validate", "input_mapping": {
                "data": {"name": "John", "age": 30},
                "json_schema": {
                    "type": "object",
                    "required": ["name", "age"],
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}
                    }
                }
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "Schema Validate - Invalid Data (missing field)",
        "stages": [
            {"id": "validate", "type": "schema_validate", "input_mapping": {
                "data": {"name": "John"},
                "json_schema": {
                    "type": "object",
                    "required": ["name", "age"],
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}
                    }
                }
            }, "depends_on": []}
        ],
        "input": {}
    },
    {
        "name": "Variable Set - Basic",
        "stages": [
            {"id": "set_var", "type": "variable_set", "input_mapping": {
                "name": "result",
                "value": {"computed": True, "data": [1, 2, 3]}
            }, "depends_on": []}
        ],
        "input": {}
    }
]

COMPLEX_PIPELINE_TESTS = [
    {
        "name": "Complex - Parallel Execution",
        "stages": [
            {"id": "a", "type": "logger", "input_mapping": {"message": "Stage A", "level": "info"}, "depends_on": []},
            {"id": "b", "type": "logger", "input_mapping": {"message": "Stage B", "level": "info"}, "depends_on": []},
            {"id": "c", "type": "logger", "input_mapping": {"message": "Stage C", "level": "info"}, "depends_on": []},
            {"id": "merge", "type": "logger", "input_mapping": {"message": "Merge", "level": "info"}, "depends_on": ["a", "b", "c"]}
        ],
        "input": {}
    },
    {
        "name": "Complex - Sequential Chain",
        "stages": [
            {"id": "s1", "type": "json_transform", "input_mapping": {"data": {"x": 1}, "mapping": {"y": "x"}}, "depends_on": []},
            {"id": "s2", "type": "filter", "input_mapping": {"data": {"score": 90}, "condition": "data['score'] > 80"}, "depends_on": ["s1"]},
            {"id": "s3", "type": "logger", "input_mapping": {"message": "Done", "level": "info"}, "depends_on": ["s2"]}
        ],
        "input": {}
    },
    {
        "name": "Complex - Conditional with Branches",
        "stages": [
            {"id": "check", "type": "conditional", "input_mapping": {
                "condition": True,
                "true_branch_stages": ["process_a", "process_b"],
                "false_branch_stages": ["fallback"]
            }, "depends_on": []},
            {"id": "process_a", "type": "logger", "input_mapping": {"message": "Process A", "level": "info"}, "depends_on": ["check"]},
            {"id": "process_b", "type": "logger", "input_mapping": {"message": "Process B", "level": "info"}, "depends_on": ["process_a"]},
            {"id": "fallback", "type": "logger", "input_mapping": {"message": "Fallback", "level": "warning"}, "depends_on": ["check"]},
            {"id": "final", "type": "logger", "input_mapping": {"message": "Final", "level": "info"}, "depends_on": ["process_b", "fallback"]}
        ],
        "input": {}
    }
]


# =============================================================================
# Demo Runner
# =============================================================================

class DemoRunner:
    """Runs demo pipelines and collects statistics."""

    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
        self.stats = DemoStatistics()

    async def run_test(self, test_case: dict, pipeline_name: str) -> PipelineRunStats:
        """Run a single test case and collect statistics."""
        context = ExecutionContext(
            run_id=f"demo-{pipeline_name}-{int(time.time()*1000)}",
            pipeline_id=f"demo-{pipeline_name}",
            pipeline_version="1.0.0",
            pipeline_input=test_case.get("input", {})
        )

        stages = [ComponentConfig(**s) for s in test_case["stages"]]
        dag = DAGExecutor(self.registry, context)

        start_time = time.time()
        try:
            results = await dag.execute(stages, test_case.get("input", {}))
            duration_ms = (time.time() - start_time) * 1000

            # Collect stage stats
            stage_stats = []
            stages_executed = 0
            stages_skipped = 0
            control_flow_decisions = {}

            for stage_id, result in results.items():
                stage_config = next((s for s in test_case["stages"] if s["id"] == stage_id), {})

                if result.status == "success":
                    stages_executed += 1
                elif result.status == "skipped":
                    stages_skipped += 1

                stage_stat = StageStats(
                    stage_id=stage_id,
                    component_type=stage_config.get("type", "unknown"),
                    status=result.status,
                    duration_ms=getattr(result.usage, 'duration_ms', 0) if result.usage else 0,
                    output_keys=list(result.output.keys()) if isinstance(result.output, dict) else []
                )
                stage_stats.append(stage_stat)

                # Track control flow decisions
                if stage_config.get("type") == "conditional" and result.output:
                    control_flow_decisions["conditional"] = result.output.get("branch_taken")
                elif stage_config.get("type") == "router" and result.output:
                    control_flow_decisions["router"] = result.output.get("route_taken")
                elif stage_config.get("type") == "foreach" and result.output:
                    control_flow_decisions["foreach_items"] = result.output.get("total_items", 0)
                elif stage_config.get("type") == "return" and result.output:
                    control_flow_decisions["return"] = result.output.get("should_return")

            return PipelineRunStats(
                pipeline_name=pipeline_name,
                test_case=test_case["name"],
                status="success",
                total_duration_ms=duration_ms,
                stages_executed=stages_executed,
                stages_skipped=stages_skipped,
                stages_failed=0,
                stage_stats=stage_stats,
                control_flow_decisions=control_flow_decisions
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return PipelineRunStats(
                pipeline_name=pipeline_name,
                test_case=test_case["name"],
                status="failed",
                total_duration_ms=duration_ms,
                stages_executed=0,
                stages_skipped=0,
                stages_failed=len(test_case["stages"]),
                error=str(e)
            )

    async def run_all_demos(self):
        """Run all demo test cases."""
        all_tests = [
            ("Conditional", CONDITIONAL_TESTS),
            ("Router", ROUTER_TESTS),
            ("ForEach", FOREACH_TESTS),
            ("TryCatch", TRYCATCH_TESTS),
            ("SubPipeline", SUBPIPELINE_TESTS),
            ("Return", RETURN_TESTS),
            ("Operators", OPERATOR_TESTS),
            ("Complex Pipelines", COMPLEX_PIPELINE_TESTS),
        ]

        for pipeline_name, tests in all_tests:
            print(f"\n  Running {pipeline_name} tests...")
            for test in tests:
                run_stats = await self.run_test(test, pipeline_name)
                self.stats.add_run(run_stats)

                status_icon = "✓" if run_stats.status == "success" else "✗"
                print(f"    {status_icon} {test['name']} ({run_stats.total_duration_ms:.1f}ms)")

        return self.stats


def print_statistics(stats: DemoStatistics):
    """Print comprehensive statistics report."""
    print("\n" + "="*70)
    print("                    FLOWMASON DEMO EXECUTION REPORT")
    print("="*70)

    print(f"\n  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Summary
    print("\n" + "-"*70)
    print("  SUMMARY")
    print("-"*70)
    print(f"  Total Test Runs:        {stats.total_runs}")
    print(f"  Successful Runs:        {stats.successful_runs} ({100*stats.successful_runs/stats.total_runs:.1f}%)")
    print(f"  Failed Runs:            {stats.failed_runs}")
    print(f"  Total Execution Time:   {stats.total_execution_time_ms:.1f}ms")
    print(f"  Avg Time per Run:       {stats.total_execution_time_ms/stats.total_runs:.2f}ms")
    print(f"  Total Stages Executed:  {stats.total_stages_executed}")
    print(f"  Total Stages Skipped:   {stats.total_stages_skipped}")

    # Component Usage
    print("\n" + "-"*70)
    print("  COMPONENT USAGE")
    print("-"*70)
    sorted_components = sorted(stats.component_usage.items(), key=lambda x: x[1], reverse=True)
    for comp_type, count in sorted_components:
        bar = "█" * min(count, 30)
        print(f"  {comp_type:20} {count:3} {bar}")

    # Control Flow Statistics
    print("\n" + "-"*70)
    print("  CONTROL FLOW DECISIONS")
    print("-"*70)

    if "conditional" in stats.control_flow_stats:
        print("\n  Conditional Branches:")
        for branch, count in stats.control_flow_stats["conditional"].items():
            print(f"    {branch}: {count}")

    if "router" in stats.control_flow_stats:
        print("\n  Router Routes:")
        for route, count in stats.control_flow_stats["router"].items():
            print(f"    {route}: {count}")

    if "return" in stats.control_flow_stats:
        print("\n  Return Decisions:")
        for decision, count in stats.control_flow_stats["return"].items():
            print(f"    should_return={decision}: {count}")

    # Test Results by Pipeline
    print("\n" + "-"*70)
    print("  RESULTS BY PIPELINE TYPE")
    print("-"*70)

    pipeline_stats = defaultdict(lambda: {"success": 0, "failed": 0, "time": 0.0})
    for run in stats.pipeline_runs:
        ps = pipeline_stats[run.pipeline_name]
        ps["success" if run.status == "success" else "failed"] += 1
        ps["time"] += run.total_duration_ms

    for pipeline, ps in sorted(pipeline_stats.items()):
        total = ps["success"] + ps["failed"]
        pct = 100 * ps["success"] / total if total > 0 else 0
        print(f"  {pipeline:20} {ps['success']}/{total} passed ({pct:.0f}%)  {ps['time']:.1f}ms")

    # Failures (if any)
    failures = [r for r in stats.pipeline_runs if r.status == "failed"]
    if failures:
        print("\n" + "-"*70)
        print("  FAILURES")
        print("-"*70)
        for f in failures:
            print(f"  ✗ {f.test_case}")
            print(f"    Error: {f.error[:80]}..." if len(str(f.error)) > 80 else f"    Error: {f.error}")

    print("\n" + "="*70)
    print("                         END OF REPORT")
    print("="*70 + "\n")


async def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("           FLOWMASON DEMO RUNNER WITH STATISTICS")
    print("="*70)

    # Setup
    with tempfile.TemporaryDirectory() as tmp_dir:
        pkg_dir = Path(tmp_dir) / "packages"
        pkg_dir.mkdir()

        print("\n  Setting up registry...")
        registry = setup_registry(pkg_dir)
        print(f"  Loaded {len(registry.list_components())} components")

        # Run demos
        runner = DemoRunner(registry)
        stats = await runner.run_all_demos()

        # Print report
        print_statistics(stats)

        # Export to JSON
        export_path = Path(__file__).parent / "demo_stats.json"
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_runs": stats.total_runs,
                "successful_runs": stats.successful_runs,
                "failed_runs": stats.failed_runs,
                "success_rate": stats.successful_runs / stats.total_runs if stats.total_runs > 0 else 0,
                "total_execution_time_ms": stats.total_execution_time_ms,
                "avg_time_per_run_ms": stats.total_execution_time_ms / stats.total_runs if stats.total_runs > 0 else 0,
                "total_stages_executed": stats.total_stages_executed,
                "total_stages_skipped": stats.total_stages_skipped,
            },
            "component_usage": dict(stats.component_usage),
            "control_flow_stats": {k: dict(v) for k, v in stats.control_flow_stats.items()},
            "pipeline_runs": [
                {
                    "pipeline_name": r.pipeline_name,
                    "test_case": r.test_case,
                    "status": r.status,
                    "duration_ms": r.total_duration_ms,
                    "stages_executed": r.stages_executed,
                    "control_flow_decisions": r.control_flow_decisions,
                    "error": r.error
                }
                for r in stats.pipeline_runs
            ]
        }

        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2)
        print(f"\n  Statistics exported to: {export_path}")

        return stats


if __name__ == "__main__":
    asyncio.run(main())
