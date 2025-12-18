/**
 * Pipeline Diff Provider for FlowMason VSCode Extension.
 *
 * Provides visual diff capabilities for pipeline files, showing:
 * - Added/removed/modified stages
 * - Configuration changes
 * - Schema changes
 * - Dependency graph changes
 */
import * as vscode from 'vscode';
export declare class PipelineDiffProvider implements vscode.TextDocumentContentProvider {
    private context;
    private static readonly scheme;
    private _onDidChange;
    readonly onDidChange: vscode.Event<vscode.Uri>;
    private diffCache;
    constructor(context: vscode.ExtensionContext);
    provideTextDocumentContent(uri: vscode.Uri): Promise<string>;
    /**
     * Compute diff between two pipeline files using the CLI.
     */
    private computeDiff;
    /**
     * Format diff result as HTML for webview.
     */
    private formatDiffAsHtml;
    private formatValue;
    /**
     * Clear the diff cache.
     */
    clearCache(): void;
    /**
     * Trigger a refresh of the diff view.
     */
    refresh(uri: vscode.Uri): void;
}
/**
 * Register the diff command.
 */
export declare function registerPipelineDiffCommands(context: vscode.ExtensionContext, provider: PipelineDiffProvider): void;
//# sourceMappingURL=pipelineDiffProvider.d.ts.map