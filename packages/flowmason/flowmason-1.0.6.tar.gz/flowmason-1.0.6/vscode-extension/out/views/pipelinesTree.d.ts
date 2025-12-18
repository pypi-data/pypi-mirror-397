/**
 * Pipelines Tree View Provider
 *
 * Shows FlowMason pipelines in the sidebar.
 */
import * as vscode from 'vscode';
import { FlowMasonService, Pipeline } from '../services/flowmasonService';
export declare class PipelinesTreeProvider implements vscode.TreeDataProvider<PipelineTreeItem> {
    private flowmasonService;
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: vscode.Event<PipelineTreeItem | undefined | null | void>;
    constructor(flowmasonService: FlowMasonService);
    refresh(): void;
    getTreeItem(element: PipelineTreeItem): vscode.TreeItem;
    getChildren(element?: PipelineTreeItem): Promise<PipelineTreeItem[]>;
    private getPipelines;
}
export declare class PipelineTreeItem extends vscode.TreeItem {
    readonly label: string;
    readonly collapsibleState: vscode.TreeItemCollapsibleState;
    readonly contextValue: string;
    pipeline?: Pipeline;
    constructor(label: string, collapsibleState: vscode.TreeItemCollapsibleState, contextValue: string);
}
//# sourceMappingURL=pipelinesTree.d.ts.map