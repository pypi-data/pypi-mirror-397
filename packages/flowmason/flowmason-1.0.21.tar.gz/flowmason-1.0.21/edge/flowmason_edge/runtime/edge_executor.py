"""
Edge Executor for FlowMason Edge.

Lightweight pipeline executor optimized for resource-constrained environments.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    """Status of an execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StageResult:
    """Result of a stage execution."""
    stage_id: str
    status: ExecutionStatus
    output: Any
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0


@dataclass
class ExecutionResult:
    """Result of a pipeline execution."""
    run_id: str
    pipeline_name: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: int
    stages: Dict[str, StageResult]
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EdgeExecutor:
    """
    Lightweight pipeline executor for edge devices.

    Optimized for:
    - Minimal memory footprint
    - Offline execution
    - Local LLM integration
    - Resource-constrained environments

    Example:
        executor = EdgeExecutor(
            llm_adapter=OllamaAdapter("llama2"),
            max_concurrent=2,
        )

        result = await executor.execute(pipeline_config, inputs)
    """

    def __init__(
        self,
        llm_adapter=None,
        max_concurrent: int = 2,
        timeout_seconds: int = 300,
        progress_callback: Optional[Callable] = None,
    ):
        """
        Initialize the edge executor.

        Args:
            llm_adapter: Local LLM adapter (Ollama, llama.cpp, etc.)
            max_concurrent: Maximum concurrent stage executions
            timeout_seconds: Default timeout for executions
            progress_callback: Callback for progress updates
        """
        self.llm_adapter = llm_adapter
        self.max_concurrent = max_concurrent
        self.timeout_seconds = timeout_seconds
        self.progress_callback = progress_callback

        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._running: Dict[str, asyncio.Task] = {}
        self._cancelled: set = set()

    async def execute(
        self,
        pipeline: Dict[str, Any],
        inputs: Dict[str, Any],
        run_id: Optional[str] = None,
    ) -> ExecutionResult:
        """
        Execute a pipeline.

        Args:
            pipeline: Pipeline configuration
            inputs: Input data
            run_id: Optional run identifier

        Returns:
            ExecutionResult
        """
        import uuid

        run_id = run_id or str(uuid.uuid4())
        pipeline_name = pipeline.get("name", "unknown")
        started_at = datetime.utcnow()

        logger.info(f"Starting execution: {run_id} for pipeline {pipeline_name}")

        stage_results: Dict[str, StageResult] = {}
        context = {"inputs": inputs, "outputs": {}}

        try:
            # Build execution order from stages
            stages = pipeline.get("stages", [])
            execution_order = self._build_execution_order(stages)

            # Execute stages in order
            for stage_batch in execution_order:
                if run_id in self._cancelled:
                    raise asyncio.CancelledError("Execution cancelled")

                # Execute batch concurrently
                batch_tasks = []
                for stage in stage_batch:
                    task = self._execute_stage(stage, context, run_id)
                    batch_tasks.append(task)

                results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                # Process results
                for stage, result in zip(stage_batch, results):
                    stage_id = stage.get("id", "unknown")

                    if isinstance(result, Exception):
                        stage_results[stage_id] = StageResult(
                            stage_id=stage_id,
                            status=ExecutionStatus.FAILED,
                            output=None,
                            error=str(result),
                        )
                        raise result
                    else:
                        stage_results[stage_id] = result
                        context["outputs"][stage_id] = result.output

            # Determine final output
            final_output = self._get_final_output(stages, context)

            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            return ExecutionResult(
                run_id=run_id,
                pipeline_name=pipeline_name,
                status=ExecutionStatus.COMPLETED,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                stages=stage_results,
                output=final_output,
            )

        except asyncio.CancelledError:
            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            return ExecutionResult(
                run_id=run_id,
                pipeline_name=pipeline_name,
                status=ExecutionStatus.CANCELLED,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                stages=stage_results,
                output=None,
                error="Execution cancelled",
            )

        except Exception as e:
            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            logger.error(f"Execution failed: {run_id} - {e}")

            return ExecutionResult(
                run_id=run_id,
                pipeline_name=pipeline_name,
                status=ExecutionStatus.FAILED,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                stages=stage_results,
                output=None,
                error=str(e),
            )

    async def _execute_stage(
        self,
        stage: Dict[str, Any],
        context: Dict[str, Any],
        run_id: str,
    ) -> StageResult:
        """Execute a single stage."""
        stage_id = stage.get("id", "unknown")
        component_type = stage.get("component_type", "")
        config = stage.get("config", {})

        started_at = datetime.utcnow()

        async with self._semaphore:
            try:
                # Report progress
                if self.progress_callback:
                    self.progress_callback(run_id, stage_id, "started", 0)

                # Resolve inputs
                inputs = self._resolve_inputs(stage, context)

                # Execute based on component type
                output = await self._run_component(
                    component_type, config, inputs, context
                )

                completed_at = datetime.utcnow()
                duration_ms = int((completed_at - started_at).total_seconds() * 1000)

                # Report progress
                if self.progress_callback:
                    self.progress_callback(run_id, stage_id, "completed", 100)

                return StageResult(
                    stage_id=stage_id,
                    status=ExecutionStatus.COMPLETED,
                    output=output,
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_ms=duration_ms,
                )

            except Exception as e:
                completed_at = datetime.utcnow()
                duration_ms = int((completed_at - started_at).total_seconds() * 1000)

                logger.error(f"Stage {stage_id} failed: {e}")

                if self.progress_callback:
                    self.progress_callback(run_id, stage_id, "failed", 0)

                return StageResult(
                    stage_id=stage_id,
                    status=ExecutionStatus.FAILED,
                    output=None,
                    error=str(e),
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_ms=duration_ms,
                )

    async def _run_component(
        self,
        component_type: str,
        config: Dict[str, Any],
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Any:
        """Run a component by type."""
        # Built-in lightweight components
        if component_type == "generator":
            return await self._run_generator(config, inputs)
        elif component_type == "json_transform":
            return self._run_json_transform(config, inputs)
        elif component_type == "filter":
            return self._run_filter(config, inputs)
        elif component_type == "logger":
            return self._run_logger(config, inputs)
        elif component_type == "variable_set":
            return self._run_variable_set(config, inputs)
        elif component_type == "schema_validate":
            return self._run_schema_validate(config, inputs)
        else:
            raise ValueError(f"Unknown component type: {component_type}")

    async def _run_generator(
        self,
        config: Dict[str, Any],
        inputs: Dict[str, Any],
    ) -> Any:
        """Run generator component using local LLM."""
        if not self.llm_adapter:
            raise RuntimeError("No LLM adapter configured for generator")

        from flowmason_edge.adapters.base import GenerationConfig

        prompt = config.get("prompt", "")
        system_prompt = config.get("system_prompt")

        # Resolve template variables
        prompt = self._resolve_template(prompt, inputs)
        if system_prompt:
            system_prompt = self._resolve_template(system_prompt, inputs)

        gen_config = GenerationConfig(
            max_tokens=config.get("max_tokens", 512),
            temperature=config.get("temperature", 0.7),
            top_p=config.get("top_p", 0.9),
        )

        result = await self.llm_adapter.generate(
            prompt=prompt,
            config=gen_config,
            system_prompt=system_prompt,
        )

        return {"text": result.text, "tokens": result.tokens_generated}

    def _run_json_transform(
        self,
        config: Dict[str, Any],
        inputs: Dict[str, Any],
    ) -> Any:
        """Run JSON transform component."""
        mapping = config.get("mapping", {})
        source = inputs.get("source", inputs)

        result = {}
        for target_key, source_path in mapping.items():
            value = self._get_nested_value(source, source_path)
            self._set_nested_value(result, target_key, value)

        return result

    def _run_filter(
        self,
        config: Dict[str, Any],
        inputs: Dict[str, Any],
    ) -> Any:
        """Run filter component."""
        condition = config.get("condition", "")
        items = inputs.get("items", [])

        if not condition:
            return items

        # Simple expression evaluation
        filtered = []
        for item in items:
            try:
                # Safe evaluation context
                eval_context = {"item": item, **inputs}
                if eval(condition, {"__builtins__": {}}, eval_context):
                    filtered.append(item)
            except Exception:
                pass

        return filtered

    def _run_logger(
        self,
        config: Dict[str, Any],
        inputs: Dict[str, Any],
    ) -> Any:
        """Run logger component."""
        message = config.get("message", "")
        level = config.get("level", "info")

        message = self._resolve_template(message, inputs)

        log_func = getattr(logger, level, logger.info)
        log_func(f"[Pipeline] {message}")

        return {"logged": message}

    def _run_variable_set(
        self,
        config: Dict[str, Any],
        inputs: Dict[str, Any],
    ) -> Any:
        """Run variable_set component."""
        variables = config.get("variables", {})
        result = {}

        for name, value in variables.items():
            if isinstance(value, str):
                result[name] = self._resolve_template(value, inputs)
            else:
                result[name] = value

        return result

    def _run_schema_validate(
        self,
        config: Dict[str, Any],
        inputs: Dict[str, Any],
    ) -> Any:
        """Run schema validation component."""
        schema = config.get("schema", {})
        data = inputs.get("data", inputs)

        try:
            import jsonschema
            jsonschema.validate(data, schema)
            return {"valid": True, "data": data}
        except ImportError:
            logger.warning("jsonschema not installed, skipping validation")
            return {"valid": True, "data": data, "skipped": True}
        except jsonschema.ValidationError as e:
            return {"valid": False, "error": str(e)}

    def _resolve_inputs(
        self,
        stage: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve stage inputs from context."""
        input_mapping = stage.get("inputs", {})
        resolved = {}

        for input_name, source in input_mapping.items():
            if isinstance(source, str):
                if source.startswith("$inputs."):
                    key = source[8:]
                    resolved[input_name] = self._get_nested_value(
                        context["inputs"], key
                    )
                elif source.startswith("$"):
                    # Reference to another stage output
                    parts = source[1:].split(".")
                    stage_id = parts[0]
                    if stage_id in context["outputs"]:
                        value = context["outputs"][stage_id]
                        for part in parts[1:]:
                            if isinstance(value, dict):
                                value = value.get(part)
                        resolved[input_name] = value
                else:
                    resolved[input_name] = source
            else:
                resolved[input_name] = source

        # If no explicit mapping, pass through inputs
        if not resolved:
            resolved = context.get("inputs", {}).copy()

        return resolved

    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """Resolve template variables."""
        import re

        def replace_var(match):
            var_path = match.group(1)
            value = self._get_nested_value(context, var_path)
            return str(value) if value is not None else match.group(0)

        return re.sub(r'\{\{(\w+(?:\.\w+)*)\}\}', replace_var, template)

    def _get_nested_value(self, data: Any, path: str) -> Any:
        """Get nested value from dict using dot notation."""
        if not path:
            return data

        parts = path.split(".")
        value = data

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list) and part.isdigit():
                value = value[int(part)] if int(part) < len(value) else None
            else:
                return None

        return value

    def _set_nested_value(self, data: Dict, path: str, value: Any) -> None:
        """Set nested value in dict using dot notation."""
        parts = path.split(".")

        for part in parts[:-1]:
            if part not in data:
                data[part] = {}
            data = data[part]

        data[parts[-1]] = value

    def _build_execution_order(
        self,
        stages: List[Dict[str, Any]],
    ) -> List[List[Dict[str, Any]]]:
        """Build execution order respecting dependencies."""
        # Simple topological sort
        # For now, sequential execution
        return [[stage] for stage in stages]

    def _get_final_output(
        self,
        stages: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Any:
        """Get final output from the last stage."""
        if not stages:
            return context.get("inputs")

        last_stage = stages[-1]
        stage_id = last_stage.get("id", "unknown")

        return context["outputs"].get(stage_id)

    def cancel(self, run_id: str) -> bool:
        """Cancel a running execution."""
        self._cancelled.add(run_id)

        if run_id in self._running:
            self._running[run_id].cancel()
            return True

        return False
