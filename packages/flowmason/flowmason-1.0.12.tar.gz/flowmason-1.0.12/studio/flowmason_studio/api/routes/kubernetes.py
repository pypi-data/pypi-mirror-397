"""
Kubernetes Integration API Routes.

Provides HTTP API for generating and managing Kubernetes CRDs.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from flowmason_studio.models.kubernetes import (
    CRDGenerationOptions,
    CreatePipelineCRDRequest,
    CreatePipelineCRDResponse,
    FlowMasonPipeline,
    FlowMasonPipelineRun,
    ListPipelineCRDsResponse,
    ResourceSpec,
    ScheduleSpec,
    ScheduleType,
    TriggerPipelineRunRequest,
    TriggerPipelineRunResponse,
)
from flowmason_studio.services.kubernetes_service import get_kubernetes_service
from flowmason_studio.services.storage import get_pipeline_storage

router = APIRouter(prefix="/kubernetes", tags=["kubernetes"])


# =============================================================================
# CRD Generation
# =============================================================================


@router.post("/crd/generate", response_model=CreatePipelineCRDResponse)
async def generate_pipeline_crd(
    request: CreatePipelineCRDRequest,
) -> CreatePipelineCRDResponse:
    """
    Generate a Kubernetes Pipeline CRD from a FlowMason pipeline.

    Converts the pipeline definition to a Kubernetes-native format
    that can be applied with kubectl.
    """
    storage = get_pipeline_storage()
    k8s_service = get_kubernetes_service()

    pipeline = storage.get_pipeline(request.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    crd = k8s_service.pipeline_to_crd(
        pipeline=pipeline,
        name=request.name,
        namespace=request.namespace,
        labels=request.labels,
        schedule=request.schedule,
        resources=request.resources,
    )

    yaml_content = k8s_service.crd_to_yaml(crd)

    return CreatePipelineCRDResponse(
        crd=crd,
        yaml=yaml_content,
    )


@router.get("/crd/generate/{pipeline_id}/yaml", response_class=PlainTextResponse)
async def generate_pipeline_crd_yaml(
    pipeline_id: str,
    name: Optional[str] = Query(None, description="Kubernetes resource name"),
    namespace: str = Query(default="default"),
    schedule_cron: Optional[str] = Query(None, description="Cron schedule"),
    schedule_interval: Optional[str] = Query(None, description="Interval schedule"),
) -> str:
    """
    Generate Pipeline CRD YAML directly for download or piping to kubectl.

    Example: curl ... | kubectl apply -f -
    """
    storage = get_pipeline_storage()
    k8s_service = get_kubernetes_service()

    pipeline = storage.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Use pipeline name if no name specified
    resource_name = name or pipeline.get("name", pipeline_id)

    # Build schedule if specified
    schedule = None
    if schedule_cron:
        schedule = ScheduleSpec(type=ScheduleType.CRON, cron=schedule_cron)
    elif schedule_interval:
        schedule = ScheduleSpec(type=ScheduleType.INTERVAL, interval=schedule_interval)

    crd = k8s_service.pipeline_to_crd(
        pipeline=pipeline,
        name=resource_name,
        namespace=namespace,
        schedule=schedule,
    )

    return k8s_service.crd_to_yaml(crd)


# =============================================================================
# Pipeline CRD Management
# =============================================================================


@router.get("/pipelines", response_model=ListPipelineCRDsResponse)
async def list_pipeline_crds(
    namespace: Optional[str] = Query(None),
) -> ListPipelineCRDsResponse:
    """
    List generated Pipeline CRDs.

    Note: This lists CRDs generated through the API, not those in a cluster.
    """
    k8s_service = get_kubernetes_service()
    pipelines = k8s_service.list_pipelines(namespace=namespace)

    return ListPipelineCRDsResponse(
        items=pipelines,
        total=len(pipelines),
    )


@router.get("/pipelines/{namespace}/{name}", response_model=FlowMasonPipeline)
async def get_pipeline_crd(
    namespace: str,
    name: str,
) -> FlowMasonPipeline:
    """
    Get a specific Pipeline CRD.
    """
    k8s_service = get_kubernetes_service()
    pipeline = k8s_service.get_pipeline(name, namespace)

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline CRD not found")

    return pipeline


# =============================================================================
# PipelineRun Management
# =============================================================================


@router.post("/runs", response_model=TriggerPipelineRunResponse)
async def trigger_pipeline_run(
    request: TriggerPipelineRunRequest,
) -> TriggerPipelineRunResponse:
    """
    Generate a PipelineRun CRD to trigger pipeline execution.

    Returns the PipelineRun CRD that can be applied to the cluster.
    """
    k8s_service = get_kubernetes_service()

    run = k8s_service.create_pipeline_run(
        pipeline_name=request.pipeline_name,
        namespace=request.namespace,
        inputs=request.inputs,
        run_name=request.run_name,
    )

    yaml_content = k8s_service.pipeline_run_to_yaml(run)

    return TriggerPipelineRunResponse(
        run=run,
        yaml=yaml_content,
    )


@router.get("/runs/{namespace}/{name}/yaml", response_class=PlainTextResponse)
async def get_run_yaml(
    namespace: str,
    name: str,
) -> str:
    """
    Get PipelineRun CRD as YAML.
    """
    k8s_service = get_kubernetes_service()
    runs = k8s_service.list_runs(namespace=namespace)

    for run in runs:
        if run.metadata.name == name:
            return k8s_service.pipeline_run_to_yaml(run)

    raise HTTPException(status_code=404, detail="PipelineRun not found")


@router.get("/runs")
async def list_pipeline_runs(
    pipeline_name: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
) -> dict:
    """
    List generated PipelineRun CRDs.
    """
    k8s_service = get_kubernetes_service()
    runs = k8s_service.list_runs(
        pipeline_name=pipeline_name,
        namespace=namespace,
    )

    return {
        "items": [r.model_dump() for r in runs],
        "total": len(runs),
    }


# =============================================================================
# Operator Manifests
# =============================================================================


@router.get("/operator/manifests")
async def get_operator_manifests() -> dict:
    """
    Get all manifests needed to deploy the FlowMason operator.

    Returns a dict of filename -> YAML content.
    """
    k8s_service = get_kubernetes_service()
    manifests = k8s_service.generate_operator_manifests()

    return {
        "manifests": manifests,
        "install_order": ["crds.yaml", "rbac.yaml", "configmap.yaml", "operator.yaml"],
        "instructions": """
To install the FlowMason operator:

1. Apply the CRD definitions:
   kubectl apply -f crds.yaml

2. Apply RBAC configuration:
   kubectl apply -f rbac.yaml

3. Apply ConfigMap:
   kubectl apply -f configmap.yaml

4. Deploy the operator:
   kubectl apply -f operator.yaml

5. Verify the operator is running:
   kubectl get pods -n flowmason-system
""",
    }


@router.get("/operator/manifests/{filename}", response_class=PlainTextResponse)
async def get_operator_manifest(filename: str) -> str:
    """
    Get a specific operator manifest by filename.
    """
    k8s_service = get_kubernetes_service()
    manifests = k8s_service.generate_operator_manifests()

    if filename not in manifests:
        raise HTTPException(
            status_code=404,
            detail=f"Manifest not found. Available: {list(manifests.keys())}",
        )

    return manifests[filename]


@router.get("/operator/install-script", response_class=PlainTextResponse)
async def get_install_script() -> str:
    """
    Get a shell script to install the FlowMason operator.
    """
    return """#!/bin/bash
# FlowMason Operator Installation Script

set -e

API_URL="${FLOWMASON_API_URL:-http://localhost:8999}"

echo "Installing FlowMason Operator..."

# Apply CRDs
echo "Applying CRDs..."
curl -s "${API_URL}/api/v1/kubernetes/operator/manifests/crds.yaml" | kubectl apply -f -

# Apply RBAC
echo "Applying RBAC..."
curl -s "${API_URL}/api/v1/kubernetes/operator/manifests/rbac.yaml" | kubectl apply -f -

# Apply ConfigMap
echo "Applying ConfigMap..."
curl -s "${API_URL}/api/v1/kubernetes/operator/manifests/configmap.yaml" | kubectl apply -f -

# Deploy operator
echo "Deploying operator..."
curl -s "${API_URL}/api/v1/kubernetes/operator/manifests/operator.yaml" | kubectl apply -f -

echo "Waiting for operator to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/flowmason-operator -n flowmason-system

echo "FlowMason Operator installed successfully!"
kubectl get pods -n flowmason-system
"""


# =============================================================================
# Helm Chart
# =============================================================================


@router.get("/helm/values")
async def get_helm_values() -> dict:
    """
    Get default Helm values for FlowMason operator installation.
    """
    return {
        "operator": {
            "image": {
                "repository": "flowmason/operator",
                "tag": "latest",
                "pullPolicy": "IfNotPresent",
            },
            "resources": {
                "requests": {
                    "cpu": "100m",
                    "memory": "128Mi",
                },
                "limits": {
                    "cpu": "500m",
                    "memory": "512Mi",
                },
            },
            "replicaCount": 1,
        },
        "runner": {
            "image": {
                "repository": "flowmason/runner",
                "tag": "latest",
            },
            "defaultTimeout": "1h",
            "maxParallelism": 10,
        },
        "rbac": {
            "create": True,
        },
        "serviceAccount": {
            "create": True,
            "name": "flowmason-operator",
        },
        "monitoring": {
            "enabled": False,
            "serviceMonitor": {
                "enabled": False,
            },
        },
    }


# =============================================================================
# Utilities
# =============================================================================


@router.post("/validate")
async def validate_crd(crd: FlowMasonPipeline) -> dict:
    """
    Validate a Pipeline CRD configuration.

    Checks for common issues before applying to a cluster.
    """
    issues = []
    warnings = []

    # Validate stages
    if not crd.spec.stages:
        issues.append("Pipeline must have at least one stage")

    stage_ids = set()
    for stage in crd.spec.stages:
        if stage.id in stage_ids:
            issues.append(f"Duplicate stage ID: {stage.id}")
        stage_ids.add(stage.id)

        # Check dependencies
        for dep in stage.dependsOn:
            if dep not in stage_ids:
                # Could be forward reference, just warn
                warnings.append(f"Stage '{stage.id}' depends on '{dep}' which may not exist")

    # Validate schedule
    if crd.spec.schedule:
        if crd.spec.schedule.type == ScheduleType.CRON and not crd.spec.schedule.cron:
            issues.append("Cron schedule requires 'cron' expression")
        if crd.spec.schedule.type == ScheduleType.INTERVAL and not crd.spec.schedule.interval:
            issues.append("Interval schedule requires 'interval' value")

    # Check resource names
    name = crd.metadata.name
    if not name or len(name) > 63:
        issues.append("Resource name must be 1-63 characters")
    if not name[0].isalnum() or not name[-1].isalnum():
        issues.append("Resource name must start and end with alphanumeric character")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }


@router.get("/api-resources")
async def get_api_resources() -> dict:
    """
    Get information about FlowMason Kubernetes API resources.
    """
    return {
        "apiVersion": "flowmason.io/v1alpha1",
        "resources": [
            {
                "name": "pipelines",
                "singularName": "pipeline",
                "kind": "Pipeline",
                "shortNames": ["fmp", "fmpipe"],
                "namespaced": True,
                "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"],
            },
            {
                "name": "pipelineruns",
                "singularName": "pipelinerun",
                "kind": "PipelineRun",
                "shortNames": ["fmpr", "fmrun"],
                "namespaced": True,
                "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"],
            },
        ],
    }
