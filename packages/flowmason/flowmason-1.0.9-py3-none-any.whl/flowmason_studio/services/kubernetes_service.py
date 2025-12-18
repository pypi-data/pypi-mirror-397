"""
Kubernetes Integration Service.

Converts FlowMason pipelines to Kubernetes CRDs and manages k8s resources.
"""

import re
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import yaml

from flowmason_studio.models.kubernetes import (
    CRDGenerationOptions,
    ConditionStatus,
    FlowMasonPipeline,
    FlowMasonPipelineRun,
    ObjectMeta,
    PipelineCondition,
    PipelinePhase,
    PipelineRunSpec,
    PipelineRunStatus,
    PipelineSpec,
    PipelineStatus,
    ProviderSpec,
    ResourceSpec,
    RunPhase,
    ScheduleSpec,
    ScheduleType,
    StageRunStatus,
    StageSpec,
)


class KubernetesService:
    """Service for Kubernetes integration."""

    def __init__(self):
        self._pipelines: Dict[str, FlowMasonPipeline] = {}
        self._runs: Dict[str, FlowMasonPipelineRun] = {}

    def pipeline_to_crd(
        self,
        pipeline: Dict[str, Any],
        name: str,
        namespace: str = "default",
        labels: Optional[Dict[str, str]] = None,
        schedule: Optional[ScheduleSpec] = None,
        resources: Optional[ResourceSpec] = None,
        options: Optional[CRDGenerationOptions] = None,
    ) -> FlowMasonPipeline:
        """
        Convert a FlowMason pipeline to a Kubernetes CRD.

        Args:
            pipeline: FlowMason pipeline dict
            name: Kubernetes resource name
            namespace: Kubernetes namespace
            labels: Additional labels
            schedule: Optional schedule configuration
            resources: Optional resource requirements
            options: Generation options

        Returns:
            FlowMasonPipeline CRD
        """
        options = options or CRDGenerationOptions()

        # Sanitize name for Kubernetes (lowercase, alphanumeric, hyphens)
        k8s_name = self._sanitize_name(name)

        # Build metadata
        metadata = ObjectMeta(
            name=k8s_name,
            namespace=namespace,
            labels={
                "app.kubernetes.io/name": "flowmason",
                "app.kubernetes.io/component": "pipeline",
                "flowmason.io/pipeline-id": pipeline.get("id", ""),
                **(labels or {}),
            },
            annotations={
                "flowmason.io/source-name": pipeline.get("name", ""),
                "flowmason.io/generated-at": datetime.utcnow().isoformat() + "Z",
            },
        )

        # Convert stages
        stages = self._convert_stages(pipeline.get("stages", []))

        # Convert providers
        providers = self._convert_providers(
            pipeline.get("providers", {}),
            options.resolve_secrets,
        )

        # Build spec
        # Convert timeout to string if it's a number (seconds)
        timeout = pipeline.get("settings", {}).get("timeout", "1h")
        if isinstance(timeout, (int, float)):
            timeout = f"{int(timeout)}s"

        spec = PipelineSpec(
            description=pipeline.get("description", ""),
            stages=stages,
            variables=pipeline.get("variables", {}),
            providers=providers,
            schedule=schedule,
            timeout=timeout,
            parallelism=pipeline.get("settings", {}).get("parallelism", 1),
            resources=resources,
            runnerImage=options.runner_image,
        )

        # Build status if requested
        status = None
        if options.include_status:
            status = PipelineStatus(
                phase=PipelinePhase.PENDING,
                conditions=[
                    PipelineCondition(
                        type="Ready",
                        status=ConditionStatus.FALSE,
                        reason="PendingReconciliation",
                        message="Waiting for controller to reconcile",
                    ),
                ],
            )

        crd = FlowMasonPipeline(
            metadata=metadata,
            spec=spec,
            status=status,
        )

        # Store for later reference
        self._pipelines[f"{namespace}/{k8s_name}"] = crd

        return crd

    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for Kubernetes (RFC 1123)."""
        # Convert to lowercase
        name = name.lower()
        # Replace spaces and underscores with hyphens
        name = re.sub(r"[\s_]+", "-", name)
        # Remove invalid characters
        name = re.sub(r"[^a-z0-9-]", "", name)
        # Ensure it starts with alphanumeric
        name = re.sub(r"^[^a-z0-9]+", "", name)
        # Ensure it ends with alphanumeric
        name = re.sub(r"[^a-z0-9]+$", "", name)
        # Truncate to 63 characters
        name = name[:63]
        return name or "pipeline"

    def _convert_stages(self, stages: List[Dict]) -> List[StageSpec]:
        """Convert FlowMason stages to Kubernetes StageSpec."""
        result = []
        for stage in stages:
            stage_spec = StageSpec(
                id=stage.get("id", ""),
                name=stage.get("name", stage.get("id", "")),
                componentType=stage.get("component_type", ""),
                config=stage.get("config", {}),
                dependsOn=stage.get("depends_on", []),
            )

            # Convert retry policy if present
            if stage.get("retry"):
                stage_spec.retryPolicy = {
                    "maxRetries": stage["retry"].get("max_retries", 3),
                    "backoff": stage["retry"].get("backoff", "exponential"),
                }

            # Convert timeout if present
            if stage.get("timeout"):
                stage_spec.timeout = f"{stage['timeout']}s"

            result.append(stage_spec)

        return result

    def _convert_providers(
        self,
        providers: Dict[str, Any],
        resolve_secrets: bool,
    ) -> List[ProviderSpec]:
        """Convert provider configurations to Kubernetes ProviderSpec."""
        result = []
        for name, config in providers.items():
            provider_spec = ProviderSpec(
                name=name,
                type=config.get("type", name),
                config={
                    k: v for k, v in config.items()
                    if k not in ("api_key", "secret", "type")
                },
            )

            # If resolving secrets, add secret references
            if resolve_secrets:
                provider_spec.secretRef = f"flowmason-{name}-credentials"

            result.append(provider_spec)

        return result

    def crd_to_yaml(self, crd: FlowMasonPipeline) -> str:
        """Convert a CRD to YAML for kubectl apply."""
        # Convert to dict, excluding None values
        crd_dict = crd.model_dump(exclude_none=True, by_alias=True)

        # Custom YAML representation
        return yaml.dump(
            crd_dict,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    def create_pipeline_run(
        self,
        pipeline_name: str,
        namespace: str = "default",
        inputs: Optional[Dict[str, Any]] = None,
        run_name: Optional[str] = None,
    ) -> FlowMasonPipelineRun:
        """
        Create a PipelineRun CRD to trigger execution.

        Args:
            pipeline_name: Name of the Pipeline CRD
            namespace: Kubernetes namespace
            inputs: Input values for the run
            run_name: Optional custom run name

        Returns:
            FlowMasonPipelineRun CRD
        """
        if not run_name:
            run_name = f"{pipeline_name}-run-{uuid.uuid4().hex[:8]}"

        run_name = self._sanitize_name(run_name)

        metadata = ObjectMeta(
            name=run_name,
            namespace=namespace,
            labels={
                "app.kubernetes.io/name": "flowmason",
                "app.kubernetes.io/component": "pipeline-run",
                "flowmason.io/pipeline": pipeline_name,
            },
        )

        spec = PipelineRunSpec(
            pipelineRef=pipeline_name,
            inputs=inputs or {},
        )

        status = PipelineRunStatus(
            phase=RunPhase.PENDING,
            conditions=[
                PipelineCondition(
                    type="Initialized",
                    status=ConditionStatus.FALSE,
                    reason="PendingStart",
                    message="Waiting for controller to start execution",
                ),
            ],
        )

        run = FlowMasonPipelineRun(
            metadata=metadata,
            spec=spec,
            status=status,
        )

        # Store for later reference
        self._runs[f"{namespace}/{run_name}"] = run

        return run

    def pipeline_run_to_yaml(self, run: FlowMasonPipelineRun) -> str:
        """Convert a PipelineRun to YAML."""
        run_dict = run.model_dump(exclude_none=True, by_alias=True)
        return yaml.dump(
            run_dict,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    def generate_operator_manifests(self) -> Dict[str, str]:
        """
        Generate Kubernetes manifests for deploying the FlowMason operator.

        Returns dict of filename -> YAML content.
        """
        manifests = {}

        # CRD definitions
        manifests["crds.yaml"] = self._generate_crd_definitions()

        # RBAC
        manifests["rbac.yaml"] = self._generate_rbac()

        # Operator deployment
        manifests["operator.yaml"] = self._generate_operator_deployment()

        # ConfigMap for operator settings
        manifests["configmap.yaml"] = self._generate_configmap()

        return manifests

    def _generate_crd_definitions(self) -> str:
        """Generate CRD definitions for Pipeline and PipelineRun."""
        pipeline_crd = {
            "apiVersion": "apiextensions.k8s.io/v1",
            "kind": "CustomResourceDefinition",
            "metadata": {
                "name": "pipelines.flowmason.io",
            },
            "spec": {
                "group": "flowmason.io",
                "versions": [
                    {
                        "name": "v1alpha1",
                        "served": True,
                        "storage": True,
                        "schema": {
                            "openAPIV3Schema": {
                                "type": "object",
                                "properties": {
                                    "spec": {
                                        "type": "object",
                                        "properties": {
                                            "description": {"type": "string"},
                                            "stages": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": ["id", "componentType"],
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "name": {"type": "string"},
                                                        "componentType": {"type": "string"},
                                                        "config": {"type": "object", "x-kubernetes-preserve-unknown-fields": True},
                                                        "dependsOn": {"type": "array", "items": {"type": "string"}},
                                                    },
                                                },
                                            },
                                            "variables": {"type": "object", "x-kubernetes-preserve-unknown-fields": True},
                                            "schedule": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {"type": "string", "enum": ["cron", "interval", "event"]},
                                                    "cron": {"type": "string"},
                                                    "interval": {"type": "string"},
                                                    "suspend": {"type": "boolean"},
                                                },
                                            },
                                            "timeout": {"type": "string"},
                                            "suspend": {"type": "boolean"},
                                        },
                                    },
                                    "status": {
                                        "type": "object",
                                        "properties": {
                                            "phase": {"type": "string"},
                                            "conditions": {"type": "array", "items": {"type": "object"}},
                                            "totalRuns": {"type": "integer"},
                                            "successfulRuns": {"type": "integer"},
                                            "failedRuns": {"type": "integer"},
                                        },
                                    },
                                },
                            },
                        },
                        "subresources": {"status": {}},
                        "additionalPrinterColumns": [
                            {"name": "Phase", "type": "string", "jsonPath": ".status.phase"},
                            {"name": "Runs", "type": "integer", "jsonPath": ".status.totalRuns"},
                            {"name": "Age", "type": "date", "jsonPath": ".metadata.creationTimestamp"},
                        ],
                    },
                ],
                "scope": "Namespaced",
                "names": {
                    "plural": "pipelines",
                    "singular": "pipeline",
                    "kind": "Pipeline",
                    "shortNames": ["fmp", "fmpipe"],
                },
            },
        }

        pipeline_run_crd = {
            "apiVersion": "apiextensions.k8s.io/v1",
            "kind": "CustomResourceDefinition",
            "metadata": {
                "name": "pipelineruns.flowmason.io",
            },
            "spec": {
                "group": "flowmason.io",
                "versions": [
                    {
                        "name": "v1alpha1",
                        "served": True,
                        "storage": True,
                        "schema": {
                            "openAPIV3Schema": {
                                "type": "object",
                                "properties": {
                                    "spec": {
                                        "type": "object",
                                        "required": ["pipelineRef"],
                                        "properties": {
                                            "pipelineRef": {"type": "string"},
                                            "inputs": {"type": "object", "x-kubernetes-preserve-unknown-fields": True},
                                            "timeout": {"type": "string"},
                                        },
                                    },
                                    "status": {
                                        "type": "object",
                                        "properties": {
                                            "phase": {"type": "string"},
                                            "startTime": {"type": "string"},
                                            "completionTime": {"type": "string"},
                                            "stages": {"type": "array", "items": {"type": "object"}},
                                            "output": {"type": "object", "x-kubernetes-preserve-unknown-fields": True},
                                            "error": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                        "subresources": {"status": {}},
                        "additionalPrinterColumns": [
                            {"name": "Pipeline", "type": "string", "jsonPath": ".spec.pipelineRef"},
                            {"name": "Phase", "type": "string", "jsonPath": ".status.phase"},
                            {"name": "Age", "type": "date", "jsonPath": ".metadata.creationTimestamp"},
                        ],
                    },
                ],
                "scope": "Namespaced",
                "names": {
                    "plural": "pipelineruns",
                    "singular": "pipelinerun",
                    "kind": "PipelineRun",
                    "shortNames": ["fmpr", "fmrun"],
                },
            },
        }

        return yaml.dump_all(
            [pipeline_crd, pipeline_run_crd],
            default_flow_style=False,
            sort_keys=False,
        )

    def _generate_rbac(self) -> str:
        """Generate RBAC manifests for the operator."""
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "flowmason-operator",
                "namespace": "flowmason-system",
            },
        }

        cluster_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": "flowmason-operator",
            },
            "rules": [
                {
                    "apiGroups": ["flowmason.io"],
                    "resources": ["pipelines", "pipelineruns"],
                    "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"],
                },
                {
                    "apiGroups": ["flowmason.io"],
                    "resources": ["pipelines/status", "pipelineruns/status"],
                    "verbs": ["get", "update", "patch"],
                },
                {
                    "apiGroups": [""],
                    "resources": ["pods", "configmaps", "secrets"],
                    "verbs": ["get", "list", "watch", "create", "update", "delete"],
                },
                {
                    "apiGroups": [""],
                    "resources": ["events"],
                    "verbs": ["create", "patch"],
                },
                {
                    "apiGroups": ["batch"],
                    "resources": ["jobs"],
                    "verbs": ["get", "list", "watch", "create", "update", "delete"],
                },
            ],
        }

        cluster_role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": "flowmason-operator",
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "flowmason-operator",
                    "namespace": "flowmason-system",
                },
            ],
            "roleRef": {
                "kind": "ClusterRole",
                "name": "flowmason-operator",
                "apiGroup": "rbac.authorization.k8s.io",
            },
        }

        return yaml.dump_all(
            [service_account, cluster_role, cluster_role_binding],
            default_flow_style=False,
            sort_keys=False,
        )

    def _generate_operator_deployment(self) -> str:
        """Generate the operator deployment manifest."""
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "flowmason-system",
                "labels": {
                    "app.kubernetes.io/name": "flowmason",
                },
            },
        }

        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "flowmason-operator",
                "namespace": "flowmason-system",
                "labels": {
                    "app.kubernetes.io/name": "flowmason",
                    "app.kubernetes.io/component": "operator",
                },
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app.kubernetes.io/name": "flowmason",
                        "app.kubernetes.io/component": "operator",
                    },
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app.kubernetes.io/name": "flowmason",
                            "app.kubernetes.io/component": "operator",
                        },
                    },
                    "spec": {
                        "serviceAccountName": "flowmason-operator",
                        "containers": [
                            {
                                "name": "operator",
                                "image": "flowmason/operator:latest",
                                "imagePullPolicy": "IfNotPresent",
                                "ports": [
                                    {"containerPort": 8080, "name": "metrics"},
                                    {"containerPort": 8081, "name": "health"},
                                ],
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/healthz",
                                        "port": "health",
                                    },
                                    "initialDelaySeconds": 15,
                                    "periodSeconds": 20,
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/readyz",
                                        "port": "health",
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 10,
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
                                "env": [
                                    {
                                        "name": "WATCH_NAMESPACE",
                                        "valueFrom": {
                                            "fieldRef": {
                                                "fieldPath": "metadata.namespace",
                                            },
                                        },
                                    },
                                    {
                                        "name": "POD_NAME",
                                        "valueFrom": {
                                            "fieldRef": {
                                                "fieldPath": "metadata.name",
                                            },
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                },
            },
        }

        return yaml.dump_all(
            [namespace, deployment],
            default_flow_style=False,
            sort_keys=False,
        )

    def _generate_configmap(self) -> str:
        """Generate ConfigMap for operator configuration."""
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "flowmason-operator-config",
                "namespace": "flowmason-system",
            },
            "data": {
                "runner-image": "flowmason/runner:latest",
                "default-timeout": "1h",
                "max-parallelism": "10",
                "log-level": "info",
            },
        }

        return yaml.dump(configmap, default_flow_style=False, sort_keys=False)

    def list_pipelines(
        self,
        namespace: Optional[str] = None,
    ) -> List[FlowMasonPipeline]:
        """List stored Pipeline CRDs."""
        if namespace:
            return [
                p for key, p in self._pipelines.items()
                if key.startswith(f"{namespace}/")
            ]
        return list(self._pipelines.values())

    def get_pipeline(
        self,
        name: str,
        namespace: str = "default",
    ) -> Optional[FlowMasonPipeline]:
        """Get a Pipeline CRD by name."""
        return self._pipelines.get(f"{namespace}/{name}")

    def list_runs(
        self,
        pipeline_name: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> List[FlowMasonPipelineRun]:
        """List stored PipelineRun CRDs."""
        runs = list(self._runs.values())

        if namespace:
            runs = [
                r for r in runs
                if r.metadata.namespace == namespace
            ]

        if pipeline_name:
            runs = [
                r for r in runs
                if r.spec.pipelineRef == pipeline_name
            ]

        return runs


# Singleton instance
_kubernetes_service: Optional[KubernetesService] = None


def get_kubernetes_service() -> KubernetesService:
    """Get or create the Kubernetes service singleton."""
    global _kubernetes_service
    if _kubernetes_service is None:
        _kubernetes_service = KubernetesService()
    return _kubernetes_service
