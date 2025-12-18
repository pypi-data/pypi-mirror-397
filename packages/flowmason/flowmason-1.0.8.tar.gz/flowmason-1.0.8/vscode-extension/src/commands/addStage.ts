/**
 * Add Stage Command
 *
 * Uses native VSCode QuickPick to add stages to .pipeline.json files.
 * Provides a Cmd+Shift+P style experience for component selection.
 */

import * as vscode from 'vscode';
import { FlowMasonService, Component } from '../services/flowmasonService';
import { PipelineFile, PipelineStage } from '../views/pipelineStagesTree';
import { DagCanvasProvider } from '../editors/dagCanvasProvider';

/**
 * Get the current pipeline document, whether from active text editor or DAG canvas
 */
function getCurrentPipelineDocument(): vscode.TextDocument | undefined {
    // First check active text editor
    const editor = vscode.window.activeTextEditor;
    if (editor && editor.document.fileName.endsWith('.pipeline.json')) {
        return editor.document;
    }

    // Fallback to DAG canvas current document
    const dagDocument = DagCanvasProvider.currentDocument;
    if (dagDocument && dagDocument.fileName.endsWith('.pipeline.json')) {
        return dagDocument;
    }

    return undefined;
}

interface ComponentQuickPickItem extends vscode.QuickPickItem {
    component: Component;
}

interface StageQuickPickItem extends vscode.QuickPickItem {
    stageId: string;
}

export function registerAddStageCommand(
    context: vscode.ExtensionContext,
    flowmasonService: FlowMasonService
): void {
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.addStage', async () => {
            await addStageFlow(flowmasonService);
        })
    );

    // Also register a command to add stage at a specific position
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.addStageAfter', async (afterStageId: string) => {
            await addStageFlow(flowmasonService, afterStageId);
        })
    );
}

async function addStageFlow(
    flowmasonService: FlowMasonService,
    afterStageId?: string
): Promise<void> {
    // Get current pipeline document (from text editor or DAG canvas)
    const document = getCurrentPipelineDocument();
    if (!document) {
        vscode.window.showWarningMessage('Open a .pipeline.json file to add stages');
        return;
    }

    // Parse current pipeline
    let pipeline: PipelineFile;
    try {
        pipeline = JSON.parse(document.getText());
    } catch {
        vscode.window.showErrorMessage('Invalid pipeline JSON. Fix syntax errors first.');
        return;
    }

    // Step 1: Select component type category
    const categoryChoice = await vscode.window.showQuickPick(
        [
            {
                label: '$(sparkle) AI Nodes',
                description: 'LLM-powered components',
                detail: 'Generator, Critic, Improver, Selector, Synthesizer',
                category: 'node'
            },
            {
                label: '$(symbol-function) Operators',
                description: 'Utility and transformation components',
                detail: 'HTTP, JSON Transform, Filter, Validate, Variables',
                category: 'operator'
            },
            {
                label: '$(git-branch) Control Flow',
                description: 'Flow control components',
                detail: 'Conditional, ForEach, TryCatch, Router, SubPipeline',
                category: 'control_flow'
            }
        ],
        {
            placeHolder: 'Select component category',
            title: 'Add Stage - Step 1/3'
        }
    );

    if (!categoryChoice) {
        return; // User cancelled
    }

    // Step 2: Select specific component
    const components = await flowmasonService.getComponents();
    const filteredComponents = components.filter(c => {
        if (categoryChoice.category === 'node') {
            return c.requires_llm;
        } else if (categoryChoice.category === 'control_flow') {
            return c.type === 'control_flow';
        } else {
            return !c.requires_llm && c.type !== 'control_flow';
        }
    });

    if (filteredComponents.length === 0) {
        // Fallback: show all components if filtering returned none
        const allComponentItems = components.map(c => createComponentQuickPickItem(c));

        const componentChoice = await vscode.window.showQuickPick(allComponentItems, {
            placeHolder: 'Select component',
            title: 'Add Stage - Step 2/3',
            matchOnDescription: true,
            matchOnDetail: true
        });

        if (!componentChoice) {
            return;
        }

        await completeAddStage(document, pipeline, componentChoice.component, afterStageId);
        return;
    }

    const componentItems: ComponentQuickPickItem[] = filteredComponents.map(c =>
        createComponentQuickPickItem(c)
    );

    const componentChoice = await vscode.window.showQuickPick(componentItems, {
        placeHolder: 'Select component',
        title: 'Add Stage - Step 2/3',
        matchOnDescription: true,
        matchOnDetail: true
    });

    if (!componentChoice) {
        return;
    }

    await completeAddStage(document, pipeline, componentChoice.component, afterStageId);
}

function createComponentQuickPickItem(component: Component): ComponentQuickPickItem {
    let icon = '$(symbol-method)';
    if (component.requires_llm) {
        icon = '$(sparkle)';
    } else if (component.type === 'control_flow') {
        icon = '$(git-branch)';
    } else {
        icon = '$(symbol-function)';
    }

    return {
        label: `${icon} ${component.name}`,
        description: component.category,
        detail: component.description,
        component
    };
}

async function completeAddStage(
    document: vscode.TextDocument,
    pipeline: PipelineFile,
    component: Component,
    afterStageId?: string
): Promise<void> {
    // Step 3: Enter stage ID
    const existingIds = new Set(pipeline.stages?.map(s => s.id) || []);

    // Generate a suggested ID based on component name
    let suggestedId = component.name.replace(/-/g, '_');
    let counter = 1;
    while (existingIds.has(suggestedId)) {
        suggestedId = `${component.name.replace(/-/g, '_')}_${counter}`;
        counter++;
    }

    const stageId = await vscode.window.showInputBox({
        prompt: 'Enter stage ID',
        title: 'Add Stage - Step 3/3',
        value: suggestedId,
        validateInput: (value) => {
            if (!value || value.trim().length === 0) {
                return 'Stage ID is required';
            }
            if (existingIds.has(value)) {
                return `Stage ID "${value}" already exists`;
            }
            if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(value)) {
                return 'ID must start with a letter and contain only letters, numbers, hyphens, or underscores';
            }
            return null;
        }
    });

    if (!stageId) {
        return;
    }

    // Step 4: Select dependencies (optional)
    let dependsOn: string[] = [];

    if (pipeline.stages && pipeline.stages.length > 0) {
        const dependencyItems: StageQuickPickItem[] = pipeline.stages.map(s => ({
            label: s.id,
            description: s.component_type,
            stageId: s.id,
            picked: afterStageId === s.id // Pre-select if adding after specific stage
        }));

        const selectedDeps = await vscode.window.showQuickPick(dependencyItems, {
            placeHolder: 'Select dependencies (optional)',
            title: 'Add Stage - Dependencies',
            canPickMany: true
        });

        if (selectedDeps) {
            dependsOn = selectedDeps.map(d => d.stageId);
        }
    }

    // Build the new stage
    const newStage: PipelineStage = {
        id: stageId,
        component_type: component.name,
        config: generateDefaultConfig(component)
    };

    if (dependsOn.length > 0) {
        newStage.depends_on = dependsOn;
    }

    // Insert the stage into the pipeline
    await insertStageIntoPipeline(document, pipeline, newStage, afterStageId);

    vscode.window.showInformationMessage(`Added stage "${stageId}" using ${component.name}`);
}

/**
 * Generate default config based on component's input schema
 */
function generateDefaultConfig(component: Component): Record<string, unknown> {
    const config: Record<string, unknown> = {};

    if (component.input_schema) {
        const schema = component.input_schema as {
            properties?: Record<string, { default?: unknown; type?: string }>;
            required?: string[];
        };

        if (schema.properties) {
            for (const [key, prop] of Object.entries(schema.properties)) {
                // Add default values or placeholders for required fields
                if (prop.default !== undefined) {
                    config[key] = prop.default;
                } else if (schema.required?.includes(key)) {
                    // Add placeholder based on type
                    if (prop.type === 'string') {
                        config[key] = '';
                    } else if (prop.type === 'number' || prop.type === 'integer') {
                        config[key] = 0;
                    } else if (prop.type === 'boolean') {
                        config[key] = false;
                    } else if (prop.type === 'array') {
                        config[key] = [];
                    } else if (prop.type === 'object') {
                        config[key] = {};
                    }
                }
            }
        }
    }

    return config;
}

/**
 * Insert a new stage into the pipeline document
 */
async function insertStageIntoPipeline(
    document: vscode.TextDocument,
    pipeline: PipelineFile,
    newStage: PipelineStage,
    afterStageId?: string
): Promise<void> {
    const text = document.getText();

    // Find where to insert
    let insertIndex: number;
    let insertPosition: vscode.Position;

    if (afterStageId && pipeline.stages) {
        // Insert after specific stage
        const afterIndex = pipeline.stages.findIndex(s => s.id === afterStageId);
        if (afterIndex >= 0) {
            // Find the end of the afterStage in the document
            const stageEndPos = findStageEndPosition(document, afterStageId);
            if (stageEndPos) {
                insertPosition = stageEndPos;
            } else {
                // Fallback: insert at end of stages array
                insertPosition = findStagesArrayEndPosition(document) || new vscode.Position(0, 0);
            }
        } else {
            insertPosition = findStagesArrayEndPosition(document) || new vscode.Position(0, 0);
        }
    } else {
        // Insert at end of stages array
        insertPosition = findStagesArrayEndPosition(document) || new vscode.Position(0, 0);
    }

    // Format the new stage JSON
    const stageJson = JSON.stringify(newStage, null, 2);
    const indentedStageJson = stageJson
        .split('\n')
        .map((line, i) => i === 0 ? line : '    ' + line)
        .join('\n');

    // Determine if we need a comma before
    const textBeforeInsert = document.getText(new vscode.Range(new vscode.Position(0, 0), insertPosition));
    const needsCommaBefore = /\}\s*$/.test(textBeforeInsert.trim());

    const insertText = needsCommaBefore
        ? `,\n    ${indentedStageJson}`
        : `\n    ${indentedStageJson}`;

    // Apply the edit
    const edit = new vscode.WorkspaceEdit();
    edit.insert(document.uri, insertPosition, insertText);
    await vscode.workspace.applyEdit(edit);

    // Format the document
    await vscode.commands.executeCommand('editor.action.formatDocument');

    // Move cursor to the new stage
    const editor = vscode.window.activeTextEditor;
    if (editor) {
        const newText = editor.document.getText();
        const stageIdPattern = `"id"\\s*:\\s*"${newStage.id}"`;
        const match = new RegExp(stageIdPattern).exec(newText);
        if (match) {
            const pos = editor.document.positionAt(match.index);
            editor.selection = new vscode.Selection(pos, pos);
            editor.revealRange(new vscode.Range(pos, pos), vscode.TextEditorRevealType.InCenter);
        }
    }
}

/**
 * Find the end position of a specific stage in the document
 */
function findStageEndPosition(document: vscode.TextDocument, stageId: string): vscode.Position | null {
    const text = document.getText();
    const idPattern = `"id"\\s*:\\s*"${stageId}"`;
    const idMatch = new RegExp(idPattern).exec(text);

    if (!idMatch) {
        return null;
    }

    // Find the closing brace of this stage
    let braceCount = 0;
    let startIndex = idMatch.index;

    // Find opening brace
    for (let i = idMatch.index; i >= 0; i--) {
        if (text[i] === '}') {
            braceCount++;
        } else if (text[i] === '{') {
            if (braceCount === 0) {
                startIndex = i;
                break;
            }
            braceCount--;
        }
    }

    // Find closing brace
    braceCount = 1;
    for (let i = startIndex + 1; i < text.length; i++) {
        if (text[i] === '{') {
            braceCount++;
        } else if (text[i] === '}') {
            braceCount--;
            if (braceCount === 0) {
                return document.positionAt(i + 1);
            }
        }
    }

    return null;
}

/**
 * Find the position just before the closing bracket of the stages array
 */
function findStagesArrayEndPosition(document: vscode.TextDocument): vscode.Position | null {
    const text = document.getText();

    // Find "stages": [
    const stagesMatch = /"stages"\s*:\s*\[/.exec(text);
    if (!stagesMatch) {
        return null;
    }

    // Find the matching closing bracket
    const startIndex = stagesMatch.index + stagesMatch[0].length - 1;
    let bracketCount = 1;

    for (let i = startIndex + 1; i < text.length; i++) {
        if (text[i] === '[') {
            bracketCount++;
        } else if (text[i] === ']') {
            bracketCount--;
            if (bracketCount === 0) {
                // Return position just before the closing bracket
                // Find the last non-whitespace before the bracket
                let insertPos = i;
                for (let j = i - 1; j > startIndex; j--) {
                    if (text[j] !== ' ' && text[j] !== '\n' && text[j] !== '\t' && text[j] !== '\r') {
                        insertPos = j + 1;
                        break;
                    }
                }
                return document.positionAt(insertPos);
            }
        }
    }

    return null;
}
