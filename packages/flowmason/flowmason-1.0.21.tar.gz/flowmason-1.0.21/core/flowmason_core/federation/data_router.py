"""
Data Router for FlowMason Federation.

Routes data to optimal regions based on locality, load, and cost.
"""

import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from flowmason_core.federation.models import (
    FederationStrategy,
    RegionConfig,
    RemoteNode,
    RegionMetrics,
)

logger = logging.getLogger(__name__)


@dataclass
class RouteDecision:
    """Result of a routing decision."""
    regions: List[str]
    strategy: FederationStrategy
    reason: str
    scores: Dict[str, float]


class DataRouter:
    """
    Routes data and requests to optimal regions.

    Supports:
    - Nearest region by latency
    - Load-based routing
    - Cost-based routing
    - Data locality routing
    - Round-robin distribution

    Example:
        router = DataRouter(regions, nodes)

        decision = router.route(
            strategy=FederationStrategy.NEAREST,
            data_size_bytes=10000,
        )
    """

    def __init__(
        self,
        regions: Dict[str, RegionConfig],
        nodes: Optional[Dict[str, RemoteNode]] = None,
        metrics: Optional[Dict[str, RegionMetrics]] = None,
    ):
        """
        Initialize the data router.

        Args:
            regions: Region configurations
            nodes: Current node status
            metrics: Historical metrics
        """
        self.regions = regions
        self.nodes = nodes or {}
        self.metrics = metrics or {}

        # Round-robin state
        self._rr_index = 0

    def route(
        self,
        strategy: FederationStrategy,
        target_regions: Optional[List[str]] = None,
        client_location: Optional[Tuple[float, float]] = None,
        data_size_bytes: int = 0,
        data_locality_hint: Optional[str] = None,
        min_regions: int = 1,
        max_regions: Optional[int] = None,
    ) -> RouteDecision:
        """
        Make a routing decision.

        Args:
            strategy: Routing strategy
            target_regions: Specific regions to consider (None = all)
            client_location: Client lat/lon for nearest routing
            data_size_bytes: Size of data being sent
            data_locality_hint: Hint about where data originated
            min_regions: Minimum regions to route to
            max_regions: Maximum regions to route to

        Returns:
            RouteDecision with selected regions
        """
        # Get available regions
        available = self._get_available_regions(target_regions)

        if not available:
            return RouteDecision(
                regions=[],
                strategy=strategy,
                reason="No available regions",
                scores={},
            )

        # Route based on strategy
        if strategy == FederationStrategy.PARALLEL:
            return self._route_parallel(available, min_regions, max_regions)

        elif strategy == FederationStrategy.SEQUENTIAL:
            return self._route_sequential(available)

        elif strategy == FederationStrategy.NEAREST:
            return self._route_nearest(available, client_location, data_locality_hint)

        elif strategy == FederationStrategy.ROUND_ROBIN:
            return self._route_round_robin(available, min_regions)

        elif strategy == FederationStrategy.LOAD_BASED:
            return self._route_load_based(available, min_regions)

        elif strategy == FederationStrategy.COST_BASED:
            return self._route_cost_based(available, data_size_bytes, min_regions)

        else:
            return self._route_parallel(available, min_regions, max_regions)

    def _get_available_regions(
        self,
        target_regions: Optional[List[str]] = None,
    ) -> List[RegionConfig]:
        """Get available regions."""
        available = []

        for name, config in self.regions.items():
            if not config.enabled:
                continue

            if target_regions and name not in target_regions:
                continue

            # Check if node is online
            node = self.nodes.get(name)
            if node and node.status.value == "offline":
                continue

            available.append(config)

        return available

    def _route_parallel(
        self,
        regions: List[RegionConfig],
        min_regions: int,
        max_regions: Optional[int],
    ) -> RouteDecision:
        """Route to all regions in parallel."""
        # Sort by priority
        sorted_regions = sorted(regions, key=lambda r: r.priority, reverse=True)

        if max_regions:
            sorted_regions = sorted_regions[:max_regions]

        return RouteDecision(
            regions=[r.name for r in sorted_regions],
            strategy=FederationStrategy.PARALLEL,
            reason=f"Parallel execution on {len(sorted_regions)} regions",
            scores={r.name: r.priority for r in sorted_regions},
        )

    def _route_sequential(
        self,
        regions: List[RegionConfig],
    ) -> RouteDecision:
        """Route to regions sequentially by priority."""
        sorted_regions = sorted(regions, key=lambda r: r.priority, reverse=True)

        return RouteDecision(
            regions=[r.name for r in sorted_regions],
            strategy=FederationStrategy.SEQUENTIAL,
            reason="Sequential execution by priority",
            scores={r.name: float(i) for i, r in enumerate(sorted_regions)},
        )

    def _route_nearest(
        self,
        regions: List[RegionConfig],
        client_location: Optional[Tuple[float, float]],
        data_locality_hint: Optional[str],
    ) -> RouteDecision:
        """Route to nearest region."""
        scores = {}

        # If data locality hint matches a region, use it
        if data_locality_hint:
            for r in regions:
                if r.name == data_locality_hint:
                    return RouteDecision(
                        regions=[r.name],
                        strategy=FederationStrategy.NEAREST,
                        reason=f"Data locality match: {r.name}",
                        scores={r.name: 1.0},
                    )

        # Calculate distance to each region
        for region in regions:
            if client_location and region.latitude and region.longitude:
                distance = self._haversine_distance(
                    client_location[0], client_location[1],
                    region.latitude, region.longitude,
                )
                scores[region.name] = 1.0 / (1.0 + distance / 1000)  # Normalize
            else:
                # Use latency if available
                node = self.nodes.get(region.name)
                if node and node.avg_latency_ms > 0:
                    scores[region.name] = 1.0 / (1.0 + node.avg_latency_ms / 100)
                else:
                    scores[region.name] = region.weight

        # Select best
        if scores:
            best = max(scores.keys(), key=lambda k: scores[k])
            return RouteDecision(
                regions=[best],
                strategy=FederationStrategy.NEAREST,
                reason=f"Nearest region: {best}",
                scores=scores,
            )

        return RouteDecision(
            regions=[regions[0].name],
            strategy=FederationStrategy.NEAREST,
            reason="Fallback to first region",
            scores={regions[0].name: 1.0},
        )

    def _route_round_robin(
        self,
        regions: List[RegionConfig],
        count: int = 1,
    ) -> RouteDecision:
        """Route using round-robin."""
        selected = []
        scores = {}

        for i in range(count):
            idx = (self._rr_index + i) % len(regions)
            selected.append(regions[idx].name)
            scores[regions[idx].name] = 1.0

        self._rr_index = (self._rr_index + count) % len(regions)

        return RouteDecision(
            regions=selected,
            strategy=FederationStrategy.ROUND_ROBIN,
            reason=f"Round-robin selection: {selected}",
            scores=scores,
        )

    def _route_load_based(
        self,
        regions: List[RegionConfig],
        min_regions: int = 1,
    ) -> RouteDecision:
        """Route based on current load."""
        scores = {}

        for region in regions:
            node = self.nodes.get(region.name)
            if node:
                # Higher score = lower load
                available_capacity = node.max_capacity - (node.current_load * node.max_capacity)
                scores[region.name] = max(0, available_capacity)
            else:
                scores[region.name] = region.max_concurrent * 0.5  # Assume 50% available

        # Sort by score (available capacity)
        sorted_regions = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        selected = sorted_regions[:min_regions]

        return RouteDecision(
            regions=selected,
            strategy=FederationStrategy.LOAD_BASED,
            reason=f"Load-based selection: {selected}",
            scores=scores,
        )

    def _route_cost_based(
        self,
        regions: List[RegionConfig],
        data_size_bytes: int,
        min_regions: int = 1,
    ) -> RouteDecision:
        """Route to cheapest region."""
        scores = {}

        for region in regions:
            # Estimate cost
            base_cost = region.cost_per_execution
            # Higher score = lower cost
            if base_cost > 0:
                scores[region.name] = 1.0 / base_cost
            else:
                scores[region.name] = 100.0  # Free is best

        # Sort by score (inverse cost)
        sorted_regions = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        selected = sorted_regions[:min_regions]

        return RouteDecision(
            regions=selected,
            strategy=FederationStrategy.COST_BASED,
            reason=f"Cost-based selection: {selected}",
            scores=scores,
        )

    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float,
    ) -> float:
        """Calculate distance between two points in km."""
        R = 6371  # Earth's radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def update_nodes(self, nodes: Dict[str, RemoteNode]) -> None:
        """Update node status."""
        self.nodes = nodes

    def update_metrics(self, metrics: Dict[str, RegionMetrics]) -> None:
        """Update region metrics."""
        self.metrics = metrics


class ResultAggregator:
    """Aggregates results from multiple regions."""

    @staticmethod
    def merge(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge results into single dict."""
        merged = {}
        for result in results:
            if isinstance(result, dict):
                merged.update(result)
        return merged

    @staticmethod
    def concat(results: List[Any]) -> List[Any]:
        """Concatenate list results."""
        combined = []
        for result in results:
            if isinstance(result, list):
                combined.extend(result)
            else:
                combined.append(result)
        return combined

    @staticmethod
    def first_success(results: List[Any]) -> Optional[Any]:
        """Return first non-None result."""
        for result in results:
            if result is not None:
                return result
        return None

    @staticmethod
    def vote(results: List[Any], field: Optional[str] = None) -> Any:
        """Majority voting."""
        values = []
        for result in results:
            if field and isinstance(result, dict):
                values.append(result.get(field))
            else:
                values.append(result)

        if not values:
            return None

        # Count votes
        counts: Dict[Any, int] = {}
        for v in values:
            hashable_v = str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
            counts[hashable_v] = counts.get(hashable_v, 0) + 1

        # Return most common
        return max(counts.keys(), key=lambda k: counts[k])

    @staticmethod
    def best(
        results: List[Dict[str, Any]],
        score_field: str,
        higher_is_better: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Select result with best score."""
        if not results:
            return None

        def get_score(r):
            if isinstance(r, dict):
                return r.get(score_field, 0)
            return 0

        if higher_is_better:
            return max(results, key=get_score)
        else:
            return min(results, key=get_score)

    @staticmethod
    def reduce(results: List[Any], func: str) -> Any:
        """Apply reduction function."""
        if not results:
            return None

        if func == "sum":
            return sum(r for r in results if isinstance(r, (int, float)))
        elif func == "avg":
            nums = [r for r in results if isinstance(r, (int, float))]
            return sum(nums) / len(nums) if nums else 0
        elif func == "min":
            nums = [r for r in results if isinstance(r, (int, float))]
            return min(nums) if nums else None
        elif func == "max":
            nums = [r for r in results if isinstance(r, (int, float))]
            return max(nums) if nums else None
        elif func == "count":
            return len(results)
        else:
            return results
