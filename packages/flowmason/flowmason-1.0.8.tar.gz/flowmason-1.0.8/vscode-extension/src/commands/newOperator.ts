/**
 * New Operator Command
 *
 * Creates a new FlowMason operator with interactive prompts.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { getOperatorTemplate } from '../templates/operatorTemplate';

interface OperatorOptions {
    name: string;
    className: string;
    category: string;
    description: string;
    icon: string;
    color: string;
}

export function registerNewOperatorCommand(context: vscode.ExtensionContext): void {
    const command = vscode.commands.registerCommand('flowmason.newOperator', async () => {
        try {
            // Get operator name
            const name = await vscode.window.showInputBox({
                prompt: 'Enter the operator name (kebab-case)',
                placeHolder: 'json-parser',
                validateInput: (value) => {
                    if (!value) return 'Name is required';
                    if (!/^[a-z][a-z0-9-]*$/.test(value)) {
                        return 'Name must be kebab-case (lowercase letters, numbers, hyphens)';
                    }
                    return null;
                },
            });

            if (!name) return;

            // Get class name (derived from operator name by default)
            const defaultClassName = name
                .split('-')
                .map(part => part.charAt(0).toUpperCase() + part.slice(1))
                .join('') + 'Operator';

            const className = await vscode.window.showInputBox({
                prompt: 'Enter the class name',
                value: defaultClassName,
                validateInput: (value) => {
                    if (!value) return 'Class name is required';
                    if (!/^[A-Z][a-zA-Z0-9]*$/.test(value)) {
                        return 'Class name must be PascalCase';
                    }
                    return null;
                },
            });

            if (!className) return;

            // Get category
            const category = await vscode.window.showQuickPick(
                [
                    { label: 'transform', description: 'Data transformation' },
                    { label: 'validation', description: 'Data validation' },
                    { label: 'parsing', description: 'Parsing and extraction' },
                    { label: 'filter', description: 'Filtering and selection' },
                    { label: 'aggregation', description: 'Data aggregation' },
                    { label: 'format', description: 'Format conversion' },
                    { label: 'utility', description: 'Utility functions' },
                    { label: 'custom', description: 'Custom category' },
                ],
                {
                    placeHolder: 'Select a category',
                }
            );

            if (!category) return;

            let finalCategory = category.label;
            if (category.label === 'custom') {
                const customCategory = await vscode.window.showInputBox({
                    prompt: 'Enter custom category name',
                    placeHolder: 'my-category',
                });
                if (!customCategory) return;
                finalCategory = customCategory;
            }

            // Get description
            const description = await vscode.window.showInputBox({
                prompt: 'Enter a description for the operator',
                placeHolder: 'Parses JSON strings into structured data',
            });

            if (description === undefined) return;

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

            if (!icon) return;

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

            if (!color) return;

            // Generate the operator code
            const options: OperatorOptions = {
                name,
                className,
                category: finalCategory,
                description: description || '',
                icon: icon.label,
                color: color.label,
            };

            const operatorCode = getOperatorTemplate(options);

            // Determine where to save the file
            let targetPath: string | undefined;

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
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create operator: ${error}`);
        }
    });

    context.subscriptions.push(command);
}
