"""
AI-Powered Insights Service.

Analyzes execution data to generate actionable insights:
- Pattern detection (usage trends, failure patterns, cost spikes)
- Anomaly detection (unusual behavior, performance degradation)
- Recommendations (cost optimization, model selection, reliability)
"""

import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import mean, median, stdev
from typing import Any, Dict, List, Optional, Tuple

from flowmason_studio.models.insights import (
    CostBreakdown,
    CostForecast,
    FailureAnalysis,
    Insight,
    InsightCategory,
    InsightsReport,
    InsightSeverity,
    InsightsSummary,
    InsightType,
    MetricTrend,
    ModelEfficiency,
    OptimizationOpportunity,
    PerformanceMetrics,
    TrendDirection,
    UsagePattern,
)
from flowmason_studio.services.storage import get_pipeline_storage, get_run_storage
from flowmason_studio.services.usage_storage import PROVIDER_PRICING, get_usage_storage


class InsightsService:
    """Service for generating AI-powered insights from execution data."""

    # Thresholds for anomaly detection
    COST_SPIKE_THRESHOLD = 0.5  # 50% increase is a spike
    FAILURE_RATE_WARNING = 0.1  # 10% failure rate triggers warning
    FAILURE_RATE_CRITICAL = 0.25  # 25% failure rate is critical
    PERFORMANCE_DEGRADATION_THRESHOLD = 0.3  # 30% slower is degradation
    SIGNIFICANCE_THRESHOLD = 0.1  # 10% change is significant

    def __init__(self):
        """Initialize the insights service."""
        self._run_storage = get_run_storage()
        self._pipeline_storage = get_pipeline_storage()
        self._usage_storage = get_usage_storage()

    def generate_report(
        self,
        org_id: str,
        days: int = 30,
        pipeline_id: Optional[str] = None,
        include_recommendations: bool = True,
        include_forecasts: bool = True,
    ) -> InsightsReport:
        """Generate a complete insights report."""
        now = datetime.utcnow()
        period_end = now
        period_start = now - timedelta(days=days)

        # Get all runs in period
        runs = self._get_runs_in_period(period_start, period_end, pipeline_id)
        prev_runs = self._get_runs_in_period(
            period_start - timedelta(days=days),
            period_start,
            pipeline_id,
        )

        # Get usage data
        usage_summary = self._usage_storage.get_summary(
            org_id=org_id,
            pipeline_id=pipeline_id,
            days=days,
            include_by_pipeline=True,
        )

        prev_usage_summary = self._usage_storage.get_summary(
            org_id=org_id,
            pipeline_id=pipeline_id,
            days=days * 2,  # Get previous period
            include_by_pipeline=True,
        )

        # Generate insights
        insights: List[Insight] = []

        # Cost analysis
        cost_breakdown = self._analyze_cost_breakdown(usage_summary)
        cost_trend = self._calculate_trend(
            "cost",
            usage_summary.total_cost_usd,
            prev_usage_summary.total_cost_usd / 2 if prev_usage_summary.total_cost_usd else 0,
        )
        insights.extend(self._detect_cost_anomalies(usage_summary, prev_usage_summary, org_id))

        # Performance analysis
        performance_metrics = self._analyze_performance(runs)
        prev_performance = self._analyze_performance(prev_runs)
        performance_trend = self._calculate_trend(
            "avg_duration",
            performance_metrics.avg_duration_ms,
            prev_performance.avg_duration_ms if prev_performance else 0,
            lower_is_better=True,
        )
        insights.extend(self._detect_performance_issues(
            performance_metrics, prev_performance, runs
        ))

        # Failure analysis
        failure_analysis = self._analyze_failures(runs)
        prev_failure_analysis = self._analyze_failures(prev_runs)
        reliability_trend = self._calculate_trend(
            "success_rate",
            1 - failure_analysis.failure_rate,
            1 - prev_failure_analysis.failure_rate if prev_failure_analysis else 1,
        )
        insights.extend(self._detect_failure_patterns(failure_analysis, runs))

        # Usage patterns
        usage_patterns = self._analyze_usage_patterns(runs, usage_summary)
        usage_trend = self._calculate_trend(
            "run_count",
            len(runs),
            len(prev_runs) if prev_runs else 0,
        )
        insights.extend(self._detect_usage_anomalies(usage_patterns, runs))

        # Model efficiency
        model_efficiency = self._analyze_model_efficiency(usage_summary)
        if include_recommendations:
            insights.extend(self._generate_model_recommendations(model_efficiency))

        # Cost forecast
        cost_forecast = CostForecast(
            current_daily_avg=0,
            projected_daily=0,
            projected_weekly=0,
            projected_monthly=0,
            trend=TrendDirection.STABLE,
            confidence=0,
        )
        if include_forecasts:
            cost_forecast = self._forecast_costs(usage_summary, days)

        # Optimization opportunities
        opportunities: List[OptimizationOpportunity] = []
        if include_recommendations:
            opportunities = self._identify_optimization_opportunities(
                usage_summary, model_efficiency, performance_metrics, failure_analysis
            )

        # Calculate summary stats
        total_runs = len(runs)
        success_count = sum(1 for r in runs if r.get("status") == "completed")
        avg_success_rate = success_count / total_runs if total_runs > 0 else 0

        # Count insights by category and severity
        insights_by_category: Dict[str, int] = defaultdict(int)
        insights_by_severity: Dict[str, int] = defaultdict(int)

        for insight in insights:
            insights_by_category[insight.category.value] += 1
            insights_by_severity[insight.severity.value] += 1

        return InsightsReport(
            generated_at=now.isoformat(),
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            org_id=org_id,
            total_runs=total_runs,
            total_cost=usage_summary.total_cost_usd,
            avg_success_rate=avg_success_rate,
            avg_duration_ms=performance_metrics.avg_duration_ms,
            cost_trend=cost_trend,
            usage_trend=usage_trend,
            performance_trend=performance_trend,
            reliability_trend=reliability_trend,
            cost_breakdown=cost_breakdown,
            performance_metrics=performance_metrics,
            failure_analysis=failure_analysis,
            usage_patterns=usage_patterns,
            cost_forecast=cost_forecast,
            model_efficiency=model_efficiency,
            optimization_opportunities=opportunities,
            insights=insights,
            insights_by_category=dict(insights_by_category),
            insights_by_severity=dict(insights_by_severity),
        )

    def get_summary(
        self,
        org_id: str,
        days: int = 7,
        pipeline_id: Optional[str] = None,
    ) -> InsightsSummary:
        """Get a quick summary of key insights."""
        report = self.generate_report(
            org_id=org_id,
            days=days,
            pipeline_id=pipeline_id,
            include_recommendations=True,
            include_forecasts=False,
        )

        # Count by severity
        critical_count = sum(1 for i in report.insights if i.severity == InsightSeverity.CRITICAL)
        warning_count = sum(1 for i in report.insights if i.severity == InsightSeverity.WARNING)
        info_count = sum(1 for i in report.insights if i.severity == InsightSeverity.INFO)

        # Get top insight by category
        def get_top_insight(category: InsightCategory) -> Optional[Insight]:
            category_insights = [i for i in report.insights if i.category == category]
            if not category_insights:
                return None
            # Sort by severity (critical > warning > info)
            severity_order = {InsightSeverity.CRITICAL: 0, InsightSeverity.WARNING: 1, InsightSeverity.INFO: 2}
            return sorted(category_insights, key=lambda x: severity_order[x.severity])[0]

        # Calculate estimated savings
        estimated_savings = sum(opp.potential_savings for opp in report.optimization_opportunities)

        return InsightsSummary(
            generated_at=report.generated_at,
            total_insights=len(report.insights),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            top_cost_insight=get_top_insight(InsightCategory.COST),
            top_performance_insight=get_top_insight(InsightCategory.PERFORMANCE),
            top_reliability_insight=get_top_insight(InsightCategory.RELIABILITY),
            estimated_savings=estimated_savings,
            performance_change_percent=report.performance_trend.change_percent,
            reliability_change_percent=report.reliability_trend.change_percent,
        )

    def get_insights(
        self,
        org_id: str,
        days: int = 7,
        pipeline_id: Optional[str] = None,
        category: Optional[InsightCategory] = None,
        severity: Optional[InsightSeverity] = None,
        limit: int = 50,
    ) -> List[Insight]:
        """Get filtered list of insights."""
        report = self.generate_report(
            org_id=org_id,
            days=days,
            pipeline_id=pipeline_id,
            include_recommendations=True,
            include_forecasts=False,
        )

        insights = report.insights

        # Filter by category
        if category:
            insights = [i for i in insights if i.category == category]

        # Filter by severity
        if severity:
            insights = [i for i in insights if i.severity == severity]

        # Sort by severity (critical first)
        severity_order = {InsightSeverity.CRITICAL: 0, InsightSeverity.WARNING: 1, InsightSeverity.INFO: 2}
        insights = sorted(insights, key=lambda x: severity_order[x.severity])

        return insights[:limit]

    # =========================================================================
    # Data Collection
    # =========================================================================

    def _get_runs_in_period(
        self,
        start: datetime,
        end: datetime,
        pipeline_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all runs within a time period."""
        all_runs = [r.model_dump() for r in self._run_storage.list(limit=10000)[0]]

        filtered = []
        for run in all_runs:
            started_at = run.get("started_at")
            if not started_at:
                continue

            try:
                run_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                run_time = run_time.replace(tzinfo=None)  # Make naive for comparison
                if start <= run_time <= end:
                    if pipeline_id is None or run.get("pipeline_id") == pipeline_id:
                        filtered.append(run)
            except (ValueError, TypeError):
                continue

        return filtered

    # =========================================================================
    # Analysis Methods
    # =========================================================================

    def _analyze_cost_breakdown(self, usage_summary: Any) -> CostBreakdown:
        """Analyze cost distribution."""
        by_provider: Dict[str, float] = {}
        for provider, data in usage_summary.by_provider.items():
            by_provider[provider] = data.get("cost_usd", 0)

        by_model: Dict[str, float] = {}
        for model_key, data in usage_summary.by_model.items():
            by_model[model_key] = data.get("cost_usd", 0)

        by_pipeline: Dict[str, float] = {}
        if usage_summary.by_pipeline:
            for pipeline_id, data in usage_summary.by_pipeline.items():
                by_pipeline[pipeline_id] = data.get("cost_usd", 0)

        return CostBreakdown(
            total_cost=usage_summary.total_cost_usd,
            by_provider=by_provider,
            by_model=by_model,
            by_pipeline=by_pipeline,
            by_stage_type={},  # Would need stage type tracking
        )

    def _analyze_performance(self, runs: List[Dict[str, Any]]) -> PerformanceMetrics:
        """Analyze execution performance."""
        durations: List[float] = []

        for run in runs:
            started = run.get("started_at")
            completed = run.get("completed_at")
            if started and completed:
                try:
                    start_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(completed.replace("Z", "+00:00"))
                    duration_ms = (end_dt - start_dt).total_seconds() * 1000
                    if duration_ms > 0:
                        durations.append(duration_ms)
                except (ValueError, TypeError):
                    continue

        if not durations:
            return PerformanceMetrics(
                avg_duration_ms=0,
                p50_duration_ms=0,
                p95_duration_ms=0,
                p99_duration_ms=0,
                slowest_stages=[],
                fastest_stages=[],
            )

        sorted_durations = sorted(durations)
        n = len(sorted_durations)

        return PerformanceMetrics(
            avg_duration_ms=mean(durations),
            p50_duration_ms=sorted_durations[n // 2],
            p95_duration_ms=sorted_durations[int(n * 0.95)] if n >= 20 else sorted_durations[-1],
            p99_duration_ms=sorted_durations[int(n * 0.99)] if n >= 100 else sorted_durations[-1],
            slowest_stages=[],  # Would need stage-level timing
            fastest_stages=[],
        )

    def _analyze_failures(self, runs: List[Dict[str, Any]]) -> FailureAnalysis:
        """Analyze failure patterns."""
        total = len(runs)
        if total == 0:
            return FailureAnalysis(
                total_failures=0,
                failure_rate=0,
                by_error_type={},
                by_stage={},
                by_pipeline={},
                common_patterns=[],
            )

        failures = [r for r in runs if r.get("status") == "failed"]
        failure_count = len(failures)

        by_pipeline: Dict[str, int] = defaultdict(int)
        by_stage: Dict[str, int] = defaultdict(int)
        by_error_type: Dict[str, int] = defaultdict(int)
        error_messages: List[str] = []

        for run in failures:
            pipeline_id = run.get("pipeline_id", "unknown")
            by_pipeline[pipeline_id] += 1

            # Analyze error from run data
            error = run.get("error", "")
            if error:
                error_messages.append(error)
                # Simple error type classification
                if "timeout" in error.lower():
                    by_error_type["timeout"] += 1
                elif "api" in error.lower() or "rate limit" in error.lower():
                    by_error_type["api_error"] += 1
                elif "validation" in error.lower() or "schema" in error.lower():
                    by_error_type["validation_error"] += 1
                elif "permission" in error.lower() or "auth" in error.lower():
                    by_error_type["auth_error"] += 1
                else:
                    by_error_type["other"] += 1

            # Check stage results for failed stages
            stage_results = run.get("stage_results", {})
            for stage_id, result in stage_results.items():
                if isinstance(result, dict) and result.get("status") == "failed":
                    by_stage[stage_id] += 1

        # Detect common patterns
        patterns: List[str] = []
        if by_error_type:
            top_error = max(by_error_type, key=lambda k: by_error_type[k])
            if by_error_type[top_error] > failure_count * 0.3:
                patterns.append(f"Most failures ({by_error_type[top_error]}) are {top_error}")

        if by_pipeline:
            top_pipeline = max(by_pipeline, key=lambda k: by_pipeline[k])
            if by_pipeline[top_pipeline] > failure_count * 0.5:
                patterns.append(f"Pipeline {top_pipeline} accounts for most failures")

        return FailureAnalysis(
            total_failures=failure_count,
            failure_rate=failure_count / total,
            by_error_type=dict(by_error_type),
            by_stage=dict(by_stage),
            by_pipeline=dict(by_pipeline),
            common_patterns=patterns,
        )

    def _analyze_usage_patterns(
        self,
        runs: List[Dict[str, Any]],
        usage_summary: Any,
    ) -> UsagePattern:
        """Analyze usage patterns."""
        hourly_counts: Dict[int, int] = defaultdict(int)
        daily_counts: Dict[str, int] = defaultdict(int)
        pipeline_counts: Dict[str, int] = defaultdict(int)

        for run in runs:
            started = run.get("started_at")
            if started:
                try:
                    dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    hourly_counts[dt.hour] += 1
                    daily_counts[dt.strftime("%A")] += 1
                except (ValueError, TypeError):
                    continue

            pipeline_id = run.get("pipeline_id")
            if pipeline_id:
                pipeline_counts[pipeline_id] += 1

        # Find peak hours (top 3)
        peak_hours = sorted(hourly_counts, key=lambda h: hourly_counts[h], reverse=True)[:3]

        # Find peak days
        peak_days = sorted(daily_counts, key=lambda d: daily_counts[d], reverse=True)[:3]

        # Busiest pipeline
        busiest_pipeline = max(pipeline_counts, key=lambda p: pipeline_counts[p]) if pipeline_counts else None

        # Most used model
        most_used_model = None
        if usage_summary.by_model:
            most_used_model = max(
                usage_summary.by_model,
                key=lambda m: usage_summary.by_model[m].get("request_count", 0),
            )

        # Daily averages
        days_covered = len(set(daily_counts.keys())) or 1
        avg_daily_runs = len(runs) / days_covered
        avg_daily_cost = usage_summary.total_cost_usd / days_covered

        return UsagePattern(
            peak_hours=peak_hours,
            peak_days=peak_days,
            busiest_pipeline_id=busiest_pipeline,
            most_used_model=most_used_model,
            avg_daily_runs=avg_daily_runs,
            avg_daily_cost=avg_daily_cost,
        )

    def _analyze_model_efficiency(self, usage_summary: Any) -> List[ModelEfficiency]:
        """Analyze efficiency of different models."""
        efficiencies: List[ModelEfficiency] = []

        for model_key, data in usage_summary.by_model.items():
            parts = model_key.split(":", 1)
            provider = parts[0] if len(parts) > 1 else "unknown"
            model = parts[1] if len(parts) > 1 else model_key

            request_count = data.get("request_count", 0)
            if request_count == 0:
                continue

            total_tokens = data.get("total_tokens", 0)
            total_cost = data.get("cost_usd", 0)

            efficiencies.append(ModelEfficiency(
                provider=provider,
                model=model,
                avg_latency_ms=0,  # Would need timing data per request
                avg_tokens_per_request=total_tokens / request_count if request_count else 0,
                cost_per_1k_tokens=(total_cost / total_tokens * 1000) if total_tokens else 0,
                success_rate=1.0,  # Would need success tracking per model
                usage_count=request_count,
            ))

        return sorted(efficiencies, key=lambda e: e.usage_count, reverse=True)

    def _forecast_costs(self, usage_summary: Any, days: int) -> CostForecast:
        """Forecast future costs based on current trends."""
        daily_usage = self._usage_storage.get_daily_usage(
            org_id="default",  # Would need org context
            days=days,
        )

        if not daily_usage or len(daily_usage) < 3:
            return CostForecast(
                current_daily_avg=usage_summary.total_cost_usd / max(days, 1),
                projected_daily=0,
                projected_weekly=0,
                projected_monthly=0,
                trend=TrendDirection.STABLE,
                confidence=0.3,
            )

        daily_costs = [d.get("cost_usd", 0) for d in daily_usage]
        avg_daily = mean(daily_costs) if daily_costs else 0

        # Simple trend detection using first and second half
        mid = len(daily_costs) // 2
        first_half_avg = mean(daily_costs[:mid]) if daily_costs[:mid] else 0
        second_half_avg = mean(daily_costs[mid:]) if daily_costs[mid:] else 0

        if second_half_avg > first_half_avg * 1.1:
            trend = TrendDirection.UP
            projected_daily = avg_daily * 1.1
        elif second_half_avg < first_half_avg * 0.9:
            trend = TrendDirection.DOWN
            projected_daily = avg_daily * 0.9
        else:
            trend = TrendDirection.STABLE
            projected_daily = avg_daily

        # Confidence based on data consistency
        if len(daily_costs) >= 2:
            variance = stdev(daily_costs) / avg_daily if avg_daily > 0 else 1
            confidence = max(0.3, min(0.95, 1 - variance))
        else:
            confidence = 0.3

        return CostForecast(
            current_daily_avg=avg_daily,
            projected_daily=projected_daily,
            projected_weekly=projected_daily * 7,
            projected_monthly=projected_daily * 30,
            trend=trend,
            confidence=confidence,
        )

    # =========================================================================
    # Insight Detection
    # =========================================================================

    def _calculate_trend(
        self,
        metric_name: str,
        current: float,
        previous: float,
        lower_is_better: bool = False,
    ) -> MetricTrend:
        """Calculate trend for a metric."""
        if previous == 0:
            change_percent = 100 if current > 0 else 0
        else:
            change_percent = ((current - previous) / previous) * 100

        if abs(change_percent) < 1:
            direction = TrendDirection.STABLE
        elif change_percent > 0:
            direction = TrendDirection.UP
        else:
            direction = TrendDirection.DOWN

        is_significant = abs(change_percent) >= self.SIGNIFICANCE_THRESHOLD * 100

        return MetricTrend(
            metric_name=metric_name,
            current_value=current,
            previous_value=previous,
            change_percent=change_percent,
            direction=direction,
            is_significant=is_significant,
        )

    def _detect_cost_anomalies(
        self,
        current: Any,
        previous: Any,
        org_id: str,
    ) -> List[Insight]:
        """Detect cost-related anomalies."""
        insights: List[Insight] = []
        now = datetime.utcnow().isoformat()

        # Cost spike detection
        prev_cost = previous.total_cost_usd / 2 if previous.total_cost_usd else 0
        if prev_cost > 0 and current.total_cost_usd > prev_cost * (1 + self.COST_SPIKE_THRESHOLD):
            increase_pct = ((current.total_cost_usd - prev_cost) / prev_cost) * 100
            insights.append(Insight(
                id=str(uuid.uuid4()),
                type=InsightType.COST_SPIKE,
                severity=InsightSeverity.WARNING if increase_pct < 100 else InsightSeverity.CRITICAL,
                category=InsightCategory.COST,
                title=f"Cost increased by {increase_pct:.0f}%",
                description=f"Spending increased from ${prev_cost:.2f} to ${current.total_cost_usd:.2f} compared to the previous period.",
                data={
                    "previous_cost": prev_cost,
                    "current_cost": current.total_cost_usd,
                    "increase_percent": increase_pct,
                },
                metrics={"cost_change": current.total_cost_usd - prev_cost},
                recommendations=[
                    "Review usage patterns to identify unexpected increases",
                    "Consider using smaller models for simple tasks",
                    "Check for runaway or stuck pipelines",
                ],
                detected_at=now,
            ))

        # Model concentration detection
        if current.by_model:
            total_cost = current.total_cost_usd
            for model_key, data in current.by_model.items():
                model_cost = data.get("cost_usd", 0)
                if total_cost > 0 and model_cost / total_cost > 0.8:
                    insights.append(Insight(
                        id=str(uuid.uuid4()),
                        type=InsightType.COST_OPTIMIZATION,
                        severity=InsightSeverity.INFO,
                        category=InsightCategory.COST,
                        title=f"High concentration on {model_key}",
                        description=f"80%+ of costs come from {model_key}. Consider if a smaller model could handle some requests.",
                        data={"model": model_key, "cost_percent": (model_cost / total_cost) * 100},
                        metrics={"model_cost": model_cost},
                        recommendations=[
                            "Evaluate if simpler tasks could use a smaller/cheaper model",
                            "Consider model routing based on task complexity",
                        ],
                        detected_at=now,
                    ))

        return insights

    def _detect_performance_issues(
        self,
        current: PerformanceMetrics,
        previous: Optional[PerformanceMetrics],
        runs: List[Dict[str, Any]],
    ) -> List[Insight]:
        """Detect performance-related issues."""
        insights: List[Insight] = []
        now = datetime.utcnow().isoformat()

        # Performance degradation
        if previous and previous.avg_duration_ms > 0:
            if current.avg_duration_ms > previous.avg_duration_ms * (1 + self.PERFORMANCE_DEGRADATION_THRESHOLD):
                increase_pct = ((current.avg_duration_ms - previous.avg_duration_ms) / previous.avg_duration_ms) * 100
                insights.append(Insight(
                    id=str(uuid.uuid4()),
                    type=InsightType.PERFORMANCE_DEGRADATION,
                    severity=InsightSeverity.WARNING,
                    category=InsightCategory.PERFORMANCE,
                    title=f"Execution time increased by {increase_pct:.0f}%",
                    description=f"Average execution time increased from {previous.avg_duration_ms:.0f}ms to {current.avg_duration_ms:.0f}ms.",
                    data={
                        "previous_avg_ms": previous.avg_duration_ms,
                        "current_avg_ms": current.avg_duration_ms,
                    },
                    metrics={"duration_increase_ms": current.avg_duration_ms - previous.avg_duration_ms},
                    recommendations=[
                        "Check for slow API responses or rate limiting",
                        "Review any recent pipeline changes",
                        "Consider caching repeated operations",
                    ],
                    detected_at=now,
                ))

        # High P95/P50 ratio (indicates inconsistent performance)
        if current.p50_duration_ms > 0:
            ratio = current.p95_duration_ms / current.p50_duration_ms
            if ratio > 3:
                insights.append(Insight(
                    id=str(uuid.uuid4()),
                    type=InsightType.ANOMALY,
                    severity=InsightSeverity.INFO,
                    category=InsightCategory.PERFORMANCE,
                    title="High performance variability detected",
                    description=f"P95 latency is {ratio:.1f}x the median, indicating inconsistent execution times.",
                    data={
                        "p50_ms": current.p50_duration_ms,
                        "p95_ms": current.p95_duration_ms,
                        "ratio": ratio,
                    },
                    metrics={"p95_p50_ratio": ratio},
                    recommendations=[
                        "Investigate outlier runs for issues",
                        "Check for intermittent API slowdowns",
                        "Consider adding timeouts for long-running stages",
                    ],
                    detected_at=now,
                ))

        return insights

    def _detect_failure_patterns(
        self,
        failure_analysis: FailureAnalysis,
        runs: List[Dict[str, Any]],
    ) -> List[Insight]:
        """Detect failure patterns."""
        insights: List[Insight] = []
        now = datetime.utcnow().isoformat()

        # High failure rate
        if failure_analysis.failure_rate > self.FAILURE_RATE_CRITICAL:
            insights.append(Insight(
                id=str(uuid.uuid4()),
                type=InsightType.FAILURE_PATTERN,
                severity=InsightSeverity.CRITICAL,
                category=InsightCategory.RELIABILITY,
                title=f"Critical failure rate: {failure_analysis.failure_rate*100:.0f}%",
                description=f"{failure_analysis.total_failures} of {len(runs)} runs failed. Immediate attention required.",
                data={
                    "failure_rate": failure_analysis.failure_rate,
                    "total_failures": failure_analysis.total_failures,
                    "by_error_type": failure_analysis.by_error_type,
                },
                metrics={"failure_count": failure_analysis.total_failures},
                recommendations=[
                    "Check recent changes to pipelines or configurations",
                    "Verify API credentials and rate limits",
                    "Review error logs for root cause",
                ],
                detected_at=now,
            ))
        elif failure_analysis.failure_rate > self.FAILURE_RATE_WARNING:
            insights.append(Insight(
                id=str(uuid.uuid4()),
                type=InsightType.FAILURE_PATTERN,
                severity=InsightSeverity.WARNING,
                category=InsightCategory.RELIABILITY,
                title=f"Elevated failure rate: {failure_analysis.failure_rate*100:.0f}%",
                description=f"{failure_analysis.total_failures} runs failed in this period.",
                data={
                    "failure_rate": failure_analysis.failure_rate,
                    "total_failures": failure_analysis.total_failures,
                },
                metrics={"failure_count": failure_analysis.total_failures},
                recommendations=[
                    "Review common error patterns",
                    "Consider adding retry logic for transient failures",
                ],
                detected_at=now,
            ))

        # Concentrated failures
        if failure_analysis.by_pipeline:
            total_failures = failure_analysis.total_failures
            for pipeline_id, count in failure_analysis.by_pipeline.items():
                if count > total_failures * 0.7:
                    insights.append(Insight(
                        id=str(uuid.uuid4()),
                        type=InsightType.FAILURE_PATTERN,
                        severity=InsightSeverity.WARNING,
                        category=InsightCategory.RELIABILITY,
                        title=f"Failures concentrated in one pipeline",
                        description=f"Pipeline {pipeline_id} accounts for {count} of {total_failures} failures.",
                        pipeline_id=pipeline_id,
                        data={"pipeline_id": pipeline_id, "failure_count": count},
                        metrics={"pipeline_failures": count},
                        recommendations=[
                            "Review this pipeline's configuration",
                            "Check stage inputs and outputs",
                            "Verify external service dependencies",
                        ],
                        detected_at=now,
                    ))

        return insights

    def _detect_usage_anomalies(
        self,
        usage_patterns: UsagePattern,
        runs: List[Dict[str, Any]],
    ) -> List[Insight]:
        """Detect usage pattern anomalies."""
        insights: List[Insight] = []
        now = datetime.utcnow().isoformat()

        # Low usage warning
        if usage_patterns.avg_daily_runs < 1 and len(runs) > 0:
            insights.append(Insight(
                id=str(uuid.uuid4()),
                type=InsightType.USAGE_TREND,
                severity=InsightSeverity.INFO,
                category=InsightCategory.USAGE,
                title="Low pipeline usage detected",
                description=f"Average of {usage_patterns.avg_daily_runs:.1f} runs per day. Pipelines may be underutilized.",
                data={"avg_daily_runs": usage_patterns.avg_daily_runs},
                metrics={"daily_runs": usage_patterns.avg_daily_runs},
                recommendations=[
                    "Review if pipelines meet current needs",
                    "Consider automating pipeline triggers",
                ],
                detected_at=now,
            ))

        return insights

    def _generate_model_recommendations(
        self,
        model_efficiency: List[ModelEfficiency],
    ) -> List[Insight]:
        """Generate model usage recommendations."""
        insights: List[Insight] = []
        now = datetime.utcnow().isoformat()

        # Find expensive models that could be replaced
        for eff in model_efficiency:
            if eff.usage_count < 10:
                continue

            # Check if there's a cheaper alternative
            provider_pricing = PROVIDER_PRICING.get(eff.provider.lower(), {})
            model_pricing = provider_pricing.get(eff.model, {})
            model_input_price = model_pricing.get("input", 0)

            # Look for cheaper models from same provider
            cheaper_models: List[Tuple[str, float]] = []
            for model, pricing in provider_pricing.items():
                if model != eff.model and pricing.get("input", 0) < model_input_price * 0.5:
                    cheaper_models.append((model, pricing.get("input", 0)))

            if cheaper_models and model_input_price > 1:  # Only suggest if current model is >$1/M input
                cheapest = min(cheaper_models, key=lambda x: x[1])
                insights.append(Insight(
                    id=str(uuid.uuid4()),
                    type=InsightType.MODEL_RECOMMENDATION,
                    severity=InsightSeverity.INFO,
                    category=InsightCategory.OPTIMIZATION,
                    title=f"Consider {cheapest[0]} for simpler tasks",
                    description=f"{cheapest[0]} is {(model_input_price/cheapest[1]):.0f}x cheaper than {eff.model}. Evaluate if some tasks could use the smaller model.",
                    data={
                        "current_model": eff.model,
                        "suggested_model": cheapest[0],
                        "price_ratio": model_input_price / cheapest[1],
                    },
                    metrics={"potential_savings_ratio": model_input_price / cheapest[1]},
                    recommendations=[
                        f"Route simple tasks to {cheapest[0]}",
                        "Use model selection based on task complexity",
                    ],
                    detected_at=now,
                ))

        return insights

    def _identify_optimization_opportunities(
        self,
        usage_summary: Any,
        model_efficiency: List[ModelEfficiency],
        performance_metrics: PerformanceMetrics,
        failure_analysis: FailureAnalysis,
    ) -> List[OptimizationOpportunity]:
        """Identify cost and performance optimization opportunities."""
        opportunities: List[OptimizationOpportunity] = []

        # Model downgrade opportunity
        if usage_summary.by_model:
            for model_key, data in usage_summary.by_model.items():
                parts = model_key.split(":", 1)
                provider = parts[0].lower() if len(parts) > 1 else "unknown"
                model = parts[1] if len(parts) > 1 else model_key

                provider_pricing = PROVIDER_PRICING.get(provider, {})
                model_pricing = provider_pricing.get(model, {})
                model_input_price = model_pricing.get("input", 0)

                # Check for cheaper alternatives
                for alt_model, alt_pricing in provider_pricing.items():
                    if alt_model != model and alt_pricing.get("input", 0) < model_input_price * 0.3:
                        current_cost = data.get("cost_usd", 0)
                        potential_savings = current_cost * 0.7  # Estimate 70% savings

                        if potential_savings > 1:  # Only show if >$1 savings
                            opportunities.append(OptimizationOpportunity(
                                type="model_downgrade",
                                description=f"Switch from {model} to {alt_model} for simple tasks",
                                current_cost=current_cost,
                                potential_savings=potential_savings,
                                savings_percent=70,
                                recommendation=f"Route simpler tasks to {alt_model} which is significantly cheaper",
                                difficulty="medium",
                            ))
                        break  # One suggestion per model

        # Failure reduction opportunity
        if failure_analysis.failure_rate > 0.05:
            # Estimate cost of failures (reruns, wasted tokens)
            estimated_waste = usage_summary.total_cost_usd * failure_analysis.failure_rate * 0.5
            if estimated_waste > 0.5:
                opportunities.append(OptimizationOpportunity(
                    type="reliability",
                    description="Reduce failures to cut wasted resources",
                    current_cost=estimated_waste,
                    potential_savings=estimated_waste * 0.8,
                    savings_percent=int(failure_analysis.failure_rate * 80),
                    recommendation="Address common failure causes to reduce wasted API calls",
                    difficulty="medium",
                ))

        return opportunities


# Global instance
_insights_service: Optional[InsightsService] = None


def get_insights_service() -> InsightsService:
    """Get the global insights service instance."""
    global _insights_service
    if _insights_service is None:
        _insights_service = InsightsService()
    return _insights_service
