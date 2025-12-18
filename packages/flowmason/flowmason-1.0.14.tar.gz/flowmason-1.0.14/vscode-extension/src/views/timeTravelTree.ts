/**
 * Time Travel Tree View Provider
 *
 * Provides a tree view for navigating execution history during debugging.
 * Allows stepping backward and forward through snapshots.
 */

import * as vscode from 'vscode';

import { FlowMasonService, TimeTravelTimeline, TimeTravelSnapshot, TimeTravelDiff } from '../services/flowmasonService';

type TreeItemType = 'timeline' | 'stage' | 'snapshot' | 'loading' | 'empty' | 'error';

class TimeTravelTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly itemType: TreeItemType,
        public readonly data?: TimeTravelTimeline | TimeTravelSnapshot | { stage_id: string; stage_name: string; snapshots: TimeTravelSnapshot[] } | null,
        public readonly snapshotId?: string
    ) {
        super(label, collapsibleState);

        switch (itemType) {
            case 'timeline':
                this.iconPath = new vscode.ThemeIcon('timeline-view-icon');
                this.contextValue = 'timeTravelTimeline';
                const timeline = data as TimeTravelTimeline;
                this.description = timeline ? `${timeline.total_snapshots} snapshots` : '';
                break;
            case 'stage':
                const stageData = data as { stage_id: string; stage_name: string; snapshots: TimeTravelSnapshot[] };
                this.iconPath = this.getStageIcon(stageData?.snapshots);
                this.contextValue = 'timeTravelStage';
                this.description = stageData ? `${stageData.snapshots?.length || 0} snapshots` : '';
                break;
            case 'snapshot':
                const snapshot = data as TimeTravelSnapshot;
                this.iconPath = this.getSnapshotIcon(snapshot?.snapshot_type);
                this.contextValue = 'timeTravelSnapshot';
                this.description = this.getSnapshotDescription(snapshot);
                this.tooltip = this.getSnapshotTooltip(snapshot);
                this.command = {
                    command: 'flowmason.timeTravel.viewSnapshot',
                    title: 'View Snapshot',
                    arguments: [snapshot?.id]
                };
                break;
            case 'loading':
                this.iconPath = new vscode.ThemeIcon('loading~spin');
                this.contextValue = 'loading';
                break;
            case 'empty':
                this.iconPath = new vscode.ThemeIcon('info');
                this.contextValue = 'empty';
                break;
            case 'error':
                this.iconPath = new vscode.ThemeIcon('error');
                this.contextValue = 'error';
                break;
        }
    }

    private getStageIcon(snapshots?: TimeTravelSnapshot[]): vscode.ThemeIcon {
        if (!snapshots || snapshots.length === 0) {
            return new vscode.ThemeIcon('circle-outline');
        }

        // Check if there's an error snapshot
        const hasError = snapshots.some(s => s.snapshot_type === 'stage_error');
        if (hasError) {
            return new vscode.ThemeIcon('error', new vscode.ThemeColor('errorForeground'));
        }

        // Check if completed
        const hasComplete = snapshots.some(s => s.snapshot_type === 'stage_complete');
        if (hasComplete) {
            return new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
        }

        // In progress
        return new vscode.ThemeIcon('play-circle');
    }

    private getSnapshotIcon(snapshotType?: string): vscode.ThemeIcon {
        switch (snapshotType) {
            case 'stage_start':
                return new vscode.ThemeIcon('debug-start');
            case 'stage_complete':
                return new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
            case 'stage_error':
                return new vscode.ThemeIcon('error', new vscode.ThemeColor('errorForeground'));
            case 'run_start':
                return new vscode.ThemeIcon('play');
            case 'run_complete':
                return new vscode.ThemeIcon('pass-filled', new vscode.ThemeColor('testing.iconPassed'));
            case 'breakpoint':
                return new vscode.ThemeIcon('debug-breakpoint');
            default:
                return new vscode.ThemeIcon('circle-outline');
        }
    }

    private getSnapshotDescription(snapshot?: TimeTravelSnapshot): string {
        if (!snapshot) return '';

        const time = new Date(snapshot.timestamp).toLocaleTimeString();
        return `#${snapshot.sequence_number} at ${time}`;
    }

    private getSnapshotTooltip(snapshot?: TimeTravelSnapshot): string {
        if (!snapshot) return '';

        const lines = [
            `Snapshot #${snapshot.sequence_number}`,
            `Type: ${snapshot.snapshot_type}`,
            `Stage: ${snapshot.stage_name}`,
            `Time: ${new Date(snapshot.timestamp).toLocaleString()}`,
            '',
            'State:',
            `  Variables: ${Object.keys(snapshot.state?.variables || {}).length}`,
            `  Outputs: ${Object.keys(snapshot.state?.outputs || {}).length}`,
            `  Completed Stages: ${snapshot.state?.completed_stages?.length || 0}`,
        ];

        return lines.join('\n');
    }
}

export class TimeTravelTreeProvider implements vscode.TreeDataProvider<TimeTravelTreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<TimeTravelTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private currentRunId: string | null = null;
    private currentTimeline: TimeTravelTimeline | null = null;
    private snapshots: TimeTravelSnapshot[] = [];
    private currentSnapshotId: string | null = null;
    private isLoading = false;
    private lastError: string | null = null;

    constructor(private readonly service: FlowMasonService) {}

    refresh(): void {
        this.lastError = null;
        this._onDidChangeTreeData.fire();

        if (this.currentRunId) {
            this.loadTimeline(this.currentRunId);
        }
    }

    setRunId(runId: string | null): void {
        this.currentRunId = runId;
        this.currentTimeline = null;
        this.snapshots = [];
        this.currentSnapshotId = null;
        this.lastError = null;

        if (runId) {
            this.loadTimeline(runId);
        } else {
            this._onDidChangeTreeData.fire();
        }
    }

    getCurrentRunId(): string | null {
        return this.currentRunId;
    }

    getCurrentSnapshotId(): string | null {
        return this.currentSnapshotId;
    }

    setCurrentSnapshotId(snapshotId: string | null): void {
        this.currentSnapshotId = snapshotId;
        this._onDidChangeTreeData.fire();
    }

    private async loadTimeline(runId: string): Promise<void> {
        this.isLoading = true;
        this._onDidChangeTreeData.fire();

        try {
            const [timeline, snapshots] = await Promise.all([
                this.service.getTimeTravelTimeline(runId),
                this.service.getTimeTravelSnapshots(runId),
            ]);

            this.currentTimeline = timeline;
            this.snapshots = snapshots;

            // Set current snapshot to the latest if not set
            if (!this.currentSnapshotId && snapshots.length > 0) {
                this.currentSnapshotId = snapshots[snapshots.length - 1].id;
            }

            this.lastError = null;
        } catch (error) {
            this.lastError = `Failed to load timeline: ${error}`;
        } finally {
            this.isLoading = false;
            this._onDidChangeTreeData.fire();
        }
    }

    getTreeItem(element: TimeTravelTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: TimeTravelTreeItem): Promise<TimeTravelTreeItem[]> {
        // Root level
        if (!element) {
            if (!this.currentRunId) {
                return [new TimeTravelTreeItem(
                    'Start debugging a pipeline to enable time travel',
                    vscode.TreeItemCollapsibleState.None,
                    'empty'
                )];
            }

            if (this.isLoading) {
                return [new TimeTravelTreeItem('Loading timeline...', vscode.TreeItemCollapsibleState.None, 'loading')];
            }

            if (this.lastError) {
                return [new TimeTravelTreeItem(this.lastError, vscode.TreeItemCollapsibleState.None, 'error')];
            }

            if (!this.currentTimeline) {
                return [new TimeTravelTreeItem('No timeline data available', vscode.TreeItemCollapsibleState.None, 'empty')];
            }

            // Group snapshots by stage
            const stageMap = new Map<string, { stage_id: string; stage_name: string; snapshots: TimeTravelSnapshot[] }>();

            for (const snapshot of this.snapshots) {
                const stageId = snapshot.stage_id;
                if (!stageMap.has(stageId)) {
                    stageMap.set(stageId, {
                        stage_id: stageId,
                        stage_name: snapshot.stage_name,
                        snapshots: [],
                    });
                }
                stageMap.get(stageId)!.snapshots.push(snapshot);
            }

            // Create stage items
            const items: TimeTravelTreeItem[] = [];

            // Add timeline header
            items.push(new TimeTravelTreeItem(
                this.currentTimeline.pipeline_name,
                vscode.TreeItemCollapsibleState.None,
                'timeline',
                this.currentTimeline
            ));

            // Add stages
            for (const [stageId, stageData] of stageMap) {
                items.push(new TimeTravelTreeItem(
                    stageData.stage_name,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'stage',
                    stageData
                ));
            }

            return items;
        }

        // Stage children - show snapshots
        if (element.itemType === 'stage') {
            const stageData = element.data as { stage_id: string; stage_name: string; snapshots: TimeTravelSnapshot[] };
            if (!stageData?.snapshots) return [];

            return stageData.snapshots.map(snapshot => {
                const item = new TimeTravelTreeItem(
                    this.getSnapshotLabel(snapshot),
                    vscode.TreeItemCollapsibleState.None,
                    'snapshot',
                    snapshot,
                    snapshot.id
                );

                // Highlight current snapshot
                if (snapshot.id === this.currentSnapshotId) {
                    item.iconPath = new vscode.ThemeIcon('arrow-right', new vscode.ThemeColor('focusBorder'));
                }

                return item;
            });
        }

        return [];
    }

    private getSnapshotLabel(snapshot: TimeTravelSnapshot): string {
        switch (snapshot.snapshot_type) {
            case 'stage_start':
                return `Start`;
            case 'stage_complete':
                return `Complete`;
            case 'stage_error':
                return `Error`;
            case 'run_start':
                return `Run Started`;
            case 'run_complete':
                return `Run Complete`;
            case 'breakpoint':
                return `Breakpoint`;
            default:
                return snapshot.snapshot_type;
        }
    }
}

export function registerTimeTravelCommands(
    context: vscode.ExtensionContext,
    service: FlowMasonService,
    outputChannel: vscode.OutputChannel
): TimeTravelTreeProvider {
    const provider = new TimeTravelTreeProvider(service);

    // Register tree view
    vscode.window.registerTreeDataProvider('flowmason.timeTravel', provider);

    // Show timeline command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.timeTravel.showTimeline', async () => {
            const runId = provider.getCurrentRunId();
            if (!runId) {
                vscode.window.showWarningMessage('No active debug session. Start debugging a pipeline first.');
                return;
            }

            provider.refresh();
            vscode.commands.executeCommand('flowmason.timeTravel.focus');
        })
    );

    // View snapshot command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.timeTravel.viewSnapshot', async (snapshotId: string) => {
            try {
                const snapshot = await service.getTimeTravelSnapshot(snapshotId);
                if (!snapshot) {
                    vscode.window.showErrorMessage('Snapshot not found');
                    return;
                }

                provider.setCurrentSnapshotId(snapshotId);

                // Show snapshot in a webview
                const panel = vscode.window.createWebviewPanel(
                    'flowmasonSnapshot',
                    `Snapshot #${snapshot.sequence_number}`,
                    vscode.ViewColumn.Beside,
                    { enableScripts: true }
                );

                panel.webview.html = getSnapshotDetailHtml(snapshot);

                // Handle messages
                panel.webview.onDidReceiveMessage(
                    async message => {
                        switch (message.command) {
                            case 'replay':
                                await vscode.commands.executeCommand('flowmason.timeTravel.replay', snapshotId);
                                break;
                            case 'whatif':
                                await vscode.commands.executeCommand('flowmason.timeTravel.whatIf', snapshotId);
                                break;
                        }
                    },
                    undefined,
                    context.subscriptions
                );
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to load snapshot: ${error}`);
            }
        })
    );

    // Step back command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.timeTravel.stepBack', async () => {
            const runId = provider.getCurrentRunId();
            if (!runId) {
                vscode.window.showWarningMessage('No active debug session');
                return;
            }

            try {
                const currentSnapshotId = provider.getCurrentSnapshotId();
                const snapshot = await service.timeTravelStepBack(runId, currentSnapshotId || undefined);

                if (snapshot) {
                    provider.setCurrentSnapshotId(snapshot.id);
                    outputChannel.appendLine(`Stepped back to snapshot #${snapshot.sequence_number}`);
                    vscode.window.showInformationMessage(
                        `Stepped back to: ${snapshot.stage_name} (${snapshot.snapshot_type})`
                    );
                } else {
                    vscode.window.showWarningMessage('Already at the beginning of execution');
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to step back: ${error}`);
            }
        })
    );

    // Step forward command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.timeTravel.stepForward', async () => {
            const runId = provider.getCurrentRunId();
            if (!runId) {
                vscode.window.showWarningMessage('No active debug session');
                return;
            }

            try {
                const currentSnapshotId = provider.getCurrentSnapshotId();
                const snapshot = await service.timeTravelStepForward(runId, currentSnapshotId || undefined);

                if (snapshot) {
                    provider.setCurrentSnapshotId(snapshot.id);
                    outputChannel.appendLine(`Stepped forward to snapshot #${snapshot.sequence_number}`);
                    vscode.window.showInformationMessage(
                        `Stepped forward to: ${snapshot.stage_name} (${snapshot.snapshot_type})`
                    );
                } else {
                    vscode.window.showWarningMessage('Already at the end of execution');
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to step forward: ${error}`);
            }
        })
    );

    // Compare diff command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.timeTravel.compareDiff', async () => {
            const runId = provider.getCurrentRunId();
            if (!runId) {
                vscode.window.showWarningMessage('No active debug session');
                return;
            }

            try {
                const snapshots = await service.getTimeTravelSnapshots(runId);
                if (snapshots.length < 2) {
                    vscode.window.showWarningMessage('Need at least 2 snapshots to compare');
                    return;
                }

                // Let user pick two snapshots
                const snapshotItems = snapshots.map(s => ({
                    label: `#${s.sequence_number}: ${s.stage_name}`,
                    description: s.snapshot_type,
                    detail: new Date(s.timestamp).toLocaleString(),
                    id: s.id,
                }));

                const from = await vscode.window.showQuickPick(snapshotItems, {
                    placeHolder: 'Select the FROM snapshot',
                });
                if (!from) return;

                const to = await vscode.window.showQuickPick(
                    snapshotItems.filter(s => s.id !== from.id),
                    { placeHolder: 'Select the TO snapshot' }
                );
                if (!to) return;

                const diff = await service.getTimeTravelDiff(from.id, to.id);
                if (!diff) {
                    vscode.window.showErrorMessage('Failed to compute diff');
                    return;
                }

                // Show diff in a webview
                const panel = vscode.window.createWebviewPanel(
                    'flowmasonDiff',
                    'Snapshot Comparison',
                    vscode.ViewColumn.Active,
                    { enableScripts: true }
                );

                panel.webview.html = getDiffDetailHtml(diff, from.label, to.label);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to compare snapshots: ${error}`);
            }
        })
    );

    // Replay command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.timeTravel.replay', async (snapshotId?: string) => {
            const targetSnapshotId = snapshotId || provider.getCurrentSnapshotId();
            if (!targetSnapshotId) {
                vscode.window.showWarningMessage('No snapshot selected');
                return;
            }

            const confirm = await vscode.window.showWarningMessage(
                'This will re-run the pipeline from this snapshot. Continue?',
                'Replay',
                'Cancel'
            );

            if (confirm !== 'Replay') return;

            try {
                outputChannel.appendLine(`Starting replay from snapshot ${targetSnapshotId}`);

                const result = await service.startTimeTravelReplay(targetSnapshotId);
                outputChannel.appendLine(`Replay started: ${result.message}`);

                vscode.window.showInformationMessage(result.message);
            } catch (error) {
                outputChannel.appendLine(`Replay failed: ${error}`);
                vscode.window.showErrorMessage(`Failed to start replay: ${error}`);
            }
        })
    );

    // What-if analysis command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.timeTravel.whatIf', async (snapshotId?: string) => {
            const targetSnapshotId = snapshotId || provider.getCurrentSnapshotId();
            if (!targetSnapshotId) {
                vscode.window.showWarningMessage('No snapshot selected');
                return;
            }

            // Get the snapshot to show current values
            const snapshot = await service.getTimeTravelSnapshot(targetSnapshotId);
            if (!snapshot) {
                vscode.window.showErrorMessage('Snapshot not found');
                return;
            }

            // Let user input modified values
            const input = await vscode.window.showInputBox({
                prompt: 'Enter modifications as JSON (e.g., {"variable_name": "new_value"})',
                placeHolder: '{"key": "value"}',
                validateInput: (value) => {
                    try {
                        JSON.parse(value);
                        return null;
                    } catch {
                        return 'Invalid JSON';
                    }
                }
            });

            if (!input) return;

            try {
                const modifications = JSON.parse(input);
                outputChannel.appendLine(`Starting what-if analysis from snapshot ${targetSnapshotId}`);
                outputChannel.appendLine(`Modifications: ${JSON.stringify(modifications)}`);

                const result = await service.startWhatIfAnalysis(targetSnapshotId, modifications);
                outputChannel.appendLine(`What-if analysis started: ${result.message}`);

                vscode.window.showInformationMessage(result.message);
            } catch (error) {
                outputChannel.appendLine(`What-if analysis failed: ${error}`);
                vscode.window.showErrorMessage(`Failed to start what-if analysis: ${error}`);
            }
        })
    );

    // Listen for debug session changes
    context.subscriptions.push(
        vscode.debug.onDidStartDebugSession(session => {
            if (session.type === 'flowmason') {
                // The run ID will be set by the debug adapter
                // We'll need to communicate it somehow - for now, use a shared state
                outputChannel.appendLine('Debug session started - Time Travel ready');
            }
        })
    );

    context.subscriptions.push(
        vscode.debug.onDidTerminateDebugSession(session => {
            if (session.type === 'flowmason') {
                // Clear the time travel state when debugging ends
                // Keep the data for review
                outputChannel.appendLine('Debug session ended - Time Travel data preserved');
            }
        })
    );

    return provider;
}

function getSnapshotDetailHtml(snapshot: TimeTravelSnapshot): string {
    const formatJson = (obj: unknown) => JSON.stringify(obj, null, 2);

    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: var(--vscode-font-family); padding: 20px; color: var(--vscode-foreground); }
        .header { margin-bottom: 20px; }
        h1 { font-size: 20px; margin: 0 0 8px 0; }
        .meta { color: var(--vscode-descriptionForeground); font-size: 13px; }
        .section { margin: 20px 0; }
        .section h2 { font-size: 14px; margin-bottom: 8px; border-bottom: 1px solid var(--vscode-panel-border); padding-bottom: 4px; }
        pre { background: var(--vscode-textBlockQuote-background); padding: 12px; border-radius: 4px; overflow: auto; font-size: 12px; }
        .actions { margin-top: 20px; display: flex; gap: 8px; }
        .btn { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 6px 16px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: var(--vscode-button-hoverBackground); }
        .btn-secondary { background: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground); }
        .type-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; background: var(--vscode-badge-background); color: var(--vscode-badge-foreground); }
    </style>
</head>
<body>
    <div class="header">
        <h1>${snapshot.stage_name}</h1>
        <div class="meta">
            <span class="type-badge">${snapshot.snapshot_type}</span>
            Snapshot #${snapshot.sequence_number} · ${new Date(snapshot.timestamp).toLocaleString()}
        </div>
    </div>

    <div class="section">
        <h2>Variables (${Object.keys(snapshot.state?.variables || {}).length})</h2>
        <pre>${formatJson(snapshot.state?.variables || {})}</pre>
    </div>

    <div class="section">
        <h2>Outputs (${Object.keys(snapshot.state?.outputs || {}).length})</h2>
        <pre>${formatJson(snapshot.state?.outputs || {})}</pre>
    </div>

    <div class="section">
        <h2>Completed Stages (${snapshot.state?.completed_stages?.length || 0})</h2>
        <pre>${formatJson(snapshot.state?.completed_stages || [])}</pre>
    </div>

    ${snapshot.metadata ? `
    <div class="section">
        <h2>Metadata</h2>
        <pre>${formatJson(snapshot.metadata)}</pre>
    </div>
    ` : ''}

    <div class="actions">
        <button class="btn" onclick="replay()">Replay from Here</button>
        <button class="btn btn-secondary" onclick="whatif()">What-If Analysis</button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        function replay() { vscode.postMessage({ command: 'replay' }); }
        function whatif() { vscode.postMessage({ command: 'whatif' }); }
    </script>
</body>
</html>`;
}

function getDiffDetailHtml(diff: TimeTravelDiff, fromLabel: string, toLabel: string): string {
    const formatJson = (obj: unknown) => JSON.stringify(obj, null, 2);

    const hasVariableChanges =
        Object.keys(diff.changes.variables.added).length > 0 ||
        diff.changes.variables.removed.length > 0 ||
        Object.keys(diff.changes.variables.modified).length > 0;

    const hasOutputChanges =
        Object.keys(diff.changes.outputs.added).length > 0 ||
        diff.changes.outputs.removed.length > 0 ||
        Object.keys(diff.changes.outputs.modified).length > 0;

    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: var(--vscode-font-family); padding: 20px; color: var(--vscode-foreground); }
        h1 { font-size: 20px; margin-bottom: 16px; }
        .comparison { color: var(--vscode-descriptionForeground); margin-bottom: 20px; }
        .section { margin: 20px 0; }
        .section h2 { font-size: 14px; margin-bottom: 8px; border-bottom: 1px solid var(--vscode-panel-border); padding-bottom: 4px; }
        pre { background: var(--vscode-textBlockQuote-background); padding: 12px; border-radius: 4px; overflow: auto; font-size: 12px; }
        .added { color: var(--vscode-gitDecoration-addedResourceForeground); }
        .removed { color: var(--vscode-gitDecoration-deletedResourceForeground); }
        .modified { color: var(--vscode-gitDecoration-modifiedResourceForeground); }
        .change-item { margin: 8px 0; padding: 8px; background: var(--vscode-editor-background); border-radius: 4px; }
        .change-key { font-weight: bold; }
        .old-value { color: var(--vscode-gitDecoration-deletedResourceForeground); }
        .new-value { color: var(--vscode-gitDecoration-addedResourceForeground); }
        .no-changes { color: var(--vscode-descriptionForeground); font-style: italic; }
    </style>
</head>
<body>
    <h1>Snapshot Comparison</h1>
    <div class="comparison">
        <strong>From:</strong> ${fromLabel}<br>
        <strong>To:</strong> ${toLabel}
    </div>

    <div class="section">
        <h2>Variable Changes</h2>
        ${!hasVariableChanges ? '<p class="no-changes">No variable changes</p>' : `
            ${Object.keys(diff.changes.variables.added).length > 0 ? `
                <h3 class="added">Added</h3>
                <pre>${formatJson(diff.changes.variables.added)}</pre>
            ` : ''}
            ${diff.changes.variables.removed.length > 0 ? `
                <h3 class="removed">Removed</h3>
                <pre>${formatJson(diff.changes.variables.removed)}</pre>
            ` : ''}
            ${Object.keys(diff.changes.variables.modified).length > 0 ? `
                <h3 class="modified">Modified</h3>
                ${Object.entries(diff.changes.variables.modified).map(([key, change]: [string, any]) => `
                    <div class="change-item">
                        <div class="change-key">${key}</div>
                        <div class="old-value">- ${JSON.stringify(change.old)}</div>
                        <div class="new-value">+ ${JSON.stringify(change.new)}</div>
                    </div>
                `).join('')}
            ` : ''}
        `}
    </div>

    <div class="section">
        <h2>Output Changes</h2>
        ${!hasOutputChanges ? '<p class="no-changes">No output changes</p>' : `
            ${Object.keys(diff.changes.outputs.added).length > 0 ? `
                <h3 class="added">Added</h3>
                <pre>${formatJson(diff.changes.outputs.added)}</pre>
            ` : ''}
            ${diff.changes.outputs.removed.length > 0 ? `
                <h3 class="removed">Removed</h3>
                <pre>${formatJson(diff.changes.outputs.removed)}</pre>
            ` : ''}
            ${Object.keys(diff.changes.outputs.modified).length > 0 ? `
                <h3 class="modified">Modified</h3>
                ${Object.entries(diff.changes.outputs.modified).map(([key, change]: [string, any]) => `
                    <div class="change-item">
                        <div class="change-key">${key}</div>
                        <div class="old-value">- ${JSON.stringify(change.old)}</div>
                        <div class="new-value">+ ${JSON.stringify(change.new)}</div>
                    </div>
                `).join('')}
            ` : ''}
        `}
    </div>

    ${diff.changes.stages_completed.length > 0 ? `
    <div class="section">
        <h2>Stages Completed</h2>
        <pre>${formatJson(diff.changes.stages_completed)}</pre>
    </div>
    ` : ''}
</body>
</html>`;
}
