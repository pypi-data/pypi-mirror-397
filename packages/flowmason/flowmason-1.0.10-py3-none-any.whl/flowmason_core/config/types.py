"""
Configuration Types for FlowMason.

Defines the data structures for pipeline and component configuration.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    pass


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""

    max_retries: int = Field(default=3, ge=0, le=10)
    initial_delay_ms: int = Field(default=1000, ge=100)
    max_delay_ms: int = Field(default=30000, ge=1000)
    backoff_multiplier: float = Field(default=2.0, ge=1.0, le=5.0)


class ComponentConfig(BaseModel):
    """
    Configuration for a single component in a pipeline stage.

    This is the JSON configuration that gets mapped to a component's
    Pydantic Input model at runtime.
    """

    model_config = ConfigDict(extra="allow")

    # Identification
    id: str = Field(description="Unique identifier for this stage in the pipeline")
    type: str = Field(description="Component type (e.g., 'generator', 'support_triage')")

    # Package reference (optional - defaults to looking up by type)
    component_package: Optional[str] = Field(
        default=None,
        description="Full package reference (e.g., 'acme-corp/support-triage@1.0.0')"
    )

    # Input mapping - how to populate the component's Input model
    input_mapping: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mapping from config values to component Input fields"
    )

    # Runtime overrides
    provider: Optional[str] = Field(
        default=None,
        description="Override the default provider for this component"
    )
    timeout_ms: Optional[int] = Field(
        default=None,
        ge=100,
        le=600000,
        description="Execution timeout in milliseconds"
    )
    retry_config: Optional[RetryConfig] = Field(
        default=None,
        description="Retry configuration for failures"
    )

    # Dependencies
    depends_on: List[str] = Field(
        default_factory=list,
        description="List of stage IDs this component depends on"
    )


class PipelineInput(BaseModel):
    """
    Schema definition for pipeline input.

    This defines what the pipeline accepts as input when called via API.
    """

    model_config = ConfigDict(extra="forbid")

    type: str = Field(default="object")
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class PipelineOutput(BaseModel):
    """
    Schema definition for pipeline output.

    This defines what the pipeline returns when executed.
    """

    model_config = ConfigDict(extra="forbid")

    type: str = Field(default="object")
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class CompositionConfig(BaseModel):
    """
    Configuration for composing a sub-pipeline within a parent pipeline.

    Allows embedding and reusing pipelines as stages within other pipelines.
    """

    model_config = ConfigDict(extra="allow")

    id: str = Field(description="Unique stage ID for this composition")
    pipeline: str = Field(description="Reference to pipeline (name or name@version)")
    input_mapping: Dict[str, Any] = Field(
        default_factory=dict,
        description="Map parent context to sub-pipeline input"
    )
    output_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Map sub-pipeline output to parent context"
    )
    depends_on: List[str] = Field(
        default_factory=list,
        description="Dependencies from parent pipeline"
    )


class PipelineConfig(BaseModel):
    """
    Complete configuration for a FlowMason pipeline.

    Pipelines are DAGs of components that get exposed as HTTP APIs.
    Supports inheritance (extends) and composition (sub-pipelines).
    """

    model_config = ConfigDict(extra="allow")

    # Identification
    id: str = Field(description="Unique identifier for the pipeline")
    name: str = Field(description="Human-readable name")
    version: str = Field(default="1.0.0", description="Semantic version")
    description: str = Field(default="", description="Pipeline description")

    # Inheritance
    extends: Optional[str] = Field(
        default=None,
        description="Parent pipeline reference (name or name@version)"
    )
    abstract: bool = Field(
        default=False,
        description="If true, pipeline cannot be executed directly (must be extended)"
    )
    overrides: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Stage overrides by stage ID (for inherited pipelines)"
    )

    # Compositions (sub-pipelines)
    compositions: List[CompositionConfig] = Field(
        default_factory=list,
        description="Sub-pipelines to embed as stages"
    )

    # Schemas
    input_schema: PipelineInput = Field(
        default_factory=PipelineInput,
        description="JSON Schema for pipeline input"
    )
    output_schema: PipelineOutput = Field(
        default_factory=PipelineOutput,
        description="JSON Schema for pipeline output"
    )

    # Stages (components in execution order)
    stages: List[ComponentConfig] = Field(
        default_factory=list,
        description="Pipeline stages (components) in DAG order"
    )

    # Output configuration
    output_stage_id: Optional[str] = Field(
        default=None,
        description="ID of the stage that produces the final output"
    )

    # Metadata
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None

    def get_stage(self, stage_id: str) -> Optional[ComponentConfig]:
        """Get a stage by ID."""
        for stage in self.stages:
            if stage.id == stage_id:
                return stage
        return None

    def get_dependencies(self, stage_id: str) -> List[str]:
        """Get dependency IDs for a stage."""
        stage = self.get_stage(stage_id)
        return stage.depends_on if stage else []


class LLMHelper:
    """
    Helper class for components to call LLM providers.

    Provides a simple interface for text generation that abstracts
    away provider selection and configuration.

    Usage in components:
        async def execute(self, input: Input, context: ExecutionContext) -> Output:
            response = await context.llm.generate(
                prompt="Hello, world!",
                system_prompt="You are a helpful assistant.",
            )
            return Output(text=response.content)
    """

    def __init__(self, provider: Any, default_model: Optional[str] = None):
        """
        Initialize the LLM helper.

        Args:
            provider: The provider instance to use for generation
            default_model: Default model to use (overrides provider default)
        """
        self._provider = provider
        self._default_model = default_model

    @property
    def provider(self) -> Any:
        """Get the underlying provider instance."""
        return self._provider

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return str(self._provider.name) if self._provider else "none"

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Any:
        """
        Generate text synchronously.

        Args:
            prompt: User prompt
            system_prompt: System prompt / instructions
            model: Model to use (defaults to provider's default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific options

        Returns:
            ProviderResponse with content and metadata
        """
        if not self._provider:
            raise RuntimeError("No LLM provider configured")

        return self._provider.call(
            prompt=prompt,
            system=system_prompt,
            model=model or self._default_model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Any:
        """
        Generate text asynchronously.

        Args:
            prompt: User prompt
            system_prompt: System prompt / instructions
            model: Model to use (defaults to provider's default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific options

        Returns:
            ProviderResponse with content and metadata
        """
        if not self._provider:
            raise RuntimeError("No LLM provider configured")

        return await self._provider.call_async(
            prompt=prompt,
            system=system_prompt,
            model=model or self._default_model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    def parse_json(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from response text.

        Handles markdown code blocks, surrounding text, etc.
        """
        if self._provider:
            result = self._provider.parse_json(text)
            return dict(result) if isinstance(result, dict) else {}

        # Fallback basic JSON parsing
        import json
        result = json.loads(text.strip())
        return dict(result) if isinstance(result, dict) else {}


class ExecutionContext(BaseModel):
    """
    Runtime context passed to components during execution.

    Contains information about the current execution, available providers,
    and pipeline-level data.
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    # Execution identity
    run_id: str = Field(description="Unique ID for this execution run")
    pipeline_id: str = Field(description="ID of the pipeline being executed")
    pipeline_version: str = Field(description="Version of the pipeline")

    # Stage context
    stage_id: Optional[str] = Field(
        default=None,
        description="Current stage being executed"
    )

    # Input data
    pipeline_input: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original input to the pipeline"
    )

    # Upstream results
    stage_outputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Outputs from previously executed stages"
    )

    # Environment variables (sanitized)
    environment: Dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables available to components"
    )

    # Runtime variables (e.g., loop variables from control flow)
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime variables set by control flow (e.g., loop item, index)"
    )

    # Provider references (set at runtime)
    providers: Dict[str, Any] = Field(
        default_factory=dict,
        description="Available provider instances"
    )

    # LLM Helper (set at runtime)
    llm: Optional[LLMHelper] = Field(
        default=None,
        description="LLM helper for text generation"
    )

    # Logging and Metrics (set at runtime)
    logger: Optional[Any] = Field(
        default=None,
        description="Structured logger for node output"
    )
    metrics: Optional[Any] = Field(
        default=None,
        description="Metrics collector for observability"
    )
    cache: Optional[Any] = Field(
        default=None,
        description="Cache interface for node data"
    )

    # Tracing
    trace_id: Optional[str] = Field(
        default=None,
        description="Distributed tracing ID"
    )

    def with_stage(self, stage_id: str) -> "ExecutionContext":
        """Create a copy of context with updated stage_id."""
        return self.model_copy(update={"stage_id": stage_id})

    def add_stage_output(self, stage_id: str, output: Any) -> None:
        """Record output from a completed stage."""
        self.stage_outputs[stage_id] = output

    def get_provider(self, name: str) -> Optional[Any]:
        """Get a specific provider by name."""
        return self.providers.get(name)


class ValidationError(BaseModel):
    """A single validation error."""

    field: str = Field(description="Field that failed validation")
    error_type: str = Field(description="Type of error (e.g., 'missing_required', 'type_mismatch')")
    message: str = Field(description="Human-readable error message")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix")


class ValidationResult(BaseModel):
    """Result of validating a configuration."""

    is_valid: bool = Field(description="Whether validation passed")
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    def add_error(
        self,
        field: str,
        error_type: str,
        message: str,
        suggestion: Optional[str] = None
    ) -> None:
        """Add a validation error."""
        self.errors.append(ValidationError(
            field=field,
            error_type=error_type,
            message=message,
            suggestion=suggestion
        ))
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(message)


class MappingError(Exception):
    """Error during config-to-input mapping."""

    def __init__(self, field: str, message: str, suggestion: Optional[str] = None):
        self.field = field
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"Mapping error for field '{field}': {message}")


class TemplateError(Exception):
    """Error resolving a template variable."""

    def __init__(self, template: str, message: str):
        self.template = template
        self.message = message
        super().__init__(f"Template error in '{template}': {message}")
