"""
Pipeline Inheritance & Composition Models.

Models for extending and composing pipelines from base templates.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class InheritanceMode(str, Enum):
    """How inheritance works for stages."""

    EXTEND = "extend"  # Add to parent stages
    OVERRIDE = "override"  # Replace matching parent stages
    MERGE = "merge"  # Merge configurations


class CompositionMode(str, Enum):
    """How pipelines are composed together."""

    SEQUENTIAL = "sequential"  # Run one after another
    PARALLEL = "parallel"  # Run in parallel, merge outputs
    CONDITIONAL = "conditional"  # Choose based on condition


class StageOverride(BaseModel):
    """Override for a specific stage from parent pipeline."""

    stage_id: str = Field(description="ID of stage to override")
    mode: InheritanceMode = Field(
        default=InheritanceMode.MERGE,
        description="How to apply the override"
    )

    # What to override
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Configuration overrides"
    )
    component_type: Optional[str] = Field(
        default=None,
        description="Override component type"
    )
    depends_on: Optional[List[str]] = Field(
        default=None,
        description="Override dependencies"
    )
    enabled: Optional[bool] = Field(
        default=None,
        description="Enable/disable stage"
    )


class StageAddition(BaseModel):
    """New stage to add in derived pipeline."""

    id: str = Field(description="Stage ID")
    name: str = Field(description="Stage name")
    component_type: str = Field(description="Component type")
    config: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)

    # Positioning
    insert_after: Optional[str] = Field(
        default=None,
        description="Insert after this stage ID"
    )
    insert_before: Optional[str] = Field(
        default=None,
        description="Insert before this stage ID"
    )


class StageRemoval(BaseModel):
    """Stage to remove from parent pipeline."""

    stage_id: str = Field(description="ID of stage to remove")
    cascade: bool = Field(
        default=True,
        description="Also remove stages that depend on this one"
    )


class VariableOverride(BaseModel):
    """Override for pipeline variables."""

    name: str = Field(description="Variable name")
    value: Any = Field(description="New value")
    mode: InheritanceMode = Field(
        default=InheritanceMode.OVERRIDE,
        description="How to apply override"
    )


class BasePipelineReference(BaseModel):
    """Reference to a base pipeline."""

    pipeline_id: str = Field(description="ID of base pipeline")
    version: Optional[str] = Field(
        default=None,
        description="Specific version (None = latest)"
    )


class PipelineInheritance(BaseModel):
    """Inheritance configuration for a pipeline."""

    extends: BasePipelineReference = Field(
        description="Base pipeline to extend"
    )

    # Stage modifications
    stage_overrides: List[StageOverride] = Field(
        default_factory=list,
        description="Overrides for parent stages"
    )
    stage_additions: List[StageAddition] = Field(
        default_factory=list,
        description="New stages to add"
    )
    stage_removals: List[StageRemoval] = Field(
        default_factory=list,
        description="Stages to remove"
    )

    # Variable modifications
    variable_overrides: List[VariableOverride] = Field(
        default_factory=list,
        description="Variable overrides"
    )

    # Settings
    inherit_settings: bool = Field(
        default=True,
        description="Inherit pipeline settings from parent"
    )
    inherit_providers: bool = Field(
        default=True,
        description="Inherit provider configurations"
    )


class ComposedPipeline(BaseModel):
    """A pipeline composed from other pipelines."""

    id: str = Field(description="Composition ID")
    pipelines: List[str] = Field(description="Pipeline IDs to compose")
    mode: CompositionMode = Field(
        default=CompositionMode.SEQUENTIAL,
        description="Composition mode"
    )

    # For sequential mode
    output_mapping: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Map outputs between pipelines: {from_pipeline: {output_key: input_key}}"
    )

    # For conditional mode
    condition: Optional[str] = Field(
        default=None,
        description="Condition expression for choosing pipeline"
    )
    condition_map: Dict[str, str] = Field(
        default_factory=dict,
        description="Condition value -> pipeline ID mapping"
    )
    default_pipeline: Optional[str] = Field(
        default=None,
        description="Default pipeline if no condition matches"
    )

    # For parallel mode
    merge_strategy: str = Field(
        default="merge",
        description="How to merge parallel outputs: merge, array, first"
    )


class ResolvedPipeline(BaseModel):
    """A fully resolved pipeline after applying inheritance/composition."""

    id: str = Field(description="Original pipeline ID")
    name: str = Field(description="Pipeline name")
    description: str = Field(default="")

    # Resolved content
    stages: List[Dict[str, Any]] = Field(description="Resolved stages")
    variables: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)

    # Lineage
    base_pipelines: List[str] = Field(
        default_factory=list,
        description="IDs of base pipelines (inheritance chain)"
    )
    composed_from: List[str] = Field(
        default_factory=list,
        description="IDs of composed pipelines"
    )

    # Resolution metadata
    resolved_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    resolution_warnings: List[str] = Field(default_factory=list)


class BasePipeline(BaseModel):
    """A pipeline that can be used as a base template."""

    id: str = Field(description="Pipeline ID")
    name: str = Field(description="Template name")
    description: str = Field(default="")
    category: str = Field(default="general", description="Template category")
    tags: List[str] = Field(default_factory=list)

    # Template configuration
    is_abstract: bool = Field(
        default=False,
        description="If true, cannot be run directly"
    )
    required_overrides: List[str] = Field(
        default_factory=list,
        description="Stage IDs that must be overridden"
    )
    sealed_stages: List[str] = Field(
        default_factory=list,
        description="Stage IDs that cannot be overridden"
    )

    # Pipeline content
    stages: List[Dict[str, Any]] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    created_by: Optional[str] = None
    version: str = Field(default="1.0.0")


# API Request/Response Models


class CreateBasePipelineRequest(BaseModel):
    """Request to create a base pipeline template."""

    name: str
    description: str = ""
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    is_abstract: bool = False
    required_overrides: List[str] = Field(default_factory=list)
    sealed_stages: List[str] = Field(default_factory=list)
    stages: List[Dict[str, Any]]
    variables: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)


class ExtendPipelineRequest(BaseModel):
    """Request to create a pipeline by extending a base."""

    name: str
    description: str = ""
    base_pipeline_id: str
    base_version: Optional[str] = None

    # Modifications
    stage_overrides: List[StageOverride] = Field(default_factory=list)
    stage_additions: List[StageAddition] = Field(default_factory=list)
    stage_removals: List[StageRemoval] = Field(default_factory=list)
    variable_overrides: List[VariableOverride] = Field(default_factory=list)


class ComposePipelinesRequest(BaseModel):
    """Request to compose multiple pipelines."""

    name: str
    description: str = ""
    pipeline_ids: List[str]
    mode: CompositionMode = CompositionMode.SEQUENTIAL
    output_mapping: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    condition: Optional[str] = None
    condition_map: Dict[str, str] = Field(default_factory=dict)
    default_pipeline: Optional[str] = None
    merge_strategy: str = "merge"


class ResolvePipelineRequest(BaseModel):
    """Request to resolve a pipeline's inheritance."""

    pipeline_id: str
    include_source_mapping: bool = Field(
        default=False,
        description="Include mapping of which base each stage came from"
    )


class ResolvePipelineResponse(BaseModel):
    """Response with resolved pipeline."""

    pipeline: ResolvedPipeline
    source_mapping: Optional[Dict[str, str]] = Field(
        default=None,
        description="Stage ID -> source pipeline ID"
    )


class ListBasePipelinesResponse(BaseModel):
    """Response listing base pipeline templates."""

    templates: List[BasePipeline]
    total: int
    categories: List[str]


class ValidateInheritanceResponse(BaseModel):
    """Response from validating inheritance configuration."""

    valid: bool
    errors: List[str]
    warnings: List[str]
    missing_overrides: List[str] = Field(
        default_factory=list,
        description="Required overrides that are missing"
    )
    sealed_violations: List[str] = Field(
        default_factory=list,
        description="Attempted overrides of sealed stages"
    )
