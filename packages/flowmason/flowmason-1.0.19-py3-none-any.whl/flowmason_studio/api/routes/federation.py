"""
Federation API Routes for FlowMason Studio.

API endpoints for managing federated execution.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from flowmason_core.federation import (
    FederationCoordinator,
    FederationConfig,
    FederationStrategy,
    AggregationStrategy,
    RegionConfig,
    FederatedStageConfig,
)

router = APIRouter(prefix="/federation", tags=["federation"])

# Global coordinator instance (initialized by app)
_coordinator: Optional[FederationCoordinator] = None


def get_coordinator() -> FederationCoordinator:
    """Get federation coordinator."""
    if _coordinator is None:
        raise HTTPException(status_code=503, detail="Federation not configured")
    return _coordinator


def init_coordinator(config: FederationConfig) -> FederationCoordinator:
    """Initialize federation coordinator."""
    global _coordinator
    _coordinator = FederationCoordinator(config)
    return _coordinator


# Request/Response models


class RegionConfigModel(BaseModel):
    """Region configuration."""
    name: str
    endpoint: str
    api_key: str
    priority: int = 0
    weight: float = 1.0
    max_concurrent: int = 10
    timeout_seconds: int = 300
    enabled: bool = True
    cost_per_execution: float = 0.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FederatedExecuteRequest(BaseModel):
    """Request for federated execution."""
    stage: Dict[str, Any]
    inputs: Dict[str, Any]
    strategy: str = "parallel"
    regions: List[str] = []
    aggregation: str = "merge"
    min_regions: int = 1
    timeout_seconds: int = 300


class FederatedExecuteResponse(BaseModel):
    """Response from federated execution."""
    success: bool
    output: Any
    total_latency_ms: int
    total_cost: float
    regions_completed: List[str]
    regions_failed: List[str]
    error: Optional[str] = None


class RegionStatusResponse(BaseModel):
    """Region status response."""
    name: str
    enabled: bool
    status: str
    last_heartbeat: Optional[str]
    current_load: float
    avg_latency_ms: float
    success_rate: float
    total_executions: int


# Endpoints


@router.get("/status")
async def get_federation_status() -> Dict[str, Any]:
    """Get federation status."""
    coordinator = get_coordinator()

    region_status = coordinator.get_region_status()

    return {
        "enabled": True,
        "regions": len(region_status),
        "online_regions": sum(
            1 for r in region_status.values()
            if r.get("status") == "online"
        ),
        "region_details": region_status,
    }


@router.get("/regions")
async def list_regions() -> List[RegionStatusResponse]:
    """List all configured regions."""
    coordinator = get_coordinator()
    status = coordinator.get_region_status()

    return [
        RegionStatusResponse(
            name=name,
            enabled=info.get("enabled", False),
            status=info.get("status", "unknown"),
            last_heartbeat=info.get("last_heartbeat"),
            current_load=info.get("current_load", 0),
            avg_latency_ms=info.get("avg_latency_ms", 0),
            success_rate=info.get("success_rate", 1.0),
            total_executions=info.get("total_executions", 0),
        )
        for name, info in status.items()
    ]


@router.post("/regions")
async def add_region(config: RegionConfigModel) -> Dict[str, str]:
    """Add a new region."""
    coordinator = get_coordinator()

    region = RegionConfig(
        name=config.name,
        endpoint=config.endpoint,
        api_key=config.api_key,
        priority=config.priority,
        weight=config.weight,
        max_concurrent=config.max_concurrent,
        timeout_seconds=config.timeout_seconds,
        enabled=config.enabled,
        cost_per_execution=config.cost_per_execution,
        latitude=config.latitude,
        longitude=config.longitude,
    )

    coordinator.add_region(region)

    return {"status": "added", "region": config.name}


@router.delete("/regions/{name}")
async def remove_region(name: str) -> Dict[str, str]:
    """Remove a region."""
    coordinator = get_coordinator()
    coordinator.remove_region(name)
    return {"status": "removed", "region": name}


@router.post("/execute")
async def execute_federated(
    request: FederatedExecuteRequest,
) -> FederatedExecuteResponse:
    """Execute a stage across federated regions."""
    coordinator = get_coordinator()

    try:
        strategy = FederationStrategy(request.strategy)
    except ValueError:
        strategy = FederationStrategy.PARALLEL

    try:
        aggregation = AggregationStrategy(request.aggregation)
    except ValueError:
        aggregation = AggregationStrategy.MERGE

    federation = FederatedStageConfig(
        strategy=strategy,
        regions=request.regions,
        aggregation=aggregation,
        min_regions=request.min_regions,
        timeout_seconds=request.timeout_seconds,
    )

    result = await coordinator.execute_federated(
        stage=request.stage,
        inputs=request.inputs,
        federation=federation,
    )

    return FederatedExecuteResponse(
        success=result.success,
        output=result.output,
        total_latency_ms=result.total_latency_ms,
        total_cost=result.total_cost,
        regions_completed=list(
            r.region for r in result.region_results.values() if r.success
        ),
        regions_failed=list(
            r.region for r in result.region_results.values() if not r.success
        ),
        error=result.error,
    )


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str) -> Dict[str, Any]:
    """Get execution details."""
    coordinator = get_coordinator()
    execution = coordinator.get_execution(execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return {
        "id": execution.id,
        "pipeline_name": execution.pipeline_name,
        "stage_id": execution.stage_id,
        "strategy": execution.strategy.value,
        "started_at": execution.started_at.isoformat(),
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "regions_targeted": execution.regions_targeted,
        "regions_completed": execution.regions_completed,
        "regions_failed": execution.regions_failed,
        "error": execution.error,
    }


@router.get("/strategies")
async def list_strategies() -> Dict[str, Any]:
    """List available federation strategies."""
    return {
        "strategies": [
            {
                "name": strategy.value,
                "description": _get_strategy_description(strategy),
            }
            for strategy in FederationStrategy
        ],
        "aggregations": [
            {
                "name": agg.value,
                "description": _get_aggregation_description(agg),
            }
            for agg in AggregationStrategy
        ],
    }


def _get_strategy_description(strategy: FederationStrategy) -> str:
    """Get description for a strategy."""
    descriptions = {
        FederationStrategy.PARALLEL: "Execute on all regions simultaneously",
        FederationStrategy.SEQUENTIAL: "Execute on regions in order",
        FederationStrategy.NEAREST: "Route to nearest region by latency",
        FederationStrategy.ROUND_ROBIN: "Distribute evenly across regions",
        FederationStrategy.LOAD_BASED: "Route based on current load",
        FederationStrategy.COST_BASED: "Route to cheapest region",
    }
    return descriptions.get(strategy, "Unknown strategy")


def _get_aggregation_description(agg: AggregationStrategy) -> str:
    """Get description for an aggregation."""
    descriptions = {
        AggregationStrategy.MERGE: "Merge all results into one object",
        AggregationStrategy.REDUCE: "Apply reduction function",
        AggregationStrategy.FIRST: "Use first successful result",
        AggregationStrategy.CONCAT: "Concatenate array results",
        AggregationStrategy.VOTE: "Majority voting for classification",
        AggregationStrategy.BEST: "Select best result by score",
    }
    return descriptions.get(agg, "Unknown aggregation")
