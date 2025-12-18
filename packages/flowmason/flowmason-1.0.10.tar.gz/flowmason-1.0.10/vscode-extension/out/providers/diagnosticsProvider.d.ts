/**
 * FlowMason Diagnostics Provider
 *
 * Provides linting and error detection for FlowMason components.
 */
import * as vscode from 'vscode';
export declare class FlowMasonDiagnosticsProvider {
    private diagnosticCollection;
    private rules;
    constructor();
    activate(context: vscode.ExtensionContext): void;
    updateDiagnostics(document: vscode.TextDocument): void;
    private isFlowMasonFile;
    private createRules;
    private runDocumentChecks;
    dispose(): void;
}
//# sourceMappingURL=diagnosticsProvider.d.ts.map