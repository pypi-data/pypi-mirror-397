"""
Multi-Region Deployment Models.

Models for deploying pipelines across multiple geographic regions.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RegionStatus(str, Enum):
    """Status of a region."""

    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class DeploymentStatus(str, Enum):
    """Status of a deployment."""

    PENDING = "pending"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    STOPPED = "stopped"


class RoutingStrategy(str, Enum):
    """Traffic routing strategies."""

    LATENCY = "latency"  # Route to lowest latency region
    GEOLOCATION = "geolocation"  # Route based on user location
    WEIGHTED = "weighted"  # Distribute by weight
    FAILOVER = "failover"  # Primary with failover
    ROUND_ROBIN = "round_robin"  # Equal distribution


class HealthCheckType(str, Enum):
    """Types of health checks."""

    HTTP = "http"
    TCP = "tcp"
    PIPELINE = "pipeline"  # Run a test pipeline


class Region(BaseModel):
    """A geographic region for deployment."""

    id: str
    name: str
    code: str = Field(description="Region code like us-east-1, eu-west-1")
    location: str = Field(description="Geographic location")
    provider: str = Field(default="flowmason", description="Infrastructure provider")

    # Status
    status: RegionStatus = RegionStatus.ACTIVE
    status_message: Optional[str] = None

    # Capabilities
    supports_gpu: bool = False
    max_concurrent_runs: int = Field(default=100)
    available_providers: List[str] = Field(
        default_factory=lambda: ["openai", "anthropic"],
        description="LLM providers available in this region"
    )

    # Metrics
    current_load: float = Field(default=0.0, ge=0, le=1)
    average_latency_ms: float = Field(default=0.0, ge=0)
    uptime_percentage: float = Field(default=100.0, ge=0, le=100)

    # Coordinates for geolocation routing
    latitude: float = 0.0
    longitude: float = 0.0


class RegionEndpoint(BaseModel):
    """Endpoint information for a region."""

    region_id: str
    api_url: str
    ws_url: Optional[str] = None
    health_check_url: str


class HealthCheck(BaseModel):
    """Health check configuration."""

    type: HealthCheckType = HealthCheckType.HTTP
    interval_seconds: int = Field(default=30, ge=5)
    timeout_seconds: int = Field(default=10, ge=1)
    healthy_threshold: int = Field(default=2, ge=1)
    unhealthy_threshold: int = Field(default=3, ge=1)

    # HTTP specific
    path: str = Field(default="/health")
    expected_status: int = Field(default=200)

    # Pipeline specific
    test_pipeline_id: Optional[str] = None
    test_input: Optional[Dict[str, Any]] = None


class RoutingRule(BaseModel):
    """A rule for routing traffic."""

    id: str
    name: str
    priority: int = Field(default=0, description="Higher priority rules are evaluated first")
    enabled: bool = True

    # Conditions
    source_regions: List[str] = Field(
        default_factory=list,
        description="Source regions to match (empty = all)"
    )
    source_countries: List[str] = Field(
        default_factory=list,
        description="ISO country codes to match"
    )
    header_conditions: Dict[str, str] = Field(
        default_factory=dict,
        description="Header conditions to match"
    )

    # Action
    target_regions: List[str]
    weights: Optional[Dict[str, int]] = Field(
        default=None,
        description="Region weights for weighted routing"
    )
    fallback_regions: List[str] = Field(default_factory=list)


class DeploymentConfig(BaseModel):
    """Configuration for a multi-region deployment."""

    # Regions
    primary_region: str
    replica_regions: List[str] = Field(default_factory=list)
    excluded_regions: List[str] = Field(default_factory=list)

    # Routing
    routing_strategy: RoutingStrategy = RoutingStrategy.LATENCY
    routing_rules: List[RoutingRule] = Field(default_factory=list)

    # Health
    health_check: HealthCheck = Field(default_factory=HealthCheck)

    # Scaling
    min_replicas_per_region: int = Field(default=1, ge=1)
    max_replicas_per_region: int = Field(default=10, ge=1)
    auto_scaling_enabled: bool = True
    scale_up_threshold: float = Field(default=0.7, ge=0, le=1)
    scale_down_threshold: float = Field(default=0.3, ge=0, le=1)

    # Failover
    auto_failover_enabled: bool = True
    failover_threshold: int = Field(
        default=3,
        description="Number of failed health checks before failover"
    )
    failover_cooldown_seconds: int = Field(default=300)

    # Data
    sync_state: bool = Field(
        default=True,
        description="Sync execution state across regions"
    )
    sync_interval_seconds: int = Field(default=5)


class RegionDeployment(BaseModel):
    """Deployment status for a specific region."""

    region_id: str
    status: DeploymentStatus
    version: str
    replicas: int
    healthy_replicas: int
    deployed_at: str
    last_health_check: Optional[str] = None
    health_check_status: str = Field(default="unknown")
    error_message: Optional[str] = None

    # Metrics
    requests_per_second: float = 0.0
    average_latency_ms: float = 0.0
    error_rate: float = 0.0


class PipelineDeployment(BaseModel):
    """Multi-region deployment for a pipeline."""

    id: str
    pipeline_id: str
    pipeline_version: str
    name: str

    # Configuration
    config: DeploymentConfig

    # Status
    status: DeploymentStatus
    created_at: str
    updated_at: str
    deployed_by: str

    # Region deployments
    regions: List[RegionDeployment] = Field(default_factory=list)

    # Global metrics
    total_requests: int = 0
    total_errors: int = 0
    global_error_rate: float = 0.0


class FailoverEvent(BaseModel):
    """Record of a failover event."""

    id: str
    deployment_id: str
    from_region: str
    to_region: str
    reason: str
    triggered_at: str
    completed_at: Optional[str] = None
    success: bool = False
    affected_requests: int = 0


class RegionMetrics(BaseModel):
    """Metrics for a region."""

    region_id: str
    timestamp: str
    requests: int
    errors: int
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    cpu_usage: float
    memory_usage: float
    active_runs: int


class GlobalMetrics(BaseModel):
    """Global metrics across all regions."""

    timestamp: str
    total_requests: int
    total_errors: int
    global_latency_p50_ms: float
    global_latency_p95_ms: float
    regions: Dict[str, RegionMetrics] = Field(default_factory=dict)
    routing_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Request count per region"
    )


# API Request/Response Models

class CreateDeploymentRequest(BaseModel):
    """Request to create a multi-region deployment."""

    pipeline_id: str
    pipeline_version: Optional[str] = Field(
        default=None,
        description="Version to deploy (latest if not specified)"
    )
    name: Optional[str] = None
    config: DeploymentConfig


class UpdateDeploymentRequest(BaseModel):
    """Request to update a deployment."""

    config: Optional[DeploymentConfig] = None
    pipeline_version: Optional[str] = None


class ScaleRegionRequest(BaseModel):
    """Request to scale a region."""

    replicas: int = Field(..., ge=0)


class FailoverRequest(BaseModel):
    """Request to trigger manual failover."""

    from_region: str
    to_region: str
    reason: str = Field(default="Manual failover")


class AddRegionRequest(BaseModel):
    """Request to add a region to deployment."""

    region_id: str
    replicas: int = Field(default=1, ge=1)
    weight: Optional[int] = Field(
        default=None,
        description="Weight for weighted routing"
    )


class RemoveRegionRequest(BaseModel):
    """Request to remove a region from deployment."""

    region_id: str
    drain_timeout_seconds: int = Field(
        default=300,
        description="Time to drain existing requests"
    )


class DeploymentListResponse(BaseModel):
    """Response with list of deployments."""

    deployments: List[PipelineDeployment]
    total: int


class RegionListResponse(BaseModel):
    """Response with list of regions."""

    regions: List[Region]
    total: int
