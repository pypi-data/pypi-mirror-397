/**
 * Pipeline Diagnostics Provider
 *
 * Validates .pipeline.json files and shows errors/warnings in the
 * native VSCode Problems panel.
 */

import * as vscode from 'vscode';
import { FlowMasonService } from '../services/flowmasonService';
import { PipelineFile, PipelineStage } from '../views/pipelineStagesTree';

export class PipelineDiagnosticsProvider implements vscode.Disposable {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private disposables: vscode.Disposable[] = [];
    private knownComponents: Set<string> = new Set();

    constructor(private flowmasonService: FlowMasonService) {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('flowmason-pipeline');

        // Watch for document changes
        this.disposables.push(
            vscode.workspace.onDidChangeTextDocument(event => {
                if (event.document.fileName.endsWith('.pipeline.json')) {
                    this.validateDocument(event.document);
                }
            })
        );

        // Watch for document opens
        this.disposables.push(
            vscode.workspace.onDidOpenTextDocument(document => {
                if (document.fileName.endsWith('.pipeline.json')) {
                    this.validateDocument(document);
                }
            })
        );

        // Watch for document closes
        this.disposables.push(
            vscode.workspace.onDidCloseTextDocument(document => {
                if (document.fileName.endsWith('.pipeline.json')) {
                    this.diagnosticCollection.delete(document.uri);
                }
            })
        );

        // Validate all open pipeline documents
        for (const document of vscode.workspace.textDocuments) {
            if (document.fileName.endsWith('.pipeline.json')) {
                this.validateDocument(document);
            }
        }

        // Load known components from API
        this.loadKnownComponents();
    }

    private async loadKnownComponents(): Promise<void> {
        try {
            const components = await this.flowmasonService.getComponents();
            this.knownComponents = new Set(components.map(c => c.name));

            // Re-validate all open documents now that we have component list
            for (const document of vscode.workspace.textDocuments) {
                if (document.fileName.endsWith('.pipeline.json')) {
                    this.validateDocument(document);
                }
            }
        } catch {
            // Studio may not be running - that's okay
        }
    }

    /**
     * Refresh known components (e.g., after Studio starts)
     */
    refresh(): void {
        this.loadKnownComponents();
    }

    async validateDocument(document: vscode.TextDocument): Promise<void> {
        const diagnostics: vscode.Diagnostic[] = [];

        // Try to parse JSON
        let pipeline: PipelineFile;
        try {
            pipeline = JSON.parse(document.getText());
        } catch (error) {
            // JSON syntax error
            const syntaxError = error as SyntaxError;
            const position = this.extractErrorPosition(syntaxError.message, document);
            diagnostics.push(new vscode.Diagnostic(
                new vscode.Range(position, position.translate(0, 1)),
                `Invalid JSON: ${syntaxError.message}`,
                vscode.DiagnosticSeverity.Error
            ));
            this.diagnosticCollection.set(document.uri, diagnostics);
            return;
        }

        // Validate pipeline structure
        this.validatePipelineStructure(document, pipeline, diagnostics);

        // Validate stages
        if (pipeline.stages && Array.isArray(pipeline.stages)) {
            const stageIds = new Set<string>();

            for (const stage of pipeline.stages) {
                this.validateStage(document, stage, stageIds, pipeline.stages, diagnostics);
            }
        }

        this.diagnosticCollection.set(document.uri, diagnostics);
    }

    private validatePipelineStructure(
        document: vscode.TextDocument,
        pipeline: PipelineFile,
        diagnostics: vscode.Diagnostic[]
    ): void {
        // Required: name
        if (!pipeline.name) {
            const range = this.findPropertyRange(document, 'name') ||
                          new vscode.Range(0, 0, 0, 1);
            diagnostics.push(new vscode.Diagnostic(
                range,
                'Pipeline must have a "name" property',
                vscode.DiagnosticSeverity.Error
            ));
        }

        // Required: stages array
        if (!pipeline.stages) {
            diagnostics.push(new vscode.Diagnostic(
                new vscode.Range(0, 0, 0, 1),
                'Pipeline must have a "stages" array',
                vscode.DiagnosticSeverity.Error
            ));
        } else if (!Array.isArray(pipeline.stages)) {
            const range = this.findPropertyRange(document, 'stages') ||
                          new vscode.Range(0, 0, 0, 1);
            diagnostics.push(new vscode.Diagnostic(
                range,
                '"stages" must be an array',
                vscode.DiagnosticSeverity.Error
            ));
        } else if (pipeline.stages.length === 0) {
            const range = this.findPropertyRange(document, 'stages') ||
                          new vscode.Range(0, 0, 0, 1);
            diagnostics.push(new vscode.Diagnostic(
                range,
                'Pipeline has no stages defined',
                vscode.DiagnosticSeverity.Warning
            ));
        }
    }

    private validateStage(
        document: vscode.TextDocument,
        stage: PipelineStage,
        stageIds: Set<string>,
        allStages: PipelineStage[],
        diagnostics: vscode.Diagnostic[]
    ): void {
        const stageRange = this.findStageRange(document, stage.id);
        const defaultRange = stageRange || new vscode.Range(0, 0, 0, 1);

        // Required: id
        if (!stage.id) {
            diagnostics.push(new vscode.Diagnostic(
                defaultRange,
                'Stage must have an "id" property',
                vscode.DiagnosticSeverity.Error
            ));
            return;
        }

        // Check for duplicate IDs
        if (stageIds.has(stage.id)) {
            const idRange = this.findStagePropertyRange(document, stage.id, 'id') || defaultRange;
            diagnostics.push(new vscode.Diagnostic(
                idRange,
                `Duplicate stage ID: "${stage.id}"`,
                vscode.DiagnosticSeverity.Error
            ));
        }
        stageIds.add(stage.id);

        // Required: component_type
        if (!stage.component_type) {
            diagnostics.push(new vscode.Diagnostic(
                defaultRange,
                `Stage "${stage.id}" must have a "component_type" property`,
                vscode.DiagnosticSeverity.Error
            ));
        } else if (this.knownComponents.size > 0 && !this.knownComponents.has(stage.component_type)) {
            const typeRange = this.findStagePropertyRange(document, stage.id, 'component_type') || defaultRange;
            diagnostics.push(new vscode.Diagnostic(
                typeRange,
                `Unknown component type: "${stage.component_type}"`,
                vscode.DiagnosticSeverity.Warning
            ));
        }

        // Validate dependencies
        if (stage.depends_on && Array.isArray(stage.depends_on)) {
            for (const dep of stage.depends_on) {
                // Check if dependency exists
                const depExists = allStages.some(s => s.id === dep);
                if (!depExists) {
                    const depsRange = this.findStagePropertyRange(document, stage.id, 'depends_on') || defaultRange;
                    diagnostics.push(new vscode.Diagnostic(
                        depsRange,
                        `Stage "${stage.id}" depends on unknown stage: "${dep}"`,
                        vscode.DiagnosticSeverity.Error
                    ));
                }

                // Check for self-dependency
                if (dep === stage.id) {
                    const depsRange = this.findStagePropertyRange(document, stage.id, 'depends_on') || defaultRange;
                    diagnostics.push(new vscode.Diagnostic(
                        depsRange,
                        `Stage "${stage.id}" cannot depend on itself`,
                        vscode.DiagnosticSeverity.Error
                    ));
                }
            }
        }

        // Validate ID format (recommend kebab-case or snake_case)
        if (stage.id && !/^[a-z][a-z0-9_-]*$/i.test(stage.id)) {
            const idRange = this.findStagePropertyRange(document, stage.id, 'id') || defaultRange;
            diagnostics.push(new vscode.Diagnostic(
                idRange,
                `Stage ID "${stage.id}" should use alphanumeric characters, hyphens, or underscores`,
                vscode.DiagnosticSeverity.Information
            ));
        }
    }

    /**
     * Detect circular dependencies in the pipeline
     */
    detectCircularDependencies(
        stages: PipelineStage[],
        document: vscode.TextDocument,
        diagnostics: vscode.Diagnostic[]
    ): void {
        const stageMap = new Map<string, PipelineStage>();
        for (const stage of stages) {
            stageMap.set(stage.id, stage);
        }

        const visited = new Set<string>();
        const recursionStack = new Set<string>();

        const hasCycle = (stageId: string, path: string[]): boolean => {
            if (recursionStack.has(stageId)) {
                // Found a cycle - report it
                const cycleStart = path.indexOf(stageId);
                const cyclePath = [...path.slice(cycleStart), stageId];

                const range = this.findStageRange(document, stageId) || new vscode.Range(0, 0, 0, 1);
                diagnostics.push(new vscode.Diagnostic(
                    range,
                    `Circular dependency detected: ${cyclePath.join(' → ')}`,
                    vscode.DiagnosticSeverity.Error
                ));
                return true;
            }

            if (visited.has(stageId)) {
                return false;
            }

            visited.add(stageId);
            recursionStack.add(stageId);

            const stage = stageMap.get(stageId);
            if (stage?.depends_on) {
                for (const dep of stage.depends_on) {
                    if (hasCycle(dep, [...path, stageId])) {
                        return true;
                    }
                }
            }

            recursionStack.delete(stageId);
            return false;
        };

        for (const stage of stages) {
            hasCycle(stage.id, []);
        }
    }

    private extractErrorPosition(message: string, document: vscode.TextDocument): vscode.Position {
        // Try to extract position from JSON parse error message
        // Format: "... at position N" or "... at line L column C"
        const positionMatch = message.match(/position\s+(\d+)/i);
        if (positionMatch) {
            const offset = parseInt(positionMatch[1], 10);
            return document.positionAt(offset);
        }

        const lineColMatch = message.match(/line\s+(\d+)\s+column\s+(\d+)/i);
        if (lineColMatch) {
            const line = parseInt(lineColMatch[1], 10) - 1;
            const col = parseInt(lineColMatch[2], 10) - 1;
            return new vscode.Position(line, col);
        }

        return new vscode.Position(0, 0);
    }

    private findPropertyRange(document: vscode.TextDocument, property: string): vscode.Range | null {
        const text = document.getText();
        const regex = new RegExp(`"${property}"\\s*:`);
        const match = regex.exec(text);

        if (match) {
            const start = document.positionAt(match.index);
            const end = document.positionAt(match.index + match[0].length);
            return new vscode.Range(start, end);
        }

        return null;
    }

    private findStageRange(document: vscode.TextDocument, stageId: string): vscode.Range | null {
        const text = document.getText();
        const idPattern = `"id"\\s*:\\s*"${stageId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}"`;
        const idRegex = new RegExp(idPattern);
        const idMatch = idRegex.exec(text);

        if (!idMatch) {
            return null;
        }

        // Find the opening brace before this ID
        let braceCount = 0;
        let startIndex = idMatch.index;

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

        // Find the closing brace after
        braceCount = 1;
        let endIndex = startIndex + 1;

        for (let i = startIndex + 1; i < text.length; i++) {
            if (text[i] === '{') {
                braceCount++;
            } else if (text[i] === '}') {
                braceCount--;
                if (braceCount === 0) {
                    endIndex = i + 1;
                    break;
                }
            }
        }

        const start = document.positionAt(startIndex);
        const end = document.positionAt(endIndex);
        return new vscode.Range(start, end);
    }

    private findStagePropertyRange(
        document: vscode.TextDocument,
        stageId: string,
        property: string
    ): vscode.Range | null {
        const stageRange = this.findStageRange(document, stageId);
        if (!stageRange) {
            return null;
        }

        const stageText = document.getText(stageRange);
        const regex = new RegExp(`"${property}"\\s*:`);
        const match = regex.exec(stageText);

        if (match) {
            const stageStartOffset = document.offsetAt(stageRange.start);
            const start = document.positionAt(stageStartOffset + match.index);
            const end = document.positionAt(stageStartOffset + match.index + match[0].length);
            return new vscode.Range(start, end);
        }

        return null;
    }

    dispose(): void {
        this.diagnosticCollection.dispose();
        for (const disposable of this.disposables) {
            disposable.dispose();
        }
    }
}
