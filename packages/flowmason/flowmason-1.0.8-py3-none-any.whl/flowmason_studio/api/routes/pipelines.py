"""
Pipeline API Routes.

Endpoints for managing pipelines:
- Create, read, update, delete pipelines
- List pipelines with filtering
- Validate pipeline configurations

Authentication:
- Read operations: Optional auth (works without, logs when present)
- Write operations: Required auth in production mode
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from flowmason_core.config import PipelineConfig as CorePipelineConfig
from flowmason_core.config import SchemaValidator
from flowmason_core.registry import ComponentRegistry

from flowmason_studio.api.routes.registry import get_registry
from flowmason_studio.auth import AuthContext, get_auth_service, optional_auth
from flowmason_studio.models.api import (
    APIError,
    PipelineCreate,
    PipelineDetail,
    PipelineListResponse,
    PipelineStatus,
    PipelineUpdate,
    PublishPipelineRequest,
    PublishPipelineResponse,
    RunStatus,
    TestPipelineRequest,
    TestPipelineResponse,
    UnpublishPipelineResponse,
)
from flowmason_studio.services.storage import (
    PipelineStorage,
    RunStorage,
    get_pipeline_storage,
    get_run_storage,
)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.post(
    "",
    response_model=PipelineDetail,
    status_code=201,
    summary="Create a new pipeline",
    description="Create a new pipeline configuration."
)
async def create_pipeline(
    pipeline: PipelineCreate,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> PipelineDetail:
    """Create a new pipeline."""
    # Validate that all component types exist
    for stage in pipeline.stages:
        if not registry.has_component(stage.component_type):
            raise HTTPException(
                status_code=400,
                detail=f"Unknown component type: '{stage.component_type}'"
            )

    # Validate stage dependencies
    stage_ids = {s.id for s in pipeline.stages}
    for stage in pipeline.stages:
        for dep in stage.depends_on:
            if dep not in stage_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stage '{stage.id}' depends on unknown stage '{dep}'"
                )

    # Validate output_stage_id if provided
    if pipeline.output_stage_id and pipeline.output_stage_id not in stage_ids:
        raise HTTPException(
            status_code=400,
            detail=f"output_stage_id '{pipeline.output_stage_id}' is not a valid stage"
        )

    # Check for duplicate stage IDs
    if len(stage_ids) != len(pipeline.stages):
        raise HTTPException(
            status_code=400,
            detail="Duplicate stage IDs found"
        )

    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None
    result = storage.create(pipeline, org_id=org_id)

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="pipeline.create",
            resource_type="pipeline",
            resource_id=result.id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"name": pipeline.name},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    return result


@router.get(
    "",
    response_model=PipelineListResponse,
    summary="List pipelines",
    description="List all pipelines with optional filtering."
)
async def list_pipelines(
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    status: Optional[str] = Query(None, description="Filter by status (draft/published)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    storage: PipelineStorage = Depends(get_pipeline_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> PipelineListResponse:
    """List all pipelines."""
    tag_list = tags.split(",") if tags else None
    org_id = auth.org.id if auth else None
    pipelines, total = storage.list(
        category=category,
        tags=tag_list,
        status=status,
        org_id=org_id,
        limit=limit,
        offset=offset
    )

    page = (offset // limit) + 1 if limit > 0 else 1
    has_more = (offset + len(pipelines)) < total

    return PipelineListResponse(
        items=pipelines,
        total=total,
        page=page,
        page_size=limit,
        has_more=has_more,
    )


@router.get(
    "/by-name/{name}",
    response_model=PipelineDetail,
    summary="Get pipeline by name",
    description="Get detailed information about a pipeline by its name.",
    responses={404: {"model": APIError}}
)
async def get_pipeline_by_name(
    name: str,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> PipelineDetail:
    """Get a pipeline by name (used by deploy/pull commands)."""
    org_id = auth.org.id if auth else None
    pipeline = storage.get_by_name(name, org_id=org_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline with name '{name}' not found"
        )
    return pipeline


@router.get(
    "/{pipeline_id}",
    response_model=PipelineDetail,
    summary="Get pipeline details",
    description="Get detailed information about a specific pipeline.",
    responses={404: {"model": APIError}}
)
async def get_pipeline(
    pipeline_id: str,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> PipelineDetail:
    """Get a pipeline by ID."""
    org_id = auth.org.id if auth else None
    pipeline = storage.get(pipeline_id, org_id=org_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found"
        )
    return pipeline


@router.put(
    "/{pipeline_id}",
    response_model=PipelineDetail,
    summary="Update a pipeline",
    description="Update an existing pipeline configuration.",
    responses={404: {"model": APIError}}
)
async def update_pipeline(
    pipeline_id: str,
    update: PipelineUpdate,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> PipelineDetail:
    """Update a pipeline."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    # Check pipeline exists
    existing = storage.get(pipeline_id, org_id=org_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found"
        )

    # Validate component types if stages are being updated
    if update.stages:
        for stage in update.stages:
            if not registry.has_component(stage.component_type):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown component type: '{stage.component_type}'"
                )

        # Validate dependencies
        stage_ids = {s.id for s in update.stages}
        for stage in update.stages:
            for dep in stage.depends_on:
                if dep not in stage_ids:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stage '{stage.id}' depends on unknown stage '{dep}'"
                    )

        # Validate output_stage_id
        output_stage = update.output_stage_id or existing.output_stage_id
        if output_stage and output_stage not in stage_ids:
            raise HTTPException(
                status_code=400,
                detail=f"output_stage_id '{output_stage}' is not a valid stage"
            )

    updated = storage.update(pipeline_id, update, org_id=org_id)
    if not updated:
        raise HTTPException(
            status_code=500,
            detail="Failed to update pipeline"
        )

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="pipeline.update",
            resource_type="pipeline",
            resource_id=pipeline_id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"name": updated.name},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    return updated


@router.delete(
    "/{pipeline_id}",
    status_code=204,
    summary="Delete a pipeline",
    description="Delete a pipeline.",
    responses={404: {"model": APIError}}
)
async def delete_pipeline(
    pipeline_id: str,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> None:
    """Delete a pipeline."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    # Get pipeline info for audit log before deletion
    pipeline = storage.get(pipeline_id, org_id=org_id) if auth else None

    success = storage.delete(pipeline_id, org_id=org_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found"
        )

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="pipeline.delete",
            resource_type="pipeline",
            resource_id=pipeline_id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"name": pipeline.name if pipeline else None},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )


@router.post(
    "/{pipeline_id}/validate",
    summary="Validate a pipeline",
    description="Validate pipeline configuration without executing.",
    responses={404: {"model": APIError}}
)
async def validate_pipeline(
    pipeline_id: str,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> dict:
    """Validate a pipeline configuration."""
    org_id = auth.org.id if auth else None
    pipeline = storage.get(pipeline_id, org_id=org_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found"
        )

    errors = []
    warnings = []

    # Validate each stage
    for stage in pipeline.stages:
        # Check component exists
        if not registry.has_component(stage.component_type):
            errors.append({
                "stage": stage.id,
                "error": f"Unknown component type: '{stage.component_type}'"
            })
            continue

        # Get component Input class for validation
        try:
            ComponentClass = registry.get_component_class(stage.component_type)
            if hasattr(ComponentClass, 'Input'):
                # Build schema validators can validate input_mapping
                _validator = SchemaValidator()  # noqa: F841 - full validation requires runtime context
                # For now, just check that required mappings exist
                input_fields = ComponentClass.Input.model_fields
                for field_name, field_info in input_fields.items():
                    if field_info.is_required() and field_name not in stage.input_mapping:
                        warnings.append({
                            "stage": stage.id,
                            "warning": f"Required field '{field_name}' not in input_mapping"
                        })
        except Exception as e:
            warnings.append({
                "stage": stage.id,
                "warning": f"Could not validate Input schema: {str(e)}"
            })

    # Check output_stage_id
    if pipeline.output_stage_id:
        stage_ids = {s.id for s in pipeline.stages}
        if pipeline.output_stage_id not in stage_ids:
            errors.append({
                "field": "output_stage_id",
                "error": f"'{pipeline.output_stage_id}' is not a valid stage ID"
            })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


@router.post(
    "/{pipeline_id}/clone",
    response_model=PipelineDetail,
    status_code=201,
    summary="Clone a pipeline",
    description="Create a copy of an existing pipeline.",
    responses={404: {"model": APIError}}
)
async def clone_pipeline(
    pipeline_id: str,
    new_name: Optional[str] = Query(None, description="Name for the cloned pipeline"),
    storage: PipelineStorage = Depends(get_pipeline_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> PipelineDetail:
    """Clone a pipeline."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    pipeline = storage.get(pipeline_id, org_id=org_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found"
        )

    # Create a new pipeline with the same config
    clone_data = PipelineCreate(
        name=new_name or f"{pipeline.name} (Copy)",
        description=pipeline.description,
        input_schema=pipeline.input_schema,
        output_schema=pipeline.output_schema,
        stages=pipeline.stages,
        output_stage_id=pipeline.output_stage_id,
        tags=pipeline.tags,
        category=pipeline.category,
        sample_input=pipeline.sample_input,
    )

    result = storage.create(clone_data, org_id=org_id)

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="pipeline.clone",
            resource_type="pipeline",
            resource_id=result.id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"source_id": pipeline_id, "name": result.name},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    return result


@router.post(
    "/{pipeline_id}/publish",
    response_model=PublishPipelineResponse,
    summary="Publish a pipeline",
    description="Publish a pipeline after successful test execution. Only pipelines with a successful test run can be published.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def publish_pipeline(
    pipeline_id: str,
    request: PublishPipelineRequest,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> PublishPipelineResponse:
    """Publish a pipeline after successful test."""

    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    # Check pipeline exists
    pipeline = storage.get(pipeline_id, org_id=org_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found"
        )

    # Check the test run exists and was successful
    test_run = run_storage.get(request.test_run_id, org_id=org_id)
    if not test_run:
        raise HTTPException(
            status_code=400,
            detail=f"Test run '{request.test_run_id}' not found"
        )

    if test_run.pipeline_id != pipeline_id:
        raise HTTPException(
            status_code=400,
            detail=f"Test run '{request.test_run_id}' is not for pipeline '{pipeline_id}'"
        )

    if test_run.status != RunStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Test run must be completed successfully. Current status: {test_run.status}"
        )

    # Publish the pipeline
    updated = storage.publish(pipeline_id, request.test_run_id, org_id=org_id)
    if not updated:
        raise HTTPException(
            status_code=500,
            detail="Failed to publish pipeline"
        )

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="pipeline.publish",
            resource_type="pipeline",
            resource_id=pipeline_id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"name": updated.name, "version": updated.version},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    return PublishPipelineResponse(
        pipeline_id=updated.id,
        status=updated.status,
        published_at=updated.published_at,  # type: ignore[arg-type]
        version=updated.version,
        message=f"Pipeline '{updated.name}' has been published successfully"
    )


@router.post(
    "/{pipeline_id}/unpublish",
    response_model=UnpublishPipelineResponse,
    summary="Unpublish a pipeline",
    description="Revert a published pipeline back to draft state.",
    responses={404: {"model": APIError}}
)
async def unpublish_pipeline(
    pipeline_id: str,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> UnpublishPipelineResponse:
    """Unpublish a pipeline (revert to draft)."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    # Check pipeline exists
    pipeline = storage.get(pipeline_id, org_id=org_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found"
        )

    if pipeline.status != PipelineStatus.PUBLISHED:
        raise HTTPException(
            status_code=400,
            detail=f"Pipeline is not published. Current status: {pipeline.status}"
        )

    # Unpublish the pipeline
    updated = storage.unpublish(pipeline_id, org_id=org_id)
    if not updated:
        raise HTTPException(
            status_code=500,
            detail="Failed to unpublish pipeline"
        )

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="pipeline.unpublish",
            resource_type="pipeline",
            resource_id=pipeline_id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"name": updated.name},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    return UnpublishPipelineResponse(
        pipeline_id=updated.id,
        status=updated.status,
        message=f"Pipeline '{updated.name}' has been reverted to draft"
    )


@router.post(
    "/{pipeline_id}/test",
    response_model=TestPipelineResponse,
    summary="Test a pipeline",
    description="Execute a test run of the pipeline with sample input. This run can be used to publish the pipeline.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def test_pipeline(
    pipeline_id: str,
    request: Optional[TestPipelineRequest] = None,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    run_storage: RunStorage = Depends(get_run_storage),
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> TestPipelineResponse:
    """Test a pipeline with sample input."""
    from flowmason_core.config.types import ComponentConfig
    from flowmason_core.executor import PipelineExecutor

    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    # Check pipeline exists
    pipeline = storage.get(pipeline_id, org_id=org_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found"
        )

    # Determine input to use
    test_input = None
    if request and request.sample_input:
        test_input = request.sample_input
    elif pipeline.sample_input:
        test_input = pipeline.sample_input
    else:
        raise HTTPException(
            status_code=400,
            detail="No sample input provided. Either provide sample_input in request or set it on the pipeline."
        )

    # Create test run
    run = run_storage.create(pipeline_id, test_input, org_id=org_id)
    run_storage.update_status(run.id, "running", org_id=org_id)

    try:
        # Build core pipeline config
        stages = []
        for stage in pipeline.stages:
            stage_config = ComponentConfig(  # type: ignore[call-arg]
                id=stage.id,
                type=stage.component_type,
                input_mapping=stage.input_mapping or {},
                depends_on=stage.depends_on or [],
            )
            stages.append(stage_config)

        core_config = CorePipelineConfig(  # type: ignore[call-arg]
            id=pipeline.id,
            name=pipeline.name,
            stages=stages,
            input_schema=pipeline.input_schema.model_dump() if pipeline.input_schema else None,  # type: ignore[arg-type]
            output_schema=pipeline.output_schema.model_dump() if pipeline.output_schema else None,  # type: ignore[arg-type]
            output_stage_id=pipeline.output_stage_id,
        )

        # Execute
        executor = PipelineExecutor(registry)
        result = await executor.execute(core_config, test_input)

        # Determine success
        is_success = result.status == "completed"

        # Complete the run
        from flowmason_studio.models.api import StageResult
        stage_results = {}
        if result.stage_results:
            for stage_id, stage_res in result.stage_results.items():
                stage_results[stage_id] = StageResult(
                    stage_id=stage_id,
                    status=stage_res.get("status", "unknown"),
                    output=stage_res.get("output"),
                    error=stage_res.get("error"),
                    started_at=stage_res.get("started_at"),
                    completed_at=stage_res.get("completed_at"),
                )

        run_storage.complete_run(
            run.id,
            status="completed" if is_success else "failed",
            output=result.output,
            error=result.error,
            stage_results=stage_results,
            org_id=org_id,
        )

        # Get updated run
        run = run_storage.get(run.id, org_id=org_id)  # type: ignore[assignment]

        # Audit log if authenticated
        if auth:
            auth_service = get_auth_service()
            auth_service.log_action(
                org_id=auth.org.id,
                action="pipeline.test",
                resource_type="pipeline",
                resource_id=pipeline_id,
                api_key_id=auth.api_key.id if auth.api_key else None,
                user_id=auth.user.id if auth.user else None,
                details={"run_id": run.id, "success": is_success},
                ip_address=auth.ip_address,
                user_agent=auth.user_agent,
                success=is_success,
            )

        return TestPipelineResponse(
            run_id=run.id,
            pipeline_id=pipeline_id,
            status=run.status,
            is_success=is_success,
            result=result.output,
            error=result.error,
            can_publish=is_success,
        )

    except Exception as e:
        run_storage.complete_run(run.id, status="failed", error=str(e), org_id=org_id)
        run = run_storage.get(run.id, org_id=org_id)  # type: ignore[assignment]

        # Audit log failure if authenticated
        if auth:
            auth_service = get_auth_service()
            auth_service.log_action(
                org_id=auth.org.id,
                action="pipeline.test",
                resource_type="pipeline",
                resource_id=pipeline_id,
                api_key_id=auth.api_key.id if auth.api_key else None,
                user_id=auth.user.id if auth.user else None,
                details={"run_id": run.id, "error": str(e)},
                ip_address=auth.ip_address,
                user_agent=auth.user_agent,
                success=False,
            )

        return TestPipelineResponse(
            run_id=run.id,
            pipeline_id=pipeline_id,
            status=RunStatus.FAILED,
            is_success=False,
            error=str(e),
            can_publish=False,
        )
