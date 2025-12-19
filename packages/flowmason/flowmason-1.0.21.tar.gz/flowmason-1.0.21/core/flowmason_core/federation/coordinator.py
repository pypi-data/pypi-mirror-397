"""
Federation Coordinator for FlowMason.

Orchestrates distributed pipeline execution across regions.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from flowmason_core.federation.models import (
    FederationConfig,
    FederationStrategy,
    FederatedStageConfig,
    AggregationStrategy,
    RegionConfig,
    RemoteNode,
    FederatedExecution,
    RegionMetrics,
)
from flowmason_core.federation.remote_executor import RemoteExecutor, RemoteExecutionResult
from flowmason_core.federation.data_router import DataRouter, ResultAggregator

logger = logging.getLogger(__name__)


@dataclass
class FederatedStageResult:
    """Result of a federated stage execution."""
    stage_id: str
    success: bool
    output: Any
    region_results: Dict[str, RemoteExecutionResult]
    aggregation_method: AggregationStrategy
    total_latency_ms: int
    total_cost: float
    error: Optional[str] = None


class FederationCoordinator:
    """
    Coordinates federated pipeline execution.

    Manages:
    - Stage distribution across regions
    - Result aggregation
    - Health monitoring
    - Metrics collection

    Example:
        config = FederationConfig()
        config.add_region(RegionConfig(
            name="us-east-1",
            endpoint="https://us-east.flowmason.io",
            api_key="...",
        ))

        coordinator = FederationCoordinator(config)
        await coordinator.start()

        result = await coordinator.execute_federated(
            stage=stage_config,
            inputs=inputs,
            federation=FederatedStageConfig(
                strategy=FederationStrategy.PARALLEL,
                regions=["us-east-1", "eu-west-1"],
            ),
        )
    """

    def __init__(
        self,
        config: FederationConfig,
        on_progress: Optional[Callable] = None,
    ):
        """
        Initialize the federation coordinator.

        Args:
            config: Federation configuration
            on_progress: Progress callback
        """
        self.config = config
        self.on_progress = on_progress

        self._executor = RemoteExecutor()
        self._router: Optional[DataRouter] = None
        self._nodes: Dict[str, RemoteNode] = {}
        self._metrics: Dict[str, RegionMetrics] = {}
        self._executions: Dict[str, FederatedExecution] = {}

        self._running = False
        self._health_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the federation coordinator."""
        if self._running:
            return

        self._running = True

        # Initialize router
        self._router = DataRouter(
            regions=self.config.regions,
            nodes=self._nodes,
            metrics=self._metrics,
        )

        # Start health monitoring
        self._health_task = asyncio.create_task(self._health_loop())

        logger.info("Federation coordinator started")

    async def stop(self) -> None:
        """Stop the federation coordinator."""
        if not self._running:
            return

        self._running = False

        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        logger.info("Federation coordinator stopped")

    async def execute_federated(
        self,
        stage: Dict[str, Any],
        inputs: Dict[str, Any],
        federation: FederatedStageConfig,
        run_id: Optional[str] = None,
    ) -> FederatedStageResult:
        """
        Execute a stage across federated regions.

        Args:
            stage: Stage configuration
            inputs: Input data
            federation: Federation configuration for this stage
            run_id: Optional run identifier

        Returns:
            FederatedStageResult
        """
        execution_id = str(uuid.uuid4())
        stage_id = stage.get("id", "unknown")
        start_time = datetime.utcnow()

        logger.info(f"Starting federated execution: {execution_id} for stage {stage_id}")

        # Track execution
        execution = FederatedExecution(
            id=execution_id,
            pipeline_name=stage.get("pipeline", "unknown"),
            stage_id=stage_id,
            strategy=federation.strategy,
            started_at=start_time,
        )
        self._executions[execution_id] = execution

        try:
            # Get target regions
            target_regions = self._get_target_regions(federation)
            execution.regions_targeted = [r.name for r in target_regions]

            if not target_regions:
                return FederatedStageResult(
                    stage_id=stage_id,
                    success=False,
                    output=None,
                    region_results={},
                    aggregation_method=federation.aggregation,
                    total_latency_ms=0,
                    total_cost=0,
                    error="No available regions",
                )

            # Route based on strategy
            if self._router:
                decision = self._router.route(
                    strategy=federation.strategy,
                    target_regions=[r.name for r in target_regions],
                    min_regions=federation.min_regions,
                )
                logger.debug(f"Routing decision: {decision.reason}")

            # Execute based on strategy
            if federation.strategy == FederationStrategy.PARALLEL:
                results = await self._execute_parallel(
                    target_regions, stage, inputs, federation.timeout_seconds
                )
            elif federation.strategy == FederationStrategy.SEQUENTIAL:
                results = await self._execute_sequential(
                    target_regions, stage, inputs, federation.timeout_seconds
                )
            elif federation.strategy in (
                FederationStrategy.NEAREST,
                FederationStrategy.ROUND_ROBIN,
                FederationStrategy.LOAD_BASED,
                FederationStrategy.COST_BASED,
            ):
                # Single region routing
                if self._router:
                    selected = [
                        self.config.regions[r]
                        for r in decision.regions
                        if r in self.config.regions
                    ]
                else:
                    selected = target_regions[:1]
                results = await self._execute_parallel(
                    selected, stage, inputs, federation.timeout_seconds
                )
            else:
                results = await self._execute_parallel(
                    target_regions, stage, inputs, federation.timeout_seconds
                )

            # Process results
            region_results = {r.region: r for r in results}
            successful_results = [r for r in results if r.success]
            failed_results = [r for r in results if not r.success]

            execution.regions_completed = [r.region for r in successful_results]
            execution.regions_failed = [r.region for r in failed_results]

            # Check minimum regions
            if len(successful_results) < federation.min_regions:
                error = f"Only {len(successful_results)} of {federation.min_regions} required regions succeeded"
                return FederatedStageResult(
                    stage_id=stage_id,
                    success=False,
                    output=None,
                    region_results=region_results,
                    aggregation_method=federation.aggregation,
                    total_latency_ms=sum(r.latency_ms for r in results),
                    total_cost=sum(r.cost for r in results),
                    error=error,
                )

            # Aggregate results
            outputs = [r.output for r in successful_results]
            aggregated = self._aggregate_results(
                outputs,
                federation.aggregation,
                federation.reduce_function,
                federation.score_field,
                federation.vote_field,
            )

            execution.aggregated_result = aggregated
            execution.completed_at = datetime.utcnow()

            # Update metrics
            for result in results:
                self._update_metrics(result)

            return FederatedStageResult(
                stage_id=stage_id,
                success=True,
                output=aggregated,
                region_results=region_results,
                aggregation_method=federation.aggregation,
                total_latency_ms=sum(r.latency_ms for r in results),
                total_cost=sum(r.cost for r in results),
            )

        except Exception as e:
            logger.error(f"Federated execution error: {e}")
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()

            return FederatedStageResult(
                stage_id=stage_id,
                success=False,
                output=None,
                region_results={},
                aggregation_method=federation.aggregation,
                total_latency_ms=0,
                total_cost=0,
                error=str(e),
            )

    async def _execute_parallel(
        self,
        regions: List[RegionConfig],
        stage: Dict[str, Any],
        inputs: Dict[str, Any],
        timeout: int,
    ) -> List[RemoteExecutionResult]:
        """Execute on regions in parallel."""
        return await self._executor.execute_parallel(
            regions, stage, inputs, timeout
        )

    async def _execute_sequential(
        self,
        regions: List[RegionConfig],
        stage: Dict[str, Any],
        inputs: Dict[str, Any],
        timeout: int,
    ) -> List[RemoteExecutionResult]:
        """Execute on regions sequentially."""
        return await self._executor.execute_sequential(
            regions, stage, inputs, timeout
        )

    def _get_target_regions(
        self,
        federation: FederatedStageConfig,
    ) -> List[RegionConfig]:
        """Get target regions for execution."""
        if federation.regions:
            # Specific regions requested
            return [
                self.config.regions[name]
                for name in federation.regions
                if name in self.config.regions
                and self.config.regions[name].enabled
            ]
        else:
            # All enabled regions
            return self.config.get_enabled_regions()

    def _aggregate_results(
        self,
        outputs: List[Any],
        strategy: AggregationStrategy,
        reduce_function: Optional[str],
        score_field: Optional[str],
        vote_field: Optional[str],
    ) -> Any:
        """Aggregate results based on strategy."""
        if not outputs:
            return None

        if strategy == AggregationStrategy.MERGE:
            return ResultAggregator.merge(outputs)

        elif strategy == AggregationStrategy.CONCAT:
            return ResultAggregator.concat(outputs)

        elif strategy == AggregationStrategy.FIRST:
            return ResultAggregator.first_success(outputs)

        elif strategy == AggregationStrategy.VOTE:
            return ResultAggregator.vote(outputs, vote_field)

        elif strategy == AggregationStrategy.BEST:
            return ResultAggregator.best(outputs, score_field or "score")

        elif strategy == AggregationStrategy.REDUCE:
            return ResultAggregator.reduce(outputs, reduce_function or "sum")

        else:
            return outputs[0] if outputs else None

    def _update_metrics(self, result: RemoteExecutionResult) -> None:
        """Update metrics for a region."""
        if result.region not in self._metrics:
            self._metrics[result.region] = RegionMetrics(region=result.region)

        metrics = self._metrics[result.region]
        metrics.executions_total += 1
        metrics.total_latency_ms += result.latency_ms
        metrics.total_cost += result.cost
        metrics.last_execution = datetime.utcnow()

        if result.success:
            metrics.executions_success += 1
        else:
            metrics.executions_failed += 1

        # Update router
        if self._router:
            self._router.update_metrics(self._metrics)

    async def _health_loop(self) -> None:
        """Background health check loop."""
        while self._running:
            try:
                regions = list(self.config.regions.values())
                self._nodes = await self._executor.check_all_health(regions)

                if self._router:
                    self._router.update_nodes(self._nodes)

                await asyncio.sleep(self.config.health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(self.config.health_check_interval)

    def get_region_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all regions."""
        status = {}

        for name, config in self.config.regions.items():
            node = self._nodes.get(name)
            metrics = self._metrics.get(name)

            status[name] = {
                "enabled": config.enabled,
                "status": node.status.value if node else "unknown",
                "last_heartbeat": node.last_heartbeat.isoformat() if node and node.last_heartbeat else None,
                "current_load": node.current_load if node else 0,
                "avg_latency_ms": metrics.avg_latency_ms if metrics else 0,
                "success_rate": metrics.success_rate if metrics else 1.0,
                "total_executions": metrics.executions_total if metrics else 0,
            }

        return status

    def get_execution(self, execution_id: str) -> Optional[FederatedExecution]:
        """Get execution by ID."""
        return self._executions.get(execution_id)

    def add_region(self, region: RegionConfig) -> None:
        """Add a new region."""
        self.config.add_region(region)
        if self._router:
            self._router.regions = self.config.regions

    def remove_region(self, name: str) -> None:
        """Remove a region."""
        self.config.remove_region(name)
        if self._router:
            self._router.regions = self.config.regions
