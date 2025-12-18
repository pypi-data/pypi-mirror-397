"""
Component Visual API Routes.

Provides HTTP API for rich visual component representations.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from flowmason_studio.api.routes.registry import get_registry
from flowmason_studio.models.component_visual import (
    ComponentCategory,
    ComponentGroup,
    ComponentPalette,
    ComponentVisual,
    ConnectionStyle,
    PipelineVisual,
    UpdateFavoritesRequest,
)
from flowmason_studio.services.component_visual_service import get_component_visual_service
from flowmason_studio.services.storage import get_pipeline_storage

router = APIRouter(prefix="/component-visual", tags=["component-visual"])


# =============================================================================
# Component Visuals
# =============================================================================


@router.get("/components", response_model=List[ComponentVisual])
async def list_component_visuals(
    category: Optional[ComponentCategory] = Query(None, description="Filter by category"),
    include_preview: bool = Query(True, description="Include preview snippets"),
    include_capabilities: bool = Query(True, description="Include capability list"),
) -> List[ComponentVisual]:
    """
    Get visual representations for all available components.

    Returns rich visual metadata including themes, icons, ports, and badges
    for building visual pipeline editors.
    """
    service = get_component_visual_service()
    registry = get_registry()

    visuals = []

    # Get components from registry if available
    if registry:
        for component_type, component_info in registry.get_all_components().items():
            visual = service.get_component_visual(
                component_type=component_type,
                component_info={"name": component_info.name, "description": component_info.description},
                include_preview=include_preview,
                include_capabilities=include_capabilities,
            )
            if category is None or visual.category == category:
                visuals.append(visual)
    else:
        # Use known component types
        known_types = [
            "generator", "critic", "improver", "synthesizer", "selector",
            "filter", "json_transform", "schema_validate", "variable_set",
            "http_request", "webhook", "logger",
            "loop", "foreach", "conditional", "parallel", "output_router",
        ]
        for component_type in known_types:
            visual = service.get_component_visual(
                component_type=component_type,
                include_preview=include_preview,
                include_capabilities=include_capabilities,
            )
            if category is None or visual.category == category:
                visuals.append(visual)

    return visuals


@router.get("/components/{component_type}", response_model=ComponentVisual)
async def get_component_visual(
    component_type: str,
    include_preview: bool = Query(True),
    include_capabilities: bool = Query(True),
) -> ComponentVisual:
    """
    Get visual representation for a specific component type.
    """
    service = get_component_visual_service()
    registry = get_registry()

    component_info = None
    if registry:
        comp = registry.get_component(component_type)
        if comp:
            component_info = {"name": comp.name, "description": comp.description}

    return service.get_component_visual(
        component_type=component_type,
        component_info=component_info,
        include_preview=include_preview,
        include_capabilities=include_capabilities,
    )


# =============================================================================
# Component Palette
# =============================================================================


@router.get("/palette", response_model=ComponentPalette)
async def get_palette(
    categories: Optional[List[ComponentCategory]] = Query(None, description="Filter categories"),
) -> ComponentPalette:
    """
    Get the component palette with grouped components.

    The palette organizes components into logical groups and includes
    recently used and favorite components for quick access.
    """
    service = get_component_visual_service()
    registry = get_registry()

    return service.get_palette(
        categories=categories,
        component_registry=registry,
    )


@router.get("/palette/groups", response_model=List[ComponentGroup])
async def list_groups() -> List[ComponentGroup]:
    """
    List all component groups.
    """
    service = get_component_visual_service()
    palette = service.get_palette()
    return palette.groups


@router.get("/palette/groups/{group_id}", response_model=ComponentGroup)
async def get_group(group_id: str) -> ComponentGroup:
    """
    Get a specific component group.
    """
    service = get_component_visual_service()
    palette = service.get_palette()

    group = next((g for g in palette.groups if g.id == group_id), None)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return group


# =============================================================================
# Favorites and Recent
# =============================================================================


@router.get("/favorites", response_model=List[str])
async def get_favorites() -> List[str]:
    """
    Get favorite component types.
    """
    service = get_component_visual_service()
    palette = service.get_palette()
    return palette.favorites


@router.put("/favorites", response_model=List[str])
async def update_favorites(request: UpdateFavoritesRequest) -> List[str]:
    """
    Update favorite component types.
    """
    service = get_component_visual_service()
    service.update_favorites(request.favorites)
    return request.favorites


@router.post("/favorites/{component_type}")
async def add_favorite(component_type: str) -> dict:
    """
    Add a component to favorites.
    """
    service = get_component_visual_service()
    palette = service.get_palette()

    if component_type not in palette.favorites:
        service.update_favorites([*palette.favorites, component_type])

    return {"success": True, "favorites": service.get_palette().favorites}


@router.delete("/favorites/{component_type}")
async def remove_favorite(component_type: str) -> dict:
    """
    Remove a component from favorites.
    """
    service = get_component_visual_service()
    palette = service.get_palette()

    if component_type in palette.favorites:
        new_favorites = [f for f in palette.favorites if f != component_type]
        service.update_favorites(new_favorites)

    return {"success": True, "favorites": service.get_palette().favorites}


@router.get("/recent", response_model=List[str])
async def get_recently_used(
    limit: int = Query(10, ge=1, le=50),
) -> List[str]:
    """
    Get recently used component types.
    """
    service = get_component_visual_service()
    palette = service.get_palette()
    return palette.recently_used[:limit]


@router.post("/recent/{component_type}")
async def add_recently_used(component_type: str) -> dict:
    """
    Record that a component was used.
    """
    service = get_component_visual_service()
    service.add_to_recently_used(component_type)
    return {"success": True}


# =============================================================================
# Pipeline Visuals
# =============================================================================


@router.get("/pipelines/{pipeline_id}", response_model=PipelineVisual)
async def get_pipeline_visual(
    pipeline_id: str,
    include_execution_state: bool = Query(False),
) -> PipelineVisual:
    """
    Get visual representation of a pipeline.

    Returns complete visual data including stage positions, connections,
    and optionally execution state for live visualization.
    """
    service = get_component_visual_service()
    storage = get_pipeline_storage()

    # Get pipeline data
    pipeline = storage.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Get execution state if requested
    execution_state = None
    if include_execution_state:
        # This would come from the run storage in a real implementation
        pass

    return service.get_pipeline_visual(
        pipeline_id=pipeline_id,
        pipeline_data=pipeline,
        execution_state=execution_state,
    )


class UpdatePositionRequest(BaseModel):
    """Request to update stage position."""

    x: float
    y: float


@router.put("/pipelines/{pipeline_id}/stages/{stage_id}/position")
async def update_stage_position(
    pipeline_id: str,
    stage_id: str,
    request: UpdatePositionRequest,
) -> dict:
    """
    Update the visual position of a stage.

    This updates the visual layout without changing the pipeline logic.
    """
    # In a full implementation, this would persist to layout storage
    return {
        "success": True,
        "stage_id": stage_id,
        "position": {"x": request.x, "y": request.y},
    }


class UpdateViewportRequest(BaseModel):
    """Request to update viewport."""

    x: float
    y: float
    zoom: float


@router.put("/pipelines/{pipeline_id}/viewport")
async def update_viewport(
    pipeline_id: str,
    request: UpdateViewportRequest,
) -> dict:
    """
    Update the canvas viewport state.
    """
    return {
        "success": True,
        "viewport": {
            "x": request.x,
            "y": request.y,
            "zoom": request.zoom,
        },
    }


# =============================================================================
# Connection Styles
# =============================================================================


@router.get("/connection-style", response_model=ConnectionStyle)
async def get_connection_style(
    source_type: str = Query(..., description="Source component type"),
    target_type: str = Query(..., description="Target component type"),
) -> ConnectionStyle:
    """
    Get the recommended connection style between two component types.
    """
    service = get_component_visual_service()
    return service.get_connection_style(source_type, target_type)


# =============================================================================
# Categories
# =============================================================================


class CategoryInfo(BaseModel):
    """Information about a component category."""

    category: ComponentCategory
    name: str
    description: str
    color: str
    icon: str
    component_count: int


@router.get("/categories", response_model=List[CategoryInfo])
async def list_categories() -> List[CategoryInfo]:
    """
    List all component categories with metadata.
    """
    service = get_component_visual_service()
    palette = service.get_palette()

    category_info = {
        ComponentCategory.AI: {
            "name": "AI Components",
            "description": "LLM-powered components for generation and evaluation",
            "color": "#8b5cf6",
            "icon": "sparkles",
        },
        ComponentCategory.DATA: {
            "name": "Data Processing",
            "description": "Transform and validate data",
            "color": "#3b82f6",
            "icon": "database",
        },
        ComponentCategory.INTEGRATION: {
            "name": "Integrations",
            "description": "Connect to external services",
            "color": "#10b981",
            "icon": "plug",
        },
        ComponentCategory.CONTROL: {
            "name": "Control Flow",
            "description": "Manage execution flow",
            "color": "#f59e0b",
            "icon": "git-branch",
        },
        ComponentCategory.UTILITY: {
            "name": "Utilities",
            "description": "Helper components",
            "color": "#6b7280",
            "icon": "wrench",
        },
        ComponentCategory.CUSTOM: {
            "name": "Custom",
            "description": "User-defined components",
            "color": "#ec4899",
            "icon": "puzzle-piece",
        },
    }

    # Count components per category
    category_counts: Dict[ComponentCategory, int] = {}
    for group in palette.groups:
        cat = ComponentCategory(group.id) if group.id in [c.value for c in ComponentCategory] else ComponentCategory.CUSTOM
        category_counts[cat] = len(group.components)

    return [
        CategoryInfo(
            category=cat,
            name=info["name"],
            description=info["description"],
            color=info["color"],
            icon=info["icon"],
            component_count=category_counts.get(cat, 0),
        )
        for cat, info in category_info.items()
    ]


# =============================================================================
# Search
# =============================================================================


@router.get("/search", response_model=List[ComponentVisual])
async def search_components(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
) -> List[ComponentVisual]:
    """
    Search for components by name, description, or tags.
    """
    service = get_component_visual_service()
    palette = service.get_palette()
    query_lower = q.lower()

    # Get all component types
    all_types = []
    for group in palette.groups:
        all_types.extend(group.components)

    # Search and score
    scored = []
    for component_type in all_types:
        visual = service.get_component_visual(component_type)
        score = 0

        if query_lower in visual.name.lower():
            score += 3
        if query_lower in visual.description.lower():
            score += 2
        if any(query_lower in tag for tag in visual.tags):
            score += 1

        if score > 0:
            scored.append((score, visual))

    # Sort by score and return
    scored.sort(key=lambda x: x[0], reverse=True)
    return [v for _, v in scored[:limit]]
