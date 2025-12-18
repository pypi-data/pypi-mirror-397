"""
Execution API Routes.

Endpoints for executing pipelines and tracking runs:
- Execute pipelines with input data
- Get run status and results
- Get execution traces
- Cancel running executions
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from flowmason_core.config import ComponentConfig, ExecutionContext
from flowmason_core.config import PipelineConfig as CorePipelineConfig
from flowmason_core.execution import DAGExecutor, ExecutionError
from flowmason_core.providers import (
    get_provider,
    list_providers,
)
from flowmason_core.registry import ComponentRegistry

from flowmason_studio.api.routes.registry import get_registry
from flowmason_studio.auth import AuthContext, get_auth_service, optional_auth
from flowmason_studio.models.api import (
    APIError,
    DebugRunRequest,
    ExecutePipelineRequest,
    OutputDestination,
    PipelineOutputConfig,
    RunDetail,
    RunListResponse,
    RunPipelineRequest,
    RunPipelineResponse,
    StageResult,
)
from flowmason_studio.models.debug import (
    DebugCommandResponse,
    DebugMode,
    ExceptionBreakpointFilter,
    SetBreakpointsRequest,
    SetExceptionBreakpointsRequest,
)
from flowmason_studio.services.execution_controller import (
    ExecutionController,
    create_controller,
    get_controller,
    remove_controller,
)
from flowmason_studio.services.storage import (
    PipelineStorage,
    RunStorage,
    get_pipeline_storage,
    get_run_storage,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["execution"])

# Mapping of provider names to their environment variable names
PROVIDER_ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
}


def _initialize_providers() -> Dict[str, Any]:
    """
    Initialize all available providers from environment variables.

    Returns dict of provider_name -> provider_instance for providers
    that have valid API keys configured.
    """
    providers = {}

    for provider_name in list_providers():
        env_var = PROVIDER_ENV_VARS.get(provider_name)
        if not env_var:
            continue

        # Check if API key is set
        api_key = os.environ.get(env_var)
        if not api_key:
            logger.debug(f"Provider '{provider_name}' not configured (missing {env_var})")
            continue

        try:
            # Get provider class and instantiate
            ProviderClass = get_provider(provider_name)
            if ProviderClass:
                providers[provider_name] = ProviderClass(api_key=api_key)
                logger.info(f"Initialized provider: {provider_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize provider '{provider_name}': {e}")

    return providers


def _convert_to_core_config(pipeline_detail) -> CorePipelineConfig:
    """Convert Studio pipeline model to Core pipeline config."""
    stages = []
    for stage in pipeline_detail.stages:
        stages.append(ComponentConfig(
            id=stage.id,
            type=stage.component_type,
            input_mapping=stage.config or {},
            depends_on=stage.depends_on or [],
        ))

    # Convert input/output schemas from Pydantic models to dicts if needed
    input_schema = pipeline_detail.input_schema
    if hasattr(input_schema, 'model_dump'):
        input_schema = input_schema.model_dump()
    elif not isinstance(input_schema, dict):
        input_schema = {}

    output_schema = pipeline_detail.output_schema
    if hasattr(output_schema, 'model_dump'):
        output_schema = output_schema.model_dump()
    elif not isinstance(output_schema, dict):
        output_schema = {}

    return CorePipelineConfig(
        id=pipeline_detail.id,
        name=pipeline_detail.name,
        version=pipeline_detail.version,
        description=pipeline_detail.description or "",
        stages=stages,
        output_stage_id=pipeline_detail.output_stage_id,
    )


async def _execute_pipeline_task(
    run_id: str,
    pipeline_detail,
    inputs: Dict[str, Any],
    registry: ComponentRegistry,
    run_storage: RunStorage,
    breakpoints: Optional[list] = None,
    org_id: Optional[str] = None,
):
    """Background task to execute a pipeline."""
    controller: Optional[ExecutionController] = None

    try:
        # Mark as running
        run_storage.update_status(run_id, "running", org_id=org_id)
        logger.info(f"[{run_id}] Starting pipeline execution for {pipeline_detail.name}")

        # Convert to core config
        core_config = _convert_to_core_config(pipeline_detail)
        logger.info(f"[{run_id}] Converted config with {len(core_config.stages)} stages")

        # Initialize providers from environment
        providers = _initialize_providers()
        logger.info(f"[{run_id}] Initialized providers: {list(providers.keys())}")
        for name, prov in providers.items():
            logger.info(f"[{run_id}]   Provider '{name}': {type(prov).__name__} at {id(prov)}")
        if not providers:
            logger.warning("No LLM providers configured. Nodes requiring LLM will fail.")

        # Create execution context with providers
        context = ExecutionContext(
            run_id=run_id,
            pipeline_id=pipeline_detail.id,
            pipeline_version=pipeline_detail.version,
            pipeline_input=inputs,
            providers=providers,
        )

        # Determine default provider (prefer anthropic if available)
        default_provider = None
        if "anthropic" in providers:
            default_provider = "anthropic"
        elif providers:
            default_provider = next(iter(providers.keys()))

        # Create execution controller for debugging/real-time updates
        controller = await create_controller(
            run_id=run_id,
            breakpoints=breakpoints,
            org_id=org_id,
            pipeline_id=pipeline_detail.id,
        )

        # Create executor WITH providers, context, and hooks
        executor = DAGExecutor(
            registry=registry,
            context=context,
            providers=providers,
            default_provider=default_provider,
            hooks=controller,  # type: ignore[arg-type]  # ExecutionController implements ExecutionHooks protocol
        )
        logger.info(f"[{run_id}] Created DAGExecutor")
        logger.info(f"[{run_id}]   executor.context.llm: {executor.context.llm}")
        if executor.context.llm:
            logger.info(f"[{run_id}]   executor.context.llm._provider: {executor.context.llm._provider}")
            logger.info(f"[{run_id}]   executor.context.llm._provider type: {type(executor.context.llm._provider)}")

        # Execute the pipeline stages
        logger.info(f"[{run_id}] Starting DAG execution...")
        stage_results_raw = await executor.execute(
            stages=core_config.stages,
            pipeline_input=inputs,
        )
        logger.info(f"[{run_id}] DAG execution completed with {len(stage_results_raw)} results")

        # Convert ComponentResult objects to StageResult for storage
        stage_results = {}
        final_output = None

        for stage_id, comp_result in stage_results_raw.items():
            stage_results[stage_id] = StageResult(
                stage_id=stage_id,
                status=comp_result.status,
                output=comp_result.output,
                started_at=comp_result.started_at,
                completed_at=comp_result.completed_at,
                duration_ms=int((comp_result.completed_at - comp_result.started_at).total_seconds() * 1000) if comp_result.completed_at and comp_result.started_at else None,
                error=None,
            )

        # Get final output from the output stage
        if core_config.output_stage_id and core_config.output_stage_id in stage_results_raw:
            final_output = stage_results_raw[core_config.output_stage_id].output
        elif stage_results_raw:
            # Use the last stage's output as fallback
            last_stage_id = list(stage_results_raw.keys())[-1]
            final_output = stage_results_raw[last_stage_id].output

        # Update run with success
        run_storage.complete_run(
            run_id=run_id,
            status="completed",
            output=final_output,
            stage_results=stage_results,
            org_id=org_id,
        )

    except ExecutionError as e:
        # Update run with failure
        import sys
        import traceback
        print(f"[{run_id}] ExecutionError: {e}", file=sys.stderr, flush=True)
        print(f"[{run_id}] Traceback:\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        run_storage.complete_run(
            run_id=run_id,
            status="failed",
            error=str(e),
            org_id=org_id,
        )
    except Exception as e:
        # Update run with unexpected error
        import sys
        import traceback
        print(f"[{run_id}] Unexpected error: {e}", file=sys.stderr, flush=True)
        print(f"[{run_id}] Traceback:\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        run_storage.complete_run(
            run_id=run_id,
            status="failed",
            error=f"Unexpected error: {str(e)}",
            org_id=org_id,
        )
    finally:
        # Clean up controller
        if controller:
            await remove_controller(run_id)


@router.post(
    "/pipelines/{pipeline_id}/run",
    response_model=RunDetail,
    status_code=202,
    summary="Execute a pipeline",
    description="Start execution of a pipeline with provided inputs.",
    responses={404: {"model": APIError}}
)
async def execute_pipeline(
    pipeline_id: str,
    request: ExecutePipelineRequest,
    background_tasks: BackgroundTasks,
    pipeline_storage: PipelineStorage = Depends(get_pipeline_storage),
    run_storage: RunStorage = Depends(get_run_storage),
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> RunDetail:
    """Execute a pipeline."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    # Get pipeline
    pipeline = pipeline_storage.get(pipeline_id, org_id=org_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found"
        )

    # Create run record
    run = run_storage.create(
        pipeline_id=pipeline_id,
        inputs=request.inputs,
        org_id=org_id,
    )

    # Schedule background execution
    background_tasks.add_task(
        _execute_pipeline_task,
        run.id,
        pipeline,
        request.inputs,
        registry,
        run_storage,
        None,  # breakpoints
        org_id,
    )

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="run.execute",
            resource_type="run",
            resource_id=run.id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"pipeline_id": pipeline_id, "pipeline_name": pipeline.name},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    return run


@router.post(
    "/debug/run",
    response_model=RunDetail,
    status_code=202,
    summary="Start a debug run from pipeline definition",
    description="Execute a pipeline from inline definition (for VSCode debugging).",
)
async def debug_run(
    request: DebugRunRequest,
    background_tasks: BackgroundTasks,
    run_storage: RunStorage = Depends(get_run_storage),
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> RunDetail:
    """Start a debug run from inline pipeline definition."""
    from flowmason_studio.models.api import PipelineDetail, PipelineStage

    org_id = auth.org.id if auth else None
    pipeline_data = request.pipeline

    # Convert inline pipeline to PipelineDetail
    stages = []
    for stage_data in pipeline_data.get("stages", []):
        stages.append(PipelineStage(
            id=stage_data.get("id"),
            name=stage_data.get("name", stage_data.get("id")),
            component_type=stage_data.get("component_type") or stage_data.get("component"),
            config=stage_data.get("config", {}),
            input_mapping=stage_data.get("input_mapping", {}),
            depends_on=stage_data.get("depends_on", []),
        ))

    now = datetime.now()
    pipeline = PipelineDetail(  # type: ignore[call-arg]
        id=f"debug-{now.strftime('%Y%m%d%H%M%S')}",
        name=pipeline_data.get("name", "Debug Pipeline"),
        version=pipeline_data.get("version", "1.0.0"),
        description=pipeline_data.get("description", "Debug run from VSCode"),
        category=pipeline_data.get("category"),
        tags=pipeline_data.get("tags", []),
        status="draft",  # type: ignore[arg-type]
        stages=stages,
        input_schema=pipeline_data.get("input_schema", {}),
        output_schema=pipeline_data.get("output_schema", {}),
        output_stage_id=pipeline_data.get("output_stage_id"),
        created_at=now,
        updated_at=now,
    )

    # Create run record
    run = run_storage.create(
        pipeline_id=pipeline.id,
        inputs=request.inputs,
        org_id=org_id,
    )

    # Schedule background execution with breakpoints
    background_tasks.add_task(
        _execute_pipeline_task,
        run.id,
        pipeline,
        request.inputs,
        registry,
        run_storage,
        request.breakpoints if request.breakpoints else None,
        org_id,
    )

    return run


@router.get(
    "/runs",
    response_model=RunListResponse,
    summary="List runs",
    description="List all pipeline runs with optional filtering."
)
async def list_runs(
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> RunListResponse:
    """List all runs."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    runs, total = run_storage.list(
        pipeline_id=pipeline_id,
        status=status,
        limit=limit,
        offset=offset,
        org_id=org_id,
    )

    return RunListResponse(
        runs=runs,
        total=total,
    )


@router.get(
    "/runs/{run_id}",
    response_model=RunDetail,
    summary="Get run details",
    description="Get detailed information about a specific run.",
    responses={404: {"model": APIError}}
)
async def get_run(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> RunDetail:
    """Get a run by ID."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found"
        )
    return run


@router.get(
    "/runs/{run_id}/trace",
    summary="Get run trace",
    description="Get detailed execution trace for a run.",
    responses={404: {"model": APIError}}
)
async def get_run_trace(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> dict:
    """Get execution trace for a run."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found"
        )

    # Return trace information
    return {
        "run_id": run.id,
        "pipeline_id": run.pipeline_id,
        "status": run.status,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "duration_ms": run.duration_ms,
        "stages": {
            stage_id: {
                "status": result.status,
                "started_at": result.started_at,
                "completed_at": result.completed_at,
                "duration_ms": result.duration_ms,
                "output": result.output,
                "error": result.error,
            }
            for stage_id, result in (run.stage_results or {}).items()
        },
        "error": run.error,
    }


@router.post(
    "/runs/{run_id}/cancel",
    summary="Cancel a run",
    description="Attempt to cancel a running pipeline execution.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def cancel_run(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> dict:
    """Cancel a running pipeline."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found"
        )

    if run.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel run with status '{run.status}'"
        )

    # Note: Actual cancellation of async task requires more infrastructure
    # For now, just mark as cancelled
    run_storage.update_status(run_id, "cancelled", org_id=org_id)

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="run.cancel",
            resource_type="run",
            resource_id=run_id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"pipeline_id": run.pipeline_id},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    return {
        "run_id": run_id,
        "status": "cancelled",
        "message": "Run cancellation requested"
    }


@router.delete(
    "/runs/{run_id}",
    status_code=204,
    summary="Delete a run",
    description="Delete a run record.",
    responses={404: {"model": APIError}}
)
async def delete_run(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> None:
    """Delete a run."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    # Get run info for audit log before deletion
    run = run_storage.get(run_id, org_id=org_id) if auth else None

    success = run_storage.delete(run_id, org_id=org_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found"
        )

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="run.delete",
            resource_type="run",
            resource_id=run_id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"pipeline_id": run.pipeline_id if run else None},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )


# =============================================================================
# Debug Control Endpoints
# =============================================================================

@router.post(
    "/runs/{run_id}/debug/pause",
    response_model=DebugCommandResponse,
    summary="Pause execution",
    description="Pause a running pipeline execution.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def pause_run(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> DebugCommandResponse:
    """Pause a running pipeline."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    if run.status != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pause run with status '{run.status}'"
        )

    controller = await get_controller(run_id)
    if not controller:
        raise HTTPException(
            status_code=400,
            detail="No active execution controller for this run"
        )

    success = await controller.pause()
    state = controller.get_state()

    return DebugCommandResponse(
        run_id=run_id,
        success=success,
        mode=state.mode,
        message="Execution paused" if success else "Already paused",
        current_stage_id=state.current_stage_id,
        breakpoints=state.breakpoints,
    )


@router.post(
    "/runs/{run_id}/debug/resume",
    response_model=DebugCommandResponse,
    summary="Resume execution",
    description="Resume a paused pipeline execution.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def resume_run(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> DebugCommandResponse:
    """Resume a paused pipeline."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    controller = await get_controller(run_id)
    if not controller:
        raise HTTPException(
            status_code=400,
            detail="No active execution controller for this run"
        )

    success = await controller.resume()
    state = controller.get_state()

    return DebugCommandResponse(
        run_id=run_id,
        success=success,
        mode=state.mode,
        message="Execution resumed" if success else "Not paused",
        current_stage_id=state.current_stage_id,
        breakpoints=state.breakpoints,
    )


@router.post(
    "/runs/{run_id}/debug/step",
    response_model=DebugCommandResponse,
    summary="Step execution",
    description="Execute one stage and then pause.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def step_run(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> DebugCommandResponse:
    """Step through one stage of a pipeline."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    controller = await get_controller(run_id)
    if not controller:
        raise HTTPException(
            status_code=400,
            detail="No active execution controller for this run"
        )

    success = await controller.step()
    state = controller.get_state()

    return DebugCommandResponse(
        run_id=run_id,
        success=success,
        mode=state.mode,
        message="Step mode enabled",
        current_stage_id=state.current_stage_id,
        breakpoints=state.breakpoints,
    )


@router.post(
    "/runs/{run_id}/debug/stop",
    response_model=DebugCommandResponse,
    summary="Stop execution",
    description="Stop pipeline execution entirely.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def stop_run(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> DebugCommandResponse:
    """Stop a running pipeline."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    controller = await get_controller(run_id)
    if not controller:
        # If no controller, just update status
        run_storage.update_status(run_id, "cancelled", org_id=org_id)
        return DebugCommandResponse(
            run_id=run_id,
            success=True,
            mode=DebugMode.STOPPED,
            message="Execution stopped",
            breakpoints=[],
        )

    success = await controller.stop()
    state = controller.get_state()

    return DebugCommandResponse(
        run_id=run_id,
        success=success,
        mode=state.mode,
        message="Execution stopped" if success else "Already stopped",
        current_stage_id=state.current_stage_id,
        breakpoints=state.breakpoints,
    )


@router.put(
    "/runs/{run_id}/debug/breakpoints",
    response_model=DebugCommandResponse,
    summary="Set breakpoints",
    description="Set breakpoints for a run. Replaces all existing breakpoints.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def set_breakpoints(
    run_id: str,
    request: SetBreakpointsRequest,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> DebugCommandResponse:
    """Set breakpoints for a run."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    controller = await get_controller(run_id)
    if not controller:
        raise HTTPException(
            status_code=400,
            detail="No active execution controller for this run"
        )

    await controller.set_breakpoints(request.stage_ids)
    state = controller.get_state()

    return DebugCommandResponse(
        run_id=run_id,
        success=True,
        mode=state.mode,
        message=f"Set {len(request.stage_ids)} breakpoint(s)",
        current_stage_id=state.current_stage_id,
        breakpoints=state.breakpoints,
    )


@router.put(
    "/runs/{run_id}/debug/exception-breakpoints",
    response_model=DebugCommandResponse,
    summary="Set exception breakpoints",
    description="Set exception breakpoints for a run. Configure which exceptions pause execution.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def set_exception_breakpoints(
    run_id: str,
    request: SetExceptionBreakpointsRequest,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> DebugCommandResponse:
    """
    Set exception breakpoints for a run.

    Available filters:
    - 'all': Pause on all errors
    - 'uncaught': Pause on uncaught errors
    - 'error': Pause on ERROR severity
    - 'warning': Pause on WARNING severity
    - 'timeout': Pause on timeout errors
    - 'validation': Pause on validation errors
    - 'connectivity': Pause on connectivity errors
    """
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    controller = await get_controller(run_id)
    if not controller:
        raise HTTPException(
            status_code=400,
            detail="No active execution controller for this run"
        )

    # Validate filters
    valid_filters = {f.value for f in ExceptionBreakpointFilter}
    invalid_filters = [f for f in request.filters if f not in valid_filters]
    if invalid_filters:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid exception filters: {invalid_filters}. Valid filters: {list(valid_filters)}"
        )

    await controller.set_exception_breakpoints(request.filters)
    state = controller.get_state()

    return DebugCommandResponse(
        run_id=run_id,
        success=True,
        mode=state.mode,
        message=f"Set {len(request.filters)} exception breakpoint filter(s)",
        current_stage_id=state.current_stage_id,
        breakpoints=state.breakpoints,
    )


@router.get(
    "/runs/{run_id}/debug/exception-info",
    summary="Get exception info",
    description="Get information about the current exception (if paused due to exception).",
    responses={404: {"model": APIError}}
)
async def get_exception_info(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> dict:
    """Get information about the current exception."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    controller = await get_controller(run_id)
    if not controller:
        return {
            "run_id": run_id,
            "has_exception": False,
            "exception": None,
        }

    exception_info = controller.get_exception_info()

    if exception_info:
        return {
            "run_id": run_id,
            "has_exception": True,
            "exception": exception_info.model_dump(mode='json'),
        }
    else:
        return {
            "run_id": run_id,
            "has_exception": False,
            "exception": None,
        }


@router.get(
    "/runs/{run_id}/debug/state",
    response_model=DebugCommandResponse,
    summary="Get debug state",
    description="Get current debug state for a run.",
    responses={404: {"model": APIError}}
)
async def get_debug_state(
    run_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> DebugCommandResponse:
    """Get debug state for a run."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    controller = await get_controller(run_id)
    if not controller:
        # Return default state if no controller
        return DebugCommandResponse(
            run_id=run_id,
            success=True,
            mode=DebugMode.RUNNING if run.status == "running" else DebugMode.STOPPED,
            message="No active debug session",
            breakpoints=[],
        )

    state = controller.get_state()

    return DebugCommandResponse(
        run_id=run_id,
        success=True,
        mode=state.mode,
        message="Debug state retrieved",
        current_stage_id=state.current_stage_id,
        breakpoints=state.breakpoints,
    )


@router.get(
    "/runs/{run_id}/debug/stage/{stage_id}/prompt",
    summary="Get stage prompt info",
    description="Get prompt information for an LLM stage.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def get_stage_prompt(
    run_id: str,
    stage_id: str,
    run_storage: RunStorage = Depends(get_run_storage),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> dict:
    """Get prompt information for a stage."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    controller = await get_controller(run_id)
    if not controller:
        raise HTTPException(
            status_code=400,
            detail="No active execution controller for this run"
        )

    # Get stage info from controller
    stage_info = controller.get_stage_info(stage_id)
    if not stage_info:
        raise HTTPException(status_code=404, detail=f"Stage '{stage_id}' not found")

    # Return prompt info
    return {
        "run_id": run_id,
        "stage_id": stage_id,
        "stage_name": stage_info.get("name", stage_id),
        "component_type": stage_info.get("component_type", "unknown"),
        "system_prompt": stage_info.get("system_prompt", ""),
        "user_prompt": stage_info.get("user_prompt", ""),
        "variables": stage_info.get("variables", {}),
        "input": stage_info.get("input", {}),
        "output": stage_info.get("output"),
    }


@router.post(
    "/runs/{run_id}/debug/stage/{stage_id}/rerun",
    summary="Re-run a stage with modified prompt",
    description="Re-execute a single stage with modified prompts.",
    responses={404: {"model": APIError}, 400: {"model": APIError}}
)
async def rerun_stage(
    run_id: str,
    stage_id: str,
    request: dict,
    run_storage: RunStorage = Depends(get_run_storage),
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> dict:
    """Re-run a stage with modified prompts."""
    # Pass org_id from auth context for multi-tenancy
    org_id = auth.org.id if auth else None

    run = run_storage.get(run_id, org_id=org_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    controller = await get_controller(run_id)
    if not controller:
        raise HTTPException(
            status_code=400,
            detail="No active execution controller for this run"
        )

    # Get the modified prompts from request
    system_prompt = request.get("system_prompt")
    user_prompt = request.get("user_prompt")

    try:
        # Re-execute the stage with modified prompts
        result = await controller.rerun_stage(
            stage_id=stage_id,
            registry=registry,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        return {
            "run_id": run_id,
            "stage_id": stage_id,
            "success": True,
            "output": result.get("output"),
            "tokens": result.get("tokens"),
            "duration_ms": result.get("duration_ms"),
        }

    except Exception as e:
        logger.error(f"Failed to re-run stage {stage_id}: {e}")
        return {
            "run_id": run_id,
            "stage_id": stage_id,
            "success": False,
            "error": str(e),
        }


# =============================================================================
# Named Pipeline Execution (Public API)
# =============================================================================

def _parse_pipeline_reference(pipeline_ref: str) -> tuple[str, Optional[str]]:
    """Parse a pipeline reference like 'my-pipeline@1.0.0' into (name, version).

    Returns:
        Tuple of (pipeline_name, version) where version may be None.
    """
    if "@" in pipeline_ref:
        parts = pipeline_ref.split("@", 1)
        return parts[0], parts[1]
    return pipeline_ref, None


def _merge_output_configs(
    designer_config: Optional[PipelineOutputConfig],
    caller_config: Optional[PipelineOutputConfig]
) -> PipelineOutputConfig:
    """Merge designer defaults with caller overrides.

    Logic:
    - If caller provides config and designer allows override, use caller's config entirely
    - If caller provides config and designer allows caller destinations, extend designer's
    - Otherwise, use designer's config

    Returns:
        Merged PipelineOutputConfig
    """
    if not designer_config:
        designer_config = PipelineOutputConfig()

    if not caller_config:
        return designer_config

    # If designer allows complete override
    if designer_config.allow_caller_override:
        return caller_config

    # If designer allows adding caller destinations, merge them
    if designer_config.allow_caller_destinations:
        merged_destinations = list(designer_config.destinations)

        # Add caller destinations (avoid duplicates by ID)
        existing_ids = {d.id for d in merged_destinations}
        for dest in caller_config.destinations:
            if dest.id not in existing_ids:
                merged_destinations.append(dest)

        return PipelineOutputConfig(
            destinations=merged_destinations,
            allow_caller_destinations=designer_config.allow_caller_destinations,
            allow_caller_override=designer_config.allow_caller_override,
        )

    # Designer doesn't allow caller destinations, return designer's config
    return designer_config


@router.post(
    "/run",
    response_model=RunPipelineResponse,
    status_code=202,
    summary="Run pipeline by name",
    description="""
Execute a pipeline by name with optional output configuration.

This is the primary API for external systems to invoke FlowMason pipelines.

**Pipeline Reference:**
- `my-pipeline` - Use latest version
- `my-pipeline@1.0.0` - Use specific version

**Output Configuration:**
The caller can specify output destinations (webhooks, email, etc.) that will
be merged with the pipeline's default configuration. All destinations are
validated against the organization's allowlist.

**Async vs Sync:**
- `async_mode=true` (default): Returns immediately with run_id
- `async_mode=false`: Waits for completion and returns result
""",
    responses={404: {"model": APIError}, 403: {"model": APIError}}
)
async def run_pipeline_by_name(
    request: RunPipelineRequest,
    background_tasks: BackgroundTasks,
    pipeline_storage: PipelineStorage = Depends(get_pipeline_storage),
    run_storage: RunStorage = Depends(get_run_storage),
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> RunPipelineResponse:
    """Run a pipeline by name with optional output configuration."""
    from flowmason_studio.models.allowlist import AllowlistValidationRequest
    from flowmason_studio.services import allowlist_storage

    org_id = auth.org.id if auth else None

    # Parse pipeline reference
    pipeline_name, pipeline_version = _parse_pipeline_reference(request.pipeline)

    # Look up pipeline by name
    pipeline = pipeline_storage.get_by_name(pipeline_name, org_id=org_id)
    if not pipeline:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_name}' not found"
        )

    # Check version if specified
    if pipeline_version and pipeline.version != pipeline_version:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_name}' version '{pipeline_version}' not found (available: {pipeline.version})"
        )

    # Get designer's output config from pipeline
    designer_config = None
    if hasattr(pipeline, 'output_config') and pipeline.output_config:
        if isinstance(pipeline.output_config, dict):
            designer_config = PipelineOutputConfig(**pipeline.output_config)
        elif isinstance(pipeline.output_config, PipelineOutputConfig):
            designer_config = pipeline.output_config

    # Merge output configs
    merged_config = _merge_output_configs(designer_config, request.output_config)

    # Handle callback_url shorthand (creates a webhook destination)
    if request.callback_url:
        callback_dest = OutputDestination(
            id="callback",
            type="webhook",  # type: ignore[arg-type]
            name="Callback URL",
            enabled=True,
            config={"url": request.callback_url, "method": "POST"},
            on_success=True,
            on_error=True,
        )
        merged_config.destinations.append(callback_dest)

    # Validate all destinations against allowlist
    if org_id and merged_config.destinations:
        for dest in merged_config.destinations:
            if not dest.enabled:
                continue

            # Determine validation value based on destination type
            if dest.type == "webhook":
                validation_value = dest.config.get("url", "")
            elif dest.type == "email":
                # For email, validate the domain
                to_list = dest.config.get("to", [])
                if to_list:
                    validation_value = to_list[0]  # Validate first recipient
                else:
                    continue
            elif dest.type in ("database", "message_queue"):
                validation_value = dest.config.get("connection_id", "")
            else:
                continue

            validation_req = AllowlistValidationRequest(
                destination_type=dest.type,
                destination_value=validation_value
            )
            result = allowlist_storage.validate_destination(org_id, validation_req)

            if not result.is_allowed:
                raise HTTPException(
                    status_code=403,
                    detail=f"Output destination '{dest.name}' ({dest.type}) rejected: {result.reason}"
                )

    # Create run record
    run = run_storage.create(
        pipeline_id=pipeline.id,
        inputs=request.input,
        org_id=org_id,
    )

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="run.execute_by_name",
            resource_type="run",
            resource_id=run.id,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={
                "pipeline_name": pipeline_name,
                "pipeline_id": pipeline.id,
                "output_destinations": len(merged_config.destinations),
            },
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    if request.async_mode:
        # Schedule background execution
        background_tasks.add_task(
            _execute_pipeline_with_routing,
            run.id,
            pipeline,
            request.input,
            registry,
            run_storage,
            merged_config,
            org_id,
        )

        return RunPipelineResponse(
            run_id=run.id,
            pipeline_id=pipeline.id,
            pipeline_name=pipeline.name,
            pipeline_version=pipeline.version,
            status=run.status,
            message="Pipeline execution started",
        )
    else:
        # Synchronous execution - wait for completion
        await _execute_pipeline_with_routing(
            run.id,
            pipeline,
            request.input,
            registry,
            run_storage,
            merged_config,
            org_id,
        )

        # Get updated run
        completed_run = run_storage.get(run.id, org_id=org_id)

        # Get delivery report if there were destinations
        delivery_report = None
        if merged_config.destinations:
            from flowmason_studio.models.api import OutputDeliveryReport
            deliveries = allowlist_storage.get_deliveries_for_run(run.id)
            if deliveries:
                successful = sum(1 for d in deliveries if d.status == "success")
                delivery_report = OutputDeliveryReport(
                    run_id=run.id,
                    total_destinations=len(deliveries),
                    successful_deliveries=successful,
                    failed_deliveries=len(deliveries) - successful,
                    results=[],  # Simplified for now
                )

        return RunPipelineResponse(
            run_id=run.id,
            pipeline_id=pipeline.id,
            pipeline_name=pipeline.name,
            pipeline_version=pipeline.version,
            status=completed_run.status if completed_run else run.status,
            result=completed_run.output if completed_run else None,
            error=completed_run.error if completed_run else None,
            delivery_report=delivery_report,
            message="Pipeline execution completed" if completed_run and completed_run.status == "completed" else "Pipeline execution failed",
        )


async def _execute_pipeline_with_routing(
    run_id: str,
    pipeline_detail,
    inputs: Dict[str, Any],
    registry: ComponentRegistry,
    run_storage: RunStorage,
    output_config: PipelineOutputConfig,
    org_id: Optional[str] = None,
):
    """Execute a pipeline with output routing to configured destinations."""

    try:
        # Execute the pipeline (reuse existing execution logic)
        await _execute_pipeline_task(
            run_id=run_id,
            pipeline_detail=pipeline_detail,
            inputs=inputs,
            registry=registry,
            run_storage=run_storage,
            breakpoints=None,
            org_id=org_id,
        )

        # Get the completed run
        run = run_storage.get(run_id, org_id=org_id)
        is_success = run and run.status == "completed"

        # Route output to destinations
        for dest in output_config.destinations:
            if not dest.enabled:
                continue

            # Check if we should deliver based on success/error
            should_deliver = False
            if is_success and dest.on_success:
                should_deliver = True
            elif not is_success and dest.on_error:
                # Check error type filtering
                if dest.error_types:
                    # TODO: Check if run.error matches any of the error types
                    should_deliver = True
                else:
                    should_deliver = True

            if should_deliver:
                await _deliver_to_destination(
                    run_id=run_id,
                    destination=dest,
                    output=run.output if run else None,
                    error=run.error if run else None,
                    org_id=org_id,
                )

    except Exception as e:
        logger.error(f"[{run_id}] Error in pipeline execution with routing: {e}")
        # Run was already marked as failed by _execute_pipeline_task
        # Try to deliver error to error destinations
        for dest in output_config.destinations:
            if dest.enabled and dest.on_error:
                try:
                    await _deliver_to_destination(
                        run_id=run_id,
                        destination=dest,
                        output=None,
                        error=str(e),
                        org_id=org_id,
                    )
                except Exception as delivery_error:
                    logger.error(f"[{run_id}] Failed to deliver error to {dest.name}: {delivery_error}")


async def _deliver_to_destination(
    run_id: str,
    destination: OutputDestination,
    output: Any,
    error: Optional[str],
    org_id: Optional[str] = None,
):
    """Deliver output to a single destination."""
    import json

    import httpx

    from flowmason_studio.services import allowlist_storage

    # Log delivery start
    delivery_id = allowlist_storage.log_delivery_start(
        run_id=run_id,
        destination_id=destination.id,
        destination_type=destination.type,
        destination_name=destination.name,
    )

    try:
        # Prepare payload
        payload = {
            "run_id": run_id,
            "status": "completed" if not error else "failed",
            "output": output,
            "error": error,
        }

        # Apply payload template if specified
        if destination.payload_template:
            # TODO: Implement Jinja2 template rendering
            pass

        payload_json = json.dumps(payload, default=str)
        payload_size = len(payload_json.encode('utf-8'))

        if destination.type == "webhook":
            # Deliver via HTTP
            url = destination.config.get("url")
            method = destination.config.get("method", "POST").upper()
            headers = destination.config.get("headers", {})
            timeout = destination.config.get("timeout_ms", 30000) / 1000

            headers["Content-Type"] = "application/json"

            async with httpx.AsyncClient() as client:
                if method == "POST":
                    response = await client.post(
                        url,  # type: ignore[arg-type]
                        content=payload_json,
                        headers=headers,
                        timeout=timeout,
                    )
                elif method == "PUT":
                    response = await client.put(
                        url,  # type: ignore[arg-type]
                        content=payload_json,
                        headers=headers,
                        timeout=timeout,
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                allowlist_storage.log_delivery_success(
                    delivery_id=delivery_id,
                    response_code=response.status_code,
                    response_body=response.text[:1000] if response.text else None,
                    payload_size=payload_size,
                )

        elif destination.type == "email":
            # TODO: Implement email delivery
            logger.warning(f"Email delivery not yet implemented for {destination.name}")
            allowlist_storage.log_delivery_failure(
                delivery_id=delivery_id,
                error_message="Email delivery not yet implemented",
            )

        elif destination.type == "database":
            # TODO: Implement database delivery
            logger.warning(f"Database delivery not yet implemented for {destination.name}")
            allowlist_storage.log_delivery_failure(
                delivery_id=delivery_id,
                error_message="Database delivery not yet implemented",
            )

        elif destination.type == "message_queue":
            # TODO: Implement message queue delivery
            logger.warning(f"Message queue delivery not yet implemented for {destination.name}")
            allowlist_storage.log_delivery_failure(
                delivery_id=delivery_id,
                error_message="Message queue delivery not yet implemented",
            )

    except httpx.HTTPError as e:
        logger.error(f"HTTP error delivering to {destination.name}: {e}")
        response_code = None
        if hasattr(e, 'response') and e.response is not None:
            response_code = getattr(e.response, 'status_code', None)
        allowlist_storage.log_delivery_failure(
            delivery_id=delivery_id,
            error_message=str(e),
            response_code=response_code,
        )
    except Exception as e:
        logger.error(f"Error delivering to {destination.name}: {e}")
        allowlist_storage.log_delivery_failure(
            delivery_id=delivery_id,
            error_message=str(e),
        )
