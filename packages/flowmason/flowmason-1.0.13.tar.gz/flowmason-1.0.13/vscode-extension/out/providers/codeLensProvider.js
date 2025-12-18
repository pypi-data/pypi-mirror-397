"use strict";
/**
 * FlowMason CodeLens Provider
 *
 * Shows actionable buttons above execute methods and component decorators.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowMasonCodeLensProvider = void 0;
exports.registerRunComponentInlineCommand = registerRunComponentInlineCommand;
const vscode = __importStar(require("vscode"));
class FlowMasonCodeLensProvider {
    constructor(componentParser) {
        this._onDidChangeCodeLenses = new vscode.EventEmitter();
        this.onDidChangeCodeLenses = this._onDidChangeCodeLenses.event;
        this.componentParser = componentParser;
        // Refresh code lenses when configuration changes
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('flowmason')) {
                this._onDidChangeCodeLenses.fire();
            }
        });
    }
    provideCodeLenses(document, _token) {
        if (document.languageId !== 'python') {
            return [];
        }
        const text = document.getText();
        if (!text.includes('@node') && !text.includes('@operator')) {
            return [];
        }
        const codeLenses = [];
        const components = this.componentParser.parseDocument(document);
        for (const component of components) {
            // Add CodeLens above the decorator
            codeLenses.push(...this.getComponentCodeLenses(document, component));
            // Add CodeLens above execute method
            codeLenses.push(...this.getExecuteCodeLenses(document, component));
        }
        return codeLenses;
    }
    resolveCodeLens(codeLens, _token) {
        return codeLens;
    }
    getComponentCodeLenses(document, component) {
        const codeLenses = [];
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
    getExecuteCodeLenses(document, component) {
        const codeLenses = [];
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
exports.FlowMasonCodeLensProvider = FlowMasonCodeLensProvider;
/**
 * Register the run component inline command
 */
function registerRunComponentInlineCommand(context, outputChannel) {
    const command = vscode.commands.registerCommand('flowmason.runComponentInline', async (uri, componentName) => {
        outputChannel.appendLine(`\n=== Running ${componentName} ===`);
        outputChannel.show();
        // Get the document
        const document = await vscode.workspace.openTextDocument(uri);
        const fileName = document.fileName;
        // Get Python path from config
        const config = vscode.workspace.getConfiguration('flowmason');
        const pythonPath = config.get('pythonPath') || 'python';
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
    });
    context.subscriptions.push(command);
}
//# sourceMappingURL=codeLensProvider.js.map