"""
FlowMason Benchmark Pipelines

Complex pipelines designed for performance benchmarking:
1. Parallel Scaling - Test parallel execution with varying concurrency
2. Deep Sequential - Test long chains of sequential operations
3. Nested Control Flow - Test deeply nested conditionals and loops
4. Large Data Processing - Test ForEach with large collections
5. Mixed Workload - Combine all patterns
6. Branch Explosion - Test router with many branches
7. Error Recovery Stress - Test TryCatch under load
"""

import asyncio
import time
import json
import statistics
import sys
import os
import tempfile
import shutil
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "lab"))
sys.path.insert(0, str(Path(__file__).parent.parent / "studio"))

from flowmason_core.execution import DAGExecutor
from flowmason_core.config.types import PipelineConfig, ComponentConfig
from flowmason_core.config import ExecutionContext
from flowmason_core.registry import ComponentRegistry


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    stages_per_run: int
    throughput_ops_sec: float
    memory_estimate_kb: float = 0


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results."""
    results: List[BenchmarkResult] = field(default_factory=list)
    total_time_sec: float = 0

    def add(self, result: BenchmarkResult):
        self.results.append(result)

    def to_dict(self) -> dict:
        return {
            "total_time_sec": self.total_time_sec,
            "benchmarks": [
                {
                    "name": r.name,
                    "iterations": r.iterations,
                    "total_time_ms": round(r.total_time_ms, 3),
                    "avg_time_ms": round(r.avg_time_ms, 3),
                    "min_time_ms": round(r.min_time_ms, 3),
                    "max_time_ms": round(r.max_time_ms, 3),
                    "std_dev_ms": round(r.std_dev_ms, 3),
                    "stages_per_run": r.stages_per_run,
                    "throughput_ops_sec": round(r.throughput_ops_sec, 2),
                }
                for r in self.results
            ]
        }


def create_test_package(output_dir: Path, name: str, source: str, comp_type: str = "operator") -> Path:
    """Create a test .fmpkg package."""
    import zipfile
    pkg_path = output_dir / f"{name}-1.0.0.fmpkg"
    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": f"Benchmark package: {name}",
        "type": comp_type,
        "author": {"name": "Benchmark", "email": "bench@test.com"},
        "license": "MIT",
        "category": "benchmark",
        "entry_point": "index.py",
        "requires_llm": False,
        "dependencies": []
    }
    with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("flowmason-package.json", json.dumps(manifest, indent=2))
        zf.writestr("index.py", source)
    return pkg_path


def create_packages() -> tuple[str, ComponentRegistry]:
    """Create component packages from lab sources and return registry."""
    temp_dir = tempfile.mkdtemp(prefix="flowmason_bench_")
    pkg_dir = Path(temp_dir)
    lab_dir = Path(__file__).parent.parent / "lab" / "flowmason_lab"

    # Component sources mapping
    components = {
        # Core operators
        "logger": (lab_dir / "operators" / "core" / "logger.py", "operator"),
        "json_transform": (lab_dir / "operators" / "core" / "json_transform.py", "operator"),
        "filter": (lab_dir / "operators" / "core" / "filter.py", "operator"),
        "schema_validate": (lab_dir / "operators" / "core" / "schema_validate.py", "operator"),
        "variable_set": (lab_dir / "operators" / "core" / "variable_set.py", "operator"),
        # Control flow
        "conditional": (lab_dir / "operators" / "control_flow" / "conditional.py", "control_flow"),
        "router": (lab_dir / "operators" / "control_flow" / "router.py", "control_flow"),
        "foreach": (lab_dir / "operators" / "control_flow" / "foreach.py", "control_flow"),
        "trycatch": (lab_dir / "operators" / "control_flow" / "trycatch.py", "control_flow"),
        "subpipeline": (lab_dir / "operators" / "control_flow" / "subpipeline.py", "control_flow"),
        "return": (lab_dir / "operators" / "control_flow" / "return_early.py", "control_flow"),
    }

    for name, (source_path, comp_type) in components.items():
        if source_path.exists():
            source = source_path.read_text()
            create_test_package(pkg_dir, name, source, comp_type)

    # Create registry with auto_scan
    registry = ComponentRegistry(pkg_dir, auto_scan=True)
    return temp_dir, registry


class BenchmarkRunner:
    """Runs benchmark pipelines and collects metrics."""

    def __init__(self, registry: ComponentRegistry, iterations: int = 10):
        self.registry = registry
        self.iterations = iterations
        self.suite = BenchmarkSuite()

    async def run_benchmark(
        self,
        name: str,
        pipeline: PipelineConfig,
        inputs: Dict[str, Any],
        iterations: Optional[int] = None
    ) -> BenchmarkResult:
        """Run a benchmark multiple times and collect statistics."""
        iters = iterations or self.iterations
        times = []

        for i in range(iters):
            # Create fresh context for each run
            context = ExecutionContext(
                run_id=f"bench-{name}-{i}",
                pipeline_id=pipeline.id,
                pipeline_version=pipeline.version,
                pipeline_input=inputs
            )
            executor = DAGExecutor(self.registry, context)

            start = time.perf_counter()
            await executor.execute(pipeline.stages, inputs)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        total_time = sum(times)
        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0

        result = BenchmarkResult(
            name=name,
            iterations=iters,
            total_time_ms=total_time,
            avg_time_ms=avg_time,
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=std_dev,
            stages_per_run=len(pipeline.stages),
            throughput_ops_sec=(iters / total_time) * 1000 if total_time > 0 else 0
        )

        self.suite.add(result)
        return result

    # =========================================================================
    # BENCHMARK 1: Parallel Scaling
    # =========================================================================

    def create_parallel_pipeline(self, width: int) -> PipelineConfig:
        """Create pipeline with N parallel logger stages."""
        stages = [
            ComponentConfig(
                id="start",
                type="logger",
                input_mapping={"message": "Starting parallel benchmark", "level": "info"}
            )
        ]

        # Add N parallel stages
        for i in range(width):
            stages.append(ComponentConfig(
                id=f"parallel_{i}",
                type="logger",
                input_mapping={
                    "message": f"Parallel worker {i}",
                    "level": "debug"
                },
                depends_on=["start"]
            ))

        # Final aggregation
        stages.append(ComponentConfig(
            id="end",
            type="logger",
            input_mapping={"message": "Parallel complete", "level": "info"},
            depends_on=[f"parallel_{i}" for i in range(width)]
        ))

        return PipelineConfig(
            id=f"parallel-{width}",
            name=f"parallel_{width}",
            stages=stages
        )

    async def benchmark_parallel_scaling(self):
        """Test parallel execution with increasing width."""
        print("\n  Benchmark: Parallel Scaling")

        for width in [5, 10, 25, 50, 100]:
            pipeline = self.create_parallel_pipeline(width)
            result = await self.run_benchmark(
                f"Parallel-{width}",
                pipeline,
                {},
                iterations=5
            )
            print(f"    Width={width:3d}: {result.avg_time_ms:7.2f}ms avg, "
                  f"{result.throughput_ops_sec:7.1f} ops/sec")

    # =========================================================================
    # BENCHMARK 2: Deep Sequential Chain
    # =========================================================================

    def create_sequential_pipeline(self, depth: int) -> PipelineConfig:
        """Create pipeline with N sequential stages."""
        stages = []

        for i in range(depth):
            stage = ComponentConfig(
                id=f"stage_{i}",
                type="json_transform",
                input_mapping={
                    "data": f"{{{{upstream.stage_{i-1}.result}}}}" if i > 0 else {"count": 0},
                    "mapping": {"count": "data.count + 1"}
                },
                depends_on=[f"stage_{i-1}"] if i > 0 else []
            )
            stages.append(stage)

        return PipelineConfig(
            id=f"sequential-{depth}",
            name=f"sequential_{depth}",
            stages=stages
        )

    async def benchmark_sequential_depth(self):
        """Test sequential execution with increasing depth."""
        print("\n  Benchmark: Sequential Depth")

        for depth in [10, 25, 50, 100, 200]:
            pipeline = self.create_sequential_pipeline(depth)
            result = await self.run_benchmark(
                f"Sequential-{depth}",
                pipeline,
                {},
                iterations=5
            )
            print(f"    Depth={depth:3d}: {result.avg_time_ms:7.2f}ms avg, "
                  f"{result.stages_per_run/result.avg_time_ms*1000:.0f} stages/sec")

    # =========================================================================
    # BENCHMARK 3: Nested Control Flow
    # =========================================================================

    def create_nested_conditional_pipeline(self, depth: int) -> PipelineConfig:
        """Create pipeline with nested conditionals."""
        stages = []

        # Create nested conditionals with direct values
        for i in range(depth):
            stages.append(ComponentConfig(
                id=f"cond_{i}",
                type="conditional",
                input_mapping={
                    "condition": True,  # Always true for benchmark
                    "true_value": f"branch_true_{i}",
                    "false_value": f"branch_false_{i}"
                },
                depends_on=[f"cond_{i-1}"] if i > 0 else []
            ))

        # Final logger
        stages.append(ComponentConfig(
            id="result",
            type="logger",
            input_mapping={
                "message": f"Nested depth {depth} complete",
                "level": "info"
            },
            depends_on=[f"cond_{depth-1}"]
        ))

        return PipelineConfig(
            id=f"nested-cond-{depth}",
            name=f"nested_cond_{depth}",
            stages=stages
        )

    async def benchmark_nested_control_flow(self):
        """Test nested control flow structures."""
        print("\n  Benchmark: Nested Control Flow")

        for depth in [5, 10, 20, 30, 50]:
            pipeline = self.create_nested_conditional_pipeline(depth)
            result = await self.run_benchmark(
                f"NestedCond-{depth}",
                pipeline,
                {},
                iterations=5
            )
            print(f"    Depth={depth:2d}: {result.avg_time_ms:7.2f}ms avg")

    # =========================================================================
    # BENCHMARK 4: Large Data Processing (ForEach)
    # =========================================================================

    def create_foreach_pipeline(self, item_count: int) -> PipelineConfig:
        """Create pipeline with foreach component (tests directive handling)."""
        stages = [
            ComponentConfig(
                id="foreach",
                type="foreach",
                input_mapping={
                    "items": [{"id": i, "value": i * 10} for i in range(item_count)],
                    "item_variable": "item",
                    "loop_stages": []  # Empty - just benchmark directive overhead
                }
            ),
            ComponentConfig(
                id="complete",
                type="logger",
                input_mapping={
                    "message": f"ForEach with {item_count} items complete",
                    "level": "info"
                },
                depends_on=["foreach"]
            )
        ]

        return PipelineConfig(
            id=f"foreach-{item_count}",
            name=f"foreach_{item_count}",
            stages=stages
        )

    async def benchmark_foreach_scaling(self):
        """Test ForEach with increasing collection sizes."""
        print("\n  Benchmark: ForEach Scaling")

        for count in [10, 50, 100, 250, 500]:
            pipeline = self.create_foreach_pipeline(count)
            result = await self.run_benchmark(
                f"ForEach-{count}",
                pipeline,
                {},
                iterations=5
            )
            print(f"    Items={count:3d}: {result.avg_time_ms:7.2f}ms avg, "
                  f"{count/result.avg_time_ms*1000:.0f} items/sec")

    # =========================================================================
    # BENCHMARK 5: Wide Parallel with Conditionals
    # =========================================================================

    def create_wide_conditional_pipeline(self, width: int) -> PipelineConfig:
        """Create pipeline with N parallel conditional branches."""
        stages = []

        # Create N parallel conditionals
        for i in range(width):
            stages.append(ComponentConfig(
                id=f"cond_{i}",
                type="conditional",
                input_mapping={
                    "condition": i % 3 == 0,  # Mix of true/false
                    "true_value": f"branch_a_{i}",
                    "false_value": f"branch_b_{i}"
                },
                depends_on=[]
            ))

        # Final aggregation
        stages.append(ComponentConfig(
            id="aggregator",
            type="logger",
            input_mapping={"message": "Wide conditional complete", "level": "info"},
            depends_on=[f"cond_{i}" for i in range(width)]
        ))

        return PipelineConfig(
            id=f"wide-cond-{width}",
            name=f"wide_cond_{width}",
            stages=stages
        )

    async def benchmark_wide_conditionals(self):
        """Test wide parallel conditionals."""
        print("\n  Benchmark: Wide Parallel Conditionals")

        for width in [10, 25, 50, 100, 200]:
            pipeline = self.create_wide_conditional_pipeline(width)
            result = await self.run_benchmark(
                f"WideCond-{width}",
                pipeline,
                {},
                iterations=5
            )
            print(f"    Width={width:3d}: {result.avg_time_ms:7.2f}ms avg, "
                  f"{width/result.avg_time_ms*1000:.0f} cond/sec")

    # =========================================================================
    # BENCHMARK 6: Mixed Workload
    # =========================================================================

    def create_mixed_workload_pipeline(self, complexity: int) -> PipelineConfig:
        """Create pipeline combining sequential + parallel patterns."""
        stages = []

        # Start with a sequential chain of transforms
        for i in range(3):
            stages.append(ComponentConfig(
                id=f"seq_{i}",
                type="json_transform",
                input_mapping={
                    "data": {"step": i},
                    "mapping": {"result": f"step_{i}"}
                },
                depends_on=[f"seq_{i-1}"] if i > 0 else []
            ))

        # Then fan out to N parallel conditionals
        for i in range(complexity):
            stages.append(ComponentConfig(
                id=f"cond_{i}",
                type="conditional",
                input_mapping={
                    "condition": i % 2 == 0,
                    "true_value": f"even_{i}",
                    "false_value": f"odd_{i}"
                },
                depends_on=["seq_2"]  # All depend on last sequential
            ))

        # Final aggregation logger
        stages.append(ComponentConfig(
            id="aggregator",
            type="logger",
            input_mapping={"message": "Mixed workload complete", "level": "info"},
            depends_on=[f"cond_{i}" for i in range(complexity)]
        ))

        return PipelineConfig(
            id=f"mixed-{complexity}",
            name=f"mixed_{complexity}",
            stages=stages
        )

    async def benchmark_mixed_workload(self):
        """Test mixed workload pipelines."""
        print("\n  Benchmark: Mixed Workload")

        for complexity in [10, 25, 50, 100]:
            pipeline = self.create_mixed_workload_pipeline(complexity)
            result = await self.run_benchmark(
                f"Mixed-{complexity}",
                pipeline,
                {},
                iterations=5
            )
            print(f"    Complexity={complexity:3d}: {result.avg_time_ms:7.2f}ms avg, "
                  f"{complexity/result.avg_time_ms*1000:.0f} branches/sec")

    # =========================================================================
    # BENCHMARK 7: Deep JSON Transform Chain
    # =========================================================================

    def create_transform_chain_pipeline(self, depth: int) -> PipelineConfig:
        """Create pipeline with chained JSON transforms."""
        stages = []

        for i in range(depth):
            stages.append(ComponentConfig(
                id=f"transform_{i}",
                type="json_transform",
                input_mapping={
                    "data": {"step": i, "value": i * 2},
                    "mapping": {"next_step": f"step_{i+1}"}
                },
                depends_on=[f"transform_{i-1}"] if i > 0 else []
            ))

        # Final logger
        stages.append(ComponentConfig(
            id="complete",
            type="logger",
            input_mapping={"message": f"Transform chain {depth} complete", "level": "info"},
            depends_on=[f"transform_{depth-1}"]
        ))

        return PipelineConfig(
            id=f"transform-chain-{depth}",
            name=f"transform_chain_{depth}",
            stages=stages
        )

    async def benchmark_transform_chain(self):
        """Test deep JSON transform chain."""
        print("\n  Benchmark: Transform Chain")

        for depth in [10, 25, 50, 100, 200]:
            pipeline = self.create_transform_chain_pipeline(depth)
            result = await self.run_benchmark(
                f"Transform-{depth}",
                pipeline,
                {},
                iterations=5
            )
            print(f"    Depth={depth:3d}: {result.avg_time_ms:7.2f}ms avg, "
                  f"{depth/result.avg_time_ms*1000:.0f} transforms/sec")

    # =========================================================================
    # Run All Benchmarks
    # =========================================================================

    async def run_all(self):
        """Run all benchmark suites."""
        start_time = time.perf_counter()

        await self.benchmark_parallel_scaling()
        await self.benchmark_sequential_depth()
        await self.benchmark_nested_control_flow()
        await self.benchmark_foreach_scaling()
        await self.benchmark_wide_conditionals()
        await self.benchmark_mixed_workload()
        await self.benchmark_transform_chain()

        self.suite.total_time_sec = time.perf_counter() - start_time
        return self.suite


def print_summary(suite: BenchmarkSuite):
    """Print benchmark summary."""
    print("\n" + "=" * 70)
    print("                    BENCHMARK SUMMARY")
    print("=" * 70)

    print(f"\n  Total Benchmarks: {len(suite.results)}")
    print(f"  Total Time: {suite.total_time_sec:.2f}s")

    # Group by category
    categories = {}
    for r in suite.results:
        cat = r.name.split("-")[0]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    print("\n  Performance by Category:")
    print("-" * 70)

    for cat, results in sorted(categories.items()):
        avg_time = statistics.mean([r.avg_time_ms for r in results])
        avg_throughput = statistics.mean([r.throughput_ops_sec for r in results])
        print(f"  {cat:20s}: {avg_time:8.2f}ms avg, {avg_throughput:8.1f} ops/sec")

    # Find best/worst
    sorted_by_time = sorted(suite.results, key=lambda r: r.avg_time_ms)

    print("\n  Fastest Benchmarks:")
    for r in sorted_by_time[:5]:
        print(f"    {r.name:30s}: {r.avg_time_ms:.2f}ms")

    print("\n  Slowest Benchmarks:")
    for r in sorted_by_time[-5:]:
        print(f"    {r.name:30s}: {r.avg_time_ms:.2f}ms")

    print("\n" + "=" * 70)


async def main():
    print("=" * 70)
    print("           FLOWMASON BENCHMARK SUITE")
    print("=" * 70)

    # Setup
    print("\n  Setting up registry...")
    temp_dir, registry = create_packages()
    component_count = len(list(registry.list_packages()))
    print(f"  Loaded {component_count} components")

    try:
        # Run benchmarks
        runner = BenchmarkRunner(registry, iterations=10)
        suite = await runner.run_all()

        # Print summary
        print_summary(suite)

        # Export results
        output_path = Path(__file__).parent / "benchmark_results.json"
        with open(output_path, "w") as f:
            json.dump(suite.to_dict(), f, indent=2)
        print(f"\n  Results exported to: {output_path}")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
