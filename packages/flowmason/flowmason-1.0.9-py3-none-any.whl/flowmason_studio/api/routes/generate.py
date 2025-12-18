"""
Pipeline Generation API Routes.

Provides HTTP API for AI-powered pipeline generation from natural language.
This is a convenience wrapper around the nl-builder service.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from flowmason_studio.api.routes.execution import _execute_pipeline_task  # type: ignore
from flowmason_studio.models.api import PipelineDetail, PipelineInputSchema, PipelineOutputSchema, PipelineStage
from flowmason_studio.services.nl_builder_service import get_nl_builder_service
from flowmason_studio.services.storage import get_pipeline_storage

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

    try:
        # Normalize options and read toggle for AI interpreter
        raw_options = request.options or {}
        use_ai_interpreter = bool(raw_options.get("use_ai_interpreter", False))
        base_context: Dict[str, Any] = {
            k: v for k, v in raw_options.items() if k != "use_ai_interpreter"
        }

        # ------------------------------------------------------------------
        # Step 1: Optionally run the NL interpreter pipeline to get context
        # ------------------------------------------------------------------
        interpreter_context: Optional[Dict[str, Any]] = None

        if use_ai_interpreter:
            storage = get_pipeline_storage()
            interpreter = storage.get_by_name("nl-interpreter")

            if interpreter:
                # Minimal inline run of the interpreter pipeline using the same
                # execution task used by the main execution API.
                from flowmason_studio.services.storage import RunStorage, get_run_storage
                from flowmason_studio.services.registry import get_registry

                run_storage: RunStorage = get_run_storage()
                registry = get_registry()

                # Create a temporary run record
                run = run_storage.create(
                    pipeline_id=interpreter.id,
                    inputs={"description": request.description},
                    org_id=None,
                )

                await _execute_pipeline_task(
                    run_id=run.id,
                    pipeline_detail=interpreter,
                    inputs={"description": request.description},
                    registry=registry,
                    run_storage=run_storage,
                    breakpoints=None,
                    org_id=None,
                )

                completed = run_storage.get(run.id, org_id=None)
                if completed and completed.output:
                    # Expect shape: {"context": {...}}
                    output = completed.output
                    if isinstance(output, dict):
                        interpreter_context = output.get("context") or output

        # ------------------------------------------------------------------
        # Step 2: Use NL builder with interpreter-derived context
        # ------------------------------------------------------------------
        service = get_nl_builder_service()

        generation_context: Dict[str, Any] = base_context
        if interpreter_context:
            # Merge interpreter context into options; interpreter wins on conflicts
            generation_context = {**generation_context, **interpreter_context}

        result = await service.generate_pipeline(
            description=request.description,
            mode="detailed",
            context=generation_context,
        )

        # Use the generated pipeline if available; otherwise synthesize a
        # simple one-stage pipeline directly from the prompt so that any
        # non-empty description yields a valid pipeline.
        pipeline_data = result.pipeline

        if pipeline_data and pipeline_data.stages:
            stages = [
                GeneratedStage(
                    id=s.id,
                    name=s.name,
                    component_type=s.component_type,
                    config=s.config if hasattr(s, "config") else {},
                    depends_on=s.depends_on if hasattr(s, "depends_on") else [],
                )
                for s in pipeline_data.stages
            ]

            # Determine output_stage_id - find stages that no other stage depends on
            all_stage_ids = {s.id for s in stages}
            dependent_ids = set()
            for s in stages:
                dependent_ids.update(s.depends_on)
            output_candidates = all_stage_ids - dependent_ids
            output_stage_id = (
                list(output_candidates)[0]
                if output_candidates
                else (stages[-1].id if stages else "output")
            )

            pipeline = GeneratedPipeline(
                name=pipeline_data.name,
                version=getattr(pipeline_data, "version", "1.0.0"),
                description=pipeline_data.description,
                input_schema=pipeline_data.input_schema
                or {"type": "object", "properties": {}},
                stages=stages,
                output_stage_id=output_stage_id,
            )
        else:
            # Synthesized fallback pipeline
            prompt = request.description.strip()
            stages = [
                GeneratedStage(
                    id="generator_1",
                    name="Generate content",
                    component_type="generator",
                    config={
                        "prompt": prompt,
                        "max_tokens": 1000,
                        "temperature": 0.7,
                    },
                    depends_on=[],
                )
            ]
            pipeline = GeneratedPipeline(
                name="Generated Pipeline",
                version="1.0.0",
                description=prompt,
                input_schema={
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Input text to process",
                        }
                    },
                    "required": ["input"],
                },
                stages=stages,
                output_stage_id="generator_1",
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
