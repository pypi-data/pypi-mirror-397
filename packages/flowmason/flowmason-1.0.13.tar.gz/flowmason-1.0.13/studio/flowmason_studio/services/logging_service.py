"""
Logging Service for FlowMason Studio.

Provides configurable logging with in-memory buffer for streaming to frontend.
Similar to Salesforce's debug logs with adjustable log levels.
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import RLock
from typing import Any, Deque, Dict, List, Optional


class LogLevel(str, Enum):
    """Log level enum matching Python logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_python_level(cls, level: int) -> "LogLevel":
        """Convert Python logging level to LogLevel."""
        if level <= logging.DEBUG:
            return cls.DEBUG
        elif level <= logging.INFO:
            return cls.INFO
        elif level <= logging.WARNING:
            return cls.WARNING
        elif level <= logging.ERROR:
            return cls.ERROR
        else:
            return cls.CRITICAL

    def to_python_level(self) -> int:
        """Convert to Python logging level."""
        return int(getattr(logging, self.value))


class LogCategory(str, Enum):
    """Categories for filtering logs (similar to Salesforce log categories)."""
    SYSTEM = "SYSTEM"          # System startup, config changes
    API = "API"                # HTTP requests/responses
    EXECUTION = "EXECUTION"    # Pipeline/node execution
    PROVIDER = "PROVIDER"      # LLM provider calls
    REGISTRY = "REGISTRY"      # Component registry operations
    STORAGE = "STORAGE"        # Data storage operations
    DATABASE = "DATABASE"      # Database operations (future)
    VALIDATION = "VALIDATION"  # Schema/input validation
    CALLOUT = "CALLOUT"        # External API calls (webhooks, etc.)


@dataclass
class LogEntry:
    """A single log entry."""
    id: str
    timestamp: str
    level: str
    category: str
    message: str
    logger_name: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "level": self.level,
            "category": self.category,
            "message": self.message,
            "logger_name": self.logger_name,
            "details": self.details,
            "duration_ms": self.duration_ms,
        }


@dataclass
class LogConfig:
    """Configuration for logging levels by category."""
    global_level: LogLevel = LogLevel.INFO
    category_levels: Dict[str, LogLevel] = field(default_factory=lambda: {
        LogCategory.SYSTEM.value: LogLevel.INFO,
        LogCategory.API.value: LogLevel.INFO,
        LogCategory.EXECUTION.value: LogLevel.INFO,
        LogCategory.PROVIDER.value: LogLevel.INFO,
        LogCategory.REGISTRY.value: LogLevel.INFO,
        LogCategory.STORAGE.value: LogLevel.WARNING,
        LogCategory.DATABASE.value: LogLevel.WARNING,
        LogCategory.VALIDATION.value: LogLevel.INFO,
        LogCategory.CALLOUT.value: LogLevel.INFO,
    })
    max_entries: int = 1000
    enabled: bool = True


class LogBufferHandler(logging.Handler):
    """Custom logging handler that writes to the log buffer."""

    def __init__(self, log_service: "LoggingService"):
        super().__init__()
        self.log_service = log_service
        self._id_counter = 0
        self._lock = RLock()

    def emit(self, record: logging.LogRecord):
        """Handle a log record."""
        try:
            # Generate unique ID
            with self._lock:
                self._id_counter += 1
                log_id = f"log_{int(time.time() * 1000)}_{self._id_counter}"

            # Determine category from logger name or extras
            category = getattr(record, 'category', None)
            if category is None:
                # Infer category from logger name
                name = record.name.lower()
                if 'api' in name or 'route' in name:
                    category = LogCategory.API.value
                elif 'execut' in name:
                    category = LogCategory.EXECUTION.value
                elif 'provider' in name:
                    category = LogCategory.PROVIDER.value
                elif 'registry' in name:
                    category = LogCategory.REGISTRY.value
                elif 'storage' in name:
                    category = LogCategory.STORAGE.value
                elif 'valid' in name:
                    category = LogCategory.VALIDATION.value
                else:
                    category = LogCategory.SYSTEM.value

            # Extract extra details
            details = getattr(record, 'details', None)
            duration_ms = getattr(record, 'duration_ms', None)

            # Create entry
            entry = LogEntry(
                id=log_id,
                timestamp=datetime.utcnow().isoformat() + "Z",
                level=record.levelname,
                category=category,
                message=self.format(record),
                logger_name=record.name,
                details=details,
                duration_ms=duration_ms,
            )

            self.log_service.add_entry(entry)

        except Exception:
            self.handleError(record)


class LoggingService:
    """
    Central logging service for FlowMason Studio.

    Features:
    - In-memory log buffer for streaming to frontend
    - Configurable log levels per category
    - Log retention with automatic cleanup
    - Category-based filtering
    """

    def __init__(self, config: Optional[LogConfig] = None):
        self._config = config or LogConfig()
        self._lock = RLock()
        self._entries: Deque[LogEntry] = deque(maxlen=self._config.max_entries)
        self._handler: Optional[LogBufferHandler] = None
        self._original_handlers: Dict[str, List[logging.Handler]] = {}

        # Configure logging
        self._setup_logging()

    def _setup_logging(self):
        """Set up Python logging with custom handler."""
        # Create and add our handler
        self._handler = LogBufferHandler(self)
        self._handler.setFormatter(logging.Formatter(
            '%(name)s - %(message)s'
        ))

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self._handler)
        root_logger.setLevel(self._config.global_level.to_python_level())

        # Also add to key loggers
        for logger_name in ['flowmason_core', 'flowmason_studio', 'flowmason_lab', 'uvicorn']:
            logger = logging.getLogger(logger_name)
            logger.addHandler(self._handler)
            logger.setLevel(self._config.global_level.to_python_level())

    @property
    def config(self) -> LogConfig:
        """Get current log configuration."""
        with self._lock:
            return self._config

    def set_config(self, config: LogConfig):
        """Update log configuration."""
        with self._lock:
            self._config = config

            # Update max entries
            if len(self._entries) > config.max_entries:
                # Trim old entries
                new_entries = deque(list(self._entries)[-config.max_entries:], maxlen=config.max_entries)
                self._entries = new_entries
            else:
                self._entries = deque(self._entries, maxlen=config.max_entries)

            # Update logging level
            root_logger = logging.getLogger()
            root_logger.setLevel(config.global_level.to_python_level())

            for logger_name in ['flowmason_core', 'flowmason_studio', 'flowmason_lab', 'uvicorn']:
                logger = logging.getLogger(logger_name)
                logger.setLevel(config.global_level.to_python_level())

    def set_global_level(self, level: LogLevel):
        """Set the global log level."""
        with self._lock:
            self._config.global_level = level
            self.set_config(self._config)

    def set_category_level(self, category: str, level: LogLevel):
        """Set log level for a specific category."""
        with self._lock:
            self._config.category_levels[category] = level

    def add_entry(self, entry: LogEntry):
        """Add a log entry to the buffer."""
        if not self._config.enabled:
            return

        # Check if entry should be logged based on category level
        category_level = self._config.category_levels.get(
            entry.category,
            self._config.global_level
        )
        entry_level = LogLevel(entry.level) if entry.level in LogLevel.__members__ else LogLevel.INFO

        if entry_level.to_python_level() >= category_level.to_python_level():
            with self._lock:
                self._entries.append(entry)

    def get_entries(
        self,
        limit: int = 100,
        offset: int = 0,
        level: Optional[LogLevel] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        since: Optional[str] = None,
    ) -> List[LogEntry]:
        """
        Get log entries with optional filtering.

        Args:
            limit: Maximum entries to return
            offset: Number of entries to skip
            level: Filter by minimum log level
            category: Filter by category
            search: Search string in message
            since: Only entries after this ISO timestamp
        """
        with self._lock:
            entries = list(self._entries)

        # Apply filters
        if level:
            level_value = level.to_python_level()
            entries = [e for e in entries if LogLevel(e.level).to_python_level() >= level_value]

        if category:
            entries = [e for e in entries if e.category == category]

        if search:
            search_lower = search.lower()
            entries = [e for e in entries if search_lower in e.message.lower()]

        if since:
            entries = [e for e in entries if e.timestamp > since]

        # Sort by timestamp descending (most recent first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)

        # Apply pagination
        return entries[offset:offset + limit]

    def get_entry_count(self) -> int:
        """Get total number of entries in buffer."""
        with self._lock:
            return len(self._entries)

    def clear(self):
        """Clear all log entries."""
        with self._lock:
            self._entries.clear()

    def log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
        logger_name: str = "flowmason_studio",
    ):
        """
        Log a message directly to the service.

        This is useful for structured logging from within the application.
        """
        logger = logging.getLogger(logger_name)
        extra = {
            'category': category.value,
            'details': details,
            'duration_ms': duration_ms,
        }
        logger.log(level.to_python_level(), message, extra=extra)


# Global singleton instance
_logging_service: Optional[LoggingService] = None
_service_lock = RLock()


def get_logging_service() -> LoggingService:
    """Get the global logging service instance."""
    global _logging_service
    with _service_lock:
        if _logging_service is None:
            _logging_service = LoggingService()
        return _logging_service


def log_debug(category: LogCategory, message: str, **kwargs):
    """Convenience function for debug logging."""
    get_logging_service().log(LogLevel.DEBUG, category, message, **kwargs)


def log_info(category: LogCategory, message: str, **kwargs):
    """Convenience function for info logging."""
    get_logging_service().log(LogLevel.INFO, category, message, **kwargs)


def log_warning(category: LogCategory, message: str, **kwargs):
    """Convenience function for warning logging."""
    get_logging_service().log(LogLevel.WARNING, category, message, **kwargs)


def log_error(category: LogCategory, message: str, **kwargs):
    """Convenience function for error logging."""
    get_logging_service().log(LogLevel.ERROR, category, message, **kwargs)
