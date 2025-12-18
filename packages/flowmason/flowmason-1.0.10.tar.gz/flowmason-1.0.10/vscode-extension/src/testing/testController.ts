/**
 * FlowMason Test Controller
 *
 * Integrates with VSCode's Test Explorer to discover and run FlowMason tests.
 * Includes coverage reporting for stage-level metrics.
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import axios, { AxiosInstance } from 'axios';
import {
    TestFile,
    TestCase,
    TestResult,
    TestSuiteResult,
    TestRunRequest,
    TestCoverageResult,
    StageCoverageResult,
    CoverageSummary,
} from './types';
import { getCoverageGuttersProvider, StageCoverageStatus } from './coverageGutters';

/**
 * FlowMason Test Controller
 * Provides test discovery and execution for .test.json files
 * with coverage reporting support.
 */
export class FlowMasonTestController {
    private controller: vscode.TestController;
    private client: AxiosInstance;
    private testItems: Map<string, vscode.TestItem> = new Map();
    private testData: WeakMap<vscode.TestItem, TestCase> = new WeakMap();
    private fileWatcher: vscode.FileSystemWatcher;
    private outputChannel: vscode.OutputChannel;
    private includeCoverage: boolean = true;

    constructor(context: vscode.ExtensionContext) {
        // Create test controller
        this.controller = vscode.tests.createTestController(
            'flowmasonTestController',
            'FlowMason Tests'
        );
        context.subscriptions.push(this.controller);

        // Create output channel for coverage reports
        this.outputChannel = vscode.window.createOutputChannel('FlowMason Test Coverage');
        context.subscriptions.push(this.outputChannel);

        // Setup HTTP client
        const config = vscode.workspace.getConfiguration('flowmason');
        const studioUrl = config.get<string>('studioUrl') || 'http://localhost:8999';
        this.includeCoverage = config.get<boolean>('tests.includeCoverage') ?? true;
        this.client = axios.create({
            baseURL: studioUrl,
            timeout: 60000,
        });

        // Setup test run profiles
        this.controller.createRunProfile(
            'Run Tests',
            vscode.TestRunProfileKind.Run,
            (request, token) => this.runTests(request, token),
            true
        );

        this.controller.createRunProfile(
            'Run Tests with Coverage',
            vscode.TestRunProfileKind.Coverage,
            (request, token) => this.runTestsWithCoverage(request, token),
            false
        );

        this.controller.createRunProfile(
            'Debug Tests',
            vscode.TestRunProfileKind.Debug,
            (request, token) => this.debugTests(request, token),
            false
        );

        // Setup test discovery
        this.controller.resolveHandler = async (item) => {
            if (!item) {
                await this.discoverAllTests();
            } else {
                await this.resolveTestItem(item);
            }
        };

        // Watch for test file changes
        this.fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.test.json');
        this.fileWatcher.onDidCreate(uri => this.onTestFileCreated(uri));
        this.fileWatcher.onDidChange(uri => this.onTestFileChanged(uri));
        this.fileWatcher.onDidDelete(uri => this.onTestFileDeleted(uri));
        context.subscriptions.push(this.fileWatcher);

        // Initial discovery
        this.discoverAllTests();
    }

    /**
     * Discover all test files in the workspace
     */
    private async discoverAllTests(): Promise<void> {
        const testFiles = await vscode.workspace.findFiles('**/*.test.json', '**/node_modules/**');

        for (const uri of testFiles) {
            await this.loadTestFile(uri);
        }
    }

    /**
     * Load tests from a .test.json file
     */
    private async loadTestFile(uri: vscode.Uri): Promise<void> {
        try {
            const content = fs.readFileSync(uri.fsPath, 'utf-8');
            const testFile: TestFile = JSON.parse(content);

            // Create test item for the file
            const fileItem = this.controller.createTestItem(
                uri.fsPath,
                testFile.name || path.basename(uri.fsPath, '.test.json'),
                uri
            );
            fileItem.description = testFile.description;
            fileItem.canResolveChildren = true;

            // Add test cases as children
            for (const test of testFile.tests) {
                const testItem = this.controller.createTestItem(
                    `${uri.fsPath}#${test.name}`,
                    test.name,
                    uri
                );
                testItem.description = test.description;

                if (test.tags) {
                    testItem.tags = test.tags.map(tag => new vscode.TestTag(tag));
                }

                // Store test data
                this.testData.set(testItem, test);
                this.testItems.set(testItem.id, testItem);

                fileItem.children.add(testItem);
            }

            // Store file item
            this.testItems.set(fileItem.id, fileItem);
            this.controller.items.add(fileItem);

        } catch (error) {
            console.error(`Failed to load test file ${uri.fsPath}:`, error);
        }
    }

    /**
     * Resolve a test item (lazy loading)
     */
    private async resolveTestItem(item: vscode.TestItem): Promise<void> {
        if (item.uri && item.children.size === 0) {
            await this.loadTestFile(item.uri);
        }
    }

    /**
     * Run tests
     */
    private async runTests(
        request: vscode.TestRunRequest,
        token: vscode.CancellationToken
    ): Promise<void> {
        const run = this.controller.createTestRun(request);
        const queue: vscode.TestItem[] = [];

        // Collect tests to run
        if (request.include) {
            request.include.forEach(item => this.collectTests(item, queue));
        } else {
            this.controller.items.forEach(item => this.collectTests(item, queue));
        }

        // Filter out excluded tests
        const testsToRun = queue.filter(item => !request.exclude?.includes(item));

        // Group tests by file
        const testsByFile = new Map<string, vscode.TestItem[]>();
        for (const item of testsToRun) {
            const filePath = item.uri?.fsPath;
            if (filePath) {
                const fileTests = testsByFile.get(filePath) || [];
                fileTests.push(item);
                testsByFile.set(filePath, fileTests);
            }
        }

        // Run tests for each file
        for (const [filePath, items] of testsByFile) {
            if (token.isCancellationRequested) {
                items.forEach(item => run.skipped(item));
                continue;
            }

            await this.runTestFile(filePath, items, run, token);
        }

        run.end();
    }

    /**
     * Run tests with coverage collection
     */
    private async runTestsWithCoverage(
        request: vscode.TestRunRequest,
        token: vscode.CancellationToken
    ): Promise<void> {
        const originalIncludeCoverage = this.includeCoverage;
        this.includeCoverage = true;
        try {
            await this.runTests(request, token);
        } finally {
            this.includeCoverage = originalIncludeCoverage;
        }
    }

    /**
     * Debug tests (runs with debug mode)
     */
    private async debugTests(
        request: vscode.TestRunRequest,
        token: vscode.CancellationToken
    ): Promise<void> {
        // For now, same as run but could integrate with debug adapter
        await this.runTests(request, token);
    }

    /**
     * Collect all test items recursively
     */
    private collectTests(item: vscode.TestItem, queue: vscode.TestItem[]): void {
        if (item.children.size === 0) {
            // Leaf node - actual test
            queue.push(item);
        } else {
            // Parent node - recurse
            item.children.forEach(child => this.collectTests(child, queue));
        }
    }

    /**
     * Run tests from a single test file
     */
    private async runTestFile(
        filePath: string,
        items: vscode.TestItem[],
        run: vscode.TestRun,
        token: vscode.CancellationToken
    ): Promise<void> {
        // Mark tests as started
        items.forEach(item => run.started(item));

        try {
            // Load test file
            const content = fs.readFileSync(filePath, 'utf-8');
            const testFile: TestFile = JSON.parse(content);

            // Resolve pipeline path
            const pipelinePath = testFile.pipeline
                ? path.resolve(path.dirname(filePath), testFile.pipeline)
                : undefined;

            // Get test names to run
            const testNames = items.map(item => {
                const data = this.testData.get(item);
                return data?.name;
            }).filter(Boolean) as string[];

            // Execute tests via backend with optional coverage
            const url = this.includeCoverage
                ? '/api/v1/tests/run?include_coverage=true'
                : '/api/v1/tests/run';

            const response = await this.client.post(url, {
                testFile: filePath,
                pipelinePath,
                componentType: testFile.componentType,
                testNames,
                env: testFile.setup?.env,
            } as TestRunRequest);

            const result: TestSuiteResult = response.data;

            // Display coverage report if available
            if (result.coverage && this.includeCoverage) {
                this.displayCoverageReport(result.coverage, testFile.name, pipelinePath);
            }

            // Map results to test items
            for (const item of items) {
                const data = this.testData.get(item);
                if (!data) continue;

                const testResult = result.tests.find(r => r.name === data.name);
                if (!testResult) {
                    run.skipped(item);
                    continue;
                }

                const duration = testResult.duration;

                switch (testResult.status) {
                    case 'passed':
                        run.passed(item, duration);
                        // Append coverage info to test output
                        if (testResult.coverage) {
                            run.appendOutput(
                                this.formatTestCoverage(testResult.coverage),
                                undefined,
                                item
                            );
                        }
                        break;
                    case 'failed':
                        const message = new vscode.TestMessage(testResult.error || 'Test failed');
                        if (testResult.assertions) {
                            const failedAssertions = testResult.assertions.filter(a => !a.passed);
                            if (failedAssertions.length > 0) {
                                message.message = failedAssertions
                                    .map(a => `${a.path}: ${a.message || 'assertion failed'}\n  Expected: ${JSON.stringify(a.expected)}\n  Actual: ${JSON.stringify(a.actual)}`)
                                    .join('\n\n');
                            }
                        }
                        run.failed(item, message, duration);
                        break;
                    case 'skipped':
                        run.skipped(item);
                        break;
                    case 'error':
                        run.errored(item, new vscode.TestMessage(testResult.error || 'Test error'), duration);
                        break;
                }
            }

        } catch (error) {
            // All tests in this file failed
            const errorMessage = error instanceof Error ? error.message : String(error);
            for (const item of items) {
                run.errored(item, new vscode.TestMessage(`Failed to run tests: ${errorMessage}`));
            }
        }
    }

    /**
     * Display coverage report in output channel and update gutters
     */
    private displayCoverageReport(coverage: any, suiteName: string, pipelinePath?: string): void {
        this.outputChannel.clear();
        this.outputChannel.appendLine('========================================');
        this.outputChannel.appendLine(`  FlowMason Test Coverage Report`);
        this.outputChannel.appendLine(`  Suite: ${suiteName}`);
        this.outputChannel.appendLine('========================================');
        this.outputChannel.appendLine('');

        // Summary section
        const summary = coverage.aggregated_summary || coverage.summary;
        if (summary) {
            this.outputChannel.appendLine('SUMMARY');
            this.outputChannel.appendLine('--------');
            this.outputChannel.appendLine(`  Coverage: ${summary.coverage_percentage?.toFixed(1) || 0}%`);
            this.outputChannel.appendLine(`  Stages: ${summary.stages_executed || 0}/${summary.total_stages || 0} executed`);
            this.outputChannel.appendLine(`  Failed: ${summary.stages_failed || 0}`);
            this.outputChannel.appendLine(`  Skipped: ${summary.stages_skipped || 0}`);
            this.outputChannel.appendLine(`  Duration: ${summary.total_duration_ms || 0}ms`);
            this.outputChannel.appendLine('');

            // LLM Usage
            if (summary.total_llm_calls > 0) {
                this.outputChannel.appendLine('LLM USAGE');
                this.outputChannel.appendLine('---------');
                this.outputChannel.appendLine(`  Calls: ${summary.total_llm_calls}`);
                this.outputChannel.appendLine(`  Input Tokens: ${summary.total_input_tokens}`);
                this.outputChannel.appendLine(`  Output Tokens: ${summary.total_output_tokens}`);
                this.outputChannel.appendLine(`  Cost: $${summary.total_llm_cost_usd?.toFixed(4) || '0.0000'}`);
                this.outputChannel.appendLine('');
            }
        }

        // Per-test breakdown
        if (coverage.test_results && coverage.test_results.length > 0) {
            this.outputChannel.appendLine('TEST DETAILS');
            this.outputChannel.appendLine('------------');
            for (const testResult of coverage.test_results) {
                this.outputChannel.appendLine(`\n  ${testResult.test_name}: ${testResult.overall_status.toUpperCase()}`);
                this.outputChannel.appendLine(`    Duration: ${testResult.overall_duration_ms}ms`);
                if (testResult.summary) {
                    this.outputChannel.appendLine(`    Coverage: ${testResult.summary.coverage_percentage?.toFixed(1)}%`);
                }
                if (testResult.execution_order && testResult.execution_order.length > 0) {
                    this.outputChannel.appendLine(`    Stages executed: ${testResult.execution_order.join(' -> ')}`);
                }
            }
        }

        this.outputChannel.appendLine('');
        this.outputChannel.appendLine('========================================');
        this.outputChannel.show(true);

        // Update coverage gutters if we have a pipeline path
        if (pipelinePath) {
            this.updateCoverageGutters(pipelinePath, coverage);
        }
    }

    /**
     * Update coverage gutters for a pipeline file
     */
    private updateCoverageGutters(pipelinePath: string, coverage: any): void {
        try {
            const guttersProvider = getCoverageGuttersProvider();

            // Collect stage coverage from all test results
            const stageCoverageMap = new Map<string, {
                stageId: string;
                status: StageCoverageStatus;
                executionCount: number;
                duration?: number;
                error?: string;
            }>();

            // Process test results
            const testResults = coverage.test_results || [];
            for (const testResult of testResults) {
                const stages = testResult.stages || [];
                for (const stage of stages) {
                    const stageId = stage.stage_id || stage.id;
                    if (!stageId) continue;

                    const existing = stageCoverageMap.get(stageId);
                    const execCount = (existing?.executionCount || 0) + 1;

                    // Determine status
                    let status: StageCoverageStatus = 'not_covered';
                    if (stage.status === 'completed' || stage.status === 'passed') {
                        status = 'executed';
                    } else if (stage.status === 'failed' || stage.status === 'error') {
                        status = 'failed';
                    } else if (stage.status === 'skipped') {
                        status = 'skipped';
                    }

                    // Keep the worst status (failed > skipped > executed)
                    if (existing) {
                        if (status === 'failed' || existing.status === 'failed') {
                            status = 'failed';
                        } else if (status === 'skipped' && existing.status !== 'executed') {
                            status = 'skipped';
                        } else if (existing.status === 'executed') {
                            status = 'executed';
                        }
                    }

                    stageCoverageMap.set(stageId, {
                        stageId,
                        status,
                        executionCount: execCount,
                        duration: stage.duration_ms || stage.duration,
                        error: stage.error || stage.error_message,
                    });
                }
            }

            // Update the gutters provider
            guttersProvider.updateCoverage(
                pipelinePath,
                Array.from(stageCoverageMap.values())
            );

        } catch (error) {
            console.error('Failed to update coverage gutters:', error);
        }
    }

    /**
     * Format test coverage for inline display
     */
    private formatTestCoverage(coverage: TestCoverageResult): string {
        const lines: string[] = ['\n--- Coverage ---'];

        if (coverage.summary) {
            lines.push(`Coverage: ${coverage.summary.coverage_percentage?.toFixed(1) || 0}%`);
            lines.push(`Stages: ${coverage.summary.stages_executed}/${coverage.summary.total_stages}`);
            lines.push(`Duration: ${coverage.summary.total_duration_ms}ms`);

            if (coverage.summary.total_llm_calls > 0) {
                lines.push(`LLM Calls: ${coverage.summary.total_llm_calls} (${coverage.summary.total_input_tokens}/${coverage.summary.total_output_tokens} tokens)`);
            }
        }

        if (coverage.execution_order && coverage.execution_order.length > 0) {
            lines.push(`Execution: ${coverage.execution_order.join(' -> ')}`);
        }

        return lines.join('\n') + '\n';
    }

    /**
     * Handle test file created
     */
    private async onTestFileCreated(uri: vscode.Uri): Promise<void> {
        await this.loadTestFile(uri);
    }

    /**
     * Handle test file changed
     */
    private async onTestFileChanged(uri: vscode.Uri): Promise<void> {
        // Remove old test items
        const existingItem = this.testItems.get(uri.fsPath);
        if (existingItem) {
            this.controller.items.delete(existingItem.id);
            this.testItems.delete(uri.fsPath);
        }

        // Reload
        await this.loadTestFile(uri);
    }

    /**
     * Handle test file deleted
     */
    private onTestFileDeleted(uri: vscode.Uri): void {
        const existingItem = this.testItems.get(uri.fsPath);
        if (existingItem) {
            this.controller.items.delete(existingItem.id);
            this.testItems.delete(uri.fsPath);
        }
    }

    /**
     * Dispose resources
     */
    dispose(): void {
        this.controller.dispose();
        this.fileWatcher.dispose();
    }
}

/**
 * Register test controller commands
 */
export function registerTestCommands(context: vscode.ExtensionContext): void {
    // Run all tests command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.runAllTests', async () => {
            await vscode.commands.executeCommand('testing.runAll');
        })
    );

    // Run tests in current file
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.runTestsInFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document.fileName.endsWith('.test.json')) {
                await vscode.commands.executeCommand('testing.runCurrentFile');
            } else {
                vscode.window.showWarningMessage('Open a .test.json file to run tests');
            }
        })
    );

    // Create test file command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.createTestFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('Open a file first');
                return;
            }

            const currentFile = editor.document.fileName;
            let testFileName: string;
            let testContent: TestFile;

            if (currentFile.endsWith('.pipeline.json')) {
                // Create pipeline test
                testFileName = currentFile.replace('.pipeline.json', '.test.json');
                const pipelineName = path.basename(currentFile, '.pipeline.json');
                testContent = {
                    name: `${pipelineName} Tests`,
                    description: `Tests for ${pipelineName} pipeline`,
                    pipeline: `./${path.basename(currentFile)}`,
                    tests: [
                        {
                            name: 'should complete successfully',
                            input: {},
                            assertions: [
                                { path: 'output', type: 'exists' }
                            ]
                        }
                    ]
                };
            } else if (currentFile.endsWith('.py')) {
                // Create component test
                testFileName = currentFile.replace('.py', '.test.json');
                const componentName = path.basename(currentFile, '.py');
                testContent = {
                    name: `${componentName} Tests`,
                    description: `Tests for ${componentName} component`,
                    componentType: componentName,
                    tests: [
                        {
                            name: 'should execute with valid input',
                            input: {},
                            assertions: [
                                { path: 'output', type: 'exists' }
                            ]
                        }
                    ]
                };
            } else {
                vscode.window.showWarningMessage('Create tests for .pipeline.json or .py files');
                return;
            }

            // Check if file exists
            if (fs.existsSync(testFileName)) {
                const action = await vscode.window.showWarningMessage(
                    'Test file already exists. Overwrite?',
                    'Overwrite',
                    'Cancel'
                );
                if (action !== 'Overwrite') {
                    return;
                }
            }

            // Write test file
            fs.writeFileSync(testFileName, JSON.stringify(testContent, null, 2));

            // Open the file
            const doc = await vscode.workspace.openTextDocument(testFileName);
            await vscode.window.showTextDocument(doc);

            vscode.window.showInformationMessage(`Created test file: ${path.basename(testFileName)}`);
        })
    );
}
