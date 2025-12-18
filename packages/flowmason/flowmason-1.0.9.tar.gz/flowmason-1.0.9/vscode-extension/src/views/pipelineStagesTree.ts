/**
 * Pipeline Stages Tree View Provider
 *
 * Shows stages of the currently active .pipeline.json file in the sidebar.
 * This is a native VSCode TreeView that updates when editing pipeline files.
 */

import * as vscode from 'vscode';

/**
 * Output destination configuration
 */
export interface OutputDestination {
    id?: string;
    type: 'webhook' | 'email' | 'database' | 'message_queue';
    name?: string;
    enabled?: boolean;
    on_success?: boolean;
    on_error?: boolean;
    error_types?: string[];
    config: Record<string, unknown>;
}

/**
 * Output configuration for pipeline or stage
 */
export interface OutputConfig {
    destinations?: OutputDestination[];
}

/**
 * Stage definition from .pipeline.json files
 */
export interface PipelineStage {
    id: string;
    component_type: string;
    config?: Record<string, unknown>;
    depends_on?: string[];
    position?: { x: number; y: number };
    output_config?: OutputConfig;
}

/**
 * JSON Schema definition for input validation
 */
export interface InputSchema {
    type?: string;
    properties?: Record<string, {
        type?: string;
        description?: string;
        default?: unknown;
        enum?: unknown[];
    }>;
    required?: string[];
}

/**
 * Pipeline definition from .pipeline.json files
 */
export interface PipelineFile {
    name: string;
    version?: string;
    description?: string;
    stages: PipelineStage[];
    input_schema?: InputSchema;
    output_config?: OutputConfig;
}

/**
 * Tree item types for the Pipeline Stages tree
 */
type StageTreeItemType = 'stage' | 'dependency' | 'config' | 'config-value' | 'empty' | 'error';

export class PipelineStagesTreeProvider implements vscode.TreeDataProvider<StageTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<StageTreeItem | undefined | null | void> =
        new vscode.EventEmitter<StageTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<StageTreeItem | undefined | null | void> =
        this._onDidChangeTreeData.event;

    private pipeline: PipelineFile | null = null;
    private document: vscode.TextDocument | null = null;
    private disposables: vscode.Disposable[] = [];

    constructor() {
        // Watch for active editor changes
        this.disposables.push(
            vscode.window.onDidChangeActiveTextEditor(editor => {
                this.updateFromEditor(editor);
            })
        );

        // Watch for document changes (live editing)
        this.disposables.push(
            vscode.workspace.onDidChangeTextDocument(event => {
                if (this.document && event.document.uri.toString() === this.document.uri.toString()) {
                    this.loadPipeline(event.document);
                }
            })
        );

        // Load initial state if a pipeline is already open
        if (vscode.window.activeTextEditor) {
            this.updateFromEditor(vscode.window.activeTextEditor);
        }
    }

    private updateFromEditor(editor: vscode.TextEditor | undefined): void {
        if (editor && editor.document.fileName.endsWith('.pipeline.json')) {
            this.loadPipeline(editor.document);
        } else {
            // Not a pipeline file - clear the tree
            this.pipeline = null;
            this.document = null;
            this._onDidChangeTreeData.fire();
        }

        // Update context for conditional UI
        vscode.commands.executeCommand(
            'setContext',
            'flowmason.pipelineOpen',
            this.pipeline !== null
        );
    }

    private loadPipeline(document: vscode.TextDocument): void {
        this.document = document;
        try {
            const content = document.getText();
            this.pipeline = JSON.parse(content) as PipelineFile;
            this._onDidChangeTreeData.fire();
        } catch (error) {
            // Invalid JSON - show error state
            this.pipeline = null;
            this._onDidChangeTreeData.fire();
        }
    }

    refresh(): void {
        if (this.document) {
            this.loadPipeline(this.document);
        }
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: StageTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: StageTreeItem): Promise<StageTreeItem[]> {
        if (!element) {
            return this.getRootChildren();
        }

        // Children of a stage
        if (element.contextValue === 'stage' && element.stage) {
            return this.getStageChildren(element.stage);
        }

        return [];
    }

    private getRootChildren(): StageTreeItem[] {
        // No pipeline file open
        if (!this.document) {
            const item = new StageTreeItem(
                'Open a .pipeline.json file',
                vscode.TreeItemCollapsibleState.None,
                'empty'
            );
            item.iconPath = new vscode.ThemeIcon('info');
            return [item];
        }

        // Invalid JSON
        if (!this.pipeline) {
            const item = new StageTreeItem(
                'Invalid pipeline JSON',
                vscode.TreeItemCollapsibleState.None,
                'error'
            );
            item.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('errorForeground'));
            return [item];
        }

        // No stages
        if (!this.pipeline.stages || this.pipeline.stages.length === 0) {
            const item = new StageTreeItem(
                'No stages defined',
                vscode.TreeItemCollapsibleState.None,
                'empty'
            );
            item.iconPath = new vscode.ThemeIcon('info');
            item.description = 'Add stages to get started';
            return [item];
        }

        // Build stage items
        return this.pipeline.stages.map(stage => this.stageToTreeItem(stage));
    }

    private stageToTreeItem(stage: PipelineStage): StageTreeItem {
        const hasChildren = (stage.depends_on && stage.depends_on.length > 0) ||
                           (stage.config && Object.keys(stage.config).length > 0);

        const item = new StageTreeItem(
            stage.id,
            hasChildren ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None,
            'stage'
        );

        item.description = stage.component_type;
        item.stage = stage;

        // Build tooltip with stage details
        const tooltipLines = [
            `**${stage.id}**`,
            `Component: ${stage.component_type}`,
        ];
        if (stage.depends_on && stage.depends_on.length > 0) {
            tooltipLines.push(`Dependencies: ${stage.depends_on.join(', ')}`);
        }
        if (stage.config) {
            tooltipLines.push(`Config keys: ${Object.keys(stage.config).join(', ')}`);
        }
        item.tooltip = new vscode.MarkdownString(tooltipLines.join('\n\n'));

        // Icon based on component type
        item.iconPath = this.getComponentIcon(stage.component_type);

        // Command to navigate to stage in JSON
        if (this.document) {
            const range = this.findStageRange(stage.id);
            if (range) {
                item.command = {
                    command: 'flowmason.selectStage',
                    title: 'Select Stage',
                    arguments: [stage.id, this.document.uri, range]
                };
            }
        }

        return item;
    }

    private getStageChildren(stage: PipelineStage): StageTreeItem[] {
        const children: StageTreeItem[] = [];

        // Dependencies
        if (stage.depends_on && stage.depends_on.length > 0) {
            for (const dep of stage.depends_on) {
                const item = new StageTreeItem(
                    dep,
                    vscode.TreeItemCollapsibleState.None,
                    'dependency'
                );
                item.iconPath = new vscode.ThemeIcon('arrow-left');
                item.description = 'dependency';
                item.tooltip = `Depends on stage: ${dep}`;

                // Command to jump to dependency
                if (this.document) {
                    const range = this.findStageRange(dep);
                    if (range) {
                        item.command = {
                            command: 'flowmason.selectStage',
                            title: 'Go to Stage',
                            arguments: [dep, this.document.uri, range]
                        };
                    }
                }
                children.push(item);
            }
        }

        // Config values (top-level only for brevity)
        if (stage.config) {
            for (const [key, value] of Object.entries(stage.config)) {
                const item = new StageTreeItem(
                    key,
                    vscode.TreeItemCollapsibleState.None,
                    'config-value'
                );
                item.iconPath = new vscode.ThemeIcon('symbol-property');

                // Format value for display
                const displayValue = this.formatConfigValue(value);
                item.description = displayValue;
                item.tooltip = `${key}: ${JSON.stringify(value, null, 2)}`;

                children.push(item);
            }
        }

        return children;
    }

    private formatConfigValue(value: unknown): string {
        if (typeof value === 'string') {
            // Truncate long strings
            if (value.length > 30) {
                return `"${value.substring(0, 27)}..."`;
            }
            return `"${value}"`;
        }
        if (typeof value === 'number' || typeof value === 'boolean') {
            return String(value);
        }
        if (Array.isArray(value)) {
            return `[${value.length} items]`;
        }
        if (typeof value === 'object' && value !== null) {
            return `{${Object.keys(value).length} keys}`;
        }
        return String(value);
    }

    private getComponentIcon(componentType: string): vscode.ThemeIcon {
        // Control flow components
        if (componentType.includes('conditional') || componentType.includes('if')) {
            return new vscode.ThemeIcon('git-branch', new vscode.ThemeColor('charts.yellow'));
        }
        if (componentType.includes('foreach') || componentType.includes('loop')) {
            return new vscode.ThemeIcon('sync', new vscode.ThemeColor('charts.blue'));
        }
        if (componentType.includes('trycatch') || componentType.includes('error')) {
            return new vscode.ThemeIcon('shield', new vscode.ThemeColor('charts.orange'));
        }
        if (componentType.includes('router') || componentType.includes('switch')) {
            return new vscode.ThemeIcon('split-horizontal', new vscode.ThemeColor('charts.purple'));
        }
        if (componentType.includes('subpipeline') || componentType.includes('sub-pipeline')) {
            return new vscode.ThemeIcon('git-merge', new vscode.ThemeColor('charts.green'));
        }

        // AI nodes (typically have "generator", "critic", "improver", etc.)
        if (componentType.includes('generator') || componentType.includes('llm') ||
            componentType.includes('ai') || componentType.includes('critic') ||
            componentType.includes('improver') || componentType.includes('synthesizer')) {
            return new vscode.ThemeIcon('sparkle', new vscode.ThemeColor('charts.purple'));
        }

        // HTTP/API
        if (componentType.includes('http') || componentType.includes('api') || componentType.includes('fetch')) {
            return new vscode.ThemeIcon('cloud', new vscode.ThemeColor('charts.blue'));
        }

        // Transform/JSON
        if (componentType.includes('transform') || componentType.includes('json') || componentType.includes('map')) {
            return new vscode.ThemeIcon('json', new vscode.ThemeColor('charts.green'));
        }

        // Filter
        if (componentType.includes('filter')) {
            return new vscode.ThemeIcon('filter', new vscode.ThemeColor('charts.yellow'));
        }

        // Validate
        if (componentType.includes('validate') || componentType.includes('schema')) {
            return new vscode.ThemeIcon('check', new vscode.ThemeColor('charts.green'));
        }

        // Default
        return new vscode.ThemeIcon('symbol-method');
    }

    /**
     * Find the range of a stage in the document for navigation
     */
    private findStageRange(stageId: string): vscode.Range | null {
        if (!this.document) {
            return null;
        }

        const text = this.document.getText();

        // Look for the stage ID in the JSON
        // This is a simple search - could be improved with proper JSON parsing
        const searchPattern = `"id"\\s*:\\s*"${stageId}"`;
        const regex = new RegExp(searchPattern);
        const match = regex.exec(text);

        if (match) {
            const startPos = this.document.positionAt(match.index);
            const endPos = this.document.positionAt(match.index + match[0].length);
            return new vscode.Range(startPos, endPos);
        }

        return null;
    }

    /**
     * Get the current pipeline data (for use by other providers)
     */
    getPipeline(): PipelineFile | null {
        return this.pipeline;
    }

    /**
     * Get the current document (for use by other providers)
     */
    getDocument(): vscode.TextDocument | null {
        return this.document;
    }

    dispose(): void {
        for (const disposable of this.disposables) {
            disposable.dispose();
        }
    }
}

export class StageTreeItem extends vscode.TreeItem {
    stage?: PipelineStage;

    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue: StageTreeItemType
    ) {
        super(label, collapsibleState);
        this.contextValue = contextValue;
    }
}

/**
 * Register the selectStage command for navigation
 */
export function registerPipelineStagesCommands(context: vscode.ExtensionContext): void {
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'flowmason.selectStage',
            async (stageId: string, uri: vscode.Uri, range: vscode.Range) => {
                const doc = await vscode.workspace.openTextDocument(uri);
                const editor = await vscode.window.showTextDocument(doc);
                editor.selection = new vscode.Selection(range.start, range.end);
                editor.revealRange(range, vscode.TextEditorRevealType.InCenter);
            }
        )
    );
}
