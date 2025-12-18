/**
 * New Node Command
 *
 * Creates a new FlowMason node with interactive prompts.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { getNodeTemplate } from '../templates/nodeTemplate';

interface NodeOptions {
    name: string;
    className: string;
    category: string;
    description: string;
    icon: string;
    color: string;
    requiresLlm: boolean;
}

export function registerNewNodeCommand(context: vscode.ExtensionContext): void {
    const command = vscode.commands.registerCommand('flowmason.newNode', async () => {
        try {
            // Get node name
            const name = await vscode.window.showInputBox({
                prompt: 'Enter the node name (kebab-case)',
                placeHolder: 'sentiment-analyzer',
                validateInput: (value) => {
                    if (!value) return 'Name is required';
                    if (!/^[a-z][a-z0-9-]*$/.test(value)) {
                        return 'Name must be kebab-case (lowercase letters, numbers, hyphens)';
                    }
                    return null;
                },
            });

            if (!name) return;

            // Get class name (derived from node name by default)
            const defaultClassName = name
                .split('-')
                .map(part => part.charAt(0).toUpperCase() + part.slice(1))
                .join('') + 'Node';

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
                    { label: 'ai', description: 'AI/LLM nodes' },
                    { label: 'transform', description: 'Data transformation' },
                    { label: 'analysis', description: 'Analysis and processing' },
                    { label: 'integration', description: 'External integrations' },
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
                prompt: 'Enter a description for the node',
                placeHolder: 'Analyzes text sentiment using AI',
            });

            if (description === undefined) return;

            // Get icon
            const iconOptions = [
                { label: 'brain', description: 'AI/ML operations' },
                { label: 'sparkles', description: 'Generation/creative' },
                { label: 'message-square', description: 'Text/chat' },
                { label: 'search', description: 'Analysis/search' },
                { label: 'zap', description: 'Fast/utility' },
                { label: 'database', description: 'Data operations' },
                { label: 'globe', description: 'Web/API' },
                { label: 'file-text', description: 'Document processing' },
            ];

            const icon = await vscode.window.showQuickPick(iconOptions, {
                placeHolder: 'Select an icon',
            });

            if (!icon) return;

            // Get color
            const colorOptions = [
                { label: '#6366f1', description: 'Indigo (AI)' },
                { label: '#8b5cf6', description: 'Purple (Creative)' },
                { label: '#06b6d4', description: 'Cyan (Analysis)' },
                { label: '#10b981', description: 'Emerald (Success)' },
                { label: '#f59e0b', description: 'Amber (Warning)' },
                { label: '#ef4444', description: 'Red (Critical)' },
                { label: '#64748b', description: 'Slate (Utility)' },
            ];

            const color = await vscode.window.showQuickPick(colorOptions, {
                placeHolder: 'Select a color',
            });

            if (!color) return;

            // Ask if node requires LLM
            const requiresLlm = await vscode.window.showQuickPick(
                [
                    { label: 'Yes', description: 'Node uses LLM for processing', value: true },
                    { label: 'No', description: 'Node does not use LLM', value: false },
                ],
                {
                    placeHolder: 'Does this node require an LLM?',
                }
            );

            if (!requiresLlm) return;

            // Generate the node code
            const options: NodeOptions = {
                name,
                className,
                category: finalCategory,
                description: description || '',
                icon: icon.label,
                color: color.label,
                requiresLlm: requiresLlm.value,
            };

            const nodeCode = getNodeTemplate(options);

            // Determine where to save the file
            let targetPath: string | undefined;

            // Check if we're in a workspace
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                const defaultPath = path.join(workspaceFolders[0].uri.fsPath, `${name}.py`);

                const uri = await vscode.window.showSaveDialog({
                    defaultUri: vscode.Uri.file(defaultPath),
                    filters: { 'Python': ['py'] },
                    title: 'Save Node File',
                });

                if (uri) {
                    targetPath = uri.fsPath;
                }
            }

            if (!targetPath) {
                // Open as untitled document
                const doc = await vscode.workspace.openTextDocument({
                    language: 'python',
                    content: nodeCode,
                });
                await vscode.window.showTextDocument(doc);
                vscode.window.showInformationMessage(`Node "${name}" created. Save the file to complete.`);
                return;
            }

            // Write the file
            fs.writeFileSync(targetPath, nodeCode);

            // Open the file
            const doc = await vscode.workspace.openTextDocument(targetPath);
            await vscode.window.showTextDocument(doc);

            vscode.window.showInformationMessage(`Node "${name}" created at ${targetPath}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create node: ${error}`);
        }
    });

    context.subscriptions.push(command);
}
