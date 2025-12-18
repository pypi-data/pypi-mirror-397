"""
Saved Demo Pipelines for FlowMason.

These pipelines demonstrate various FlowMason capabilities and can be used for:
- Demos and presentations
- Testing and benchmarking
- Learning FlowMason patterns

Each pipeline is exported as a PipelineConfig that can be executed directly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from flowmason_core.config.types import PipelineConfig, ComponentConfig


# =============================================================================
# PIPELINE 1: Parallel Processing Demo
# =============================================================================
# Demonstrates parallel execution with fan-out and fan-in pattern

def create_parallel_processing_pipeline(worker_count: int = 5) -> PipelineConfig:
    """
    Pipeline that fans out to N parallel workers then aggregates results.

    Pattern: Start -> [Worker_1, Worker_2, ..., Worker_N] -> Aggregate

    Use case: Processing multiple independent tasks simultaneously
    """
    stages = [
        ComponentConfig(
            id="start",
            type="logger",
            input_mapping={
                "message": f"Starting parallel processing with {worker_count} workers",
                "level": "info"
            }
        )
    ]

    # Add parallel workers
    for i in range(worker_count):
        stages.append(ComponentConfig(
            id=f"worker_{i}",
            type="json_transform",
            input_mapping={
                "data": {"worker_id": i, "task": f"task_{i}"},
                "defaults": {"result": f"processed_by_worker_{i}"}
            },
            depends_on=["start"]
        ))

    # Aggregation stage
    stages.append(ComponentConfig(
        id="aggregate",
        type="logger",
        input_mapping={
            "message": f"All {worker_count} workers completed",
            "level": "info"
        },
        depends_on=[f"worker_{i}" for i in range(worker_count)]
    ))

    return PipelineConfig(
        id="parallel-processing-demo",
        name="Parallel Processing Demo",
        description=f"Demonstrates parallel execution with {worker_count} workers",
        version="1.0.0",
        stages=stages,
        tags=["demo", "parallel", "fan-out", "fan-in"],
        category="demo"
    )


# =============================================================================
# PIPELINE 2: Sequential Data Processing Chain
# =============================================================================
# Demonstrates sequential processing with data transformation

def create_data_processing_pipeline(steps: int = 5) -> PipelineConfig:
    """
    Pipeline that processes data through a series of transformations.

    Pattern: Transform_1 -> Transform_2 -> ... -> Transform_N -> Log Result

    Use case: ETL pipelines, data enrichment workflows
    """
    stages = []

    for i in range(steps):
        stages.append(ComponentConfig(
            id=f"transform_{i}",
            type="json_transform",
            input_mapping={
                "data": {"step": i, "value": i * 10, "timestamp": f"2024-01-0{i+1}"},
                "mapping": {
                    "step": "data.step",
                    "original_value": "data.value",
                    "timestamp": "data.timestamp"
                },
                "defaults": {
                    "stage": f"stage_{i}",
                    "processed": True
                }
            },
            depends_on=[f"transform_{i-1}"] if i > 0 else []
        ))

    # Final logging
    stages.append(ComponentConfig(
        id="log_result",
        type="logger",
        input_mapping={
            "message": f"Data processing complete after {steps} transformations",
            "level": "info"
        },
        depends_on=[f"transform_{steps-1}"]
    ))

    return PipelineConfig(
        id="data-processing-chain",
        name="Data Processing Chain",
        description=f"Sequential data processing with {steps} transformation steps",
        version="1.0.0",
        stages=stages,
        tags=["demo", "sequential", "etl", "transformation"],
        category="demo"
    )


# =============================================================================
# PIPELINE 3: Conditional Branching Demo
# =============================================================================
# Demonstrates conditional logic with true/false branches

def create_conditional_branching_pipeline() -> PipelineConfig:
    """
    Pipeline demonstrating conditional branching logic.

    Pattern: Check Condition -> (True Branch | False Branch) -> Merge

    Use case: Decision-based workflows, A/B processing
    """
    stages = [
        # Input validation - pass through data with extracted fields
        ComponentConfig(
            id="validate_input",
            type="json_transform",
            input_mapping={
                "data": {"score": 85, "threshold": 70},
                "mapping": {
                    "score": "data.score",
                    "threshold": "data.threshold"
                }
            }
        ),

        # Conditional check
        ComponentConfig(
            id="check_score",
            type="conditional",
            input_mapping={
                "condition": True,  # In real use: "{{upstream.validate_input.is_passing}}"
                "true_value": "passed",
                "false_value": "failed"
            },
            depends_on=["validate_input"]
        ),

        # True branch - passing score
        ComponentConfig(
            id="process_passing",
            type="logger",
            input_mapping={
                "message": "Score passed threshold - processing success path",
                "level": "info"
            },
            depends_on=["check_score"]
        ),

        # False branch - failing score
        ComponentConfig(
            id="process_failing",
            type="logger",
            input_mapping={
                "message": "Score below threshold - processing remediation path",
                "level": "warning"
            },
            depends_on=["check_score"]
        ),

        # Merge point
        ComponentConfig(
            id="finalize",
            type="logger",
            input_mapping={
                "message": "Conditional processing complete",
                "level": "info"
            },
            depends_on=["process_passing", "process_failing"]
        )
    ]

    return PipelineConfig(
        id="conditional-branching-demo",
        name="Conditional Branching Demo",
        description="Demonstrates conditional logic with branching paths",
        version="1.0.0",
        stages=stages,
        tags=["demo", "conditional", "branching", "decision"],
        category="demo"
    )


# =============================================================================
# PIPELINE 4: Nested Conditionals Demo
# =============================================================================
# Demonstrates deeply nested conditional logic

def create_nested_conditionals_pipeline(depth: int = 5) -> PipelineConfig:
    """
    Pipeline with nested conditional checks.

    Pattern: Cond_1 -> Cond_2 -> ... -> Cond_N -> Result

    Use case: Multi-level decision trees, complex business rules
    """
    stages = []

    for i in range(depth):
        stages.append(ComponentConfig(
            id=f"condition_{i}",
            type="conditional",
            input_mapping={
                "condition": i % 2 == 0,  # Alternates true/false
                "true_value": f"level_{i}_passed",
                "false_value": f"level_{i}_failed"
            },
            depends_on=[f"condition_{i-1}"] if i > 0 else []
        ))

    # Final result
    stages.append(ComponentConfig(
        id="final_result",
        type="logger",
        input_mapping={
            "message": f"Completed {depth} levels of conditional checks",
            "level": "info"
        },
        depends_on=[f"condition_{depth-1}"]
    ))

    return PipelineConfig(
        id="nested-conditionals-demo",
        name="Nested Conditionals Demo",
        description=f"Demonstrates {depth} levels of nested conditional logic",
        version="1.0.0",
        stages=stages,
        tags=["demo", "conditional", "nested", "decision-tree"],
        category="demo"
    )


# =============================================================================
# PIPELINE 5: ForEach Collection Processing
# =============================================================================
# Demonstrates iteration over collections

def create_foreach_pipeline(item_count: int = 10) -> PipelineConfig:
    """
    Pipeline that iterates over a collection of items.

    Pattern: ForEach(items) -> Process Each -> Collect Results

    Use case: Batch processing, list operations
    """
    items = [{"id": i, "name": f"item_{i}", "value": i * 100} for i in range(item_count)]

    stages = [
        ComponentConfig(
            id="foreach_items",
            type="foreach",
            input_mapping={
                "items": items,
                "item_variable": "current_item",
                "loop_stages": []  # Empty for demo - in real use would include processing stages
            }
        ),
        ComponentConfig(
            id="collection_complete",
            type="logger",
            input_mapping={
                "message": f"ForEach processed {item_count} items",
                "level": "info"
            },
            depends_on=["foreach_items"]
        )
    ]

    return PipelineConfig(
        id="foreach-collection-demo",
        name="ForEach Collection Demo",
        description=f"Demonstrates iteration over {item_count} items",
        version="1.0.0",
        stages=stages,
        tags=["demo", "foreach", "iteration", "collection"],
        category="demo"
    )


# =============================================================================
# PIPELINE 6: Mixed Workload Pipeline
# =============================================================================
# Combines sequential and parallel patterns

def create_mixed_workload_pipeline(parallel_branches: int = 10) -> PipelineConfig:
    """
    Pipeline combining sequential preprocessing with parallel processing.

    Pattern: Preprocess_1 -> Preprocess_2 -> [Branch_1, Branch_2, ...] -> Aggregate

    Use case: Real-world workflows with setup, parallel work, and aggregation
    """
    stages = []

    # Sequential preprocessing
    for i in range(3):
        stages.append(ComponentConfig(
            id=f"preprocess_{i}",
            type="json_transform",
            input_mapping={
                "data": {"stage": f"preprocess_{i}"},
                "mapping": {"stage_name": "data.stage"},
                "defaults": {"status": "preprocessed"}
            },
            depends_on=[f"preprocess_{i-1}"] if i > 0 else []
        ))

    # Parallel branches
    for i in range(parallel_branches):
        stages.append(ComponentConfig(
            id=f"branch_{i}",
            type="conditional",
            input_mapping={
                "condition": i % 2 == 0,
                "true_value": f"even_branch_{i}",
                "false_value": f"odd_branch_{i}"
            },
            depends_on=["preprocess_2"]
        ))

    # Aggregation
    stages.append(ComponentConfig(
        id="aggregate_results",
        type="logger",
        input_mapping={
            "message": f"Mixed workload complete: 3 sequential + {parallel_branches} parallel",
            "level": "info"
        },
        depends_on=[f"branch_{i}" for i in range(parallel_branches)]
    ))

    return PipelineConfig(
        id="mixed-workload-demo",
        name="Mixed Workload Demo",
        description=f"Sequential preprocessing followed by {parallel_branches} parallel branches",
        version="1.0.0",
        stages=stages,
        tags=["demo", "mixed", "sequential", "parallel"],
        category="demo"
    )


# =============================================================================
# PIPELINE 7: Data Validation Pipeline
# =============================================================================
# Demonstrates schema validation workflow

def create_validation_pipeline() -> PipelineConfig:
    """
    Pipeline demonstrating data validation patterns.

    Pattern: Input -> Validate Schema -> (Valid: Process | Invalid: Log Error)

    Use case: API input validation, data quality checks
    """
    stages = [
        # Initial data
        ComponentConfig(
            id="prepare_data",
            type="json_transform",
            input_mapping={
                "data": {
                    "user_id": 123,
                    "email": "user@example.com",
                    "age": 25
                },
                "mapping": {
                    "user_id": "data.user_id",
                    "email": "data.email",
                    "age": "data.age"
                }
            }
        ),

        # Schema validation
        ComponentConfig(
            id="validate_schema",
            type="schema_validate",
            input_mapping={
                "data": {
                    "user_id": 123,
                    "email": "user@example.com",
                    "age": 25
                },
                "json_schema": {
                    "type": "object",
                    "required": ["user_id", "email"],
                    "properties": {
                        "user_id": {"type": "integer"},
                        "email": {"type": "string", "format": "email"},
                        "age": {"type": "integer", "minimum": 0}
                    }
                }
            },
            depends_on=["prepare_data"]
        ),

        # Log validation result
        ComponentConfig(
            id="log_result",
            type="logger",
            input_mapping={
                "message": "Data validation completed",
                "level": "info"
            },
            depends_on=["validate_schema"]
        )
    ]

    return PipelineConfig(
        id="data-validation-demo",
        name="Data Validation Demo",
        description="Demonstrates schema validation workflow",
        version="1.0.0",
        stages=stages,
        tags=["demo", "validation", "schema", "data-quality"],
        category="demo"
    )


# =============================================================================
# PIPELINE 8: Filter and Transform Pipeline
# =============================================================================
# Demonstrates filtering with transformations

def create_filter_transform_pipeline() -> PipelineConfig:
    """
    Pipeline demonstrating filter and transform operations.

    Pattern: Input -> Filter -> Transform -> Output

    Use case: Data pipelines with conditional processing
    """
    stages = [
        # Initial filter
        ComponentConfig(
            id="filter_active",
            type="filter",
            input_mapping={
                "data": {"status": "active", "priority": 5},
                "condition": "data.status == 'active' and data.priority > 3"
            }
        ),

        # Transform filtered data - use defaults for literal values
        ComponentConfig(
            id="transform_data",
            type="json_transform",
            input_mapping={
                "data": {"status": "active", "priority": 5},
                "defaults": {
                    "processed": True,
                    "priority_level": "high"
                }
            },
            depends_on=["filter_active"]
        ),

        # Second filter
        ComponentConfig(
            id="filter_high_priority",
            type="filter",
            input_mapping={
                "data": {"processed": True, "priority_level": "high"},
                "condition": "data.priority_level == 'high'"
            },
            depends_on=["transform_data"]
        ),

        # Final output
        ComponentConfig(
            id="output_result",
            type="logger",
            input_mapping={
                "message": "Filter and transform pipeline complete",
                "level": "info"
            },
            depends_on=["filter_high_priority"]
        )
    ]

    return PipelineConfig(
        id="filter-transform-demo",
        name="Filter and Transform Demo",
        description="Demonstrates filtering and transformation patterns",
        version="1.0.0",
        stages=stages,
        tags=["demo", "filter", "transform", "data-pipeline"],
        category="demo"
    )


# =============================================================================
# BENCHMARK PIPELINES (exact pipelines used in benchmark suite)
# =============================================================================

def create_benchmark_parallel_pipeline(width: int) -> PipelineConfig:
    """
    BENCHMARK: Parallel Scaling
    Tests fan-out/fan-in with N parallel logger stages.
    """
    stages = [
        ComponentConfig(
            id="start",
            type="logger",
            input_mapping={"message": "Starting parallel benchmark", "level": "info"}
        )
    ]

    for i in range(width):
        stages.append(ComponentConfig(
            id=f"parallel_{i}",
            type="logger",
            input_mapping={"message": f"Parallel worker {i}", "level": "debug"},
            depends_on=["start"]
        ))

    stages.append(ComponentConfig(
        id="end",
        type="logger",
        input_mapping={"message": "Parallel complete", "level": "info"},
        depends_on=[f"parallel_{i}" for i in range(width)]
    ))

    return PipelineConfig(
        id=f"benchmark-parallel-{width}",
        name=f"Benchmark: Parallel {width}",
        description=f"Benchmark pipeline with {width} parallel stages",
        version="1.0.0",
        stages=stages,
        tags=["benchmark", "parallel"],
        category="benchmark"
    )


def create_benchmark_sequential_pipeline(depth: int) -> PipelineConfig:
    """
    BENCHMARK: Sequential Depth
    Tests long chains of sequential json_transform stages.
    """
    stages = []

    for i in range(depth):
        stages.append(ComponentConfig(
            id=f"stage_{i}",
            type="json_transform",
            input_mapping={
                "data": {"count": i, "step": i},
                "mapping": {"original_count": "data.count", "step": "data.step"}
            },
            depends_on=[f"stage_{i-1}"] if i > 0 else []
        ))

    return PipelineConfig(
        id=f"benchmark-sequential-{depth}",
        name=f"Benchmark: Sequential {depth}",
        description=f"Benchmark pipeline with {depth} sequential stages",
        version="1.0.0",
        stages=stages,
        tags=["benchmark", "sequential"],
        category="benchmark"
    )


def create_benchmark_nested_conditional_pipeline(depth: int) -> PipelineConfig:
    """
    BENCHMARK: Nested Control Flow
    Tests deeply nested conditional logic.
    """
    stages = []

    for i in range(depth):
        stages.append(ComponentConfig(
            id=f"cond_{i}",
            type="conditional",
            input_mapping={
                "condition": True,
                "true_value": f"branch_true_{i}",
                "false_value": f"branch_false_{i}"
            },
            depends_on=[f"cond_{i-1}"] if i > 0 else []
        ))

    stages.append(ComponentConfig(
        id="result",
        type="logger",
        input_mapping={"message": f"Nested depth {depth} complete", "level": "info"},
        depends_on=[f"cond_{depth-1}"]
    ))

    return PipelineConfig(
        id=f"benchmark-nested-cond-{depth}",
        name=f"Benchmark: Nested Conditionals {depth}",
        description=f"Benchmark pipeline with {depth} nested conditionals",
        version="1.0.0",
        stages=stages,
        tags=["benchmark", "conditional", "nested"],
        category="benchmark"
    )


def create_benchmark_foreach_pipeline(item_count: int) -> PipelineConfig:
    """
    BENCHMARK: ForEach Scaling
    Tests iteration over collections of varying sizes.
    """
    stages = [
        ComponentConfig(
            id="foreach",
            type="foreach",
            input_mapping={
                "items": [{"id": i, "value": i * 10} for i in range(item_count)],
                "item_variable": "item",
                "loop_stages": []
            }
        ),
        ComponentConfig(
            id="complete",
            type="logger",
            input_mapping={"message": f"ForEach with {item_count} items complete", "level": "info"},
            depends_on=["foreach"]
        )
    ]

    return PipelineConfig(
        id=f"benchmark-foreach-{item_count}",
        name=f"Benchmark: ForEach {item_count}",
        description=f"Benchmark pipeline iterating over {item_count} items",
        version="1.0.0",
        stages=stages,
        tags=["benchmark", "foreach", "iteration"],
        category="benchmark"
    )


def create_benchmark_wide_conditional_pipeline(width: int) -> PipelineConfig:
    """
    BENCHMARK: Wide Parallel Conditionals
    Tests many conditional evaluations in parallel.
    """
    stages = []

    for i in range(width):
        stages.append(ComponentConfig(
            id=f"cond_{i}",
            type="conditional",
            input_mapping={
                "condition": i % 3 == 0,
                "true_value": f"branch_a_{i}",
                "false_value": f"branch_b_{i}"
            },
            depends_on=[]
        ))

    stages.append(ComponentConfig(
        id="aggregator",
        type="logger",
        input_mapping={"message": "Wide conditional complete", "level": "info"},
        depends_on=[f"cond_{i}" for i in range(width)]
    ))

    return PipelineConfig(
        id=f"benchmark-wide-cond-{width}",
        name=f"Benchmark: Wide Conditionals {width}",
        description=f"Benchmark pipeline with {width} parallel conditionals",
        version="1.0.0",
        stages=stages,
        tags=["benchmark", "conditional", "parallel"],
        category="benchmark"
    )


def create_benchmark_mixed_pipeline(complexity: int) -> PipelineConfig:
    """
    BENCHMARK: Mixed Workload
    Tests sequential preprocessing followed by parallel fan-out.
    """
    stages = []

    # Sequential preprocessing (3 stages)
    for i in range(3):
        stages.append(ComponentConfig(
            id=f"seq_{i}",
            type="json_transform",
            input_mapping={
                "data": {"step": i},
                "mapping": {"step_num": "data.step"},
                "defaults": {"result": f"step_{i}"}
            },
            depends_on=[f"seq_{i-1}"] if i > 0 else []
        ))

    # Parallel conditionals
    for i in range(complexity):
        stages.append(ComponentConfig(
            id=f"cond_{i}",
            type="conditional",
            input_mapping={
                "condition": i % 2 == 0,
                "true_value": f"even_{i}",
                "false_value": f"odd_{i}"
            },
            depends_on=["seq_2"]
        ))

    # Aggregation
    stages.append(ComponentConfig(
        id="aggregator",
        type="logger",
        input_mapping={"message": "Mixed workload complete", "level": "info"},
        depends_on=[f"cond_{i}" for i in range(complexity)]
    ))

    return PipelineConfig(
        id=f"benchmark-mixed-{complexity}",
        name=f"Benchmark: Mixed Workload {complexity}",
        description=f"Benchmark with 3 sequential + {complexity} parallel stages",
        version="1.0.0",
        stages=stages,
        tags=["benchmark", "mixed", "sequential", "parallel"],
        category="benchmark"
    )


def create_benchmark_transform_chain_pipeline(depth: int) -> PipelineConfig:
    """
    BENCHMARK: Transform Chain
    Tests JSON transformation operations in sequence.
    """
    stages = []

    for i in range(depth):
        stages.append(ComponentConfig(
            id=f"transform_{i}",
            type="json_transform",
            input_mapping={
                "data": {"step": i, "value": i * 2},
                "mapping": {"step": "data.step", "value": "data.value"},
                "defaults": {"next_step": f"step_{i+1}"}
            },
            depends_on=[f"transform_{i-1}"] if i > 0 else []
        ))

    stages.append(ComponentConfig(
        id="complete",
        type="logger",
        input_mapping={"message": f"Transform chain {depth} complete", "level": "info"},
        depends_on=[f"transform_{depth-1}"]
    ))

    return PipelineConfig(
        id=f"benchmark-transform-{depth}",
        name=f"Benchmark: Transform Chain {depth}",
        description=f"Benchmark with {depth} chained JSON transforms",
        version="1.0.0",
        stages=stages,
        tags=["benchmark", "transform", "sequential"],
        category="benchmark"
    )


# =============================================================================
# EXPORTED PIPELINES
# =============================================================================

# Pre-configured demo pipelines
DEMO_PIPELINES = {
    # Demo pipelines
    "parallel_5": create_parallel_processing_pipeline(5),
    "parallel_10": create_parallel_processing_pipeline(10),
    "parallel_25": create_parallel_processing_pipeline(25),

    "sequential_5": create_data_processing_pipeline(5),
    "sequential_10": create_data_processing_pipeline(10),
    "sequential_25": create_data_processing_pipeline(25),

    "conditional_branching": create_conditional_branching_pipeline(),

    "nested_conditionals_5": create_nested_conditionals_pipeline(5),
    "nested_conditionals_10": create_nested_conditionals_pipeline(10),

    "foreach_10": create_foreach_pipeline(10),
    "foreach_50": create_foreach_pipeline(50),
    "foreach_100": create_foreach_pipeline(100),

    "mixed_workload_10": create_mixed_workload_pipeline(10),
    "mixed_workload_25": create_mixed_workload_pipeline(25),

    "data_validation": create_validation_pipeline(),

    "filter_transform": create_filter_transform_pipeline(),
}

# Benchmark pipelines (exact pipelines used in benchmark suite)
BENCHMARK_PIPELINES = {
    # Parallel Scaling benchmarks
    "bench_parallel_5": create_benchmark_parallel_pipeline(5),
    "bench_parallel_10": create_benchmark_parallel_pipeline(10),
    "bench_parallel_25": create_benchmark_parallel_pipeline(25),
    "bench_parallel_50": create_benchmark_parallel_pipeline(50),
    "bench_parallel_100": create_benchmark_parallel_pipeline(100),

    # Sequential Depth benchmarks
    "bench_sequential_10": create_benchmark_sequential_pipeline(10),
    "bench_sequential_25": create_benchmark_sequential_pipeline(25),
    "bench_sequential_50": create_benchmark_sequential_pipeline(50),
    "bench_sequential_100": create_benchmark_sequential_pipeline(100),
    "bench_sequential_200": create_benchmark_sequential_pipeline(200),

    # Nested Conditionals benchmarks
    "bench_nested_cond_5": create_benchmark_nested_conditional_pipeline(5),
    "bench_nested_cond_10": create_benchmark_nested_conditional_pipeline(10),
    "bench_nested_cond_20": create_benchmark_nested_conditional_pipeline(20),
    "bench_nested_cond_30": create_benchmark_nested_conditional_pipeline(30),
    "bench_nested_cond_50": create_benchmark_nested_conditional_pipeline(50),

    # ForEach Scaling benchmarks
    "bench_foreach_10": create_benchmark_foreach_pipeline(10),
    "bench_foreach_50": create_benchmark_foreach_pipeline(50),
    "bench_foreach_100": create_benchmark_foreach_pipeline(100),
    "bench_foreach_250": create_benchmark_foreach_pipeline(250),
    "bench_foreach_500": create_benchmark_foreach_pipeline(500),

    # Wide Parallel Conditionals benchmarks
    "bench_wide_cond_10": create_benchmark_wide_conditional_pipeline(10),
    "bench_wide_cond_25": create_benchmark_wide_conditional_pipeline(25),
    "bench_wide_cond_50": create_benchmark_wide_conditional_pipeline(50),
    "bench_wide_cond_100": create_benchmark_wide_conditional_pipeline(100),
    "bench_wide_cond_200": create_benchmark_wide_conditional_pipeline(200),

    # Mixed Workload benchmarks
    "bench_mixed_10": create_benchmark_mixed_pipeline(10),
    "bench_mixed_25": create_benchmark_mixed_pipeline(25),
    "bench_mixed_50": create_benchmark_mixed_pipeline(50),
    "bench_mixed_100": create_benchmark_mixed_pipeline(100),

    # Transform Chain benchmarks
    "bench_transform_10": create_benchmark_transform_chain_pipeline(10),
    "bench_transform_25": create_benchmark_transform_chain_pipeline(25),
    "bench_transform_50": create_benchmark_transform_chain_pipeline(50),
    "bench_transform_100": create_benchmark_transform_chain_pipeline(100),
    "bench_transform_200": create_benchmark_transform_chain_pipeline(200),
}

# Combined: all pipelines
ALL_PIPELINES = {**DEMO_PIPELINES, **BENCHMARK_PIPELINES}


def get_pipeline(name: str) -> PipelineConfig:
    """Get any pipeline by name (demo or benchmark)."""
    if name in ALL_PIPELINES:
        return ALL_PIPELINES[name]
    available = ", ".join(ALL_PIPELINES.keys())
    raise ValueError(f"Pipeline '{name}' not found. Available: {available}")


def get_demo_pipeline(name: str) -> PipelineConfig:
    """Get a demo pipeline by name."""
    if name in DEMO_PIPELINES:
        return DEMO_PIPELINES[name]
    available = ", ".join(DEMO_PIPELINES.keys())
    raise ValueError(f"Demo pipeline '{name}' not found. Available: {available}")


def get_benchmark_pipeline(name: str) -> PipelineConfig:
    """Get a benchmark pipeline by name."""
    if name in BENCHMARK_PIPELINES:
        return BENCHMARK_PIPELINES[name]
    available = ", ".join(BENCHMARK_PIPELINES.keys())
    raise ValueError(f"Benchmark pipeline '{name}' not found. Available: {available}")


def list_pipelines() -> list[str]:
    """List all available pipeline names."""
    return list(ALL_PIPELINES.keys())


def list_demo_pipelines() -> list[str]:
    """List demo pipeline names."""
    return list(DEMO_PIPELINES.keys())


def list_benchmark_pipelines() -> list[str]:
    """List benchmark pipeline names."""
    return list(BENCHMARK_PIPELINES.keys())


if __name__ == "__main__":
    print("=" * 70)
    print("                    FLOWMASON SAVED PIPELINES")
    print("=" * 70)

    print(f"\n  DEMO PIPELINES ({len(DEMO_PIPELINES)}):")
    print("-" * 70)
    for name, pipeline in DEMO_PIPELINES.items():
        stage_count = len(pipeline.stages)
        desc = pipeline.description[:45] if pipeline.description else "No description"
        print(f"  {name:30s} {stage_count:3d} stages  {desc}...")

    print(f"\n  BENCHMARK PIPELINES ({len(BENCHMARK_PIPELINES)}):")
    print("-" * 70)
    for name, pipeline in BENCHMARK_PIPELINES.items():
        stage_count = len(pipeline.stages)
        desc = pipeline.description[:45] if pipeline.description else "No description"
        print(f"  {name:30s} {stage_count:3d} stages  {desc}...")

    print("\n" + "=" * 70)
    print(f"  TOTAL: {len(ALL_PIPELINES)} pipelines available")
    print("=" * 70)

    print("\n  USAGE:")
    print("  ------")
    print("  from demos.saved_pipelines import get_pipeline, ALL_PIPELINES")
    print("  from demos.saved_pipelines import DEMO_PIPELINES, BENCHMARK_PIPELINES")
    print("")
    print("  # Get any pipeline")
    print("  pipeline = get_pipeline('bench_parallel_100')")
    print("")
    print("  # Access collections directly")
    print("  pipeline = BENCHMARK_PIPELINES['bench_sequential_200']")
    print("  pipeline = DEMO_PIPELINES['mixed_workload_25']")
    print("")
