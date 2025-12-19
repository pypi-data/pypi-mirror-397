"""
Component Visual Models.

Models for rich visual representation of pipeline components.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ComponentCategory(str, Enum):
    """Visual categories for components."""

    AI = "ai"
    DATA = "data"
    INTEGRATION = "integration"
    CONTROL = "control"
    UTILITY = "utility"
    CUSTOM = "custom"


class PortType(str, Enum):
    """Types of component ports."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    ANY = "any"


class PortDirection(str, Enum):
    """Port direction."""

    INPUT = "input"
    OUTPUT = "output"


class ComponentPort(BaseModel):
    """A component input/output port."""

    id: str
    name: str
    direction: PortDirection
    type: PortType
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None
    multiple: bool = Field(
        default=False,
        description="Whether this port accepts multiple connections"
    )


class ComponentBadge(BaseModel):
    """A badge/indicator for component status or capability."""

    id: str
    label: str
    color: str = Field(
        default="gray",
        description="Badge color: primary, success, warning, danger, info, gray"
    )
    icon: Optional[str] = None
    tooltip: Optional[str] = None


class ComponentTheme(BaseModel):
    """Visual theme for a component."""

    primary_color: str = Field(
        default="#6366f1",
        description="Primary color (hex)"
    )
    secondary_color: str = Field(
        default="#818cf8",
        description="Secondary color (hex)"
    )
    icon: str = Field(
        default="cube",
        description="Icon identifier"
    )
    icon_color: str = Field(
        default="#ffffff",
        description="Icon color (hex)"
    )
    gradient: Optional[str] = Field(
        default=None,
        description="CSS gradient for background"
    )


class ComponentPreview(BaseModel):
    """Preview snippet for a component."""

    type: str = Field(
        default="text",
        description="Preview type: text, code, json, image"
    )
    content: str
    language: Optional[str] = Field(
        default=None,
        description="Code language for syntax highlighting"
    )
    max_lines: int = Field(
        default=5,
        description="Maximum lines to show in preview"
    )


class ComponentCapability(BaseModel):
    """A capability that a component provides."""

    id: str
    name: str
    description: str
    level: str = Field(
        default="standard",
        description="Capability level: basic, standard, advanced"
    )


class ComponentVisual(BaseModel):
    """Rich visual representation of a component."""

    # Identity
    component_type: str
    name: str
    description: str
    version: Optional[str] = None

    # Categorization
    category: ComponentCategory
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Visual theme
    theme: ComponentTheme

    # Ports (inputs/outputs)
    ports: List[ComponentPort] = Field(default_factory=list)

    # Status and capabilities
    badges: List[ComponentBadge] = Field(default_factory=list)
    capabilities: List[ComponentCapability] = Field(default_factory=list)

    # Preview
    preview: Optional[ComponentPreview] = None

    # Metadata
    author: Optional[str] = None
    documentation_url: Optional[str] = None
    usage_count: int = Field(default=0, description="Times used in pipelines")
    popularity_score: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Popularity score 0-1"
    )

    # Interaction hints
    draggable: bool = Field(default=True)
    resizable: bool = Field(default=False)
    min_width: int = Field(default=200)
    min_height: int = Field(default=100)


class ComponentGroup(BaseModel):
    """A group of related components."""

    id: str
    name: str
    description: str
    icon: str
    color: str
    components: List[str] = Field(
        default_factory=list,
        description="Component type IDs in this group"
    )
    order: int = Field(default=0, description="Display order")


class ComponentPalette(BaseModel):
    """A palette of components organized into groups."""

    groups: List[ComponentGroup]
    recently_used: List[str] = Field(
        default_factory=list,
        description="Recently used component types"
    )
    favorites: List[str] = Field(
        default_factory=list,
        description="User favorite component types"
    )


class ConnectionStyle(BaseModel):
    """Visual style for connections between components."""

    type: str = Field(
        default="bezier",
        description="Connection type: bezier, straight, step, smoothstep"
    )
    color: str = Field(default="#94a3b8")
    width: int = Field(default=2)
    animated: bool = Field(default=False)
    dashed: bool = Field(default=False)


class StageVisual(BaseModel):
    """Visual representation of a pipeline stage (component instance)."""

    stage_id: str
    component: ComponentVisual
    position: Dict[str, float] = Field(
        default_factory=lambda: {"x": 0, "y": 0},
        description="Position on canvas"
    )
    size: Dict[str, int] = Field(
        default_factory=lambda: {"width": 250, "height": 150},
        description="Size on canvas"
    )
    collapsed: bool = Field(default=False)
    status: str = Field(
        default="idle",
        description="Status: idle, running, completed, failed, skipped"
    )
    progress: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Execution progress 0-1"
    )


class ConnectionVisual(BaseModel):
    """Visual representation of a connection between stages."""

    id: str
    source_stage: str
    source_port: str
    target_stage: str
    target_port: str
    style: ConnectionStyle = Field(default_factory=ConnectionStyle)
    label: Optional[str] = None


class PipelineVisual(BaseModel):
    """Complete visual representation of a pipeline."""

    pipeline_id: str
    name: str
    stages: List[StageVisual]
    connections: List[ConnectionVisual]
    viewport: Dict[str, float] = Field(
        default_factory=lambda: {"x": 0, "y": 0, "zoom": 1.0},
        description="Canvas viewport state"
    )
    grid_enabled: bool = Field(default=True)
    snap_to_grid: bool = Field(default=True)
    grid_size: int = Field(default=20)


# API Request/Response Models

class GetComponentVisualRequest(BaseModel):
    """Request for component visual."""

    component_type: str
    include_preview: bool = True
    include_capabilities: bool = True


class GetPaletteRequest(BaseModel):
    """Request for component palette."""

    categories: Optional[List[ComponentCategory]] = None
    include_hidden: bool = False


class UpdateFavoritesRequest(BaseModel):
    """Request to update favorites."""

    favorites: List[str]


class UpdateRecentRequest(BaseModel):
    """Request to update recently used."""

    component_type: str


class GetPipelineVisualRequest(BaseModel):
    """Request for pipeline visual."""

    pipeline_id: str
    include_execution_state: bool = False


class UpdatePositionRequest(BaseModel):
    """Request to update stage position."""

    stage_id: str
    x: float
    y: float


class UpdateViewportRequest(BaseModel):
    """Request to update viewport."""

    x: float
    y: float
    zoom: float
