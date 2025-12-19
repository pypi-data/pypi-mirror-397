"""
Remote Executor for FlowMason Federation.

Executes stages on remote nodes.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from flowmason_core.federation.models import (
    RegionConfig,
    RemoteNode,
    NodeStatus,
)

logger = logging.getLogger(__name__)


@dataclass
class RemoteExecutionResult:
    """Result of a remote execution."""
    region: str
    success: bool
    output: Any
    error: Optional[str] = None
    latency_ms: int = 0
    tokens_used: int = 0
    cost: float = 0.0


class RemoteExecutor:
    """
    Executes pipeline stages on remote nodes.

    Handles:
    - HTTP communication with remote nodes
    - Authentication
    - Timeout and retry
    - Result collection

    Example:
        executor = RemoteExecutor()

        result = await executor.execute(
            region=region_config,
            stage=stage_config,
            inputs=inputs,
        )
    """

    DEFAULT_TIMEOUT = 300

    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        default_timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize remote executor.

        Args:
            session: Optional aiohttp session
            default_timeout: Default timeout in seconds
        """
        self._session = session
        self._owns_session = session is None
        self.default_timeout = default_timeout

        # Circuit breaker state per region
        self._failures: Dict[str, int] = {}
        self._circuit_open: Dict[str, datetime] = {}

    async def __aenter__(self):
        if self._owns_session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._owns_session and self._session:
            await self._session.close()

    async def execute(
        self,
        region: RegionConfig,
        stage: Dict[str, Any],
        inputs: Dict[str, Any],
        timeout: Optional[int] = None,
    ) -> RemoteExecutionResult:
        """
        Execute a stage on a remote region.

        Args:
            region: Region configuration
            stage: Stage configuration
            inputs: Input data
            timeout: Optional timeout override

        Returns:
            RemoteExecutionResult
        """
        # Check circuit breaker
        if self._is_circuit_open(region.name):
            return RemoteExecutionResult(
                region=region.name,
                success=False,
                output=None,
                error="Circuit breaker open",
            )

        timeout = timeout or region.timeout_seconds or self.default_timeout
        start_time = time.time()

        try:
            # Ensure session
            if self._session is None:
                self._session = aiohttp.ClientSession()

            # Build request
            url = f"{region.endpoint}/api/v1/execute"
            headers = {
                "Authorization": f"Bearer {region.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "stage": stage,
                "inputs": inputs,
            }

            # Execute request
            async with self._session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                latency_ms = int((time.time() - start_time) * 1000)

                if response.status == 200:
                    data = await response.json()

                    # Reset circuit breaker on success
                    self._record_success(region.name)

                    return RemoteExecutionResult(
                        region=region.name,
                        success=True,
                        output=data.get("output"),
                        latency_ms=latency_ms,
                        tokens_used=data.get("tokens_used", 0),
                        cost=data.get("cost", 0.0),
                    )
                else:
                    error_text = await response.text()
                    self._record_failure(region.name)

                    return RemoteExecutionResult(
                        region=region.name,
                        success=False,
                        output=None,
                        error=f"HTTP {response.status}: {error_text}",
                        latency_ms=latency_ms,
                    )

        except asyncio.TimeoutError:
            self._record_failure(region.name)
            return RemoteExecutionResult(
                region=region.name,
                success=False,
                output=None,
                error="Timeout",
                latency_ms=int((time.time() - start_time) * 1000),
            )

        except Exception as e:
            self._record_failure(region.name)
            logger.error(f"Remote execution error ({region.name}): {e}")
            return RemoteExecutionResult(
                region=region.name,
                success=False,
                output=None,
                error=str(e),
                latency_ms=int((time.time() - start_time) * 1000),
            )

    async def execute_parallel(
        self,
        regions: List[RegionConfig],
        stage: Dict[str, Any],
        inputs: Dict[str, Any],
        timeout: Optional[int] = None,
    ) -> List[RemoteExecutionResult]:
        """
        Execute on multiple regions in parallel.

        Args:
            regions: List of region configs
            stage: Stage configuration
            inputs: Input data
            timeout: Optional timeout

        Returns:
            List of results from all regions
        """
        tasks = [
            self.execute(region, stage, inputs, timeout)
            for region in regions
        ]

        return await asyncio.gather(*tasks)

    async def execute_sequential(
        self,
        regions: List[RegionConfig],
        stage: Dict[str, Any],
        inputs: Dict[str, Any],
        timeout: Optional[int] = None,
        stop_on_success: bool = False,
    ) -> List[RemoteExecutionResult]:
        """
        Execute on regions sequentially.

        Args:
            regions: List of region configs
            stage: Stage configuration
            inputs: Input data
            timeout: Optional timeout
            stop_on_success: Stop after first success

        Returns:
            List of results
        """
        results = []

        for region in regions:
            result = await self.execute(region, stage, inputs, timeout)
            results.append(result)

            if stop_on_success and result.success:
                break

        return results

    async def check_health(self, region: RegionConfig) -> RemoteNode:
        """
        Check health of a remote region.

        Args:
            region: Region configuration

        Returns:
            RemoteNode with status
        """
        try:
            if self._session is None:
                self._session = aiohttp.ClientSession()

            url = f"{region.endpoint}/api/v1/health"
            headers = {"Authorization": f"Bearer {region.api_key}"}

            start_time = time.time()

            async with self._session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                latency = int((time.time() - start_time) * 1000)

                if response.status == 200:
                    data = await response.json()
                    return RemoteNode(
                        id=data.get("node_id", region.name),
                        region=region.name,
                        endpoint=region.endpoint,
                        status=NodeStatus.ONLINE,
                        last_heartbeat=datetime.utcnow(),
                        current_load=data.get("load", 0.0),
                        max_capacity=data.get("capacity", region.max_concurrent),
                        avg_latency_ms=latency,
                    )
                else:
                    return RemoteNode(
                        id=region.name,
                        region=region.name,
                        endpoint=region.endpoint,
                        status=NodeStatus.DEGRADED,
                        last_heartbeat=datetime.utcnow(),
                    )

        except Exception as e:
            logger.warning(f"Health check failed for {region.name}: {e}")
            return RemoteNode(
                id=region.name,
                region=region.name,
                endpoint=region.endpoint,
                status=NodeStatus.OFFLINE,
            )

    async def check_all_health(
        self,
        regions: List[RegionConfig],
    ) -> Dict[str, RemoteNode]:
        """Check health of all regions."""
        tasks = [self.check_health(r) for r in regions]
        nodes = await asyncio.gather(*tasks)
        return {node.region: node for node in nodes}

    def _is_circuit_open(self, region: str) -> bool:
        """Check if circuit breaker is open for region."""
        if region not in self._circuit_open:
            return False

        open_time = self._circuit_open[region]
        if (datetime.utcnow() - open_time).total_seconds() > 60:
            # Reset after 60 seconds
            del self._circuit_open[region]
            self._failures[region] = 0
            return False

        return True

    def _record_success(self, region: str) -> None:
        """Record successful execution."""
        self._failures[region] = 0
        if region in self._circuit_open:
            del self._circuit_open[region]

    def _record_failure(self, region: str) -> None:
        """Record failed execution."""
        self._failures[region] = self._failures.get(region, 0) + 1

        if self._failures[region] >= 5:
            self._circuit_open[region] = datetime.utcnow()
            logger.warning(f"Circuit breaker opened for region: {region}")
