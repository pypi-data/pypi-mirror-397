/**
 * FlowMason Coverage Gutters
 *
 * Provides visual coverage indicators in the editor gutter for pipeline files.
 * Shows which stages were executed during test runs with color-coded indicators.
 */
import * as vscode from 'vscode';
/**
 * Stage coverage status
 */
export type StageCoverageStatus = 'executed' | 'failed' | 'skipped' | 'not_covered';
/**
 * Coverage data for a single stage
 */
export interface StageCoverage {
    stageId: string;
    status: StageCoverageStatus;
    executionCount: number;
    lastDuration?: number;
    errorMessage?: string;
}
/**
 * Coverage data for a file
 */
export interface FileCoverage {
    filePath: string;
    stages: Map<string, StageCoverage>;
    summary: {
        total: number;
        executed: number;
        failed: number;
        skipped: number;
        coveragePercent: number;
    };
    timestamp: Date;
}
/**
 * Coverage Gutters Provider
 *
 * Manages coverage decorations in the editor gutter.
 */
export declare class CoverageGuttersProvider implements vscode.Disposable {
    private executedDecoration;
    private failedDecoration;
    private skippedDecoration;
    private notCoveredDecoration;
    private coverageData;
    private disposables;
    private enabled;
    constructor();
    /**
     * Create a simple colored circle icon for the gutter
     */
    private createGutterIcon;
    /**
     * Update coverage data for a file
     */
    updateCoverage(filePath: string, stages: Array<{
        stageId: string;
        status: StageCoverageStatus;
        executionCount?: number;
        duration?: number;
        error?: string;
    }>): void;
    /**
     * Clear coverage data for a file
     */
    clearCoverage(filePath: string): void;
    /**
     * Clear all coverage data
     */
    clearAllCoverage(): void;
    /**
     * Toggle coverage display
     */
    toggle(): void;
    /**
     * Update decorations for an editor
     */
    private updateDecorations;
    /**
     * Clear decorations from an editor
     */
    private clearDecorations;
    /**
     * Get line numbers for each stage in a pipeline file
     */
    private getStageLineNumbers;
    /**
     * Create hover message for a stage
     */
    private createHoverMessage;
    /**
     * Get coverage summary for status bar
     */
    getCoverageSummary(filePath: string): string | null;
    /**
     * Dispose resources
     */
    dispose(): void;
}
/**
 * Get the global coverage gutters provider
 */
export declare function getCoverageGuttersProvider(): CoverageGuttersProvider;
/**
 * Register coverage gutters commands
 */
export declare function registerCoverageCommands(context: vscode.ExtensionContext): void;
//# sourceMappingURL=coverageGutters.d.ts.map