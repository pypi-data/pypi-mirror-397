"""
FlowMason MCP API Routes.

Provides HTTP API endpoints that mirror MCP (Model Context Protocol) tools,
enabling AI assistants to interact with FlowMason Studio via HTTP.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from flowmason_studio.api.routes.registry import get_registry
from flowmason_studio.services.storage import get_pipeline_storage

router = APIRouter(prefix="/mcp", tags=["mcp"])


# =============================================================================
# Request/Response Models
# =============================================================================


class ToolCallRequest(BaseModel):
    """Request to execute an MCP tool."""

    tool_name: str = Field(..., description="Name of the tool to execute")
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="Arguments to pass to the tool"
    )


class ToolCallResponse(BaseModel):
    """Response from an MCP tool execution."""

    success: bool
    content: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PipelineSuggestionRequest(BaseModel):
    """Request for pipeline suggestions."""

    task_description: str = Field(..., description="Natural language description of desired pipeline")


class StageSuggestion(BaseModel):
    """A suggested stage for a pipeline."""

    component: str
    purpose: str
    rationale: str


class PipelineSuggestionResponse(BaseModel):
    """Response with pipeline suggestions."""

    name: str
    description: str
    stages: List[StageSuggestion]
    example_pipeline: Optional[Dict[str, Any]] = None


class GenerateStageRequest(BaseModel):
    """Request to generate a stage configuration."""

    stage_type: str = Field(..., description="Component type for the stage")
    purpose: str = Field(..., description="What the stage should accomplish")
    input_source: str = Field(default="input", description="Input source (input or stages.<id>.output)")


class GeneratedStage(BaseModel):
    """A generated stage configuration."""

    id: str
    name: str
    component_type: str
    config: Dict[str, Any]
    depends_on: Optional[List[str]] = None


class ValidatePipelineRequest(BaseModel):
    """Request to validate a pipeline configuration."""

    pipeline_json: str = Field(..., description="Pipeline configuration as JSON string")


class ValidationResult(BaseModel):
    """Result of pipeline validation."""

    valid: bool
    errors: List[str]
    warnings: List[str]


class CreatePipelineRequest(BaseModel):
    """Request to create a new pipeline."""

    name: str = Field(..., description="Pipeline name")
    description: str = Field(..., description="Pipeline description")
    stages: List[Dict[str, Any]] = Field(..., description="List of stage configurations")
    input_schema: Optional[Dict[str, Any]] = None


class CreatePipelineResponse(BaseModel):
    """Response after creating a pipeline."""

    pipeline_id: str
    name: str
    path: Optional[str] = None
    message: str


# =============================================================================
# Tool Endpoints
# =============================================================================


@router.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """
    Execute an MCP tool by name.

    This endpoint provides a unified interface for executing MCP-style tools,
    matching the same interface used by the CLI MCP server.
    """
    tool_handlers = {
        "list_pipelines": handle_list_pipelines,
        "list_components": handle_list_components,
        "get_component": handle_get_component,
        "suggest_pipeline": handle_suggest_pipeline,
        "generate_stage": handle_generate_stage,
        "validate_pipeline_config": handle_validate_pipeline,
        "create_pipeline": handle_create_pipeline,
    }

    handler = tool_handlers.get(request.tool_name)
    if not handler:
        return ToolCallResponse(
            success=False,
            content="",
            error=f"Unknown tool: {request.tool_name}. Available tools: {', '.join(tool_handlers.keys())}",
        )

    try:
        result = await handler(request.arguments)
        return result
    except Exception as e:
        return ToolCallResponse(
            success=False,
            content="",
            error=str(e),
        )


@router.get("/tools", response_model=List[Dict[str, Any]])
async def list_tools() -> List[Dict[str, Any]]:
    """List all available MCP tools."""
    return [
        {
            "name": "list_pipelines",
            "description": "List all available pipelines in the workspace",
            "parameters": {},
        },
        {
            "name": "list_components",
            "description": "List all available FlowMason components",
            "parameters": {},
        },
        {
            "name": "get_component",
            "description": "Get detailed information about a specific component",
            "parameters": {
                "component_type": {"type": "string", "required": True},
            },
        },
        {
            "name": "suggest_pipeline",
            "description": "Get AI-powered suggestions for building a pipeline",
            "parameters": {
                "task_description": {"type": "string", "required": True},
            },
        },
        {
            "name": "generate_stage",
            "description": "Generate a stage configuration for a component type",
            "parameters": {
                "stage_type": {"type": "string", "required": True},
                "purpose": {"type": "string", "required": True},
                "input_source": {"type": "string", "default": "input"},
            },
        },
        {
            "name": "validate_pipeline_config",
            "description": "Validate a pipeline configuration",
            "parameters": {
                "pipeline_json": {"type": "string", "required": True},
            },
        },
        {
            "name": "create_pipeline",
            "description": "Create a new pipeline from a configuration",
            "parameters": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "stages_json": {"type": "string", "required": True},
                "input_schema_json": {"type": "string", "required": False},
            },
        },
    ]


# =============================================================================
# Convenience Endpoints (Direct access to common tools)
# =============================================================================


@router.post("/suggest", response_model=PipelineSuggestionResponse)
async def suggest_pipeline(request: PipelineSuggestionRequest) -> PipelineSuggestionResponse:
    """
    Get pipeline suggestions based on a task description.

    This is a convenience endpoint for the suggest_pipeline tool.
    """
    result = await handle_suggest_pipeline({"task_description": request.task_description})
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    # Parse the result content
    return parse_suggestion_response(result.content, request.task_description)


@router.post("/generate-stage", response_model=GeneratedStage)
async def generate_stage(request: GenerateStageRequest) -> GeneratedStage:
    """
    Generate a stage configuration.

    This is a convenience endpoint for the generate_stage tool.
    """
    result = await handle_generate_stage({
        "stage_type": request.stage_type,
        "purpose": request.purpose,
        "input_source": request.input_source,
    })
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return parse_stage_response(result.content)


@router.post("/validate", response_model=ValidationResult)
async def validate_pipeline(request: ValidatePipelineRequest) -> ValidationResult:
    """
    Validate a pipeline configuration.

    This is a convenience endpoint for the validate_pipeline_config tool.
    """
    result = await handle_validate_pipeline({"pipeline_json": request.pipeline_json})
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return parse_validation_response(result.content)


@router.post("/create", response_model=CreatePipelineResponse)
async def create_pipeline(request: CreatePipelineRequest) -> CreatePipelineResponse:
    """
    Create a new pipeline.

    This is a convenience endpoint for the create_pipeline tool.
    """
    result = await handle_create_pipeline({
        "name": request.name,
        "description": request.description,
        "stages_json": json.dumps(request.stages),
        "input_schema_json": json.dumps(request.input_schema) if request.input_schema else None,
    })
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return CreatePipelineResponse(
        pipeline_id=result.metadata.get("pipeline_id", ""),
        name=request.name,
        path=result.metadata.get("path"),
        message="Pipeline created successfully",
    )


# =============================================================================
# Tool Handlers
# =============================================================================


async def handle_list_pipelines(args: Dict[str, Any]) -> ToolCallResponse:
    """List all pipelines."""
    try:
        storage = get_pipeline_storage()
        pipelines, total = storage.list(limit=100, offset=0)

        if not pipelines:
            return ToolCallResponse(
                success=True,
                content="No pipelines found.",
            )

        content = "Available Pipelines:\n\n"
        for p in pipelines:
            content += f"## {p.name} (v{p.version})\n"
            content += f"Status: {p.status.value}\n"
            content += f"Stages: {p.stage_count}\n"
            content += f"{p.description or 'No description'}\n\n"

        return ToolCallResponse(success=True, content=content)
    except Exception as e:
        return ToolCallResponse(success=False, content="", error=str(e))


async def handle_list_components(args: Dict[str, Any]) -> ToolCallResponse:
    """List all components."""
    try:
        registry = get_registry()
        components = registry.list_components()

        if not components:
            return ToolCallResponse(
                success=True,
                content="No components found.",
            )

        # Group by category
        by_category: Dict[str, List] = {}
        for c in components:
            cat = c.category or "uncategorized"
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(c)

        content = "Available Components:\n\n"
        for cat in sorted(by_category.keys()):
            content += f"## {cat.title()}\n\n"
            for c in by_category[cat]:
                llm = " (requires LLM)" if c.requires_llm else ""
                content += f"- **{c.name}** (`{c.component_type}`){llm}\n"
                content += f"  {c.description or 'No description'}\n"
            content += "\n"

        return ToolCallResponse(success=True, content=content)
    except Exception as e:
        return ToolCallResponse(success=False, content="", error=str(e))


async def handle_get_component(args: Dict[str, Any]) -> ToolCallResponse:
    """Get details about a specific component."""
    component_type = args.get("component_type")
    if not component_type:
        return ToolCallResponse(success=False, content="", error="component_type is required")

    try:
        registry = get_registry()
        component = registry.get(component_type)

        if not component:
            return ToolCallResponse(
                success=False,
                content="",
                error=f"Component '{component_type}' not found",
            )

        content = f"# {component.name}\n\n"
        content += f"**Type:** `{component.component_type}`\n"
        content += f"**Kind:** {component.component_kind or 'operator'}\n"
        content += f"**Category:** {component.category or 'uncategorized'}\n"
        content += f"**Version:** {component.version or '1.0.0'}\n"

        if component.requires_llm:
            content += "**Requires LLM:** Yes\n"

        content += f"\n{component.description or 'No description'}\n"

        if component.input_schema and component.input_schema.get("properties"):
            content += "\n## Configuration\n\n"
            for prop, schema in component.input_schema["properties"].items():
                content += f"- **{prop}** ({schema.get('type', 'any')}): {schema.get('description', '')}\n"

        return ToolCallResponse(success=True, content=content)
    except Exception as e:
        return ToolCallResponse(success=False, content="", error=str(e))


async def handle_suggest_pipeline(args: Dict[str, Any]) -> ToolCallResponse:
    """Suggest pipeline structure based on task description."""
    task = args.get("task_description", "")
    if not task:
        return ToolCallResponse(success=False, content="", error="task_description is required")

    task_lower = task.lower()
    suggestions: List[Dict[str, str]] = []

    # Analyze keywords and suggest components
    if any(kw in task_lower for kw in ["summarize", "summary", "condense"]):
        suggestions.append({
            "component": "generator",
            "purpose": "Generate summary",
            "rationale": "Use LLM to create a summary of the input",
        })

    if any(kw in task_lower for kw in ["filter", "select", "choose", "pick"]):
        suggestions.append({
            "component": "filter",
            "purpose": "Filter items based on criteria",
            "rationale": "Filter data to include only relevant items",
        })

    if any(kw in task_lower for kw in ["transform", "convert", "format", "restructure"]):
        suggestions.append({
            "component": "json_transform",
            "purpose": "Transform data structure",
            "rationale": "Restructure data into desired format",
        })

    if any(kw in task_lower for kw in ["api", "http", "fetch", "request", "call"]):
        suggestions.append({
            "component": "http_request",
            "purpose": "Call external API",
            "rationale": "Make HTTP requests to external services",
        })

    if any(kw in task_lower for kw in ["loop", "iterate", "each", "batch"]):
        suggestions.append({
            "component": "loop",
            "purpose": "Process items in a loop",
            "rationale": "Iterate over items and process each one",
        })

    if any(kw in task_lower for kw in ["validate", "check", "verify", "review"]):
        suggestions.append({
            "component": "critic",
            "purpose": "Validate or review content",
            "rationale": "Use LLM to evaluate and validate content",
        })

    if any(kw in task_lower for kw in ["generate", "create", "write", "produce"]):
        if not any(s["component"] == "generator" for s in suggestions):
            suggestions.append({
                "component": "generator",
                "purpose": "Generate content",
                "rationale": "Use LLM to generate new content",
            })

    # Build response
    content = f"## Suggested Pipeline for: {task[:100]}...\n\n"

    if suggestions:
        content += "### Recommended Components\n\n"
        for i, s in enumerate(suggestions, 1):
            content += f"**{i}. {s['component']}**\n"
            content += f"   Purpose: {s['purpose']}\n"
            content += f"   Rationale: {s['rationale']}\n\n"

        # Build example pipeline
        stages = []
        for i, s in enumerate(suggestions):
            stage = {
                "id": f"{s['component']}-{i + 1}",
                "name": s["purpose"],
                "component_type": s["component"],
                "config": {},
            }
            if i > 0:
                stage["depends_on"] = [f"{suggestions[i - 1]['component']}-{i}"]
            stages.append(stage)

        example = {
            "name": "suggested-pipeline",
            "description": task[:200],
            "version": "1.0.0",
            "stages": stages,
        }

        content += "### Example Pipeline Structure\n\n```json\n"
        content += json.dumps(example, indent=2)
        content += "\n```"
    else:
        content += "Could not automatically suggest components.\n"
        content += "Use list_components to see available options."

    return ToolCallResponse(success=True, content=content)


async def handle_generate_stage(args: Dict[str, Any]) -> ToolCallResponse:
    """Generate a stage configuration."""
    stage_type = args.get("stage_type", "")
    purpose = args.get("purpose", "")
    input_source = args.get("input_source", "input")

    if not stage_type or not purpose:
        return ToolCallResponse(
            success=False,
            content="",
            error="stage_type and purpose are required",
        )

    stage_id = f"{stage_type}-{uuid.uuid4().hex[:6]}"
    config: Dict[str, Any] = {}

    # Generate config based on stage type
    if stage_type == "generator":
        config = {
            "prompt": f"Based on the following input, {purpose}:\n\n{{{{{input_source}}}}}",
            "max_tokens": 1000,
            "temperature": 0.7,
        }
    elif stage_type == "filter":
        config = {
            "items_path": f"{{{{{input_source}.items}}}}",
            "condition": f"# Condition for: {purpose}\nTrue",
        }
    elif stage_type == "json_transform":
        config = {
            "template": {
                "result": f"{{{{{input_source}}}}}",
                "metadata": {"purpose": purpose},
            },
        }
    elif stage_type == "http_request":
        config = {
            "url": "https://api.example.com/endpoint",
            "method": "POST",
            "body": f"{{{{{input_source}}}}}",
        }
    elif stage_type == "loop":
        config = {
            "items_path": f"{{{{{input_source}.items}}}}",
            "max_iterations": 10,
        }
    elif stage_type == "critic":
        config = {
            "prompt": f"Evaluate the following for: {purpose}\n\nContent: {{{{{input_source}}}}}",
            "criteria": ["accuracy", "relevance", "quality"],
        }
    else:
        config = {
            "input": f"{{{{{input_source}}}}}",
            "purpose": purpose,
        }

    stage: Dict[str, Any] = {
        "id": stage_id,
        "name": purpose[:50],
        "component_type": stage_type,
        "config": config,
    }

    # Add depends_on if input is from another stage
    if input_source != "input" and input_source.startswith("stages."):
        dep_stage_id = input_source.replace("stages.", "").split(".")[0]
        stage["depends_on"] = [dep_stage_id]

    content = f"Generated stage configuration:\n\n```json\n{json.dumps(stage, indent=2)}\n```"
    return ToolCallResponse(success=True, content=content)


async def handle_validate_pipeline(args: Dict[str, Any]) -> ToolCallResponse:
    """Validate a pipeline configuration."""
    pipeline_json = args.get("pipeline_json", "")
    if not pipeline_json:
        return ToolCallResponse(success=False, content="", error="pipeline_json is required")

    try:
        pipeline = json.loads(pipeline_json)
    except json.JSONDecodeError as e:
        return ToolCallResponse(success=False, content="", error=f"Invalid JSON: {e}")

    errors: List[str] = []
    warnings: List[str] = []

    # Validate required fields
    if not pipeline.get("name"):
        errors.append("Missing required field: 'name'")

    if not pipeline.get("stages"):
        errors.append("Missing required field: 'stages'")
    elif not isinstance(pipeline["stages"], list):
        errors.append("'stages' must be an array")
    elif len(pipeline["stages"]) == 0:
        errors.append("Pipeline must have at least one stage")
    else:
        stage_ids = set()
        for i, stage in enumerate(pipeline["stages"]):
            if not stage.get("id"):
                errors.append(f"Stage {i}: missing 'id' field")
            else:
                if stage["id"] in stage_ids:
                    errors.append(f"Stage {i}: duplicate stage ID '{stage['id']}'")
                stage_ids.add(stage["id"])

            if not stage.get("component_type"):
                errors.append(f"Stage {i}: missing 'component_type' field")

            if not stage.get("name"):
                warnings.append(f"Stage '{stage.get('id', i)}': consider adding 'name'")

    if not pipeline.get("description"):
        warnings.append("Consider adding a 'description' field")

    if not pipeline.get("version"):
        warnings.append("Consider adding a 'version' field")

    # Build response
    content = "## Validation Failed\n\n" if errors else "## Validation Passed\n\n"

    if errors:
        content += "**Errors:**\n"
        for err in errors:
            content += f"- {err}\n"

    if warnings:
        content += "\n**Warnings:**\n"
        for warn in warnings:
            content += f"- {warn}\n"

    return ToolCallResponse(success=True, content=content)


async def handle_create_pipeline(args: Dict[str, Any]) -> ToolCallResponse:
    """Create a new pipeline."""
    name = args.get("name", "")
    description = args.get("description", "")
    stages_json = args.get("stages_json", "")
    input_schema_json = args.get("input_schema_json")

    if not name or not stages_json:
        return ToolCallResponse(
            success=False,
            content="",
            error="name and stages_json are required",
        )

    try:
        stages = json.loads(stages_json)
    except json.JSONDecodeError as e:
        return ToolCallResponse(success=False, content="", error=f"Invalid stages JSON: {e}")

    input_schema = None
    if input_schema_json:
        try:
            input_schema = json.loads(input_schema_json)
        except json.JSONDecodeError as e:
            return ToolCallResponse(success=False, content="", error=f"Invalid input_schema JSON: {e}")

    pipeline = {
        "name": name,
        "version": "1.0.0",
        "description": description,
        "stages": stages,
        "input_schema": input_schema,
    }

    try:
        from flowmason_studio.models.api import PipelineCreate, PipelineInputSchema, PipelineStage

        # Convert stage dicts to PipelineStage models
        stage_models = [PipelineStage(**s) if isinstance(s, dict) else s for s in stages]

        # Convert input_schema dict to model if provided
        input_schema_model = PipelineInputSchema(**input_schema) if input_schema else PipelineInputSchema()

        pipeline_create = PipelineCreate(
            name=name,
            description=description,
            stages=stage_models,
            input_schema=input_schema_model,
        )

        storage = get_pipeline_storage()
        created = storage.create(pipeline_create)

        content = f"""Pipeline created successfully!

**ID:** {created.id}
**Name:** {name}
**Stages:** {len(stages)}

You can now run this pipeline from the Studio UI or CLI.
"""
        return ToolCallResponse(
            success=True,
            content=content,
            metadata={"pipeline_id": created.id},
        )
    except Exception as exc:
        return ToolCallResponse(success=False, content="", error=str(exc))


# =============================================================================
# Response Parsers
# =============================================================================


def parse_suggestion_response(content: str, task: str) -> PipelineSuggestionResponse:
    """Parse suggestion response content into structured format."""
    stages: List[StageSuggestion] = []

    # Parse stages from content
    import re

    pattern = r"\*\*\d+\.\s+(\w+)\*\*\s*\n\s*Purpose:\s*(.+?)\n\s*Rationale:\s*(.+?)(?=\n\n|\*\*\d+|$)"
    matches = re.findall(pattern, content, re.DOTALL)
    for match in matches:
        stages.append(StageSuggestion(
            component=match[0],
            purpose=match[1].strip(),
            rationale=match[2].strip(),
        ))

    # Try to extract example pipeline
    example_pipeline = None
    json_match = re.search(r"```json\n([\s\S]+?)\n```", content)
    if json_match:
        try:
            example_pipeline = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    return PipelineSuggestionResponse(
        name="suggested-pipeline",
        description=task[:200],
        stages=stages,
        example_pipeline=example_pipeline,
    )


def parse_stage_response(content: str) -> GeneratedStage:
    """Parse generated stage response into structured format."""
    import re

    json_match = re.search(r"```json\n([\s\S]+?)\n```", content)
    if not json_match:
        raise HTTPException(status_code=500, detail="Failed to parse stage response")

    try:
        stage_data = json.loads(json_match.group(1))
        return GeneratedStage(**stage_data)
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse stage: {e}")


def parse_validation_response(content: str) -> ValidationResult:
    """Parse validation response into structured format."""
    valid = "Validation Passed" in content
    errors: List[str] = []
    warnings: List[str] = []

    import re

    # Parse errors
    error_section = re.search(r"\*\*Errors:\*\*\n([\s\S]*?)(?=\n\*\*|$)", content)
    if error_section:
        error_matches = re.findall(r"^-\s*(.+)$", error_section.group(1), re.MULTILINE)
        errors = list(error_matches)

    # Parse warnings
    warning_section = re.search(r"\*\*Warnings:\*\*\n([\s\S]*?)(?=\n\*\*|$)", content)
    if warning_section:
        warning_matches = re.findall(r"^-\s*(.+)$", warning_section.group(1), re.MULTILINE)
        warnings = list(warning_matches)

    return ValidationResult(valid=valid, errors=errors, warnings=warnings)
