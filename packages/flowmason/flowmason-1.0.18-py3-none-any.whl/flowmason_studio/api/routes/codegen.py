"""
Code Generation API Routes.

Provides HTTP API for generating standalone code from pipelines.
"""

import io
import zipfile
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from flowmason_studio.models.codegen import (
    CodeGenOptions,
    CodeGenResult,
    GenerateCodeRequest,
    GenerateCodeResponse,
    ListTemplatesResponse,
    OutputFormat,
    PreviewCodeRequest,
    PreviewCodeResponse,
    TargetLanguage,
    TargetPlatform,
)
from flowmason_studio.services.codegen_python import get_python_code_generator
from flowmason_studio.services.codegen_typescript import get_typescript_code_generator
from flowmason_studio.services.codegen_go import get_go_code_generator
from flowmason_studio.services.codegen_apex import get_apex_code_generator
from flowmason_studio.services.storage import get_pipeline_storage

router = APIRouter(prefix="/codegen", tags=["codegen"])


@router.post("/generate", response_model=GenerateCodeResponse)
async def generate_code(request: GenerateCodeRequest) -> GenerateCodeResponse:
    """
    Generate standalone code from a pipeline.

    Converts a FlowMason pipeline into runnable code for the specified
    language and platform.
    """
    storage = get_pipeline_storage()
    pipeline = storage.get_pipeline(request.pipeline_id)

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Get appropriate generator
    if request.options.language == TargetLanguage.PYTHON:
        generator = get_python_code_generator()
    elif request.options.language in (TargetLanguage.TYPESCRIPT, TargetLanguage.NODEJS):
        generator = get_typescript_code_generator()
    elif request.options.language == TargetLanguage.GO:
        generator = get_go_code_generator()
    elif request.options.language == TargetLanguage.APEX:
        generator = get_apex_code_generator()
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Language {request.options.language} not yet supported"
        )

    # Generate code
    result = generator.generate(pipeline, request.options)

    return GenerateCodeResponse(
        result=result,
        download_url=f"/api/v1/codegen/download/{result.id}",
    )


@router.post("/preview", response_model=PreviewCodeResponse)
async def preview_code(request: PreviewCodeRequest) -> PreviewCodeResponse:
    """
    Preview generated code without saving.

    Returns a preview of what the generated code would look like.
    """
    storage = get_pipeline_storage()
    pipeline = storage.get_pipeline(request.pipeline_id)

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Get generator
    if request.options.language == TargetLanguage.PYTHON:
        generator = get_python_code_generator()
    elif request.options.language in (TargetLanguage.TYPESCRIPT, TargetLanguage.NODEJS):
        generator = get_typescript_code_generator()
    elif request.options.language == TargetLanguage.GO:
        generator = get_go_code_generator()
    elif request.options.language == TargetLanguage.APEX:
        generator = get_apex_code_generator()
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Language {request.options.language} not yet supported"
        )

    # Generate
    result = generator.generate(pipeline, request.options)

    # Filter to specific file if requested
    files = result.files
    if request.file_path:
        files = [f for f in files if f.path == request.file_path]

    return PreviewCodeResponse(
        files=files,
        entry_point=result.entry_point,
        estimated_lines=result.total_lines,
    )


@router.get("/download/{generation_id}")
async def download_code(
    generation_id: str,
    pipeline_id: str = Query(..., description="Pipeline ID"),
    language: TargetLanguage = Query(default=TargetLanguage.PYTHON),
    platform: TargetPlatform = Query(default=TargetPlatform.STANDALONE),
) -> StreamingResponse:
    """
    Download generated code as a ZIP file.
    """
    storage = get_pipeline_storage()
    pipeline = storage.get_pipeline(pipeline_id)

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Generate code
    options = CodeGenOptions(
        language=language,
        platform=platform,
        output_format=OutputFormat.PACKAGE,
    )

    if language == TargetLanguage.PYTHON:
        generator = get_python_code_generator()
    elif language in (TargetLanguage.TYPESCRIPT, TargetLanguage.NODEJS):
        generator = get_typescript_code_generator()
    elif language == TargetLanguage.GO:
        generator = get_go_code_generator()
    elif language == TargetLanguage.APEX:
        generator = get_apex_code_generator()
    else:
        raise HTTPException(status_code=400, detail="Unsupported language")

    result = generator.generate(pipeline, options)

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in result.files:
            zf.writestr(file.path, file.content)

    zip_buffer.seek(0)

    pipeline_name = pipeline.get("name", "pipeline").replace(" ", "_").lower()
    filename = f"{pipeline_name}_generated.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/languages")
async def list_languages() -> dict:
    """
    List supported target languages.
    """
    return {
        "languages": [
            {
                "id": "python",
                "name": "Python",
                "description": "Generate Python 3.9+ code",
                "supported": True,
                "platforms": ["standalone", "aws_lambda", "docker", "azure_functions", "firebase_functions"],
            },
            {
                "id": "typescript",
                "name": "TypeScript",
                "description": "Generate TypeScript/Node.js code",
                "supported": True,
                "platforms": ["standalone", "cloudflare_workers", "aws_lambda", "firebase_functions"],
            },
            {
                "id": "nodejs",
                "name": "Node.js",
                "description": "Generate JavaScript/Node.js code",
                "supported": True,
                "platforms": ["standalone", "cloudflare_workers", "aws_lambda", "firebase_functions"],
            },
            {
                "id": "go",
                "name": "Go",
                "description": "Generate Go 1.21+ code",
                "supported": True,
                "platforms": ["standalone", "aws_lambda", "docker"],
            },
            {
                "id": "apex",
                "name": "Salesforce Apex",
                "description": "Generate Salesforce Apex classes for Flow integration",
                "supported": True,
                "platforms": ["salesforce"],
            },
        ]
    }


@router.get("/platforms")
async def list_platforms() -> dict:
    """
    List supported deployment platforms.
    """
    return {
        "platforms": [
            {
                "id": "standalone",
                "name": "Standalone",
                "description": "Generate a standalone runnable application",
                "languages": ["python", "typescript", "nodejs", "go"],
            },
            {
                "id": "aws_lambda",
                "name": "AWS Lambda",
                "description": "Generate AWS Lambda function with SAM template",
                "languages": ["python", "typescript", "nodejs", "go"],
            },
            {
                "id": "cloudflare_workers",
                "name": "Cloudflare Workers",
                "description": "Generate Cloudflare Worker with wrangler config",
                "languages": ["typescript", "nodejs"],
            },
            {
                "id": "azure_functions",
                "name": "Azure Functions",
                "description": "Generate Azure Function with deployment config",
                "languages": ["python", "nodejs"],
            },
            {
                "id": "firebase_functions",
                "name": "Firebase Functions",
                "description": "Generate Google Firebase Cloud Functions with firebase.json config",
                "languages": ["python", "typescript", "nodejs"],
            },
            {
                "id": "docker",
                "name": "Docker",
                "description": "Generate Dockerfile and docker-compose.yml",
                "languages": ["python", "nodejs", "go"],
            },
            {
                "id": "salesforce",
                "name": "Salesforce",
                "description": "Generate Salesforce Apex classes with Flow integration",
                "languages": ["apex"],
            },
        ]
    }


@router.get("/templates")
async def list_templates() -> dict:
    """
    List available code generation templates.
    """
    return {
        "templates": {
            "generator": {
                "description": "AI text generation (OpenAI, Anthropic)",
                "providers": ["openai", "anthropic", "google"],
            },
            "http_request": {
                "description": "HTTP API requests",
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            },
            "json_transform": {
                "description": "JSON data transformation",
                "features": ["field_mapping", "expressions", "jq_style"],
            },
            "filter": {
                "description": "Conditional filtering",
                "features": ["boolean_conditions", "comparison_operators"],
            },
            "variable_set": {
                "description": "Variable assignment",
                "features": ["template_strings", "static_values"],
            },
            "logger": {
                "description": "Logging output",
                "levels": ["debug", "info", "warning", "error"],
            },
        }
    }


@router.post("/validate")
async def validate_for_codegen(pipeline_id: str) -> dict:
    """
    Validate if a pipeline can be converted to code.

    Checks for:
    - Unsupported component types
    - Dynamic features that can't be statically compiled
    - Missing configurations
    """
    storage = get_pipeline_storage()
    pipeline = storage.get_pipeline(pipeline_id)

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    issues = []
    warnings = []

    stages = pipeline.get("stages", [])

    # Check each stage
    supported_components = {
        "generator", "http_request", "json_transform", "filter",
        "variable_set", "logger", "selector", "loop", "foreach",
    }

    for stage in stages:
        component_type = stage.get("component_type", "unknown")
        stage_id = stage.get("id", "unknown")

        if component_type not in supported_components:
            issues.append({
                "stage": stage_id,
                "issue": f"Component type '{component_type}' not supported for code generation",
                "severity": "error",
            })

        # Check for dynamic features
        config = stage.get("config", {})
        if config.get("dynamic_provider"):
            warnings.append({
                "stage": stage_id,
                "issue": "Dynamic provider selection will use default provider in generated code",
                "severity": "warning",
            })

    # Check for control flow
    control_flow = pipeline.get("control_flow", {})
    if control_flow.get("branches"):
        warnings.append({
            "issue": "Complex branching may require manual adjustment in generated code",
            "severity": "warning",
        })

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "supported_stages": len(stages) - len(issues),
        "total_stages": len(stages),
    }
