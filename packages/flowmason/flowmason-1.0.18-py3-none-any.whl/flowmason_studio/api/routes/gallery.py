"""
Template Gallery API Routes.

Endpoints for browsing and using pipeline templates.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...models.api import PipelineCreate, PipelineStage
from ...services.storage import get_pipeline_storage
from ...services.template_gallery import PipelineTemplate, get_template_gallery

router = APIRouter(prefix="/gallery", tags=["gallery"])


# Response Models
class TemplateListItem(BaseModel):
    """Summary of a template for listing."""
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    difficulty: str
    estimated_time: str
    use_case: str


class TemplateDetail(BaseModel):
    """Full template details."""
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    difficulty: str
    estimated_time: str
    use_case: str
    pipeline: dict
    sample_input: dict
    documentation: str
    prerequisites: List[str]


class CreateFromTemplateRequest(BaseModel):
    """Request to create a pipeline from a template."""
    name: Optional[str] = Field(None, description="Custom name for the pipeline")
    description: Optional[str] = Field(None, description="Custom description")


class CreateFromTemplateResponse(BaseModel):
    """Response after creating a pipeline from a template."""
    pipeline_id: str
    name: str
    message: str


class CategoryStats(BaseModel):
    """Category with template count."""
    name: str
    count: int


def _template_to_list_item(t: PipelineTemplate) -> TemplateListItem:
    """Convert template to list item."""
    return TemplateListItem(
        id=t.id,
        name=t.name,
        description=t.description,
        category=t.category,
        tags=t.tags,
        difficulty=t.difficulty,
        estimated_time=t.estimated_time,
        use_case=t.use_case,
    )


def _template_to_detail(t: PipelineTemplate) -> TemplateDetail:
    """Convert template to full detail."""
    return TemplateDetail(
        id=t.id,
        name=t.name,
        description=t.description,
        category=t.category,
        tags=t.tags,
        difficulty=t.difficulty,
        estimated_time=t.estimated_time,
        use_case=t.use_case,
        pipeline=t.pipeline,
        sample_input=t.sample_input,
        documentation=t.documentation,
        prerequisites=t.prerequisites,
    )


@router.get("/templates", response_model=List[TemplateListItem])
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    search: Optional[str] = Query(None, description="Search in name, description, tags"),
):
    """
    List available pipeline templates.

    Templates are starter pipelines for common use cases. Use filters
    to narrow down the list, or search by keyword.
    """
    gallery = get_template_gallery()
    templates = gallery.list_templates(
        category=category,
        difficulty=difficulty,
        search=search,
    )
    return [_template_to_list_item(t) for t in templates]


@router.get("/templates/categories", response_model=List[CategoryStats])
async def list_categories():
    """
    List all template categories with counts.

    Returns categories like 'content', 'data', 'analysis', etc.
    """
    gallery = get_template_gallery()
    templates = gallery.list_templates()

    category_counts = {}
    for t in templates:
        category_counts[t.category] = category_counts.get(t.category, 0) + 1

    return [
        CategoryStats(name=name, count=count)
        for name, count in sorted(category_counts.items())
    ]


@router.get("/templates/tags", response_model=List[str])
async def list_tags():
    """
    List all template tags.

    Tags are keywords like 'writing', 'api', 'code-review', etc.
    """
    gallery = get_template_gallery()
    return gallery.list_tags()


@router.get("/templates/{template_id}", response_model=TemplateDetail)
async def get_template(template_id: str):
    """
    Get full details of a template.

    Includes the pipeline definition, sample input, and documentation.
    """
    gallery = get_template_gallery()
    template = gallery.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return _template_to_detail(template)


@router.post("/templates/{template_id}/create-pipeline", response_model=CreateFromTemplateResponse)
async def create_pipeline_from_template(
    template_id: str,
    request: CreateFromTemplateRequest = CreateFromTemplateRequest(),  # type: ignore[call-arg]
):
    """
    Create a new pipeline from a template.

    This copies the template's pipeline definition into your pipelines,
    allowing you to customize it.
    """
    gallery = get_template_gallery()
    template = gallery.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Create pipeline from template
    name = request.name or template.pipeline.get("name", template.name)
    description = request.description or template.pipeline.get("description", template.description)

    # Convert template stages to PipelineStage objects
    template_stages = template.pipeline.get("stages", [])
    stages = [
        PipelineStage(
            id=s.get("id", f"stage_{i}"),
            name=s.get("name", s.get("id", f"Stage {i}")),
            component_type=s.get("component_type", s.get("component", "unknown")),
            config=s.get("config", {}),
            depends_on=s.get("depends_on", []),
        )
        for i, s in enumerate(template_stages)
    ]

    # Determine output stage
    output_stage_id = template.pipeline.get("output_stage_id")
    if not output_stage_id and stages:
        output_stage_id = stages[-1].id

    # Create pipeline using proper API
    pipeline_create = PipelineCreate(
        name=name,
        description=description,
        stages=stages,
        input_schema=template.pipeline.get("input_schema"),  # type: ignore[arg-type]
        output_schema=template.pipeline.get("output_schema"),  # type: ignore[arg-type]
        output_stage_id=output_stage_id,
        tags=[f"template:{template_id}"],
    )

    # Save to storage
    storage = get_pipeline_storage()
    created_pipeline = storage.create(pipeline_create)

    return CreateFromTemplateResponse(
        pipeline_id=created_pipeline.id,
        name=created_pipeline.name,
        message=f"Pipeline created from template '{template.name}'",
    )


@router.get("/templates/{template_id}/preview")
async def preview_template(template_id: str):
    """
    Preview a template's pipeline structure.

    Returns a simplified view of the pipeline stages and flow,
    useful for understanding what the template does before using it.
    """
    gallery = get_template_gallery()
    template = gallery.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    stages = template.pipeline.get("stages", [])

    return {
        "name": template.name,
        "description": template.description,
        "stages": [
            {
                "id": s.get("id"),
                "component_type": s.get("component_type"),
                "depends_on": s.get("depends_on", []),
            }
            for s in stages
        ],
        "input_schema": template.pipeline.get("input_schema"),
        "sample_input": template.sample_input,
    }
