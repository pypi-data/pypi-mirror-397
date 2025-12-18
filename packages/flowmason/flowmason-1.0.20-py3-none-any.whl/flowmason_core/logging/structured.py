"""
FlowMason Structured Logging and Metrics.

Provides context-aware logging for nodes and metrics collection for observability.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class StructuredLogger:
    """
    Structured logger with node context.

    Formats log messages with the node name prefix and supports
    structured logging with key=value pairs.

    Usage:
        logger = StructuredLogger("my-node")
        logger.info("Processing started", items=10, batch_size=5)
        # Output: [my-node] Processing started | items=10 batch_size=5
    """

    def __init__(self, node_name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize structured logger.

        Args:
            node_name: Name of the node for log prefix
            logger: Optional Python logger instance (defaults to flowmason.node.{name})
        """
        self.node_name = node_name
        self._logger = logger or logging.getLogger(f"flowmason.node.{node_name}")

    def _format(self, message: str, **kwargs) -> str:
        """Format message with node context and key=value pairs."""
        extra = " ".join(f"{k}={v}" for k, v in kwargs.items())
        if extra:
            return f"[{self.node_name}] {message} | {extra}"
        return f"[{self.node_name}] {message}"

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(self._format(message, **kwargs))

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._logger.info(self._format(message, **kwargs))

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(self._format(message, **kwargs))

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._logger.error(self._format(message, **kwargs))

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self._logger.exception(self._format(message, **kwargs))


class MetricsCollector:
    """
    Collects execution metrics for a node.

    Supports timers, counters, gauges, and timestamped events
    for detailed observability.

    Usage:
        metrics = MetricsCollector()
        metrics.start_timer("llm_call")
        # ... perform LLM call ...
        duration = metrics.stop_timer("llm_call")
        metrics.increment("tokens_used", 150)
        metrics.set_gauge("temperature", 0.7)
        metrics.record_event("completion", model="claude-3")
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._timers: Dict[str, float] = {}
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._events: List[Dict[str, Any]] = []

    def start_timer(self, name: str) -> None:
        """
        Start a named timer.

        Args:
            name: Timer name
        """
        self._timers[f"{name}_start"] = time.time()

    def stop_timer(self, name: str) -> float:
        """
        Stop a named timer and return elapsed time in milliseconds.

        Args:
            name: Timer name

        Returns:
            Elapsed time in milliseconds, or 0.0 if timer wasn't started
        """
        start_key = f"{name}_start"
        if start_key not in self._timers:
            return 0.0
        elapsed = (time.time() - self._timers[start_key]) * 1000
        self._timers[name] = elapsed
        del self._timers[start_key]
        return elapsed

    def increment(self, name: str, value: int = 1) -> None:
        """
        Increment a counter.

        Args:
            name: Counter name
            value: Value to add (default 1)
        """
        self._counters[name] = self._counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float) -> None:
        """
        Set a gauge value.

        Args:
            name: Gauge name
            value: Gauge value
        """
        self._gauges[name] = value

    def record_event(self, name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a timestamped event.

        Args:
            name: Event name
            data: Optional event data
        """
        self._events.append({
            "name": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data or {},
        })

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.

        Returns:
            Dict with timers, counters, gauges, and events
        """
        return {
            "timers": dict(self._timers),
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "events": list(self._events),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self._timers.clear()
        self._counters.clear()
        self._gauges.clear()
        self._events.clear()


class CacheInterface:
    """
    Simple cache interface for nodes.

    Provides async get/set/delete operations with optional TTL support.
    Default implementation uses an in-memory dict, but can be backed
    by Redis or other cache stores.

    Usage:
        cache = CacheInterface()
        await cache.set("key", {"data": "value"}, ttl_seconds=300)
        value = await cache.get("key")
    """

    def __init__(self, cache_store: Optional[Dict[str, Any]] = None):
        """
        Initialize cache interface.

        Args:
            cache_store: Optional external cache store (defaults to in-memory dict)
        """
        self._store = cache_store if cache_store is not None else {}
        self._ttls: Dict[str, float] = {}

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._store:
            return None

        # Check TTL
        if key in self._ttls:
            if time.time() > self._ttls[key]:
                del self._store[key]
                del self._ttls[key]
                return None

        return self._store[key]

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set a cached value with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional time-to-live in seconds
        """
        self._store[key] = value
        if ttl_seconds:
            self._ttls[key] = time.time() + ttl_seconds

    async def delete(self, key: str) -> bool:
        """
        Delete a cached value.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted, False otherwise
        """
        if key in self._store:
            del self._store[key]
            self._ttls.pop(key, None)
            return True
        return False

    async def clear(self) -> None:
        """Clear all cached values."""
        self._store.clear()
        self._ttls.clear()

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists and is not expired
        """
        value = await self.get(key)
        return value is not None
