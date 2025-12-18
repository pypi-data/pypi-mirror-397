"""
FlowMason Kubernetes Integration Module.

Provides Python client for FlowMason Kubernetes operator:
- Pipeline CRD management
- PipelineRun CRD management
- Status monitoring

Example:
    from flowmason_core.kubernetes import FlowMasonK8sClient

    client = FlowMasonK8sClient()

    # Create a pipeline
    client.create_pipeline(
        name="my-pipeline",
        namespace="default",
        stages=[...],
        schedule="0 * * * *",
    )

    # Trigger a run
    run = client.create_run(
        name="my-run",
        pipeline_ref="my-pipeline",
        inputs={"key": "value"},
    )

    # Watch status
    for status in client.watch_run(run.name):
        print(f"Status: {status.phase}")
"""

from flowmason_core.kubernetes.client import FlowMasonK8sClient
from flowmason_core.kubernetes.models import (
    Pipeline,
    PipelineRun,
    PipelineSpec,
    PipelineRunSpec,
    PipelineStatus,
    PipelineRunStatus,
    StageSpec,
    StageStatus,
)

__all__ = [
    "FlowMasonK8sClient",
    "Pipeline",
    "PipelineRun",
    "PipelineSpec",
    "PipelineRunSpec",
    "PipelineStatus",
    "PipelineRunStatus",
    "StageSpec",
    "StageStatus",
]
