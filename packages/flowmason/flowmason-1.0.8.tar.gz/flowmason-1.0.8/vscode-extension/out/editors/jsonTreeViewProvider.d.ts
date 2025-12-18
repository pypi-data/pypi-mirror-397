/**
 * JSON Tree View Provider
 *
 * A read-only Custom Text Editor that displays .pipeline.json files
 * as a collapsible tree view (like browser DevTools).
 *
 * Features:
 * - Collapsible/expandable nodes for objects and arrays
 * - Syntax highlighting using VSCode theme colors
 * - Copy JSON to clipboard
 * - "Edit in DAG Canvas" button
 * - Expand All / Collapse All
 * - Search/filter (optional)
 */
import * as vscode from 'vscode';
export declare class JsonTreeViewProvider implements vscode.CustomTextEditorProvider {
    static readonly viewType = "flowmason.jsonTreeView";
    constructor();
    resolveCustomTextEditor(document: vscode.TextDocument, webviewPanel: vscode.WebviewPanel, _token: vscode.CancellationToken): Promise<void>;
    private updateWebview;
    private getHtmlForWebview;
    private renderTreeNode;
    private renderLeafNode;
    private escapeHtml;
}
/**
 * Helper function to register the JSON tree view provider
 */
export declare function registerJsonTreeViewProvider(): vscode.Disposable;
//# sourceMappingURL=jsonTreeViewProvider.d.ts.map