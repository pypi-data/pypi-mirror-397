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
    position?: {
        x: number;
        y: number;
    };
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
export declare class PipelineStagesTreeProvider implements vscode.TreeDataProvider<StageTreeItem> {
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: vscode.Event<StageTreeItem | undefined | null | void>;
    private pipeline;
    private document;
    private disposables;
    constructor();
    private updateFromEditor;
    private loadPipeline;
    refresh(): void;
    getTreeItem(element: StageTreeItem): vscode.TreeItem;
    getChildren(element?: StageTreeItem): Promise<StageTreeItem[]>;
    private getRootChildren;
    private stageToTreeItem;
    private getStageChildren;
    private formatConfigValue;
    private getComponentIcon;
    /**
     * Find the range of a stage in the document for navigation
     */
    private findStageRange;
    /**
     * Get the current pipeline data (for use by other providers)
     */
    getPipeline(): PipelineFile | null;
    /**
     * Get the current document (for use by other providers)
     */
    getDocument(): vscode.TextDocument | null;
    dispose(): void;
}
export declare class StageTreeItem extends vscode.TreeItem {
    readonly label: string;
    readonly collapsibleState: vscode.TreeItemCollapsibleState;
    readonly contextValue: StageTreeItemType;
    stage?: PipelineStage;
    constructor(label: string, collapsibleState: vscode.TreeItemCollapsibleState, contextValue: StageTreeItemType);
}
/**
 * Register the selectStage command for navigation
 */
export declare function registerPipelineStagesCommands(context: vscode.ExtensionContext): void;
export {};
//# sourceMappingURL=pipelineStagesTree.d.ts.map