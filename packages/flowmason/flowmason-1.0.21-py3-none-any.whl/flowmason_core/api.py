"""
FlowMason Public API.

This module provides the high-level public API for FlowMason.
Use this for programmatic access to pipelines and components.

Quick Start:
    from flowmason_core.api import FlowMason

    # Initialize with API keys
    fm = FlowMason(providers={"anthropic": "sk-..."})

    # Load packages
    fm.load_packages("./packages")

    # Define a pipeline inline
    pipeline = fm.pipeline(
        name="Content Generator",
        stages=[
            fm.stage("generator", config={"prompt": "Write about {topic}"}),
            fm.stage("critic", depends_on=["generator"]),
        ]
    )

    # Run it
    result = await pipeline.run({"topic": "AI"})
    print(result.output)

    # Or load from file
    result = await fm.run_pipeline_file("./pipelines/my-pipeline.pipeline.json", {"topic": "AI"})

    # With progress callbacks
    async def on_stage_complete(stage_id, output):
        print(f"Stage {stage_id} completed")

    result = await pipeline.run({"topic": "AI"}, on_stage_complete=on_stage_complete)
"""

import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from flowmason_core.config import ComponentConfig, ExecutionContext
from flowmason_core.execution import ComponentResult, DAGExecutor, UsageMetrics
from flowmason_core.providers import get_provider, list_providers
from flowmason_core.registry import ComponentRegistry

# Type aliases for callbacks
StageCallback = Callable[[str, Any], None]  # (stage_id, output) -> None
AsyncStageCallback = Callable[[str, Any], Any]  # Async version


# Environment variable map for provider API keys
PROVIDER_ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
}


@dataclass
class PipelineDefinition:
    """Definition of a pipeline."""
    name: str
    description: str = ""
    stages: List["StageDefinition"] = field(default_factory=list)
    version: str = "1.0.0"


@dataclass
class StageDefinition:
    """Definition of a stage in a pipeline."""
    id: str
    component_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    name: Optional[str] = None


@dataclass
class PipelineResult:
    """Result from running a pipeline."""
    success: bool
    output: Dict[str, Any]
    stage_results: Dict[str, ComponentResult]
    usage: UsageMetrics
    error: Optional[str] = None

    @property
    def final_output(self) -> Any:
        """Get the output from the final stage."""
        if self.stage_results:
            last_stage_id = list(self.stage_results.keys())[-1]
            return self.stage_results[last_stage_id].output
        return None


class Pipeline:
    """
    Executable pipeline.

    Created by FlowMason.pipeline() method.
    """

    def __init__(
        self,
        definition: PipelineDefinition,
        registry: ComponentRegistry,
        providers: Dict[str, Any],
        default_provider: Optional[str] = None,
    ):
        self.definition = definition
        self.registry = registry
        self.providers = providers
        self.default_provider = default_provider

    async def run(
        self,
        input: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        on_stage_start: Optional[AsyncStageCallback] = None,
        on_stage_complete: Optional[AsyncStageCallback] = None,
        on_stage_error: Optional[AsyncStageCallback] = None,
    ) -> PipelineResult:
        """
        Run the pipeline.

        Args:
            input: Input data for the pipeline
            trace_id: Optional trace ID for observability
            on_stage_start: Async callback called when a stage starts
            on_stage_complete: Async callback called when a stage completes
            on_stage_error: Async callback called when a stage fails

        Returns:
            PipelineResult with output and metrics

        Example:
            async def log_progress(stage_id, data):
                print(f"Stage {stage_id}: {data}")

            result = await pipeline.run(
                {"topic": "AI"},
                on_stage_complete=log_progress
            )
        """

        input = input or {}
        run_id = str(uuid.uuid4())

        # Create execution context
        context = ExecutionContext(
            run_id=run_id,
            pipeline_id=self.definition.name,
            pipeline_version=self.definition.version,
            pipeline_input=input,
            trace_id=trace_id or run_id,
            providers=self.providers,
        )

        # Create DAG executor
        executor = DAGExecutor(
            registry=self.registry,
            context=context,
            providers=self.providers,
            default_provider=self.default_provider,
        )

        # Convert stage definitions to ComponentConfigs
        stages = [
            ComponentConfig(
                id=stage.id,
                type=stage.component_type,
                input_mapping=stage.config,
                depends_on=stage.depends_on,
            )
            for stage in self.definition.stages
        ]

        try:
            # Execute with callbacks
            results = {}
            for stage in stages:
                # Call start callback
                if on_stage_start:
                    try:
                        await on_stage_start(stage.id, {"status": "starting"})
                    except Exception:
                        pass  # Don't fail on callback errors

                try:
                    # Execute single stage
                    stage_results = await executor.execute([stage], input)
                    results.update(stage_results)

                    # Call complete callback
                    if on_stage_complete and stage.id in stage_results:
                        try:
                            await on_stage_complete(stage.id, stage_results[stage.id].output)
                        except Exception:
                            pass

                except Exception as stage_error:
                    # Call error callback
                    if on_stage_error:
                        try:
                            await on_stage_error(stage.id, {"error": str(stage_error)})
                        except Exception:
                            pass
                    raise

            usage = executor.aggregate_usage(results)

            # Get final output
            output = {}
            if results:
                last_stage_id = self.definition.stages[-1].id
                if last_stage_id in results:
                    output = results[last_stage_id].output

            return PipelineResult(
                success=True,
                output=output,
                stage_results=results,
                usage=usage,
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                output={},
                stage_results={},
                usage=UsageMetrics(),
                error=str(e),
            )

    def validate(self) -> List[str]:
        """
        Validate the pipeline configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check all component types exist
        for stage in self.definition.stages:
            try:
                self.registry.get_component_metadata(stage.component_type)
            except Exception:
                errors.append(f"Unknown component type: {stage.component_type}")

        # Check dependencies
        stage_ids = {s.id for s in self.definition.stages}
        for stage in self.definition.stages:
            for dep in stage.depends_on:
                if dep not in stage_ids:
                    errors.append(f"Stage '{stage.id}' depends on unknown stage '{dep}'")

        return errors


class FlowMason:
    """
    FlowMason high-level API.

    This is the main entry point for using FlowMason programmatically.

    Example:
        fm = FlowMason()
        fm.load_packages("./packages")

        # Simple component execution
        result = await fm.run_component("generator", {"prompt": "Hello"})

        # Pipeline execution
        pipeline = fm.pipeline(
            name="My Pipeline",
            stages=[
                fm.stage("generator", config={"prompt": "Write about {topic}"}),
            ]
        )
        result = await pipeline.run({"topic": "AI"})
    """

    def __init__(
        self,
        providers: Optional[Dict[str, str]] = None,
        default_provider: Optional[str] = None,
        auto_load_env: bool = True,
    ):
        """
        Initialize FlowMason.

        Args:
            providers: Dict of provider_name -> api_key
            default_provider: Name of default provider for LLM operations
            auto_load_env: Auto-load API keys from environment variables
        """
        self.registry = ComponentRegistry()
        self._provider_keys: Dict[str, str] = {}
        self._provider_instances: Dict[str, Any] = {}
        self.default_provider = default_provider

        # Load from environment if requested
        if auto_load_env:
            for name, env_var in PROVIDER_ENV_VARS.items():
                key = os.environ.get(env_var)
                if key:
                    self._provider_keys[name] = key

        # Override with explicit providers
        if providers:
            self._provider_keys.update(providers)

        # Set default provider
        if not self.default_provider and self._provider_keys:
            self.default_provider = next(iter(self._provider_keys.keys()))

        # Initialize provider instances
        self._init_providers()

    def _init_providers(self) -> None:
        """Initialize provider instances from API keys."""
        for name in list_providers():
            if name in self._provider_keys:
                try:
                    ProviderClass = get_provider(name)
                    if ProviderClass is not None:
                        self._provider_instances[name] = ProviderClass(
                            api_key=self._provider_keys[name]
                        )
                except Exception:
                    pass  # Provider not available

    def load_packages(self, path: Union[str, Path]) -> int:
        """
        Load component packages from a directory.

        Args:
            path: Path to directory containing .fmpkg packages

        Returns:
            Number of packages loaded
        """
        path = Path(path)
        if not path.exists():
            return 0

        return self.registry.scan_packages(path)

    def load_package(self, path: Union[str, Path]) -> bool:
        """
        Load a single component package.

        Args:
            path: Path to .fmpkg package file

        Returns:
            True if loaded successfully
        """
        path = Path(path)
        if not path.exists():
            return False

        try:
            self.registry.register_package(path)
            return True
        except Exception:
            return False

    def list_components(self, category: Optional[str] = None) -> List[str]:
        """
        List available component types.

        Args:
            category: Optional category filter

        Returns:
            List of component type names
        """
        components = self.registry.list_components(category=category)
        return [c.component_type for c in components]

    def get_component_info(self, component_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a component.

        Args:
            component_type: The component type name

        Returns:
            Component metadata dict or None if not found
        """
        try:
            info = self.registry.get_component_metadata(component_type)
            return {
                "type": info.component_type,
                "kind": info.component_kind,
                "name": info.component_type,  # ComponentInfo uses component_type as identifier
                "description": info.description,
                "category": info.category,
                "requires_llm": info.requires_llm,
                "input_schema": info.input_schema,
                "output_schema": info.output_schema,
            }
        except Exception:
            return None

    def stage(
        self,
        component_type: str,
        id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        depends_on: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> StageDefinition:
        """
        Create a stage definition for a pipeline.

        Args:
            component_type: Type of component to use
            id: Stage ID (auto-generated if not provided)
            config: Component configuration / input mapping
            depends_on: List of stage IDs this depends on
            name: Display name for the stage

        Returns:
            StageDefinition for use in pipeline()
        """
        stage_id = id or f"{component_type}_{uuid.uuid4().hex[:8]}"
        return StageDefinition(
            id=stage_id,
            component_type=component_type,
            config=config or {},
            depends_on=depends_on or [],
            name=name,
        )

    def pipeline(
        self,
        name: str,
        stages: List[StageDefinition],
        description: str = "",
        version: str = "1.0.0",
    ) -> Pipeline:
        """
        Create an executable pipeline.

        Args:
            name: Pipeline name
            stages: List of stage definitions
            description: Pipeline description
            version: Pipeline version

        Returns:
            Pipeline object that can be run

        Example:
            pipeline = fm.pipeline(
                name="Content Review",
                stages=[
                    fm.stage("generator", config={"prompt": "Write about {topic}"}),
                    fm.stage("critic", depends_on=["generator_xxx"]),
                ]
            )
            result = await pipeline.run({"topic": "AI"})
        """
        definition = PipelineDefinition(
            name=name,
            description=description,
            stages=stages,
            version=version,
        )
        return Pipeline(
            definition=definition,
            registry=self.registry,
            providers=self._provider_instances,
            default_provider=self.default_provider,
        )

    async def run_component(
        self,
        component_type: str,
        config: Dict[str, Any],
        trace_id: Optional[str] = None,
    ) -> ComponentResult:
        """
        Run a single component directly.

        Args:
            component_type: Type of component to run
            config: Component input configuration
            trace_id: Optional trace ID

        Returns:
            ComponentResult with output and metrics

        Example:
            result = await fm.run_component(
                "generator",
                {"prompt": "Write a haiku about coding"}
            )
            print(result.output.content)
        """
        run_id = str(uuid.uuid4())

        context = ExecutionContext(
            run_id=run_id,
            pipeline_id="direct",
            pipeline_version="1.0.0",
            pipeline_input={},
            trace_id=trace_id or run_id,
            providers=self._provider_instances,
        )

        executor = DAGExecutor(
            registry=self.registry,
            context=context,
            providers=self._provider_instances,
            default_provider=self.default_provider,
        )

        stage = ComponentConfig(
            id="component",
            type=component_type,
            input_mapping=config,
            depends_on=[],
        )

        results = await executor.execute([stage], {})
        return results["component"]

    def load_pipeline(
        self,
        path: Union[str, Path],
    ) -> Pipeline:
        """
        Load a pipeline from a file.

        Args:
            path: Path to .pipeline.json file

        Returns:
            Pipeline object that can be run

        Example:
            pipeline = fm.load_pipeline("./pipelines/my-pipeline.pipeline.json")
            result = await pipeline.run({"topic": "AI"})
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Pipeline file not found: {path}")

        with open(path, "r") as f:
            data = json.load(f)

        # Convert to stage definitions
        stages = []
        for stage_data in data.get("stages", []):
            stages.append(StageDefinition(
                id=stage_data.get("id"),
                component_type=stage_data.get("component_type") or stage_data.get("component"),
                config=stage_data.get("config", {}),
                depends_on=stage_data.get("depends_on", []),
                name=stage_data.get("name"),
            ))

        definition = PipelineDefinition(
            name=data.get("name", path.stem),
            description=data.get("description", ""),
            stages=stages,
            version=data.get("version", "1.0.0"),
        )

        return Pipeline(
            definition=definition,
            registry=self.registry,
            providers=self._provider_instances,
            default_provider=self.default_provider,
        )

    async def run_pipeline_file(
        self,
        path: Union[str, Path],
        input: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        on_stage_start: Optional[AsyncStageCallback] = None,
        on_stage_complete: Optional[AsyncStageCallback] = None,
        on_stage_error: Optional[AsyncStageCallback] = None,
    ) -> PipelineResult:
        """
        Load and run a pipeline from a file in one step.

        Args:
            path: Path to .pipeline.json file
            input: Input data for the pipeline
            trace_id: Optional trace ID for observability
            on_stage_start: Async callback when stage starts
            on_stage_complete: Async callback when stage completes
            on_stage_error: Async callback when stage fails

        Returns:
            PipelineResult with output and metrics

        Example:
            result = await fm.run_pipeline_file(
                "./pipelines/my-pipeline.pipeline.json",
                {"query": "Hello"}
            )
            print(result.output)
        """
        pipeline = self.load_pipeline(path)
        return await pipeline.run(
            input=input,
            trace_id=trace_id,
            on_stage_start=on_stage_start,
            on_stage_complete=on_stage_complete,
            on_stage_error=on_stage_error,
        )

    async def run_from_studio(
        self,
        pipeline_id: str,
        input: Optional[Dict[str, Any]] = None,
        studio_url: str = "http://localhost:8999",
        trace_id: Optional[str] = None,
    ) -> PipelineResult:
        """
        Run a pipeline stored in FlowMason Studio.

        Args:
            pipeline_id: Pipeline ID in Studio
            input: Input data for the pipeline
            studio_url: URL of Studio API
            trace_id: Optional trace ID

        Returns:
            PipelineResult with output and metrics

        Example:
            result = await fm.run_from_studio(
                "pipeline-abc123",
                {"query": "Hello"},
                studio_url="http://localhost:8999"
            )
        """
        import aiohttp

        input = input or {}
        run_id = trace_id or str(uuid.uuid4())

        async with aiohttp.ClientSession() as session:
            # Start run
            async with session.post(
                f"{studio_url}/api/v1/runs/start/{pipeline_id}",
                json={"inputs": input, "trace_id": run_id},
            ) as resp:
                if resp.status != 200 and resp.status != 202:
                    error = await resp.text()
                    return PipelineResult(
                        success=False,
                        output={},
                        stage_results={},
                        usage=UsageMetrics(),
                        error=f"Failed to start run: {error}",
                    )
                run_data = await resp.json()
                run_id = run_data.get("id", run_id)

            # Poll for completion
            import asyncio
            max_attempts = 300  # 5 minutes with 1s interval
            for _ in range(max_attempts):
                async with session.get(f"{studio_url}/api/v1/runs/{run_id}") as resp:
                    if resp.status != 200:
                        await asyncio.sleep(1)
                        continue

                    run_status = await resp.json()
                    status = run_status.get("status")

                    if status == "completed":
                        return PipelineResult(
                            success=True,
                            output=run_status.get("output", {}),
                            stage_results={},
                            usage=UsageMetrics(),
                        )
                    elif status in ("failed", "cancelled"):
                        return PipelineResult(
                            success=False,
                            output={},
                            stage_results={},
                            usage=UsageMetrics(),
                            error=run_status.get("error", "Pipeline failed"),
                        )

                await asyncio.sleep(1)

            return PipelineResult(
                success=False,
                output={},
                stage_results={},
                usage=UsageMetrics(),
                error="Pipeline execution timed out",
            )

    def register_component(
        self,
        component_class: type,
    ) -> None:
        """
        Register a custom component class.

        Args:
            component_class: A class decorated with @node or @operator

        Example:
            from flowmason_core import node, NodeInput, NodeOutput

            @node(name="my_custom_node")
            class MyNode:
                class Input(NodeInput):
                    prompt: str

                class Output(NodeOutput):
                    result: str

                async def execute(self, input, context):
                    return self.Output(result=input.prompt.upper())

            fm.register_component(MyNode)
        """
        from flowmason_core.registry import MetadataExtractor

        try:
            extractor = MetadataExtractor()
            info = extractor.extract_from_class(component_class)
            # Note: Direct component registration not yet implemented in registry
            # Components should be packaged and registered via register_package
            raise NotImplementedError(
                "Direct component registration not yet implemented. "
                "Package your component and use load_packages() instead."
            )
        except NotImplementedError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to register component: {e}")

    @property
    def configured_providers(self) -> List[str]:
        """List of providers with configured API keys."""
        return list(self._provider_instances.keys())

    @property
    def available_providers(self) -> List[str]:
        """List of all available provider types."""
        return list_providers()

    async def __aenter__(self) -> "FlowMason":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        # Cleanup if needed
        pass
