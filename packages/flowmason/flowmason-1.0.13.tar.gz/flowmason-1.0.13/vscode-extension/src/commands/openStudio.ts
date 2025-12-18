/**
 * Open Studio Command
 *
 * Opens FlowMason Studio API documentation in the browser.
 */

import * as vscode from 'vscode';
import {
    getBackendPort,
    getHost,
} from '../types/installation';

export function registerOpenStudioCommand(context: vscode.ExtensionContext): void {
    const command = vscode.commands.registerCommand('flowmason.openStudio', async () => {
        const host = getHost();
        const port = getBackendPort();
        const studioUrl = `http://${host}:${port}/docs`;

        vscode.env.openExternal(vscode.Uri.parse(studioUrl));
    });

    context.subscriptions.push(command);
}
