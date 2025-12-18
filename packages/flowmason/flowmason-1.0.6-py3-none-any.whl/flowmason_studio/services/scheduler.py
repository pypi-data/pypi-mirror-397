"""
Background Scheduler Service.

Polls for due schedules and executes pipelines automatically.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Background scheduler that runs pipelines according to cron schedules.

    This service:
    - Polls for due schedules every N seconds
    - Executes pipelines when their scheduled time arrives
    - Updates schedule metadata (next_run_at, last_run_at, etc.)
    - Handles failures gracefully
    """

    def __init__(
        self,
        poll_interval: int = 60,
        max_concurrent_runs: int = 5,
    ):
        """
        Initialize the scheduler.

        Args:
            poll_interval: How often to check for due schedules (seconds)
            max_concurrent_runs: Maximum concurrent pipeline executions
        """
        self.poll_interval = poll_interval
        self.max_concurrent_runs = max_concurrent_runs
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._semaphore: Optional[asyncio.Semaphore] = None

    async def start(self):
        """Start the scheduler background task."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._semaphore = asyncio.Semaphore(self.max_concurrent_runs)
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            f"Scheduler started (poll_interval={self.poll_interval}s, "
            f"max_concurrent={self.max_concurrent_runs})"
        )

    async def stop(self):
        """Stop the scheduler."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")

    async def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            try:
                await self._check_and_run_schedules()
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)

            await asyncio.sleep(self.poll_interval)

    async def _check_and_run_schedules(self):
        """Check for due schedules and run them."""
        from flowmason_studio.services.schedule_storage import get_schedule_storage

        storage = get_schedule_storage()
        due_schedules = storage.get_due_schedules()

        if not due_schedules:
            return

        logger.info(f"Found {len(due_schedules)} due schedules")

        # Create tasks for each due schedule
        tasks = []
        for schedule in due_schedules:
            task = asyncio.create_task(self._execute_schedule(schedule))
            tasks.append(task)

        # Wait for all to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_schedule(self, schedule):
        """Execute a single scheduled pipeline run."""
        import uuid

        from flowmason_studio.services.execution_controller import create_controller
        from flowmason_studio.services.schedule_storage import get_schedule_storage
        from flowmason_studio.services.storage import get_storage

        # Use semaphore to limit concurrency
        async with self._semaphore:
            storage = get_schedule_storage()
            run_id = str(uuid.uuid4())
            scheduled_at = schedule.next_run_at or datetime.utcnow().isoformat()

            logger.info(
                f"Executing schedule '{schedule.name}' (id={schedule.id}) "
                f"for pipeline '{schedule.pipeline_name}'"
            )

            try:
                # Record the run
                storage.record_run(
                    schedule_id=schedule.id,
                    run_id=run_id,
                    scheduled_at=scheduled_at,
                    status="running",
                )

                # Update next run time immediately
                storage.update_next_run(schedule.id)

                # Load pipeline
                pipeline_storage = get_storage()
                pipeline = pipeline_storage.get_pipeline(schedule.pipeline_id)

                if not pipeline:
                    raise ValueError(f"Pipeline {schedule.pipeline_id} not found")

                # Execute pipeline
                controller = await create_controller(
                    run_id=run_id,
                    pipeline_id=schedule.pipeline_id,
                    org_id=schedule.org_id,
                )

                await controller.execute_pipeline(
                    pipeline_config=pipeline,
                    inputs=schedule.inputs,
                )

                # Mark as completed
                storage.update_run_status(
                    schedule_id=schedule.id,
                    run_id=run_id,
                    status="completed",
                )

                logger.info(
                    f"Schedule '{schedule.name}' completed successfully "
                    f"(run_id={run_id})"
                )

            except Exception as e:
                logger.error(
                    f"Schedule '{schedule.name}' failed: {e}",
                    exc_info=True,
                )

                storage.update_run_status(
                    schedule_id=schedule.id,
                    run_id=run_id,
                    status="failed",
                    error_message=str(e),
                )

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running


# Global instance
_scheduler: Optional[SchedulerService] = None


def get_scheduler() -> SchedulerService:
    """Get the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = SchedulerService()
    return _scheduler


async def start_scheduler():
    """Start the global scheduler."""
    scheduler = get_scheduler()
    await scheduler.start()


async def stop_scheduler():
    """Stop the global scheduler."""
    scheduler = get_scheduler()
    await scheduler.stop()
