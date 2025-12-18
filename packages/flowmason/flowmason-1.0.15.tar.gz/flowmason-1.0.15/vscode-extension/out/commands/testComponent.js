"use strict";
/**
 * Test Component Command
 *
 * Tests a FlowMason component with sample input.
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
exports.registerTestComponentCommand = registerTestComponentCommand;
const vscode = __importStar(require("vscode"));
const componentParser_1 = require("../services/componentParser");
function registerTestComponentCommand(context, flowmasonService, outputChannel) {
    const componentParser = new componentParser_1.ComponentParser();
    const command = vscode.commands.registerCommand('flowmason.testComponent', async () => {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor || editor.document.languageId !== 'python') {
                vscode.window.showErrorMessage('Open a Python file with a FlowMason component');
                return;
            }
            // Parse the document
            const components = componentParser.parseDocument(editor.document);
            if (components.length === 0) {
                vscode.window.showErrorMessage('No FlowMason components found in this file');
                return;
            }
            // If multiple components, let user select
            let component = components[0];
            if (components.length > 1) {
                const selection = await vscode.window.showQuickPick(components.map(c => ({
                    label: c.name,
                    description: `${c.type} - ${c.category}`,
                    component: c,
                })), { placeHolder: 'Select component to test' });
                if (!selection)
                    return;
                component = selection.component;
            }
            // Check if FlowMason Studio is running
            const connected = await flowmasonService.checkConnection();
            if (!connected) {
                const startStudio = await vscode.window.showWarningMessage('FlowMason Studio is not running. Start it to test components.', 'Run Locally', 'Cancel');
                if (startStudio === 'Run Locally') {
                    // Run the test locally using Python
                    await runTestLocally(editor.document, component, outputChannel);
                }
                return;
            }
            // Show input panel for test data
            const inputJson = await vscode.window.showInputBox({
                prompt: `Enter test input JSON for ${component.name}`,
                placeHolder: '{"text": "Hello, world!"}',
                value: getDefaultInput(component),
            });
            if (inputJson === undefined)
                return;
            // Parse and validate input
            let input;
            try {
                input = JSON.parse(inputJson);
            }
            catch {
                vscode.window.showErrorMessage('Invalid JSON input');
                return;
            }
            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `Testing ${component.name}...`,
                cancellable: false,
            }, async () => {
                // Execute test
                const result = await flowmasonService.testComponent(component.name, {}, // Config - could be extracted from component
                input);
                outputChannel.appendLine('');
                outputChannel.appendLine(`=== Test: ${component.name} ===`);
                outputChannel.appendLine(`Input: ${JSON.stringify(input, null, 2)}`);
                outputChannel.appendLine('');
                if (result.success) {
                    outputChannel.appendLine('Status: SUCCESS');
                    outputChannel.appendLine(`Output: ${JSON.stringify(result.output, null, 2)}`);
                    if (result.duration_ms) {
                        outputChannel.appendLine(`Duration: ${result.duration_ms}ms`);
                    }
                    if (result.usage) {
                        outputChannel.appendLine(`Tokens: ${JSON.stringify(result.usage)}`);
                    }
                    vscode.window.showInformationMessage(`Test passed for ${component.name}`);
                }
                else {
                    outputChannel.appendLine('Status: FAILED');
                    outputChannel.appendLine(`Error: ${result.error}`);
                    vscode.window.showErrorMessage(`Test failed: ${result.error}`);
                }
                outputChannel.appendLine('');
                outputChannel.show();
            });
        }
        catch (error) {
            outputChannel.appendLine(`Error testing component: ${error}`);
            vscode.window.showErrorMessage(`Failed to test component: ${error}`);
        }
    });
    context.subscriptions.push(command);
}
function getDefaultInput(component) {
    const input = {};
    for (const field of component.inputFields) {
        if (field.default) {
            input[field.name] = field.default;
        }
        else if (field.type.includes('str')) {
            input[field.name] = 'test';
        }
        else if (field.type.includes('int')) {
            input[field.name] = 0;
        }
        else if (field.type.includes('float')) {
            input[field.name] = 0.0;
        }
        else if (field.type.includes('bool')) {
            input[field.name] = false;
        }
        else if (field.type.includes('List')) {
            input[field.name] = [];
        }
        else if (field.type.includes('Dict')) {
            input[field.name] = {};
        }
    }
    return JSON.stringify(input, null, 2);
}
async function runTestLocally(document, component, outputChannel) {
    const config = vscode.workspace.getConfiguration('flowmason');
    const pythonPath = config.get('pythonPath') || 'python';
    // Create a test terminal
    const terminal = vscode.window.createTerminal({
        name: `FlowMason Test: ${component.name}`,
        cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
    });
    terminal.show();
    // Run the file directly (assumes __main__ block exists)
    terminal.sendText(`${pythonPath} "${document.uri.fsPath}"`);
    outputChannel.appendLine(`Running local test for ${component.name}`);
    outputChannel.appendLine(`Command: ${pythonPath} "${document.uri.fsPath}"`);
}
//# sourceMappingURL=testComponent.js.map