"""
Pipeline Version API Routes.

Manage pipeline version history for auditing and rollback.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from flowmason_studio.models.api import PipelineStage, PipelineUpdate
from flowmason_studio.services.storage import (
    PipelineStorage,
    get_pipeline_storage,
)
from flowmason_studio.services.version_storage import (
    PipelineVersion,
    get_version_storage,
)

router = APIRouter(prefix="/pipelines/{pipeline_id}/versions", tags=["versions"])


# Request/Response Models
class CreateVersionRequest(BaseModel):
    """Request to create a version snapshot."""

    message: str = Field(default="", description="Commit-style message for this version")
    created_by: Optional[str] = Field(default=None, description="User who created this version")


class VersionResponse(BaseModel):
    """Version response."""

    id: str
    pipeline_id: str
    version: str
    org_id: str
    name: str
    description: str
    created_at: str
    created_by: Optional[str]
    message: str
    is_published: bool
    parent_version_id: Optional[str]
    changes_summary: Optional[str]
    stages_added: List[str]
    stages_removed: List[str]
    stages_modified: List[str]

    @classmethod
    def from_version(cls, v: PipelineVersion) -> "VersionResponse":
        return cls(
            id=v.id,
            pipeline_id=v.pipeline_id,
            version=v.version,
            org_id=v.org_id,
            name=v.name,
            description=v.description,
            created_at=v.created_at,
            created_by=v.created_by,
            message=v.message,
            is_published=v.is_published,
            parent_version_id=v.parent_version_id,
            changes_summary=v.changes_summary,
            stages_added=v.stages_added,
            stages_removed=v.stages_removed,
            stages_modified=v.stages_modified,
        )


class VersionDetailResponse(VersionResponse):
    """Version response with full pipeline data."""

    stages: List[Dict[str, Any]]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    output_stage_id: Optional[str]
    llm_settings: Optional[Dict[str, Any]]

    @classmethod
    def from_version(cls, v: PipelineVersion) -> "VersionDetailResponse":
        return cls(
            id=v.id,
            pipeline_id=v.pipeline_id,
            version=v.version,
            org_id=v.org_id,
            name=v.name,
            description=v.description,
            created_at=v.created_at,
            created_by=v.created_by,
            message=v.message,
            is_published=v.is_published,
            parent_version_id=v.parent_version_id,
            changes_summary=v.changes_summary,
            stages_added=v.stages_added,
            stages_removed=v.stages_removed,
            stages_modified=v.stages_modified,
            stages=v.stages,
            input_schema=v.input_schema,
            output_schema=v.output_schema,
            output_stage_id=v.output_stage_id,
            llm_settings=v.llm_settings,
        )


class VersionListResponse(BaseModel):
    """List versions response."""

    versions: List[VersionResponse]
    total: int
    limit: int
    offset: int


class VersionDiffResponse(BaseModel):
    """Response for comparing two versions."""

    version_1: Dict[str, Any]
    version_2: Dict[str, Any]
    stages_added: List[str]
    stages_removed: List[str]
    stages_modified: List[str]
    summary: str


class RestoreVersionResponse(BaseModel):
    """Response after restoring a version."""

    pipeline_id: str
    restored_from_version: str
    new_version: str
    message: str


# Dependency to get pipeline storage
def _get_pipeline_storage_dep() -> PipelineStorage:
    return get_pipeline_storage()


# Routes
@router.post("", response_model=VersionResponse)
async def create_version(
    pipeline_id: str,
    request: CreateVersionRequest,
    org_id: str = Query(default="default", description="Organization ID"),
    pipeline_storage: PipelineStorage = Depends(_get_pipeline_storage_dep),
):
    """
    Create a version snapshot of the current pipeline state.

    This saves the current pipeline configuration as a named version
    that can be restored later.
    """
    version_storage = get_version_storage()

    # Get current pipeline
    pipeline = pipeline_storage.get(pipeline_id, org_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Get latest version to set as parent
    latest = version_storage.get_latest_version(pipeline_id, org_id)
    parent_id = latest.id if latest else None

    # Create version
    version = version_storage.create_version(
        pipeline_id=pipeline_id,
        org_id=org_id,
        name=pipeline.name,
        version=pipeline.version,
        stages=[s.model_dump() for s in pipeline.stages],
        description=pipeline.description or "",
        input_schema=pipeline.input_schema.model_dump() if hasattr(pipeline.input_schema, "model_dump") else pipeline.input_schema,  # type: ignore[arg-type]
        output_schema=pipeline.output_schema.model_dump() if hasattr(pipeline.output_schema, "model_dump") else pipeline.output_schema,  # type: ignore[arg-type]
        output_stage_id=pipeline.output_stage_id,
        created_by=request.created_by,
        message=request.message,
        is_published=pipeline.status == "published",
        parent_version_id=parent_id,
    )

    return VersionResponse.from_version(version)


@router.get("", response_model=VersionListResponse)
async def list_versions(
    pipeline_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List all versions of a pipeline."""
    version_storage = get_version_storage()

    versions, total = version_storage.list_versions(
        pipeline_id=pipeline_id,
        org_id=org_id,
        limit=limit,
        offset=offset,
    )

    return VersionListResponse(
        versions=[VersionResponse.from_version(v) for v in versions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/latest", response_model=VersionDetailResponse)
async def get_latest_version(
    pipeline_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Get the most recent version of a pipeline."""
    version_storage = get_version_storage()

    version = version_storage.get_latest_version(pipeline_id, org_id)
    if not version:
        raise HTTPException(status_code=404, detail="No versions found")

    return VersionDetailResponse.from_version(version)


@router.get("/{version_id}", response_model=VersionDetailResponse)
async def get_version(
    pipeline_id: str,
    version_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Get a specific version by ID."""
    version_storage = get_version_storage()

    version = version_storage.get(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if version.pipeline_id != pipeline_id:
        raise HTTPException(status_code=404, detail="Version not found for this pipeline")

    if org_id and version.org_id != org_id:
        raise HTTPException(status_code=404, detail="Version not found")

    return VersionDetailResponse.from_version(version)


@router.get("/by-version/{version_number}", response_model=VersionDetailResponse)
async def get_version_by_number(
    pipeline_id: str,
    version_number: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Get a version by version number (e.g., '1.0.0')."""
    version_storage = get_version_storage()

    version = version_storage.get_by_version(pipeline_id, version_number, org_id)
    if not version:
        raise HTTPException(
            status_code=404,
            detail=f"Version '{version_number}' not found",
        )

    return VersionDetailResponse.from_version(version)


@router.get("/{version_id}/compare/{other_version_id}", response_model=VersionDiffResponse)
async def compare_versions(
    pipeline_id: str,
    version_id: str,
    other_version_id: str,
):
    """Compare two versions and show the diff."""
    version_storage = get_version_storage()

    diff = version_storage.compare_versions(version_id, other_version_id)
    if not diff:
        raise HTTPException(status_code=404, detail="One or both versions not found")

    return VersionDiffResponse(**diff)


@router.post("/{version_id}/restore", response_model=RestoreVersionResponse)
async def restore_version(
    pipeline_id: str,
    version_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
    pipeline_storage: PipelineStorage = Depends(_get_pipeline_storage_dep),
):
    """
    Restore a pipeline to a previous version.

    This creates a new version (current state is preserved) and updates
    the pipeline to match the specified version.
    """
    version_storage = get_version_storage()

    # Get version to restore
    version = version_storage.get(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if version.pipeline_id != pipeline_id:
        raise HTTPException(status_code=404, detail="Version not found for this pipeline")

    # Get current pipeline
    pipeline = pipeline_storage.get(pipeline_id, org_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # First, save current state as a version (so we don't lose it)
    latest = version_storage.get_latest_version(pipeline_id, org_id)
    version_storage.create_version(
        pipeline_id=pipeline_id,
        org_id=org_id,
        name=pipeline.name,
        version=pipeline.version,
        stages=[s.model_dump() for s in pipeline.stages],
        description=pipeline.description or "",
        input_schema=pipeline.input_schema.model_dump() if hasattr(pipeline.input_schema, "model_dump") else pipeline.input_schema,  # type: ignore[arg-type]
        output_schema=pipeline.output_schema.model_dump() if hasattr(pipeline.output_schema, "model_dump") else pipeline.output_schema,  # type: ignore[arg-type]
        output_stage_id=pipeline.output_stage_id,
        message=f"Auto-save before restore to {version.version}",
        parent_version_id=latest.id if latest else None,
    )

    # Update pipeline with version data
    stages = [
        PipelineStage(
            id=s.get("id") or "",
            name=s.get("name", s.get("id")) or "",
            component_type=s.get("component_type") or "",
            config=s.get("config", {}),
            input_mapping=s.get("input_mapping", {}),
            depends_on=s.get("depends_on", []),
        )
        for s in version.stages
    ]

    # Increment version number
    version_parts = pipeline.version.split(".")
    version_parts[-1] = str(int(version_parts[-1]) + 1)
    new_version = ".".join(version_parts)

    # Update pipeline
    update_data = PipelineUpdate(
        name=version.name,
        description=version.description,
        stages=stages,
        input_schema=version.input_schema,  # type: ignore[arg-type]
        output_schema=version.output_schema,  # type: ignore[arg-type]
        output_stage_id=version.output_stage_id,
    )
    pipeline_storage.update(pipeline_id, update_data, org_id)

    # Create new version for the restore
    version_storage.create_version(
        pipeline_id=pipeline_id,
        org_id=org_id,
        name=version.name,
        version=new_version,
        stages=version.stages,
        description=version.description,
        input_schema=version.input_schema,
        output_schema=version.output_schema,
        output_stage_id=version.output_stage_id,
        llm_settings=version.llm_settings,
        message=f"Restored from version {version.version}",
        parent_version_id=version.id,
    )

    return RestoreVersionResponse(
        pipeline_id=pipeline_id,
        restored_from_version=version.version,
        new_version=new_version,
        message=f"Successfully restored from version {version.version}",
    )


@router.delete("/{version_id}")
async def delete_version(
    pipeline_id: str,
    version_id: str,
    org_id: str = Query(default="default", description="Organization ID"),
):
    """Delete a version."""
    version_storage = get_version_storage()

    # Verify version belongs to pipeline
    version = version_storage.get(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if version.pipeline_id != pipeline_id:
        raise HTTPException(status_code=404, detail="Version not found for this pipeline")

    deleted = version_storage.delete_version(version_id, org_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Version not found")

    return {"deleted": True, "version_id": version_id}
