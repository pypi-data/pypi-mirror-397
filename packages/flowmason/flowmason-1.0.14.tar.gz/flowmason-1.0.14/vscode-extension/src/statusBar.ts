/**
 * FlowMason Status Bar
 *
 * Shows Studio status and provides quick actions for start/stop/restart.
 */

import * as vscode from 'vscode';
import {
    getInstallationInfo,
    getFrontendPort,
    getBackendPort,
    isBackendRunning,
} from './types/installation';

export function createStudioStatusBar(context: vscode.ExtensionContext): vscode.StatusBarItem {
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );

    // Initial state
    statusBarItem.text = '$(loading~spin) FlowMason';
    statusBarItem.tooltip = 'Checking FlowMason Studio status...';
    statusBarItem.command = 'flowmason.studioQuickPick';
    statusBarItem.show();

    // Register the quick pick command
    const quickPickCommand = vscode.commands.registerCommand('flowmason.studioQuickPick', async () => {
        const backendRunning = await isBackendRunning();
        const frontendPort = getFrontendPort();
        const backendPort = getBackendPort();

        const items: vscode.QuickPickItem[] = [];

        if (backendRunning) {
            items.push(
                { label: '$(browser) Open Frontend', description: `http://127.0.0.1:${frontendPort}` },
                { label: '$(link-external) Open API Docs', description: `http://127.0.0.1:${backendPort}/docs` },
                { label: '$(debug-restart) Restart Studio', description: 'Stop and start Studio' },
                { label: '$(stop-circle) Stop Studio', description: 'Stop both backend and frontend' }
            );
        } else {
            items.push(
                { label: '$(play) Start Studio', description: 'Start backend and frontend servers' }
            );
        }

        items.push(
            { label: '$(info) Show Status', description: 'View detailed Studio status' }
        );

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'FlowMason Studio Actions'
        });

        if (selected) {
            switch (selected.label) {
                case '$(browser) Open Frontend':
                    vscode.env.openExternal(vscode.Uri.parse(`http://127.0.0.1:${frontendPort}`));
                    break;
                case '$(link-external) Open API Docs':
                    vscode.env.openExternal(vscode.Uri.parse(`http://127.0.0.1:${backendPort}/docs`));
                    break;
                case '$(play) Start Studio':
                    vscode.commands.executeCommand('flowmason.startStudio');
                    break;
                case '$(debug-restart) Restart Studio':
                    vscode.commands.executeCommand('flowmason.restartStudio');
                    break;
                case '$(stop-circle) Stop Studio':
                    vscode.commands.executeCommand('flowmason.stopStudio');
                    break;
                case '$(info) Show Status':
                    vscode.commands.executeCommand('flowmason.studioStatus');
                    break;
            }
        }
    });

    context.subscriptions.push(quickPickCommand);
    context.subscriptions.push(statusBarItem);

    // Function to update status
    async function updateStatus() {
        const running = await isBackendRunning();
        if (running) {
            statusBarItem.text = '$(check) FlowMason';
            statusBarItem.tooltip = 'FlowMason Studio is running - Click for actions';
            statusBarItem.backgroundColor = undefined;
        } else {
            statusBarItem.text = '$(circle-slash) FlowMason';
            statusBarItem.tooltip = 'FlowMason Studio is stopped - Click to start';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        }
    }

    // Initial update
    updateStatus();

    // Periodic update every 10 seconds
    const interval = setInterval(updateStatus, 10000);
    context.subscriptions.push({ dispose: () => clearInterval(interval) });

    return statusBarItem;
}
