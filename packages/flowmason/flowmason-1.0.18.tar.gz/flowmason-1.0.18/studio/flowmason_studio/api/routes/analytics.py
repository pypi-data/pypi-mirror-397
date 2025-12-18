"""
Analytics API Routes.

Endpoints for dashboard metrics and statistics:
- Pipeline run statistics
- Execution metrics and trends
- Success/failure rates
- Usage analytics
- AI-powered insights and recommendations
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ...models.insights import (
    InsightCategory,
    InsightsReport,
    InsightSeverity,
    InsightsSummary,
    Insight,
)
from ...services.insights_service import get_insights_service
from ...services.storage import get_pipeline_storage, get_run_storage

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ==================== Response Models ====================

class ExecutionMetrics(BaseModel):
    """Overall execution metrics."""
    total_runs: int
    successful_runs: int
    failed_runs: int
    cancelled_runs: int
    running_runs: int
    success_rate: float
    avg_duration_seconds: Optional[float] = None


class PipelineMetrics(BaseModel):
    """Metrics for a single pipeline."""
    pipeline_id: str
    pipeline_name: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    avg_duration_seconds: Optional[float] = None
    last_run_at: Optional[str] = None


class DailyStats(BaseModel):
    """Statistics for a single day."""
    date: str
    total_runs: int
    successful_runs: int
    failed_runs: int


class HourlyStats(BaseModel):
    """Statistics for a single hour."""
    hour: int
    total_runs: int
    successful_runs: int
    failed_runs: int


class RecentActivity(BaseModel):
    """Recent activity item."""
    run_id: str
    pipeline_id: str
    pipeline_name: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None


class UsageSummary(BaseModel):
    """Overall usage summary."""
    period: str
    total_pipelines: int
    active_pipelines: int
    total_runs: int
    total_stages_executed: int
    avg_stages_per_run: float


class ComponentUsage(BaseModel):
    """Component usage statistics."""
    component_type: str
    usage_count: int
    success_rate: float


class DashboardOverview(BaseModel):
    """Complete dashboard overview."""
    metrics: ExecutionMetrics
    top_pipelines: List[PipelineMetrics]
    daily_stats: List[DailyStats]
    recent_activity: List[RecentActivity]


# ==================== Helper Functions ====================

def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse datetime string."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _calculate_duration(start: Optional[str], end: Optional[str]) -> Optional[float]:
    """Calculate duration in seconds between two timestamps."""
    start_dt = _parse_datetime(start)
    end_dt = _parse_datetime(end)
    if start_dt and end_dt:
        return (end_dt - start_dt).total_seconds()
    return None


# ==================== Endpoints ====================

@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to include"),
    limit: int = Query(default=5, ge=1, le=20, description="Number of top pipelines"),
):
    """
    Get complete dashboard overview.

    Returns metrics, top pipelines, daily stats, and recent activity
    for the operations dashboard.
    """
    run_storage = get_run_storage()
    pipeline_storage = get_pipeline_storage()

    # Get all runs (use mode="json" to serialize datetimes to strings)
    all_runs = [r.model_dump(mode="json") for r in run_storage.list(limit=10000)[0]]

    # Calculate date range
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Filter recent runs
    recent_runs = []
    for run in all_runs:
        started_at = _parse_datetime(run.get("started_at"))
        if started_at and started_at >= cutoff:
            recent_runs.append(run)

    # Calculate overall metrics
    total = len(recent_runs)
    successful = sum(1 for r in recent_runs if r.get("status") == "completed")
    failed = sum(1 for r in recent_runs if r.get("status") == "failed")
    cancelled = sum(1 for r in recent_runs if r.get("status") == "cancelled")
    running = sum(1 for r in recent_runs if r.get("status") in ["running", "pending"])

    # Calculate average duration
    durations = []
    for run in recent_runs:
        duration = _calculate_duration(run.get("started_at"), run.get("completed_at"))
        if duration is not None:
            durations.append(duration)

    metrics = ExecutionMetrics(
        total_runs=total,
        successful_runs=successful,
        failed_runs=failed,
        cancelled_runs=cancelled,
        running_runs=running,
        success_rate=successful / total if total > 0 else 0.0,
        avg_duration_seconds=sum(durations) / len(durations) if durations else None,
    )

    # Calculate per-pipeline metrics
    pipeline_stats: Dict[str, Dict] = defaultdict(lambda: {
        "total": 0, "successful": 0, "failed": 0, "durations": [], "last_run": None
    })

    for run in recent_runs:
        pid = run.get("pipeline_id", "unknown")
        stats = pipeline_stats[pid]
        stats["total"] += 1

        if run.get("status") == "completed":
            stats["successful"] += 1
        elif run.get("status") == "failed":
            stats["failed"] += 1

        duration = _calculate_duration(run.get("started_at"), run.get("completed_at"))
        if duration is not None:
            stats["durations"].append(duration)

        started = run.get("started_at")
        if started and (not stats["last_run"] or started > stats["last_run"]):
            stats["last_run"] = started

    # Get pipeline names
    pipeline_names: Dict[str, str] = {}
    for pid in pipeline_stats.keys():
        try:
            pipeline = pipeline_storage.get(pid)
            if pipeline:
                pipeline_names[pid] = pipeline.name or pid
        except Exception:
            pipeline_names[pid] = pid

    # Build top pipelines list
    top_pipelines = []
    sorted_pipelines = sorted(
        pipeline_stats.items(),
        key=lambda x: x[1]["total"],
        reverse=True
    )[:limit]

    for pid, stats in sorted_pipelines:
        top_pipelines.append(PipelineMetrics(
            pipeline_id=pid,
            pipeline_name=pipeline_names.get(pid, pid),
            total_runs=stats["total"],
            successful_runs=stats["successful"],
            failed_runs=stats["failed"],
            success_rate=stats["successful"] / stats["total"] if stats["total"] > 0 else 0.0,
            avg_duration_seconds=(
                sum(stats["durations"]) / len(stats["durations"])
                if stats["durations"] else None
            ),
            last_run_at=stats["last_run"],
        ))

    # Calculate daily stats
    daily_counts: Dict[str, Dict] = defaultdict(lambda: {"total": 0, "successful": 0, "failed": 0})

    for run in recent_runs:
        started = _parse_datetime(run.get("started_at"))
        if started:
            date_key = started.strftime("%Y-%m-%d")
            daily_counts[date_key]["total"] += 1
            if run.get("status") == "completed":
                daily_counts[date_key]["successful"] += 1
            elif run.get("status") == "failed":
                daily_counts[date_key]["failed"] += 1

    daily_stats = [
        DailyStats(
            date=date,
            total_runs=counts["total"],
            successful_runs=counts["successful"],
            failed_runs=counts["failed"],
        )
        for date, counts in sorted(daily_counts.items())
    ]

    # Recent activity (last 10 runs)
    sorted_runs = sorted(
        recent_runs,
        key=lambda x: x.get("started_at", ""),
        reverse=True
    )[:10]

    recent_activity = [
        RecentActivity(
            run_id=run.get("id", ""),
            pipeline_id=run.get("pipeline_id", ""),
            pipeline_name=pipeline_names.get(run.get("pipeline_id", ""), "Unknown"),
            status=run.get("status", "unknown"),
            started_at=run.get("started_at", ""),
            completed_at=run.get("completed_at"),
            duration_seconds=_calculate_duration(
                run.get("started_at"),
                run.get("completed_at")
            ),
        )
        for run in sorted_runs
    ]

    return DashboardOverview(
        metrics=metrics,
        top_pipelines=top_pipelines,
        daily_stats=daily_stats,
        recent_activity=recent_activity,
    )


@router.get("/metrics", response_model=ExecutionMetrics)
async def get_execution_metrics(
    days: int = Query(default=7, ge=1, le=90, description="Number of days"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
):
    """
    Get execution metrics.

    Returns success rates, counts, and average durations.
    """
    run_storage = get_run_storage()
    all_runs = [r.model_dump(mode="json") for r in run_storage.list(limit=10000)[0]]

    cutoff = datetime.utcnow() - timedelta(days=days)

    # Filter runs
    filtered = []
    for run in all_runs:
        started = _parse_datetime(run.get("started_at"))
        if not started or started < cutoff:
            continue
        if pipeline_id and run.get("pipeline_id") != pipeline_id:
            continue
        filtered.append(run)

    total = len(filtered)
    successful = sum(1 for r in filtered if r.get("status") == "completed")
    failed = sum(1 for r in filtered if r.get("status") == "failed")
    cancelled = sum(1 for r in filtered if r.get("status") == "cancelled")
    running = sum(1 for r in filtered if r.get("status") in ["running", "pending"])

    durations = []
    for run in filtered:
        duration = _calculate_duration(run.get("started_at"), run.get("completed_at"))
        if duration is not None:
            durations.append(duration)

    return ExecutionMetrics(
        total_runs=total,
        successful_runs=successful,
        failed_runs=failed,
        cancelled_runs=cancelled,
        running_runs=running,
        success_rate=successful / total if total > 0 else 0.0,
        avg_duration_seconds=sum(durations) / len(durations) if durations else None,
    )


@router.get("/pipelines", response_model=List[PipelineMetrics])
async def get_pipeline_metrics(
    days: int = Query(default=7, ge=1, le=90, description="Number of days"),
    limit: int = Query(default=20, ge=1, le=100, description="Max pipelines"),
    sort_by: str = Query(default="runs", description="Sort by: runs, success_rate, name"),
):
    """
    Get per-pipeline metrics.

    Returns execution statistics for each pipeline.
    """
    run_storage = get_run_storage()
    pipeline_storage = get_pipeline_storage()

    all_runs = [r.model_dump(mode="json") for r in run_storage.list(limit=10000)[0]]
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Aggregate by pipeline
    pipeline_stats: Dict[str, Dict] = defaultdict(lambda: {
        "total": 0, "successful": 0, "failed": 0, "durations": [], "last_run": None
    })

    for run in all_runs:
        started = _parse_datetime(run.get("started_at"))
        if not started or started < cutoff:
            continue

        pid = run.get("pipeline_id", "unknown")
        stats = pipeline_stats[pid]
        stats["total"] += 1

        if run.get("status") == "completed":
            stats["successful"] += 1
        elif run.get("status") == "failed":
            stats["failed"] += 1

        duration = _calculate_duration(run.get("started_at"), run.get("completed_at"))
        if duration is not None:
            stats["durations"].append(duration)

        started_str = run.get("started_at")
        if started_str and (not stats["last_run"] or started_str > stats["last_run"]):
            stats["last_run"] = started_str

    # Get pipeline names
    pipeline_names: Dict[str, str] = {}
    for pid in pipeline_stats.keys():
        try:
            pipeline = pipeline_storage.get(pid)
            if pipeline:
                pipeline_names[pid] = pipeline.name or pid
        except Exception:
            pipeline_names[pid] = pid

    # Build results
    results = []
    for pid, stats in pipeline_stats.items():
        results.append(PipelineMetrics(
            pipeline_id=pid,
            pipeline_name=pipeline_names.get(pid, pid),
            total_runs=stats["total"],
            successful_runs=stats["successful"],
            failed_runs=stats["failed"],
            success_rate=stats["successful"] / stats["total"] if stats["total"] > 0 else 0.0,
            avg_duration_seconds=(
                sum(stats["durations"]) / len(stats["durations"])
                if stats["durations"] else None
            ),
            last_run_at=stats["last_run"],
        ))

    # Sort
    if sort_by == "success_rate":
        results.sort(key=lambda x: x.success_rate, reverse=True)
    elif sort_by == "name":
        results.sort(key=lambda x: x.pipeline_name.lower())
    else:  # runs
        results.sort(key=lambda x: x.total_runs, reverse=True)

    return results[:limit]


@router.get("/daily", response_model=List[DailyStats])
async def get_daily_stats(
    days: int = Query(default=30, ge=1, le=90, description="Number of days"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
):
    """
    Get daily execution statistics.

    Returns run counts by day for charting.
    """
    run_storage = get_run_storage()
    all_runs = [r.model_dump(mode="json") for r in run_storage.list(limit=10000)[0]]

    cutoff = datetime.utcnow() - timedelta(days=days)

    daily_counts: Dict[str, Dict] = defaultdict(lambda: {"total": 0, "successful": 0, "failed": 0})

    for run in all_runs:
        started = _parse_datetime(run.get("started_at"))
        if not started or started < cutoff:
            continue
        if pipeline_id and run.get("pipeline_id") != pipeline_id:
            continue

        date_key = started.strftime("%Y-%m-%d")
        daily_counts[date_key]["total"] += 1
        if run.get("status") == "completed":
            daily_counts[date_key]["successful"] += 1
        elif run.get("status") == "failed":
            daily_counts[date_key]["failed"] += 1

    # Ensure all days are represented
    result = []
    current = cutoff.date()
    today = datetime.utcnow().date()

    while current <= today:
        date_key = current.strftime("%Y-%m-%d")
        counts = daily_counts.get(date_key, {"total": 0, "successful": 0, "failed": 0})
        result.append(DailyStats(
            date=date_key,
            total_runs=counts["total"],
            successful_runs=counts["successful"],
            failed_runs=counts["failed"],
        ))
        current += timedelta(days=1)

    return result


@router.get("/hourly", response_model=List[HourlyStats])
async def get_hourly_stats(
    days: int = Query(default=7, ge=1, le=30, description="Number of days"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
):
    """
    Get hourly execution distribution.

    Returns aggregated run counts by hour of day.
    """
    run_storage = get_run_storage()
    all_runs = [r.model_dump(mode="json") for r in run_storage.list(limit=10000)[0]]

    cutoff = datetime.utcnow() - timedelta(days=days)

    hourly_counts: Dict[int, Dict] = defaultdict(lambda: {"total": 0, "successful": 0, "failed": 0})

    for run in all_runs:
        started = _parse_datetime(run.get("started_at"))
        if not started or started < cutoff:
            continue
        if pipeline_id and run.get("pipeline_id") != pipeline_id:
            continue

        hour = started.hour
        hourly_counts[hour]["total"] += 1
        if run.get("status") == "completed":
            hourly_counts[hour]["successful"] += 1
        elif run.get("status") == "failed":
            hourly_counts[hour]["failed"] += 1

    return [
        HourlyStats(
            hour=hour,
            total_runs=hourly_counts[hour]["total"],
            successful_runs=hourly_counts[hour]["successful"],
            failed_runs=hourly_counts[hour]["failed"],
        )
        for hour in range(24)
    ]


@router.get("/recent", response_model=List[RecentActivity])
async def get_recent_activity(
    limit: int = Query(default=20, ge=1, le=100, description="Number of items"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """
    Get recent execution activity.

    Returns most recent runs with details.
    """
    run_storage = get_run_storage()
    pipeline_storage = get_pipeline_storage()

    all_runs = [r.model_dump(mode="json") for r in run_storage.list(limit=limit * 2)[0]]

    # Filter by status if specified
    if status:
        all_runs = [r for r in all_runs if r.get("status") == status]

    # Sort by started_at descending
    sorted_runs = sorted(
        all_runs,
        key=lambda x: x.get("started_at", ""),
        reverse=True
    )[:limit]

    # Get pipeline names
    pipeline_ids: set[str] = {str(r.get("pipeline_id")) for r in sorted_runs if r.get("pipeline_id")}
    pipeline_names: Dict[str, str] = {}
    for pid in pipeline_ids:
        try:
            pipeline = pipeline_storage.get(pid)
            if pipeline:
                pipeline_names[pid] = pipeline.name or pid
        except Exception:
            pipeline_names[pid] = pid

    return [
        RecentActivity(
            run_id=run.get("id", ""),
            pipeline_id=run.get("pipeline_id", ""),
            pipeline_name=pipeline_names.get(run.get("pipeline_id", ""), "Unknown"),
            status=run.get("status", "unknown"),
            started_at=run.get("started_at", ""),
            completed_at=run.get("completed_at"),
            duration_seconds=_calculate_duration(
                run.get("started_at"),
                run.get("completed_at")
            ),
        )
        for run in sorted_runs
    ]


@router.get("/usage", response_model=UsageSummary)
async def get_usage_summary(
    days: int = Query(default=30, ge=1, le=90, description="Number of days"),
):
    """
    Get usage summary.

    Returns overall usage metrics for the period.
    """
    run_storage = get_run_storage()
    pipeline_storage = get_pipeline_storage()

    all_runs = [r.model_dump(mode="json") for r in run_storage.list(limit=10000)[0]]
    all_pipelines = pipeline_storage.list()[0]

    cutoff = datetime.utcnow() - timedelta(days=days)

    # Filter recent runs
    recent_runs = []
    active_pipelines = set()
    total_stages = 0

    for run in all_runs:
        started = _parse_datetime(run.get("started_at"))
        if started and started >= cutoff:
            recent_runs.append(run)
            if run.get("pipeline_id"):
                active_pipelines.add(run.get("pipeline_id"))

            # Count stages
            stages = run.get("stage_results", {})
            total_stages += len(stages)

    return UsageSummary(
        period=f"last_{days}_days",
        total_pipelines=len(all_pipelines),
        active_pipelines=len(active_pipelines),
        total_runs=len(recent_runs),
        total_stages_executed=total_stages,
        avg_stages_per_run=total_stages / len(recent_runs) if recent_runs else 0.0,
    )


# ==================== AI Insights Endpoints ====================


@router.get("/insights/report", response_model=InsightsReport)
async def get_insights_report(
    org_id: str = Query(default="default", description="Organization ID"),
    days: int = Query(default=30, ge=1, le=90, description="Number of days to analyze"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    include_forecasts: bool = Query(True, description="Include cost forecasts"),
):
    """
    Get a comprehensive AI-powered insights report.

    Analyzes execution data to provide:
    - Cost trends and anomalies
    - Performance metrics and degradation detection
    - Failure patterns and root cause hints
    - Usage patterns and optimization opportunities
    - Model efficiency comparisons
    - Cost forecasting
    """
    service = get_insights_service()

    return service.generate_report(
        org_id=org_id,
        days=days,
        pipeline_id=pipeline_id,
        include_recommendations=include_recommendations,
        include_forecasts=include_forecasts,
    )


@router.get("/insights/summary", response_model=InsightsSummary)
async def get_insights_summary(
    org_id: str = Query(default="default", description="Organization ID"),
    days: int = Query(default=7, ge=1, le=30, description="Number of days"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
):
    """
    Get a quick summary of key insights.

    Returns the most important insights across cost, performance,
    and reliability categories with estimated savings opportunities.
    """
    service = get_insights_service()

    return service.get_summary(
        org_id=org_id,
        days=days,
        pipeline_id=pipeline_id,
    )


@router.get("/insights", response_model=List[Insight])
async def get_insights(
    org_id: str = Query(default="default", description="Organization ID"),
    days: int = Query(default=7, ge=1, le=90, description="Number of days"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
    category: Optional[InsightCategory] = Query(None, description="Filter by category"),
    severity: Optional[InsightSeverity] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=200, description="Maximum insights to return"),
):
    """
    Get a filtered list of insights.

    Returns insights sorted by severity (critical first).
    Use category and severity filters to focus on specific types.
    """
    service = get_insights_service()

    return service.get_insights(
        org_id=org_id,
        days=days,
        pipeline_id=pipeline_id,
        category=category,
        severity=severity,
        limit=limit,
    )
