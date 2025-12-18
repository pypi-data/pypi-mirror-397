/**
 * FlowMason Test Types
 *
 * Types for the .test.json test file format and test execution.
 */
/**
 * Assertion types for test validation
 */
export type AssertionType = 'equals' | 'notEquals' | 'contains' | 'notContains' | 'matches' | 'type' | 'exists' | 'notExists' | 'lessThan' | 'greaterThan' | 'lengthEquals' | 'lengthLessThan' | 'lengthGreaterThan';
/**
 * Single assertion in a test
 */
export interface TestAssertion {
    /** JSONPath to the value to check (e.g., "output.summary", "stages.fetch.output") */
    path: string;
    /** Type of assertion */
    type?: AssertionType;
    /** Expected value (for equals, contains, matches) */
    value?: unknown;
    /** For type assertions */
    expectedType?: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'null';
    /** For comparison assertions */
    lessThan?: number;
    greaterThan?: number;
    /** Custom message on failure */
    message?: string;
}
/**
 * Single test case
 */
export interface TestCase {
    /** Test name */
    name: string;
    /** Test description */
    description?: string;
    /** Input data for the pipeline/component */
    input: Record<string, unknown>;
    /** Assertions to validate output */
    assertions?: TestAssertion[];
    /** Expected error (for error case testing) */
    expectError?: string | boolean;
    /** Timeout in milliseconds */
    timeout?: number;
    /** Tags for filtering */
    tags?: string[];
    /** Skip this test */
    skip?: boolean;
    /** Only run this test */
    only?: boolean;
}
/**
 * Test file format (.test.json)
 */
export interface TestFile {
    /** Test suite name */
    name: string;
    /** Description of the test suite */
    description?: string;
    /** Path to the pipeline file (relative to test file) */
    pipeline?: string;
    /** Path to the component file (for unit tests) */
    component?: string;
    /** Component type (for component tests) */
    componentType?: string;
    /** Default timeout for all tests */
    timeout?: number;
    /** Setup configuration */
    setup?: {
        /** Environment variables */
        env?: Record<string, string>;
        /** Mock data */
        mocks?: Record<string, unknown>;
    };
    /** Test cases */
    tests: TestCase[];
}
/**
 * Coverage summary statistics
 */
export interface CoverageSummary {
    /** Total stages in pipeline */
    total_stages: number;
    /** Stages that executed */
    stages_executed: number;
    /** Stages that failed */
    stages_failed: number;
    /** Stages that were skipped */
    stages_skipped: number;
    /** Stages not reached */
    stages_not_reached: number;
    /** Coverage percentage */
    coverage_percentage: number;
    /** Total execution time */
    total_duration_ms: number;
    /** Slowest stage ID */
    slowest_stage_id?: string;
    /** Slowest stage duration */
    slowest_stage_ms?: number;
    /** LLM call count */
    total_llm_calls: number;
    /** Total input tokens */
    total_input_tokens: number;
    /** Total output tokens */
    total_output_tokens: number;
    /** Total LLM cost */
    total_llm_cost_usd: number;
}
/**
 * Stage execution status
 */
export type StageExecutionStatus = 'executed' | 'failed' | 'skipped' | 'not_reached';
/**
 * LLM usage metrics for a stage
 */
export interface LLMMetrics {
    is_llm_node: boolean;
    provider?: string;
    model?: string;
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
    cost_usd: number;
}
/**
 * Execution time metrics for a stage
 */
export interface ExecutionTimeMetrics {
    started_at?: string;
    completed_at?: string;
    duration_ms: number;
    is_slow: boolean;
    slow_threshold_ms?: number;
}
/**
 * Stage execution metrics
 */
export interface StageExecutionMetrics {
    stage_id: string;
    stage_name?: string;
    component_type: string;
    execution_order?: number;
    status: StageExecutionStatus;
    depends_on: string[];
    dependents: string[];
    skip_reason?: string;
    skipped_by?: string;
}
/**
 * Stage data metrics
 */
export interface StageDataMetrics {
    input_data?: Record<string, unknown>;
    input_size_bytes?: number;
    input_keys: string[];
    output_data?: Record<string, unknown>;
    output_size_bytes?: number;
    output_keys: string[];
    error_message?: string;
    error_type?: string;
}
/**
 * Complete coverage result for a single stage
 */
export interface StageCoverageResult {
    execution: StageExecutionMetrics;
    data: StageDataMetrics;
    timing: ExecutionTimeMetrics;
    llm?: LLMMetrics;
}
/**
 * Coverage result for a single test
 */
export interface TestCoverageResult {
    test_name: string;
    pipeline_id?: string;
    component_type?: string;
    overall_status: string;
    overall_duration_ms: number;
    stage_results: Record<string, StageCoverageResult>;
    execution_order: string[];
    summary: CoverageSummary;
    test_input?: Record<string, unknown>;
    final_output?: unknown;
    error?: string;
    executed_at: string;
}
/**
 * Aggregated coverage for a test suite
 */
export interface TestSuiteCoverageResult {
    suite_name: string;
    test_file: string;
    overall_status: string;
    overall_duration_ms: number;
    test_results: TestCoverageResult[];
    tests_total: number;
    tests_passed: number;
    tests_failed: number;
    tests_skipped: number;
    tests_error: number;
    aggregated_summary: CoverageSummary;
    total_llm_calls: number;
    total_input_tokens: number;
    total_output_tokens: number;
    total_llm_cost_usd: number;
    executed_at: string;
}
/**
 * Test run result
 */
export interface TestResult {
    /** Test case name */
    name: string;
    /** Pass/fail status */
    status: 'passed' | 'failed' | 'skipped' | 'error';
    /** Duration in milliseconds */
    duration?: number;
    /** Error message if failed */
    error?: string;
    /** Stack trace if error */
    stack?: string;
    /** Assertion results */
    assertions?: {
        path: string;
        passed: boolean;
        message?: string;
        expected?: unknown;
        actual?: unknown;
    }[];
    /** Output from the test */
    output?: unknown;
    /** Coverage data (when include_coverage=true) */
    coverage?: TestCoverageResult;
}
/**
 * Test suite result
 */
export interface TestSuiteResult {
    /** Suite name */
    name: string;
    /** Path to test file */
    file: string;
    /** Overall status */
    status: 'passed' | 'failed' | 'error';
    /** Total duration */
    duration?: number;
    /** Individual test results */
    tests: TestResult[];
    /** Summary counts */
    summary: {
        total: number;
        passed: number;
        failed: number;
        skipped: number;
        errors: number;
    };
    /** Aggregated coverage (when include_coverage=true) */
    coverage?: TestSuiteCoverageResult;
}
/**
 * Test run request to backend
 */
export interface TestRunRequest {
    /** Test file path */
    testFile: string;
    /** Pipeline file path (resolved) */
    pipelinePath?: string;
    /** Component type (for unit tests) */
    componentType?: string;
    /** Specific test names to run (empty = all) */
    testNames?: string[];
    /** Environment variables */
    env?: Record<string, string>;
}
/**
 * Test run response from backend
 */
export interface TestRunResponse {
    /** Run ID */
    runId: string;
    /** Status */
    status: 'running' | 'completed' | 'failed';
    /** Results (when completed) */
    results?: TestSuiteResult;
    /** Error message */
    error?: string;
}
//# sourceMappingURL=types.d.ts.map