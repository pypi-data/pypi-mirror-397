"""
Cancellation Support for FlowMason.

Provides cancellation tokens for graceful run cancellation.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Optional, Set

logger = logging.getLogger(__name__)


class CancellationToken:
    """
    Token for cancelling pipeline execution.

    Usage:
        token = CancellationToken()

        # Start execution with token
        task = asyncio.create_task(executor.execute(stages, input, token))

        # Later, cancel if needed
        token.cancel("User requested cancellation")

        # In executor, check token periodically
        if token.is_cancelled:
            raise CancellationError(token.reason)
    """

    def __init__(self) -> None:
        self._cancelled: bool = False
        self._reason: Optional[str] = None
        self._cancelled_at: Optional[datetime] = None
        self._callbacks: list[Callable[["CancellationToken"], Awaitable[None]]] = []
        self._active_tasks: Set[asyncio.Task[Any]] = set()
        self._lock = asyncio.Lock()

    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancelled

    @property
    def reason(self) -> Optional[str]:
        """Get the cancellation reason."""
        return self._reason

    @property
    def cancelled_at(self) -> Optional[datetime]:
        """Get when cancellation was requested."""
        return self._cancelled_at

    def cancel(self, reason: Optional[str] = None) -> None:
        """
        Request cancellation.

        Args:
            reason: Optional reason for cancellation
        """
        if self._cancelled:
            return  # Already cancelled

        self._cancelled = True
        self._reason = reason or "Cancellation requested"
        self._cancelled_at = datetime.utcnow()

        logger.info(f"Cancellation requested: {self._reason}")

        # Cancel all tracked tasks
        for task in self._active_tasks:
            if not task.done():
                task.cancel()

    async def cancel_async(self, reason: Optional[str] = None) -> None:
        """
        Request cancellation and run callbacks.

        Args:
            reason: Optional reason for cancellation
        """
        self.cancel(reason)

        # Run cancellation callbacks
        for callback in self._callbacks:
            try:
                await callback(self)
            except Exception as e:
                logger.warning(f"Cancellation callback failed: {e}")

    def register_callback(
        self,
        callback: Callable[["CancellationToken"], Awaitable[None]]
    ) -> None:
        """
        Register a callback to be called on cancellation.

        Args:
            callback: Async function to call when cancelled
        """
        self._callbacks.append(callback)

    def track_task(self, task: asyncio.Task) -> None:
        """
        Track a task for cancellation.

        Args:
            task: Task to track
        """
        self._active_tasks.add(task)
        task.add_done_callback(lambda t: self._active_tasks.discard(t))

    def untrack_task(self, task: asyncio.Task) -> None:
        """
        Stop tracking a task.

        Args:
            task: Task to untrack
        """
        self._active_tasks.discard(task)

    def check(self) -> None:
        """
        Check if cancelled and raise if so.

        Raises:
            asyncio.CancelledError: If cancellation was requested
        """
        if self._cancelled:
            raise asyncio.CancelledError(self._reason)

    async def check_async(self) -> None:
        """
        Async version of check that also yields to event loop.

        This allows checking between stages without blocking.
        """
        await asyncio.sleep(0)  # Yield to event loop
        self.check()

    def __bool__(self) -> bool:
        """Allow using token in boolean context (True if NOT cancelled)."""
        return not self._cancelled


class CancellationScope:
    """
    Context manager for automatic task tracking.

    Usage:
        async with CancellationScope(token) as scope:
            task = scope.create_task(my_coroutine())
            result = await task
    """

    def __init__(self, token: CancellationToken):
        self.token = token
        self._tasks: Set[asyncio.Task] = set()

    async def __aenter__(self) -> "CancellationScope":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        # Cancel any remaining tasks if we're being cancelled
        if self.token.is_cancelled:
            for task in self._tasks:
                if not task.done():
                    task.cancel()

        # Wait for all tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        return False

    def create_task(self, coro: Any) -> asyncio.Task:
        """
        Create and track a task.

        Args:
            coro: Coroutine to run

        Returns:
            The created task
        """
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        self.token.track_task(task)
        task.add_done_callback(lambda t: self._tasks.discard(t))
        return task


def cancellable(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """
    Decorator that makes a function check for cancellation.

    The function must accept a 'token' keyword argument.

    Usage:
        @cancellable
        async def my_function(data, token: CancellationToken = None):
            # Will check for cancellation at start
            ...
    """
    async def wrapper(*args, **kwargs) -> Any:
        token = kwargs.get('token')
        if token and isinstance(token, CancellationToken):
            token.check()
        return await func(*args, **kwargs)
    return wrapper
