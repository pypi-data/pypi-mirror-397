/**
 * Manage FlowMason Studio Commands
 *
 * Start, stop, and restart the FlowMason Studio server from VSCode.
 * Uses the `fm studio` CLI commands for compatibility with pip installs.
 * Reads installation info from ~/.flowmason/installation.json
 */

import * as vscode from 'vscode';
import { spawn } from 'child_process';
import {
    getInstallationInfo,
    updateInstallationInfo,
    isBackendRunning,
    getBackendPort,
    getHost,
    DEFAULT_BACKEND_PORT,
} from '../types/installation';

/**
 * Start FlowMason Studio (backend only - uses fm CLI)
 */
async function startStudio(outputChannel: vscode.OutputChannel): Promise<boolean> {
    const info = getInstallationInfo();
    const config = vscode.workspace.getConfiguration('flowmason');

    // Get ports
    const backendPort = info?.studio_port || DEFAULT_BACKEND_PORT;
    const host = '127.0.0.1';

    outputChannel.appendLine('=== Starting FlowMason Studio ===');
    outputChannel.appendLine(`Backend: ${host}:${backendPort}`);
    outputChannel.show();

    // Use fm studio start command (works with pip install)
    outputChannel.appendLine('\n--- Starting Backend via CLI ---');
    outputChannel.appendLine('Running: fm studio start --background');

    const backendChild = spawn('fm', ['studio', 'start', '--background', '--port', backendPort.toString(), '--host', host], {
        detached: true,
        stdio: ['ignore', 'pipe', 'pipe'],
        shell: true,
    });

    backendChild.stdout?.on('data', (data) => outputChannel.append(`${data}`));
    backendChild.stderr?.on('data', (data) => outputChannel.append(`${data}`));
    backendChild.on('error', (error) => {
        outputChannel.appendLine(`Error: ${error.message}`);
        outputChannel.appendLine('\nIf "fm" command not found, install FlowMason: pip install flowmason');
    });

    // Wait for CLI to complete
    await new Promise<void>((resolve) => {
        backendChild.on('close', () => resolve());
        // Timeout after 10 seconds
        setTimeout(resolve, 10000);
    });

    // Wait and verify
    outputChannel.appendLine('\n--- Verifying startup ---');
    await new Promise(resolve => setTimeout(resolve, 3000));

    const backendStarted = await isBackendRunning();
    outputChannel.appendLine(`Backend running: ${backendStarted}`);

    if (backendStarted) {
        // Update installation info
        updateInstallationInfo({
            studio_port: backendPort,
            studio_host: host,
            studio_started_at: new Date().toISOString(),
        });

        vscode.window.showInformationMessage(
            `FlowMason Studio started at http://${host}:${backendPort}`,
            'Open API Docs'
        ).then(action => {
            if (action === 'Open API Docs') {
                vscode.env.openExternal(vscode.Uri.parse(`http://${host}:${backendPort}/docs`));
            }
        });
        return true;
    } else {
        vscode.window.showErrorMessage(
            'Failed to start FlowMason Studio. Make sure FlowMason is installed: pip install flowmason',
            'Show Output'
        ).then(action => {
            if (action === 'Show Output') {
                outputChannel.show();
            }
        });
        return false;
    }
}

/**
 * Stop FlowMason Studio (uses fm CLI)
 */
async function stopStudio(outputChannel: vscode.OutputChannel): Promise<boolean> {
    outputChannel.appendLine('=== Stopping FlowMason Studio ===');
    outputChannel.show();

    // Use fm studio stop command
    outputChannel.appendLine('\n--- Stopping Backend via CLI ---');
    outputChannel.appendLine('Running: fm studio stop');

    const stopChild = spawn('fm', ['studio', 'stop'], {
        stdio: ['ignore', 'pipe', 'pipe'],
        shell: true,
    });

    stopChild.stdout?.on('data', (data) => outputChannel.append(`${data}`));
    stopChild.stderr?.on('data', (data) => outputChannel.append(`${data}`));

    // Wait for CLI to complete
    await new Promise<void>((resolve) => {
        stopChild.on('close', () => resolve());
        setTimeout(resolve, 5000);
    });

    // Clear state
    updateInstallationInfo({
        studio_pid: null,
        studio_started_at: null,
        frontend_pid: null,
        frontend_started_at: null,
    });

    outputChannel.appendLine('\nStudio stopped');
    vscode.window.showInformationMessage('FlowMason Studio stopped');
    return true;
}

/**
 * Restart FlowMason Studio
 */
async function restartStudio(outputChannel: vscode.OutputChannel): Promise<boolean> {
    outputChannel.appendLine('=== Restarting FlowMason Studio ===');
    outputChannel.show();

    await stopStudio(outputChannel);
    await new Promise(resolve => setTimeout(resolve, 1000));
    return startStudio(outputChannel);
}

/**
 * Show studio status
 */
async function showStudioStatus(): Promise<void> {
    const backendRunning = await isBackendRunning();
    const backendPort = getBackendPort();
    const host = getHost();

    let status = 'FlowMason Studio Status:\n\n';
    status += `Backend (${host}:${backendPort}): ${backendRunning ? '✓ Running' : '✗ Stopped'}`;

    const actions: string[] = [];
    if (backendRunning) {
        actions.push('Open API Docs', 'Stop', 'Restart');
    } else {
        actions.push('Start Studio');
    }

    const action = await vscode.window.showInformationMessage(status, ...actions);

    if (action === 'Open API Docs') {
        vscode.env.openExternal(vscode.Uri.parse(`http://${host}:${backendPort}/docs`));
    } else if (action === 'Stop') {
        const outputChannel = vscode.window.createOutputChannel('FlowMason');
        await stopStudio(outputChannel);
    } else if (action === 'Restart') {
        const outputChannel = vscode.window.createOutputChannel('FlowMason');
        await restartStudio(outputChannel);
    } else if (action === 'Start Studio') {
        const outputChannel = vscode.window.createOutputChannel('FlowMason');
        await startStudio(outputChannel);
    }
}

export function registerManageStudioCommands(context: vscode.ExtensionContext, outputChannel: vscode.OutputChannel): void {
    // Start Studio command
    const startCommand = vscode.commands.registerCommand('flowmason.startStudio', async () => {
        const backendRunning = await isBackendRunning();

        if (backendRunning) {
            const port = getBackendPort();
            const action = await vscode.window.showWarningMessage(
                'FlowMason Studio is already running',
                'Open API Docs',
                'Restart'
            );
            if (action === 'Open API Docs') {
                vscode.env.openExternal(vscode.Uri.parse(`http://127.0.0.1:${port}/docs`));
            } else if (action === 'Restart') {
                await restartStudio(outputChannel);
            }
        } else {
            await startStudio(outputChannel);
        }
    });

    // Stop Studio command
    const stopCommand = vscode.commands.registerCommand('flowmason.stopStudio', async () => {
        const backendRunning = await isBackendRunning();

        if (!backendRunning) {
            vscode.window.showInformationMessage('FlowMason Studio is not running');
        } else {
            await stopStudio(outputChannel);
        }
    });

    // Restart Studio command
    const restartCommand = vscode.commands.registerCommand('flowmason.restartStudio', async () => {
        await restartStudio(outputChannel);
    });

    // Status command
    const statusCommand = vscode.commands.registerCommand('flowmason.studioStatus', async () => {
        await showStudioStatus();
    });

    context.subscriptions.push(startCommand, stopCommand, restartCommand, statusCommand);
}
