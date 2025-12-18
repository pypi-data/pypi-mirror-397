/**
 * FlowMason Completion Provider
 *
 * Provides IntelliSense auto-completion for FlowMason components.
 */

import * as vscode from 'vscode';

export class FlowMasonCompletionProvider implements vscode.CompletionItemProvider {
    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        _token: vscode.CancellationToken,
        _context: vscode.CompletionContext
    ): vscode.ProviderResult<vscode.CompletionItem[] | vscode.CompletionList> {
        const linePrefix = document.lineAt(position).text.substring(0, position.character);
        const completions: vscode.CompletionItem[] = [];

        // Decorator completions
        if (linePrefix.endsWith('@')) {
            completions.push(...this.getDecoratorCompletions());
        }

        // Import completions
        if (linePrefix.includes('from flowmason')) {
            completions.push(...this.getImportCompletions());
        }

        // Field type completions inside Input/Output classes
        if (this.isInsideIOClass(document, position)) {
            completions.push(...this.getFieldCompletions());
        }

        // Upstream reference completions
        if (linePrefix.includes('upstream.') || linePrefix.includes('upstream[')) {
            completions.push(...this.getUpstreamCompletions(document));
        }

        // Config option completions inside decorators
        if (this.isInsideDecorator(document, position)) {
            completions.push(...this.getDecoratorOptionCompletions(document, position));
        }

        return completions;
    }

    private getDecoratorCompletions(): vscode.CompletionItem[] {
        const nodeDecorator = new vscode.CompletionItem('node', vscode.CompletionItemKind.Function);
        nodeDecorator.insertText = new vscode.SnippetString(
            'node(\n' +
            '    name="${1:my-node}",\n' +
            '    description="${2:Description}",\n' +
            '    category="${3|ai,transform,analysis,integration,utility|}",\n' +
            '    icon="${4|brain,sparkles,message-square,search,zap,database,globe,file-text|}",\n' +
            '    color="${5:#6366f1}",\n' +
            ')\n'
        );
        nodeDecorator.documentation = new vscode.MarkdownString(
            'Creates a FlowMason Node component.\n\n' +
            'Nodes are AI-powered components that use LLMs for processing.\n\n' +
            '**Required Parameters:**\n' +
            '- `name`: Unique identifier (kebab-case)\n' +
            '- `description`: Human-readable description\n\n' +
            '**Optional Parameters:**\n' +
            '- `category`: Component category\n' +
            '- `icon`: Lucide icon name\n' +
            '- `color`: Hex color code'
        );
        nodeDecorator.detail = 'FlowMason Node Decorator';

        const operatorDecorator = new vscode.CompletionItem('operator', vscode.CompletionItemKind.Function);
        operatorDecorator.insertText = new vscode.SnippetString(
            'operator(\n' +
            '    name="${1:my-operator}",\n' +
            '    description="${2:Description}",\n' +
            '    category="${3|transform,filter,aggregate,utility|}",\n' +
            '    icon="${4|filter,shuffle,merge,split,transform|}",\n' +
            '    color="${5:#10b981}",\n' +
            ')\n'
        );
        operatorDecorator.documentation = new vscode.MarkdownString(
            'Creates a FlowMason Operator component.\n\n' +
            'Operators are deterministic components that transform data without LLMs.\n\n' +
            '**Required Parameters:**\n' +
            '- `name`: Unique identifier (kebab-case)\n' +
            '- `description`: Human-readable description\n\n' +
            '**Optional Parameters:**\n' +
            '- `category`: Component category\n' +
            '- `icon`: Lucide icon name\n' +
            '- `color`: Hex color code'
        );
        operatorDecorator.detail = 'FlowMason Operator Decorator';

        return [nodeDecorator, operatorDecorator];
    }

    private getImportCompletions(): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];

        // Core imports
        const imports = [
            { label: 'node', detail: 'Node decorator' },
            { label: 'operator', detail: 'Operator decorator' },
            { label: 'BaseNode', detail: 'Base class for nodes' },
            { label: 'BaseOperator', detail: 'Base class for operators' },
            { label: 'NodeContext', detail: 'Context passed to node execute' },
            { label: 'OperatorContext', detail: 'Context passed to operator execute' },
            { label: 'Field', detail: 'Field definition for Input/Output' },
            { label: 'LLMConfig', detail: 'LLM configuration' },
            { label: 'Provider', detail: 'LLM provider enum' },
        ];

        for (const imp of imports) {
            const item = new vscode.CompletionItem(imp.label, vscode.CompletionItemKind.Class);
            item.detail = imp.detail;
            completions.push(item);
        }

        return completions;
    }

    private getFieldCompletions(): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];

        // String field
        const stringField = new vscode.CompletionItem('str = Field', vscode.CompletionItemKind.Property);
        stringField.insertText = new vscode.SnippetString(
            '${1:field_name}: str = Field(description="${2:Field description}")'
        );
        stringField.detail = 'String field';
        completions.push(stringField);

        // Integer field
        const intField = new vscode.CompletionItem('int = Field', vscode.CompletionItemKind.Property);
        intField.insertText = new vscode.SnippetString(
            '${1:field_name}: int = Field(description="${2:Field description}", default=${3:0})'
        );
        intField.detail = 'Integer field';
        completions.push(intField);

        // Boolean field
        const boolField = new vscode.CompletionItem('bool = Field', vscode.CompletionItemKind.Property);
        boolField.insertText = new vscode.SnippetString(
            '${1:field_name}: bool = Field(description="${2:Field description}", default=${3:False})'
        );
        boolField.detail = 'Boolean field';
        completions.push(boolField);

        // List field
        const listField = new vscode.CompletionItem('List = Field', vscode.CompletionItemKind.Property);
        listField.insertText = new vscode.SnippetString(
            '${1:field_name}: List[${2:str}] = Field(description="${3:Field description}", default_factory=list)'
        );
        listField.detail = 'List field';
        completions.push(listField);

        // Dict field
        const dictField = new vscode.CompletionItem('Dict = Field', vscode.CompletionItemKind.Property);
        dictField.insertText = new vscode.SnippetString(
            '${1:field_name}: Dict[str, ${2:Any}] = Field(description="${3:Field description}", default_factory=dict)'
        );
        dictField.detail = 'Dictionary field';
        completions.push(dictField);

        // Optional field
        const optField = new vscode.CompletionItem('Optional = Field', vscode.CompletionItemKind.Property);
        optField.insertText = new vscode.SnippetString(
            '${1:field_name}: Optional[${2:str}] = Field(description="${3:Field description}", default=None)'
        );
        optField.detail = 'Optional field';
        completions.push(optField);

        return completions;
    }

    private getUpstreamCompletions(document: vscode.TextDocument): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];
        const text = document.getText();

        // Find depends_on references in the file
        const dependsOnMatch = text.match(/depends_on\s*=\s*\[(.*?)\]/s);
        if (dependsOnMatch) {
            const deps = dependsOnMatch[1].match(/"([^"]+)"/g);
            if (deps) {
                for (const dep of deps) {
                    const stageName = dep.replace(/"/g, '');
                    const item = new vscode.CompletionItem(stageName, vscode.CompletionItemKind.Reference);
                    item.detail = 'Upstream stage';
                    item.documentation = `Reference to upstream stage "${stageName}"`;
                    completions.push(item);
                }
            }
        }

        // Common upstream output fields
        const outputFields = [
            { label: 'content', detail: 'Generated content (nodes)' },
            { label: 'result', detail: 'Processing result (operators)' },
            { label: 'data', detail: 'Output data' },
            { label: 'items', detail: 'List of items' },
            { label: 'success', detail: 'Success status' },
            { label: 'error', detail: 'Error message if failed' },
        ];

        for (const field of outputFields) {
            const item = new vscode.CompletionItem(field.label, vscode.CompletionItemKind.Property);
            item.detail = field.detail;
            completions.push(item);
        }

        return completions;
    }

    private getDecoratorOptionCompletions(document: vscode.TextDocument, position: vscode.Position): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];

        // Find which decorator we're in
        const textBefore = document.getText(new vscode.Range(new vscode.Position(0, 0), position));
        const isNodeDecorator = /\@node\s*\([^)]*$/s.test(textBefore);
        const isOperatorDecorator = /\@operator\s*\([^)]*$/s.test(textBefore);

        if (isNodeDecorator || isOperatorDecorator) {
            const options = [
                { label: 'name', snippet: 'name="${1:component-name}"', detail: 'Component name (kebab-case)' },
                { label: 'description', snippet: 'description="${1:Description}"', detail: 'Component description' },
                { label: 'category', snippet: 'category="${1:ai}"', detail: 'Component category' },
                { label: 'icon', snippet: 'icon="${1:brain}"', detail: 'Lucide icon name' },
                { label: 'color', snippet: 'color="${1:#6366f1}"', detail: 'Hex color code' },
                { label: 'version', snippet: 'version="${1:1.0.0}"', detail: 'Component version' },
                { label: 'tags', snippet: 'tags=[${1:"tag1", "tag2"}]', detail: 'Component tags' },
            ];

            if (isNodeDecorator) {
                options.push(
                    { label: 'requires_llm', snippet: 'requires_llm=${1:True}', detail: 'Whether node requires LLM' },
                    { label: 'default_provider', snippet: 'default_provider="${1:anthropic}"', detail: 'Default LLM provider' },
                    { label: 'default_model', snippet: 'default_model="${1:claude-sonnet-4-20250514}"', detail: 'Default model' }
                );
            }

            for (const opt of options) {
                const item = new vscode.CompletionItem(opt.label, vscode.CompletionItemKind.Property);
                item.insertText = new vscode.SnippetString(opt.snippet);
                item.detail = opt.detail;
                completions.push(item);
            }
        }

        return completions;
    }

    private isInsideIOClass(document: vscode.TextDocument, position: vscode.Position): boolean {
        // Check if we're inside an Input or Output class definition
        const textBefore = document.getText(new vscode.Range(new vscode.Position(0, 0), position));

        // Find the last class definition
        const classMatch = textBefore.match(/class\s+(Input|Output)\s*\([^)]*\)\s*:\s*$/m);
        if (!classMatch) return false;

        // Check we haven't left the class (no new class/def at same or lower indentation)
        const lastClassIndex = textBefore.lastIndexOf(classMatch[0]);
        const afterClass = textBefore.substring(lastClassIndex);

        // Simple heuristic: if there's another class/def at column 0-4, we've left
        const leftClass = /\n(class |def |@(?!node|operator))/.test(afterClass.substring(classMatch[0].length));

        return !leftClass;
    }

    private isInsideDecorator(document: vscode.TextDocument, position: vscode.Position): boolean {
        const line = document.lineAt(position).text;
        const textBefore = document.getText(new vscode.Range(new vscode.Position(0, 0), position));

        // Check if we're on a line that starts with @ or within unclosed parentheses after @
        if (line.trim().startsWith('@')) return true;

        // Check for unclosed decorator
        const decoratorStart = textBefore.lastIndexOf('@node(');
        const operatorStart = textBefore.lastIndexOf('@operator(');
        const lastStart = Math.max(decoratorStart, operatorStart);

        if (lastStart === -1) return false;

        const afterDecorator = textBefore.substring(lastStart);
        const openParens = (afterDecorator.match(/\(/g) || []).length;
        const closeParens = (afterDecorator.match(/\)/g) || []).length;

        return openParens > closeParens;
    }
}
