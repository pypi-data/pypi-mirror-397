"""
Prompt A/B Testing API Routes.

Provides HTTP API for managing prompt experiments and collecting metrics.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from flowmason_studio.models.experiments import (
    CreateExperimentRequest,
    Experiment,
    ExperimentListResponse,
    ExperimentResults,
    ExperimentStatsResponse,
    ExperimentStatus,
    MetricRecord,
    RecordMetricRequest,
    RecordMetricsRequest,
    SelectVariantRequest,
    SelectVariantResponse,
    UpdateExperimentRequest,
)
from flowmason_studio.services.experiment_storage import get_experiment_storage
from flowmason_studio.services.prompt_storage import get_prompt_storage

router = APIRouter(prefix="/experiments", tags=["experiments"])


# =============================================================================
# Response Models
# =============================================================================


class ExperimentResponse(BaseModel):
    """Response for experiment operations."""

    success: bool
    message: str
    experiment: Optional[Experiment] = None


class MetricRecordResponse(BaseModel):
    """Response for metric recording."""

    success: bool
    records: List[MetricRecord]


# =============================================================================
# Experiment CRUD
# =============================================================================


@router.get("", response_model=ExperimentListResponse)
async def list_experiments(
    org_id: str = Query(default="default", description="Organization ID"),
    status: Optional[ExperimentStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> ExperimentListResponse:
    """List all experiments for an organization."""
    storage = get_experiment_storage()

    experiments, total = storage.list_experiments(
        org_id=org_id,
        status=status,
        page=page,
        page_size=page_size,
    )

    return ExperimentListResponse(
        experiments=experiments,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=Experiment)
async def create_experiment(
    request: CreateExperimentRequest,
    org_id: str = Query(default="default", description="Organization ID"),
) -> Experiment:
    """Create a new A/B test experiment."""
    storage = get_experiment_storage()

    # Validate that at least 2 variants are provided
    if len(request.variants) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 variants are required for an A/B test"
        )

    # Validate prompt references
    prompt_storage = get_prompt_storage()
    for variant in request.variants:
        if variant.prompt_id:
            prompt = prompt_storage.get(variant.prompt_id, org_id)
            if not prompt:
                raise HTTPException(
                    status_code=400,
                    detail=f"Prompt '{variant.prompt_id}' not found"
                )

    return storage.create_experiment(
        name=request.name,
        org_id=org_id,
        variants=request.variants,
        description=request.description,
        metrics=request.metrics if request.metrics else None,
        primary_metric=request.primary_metric,
        default_model=request.default_model,
        default_temperature=request.default_temperature,
        default_max_tokens=request.default_max_tokens,
        pipeline_ids=request.pipeline_ids,
        stage_ids=request.stage_ids,
        user_percentage=request.user_percentage,
        min_samples_per_variant=request.min_samples_per_variant,
        tags=request.tags,
    )


@router.get("/{experiment_id}", response_model=Experiment)
async def get_experiment(experiment_id: str) -> Experiment:
    """Get an experiment by ID."""
    storage = get_experiment_storage()

    experiment = storage.get_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return experiment


@router.put("/{experiment_id}", response_model=Experiment)
async def update_experiment(
    experiment_id: str,
    request: UpdateExperimentRequest,
) -> Experiment:
    """Update an experiment."""
    storage = get_experiment_storage()

    # Can't modify running experiments significantly
    existing = storage.get_experiment(experiment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if existing.status == ExperimentStatus.RUNNING:
        if request.variants is not None:
            raise HTTPException(
                status_code=400,
                detail="Cannot modify variants while experiment is running"
            )

    updated = storage.update_experiment(
        experiment_id,
        name=request.name,
        description=request.description,
        status=request.status,
        variants=request.variants,
        metrics=request.metrics,
        primary_metric=request.primary_metric,
        user_percentage=request.user_percentage,
        min_samples_per_variant=request.min_samples_per_variant,
        tags=request.tags,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return updated


@router.delete("/{experiment_id}", response_model=ExperimentResponse)
async def delete_experiment(experiment_id: str) -> ExperimentResponse:
    """Delete an experiment and all its data."""
    storage = get_experiment_storage()

    # Check if running
    existing = storage.get_experiment(experiment_id)
    if existing and existing.status == ExperimentStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a running experiment. Stop it first."
        )

    success = storage.delete_experiment(experiment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return ExperimentResponse(
        success=True,
        message=f"Experiment {experiment_id} deleted",
    )


# =============================================================================
# Experiment Control
# =============================================================================


@router.post("/{experiment_id}/start", response_model=Experiment)
async def start_experiment(experiment_id: str) -> Experiment:
    """Start an experiment (begin collecting data)."""
    storage = get_experiment_storage()

    existing = storage.get_experiment(experiment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if existing.status == ExperimentStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Experiment is already running"
        )

    if existing.status == ExperimentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Cannot restart a completed experiment"
        )

    updated = storage.update_experiment(
        experiment_id,
        status=ExperimentStatus.RUNNING
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return updated


@router.post("/{experiment_id}/pause", response_model=Experiment)
async def pause_experiment(experiment_id: str) -> Experiment:
    """Pause a running experiment."""
    storage = get_experiment_storage()

    existing = storage.get_experiment(experiment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if existing.status != ExperimentStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Can only pause running experiments"
        )

    updated = storage.update_experiment(
        experiment_id,
        status=ExperimentStatus.PAUSED
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return updated


@router.post("/{experiment_id}/resume", response_model=Experiment)
async def resume_experiment(experiment_id: str) -> Experiment:
    """Resume a paused experiment."""
    storage = get_experiment_storage()

    existing = storage.get_experiment(experiment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if existing.status != ExperimentStatus.PAUSED:
        raise HTTPException(
            status_code=400,
            detail="Can only resume paused experiments"
        )

    updated = storage.update_experiment(
        experiment_id,
        status=ExperimentStatus.RUNNING
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return updated


@router.post("/{experiment_id}/complete", response_model=Experiment)
async def complete_experiment(experiment_id: str) -> Experiment:
    """Mark an experiment as completed."""
    storage = get_experiment_storage()

    existing = storage.get_experiment(experiment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if existing.status == ExperimentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Experiment is already completed"
        )

    # Get results to determine winner
    results = storage.get_results(experiment_id)

    updated = storage.update_experiment(
        experiment_id,
        status=ExperimentStatus.COMPLETED,
        winner_variant_id=results.winner_variant_id if results else None,
        confidence_level=results.confidence_level if results else None,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return updated


# =============================================================================
# Variant Selection
# =============================================================================


@router.post("/{experiment_id}/select", response_model=SelectVariantResponse)
async def select_variant(
    experiment_id: str,
    request: SelectVariantRequest,
    org_id: str = Query(default="default", description="Organization ID"),
) -> SelectVariantResponse:
    """Select a variant for a user.

    Uses consistent hashing for sticky assignment.
    Returns the variant configuration to use.
    """
    storage = get_experiment_storage()
    prompt_storage = get_prompt_storage()

    result = storage.select_variant(
        experiment_id,
        user_id=request.user_id,
        pipeline_id=request.pipeline_id,
        stage_id=request.stage_id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found or not running"
        )

    experiment, variant = result

    # Resolve prompt content
    prompt_content = variant.content
    system_prompt = variant.system_prompt

    if variant.prompt_id:
        prompt = prompt_storage.get(variant.prompt_id, org_id)
        if prompt:
            prompt_content = prompt.content
            system_prompt = prompt.system_prompt

    return SelectVariantResponse(
        experiment_id=experiment_id,
        variant_id=variant.id,
        variant_name=variant.name,
        prompt_content=prompt_content,
        system_prompt=system_prompt,
        model=variant.model or experiment.default_model,
        temperature=variant.temperature or experiment.default_temperature,
        max_tokens=variant.max_tokens or experiment.default_max_tokens,
        is_control=variant.is_control,
    )


# =============================================================================
# Metric Recording
# =============================================================================


@router.post("/{experiment_id}/metrics", response_model=MetricRecord)
async def record_metric(
    experiment_id: str,
    request: RecordMetricRequest,
) -> MetricRecord:
    """Record a single metric data point."""
    storage = get_experiment_storage()

    # Verify experiment exists
    experiment = storage.get_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # Verify variant exists
    variant_exists = any(v.id == request.variant_id for v in experiment.variants)
    if not variant_exists:
        raise HTTPException(status_code=400, detail="Variant not found in experiment")

    return storage.record_metric(
        experiment_id=experiment_id,
        variant_id=request.variant_id,
        metric_name=request.metric_name,
        value=request.value,
        run_id=request.run_id,
        pipeline_id=request.pipeline_id,
        stage_id=request.stage_id,
        user_id=request.user_id,
        metadata=request.metadata,
    )


@router.post("/{experiment_id}/metrics/batch", response_model=MetricRecordResponse)
async def record_metrics_batch(
    experiment_id: str,
    request: RecordMetricsRequest,
) -> MetricRecordResponse:
    """Record multiple metrics at once."""
    storage = get_experiment_storage()

    # Verify experiment exists
    experiment = storage.get_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # Verify variant exists
    variant_exists = any(v.id == request.variant_id for v in experiment.variants)
    if not variant_exists:
        raise HTTPException(status_code=400, detail="Variant not found in experiment")

    records = storage.record_metrics(
        experiment_id=experiment_id,
        variant_id=request.variant_id,
        metrics=request.metrics,
        run_id=request.run_id,
        pipeline_id=request.pipeline_id,
        stage_id=request.stage_id,
        user_id=request.user_id,
    )

    return MetricRecordResponse(
        success=True,
        records=records,
    )


# =============================================================================
# Results and Analysis
# =============================================================================


@router.get("/{experiment_id}/results", response_model=ExperimentResults)
async def get_results(experiment_id: str) -> ExperimentResults:
    """Get experiment results with statistical analysis."""
    storage = get_experiment_storage()

    results = storage.get_results(experiment_id)
    if not results:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return results


# =============================================================================
# Statistics
# =============================================================================


@router.get("/stats", response_model=ExperimentStatsResponse)
async def get_stats(
    org_id: str = Query(default="default", description="Organization ID"),
) -> ExperimentStatsResponse:
    """Get experiment statistics for an organization."""
    storage = get_experiment_storage()
    stats = storage.get_stats(org_id)

    return ExperimentStatsResponse(
        total_experiments=stats["total_experiments"],
        running_experiments=stats["running_experiments"],
        completed_experiments=stats["completed_experiments"],
        total_impressions=stats["total_impressions"],
        experiments_with_winners=stats["experiments_with_winners"],
    )


# =============================================================================
# Convenience Endpoints
# =============================================================================


@router.get("/running", response_model=ExperimentListResponse)
async def list_running_experiments(
    org_id: str = Query(default="default", description="Organization ID"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> ExperimentListResponse:
    """List all running experiments."""
    storage = get_experiment_storage()

    experiments, total = storage.list_experiments(
        org_id=org_id,
        status=ExperimentStatus.RUNNING,
        page=page,
        page_size=page_size,
    )

    # Filter by pipeline if specified
    if pipeline_id:
        experiments = [
            e for e in experiments
            if not e.pipeline_ids or pipeline_id in e.pipeline_ids
        ]
        total = len(experiments)

    return ExperimentListResponse(
        experiments=experiments,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{experiment_id}/declare-winner", response_model=Experiment)
async def declare_winner(
    experiment_id: str,
    variant_id: str = Query(..., description="Variant ID to declare as winner"),
    confidence: float = Query(
        default=0.95,
        ge=0, le=1,
        description="Confidence level"
    ),
) -> Experiment:
    """Manually declare a winner and complete the experiment."""
    storage = get_experiment_storage()

    existing = storage.get_experiment(experiment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # Verify variant exists
    variant_exists = any(v.id == variant_id for v in existing.variants)
    if not variant_exists:
        raise HTTPException(status_code=400, detail="Variant not found in experiment")

    updated = storage.update_experiment(
        experiment_id,
        status=ExperimentStatus.COMPLETED,
        winner_variant_id=variant_id,
        confidence_level=confidence,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return updated
