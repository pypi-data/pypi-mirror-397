/**
 * Pipelines Tree View Provider
 *
 * Shows FlowMason pipelines in the sidebar.
 */

import * as vscode from 'vscode';
import { FlowMasonService, Pipeline } from '../services/flowmasonService';

export class PipelinesTreeProvider implements vscode.TreeDataProvider<PipelineTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<PipelineTreeItem | undefined | null | void> = new vscode.EventEmitter<PipelineTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<PipelineTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private flowmasonService: FlowMasonService) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: PipelineTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: PipelineTreeItem): Promise<PipelineTreeItem[]> {
        if (!element) {
            return this.getPipelines();
        }
        return [];
    }

    private async getPipelines(): Promise<PipelineTreeItem[]> {
        try {
            const pipelines = await this.flowmasonService.getPipelines();

            if (pipelines.length === 0) {
                const item = new PipelineTreeItem(
                    'No pipelines',
                    vscode.TreeItemCollapsibleState.None,
                    'empty'
                );
                item.iconPath = new vscode.ThemeIcon('info');
                item.command = {
                    command: 'flowmason.openStudio',
                    title: 'Open Studio',
                };
                return [item];
            }

            return pipelines.map(pipeline => {
                const item = new PipelineTreeItem(
                    pipeline.name,
                    vscode.TreeItemCollapsibleState.None,
                    'pipeline'
                );

                item.description = pipeline.status === 'published' ? 'Published' : 'Draft';
                item.tooltip = `${pipeline.description || pipeline.name}\n\nStatus: ${pipeline.status}\nStages: ${pipeline.stage_count}`;

                // Icon based on status
                if (pipeline.status === 'published') {
                    item.iconPath = new vscode.ThemeIcon('check-all', new vscode.ThemeColor('charts.green'));
                } else {
                    item.iconPath = new vscode.ThemeIcon('git-merge', new vscode.ThemeColor('charts.yellow'));
                }

                item.pipeline = pipeline;

                return item;
            });
        } catch {
            const item = new PipelineTreeItem(
                'Unable to load pipelines',
                vscode.TreeItemCollapsibleState.None,
                'error'
            );
            item.iconPath = new vscode.ThemeIcon('warning');
            item.description = 'Studio may not be running';
            return [item];
        }
    }
}

export class PipelineTreeItem extends vscode.TreeItem {
    pipeline?: Pipeline;

    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue: string
    ) {
        super(label, collapsibleState);
        this.contextValue = contextValue;
    }
}
