/**
 * Time Travel Tree View Provider
 *
 * Provides a tree view for navigating execution history during debugging.
 * Allows stepping backward and forward through snapshots.
 */
import * as vscode from 'vscode';
import { FlowMasonService, TimeTravelTimeline, TimeTravelSnapshot } from '../services/flowmasonService';
type TreeItemType = 'timeline' | 'stage' | 'snapshot' | 'loading' | 'empty' | 'error';
declare class TimeTravelTreeItem extends vscode.TreeItem {
    readonly label: string;
    readonly collapsibleState: vscode.TreeItemCollapsibleState;
    readonly itemType: TreeItemType;
    readonly data?: (TimeTravelTimeline | TimeTravelSnapshot | {
        stage_id: string;
        stage_name: string;
        snapshots: TimeTravelSnapshot[];
    } | null) | undefined;
    readonly snapshotId?: string | undefined;
    constructor(label: string, collapsibleState: vscode.TreeItemCollapsibleState, itemType: TreeItemType, data?: (TimeTravelTimeline | TimeTravelSnapshot | {
        stage_id: string;
        stage_name: string;
        snapshots: TimeTravelSnapshot[];
    } | null) | undefined, snapshotId?: string | undefined);
    private getStageIcon;
    private getSnapshotIcon;
    private getSnapshotDescription;
    private getSnapshotTooltip;
}
export declare class TimeTravelTreeProvider implements vscode.TreeDataProvider<TimeTravelTreeItem> {
    private readonly service;
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: vscode.Event<void | TimeTravelTreeItem | null | undefined>;
    private currentRunId;
    private currentTimeline;
    private snapshots;
    private currentSnapshotId;
    private isLoading;
    private lastError;
    constructor(service: FlowMasonService);
    refresh(): void;
    setRunId(runId: string | null): void;
    getCurrentRunId(): string | null;
    getCurrentSnapshotId(): string | null;
    setCurrentSnapshotId(snapshotId: string | null): void;
    private loadTimeline;
    getTreeItem(element: TimeTravelTreeItem): vscode.TreeItem;
    getChildren(element?: TimeTravelTreeItem): Promise<TimeTravelTreeItem[]>;
    private getSnapshotLabel;
}
export declare function registerTimeTravelCommands(context: vscode.ExtensionContext, service: FlowMasonService, outputChannel: vscode.OutputChannel): TimeTravelTreeProvider;
export {};
//# sourceMappingURL=timeTravelTree.d.ts.map