"""
Copilot API Routes for FlowMason Studio.

Provides endpoints for AI-assisted pipeline development.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/copilot", tags=["copilot"])


# Request/Response Models

class SuggestRequest(BaseModel):
    """Request for getting suggestions."""
    request: str = Field(description="User's request/question")
    pipeline: Optional[Dict[str, Any]] = Field(default=None, description="Current pipeline")
    selected_stage_id: Optional[str] = Field(default=None, description="Currently selected stage")
    provider: str = Field(default="anthropic", description="LLM provider")
    model: Optional[str] = Field(default=None, description="Model to use")


class SuggestionItem(BaseModel):
    """A single suggestion."""
    type: str
    stage_id: Optional[str] = None
    description: str
    config: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None


class SuggestResponse(BaseModel):
    """Response with suggestions."""
    suggestions: List[SuggestionItem]
    explanation: str
    raw_response: Optional[str] = None


class ExplainRequest(BaseModel):
    """Request for explaining a pipeline."""
    pipeline: Dict[str, Any] = Field(description="Pipeline to explain")
    stage_id: Optional[str] = Field(default=None, description="Specific stage to explain")
    provider: str = Field(default="anthropic")
    model: Optional[str] = None


class ExplainResponse(BaseModel):
    """Response with explanation."""
    summary: str
    steps: List[str] = []
    data_flow: str = ""


class GenerateRequest(BaseModel):
    """Request for generating a pipeline."""
    description: str = Field(description="Natural language description")
    available_components: Optional[List[str]] = Field(default=None)
    provider: str = Field(default="anthropic")
    model: Optional[str] = None


class GenerateResponse(BaseModel):
    """Response with generated pipeline."""
    pipeline: Optional[Dict[str, Any]] = None
    explanation: str = ""


class DebugRequest(BaseModel):
    """Request for debugging assistance."""
    pipeline: Dict[str, Any] = Field(description="Pipeline with error")
    error_message: str = Field(description="Error message to diagnose")
    execution_state: Optional[Dict[str, Any]] = Field(default=None)
    provider: str = Field(default="anthropic")
    model: Optional[str] = None


class DebugResponse(BaseModel):
    """Response with debug assistance."""
    diagnosis: str
    root_cause: str
    fixes: List[Dict[str, Any]]
    prevention: str


class OptimizeRequest(BaseModel):
    """Request for optimization suggestions."""
    pipeline: Dict[str, Any] = Field(description="Pipeline to optimize")
    provider: str = Field(default="anthropic")
    model: Optional[str] = None


class OptimizeResponse(BaseModel):
    """Response with optimization suggestions."""
    optimizations: List[Dict[str, Any]]
    overall_score: Optional[int] = None
    summary: str = ""


class ChatRequest(BaseModel):
    """Request for chat interaction."""
    message: str = Field(description="User's message")
    pipeline: Optional[Dict[str, Any]] = Field(default=None)
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    provider: str = Field(default="anthropic")
    model: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from chat."""
    response: str


# Endpoints

@router.post("/suggest", response_model=SuggestResponse)
async def suggest(request: SuggestRequest):
    """
    Get AI suggestions for pipeline modifications.

    Analyzes the user's request and current pipeline to provide
    actionable suggestions for improvements or changes.
    """
    try:
        from flowmason_core.copilot import CopilotService, CopilotContext

        # Create context
        context = CopilotContext()
        if request.pipeline:
            # Convert dict to context
            from flowmason_core.copilot.context import PipelineSnapshot, StageSnapshot
            stages = []
            for s in request.pipeline.get("stages", []):
                stages.append(StageSnapshot(
                    id=s.get("id", ""),
                    component_type=s.get("component_type") or s.get("component", "unknown"),
                    name=s.get("name"),
                    input_mapping=s.get("input_mapping", {}),
                    depends_on=s.get("depends_on", []),
                ))
            context.pipeline = PipelineSnapshot(
                name=request.pipeline.get("name", ""),
                version=request.pipeline.get("version", "1.0.0"),
                description=request.pipeline.get("description", ""),
                stages=stages,
                input_schema=request.pipeline.get("input_schema", {}),
                output_schema=request.pipeline.get("output_schema", {}),
                output_stage_id=request.pipeline.get("output_stage_id"),
            )

        if request.selected_stage_id:
            context.select_stage(request.selected_stage_id)

        # Get suggestions
        service = CopilotService(
            provider=request.provider,
            model=request.model,
        )
        result = await service.suggest(request.request, context)

        return SuggestResponse(
            suggestions=[
                SuggestionItem(
                    type=s.type.value,
                    stage_id=s.stage_id,
                    description=s.description,
                    config=s.config,
                    reasoning=s.reasoning,
                )
                for s in result.suggestions
            ],
            explanation=result.explanation,
            raw_response=result.raw_response,
        )

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain", response_model=ExplainResponse)
async def explain(request: ExplainRequest):
    """
    Get an explanation of a pipeline.

    Provides a human-readable explanation of what the pipeline does,
    including step-by-step breakdown and data flow description.
    """
    try:
        from flowmason_core.copilot import CopilotService, CopilotContext
        from flowmason_core.copilot.context import PipelineSnapshot, StageSnapshot

        # Build context
        stages = []
        for s in request.pipeline.get("stages", []):
            stages.append(StageSnapshot(
                id=s.get("id", ""),
                component_type=s.get("component_type") or s.get("component", "unknown"),
                name=s.get("name"),
                input_mapping=s.get("input_mapping", {}),
                depends_on=s.get("depends_on", []),
            ))

        context = CopilotContext(
            pipeline=PipelineSnapshot(
                name=request.pipeline.get("name", ""),
                version=request.pipeline.get("version", "1.0.0"),
                description=request.pipeline.get("description", ""),
                stages=stages,
                input_schema=request.pipeline.get("input_schema", {}),
                output_schema=request.pipeline.get("output_schema", {}),
            )
        )

        if request.stage_id:
            context.select_stage(request.stage_id)

        service = CopilotService(
            provider=request.provider,
            model=request.model,
        )
        result = await service.explain(context)

        return ExplainResponse(
            summary=result.summary,
            steps=result.steps,
            data_flow=result.data_flow,
        )

    except Exception as e:
        logger.error(f"Error explaining pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate a pipeline from natural language description.

    Creates a complete pipeline configuration based on the user's
    description of what they want the pipeline to do.
    """
    try:
        from flowmason_core.copilot import CopilotService

        service = CopilotService(
            provider=request.provider,
            model=request.model,
        )
        result = await service.generate(
            description=request.description,
            available_components=request.available_components,
        )

        return GenerateResponse(
            pipeline=result.pipeline,
            explanation=result.explanation,
        )

    except Exception as e:
        logger.error(f"Error generating pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug", response_model=DebugResponse)
async def debug(request: DebugRequest):
    """
    Get debugging assistance for pipeline errors.

    Analyzes the error and provides diagnosis, fixes, and prevention tips.
    """
    try:
        from flowmason_core.copilot import CopilotService, CopilotContext
        from flowmason_core.copilot.context import PipelineSnapshot, StageSnapshot

        # Build context
        stages = []
        for s in request.pipeline.get("stages", []):
            stages.append(StageSnapshot(
                id=s.get("id", ""),
                component_type=s.get("component_type") or s.get("component", "unknown"),
                input_mapping=s.get("input_mapping", {}),
                depends_on=s.get("depends_on", []),
            ))

        context = CopilotContext(
            pipeline=PipelineSnapshot(
                name=request.pipeline.get("name", ""),
                version=request.pipeline.get("version", "1.0.0"),
                description=request.pipeline.get("description", ""),
                stages=stages,
                input_schema=request.pipeline.get("input_schema", {}),
                output_schema=request.pipeline.get("output_schema", {}),
            )
        )

        # Add execution state if provided
        if request.execution_state:
            context.add_execution(
                run_id=request.execution_state.get("run_id", ""),
                status=request.execution_state.get("status", "failed"),
                failed_stage=request.execution_state.get("failed_stage"),
                error_message=request.error_message,
            )

        service = CopilotService(
            provider=request.provider,
            model=request.model,
        )
        result = await service.debug(context, request.error_message)

        return DebugResponse(
            diagnosis=result.diagnosis,
            root_cause=result.root_cause,
            fixes=result.fixes,
            prevention=result.prevention,
        )

    except Exception as e:
        logger.error(f"Error debugging: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(request: OptimizeRequest):
    """
    Get optimization suggestions for a pipeline.

    Analyzes the pipeline for performance, cost, reliability,
    and maintainability improvements.
    """
    try:
        from flowmason_core.copilot import CopilotService, CopilotContext
        from flowmason_core.copilot.context import PipelineSnapshot, StageSnapshot

        # Build context
        stages = []
        for s in request.pipeline.get("stages", []):
            stages.append(StageSnapshot(
                id=s.get("id", ""),
                component_type=s.get("component_type") or s.get("component", "unknown"),
                input_mapping=s.get("input_mapping", {}),
                depends_on=s.get("depends_on", []),
            ))

        context = CopilotContext(
            pipeline=PipelineSnapshot(
                name=request.pipeline.get("name", ""),
                version=request.pipeline.get("version", "1.0.0"),
                description=request.pipeline.get("description", ""),
                stages=stages,
                input_schema=request.pipeline.get("input_schema", {}),
                output_schema=request.pipeline.get("output_schema", {}),
            )
        )

        service = CopilotService(
            provider=request.provider,
            model=request.model,
        )
        result = await service.optimize(context)

        return OptimizeResponse(
            optimizations=result.get("optimizations", []),
            overall_score=result.get("overall_score"),
            summary=result.get("summary", ""),
        )

    except Exception as e:
        logger.error(f"Error optimizing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Have a conversational interaction with the copilot.

    Supports ongoing dialogue about pipelines, answering questions,
    and providing assistance.
    """
    try:
        from flowmason_core.copilot import CopilotService, CopilotContext
        from flowmason_core.copilot.context import PipelineSnapshot, StageSnapshot

        context = CopilotContext()

        # Add pipeline if provided
        if request.pipeline:
            stages = []
            for s in request.pipeline.get("stages", []):
                stages.append(StageSnapshot(
                    id=s.get("id", ""),
                    component_type=s.get("component_type") or s.get("component", "unknown"),
                    input_mapping=s.get("input_mapping", {}),
                    depends_on=s.get("depends_on", []),
                ))
            context.pipeline = PipelineSnapshot(
                name=request.pipeline.get("name", ""),
                version=request.pipeline.get("version", "1.0.0"),
                description=request.pipeline.get("description", ""),
                stages=stages,
                input_schema=request.pipeline.get("input_schema", {}),
                output_schema=request.pipeline.get("output_schema", {}),
            )

        # Add conversation history
        for msg in request.conversation_history:
            context.add_message(msg.get("role", "user"), msg.get("content", ""))

        service = CopilotService(
            provider=request.provider,
            model=request.model,
        )
        response = await service.chat(request.message, context)

        return ChatResponse(response=response)

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
