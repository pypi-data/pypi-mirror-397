"""
Multi-Region Deployment API Routes.

Provides HTTP API for multi-region pipeline deployments.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from flowmason_studio.models.multi_region import (
    AddRegionRequest,
    CreateDeploymentRequest,
    DeploymentListResponse,
    DeploymentStatus,
    FailoverEvent,
    FailoverRequest,
    GlobalMetrics,
    PipelineDeployment,
    Region,
    RegionDeployment,
    RegionEndpoint,
    RegionListResponse,
    RegionMetrics,
    RegionStatus,
    RemoveRegionRequest,
    ScaleRegionRequest,
    UpdateDeploymentRequest,
)
from flowmason_studio.services.multi_region_service import get_multi_region_service

router = APIRouter(prefix="/multi-region", tags=["multi-region"])


# =============================================================================
# Regions
# =============================================================================


@router.get("/regions", response_model=RegionListResponse)
async def list_regions(
    status: Optional[RegionStatus] = Query(None, description="Filter by status"),
    supports_gpu: Optional[bool] = Query(None, description="Filter by GPU support"),
) -> RegionListResponse:
    """
    List all available regions.

    Regions are geographic locations where pipelines can be deployed.
    """
    service = get_multi_region_service()
    regions = service.list_regions(status=status, supports_gpu=supports_gpu)

    return RegionListResponse(
        regions=regions,
        total=len(regions),
    )


@router.get("/regions/{region_id}", response_model=Region)
async def get_region(region_id: str) -> Region:
    """
    Get details of a specific region.
    """
    service = get_multi_region_service()
    region = service.get_region(region_id)

    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    return region


@router.get("/regions/{region_id}/endpoint", response_model=RegionEndpoint)
async def get_region_endpoint(region_id: str) -> RegionEndpoint:
    """
    Get the API endpoint for a region.
    """
    service = get_multi_region_service()
    endpoint = service.get_region_endpoint(region_id)

    if not endpoint:
        raise HTTPException(status_code=404, detail="Region not found")

    return endpoint


@router.get("/regions/nearest", response_model=Region)
async def find_nearest_region(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    exclude: Optional[List[str]] = Query(None, description="Regions to exclude"),
) -> Region:
    """
    Find the nearest active region to a geographic location.
    """
    service = get_multi_region_service()
    region = service.find_nearest_region(latitude, longitude, exclude)

    if not region:
        raise HTTPException(status_code=404, detail="No active regions found")

    return region


# =============================================================================
# Deployments
# =============================================================================


@router.post("/deployments", response_model=PipelineDeployment)
async def create_deployment(request: CreateDeploymentRequest) -> PipelineDeployment:
    """
    Create a new multi-region deployment.

    Deploys a pipeline to multiple regions based on the configuration.
    """
    service = get_multi_region_service()

    # TODO: Get actual user from auth context
    user_id = "user_deployer"

    try:
        return service.create_deployment(
            pipeline_id=request.pipeline_id,
            user_id=user_id,
            config=request.config,
            pipeline_version=request.pipeline_version or "latest",
            name=request.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/deployments", response_model=DeploymentListResponse)
async def list_deployments(
    pipeline_id: Optional[str] = Query(None),
    status: Optional[DeploymentStatus] = Query(None),
) -> DeploymentListResponse:
    """
    List all multi-region deployments.
    """
    service = get_multi_region_service()
    deployments = service.list_deployments(pipeline_id=pipeline_id, status=status)

    return DeploymentListResponse(
        deployments=deployments,
        total=len(deployments),
    )


@router.get("/deployments/{deployment_id}", response_model=PipelineDeployment)
async def get_deployment(deployment_id: str) -> PipelineDeployment:
    """
    Get details of a deployment.
    """
    service = get_multi_region_service()
    deployment = service.get_deployment(deployment_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment


@router.patch("/deployments/{deployment_id}", response_model=PipelineDeployment)
async def update_deployment(
    deployment_id: str,
    request: UpdateDeploymentRequest,
) -> PipelineDeployment:
    """
    Update a deployment configuration.
    """
    service = get_multi_region_service()

    deployment = service.update_deployment(
        deployment_id=deployment_id,
        config=request.config,
        pipeline_version=request.pipeline_version,
    )

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment


@router.post("/deployments/{deployment_id}/stop")
async def stop_deployment(deployment_id: str) -> dict:
    """
    Stop a deployment.

    This stops the pipeline in all regions.
    """
    service = get_multi_region_service()

    success = service.stop_deployment(deployment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return {"success": True, "message": "Deployment stopped"}


@router.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: str) -> dict:
    """
    Delete a deployment.
    """
    service = get_multi_region_service()

    success = service.delete_deployment(deployment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return {"success": True}


# =============================================================================
# Region Management within Deployment
# =============================================================================


@router.post("/deployments/{deployment_id}/regions", response_model=RegionDeployment)
async def add_region(
    deployment_id: str,
    request: AddRegionRequest,
) -> RegionDeployment:
    """
    Add a new region to an existing deployment.
    """
    service = get_multi_region_service()

    region_dep = service.add_region_to_deployment(
        deployment_id=deployment_id,
        region_id=request.region_id,
        replicas=request.replicas,
    )

    if not region_dep:
        raise HTTPException(
            status_code=400,
            detail="Cannot add region (deployment not found or region already exists)"
        )

    return region_dep


@router.delete("/deployments/{deployment_id}/regions/{region_id}")
async def remove_region(
    deployment_id: str,
    region_id: str,
) -> dict:
    """
    Remove a region from a deployment.

    Cannot remove the primary region.
    """
    service = get_multi_region_service()

    success = service.remove_region_from_deployment(deployment_id, region_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove region (not found or is primary region)"
        )

    return {"success": True}


@router.put("/deployments/{deployment_id}/regions/{region_id}/scale", response_model=RegionDeployment)
async def scale_region(
    deployment_id: str,
    region_id: str,
    request: ScaleRegionRequest,
) -> RegionDeployment:
    """
    Scale replicas in a specific region.
    """
    service = get_multi_region_service()

    region_dep = service.scale_region(
        deployment_id=deployment_id,
        region_id=region_id,
        replicas=request.replicas,
    )

    if not region_dep:
        raise HTTPException(status_code=404, detail="Deployment or region not found")

    return region_dep


# =============================================================================
# Failover
# =============================================================================


@router.post("/deployments/{deployment_id}/failover", response_model=FailoverEvent)
async def trigger_failover(
    deployment_id: str,
    request: FailoverRequest,
) -> FailoverEvent:
    """
    Trigger a manual failover from one region to another.
    """
    service = get_multi_region_service()

    event = service.trigger_failover(
        deployment_id=deployment_id,
        from_region=request.from_region,
        to_region=request.to_region,
        reason=request.reason,
    )

    if not event:
        raise HTTPException(
            status_code=400,
            detail="Cannot failover (deployment or regions not found)"
        )

    return event


@router.get("/deployments/{deployment_id}/failover-events", response_model=List[FailoverEvent])
async def get_failover_events(
    deployment_id: str,
    limit: int = Query(50, ge=1, le=500),
) -> List[FailoverEvent]:
    """
    Get failover event history for a deployment.
    """
    service = get_multi_region_service()
    return service.get_failover_events(deployment_id, limit)


# =============================================================================
# Routing
# =============================================================================


@router.get("/deployments/{deployment_id}/route")
async def resolve_route(
    deployment_id: str,
    source_region: Optional[str] = Query(None),
    source_country: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
) -> dict:
    """
    Resolve which region a request should be routed to.

    Uses the deployment's routing strategy and rules.
    """
    service = get_multi_region_service()

    region_id = service.resolve_region(
        deployment_id=deployment_id,
        source_region=source_region,
        source_country=source_country,
        latitude=latitude,
        longitude=longitude,
    )

    if not region_id:
        raise HTTPException(status_code=404, detail="No healthy region found")

    endpoint = service.get_region_endpoint(region_id)

    return {
        "region_id": region_id,
        "endpoint": endpoint.model_dump() if endpoint else None,
    }


# =============================================================================
# Metrics
# =============================================================================


@router.get("/deployments/{deployment_id}/metrics", response_model=GlobalMetrics)
async def get_global_metrics(deployment_id: str) -> GlobalMetrics:
    """
    Get global metrics across all regions in a deployment.
    """
    service = get_multi_region_service()

    metrics = service.get_global_metrics(deployment_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return metrics


@router.get("/deployments/{deployment_id}/regions/{region_id}/metrics", response_model=RegionMetrics)
async def get_region_metrics(deployment_id: str, region_id: str) -> RegionMetrics:
    """
    Get metrics for a specific region in a deployment.
    """
    service = get_multi_region_service()

    metrics = service.get_region_metrics(deployment_id, region_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Deployment or region not found")

    return metrics


# =============================================================================
# Health Checks
# =============================================================================


@router.post("/deployments/{deployment_id}/regions/{region_id}/health-check")
async def run_health_check(deployment_id: str, region_id: str) -> dict:
    """
    Run a health check for a specific region.
    """
    service = get_multi_region_service()

    healthy, message = service.run_health_check(deployment_id, region_id)

    return {
        "healthy": healthy,
        "message": message,
        "region_id": region_id,
    }
