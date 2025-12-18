"""
Prompt Library API Routes.

Manage reusable prompt templates.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from flowmason_studio.services.prompt_storage import (
    PromptTemplate,
    get_prompt_storage,
)

router = APIRouter(prefix="/prompts", tags=["prompts"])


# Request/Response Models
class CreatePromptRequest(BaseModel):
    """Request to create a prompt template."""

    name: str = Field(..., description="Template name")
    content: str = Field(..., description="Prompt content with {{variables}}")
    system_prompt: Optional[str] = Field(
        default=None, description="Optional system prompt"
    )
    description: str = Field(default="", description="Template description")
    category: str = Field(default="", description="Category (e.g., extraction, generation)")
    tags: Optional[List[str]] = Field(default=None, description="Tags for filtering")
    default_values: Optional[Dict[str, str]] = Field(
        default=None, description="Default values for variables"
    )
    recommended_model: Optional[str] = Field(
        default=None, description="Recommended model ID"
    )
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    created_by: Optional[str] = Field(default=None)
    is_public: bool = Field(default=False, description="Make visible to all orgs")


class UpdatePromptRequest(BaseModel):
    """Request to update a prompt template."""

    name: Optional[str] = None
    content: Optional[str] = None
    system_prompt: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    default_values: Optional[Dict[str, str]] = None
    recommended_model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    is_public: Optional[bool] = None


class RenderPromptRequest(BaseModel):
    """Request to render a prompt with variables."""

    variables: Dict[str, str] = Field(
        default_factory=dict, description="Variable values to substitute"
    )


class PromptResponse(BaseModel):
    """Prompt template response."""

    id: str
    name: str
    org_id: str
    content: str
    system_prompt: Optional[str]
    description: str
    category: str
    tags: List[str]
    variables: List[str]
    default_values: Dict[str, str]
    recommended_model: Optional[str]
    temperature: Optional[float]
    max_tokens: Optional[int]
    version: str
    created_at: str
    updated_at: str
    created_by: Optional[str]
    usage_count: int
    last_used_at: Optional[str]
    is_public: bool
    is_featured: bool

    @classmethod
    def from_prompt(cls, p: PromptTemplate) -> "PromptResponse":
        return cls(
            id=p.id,
            name=p.name,
            org_id=p.org_id,
            content=p.content,
            system_prompt=p.system_prompt,
            description=p.description,
            category=p.category,
            tags=p.tags,
            variables=p.variables,
            default_values=p.default_values,
            recommended_model=p.recommended_model,
            temperature=p.temperature,
            max_tokens=p.max_tokens,
            version=p.version,
            created_at=p.created_at,
            updated_at=p.updated_at,
            created_by=p.created_by,
            usage_count=p.usage_count,
            last_used_at=p.last_used_at,
            is_public=p.is_public,
            is_featured=p.is_featured,
        )


class PromptListResponse(BaseModel):
    """List prompts response."""

    prompts: List[PromptResponse]
    total: int
    limit: int
    offset: int


class RenderedPromptResponse(BaseModel):
    """Rendered prompt response."""

    content: str
    system_prompt: Optional[str] = None


class CategoryListResponse(BaseModel):
    """List of categories."""

    categories: List[str]


# Routes
@router.post("", response_model=PromptResponse)
async def create_prompt(
    request: CreatePromptRequest,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """
    Create a new prompt template.

    Use {{variable}} syntax for dynamic content:
    ```
    Summarize the following {{content_type}} in {{language}}:

    {{content}}
    ```
    """
    storage = get_prompt_storage()

    prompt = storage.create(
        name=request.name,
        org_id=org_id,
        content=request.content,
        system_prompt=request.system_prompt,
        description=request.description,
        category=request.category,
        tags=request.tags,
        default_values=request.default_values,
        recommended_model=request.recommended_model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        created_by=request.created_by,
        is_public=request.is_public,
    )

    return PromptResponse.from_prompt(prompt)


@router.get("", response_model=PromptListResponse)
async def list_prompts(
    org_id: str = Query(default="default", description="Organization ID"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    search: Optional[str] = Query(default=None, description="Search in name/description"),
    include_public: bool = Query(default=True, description="Include public prompts"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """List prompt templates."""
    storage = get_prompt_storage()

    prompts, total = storage.list(
        org_id=org_id,
        category=category,
        search=search,
        include_public=include_public,
        limit=limit,
        offset=offset,
    )

    return PromptListResponse(
        prompts=[PromptResponse.from_prompt(p) for p in prompts],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories(
    org_id: str = Query(default="default", description="Organization ID"),
):
    """List all prompt categories."""
    storage = get_prompt_storage()
    categories = storage.list_categories(org_id)
    return CategoryListResponse(categories=categories)


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Get a prompt template by ID."""
    storage = get_prompt_storage()

    prompt = storage.get(prompt_id, org_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return PromptResponse.from_prompt(prompt)


@router.get("/by-name/{name}", response_model=PromptResponse)
async def get_prompt_by_name(
    name: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Get a prompt template by name."""
    storage = get_prompt_storage()

    prompt = storage.get_by_name(name, org_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return PromptResponse.from_prompt(prompt)


@router.patch("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: str,
    request: UpdatePromptRequest,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Update a prompt template."""
    storage = get_prompt_storage()

    # Verify exists
    existing = storage.get(prompt_id, org_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Can only update own prompts
    if existing.org_id != org_id:
        raise HTTPException(status_code=403, detail="Cannot modify prompts from other organizations")

    prompt = storage.update(
        prompt_id=prompt_id,
        org_id=org_id,
        name=request.name,
        content=request.content,
        system_prompt=request.system_prompt,
        description=request.description,
        category=request.category,
        tags=request.tags,
        default_values=request.default_values,
        recommended_model=request.recommended_model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        is_public=request.is_public,
    )

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return PromptResponse.from_prompt(prompt)


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Delete a prompt template."""
    storage = get_prompt_storage()

    # Verify ownership
    existing = storage.get(prompt_id, org_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    if existing.org_id != org_id:
        raise HTTPException(status_code=403, detail="Cannot delete prompts from other organizations")

    deleted = storage.delete(prompt_id, org_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return {"deleted": True, "prompt_id": prompt_id}


@router.post("/{prompt_id}/render", response_model=RenderedPromptResponse)
async def render_prompt(
    prompt_id: str,
    request: RenderPromptRequest,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """
    Render a prompt template with variable substitution.

    Pass variable values to replace {{variable}} placeholders.
    """
    storage = get_prompt_storage()

    result = storage.render(prompt_id, org_id, request.variables)
    if not result:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return RenderedPromptResponse(**result)


@router.post("/{prompt_id}/duplicate", response_model=PromptResponse)
async def duplicate_prompt(
    prompt_id: str,
    name: str = Query(..., description="Name for the duplicate"),
    org_id: str = Query(default="default", description="Organization ID"),
):
    """
    Duplicate a prompt template.

    Creates a copy of the prompt (including public prompts from other orgs).
    """
    storage = get_prompt_storage()

    # Get source prompt
    source = storage.get(prompt_id, org_id)
    if not source:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Create duplicate
    prompt = storage.create(
        name=name,
        org_id=org_id,
        content=source.content,
        system_prompt=source.system_prompt,
        description=f"Copy of {source.name}: {source.description}",
        category=source.category,
        tags=source.tags,
        default_values=source.default_values,
        recommended_model=source.recommended_model,
        temperature=source.temperature,
        max_tokens=source.max_tokens,
        is_public=False,  # Duplicates are private by default
    )

    return PromptResponse.from_prompt(prompt)
