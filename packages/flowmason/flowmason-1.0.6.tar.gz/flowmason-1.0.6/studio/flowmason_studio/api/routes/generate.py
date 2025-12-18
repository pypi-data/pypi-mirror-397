"""
Pipeline Generation API Routes.

Provides HTTP API for AI-powered pipeline generation from natural language.
This is a convenience wrapper around the nl-builder service.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from flowmason_studio.services.nl_builder_service import get_nl_builder_service

router = APIRouter(prefix="/generate", tags=["generate"])


class GeneratePipelineRequest(BaseModel):
    """Request to generate a pipeline from natural language."""
    description: str
    options: Optional[Dict[str, Any]] = None


class GeneratedStage(BaseModel):
    """A generated pipeline stage."""
    id: str
    name: str
    component_type: str
    config: Dict[str, Any]
    depends_on: List[str] = []


class GeneratedPipeline(BaseModel):
    """A generated pipeline definition."""
    name: str
    version: str = "1.0.0"
    description: str
    input_schema: Dict[str, Any]
    stages: List[GeneratedStage]
    output_stage_id: str


class GeneratePipelineResponse(BaseModel):
    """Response containing the generated pipeline."""
    pipeline: GeneratedPipeline
    analysis: Optional[Dict[str, Any]] = None


@router.post("/pipeline", response_model=GeneratePipelineResponse)
async def generate_pipeline(request: GeneratePipelineRequest) -> GeneratePipelineResponse:
    """
    Generate a pipeline from a natural language description.

    The AI analyzes your description and generates a complete pipeline
    with appropriate components and configurations.

    **Example:**
    ```json
    {
      "description": "Summarize a long article, then translate the summary to Spanish",
      "options": {
        "include_validation": true,
        "include_logging": true
      }
    }
    ```
    """
    # Validate description
    if not request.description or not request.description.strip():
        raise HTTPException(
            status_code=400,
            detail="Description is required and cannot be empty"
        )

    service = get_nl_builder_service()

    try:
        result = await service.generate_pipeline(
            description=request.description,
            mode="detailed",
            context=request.options,
        )

        # Convert the nl_builder response to our response format
        pipeline_data = result.pipeline

        if not pipeline_data:
            # Surface validation/analysis errors as a client error instead of an internal error
            detail = result.error or "Failed to generate pipeline: no pipeline returned from service"
            raise HTTPException(
                status_code=400,
                detail=detail,
            )

        stages = [
            GeneratedStage(
                id=s.id,
                name=s.name,
                component_type=s.component_type,
                config=s.config if hasattr(s, 'config') else {},
                depends_on=s.depends_on if hasattr(s, 'depends_on') else [],
            )
            for s in pipeline_data.stages
        ]

        # Determine output_stage_id - find stages that no other stage depends on
        all_stage_ids = {s.id for s in stages}
        dependent_ids = set()
        for s in stages:
            dependent_ids.update(s.depends_on)
        output_candidates = all_stage_ids - dependent_ids
        output_stage_id = list(output_candidates)[0] if output_candidates else (stages[-1].id if stages else "output")

        pipeline = GeneratedPipeline(
            name=pipeline_data.name,
            version=getattr(pipeline_data, 'version', '1.0.0'),
            description=pipeline_data.description,
            input_schema=pipeline_data.input_schema or {"type": "object", "properties": {}},
            stages=stages,
            output_stage_id=output_stage_id,
        )

        return GeneratePipelineResponse(
            pipeline=pipeline,
            analysis=result.analysis.model_dump() if result.analysis else None,
        )

    except HTTPException:
        # Propagate HTTPExceptions (e.g., validation errors) unchanged
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate pipeline: {str(e)}"
        )
