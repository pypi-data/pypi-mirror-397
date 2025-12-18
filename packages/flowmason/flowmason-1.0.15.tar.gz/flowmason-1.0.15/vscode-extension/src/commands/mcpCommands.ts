/**
 * MCP Commands
 *
 * VSCode commands for AI-assisted pipeline creation via MCP (Model Context Protocol).
 */

import * as vscode from 'vscode';
import { MCPService, GeneratedStage, PipelineSuggestion } from '../services/mcpService';

interface StageQuickPickItem extends vscode.QuickPickItem {
    stage: {
        component: string;
        purpose: string;
        rationale: string;
    };
    index: number;
}

export function registerMCPCommands(
    context: vscode.ExtensionContext,
    mcpService: MCPService,
    outputChannel: vscode.OutputChannel
): void {
    // Command: Create Pipeline with AI Assistance
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.mcp.createPipeline', async () => {
            await createPipelineWithAI(mcpService, outputChannel);
        })
    );

    // Command: Get Pipeline Suggestions
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.mcp.suggestPipeline', async () => {
            await suggestPipeline(mcpService, outputChannel);
        })
    );

    // Command: Generate Stage
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.mcp.generateStage', async () => {
            await generateStage(mcpService, outputChannel);
        })
    );

    // Command: Validate Current Pipeline
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.mcp.validatePipeline', async () => {
            await validateCurrentPipeline(mcpService, outputChannel);
        })
    );

    // Command: Add AI-Generated Stage to Current Pipeline
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.mcp.addGeneratedStage', async () => {
            await addGeneratedStageToPipeline(mcpService, outputChannel);
        })
    );

    outputChannel.appendLine('MCP commands registered');
}

/**
 * Create a pipeline with AI assistance
 */
async function createPipelineWithAI(
    mcpService: MCPService,
    outputChannel: vscode.OutputChannel
): Promise<void> {
    // Step 1: Get task description
    const taskDescription = await vscode.window.showInputBox({
        prompt: 'Describe what you want your pipeline to do',
        placeHolder: 'e.g., Summarize articles and filter by sentiment',
        title: 'Create Pipeline with AI - Step 1/4',
        validateInput: (value) => {
            if (!value || value.trim().length < 10) {
                return 'Please provide a more detailed description (at least 10 characters)';
            }
            return null;
        }
    });

    if (!taskDescription) {
        return;
    }

    // Step 2: Get suggestions
    const suggestionProgress = await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Analyzing task...',
            cancellable: false
        },
        async () => {
            return mcpService.suggestPipeline(taskDescription);
        }
    );

    if (!suggestionProgress) {
        return;
    }

    outputChannel.appendLine(`Pipeline suggestion received: ${suggestionProgress.stages.length} stages`);

    // Step 3: Review and modify stages
    const stages = await reviewSuggestion(suggestionProgress, mcpService, outputChannel);
    if (!stages || stages.length === 0) {
        return;
    }

    // Step 4: Get pipeline name
    const pipelineName = await vscode.window.showInputBox({
        prompt: 'Enter pipeline name',
        title: 'Create Pipeline with AI - Step 4/4',
        value: suggestionProgress.name || 'my-pipeline',
        validateInput: (value) => {
            if (!value || value.trim().length === 0) {
                return 'Pipeline name is required';
            }
            if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(value)) {
                return 'Name must start with a letter and contain only letters, numbers, hyphens, or underscores';
            }
            return null;
        }
    });

    if (!pipelineName) {
        return;
    }

    // Create the pipeline
    const filePath = await mcpService.createPipeline(
        pipelineName,
        taskDescription,
        stages as GeneratedStage[]
    );

    if (filePath) {
        outputChannel.appendLine(`Created pipeline: ${filePath}`);
        vscode.window.showInformationMessage(`Pipeline created: ${pipelineName}`);
    }
}

/**
 * Review and modify suggested stages
 */
async function reviewSuggestion(
    suggestion: PipelineSuggestion,
    mcpService: MCPService,
    outputChannel: vscode.OutputChannel
): Promise<GeneratedStage[] | null> {
    const stages: GeneratedStage[] = [];

    // Show stages for review
    const stageItems: StageQuickPickItem[] = suggestion.stages.map((s, i) => ({
        label: `${i + 1}. ${s.component}`,
        description: s.purpose,
        detail: s.rationale,
        stage: s,
        index: i,
        picked: true
    }));

    const selectedStages = await vscode.window.showQuickPick(stageItems, {
        title: 'Review Suggested Stages - Step 2/4',
        placeHolder: 'Select stages to include (multi-select)',
        canPickMany: true
    });

    if (!selectedStages || selectedStages.length === 0) {
        return null;
    }

    // Generate full stage configs for each selected stage
    let previousStageId = '';

    for (const item of selectedStages) {
        const inputSource = previousStageId
            ? `stages.${previousStageId}.output`
            : 'input';

        const generated = await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: `Generating ${item.stage.component} stage...`,
                cancellable: false
            },
            async () => {
                return mcpService.generateStage(
                    item.stage.component,
                    item.stage.purpose,
                    inputSource
                );
            }
        );

        if (generated) {
            stages.push(generated);
            previousStageId = generated.id;
            outputChannel.appendLine(`Generated stage: ${generated.id}`);
        }
    }

    // Step 3: Review generated stages
    const reviewChoice = await vscode.window.showQuickPick(
        [
            {
                label: '$(check) Accept All',
                description: 'Use all generated stages as-is',
                action: 'accept'
            },
            {
                label: '$(edit) Customize',
                description: 'Edit stage configurations in editor',
                action: 'customize'
            },
            {
                label: '$(close) Cancel',
                description: 'Cancel pipeline creation',
                action: 'cancel'
            }
        ],
        {
            title: 'Review Generated Stages - Step 3/4',
            placeHolder: `${stages.length} stages generated`
        }
    );

    if (!reviewChoice || reviewChoice.action === 'cancel') {
        return null;
    }

    if (reviewChoice.action === 'customize') {
        // Open stages in editor for customization
        const stagesJson = JSON.stringify(stages, null, 2);
        const document = await vscode.workspace.openTextDocument({
            content: stagesJson,
            language: 'json'
        });
        await vscode.window.showTextDocument(document);

        const proceed = await vscode.window.showInformationMessage(
            'Edit the stages in the editor, then click "Continue" when done.',
            'Continue',
            'Cancel'
        );

        if (proceed === 'Continue') {
            // Re-parse the edited content
            try {
                const editedContent = document.getText();
                return JSON.parse(editedContent);
            } catch (e) {
                vscode.window.showErrorMessage('Invalid JSON in edited stages');
                return null;
            }
        }
        return null;
    }

    return stages;
}

/**
 * Get pipeline suggestions for a task
 */
async function suggestPipeline(
    mcpService: MCPService,
    outputChannel: vscode.OutputChannel
): Promise<void> {
    const taskDescription = await vscode.window.showInputBox({
        prompt: 'What do you want your pipeline to accomplish?',
        placeHolder: 'e.g., Process customer feedback and generate reports',
        title: 'Get Pipeline Suggestions'
    });

    if (!taskDescription) {
        return;
    }

    const suggestion = await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Getting pipeline suggestions...',
            cancellable: false
        },
        async () => {
            return mcpService.suggestPipeline(taskDescription);
        }
    );

    if (!suggestion) {
        return;
    }

    // Show suggestions in output panel
    outputChannel.show();
    outputChannel.appendLine('');
    outputChannel.appendLine('='.repeat(60));
    outputChannel.appendLine(`Pipeline Suggestions for: ${taskDescription}`);
    outputChannel.appendLine('='.repeat(60));
    outputChannel.appendLine('');

    suggestion.stages.forEach((stage, i) => {
        outputChannel.appendLine(`${i + 1}. ${stage.component}`);
        outputChannel.appendLine(`   Purpose: ${stage.purpose}`);
        outputChannel.appendLine(`   Rationale: ${stage.rationale}`);
        outputChannel.appendLine('');
    });

    if (suggestion.examplePipeline) {
        outputChannel.appendLine('Example Pipeline:');
        outputChannel.appendLine(JSON.stringify(suggestion.examplePipeline, null, 2));
    }

    // Offer to create the pipeline
    const action = await vscode.window.showInformationMessage(
        `Suggested ${suggestion.stages.length} stages for your pipeline.`,
        'Create Pipeline',
        'View Details',
        'Dismiss'
    );

    if (action === 'Create Pipeline') {
        // Generate stages and create pipeline
        const stages: GeneratedStage[] = [];
        let previousStageId = '';

        for (const stage of suggestion.stages) {
            const inputSource = previousStageId
                ? `stages.${previousStageId}.output`
                : 'input';

            const generated = await mcpService.generateStage(
                stage.component,
                stage.purpose,
                inputSource
            );

            if (generated) {
                stages.push(generated);
                previousStageId = generated.id;
            }
        }

        const pipelineName = await vscode.window.showInputBox({
            prompt: 'Enter pipeline name',
            value: 'my-pipeline'
        });

        if (pipelineName && stages.length > 0) {
            await mcpService.createPipeline(pipelineName, taskDescription, stages);
        }
    } else if (action === 'View Details') {
        outputChannel.show();
    }
}

/**
 * Generate a single stage
 */
async function generateStage(
    mcpService: MCPService,
    outputChannel: vscode.OutputChannel
): Promise<void> {
    // Select component type
    const componentTypes = [
        { label: '$(sparkle) generator', description: 'AI-powered content generation' },
        { label: '$(filter) filter', description: 'Filter items based on criteria' },
        { label: '$(json) json_transform', description: 'Transform data structure' },
        { label: '$(globe) http_request', description: 'Make HTTP API calls' },
        { label: '$(sync) loop', description: 'Iterate over items' },
        { label: '$(comment) critic', description: 'AI-powered content evaluation' },
        { label: '$(list-selection) selector', description: 'Select from multiple options' },
        { label: '$(combine) synthesizer', description: 'Combine multiple inputs' }
    ];

    const selectedType = await vscode.window.showQuickPick(componentTypes, {
        title: 'Generate Stage - Step 1/3',
        placeHolder: 'Select component type'
    });

    if (!selectedType) {
        return;
    }

    const componentType = selectedType.label.split(' ')[1]; // Remove icon

    // Get purpose
    const purpose = await vscode.window.showInputBox({
        prompt: 'What should this stage do?',
        placeHolder: 'e.g., summarize the article content',
        title: 'Generate Stage - Step 2/3'
    });

    if (!purpose) {
        return;
    }

    // Get input source
    const inputSource = await vscode.window.showInputBox({
        prompt: 'Input source (use "input" for pipeline input or "stages.<stage_id>.output")',
        value: 'input',
        title: 'Generate Stage - Step 3/3'
    });

    if (!inputSource) {
        return;
    }

    // Generate the stage
    const stage = await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Generating stage configuration...',
            cancellable: false
        },
        async () => {
            return mcpService.generateStage(componentType, purpose, inputSource);
        }
    );

    if (!stage) {
        return;
    }

    // Show the generated stage
    const stageJson = JSON.stringify(stage, null, 2);
    const document = await vscode.workspace.openTextDocument({
        content: stageJson,
        language: 'json'
    });
    await vscode.window.showTextDocument(document);

    outputChannel.appendLine(`Generated stage: ${stage.id}`);
    vscode.window.showInformationMessage(
        `Generated ${componentType} stage: ${stage.id}`,
        'Copy to Clipboard'
    ).then(action => {
        if (action === 'Copy to Clipboard') {
            vscode.env.clipboard.writeText(stageJson);
        }
    });
}

/**
 * Validate the current pipeline
 */
async function validateCurrentPipeline(
    mcpService: MCPService,
    outputChannel: vscode.OutputChannel
): Promise<void> {
    const editor = vscode.window.activeTextEditor;

    if (!editor || !editor.document.fileName.endsWith('.pipeline.json')) {
        vscode.window.showWarningMessage('Open a .pipeline.json file to validate');
        return;
    }

    const pipelineJson = editor.document.getText();

    const result = await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Validating pipeline...',
            cancellable: false
        },
        async () => {
            return mcpService.validatePipeline(pipelineJson);
        }
    );

    outputChannel.show();
    outputChannel.appendLine('');
    outputChannel.appendLine('='.repeat(60));
    outputChannel.appendLine(`Validation Result: ${editor.document.fileName}`);
    outputChannel.appendLine('='.repeat(60));

    if (result.valid) {
        outputChannel.appendLine('✓ Pipeline is valid');
        vscode.window.showInformationMessage('Pipeline validation passed');
    } else {
        outputChannel.appendLine('✗ Pipeline has errors:');
        result.errors.forEach(e => outputChannel.appendLine(`  - ${e}`));
        vscode.window.showErrorMessage(`Pipeline validation failed: ${result.errors.length} error(s)`);
    }

    if (result.warnings.length > 0) {
        outputChannel.appendLine('\nWarnings:');
        result.warnings.forEach(w => outputChannel.appendLine(`  - ${w}`));
    }
}

/**
 * Add an AI-generated stage to the current pipeline
 */
async function addGeneratedStageToPipeline(
    mcpService: MCPService,
    outputChannel: vscode.OutputChannel
): Promise<void> {
    const editor = vscode.window.activeTextEditor;

    if (!editor || !editor.document.fileName.endsWith('.pipeline.json')) {
        vscode.window.showWarningMessage('Open a .pipeline.json file to add a stage');
        return;
    }

    // Parse current pipeline
    let pipeline: { stages?: Array<{ id: string }> };
    try {
        pipeline = JSON.parse(editor.document.getText());
    } catch {
        vscode.window.showErrorMessage('Invalid pipeline JSON');
        return;
    }

    // Get existing stage IDs for input source options
    const existingStages = pipeline.stages || [];
    const inputOptions = [
        { label: 'input', description: 'Pipeline input' },
        ...existingStages.map(s => ({
            label: `stages.${s.id}.output`,
            description: `Output of stage: ${s.id}`
        }))
    ];

    // Select component type
    const componentTypes = [
        { label: '$(sparkle) generator', description: 'AI-powered content generation' },
        { label: '$(filter) filter', description: 'Filter items based on criteria' },
        { label: '$(json) json_transform', description: 'Transform data structure' },
        { label: '$(globe) http_request', description: 'Make HTTP API calls' },
        { label: '$(sync) loop', description: 'Iterate over items' },
        { label: '$(comment) critic', description: 'AI-powered content evaluation' }
    ];

    const selectedType = await vscode.window.showQuickPick(componentTypes, {
        title: 'Add AI-Generated Stage - Step 1/3',
        placeHolder: 'Select component type'
    });

    if (!selectedType) {
        return;
    }

    const componentType = selectedType.label.split(' ')[1];

    // Get purpose
    const purpose = await vscode.window.showInputBox({
        prompt: 'What should this stage do?',
        placeHolder: 'e.g., filter out invalid entries',
        title: 'Add AI-Generated Stage - Step 2/3'
    });

    if (!purpose) {
        return;
    }

    // Select input source
    const selectedInput = await vscode.window.showQuickPick(inputOptions, {
        title: 'Add AI-Generated Stage - Step 3/3',
        placeHolder: 'Select input source'
    });

    if (!selectedInput) {
        return;
    }

    // Generate the stage
    const stage = await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Generating stage...',
            cancellable: false
        },
        async () => {
            return mcpService.generateStage(componentType, purpose, selectedInput.label);
        }
    );

    if (!stage) {
        return;
    }

    // Add stage to pipeline
    const updatedPipeline = {
        ...pipeline,
        stages: [...existingStages, stage]
    };

    // Update document
    const edit = new vscode.WorkspaceEdit();
    const fullRange = new vscode.Range(
        editor.document.positionAt(0),
        editor.document.positionAt(editor.document.getText().length)
    );
    edit.replace(editor.document.uri, fullRange, JSON.stringify(updatedPipeline, null, 2));
    await vscode.workspace.applyEdit(edit);

    // Format
    await vscode.commands.executeCommand('editor.action.formatDocument');

    outputChannel.appendLine(`Added stage: ${stage.id}`);
    vscode.window.showInformationMessage(`Added ${componentType} stage: ${stage.id}`);
}
