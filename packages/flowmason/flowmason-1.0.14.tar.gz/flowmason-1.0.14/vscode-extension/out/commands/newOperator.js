"use strict";
/**
 * New Operator Command
 *
 * Creates a new FlowMason operator with interactive prompts.
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
exports.registerNewOperatorCommand = registerNewOperatorCommand;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const operatorTemplate_1 = require("../templates/operatorTemplate");
function registerNewOperatorCommand(context) {
    const command = vscode.commands.registerCommand('flowmason.newOperator', async () => {
        try {
            // Get operator name
            const name = await vscode.window.showInputBox({
                prompt: 'Enter the operator name (kebab-case)',
                placeHolder: 'json-parser',
                validateInput: (value) => {
                    if (!value)
                        return 'Name is required';
                    if (!/^[a-z][a-z0-9-]*$/.test(value)) {
                        return 'Name must be kebab-case (lowercase letters, numbers, hyphens)';
                    }
                    return null;
                },
            });
            if (!name)
                return;
            // Get class name (derived from operator name by default)
            const defaultClassName = name
                .split('-')
                .map(part => part.charAt(0).toUpperCase() + part.slice(1))
                .join('') + 'Operator';
            const className = await vscode.window.showInputBox({
                prompt: 'Enter the class name',
                value: defaultClassName,
                validateInput: (value) => {
                    if (!value)
                        return 'Class name is required';
                    if (!/^[A-Z][a-zA-Z0-9]*$/.test(value)) {
                        return 'Class name must be PascalCase';
                    }
                    return null;
                },
            });
            if (!className)
                return;
            // Get category
            const category = await vscode.window.showQuickPick([
                { label: 'transform', description: 'Data transformation' },
                { label: 'validation', description: 'Data validation' },
                { label: 'parsing', description: 'Parsing and extraction' },
                { label: 'filter', description: 'Filtering and selection' },
                { label: 'aggregation', description: 'Data aggregation' },
                { label: 'format', description: 'Format conversion' },
                { label: 'utility', description: 'Utility functions' },
                { label: 'custom', description: 'Custom category' },
            ], {
                placeHolder: 'Select a category',
            });
            if (!category)
                return;
            let finalCategory = category.label;
            if (category.label === 'custom') {
                const customCategory = await vscode.window.showInputBox({
                    prompt: 'Enter custom category name',
                    placeHolder: 'my-category',
                });
                if (!customCategory)
                    return;
                finalCategory = customCategory;
            }
            // Get description
            const description = await vscode.window.showInputBox({
                prompt: 'Enter a description for the operator',
                placeHolder: 'Parses JSON strings into structured data',
            });
            if (description === undefined)
                return;
            // Get icon
            const iconOptions = [
                { label: 'shuffle', description: 'Transform/convert' },
                { label: 'filter', description: 'Filter/select' },
                { label: 'code', description: 'Parse/process' },
                { label: 'check-circle', description: 'Validate/verify' },
                { label: 'layers', description: 'Aggregate/combine' },
                { label: 'file-json', description: 'JSON operations' },
                { label: 'file-text', description: 'Text operations' },
                { label: 'calculator', description: 'Math/compute' },
            ];
            const icon = await vscode.window.showQuickPick(iconOptions, {
                placeHolder: 'Select an icon',
            });
            if (!icon)
                return;
            // Get color
            const colorOptions = [
                { label: '#10b981', description: 'Emerald (Transform)' },
                { label: '#06b6d4', description: 'Cyan (Parse)' },
                { label: '#f59e0b', description: 'Amber (Filter)' },
                { label: '#8b5cf6', description: 'Purple (Validate)' },
                { label: '#3b82f6', description: 'Blue (Format)' },
                { label: '#64748b', description: 'Slate (Utility)' },
                { label: '#ec4899', description: 'Pink (Special)' },
            ];
            const color = await vscode.window.showQuickPick(colorOptions, {
                placeHolder: 'Select a color',
            });
            if (!color)
                return;
            // Generate the operator code
            const options = {
                name,
                className,
                category: finalCategory,
                description: description || '',
                icon: icon.label,
                color: color.label,
            };
            const operatorCode = (0, operatorTemplate_1.getOperatorTemplate)(options);
            // Determine where to save the file
            let targetPath;
            // Check if we're in a workspace
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                const defaultPath = path.join(workspaceFolders[0].uri.fsPath, `${name}.py`);
                const uri = await vscode.window.showSaveDialog({
                    defaultUri: vscode.Uri.file(defaultPath),
                    filters: { 'Python': ['py'] },
                    title: 'Save Operator File',
                });
                if (uri) {
                    targetPath = uri.fsPath;
                }
            }
            if (!targetPath) {
                // Open as untitled document
                const doc = await vscode.workspace.openTextDocument({
                    language: 'python',
                    content: operatorCode,
                });
                await vscode.window.showTextDocument(doc);
                vscode.window.showInformationMessage(`Operator "${name}" created. Save the file to complete.`);
                return;
            }
            // Write the file
            fs.writeFileSync(targetPath, operatorCode);
            // Open the file
            const doc = await vscode.workspace.openTextDocument(targetPath);
            await vscode.window.showTextDocument(doc);
            vscode.window.showInformationMessage(`Operator "${name}" created at ${targetPath}`);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to create operator: ${error}`);
        }
    });
    context.subscriptions.push(command);
}
//# sourceMappingURL=newOperator.js.map