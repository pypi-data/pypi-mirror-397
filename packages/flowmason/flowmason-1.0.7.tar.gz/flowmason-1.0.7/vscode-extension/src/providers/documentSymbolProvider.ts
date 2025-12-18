/**
 * FlowMason Document Symbol Provider
 *
 * Provides outline view symbols for FlowMason components.
 * Shows:
 * - Component class
 * - Input/Output classes with their fields
 * - execute method
 * - Configuration fields
 */

import * as vscode from 'vscode';
import { ComponentParser, ParsedComponent, ParsedField } from '../services/componentParser';

export class FlowMasonDocumentSymbolProvider implements vscode.DocumentSymbolProvider {
    private componentParser: ComponentParser;

    constructor(componentParser: ComponentParser) {
        this.componentParser = componentParser;
    }

    provideDocumentSymbols(
        document: vscode.TextDocument,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.SymbolInformation[] | vscode.DocumentSymbol[]> {
        if (document.languageId !== 'python') {
            return [];
        }

        const text = document.getText();
        if (!text.includes('@node') && !text.includes('@operator')) {
            return [];
        }

        const symbols: vscode.DocumentSymbol[] = [];
        const components = this.componentParser.parseDocument(document);

        for (const component of components) {
            const componentSymbol = this.createComponentSymbol(document, component);
            symbols.push(componentSymbol);
        }

        return symbols;
    }

    private createComponentSymbol(
        document: vscode.TextDocument,
        component: ParsedComponent
    ): vscode.DocumentSymbol {
        const kind = component.type === 'node'
            ? vscode.SymbolKind.Class
            : vscode.SymbolKind.Function;

        const icon = component.type === 'node' ? '🧠' : '⚙️';
        const detail = `${component.type} - ${component.category}`;

        const componentSymbol = new vscode.DocumentSymbol(
            `${icon} ${component.className}`,
            detail,
            kind,
            component.range,
            component.range
        );

        const children: vscode.DocumentSymbol[] = [];

        // Add Input class symbol
        if (component.inputFields.length > 0) {
            const inputSymbol = this.createIOClassSymbol(
                document,
                'Input',
                component.inputFields,
                component.range
            );
            if (inputSymbol) children.push(inputSymbol);
        }

        // Add Output class symbol
        if (component.outputFields.length > 0) {
            const outputSymbol = this.createIOClassSymbol(
                document,
                'Output',
                component.outputFields,
                component.range
            );
            if (outputSymbol) children.push(outputSymbol);
        }

        // Add execute method symbol
        const executeSymbol = this.findExecuteMethod(document, component);
        if (executeSymbol) children.push(executeSymbol);

        componentSymbol.children = children;
        return componentSymbol;
    }

    private createIOClassSymbol(
        document: vscode.TextDocument,
        className: string,
        fields: ParsedField[],
        componentRange: vscode.Range
    ): vscode.DocumentSymbol | null {
        // Find the class definition in the document
        const text = document.getText();
        const lines = text.split('\n');

        let classLine = -1;
        let classEndLine = -1;

        for (let i = componentRange.start.line; i <= componentRange.end.line && i < lines.length; i++) {
            if (lines[i].match(new RegExp(`class\\s+${className}\\s*[:(]`))) {
                classLine = i;
                // Find end of class
                const indent = this.getIndent(lines[i]);
                for (let j = i + 1; j < lines.length; j++) {
                    const lineIndent = this.getIndent(lines[j]);
                    const trimmed = lines[j].trim();
                    if (trimmed !== '' && lineIndent <= indent) {
                        classEndLine = j - 1;
                        break;
                    }
                }
                if (classEndLine === -1) classEndLine = componentRange.end.line;
                break;
            }
        }

        if (classLine === -1) return null;

        const range = new vscode.Range(classLine, 0, classEndLine, lines[classEndLine]?.length || 0);
        const icon = className === 'Input' ? '📥' : '📤';

        const classSymbol = new vscode.DocumentSymbol(
            `${icon} ${className}`,
            `${fields.length} fields`,
            vscode.SymbolKind.Struct,
            range,
            range
        );

        // Add field symbols
        classSymbol.children = fields.map(field => {
            const fieldLine = this.findFieldLine(document, field.name, classLine, classEndLine);
            const fieldRange = fieldLine >= 0
                ? new vscode.Range(fieldLine, 0, fieldLine, lines[fieldLine]?.length || 0)
                : range;

            return new vscode.DocumentSymbol(
                field.name,
                `${field.type}${field.required ? '' : '?'}`,
                vscode.SymbolKind.Field,
                fieldRange,
                fieldRange
            );
        });

        return classSymbol;
    }

    private findExecuteMethod(
        document: vscode.TextDocument,
        component: ParsedComponent
    ): vscode.DocumentSymbol | null {
        const text = document.getText();
        const lines = text.split('\n');

        for (let i = component.range.start.line; i <= component.range.end.line && i < lines.length; i++) {
            const line = lines[i];
            const match = line.match(/^\s+(async\s+)?def\s+execute\s*\(/);

            if (match) {
                // Find end of method
                const methodIndent = this.getIndent(line);
                let endLine = i;

                for (let j = i + 1; j < lines.length; j++) {
                    const lineIndent = this.getIndent(lines[j]);
                    const trimmed = lines[j].trim();
                    if (trimmed !== '' && lineIndent <= methodIndent) {
                        endLine = j - 1;
                        break;
                    }
                    endLine = j;
                }

                const range = new vscode.Range(i, 0, endLine, lines[endLine]?.length || 0);
                const isAsync = match[1] !== undefined;

                return new vscode.DocumentSymbol(
                    `▶️ execute`,
                    isAsync ? 'async' : 'sync',
                    vscode.SymbolKind.Method,
                    range,
                    range
                );
            }
        }

        return null;
    }

    private findFieldLine(
        document: vscode.TextDocument,
        fieldName: string,
        startLine: number,
        endLine: number
    ): number {
        const lines = document.getText().split('\n');

        for (let i = startLine; i <= endLine && i < lines.length; i++) {
            if (lines[i].match(new RegExp(`^\\s+${fieldName}\\s*:`))) {
                return i;
            }
        }

        return -1;
    }

    private getIndent(line: string): number {
        const match = line.match(/^(\s*)/);
        return match ? match[1].length : 0;
    }
}
