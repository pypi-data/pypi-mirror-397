/**
 * Packages Tree View Provider
 *
 * Shows FlowMason packages in the sidebar.
 */

import * as vscode from 'vscode';
import { FlowMasonService, Package } from '../services/flowmasonService';

export class PackagesTreeProvider implements vscode.TreeDataProvider<PackageTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<PackageTreeItem | undefined | null | void> = new vscode.EventEmitter<PackageTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<PackageTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private flowmasonService: FlowMasonService) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: PackageTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: PackageTreeItem): Promise<PackageTreeItem[]> {
        if (!element) {
            // Root level - show packages
            return this.getPackages();
        }

        if (element.contextValue === 'package' && element.package) {
            // Package level - show components
            return this.getPackageComponents(element.package);
        }

        return [];
    }

    private async getPackages(): Promise<PackageTreeItem[]> {
        const packages = await this.flowmasonService.getLocalPackages();

        if (packages.length === 0) {
            const item = new PackageTreeItem(
                'No packages installed',
                vscode.TreeItemCollapsibleState.None,
                'empty'
            );
            item.iconPath = new vscode.ThemeIcon('info');
            return [item];
        }

        return packages.map(pkg => {
            const item = new PackageTreeItem(
                pkg.name,
                vscode.TreeItemCollapsibleState.Collapsed,
                'package'
            );
            item.description = `v${pkg.version}`;
            item.tooltip = `${pkg.description || pkg.name}\n\nPath: ${pkg.path}`;
            item.iconPath = new vscode.ThemeIcon('package');
            item.package = pkg;
            return item;
        });
    }

    private getPackageComponents(pkg: Package): PackageTreeItem[] {
        return pkg.components.map(comp => {
            const item = new PackageTreeItem(
                comp.name,
                vscode.TreeItemCollapsibleState.None,
                'packageComponent'
            );
            item.description = comp.type === 'node' ? 'Node' : 'Operator';
            item.tooltip = comp.description || comp.name;

            if (comp.type === 'node') {
                item.iconPath = new vscode.ThemeIcon('symbol-method');
            } else {
                item.iconPath = new vscode.ThemeIcon('symbol-function');
            }

            return item;
        });
    }
}

export class PackageTreeItem extends vscode.TreeItem {
    package?: Package;

    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue: string
    ) {
        super(label, collapsibleState);
        this.contextValue = contextValue;
    }
}
