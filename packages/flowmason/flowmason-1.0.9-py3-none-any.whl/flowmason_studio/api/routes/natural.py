"""
Natural Language Trigger API Routes for FlowMason Studio.

Provides endpoints for triggering pipelines using natural language commands.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from flowmason_studio.api.routes.registry import get_registry
from flowmason_studio.services.storage import get_pipeline_storage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/natural", tags=["natural-language"])


# Request/Response Models

class ParseRequest(BaseModel):
    """Request to parse a natural language command."""
    command: str = Field(description="Natural language command")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence threshold")
    use_llm: bool = Field(default=False, description="Use LLM for better accuracy")


class IntentInfo(BaseModel):
    """Information about parsed intent."""
    type: str
    action: str
    target: Optional[str] = None
    confidence: float


class MatchInfo(BaseModel):
    """Information about a pipeline match."""
    pipeline_name: str
    confidence: float
    reasoning: str = ""
    matched_pattern: Optional[str] = None


class ParseResponse(BaseModel):
    """Response from parsing a natural language command."""
    success: bool
    pipeline_name: Optional[str] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    intent: Optional[IntentInfo] = None
    match: Optional[MatchInfo] = None
    error: Optional[str] = None
    alternatives: List[MatchInfo] = Field(default_factory=list)


class RunNaturalRequest(BaseModel):
    """Request to run a pipeline using natural language."""
    command: str = Field(description="Natural language command")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    additional_inputs: Optional[Dict[str, Any]] = Field(default=None, description="Additional inputs to merge")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    use_llm: bool = Field(default=False)


class RunNaturalResponse(BaseModel):
    """Response from running a pipeline with natural language."""
    success: bool
    run_id: Optional[str] = None
    pipeline_name: Optional[str] = None
    inputs_used: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    error: Optional[str] = None


class SuggestRequest(BaseModel):
    """Request for pipeline suggestions."""
    query: str = Field(description="Partial command or query")
    max_suggestions: int = Field(default=5, ge=1, le=20)


class SuggestionItem(BaseModel):
    """A single pipeline suggestion."""
    name: str
    description: str = ""
    confidence: float


class SuggestResponse(BaseModel):
    """Response with pipeline suggestions."""
    suggestions: List[SuggestionItem]


# Endpoints

@router.post("/parse", response_model=ParseResponse)
async def parse_command(request: ParseRequest):
    """
    Parse a natural language command and match to a pipeline.

    Does not execute the pipeline, just returns the match result.
    """
    try:
        from flowmason_core.nlp import NLPTriggerService

        # Load pipelines
        pipelines = await _load_pipelines()

        if not pipelines:
            return ParseResponse(
                success=False,
                error="No pipelines available",
            )

        # Create service
        llm_client = _get_llm_client() if request.use_llm else None
        service = NLPTriggerService(
            pipelines=pipelines,
            use_llm=request.use_llm and llm_client is not None,
            llm_client=llm_client,
        )

        # Parse command
        result = service.parse_sync(
            command=request.command,
            context=request.context,
            threshold=request.threshold,
        )

        # Build response
        intent_info = None
        if result.intent:
            intent_info = IntentInfo(
                type=result.intent.type.value,
                action=result.intent.action,
                target=result.intent.target,
                confidence=result.intent.confidence,
            )

        match_info = None
        if result.match:
            match_info = MatchInfo(
                pipeline_name=result.match.pipeline_name,
                confidence=result.match.confidence,
                reasoning=result.match.reasoning,
                matched_pattern=result.match.matched_pattern,
            )

        alternatives = []
        for alt in result.alternatives:
            alternatives.append(MatchInfo(
                pipeline_name=alt.pipeline_name,
                confidence=alt.confidence,
                reasoning=alt.reasoning,
            ))

        return ParseResponse(
            success=result.success,
            pipeline_name=result.pipeline_name,
            inputs=result.inputs,
            confidence=result.confidence,
            intent=intent_info,
            match=match_info,
            error=result.error,
            alternatives=alternatives,
        )

    except Exception as e:
        logger.error(f"Error parsing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run", response_model=RunNaturalResponse)
async def run_natural(request: RunNaturalRequest):
    """
    Run a pipeline using natural language command.

    Parses the command, matches to a pipeline, and executes it.
    """
    try:
        from flowmason_core.nlp import NLPTriggerService

        from flowmason_studio.services.execution_controller import get_execution_controller

        # Load pipelines
        pipelines = await _load_pipelines()

        if not pipelines:
            return RunNaturalResponse(
                success=False,
                error="No pipelines available",
            )

        # Create service
        llm_client = _get_llm_client() if request.use_llm else None
        service = NLPTriggerService(
            pipelines=pipelines,
            use_llm=request.use_llm and llm_client is not None,
            llm_client=llm_client,
        )

        # Parse command
        result = service.parse_sync(
            command=request.command,
            context=request.context,
            threshold=request.threshold,
        )

        if not result.success:
            return RunNaturalResponse(
                success=False,
                error=result.error,
            )

        # Merge additional inputs
        inputs = result.inputs.copy()
        if request.additional_inputs:
            inputs.update(request.additional_inputs)

        # Get pipeline storage to find full pipeline config
        storage = get_pipeline_storage()
        pipeline_data = None

        # Try to find pipeline by name
        all_pipelines = storage.list_pipelines()
        for p in all_pipelines:
            if p.get("name") == result.pipeline_name:
                pipeline_data = storage.get_pipeline(p.get("id"))
                break

        if not pipeline_data:
            # Use the in-memory pipeline
            pipeline_data = pipelines.get(result.pipeline_name)

        if not pipeline_data:
            return RunNaturalResponse(
                success=False,
                error=f"Pipeline '{result.pipeline_name}' not found",
            )

        # Execute pipeline
        controller = get_execution_controller()
        run_result = await controller.execute_pipeline(
            pipeline=pipeline_data,
            inputs=inputs,
            run_source="natural_language",
        )

        return RunNaturalResponse(
            success=run_result.get("status") in ("success", "running"),
            run_id=run_result.get("run_id"),
            pipeline_name=result.pipeline_name,
            inputs_used=inputs,
            confidence=result.confidence,
            error=run_result.get("error"),
        )

    except Exception as e:
        logger.error(f"Error running natural language command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_pipelines(request: SuggestRequest):
    """
    Get pipeline suggestions based on a partial query.

    Useful for autocomplete in UI.
    """
    try:
        from flowmason_core.nlp import NLPTriggerService

        pipelines = await _load_pipelines()

        if not pipelines:
            return SuggestResponse(suggestions=[])

        service = NLPTriggerService(pipelines=pipelines)
        suggestions = service.suggest_pipelines(
            request.query,
            max_suggestions=request.max_suggestions,
        )

        return SuggestResponse(
            suggestions=[
                SuggestionItem(
                    name=s["name"],
                    description=s.get("description", ""),
                    confidence=s["confidence"],
                )
                for s in suggestions
            ]
        )

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/examples")
async def get_examples():
    """
    Get example natural language commands for available pipelines.

    Returns examples based on registered pipelines.
    """
    try:
        pipelines = await _load_pipelines()

        examples = []
        for name, pipeline in pipelines.items():
            desc = ""
            if isinstance(pipeline, dict):
                desc = pipeline.get("description", "")

            # Generate example commands
            example_commands = [
                f"run the {name} pipeline",
                f"execute {name}",
            ]

            # Add trigger-based examples
            triggers = pipeline.get("triggers", {}) if isinstance(pipeline, dict) else {}
            nl_config = triggers.get("natural_language", {})
            if nl_config.get("patterns"):
                example_commands.extend(nl_config["patterns"][:2])

            examples.append({
                "pipeline": name,
                "description": desc,
                "examples": example_commands[:3],
            })

        return {"examples": examples}

    except Exception as e:
        logger.error(f"Error getting examples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _load_pipelines() -> Dict[str, Any]:
    """Load all available pipelines."""
    pipelines: Dict[str, Any] = {}

    # Load from storage
    try:
        storage = get_pipeline_storage()
        stored_pipelines = storage.list_pipelines()
        for p in stored_pipelines:
            full_pipeline = storage.get_pipeline(p.get("id"))
            if full_pipeline:
                name = full_pipeline.get("name", p.get("id"))
                pipelines[name] = full_pipeline
    except Exception as e:
        logger.warning(f"Could not load pipelines from storage: {e}")

    # Also include any from registry components
    try:
        registry = get_registry()
        if registry:
            # Components aren't pipelines, but we could add pipeline templates here
            pass
    except Exception:
        pass

    return pipelines


def _get_llm_client() -> Any:
    """Get LLM client for enhanced matching."""
    import os

    # Try Anthropic first
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            return anthropic.Anthropic(api_key=api_key)
        except ImportError:
            pass

    # Try OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            return openai.OpenAI(api_key=api_key)
        except ImportError:
            pass

    return None
