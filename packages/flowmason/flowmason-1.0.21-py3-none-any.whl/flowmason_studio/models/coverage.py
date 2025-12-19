"""
Coverage Reporting Models for FlowMason Test Framework.

Models for capturing and reporting test coverage metrics including:
- Stage execution tracking
- Input/output data per stage
- Token usage for LLM nodes
- Execution timing
- Overall test coverage metrics
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StageExecutionStatus(str, Enum):
    """Status of a stage during test execution."""
    EXECUTED = "executed"        # Stage ran successfully
    FAILED = "failed"            # Stage ran but failed
    SKIPPED = "skipped"          # Stage was skipped (dependency failed, conditional, etc.)
    NOT_REACHED = "not_reached"  # Stage was never reached


class StageExecutionMetrics(BaseModel):
    """
    Metrics for a single stage execution during testing.

    Captures execution order, status, dependencies, and skip reasons.
    """
    stage_id: str = Field(description="Stage identifier")
    stage_name: Optional[str] = Field(default=None, description="Human-readable stage name")
    component_type: str = Field(description="Component type (e.g., 'generator', 'http_request')")

    # Execution order and status
    execution_order: Optional[int] = Field(default=None, description="Order of execution (1, 2, 3...)")
    status: StageExecutionStatus = Field(default=StageExecutionStatus.NOT_REACHED)

    # Dependencies
    depends_on: List[str] = Field(default_factory=list, description="Stage IDs this stage depends on")
    dependents: List[str] = Field(default_factory=list, description="Stage IDs that depend on this stage")

    # Skip information
    skip_reason: Optional[str] = Field(
        default=None,
        description="Reason for skip: dependency_failed, conditional_false, error_handler, etc."
    )
    skipped_by: Optional[str] = Field(default=None, description="Stage ID that caused this to be skipped")


class StageDataMetrics(BaseModel):
    """
    Input/output data captured for a stage execution.

    Tracks the data flowing through the pipeline.
    """
    # Input data
    input_data: Optional[Dict[str, Any]] = Field(default=None, description="Input data to the stage")
    input_size_bytes: Optional[int] = Field(default=None, description="Size of input data")
    input_keys: List[str] = Field(default_factory=list, description="Keys in input data")

    # Output data
    output_data: Optional[Dict[str, Any]] = Field(default=None, description="Output data from the stage")
    output_size_bytes: Optional[int] = Field(default=None, description="Size of output data")
    output_keys: List[str] = Field(default_factory=list, description="Keys in output data")

    # Error output
    error_message: Optional[str] = Field(default=None, description="Error message if stage failed")
    error_type: Optional[str] = Field(default=None, description="Error type classification")


class LLMMetrics(BaseModel):
    """
    LLM-specific metrics for AI node stages.

    Captures token usage and cost for LLM calls.
    """
    is_llm_node: bool = Field(default=False, description="Whether this stage involved an LLM call")
    provider: Optional[str] = Field(default=None, description="LLM provider (anthropic, openai, etc.)")
    model: Optional[str] = Field(default=None, description="Model name (claude-3-5-sonnet, etc.)")

    # Token usage
    input_tokens: int = Field(default=0, ge=0, description="Input tokens consumed")
    output_tokens: int = Field(default=0, ge=0, description="Output tokens generated")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens (input + output)")

    # Cost
    cost_usd: float = Field(default=0.0, ge=0.0, description="Estimated cost in USD")

    # Cache information
    cache_hits: Optional[int] = Field(default=None, description="Number of cache hits")
    cache_read_tokens: Optional[int] = Field(default=None, description="Tokens read from cache")


class ExecutionTimeMetrics(BaseModel):
    """
    Timing metrics for a stage execution.

    Captures when the stage ran and how long it took.
    """
    started_at: Optional[datetime] = Field(default=None, description="When execution started")
    completed_at: Optional[datetime] = Field(default=None, description="When execution completed")
    duration_ms: int = Field(default=0, ge=0, description="Total duration in milliseconds")

    # Time breakdown (if available)
    input_mapping_ms: Optional[int] = Field(default=None, description="Time to resolve input templates")
    execution_ms: Optional[int] = Field(default=None, description="Actual component execution time")
    output_validation_ms: Optional[int] = Field(default=None, description="Time to validate output")

    # Performance flags
    is_slow: bool = Field(default=False, description="Whether this stage was slower than expected")
    slow_threshold_ms: Optional[int] = Field(default=None, description="Threshold used for slow detection")


class StageCoverageResult(BaseModel):
    """
    Complete coverage result for a single stage.

    Combines all metrics for comprehensive stage coverage reporting.
    """
    execution: StageExecutionMetrics
    data: StageDataMetrics
    timing: ExecutionTimeMetrics
    llm: Optional[LLMMetrics] = None


class CoverageSummary(BaseModel):
    """
    Summary statistics for test coverage.
    """
    # Stage counts
    total_stages: int = Field(default=0, description="Total stages in pipeline")
    stages_executed: int = Field(default=0, description="Stages that ran")
    stages_failed: int = Field(default=0, description="Stages that failed")
    stages_skipped: int = Field(default=0, description="Stages that were skipped")
    stages_not_reached: int = Field(default=0, description="Stages never reached")

    # Coverage percentage
    coverage_percentage: float = Field(default=0.0, description="Percentage of stages executed")

    # Timing
    total_duration_ms: int = Field(default=0, description="Total execution time")
    slowest_stage_id: Optional[str] = Field(default=None, description="ID of slowest stage")
    slowest_stage_ms: Optional[int] = Field(default=None, description="Duration of slowest stage")

    # LLM usage
    total_llm_calls: int = Field(default=0, description="Number of LLM calls made")
    total_input_tokens: int = Field(default=0, description="Total input tokens")
    total_output_tokens: int = Field(default=0, description="Total output tokens")
    total_llm_cost_usd: float = Field(default=0.0, description="Total LLM cost in USD")


class TestCoverageResult(BaseModel):
    """
    Complete coverage report for a single test.

    Includes all stage-level metrics and summary statistics.
    """
    # Test identification
    test_name: str = Field(description="Name of the test")
    pipeline_id: Optional[str] = Field(default=None, description="Pipeline ID if pipeline test")
    component_type: Optional[str] = Field(default=None, description="Component type if component test")

    # Overall status
    overall_status: str = Field(description="passed, failed, error, skipped")
    overall_duration_ms: int = Field(default=0, description="Total test duration")

    # Stage-level results
    stage_results: Dict[str, StageCoverageResult] = Field(
        default_factory=dict,
        description="Coverage results per stage"
    )

    # Execution order
    execution_order: List[str] = Field(
        default_factory=list,
        description="Order in which stages executed"
    )

    # Summary
    summary: CoverageSummary = Field(default_factory=CoverageSummary)

    # Test inputs/outputs
    test_input: Optional[Dict[str, Any]] = Field(default=None, description="Input provided to test")
    final_output: Optional[Any] = Field(default=None, description="Final test output")
    error: Optional[str] = Field(default=None, description="Error message if test failed")

    # Timestamp
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class TestSuiteCoverageResult(BaseModel):
    """
    Aggregated coverage report for a test suite.
    """
    # Suite identification
    suite_name: str
    test_file: str

    # Overall status
    overall_status: str
    overall_duration_ms: int = 0

    # Individual test results
    test_results: List[TestCoverageResult] = Field(default_factory=list)

    # Summary counts
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    tests_error: int = 0

    # Aggregated coverage
    aggregated_summary: CoverageSummary = Field(default_factory=CoverageSummary)

    # Aggregated LLM usage
    total_llm_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_llm_cost_usd: float = 0.0

    # Timestamp
    executed_at: datetime = Field(default_factory=datetime.utcnow)
