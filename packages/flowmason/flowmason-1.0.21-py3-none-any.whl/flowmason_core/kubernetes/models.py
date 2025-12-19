"""
Kubernetes Resource Models for FlowMason.

Pydantic models for FlowMason CRDs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PipelinePhase(str, Enum):
    """Phase of a Pipeline."""
    PENDING = "Pending"
    READY = "Ready"
    RUNNING = "Running"
    FAILED = "Failed"
    SUSPENDED = "Suspended"


class RunPhase(str, Enum):
    """Phase of a PipelineRun."""
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    TIMED_OUT = "TimedOut"


class StagePhase(str, Enum):
    """Phase of a stage in a PipelineRun."""
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    SKIPPED = "Skipped"


class ResourceRequirements(BaseModel):
    """Resource requirements for execution."""
    requests: Optional[Dict[str, str]] = None
    limits: Optional[Dict[str, str]] = None


class EnvVar(BaseModel):
    """Environment variable configuration."""
    name: str
    value: Optional[str] = None
    valueFrom: Optional[Dict[str, Any]] = None


class ProviderConfig(BaseModel):
    """LLM provider configuration."""
    model: Optional[str] = None
    secretRef: Optional[str] = None


class ProvidersConfig(BaseModel):
    """Providers configuration."""
    default: Optional[str] = None
    anthropic: Optional[ProviderConfig] = None
    openai: Optional[ProviderConfig] = None


class TriggerConfig(BaseModel):
    """Trigger configuration."""
    webhook: Optional[Dict[str, Any]] = None
    event: Optional[Dict[str, Any]] = None


class StageSpec(BaseModel):
    """Specification for a pipeline stage."""
    id: str
    name: Optional[str] = None
    componentType: str = Field(alias="component_type")
    dependsOn: List[str] = Field(default_factory=list, alias="depends_on")
    config: Optional[Dict[str, Any]] = None
    inputMapping: Optional[Dict[str, Any]] = Field(default=None, alias="input_mapping")

    class Config:
        populate_by_name = True


class PipelineSpec(BaseModel):
    """Specification for a Pipeline CRD."""
    stages: List[StageSpec]
    source: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None
    triggers: Optional[TriggerConfig] = None
    resources: Optional[ResourceRequirements] = None
    env: Optional[List[EnvVar]] = None
    providers: Optional[ProvidersConfig] = None
    timeout: Optional[str] = None
    retries: int = 0
    parallelism: bool = True
    inputSchema: Optional[Dict[str, Any]] = Field(default=None, alias="input_schema")
    outputSchema: Optional[Dict[str, Any]] = Field(default=None, alias="output_schema")
    outputStageId: Optional[str] = Field(default=None, alias="output_stage_id")

    class Config:
        populate_by_name = True


class Condition(BaseModel):
    """Status condition."""
    type: str
    status: str
    lastTransitionTime: Optional[datetime] = None
    reason: Optional[str] = None
    message: Optional[str] = None


class PipelineStatus(BaseModel):
    """Status of a Pipeline CRD."""
    phase: Optional[PipelinePhase] = None
    conditions: List[Condition] = Field(default_factory=list)
    lastRunId: Optional[str] = None
    lastRunTime: Optional[datetime] = None
    lastRunStatus: Optional[str] = None
    nextScheduledRun: Optional[datetime] = None
    observedGeneration: Optional[int] = None


class Pipeline(BaseModel):
    """FlowMason Pipeline CRD."""
    apiVersion: str = "flowmason.io/v1"
    kind: str = "Pipeline"
    metadata: Dict[str, Any]
    spec: PipelineSpec
    status: Optional[PipelineStatus] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pipeline":
        """Create from dictionary."""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Kubernetes API."""
        result = {
            "apiVersion": self.apiVersion,
            "kind": self.kind,
            "metadata": self.metadata,
            "spec": self.spec.model_dump(by_alias=True, exclude_none=True),
        }
        if self.status:
            result["status"] = self.status.model_dump(exclude_none=True)
        return result


class PipelineRunSpec(BaseModel):
    """Specification for a PipelineRun CRD."""
    pipelineRef: str = Field(alias="pipeline_ref")
    inputs: Optional[Dict[str, Any]] = None
    inputsFrom: Optional[Dict[str, str]] = None
    timeout: Optional[str] = None
    retries: Optional[int] = None
    env: Optional[List[EnvVar]] = None
    serviceAccountName: Optional[str] = None
    nodeSelector: Optional[Dict[str, str]] = None
    tolerations: Optional[List[Dict[str, Any]]] = None

    class Config:
        populate_by_name = True


class StageStatus(BaseModel):
    """Status of a stage in a run."""
    id: str
    name: Optional[str] = None
    phase: StagePhase = StagePhase.PENDING
    startTime: Optional[datetime] = None
    completionTime: Optional[datetime] = None
    duration: Optional[str] = None
    error: Optional[str] = None
    outputPreview: Optional[str] = None


class RunMetrics(BaseModel):
    """Execution metrics."""
    totalTokens: Optional[int] = None
    totalCost: Optional[str] = None
    stagesCompleted: int = 0
    stagesTotal: int = 0


class RunError(BaseModel):
    """Error information."""
    message: str
    stage: Optional[str] = None
    details: Optional[str] = None


class PipelineRunStatus(BaseModel):
    """Status of a PipelineRun CRD."""
    phase: Optional[RunPhase] = None
    conditions: List[Condition] = Field(default_factory=list)
    startTime: Optional[datetime] = None
    completionTime: Optional[datetime] = None
    duration: Optional[str] = None
    stages: List[StageStatus] = Field(default_factory=list)
    output: Optional[Dict[str, Any]] = None
    error: Optional[RunError] = None
    metrics: Optional[RunMetrics] = None
    podName: Optional[str] = None
    runId: Optional[str] = None
    observedGeneration: Optional[int] = None


class PipelineRun(BaseModel):
    """FlowMason PipelineRun CRD."""
    apiVersion: str = "flowmason.io/v1"
    kind: str = "PipelineRun"
    metadata: Dict[str, Any]
    spec: PipelineRunSpec
    status: Optional[PipelineRunStatus] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineRun":
        """Create from dictionary."""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Kubernetes API."""
        result = {
            "apiVersion": self.apiVersion,
            "kind": self.kind,
            "metadata": self.metadata,
            "spec": self.spec.model_dump(by_alias=True, exclude_none=True),
        }
        if self.status:
            result["status"] = self.status.model_dump(exclude_none=True)
        return result

    @property
    def is_complete(self) -> bool:
        """Check if run is complete."""
        if self.status and self.status.phase:
            return self.status.phase in (
                RunPhase.SUCCEEDED,
                RunPhase.FAILED,
                RunPhase.CANCELLED,
                RunPhase.TIMED_OUT,
            )
        return False

    @property
    def is_successful(self) -> bool:
        """Check if run succeeded."""
        return self.status and self.status.phase == RunPhase.SUCCEEDED
