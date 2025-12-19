"""
Tests for NLBuilderService pipeline generation from natural language.
"""

import asyncio

from flowmason_studio.services.nl_builder_service import NLBuilderService
from flowmason_studio.models.nl_builder import GenerationStatus


async def _generate(description: str) -> tuple[GenerationStatus, object]:
    service = NLBuilderService()
    result = await service.generate_pipeline(description=description)
    return result.status, result.pipeline


def test_generate_simple_summarization_pipeline():
    """Summarization + translation prompt should produce a generator-based pipeline."""

    async def run():
        status, pipeline = await _generate(
            "Summarize a long article and then translate the summary to Spanish"
        )
        assert status == GenerationStatus.COMPLETED
        assert pipeline is not None
        # Expect at least one generator stage
        component_types = [s.component_type for s in pipeline.stages]
        assert "generator" in component_types

    asyncio.run(run())


def test_generate_foreach_pattern_pipeline():
    """Foreach-style prompt should produce a foreach + per-item generator pattern."""

    async def run():
        status, pipeline = await _generate(
            "Take a list of items and for each item run an AI analysis and collect all answers."
        )
        assert status == GenerationStatus.COMPLETED
        assert pipeline is not None

        stage_ids = {s.id for s in pipeline.stages}
        # Our foreach pattern helper should create these stages
        assert {"foreach_items", "qa_each", "aggregate_results"}.issubset(stage_ids)

        # Input schema should expose items as an array
        assert pipeline.input_schema["type"] == "object"
        assert "items" in pipeline.input_schema["properties"]
        assert pipeline.input_schema["properties"]["items"]["type"] == "array"

    asyncio.run(run())


def test_generate_validation_transform_pipeline():
    """Validation + transform prompt should use schema_validate then json_transform."""

    async def run():
        status, pipeline = await _generate(
            "Validate incoming records and then transform them into a normalized format."
        )
        assert status == GenerationStatus.COMPLETED
        assert pipeline is not None

        ids_types = {(s.id, s.component_type) for s in pipeline.stages}
        assert ("validate_data", "schema_validate") in ids_types
        assert ("transform_data", "json_transform") in ids_types

        assert pipeline.input_schema["type"] == "object"
        assert "data" in pipeline.input_schema["properties"]

    asyncio.run(run())


def test_generate_http_ingest_pipeline():
    """HTTP ingest + send prompt should use http_request -> json_transform -> http_request pattern."""

    async def run():
        status, pipeline = await _generate(
            "Fetch data from a source API and then send the processed results to another endpoint."
        )
        assert status == GenerationStatus.COMPLETED
        assert pipeline is not None

        ids_types = [(s.id, s.component_type) for s in pipeline.stages]
        assert ("fetch_source", "http_request") in ids_types
        assert ("transform_payload", "json_transform") in ids_types
        assert ("send_output", "http_request") in ids_types

        props = pipeline.input_schema["properties"]
        assert "source_url" in props and "target_url" in props

    asyncio.run(run())


def test_generate_conditional_pipeline():
    """Conditional prompt should produce conditional + true/false logger branches."""

    async def run():
        status, pipeline = await _generate(
            "If the score is high then send an email, otherwise log a warning."
        )
        assert status == GenerationStatus.COMPLETED
        assert pipeline is not None

        ids_types = [(s.id, s.component_type) for s in pipeline.stages]
        assert ("check_condition", "conditional") in ids_types
        assert ("true_path", "logger") in ids_types
        assert ("false_path", "logger") in ids_types

        props = pipeline.input_schema["properties"]
        assert "condition" in props

    asyncio.run(run())
