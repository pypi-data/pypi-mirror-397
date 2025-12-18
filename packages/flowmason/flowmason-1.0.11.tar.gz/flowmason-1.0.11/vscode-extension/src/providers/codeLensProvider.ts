/**
 * FlowMason CodeLens Provider
 *
 * Shows actionable buttons above execute methods and component decorators.
 */

import * as vscode from 'vscode';
import { ComponentParser, ParsedComponent } from '../services/componentParser';

export class FlowMasonCodeLensProvider implements vscode.CodeLensProvider {
    private _onDidChangeCodeLenses: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
    public readonly onDidChangeCodeLenses: vscode.Event<void> = this._onDidChangeCodeLenses.event;

    private componentParser: ComponentParser;

    constructor(componentParser: ComponentParser) {
        this.componentParser = componentParser;

        // Refresh code lenses when configuration changes
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('flowmason')) {
                this._onDidChangeCodeLenses.fire();
            }
        });
    }

    provideCodeLenses(
        document: vscode.TextDocument,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.CodeLens[]> {
        if (document.languageId !== 'python') {
            return [];
        }

        const text = document.getText();
        if (!text.includes('@node') && !text.includes('@operator')) {
            return [];
        }

        const codeLenses: vscode.CodeLens[] = [];
        const components = this.componentParser.parseDocument(document);

        for (const component of components) {
            // Add CodeLens above the decorator
            codeLenses.push(...this.getComponentCodeLenses(document, component));

            // Add CodeLens above execute method
            codeLenses.push(...this.getExecuteCodeLenses(document, component));
        }

        return codeLenses;
    }

    resolveCodeLens(
        codeLens: vscode.CodeLens,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.CodeLens> {
        return codeLens;
    }

    private getComponentCodeLenses(
        document: vscode.TextDocument,
        component: ParsedComponent
    ): vscode.CodeLens[] {
        const codeLenses: vscode.CodeLens[] = [];
        const decoratorLine = component.range.start.line;
        const range = new vscode.Range(decoratorLine, 0, decoratorLine, 0);

        // Preview component
        codeLenses.push(new vscode.CodeLens(range, {
            title: '$(eye) Preview',
            command: 'flowmason.previewComponent',
            tooltip: 'Preview component schema and metadata',
        }));

        // Test component
        codeLenses.push(new vscode.CodeLens(range, {
            title: '$(play) Test',
            command: 'flowmason.testComponent',
            tooltip: 'Run component test',
        }));

        // Open in Studio
        codeLenses.push(new vscode.CodeLens(range, {
            title: '$(browser) Studio',
            command: 'flowmason.openStudio',
            tooltip: 'Open FlowMason Studio',
        }));

        return codeLenses;
    }

    private getExecuteCodeLenses(
        document: vscode.TextDocument,
        component: ParsedComponent
    ): vscode.CodeLens[] {
        const codeLenses: vscode.CodeLens[] = [];
        const text = document.getText();
        const lines = text.split('\n');

        // Find the execute method within the component's range
        for (let i = component.range.start.line; i <= component.range.end.line && i < lines.length; i++) {
            const line = lines[i];
            const executeMatch = line.match(/^\s+(async\s+)?def\s+execute\s*\(/);

            if (executeMatch) {
                const range = new vscode.Range(i, 0, i, 0);

                // Run test with sample input
                codeLenses.push(new vscode.CodeLens(range, {
                    title: '$(debug-start) Run with Test Input',
                    command: 'flowmason.runComponentInline',
                    arguments: [document.uri, component.name],
                    tooltip: 'Execute component with test input',
                }));

                // Debug execution
                if (component.type === 'node') {
                    codeLenses.push(new vscode.CodeLens(range, {
                        title: '$(symbol-event) ' + (component.requires_llm ? 'Uses LLM' : 'No LLM'),
                        command: '',
                        tooltip: component.requires_llm
                            ? 'This node uses an LLM for processing'
                            : 'This node does not require an LLM',
                    }));
                }

                break;
            }
        }

        return codeLenses;
    }
}

/**
 * Register the run component inline command
 */
export function registerRunComponentInlineCommand(
    context: vscode.ExtensionContext,
    outputChannel: vscode.OutputChannel
): void {
    const command = vscode.commands.registerCommand(
        'flowmason.runComponentInline',
        async (uri: vscode.Uri, componentName: string) => {
            outputChannel.appendLine(`\n=== Running ${componentName} ===`);
            outputChannel.show();

            // Get the document
            const document = await vscode.workspace.openTextDocument(uri);
            const fileName = document.fileName;

            // Get Python path from config
            const config = vscode.workspace.getConfiguration('flowmason');
            const pythonPath = config.get<string>('pythonPath') || 'python';

            // Create a simple test runner script
            const testScript = `
import sys
import asyncio
sys.path.insert(0, '${require('path').dirname(fileName)}')

# Import the module
import importlib.util
spec = importlib.util.spec_from_file_location("component", "${fileName}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Find the component class
component_class = None
for name, obj in vars(module).items():
    if hasattr(obj, '__flowmason_component__'):
        component_class = obj
        break

if component_class is None:
    print("No FlowMason component found in file")
    sys.exit(1)

# Run the test
async def run_test():
    component = component_class()
    if hasattr(component, 'test'):
        result = await component.test()
        print("Result:", result)
    else:
        print("Component does not have a test method")

asyncio.run(run_test())
`;

            // Run via terminal for better visibility
            const terminal = vscode.window.createTerminal({
                name: `FlowMason: ${componentName}`,
                cwd: require('path').dirname(fileName),
            });

            terminal.show();
            terminal.sendText(`${pythonPath} -c "${testScript.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"`);

            outputChannel.appendLine(`Test started for ${componentName}`);
        }
    );

    context.subscriptions.push(command);
}
