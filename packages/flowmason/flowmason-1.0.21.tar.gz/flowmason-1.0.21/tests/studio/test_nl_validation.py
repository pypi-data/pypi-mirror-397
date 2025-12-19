"""
Additional validation tests for NLBuilderService.

These focus on control-flow patterns and basic structural checks so
we can catch miswired pipelines early.
"""

import asyncio

from flowmason_studio.services.nl_builder_service import NLBuilderService
from flowmason_studio.models.nl_builder import GenerationStatus


async def _generate(description: str):
    service = NLBuilderService()
    result = await service.generate_pipeline(description=description)
    return result


def test_validation_flags_unknown_dependencies():
    """Pipelines with dangling dependencies should fail validation."""

    async def run():
        service = NLBuilderService()
        # Start from a simple valid pipeline
        result = await service.generate_pipeline(
            description="Summarize a document with AI."
        )
        assert result.pipeline is not None

        # Introduce an invalid dependency
        pipeline = result.pipeline
        pipeline.stages[0].depends_on.append("non_existent_stage")

        errors, _warnings = service._validate_pipeline(pipeline)  # type: ignore[attr-defined]
        assert any("depends_on unknown stage" in e for e in errors)

    asyncio.run(run())


def test_validation_warns_on_foreach_loop_stages():
    """Foreach pattern should have loop_stages that reference known stages."""

    async def run():
        result = await _generate(
            "Take a list of items and for each item run an AI analysis and collect all answers."
        )
        assert result.status == GenerationStatus.COMPLETED
        assert result.pipeline is not None

        service = NLBuilderService()
        errors, warnings = service._validate_pipeline(result.pipeline)  # type: ignore[attr-defined]

        # Foreach helper should wire loop_stages correctly, so there should
        # be no foreach-specific warnings in this case.
        assert not any("foreach" in w for w in warnings)
        assert not errors

    asyncio.run(run())


def test_validation_warns_on_conditional_branches():
    """Conditional pattern should reference valid true/false stages."""

    async def run():
        result = await _generate(
            "If the score is high then send an email, otherwise log a warning."
        )
        assert result.status == GenerationStatus.COMPLETED
        assert result.pipeline is not None

        service = NLBuilderService()
        errors, warnings = service._validate_pipeline(result.pipeline)  # type: ignore[attr-defined]

        # Our conditional helper wires true/false branches to existing logger stages,
        # so there should be no conditional-specific warnings or errors.
        assert not any("conditional" in w for w in warnings)
        assert not errors

    asyncio.run(run())

