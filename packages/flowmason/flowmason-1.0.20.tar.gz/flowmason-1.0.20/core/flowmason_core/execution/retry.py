"""
Retry Logic for FlowMason.

Provides retry functionality with exponential backoff for component execution.
"""

import asyncio
import logging
from functools import wraps
from typing import Awaitable, Callable, Optional, Set, Type, TypeVar

from flowmason_core.config.types import RetryConfig
from flowmason_core.execution.types import (
    RetryableError,
    RetryExhaustedError,
    TimeoutExecutionError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


# Default errors that are retryable
DEFAULT_RETRYABLE_ERRORS: Set[Type[Exception]] = {
    RetryableError,
    TimeoutExecutionError,
    ConnectionError,
    TimeoutError,
    asyncio.TimeoutError,
}


def calculate_backoff(
    attempt: int,
    config: RetryConfig,
    jitter: bool = True,
) -> float:
    """
    Calculate the backoff delay for a retry attempt.

    Uses exponential backoff with optional jitter.

    Args:
        attempt: The current attempt number (0-indexed)
        config: Retry configuration
        jitter: Whether to add random jitter

    Returns:
        Delay in seconds
    """
    import random

    # Exponential backoff: initial_delay * (multiplier ^ attempt)
    delay_ms = config.initial_delay_ms * (config.backoff_multiplier ** attempt)

    # Cap at max delay
    delay_ms = min(delay_ms, config.max_delay_ms)

    # Add jitter (±25%)
    if jitter:
        jitter_factor = 0.75 + (random.random() * 0.5)
        delay_ms *= jitter_factor

    return delay_ms / 1000.0  # Convert to seconds


def is_retryable(
    error: Exception,
    retryable_errors: Optional[Set[Type[Exception]]] = None,
) -> bool:
    """
    Check if an error is retryable.

    Args:
        error: The exception to check
        retryable_errors: Set of exception types that are retryable

    Returns:
        True if the error can be retried
    """
    retryable_types = retryable_errors or DEFAULT_RETRYABLE_ERRORS

    # Check if it's a FlowMason error with recoverable flag
    if hasattr(error, "recoverable") and error.recoverable:
        return True

    # Check if it's an instance of any retryable type
    for error_type in retryable_types:
        if isinstance(error, error_type):
            return True

    # Check for specific error conditions
    error_msg = str(error).lower()

    # Rate limit errors
    if "rate" in error_msg and "limit" in error_msg:
        return True

    # Temporary failures
    if any(x in error_msg for x in ["temporary", "retry", "again", "unavailable"]):
        return True

    return False


async def with_retry(
    func: Callable[[], Awaitable[T]],
    config: Optional[RetryConfig] = None,
    retryable_errors: Optional[Set[Type[Exception]]] = None,
    component_id: Optional[str] = None,
    component_type: Optional[str] = None,
    on_retry: Optional[Callable[[int, Exception, float], Awaitable[None]]] = None,
) -> T:
    """
    Execute an async function with retry logic.

    Args:
        func: Async function to execute
        config: Retry configuration (defaults to RetryConfig defaults)
        retryable_errors: Set of exception types that are retryable
        component_id: Component ID for error reporting
        component_type: Component type for error reporting
        on_retry: Optional callback called before each retry (attempt, error, delay)

    Returns:
        The result of the function

    Raises:
        RetryExhaustedError: If all retries are exhausted
        Exception: The original exception if not retryable
    """
    if config is None:
        config = RetryConfig()

    errors = retryable_errors or DEFAULT_RETRYABLE_ERRORS
    last_error: Optional[Exception] = None

    for attempt in range(config.max_retries + 1):
        try:
            return await func()

        except Exception as e:
            last_error = e

            # Check if we should retry
            if not is_retryable(e, errors):
                logger.debug(f"Error is not retryable: {type(e).__name__}: {e}")
                raise

            # Check if we have retries left
            if attempt >= config.max_retries:
                logger.warning(
                    f"Retry exhausted after {attempt + 1} attempts for "
                    f"{component_id or 'unknown'}: {e}"
                )
                break

            # Calculate delay
            delay = calculate_backoff(attempt, config)

            logger.info(
                f"Retry {attempt + 1}/{config.max_retries} for "
                f"{component_id or 'unknown'} after {delay:.2f}s: {e}"
            )

            # Call retry callback if provided
            if on_retry:
                await on_retry(attempt, e, delay)

            # Wait before retrying
            await asyncio.sleep(delay)

    # All retries exhausted
    raise RetryExhaustedError(
        component_id=component_id or "unknown",
        attempts=config.max_retries + 1,
        last_error=last_error,
        component_type=component_type,
    )


def retry(
    config: Optional[RetryConfig] = None,
    retryable_errors: Optional[Set[Type[Exception]]] = None,
):
    """
    Decorator for adding retry logic to async functions.

    Usage:
        @retry(config=RetryConfig(max_retries=3))
        async def my_function():
            ...

    Args:
        config: Retry configuration
        retryable_errors: Set of exception types that are retryable
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await with_retry(
                lambda: func(*args, **kwargs),
                config=config,
                retryable_errors=retryable_errors,
            )
        return wrapper
    return decorator


class RetryContext:
    """
    Context manager for retry operations with state tracking.

    Usage:
        async with RetryContext(config=config, component_id="stage-1") as ctx:
            result = await ctx.execute(my_async_func)
    """

    def __init__(
        self,
        config: Optional[RetryConfig] = None,
        component_id: Optional[str] = None,
        component_type: Optional[str] = None,
        retryable_errors: Optional[Set[Type[Exception]]] = None,
    ):
        self.config = config or RetryConfig()
        self.component_id = component_id
        self.component_type = component_type
        self.retryable_errors = retryable_errors or DEFAULT_RETRYABLE_ERRORS
        self.attempts = 0
        self.last_error: Optional[Exception] = None
        self.errors: list = []

    async def __aenter__(self) -> "RetryContext":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False

    async def execute(
        self,
        func: Callable[[], Awaitable[T]],
        on_retry: Optional[Callable[[int, Exception, float], Awaitable[None]]] = None,
    ) -> T:
        """Execute the function with retry logic."""
        self.attempts = 0
        self.errors = []

        for attempt in range(self.config.max_retries + 1):
            self.attempts = attempt + 1
            try:
                return await func()

            except Exception as e:
                self.last_error = e
                self.errors.append({
                    "attempt": attempt + 1,
                    "error_type": type(e).__name__,
                    "message": str(e),
                })

                if not is_retryable(e, self.retryable_errors):
                    raise

                if attempt >= self.config.max_retries:
                    break

                delay = calculate_backoff(attempt, self.config)

                if on_retry:
                    await on_retry(attempt, e, delay)

                await asyncio.sleep(delay)

        raise RetryExhaustedError(
            component_id=self.component_id or "unknown",
            attempts=self.attempts,
            last_error=self.last_error,
            component_type=self.component_type,
        )

    @property
    def stats(self) -> dict:
        """Get retry statistics."""
        return {
            "attempts": self.attempts,
            "errors": self.errors,
            "exhausted": self.attempts > self.config.max_retries,
        }
