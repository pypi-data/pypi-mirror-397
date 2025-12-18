/**
 * FlowMason Test Controller
 *
 * Integrates with VSCode's Test Explorer to discover and run FlowMason tests.
 * Includes coverage reporting for stage-level metrics.
 */
import * as vscode from 'vscode';
/**
 * FlowMason Test Controller
 * Provides test discovery and execution for .test.json files
 * with coverage reporting support.
 */
export declare class FlowMasonTestController {
    private controller;
    private client;
    private testItems;
    private testData;
    private fileWatcher;
    private outputChannel;
    private includeCoverage;
    constructor(context: vscode.ExtensionContext);
    /**
     * Discover all test files in the workspace
     */
    private discoverAllTests;
    /**
     * Load tests from a .test.json file
     */
    private loadTestFile;
    /**
     * Resolve a test item (lazy loading)
     */
    private resolveTestItem;
    /**
     * Run tests
     */
    private runTests;
    /**
     * Run tests with coverage collection
     */
    private runTestsWithCoverage;
    /**
     * Debug tests (runs with debug mode)
     */
    private debugTests;
    /**
     * Collect all test items recursively
     */
    private collectTests;
    /**
     * Run tests from a single test file
     */
    private runTestFile;
    /**
     * Display coverage report in output channel and update gutters
     */
    private displayCoverageReport;
    /**
     * Update coverage gutters for a pipeline file
     */
    private updateCoverageGutters;
    /**
     * Format test coverage for inline display
     */
    private formatTestCoverage;
    /**
     * Handle test file created
     */
    private onTestFileCreated;
    /**
     * Handle test file changed
     */
    private onTestFileChanged;
    /**
     * Handle test file deleted
     */
    private onTestFileDeleted;
    /**
     * Dispose resources
     */
    dispose(): void;
}
/**
 * Register test controller commands
 */
export declare function registerTestCommands(context: vscode.ExtensionContext): void;
//# sourceMappingURL=testController.d.ts.map