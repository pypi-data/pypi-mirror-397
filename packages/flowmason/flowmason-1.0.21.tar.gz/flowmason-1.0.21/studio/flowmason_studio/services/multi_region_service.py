"""
Multi-Region Deployment Service.

Manages multi-region pipeline deployments.
"""

import math
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from flowmason_studio.models.multi_region import (
    DeploymentConfig,
    DeploymentStatus,
    FailoverEvent,
    GlobalMetrics,
    HealthCheck,
    PipelineDeployment,
    Region,
    RegionDeployment,
    RegionEndpoint,
    RegionMetrics,
    RegionStatus,
    RoutingRule,
    RoutingStrategy,
)


class MultiRegionService:
    """Service for managing multi-region deployments."""

    def __init__(self):
        """Initialize the service."""
        self._regions: Dict[str, Region] = {}
        self._endpoints: Dict[str, RegionEndpoint] = {}
        self._deployments: Dict[str, PipelineDeployment] = {}
        self._failover_events: Dict[str, List[FailoverEvent]] = {}
        self._metrics_history: Dict[str, List[RegionMetrics]] = {}

        # Initialize default regions
        self._init_default_regions()

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return secrets.token_urlsafe(16)

    def _now(self) -> str:
        """Get current ISO timestamp."""
        return datetime.utcnow().isoformat() + "Z"

    def _init_default_regions(self):
        """Initialize default regions."""
        default_regions = [
            Region(
                id="us-east-1",
                name="US East (Virginia)",
                code="us-east-1",
                location="Virginia, USA",
                latitude=37.4316,
                longitude=-78.6569,
                supports_gpu=True,
                max_concurrent_runs=500,
                available_providers=["openai", "anthropic", "google"],
                uptime_percentage=99.95,
            ),
            Region(
                id="us-west-2",
                name="US West (Oregon)",
                code="us-west-2",
                location="Oregon, USA",
                latitude=45.8399,
                longitude=-119.7006,
                supports_gpu=True,
                max_concurrent_runs=300,
                available_providers=["openai", "anthropic"],
                uptime_percentage=99.92,
            ),
            Region(
                id="eu-west-1",
                name="Europe (Ireland)",
                code="eu-west-1",
                location="Dublin, Ireland",
                latitude=53.3498,
                longitude=-6.2603,
                supports_gpu=True,
                max_concurrent_runs=400,
                available_providers=["openai", "anthropic", "google"],
                uptime_percentage=99.94,
            ),
            Region(
                id="eu-central-1",
                name="Europe (Frankfurt)",
                code="eu-central-1",
                location="Frankfurt, Germany",
                latitude=50.1109,
                longitude=8.6821,
                supports_gpu=False,
                max_concurrent_runs=200,
                available_providers=["openai", "anthropic"],
                uptime_percentage=99.90,
            ),
            Region(
                id="ap-northeast-1",
                name="Asia Pacific (Tokyo)",
                code="ap-northeast-1",
                location="Tokyo, Japan",
                latitude=35.6762,
                longitude=139.6503,
                supports_gpu=True,
                max_concurrent_runs=300,
                available_providers=["openai", "anthropic"],
                uptime_percentage=99.93,
            ),
            Region(
                id="ap-southeast-1",
                name="Asia Pacific (Singapore)",
                code="ap-southeast-1",
                location="Singapore",
                latitude=1.3521,
                longitude=103.8198,
                supports_gpu=False,
                max_concurrent_runs=200,
                available_providers=["openai", "anthropic"],
                uptime_percentage=99.91,
            ),
        ]

        for region in default_regions:
            self._regions[region.id] = region
            self._endpoints[region.id] = RegionEndpoint(
                region_id=region.id,
                api_url=f"https://{region.code}.api.flowmason.io",
                ws_url=f"wss://{region.code}.api.flowmason.io/ws",
                health_check_url=f"https://{region.code}.api.flowmason.io/health",
            )

    # =========================================================================
    # Regions
    # =========================================================================

    def list_regions(
        self,
        status: Optional[RegionStatus] = None,
        supports_gpu: Optional[bool] = None,
    ) -> List[Region]:
        """List all available regions."""
        regions = list(self._regions.values())

        if status:
            regions = [r for r in regions if r.status == status]

        if supports_gpu is not None:
            regions = [r for r in regions if r.supports_gpu == supports_gpu]

        return regions

    def get_region(self, region_id: str) -> Optional[Region]:
        """Get a region by ID."""
        return self._regions.get(region_id)

    def get_region_endpoint(self, region_id: str) -> Optional[RegionEndpoint]:
        """Get endpoint for a region."""
        return self._endpoints.get(region_id)

    def update_region_status(
        self,
        region_id: str,
        status: RegionStatus,
        message: Optional[str] = None,
    ) -> Optional[Region]:
        """Update region status."""
        region = self._regions.get(region_id)
        if region:
            region.status = status
            region.status_message = message
        return region

    def find_nearest_region(
        self,
        latitude: float,
        longitude: float,
        exclude: Optional[List[str]] = None,
    ) -> Optional[Region]:
        """Find the nearest active region to a location."""
        exclude = exclude or []
        active_regions = [
            r for r in self._regions.values()
            if r.status == RegionStatus.ACTIVE and r.id not in exclude
        ]

        if not active_regions:
            return None

        def distance(region: Region) -> float:
            # Haversine formula for distance
            lat1, lon1 = math.radians(latitude), math.radians(longitude)
            lat2, lon2 = math.radians(region.latitude), math.radians(region.longitude)

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            return 6371 * c  # Earth radius in km

        return min(active_regions, key=distance)

    # =========================================================================
    # Deployments
    # =========================================================================

    def create_deployment(
        self,
        pipeline_id: str,
        user_id: str,
        config: DeploymentConfig,
        pipeline_version: str = "latest",
        name: Optional[str] = None,
    ) -> PipelineDeployment:
        """Create a new multi-region deployment."""
        deployment_id = self._generate_id()
        now = self._now()

        # Validate regions
        all_regions = [config.primary_region] + config.replica_regions
        for region_id in all_regions:
            if region_id not in self._regions:
                raise ValueError(f"Unknown region: {region_id}")

        # Create region deployments
        region_deployments = []
        for region_id in all_regions:
            region_deployments.append(
                RegionDeployment(
                    region_id=region_id,
                    status=DeploymentStatus.PENDING,
                    version=pipeline_version,
                    replicas=config.min_replicas_per_region,
                    healthy_replicas=0,
                    deployed_at=now,
                )
            )

        deployment = PipelineDeployment(
            id=deployment_id,
            pipeline_id=pipeline_id,
            pipeline_version=pipeline_version,
            name=name or f"deployment-{deployment_id[:8]}",
            config=config,
            status=DeploymentStatus.PENDING,
            created_at=now,
            updated_at=now,
            deployed_by=user_id,
            regions=region_deployments,
        )

        self._deployments[deployment_id] = deployment
        self._failover_events[deployment_id] = []

        # Simulate deployment
        self._simulate_deployment(deployment)

        return deployment

    def _simulate_deployment(self, deployment: PipelineDeployment) -> None:
        """Simulate deployment to regions (in real implementation, this would be async)."""
        deployment.status = DeploymentStatus.DEPLOYING

        for region_dep in deployment.regions:
            region_dep.status = DeploymentStatus.DEPLOYING

        # Mark as active (simulated)
        deployment.status = DeploymentStatus.ACTIVE
        deployment.updated_at = self._now()

        for region_dep in deployment.regions:
            region_dep.status = DeploymentStatus.ACTIVE
            region_dep.healthy_replicas = region_dep.replicas
            region_dep.health_check_status = "healthy"
            region_dep.last_health_check = self._now()

    def get_deployment(self, deployment_id: str) -> Optional[PipelineDeployment]:
        """Get a deployment by ID."""
        return self._deployments.get(deployment_id)

    def list_deployments(
        self,
        pipeline_id: Optional[str] = None,
        status: Optional[DeploymentStatus] = None,
    ) -> List[PipelineDeployment]:
        """List deployments."""
        deployments = list(self._deployments.values())

        if pipeline_id:
            deployments = [d for d in deployments if d.pipeline_id == pipeline_id]

        if status:
            deployments = [d for d in deployments if d.status == status]

        return deployments

    def update_deployment(
        self,
        deployment_id: str,
        config: Optional[DeploymentConfig] = None,
        pipeline_version: Optional[str] = None,
    ) -> Optional[PipelineDeployment]:
        """Update a deployment."""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return None

        if config:
            deployment.config = config

        if pipeline_version:
            deployment.pipeline_version = pipeline_version
            for region_dep in deployment.regions:
                region_dep.version = pipeline_version

        deployment.updated_at = self._now()
        return deployment

    def stop_deployment(self, deployment_id: str) -> bool:
        """Stop a deployment."""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return False

        deployment.status = DeploymentStatus.STOPPED
        deployment.updated_at = self._now()

        for region_dep in deployment.regions:
            region_dep.status = DeploymentStatus.STOPPED
            region_dep.healthy_replicas = 0

        return True

    def delete_deployment(self, deployment_id: str) -> bool:
        """Delete a deployment."""
        if deployment_id not in self._deployments:
            return False

        del self._deployments[deployment_id]
        self._failover_events.pop(deployment_id, None)
        return True

    # =========================================================================
    # Region Management
    # =========================================================================

    def add_region_to_deployment(
        self,
        deployment_id: str,
        region_id: str,
        replicas: int = 1,
    ) -> Optional[RegionDeployment]:
        """Add a region to an existing deployment."""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return None

        if region_id not in self._regions:
            return None

        # Check if already exists
        if any(r.region_id == region_id for r in deployment.regions):
            return None

        now = self._now()
        region_dep = RegionDeployment(
            region_id=region_id,
            status=DeploymentStatus.ACTIVE,
            version=deployment.pipeline_version,
            replicas=replicas,
            healthy_replicas=replicas,
            deployed_at=now,
            last_health_check=now,
            health_check_status="healthy",
        )

        deployment.regions.append(region_dep)
        deployment.config.replica_regions.append(region_id)
        deployment.updated_at = now

        return region_dep

    def remove_region_from_deployment(
        self,
        deployment_id: str,
        region_id: str,
    ) -> bool:
        """Remove a region from a deployment."""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return False

        # Can't remove primary region
        if region_id == deployment.config.primary_region:
            return False

        deployment.regions = [r for r in deployment.regions if r.region_id != region_id]
        if region_id in deployment.config.replica_regions:
            deployment.config.replica_regions.remove(region_id)

        deployment.updated_at = self._now()
        return True

    def scale_region(
        self,
        deployment_id: str,
        region_id: str,
        replicas: int,
    ) -> Optional[RegionDeployment]:
        """Scale replicas in a region."""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return None

        region_dep = next(
            (r for r in deployment.regions if r.region_id == region_id),
            None
        )
        if not region_dep:
            return None

        region_dep.replicas = replicas
        region_dep.healthy_replicas = min(region_dep.healthy_replicas, replicas)
        deployment.updated_at = self._now()

        return region_dep

    # =========================================================================
    # Failover
    # =========================================================================

    def trigger_failover(
        self,
        deployment_id: str,
        from_region: str,
        to_region: str,
        reason: str = "Manual failover",
    ) -> Optional[FailoverEvent]:
        """Trigger a failover from one region to another."""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return None

        # Validate regions
        from_dep = next(
            (r for r in deployment.regions if r.region_id == from_region),
            None
        )
        to_dep = next(
            (r for r in deployment.regions if r.region_id == to_region),
            None
        )

        if not from_dep or not to_dep:
            return None

        now = self._now()
        event = FailoverEvent(
            id=self._generate_id(),
            deployment_id=deployment_id,
            from_region=from_region,
            to_region=to_region,
            reason=reason,
            triggered_at=now,
        )

        # Perform failover
        if deployment.config.primary_region == from_region:
            deployment.config.primary_region = to_region
            if to_region in deployment.config.replica_regions:
                deployment.config.replica_regions.remove(to_region)
            deployment.config.replica_regions.append(from_region)

        # Mark from_region as degraded
        from_dep.health_check_status = "unhealthy"
        from_dep.healthy_replicas = 0

        event.completed_at = self._now()
        event.success = True

        self._failover_events[deployment_id].append(event)
        deployment.updated_at = self._now()

        return event

    def get_failover_events(
        self,
        deployment_id: str,
        limit: int = 50,
    ) -> List[FailoverEvent]:
        """Get failover events for a deployment."""
        events = self._failover_events.get(deployment_id, [])
        return events[-limit:]

    # =========================================================================
    # Routing
    # =========================================================================

    def resolve_region(
        self,
        deployment_id: str,
        source_region: Optional[str] = None,
        source_country: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Resolve which region to route a request to."""
        deployment = self._deployments.get(deployment_id)
        if not deployment or deployment.status != DeploymentStatus.ACTIVE:
            return None

        config = deployment.config

        # Get healthy regions
        healthy_regions = [
            r.region_id for r in deployment.regions
            if r.status == DeploymentStatus.ACTIVE and r.healthy_replicas > 0
        ]

        if not healthy_regions:
            return None

        # Check routing rules first
        for rule in sorted(config.routing_rules, key=lambda r: -r.priority):
            if not rule.enabled:
                continue

            # Check conditions
            if rule.source_regions and source_region not in rule.source_regions:
                continue
            if rule.source_countries and source_country not in rule.source_countries:
                continue
            if rule.header_conditions:
                if not headers:
                    continue
                if not all(headers.get(k) == v for k, v in rule.header_conditions.items()):
                    continue

            # Apply rule
            target = [r for r in rule.target_regions if r in healthy_regions]
            if target:
                if rule.weights:
                    # Weighted selection
                    import random
                    weighted = [(r, rule.weights.get(r, 1)) for r in target]
                    total = sum(w for _, w in weighted)
                    rand = random.uniform(0, total)
                    cumulative = 0
                    for region, weight in weighted:
                        cumulative += weight
                        if rand <= cumulative:
                            return region
                return target[0]

        # Apply default routing strategy
        if config.routing_strategy == RoutingStrategy.LATENCY:
            # Return lowest latency region
            region_latencies = {
                r.region_id: r.average_latency_ms
                for r in deployment.regions
                if r.region_id in healthy_regions
            }
            return min(region_latencies.keys(), key=lambda k: region_latencies[k])

        elif config.routing_strategy == RoutingStrategy.GEOLOCATION:
            if latitude is not None and longitude is not None:
                nearest = self.find_nearest_region(
                    latitude,
                    longitude,
                    exclude=[r for r in self._regions if r not in healthy_regions],
                )
                if nearest and nearest.id in healthy_regions:
                    return nearest.id
            # Fall back to primary
            return config.primary_region if config.primary_region in healthy_regions else healthy_regions[0]

        elif config.routing_strategy == RoutingStrategy.FAILOVER:
            if config.primary_region in healthy_regions:
                return config.primary_region
            # Use first healthy fallback
            for fallback in config.replica_regions:
                if fallback in healthy_regions:
                    return fallback
            return healthy_regions[0] if healthy_regions else None

        elif config.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            # Simple round-robin (in production, would track state)
            import random
            return random.choice(healthy_regions)

        elif config.routing_strategy == RoutingStrategy.WEIGHTED:
            # Use routing rule weights or equal distribution
            import random
            return random.choice(healthy_regions)

        # Default to primary
        return config.primary_region if config.primary_region in healthy_regions else healthy_regions[0]

    # =========================================================================
    # Metrics
    # =========================================================================

    def get_region_metrics(
        self,
        deployment_id: str,
        region_id: str,
    ) -> Optional[RegionMetrics]:
        """Get current metrics for a region."""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return None

        region_dep = next(
            (r for r in deployment.regions if r.region_id == region_id),
            None
        )
        if not region_dep:
            return None

        # Generate simulated metrics
        import random
        return RegionMetrics(
            region_id=region_id,
            timestamp=self._now(),
            requests=random.randint(100, 1000),
            errors=random.randint(0, 10),
            latency_p50_ms=random.uniform(50, 150),
            latency_p95_ms=random.uniform(150, 300),
            latency_p99_ms=random.uniform(300, 500),
            cpu_usage=random.uniform(0.2, 0.7),
            memory_usage=random.uniform(0.3, 0.6),
            active_runs=random.randint(5, 50),
        )

    def get_global_metrics(
        self,
        deployment_id: str,
    ) -> Optional[GlobalMetrics]:
        """Get global metrics across all regions."""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return None

        region_metrics = {}
        total_requests = 0
        total_errors = 0
        latencies = []

        for region_dep in deployment.regions:
            metrics = self.get_region_metrics(deployment_id, region_dep.region_id)
            if metrics:
                region_metrics[region_dep.region_id] = metrics
                total_requests += metrics.requests
                total_errors += metrics.errors
                latencies.append(metrics.latency_p50_ms)

        return GlobalMetrics(
            timestamp=self._now(),
            total_requests=total_requests,
            total_errors=total_errors,
            global_latency_p50_ms=sum(latencies) / len(latencies) if latencies else 0,
            global_latency_p95_ms=max((m.latency_p95_ms for m in region_metrics.values()), default=0),
            regions=region_metrics,
            routing_distribution={r: m.requests for r, m in region_metrics.items()},
        )

    # =========================================================================
    # Health Checks
    # =========================================================================

    def run_health_check(
        self,
        deployment_id: str,
        region_id: str,
    ) -> Tuple[bool, str]:
        """Run health check for a region (simulated)."""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return False, "Deployment not found"

        region_dep = next(
            (r for r in deployment.regions if r.region_id == region_id),
            None
        )
        if not region_dep:
            return False, "Region not in deployment"

        # Simulate health check (in production, would actually check endpoint)
        region = self._regions.get(region_id)
        if not region or region.status != RegionStatus.ACTIVE:
            region_dep.health_check_status = "unhealthy"
            return False, "Region is not active"

        region_dep.health_check_status = "healthy"
        region_dep.last_health_check = self._now()
        return True, "Healthy"


# Singleton instance
_service: Optional[MultiRegionService] = None


def get_multi_region_service() -> MultiRegionService:
    """Get the singleton MultiRegionService instance."""
    global _service
    if _service is None:
        _service = MultiRegionService()
    return _service
