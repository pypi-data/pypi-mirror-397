"""
Natural Language Pipeline Builder API Routes.

Provides HTTP API for AI-powered pipeline generation from natural language.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from flowmason_studio.models.nl_builder import (
    AnalyzeRequestResponse,
    ComponentMatch,
    ComponentMatchRequest,
    ComponentMatchResponse,
    GeneratePipelineRequest,
    GeneratePipelineResponse,
    GeneratedPipeline,
    GenerationAnalysis,
    GenerationMode,
    GenerationResult,
    RefinementRequest,
    RefinementResult,
)
from flowmason_studio.services.nl_builder_service import get_nl_builder_service

router = APIRouter(prefix="/nl-builder", tags=["nl-builder"])


# =============================================================================
# Pipeline Generation
# =============================================================================


@router.post("/generate", response_model=GeneratePipelineResponse)
async def generate_pipeline(request: GeneratePipelineRequest) -> GeneratePipelineResponse:
    """
    Generate a pipeline from a natural language description.

    The AI analyzes your description and generates a complete pipeline
    with appropriate components and configurations.

    **Example:**
    ```json
    {
      "description": "Summarize a long article, then translate the summary to Spanish",
      "mode": "detailed"
    }
    ```
    """
    service = get_nl_builder_service()

    result = await service.generate_pipeline(
        description=request.description,
        mode=request.mode,
        context=request.context,
        examples=request.examples,
        preferred_components=request.preferred_components,
        avoid_components=request.avoid_components,
    )

    success = result.pipeline is not None
    message = "Pipeline generated successfully" if success else (result.error or "Generation failed")

    return GeneratePipelineResponse(
        success=success,
        result=result,
        message=message,
    )


@router.get("/generations/{generation_id}", response_model=GenerationResult)
async def get_generation(generation_id: str) -> GenerationResult:
    """
    Get a previous generation result by ID.

    Use this to retrieve the results of a generation request,
    including the generated pipeline and any validation messages.
    """
    service = get_nl_builder_service()
    result = service.get_generation(generation_id)

    if not result:
        raise HTTPException(status_code=404, detail="Generation not found")

    return result


@router.post("/refine", response_model=RefinementResult)
async def refine_pipeline(request: RefinementRequest) -> RefinementResult:
    """
    Refine a previously generated pipeline based on feedback.

    Provide feedback on what to change, and the AI will modify
    the pipeline accordingly.

    **Example:**
    ```json
    {
      "generation_id": "abc123",
      "feedback": "Add error handling and make the output more structured"
    }
    ```
    """
    service = get_nl_builder_service()

    try:
        result = await service.refine_pipeline(
            generation_id=request.generation_id,
            feedback=request.feedback,
            modifications=request.modifications,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =============================================================================
# Analysis
# =============================================================================


@router.post("/analyze", response_model=AnalyzeRequestResponse)
async def analyze_request(
    description: str = Query(..., min_length=10, description="Description to analyze"),
) -> AnalyzeRequestResponse:
    """
    Analyze a natural language request without generating a pipeline.

    Returns the identified intent, entities, actions, and any ambiguities
    that might need clarification.

    Useful for understanding how the AI interprets your description
    before generating a pipeline.
    """
    service = get_nl_builder_service()
    analysis = await service.analyze_request(description)

    # Estimate complexity
    complexity = "simple"
    if len(analysis.actions) > 2 or len(analysis.constraints) > 1:
        complexity = "moderate"
    if len(analysis.actions) > 4 or len(analysis.ambiguities) > 2:
        complexity = "complex"

    # Estimate stages
    estimated_stages = max(1, len(analysis.actions) + len(analysis.data_sources))

    # Generate suggested approach
    approach_parts = []
    if analysis.data_sources:
        approach_parts.append(f"fetch data from {', '.join(analysis.data_sources)}")
    if analysis.actions:
        approach_parts.append(f"perform {', '.join(analysis.actions)}")
    if analysis.outputs:
        approach_parts.append(f"output as {', '.join(analysis.outputs)}")

    suggested_approach = " → ".join(approach_parts) if approach_parts else "Process input and generate output"

    return AnalyzeRequestResponse(
        analysis=analysis,
        suggested_approach=suggested_approach,
        estimated_complexity=complexity,
        estimated_stages=estimated_stages,
    )


# =============================================================================
# Component Matching
# =============================================================================


@router.post("/match-components", response_model=ComponentMatchResponse)
async def match_components(request: ComponentMatchRequest) -> ComponentMatchResponse:
    """
    Find components that match a task description.

    Returns components ranked by relevance to the described task.

    **Example:**
    ```json
    {
      "task": "filter a list of products by price",
      "limit": 3
    }
    ```
    """
    service = get_nl_builder_service()
    matches = await service.find_components(
        task=request.task,
        limit=request.limit,
    )

    return ComponentMatchResponse(
        task=request.task,
        matches=matches,
    )


@router.get("/components/search", response_model=List[ComponentMatch])
async def search_components(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum results"),
) -> List[ComponentMatch]:
    """
    Search for components by keyword.

    A convenience endpoint for quick component lookup.
    """
    service = get_nl_builder_service()
    return await service.find_components(task=q, limit=limit)


# =============================================================================
# Quick Generation
# =============================================================================


@router.post("/quick", response_model=GeneratedPipeline)
async def quick_generate(
    description: str = Query(..., min_length=10, description="Pipeline description"),
) -> GeneratedPipeline:
    """
    Quick pipeline generation from a short description.

    A convenience endpoint that returns just the generated pipeline
    without detailed analysis. Best for simple pipelines.
    """
    service = get_nl_builder_service()

    result = await service.generate_pipeline(
        description=description,
        mode=GenerationMode.QUICK,
    )

    if not result.pipeline:
        raise HTTPException(
            status_code=400,
            detail=result.error or "Failed to generate pipeline",
        )

    return result.pipeline


# =============================================================================
# Templates
# =============================================================================


class PipelineTemplate(BaseModel):
    """A predefined pipeline template."""

    id: str
    name: str
    description: str
    category: str
    example_prompt: str
    stages: int


TEMPLATES = [
    PipelineTemplate(
        id="summarization",
        name="Text Summarization",
        description="Summarize long text into concise points",
        category="ai",
        example_prompt="Summarize this article into 3 key points",
        stages=1,
    ),
    PipelineTemplate(
        id="content-review",
        name="Content Review",
        description="Generate content and have it reviewed for quality",
        category="ai",
        example_prompt="Generate a product description and review it for accuracy",
        stages=2,
    ),
    PipelineTemplate(
        id="data-enrichment",
        name="Data Enrichment",
        description="Fetch external data and combine with input",
        category="integration",
        example_prompt="Enrich customer data with external API lookup",
        stages=3,
    ),
    PipelineTemplate(
        id="batch-processing",
        name="Batch Processing",
        description="Process a list of items one by one",
        category="data",
        example_prompt="Process each item in a list and generate summaries",
        stages=2,
    ),
    PipelineTemplate(
        id="validation-pipeline",
        name="Validation Pipeline",
        description="Validate input data and report issues",
        category="data",
        example_prompt="Validate JSON data against a schema and report errors",
        stages=2,
    ),
]


@router.get("/templates", response_model=List[PipelineTemplate])
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
) -> List[PipelineTemplate]:
    """
    List available pipeline templates.

    Templates provide starting points for common pipeline patterns.
    Use the example_prompt as a guide for your own descriptions.
    """
    templates = TEMPLATES
    if category:
        templates = [t for t in templates if t.category == category]
    return templates


@router.post("/from-template/{template_id}", response_model=GeneratePipelineResponse)
async def generate_from_template(
    template_id: str,
    customization: Optional[str] = Query(
        None,
        description="Additional customization to apply"
    ),
) -> GeneratePipelineResponse:
    """
    Generate a pipeline from a template.

    Uses the template's example prompt as a base, with optional
    customization applied.
    """
    template = next((t for t in TEMPLATES if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    description = template.example_prompt
    if customization:
        description = f"{description}. {customization}"

    service = get_nl_builder_service()
    result = await service.generate_pipeline(
        description=description,
        mode=GenerationMode.DETAILED,
    )

    success = result.pipeline is not None
    return GeneratePipelineResponse(
        success=success,
        result=result,
        message=f"Generated from template: {template.name}",
    )
