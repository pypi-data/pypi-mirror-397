/**
 * Packages Tree View Provider
 *
 * Shows FlowMason packages in the sidebar.
 */
import * as vscode from 'vscode';
import { FlowMasonService, Package } from '../services/flowmasonService';
export declare class PackagesTreeProvider implements vscode.TreeDataProvider<PackageTreeItem> {
    private flowmasonService;
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: vscode.Event<PackageTreeItem | undefined | null | void>;
    constructor(flowmasonService: FlowMasonService);
    refresh(): void;
    getTreeItem(element: PackageTreeItem): vscode.TreeItem;
    getChildren(element?: PackageTreeItem): Promise<PackageTreeItem[]>;
    private getPackages;
    private getPackageComponents;
}
export declare class PackageTreeItem extends vscode.TreeItem {
    readonly label: string;
    readonly collapsibleState: vscode.TreeItemCollapsibleState;
    readonly contextValue: string;
    package?: Package;
    constructor(label: string, collapsibleState: vscode.TreeItemCollapsibleState, contextValue: string);
}
//# sourceMappingURL=packagesTree.d.ts.map