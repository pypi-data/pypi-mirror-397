"""
Sync Manager for FlowMason Edge.

Handles synchronization with cloud when connectivity is available.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class SyncStatus(str, Enum):
    """Sync status."""
    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"
    OFFLINE = "offline"


class ConnectionStatus(str, Enum):
    """Connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CHECKING = "checking"


@dataclass
class SyncState:
    """Current sync state."""
    status: SyncStatus
    connection: ConnectionStatus
    last_sync: Optional[datetime]
    pending_results: int
    pending_pipelines: int
    last_error: Optional[str]


class SyncManager:
    """
    Manages synchronization between edge and cloud.

    Provides:
    - Connectivity monitoring
    - Result upload when online
    - Pipeline sync from cloud
    - Automatic retry on failure

    Example:
        sync = SyncManager(
            cloud_url="https://studio.flowmason.io",
            api_key="...",
            result_store=result_store,
            pipeline_cache=pipeline_cache,
        )

        # Start background sync
        await sync.start()

        # Manual sync
        await sync.sync_results()
    """

    DEFAULT_SYNC_INTERVAL = 60  # seconds
    DEFAULT_PING_INTERVAL = 30  # seconds
    DEFAULT_RETRY_DELAY = 5  # seconds

    def __init__(
        self,
        cloud_url: str,
        api_key: str,
        result_store=None,
        pipeline_cache=None,
        sync_interval: int = DEFAULT_SYNC_INTERVAL,
        ping_interval: int = DEFAULT_PING_INTERVAL,
        on_status_change: Optional[Callable] = None,
    ):
        """
        Initialize the sync manager.

        Args:
            cloud_url: Cloud Studio URL
            api_key: API key for authentication
            result_store: ResultStore instance
            pipeline_cache: PipelineCache instance
            sync_interval: Seconds between sync attempts
            ping_interval: Seconds between connectivity checks
            on_status_change: Callback for status changes
        """
        self.cloud_url = cloud_url.rstrip("/")
        self.api_key = api_key
        self.result_store = result_store
        self.pipeline_cache = pipeline_cache
        self.sync_interval = sync_interval
        self.ping_interval = ping_interval
        self.on_status_change = on_status_change

        self._status = SyncStatus.IDLE
        self._connection = ConnectionStatus.DISCONNECTED
        self._last_sync: Optional[datetime] = None
        self._last_error: Optional[str] = None
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None

    @property
    def state(self) -> SyncState:
        """Get current sync state."""
        pending_results = 0
        if self.result_store:
            stats = self.result_store.get_stats()
            pending_results = stats.get("pending", 0) + stats.get("failed", 0)

        pending_pipelines = 0  # TODO: Track pending pipeline syncs

        return SyncState(
            status=self._status,
            connection=self._connection,
            last_sync=self._last_sync,
            pending_results=pending_results,
            pending_pipelines=pending_pipelines,
            last_error=self._last_error,
        )

    async def start(self) -> None:
        """Start background sync tasks."""
        if self._running:
            return

        self._running = True
        self._ping_task = asyncio.create_task(self._ping_loop())
        self._sync_task = asyncio.create_task(self._sync_loop())

        logger.info("Sync manager started")

    async def stop(self) -> None:
        """Stop background sync tasks."""
        self._running = False

        if self._ping_task:
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass

        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass

        logger.info("Sync manager stopped")

    async def check_connectivity(self) -> bool:
        """Check cloud connectivity."""
        self._connection = ConnectionStatus.CHECKING

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.cloud_url}/api/v1/health"
                headers = {"Authorization": f"Bearer {self.api_key}"}

                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        self._connection = ConnectionStatus.CONNECTED
                        self._notify_status_change()
                        return True

            self._connection = ConnectionStatus.DISCONNECTED
            self._notify_status_change()
            return False

        except Exception as e:
            logger.debug(f"Connectivity check failed: {e}")
            self._connection = ConnectionStatus.DISCONNECTED
            self._notify_status_change()
            return False

    async def sync_results(self) -> Dict[str, Any]:
        """Sync pending results to cloud."""
        if not self.result_store:
            return {"synced": 0, "failed": 0}

        if self._connection != ConnectionStatus.CONNECTED:
            if not await self.check_connectivity():
                return {"synced": 0, "failed": 0, "offline": True}

        self._status = SyncStatus.SYNCING
        self._notify_status_change()

        synced = 0
        failed = 0

        try:
            pending = self.result_store.get_pending(limit=50)

            async with aiohttp.ClientSession() as session:
                for result in pending:
                    try:
                        # Mark as syncing
                        self.result_store.mark_syncing(result.id)

                        # Upload to cloud
                        success = await self._upload_result(session, result)

                        if success:
                            self.result_store.mark_synced(result.id)
                            synced += 1
                        else:
                            self.result_store.mark_failed(result.id, "Upload failed")
                            failed += 1

                    except Exception as e:
                        logger.error(f"Failed to sync result {result.id}: {e}")
                        self.result_store.mark_failed(result.id, str(e))
                        failed += 1

            self._last_sync = datetime.utcnow()
            self._status = SyncStatus.IDLE
            self._last_error = None
            self._notify_status_change()

            logger.info(f"Sync completed: {synced} synced, {failed} failed")

            return {"synced": synced, "failed": failed}

        except Exception as e:
            self._status = SyncStatus.ERROR
            self._last_error = str(e)
            self._notify_status_change()
            logger.error(f"Sync failed: {e}")
            return {"synced": synced, "failed": failed, "error": str(e)}

    async def sync_pipelines(
        self,
        pipeline_names: Optional[List[str]] = None,
    ) -> Dict[str, bool]:
        """Sync pipelines from cloud."""
        if not self.pipeline_cache:
            return {}

        if self._connection != ConnectionStatus.CONNECTED:
            if not await self.check_connectivity():
                return {}

        self._status = SyncStatus.SYNCING
        self._notify_status_change()

        results = {}

        try:
            async with aiohttp.ClientSession() as session:
                # Get list of pipelines to sync
                if pipeline_names is None:
                    pipeline_names = await self._fetch_pipeline_list(session)

                for name in pipeline_names:
                    try:
                        config = await self._fetch_pipeline(session, name)
                        if config:
                            self.pipeline_cache.put(name, config, source="cloud")
                            results[name] = True
                        else:
                            results[name] = False
                    except Exception as e:
                        logger.error(f"Failed to sync pipeline {name}: {e}")
                        results[name] = False

            self._last_sync = datetime.utcnow()
            self._status = SyncStatus.IDLE
            self._notify_status_change()

            return results

        except Exception as e:
            self._status = SyncStatus.ERROR
            self._last_error = str(e)
            self._notify_status_change()
            logger.error(f"Pipeline sync failed: {e}")
            return results

    async def _upload_result(self, session: aiohttp.ClientSession, result) -> bool:
        """Upload a result to cloud."""
        url = f"{self.cloud_url}/api/v1/edge/results"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "id": result.id,
            "run_id": result.run_id,
            "pipeline_name": result.pipeline_name,
            "created_at": result.created_at.isoformat(),
            "output": result.output,
            "metadata": result.metadata,
        }

        try:
            async with session.post(url, headers=headers, json=payload) as resp:
                return resp.status in (200, 201)
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return False

    async def _fetch_pipeline_list(
        self,
        session: aiohttp.ClientSession,
    ) -> List[str]:
        """Fetch list of available pipelines from cloud."""
        url = f"{self.cloud_url}/api/v1/edge/pipelines"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("pipelines", [])
                return []
        except Exception as e:
            logger.error(f"Failed to fetch pipeline list: {e}")
            return []

    async def _fetch_pipeline(
        self,
        session: aiohttp.ClientSession,
        name: str,
    ) -> Optional[Dict[str, Any]]:
        """Fetch a pipeline configuration from cloud."""
        url = f"{self.cloud_url}/api/v1/edge/pipelines/{name}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except Exception as e:
            logger.error(f"Failed to fetch pipeline {name}: {e}")
            return None

    async def _ping_loop(self) -> None:
        """Background task to check connectivity."""
        while self._running:
            try:
                await self.check_connectivity()
                await asyncio.sleep(self.ping_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ping loop error: {e}")
                await asyncio.sleep(self.ping_interval)

    async def _sync_loop(self) -> None:
        """Background task to sync results."""
        while self._running:
            try:
                if self._connection == ConnectionStatus.CONNECTED:
                    await self.sync_results()
                await asyncio.sleep(self.sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                await asyncio.sleep(self.DEFAULT_RETRY_DELAY)

    def _notify_status_change(self) -> None:
        """Notify status change callback."""
        if self.on_status_change:
            try:
                self.on_status_change(self.state)
            except Exception as e:
                logger.error(f"Status change callback error: {e}")


class OfflineQueue:
    """
    Queue for offline operations.

    Stores operations to be executed when connectivity returns.
    """

    def __init__(self, max_size: int = 1000):
        self._queue: List[Dict[str, Any]] = []
        self.max_size = max_size

    def add(
        self,
        operation: str,
        data: Dict[str, Any],
        priority: int = 0,
    ) -> bool:
        """Add operation to queue."""
        if len(self._queue) >= self.max_size:
            return False

        self._queue.append({
            "operation": operation,
            "data": data,
            "priority": priority,
            "added_at": datetime.utcnow().isoformat(),
        })

        # Sort by priority
        self._queue.sort(key=lambda x: x["priority"], reverse=True)

        return True

    def pop(self) -> Optional[Dict[str, Any]]:
        """Get next operation from queue."""
        if not self._queue:
            return None
        return self._queue.pop(0)

    def peek(self) -> Optional[Dict[str, Any]]:
        """Peek at next operation without removing."""
        if not self._queue:
            return None
        return self._queue[0]

    def size(self) -> int:
        """Get queue size."""
        return len(self._queue)

    def clear(self) -> None:
        """Clear the queue."""
        self._queue.clear()
