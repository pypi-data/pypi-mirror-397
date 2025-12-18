"""
Prompt A/B Testing Models.

Defines data structures for prompt experiments and variants.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExperimentStatus(str, Enum):
    """Experiment status."""

    DRAFT = "draft"  # Not yet started
    RUNNING = "running"  # Actively collecting data
    PAUSED = "paused"  # Temporarily stopped
    COMPLETED = "completed"  # Finished, has results
    ARCHIVED = "archived"  # No longer active


class MetricType(str, Enum):
    """Types of metrics to track."""

    LATENCY = "latency"  # Response time in ms
    TOKENS = "tokens"  # Token count
    RATING = "rating"  # User rating (1-5)
    THUMBS = "thumbs"  # Thumbs up/down (0 or 1)
    COMPLETION = "completion"  # Task completion rate
    CUSTOM = "custom"  # Custom numeric metric


class MetricAggregation(str, Enum):
    """How to aggregate metrics."""

    AVERAGE = "average"
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    P50 = "p50"  # Median
    P95 = "p95"
    P99 = "p99"


class PromptVariant(BaseModel):
    """A variant in an A/B test."""

    id: str = Field(description="Unique variant ID")
    name: str = Field(description="Variant name (e.g., 'Control', 'Variant A')")
    description: str = Field(default="", description="Variant description")

    # Prompt configuration
    prompt_id: Optional[str] = Field(
        default=None,
        description="Reference to existing prompt template"
    )
    content: Optional[str] = Field(
        default=None,
        description="Inline prompt content (if not using prompt_id)"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="System prompt for this variant"
    )

    # Model settings (can override experiment defaults)
    model: Optional[str] = Field(default=None)
    temperature: Optional[float] = Field(default=None)
    max_tokens: Optional[int] = Field(default=None)

    # Traffic allocation
    weight: float = Field(
        default=1.0,
        ge=0,
        description="Relative weight for traffic allocation"
    )

    # Tracking
    is_control: bool = Field(
        default=False,
        description="Whether this is the control variant"
    )
    impressions: int = Field(default=0, description="Number of times shown")
    created_at: Optional[datetime] = Field(default=None)


class MetricDefinition(BaseModel):
    """Definition of a metric to track."""

    name: str = Field(description="Metric name")
    type: MetricType = Field(description="Type of metric")
    description: str = Field(default="")
    aggregation: MetricAggregation = Field(
        default=MetricAggregation.AVERAGE,
        description="How to aggregate this metric"
    )
    higher_is_better: bool = Field(
        default=True,
        description="Whether higher values are better"
    )
    target_value: Optional[float] = Field(
        default=None,
        description="Target value to beat"
    )


class Experiment(BaseModel):
    """A prompt A/B test experiment."""

    id: str = Field(description="Unique experiment ID")
    name: str = Field(description="Experiment name")
    description: str = Field(default="")
    org_id: str = Field(description="Organization ID")

    # Experiment configuration
    status: ExperimentStatus = Field(default=ExperimentStatus.DRAFT)
    variants: List[PromptVariant] = Field(
        default_factory=list,
        description="Prompt variants to test"
    )

    # Default model settings (can be overridden per variant)
    default_model: Optional[str] = Field(default=None)
    default_temperature: Optional[float] = Field(default=None)
    default_max_tokens: Optional[int] = Field(default=None)

    # Metrics to track
    metrics: List[MetricDefinition] = Field(
        default_factory=list,
        description="Metrics to collect"
    )
    primary_metric: str = Field(
        default="rating",
        description="Primary metric for determining winner"
    )

    # Targeting
    pipeline_ids: List[str] = Field(
        default_factory=list,
        description="Pipelines where this experiment runs"
    )
    stage_ids: List[str] = Field(
        default_factory=list,
        description="Specific stages to target"
    )
    user_percentage: float = Field(
        default=100.0,
        ge=0, le=100,
        description="Percentage of users to include in experiment"
    )

    # Duration
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    min_samples_per_variant: int = Field(
        default=100,
        description="Minimum samples before declaring winner"
    )

    # Results
    winner_variant_id: Optional[str] = Field(default=None)
    confidence_level: Optional[float] = Field(default=None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None)
    tags: List[str] = Field(default_factory=list)


class MetricRecord(BaseModel):
    """A single metric data point."""

    id: str = Field(description="Record ID")
    experiment_id: str = Field(description="Experiment this belongs to")
    variant_id: str = Field(description="Variant that was shown")
    metric_name: str = Field(description="Name of the metric")
    value: float = Field(description="Metric value")

    # Context
    run_id: Optional[str] = Field(default=None)
    pipeline_id: Optional[str] = Field(default=None)
    stage_id: Optional[str] = Field(default=None)
    user_id: Optional[str] = Field(default=None)

    # Metadata
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VariantStats(BaseModel):
    """Statistics for a variant."""

    variant_id: str
    variant_name: str
    is_control: bool
    impressions: int
    samples: int

    # Metric stats
    metrics: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Metric name -> {mean, std, min, max, p50, p95}"
    )

    # Comparison to control
    lift_vs_control: Optional[float] = Field(
        default=None,
        description="Percentage improvement over control"
    )
    p_value: Optional[float] = Field(
        default=None,
        description="Statistical significance (p-value)"
    )
    is_significant: bool = Field(
        default=False,
        description="Whether result is statistically significant"
    )


class ExperimentResults(BaseModel):
    """Results of an experiment."""

    experiment_id: str
    experiment_name: str
    status: ExperimentStatus
    primary_metric: str

    # Variant statistics
    variant_stats: List[VariantStats]

    # Winner determination
    has_winner: bool = False
    winner_variant_id: Optional[str] = None
    winner_variant_name: Optional[str] = None
    confidence_level: Optional[float] = None
    recommendation: str = Field(
        default="",
        description="Human-readable recommendation"
    )

    # Metadata
    total_samples: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_hours: Optional[float] = None


# API Request/Response Models


class CreateExperimentRequest(BaseModel):
    """Request to create an experiment."""

    name: str
    description: str = ""
    variants: List[PromptVariant]
    metrics: List[MetricDefinition] = Field(default_factory=list)
    primary_metric: str = "rating"
    default_model: Optional[str] = None
    default_temperature: Optional[float] = None
    default_max_tokens: Optional[int] = None
    pipeline_ids: List[str] = Field(default_factory=list)
    stage_ids: List[str] = Field(default_factory=list)
    user_percentage: float = 100.0
    min_samples_per_variant: int = 100
    tags: List[str] = Field(default_factory=list)


class UpdateExperimentRequest(BaseModel):
    """Request to update an experiment."""

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ExperimentStatus] = None
    variants: Optional[List[PromptVariant]] = None
    metrics: Optional[List[MetricDefinition]] = None
    primary_metric: Optional[str] = None
    user_percentage: Optional[float] = None
    min_samples_per_variant: Optional[int] = None
    tags: Optional[List[str]] = None


class RecordMetricRequest(BaseModel):
    """Request to record a metric."""

    variant_id: str
    metric_name: str
    value: float
    run_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    stage_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecordMetricsRequest(BaseModel):
    """Request to record multiple metrics at once."""

    variant_id: str
    metrics: Dict[str, float] = Field(description="Metric name -> value")
    run_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    stage_id: Optional[str] = None
    user_id: Optional[str] = None


class SelectVariantRequest(BaseModel):
    """Request to select a variant for a user."""

    user_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    stage_id: Optional[str] = None


class SelectVariantResponse(BaseModel):
    """Response with selected variant."""

    experiment_id: str
    variant_id: str
    variant_name: str
    prompt_content: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    is_control: bool


class ExperimentListResponse(BaseModel):
    """Response listing experiments."""

    experiments: List[Experiment]
    total: int
    page: int = 1
    page_size: int = 50


class ExperimentStatsResponse(BaseModel):
    """Quick stats for experiments."""

    total_experiments: int
    running_experiments: int
    completed_experiments: int
    total_impressions: int
    experiments_with_winners: int
