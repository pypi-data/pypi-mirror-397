/**
 * Components Tree View Provider
 *
 * Shows FlowMason components in the sidebar.
 */
import * as vscode from 'vscode';
import { FlowMasonService, Component } from '../services/flowmasonService';
import { ComponentParser } from '../services/componentParser';
export declare class ComponentsTreeProvider implements vscode.TreeDataProvider<ComponentTreeItem> {
    private flowmasonService;
    private componentParser;
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: vscode.Event<ComponentTreeItem | undefined | null | void>;
    constructor(flowmasonService: FlowMasonService, componentParser: ComponentParser);
    refresh(): void;
    getTreeItem(element: ComponentTreeItem): vscode.TreeItem;
    getChildren(element?: ComponentTreeItem): Promise<ComponentTreeItem[]>;
    private getCategories;
    private getComponentsInCategory;
    private componentToTreeItem;
    /**
     * Map hex color to nearest VSCode theme color.
     * VSCode has limited theme colors for icons, so we map to the closest one.
     */
    private hexToThemeColor;
    private getWorkspaceComponents;
}
export declare class ComponentTreeItem extends vscode.TreeItem {
    readonly label: string;
    readonly collapsibleState: vscode.TreeItemCollapsibleState;
    readonly contextValue: string;
    component?: Component;
    constructor(label: string, collapsibleState: vscode.TreeItemCollapsibleState, contextValue: string);
}
//# sourceMappingURL=componentsTree.d.ts.map