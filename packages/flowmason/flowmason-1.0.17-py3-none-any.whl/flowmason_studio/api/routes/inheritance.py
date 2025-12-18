"""
Pipeline Inheritance & Composition API Routes.

Provides HTTP API for extending and composing pipelines.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from flowmason_studio.models.inheritance import (
    BasePipeline,
    ComposedPipeline,
    ComposePipelinesRequest,
    CompositionMode,
    CreateBasePipelineRequest,
    ExtendPipelineRequest,
    ListBasePipelinesResponse,
    ResolvedPipeline,
    ResolvePipelineRequest,
    ResolvePipelineResponse,
    ValidateInheritanceResponse,
)
from flowmason_studio.services.inheritance_service import get_inheritance_service
from flowmason_studio.services.storage import get_pipeline_storage

router = APIRouter(prefix="/inheritance", tags=["inheritance"])


# =============================================================================
# Base Pipeline Templates
# =============================================================================


@router.get("/templates", response_model=ListBasePipelinesResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    include_abstract: bool = Query(True, description="Include abstract templates"),
) -> ListBasePipelinesResponse:
    """
    List all available base pipeline templates.

    Templates are reusable pipeline patterns that can be extended.
    """
    service = get_inheritance_service()
    templates = service.list_base_pipelines(
        category=category,
        include_abstract=include_abstract,
    )
    categories = service.get_categories()

    return ListBasePipelinesResponse(
        templates=templates,
        total=len(templates),
        categories=categories,
    )


@router.get("/templates/{template_id}", response_model=BasePipeline)
async def get_template(template_id: str) -> BasePipeline:
    """
    Get a base pipeline template by ID.
    """
    service = get_inheritance_service()
    template = service.get_base_pipeline(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.post("/templates", response_model=BasePipeline)
async def create_template(request: CreateBasePipelineRequest) -> BasePipeline:
    """
    Create a new base pipeline template.

    Templates can be:
    - Abstract: Cannot run directly, must be extended
    - Concrete: Can run directly or be extended
    """
    service = get_inheritance_service()

    template = service.create_base_pipeline(
        name=request.name,
        description=request.description,
        category=request.category,
        tags=request.tags,
        is_abstract=request.is_abstract,
        required_overrides=request.required_overrides,
        sealed_stages=request.sealed_stages,
        stages=request.stages,
        variables=request.variables,
        settings=request.settings,
    )

    return template


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str) -> dict:
    """
    Delete a base pipeline template.
    """
    service = get_inheritance_service()

    if not service.delete_base_pipeline(template_id):
        raise HTTPException(status_code=404, detail="Template not found")

    return {"success": True}


@router.get("/categories")
async def list_categories() -> dict:
    """
    List all template categories.
    """
    service = get_inheritance_service()
    return {"categories": service.get_categories()}


# =============================================================================
# Pipeline Extension
# =============================================================================


@router.post("/extend")
async def extend_pipeline(request: ExtendPipelineRequest) -> dict:
    """
    Create a new pipeline by extending a base template.

    The new pipeline inherits all stages from the base and can:
    - Override existing stages
    - Add new stages
    - Remove stages
    - Override variables
    """
    service = get_inheritance_service()

    try:
        pipeline, warnings = service.extend_pipeline(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Optionally save to storage
    storage = get_pipeline_storage()
    storage.save_pipeline(pipeline["id"], pipeline)

    return {
        "pipeline": pipeline,
        "warnings": warnings,
    }


@router.post("/validate")
async def validate_inheritance(
    base_pipeline_id: str,
    request: ExtendPipelineRequest,
) -> ValidateInheritanceResponse:
    """
    Validate inheritance configuration before applying.

    Checks for:
    - Required overrides
    - Sealed stage violations
    - Circular dependencies
    """
    service = get_inheritance_service()

    result = service.validate_inheritance(
        base_pipeline_id,
        request.stage_overrides,
        request.stage_additions,
        request.stage_removals,
    )

    return ValidateInheritanceResponse(**result)


# =============================================================================
# Pipeline Composition
# =============================================================================


@router.post("/compose", response_model=ComposedPipeline)
async def compose_pipelines(request: ComposePipelinesRequest) -> ComposedPipeline:
    """
    Create a composed pipeline from multiple pipelines.

    Composition modes:
    - sequential: Run pipelines one after another
    - parallel: Run pipelines in parallel, merge outputs
    - conditional: Choose pipeline based on condition
    """
    service = get_inheritance_service()

    composition = service.compose_pipelines(
        name=request.name,
        pipeline_ids=request.pipeline_ids,
        mode=request.mode,
        output_mapping=request.output_mapping,
        condition=request.condition,
        condition_map=request.condition_map,
        default_pipeline=request.default_pipeline,
        merge_strategy=request.merge_strategy,
    )

    return composition


@router.get("/compose/{composition_id}", response_model=ComposedPipeline)
async def get_composition(composition_id: str) -> ComposedPipeline:
    """
    Get a pipeline composition by ID.
    """
    service = get_inheritance_service()
    composition = service.get_composition(composition_id)

    if not composition:
        raise HTTPException(status_code=404, detail="Composition not found")

    return composition


@router.post("/compose/{composition_id}/resolve", response_model=ResolvedPipeline)
async def resolve_composition(composition_id: str) -> ResolvedPipeline:
    """
    Resolve a composition into an executable pipeline.

    Combines all composed pipelines into a single pipeline with
    properly connected stages.
    """
    service = get_inheritance_service()
    storage = get_pipeline_storage()

    composition = service.get_composition(composition_id)
    if not composition:
        raise HTTPException(status_code=404, detail="Composition not found")

    # Fetch all pipelines
    pipelines = {}
    for pid in composition.pipelines:
        pipeline = storage.get_pipeline(pid)
        if pipeline:
            pipelines[pid] = pipeline

    resolved = service.resolve_composition(composition_id, pipelines)
    return resolved


# =============================================================================
# Resolution
# =============================================================================


@router.post("/resolve", response_model=ResolvePipelineResponse)
async def resolve_pipeline(request: ResolvePipelineRequest) -> ResolvePipelineResponse:
    """
    Fully resolve a pipeline's inheritance chain.

    Returns the pipeline with all inherited stages merged.
    """
    service = get_inheritance_service()
    storage = get_pipeline_storage()

    pipeline = storage.get_pipeline(request.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    resolved = service.resolve_pipeline(
        request.pipeline_id,
        pipeline,
        storage.get_pipeline,
    )

    source_mapping = None
    if request.include_source_mapping:
        source_mapping = {}
        for stage in resolved.stages:
            source = stage.get("_source_pipeline", request.pipeline_id)
            source_mapping[stage["id"]] = source

    return ResolvePipelineResponse(
        pipeline=resolved,
        source_mapping=source_mapping,
    )


@router.get("/lineage/{pipeline_id}")
async def get_pipeline_lineage(pipeline_id: str) -> dict:
    """
    Get the inheritance lineage of a pipeline.

    Shows which base pipelines this pipeline extends.
    """
    service = get_inheritance_service()
    storage = get_pipeline_storage()

    pipeline = storage.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    resolved = service.resolve_pipeline(
        pipeline_id,
        pipeline,
        storage.get_pipeline,
    )

    return {
        "pipeline_id": pipeline_id,
        "base_pipelines": resolved.base_pipelines,
        "composed_from": resolved.composed_from,
    }
