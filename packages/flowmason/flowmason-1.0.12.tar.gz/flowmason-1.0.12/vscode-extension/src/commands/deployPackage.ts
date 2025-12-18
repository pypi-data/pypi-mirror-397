/**
 * Deploy Package Command
 *
 * Deploys a FlowMason package to the local packages directory.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';

export function registerDeployPackageCommand(
    context: vscode.ExtensionContext,
    outputChannel: vscode.OutputChannel
): void {
    const command = vscode.commands.registerCommand('flowmason.deployPackage', async (uri?: vscode.Uri) => {
        try {
            const config = vscode.workspace.getConfiguration('flowmason');
            const packagesPath = config.get<string>('packagesDirectory') || '~/.flowmason/packages';
            const packagesDir = packagesPath.replace(/^~/, os.homedir());

            let sourcePath: string | undefined;

            if (uri) {
                sourcePath = uri.fsPath;
            } else {
                // Find package in workspace
                const workspaceFolders = vscode.workspace.workspaceFolders;
                if (!workspaceFolders) {
                    vscode.window.showErrorMessage('No workspace folder open');
                    return;
                }

                const files = await vscode.workspace.findFiles('**/flowmason-package.json', '**/node_modules/**');

                if (files.length === 0) {
                    vscode.window.showErrorMessage('No FlowMason package found in workspace');
                    return;
                }

                if (files.length === 1) {
                    sourcePath = path.dirname(files[0].fsPath);
                } else {
                    const selection = await vscode.window.showQuickPick(
                        files.map(f => ({
                            label: path.basename(path.dirname(f.fsPath)),
                            description: path.dirname(f.fsPath),
                            path: path.dirname(f.fsPath),
                        })),
                        { placeHolder: 'Select package to deploy' }
                    );

                    if (!selection) return;
                    sourcePath = selection.path;
                }
            }

            if (!sourcePath) {
                vscode.window.showErrorMessage('Could not determine package source');
                return;
            }

            // Validate the source has a manifest
            const manifestPath = path.join(sourcePath, 'flowmason-package.json');
            if (!fs.existsSync(manifestPath)) {
                vscode.window.showErrorMessage('Package manifest not found');
                return;
            }

            // Read manifest
            const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
            const packageId = manifest.id || path.basename(sourcePath);

            // Create packages directory if needed
            if (!fs.existsSync(packagesDir)) {
                fs.mkdirSync(packagesDir, { recursive: true });
            }

            const targetDir = path.join(packagesDir, packageId);

            // Check if package already exists
            if (fs.existsSync(targetDir)) {
                const overwrite = await vscode.window.showWarningMessage(
                    `Package "${packageId}" already exists. Overwrite?`,
                    'Overwrite',
                    'Cancel'
                );

                if (overwrite !== 'Overwrite') return;

                fs.rmSync(targetDir, { recursive: true });
            }

            // Copy files
            outputChannel.appendLine(`Deploying package: ${manifest.name} v${manifest.version}`);
            outputChannel.appendLine(`Source: ${sourcePath}`);
            outputChannel.appendLine(`Target: ${targetDir}`);

            copyDirectory(sourcePath, targetDir);

            outputChannel.appendLine('Package deployed successfully!');
            outputChannel.show();

            vscode.window.showInformationMessage(
                `Package "${manifest.name}" deployed successfully`,
                'Open Studio',
                'Refresh'
            ).then(action => {
                if (action === 'Open Studio') {
                    vscode.commands.executeCommand('flowmason.openStudio');
                } else if (action === 'Refresh') {
                    vscode.commands.executeCommand('flowmason.refreshRegistry');
                }
            });

        } catch (error) {
            outputChannel.appendLine(`Error deploying package: ${error}`);
            vscode.window.showErrorMessage(`Failed to deploy package: ${error}`);
        }
    });

    context.subscriptions.push(command);
}

function copyDirectory(src: string, dest: string): void {
    fs.mkdirSync(dest, { recursive: true });
    const entries = fs.readdirSync(src, { withFileTypes: true });

    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);

        // Skip certain directories/files
        if (entry.name === '__pycache__' || entry.name === '.git' || entry.name === 'dist') {
            continue;
        }

        if (entry.isDirectory()) {
            copyDirectory(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}
