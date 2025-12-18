"use strict";
/**
 * Import Package Command
 *
 * Import a local .fmpkg package file into the FlowMason project.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerImportPackageCommand = registerImportPackageCommand;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const child_process_1 = require("child_process");
/**
 * Register the import package command.
 */
function registerImportPackageCommand(context, outputChannel) {
    const command = vscode.commands.registerCommand('flowmason.importPackage', async () => {
        // Show file picker for .fmpkg files
        const fileUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: {
                'FlowMason Package': ['fmpkg'],
            },
            title: 'Select FlowMason Package to Import',
        });
        if (!fileUri || fileUri.length === 0) {
            return; // User cancelled
        }
        const packagePath = fileUri[0].fsPath;
        const packageName = path.basename(packagePath);
        outputChannel.appendLine(`Importing package: ${packagePath}`);
        outputChannel.show();
        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Importing ${packageName}...`,
            cancellable: false,
        }, async (progress) => {
            try {
                // Try to find flowmason CLI
                const fmCommand = await findFlowMasonCLI();
                if (!fmCommand) {
                    throw new Error('FlowMason CLI not found. Install with: pip install flowmason');
                }
                progress.report({ message: 'Installing package...' });
                // Run install command
                const result = await runCommand(fmCommand, ['install', packagePath], outputChannel);
                if (result.success) {
                    outputChannel.appendLine('Package installed successfully');
                    // Parse manifest info from output
                    const manifestInfo = parseManifestFromOutput(result.output);
                    // Show success message
                    const message = manifestInfo
                        ? `Package "${manifestInfo.name}@${manifestInfo.version}" imported successfully`
                        : `Package "${packageName}" imported successfully`;
                    const action = await vscode.window.showInformationMessage(message, 'Refresh Registry', 'Dismiss');
                    if (action === 'Refresh Registry') {
                        vscode.commands.executeCommand('flowmason.refreshRegistry');
                    }
                }
                else {
                    throw new Error(result.error || 'Failed to install package');
                }
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                outputChannel.appendLine(`Error: ${errorMessage}`);
                vscode.window.showErrorMessage(`Failed to import package: ${errorMessage}`);
            }
        });
    });
    context.subscriptions.push(command);
}
/**
 * Find the FlowMason CLI command.
 */
async function findFlowMasonCLI() {
    // Try different command names
    const commands = ['fm', 'flowmason', 'python -m flowmason'];
    for (const cmd of commands) {
        try {
            (0, child_process_1.execSync)(`${cmd} --version`, { stdio: 'pipe' });
            return cmd;
        }
        catch {
            continue;
        }
    }
    return null;
}
/**
 * Run a command and capture output.
 */
function runCommand(command, args, outputChannel) {
    return new Promise((resolve) => {
        let output = '';
        let error = '';
        // Handle command with spaces (like "python -m flowmason")
        let cmd = command;
        let allArgs = args;
        if (command.includes(' ')) {
            const parts = command.split(' ');
            cmd = parts[0];
            allArgs = [...parts.slice(1), ...args];
        }
        const proc = (0, child_process_1.spawn)(cmd, allArgs, {
            shell: true,
            cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
        });
        proc.stdout.on('data', (data) => {
            const text = data.toString();
            output += text;
            outputChannel.append(text);
        });
        proc.stderr.on('data', (data) => {
            const text = data.toString();
            error += text;
            outputChannel.append(text);
        });
        proc.on('close', (code) => {
            resolve({
                success: code === 0,
                output,
                error: code !== 0 ? error : undefined,
            });
        });
        proc.on('error', (err) => {
            resolve({
                success: false,
                output,
                error: err.message,
            });
        });
    });
}
/**
 * Parse manifest info from CLI output.
 */
function parseManifestFromOutput(output) {
    // Try to extract name and version from the output
    const nameMatch = output.match(/Name:\s*(.+)/);
    const versionMatch = output.match(/Version:\s*(.+)/);
    if (nameMatch && versionMatch) {
        return {
            name: nameMatch[1].trim(),
            version: versionMatch[1].trim(),
        };
    }
    return null;
}
//# sourceMappingURL=importPackage.js.map