/**
 * Pipeline Diff Provider for FlowMason VSCode Extension.
 *
 * Provides visual diff capabilities for pipeline files, showing:
 * - Added/removed/modified stages
 * - Configuration changes
 * - Schema changes
 * - Dependency graph changes
 */

import * as vscode from 'vscode';
import * as path from 'path';

interface StageDiff {
    stageId: string;
    changeType: 'added' | 'removed' | 'modified' | 'moved' | 'unchanged';
    oldIndex?: number;
    newIndex?: number;
    changes?: FieldChange[];
}

interface FieldChange {
    field: string;
    old: any;
    new: any;
    type: 'added' | 'removed' | 'modified';
}

interface DiffResult {
    summary: string;
    hasChanges: boolean;
    metadata: {
        nameChanged: boolean;
        versionChanged: boolean;
        descriptionChanged: boolean;
    };
    stages: {
        added: StageDiff[];
        removed: StageDiff[];
        modified: StageDiff[];
        moved: StageDiff[];
    };
    schemas: {
        inputChanged: boolean;
        outputChanged: boolean;
    };
    dependencies: {
        from: string;
        to: string;
        type: 'added' | 'removed';
    }[];
}

export class PipelineDiffProvider implements vscode.TextDocumentContentProvider {
    private static readonly scheme = 'flowmason-diff';
    private _onDidChange = new vscode.EventEmitter<vscode.Uri>();
    public readonly onDidChange = this._onDidChange.event;

    private diffCache: Map<string, DiffResult> = new Map();

    constructor(private context: vscode.ExtensionContext) {}

    public async provideTextDocumentContent(uri: vscode.Uri): Promise<string> {
        const params = new URLSearchParams(uri.query);
        const leftPath = params.get('left');
        const rightPath = params.get('right');

        if (!leftPath || !rightPath) {
            return 'Error: Missing file paths for diff';
        }

        const diff = await this.computeDiff(leftPath, rightPath);
        return this.formatDiffAsHtml(diff, leftPath, rightPath);
    }

    /**
     * Compute diff between two pipeline files using the CLI.
     */
    private async computeDiff(leftPath: string, rightPath: string): Promise<DiffResult> {
        const cacheKey = `${leftPath}:${rightPath}`;

        // Check cache
        if (this.diffCache.has(cacheKey)) {
            return this.diffCache.get(cacheKey)!;
        }

        try {
            const { exec } = require('child_process');
            const { promisify } = require('util');
            const execAsync = promisify(exec);

            // Use fm diff --format json to get structured diff
            const { stdout } = await execAsync(
                `fm diff "${leftPath}" "${rightPath}" --format json`,
                { maxBuffer: 10 * 1024 * 1024 }
            );

            const result: DiffResult = JSON.parse(stdout);
            this.diffCache.set(cacheKey, result);
            return result;
        } catch (error: any) {
            // If exit code 1 but output exists, parse it (diff found changes)
            if (error.stdout) {
                try {
                    const result: DiffResult = JSON.parse(error.stdout);
                    this.diffCache.set(cacheKey, result);
                    return result;
                } catch {
                    // Fall through to error handling
                }
            }

            // Return empty diff on error
            return {
                summary: `Error computing diff: ${error.message}`,
                hasChanges: false,
                metadata: { nameChanged: false, versionChanged: false, descriptionChanged: false },
                stages: { added: [], removed: [], modified: [], moved: [] },
                schemas: { inputChanged: false, outputChanged: false },
                dependencies: []
            };
        }
    }

    /**
     * Format diff result as HTML for webview.
     */
    private formatDiffAsHtml(diff: DiffResult, leftPath: string, rightPath: string): string {
        const leftName = path.basename(leftPath);
        const rightName = path.basename(rightPath);

        return `<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--vscode-panel-border);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .summary {
            background: var(--vscode-textBlockQuote-background);
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .section {
            margin-bottom: 25px;
        }
        .section-title {
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 10px;
            color: var(--vscode-textLink-foreground);
        }
        .stage {
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 4px;
            font-family: var(--vscode-editor-font-family);
        }
        .stage.added {
            background: rgba(40, 167, 69, 0.15);
            border-left: 3px solid #28a745;
        }
        .stage.removed {
            background: rgba(220, 53, 69, 0.15);
            border-left: 3px solid #dc3545;
        }
        .stage.modified {
            background: rgba(255, 193, 7, 0.15);
            border-left: 3px solid #ffc107;
        }
        .stage.moved {
            background: rgba(23, 162, 184, 0.15);
            border-left: 3px solid #17a2b8;
        }
        .change-list {
            margin-left: 20px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }
        .change-item {
            margin: 2px 0;
        }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
        }
        .badge.added { background: #28a745; color: white; }
        .badge.removed { background: #dc3545; color: white; }
        .badge.modified { background: #ffc107; color: black; }
        .no-changes {
            text-align: center;
            padding: 40px;
            color: var(--vscode-descriptionForeground);
        }
        .dep-arrow {
            font-family: monospace;
            color: var(--vscode-descriptionForeground);
        }
    </style>
</head>
<body>
    <div class="header">
        <h2>Pipeline Diff</h2>
        <span>${leftName} → ${rightName}</span>
    </div>

    <div class="summary">
        <strong>Summary:</strong> ${diff.summary || 'No changes'}
    </div>

    ${!diff.hasChanges ? '<div class="no-changes">No differences found</div>' : `

    ${diff.stages.added.length > 0 ? `
    <div class="section">
        <div class="section-title">Added Stages <span class="badge added">${diff.stages.added.length}</span></div>
        ${diff.stages.added.map(s => `
            <div class="stage added">
                <strong>+ ${s.stageId}</strong>
            </div>
        `).join('')}
    </div>
    ` : ''}

    ${diff.stages.removed.length > 0 ? `
    <div class="section">
        <div class="section-title">Removed Stages <span class="badge removed">${diff.stages.removed.length}</span></div>
        ${diff.stages.removed.map(s => `
            <div class="stage removed">
                <strong>- ${s.stageId}</strong>
            </div>
        `).join('')}
    </div>
    ` : ''}

    ${diff.stages.modified.length > 0 ? `
    <div class="section">
        <div class="section-title">Modified Stages <span class="badge modified">${diff.stages.modified.length}</span></div>
        ${diff.stages.modified.map(s => `
            <div class="stage modified">
                <strong>~ ${s.stageId}</strong>
                ${s.changes && s.changes.length > 0 ? `
                <div class="change-list">
                    ${s.changes.slice(0, 5).map(c => `
                        <div class="change-item">
                            ${c.type === 'added' ? '+' : c.type === 'removed' ? '-' : '~'}
                            ${c.field}: ${this.formatValue(c.old)} → ${this.formatValue(c.new)}
                        </div>
                    `).join('')}
                    ${s.changes.length > 5 ? `<div class="change-item">... and ${s.changes.length - 5} more</div>` : ''}
                </div>
                ` : ''}
            </div>
        `).join('')}
    </div>
    ` : ''}

    ${diff.stages.moved.length > 0 ? `
    <div class="section">
        <div class="section-title">Moved Stages</div>
        ${diff.stages.moved.map(s => `
            <div class="stage moved">
                <strong>> ${s.stageId}</strong>
                <span class="change-list">[${s.oldIndex} → ${s.newIndex}]</span>
            </div>
        `).join('')}
    </div>
    ` : ''}

    ${diff.dependencies.length > 0 ? `
    <div class="section">
        <div class="section-title">Dependency Changes</div>
        ${diff.dependencies.map(d => `
            <div class="stage ${d.type}">
                ${d.type === 'added' ? '+' : '-'}
                <span class="dep-arrow">${d.from} → ${d.to}</span>
            </div>
        `).join('')}
    </div>
    ` : ''}

    ${diff.schemas.inputChanged || diff.schemas.outputChanged ? `
    <div class="section">
        <div class="section-title">Schema Changes</div>
        ${diff.schemas.inputChanged ? '<div class="stage modified">~ Input schema changed</div>' : ''}
        ${diff.schemas.outputChanged ? '<div class="stage modified">~ Output schema changed</div>' : ''}
    </div>
    ` : ''}

    `}
</body>
</html>`;
    }

    private formatValue(value: any): string {
        if (value === null || value === undefined) return 'null';
        if (typeof value === 'object') {
            const str = JSON.stringify(value);
            return str.length > 30 ? str.substring(0, 30) + '...' : str;
        }
        return String(value);
    }

    /**
     * Clear the diff cache.
     */
    public clearCache(): void {
        this.diffCache.clear();
    }

    /**
     * Trigger a refresh of the diff view.
     */
    public refresh(uri: vscode.Uri): void {
        this._onDidChange.fire(uri);
    }
}

/**
 * Register the diff command.
 */
export function registerPipelineDiffCommands(
    context: vscode.ExtensionContext,
    provider: PipelineDiffProvider
): void {
    // Command to diff two files
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.diffPipelines', async (leftUri?: vscode.Uri) => {
            let leftPath: string;
            let rightPath: string;

            if (leftUri) {
                leftPath = leftUri.fsPath;
            } else {
                // Prompt for first file
                const leftFiles = await vscode.window.showOpenDialog({
                    canSelectMany: false,
                    filters: { 'Pipeline Files': ['json'] },
                    title: 'Select base pipeline (old)'
                });
                if (!leftFiles || leftFiles.length === 0) return;
                leftPath = leftFiles[0].fsPath;
            }

            // Prompt for second file
            const rightFiles = await vscode.window.showOpenDialog({
                canSelectMany: false,
                filters: { 'Pipeline Files': ['json'] },
                title: 'Select target pipeline (new)'
            });
            if (!rightFiles || rightFiles.length === 0) return;
            rightPath = rightFiles[0].fsPath;

            // Open diff view
            const diffUri = vscode.Uri.parse(
                `flowmason-diff:Pipeline Diff?left=${encodeURIComponent(leftPath)}&right=${encodeURIComponent(rightPath)}`
            );

            const doc = await vscode.workspace.openTextDocument(diffUri);
            await vscode.window.showTextDocument(doc, { preview: true });
        })
    );

    // Command to diff with git HEAD
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.diffWithHead', async (uri?: vscode.Uri) => {
            const filePath = uri?.fsPath || vscode.window.activeTextEditor?.document.uri.fsPath;
            if (!filePath) {
                vscode.window.showErrorMessage('No pipeline file selected');
                return;
            }

            // Check if in git repo
            const { exec } = require('child_process');
            const { promisify } = require('util');
            const execAsync = promisify(exec);

            try {
                // Get HEAD version
                const { stdout } = await execAsync(
                    `git show HEAD:"${path.relative(vscode.workspace.workspaceFolders?.[0].uri.fsPath || '', filePath)}"`,
                    { cwd: vscode.workspace.workspaceFolders?.[0].uri.fsPath }
                );

                // Save to temp file
                const fs = require('fs');
                const os = require('os');
                const tempDir = os.tmpdir();
                const tempFile = path.join(tempDir, `HEAD-${path.basename(filePath)}`);
                fs.writeFileSync(tempFile, stdout);

                // Open native diff
                const leftUri = vscode.Uri.file(tempFile);
                const rightUri = vscode.Uri.file(filePath);

                await vscode.commands.executeCommand(
                    'vscode.diff',
                    leftUri,
                    rightUri,
                    `HEAD ↔ ${path.basename(filePath)}`
                );
            } catch (error: any) {
                vscode.window.showErrorMessage(`Failed to get git HEAD: ${error.message}`);
            }
        })
    );

    // Register content provider
    context.subscriptions.push(
        vscode.workspace.registerTextDocumentContentProvider(
            'flowmason-diff',
            provider
        )
    );
}
