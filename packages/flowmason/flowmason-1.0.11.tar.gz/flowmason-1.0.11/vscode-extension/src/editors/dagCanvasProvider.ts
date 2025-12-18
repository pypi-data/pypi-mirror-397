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
import { PipelineFile, PipelineStage } from '../views/pipelineStagesTree';

interface NodePosition {
    x: number;
    y: number;
}

export class DagCanvasProvider implements vscode.CustomTextEditorProvider {
    public static readonly viewType = 'flowmason.dagCanvas';

    // Track the currently active DAG document
    private static _currentDocument: vscode.TextDocument | undefined;

    // Track which document URIs are being edited by DAG canvas (to allow bypass protection)
    private static _editingDocuments = new Set<string>();

    public static get currentDocument(): vscode.TextDocument | undefined {
        return DagCanvasProvider._currentDocument;
    }

    public static isEditingDocument(uri: string): boolean {
        return DagCanvasProvider._editingDocuments.has(uri);
    }

    constructor(private readonly context: vscode.ExtensionContext) {}

    async resolveCustomTextEditor(
        document: vscode.TextDocument,
        webviewPanel: vscode.WebviewPanel,
        _token: vscode.CancellationToken
    ): Promise<void> {
        webviewPanel.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.context.extensionUri]
        };

        // Track this as the current document
        DagCanvasProvider._currentDocument = document;

        // Set context to show pipeline-related views
        vscode.commands.executeCommand('setContext', 'flowmason.pipelineOpen', true);

        // Update current document when panel becomes active
        webviewPanel.onDidChangeViewState(e => {
            if (e.webviewPanel.active) {
                DagCanvasProvider._currentDocument = document;
                vscode.commands.executeCommand('setContext', 'flowmason.pipelineOpen', true);
            }
        });

        // Initial render
        this.updateWebview(webviewPanel.webview, document);

        // Watch for document changes
        const changeDocumentSubscription = vscode.workspace.onDidChangeTextDocument(e => {
            if (e.document.uri.toString() === document.uri.toString()) {
                this.updateWebview(webviewPanel.webview, document);
            }
        });

        // Handle messages from webview
        webviewPanel.webview.onDidReceiveMessage(async message => {
            switch (message.type) {
                case 'selectStage':
                    vscode.commands.executeCommand('flowmason.showStageConfig', message.stageId);
                    this.highlightStageInJson(document, message.stageId);
                    break;

                case 'addConnection':
                    await this.addConnection(document, message.from, message.to);
                    break;

                case 'removeConnection':
                    await this.removeConnection(document, message.from, message.to);
                    break;

                case 'reconnectEdge':
                    await this.reconnectEdge(document, message.oldFrom, message.oldTo, message.newFrom, message.newTo);
                    break;

                case 'updatePositions':
                    await this.updatePositions(document, message.positions);
                    break;

                case 'deleteStage':
                    await this.deleteStage(document, message.stageId);
                    break;

                case 'deleteStages':
                    await this.deleteStages(document, message.stageIds);
                    break;

                case 'duplicateStage':
                    await this.duplicateStage(document, message.stageId);
                    break;

                case 'addStage':
                    vscode.commands.executeCommand('flowmason.addStage');
                    break;

                case 'addStageWithComponent':
                    await this.addStageWithComponent(document, message.componentType, message.position);
                    break;

                case 'editStageConfig':
                    vscode.commands.executeCommand('flowmason.showStageConfig', message.stageId);
                    break;

                case 'setBreakpoint':
                    vscode.commands.executeCommand('flowmason.toggleBreakpoint', message.stageId);
                    break;

                case 'openJsonEditor':
                    // Open the JSON source code in text editor (bidirectional sync)
                    vscode.commands.executeCommand('vscode.openWith', document.uri, 'default');
                    break;

                case 'runFromStage':
                    vscode.window.showInformationMessage(`Run from stage: ${message.stageId} (coming soon)`);
                    break;
            }
        });

        // Cleanup
        webviewPanel.onDidDispose(() => {
            changeDocumentSubscription.dispose();
            if (DagCanvasProvider._currentDocument === document) {
                DagCanvasProvider._currentDocument = undefined;
            }
        });
    }

    private updateWebview(webview: vscode.Webview, document: vscode.TextDocument): void {
        let pipeline: PipelineFile | null = null;

        try {
            pipeline = JSON.parse(document.getText());
        } catch {
            // Invalid JSON
        }

        webview.html = this.getHtml(webview, pipeline);
    }

    private async highlightStageInJson(document: vscode.TextDocument, stageId: string): Promise<void> {
        const text = document.getText();
        const pattern = `"id"\\s*:\\s*"${stageId}"`;
        const match = new RegExp(pattern).exec(text);

        if (match) {
            const pos = document.positionAt(match.index);
            const range = new vscode.Range(pos, pos.translate(0, match[0].length));

            const jsonUri = document.uri;
            const editor = await vscode.window.showTextDocument(jsonUri, {
                viewColumn: vscode.ViewColumn.Beside,
                preserveFocus: true,
                preview: true
            });
            editor.selection = new vscode.Selection(range.start, range.end);
            editor.revealRange(range, vscode.TextEditorRevealType.InCenter);
        }
    }

    private async addConnection(document: vscode.TextDocument, fromId: string, toId: string): Promise<void> {
        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;
            const toStage = pipeline.stages.find(s => s.id === toId);
            const fromStage = pipeline.stages.find(s => s.id === fromId);

            if (!toStage || !fromStage) return;

            // Check if connection already exists
            if (toStage.depends_on?.includes(fromId)) {
                return;
            }

            // Check for cycles: would adding fromId -> toId create a cycle?
            // A cycle exists if toId can reach fromId through existing dependencies
            if (this.wouldCreateCycle(pipeline, fromId, toId)) {
                vscode.window.showWarningMessage(
                    `Cannot connect "${fromId}" → "${toId}": this would create a circular dependency`
                );
                return;
            }

            if (!toStage.depends_on) {
                toStage.depends_on = [];
            }

            toStage.depends_on.push(fromId);
            await this.updateDocument(document, pipeline);
        } catch {
            vscode.window.showErrorMessage('Failed to add connection');
        }
    }

    /**
     * Check if adding an edge from fromId to toId would create a cycle.
     * Returns true if toId can already reach fromId (meaning adding the edge would create a cycle).
     */
    private wouldCreateCycle(pipeline: PipelineFile, fromId: string, toId: string): boolean {
        // Build adjacency list: for each stage, what stages depend on it (downstream)
        const downstream = new Map<string, string[]>();
        for (const stage of pipeline.stages) {
            downstream.set(stage.id, []);
        }
        for (const stage of pipeline.stages) {
            for (const dep of stage.depends_on || []) {
                const existing = downstream.get(dep);
                if (existing) {
                    existing.push(stage.id);
                }
            }
        }

        // Check if we can reach fromId starting from toId (following downstream edges)
        // If yes, then adding fromId -> toId would create a cycle
        const visited = new Set<string>();
        const stack = [toId];

        while (stack.length > 0) {
            const current = stack.pop()!;
            if (current === fromId) {
                return true; // Found a path from toId to fromId, would create cycle
            }
            if (visited.has(current)) {
                continue;
            }
            visited.add(current);

            const children = downstream.get(current) || [];
            for (const child of children) {
                if (!visited.has(child)) {
                    stack.push(child);
                }
            }
        }

        return false;
    }

    private async removeConnection(document: vscode.TextDocument, fromId: string, toId: string): Promise<void> {
        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;
            const toStage = pipeline.stages.find(s => s.id === toId);

            if (!toStage || !toStage.depends_on) return;

            toStage.depends_on = toStage.depends_on.filter(d => d !== fromId);
            if (toStage.depends_on.length === 0) {
                delete toStage.depends_on;
            }

            await this.updateDocument(document, pipeline);
        } catch {
            vscode.window.showErrorMessage('Failed to remove connection');
        }
    }

    private async reconnectEdge(
        document: vscode.TextDocument,
        oldFromId: string,
        oldToId: string,
        newFromId: string,
        newToId: string
    ): Promise<void> {
        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;

            // Validate new nodes exist
            const newFromStage = pipeline.stages.find(s => s.id === newFromId);
            const newToStage = pipeline.stages.find(s => s.id === newToId);
            if (!newFromStage || !newToStage) {
                vscode.window.showErrorMessage('Invalid reconnection target');
                return;
            }

            // Check if new connection would create a cycle
            if (newFromId !== oldFromId || newToId !== oldToId) {
                // Temporarily remove old connection for cycle check
                const oldToStage = pipeline.stages.find(s => s.id === oldToId);
                if (oldToStage?.depends_on) {
                    oldToStage.depends_on = oldToStage.depends_on.filter(d => d !== oldFromId);
                }

                if (this.wouldCreateCycle(pipeline, newFromId, newToId)) {
                    vscode.window.showWarningMessage(
                        `Cannot reconnect: this would create a circular dependency`
                    );
                    return;
                }

                // Check if connection already exists
                if (newToStage.depends_on?.includes(newFromId)) {
                    vscode.window.showWarningMessage('This connection already exists');
                    return;
                }
            }

            // Remove old connection
            const oldToStage = pipeline.stages.find(s => s.id === oldToId);
            if (oldToStage?.depends_on) {
                oldToStage.depends_on = oldToStage.depends_on.filter(d => d !== oldFromId);
                if (oldToStage.depends_on.length === 0) {
                    delete oldToStage.depends_on;
                }
            }

            // Add new connection
            if (!newToStage.depends_on) {
                newToStage.depends_on = [];
            }
            if (!newToStage.depends_on.includes(newFromId)) {
                newToStage.depends_on.push(newFromId);
            }

            await this.updateDocument(document, pipeline);
        } catch {
            vscode.window.showErrorMessage('Failed to reconnect edge');
        }
    }

    private async updatePositions(
        document: vscode.TextDocument,
        positions: Record<string, NodePosition>
    ): Promise<void> {
        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;

            for (const stage of pipeline.stages) {
                if (positions[stage.id]) {
                    stage.position = positions[stage.id];
                }
            }

            await this.updateDocument(document, pipeline);
        } catch {
            // Silently ignore position update failures
        }
    }

    private async deleteStage(document: vscode.TextDocument, stageId: string): Promise<void> {
        const confirm = await vscode.window.showWarningMessage(
            `Delete stage "${stageId}"?`,
            { modal: true },
            'Delete'
        );

        if (confirm !== 'Delete') return;

        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;

            pipeline.stages = pipeline.stages.filter(s => s.id !== stageId);

            for (const stage of pipeline.stages) {
                if (stage.depends_on) {
                    stage.depends_on = stage.depends_on.filter(d => d !== stageId);
                    if (stage.depends_on.length === 0) {
                        delete stage.depends_on;
                    }
                }
            }

            await this.updateDocument(document, pipeline);
            vscode.window.showInformationMessage(`Deleted stage "${stageId}"`);
        } catch {
            vscode.window.showErrorMessage('Failed to delete stage');
        }
    }

    private async deleteStages(document: vscode.TextDocument, stageIds: string[]): Promise<void> {
        if (stageIds.length === 0) return;

        const confirm = await vscode.window.showWarningMessage(
            `Delete ${stageIds.length} stage(s)?`,
            { modal: true },
            'Delete'
        );

        if (confirm !== 'Delete') return;

        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;
            const idsToDelete = new Set(stageIds);

            pipeline.stages = pipeline.stages.filter(s => !idsToDelete.has(s.id));

            for (const stage of pipeline.stages) {
                if (stage.depends_on) {
                    stage.depends_on = stage.depends_on.filter(d => !idsToDelete.has(d));
                    if (stage.depends_on.length === 0) {
                        delete stage.depends_on;
                    }
                }
            }

            await this.updateDocument(document, pipeline);
            vscode.window.showInformationMessage(`Deleted ${stageIds.length} stage(s)`);
        } catch {
            vscode.window.showErrorMessage('Failed to delete stages');
        }
    }

    private async duplicateStage(document: vscode.TextDocument, stageId: string): Promise<void> {
        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;
            const sourceStage = pipeline.stages.find(s => s.id === stageId);

            if (!sourceStage) return;

            // Generate new ID
            let newId = `${stageId}_copy`;
            let counter = 1;
            const existingIds = new Set(pipeline.stages.map(s => s.id));
            while (existingIds.has(newId)) {
                newId = `${stageId}_copy_${counter}`;
                counter++;
            }

            // Clone stage
            const newStage: PipelineStage = {
                ...JSON.parse(JSON.stringify(sourceStage)),
                id: newId,
                position: sourceStage.position ? {
                    x: sourceStage.position.x + 50,
                    y: sourceStage.position.y + 50
                } : undefined
            };

            pipeline.stages.push(newStage);
            await this.updateDocument(document, pipeline);
            vscode.window.showInformationMessage(`Duplicated as "${newId}"`);
        } catch {
            vscode.window.showErrorMessage('Failed to duplicate stage');
        }
    }

    private async addStageWithComponent(
        document: vscode.TextDocument,
        componentType: string,
        position: NodePosition
    ): Promise<void> {
        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;

            // Generate ID from component type
            let stageId = componentType.replace(/-/g, '_');
            let counter = 1;
            const existingIds = new Set(pipeline.stages.map(s => s.id));
            while (existingIds.has(stageId)) {
                stageId = `${componentType.replace(/-/g, '_')}_${counter}`;
                counter++;
            }

            const newStage: PipelineStage = {
                id: stageId,
                component_type: componentType,
                config: {},
                position
            };

            pipeline.stages.push(newStage);
            await this.updateDocument(document, pipeline);
            vscode.window.showInformationMessage(`Added stage "${stageId}"`);
        } catch {
            vscode.window.showErrorMessage('Failed to add stage');
        }
    }

    private async updateDocument(document: vscode.TextDocument, pipeline: PipelineFile): Promise<void> {
        const uri = document.uri.toString();
        const edit = new vscode.WorkspaceEdit();
        edit.replace(
            document.uri,
            new vscode.Range(0, 0, document.lineCount, 0),
            JSON.stringify(pipeline, null, 2)
        );
        // Mark this document as being edited by DAG canvas
        DagCanvasProvider._editingDocuments.add(uri);
        await vscode.workspace.applyEdit(edit);
        // Remove from set after a delay to ensure event handler sees it
        setTimeout(() => {
            DagCanvasProvider._editingDocuments.delete(uri);
        }, 500);
    }

    private getHtml(webview: vscode.Webview, pipeline: PipelineFile | null): string {
        const stages = pipeline?.stages || [];
        const stagesJson = JSON.stringify(stages);

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, height=device-height">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    background: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                    font-family: var(--vscode-font-family);
                    overflow: hidden;
                    width: 100vw;
                    height: 100vh;
                    outline: none;
                }
                body:focus {
                    outline: none;
                }

                /* Toolbar */
                #toolbar {
                    position: fixed;
                    top: 8px;
                    left: 8px;
                    display: flex;
                    gap: 8px;
                    z-index: 100;
                }
                .toolbar-btn {
                    padding: 6px 12px;
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                    font-size: 12px;
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }
                .toolbar-btn:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                .toolbar-btn.secondary {
                    background: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                }

                /* Canvas */
                #canvas {
                    width: 100%;
                    height: 100%;
                    cursor: grab;
                    background-color: var(--vscode-editor-background);
                }
                #canvas.dragging {
                    cursor: grabbing;
                }
                #canvas.connecting {
                    cursor: crosshair;
                }

                /* Grid pattern */
                .grid-pattern {
                    stroke: var(--vscode-panel-border);
                    stroke-width: 0.5;
                    opacity: 0.3;
                }
                .grid-pattern-major {
                    stroke: var(--vscode-panel-border);
                    stroke-width: 1;
                    opacity: 0.5;
                }

                /* Canvas border frame */
                .canvas-frame {
                    fill: none;
                    stroke: var(--vscode-panel-border);
                    stroke-width: 2;
                    rx: 8;
                }

                /* Nodes */
                .node {
                    cursor: pointer;
                    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
                }
                .node rect.node-bg {
                    fill: var(--vscode-editor-background);
                    stroke: var(--vscode-panel-border);
                    stroke-width: 1.5;
                    rx: 8;
                    transition: stroke 0.15s, stroke-width 0.15s, fill 0.15s, filter 0.15s;
                }
                .node:hover {
                    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.25));
                }
                .node:hover rect.node-bg {
                    stroke: var(--vscode-focusBorder);
                    stroke-width: 2;
                }
                .node.selected {
                    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
                }
                .node.selected rect.node-bg {
                    stroke: var(--vscode-button-background);
                    stroke-width: 2.5;
                    fill: var(--vscode-list-activeSelectionBackground);
                }
                .node.dragging {
                    cursor: grabbing;
                    opacity: 0.85;
                    filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.35));
                }
                .node-label {
                    fill: var(--vscode-editor-foreground);
                    font-size: 12px;
                    font-weight: 600;
                    pointer-events: none;
                }
                .node-type {
                    fill: var(--vscode-descriptionForeground);
                    font-size: 10px;
                    pointer-events: none;
                }

                /* Connection ports */
                .port {
                    fill: var(--vscode-button-background);
                    stroke: var(--vscode-editor-background);
                    stroke-width: 2;
                    cursor: crosshair;
                    opacity: 0;
                    transition: opacity 0.15s, r 0.15s;
                }
                .node:hover .port, .port:hover {
                    opacity: 1;
                }
                .port:hover {
                    r: 8;
                }
                .port.connecting {
                    opacity: 1;
                    fill: var(--vscode-textLink-foreground);
                    r: 8;
                }
                /* Show all input ports when canvas is in connecting mode */
                #canvas.connecting .input-port {
                    opacity: 0.7;
                }
                #canvas.connecting .node:hover .input-port {
                    opacity: 1;
                    r: 8;
                }
                /* Show all output ports when reconnecting source */
                #canvas.connecting .output-port {
                    opacity: 0.7;
                }
                #canvas.connecting .node:hover .output-port {
                    opacity: 1;
                    r: 8;
                }

                /* Edges */
                .edge {
                    fill: none;
                    stroke: var(--vscode-textLink-foreground);
                    stroke-width: 2;
                    pointer-events: stroke;
                    cursor: pointer;
                    transition: stroke 0.15s, stroke-width 0.15s;
                }
                .edge:hover {
                    stroke: var(--vscode-textLink-activeForeground, var(--vscode-textLink-foreground));
                    stroke-width: 3;
                }
                .edge.selected {
                    stroke: var(--vscode-button-background);
                    stroke-width: 3;
                }
                .edge.selected:hover {
                    stroke: var(--vscode-errorForeground);
                    stroke-width: 4;
                }
                .edge-temp {
                    fill: none;
                    stroke: var(--vscode-textLink-foreground);
                    stroke-width: 2;
                    stroke-dasharray: 5, 5;
                    pointer-events: none;
                }

                /* Edge reconnection handles */
                .edge-handle {
                    fill: var(--vscode-button-background);
                    stroke: var(--vscode-editor-background);
                    stroke-width: 2;
                    cursor: grab;
                    opacity: 0;
                    transition: opacity 0.15s, r 0.15s;
                }
                .edge-group:hover .edge-handle {
                    opacity: 0.8;
                }
                .edge.selected + .edge-handle,
                .edge-group.selected .edge-handle {
                    opacity: 1;
                }
                .edge-handle:hover {
                    opacity: 1;
                    r: 8;
                }
                .edge-handle.dragging {
                    opacity: 1;
                    cursor: grabbing;
                }
                #arrowhead {
                    fill: var(--vscode-textLink-foreground);
                }
                #arrowhead-selected {
                    fill: var(--vscode-button-background);
                }

                /* Context Menu */
                .context-menu {
                    position: fixed;
                    background: var(--vscode-menu-background);
                    border: 1px solid var(--vscode-menu-border);
                    border-radius: 4px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                    min-width: 160px;
                    z-index: 1000;
                    padding: 4px 0;
                    display: none;
                }
                .context-menu.visible {
                    display: block;
                }
                .context-menu-item {
                    padding: 6px 12px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 13px;
                    color: var(--vscode-menu-foreground);
                }
                .context-menu-item:hover {
                    background: var(--vscode-menu-selectionBackground);
                    color: var(--vscode-menu-selectionForeground);
                }
                .context-menu-item.disabled {
                    opacity: 0.5;
                    pointer-events: none;
                }
                .context-menu-separator {
                    height: 1px;
                    background: var(--vscode-menu-separatorBackground);
                    margin: 4px 0;
                }
                .context-menu-item .shortcut {
                    margin-left: auto;
                    opacity: 0.6;
                    font-size: 11px;
                }

                /* Selection box */
                .selection-box {
                    fill: var(--vscode-editor-selectionBackground);
                    stroke: var(--vscode-focusBorder);
                    stroke-width: 1;
                    opacity: 0.3;
                }

                /* Drop zone highlight */
                .drop-zone-active {
                    background: var(--vscode-editor-selectionBackground);
                }

                /* Empty/Error states */
                .empty-state, .error-state {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    text-align: center;
                }
                .empty-state {
                    color: var(--vscode-descriptionForeground);
                }
                .error-state {
                    color: var(--vscode-errorForeground);
                }
                .empty-state h2, .error-state h2 {
                    margin-bottom: 12px;
                    font-weight: 500;
                }

                /* Status hints */
                .status-hint {
                    position: fixed;
                    bottom: 8px;
                    left: 8px;
                    background: var(--vscode-editorWidget-background);
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                    color: var(--vscode-descriptionForeground);
                    display: none;
                }
                .status-hint.visible {
                    display: block;
                }

                /* Minimap */
                #minimap {
                    position: fixed;
                    bottom: 8px;
                    right: 8px;
                    width: 150px;
                    height: 100px;
                    background: var(--vscode-editorWidget-background);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                    overflow: hidden;
                }
                #minimap svg {
                    width: 100%;
                    height: 100%;
                }
                .minimap-viewport {
                    fill: var(--vscode-editor-selectionBackground);
                    stroke: var(--vscode-focusBorder);
                    stroke-width: 1;
                    opacity: 0.5;
                }
            </style>
        </head>
        <body tabindex="0">
            <div id="toolbar">
                <button class="toolbar-btn" onclick="addStage()" title="Add Stage (A)">
                    <span>+ Add Stage</span>
                </button>
                <button class="toolbar-btn secondary" onclick="fitView()" title="Fit View (F)">
                    <span>Fit View</span>
                </button>
                <button class="toolbar-btn secondary" onclick="openJson()" title="Edit JSON Source">
                    <span>Edit JSON</span>
                </button>
            </div>

            <div id="context-menu" class="context-menu"></div>

            <div id="status-hint" class="status-hint"></div>

            ${!pipeline ? `
                <div class="error-state">
                    <h2>Invalid Pipeline JSON</h2>
                    <p>Fix the syntax errors in the JSON file</p>
                    <button class="toolbar-btn" onclick="openJson()" style="margin-top: 12px;">Edit JSON</button>
                </div>
            ` : stages.length === 0 ? `
                <div class="empty-state">
                    <h2>Empty Pipeline</h2>
                    <p>Add stages to build your pipeline</p>
                    <p style="margin-top: 8px; font-size: 12px;">Right-click or press A to add a stage</p>
                    <button class="toolbar-btn" onclick="addStage()" style="margin-top: 12px;">+ Add Stage</button>
                </div>
            ` : `
                <svg id="canvas">
                    <defs>
                        <!-- Grid pattern -->
                        <pattern id="smallGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                            <path d="M 20 0 L 0 0 0 20" fill="none" class="grid-pattern"/>
                        </pattern>
                        <pattern id="largeGrid" width="100" height="100" patternUnits="userSpaceOnUse">
                            <rect width="100" height="100" fill="url(#smallGrid)"/>
                            <path d="M 100 0 L 0 0 0 100" fill="none" class="grid-pattern-major"/>
                        </pattern>
                        <!-- Arrowheads -->
                        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" />
                        </marker>
                        <marker id="arrowhead-selected" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="var(--vscode-button-background)"/>
                        </marker>
                    </defs>
                    <!-- Grid background -->
                    <rect id="grid-bg" width="100%" height="100%" fill="url(#largeGrid)" />
                    <g id="transform">
                        <g id="edges"></g>
                        <g id="nodes"></g>
                        <path id="temp-edge" class="edge-temp" d="" style="display: none;"></path>
                        <rect id="selection-box" class="selection-box" style="display: none;"></rect>
                    </g>
                </svg>

                <div id="minimap">
                    <svg id="minimap-svg"></svg>
                </div>
            `}

            <script>
                const vscode = acquireVsCodeApi();
                const stages = ${stagesJson};
                const NODE_WIDTH = 180;
                const NODE_HEIGHT = 70;
                const PORT_RADIUS = 6;
                const GRID_X = 220;
                const GRID_Y = 100;

                // State
                let selectedNodes = new Set();
                let selectedEdge = null; // { from: string, to: string } or null
                let pan = { x: 50, y: 50 };
                let zoom = 1;
                let isPanning = false;
                let isDraggingNode = false;
                let isSelecting = false;
                let isConnecting = false;
                let isReconnecting = false; // Edge reconnection state
                let reconnectingEdge = null; // { from: string, to: string, end: 'source' | 'target' }
                let lastMouse = { x: 0, y: 0 };
                let dragStartPos = {};
                let connectionSource = null;
                let selectionStart = { x: 0, y: 0 };
                let positions = {};

                // Calculate node positions using simple layered layout
                function calculatePositions() {
                    const result = {};
                    const deps = new Map();
                    const reverseDeps = new Map();

                    for (const stage of stages) {
                        deps.set(stage.id, stage.depends_on || []);
                        if (!reverseDeps.has(stage.id)) {
                            reverseDeps.set(stage.id, []);
                        }
                        for (const d of (stage.depends_on || [])) {
                            if (!reverseDeps.has(d)) {
                                reverseDeps.set(d, []);
                            }
                            reverseDeps.get(d).push(stage.id);
                        }
                    }

                    const layers = [];
                    const visited = new Set();

                    function getLayer(id) {
                        if (visited.has(id)) return -1;
                        visited.add(id);

                        const stageDeps = deps.get(id) || [];
                        let maxDepLayer = -1;

                        for (const d of stageDeps) {
                            const depLayer = getLayer(d);
                            if (depLayer !== -1) {
                                maxDepLayer = Math.max(maxDepLayer, depLayer);
                            }
                        }

                        const layer = maxDepLayer + 1;
                        while (layers.length <= layer) {
                            layers.push([]);
                        }
                        layers[layer].push(id);
                        return layer;
                    }

                    for (const stage of stages) {
                        getLayer(stage.id);
                    }

                    for (let layerIdx = 0; layerIdx < layers.length; layerIdx++) {
                        const layer = layers[layerIdx];
                        const layerHeight = layer.length * GRID_Y;
                        const startY = -layerHeight / 2 + GRID_Y / 2;

                        for (let i = 0; i < layer.length; i++) {
                            const id = layer[i];
                            const stage = stages.find(s => s.id === id);

                            if (stage?.position) {
                                result[id] = { ...stage.position };
                            } else {
                                result[id] = {
                                    x: layerIdx * GRID_X,
                                    y: startY + i * GRID_Y
                                };
                            }
                        }
                    }

                    return result;
                }

                // Transform screen coordinates to canvas coordinates
                function screenToCanvas(screenX, screenY) {
                    return {
                        x: (screenX - pan.x) / zoom,
                        y: (screenY - pan.y) / zoom
                    };
                }

                // Render the DAG
                function render(recalculatePositions = true) {
                    const canvas = document.getElementById('canvas');
                    if (!canvas || stages.length === 0) return;

                    // Only recalculate positions if not dragging
                    if (recalculatePositions && !isDraggingNode) {
                        positions = calculatePositions();
                    }
                    const edgesGroup = document.getElementById('edges');
                    const nodesGroup = document.getElementById('nodes');

                    edgesGroup.innerHTML = '';
                    nodesGroup.innerHTML = '';

                    // Apply transform
                    const transform = document.getElementById('transform');
                    transform.setAttribute('transform', \`translate(\${pan.x}, \${pan.y}) scale(\${zoom})\`);

                    // Render edges
                    for (const stage of stages) {
                        if (!stage.depends_on) continue;

                        for (const dep of stage.depends_on) {
                            const fromPos = positions[dep];
                            const toPos = positions[stage.id];
                            if (!fromPos || !toPos) continue;

                            // Create a group for edge and its handles
                            const edgeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                            edgeGroup.setAttribute('class', 'edge-group');

                            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                            const startX = fromPos.x + NODE_WIDTH;
                            const startY = fromPos.y + NODE_HEIGHT / 2;
                            const endX = toPos.x;
                            const endY = toPos.y + NODE_HEIGHT / 2;

                            const midX = (startX + endX) / 2;
                            path.setAttribute('d', \`M \${startX} \${startY} C \${midX} \${startY}, \${midX} \${endY}, \${endX} \${endY}\`);

                            // Check if this edge is selected
                            const isSelected = selectedEdge && selectedEdge.from === dep && selectedEdge.to === stage.id;
                            path.setAttribute('class', 'edge' + (isSelected ? ' selected' : ''));
                            path.setAttribute('marker-end', isSelected ? 'url(#arrowhead-selected)' : 'url(#arrowhead)');
                            path.dataset.from = dep;
                            path.dataset.to = stage.id;

                            path.addEventListener('contextmenu', (e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                // Select this edge first
                                selectEdge(dep, stage.id);
                                showEdgeContextMenu(e, dep, stage.id);
                            });

                            path.addEventListener('click', (e) => {
                                e.stopPropagation();
                                // Select this edge
                                selectEdge(dep, stage.id);
                            });

                            edgeGroup.appendChild(path);

                            // Add reconnection handles (source and target)
                            const sourceHandle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                            sourceHandle.setAttribute('class', 'edge-handle');
                            sourceHandle.setAttribute('cx', startX);
                            sourceHandle.setAttribute('cy', startY);
                            sourceHandle.setAttribute('r', 6);
                            sourceHandle.dataset.from = dep;
                            sourceHandle.dataset.to = stage.id;
                            sourceHandle.dataset.handleEnd = 'source';

                            const targetHandle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                            targetHandle.setAttribute('class', 'edge-handle');
                            targetHandle.setAttribute('cx', endX);
                            targetHandle.setAttribute('cy', endY);
                            targetHandle.setAttribute('r', 6);
                            targetHandle.dataset.from = dep;
                            targetHandle.dataset.to = stage.id;
                            targetHandle.dataset.handleEnd = 'target';

                            // Handle mousedown on handles to start reconnection
                            sourceHandle.addEventListener('mousedown', (e) => {
                                e.stopPropagation();
                                e.preventDefault();
                                startEdgeReconnection(dep, stage.id, 'source', e);
                            });

                            targetHandle.addEventListener('mousedown', (e) => {
                                e.stopPropagation();
                                e.preventDefault();
                                startEdgeReconnection(dep, stage.id, 'target', e);
                            });

                            edgeGroup.appendChild(sourceHandle);
                            edgeGroup.appendChild(targetHandle);

                            if (isSelected) {
                                edgeGroup.classList.add('selected');
                            }

                            edgesGroup.appendChild(edgeGroup);
                        }
                    }

                    // Render nodes
                    for (const stage of stages) {
                        const pos = positions[stage.id];
                        if (!pos) continue;

                        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                        g.setAttribute('class', 'node' + (selectedNodes.has(stage.id) ? ' selected' : ''));
                        g.setAttribute('transform', \`translate(\${pos.x}, \${pos.y})\`);
                        g.dataset.id = stage.id;

                        // Background rect
                        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                        rect.setAttribute('class', 'node-bg');
                        rect.setAttribute('width', NODE_WIDTH);
                        rect.setAttribute('height', NODE_HEIGHT);
                        g.appendChild(rect);

                        // Label
                        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                        label.setAttribute('class', 'node-label');
                        label.setAttribute('x', 12);
                        label.setAttribute('y', 28);
                        label.textContent = stage.id.length > 20 ? stage.id.substring(0, 18) + '...' : stage.id;
                        g.appendChild(label);

                        // Type
                        const type = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                        type.setAttribute('class', 'node-type');
                        type.setAttribute('x', 12);
                        type.setAttribute('y', 48);
                        type.textContent = stage.component_type.length > 22
                            ? stage.component_type.substring(0, 20) + '...'
                            : stage.component_type;
                        g.appendChild(type);

                        // Input port (left)
                        const inputPort = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                        inputPort.setAttribute('class', 'port input-port');
                        inputPort.setAttribute('cx', 0);
                        inputPort.setAttribute('cy', NODE_HEIGHT / 2);
                        inputPort.setAttribute('r', PORT_RADIUS);
                        inputPort.dataset.stageId = stage.id;
                        inputPort.dataset.portType = 'input';
                        g.appendChild(inputPort);

                        // Output port (right)
                        const outputPort = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                        outputPort.setAttribute('class', 'port output-port');
                        outputPort.setAttribute('cx', NODE_WIDTH);
                        outputPort.setAttribute('cy', NODE_HEIGHT / 2);
                        outputPort.setAttribute('r', PORT_RADIUS);
                        outputPort.dataset.stageId = stage.id;
                        outputPort.dataset.portType = 'output';
                        g.appendChild(outputPort);

                        // Event handlers
                        setupNodeEventHandlers(g, stage);

                        nodesGroup.appendChild(g);
                    }

                    renderMinimap();
                }

                function setupNodeEventHandlers(g, stage) {
                    // Mouse down - start drag or select
                    g.addEventListener('mousedown', (e) => {
                        if (e.target.classList.contains('port')) {
                            // Start connection from output port
                            if (e.target.dataset.portType === 'output') {
                                e.stopPropagation();
                                e.preventDefault();
                                startConnection(stage.id, e);
                            }
                            return;
                        }

                        e.stopPropagation();
                        e.preventDefault();

                        // Deselect edge when selecting nodes
                        deselectEdge();

                        if (e.shiftKey) {
                            // Toggle selection
                            if (selectedNodes.has(stage.id)) {
                                selectedNodes.delete(stage.id);
                            } else {
                                selectedNodes.add(stage.id);
                            }
                            render();
                        } else if (!selectedNodes.has(stage.id)) {
                            // Select only this node
                            selectedNodes.clear();
                            selectedNodes.add(stage.id);
                            render();
                        }

                        // Start dragging - IMPORTANT: set lastMouse for the mousemove handler
                        lastMouse = { x: e.clientX, y: e.clientY };
                        dragStartPos = {};
                        for (const id of selectedNodes) {
                            dragStartPos[id] = { ...positions[id] };
                        }

                        g.classList.add('dragging');
                        isDraggingNode = true;
                    });

                    // Click - select
                    g.addEventListener('click', (e) => {
                        if (e.target.classList.contains('port')) return;
                        e.stopPropagation();

                        if (!e.shiftKey && !isDraggingNode) {
                            selectedNodes.clear();
                            selectedNodes.add(stage.id);
                            render();
                            vscode.postMessage({ type: 'selectStage', stageId: stage.id });
                        }
                    });

                    // Double click - edit config
                    g.addEventListener('dblclick', (e) => {
                        e.stopPropagation();
                        vscode.postMessage({ type: 'editStageConfig', stageId: stage.id });
                    });

                    // Context menu
                    g.addEventListener('contextmenu', (e) => {
                        e.preventDefault();
                        e.stopPropagation();

                        if (!selectedNodes.has(stage.id)) {
                            selectedNodes.clear();
                            selectedNodes.add(stage.id);
                            render();
                        }

                        showNodeContextMenu(e, stage.id);
                    });

                    // Port hover and click for connections
                    const inputPort = g.querySelector('.input-port');
                    const outputPort = g.querySelector('.output-port');

                    inputPort.addEventListener('mouseenter', () => {
                        if ((isConnecting && connectionSource !== stage.id) ||
                            (isReconnecting && reconnectingEdge?.end === 'target')) {
                            inputPort.classList.add('connecting');
                        }
                    });
                    inputPort.addEventListener('mouseleave', () => {
                        inputPort.classList.remove('connecting');
                    });
                    inputPort.addEventListener('mouseup', (e) => {
                        if (isConnecting && connectionSource && connectionSource !== stage.id) {
                            e.stopPropagation();
                            e.preventDefault();
                            completeConnection(stage.id);
                        } else if (isReconnecting && reconnectingEdge?.end === 'target') {
                            e.stopPropagation();
                            e.preventDefault();
                            completeReconnection(stage.id);
                        }
                    });
                    // Also handle click on input port to complete connection
                    inputPort.addEventListener('click', (e) => {
                        if (isConnecting && connectionSource && connectionSource !== stage.id) {
                            e.stopPropagation();
                            e.preventDefault();
                            completeConnection(stage.id);
                        } else if (isReconnecting && reconnectingEdge?.end === 'target') {
                            e.stopPropagation();
                            e.preventDefault();
                            completeReconnection(stage.id);
                        }
                    });

                    // Output port event handlers
                    outputPort.addEventListener('mouseenter', () => {
                        if (isReconnecting && reconnectingEdge?.end === 'source') {
                            outputPort.classList.add('connecting');
                        }
                    });
                    outputPort.addEventListener('mouseleave', () => {
                        outputPort.classList.remove('connecting');
                    });
                    outputPort.addEventListener('mouseup', (e) => {
                        if (isReconnecting && reconnectingEdge?.end === 'source') {
                            e.stopPropagation();
                            e.preventDefault();
                            completeReconnection(stage.id);
                        }
                    });
                    // Make output port more responsive - also handle click
                    outputPort.addEventListener('click', (e) => {
                        if (isReconnecting && reconnectingEdge?.end === 'source') {
                            e.stopPropagation();
                            e.preventDefault();
                            completeReconnection(stage.id);
                        } else if (!isConnecting && !isReconnecting) {
                            e.stopPropagation();
                            e.preventDefault();
                            startConnection(stage.id, e);
                        }
                    });
                }

                // Connection handling
                function startConnection(sourceId, e) {
                    connectionSource = sourceId;
                    isConnecting = true;

                    const canvas = document.getElementById('canvas');
                    canvas.classList.add('connecting');

                    const tempEdge = document.getElementById('temp-edge');
                    tempEdge.style.display = 'block';

                    updateTempEdge(e);
                    showHint('Drag to a node to connect, or press Escape to cancel');
                }

                function updateTempEdge(e) {
                    if (!isConnecting || !connectionSource) return;

                    const pos = positions[connectionSource];
                    if (!pos) return;

                    const startX = pos.x + NODE_WIDTH;
                    const startY = pos.y + NODE_HEIGHT / 2;

                    const canvasPos = screenToCanvas(e.clientX, e.clientY);
                    const endX = canvasPos.x;
                    const endY = canvasPos.y;

                    const midX = (startX + endX) / 2;
                    const tempEdge = document.getElementById('temp-edge');
                    tempEdge.setAttribute('d', \`M \${startX} \${startY} C \${midX} \${startY}, \${midX} \${endY}, \${endX} \${endY}\`);
                }

                function completeConnection(targetId) {
                    if (connectionSource && targetId && connectionSource !== targetId) {
                        vscode.postMessage({
                            type: 'addConnection',
                            from: connectionSource,
                            to: targetId
                        });
                    }
                    cancelConnection();
                }

                function cancelConnection() {
                    connectionSource = null;
                    isConnecting = false;

                    const canvas = document.getElementById('canvas');
                    canvas?.classList.remove('connecting');

                    const tempEdge = document.getElementById('temp-edge');
                    if (tempEdge) tempEdge.style.display = 'none';

                    hideHint();
                }

                // Edge reconnection functions
                function startEdgeReconnection(fromId, toId, end, e) {
                    isReconnecting = true;
                    reconnectingEdge = { from: fromId, to: toId, end: end };

                    const canvas = document.getElementById('canvas');
                    canvas.classList.add('connecting');

                    const tempEdge = document.getElementById('temp-edge');
                    tempEdge.style.display = 'block';

                    updateReconnectionEdge(e);

                    if (end === 'source') {
                        showHint('Drag to a node\\'s output port to reconnect the source, or press Escape to cancel');
                    } else {
                        showHint('Drag to a node\\'s input port to reconnect the target, or press Escape to cancel');
                    }
                }

                function updateReconnectionEdge(e) {
                    if (!isReconnecting || !reconnectingEdge) return;

                    const canvasPos = screenToCanvas(e.clientX, e.clientY);
                    const tempEdge = document.getElementById('temp-edge');

                    if (reconnectingEdge.end === 'source') {
                        // Reconnecting source: fixed end is the target (input port)
                        const toPos = positions[reconnectingEdge.to];
                        if (!toPos) return;

                        const endX = toPos.x;
                        const endY = toPos.y + NODE_HEIGHT / 2;
                        const startX = canvasPos.x;
                        const startY = canvasPos.y;

                        const midX = (startX + endX) / 2;
                        tempEdge.setAttribute('d', \`M \${startX} \${startY} C \${midX} \${startY}, \${midX} \${endY}, \${endX} \${endY}\`);
                    } else {
                        // Reconnecting target: fixed end is the source (output port)
                        const fromPos = positions[reconnectingEdge.from];
                        if (!fromPos) return;

                        const startX = fromPos.x + NODE_WIDTH;
                        const startY = fromPos.y + NODE_HEIGHT / 2;
                        const endX = canvasPos.x;
                        const endY = canvasPos.y;

                        const midX = (startX + endX) / 2;
                        tempEdge.setAttribute('d', \`M \${startX} \${startY} C \${midX} \${startY}, \${midX} \${endY}, \${endX} \${endY}\`);
                    }
                }

                function completeReconnection(newNodeId) {
                    if (!isReconnecting || !reconnectingEdge) return;

                    const oldFrom = reconnectingEdge.from;
                    const oldTo = reconnectingEdge.to;
                    const end = reconnectingEdge.end;

                    // Don't reconnect to the same node or self-connections
                    if (end === 'source' && (newNodeId === oldFrom || newNodeId === oldTo)) {
                        cancelReconnection();
                        return;
                    }
                    if (end === 'target' && (newNodeId === oldTo || newNodeId === oldFrom)) {
                        cancelReconnection();
                        return;
                    }

                    // Send reconnection message
                    vscode.postMessage({
                        type: 'reconnectEdge',
                        oldFrom: oldFrom,
                        oldTo: oldTo,
                        newFrom: end === 'source' ? newNodeId : oldFrom,
                        newTo: end === 'target' ? newNodeId : oldTo
                    });

                    cancelReconnection();
                }

                function cancelReconnection() {
                    isReconnecting = false;
                    reconnectingEdge = null;

                    const canvas = document.getElementById('canvas');
                    canvas?.classList.remove('connecting');

                    const tempEdge = document.getElementById('temp-edge');
                    if (tempEdge) tempEdge.style.display = 'none';

                    hideHint();
                }

                // Context menus
                function showNodeContextMenu(e, stageId) {
                    const menu = document.getElementById('context-menu');
                    const isMulti = selectedNodes.size > 1;

                    menu.innerHTML = \`
                        <div class="context-menu-item" onclick="editConfig('\${stageId}')">
                            Edit Configuration
                        </div>
                        <div class="context-menu-item" onclick="startConnectionFromMenu('\${stageId}')">
                            Connect To...
                        </div>
                        <div class="context-menu-separator"></div>
                        <div class="context-menu-item" onclick="duplicateNode('\${stageId}')">
                            Duplicate <span class="shortcut">Ctrl+D</span>
                        </div>
                        <div class="context-menu-item" onclick="setBreakpoint('\${stageId}')">
                            Toggle Breakpoint <span class="shortcut">F9</span>
                        </div>
                        <div class="context-menu-separator"></div>
                        <div class="context-menu-item" onclick="runFromStage('\${stageId}')">
                            Run From Here
                        </div>
                        <div class="context-menu-separator"></div>
                        <div class="context-menu-item" onclick="deleteSelected()" style="color: var(--vscode-errorForeground);">
                            Delete\${isMulti ? ' (' + selectedNodes.size + ')' : ''} <span class="shortcut">Del</span>
                        </div>
                    \`;

                    showContextMenu(menu, e.clientX, e.clientY);
                }

                function showEdgeContextMenu(e, fromId, toId) {
                    const menu = document.getElementById('context-menu');

                    menu.innerHTML = \`
                        <div class="context-menu-item" onclick="removeEdge('\${fromId}', '\${toId}')" style="color: var(--vscode-errorForeground);">
                            Remove Connection
                        </div>
                    \`;

                    showContextMenu(menu, e.clientX, e.clientY);
                }

                function showCanvasContextMenu(e) {
                    const menu = document.getElementById('context-menu');
                    const canvasPos = screenToCanvas(e.clientX, e.clientY);
                    const posX = Math.round(canvasPos.x);
                    const posY = Math.round(canvasPos.y);

                    menu.innerHTML = \`
                        <div class="context-menu-item" onclick="addStageAt(\${posX}, \${posY})">
                            Add Stage Here <span class="shortcut">A</span>
                        </div>
                        <div class="context-menu-separator"></div>
                        <div class="context-menu-item" onclick="fitView()">
                            Fit View <span class="shortcut">F</span>
                        </div>
                        <div class="context-menu-item" onclick="resetZoom()">
                            Reset Zoom <span class="shortcut">0</span>
                        </div>
                        <div class="context-menu-separator"></div>
                        <div class="context-menu-item" onclick="selectAll()">
                            Select All <span class="shortcut">Ctrl+A</span>
                        </div>
                        <div class="context-menu-separator"></div>
                        <div class="context-menu-item" onclick="openJson()">
                            Edit JSON Source
                        </div>
                    \`;

                    showContextMenu(menu, e.clientX, e.clientY);
                }

                function showContextMenu(menu, x, y) {
                    // Position menu
                    menu.style.left = x + 'px';
                    menu.style.top = y + 'px';
                    menu.classList.add('visible');

                    // Adjust if off screen
                    const rect = menu.getBoundingClientRect();
                    if (rect.right > window.innerWidth) {
                        menu.style.left = (x - rect.width) + 'px';
                    }
                    if (rect.bottom > window.innerHeight) {
                        menu.style.top = (y - rect.height) + 'px';
                    }
                }

                function hideContextMenu() {
                    document.getElementById('context-menu')?.classList.remove('visible');
                }

                // Context menu actions
                function editConfig(stageId) {
                    hideContextMenu();
                    vscode.postMessage({ type: 'editStageConfig', stageId });
                }

                function startConnectionFromMenu(stageId) {
                    hideContextMenu();
                    connectionSource = stageId;
                    isConnecting = true;
                    document.getElementById('canvas')?.classList.add('connecting');
                    document.getElementById('temp-edge').style.display = 'block';
                    showHint('Click on a node to connect, or press Escape to cancel');
                }

                function duplicateNode(stageId) {
                    hideContextMenu();
                    vscode.postMessage({ type: 'duplicateStage', stageId });
                }

                function setBreakpoint(stageId) {
                    hideContextMenu();
                    vscode.postMessage({ type: 'setBreakpoint', stageId });
                }

                function runFromStage(stageId) {
                    hideContextMenu();
                    vscode.postMessage({ type: 'runFromStage', stageId });
                }

                function deleteSelected() {
                    hideContextMenu();
                    if (selectedNodes.size === 0) return;

                    if (selectedNodes.size === 1) {
                        vscode.postMessage({ type: 'deleteStage', stageId: Array.from(selectedNodes)[0] });
                    } else {
                        vscode.postMessage({ type: 'deleteStages', stageIds: Array.from(selectedNodes) });
                    }
                }

                function removeEdge(fromId, toId) {
                    hideContextMenu();
                    vscode.postMessage({ type: 'removeConnection', from: fromId, to: toId });
                }

                function selectEdge(fromId, toId) {
                    // Deselect nodes when selecting an edge
                    selectedNodes.clear();
                    selectedEdge = { from: fromId, to: toId };
                    render();
                    showHint('Edge selected. Press Delete to remove, or Escape to deselect.');
                }

                function deselectEdge() {
                    selectedEdge = null;
                    hideHint();
                }

                function deleteSelectedEdge() {
                    if (selectedEdge) {
                        vscode.postMessage({ type: 'removeConnection', from: selectedEdge.from, to: selectedEdge.to });
                        selectedEdge = null;
                        hideHint();
                    }
                }

                function addStageAt(x, y) {
                    hideContextMenu();
                    vscode.postMessage({ type: 'addStage' });
                }

                function selectAll() {
                    hideContextMenu();
                    selectedNodes.clear();
                    for (const stage of stages) {
                        selectedNodes.add(stage.id);
                    }
                    render();
                }

                function resetZoom() {
                    hideContextMenu();
                    zoom = 1;
                    render();
                }

                // Hint display
                function showHint(text) {
                    const hint = document.getElementById('status-hint');
                    if (hint) {
                        hint.textContent = text;
                        hint.classList.add('visible');
                    }
                }

                function hideHint() {
                    document.getElementById('status-hint')?.classList.remove('visible');
                }

                // Minimap
                function renderMinimap() {
                    const minimapSvg = document.getElementById('minimap-svg');
                    if (!minimapSvg || stages.length === 0) return;

                    // Calculate bounds
                    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
                    for (const id in positions) {
                        const pos = positions[id];
                        minX = Math.min(minX, pos.x);
                        minY = Math.min(minY, pos.y);
                        maxX = Math.max(maxX, pos.x + NODE_WIDTH);
                        maxY = Math.max(maxY, pos.y + NODE_HEIGHT);
                    }

                    const padding = 20;
                    const width = maxX - minX + padding * 2;
                    const height = maxY - minY + padding * 2;
                    const scale = Math.min(150 / width, 100 / height);

                    minimapSvg.innerHTML = '';

                    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                    g.setAttribute('transform', \`scale(\${scale}) translate(\${-minX + padding}, \${-minY + padding})\`);

                    // Draw nodes as small rectangles
                    for (const stage of stages) {
                        const pos = positions[stage.id];
                        if (!pos) continue;

                        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                        rect.setAttribute('x', pos.x);
                        rect.setAttribute('y', pos.y);
                        rect.setAttribute('width', NODE_WIDTH);
                        rect.setAttribute('height', NODE_HEIGHT);
                        rect.setAttribute('fill', selectedNodes.has(stage.id)
                            ? 'var(--vscode-button-background)'
                            : 'var(--vscode-panel-border)');
                        rect.setAttribute('rx', 4);
                        g.appendChild(rect);
                    }

                    minimapSvg.appendChild(g);
                }

                // Global event handlers
                const canvas = document.getElementById('canvas');
                if (canvas) {
                    // Pan
                    canvas.addEventListener('mousedown', (e) => {
                        if (e.target === canvas || e.target.tagName === 'svg' || e.target.id === 'transform') {
                            if (e.button === 0 && !e.shiftKey) {
                                isPanning = true;
                                lastMouse = { x: e.clientX, y: e.clientY };
                                canvas.classList.add('dragging');
                            } else if (e.button === 0 && e.shiftKey) {
                                // Selection box
                                isSelecting = true;
                                selectionStart = screenToCanvas(e.clientX, e.clientY);
                                const box = document.getElementById('selection-box');
                                box.style.display = 'block';
                                box.setAttribute('x', selectionStart.x);
                                box.setAttribute('y', selectionStart.y);
                                box.setAttribute('width', 0);
                                box.setAttribute('height', 0);
                            }
                        }
                    });

                    canvas.addEventListener('mousemove', (e) => {
                        if (isPanning) {
                            pan.x += e.clientX - lastMouse.x;
                            pan.y += e.clientY - lastMouse.y;
                            lastMouse = { x: e.clientX, y: e.clientY };
                            render();
                        } else if (isDraggingNode && Object.keys(dragStartPos).length > 0) {
                            const dx = (e.clientX - lastMouse.x) / zoom;
                            const dy = (e.clientY - lastMouse.y) / zoom;

                            for (const id of selectedNodes) {
                                if (positions[id]) {
                                    positions[id].x += dx;
                                    positions[id].y += dy;
                                }
                            }
                            lastMouse = { x: e.clientX, y: e.clientY };
                            render();
                        } else if (isSelecting) {
                            const current = screenToCanvas(e.clientX, e.clientY);
                            const box = document.getElementById('selection-box');
                            const x = Math.min(selectionStart.x, current.x);
                            const y = Math.min(selectionStart.y, current.y);
                            const w = Math.abs(current.x - selectionStart.x);
                            const h = Math.abs(current.y - selectionStart.y);
                            box.setAttribute('x', x);
                            box.setAttribute('y', y);
                            box.setAttribute('width', w);
                            box.setAttribute('height', h);
                        } else if (isConnecting) {
                            updateTempEdge(e);
                        } else if (isReconnecting) {
                            updateReconnectionEdge(e);
                        }
                    });

                    canvas.addEventListener('mouseup', (e) => {
                        if (isDraggingNode && Object.keys(dragStartPos).length > 0) {
                            // Save positions
                            const updatedPositions = {};
                            for (const id of selectedNodes) {
                                if (positions[id]) {
                                    updatedPositions[id] = positions[id];
                                }
                            }
                            if (Object.keys(updatedPositions).length > 0) {
                                vscode.postMessage({ type: 'updatePositions', positions: updatedPositions });
                            }
                        }

                        if (isSelecting) {
                            // Select nodes in box
                            const box = document.getElementById('selection-box');
                            const bx = parseFloat(box.getAttribute('x'));
                            const by = parseFloat(box.getAttribute('y'));
                            const bw = parseFloat(box.getAttribute('width'));
                            const bh = parseFloat(box.getAttribute('height'));

                            if (!e.shiftKey) selectedNodes.clear();

                            for (const stage of stages) {
                                const pos = positions[stage.id];
                                if (pos && pos.x >= bx && pos.y >= by &&
                                    pos.x + NODE_WIDTH <= bx + bw && pos.y + NODE_HEIGHT <= by + bh) {
                                    selectedNodes.add(stage.id);
                                }
                            }

                            box.style.display = 'none';
                            render();
                        }

                        isPanning = false;
                        isDraggingNode = false;
                        isSelecting = false;
                        dragStartPos = {};
                        canvas.classList.remove('dragging');
                        document.querySelectorAll('.node.dragging').forEach(n => n.classList.remove('dragging'));
                    });

                    canvas.addEventListener('mouseleave', () => {
                        isPanning = false;
                        canvas.classList.remove('dragging');
                    });

                    // Click to deselect
                    canvas.addEventListener('click', (e) => {
                        if ((e.target === canvas || e.target.tagName === 'svg' || e.target.id === 'transform' || e.target.id === 'grid-bg') && !isConnecting && !isReconnecting) {
                            selectedNodes.clear();
                            deselectEdge();
                            render();
                        }

                        if (isConnecting) {
                            cancelConnection();
                        }

                        if (isReconnecting) {
                            cancelReconnection();
                        }
                    });

                    // Context menu
                    canvas.addEventListener('contextmenu', (e) => {
                        e.preventDefault();
                        if (e.target === canvas || e.target.tagName === 'svg' || e.target.id === 'transform') {
                            showCanvasContextMenu(e);
                        }
                    });

                    // Zoom with scroll
                    canvas.addEventListener('wheel', (e) => {
                        e.preventDefault();
                        const delta = e.deltaY > 0 ? 0.9 : 1.1;
                        const newZoom = Math.max(0.25, Math.min(2, zoom * delta));

                        // Zoom towards mouse position
                        const rect = canvas.getBoundingClientRect();
                        const mouseX = e.clientX - rect.left;
                        const mouseY = e.clientY - rect.top;

                        pan.x = mouseX - (mouseX - pan.x) * (newZoom / zoom);
                        pan.y = mouseY - (mouseY - pan.y) * (newZoom / zoom);
                        zoom = newZoom;

                        render();
                    }, { passive: false });
                }

                // Hide context menu on click outside and ensure body has focus for keyboard events
                document.addEventListener('click', (e) => {
                    if (!e.target.closest('.context-menu')) {
                        hideContextMenu();
                    }
                    // Ensure body has focus for keyboard shortcuts
                    document.body.focus();
                });

                // Focus body on initial load
                document.body.focus();

                // Keyboard shortcuts
                document.addEventListener('keydown', (e) => {
                    // Don't handle shortcuts when typing in input fields
                    const target = e.target;
                    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
                        return;
                    }

                    // Escape - cancel connection/reconnection or deselect
                    if (e.key === 'Escape') {
                        if (isConnecting) {
                            cancelConnection();
                        } else if (isReconnecting) {
                            cancelReconnection();
                        } else if (selectedEdge) {
                            deselectEdge();
                            render();
                        } else {
                            selectedNodes.clear();
                            render();
                        }
                        hideContextMenu();
                    }

                    // Delete - delete selected nodes or edge
                    if (e.key === 'Delete' || e.key === 'Backspace') {
                        e.preventDefault();
                        if (selectedEdge) {
                            deleteSelectedEdge();
                        } else if (selectedNodes.size > 0) {
                            deleteSelected();
                        }
                    }

                    // A - add stage (only if not already in add mode)
                    if (e.key.toLowerCase() === 'a' && !e.ctrlKey && !e.metaKey && !e.altKey) {
                        e.preventDefault();
                        addStage();
                    }

                    // F - fit view
                    if (e.key.toLowerCase() === 'f' && !e.ctrlKey && !e.metaKey && !e.altKey) {
                        e.preventDefault();
                        fitView();
                    }

                    // 0 - reset zoom
                    if (e.key === '0' && !e.ctrlKey && !e.metaKey) {
                        e.preventDefault();
                        resetZoom();
                    }

                    // Ctrl+A - select all
                    if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
                        e.preventDefault();
                        selectAll();
                    }

                    // Ctrl+D - duplicate
                    if ((e.ctrlKey || e.metaKey) && e.key === 'd' && selectedNodes.size === 1) {
                        e.preventDefault();
                        duplicateNode(Array.from(selectedNodes)[0]);
                    }
                });

                // Global functions
                function addStage() {
                    vscode.postMessage({ type: 'addStage' });
                }

                function openJson() {
                    vscode.postMessage({ type: 'openJsonEditor' });
                }

                function fitView() {
                    if (stages.length === 0) return;

                    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
                    for (const id in positions) {
                        const pos = positions[id];
                        minX = Math.min(minX, pos.x);
                        minY = Math.min(minY, pos.y);
                        maxX = Math.max(maxX, pos.x + NODE_WIDTH);
                        maxY = Math.max(maxY, pos.y + NODE_HEIGHT);
                    }

                    const padding = 50;
                    const width = maxX - minX + padding * 2;
                    const height = maxY - minY + padding * 2;

                    const canvas = document.getElementById('canvas');
                    const canvasWidth = canvas.clientWidth;
                    const canvasHeight = canvas.clientHeight;

                    zoom = Math.min(canvasWidth / width, canvasHeight / height, 1);
                    pan.x = (canvasWidth - width * zoom) / 2 - minX * zoom + padding * zoom;
                    pan.y = (canvasHeight - height * zoom) / 2 - minY * zoom + padding * zoom;

                    render();
                }

                // Initial render
                render();

                // Fit view on first load
                setTimeout(fitView, 100);
            </script>
        </body>
        </html>`;
    }
}

/**
 * Register the DAG Canvas custom editor
 */
export function registerDagCanvasProvider(context: vscode.ExtensionContext): vscode.Disposable {
    const provider = new DagCanvasProvider(context);

    return vscode.window.registerCustomEditorProvider(
        DagCanvasProvider.viewType,
        provider,
        {
            webviewOptions: {
                retainContextWhenHidden: true
            },
            supportsMultipleEditorsPerDocument: false
        }
    );
}
