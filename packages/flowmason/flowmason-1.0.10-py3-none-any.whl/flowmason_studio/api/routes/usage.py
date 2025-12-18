"""
FlowMason LLM Usage API Routes.

Endpoints for querying LLM token usage and costs.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from ...auth import AuthContext, require_auth
from ...services.usage_storage import (
    UsageStorage,
    get_usage_storage,
)

router = APIRouter(prefix="/usage", tags=["usage"])


# =============================================================================
# Response Models
# =============================================================================


class UsageRecordResponse(BaseModel):
    """LLM usage record."""
    id: str
    run_id: str
    pipeline_id: str
    stage_id: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    duration_ms: int
    recorded_at: str


class UsageSummaryResponse(BaseModel):
    """Aggregated usage summary."""
    period_start: str
    period_end: str
    total_runs: int
    total_stages: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost_usd: float
    by_provider: Dict[str, Dict[str, Any]]
    by_model: Dict[str, Dict[str, Any]]
    by_pipeline: Optional[Dict[str, Dict[str, Any]]] = None


class DailyUsageResponse(BaseModel):
    """Daily usage breakdown."""
    date: str
    run_count: int
    stage_count: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float


class RunUsageResponse(BaseModel):
    """Usage summary for a specific run."""
    run_id: str
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost_usd: float
    records: List[UsageRecordResponse]


class PricingResponse(BaseModel):
    """Provider pricing information."""
    pricing: Dict[str, Dict[str, Dict[str, float]]]
    updated_at: str = Field(description="When pricing was last updated")


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline ID"),
    include_by_pipeline: bool = Query(False, description="Include breakdown by pipeline"),
    auth: AuthContext = Depends(require_auth),
    usage_storage: UsageStorage = Depends(get_usage_storage),
) -> UsageSummaryResponse:
    """
    Get aggregated LLM usage summary for the organization.

    Returns totals and breakdowns by provider, model, and optionally by pipeline.
    """
    summary = usage_storage.get_summary(
        org_id=auth.org.id,
        pipeline_id=pipeline_id,
        days=days,
        include_by_pipeline=include_by_pipeline,
    )

    return UsageSummaryResponse(
        period_start=summary.period_start,
        period_end=summary.period_end,
        total_runs=summary.total_runs,
        total_stages=summary.total_stages,
        total_input_tokens=summary.total_input_tokens,
        total_output_tokens=summary.total_output_tokens,
        total_tokens=summary.total_tokens,
        total_cost_usd=summary.total_cost_usd,
        by_provider=summary.by_provider,
        by_model=summary.by_model,
        by_pipeline=summary.by_pipeline,
    )


@router.get("/daily", response_model=List[DailyUsageResponse])
async def get_daily_usage(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline ID"),
    auth: AuthContext = Depends(require_auth),
    usage_storage: UsageStorage = Depends(get_usage_storage),
) -> List[DailyUsageResponse]:
    """
    Get daily LLM usage breakdown.

    Useful for charting usage trends over time.
    """
    daily_usage = usage_storage.get_daily_usage(
        org_id=auth.org.id,
        pipeline_id=pipeline_id,
        days=days,
    )

    return [
        DailyUsageResponse(
            date=d["date"],
            run_count=d["run_count"],
            stage_count=d["stage_count"],
            input_tokens=d["input_tokens"],
            output_tokens=d["output_tokens"],
            total_tokens=d["total_tokens"],
            cost_usd=d["cost_usd"],
        )
        for d in daily_usage
    ]


@router.get("/runs/{run_id}", response_model=RunUsageResponse)
async def get_run_usage(
    run_id: str,
    auth: AuthContext = Depends(require_auth),
    usage_storage: UsageStorage = Depends(get_usage_storage),
) -> RunUsageResponse:
    """
    Get detailed LLM usage for a specific run.

    Shows usage per stage and totals for the run.
    """
    records = usage_storage.get_run_usage(run_id, org_id=auth.org.id)

    # Calculate totals
    total_input = sum(r.input_tokens for r in records)
    total_output = sum(r.output_tokens for r in records)
    total_cost = sum(r.cost_usd for r in records)

    return RunUsageResponse(
        run_id=run_id,
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        total_tokens=total_input + total_output,
        total_cost_usd=round(total_cost, 6),
        records=[
            UsageRecordResponse(
                id=r.id,
                run_id=r.run_id,
                pipeline_id=r.pipeline_id,
                stage_id=r.stage_id,
                provider=r.provider,
                model=r.model,
                input_tokens=r.input_tokens,
                output_tokens=r.output_tokens,
                total_tokens=r.total_tokens,
                cost_usd=r.cost_usd,
                duration_ms=r.duration_ms,
                recorded_at=r.recorded_at,
            )
            for r in records
        ],
    )


@router.get("/pricing", response_model=PricingResponse)
async def get_pricing(
    auth: AuthContext = Depends(require_auth),
    usage_storage: UsageStorage = Depends(get_usage_storage),
) -> PricingResponse:
    """
    Get current LLM pricing information.

    Pricing is in USD per 1 million tokens.
    """
    from datetime import datetime

    return PricingResponse(
        pricing=usage_storage.get_pricing(),
        updated_at=datetime.utcnow().isoformat(),
    )


@router.get("/estimate")
async def estimate_cost(
    provider: str = Query(..., description="Provider name (e.g., 'anthropic', 'openai')"),
    model: str = Query(..., description="Model name (e.g., 'claude-3-5-sonnet-20241022')"),
    input_tokens: int = Query(..., ge=0, description="Estimated input tokens"),
    output_tokens: int = Query(..., ge=0, description="Estimated output tokens"),
    auth: AuthContext = Depends(require_auth),
    usage_storage: UsageStorage = Depends(get_usage_storage),
) -> Dict[str, Any]:
    """
    Estimate cost for a given number of tokens.

    Useful for cost planning before running pipelines.
    """
    pricing = usage_storage.get_pricing()
    provider_pricing = pricing.get(provider.lower(), {})
    model_pricing = provider_pricing.get(model, {"input": 0, "output": 0})

    input_cost = (input_tokens / 1_000_000) * model_pricing.get("input", 0)
    output_cost = (output_tokens / 1_000_000) * model_pricing.get("output", 0)
    total_cost = input_cost + output_cost

    return {
        "provider": provider,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "pricing_per_million": model_pricing,
        "estimated_cost": {
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6),
        },
    }
