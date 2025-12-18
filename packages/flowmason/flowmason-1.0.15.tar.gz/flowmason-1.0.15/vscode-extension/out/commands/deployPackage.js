"use strict";
/**
 * Deploy Package Command
 *
 * Deploys a FlowMason package to the local packages directory.
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
exports.registerDeployPackageCommand = registerDeployPackageCommand;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const os = __importStar(require("os"));
function registerDeployPackageCommand(context, outputChannel) {
    const command = vscode.commands.registerCommand('flowmason.deployPackage', async (uri) => {
        try {
            const config = vscode.workspace.getConfiguration('flowmason');
            const packagesPath = config.get('packagesDirectory') || '~/.flowmason/packages';
            const packagesDir = packagesPath.replace(/^~/, os.homedir());
            let sourcePath;
            if (uri) {
                sourcePath = uri.fsPath;
            }
            else {
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
                }
                else {
                    const selection = await vscode.window.showQuickPick(files.map(f => ({
                        label: path.basename(path.dirname(f.fsPath)),
                        description: path.dirname(f.fsPath),
                        path: path.dirname(f.fsPath),
                    })), { placeHolder: 'Select package to deploy' });
                    if (!selection)
                        return;
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
                const overwrite = await vscode.window.showWarningMessage(`Package "${packageId}" already exists. Overwrite?`, 'Overwrite', 'Cancel');
                if (overwrite !== 'Overwrite')
                    return;
                fs.rmSync(targetDir, { recursive: true });
            }
            // Copy files
            outputChannel.appendLine(`Deploying package: ${manifest.name} v${manifest.version}`);
            outputChannel.appendLine(`Source: ${sourcePath}`);
            outputChannel.appendLine(`Target: ${targetDir}`);
            copyDirectory(sourcePath, targetDir);
            outputChannel.appendLine('Package deployed successfully!');
            outputChannel.show();
            vscode.window.showInformationMessage(`Package "${manifest.name}" deployed successfully`, 'Open Studio', 'Refresh').then(action => {
                if (action === 'Open Studio') {
                    vscode.commands.executeCommand('flowmason.openStudio');
                }
                else if (action === 'Refresh') {
                    vscode.commands.executeCommand('flowmason.refreshRegistry');
                }
            });
        }
        catch (error) {
            outputChannel.appendLine(`Error deploying package: ${error}`);
            vscode.window.showErrorMessage(`Failed to deploy package: ${error}`);
        }
    });
    context.subscriptions.push(command);
}
function copyDirectory(src, dest) {
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
        }
        else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}
//# sourceMappingURL=deployPackage.js.map