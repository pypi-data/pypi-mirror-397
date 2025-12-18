/**
 * Pipeline Symbol Provider
 *
 * Provides document symbols for .pipeline.json files to enable
 * the native VSCode Outline view and breadcrumb navigation.
 */

import * as vscode from 'vscode';
import { PipelineFile, PipelineStage } from '../views/pipelineStagesTree';

export class PipelineSymbolProvider implements vscode.DocumentSymbolProvider {
    provideDocumentSymbols(
        document: vscode.TextDocument,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.DocumentSymbol[]> {
        // Only process .pipeline.json files
        if (!document.fileName.endsWith('.pipeline.json')) {
            return [];
        }

        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;
            return this.buildSymbols(document, pipeline);
        } catch {
            // Invalid JSON - return empty
            return [];
        }
    }

    private buildSymbols(
        document: vscode.TextDocument,
        pipeline: PipelineFile
    ): vscode.DocumentSymbol[] {
        const symbols: vscode.DocumentSymbol[] = [];

        // Pipeline name as the root symbol
        const pipelineRange = new vscode.Range(
            document.positionAt(0),
            document.positionAt(document.getText().length)
        );
        const pipelineNameRange = this.findPropertyRange(document, 'name') || pipelineRange;

        const pipelineSymbol = new vscode.DocumentSymbol(
            pipeline.name || 'Pipeline',
            pipeline.description || `${pipeline.stages?.length || 0} stages`,
            vscode.SymbolKind.Module,
            pipelineRange,
            pipelineNameRange
        );

        // Add metadata as children
        if (pipeline.version) {
            const versionRange = this.findPropertyRange(document, 'version');
            if (versionRange) {
                pipelineSymbol.children.push(new vscode.DocumentSymbol(
                    'version',
                    pipeline.version,
                    vscode.SymbolKind.Constant,
                    versionRange,
                    versionRange
                ));
            }
        }

        // Stages section
        if (pipeline.stages && pipeline.stages.length > 0) {
            const stagesRange = this.findPropertyRange(document, 'stages');
            if (stagesRange) {
                const stagesSymbol = new vscode.DocumentSymbol(
                    'stages',
                    `${pipeline.stages.length} stages`,
                    vscode.SymbolKind.Array,
                    this.expandRangeToBlock(document, stagesRange),
                    stagesRange
                );

                // Add each stage
                for (const stage of pipeline.stages) {
                    const stageSymbol = this.createStageSymbol(document, stage);
                    if (stageSymbol) {
                        stagesSymbol.children.push(stageSymbol);
                    }
                }

                pipelineSymbol.children.push(stagesSymbol);
            }
        }

        symbols.push(pipelineSymbol);
        return symbols;
    }

    private createStageSymbol(
        document: vscode.TextDocument,
        stage: PipelineStage
    ): vscode.DocumentSymbol | null {
        const stageRange = this.findStageRange(document, stage.id);
        if (!stageRange) {
            return null;
        }

        const idRange = this.findStagePropertyRange(document, stage.id, 'id') || stageRange;

        // Determine symbol kind based on component type
        const symbolKind = this.getSymbolKind(stage.component_type);

        const stageSymbol = new vscode.DocumentSymbol(
            stage.id,
            stage.component_type,
            symbolKind,
            stageRange,
            idRange
        );

        // Add dependencies as children
        if (stage.depends_on && stage.depends_on.length > 0) {
            const depsRange = this.findStagePropertyRange(document, stage.id, 'depends_on');
            if (depsRange) {
                const depsSymbol = new vscode.DocumentSymbol(
                    'depends_on',
                    stage.depends_on.join(', '),
                    vscode.SymbolKind.Array,
                    depsRange,
                    depsRange
                );
                stageSymbol.children.push(depsSymbol);
            }
        }

        // Add config as children
        if (stage.config && Object.keys(stage.config).length > 0) {
            const configRange = this.findStagePropertyRange(document, stage.id, 'config');
            if (configRange) {
                const configSymbol = new vscode.DocumentSymbol(
                    'config',
                    `${Object.keys(stage.config).length} properties`,
                    vscode.SymbolKind.Object,
                    this.expandRangeToBlock(document, configRange),
                    configRange
                );

                // Add config properties
                for (const [key, value] of Object.entries(stage.config)) {
                    const valueStr = this.formatValue(value);
                    configSymbol.children.push(new vscode.DocumentSymbol(
                        key,
                        valueStr,
                        vscode.SymbolKind.Property,
                        configRange, // Simplified - could parse more precisely
                        configRange
                    ));
                }

                stageSymbol.children.push(configSymbol);
            }
        }

        return stageSymbol;
    }

    private getSymbolKind(componentType: string): vscode.SymbolKind {
        // Control flow
        if (componentType.includes('conditional') || componentType.includes('if') ||
            componentType.includes('router') || componentType.includes('switch')) {
            return vscode.SymbolKind.Enum;
        }
        if (componentType.includes('foreach') || componentType.includes('loop')) {
            return vscode.SymbolKind.Event;
        }
        if (componentType.includes('trycatch') || componentType.includes('error')) {
            return vscode.SymbolKind.Interface;
        }
        if (componentType.includes('subpipeline') || componentType.includes('sub-pipeline')) {
            return vscode.SymbolKind.Module;
        }

        // AI nodes
        if (componentType.includes('generator') || componentType.includes('llm') ||
            componentType.includes('ai') || componentType.includes('critic') ||
            componentType.includes('improver') || componentType.includes('synthesizer')) {
            return vscode.SymbolKind.Class;
        }

        // Default - function for operators
        return vscode.SymbolKind.Function;
    }

    private formatValue(value: unknown): string {
        if (typeof value === 'string') {
            return value.length > 40 ? value.substring(0, 37) + '...' : value;
        }
        if (typeof value === 'number' || typeof value === 'boolean') {
            return String(value);
        }
        if (Array.isArray(value)) {
            return `[${value.length} items]`;
        }
        if (typeof value === 'object' && value !== null) {
            return `{...}`;
        }
        return String(value);
    }

    /**
     * Find the range of a top-level property in the document
     */
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

    /**
     * Find the range of an entire stage object by its ID
     */
    private findStageRange(document: vscode.TextDocument, stageId: string): vscode.Range | null {
        const text = document.getText();

        // Find the stage ID
        const idPattern = `"id"\\s*:\\s*"${stageId}"`;
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

    /**
     * Find a property range within a specific stage
     */
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

    /**
     * Expand a range to include the full JSON block that follows
     */
    private expandRangeToBlock(document: vscode.TextDocument, range: vscode.Range): vscode.Range {
        const text = document.getText();
        const startOffset = document.offsetAt(range.end);

        // Find the opening bracket/brace
        let bracketType: string | null = null;
        let bracketIndex = startOffset;

        for (let i = startOffset; i < text.length; i++) {
            if (text[i] === '[') {
                bracketType = '[';
                bracketIndex = i;
                break;
            } else if (text[i] === '{') {
                bracketType = '{';
                bracketIndex = i;
                break;
            } else if (text[i] !== ' ' && text[i] !== '\n' && text[i] !== '\t') {
                // Value is not a block
                return range;
            }
        }

        if (!bracketType) {
            return range;
        }

        // Find the matching closing bracket
        const closeBracket = bracketType === '[' ? ']' : '}';
        let depth = 1;
        let endIndex = bracketIndex + 1;

        for (let i = bracketIndex + 1; i < text.length; i++) {
            if (text[i] === bracketType) {
                depth++;
            } else if (text[i] === closeBracket) {
                depth--;
                if (depth === 0) {
                    endIndex = i + 1;
                    break;
                }
            }
        }

        return new vscode.Range(range.start, document.positionAt(endIndex));
    }
}
