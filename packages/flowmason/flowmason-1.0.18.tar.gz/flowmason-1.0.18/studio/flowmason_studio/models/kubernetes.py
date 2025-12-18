"""
Kubernetes Custom Resource Definition Models.

Models for FlowMason Pipeline CRDs and Kubernetes integration.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PipelinePhase(str, Enum):
    """Phase of pipeline CRD lifecycle."""

    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    SUSPENDED = "Suspended"


class RunPhase(str, Enum):
    """Phase of pipeline run."""

    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class ScheduleType(str, Enum):
    """Type of pipeline schedule."""

    CRON = "cron"
    INTERVAL = "interval"
    EVENT = "event"


# =============================================================================
# Kubernetes Metadata
# =============================================================================


class ObjectMeta(BaseModel):
    """Kubernetes ObjectMeta."""

    name: str = Field(description="Name of the resource")
    namespace: str = Field(default="default", description="Namespace")
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    uid: Optional[str] = None
    resourceVersion: Optional[str] = None
    generation: Optional[int] = None
    creationTimestamp: Optional[str] = None


class OwnerReference(BaseModel):
    """Kubernetes OwnerReference."""

    apiVersion: str
    kind: str
    name: str
    uid: str
    controller: bool = True
    blockOwnerDeletion: bool = True


# =============================================================================
# Pipeline CRD Spec
# =============================================================================


class StageSpec(BaseModel):
    """Stage specification within a Pipeline CRD."""

    id: str = Field(description="Unique stage identifier")
    name: str = Field(description="Display name")
    componentType: str = Field(description="Component type to use")
    config: Dict[str, Any] = Field(default_factory=dict)
    dependsOn: List[str] = Field(default_factory=list)
    retryPolicy: Optional[Dict[str, Any]] = None
    timeout: Optional[str] = None  # Duration string like "5m", "1h"


class ProviderSpec(BaseModel):
    """Provider configuration spec."""

    name: str = Field(description="Provider name")
    type: str = Field(description="Provider type (openai, anthropic, etc.)")
    secretRef: Optional[str] = Field(
        default=None,
        description="Reference to Kubernetes Secret with API key"
    )
    configMapRef: Optional[str] = Field(
        default=None,
        description="Reference to ConfigMap with provider config"
    )
    config: Dict[str, Any] = Field(default_factory=dict)


class ScheduleSpec(BaseModel):
    """Pipeline schedule specification."""

    type: ScheduleType = Field(default=ScheduleType.CRON)
    cron: Optional[str] = Field(
        default=None,
        description="Cron expression (if type=cron)"
    )
    interval: Optional[str] = Field(
        default=None,
        description="Interval duration (if type=interval)"
    )
    timezone: str = Field(default="UTC")
    suspend: bool = Field(default=False)
    concurrencyPolicy: str = Field(
        default="Forbid",
        description="Allow, Forbid, or Replace"
    )
    successfulRunsHistoryLimit: int = Field(default=3)
    failedRunsHistoryLimit: int = Field(default=3)


class ResourceSpec(BaseModel):
    """Resource requirements for pipeline execution."""

    requests: Dict[str, str] = Field(default_factory=dict)
    limits: Dict[str, str] = Field(default_factory=dict)


class PipelineSpec(BaseModel):
    """Specification for a FlowMason Pipeline CRD."""

    description: str = Field(default="")

    # Pipeline stages
    stages: List[StageSpec] = Field(default_factory=list)

    # Variables
    variables: Dict[str, Any] = Field(default_factory=dict)

    # Provider configurations
    providers: List[ProviderSpec] = Field(default_factory=list)

    # Execution settings
    schedule: Optional[ScheduleSpec] = None
    timeout: str = Field(default="1h", description="Overall timeout")
    retryPolicy: Optional[Dict[str, Any]] = None
    parallelism: int = Field(default=1, description="Max parallel stages")

    # Resources for runner pod
    resources: Optional[ResourceSpec] = None

    # Image to use for runner
    runnerImage: str = Field(default="flowmason/runner:latest")

    # Service account
    serviceAccountName: Optional[str] = None

    # Suspend execution
    suspend: bool = Field(default=False)


# =============================================================================
# Pipeline CRD Status
# =============================================================================


class ConditionStatus(str, Enum):
    """Condition status values."""

    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"


class PipelineCondition(BaseModel):
    """Condition in pipeline status."""

    type: str = Field(description="Condition type")
    status: ConditionStatus
    reason: str = Field(default="")
    message: str = Field(default="")
    lastTransitionTime: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )


class PipelineStatus(BaseModel):
    """Status of a FlowMason Pipeline CRD."""

    phase: PipelinePhase = Field(default=PipelinePhase.PENDING)
    conditions: List[PipelineCondition] = Field(default_factory=list)

    # Run statistics
    lastRunTime: Optional[str] = None
    lastSuccessfulRunTime: Optional[str] = None
    nextScheduledRunTime: Optional[str] = None

    # Counts
    totalRuns: int = Field(default=0)
    successfulRuns: int = Field(default=0)
    failedRuns: int = Field(default=0)

    # Current run
    activeRuns: List[str] = Field(default_factory=list)

    # Observed generation
    observedGeneration: Optional[int] = None


# =============================================================================
# Pipeline CRD
# =============================================================================


class FlowMasonPipeline(BaseModel):
    """FlowMason Pipeline Custom Resource Definition."""

    apiVersion: str = Field(default="flowmason.io/v1alpha1")
    kind: str = Field(default="Pipeline")
    metadata: ObjectMeta
    spec: PipelineSpec
    status: Optional[PipelineStatus] = None


# =============================================================================
# PipelineRun CRD
# =============================================================================


class PipelineRunSpec(BaseModel):
    """Specification for a PipelineRun."""

    pipelineRef: str = Field(description="Reference to Pipeline CRD")
    inputs: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[str] = None
    serviceAccountName: Optional[str] = None


class StageRunStatus(BaseModel):
    """Status of a stage execution."""

    stageId: str
    phase: RunPhase = Field(default=RunPhase.PENDING)
    startTime: Optional[str] = None
    completionTime: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retryCount: int = Field(default=0)


class PipelineRunStatus(BaseModel):
    """Status of a PipelineRun."""

    phase: RunPhase = Field(default=RunPhase.PENDING)
    startTime: Optional[str] = None
    completionTime: Optional[str] = None
    stages: List[StageRunStatus] = Field(default_factory=list)
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    conditions: List[PipelineCondition] = Field(default_factory=list)


class FlowMasonPipelineRun(BaseModel):
    """FlowMason PipelineRun Custom Resource Definition."""

    apiVersion: str = Field(default="flowmason.io/v1alpha1")
    kind: str = Field(default="PipelineRun")
    metadata: ObjectMeta
    spec: PipelineRunSpec
    status: Optional[PipelineRunStatus] = None


# =============================================================================
# API Request/Response Models
# =============================================================================


class CreatePipelineCRDRequest(BaseModel):
    """Request to create a Pipeline CRD from an existing pipeline."""

    pipeline_id: str = Field(description="FlowMason pipeline ID")
    name: str = Field(description="Kubernetes resource name")
    namespace: str = Field(default="default")
    labels: Dict[str, str] = Field(default_factory=dict)
    schedule: Optional[ScheduleSpec] = None
    resources: Optional[ResourceSpec] = None


class CreatePipelineCRDResponse(BaseModel):
    """Response with generated CRD."""

    crd: FlowMasonPipeline
    yaml: str = Field(description="YAML representation for kubectl apply")


class ListPipelineCRDsResponse(BaseModel):
    """Response listing Pipeline CRDs."""

    items: List[FlowMasonPipeline]
    total: int


class TriggerPipelineRunRequest(BaseModel):
    """Request to trigger a pipeline run."""

    pipeline_name: str
    namespace: str = Field(default="default")
    inputs: Dict[str, Any] = Field(default_factory=dict)
    run_name: Optional[str] = None


class TriggerPipelineRunResponse(BaseModel):
    """Response from triggering a run."""

    run: FlowMasonPipelineRun
    yaml: str


class CRDGenerationOptions(BaseModel):
    """Options for CRD generation."""

    include_status: bool = Field(
        default=False,
        description="Include status field in generated CRD"
    )
    include_schedule: bool = Field(
        default=True,
        description="Include schedule if defined"
    )
    resolve_secrets: bool = Field(
        default=False,
        description="Include secret references for providers"
    )
    runner_image: str = Field(default="flowmason/runner:latest")
