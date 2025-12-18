/**
 * FlowMason Code Action Provider
 *
 * Provides quick fixes for FlowMason diagnostics.
 */

import * as vscode from 'vscode';

export class FlowMasonCodeActionProvider implements vscode.CodeActionProvider {
    public static readonly providedCodeActionKinds = [
        vscode.CodeActionKind.QuickFix,
        vscode.CodeActionKind.Refactor,
    ];

    provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range | vscode.Selection,
        context: vscode.CodeActionContext,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<(vscode.CodeAction | vscode.Command)[]> {
        const actions: vscode.CodeAction[] = [];

        // Process diagnostics
        for (const diagnostic of context.diagnostics) {
            if (diagnostic.source !== 'flowmason') {
                continue;
            }

            const message = diagnostic.message;

            // Fix: Add missing decorator
            if (message.includes('missing @node/@operator decorator')) {
                actions.push(this.createAddDecoratorFix(document, diagnostic));
            }

            // Fix: Add description to decorator
            if (message.includes('Consider adding a description')) {
                const action = this.createAddDescriptionFix(document, diagnostic);
                if (action) actions.push(action);
            }

            // Fix: Add description to field
            if (message.includes('Consider adding a description to this field')) {
                const action = this.createAddFieldDescriptionFix(document, diagnostic);
                if (action) actions.push(action);
            }

            // Fix: Kebab-case naming
            if (message.includes('should be kebab-case')) {
                const action = this.createKebabCaseFix(document, diagnostic);
                if (action) actions.push(action);
            }

            // Fix: Add Input class
            if (message.includes('should have an Input class')) {
                actions.push(this.createAddInputClassFix(document, diagnostic));
            }

            // Fix: Add Output class
            if (message.includes('should have an Output class')) {
                actions.push(this.createAddOutputClassFix(document, diagnostic));
            }

            // Fix: Add return type annotation
            if (message.includes('return type annotation')) {
                const action = this.createAddReturnTypeFix(document, diagnostic);
                if (action) actions.push(action);
            }
        }

        // Add refactoring actions based on current line
        const lineText = document.lineAt(range.start.line).text;

        // Convert class to node/operator
        if (lineText.match(/class\s+\w+\s*\(/)) {
            if (!this.hasDecoratorAbove(document, range.start.line)) {
                actions.push(this.createConvertToNodeAction(document, range.start.line));
                actions.push(this.createConvertToOperatorAction(document, range.start.line));
            }
        }

        // Extract to Input/Output class
        if (lineText.includes(': str') || lineText.includes(': int') || lineText.includes(': bool')) {
            if (!this.isInsideClass(document, range.start.line, 'Input') &&
                !this.isInsideClass(document, range.start.line, 'Output')) {
                // Could add "Extract to Input class" action here
            }
        }

        return actions;
    }

    private createAddDecoratorFix(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Add @node decorator',
            vscode.CodeActionKind.QuickFix
        );

        const line = diagnostic.range.start.line;
        const indent = this.getIndent(document.lineAt(line).text);

        action.edit = new vscode.WorkspaceEdit();
        action.edit.insert(
            document.uri,
            new vscode.Position(line, 0),
            `${indent}@node(\n${indent}    name="component-name",\n${indent}    description="Description",\n${indent})\n`
        );

        action.diagnostics = [diagnostic];
        action.isPreferred = true;

        return action;
    }

    private createAddDescriptionFix(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): vscode.CodeAction | null {
        const lineText = document.lineAt(diagnostic.range.start.line).text;

        // Find the closing paren of the decorator
        const match = lineText.match(/@(node|operator)\s*\(([^)]*)\)/);
        if (!match) return null;

        const action = new vscode.CodeAction(
            'Add description parameter',
            vscode.CodeActionKind.QuickFix
        );

        action.edit = new vscode.WorkspaceEdit();

        // Check if there are existing parameters
        const params = match[2].trim();
        const hasParams = params.length > 0;

        if (hasParams) {
            // Add after existing params
            const insertPos = lineText.lastIndexOf(')');
            action.edit.insert(
                document.uri,
                new vscode.Position(diagnostic.range.start.line, insertPos),
                ', description="Description"'
            );
        } else {
            // Replace empty parens
            const startPos = lineText.indexOf('(') + 1;
            const endPos = lineText.indexOf(')');
            action.edit.replace(
                document.uri,
                new vscode.Range(
                    diagnostic.range.start.line, startPos,
                    diagnostic.range.start.line, endPos
                ),
                'description="Description"'
            );
        }

        action.diagnostics = [diagnostic];
        return action;
    }

    private createAddFieldDescriptionFix(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): vscode.CodeAction | null {
        const lineText = document.lineAt(diagnostic.range.start.line).text;

        // Find Field() in the line
        const match = lineText.match(/Field\s*\(([^)]*)\)/);
        if (!match) return null;

        const action = new vscode.CodeAction(
            'Add field description',
            vscode.CodeActionKind.QuickFix
        );

        action.edit = new vscode.WorkspaceEdit();

        const params = match[1].trim();
        const fieldStart = lineText.indexOf('Field(') + 6;
        const fieldEnd = lineText.indexOf(')', fieldStart);

        if (params.length > 0) {
            // Prepend description
            action.edit.insert(
                document.uri,
                new vscode.Position(diagnostic.range.start.line, fieldStart),
                'description="Field description", '
            );
        } else {
            action.edit.replace(
                document.uri,
                new vscode.Range(
                    diagnostic.range.start.line, fieldStart,
                    diagnostic.range.start.line, fieldEnd
                ),
                'description="Field description"'
            );
        }

        action.diagnostics = [diagnostic];
        return action;
    }

    private createKebabCaseFix(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): vscode.CodeAction | null {
        const lineText = document.lineAt(diagnostic.range.start.line).text;

        // Extract the name
        const match = lineText.match(/name\s*=\s*["']([^"']+)["']/);
        if (!match) return null;

        const currentName = match[1];
        const kebabName = this.toKebabCase(currentName);

        if (kebabName === currentName) return null;

        const action = new vscode.CodeAction(
            `Change to "${kebabName}"`,
            vscode.CodeActionKind.QuickFix
        );

        action.edit = new vscode.WorkspaceEdit();

        const startCol = lineText.indexOf(currentName);
        action.edit.replace(
            document.uri,
            new vscode.Range(
                diagnostic.range.start.line, startCol,
                diagnostic.range.start.line, startCol + currentName.length
            ),
            kebabName
        );

        action.diagnostics = [diagnostic];
        action.isPreferred = true;

        return action;
    }

    private createAddInputClassFix(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Add Input class',
            vscode.CodeActionKind.QuickFix
        );

        // Find the decorator line (should be above the class)
        let insertLine = diagnostic.range.start.line;
        for (let i = insertLine - 1; i >= 0; i--) {
            const line = document.lineAt(i).text;
            if (line.match(/@(node|operator)\s*\(/)) {
                insertLine = i;
                break;
            }
        }

        action.edit = new vscode.WorkspaceEdit();
        action.edit.insert(
            document.uri,
            new vscode.Position(insertLine, 0),
            'class Input:\n    text: str = Field(description="Input text")\n\n\n'
        );

        action.diagnostics = [diagnostic];
        return action;
    }

    private createAddOutputClassFix(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Add Output class',
            vscode.CodeActionKind.QuickFix
        );

        // Find where to insert (after Input class or before decorator)
        let insertLine = diagnostic.range.start.line;
        const text = document.getText();

        // Look for Input class
        const inputMatch = text.match(/class Input.*?:\n(.*?\n)*?\n/);
        if (inputMatch) {
            const inputEnd = text.indexOf(inputMatch[0]) + inputMatch[0].length;
            insertLine = document.positionAt(inputEnd).line;
        } else {
            // Insert before decorator
            for (let i = insertLine - 1; i >= 0; i--) {
                const line = document.lineAt(i).text;
                if (line.match(/@(node|operator)\s*\(/)) {
                    insertLine = i;
                    break;
                }
            }
        }

        action.edit = new vscode.WorkspaceEdit();
        action.edit.insert(
            document.uri,
            new vscode.Position(insertLine, 0),
            'class Output:\n    result: str = Field(description="Output result")\n\n\n'
        );

        action.diagnostics = [diagnostic];
        return action;
    }

    private createAddReturnTypeFix(
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): vscode.CodeAction | null {
        const lineText = document.lineAt(diagnostic.range.start.line).text;

        // Find the colon at end of def
        const colonIndex = lineText.lastIndexOf(':');
        if (colonIndex === -1) return null;

        const action = new vscode.CodeAction(
            'Add return type annotation -> Output',
            vscode.CodeActionKind.QuickFix
        );

        action.edit = new vscode.WorkspaceEdit();
        action.edit.insert(
            document.uri,
            new vscode.Position(diagnostic.range.start.line, colonIndex),
            ' -> Output'
        );

        action.diagnostics = [diagnostic];
        return action;
    }

    private createConvertToNodeAction(
        document: vscode.TextDocument,
        line: number
    ): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Convert to FlowMason Node',
            vscode.CodeActionKind.Refactor
        );

        const lineText = document.lineAt(line).text;
        const classMatch = lineText.match(/class\s+(\w+)/);
        const className = classMatch ? classMatch[1] : 'MyNode';
        const nodeName = this.toKebabCase(className.replace(/Node$/, ''));

        action.edit = new vscode.WorkspaceEdit();
        action.edit.insert(
            document.uri,
            new vscode.Position(line, 0),
            `@node(\n    name="${nodeName}",\n    description="Description",\n    category="ai",\n)\n`
        );

        return action;
    }

    private createConvertToOperatorAction(
        document: vscode.TextDocument,
        line: number
    ): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Convert to FlowMason Operator',
            vscode.CodeActionKind.Refactor
        );

        const lineText = document.lineAt(line).text;
        const classMatch = lineText.match(/class\s+(\w+)/);
        const className = classMatch ? classMatch[1] : 'MyOperator';
        const operatorName = this.toKebabCase(className.replace(/Operator$/, ''));

        action.edit = new vscode.WorkspaceEdit();
        action.edit.insert(
            document.uri,
            new vscode.Position(line, 0),
            `@operator(\n    name="${operatorName}",\n    description="Description",\n    category="transform",\n)\n`
        );

        return action;
    }

    private hasDecoratorAbove(document: vscode.TextDocument, line: number): boolean {
        if (line === 0) return false;

        for (let i = line - 1; i >= Math.max(0, line - 10); i--) {
            const text = document.lineAt(i).text.trim();
            if (text.startsWith('@node') || text.startsWith('@operator')) {
                return true;
            }
            if (text.match(/^(class |def |import |from )/)) {
                return false;
            }
        }
        return false;
    }

    private isInsideClass(document: vscode.TextDocument, line: number, className: string): boolean {
        for (let i = line - 1; i >= 0; i--) {
            const text = document.lineAt(i).text;
            if (text.match(new RegExp(`class\\s+${className}\\s*[:(]`))) {
                return true;
            }
            if (text.match(/^class\s+/) && !text.includes(className)) {
                return false;
            }
        }
        return false;
    }

    private getIndent(text: string): string {
        const match = text.match(/^(\s*)/);
        return match ? match[1] : '';
    }

    private toKebabCase(str: string): string {
        return str
            .replace(/([a-z])([A-Z])/g, '$1-$2')
            .replace(/([A-Z])([A-Z][a-z])/g, '$1-$2')
            .replace(/[\s_]+/g, '-')
            .toLowerCase();
    }
}
