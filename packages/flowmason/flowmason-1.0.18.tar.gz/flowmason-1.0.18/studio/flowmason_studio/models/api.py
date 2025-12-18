"""
API Request/Response Models for FlowMason Studio.

These Pydantic models define the API contract for all endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# =============================================================================
# Pipeline Status Enum
# =============================================================================

class PipelineStatus(str, Enum):
    """Status of a pipeline - similar to Salesforce Flow versioning."""
    DRAFT = "draft"  # Pipeline is being edited, not yet validated
    PUBLISHED = "published"  # Pipeline has been tested and is active


# =============================================================================
# Common Response Models
# =============================================================================

class APIError(BaseModel):
    """Standard API error response."""
    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class APIResponse(BaseModel):
    """Standard API success response wrapper."""
    success: bool = True
    data: Any = None
    message: Optional[str] = None


# =============================================================================
# Registry Models
# =============================================================================

class ComponentKind(str, Enum):
    """Type of component."""
    NODE = "node"
    OPERATOR = "operator"
    CONTROL_FLOW = "control_flow"


class ControlFlowType(str, Enum):
    """Type of control flow component."""
    CONDITIONAL = "conditional"
    ROUTER = "router"
    FOREACH = "foreach"
    TRYCATCH = "trycatch"
    SUBPIPELINE = "subpipeline"
    RETURN = "return"


class ComponentSummary(BaseModel):
    """Summary info for a component (list view).

    Note: This includes input_schema and requires_llm so the frontend
    can render the StageConfigPanel without additional API calls.
    """
    component_type: str = Field(description="Unique component type identifier")
    component_kind: ComponentKind = Field(description="node, operator, or control_flow")
    name: str = Field(description="Display name")
    category: str = Field(description="Component category")
    description: str = Field(description="Short description")
    version: str = Field(description="Component version")
    package_name: str = Field(description="Package this component belongs to")
    icon: str = Field(default="box")
    color: str = Field(default="#6B7280")
    # Fields needed for StageConfigPanel to render correctly
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for Input")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for Output")
    requires_llm: bool = Field(default=False, description="Whether component requires LLM")
    # Control flow specific
    control_flow_type: Optional[ControlFlowType] = Field(
        default=None, description="Type of control flow (for control_flow kind)"
    )


class AIConfig(BaseModel):
    """AI model configuration for nodes that require LLM."""
    recommended_providers: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Provider configurations: {provider_id: {model, temperature, ...}}"
    )
    default_provider: Optional[str] = Field(
        default=None,
        description="Default provider to use"
    )
    required_capabilities: Optional[List[str]] = Field(
        default=None,
        description="Required model capabilities (vision, function_calling, etc.)"
    )
    min_context_window: Optional[int] = Field(
        default=None,
        description="Minimum context window size required"
    )
    require_vision: bool = Field(default=False, description="Requires vision capability")
    require_function_calling: bool = Field(default=False, description="Requires function calling")


class ComponentDetail(ComponentSummary):
    """Detailed info for a component (detail view).

    Inherits input_schema, output_schema, requires_llm from ComponentSummary.
    Adds additional metadata fields including full AI configuration.
    """
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    # Full AI configuration (not just provider names)
    ai_config: Optional[AIConfig] = Field(
        default=None,
        description="AI model configuration for LLM-requiring nodes"
    )
    # Keep deprecated field for backwards compatibility
    recommended_providers: Optional[List[str]] = Field(
        default=None,
        description="DEPRECATED: Use ai_config.recommended_providers instead"
    )
    default_provider: Optional[str] = Field(
        default=None,
        description="Default provider (shortcut to ai_config.default_provider)"
    )
    package_version: str = Field(description="Package version")
    registered_at: Optional[datetime] = None
    # Runtime configuration from component Config class
    timeout_seconds: int = Field(default=60, description="Execution timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    supports_streaming: bool = Field(default=False, description="Whether streaming is supported")


class ComponentListResponse(BaseModel):
    """Response for listing components."""
    components: List[ComponentSummary]
    total: int
    categories: List[str]


class PackageSummary(BaseModel):
    """Summary info for a package."""
    name: str
    version: str
    description: str
    component_count: int
    components: List[str]
    registered_at: Optional[datetime] = None


class PackageListResponse(BaseModel):
    """Response for listing packages."""
    packages: List[PackageSummary]
    total: int


class DeployPackageRequest(BaseModel):
    """Request to deploy a package (metadata only, file uploaded separately)."""
    # The actual file is uploaded via multipart/form-data
    pass


class DeployPackageResponse(BaseModel):
    """Response after deploying a package."""
    package_name: str
    package_version: str
    components_registered: List[str]
    message: str


# =============================================================================
# Pipeline Models
# =============================================================================

class LLMSettings(BaseModel):
    """LLM settings for a stage."""
    provider: Optional[str] = Field(default=None, description="Override provider (e.g., 'anthropic', 'openai')")
    model: Optional[str] = Field(default=None, description="Override model (e.g., 'claude-sonnet-4-20250514')")
    temperature: Optional[float] = Field(default=None, description="Temperature 0.0-1.0")
    max_tokens: Optional[int] = Field(default=None, description="Max response tokens")
    top_p: Optional[float] = Field(default=None, description="Nucleus sampling")
    stop_sequences: Optional[List[str]] = Field(default=None, description="Stop sequences")


class StagePosition(BaseModel):
    """Position of a stage in the canvas."""
    x: float = 0
    y: float = 0


class PipelineStage(BaseModel):
    """A single stage in a pipeline."""
    id: str = Field(description="Unique stage identifier within pipeline")
    component_type: str = Field(description="Component type to execute")
    name: Optional[str] = Field(default=None, description="Display name for the stage")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Static configuration values"
    )
    input_mapping: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mapping from config to component Input"
    )
    depends_on: List[str] = Field(
        default_factory=list,
        description="Stage IDs this stage depends on"
    )
    position: Optional[StagePosition] = Field(default=None, description="Canvas position")
    llm_settings: Optional[LLMSettings] = Field(default=None, description="LLM settings for this stage")
    timeout_ms: Optional[int] = Field(default=None, description="Stage timeout")


class PipelineInputSchema(BaseModel):
    """Schema definition for pipeline input."""
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class PipelineOutputSchema(BaseModel):
    """Schema definition for pipeline output."""
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class PipelineCreate(BaseModel):
    """Request to create a new pipeline."""
    name: str = Field(description="Pipeline display name")
    description: str = Field(default="", description="Pipeline description")
    input_schema: PipelineInputSchema = Field(default_factory=PipelineInputSchema)
    output_schema: PipelineOutputSchema = Field(default_factory=PipelineOutputSchema)
    stages: List[PipelineStage] = Field(default_factory=list)
    output_stage_id: Optional[str] = Field(
        default=None,
        description="ID of stage that produces final output"
    )
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    is_template: bool = Field(default=False, description="Whether this pipeline is a template")
    sample_input: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Sample input data for testing the pipeline"
    )
    output_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Default output routing configuration (destinations, allowlist settings)"
    )


class PipelineUpdate(BaseModel):
    """Request to update an existing pipeline."""
    name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[PipelineInputSchema] = None
    output_schema: Optional[PipelineOutputSchema] = None
    stages: Optional[List[PipelineStage]] = None
    output_stage_id: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    is_template: Optional[bool] = None
    sample_input: Optional[Dict[str, Any]] = None
    output_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Output routing configuration (destinations, allowlist settings)"
    )


class PipelineSummary(BaseModel):
    """Summary info for a pipeline (list view)."""
    id: str
    name: str
    description: str
    version: str
    stage_count: int
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_template: bool = Field(default=False)
    status: PipelineStatus = Field(default=PipelineStatus.DRAFT, description="Pipeline status (draft/published)")
    last_test_run_id: Optional[str] = Field(default=None, description="ID of last successful test run")
    published_at: Optional[datetime] = Field(default=None, description="When pipeline was published")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PipelineDetail(BaseModel):
    """Detailed info for a pipeline."""
    id: str
    name: str
    description: str
    version: str
    input_schema: PipelineInputSchema
    output_schema: PipelineOutputSchema
    stages: List[PipelineStage]
    output_stage_id: Optional[str]
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_template: bool = Field(default=False)
    status: PipelineStatus = Field(default=PipelineStatus.DRAFT, description="Pipeline status (draft/published)")
    sample_input: Optional[Dict[str, Any]] = Field(default=None, description="Sample input data for testing")
    last_test_run_id: Optional[str] = Field(default=None, description="ID of last successful test run")
    published_at: Optional[datetime] = Field(default=None, description="When pipeline was published")
    output_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Default output routing configuration for this pipeline"
    )
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PipelineListResponse(BaseModel):
    """Response for listing pipelines."""
    items: List[PipelineSummary]
    total: int
    page: int = 1
    page_size: int = 100
    has_more: bool = False


# =============================================================================
# Execution Models
# =============================================================================

class RunStatus(str, Enum):
    """Status of a pipeline run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutePipelineRequest(BaseModel):
    """Request to execute a pipeline."""
    inputs: Dict[str, Any] = Field(description="Pipeline input data")
    provider_overrides: Optional[Dict[str, str]] = Field(
        default=None,
        description="Override providers for specific stages"
    )
    trace_enabled: bool = Field(default=True, description="Enable execution tracing")


class DebugRunRequest(BaseModel):
    """Request to start a debug run from a pipeline file or inline definition."""
    pipeline: Dict[str, Any] = Field(description="Pipeline definition (inline JSON)")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Pipeline input data")
    breakpoints: List[str] = Field(default_factory=list, description="Stage IDs to break on")
    stop_on_entry: bool = Field(default=False, description="Pause before first stage")


class UsageMetricsResponse(BaseModel):
    """Usage metrics from execution."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0


class StageResultResponse(BaseModel):
    """Result from a single stage execution."""
    stage_id: str
    component_type: str
    status: str
    output: Optional[Any] = None
    error: Optional[str] = None
    usage: UsageMetricsResponse = Field(default_factory=UsageMetricsResponse)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class StageResult(BaseModel):
    """Result from a single stage execution (simplified)."""
    stage_id: str
    status: str
    output: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


class RunSummary(BaseModel):
    """Summary of a pipeline run."""
    id: str
    pipeline_id: str
    status: RunStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


class TraceStage(BaseModel):
    """Stage trace info for frontend compatibility."""
    stage_id: str
    component_type: str = ""
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    usage: Optional[UsageMetricsResponse] = None


class ExecutionTrace(BaseModel):
    """Execution trace with stages array for frontend."""
    stages: List[TraceStage] = Field(default_factory=list)


class RunDetail(BaseModel):
    """Detailed info for a pipeline run."""
    id: str
    pipeline_id: str
    status: RunStatus
    inputs: Dict[str, Any]
    output: Optional[Any] = None
    error: Optional[str] = None
    stage_results: Optional[Dict[str, StageResult]] = Field(default=None)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    trace_id: Optional[str] = None
    usage: Optional[UsageMetricsResponse] = None
    trace: Optional[ExecutionTrace] = None

    def model_post_init(self, __context) -> None:
        """Build trace from stage_results after initialization."""
        if self.stage_results and not self.trace:
            stages = [
                TraceStage(
                    stage_id=stage_id,
                    component_type=stage_id,  # Use stage_id as component_type fallback
                    status=result.status,
                    started_at=result.started_at,
                    completed_at=result.completed_at,
                    output=result.output,
                    error=result.error,
                )
                for stage_id, result in self.stage_results.items()
            ]
            object.__setattr__(self, 'trace', ExecutionTrace(stages=stages))


class ExecutePipelineResponse(BaseModel):
    """Response from executing a pipeline."""
    run_id: str
    pipeline_id: str
    pipeline_version: str
    status: RunStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    usage: UsageMetricsResponse = Field(default_factory=UsageMetricsResponse)
    trace_url: Optional[str] = None


class RunListResponse(BaseModel):
    """Response for listing runs."""
    runs: List[RunSummary]
    total: int


# =============================================================================
# Health/Status Models
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    components_loaded: int = 0
    pipelines_count: int = 0


# =============================================================================
# Pipeline Publishing Models
# =============================================================================

class PublishPipelineRequest(BaseModel):
    """Request to publish a pipeline after successful test."""
    test_run_id: str = Field(description="ID of the successful test run that validates this pipeline")


class PublishPipelineResponse(BaseModel):
    """Response after publishing a pipeline."""
    pipeline_id: str
    status: PipelineStatus
    published_at: datetime
    version: str
    message: str


class UnpublishPipelineResponse(BaseModel):
    """Response after unpublishing a pipeline."""
    pipeline_id: str
    status: PipelineStatus
    message: str


# =============================================================================
# Debug & Stage Retry Models
# =============================================================================

class StageInputOutput(BaseModel):
    """Detailed input/output data for a stage (for debugging)."""
    stage_id: str
    component_type: str
    stage_name: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Resolved input data passed to the stage")
    output_data: Optional[Any] = Field(default=None, description="Output produced by the stage")
    config: Dict[str, Any] = Field(default_factory=dict, description="Stage configuration")
    llm_settings: Optional[LLMSettings] = None
    status: str
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class DebugRunDetail(BaseModel):
    """Extended run detail with full debug information for each stage."""
    id: str
    pipeline_id: str
    pipeline_name: str
    status: RunStatus
    inputs: Dict[str, Any]
    output: Optional[Any] = None
    error: Optional[str] = None
    stages: List[StageInputOutput] = Field(default_factory=list, description="Detailed stage execution info")
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    usage: Optional[UsageMetricsResponse] = None


class RetryStageRequest(BaseModel):
    """Request to retry a specific stage with optional config/input overrides."""
    run_id: str = Field(description="Original run ID to retry from")
    stage_id: str = Field(description="Stage ID to retry")
    config_override: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Override stage config (e.g., modify prompt)"
    )
    input_override: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Override resolved input data"
    )
    continue_from_stage: bool = Field(
        default=True,
        description="If True, continue executing subsequent stages after retry"
    )


class RetryStageResponse(BaseModel):
    """Response after retrying a stage."""
    new_run_id: str
    retried_stage_id: str
    status: RunStatus
    stage_result: StageInputOutput
    message: str


class TestPipelineRequest(BaseModel):
    """Request to test a pipeline with sample input."""
    sample_input: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Input to use for test. If not provided, uses pipeline's sample_input"
    )
    debug_mode: bool = Field(
        default=True,
        description="Enable detailed debug info for each stage"
    )


class TestPipelineResponse(BaseModel):
    """Response from testing a pipeline."""
    run_id: str
    pipeline_id: str
    status: RunStatus
    is_success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    debug_info: Optional[DebugRunDetail] = None
    can_publish: bool = Field(description="Whether this test run can be used to publish the pipeline")


# =============================================================================
# Output Destination Models (Input/Output Architecture)
# =============================================================================

class OutputDestinationType(str, Enum):
    """Type of output destination for pipeline results."""
    WEBHOOK = "webhook"
    EMAIL = "email"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"


class WebhookConfig(BaseModel):
    """Configuration for webhook output destination."""
    url: str = Field(description="Webhook URL to POST results to")
    method: str = Field(default="POST", description="HTTP method (POST, PUT)")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")
    timeout_ms: int = Field(default=30000, description="Request timeout in milliseconds")
    retry_count: int = Field(default=3, description="Number of retries on failure")


class EmailConfig(BaseModel):
    """Configuration for email output destination."""
    to: List[str] = Field(description="Recipient email addresses")
    cc: List[str] = Field(default_factory=list, description="CC recipients")
    subject_template: str = Field(description="Subject template (Jinja2)")
    body_template: str = Field(description="Body template (Jinja2)")
    is_html: bool = Field(default=False, description="Whether body is HTML")


class DatabaseConfig(BaseModel):
    """Configuration for database output destination."""
    connection_id: str = Field(description="ID of stored database connection")
    table: str = Field(description="Target table name")
    operation: str = Field(default="insert", description="Operation: insert, upsert")
    column_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Map output fields to columns"
    )


class MessageQueueConfig(BaseModel):
    """Configuration for message queue output destination."""
    connection_id: str = Field(description="ID of stored queue connection")
    queue_name: str = Field(description="Queue/topic name")
    message_template: Optional[str] = Field(
        default=None,
        description="Optional Jinja2 template for message body"
    )


class OutputDestination(BaseModel):
    """A single output destination for pipeline results.

    Destinations can be configured to receive success results, error results,
    or both. Error destinations can filter by specific error types.
    """
    id: str = Field(description="Unique destination identifier")
    type: OutputDestinationType = Field(description="Destination type")
    name: str = Field(description="Human-readable destination name")
    enabled: bool = Field(default=True, description="Whether destination is active")
    config: Dict[str, Any] = Field(
        description="Type-specific configuration (WebhookConfig, EmailConfig, etc.)"
    )
    on_success: bool = Field(default=True, description="Deliver on successful completion")
    on_error: bool = Field(default=False, description="Deliver on pipeline error")
    error_types: Optional[List[str]] = Field(
        default=None,
        description="Filter error delivery to specific types (TIMEOUT, VALIDATION, etc.)"
    )
    payload_template: Optional[str] = Field(
        default=None,
        description="Jinja2 template to transform output before delivery"
    )


class PipelineOutputConfig(BaseModel):
    """Output configuration for a pipeline.

    Defines default destinations set by the pipeline designer.
    Callers can extend or override these at runtime.
    """
    destinations: List[OutputDestination] = Field(
        default_factory=list,
        description="List of output destinations"
    )
    allow_caller_destinations: bool = Field(
        default=True,
        description="Allow callers to add their own destinations"
    )
    allow_caller_override: bool = Field(
        default=False,
        description="Allow callers to replace default destinations entirely"
    )


class OutputDeliveryResult(BaseModel):
    """Result of delivering output to a single destination."""
    destination_id: str
    destination_type: OutputDestinationType
    success: bool
    status_code: Optional[int] = None
    error: Optional[str] = None
    delivered_at: datetime
    retry_count: int = 0


class OutputDeliveryReport(BaseModel):
    """Summary of all output deliveries for a run."""
    run_id: str
    total_destinations: int
    successful_deliveries: int
    failed_deliveries: int
    results: List[OutputDeliveryResult]


# =============================================================================
# Named Pipeline Invocation Models
# =============================================================================

class RunPipelineRequest(BaseModel):
    """Request to run a pipeline by name with optional output configuration.

    This is the primary API for external systems to invoke pipelines.
    Supports named pipelines with optional version pinning and caller-specified
    output destinations.

    Example:
        POST /api/v1/run
        {
            "pipeline": "customer-support-triage@1.0.0",
            "input": {"ticket_id": "T-123", "message": "..."},
            "output_config": {
                "destinations": [
                    {"id": "my-webhook", "type": "webhook", "config": {...}}
                ]
            }
        }
    """
    pipeline: str = Field(
        description="Pipeline name with optional version: 'my-pipeline' or 'my-pipeline@1.0.0'"
    )
    input: Dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline input data"
    )
    output_config: Optional[PipelineOutputConfig] = Field(
        default=None,
        description="Caller-specified output configuration (extends or replaces defaults)"
    )
    async_mode: bool = Field(
        default=True,
        description="If True, returns immediately with run_id. If False, waits for completion."
    )
    callback_url: Optional[str] = Field(
        default=None,
        description="URL to POST results to when complete (shorthand for webhook destination)"
    )


class RunPipelineResponse(BaseModel):
    """Response from running a pipeline by name."""
    run_id: str
    pipeline_id: str
    pipeline_name: str
    pipeline_version: str
    status: RunStatus
    result: Optional[Any] = Field(
        default=None,
        description="Pipeline result (only populated if async_mode=False)"
    )
    error: Optional[str] = None
    delivery_report: Optional[OutputDeliveryReport] = Field(
        default=None,
        description="Output delivery results (only populated if async_mode=False)"
    )
    message: str = Field(default="Pipeline execution started")
