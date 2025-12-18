/**
 * Open Docs Command
 *
 * Opens FlowMason documentation.
 */

import * as vscode from 'vscode';

export function registerOpenDocsCommand(context: vscode.ExtensionContext): void {
    const command = vscode.commands.registerCommand('flowmason.openDocs', async () => {
        const options = [
            { label: 'Component Development Guide', url: 'docs/component-development-guide.md' },
            { label: 'Package Format', url: 'docs/package-format.md' },
            { label: 'API Reference', url: 'docs/api-reference.md' },
            { label: 'Architecture Rules', url: 'docs/architecture-rules.md' },
            { label: 'Studio User Guide', url: 'docs/studio-user-guide.md' },
        ];

        const selection = await vscode.window.showQuickPick(options, {
            placeHolder: 'Select documentation to open',
        });

        if (!selection) return;

        // Try to find the doc in the workspace first
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders) {
            const files = await vscode.workspace.findFiles(`**/${selection.url}`);
            if (files.length > 0) {
                const doc = await vscode.workspace.openTextDocument(files[0]);
                await vscode.window.showTextDocument(doc);
                return;
            }
        }

        // Open online documentation (fallback)
        vscode.window.showInformationMessage(
            `Documentation: ${selection.label}. Check the docs folder in the FlowMason repository.`
        );
    });

    context.subscriptions.push(command);
}
