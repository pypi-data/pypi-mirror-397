"""
Template API Routes.

Endpoints for managing pipeline templates:
- List templates with filtering
- Get template details
- Instantiate template (create pipeline from template)
- Mark pipeline as template
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from flowmason_studio.models.api import (
    APIError,
    PipelineCreate,
    PipelineDetail,
    PipelineInputSchema,
    PipelineOutputSchema,
    PipelineStage,
)
from flowmason_studio.services.storage import PipelineStorage, get_pipeline_storage

router = APIRouter(prefix="/templates", tags=["templates"])


# Template data directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "data" / "templates"


def _load_template_from_file(template_id: str) -> Optional[Dict[str, Any]]:
    """Load a template definition from JSON file."""
    template_file = TEMPLATES_DIR / f"{template_id}.json"
    if not template_file.exists():
        return None

    with open(template_file, "r") as f:
        result = json.load(f)
        return dict(result) if isinstance(result, dict) else None


def _get_all_file_templates() -> List[Dict[str, Any]]:
    """Load all template definitions from the templates directory."""
    templates: List[Dict[str, Any]] = []

    if not TEMPLATES_DIR.exists():
        return templates

    for template_file in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(template_file, "r") as f:
                template = json.load(f)
                # Ensure the id matches the filename
                template["id"] = template_file.stem
                templates.append(template)
        except (json.JSONDecodeError, IOError):
            # Skip invalid template files
            continue

    return templates


def _template_to_summary(template: Dict[str, Any], source: str = "file") -> Dict[str, Any]:
    """Convert a template dict to a summary format."""
    stages = template.get("stages", [])
    return {
        "id": template.get("id", ""),
        "name": template.get("name", "Untitled Template"),
        "description": template.get("description", ""),
        "version": template.get("version", "1.0.0"),
        "stage_count": len(stages),
        "category": template.get("category", "custom"),
        "tags": template.get("tags", []),
        "difficulty": template.get("difficulty", "beginner"),
        "use_cases": template.get("use_cases", []),
        "source": source,
        "is_template": True,
    }


@router.get(
    "",
    summary="List all templates",
    description="List all available templates, both built-in and user-created."
)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (beginner, intermediate, advanced)"),
    storage: PipelineStorage = Depends(get_pipeline_storage)
) -> Dict[str, Any]:
    """List all available templates."""
    templates = []

    # Load built-in templates from files
    file_templates = _get_all_file_templates()
    for template in file_templates:
        summary = _template_to_summary(template, source="builtin")

        # Apply filters
        if category and summary["category"] != category:
            continue
        if difficulty and summary.get("difficulty") != difficulty:
            continue

        templates.append(summary)

    # Load user-created templates from database
    # Query pipelines where is_template=True
    # We need to filter in storage, but current storage doesn't support is_template filter
    # For now, get all and filter
    db_pipelines, _ = storage.list(limit=1000)
    for pipeline in db_pipelines:
        if not pipeline.is_template:
            continue

        summary = {
            "id": pipeline.id,
            "name": pipeline.name,
            "description": pipeline.description,
            "version": pipeline.version,
            "stage_count": pipeline.stage_count,
            "category": pipeline.category or "custom",
            "tags": pipeline.tags,
            "difficulty": "custom",
            "use_cases": [],
            "source": "user",
            "is_template": True,
            "created_at": pipeline.created_at.isoformat() if pipeline.created_at else None,
            "updated_at": pipeline.updated_at.isoformat() if pipeline.updated_at else None,
        }

        # Apply filters
        if category and summary["category"] != category:
            continue
        if difficulty and difficulty != "custom":
            continue

        templates.append(summary)

    # Group by category
    categories: Dict[str, List[Dict[str, Any]]] = {}
    for template in templates:
        cat = template.get("category", "custom")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(template)

    # Get available categories for filtering
    available_categories = sorted(set(t.get("category", "custom") for t in templates))

    return {
        "templates": templates,
        "total": len(templates),
        "by_category": categories,
        "categories": available_categories,
    }


@router.get(
    "/{template_id}",
    summary="Get template details",
    description="Get detailed information about a specific template.",
    responses={404: {"model": APIError}}
)
async def get_template(
    template_id: str,
    storage: PipelineStorage = Depends(get_pipeline_storage)
) -> Dict[str, Any]:
    """Get a template by ID."""
    # First, try to load from file templates
    file_template = _load_template_from_file(template_id)
    if file_template:
        file_template["id"] = template_id
        file_template["source"] = "builtin"
        file_template["is_template"] = True
        return file_template

    # Then, try to load from database (user-created templates)
    pipeline = storage.get(template_id)
    if pipeline and pipeline.is_template:
        return {
            "id": pipeline.id,
            "name": pipeline.name,
            "description": pipeline.description,
            "version": pipeline.version,
            "category": pipeline.category or "custom",
            "tags": pipeline.tags,
            "stages": [s.model_dump() for s in pipeline.stages],
            "input_schema": pipeline.input_schema.model_dump() if pipeline.input_schema else {},
            "output_schema": pipeline.output_schema.model_dump() if pipeline.output_schema else {},
            "output_stage_id": pipeline.output_stage_id,
            "source": "user",
            "is_template": True,
            "created_at": pipeline.created_at.isoformat() if pipeline.created_at else None,
            "updated_at": pipeline.updated_at.isoformat() if pipeline.updated_at else None,
        }

    raise HTTPException(
        status_code=404,
        detail=f"Template '{template_id}' not found"
    )


@router.post(
    "/{template_id}/instantiate",
    response_model=PipelineDetail,
    status_code=201,
    summary="Create pipeline from template",
    description="Create a new pipeline based on a template.",
    responses={404: {"model": APIError}}
)
async def instantiate_template(
    template_id: str,
    name: Optional[str] = Query(None, description="Name for the new pipeline"),
    storage: PipelineStorage = Depends(get_pipeline_storage)
) -> PipelineDetail:
    """Create a new pipeline from a template."""
    # Load template
    template = None

    # Try file template first
    file_template = _load_template_from_file(template_id)
    if file_template:
        template = file_template
    else:
        # Try database template
        pipeline = storage.get(template_id)
        if pipeline and pipeline.is_template:
            template = {
                "name": pipeline.name,
                "description": pipeline.description,
                "category": pipeline.category,
                "tags": pipeline.tags,
                "stages": [s.model_dump() for s in pipeline.stages],
                "input_schema": pipeline.input_schema.model_dump() if pipeline.input_schema else {},
                "output_schema": pipeline.output_schema.model_dump() if pipeline.output_schema else {},
                "output_stage_id": pipeline.output_stage_id,
            }

    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_id}' not found"
        )

    # Build stages
    stages = []
    for stage_data in template.get("stages", []):
        stages.append(PipelineStage(**stage_data))

    # Build input/output schemas
    input_schema_data = template.get("input_schema", {})
    output_schema_data = template.get("output_schema", {})

    input_schema = PipelineInputSchema(**input_schema_data) if input_schema_data else PipelineInputSchema()
    output_schema = PipelineOutputSchema(**output_schema_data) if output_schema_data else PipelineOutputSchema()

    # Create the pipeline
    pipeline_name = name or f"{template.get('name', 'Template')} (Copy)"

    # Get sample input from template (can be "example_input" or "sample_input")
    sample_input = template.get("sample_input") or template.get("example_input")

    create_data = PipelineCreate(
        name=pipeline_name,
        description=template.get("description", ""),
        input_schema=input_schema,
        output_schema=output_schema,
        stages=stages,
        output_stage_id=template.get("output_stage_id"),
        tags=template.get("tags", []),
        category=template.get("category"),
        is_template=False,  # The instantiated pipeline is NOT a template
        sample_input=sample_input,  # Copy example/sample input from template
    )

    return storage.create(create_data)


@router.get(
    "/categories/list",
    summary="List template categories",
    description="Get a list of all template categories with counts."
)
async def list_categories(
    storage: PipelineStorage = Depends(get_pipeline_storage)
) -> Dict[str, Any]:
    """List all template categories."""
    category_counts: Dict[str, int] = {}

    # Count file templates
    file_templates = _get_all_file_templates()
    for template in file_templates:
        cat = template.get("category", "custom")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Count user templates
    db_pipelines, _ = storage.list(limit=1000)
    for pipeline in db_pipelines:
        if pipeline.is_template:
            cat = pipeline.category or "custom"
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Build response with category metadata
    category_info = {
        "getting-started": {"name": "Getting Started", "icon": "rocket", "order": 1},
        "content": {"name": "Content Creation", "icon": "edit", "order": 2},
        "salesforce": {"name": "Salesforce & CRM", "icon": "cloud", "order": 3},
        "analysis": {"name": "Analysis & Research", "icon": "search", "order": 4},
        "integration": {"name": "Data & Integration", "icon": "link", "order": 5},
        "quality": {"name": "Quality Assurance", "icon": "check", "order": 6},
        "custom": {"name": "Custom", "icon": "box", "order": 99},
    }

    def get_category_order(cat_id: str) -> int:
        info = category_info.get(cat_id, {})
        order = info.get("order", 50)
        return int(order) if isinstance(order, (int, float, str)) else 50

    categories = []
    for cat_id, count in sorted(category_counts.items(), key=lambda x: get_category_order(x[0])):
        info = category_info.get(cat_id, {"name": cat_id.title(), "icon": "box", "order": 50})
        categories.append({
            "id": cat_id,
            "name": info["name"],
            "icon": info["icon"],
            "count": count,
        })

    return {
        "categories": categories,
        "total": sum(category_counts.values()),
    }
