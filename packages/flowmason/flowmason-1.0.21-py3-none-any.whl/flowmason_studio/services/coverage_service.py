"""
Coverage Collection Service for FlowMason Test Framework.

Collects and analyzes test coverage from execution results.
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from flowmason_core.execution.types import ComponentResult, DAGResult, UsageMetrics

from ..models.coverage import (
    CoverageSummary,
    ExecutionTimeMetrics,
    LLMMetrics,
    StageCoverageResult,
    StageDataMetrics,
    StageExecutionMetrics,
    StageExecutionStatus,
    TestCoverageResult,
    TestSuiteCoverageResult,
)


class CoverageCollector:
    """
    Collects coverage data from execution results.

    Transforms DAGResult and ComponentResult into comprehensive
    coverage reports.
    """

    # LLM node types - components that make LLM calls
    LLM_NODE_TYPES = {
        "generator", "critic", "improver", "selector", "synthesizer",
        "llm", "chat", "completion", "ai_node"
    }

    # Slow stage threshold (5 seconds)
    SLOW_THRESHOLD_MS = 5000

    def collect_from_dag_result(
        self,
        dag_result: DAGResult,
        pipeline_config: Optional[Dict[str, Any]] = None,
        test_input: Optional[Dict[str, Any]] = None,
        test_name: str = "unknown",
    ) -> TestCoverageResult:
        """
        Collect coverage from a DAGResult.

        Args:
            dag_result: Result from DAGExecutor.execute()
            pipeline_config: Original pipeline configuration (for stage metadata)
            test_input: Input data provided to the test
            test_name: Name of the test

        Returns:
            TestCoverageResult with complete coverage data
        """
        stage_results: Dict[str, StageCoverageResult] = {}
        execution_order: List[str] = []
        order_counter = 1

        # Build dependency map from pipeline config
        dependency_map: Dict[str, List[str]] = {}
        dependents_map: Dict[str, List[str]] = {}
        stage_names: Dict[str, str] = {}

        if pipeline_config and "stages" in pipeline_config:
            for stage in pipeline_config["stages"]:
                stage_id = stage.get("id", "")
                stage_names[stage_id] = stage.get("name", stage_id)
                deps = stage.get("depends_on", [])
                dependency_map[stage_id] = deps
                for dep in deps:
                    if dep not in dependents_map:
                        dependents_map[dep] = []
                    dependents_map[dep].append(stage_id)

        # Process each stage result
        for stage_id, component_result in dag_result.stage_results.items():
            execution_order.append(stage_id)

            # Build execution metrics
            execution = StageExecutionMetrics(
                stage_id=stage_id,
                stage_name=stage_names.get(stage_id, stage_id),
                component_type=component_result.component_type,
                execution_order=order_counter,
                status=self._map_status(component_result.status),
                depends_on=dependency_map.get(stage_id, []),
                dependents=dependents_map.get(stage_id, []),
            )
            order_counter += 1

            # Build data metrics
            data = self._build_data_metrics(component_result)

            # Build timing metrics
            timing = self._build_timing_metrics(component_result)

            # Build LLM metrics if applicable
            llm = None
            if component_result.component_type.lower() in self.LLM_NODE_TYPES:
                llm = self._build_llm_metrics(component_result)

            stage_results[stage_id] = StageCoverageResult(
                execution=execution,
                data=data,
                timing=timing,
                llm=llm,
            )

        # Add stages that weren't executed (if pipeline_config provided)
        if pipeline_config and "stages" in pipeline_config:
            for stage in pipeline_config["stages"]:
                stage_id = stage.get("id", "")
                if stage_id not in stage_results:
                    execution = StageExecutionMetrics(
                        stage_id=stage_id,
                        stage_name=stage_names.get(stage_id, stage_id),
                        component_type=stage.get("component_type", "unknown"),
                        status=StageExecutionStatus.NOT_REACHED,
                        depends_on=dependency_map.get(stage_id, []),
                        dependents=dependents_map.get(stage_id, []),
                    )
                    stage_results[stage_id] = StageCoverageResult(
                        execution=execution,
                        data=StageDataMetrics(),
                        timing=ExecutionTimeMetrics(),
                    )

        # Build summary
        summary = self._build_summary(stage_results, dag_result)

        # Determine overall status
        overall_status = "passed" if dag_result.status == "success" else "failed"
        if dag_result.error:
            overall_status = "error"

        return TestCoverageResult(
            test_name=test_name,
            pipeline_id=dag_result.pipeline_id,
            overall_status=overall_status,
            overall_duration_ms=int(
                (dag_result.completed_at - dag_result.started_at).total_seconds() * 1000
            ) if dag_result.started_at and dag_result.completed_at else 0,
            stage_results=stage_results,
            execution_order=execution_order,
            summary=summary,
            test_input=test_input,
            final_output=dag_result.final_output,
            error=dag_result.error,
            executed_at=datetime.utcnow(),
        )

    def collect_from_component_result(
        self,
        component_result: ComponentResult,
        test_input: Optional[Dict[str, Any]] = None,
        test_name: str = "unknown",
    ) -> TestCoverageResult:
        """
        Collect coverage from a single ComponentResult.

        Args:
            component_result: Result from component execution
            test_input: Input data provided to the test
            test_name: Name of the test

        Returns:
            TestCoverageResult with coverage data for single component
        """
        stage_id = component_result.component_id

        # Build metrics
        execution = StageExecutionMetrics(
            stage_id=stage_id,
            component_type=component_result.component_type,
            execution_order=1,
            status=self._map_status(component_result.status),
        )

        data = self._build_data_metrics(component_result)
        timing = self._build_timing_metrics(component_result)

        llm = None
        if component_result.component_type.lower() in self.LLM_NODE_TYPES:
            llm = self._build_llm_metrics(component_result)

        stage_results = {
            stage_id: StageCoverageResult(
                execution=execution,
                data=data,
                timing=timing,
                llm=llm,
            )
        }

        # Build summary
        summary = CoverageSummary(
            total_stages=1,
            stages_executed=1 if component_result.status == "success" else 0,
            stages_failed=1 if component_result.status != "success" else 0,
            coverage_percentage=100.0 if component_result.status == "success" else 0.0,
            total_duration_ms=timing.duration_ms,
        )

        if llm:
            summary.total_llm_calls = 1
            summary.total_input_tokens = llm.input_tokens
            summary.total_output_tokens = llm.output_tokens
            summary.total_llm_cost_usd = llm.cost_usd

        overall_status = "passed" if component_result.status == "success" else "failed"
        if component_result.error:
            overall_status = "error"

        return TestCoverageResult(
            test_name=test_name,
            component_type=component_result.component_type,
            overall_status=overall_status,
            overall_duration_ms=timing.duration_ms,
            stage_results=stage_results,
            execution_order=[stage_id],
            summary=summary,
            test_input=test_input,
            final_output=component_result.output,
            error=component_result.error,
            executed_at=datetime.utcnow(),
        )

    def _map_status(self, status: str) -> StageExecutionStatus:
        """Map component status to execution status."""
        status_lower = status.lower()
        if status_lower in ("success", "completed", "passed"):
            return StageExecutionStatus.EXECUTED
        elif status_lower in ("failed", "error"):
            return StageExecutionStatus.FAILED
        elif status_lower in ("skipped", "skip"):
            return StageExecutionStatus.SKIPPED
        else:
            return StageExecutionStatus.NOT_REACHED

    def _build_data_metrics(self, result: ComponentResult) -> StageDataMetrics:
        """Build data metrics from component result."""
        output_data = None
        output_size = 0
        output_keys: List[str] = []

        if result.output is not None:
            if isinstance(result.output, dict):
                output_data = result.output
                output_keys = list(result.output.keys())
                try:
                    output_size = len(json.dumps(result.output))
                except Exception:
                    output_size = sys.getsizeof(result.output)
            else:
                output_data = {"value": result.output}
                output_keys = ["value"]
                try:
                    output_size = len(str(result.output))
                except Exception:
                    output_size = 0

        return StageDataMetrics(
            output_data=output_data,
            output_size_bytes=output_size,
            output_keys=output_keys,
            error_message=result.error,
            error_type=None,  # Could be enhanced to extract error type
        )

    def _build_timing_metrics(self, result: ComponentResult) -> ExecutionTimeMetrics:
        """Build timing metrics from component result."""
        duration_ms = 0
        if result.started_at and result.completed_at:
            duration_ms = int((result.completed_at - result.started_at).total_seconds() * 1000)
        elif result.usage:
            duration_ms = result.usage.duration_ms

        return ExecutionTimeMetrics(
            started_at=result.started_at,
            completed_at=result.completed_at,
            duration_ms=duration_ms,
            is_slow=duration_ms > self.SLOW_THRESHOLD_MS,
            slow_threshold_ms=self.SLOW_THRESHOLD_MS if duration_ms > self.SLOW_THRESHOLD_MS else None,
        )

    def _build_llm_metrics(self, result: ComponentResult) -> LLMMetrics:
        """Build LLM metrics from component result."""
        usage = result.usage or UsageMetrics()

        return LLMMetrics(
            is_llm_node=True,
            provider=usage.provider,
            model=usage.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens or (usage.input_tokens + usage.output_tokens),
            cost_usd=usage.cost_usd,
        )

    def _build_summary(
        self,
        stage_results: Dict[str, StageCoverageResult],
        dag_result: DAGResult,
    ) -> CoverageSummary:
        """Build coverage summary from stage results."""
        total = len(stage_results)
        executed = sum(
            1 for s in stage_results.values()
            if s.execution.status == StageExecutionStatus.EXECUTED
        )
        failed = sum(
            1 for s in stage_results.values()
            if s.execution.status == StageExecutionStatus.FAILED
        )
        skipped = sum(
            1 for s in stage_results.values()
            if s.execution.status == StageExecutionStatus.SKIPPED
        )
        not_reached = sum(
            1 for s in stage_results.values()
            if s.execution.status == StageExecutionStatus.NOT_REACHED
        )

        # Find slowest stage
        slowest_id = None
        slowest_ms = 0
        for stage_id, result in stage_results.items():
            if result.timing.duration_ms > slowest_ms:
                slowest_ms = result.timing.duration_ms
                slowest_id = stage_id

        # Aggregate LLM usage
        llm_calls = 0
        input_tokens = 0
        output_tokens = 0
        llm_cost = 0.0

        for result in stage_results.values():
            if result.llm and result.llm.is_llm_node:
                llm_calls += 1
                input_tokens += result.llm.input_tokens
                output_tokens += result.llm.output_tokens
                llm_cost += result.llm.cost_usd

        # Use DAG-level aggregated values if available
        if dag_result.usage:
            input_tokens = dag_result.usage.input_tokens or input_tokens
            output_tokens = dag_result.usage.output_tokens or output_tokens
            llm_cost = dag_result.usage.cost_usd or llm_cost

        total_duration = int(
            (dag_result.completed_at - dag_result.started_at).total_seconds() * 1000
        ) if dag_result.started_at and dag_result.completed_at else 0

        coverage_pct = (executed / total * 100) if total > 0 else 0.0

        return CoverageSummary(
            total_stages=total,
            stages_executed=executed,
            stages_failed=failed,
            stages_skipped=skipped,
            stages_not_reached=not_reached,
            coverage_percentage=coverage_pct,
            total_duration_ms=total_duration,
            slowest_stage_id=slowest_id,
            slowest_stage_ms=slowest_ms if slowest_ms > 0 else None,
            total_llm_calls=llm_calls,
            total_input_tokens=input_tokens,
            total_output_tokens=output_tokens,
            total_llm_cost_usd=llm_cost,
        )


class CoverageAggregator:
    """
    Aggregates coverage results from multiple tests.
    """

    def aggregate(
        self,
        test_results: List[TestCoverageResult],
        suite_name: str,
        test_file: str,
    ) -> TestSuiteCoverageResult:
        """
        Aggregate multiple test coverage results into a suite result.

        Args:
            test_results: List of individual test coverage results
            suite_name: Name of the test suite
            test_file: Path to the test file

        Returns:
            TestSuiteCoverageResult with aggregated metrics
        """
        # Count test statuses
        passed = sum(1 for r in test_results if r.overall_status == "passed")
        failed = sum(1 for r in test_results if r.overall_status == "failed")
        skipped = sum(1 for r in test_results if r.overall_status == "skipped")
        error = sum(1 for r in test_results if r.overall_status == "error")

        # Determine overall status
        if error > 0:
            overall_status = "error"
        elif failed > 0:
            overall_status = "failed"
        else:
            overall_status = "passed"

        # Aggregate duration
        total_duration = sum(r.overall_duration_ms for r in test_results)

        # Aggregate LLM usage
        total_llm_calls = sum(r.summary.total_llm_calls for r in test_results)
        total_input_tokens = sum(r.summary.total_input_tokens for r in test_results)
        total_output_tokens = sum(r.summary.total_output_tokens for r in test_results)
        total_llm_cost = sum(r.summary.total_llm_cost_usd for r in test_results)

        # Aggregate stage metrics
        total_stages = sum(r.summary.total_stages for r in test_results)
        stages_executed = sum(r.summary.stages_executed for r in test_results)
        stages_failed = sum(r.summary.stages_failed for r in test_results)
        stages_skipped = sum(r.summary.stages_skipped for r in test_results)
        stages_not_reached = sum(r.summary.stages_not_reached for r in test_results)

        coverage_pct = (stages_executed / total_stages * 100) if total_stages > 0 else 0.0

        aggregated_summary = CoverageSummary(
            total_stages=total_stages,
            stages_executed=stages_executed,
            stages_failed=stages_failed,
            stages_skipped=stages_skipped,
            stages_not_reached=stages_not_reached,
            coverage_percentage=coverage_pct,
            total_duration_ms=total_duration,
            total_llm_calls=total_llm_calls,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_llm_cost_usd=total_llm_cost,
        )

        return TestSuiteCoverageResult(
            suite_name=suite_name,
            test_file=test_file,
            overall_status=overall_status,
            overall_duration_ms=total_duration,
            test_results=test_results,
            tests_total=len(test_results),
            tests_passed=passed,
            tests_failed=failed,
            tests_skipped=skipped,
            tests_error=error,
            aggregated_summary=aggregated_summary,
            total_llm_calls=total_llm_calls,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_llm_cost_usd=total_llm_cost,
            executed_at=datetime.utcnow(),
        )
