"""
FlowMason Test Execution Routes

API endpoints for running FlowMason tests from .test.json files.
Includes coverage reporting for stage-level metrics.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from flowmason_studio.models.coverage import (
    TestCoverageResult,
    TestSuiteCoverageResult,
)
from flowmason_studio.services.coverage_service import CoverageAggregator, CoverageCollector

from .registry import get_registry

router = APIRouter(prefix="/tests", tags=["tests"])

# Coverage collection services
coverage_collector = CoverageCollector()
coverage_aggregator = CoverageAggregator()


# Request/Response Models


class TestAssertion(BaseModel):
    """Assertion to validate test output"""
    path: str
    type: str = "exists"
    value: Optional[Any] = None
    expected_type: Optional[str] = None
    less_than: Optional[float] = None
    greater_than: Optional[float] = None
    message: Optional[str] = None


class TestCase(BaseModel):
    """Individual test case"""
    name: str
    description: Optional[str] = None
    input: Dict[str, Any]
    assertions: Optional[List[TestAssertion]] = None
    expect_error: Optional[Any] = None
    timeout: Optional[int] = None
    tags: Optional[List[str]] = None
    skip: bool = False
    only: bool = False


class TestFile(BaseModel):
    """Test file format"""
    name: str
    description: Optional[str] = None
    pipeline: Optional[str] = None
    component: Optional[str] = None
    component_type: Optional[str] = None
    timeout: int = 30000
    setup: Optional[Dict[str, Any]] = None
    tests: List[TestCase]


class TestRunRequest(BaseModel):
    """Request to run tests"""
    test_file: str
    pipeline_path: Optional[str] = None
    component_type: Optional[str] = None
    test_names: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None


class AssertionResult(BaseModel):
    """Result of a single assertion"""
    path: str
    passed: bool
    message: Optional[str] = None
    expected: Optional[Any] = None
    actual: Optional[Any] = None


class TestResult(BaseModel):
    """Result of a single test"""
    name: str
    status: str  # passed, failed, skipped, error
    duration: Optional[int] = None  # milliseconds
    error: Optional[str] = None
    stack: Optional[str] = None
    assertions: Optional[List[AssertionResult]] = None
    output: Optional[Any] = None
    # Coverage data (optional, included when include_coverage=True)
    coverage: Optional[TestCoverageResult] = None


class TestSuiteResult(BaseModel):
    """Result of a test suite"""
    name: str
    file: str
    status: str  # passed, failed, error
    duration: Optional[int] = None
    tests: List[TestResult]
    summary: Dict[str, int]
    # Coverage data (optional, included when include_coverage=True)
    coverage: Optional[TestSuiteCoverageResult] = None


# Helper Functions


def get_value_at_path(obj: Any, path: str) -> Any:
    """Get value at a JSONPath-like path"""
    parts = path.split(".")
    current = obj
    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Path '{path}' not found at '{part}'")
            current = current[part]
        elif isinstance(current, list):
            try:
                index = int(part)
                current = current[index]
            except (ValueError, IndexError):
                raise KeyError(f"Invalid list index '{part}' in path '{path}'")
        else:
            raise KeyError(f"Cannot traverse '{part}' in path '{path}'")
    return current


def evaluate_assertion(assertion: TestAssertion, output: Any) -> AssertionResult:
    """Evaluate a single assertion against output"""
    try:
        actual = get_value_at_path(output, assertion.path)
        passed = True
        message = None
        expected = None

        assertion_type = assertion.type or "exists"

        if assertion_type == "exists":
            passed = actual is not None

        elif assertion_type == "notExists":
            passed = actual is None

        elif assertion_type == "equals":
            expected = assertion.value
            passed = actual == expected

        elif assertion_type == "notEquals":
            expected = assertion.value
            passed = actual != expected

        elif assertion_type == "contains":
            expected = assertion.value
            if isinstance(actual, str):
                passed = str(assertion.value) in actual
            elif isinstance(actual, (list, dict)):
                passed = assertion.value in actual
            else:
                passed = False
                message = f"Cannot check 'contains' on type {type(actual).__name__}"

        elif assertion_type == "notContains":
            expected = assertion.value
            if isinstance(actual, str):
                passed = str(assertion.value) not in actual
            elif isinstance(actual, (list, dict)):
                passed = assertion.value not in actual
            else:
                passed = False
                message = f"Cannot check 'notContains' on type {type(actual).__name__}"

        elif assertion_type == "matches":
            import re
            expected = assertion.value
            if isinstance(actual, str) and isinstance(assertion.value, str):
                passed = bool(re.search(assertion.value, actual))
            else:
                passed = False
                message = "Both actual and pattern must be strings for 'matches'"

        elif assertion_type == "type":
            expected = assertion.expected_type
            type_map: Dict[str, type | tuple[type, ...]] = {
                "string": str,
                "number": (int, float),
                "boolean": bool,
                "object": dict,
                "array": list,
                "null": type(None),
            }
            expected_python_type = type_map.get(assertion.expected_type or "")
            if expected_python_type:
                passed = isinstance(actual, expected_python_type)  # type: ignore[arg-type]
            else:
                passed = False
                message = f"Unknown type: {assertion.expected_type}"

        elif assertion_type == "lessThan":
            expected = assertion.less_than or assertion.value
            if isinstance(actual, (int, float)) and expected is not None:
                passed = actual < expected
            else:
                passed = False
                message = "Value must be numeric for 'lessThan'"

        elif assertion_type == "greaterThan":
            expected = assertion.greater_than or assertion.value
            if isinstance(actual, (int, float)) and expected is not None:
                passed = actual > expected
            else:
                passed = False
                message = "Value must be numeric for 'greaterThan'"

        elif assertion_type == "lengthEquals":
            expected = assertion.value
            if hasattr(actual, "__len__"):
                passed = len(actual) == expected
            else:
                passed = False
                message = "Value must have length for 'lengthEquals'"

        elif assertion_type == "lengthLessThan":
            expected = assertion.value
            if hasattr(actual, "__len__") and expected is not None:
                passed = len(actual) < expected
            else:
                passed = False
                message = "Value must have length for 'lengthLessThan'"

        elif assertion_type == "lengthGreaterThan":
            expected = assertion.value
            if hasattr(actual, "__len__") and expected is not None:
                passed = len(actual) > expected
            else:
                passed = False
                message = "Value must have length for 'lengthGreaterThan'"

        else:
            passed = False
            message = f"Unknown assertion type: {assertion_type}"

        return AssertionResult(
            path=assertion.path,
            passed=passed,
            message=assertion.message or message,
            expected=expected,
            actual=actual,
        )

    except KeyError as e:
        return AssertionResult(
            path=assertion.path,
            passed=False,
            message=str(e),
            expected=None,
            actual=None,
        )
    except Exception as e:
        return AssertionResult(
            path=assertion.path,
            passed=False,
            message=f"Assertion error: {str(e)}",
            expected=None,
            actual=None,
        )


async def run_single_test(
    test: TestCase,
    pipeline_path: Optional[str],
    component_type: Optional[str],
    env: Optional[Dict[str, str]],
    registry: Any,
    include_coverage: bool = False,
) -> TestResult:
    """Run a single test case with optional coverage collection"""
    start_time = datetime.now()

    if test.skip:
        return TestResult(
            name=test.name,
            status="skipped",
            duration=0,
        )

    try:
        # Execute pipeline or component
        output = None
        error_occurred = False
        error_message = None
        dag_result = None
        component_result = None
        pipeline_config = None

        if pipeline_path:
            # Load and execute pipeline
            from flowmason_core.execution import DAGExecutor
            from flowmason_core.project.loader import PipelineLoader  # type: ignore[attr-defined]

            pipeline_def = PipelineLoader.load(pipeline_path)  # type: ignore[attr-defined]

            # Store pipeline config for coverage if needed
            if include_coverage:
                pipeline_config = pipeline_def if isinstance(pipeline_def, dict) else pipeline_def.model_dump() if hasattr(pipeline_def, 'model_dump') else None

            # Apply environment variables if any
            if env:
                import os
                for key, value in env.items():
                    os.environ[key] = value

            # Execute pipeline
            executor = DAGExecutor()  # type: ignore[call-arg]
            dag_result = await executor.execute(  # type: ignore[call-arg]
                pipeline_def,
                test.input,
                run_id=f"test-{test.name}",
                timeout=test.timeout or 30000,
            )

            # Extract output - handle both DAGResult and raw dict
            if hasattr(dag_result, 'final_output'):
                output = dag_result.final_output
            elif hasattr(dag_result, 'output'):
                output = dag_result.output
            else:
                output = dag_result

        elif component_type:
            # Execute single component
            from flowmason_core.execution import UniversalExecutor

            component_info = registry.get_component(component_type)
            if not component_info:
                raise ValueError(f"Component not found: {component_type}")

            executor = UniversalExecutor()  # type: ignore[call-arg, assignment]
            component_result = await executor.execute(  # type: ignore[call-arg]
                component_info.component_class,
                test.input,
                None,  # context
                run_id=f"test-{test.name}",
            )

            output = component_result.output if hasattr(component_result, "output") else component_result
        else:
            raise ValueError("Either pipeline_path or component_type must be provided")

    except Exception as e:
        error_occurred = True
        error_message = str(e)
        import traceback
        stack = traceback.format_exc()

    duration = int((datetime.now() - start_time).total_seconds() * 1000)

    # Collect coverage if requested
    coverage_result = None
    if include_coverage and not error_occurred:
        try:
            if dag_result and hasattr(dag_result, 'stage_results'):
                coverage_result = coverage_collector.collect_from_dag_result(
                    dag_result,  # type: ignore[arg-type]
                    pipeline_config=pipeline_config,
                    test_input=test.input,
                    test_name=test.name,
                )
            elif component_result and hasattr(component_result, 'component_id'):
                coverage_result = coverage_collector.collect_from_component_result(
                    component_result,  # type: ignore[arg-type]
                    test_input=test.input,
                    test_name=test.name,
                )
        except Exception as cov_err:
            # Coverage collection failed - log but don't fail the test
            print(f"Coverage collection failed for {test.name}: {cov_err}")

    # Check if error was expected
    if test.expect_error:
        if error_occurred:
            if isinstance(test.expect_error, bool) and test.expect_error:
                return TestResult(
                    name=test.name,
                    status="passed",
                    duration=duration,
                    output={"error": error_message},
                    coverage=coverage_result,
                )
            elif isinstance(test.expect_error, str) and test.expect_error in (error_message or ""):
                return TestResult(
                    name=test.name,
                    status="passed",
                    duration=duration,
                    output={"error": error_message},
                    coverage=coverage_result,
                )
            else:
                return TestResult(
                    name=test.name,
                    status="failed",
                    duration=duration,
                    error=f"Expected error '{test.expect_error}' but got '{error_message}'",
                    coverage=coverage_result,
                )
        else:
            return TestResult(
                name=test.name,
                status="failed",
                duration=duration,
                error="Expected error but test passed",
                output=output,
                coverage=coverage_result,
            )

    # If error occurred but not expected
    if error_occurred:
        return TestResult(
            name=test.name,
            status="error",
            duration=duration,
            error=error_message,
            stack=stack,
            coverage=coverage_result,
        )

    # Evaluate assertions
    assertion_results = []
    all_passed = True

    if test.assertions:
        for assertion in test.assertions:
            result = evaluate_assertion(assertion, output)
            assertion_results.append(result)
            if not result.passed:
                all_passed = False

    return TestResult(
        name=test.name,
        status="passed" if all_passed else "failed",
        duration=duration,
        assertions=assertion_results if assertion_results else None,
        output=output,
        coverage=coverage_result,
    )


# API Routes


@router.post("/run")
async def run_tests(
    request: TestRunRequest,
    include_coverage: bool = Query(default=False, description="Include stage-level coverage metrics"),
    registry: Any = Depends(get_registry),
) -> TestSuiteResult:
    """
    Run tests from a test file.

    Args:
        request: Test run request with file path and options
        include_coverage: If True, include detailed stage-level coverage metrics
        registry: Component registry (injected)

    Returns:
        TestSuiteResult with test results and optional coverage data
    """
    start_time = datetime.now()

    # Load test file
    test_file_path = Path(request.test_file)
    if not test_file_path.exists():
        raise HTTPException(status_code=404, detail=f"Test file not found: {request.test_file}")

    try:
        with open(test_file_path, "r") as f:
            test_file_data = json.load(f)
        test_file = TestFile(**test_file_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid test file: {str(e)}")

    # Determine which tests to run
    tests_to_run = test_file.tests

    # Filter by test names if specified
    if request.test_names:
        tests_to_run = [t for t in tests_to_run if t.name in request.test_names]

    # Check for 'only' tests
    only_tests = [t for t in tests_to_run if t.only]
    if only_tests:
        tests_to_run = only_tests

    # Determine pipeline/component to test
    pipeline_path = request.pipeline_path or (
        str(test_file_path.parent / test_file.pipeline) if test_file.pipeline else None
    )
    component_type = request.component_type or test_file.component_type

    # Merge environment variables
    env = {}
    if test_file.setup and test_file.setup.get("env"):
        env.update(test_file.setup["env"])
    if request.env:
        env.update(request.env)

    # Run tests with coverage collection
    results: List[TestResult] = []
    for test in tests_to_run:
        result = await run_single_test(
            test,
            pipeline_path,
            component_type,
            env if env else None,
            registry,
            include_coverage=include_coverage,
        )
        results.append(result)

    # Calculate summary
    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r.status == "passed"),
        "failed": sum(1 for r in results if r.status == "failed"),
        "skipped": sum(1 for r in results if r.status == "skipped"),
        "errors": sum(1 for r in results if r.status == "error"),
    }

    # Determine overall status
    if summary["errors"] > 0:
        overall_status = "error"
    elif summary["failed"] > 0:
        overall_status = "failed"
    else:
        overall_status = "passed"

    duration = int((datetime.now() - start_time).total_seconds() * 1000)

    # Aggregate coverage if requested
    suite_coverage = None
    if include_coverage:
        coverage_results = [r.coverage for r in results if r.coverage is not None]
        if coverage_results:
            suite_coverage = coverage_aggregator.aggregate(
                coverage_results,
                suite_name=test_file.name,
                test_file=str(test_file_path),
            )

    return TestSuiteResult(
        name=test_file.name,
        file=str(test_file_path),
        status=overall_status,
        duration=duration,
        tests=results,
        summary=summary,
        coverage=suite_coverage,
    )


@router.post("/run/coverage")
async def run_tests_with_coverage(
    request: TestRunRequest,
    registry: Any = Depends(get_registry),
) -> TestSuiteCoverageResult:
    """
    Run tests and return only coverage data.

    This is a convenience endpoint that always returns coverage data
    in the TestSuiteCoverageResult format.
    """
    # Run tests with coverage enabled
    result = await run_tests(request, include_coverage=True, registry=registry)

    if result.coverage:
        return result.coverage

    # If no coverage was collected, return empty result
    return TestSuiteCoverageResult(
        suite_name=result.name,
        test_file=result.file,
        overall_status=result.status,
        overall_duration_ms=result.duration or 0,
        test_results=[],
        tests_total=result.summary.get("total", 0),
        tests_passed=result.summary.get("passed", 0),
        tests_failed=result.summary.get("failed", 0),
        tests_skipped=result.summary.get("skipped", 0),
        tests_error=result.summary.get("errors", 0),
    )


@router.get("/validate/{test_file:path}")
async def validate_test_file(test_file: str) -> Dict[str, Any]:
    """Validate a test file without running tests"""
    test_file_path = Path(test_file)
    if not test_file_path.exists():
        raise HTTPException(status_code=404, detail=f"Test file not found: {test_file}")

    try:
        with open(test_file_path, "r") as f:
            test_file_data = json.load(f)

        # Validate against schema
        test_file_obj = TestFile(**test_file_data)

        return {
            "valid": True,
            "name": test_file_obj.name,
            "test_count": len(test_file_obj.tests),
            "has_pipeline": test_file_obj.pipeline is not None,
            "has_component": test_file_obj.component_type is not None,
        }

    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": f"Invalid JSON: {str(e)}",
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
        }
