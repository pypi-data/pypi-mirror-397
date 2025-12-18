"use strict";
/**
 * Validate Manifest Command
 *
 * Validates a FlowMason package manifest.
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
exports.registerValidateManifestCommand = registerValidateManifestCommand;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
function registerValidateManifestCommand(context, outputChannel) {
    const command = vscode.commands.registerCommand('flowmason.validateManifest', async (uri) => {
        try {
            let manifestPath;
            if (uri) {
                manifestPath = uri.fsPath;
            }
            else {
                // Check active editor
                const editor = vscode.window.activeTextEditor;
                if (editor && editor.document.fileName.endsWith('flowmason-package.json')) {
                    manifestPath = editor.document.uri.fsPath;
                }
                else {
                    // Search for manifest in workspace
                    const files = await vscode.workspace.findFiles('**/flowmason-package.json', '**/node_modules/**');
                    if (files.length === 0) {
                        vscode.window.showErrorMessage('No flowmason-package.json found');
                        return;
                    }
                    if (files.length === 1) {
                        manifestPath = files[0].fsPath;
                    }
                    else {
                        const selection = await vscode.window.showQuickPick(files.map(f => ({
                            label: path.dirname(f.fsPath),
                            description: f.fsPath,
                            path: f.fsPath,
                        })), { placeHolder: 'Select manifest to validate' });
                        if (!selection)
                            return;
                        manifestPath = selection.path;
                    }
                }
            }
            if (!manifestPath || !fs.existsSync(manifestPath)) {
                vscode.window.showErrorMessage('Manifest file not found');
                return;
            }
            outputChannel.appendLine(`Validating: ${manifestPath}`);
            outputChannel.appendLine('');
            // Read and parse manifest
            let manifest;
            try {
                const content = fs.readFileSync(manifestPath, 'utf-8');
                manifest = JSON.parse(content);
            }
            catch (error) {
                outputChannel.appendLine('ERROR: Invalid JSON');
                outputChannel.appendLine(`${error}`);
                outputChannel.show();
                vscode.window.showErrorMessage('Invalid JSON in manifest file');
                return;
            }
            // Validate fields
            const errors = [];
            const warnings = [];
            // Required fields
            if (!manifest.id) {
                errors.push('Missing required field: id');
            }
            else if (!/^[a-z][a-z0-9-]*$/.test(manifest.id)) {
                errors.push('id must be kebab-case (lowercase letters, numbers, hyphens)');
            }
            if (!manifest.name) {
                errors.push('Missing required field: name');
            }
            if (!manifest.version) {
                errors.push('Missing required field: version');
            }
            else if (!/^\d+\.\d+\.\d+/.test(manifest.version)) {
                errors.push('version must be semver format (e.g., 1.0.0)');
            }
            // Recommended fields
            if (!manifest.description) {
                warnings.push('Missing recommended field: description');
            }
            if (!manifest.author) {
                warnings.push('Missing recommended field: author');
            }
            if (!manifest.license) {
                warnings.push('Missing recommended field: license');
            }
            // Components array
            if (manifest.components) {
                if (!Array.isArray(manifest.components)) {
                    errors.push('components must be an array');
                }
                else {
                    const components = manifest.components;
                    for (let i = 0; i < components.length; i++) {
                        const comp = components[i];
                        if (!comp.type) {
                            errors.push(`components[${i}]: missing type`);
                        }
                        if (!comp.name) {
                            errors.push(`components[${i}]: missing name`);
                        }
                    }
                }
            }
            // Dependencies
            if (manifest.dependencies) {
                if (typeof manifest.dependencies !== 'object') {
                    errors.push('dependencies must be an object');
                }
            }
            // Check for index.py
            const packageDir = path.dirname(manifestPath);
            const indexPath = path.join(packageDir, 'index.py');
            if (!fs.existsSync(indexPath)) {
                warnings.push('Missing index.py entry point');
            }
            // Output results
            outputChannel.appendLine('=== Validation Results ===');
            outputChannel.appendLine('');
            if (errors.length === 0 && warnings.length === 0) {
                outputChannel.appendLine('✓ Manifest is valid!');
                vscode.window.showInformationMessage('Manifest is valid');
            }
            else {
                if (errors.length > 0) {
                    outputChannel.appendLine(`ERRORS (${errors.length}):`);
                    errors.forEach(e => outputChannel.appendLine(`  ✗ ${e}`));
                    outputChannel.appendLine('');
                }
                if (warnings.length > 0) {
                    outputChannel.appendLine(`WARNINGS (${warnings.length}):`);
                    warnings.forEach(w => outputChannel.appendLine(`  ⚠ ${w}`));
                    outputChannel.appendLine('');
                }
                if (errors.length > 0) {
                    vscode.window.showErrorMessage(`Manifest has ${errors.length} error(s)`);
                }
                else {
                    vscode.window.showWarningMessage(`Manifest has ${warnings.length} warning(s)`);
                }
            }
            outputChannel.show();
        }
        catch (error) {
            outputChannel.appendLine(`Error validating manifest: ${error}`);
            vscode.window.showErrorMessage(`Failed to validate manifest: ${error}`);
        }
    });
    context.subscriptions.push(command);
}
//# sourceMappingURL=validateManifest.js.map