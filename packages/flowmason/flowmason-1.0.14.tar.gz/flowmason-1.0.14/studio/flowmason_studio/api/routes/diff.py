"""
Pipeline Diff & Merge API Routes.

Provides HTTP API for comparing and merging pipeline versions.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from flowmason_studio.models.diff import (
    ApplyDiffRequest,
    DiffPipelinesRequest,
    DiffPipelinesResponse,
    MergePipelinesRequest,
    MergePipelinesResponse,
    PipelineDiff,
    ResolveConflictsRequest,
    VisualDiffOptions,
)
from flowmason_studio.services.diff_service import get_diff_service
from flowmason_studio.services.storage import get_pipeline_storage
from flowmason_studio.services.version_storage import get_version_storage

router = APIRouter(prefix="/diff", tags=["diff"])


@router.post("/compare", response_model=DiffPipelinesResponse)
async def compare_pipelines(request: DiffPipelinesRequest) -> DiffPipelinesResponse:
    """
    Compare two pipeline versions and return the diff.

    Can compare:
    - Two different pipelines
    - Two versions of the same pipeline
    """
    storage = get_pipeline_storage()
    version_storage = get_version_storage()
    diff_service = get_diff_service()

    # Get base pipeline
    if request.base_version:
        base = version_storage.get_version(request.base_pipeline_id, request.base_version)
        if base:
            base = base.get("pipeline_data", {})
    else:
        base = storage.get_pipeline(request.base_pipeline_id)

    if not base:
        raise HTTPException(status_code=404, detail="Base pipeline not found")

    # Get compare pipeline
    if request.compare_version:
        compare = version_storage.get_version(request.compare_pipeline_id, request.compare_version)
        if compare:
            compare = compare.get("pipeline_data", {})
    else:
        compare = storage.get_pipeline(request.compare_pipeline_id)

    if not compare:
        raise HTTPException(status_code=404, detail="Compare pipeline not found")

    # Compute diff
    diff = diff_service.compute_diff(base, compare, request.include_unchanged)

    # Generate visual diff
    visual_diff = diff_service.generate_visual_diff(diff)

    return DiffPipelinesResponse(
        diff=diff,
        visual_diff=visual_diff,
    )


@router.get("/compare/{pipeline_id}")
async def compare_pipeline_versions(
    pipeline_id: str,
    base_version: str = Query(..., description="Base version to compare"),
    compare_version: str = Query(..., description="Version to compare against"),
    include_unchanged: bool = Query(False),
) -> DiffPipelinesResponse:
    """
    Compare two versions of the same pipeline.
    """
    version_storage = get_version_storage()
    diff_service = get_diff_service()

    base = version_storage.get_version(pipeline_id, base_version)
    if not base:
        raise HTTPException(status_code=404, detail=f"Version {base_version} not found")

    compare = version_storage.get_version(pipeline_id, compare_version)
    if not compare:
        raise HTTPException(status_code=404, detail=f"Version {compare_version} not found")

    diff = diff_service.compute_diff(
        base.get("pipeline_data", {}),
        compare.get("pipeline_data", {}),
        include_unchanged,
    )

    visual_diff = diff_service.generate_visual_diff(diff)

    return DiffPipelinesResponse(
        diff=diff,
        visual_diff=visual_diff,
    )


@router.post("/merge", response_model=MergePipelinesResponse)
async def merge_pipelines(request: MergePipelinesRequest) -> MergePipelinesResponse:
    """
    Perform a three-way merge of pipelines.

    Requires:
    - base: The common ancestor
    - ours: Our current version
    - theirs: The incoming version to merge

    Returns the merged result or conflicts that need resolution.
    """
    storage = get_pipeline_storage()
    version_storage = get_version_storage()
    diff_service = get_diff_service()

    # Get base pipeline
    if request.base_version:
        base = version_storage.get_version(request.base_pipeline_id, request.base_version)
        if base:
            base = base.get("pipeline_data", {})
    else:
        base = storage.get_pipeline(request.base_pipeline_id)

    if not base:
        raise HTTPException(status_code=404, detail="Base pipeline not found")

    # Get ours pipeline
    if request.ours_version:
        ours = version_storage.get_version(request.ours_pipeline_id, request.ours_version)
        if ours:
            ours = ours.get("pipeline_data", {})
    else:
        ours = storage.get_pipeline(request.ours_pipeline_id)

    if not ours:
        raise HTTPException(status_code=404, detail="Ours pipeline not found")

    # Get theirs pipeline
    if request.theirs_version:
        theirs = version_storage.get_version(request.theirs_pipeline_id, request.theirs_version)
        if theirs:
            theirs = theirs.get("pipeline_data", {})
    else:
        theirs = storage.get_pipeline(request.theirs_pipeline_id)

    if not theirs:
        raise HTTPException(status_code=404, detail="Theirs pipeline not found")

    # Perform merge
    result = diff_service.three_way_merge(
        base=base,
        ours=ours,
        theirs=theirs,
        resolutions=request.resolutions,
        manual_values=request.manual_resolutions,
        auto_resolve=request.auto_resolve,
        prefer_ours=request.prefer_ours,
    )

    return MergePipelinesResponse(
        result=result,
        preview=result.merged_pipeline if result.success else None,
    )


@router.post("/merge/resolve")
async def resolve_conflicts(request: ResolveConflictsRequest) -> MergePipelinesResponse:
    """
    Resolve conflicts from a previous merge attempt.

    Takes the merge session ID and conflict resolutions.
    """
    diff_service = get_diff_service()

    # Get the merge session
    session = diff_service._merge_sessions.get(request.merge_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Merge session not found or expired")

    # Re-run merge with resolutions
    result = diff_service.three_way_merge(
        base=session["base"],
        ours=session["ours"],
        theirs=session["theirs"],
        resolutions=request.resolutions,
        manual_values=request.manual_values,
    )

    return MergePipelinesResponse(
        result=result,
        preview=result.merged_pipeline if result.success else None,
    )


@router.post("/apply")
async def apply_diff(request: ApplyDiffRequest) -> dict:
    """
    Apply a diff to a target pipeline.

    Can either modify the target in place or create a new pipeline.
    """
    storage = get_pipeline_storage()
    diff_service = get_diff_service()

    target = storage.get_pipeline(request.target_pipeline_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target pipeline not found")

    # Apply the diff
    result = diff_service.apply_diff(target, request.diff)

    if request.create_new:
        # Create new pipeline
        import uuid
        new_id = f"pipeline_{uuid.uuid4().hex[:8]}"
        result["id"] = new_id
        if request.new_name:
            result["name"] = request.new_name
        storage.save_pipeline(new_id, result)
        return {
            "success": True,
            "pipeline_id": new_id,
            "created_new": True,
        }
    else:
        # Update existing
        storage.save_pipeline(request.target_pipeline_id, result)
        return {
            "success": True,
            "pipeline_id": request.target_pipeline_id,
            "created_new": False,
        }


@router.get("/history/{pipeline_id}")
async def get_version_history(
    pipeline_id: str,
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """
    Get version history for a pipeline with diffs between consecutive versions.
    """
    version_storage = get_version_storage()
    diff_service = get_diff_service()

    versions = version_storage.list_versions(pipeline_id, limit=limit)

    if not versions:
        return {"pipeline_id": pipeline_id, "versions": [], "diffs": []}

    # Compute diffs between consecutive versions
    diffs = []
    for i in range(len(versions) - 1):
        newer = versions[i]
        older = versions[i + 1]

        diff = diff_service.compute_diff(
            older.get("pipeline_data", {}),
            newer.get("pipeline_data", {}),
        )

        diffs.append({
            "from_version": older.get("version"),
            "to_version": newer.get("version"),
            "total_changes": diff.total_changes,
            "summary": {
                "stages_added": len([c for c in diff.stage_changes if c.change_type.value == "added"]),
                "stages_removed": len([c for c in diff.stage_changes if c.change_type.value == "removed"]),
                "stages_modified": len([c for c in diff.stage_changes if c.change_type.value == "modified"]),
            },
        })

    return {
        "pipeline_id": pipeline_id,
        "versions": [
            {
                "version": v.get("version"),
                "created_at": v.get("created_at"),
                "message": v.get("message"),
                "author": v.get("author"),
            }
            for v in versions
        ],
        "diffs": diffs,
    }


@router.post("/visual")
async def generate_visual_diff(
    request: DiffPipelinesRequest,
    options: Optional[VisualDiffOptions] = None,
) -> dict:
    """
    Generate a visual diff representation for UI rendering.

    Returns structured data suitable for rendering in a diff viewer component.
    """
    storage = get_pipeline_storage()
    diff_service = get_diff_service()

    base = storage.get_pipeline(request.base_pipeline_id)
    if not base:
        raise HTTPException(status_code=404, detail="Base pipeline not found")

    compare = storage.get_pipeline(request.compare_pipeline_id)
    if not compare:
        raise HTTPException(status_code=404, detail="Compare pipeline not found")

    diff = diff_service.compute_diff(base, compare, request.include_unchanged)

    options = options or VisualDiffOptions()
    visual = diff_service.generate_visual_diff(diff, side_by_side=options.side_by_side)

    return {
        "diff": diff.model_dump(),
        "visual": visual,
        "options": options.model_dump(),
    }


@router.get("/stages/{pipeline_id}/{stage_id}")
async def diff_stage_versions(
    pipeline_id: str,
    stage_id: str,
    base_version: str = Query(...),
    compare_version: str = Query(...),
) -> dict:
    """
    Get detailed diff for a specific stage between versions.
    """
    version_storage = get_version_storage()
    diff_service = get_diff_service()

    base_pipeline = version_storage.get_version(pipeline_id, base_version)
    if not base_pipeline:
        raise HTTPException(status_code=404, detail=f"Version {base_version} not found")

    compare_pipeline = version_storage.get_version(pipeline_id, compare_version)
    if not compare_pipeline:
        raise HTTPException(status_code=404, detail=f"Version {compare_version} not found")

    base_data = base_pipeline.get("pipeline_data", {})
    compare_data = compare_pipeline.get("pipeline_data", {})

    # Find the stage in each version
    base_stages = {s["id"]: s for s in base_data.get("stages", [])}
    compare_stages = {s["id"]: s for s in compare_data.get("stages", [])}

    base_stage = base_stages.get(stage_id)
    compare_stage = compare_stages.get(stage_id)

    if not base_stage and not compare_stage:
        raise HTTPException(status_code=404, detail=f"Stage {stage_id} not found in either version")

    # Compute field-level diff
    if base_stage and compare_stage:
        field_changes = diff_service._diff_stage_fields(base_stage, compare_stage)
        change_type = "modified" if field_changes else "unchanged"
    elif base_stage:
        field_changes = []
        change_type = "removed"
    else:
        field_changes = []
        change_type = "added"

    return {
        "stage_id": stage_id,
        "change_type": change_type,
        "base_version": base_version,
        "compare_version": compare_version,
        "base_stage": base_stage,
        "compare_stage": compare_stage,
        "field_changes": [fc.model_dump() for fc in field_changes],
    }
