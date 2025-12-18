"""
Federation Models for FlowMason.

Data models for federated execution configuration and state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FederationStrategy(str, Enum):
    """How to distribute work across regions."""
    PARALLEL = "parallel"       # Execute on all regions simultaneously
    SEQUENTIAL = "sequential"   # Execute on regions in order
    NEAREST = "nearest"         # Route to nearest region by latency
    ROUND_ROBIN = "round_robin" # Distribute evenly across regions
    LOAD_BASED = "load_based"   # Route based on current load
    COST_BASED = "cost_based"   # Route to cheapest region


class AggregationStrategy(str, Enum):
    """How to combine results from multiple regions."""
    MERGE = "merge"           # Merge all results into one object
    REDUCE = "reduce"         # Apply reduction function
    FIRST = "first"           # Use first successful result
    CONCAT = "concat"         # Concatenate array results
    VOTE = "vote"             # Majority voting for classification
    BEST = "best"             # Select best result by score


class NodeStatus(str, Enum):
    """Status of a remote node."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    DRAINING = "draining"


@dataclass
class RegionConfig:
    """Configuration for a region."""
    name: str
    endpoint: str
    api_key: str
    priority: int = 0
    weight: float = 1.0
    max_concurrent: int = 10
    timeout_seconds: int = 300
    tags: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True

    # Cost configuration
    cost_per_execution: float = 0.0
    cost_per_token: float = 0.0

    # Geographic info
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class RemoteNode:
    """A remote execution node."""
    id: str
    region: str
    endpoint: str
    status: NodeStatus
    last_heartbeat: Optional[datetime] = None
    current_load: float = 0.0
    max_capacity: int = 10
    avg_latency_ms: int = 0
    error_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FederatedStageConfig:
    """Federation configuration for a stage."""
    strategy: FederationStrategy = FederationStrategy.PARALLEL
    regions: List[str] = field(default_factory=list)
    aggregation: AggregationStrategy = AggregationStrategy.MERGE
    data_locality: bool = False
    min_regions: int = 1
    timeout_seconds: int = 300
    retry_count: int = 3
    retry_delay_seconds: int = 5

    # Aggregation options
    reduce_function: Optional[str] = None  # For REDUCE strategy
    score_field: Optional[str] = None      # For BEST strategy
    vote_field: Optional[str] = None       # For VOTE strategy

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy": self.strategy.value,
            "regions": self.regions,
            "aggregation": self.aggregation.value,
            "data_locality": self.data_locality,
            "min_regions": self.min_regions,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FederatedStageConfig":
        """Create from dictionary."""
        return cls(
            strategy=FederationStrategy(data.get("strategy", "parallel")),
            regions=data.get("regions", []),
            aggregation=AggregationStrategy(data.get("aggregation", "merge")),
            data_locality=data.get("data_locality", False),
            min_regions=data.get("min_regions", 1),
            timeout_seconds=data.get("timeout_seconds", 300),
            retry_count=data.get("retry_count", 3),
            retry_delay_seconds=data.get("retry_delay_seconds", 5),
            reduce_function=data.get("reduce_function"),
            score_field=data.get("score_field"),
            vote_field=data.get("vote_field"),
        )


@dataclass
class FederationConfig:
    """Global federation configuration."""
    regions: Dict[str, RegionConfig] = field(default_factory=dict)
    default_strategy: FederationStrategy = FederationStrategy.PARALLEL
    default_aggregation: AggregationStrategy = AggregationStrategy.MERGE
    health_check_interval: int = 30
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

    def add_region(self, region: RegionConfig) -> None:
        """Add a region."""
        self.regions[region.name] = region

    def remove_region(self, name: str) -> None:
        """Remove a region."""
        if name in self.regions:
            del self.regions[name]

    def get_enabled_regions(self) -> List[RegionConfig]:
        """Get enabled regions."""
        return [r for r in self.regions.values() if r.enabled]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "regions": {
                name: {
                    "name": r.name,
                    "endpoint": r.endpoint,
                    "priority": r.priority,
                    "weight": r.weight,
                    "enabled": r.enabled,
                }
                for name, r in self.regions.items()
            },
            "default_strategy": self.default_strategy.value,
            "default_aggregation": self.default_aggregation.value,
        }


@dataclass
class FederatedExecution:
    """State of a federated execution."""
    id: str
    pipeline_name: str
    stage_id: str
    strategy: FederationStrategy
    started_at: datetime
    completed_at: Optional[datetime] = None
    regions_targeted: List[str] = field(default_factory=list)
    regions_completed: List[str] = field(default_factory=list)
    regions_failed: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    aggregated_result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class RegionMetrics:
    """Metrics for a region."""
    region: str
    executions_total: int = 0
    executions_success: int = 0
    executions_failed: int = 0
    total_latency_ms: int = 0
    total_cost: float = 0.0
    last_execution: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.executions_total == 0:
            return 1.0
        return self.executions_success / self.executions_total

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.executions_total == 0:
            return 0.0
        return self.total_latency_ms / self.executions_total
