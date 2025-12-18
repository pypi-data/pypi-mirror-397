"use strict";
/**
 * Build Package Command
 *
 * Builds a FlowMason package from the current workspace or file.
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
exports.registerBuildPackageCommand = registerBuildPackageCommand;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
function registerBuildPackageCommand(context, outputChannel) {
    const command = vscode.commands.registerCommand('flowmason.buildPackage', async (uri) => {
        try {
            // Determine the package directory
            let packageDir;
            if (uri) {
                // Called from context menu on flowmason-package.json
                packageDir = path.dirname(uri.fsPath);
            }
            else {
                // Called from command palette - look for flowmason-package.json
                const workspaceFolders = vscode.workspace.workspaceFolders;
                if (!workspaceFolders) {
                    vscode.window.showErrorMessage('No workspace folder open');
                    return;
                }
                // Search for flowmason-package.json in workspace
                const files = await vscode.workspace.findFiles('**/flowmason-package.json', '**/node_modules/**');
                if (files.length === 0) {
                    // Offer to create a new package
                    const create = await vscode.window.showQuickPick(['Create New Package', 'Cancel'], { placeHolder: 'No flowmason-package.json found' });
                    if (create === 'Create New Package') {
                        await createPackageManifest(workspaceFolders[0].uri.fsPath);
                    }
                    return;
                }
                else if (files.length === 1) {
                    packageDir = path.dirname(files[0].fsPath);
                }
                else {
                    // Multiple packages - let user choose
                    const selection = await vscode.window.showQuickPick(files.map(f => ({
                        label: path.dirname(f.fsPath),
                        description: f.fsPath,
                        uri: f,
                    })), { placeHolder: 'Select package to build' });
                    if (!selection)
                        return;
                    packageDir = path.dirname(selection.uri.fsPath);
                }
            }
            if (!packageDir) {
                vscode.window.showErrorMessage('Could not determine package directory');
                return;
            }
            // Validate manifest exists
            const manifestPath = path.join(packageDir, 'flowmason-package.json');
            if (!fs.existsSync(manifestPath)) {
                vscode.window.showErrorMessage('flowmason-package.json not found');
                return;
            }
            // Read and validate manifest
            const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
            const errors = validateManifest(manifest);
            if (errors.length > 0) {
                outputChannel.appendLine('Package validation errors:');
                errors.forEach(e => outputChannel.appendLine(`  - ${e}`));
                outputChannel.show();
                vscode.window.showErrorMessage(`Package has ${errors.length} validation error(s). See output for details.`);
                return;
            }
            // Build the package
            outputChannel.appendLine(`Building package: ${manifest.name} v${manifest.version}`);
            outputChannel.show();
            const outputDir = path.join(packageDir, 'dist');
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }
            const packageFileName = `${manifest.id}-${manifest.version}.fmpkg`;
            const outputPath = path.join(outputDir, packageFileName);
            // Create the package (ZIP file)
            const packageOutDir = await createPackageDirectory(packageDir, outputPath, manifest, outputChannel);
            outputChannel.appendLine(`Package built successfully: ${packageOutDir}`);
            vscode.window.showInformationMessage(`Package built: ${path.basename(packageOutDir)}`, 'Open Folder', 'Deploy').then(action => {
                if (action === 'Open Folder') {
                    vscode.commands.executeCommand('revealFileInOS', vscode.Uri.file(packageOutDir));
                }
                else if (action === 'Deploy') {
                    vscode.commands.executeCommand('flowmason.deployPackage', vscode.Uri.file(packageOutDir));
                }
            });
        }
        catch (error) {
            outputChannel.appendLine(`Error building package: ${error}`);
            vscode.window.showErrorMessage(`Failed to build package: ${error}`);
        }
    });
    context.subscriptions.push(command);
}
async function createPackageManifest(workspaceDir) {
    const packageId = await vscode.window.showInputBox({
        prompt: 'Enter package ID (kebab-case)',
        placeHolder: 'my-custom-nodes',
        validateInput: (value) => {
            if (!value)
                return 'Package ID is required';
            if (!/^[a-z][a-z0-9-]*$/.test(value)) {
                return 'Package ID must be kebab-case';
            }
            return null;
        },
    });
    if (!packageId)
        return;
    const packageName = await vscode.window.showInputBox({
        prompt: 'Enter package name',
        placeHolder: 'My Custom Nodes',
    });
    if (!packageName)
        return;
    const description = await vscode.window.showInputBox({
        prompt: 'Enter package description',
        placeHolder: 'A collection of custom FlowMason nodes',
    });
    const manifest = {
        id: packageId,
        name: packageName,
        version: '1.0.0',
        description: description || '',
        author: '',
        license: 'MIT',
        components: [],
        dependencies: {
            flowmason_core: '>=1.0.0',
        },
    };
    const manifestPath = path.join(workspaceDir, 'flowmason-package.json');
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
    // Also create an index.py
    const indexPath = path.join(workspaceDir, 'index.py');
    if (!fs.existsSync(indexPath)) {
        fs.writeFileSync(indexPath, `"""
${packageName}

${description || 'A custom FlowMason package.'}
"""

# Import your components here
# from .my_node import MyNode
# from .my_operator import MyOperator

# Export components for registration
__all__ = []
`);
    }
    const doc = await vscode.workspace.openTextDocument(manifestPath);
    await vscode.window.showTextDocument(doc);
    vscode.window.showInformationMessage('Package manifest created. Add your components to index.py');
}
function validateManifest(manifest) {
    const errors = [];
    if (!manifest.id)
        errors.push('Missing required field: id');
    if (!manifest.name)
        errors.push('Missing required field: name');
    if (!manifest.version)
        errors.push('Missing required field: version');
    if (manifest.id && !/^[a-z][a-z0-9-]*$/.test(manifest.id)) {
        errors.push('Package ID must be kebab-case (lowercase letters, numbers, hyphens)');
    }
    if (manifest.version && !/^\d+\.\d+\.\d+/.test(manifest.version)) {
        errors.push('Version must be semver format (e.g., 1.0.0)');
    }
    return errors;
}
async function createPackageDirectory(sourceDir, _outputPath, manifest, outputChannel) {
    // Create a package directory with all the files
    const packageName = `${manifest.name}-${manifest.version}`;
    const distDir = path.join(sourceDir, 'dist');
    const packageOutDir = path.join(distDir, packageName);
    // Create dist directory if it doesn't exist
    if (!fs.existsSync(distDir)) {
        fs.mkdirSync(distDir, { recursive: true });
    }
    // Clean up existing package directory
    if (fs.existsSync(packageOutDir)) {
        fs.rmSync(packageOutDir, { recursive: true });
    }
    fs.mkdirSync(packageOutDir, { recursive: true });
    // Copy manifest
    fs.copyFileSync(path.join(sourceDir, 'flowmason-package.json'), path.join(packageOutDir, 'flowmason-package.json'));
    // Copy Python files
    const files = fs.readdirSync(sourceDir);
    for (const file of files) {
        if (file.endsWith('.py')) {
            fs.copyFileSync(path.join(sourceDir, file), path.join(packageOutDir, file));
        }
    }
    outputChannel.appendLine(`Package directory created at: ${packageOutDir}`);
    return packageOutDir;
}
//# sourceMappingURL=buildPackage.js.map