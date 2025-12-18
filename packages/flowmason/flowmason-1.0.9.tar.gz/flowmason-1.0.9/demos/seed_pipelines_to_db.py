"""
Seed Demo and Benchmark Pipelines to FlowMason Database.

This script saves all demo and benchmark pipelines to the SQLite database
so they can be accessed through the FlowMason Studio UI and API.

Usage:
    python demos/seed_pipelines_to_db.py
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "studio"))

from flowmason_studio.services.database import get_connection
from flowmason_studio.services.storage import get_pipeline_storage
from flowmason_studio.models.api import PipelineCreate, PipelineStage, PipelineInputSchema, PipelineOutputSchema

from saved_pipelines import ALL_PIPELINES, DEMO_PIPELINES, BENCHMARK_PIPELINES
from real_ai_pipelines import REAL_AI_PIPELINES


def convert_to_pipeline_create(pipeline_config) -> PipelineCreate:
    """Convert a PipelineConfig to PipelineCreate for storage."""

    # Convert stages from ComponentConfig to PipelineStage
    stages = []
    for idx, stage in enumerate(pipeline_config.stages):
        pipeline_stage = PipelineStage(
            id=stage.id,
            component_type=stage.type,  # Maps 'type' to 'component_type'
            name=stage.id.replace("_", " ").title(),  # Generate readable name
            config={},  # Static config
            input_mapping=stage.input_mapping or {},
            depends_on=stage.depends_on or [],
            position={"x": (idx % 5) * 250, "y": (idx // 5) * 150},  # Auto-layout grid
        )
        stages.append(pipeline_stage)

    return PipelineCreate(
        name=pipeline_config.name,
        description=pipeline_config.description or "",
        input_schema=PipelineInputSchema(),
        output_schema=PipelineOutputSchema(),
        stages=stages,
        output_stage_id=pipeline_config.output_stage_id,
        category=pipeline_config.category or "demo",
        tags=pipeline_config.tags or [],
        is_template=True,  # Mark as templates so they can be copied
        sample_input={},
    )


def seed_pipelines(clear_existing: bool = False):
    """Seed all pipelines to the database."""

    # Initialize database connection (this also initializes schema)
    get_connection()
    storage = get_pipeline_storage()

    # Optionally clear existing demo/benchmark pipelines
    if clear_existing:
        existing, _ = storage.list(limit=1000)
        for pipeline in existing:
            if pipeline.category in ("demo", "benchmark"):
                storage.delete(pipeline.id)
                print(f"  Deleted existing: {pipeline.name}")

    created_count = 0
    skipped_count = 0

    print("\n  Seeding Demo Pipelines...")
    print("-" * 60)

    for name, pipeline_config in DEMO_PIPELINES.items():
        try:
            pipeline_create = convert_to_pipeline_create(pipeline_config)
            pipeline_create.category = "demo"

            result = storage.create(pipeline_create)
            print(f"  + {result.name:40s} ({len(result.stages)} stages) -> {result.id}")
            created_count += 1
        except Exception as e:
            print(f"  ! Failed to create {name}: {e}")
            skipped_count += 1

    print(f"\n  Seeding Benchmark Pipelines...")
    print("-" * 60)

    for name, pipeline_config in BENCHMARK_PIPELINES.items():
        try:
            pipeline_create = convert_to_pipeline_create(pipeline_config)
            pipeline_create.category = "benchmark"

            result = storage.create(pipeline_create)
            print(f"  + {result.name:40s} ({len(result.stages)} stages) -> {result.id}")
            created_count += 1
        except Exception as e:
            print(f"  ! Failed to create {name}: {e}")
            skipped_count += 1

    print(f"\n  Seeding Real AI Pipelines...")
    print("-" * 60)

    for name, pipeline_config in REAL_AI_PIPELINES.items():
        try:
            pipeline_create = convert_to_pipeline_create(pipeline_config)
            pipeline_create.category = "real-ai"

            result = storage.create(pipeline_create)
            print(f"  + {result.name:40s} ({len(result.stages)} stages) -> {result.id}")
            created_count += 1
        except Exception as e:
            print(f"  ! Failed to create {name}: {e}")
            skipped_count += 1

    return created_count, skipped_count


def list_saved_pipelines():
    """List all pipelines in the database."""
    get_connection()
    storage = get_pipeline_storage()

    # List demo pipelines
    demos, demo_total = storage.list(category="demo", limit=100)
    benchmarks, bench_total = storage.list(category="benchmark", limit=100)
    real_ai, real_ai_total = storage.list(category="real-ai", limit=100)

    print("\n  DEMO PIPELINES IN DATABASE:")
    print("-" * 60)
    for p in demos:
        print(f"  {p.id:20s} {p.name:40s} ({p.stage_count} stages)")

    print(f"\n  BENCHMARK PIPELINES IN DATABASE:")
    print("-" * 60)
    for p in benchmarks:
        print(f"  {p.id:20s} {p.name:40s} ({p.stage_count} stages)")

    print(f"\n  REAL AI PIPELINES IN DATABASE:")
    print("-" * 60)
    for p in real_ai:
        print(f"  {p.id:20s} {p.name:40s} ({p.stage_count} stages)")

    return demo_total + bench_total + real_ai_total


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed FlowMason pipelines to database")
    parser.add_argument("--clear", action="store_true", help="Clear existing demo/benchmark pipelines first")
    parser.add_argument("--list", action="store_true", help="List existing pipelines instead of seeding")
    args = parser.parse_args()

    print("=" * 60)
    print("         FLOWMASON PIPELINE DATABASE SEEDER")
    print("=" * 60)

    if args.list:
        total = list_saved_pipelines()
        print(f"\n  Total pipelines in database: {total}")
    else:
        created, skipped = seed_pipelines(clear_existing=args.clear)

        print("\n" + "=" * 60)
        print(f"  COMPLETE: {created} pipelines created, {skipped} skipped")
        print("=" * 60)

        print("\n  Pipelines are now available in FlowMason Studio!")
        print("  Access them at: http://localhost:8999/pipelines")
        print("")
