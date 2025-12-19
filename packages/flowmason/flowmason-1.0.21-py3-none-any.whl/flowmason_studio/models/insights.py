"""
Analytics Insights Models.

Data models for AI-powered execution analytics and insights.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InsightType(str, Enum):
    """Types of insights generated."""

    COST_SPIKE = "cost_spike"
    COST_OPTIMIZATION = "cost_optimization"
    FAILURE_PATTERN = "failure_pattern"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    USAGE_TREND = "usage_trend"
    MODEL_RECOMMENDATION = "model_recommendation"
    ANOMALY = "anomaly"
    EFFICIENCY = "efficiency"
    RELIABILITY = "reliability"


class InsightSeverity(str, Enum):
    """Severity levels for insights."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class InsightCategory(str, Enum):
    """Categories for grouping insights."""

    COST = "cost"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    USAGE = "usage"
    OPTIMIZATION = "optimization"


class Insight(BaseModel):
    """A single AI-generated insight."""

    id: str
    type: InsightType
    severity: InsightSeverity
    category: InsightCategory
    title: str
    description: str

    # Context
    pipeline_id: Optional[str] = None
    stage_id: Optional[str] = None

    # Supporting data
    data: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)

    # Recommendations
    recommendations: List[str] = Field(default_factory=list)

    # Time context
    detected_at: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None


class TrendDirection(str, Enum):
    """Direction of a trend."""

    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class MetricTrend(BaseModel):
    """Trend analysis for a metric."""

    metric_name: str
    current_value: float
    previous_value: float
    change_percent: float
    direction: TrendDirection
    is_significant: bool = False


class CostBreakdown(BaseModel):
    """Detailed cost breakdown."""

    total_cost: float
    by_provider: Dict[str, float] = Field(default_factory=dict)
    by_model: Dict[str, float] = Field(default_factory=dict)
    by_pipeline: Dict[str, float] = Field(default_factory=dict)
    by_stage_type: Dict[str, float] = Field(default_factory=dict)


class PerformanceMetrics(BaseModel):
    """Performance analysis metrics."""

    avg_duration_ms: float
    p50_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    slowest_stages: List[Dict[str, Any]] = Field(default_factory=list)
    fastest_stages: List[Dict[str, Any]] = Field(default_factory=list)


class FailureAnalysis(BaseModel):
    """Failure pattern analysis."""

    total_failures: int
    failure_rate: float
    by_error_type: Dict[str, int] = Field(default_factory=dict)
    by_stage: Dict[str, int] = Field(default_factory=dict)
    by_pipeline: Dict[str, int] = Field(default_factory=dict)
    common_patterns: List[str] = Field(default_factory=list)
    mttr_seconds: Optional[float] = None  # Mean time to recovery


class UsagePattern(BaseModel):
    """Usage pattern analysis."""

    peak_hours: List[int] = Field(default_factory=list)
    peak_days: List[str] = Field(default_factory=list)
    busiest_pipeline_id: Optional[str] = None
    most_used_model: Optional[str] = None
    avg_daily_runs: float = 0.0
    avg_daily_cost: float = 0.0


class ModelEfficiency(BaseModel):
    """Model efficiency analysis."""

    provider: str
    model: str
    avg_latency_ms: float
    avg_tokens_per_request: float
    cost_per_1k_tokens: float
    success_rate: float
    usage_count: int


class CostForecast(BaseModel):
    """Cost projection/forecast."""

    current_daily_avg: float
    projected_daily: float
    projected_weekly: float
    projected_monthly: float
    trend: TrendDirection
    confidence: float


class OptimizationOpportunity(BaseModel):
    """An optimization opportunity."""

    type: str
    description: str
    current_cost: float
    potential_savings: float
    savings_percent: float
    recommendation: str
    difficulty: str = "medium"  # easy, medium, hard


class InsightsReport(BaseModel):
    """Complete insights report."""

    generated_at: str
    period_start: str
    period_end: str
    org_id: str

    # Summary metrics
    total_runs: int
    total_cost: float
    avg_success_rate: float
    avg_duration_ms: float

    # Trends
    cost_trend: MetricTrend
    usage_trend: MetricTrend
    performance_trend: MetricTrend
    reliability_trend: MetricTrend

    # Detailed analysis
    cost_breakdown: CostBreakdown
    performance_metrics: PerformanceMetrics
    failure_analysis: FailureAnalysis
    usage_patterns: UsagePattern
    cost_forecast: CostForecast

    # Model efficiency
    model_efficiency: List[ModelEfficiency] = Field(default_factory=list)

    # Opportunities
    optimization_opportunities: List[OptimizationOpportunity] = Field(default_factory=list)

    # All insights
    insights: List[Insight] = Field(default_factory=list)

    # Counts by category
    insights_by_category: Dict[str, int] = Field(default_factory=dict)
    insights_by_severity: Dict[str, int] = Field(default_factory=dict)


# API Request/Response Models

class InsightsRequest(BaseModel):
    """Request for insights analysis."""

    days: int = Field(default=30, ge=1, le=90)
    pipeline_id: Optional[str] = None
    include_recommendations: bool = True
    include_forecasts: bool = True


class InsightsListResponse(BaseModel):
    """Response with list of insights."""

    insights: List[Insight]
    total: int
    period_start: str
    period_end: str


class InsightsSummary(BaseModel):
    """Quick summary of key insights."""

    generated_at: str
    total_insights: int
    critical_count: int
    warning_count: int
    info_count: int

    # Top insights by category
    top_cost_insight: Optional[Insight] = None
    top_performance_insight: Optional[Insight] = None
    top_reliability_insight: Optional[Insight] = None

    # Quick metrics
    estimated_savings: float = 0.0
    performance_change_percent: float = 0.0
    reliability_change_percent: float = 0.0
