"""
Pipeline Diff & Merge Models.

Models for comparing and merging pipeline versions.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Type of change detected."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    MOVED = "moved"
    UNCHANGED = "unchanged"


class ConflictType(str, Enum):
    """Type of merge conflict."""

    BOTH_MODIFIED = "both_modified"
    MODIFY_DELETE = "modify_delete"
    ADD_ADD = "add_add"


class ConflictResolution(str, Enum):
    """How to resolve a conflict."""

    USE_OURS = "use_ours"
    USE_THEIRS = "use_theirs"
    USE_BOTH = "use_both"
    MANUAL = "manual"


class FieldChange(BaseModel):
    """A change to a specific field."""

    field: str = Field(description="Field path (e.g., 'config.model')")
    change_type: ChangeType
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None


class StageChange(BaseModel):
    """Change detected in a pipeline stage."""

    stage_id: str
    stage_name: str
    change_type: ChangeType

    # For modifications, what fields changed
    field_changes: List[FieldChange] = Field(default_factory=list)

    # For moves, old and new position
    old_position: Optional[int] = None
    new_position: Optional[int] = None

    # Full stage data for added/removed
    stage_data: Optional[Dict[str, Any]] = None


class VariableChange(BaseModel):
    """Change detected in pipeline variables."""

    variable_name: str
    change_type: ChangeType
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None


class SettingsChange(BaseModel):
    """Change detected in pipeline settings."""

    setting_path: str
    change_type: ChangeType
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None


class PipelineDiff(BaseModel):
    """Complete diff between two pipeline versions."""

    base_id: str = Field(description="Base pipeline ID or version")
    compare_id: str = Field(description="Compare pipeline ID or version")

    # High-level summary
    has_changes: bool = False
    total_changes: int = 0

    # Detailed changes
    stage_changes: List[StageChange] = Field(default_factory=list)
    variable_changes: List[VariableChange] = Field(default_factory=list)
    settings_changes: List[SettingsChange] = Field(default_factory=list)

    # Metadata changes
    name_changed: bool = False
    old_name: Optional[str] = None
    new_name: Optional[str] = None
    description_changed: bool = False
    old_description: Optional[str] = None
    new_description: Optional[str] = None

    # Computed at
    computed_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


class MergeConflict(BaseModel):
    """A conflict that needs resolution during merge."""

    id: str = Field(description="Conflict identifier")
    conflict_type: ConflictType
    location: str = Field(description="Where the conflict is (e.g., 'stage:generate')")

    # The conflicting values
    base_value: Optional[Any] = None
    ours_value: Optional[Any] = None
    theirs_value: Optional[Any] = None

    # Resolution
    resolution: Optional[ConflictResolution] = None
    resolved_value: Optional[Any] = None

    # Context
    description: str = ""


class MergeResult(BaseModel):
    """Result of a three-way merge."""

    success: bool
    merged_pipeline: Optional[Dict[str, Any]] = None

    # Conflicts that need resolution
    conflicts: List[MergeConflict] = Field(default_factory=list)
    has_conflicts: bool = False

    # What was auto-merged
    auto_merged_changes: int = 0

    # Warnings
    warnings: List[str] = Field(default_factory=list)


class ThreeWayMergeInput(BaseModel):
    """Input for three-way merge."""

    base: Dict[str, Any] = Field(description="Common ancestor pipeline")
    ours: Dict[str, Any] = Field(description="Our version (current)")
    theirs: Dict[str, Any] = Field(description="Their version (incoming)")


# =============================================================================
# API Request/Response Models
# =============================================================================


class DiffPipelinesRequest(BaseModel):
    """Request to diff two pipelines."""

    base_pipeline_id: str
    compare_pipeline_id: str
    base_version: Optional[str] = None
    compare_version: Optional[str] = None
    include_unchanged: bool = Field(
        default=False,
        description="Include unchanged stages in response"
    )


class DiffPipelinesResponse(BaseModel):
    """Response with pipeline diff."""

    diff: PipelineDiff
    visual_diff: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Visual diff representation for UI"
    )


class MergePipelinesRequest(BaseModel):
    """Request to merge pipelines."""

    base_pipeline_id: str
    ours_pipeline_id: str
    theirs_pipeline_id: str
    base_version: Optional[str] = None
    ours_version: Optional[str] = None
    theirs_version: Optional[str] = None

    # Pre-resolved conflicts
    resolutions: Dict[str, ConflictResolution] = Field(
        default_factory=dict,
        description="Conflict ID -> resolution strategy"
    )
    manual_resolutions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Conflict ID -> manually chosen value"
    )

    # Options
    auto_resolve: bool = Field(
        default=True,
        description="Auto-resolve non-conflicting changes"
    )
    prefer_ours: bool = Field(
        default=False,
        description="Prefer our changes when auto-resolving"
    )


class MergePipelinesResponse(BaseModel):
    """Response from merge operation."""

    result: MergeResult
    preview: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Preview of merged pipeline"
    )


class ResolveConflictsRequest(BaseModel):
    """Request to resolve merge conflicts."""

    merge_session_id: str
    resolutions: Dict[str, ConflictResolution]
    manual_values: Dict[str, Any] = Field(default_factory=dict)


class ApplyDiffRequest(BaseModel):
    """Request to apply a diff as a patch."""

    target_pipeline_id: str
    diff: PipelineDiff
    create_new: bool = Field(
        default=False,
        description="Create new pipeline instead of modifying"
    )
    new_name: Optional[str] = None


class VisualDiffOptions(BaseModel):
    """Options for visual diff generation."""

    side_by_side: bool = Field(
        default=True,
        description="Side-by-side vs unified view"
    )
    show_line_numbers: bool = True
    highlight_changes: bool = True
    collapse_unchanged: bool = True
    context_lines: int = Field(
        default=3,
        description="Lines of context around changes"
    )
