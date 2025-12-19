"""
Kubernetes Client for FlowMason.

Provides Python API for managing FlowMason Kubernetes resources.
"""

import logging
import time
from typing import Any, Dict, Generator, List, Optional

from flowmason_core.kubernetes.models import (
    Pipeline,
    PipelineRun,
    PipelineRunSpec,
    PipelineRunStatus,
    PipelineSpec,
    PipelineStatus,
    RunPhase,
    StageSpec,
)

logger = logging.getLogger(__name__)


class FlowMasonK8sClient:
    """
    Client for FlowMason Kubernetes resources.

    Provides methods to create, manage, and monitor Pipeline
    and PipelineRun custom resources.

    Example:
        client = FlowMasonK8sClient()

        # Create a pipeline
        pipeline = client.create_pipeline(
            name="my-pipeline",
            namespace="default",
            stages=[
                StageSpec(
                    id="fetch",
                    component_type="http_request",
                    config={"url": "https://api.example.com/data"},
                ),
                StageSpec(
                    id="process",
                    component_type="json_transform",
                    depends_on=["fetch"],
                    config={"mapping": {"result": "$.data"}},
                ),
            ],
            schedule="0 * * * *",
        )

        # Trigger a run
        run = client.create_run(
            name="my-run-001",
            namespace="default",
            pipeline_ref="my-pipeline",
            inputs={"param": "value"},
        )

        # Wait for completion
        result = client.wait_for_run(run.metadata["name"])
    """

    API_GROUP = "flowmason.io"
    API_VERSION = "v1"
    PIPELINE_PLURAL = "pipelines"
    PIPELINERUN_PLURAL = "pipelineruns"

    def __init__(
        self,
        kubeconfig_path: Optional[str] = None,
        context: Optional[str] = None,
        namespace: str = "default",
    ):
        """
        Initialize the client.

        Args:
            kubeconfig_path: Path to kubeconfig (uses default if None)
            context: Kubernetes context to use
            namespace: Default namespace
        """
        self._kubeconfig_path = kubeconfig_path
        self._context = context
        self._default_namespace = namespace
        self._api_client = None
        self._custom_api = None

    def _ensure_client(self) -> None:
        """Ensure Kubernetes client is initialized."""
        if self._api_client is not None:
            return

        try:
            from kubernetes import client, config

            # Load config
            if self._kubeconfig_path:
                config.load_kube_config(
                    config_file=self._kubeconfig_path,
                    context=self._context,
                )
            else:
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config(context=self._context)

            self._api_client = client.ApiClient()
            self._custom_api = client.CustomObjectsApi(self._api_client)

        except ImportError:
            raise ImportError(
                "kubernetes package not installed. Run: pip install kubernetes"
            )

    # Pipeline Operations

    def create_pipeline(
        self,
        name: str,
        stages: List[StageSpec],
        namespace: Optional[str] = None,
        schedule: Optional[str] = None,
        resources: Optional[Dict[str, Any]] = None,
        env: Optional[List[Dict[str, Any]]] = None,
        providers: Optional[Dict[str, Any]] = None,
        timeout: Optional[str] = None,
        retries: int = 0,
        parallelism: bool = True,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        output_stage_id: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
    ) -> Pipeline:
        """
        Create a Pipeline resource.

        Args:
            name: Pipeline name
            stages: List of stage specifications
            namespace: Kubernetes namespace
            schedule: Cron schedule for automatic runs
            resources: Resource requirements
            env: Environment variables
            providers: LLM provider configuration
            timeout: Execution timeout
            retries: Retry count on failure
            parallelism: Enable parallel execution
            input_schema: JSON Schema for inputs
            output_schema: JSON Schema for outputs
            output_stage_id: Stage to use for output
            labels: Kubernetes labels
            annotations: Kubernetes annotations

        Returns:
            Created Pipeline object
        """
        self._ensure_client()
        namespace = namespace or self._default_namespace

        # Build spec
        spec = PipelineSpec(
            stages=stages,
            schedule=schedule,
            resources=resources,
            env=env,
            providers=providers,
            timeout=timeout,
            retries=retries,
            parallelism=parallelism,
            input_schema=input_schema,
            output_schema=output_schema,
            output_stage_id=output_stage_id,
        )

        # Build pipeline
        pipeline = Pipeline(
            metadata={
                "name": name,
                "namespace": namespace,
                "labels": labels or {},
                "annotations": annotations or {},
            },
            spec=spec,
        )

        # Create in cluster
        result = self._custom_api.create_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINE_PLURAL,
            body=pipeline.to_dict(),
        )

        logger.info(f"Created Pipeline: {name} in {namespace}")
        return Pipeline.from_dict(result)

    def get_pipeline(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> Pipeline:
        """Get a Pipeline by name."""
        self._ensure_client()
        namespace = namespace or self._default_namespace

        result = self._custom_api.get_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINE_PLURAL,
            name=name,
        )
        return Pipeline.from_dict(result)

    def list_pipelines(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
    ) -> List[Pipeline]:
        """List Pipelines in a namespace."""
        self._ensure_client()
        namespace = namespace or self._default_namespace

        result = self._custom_api.list_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINE_PLURAL,
            label_selector=label_selector,
        )

        return [Pipeline.from_dict(item) for item in result.get("items", [])]

    def update_pipeline(
        self,
        name: str,
        spec: PipelineSpec,
        namespace: Optional[str] = None,
    ) -> Pipeline:
        """Update a Pipeline."""
        self._ensure_client()
        namespace = namespace or self._default_namespace

        # Get current pipeline
        current = self.get_pipeline(name, namespace)

        # Update spec
        current.spec = spec

        result = self._custom_api.replace_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINE_PLURAL,
            name=name,
            body=current.to_dict(),
        )

        logger.info(f"Updated Pipeline: {name}")
        return Pipeline.from_dict(result)

    def delete_pipeline(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> None:
        """Delete a Pipeline."""
        self._ensure_client()
        namespace = namespace or self._default_namespace

        self._custom_api.delete_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINE_PLURAL,
            name=name,
        )

        logger.info(f"Deleted Pipeline: {name}")

    # PipelineRun Operations

    def create_run(
        self,
        name: str,
        pipeline_ref: str,
        namespace: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        timeout: Optional[str] = None,
        retries: Optional[int] = None,
        env: Optional[List[Dict[str, Any]]] = None,
        service_account: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
    ) -> PipelineRun:
        """
        Create a PipelineRun to execute a Pipeline.

        Args:
            name: Run name
            pipeline_ref: Name of Pipeline to run
            namespace: Kubernetes namespace
            inputs: Input data for the pipeline
            timeout: Override execution timeout
            retries: Override retry count
            env: Additional environment variables
            service_account: Service account for execution
            labels: Kubernetes labels
            annotations: Kubernetes annotations

        Returns:
            Created PipelineRun object
        """
        self._ensure_client()
        namespace = namespace or self._default_namespace

        # Build spec
        spec = PipelineRunSpec(
            pipeline_ref=pipeline_ref,
            inputs=inputs,
            timeout=timeout,
            retries=retries,
            env=env,
            serviceAccountName=service_account,
        )

        # Build run
        run = PipelineRun(
            metadata={
                "name": name,
                "namespace": namespace,
                "labels": labels or {},
                "annotations": annotations or {},
            },
            spec=spec,
        )

        # Create in cluster
        result = self._custom_api.create_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINERUN_PLURAL,
            body=run.to_dict(),
        )

        logger.info(f"Created PipelineRun: {name} for {pipeline_ref}")
        return PipelineRun.from_dict(result)

    def get_run(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> PipelineRun:
        """Get a PipelineRun by name."""
        self._ensure_client()
        namespace = namespace or self._default_namespace

        result = self._custom_api.get_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINERUN_PLURAL,
            name=name,
        )
        return PipelineRun.from_dict(result)

    def list_runs(
        self,
        namespace: Optional[str] = None,
        pipeline_ref: Optional[str] = None,
        label_selector: Optional[str] = None,
    ) -> List[PipelineRun]:
        """List PipelineRuns in a namespace."""
        self._ensure_client()
        namespace = namespace or self._default_namespace

        # Build label selector
        if pipeline_ref and not label_selector:
            label_selector = f"flowmason.io/pipeline={pipeline_ref}"

        result = self._custom_api.list_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINERUN_PLURAL,
            label_selector=label_selector,
        )

        return [PipelineRun.from_dict(item) for item in result.get("items", [])]

    def delete_run(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> None:
        """Delete a PipelineRun."""
        self._ensure_client()
        namespace = namespace or self._default_namespace

        self._custom_api.delete_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINERUN_PLURAL,
            name=name,
        )

        logger.info(f"Deleted PipelineRun: {name}")

    def cancel_run(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> PipelineRun:
        """Cancel a running PipelineRun."""
        self._ensure_client()
        namespace = namespace or self._default_namespace

        # Patch with cancellation annotation
        patch = {
            "metadata": {
                "annotations": {
                    "flowmason.io/cancel": "true"
                }
            }
        }

        result = self._custom_api.patch_namespaced_custom_object(
            group=self.API_GROUP,
            version=self.API_VERSION,
            namespace=namespace,
            plural=self.PIPELINERUN_PLURAL,
            name=name,
            body=patch,
        )

        logger.info(f"Cancelled PipelineRun: {name}")
        return PipelineRun.from_dict(result)

    # Monitoring

    def wait_for_run(
        self,
        name: str,
        namespace: Optional[str] = None,
        timeout_seconds: int = 3600,
        poll_interval: int = 5,
    ) -> PipelineRun:
        """
        Wait for a PipelineRun to complete.

        Args:
            name: Run name
            namespace: Kubernetes namespace
            timeout_seconds: Maximum wait time
            poll_interval: Polling interval in seconds

        Returns:
            Completed PipelineRun

        Raises:
            TimeoutError: If run doesn't complete in time
        """
        namespace = namespace or self._default_namespace
        start_time = time.time()

        while True:
            run = self.get_run(name, namespace)

            if run.is_complete:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                raise TimeoutError(
                    f"PipelineRun {name} did not complete within {timeout_seconds}s"
                )

            logger.debug(f"Run {name} status: {run.status.phase if run.status else 'Unknown'}")
            time.sleep(poll_interval)

    def watch_run(
        self,
        name: str,
        namespace: Optional[str] = None,
        timeout_seconds: int = 3600,
    ) -> Generator[PipelineRunStatus, None, None]:
        """
        Watch a PipelineRun and yield status updates.

        Args:
            name: Run name
            namespace: Kubernetes namespace
            timeout_seconds: Watch timeout

        Yields:
            PipelineRunStatus on each update
        """
        self._ensure_client()
        namespace = namespace or self._default_namespace

        from kubernetes import watch

        w = watch.Watch()

        try:
            for event in w.stream(
                self._custom_api.list_namespaced_custom_object,
                group=self.API_GROUP,
                version=self.API_VERSION,
                namespace=namespace,
                plural=self.PIPELINERUN_PLURAL,
                field_selector=f"metadata.name={name}",
                timeout_seconds=timeout_seconds,
            ):
                obj = event.get("object", {})
                if obj.get("metadata", {}).get("name") == name:
                    run = PipelineRun.from_dict(obj)
                    if run.status:
                        yield run.status

                    if run.is_complete:
                        break

        finally:
            w.stop()

    # Utility Methods

    def trigger_pipeline(
        self,
        pipeline_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        wait: bool = False,
    ) -> PipelineRun:
        """
        Convenience method to trigger a pipeline and optionally wait.

        Args:
            pipeline_name: Name of Pipeline to run
            inputs: Input data
            namespace: Kubernetes namespace
            wait: Whether to wait for completion

        Returns:
            PipelineRun (completed if wait=True)
        """
        namespace = namespace or self._default_namespace

        # Generate run name
        import uuid
        run_name = f"{pipeline_name}-{uuid.uuid4().hex[:8]}"

        run = self.create_run(
            name=run_name,
            pipeline_ref=pipeline_name,
            namespace=namespace,
            inputs=inputs,
        )

        if wait:
            return self.wait_for_run(run_name, namespace)

        return run
