"""
Event Trigger Models.

Defines data structures for event-driven pipeline triggers.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TriggerType(str, Enum):
    """Types of event triggers."""

    FILE_WATCH = "file_watch"
    PIPELINE_COMPLETED = "pipeline_completed"
    MCP_EVENT = "mcp_event"
    MESSAGE_QUEUE = "message_queue"
    CUSTOM = "custom"


class TriggerStatus(str, Enum):
    """Trigger status."""

    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"


class FileWatchEvent(str, Enum):
    """File system events to watch."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


class PipelineCompletionStatus(str, Enum):
    """Pipeline completion statuses to trigger on."""

    SUCCESS = "success"
    FAILED = "failed"
    ANY = "any"


class MessageQueueType(str, Enum):
    """Supported message queue types."""

    REDIS = "redis"
    RABBITMQ = "rabbitmq"
    SQS = "sqs"
    KAFKA = "kafka"


# Trigger Configuration Models


class FileWatchConfig(BaseModel):
    """Configuration for file watch triggers."""

    path: str = Field(description="Path pattern to watch (supports globs)")
    events: List[FileWatchEvent] = Field(
        default=[FileWatchEvent.CREATED],
        description="Events to trigger on"
    )
    recursive: bool = Field(
        default=True,
        description="Watch subdirectories"
    )
    debounce_seconds: float = Field(
        default=1.0,
        description="Debounce time for rapid file changes"
    )
    ignore_patterns: List[str] = Field(
        default_factory=list,
        description="Patterns to ignore (e.g., '*.tmp')"
    )


class PipelineCompletedConfig(BaseModel):
    """Configuration for pipeline completion triggers."""

    source_pipeline_id: str = Field(
        description="Pipeline ID to watch for completion"
    )
    status: PipelineCompletionStatus = Field(
        default=PipelineCompletionStatus.SUCCESS,
        description="Completion status to trigger on"
    )
    pass_outputs: bool = Field(
        default=True,
        description="Pass source pipeline outputs as inputs"
    )
    output_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Map source outputs to target inputs"
    )


class MCPEventConfig(BaseModel):
    """Configuration for MCP event triggers."""

    server_name: str = Field(description="MCP server name")
    event_type: str = Field(description="Event type to listen for")
    filter: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Event filter criteria"
    )
    input_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Map event data to pipeline inputs"
    )


class MessageQueueConfig(BaseModel):
    """Configuration for message queue triggers."""

    queue_type: MessageQueueType = Field(description="Queue type")
    connection_url: str = Field(description="Queue connection URL")
    queue_name: str = Field(description="Queue/topic name")
    consumer_group: Optional[str] = Field(
        default=None,
        description="Consumer group (for Kafka)"
    )
    ack_mode: str = Field(
        default="auto",
        description="Acknowledgment mode: 'auto' or 'manual'"
    )
    input_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Map message data to pipeline inputs"
    )
    batch_size: int = Field(
        default=1,
        description="Number of messages to process per trigger"
    )


class CustomTriggerConfig(BaseModel):
    """Configuration for custom triggers."""

    endpoint: str = Field(
        description="Internal event endpoint name"
    )
    filter: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Event filter criteria"
    )
    input_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Map event data to pipeline inputs"
    )


# Unified Trigger Configuration
TriggerConfig = Union[
    FileWatchConfig,
    PipelineCompletedConfig,
    MCPEventConfig,
    MessageQueueConfig,
    CustomTriggerConfig,
]


class EventTrigger(BaseModel):
    """Event trigger definition."""

    id: str = Field(description="Unique trigger ID")
    name: str = Field(description="Display name for the trigger")
    description: str = Field(default="", description="Trigger description")

    # Target pipeline
    pipeline_id: str = Field(description="Pipeline to execute when triggered")

    # Trigger configuration
    trigger_type: TriggerType = Field(description="Type of trigger")
    config: Dict[str, Any] = Field(
        description="Type-specific configuration"
    )

    # Execution settings
    enabled: bool = Field(default=True, description="Whether trigger is active")
    max_concurrent: int = Field(
        default=1,
        description="Maximum concurrent executions from this trigger"
    )
    cooldown_seconds: float = Field(
        default=0,
        description="Minimum time between triggers"
    )
    default_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default inputs for triggered executions"
    )

    # Status tracking
    status: TriggerStatus = Field(
        default=TriggerStatus.ACTIVE,
        description="Current trigger status"
    )
    last_triggered_at: Optional[datetime] = Field(
        default=None,
        description="Last trigger time"
    )
    trigger_count: int = Field(
        default=0,
        description="Total number of times triggered"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Last error message if in error state"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None)

    def get_typed_config(self) -> TriggerConfig:
        """Get the configuration as the appropriate typed model."""
        if self.trigger_type == TriggerType.FILE_WATCH:
            return FileWatchConfig(**self.config)
        elif self.trigger_type == TriggerType.PIPELINE_COMPLETED:
            return PipelineCompletedConfig(**self.config)
        elif self.trigger_type == TriggerType.MCP_EVENT:
            return MCPEventConfig(**self.config)
        elif self.trigger_type == TriggerType.MESSAGE_QUEUE:
            return MessageQueueConfig(**self.config)
        else:
            return CustomTriggerConfig(**self.config)


# Trigger Event Models


class TriggerEvent(BaseModel):
    """An event that was triggered."""

    id: str = Field(description="Unique event ID")
    trigger_id: str = Field(description="Trigger that caused this event")
    pipeline_id: str = Field(description="Pipeline that was executed")
    run_id: Optional[str] = Field(
        default=None,
        description="Execution run ID if started"
    )

    # Event details
    event_type: str = Field(description="Type of event that occurred")
    event_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event data/payload"
    )
    resolved_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Inputs resolved for the pipeline"
    )

    # Status
    status: str = Field(
        default="pending",
        description="Event status: pending, executing, completed, failed, skipped"
    )
    error_message: Optional[str] = Field(default=None)

    # Timing
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


# API Request/Response Models


class CreateTriggerRequest(BaseModel):
    """Request to create a new trigger."""

    name: str
    description: str = ""
    pipeline_id: str
    trigger_type: TriggerType
    config: Dict[str, Any]
    enabled: bool = True
    max_concurrent: int = 1
    cooldown_seconds: float = 0
    default_inputs: Dict[str, Any] = Field(default_factory=dict)


class UpdateTriggerRequest(BaseModel):
    """Request to update a trigger."""

    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    max_concurrent: Optional[int] = None
    cooldown_seconds: Optional[float] = None
    default_inputs: Optional[Dict[str, Any]] = None


class TriggerListResponse(BaseModel):
    """Response listing triggers."""

    triggers: List[EventTrigger]
    total: int
    page: int = 1
    page_size: int = 50


class TriggerEventListResponse(BaseModel):
    """Response listing trigger events."""

    events: List[TriggerEvent]
    total: int
    page: int = 1
    page_size: int = 50


class TriggerStatsResponse(BaseModel):
    """Statistics for triggers."""

    total_triggers: int
    active_triggers: int
    paused_triggers: int
    error_triggers: int
    total_events_24h: int
    successful_events_24h: int
    failed_events_24h: int
    triggers_by_type: Dict[str, int]
