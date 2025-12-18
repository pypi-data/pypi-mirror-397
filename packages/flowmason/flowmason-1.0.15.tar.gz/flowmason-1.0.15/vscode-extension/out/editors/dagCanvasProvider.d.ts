/**
 * DAG Canvas Provider
 *
 * An interactive Custom Text Editor for visual DAG editing of .pipeline.json files.
 * Features:
 * - Drag and drop components from sidebar
 * - Right-click context menus on nodes and canvas
 * - Drag nodes to reposition
 * - Visual connection ports
 * - Keyboard shortcuts (Delete, Ctrl+D to duplicate)
 * - Multi-select with Shift+Click
 */
import * as vscode from 'vscode';
export declare class DagCanvasProvider implements vscode.CustomTextEditorProvider {
    private readonly context;
    static readonly viewType = "flowmason.dagCanvas";
    private static _currentDocument;
    private static _editingDocuments;
    static get currentDocument(): vscode.TextDocument | undefined;
    static isEditingDocument(uri: string): boolean;
    constructor(context: vscode.ExtensionContext);
    resolveCustomTextEditor(document: vscode.TextDocument, webviewPanel: vscode.WebviewPanel, _token: vscode.CancellationToken): Promise<void>;
    private updateWebview;
    private highlightStageInJson;
    private addConnection;
    /**
     * Check if adding an edge from fromId to toId would create a cycle.
     * Returns true if toId can already reach fromId (meaning adding the edge would create a cycle).
     */
    private wouldCreateCycle;
    private removeConnection;
    private reconnectEdge;
    private updatePositions;
    private deleteStage;
    private deleteStages;
    private duplicateStage;
    private addStageWithComponent;
    private updateDocument;
    private getHtml;
}
/**
 * Register the DAG Canvas custom editor
 */
export declare function registerDagCanvasProvider(context: vscode.ExtensionContext): vscode.Disposable;
//# sourceMappingURL=dagCanvasProvider.d.ts.map