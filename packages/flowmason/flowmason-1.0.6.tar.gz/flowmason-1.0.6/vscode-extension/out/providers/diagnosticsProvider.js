"use strict";
/**
 * FlowMason Diagnostics Provider
 *
 * Provides linting and error detection for FlowMason components.
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
exports.FlowMasonDiagnosticsProvider = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Create a diagnostic with the flowmason source
 */
function createDiagnostic(range, message, severity) {
    const diag = new vscode.Diagnostic(range, message, severity);
    diag.source = 'flowmason';
    return diag;
}
class FlowMasonDiagnosticsProvider {
    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('flowmason');
        this.rules = this.createRules();
    }
    activate(context) {
        // Run diagnostics on active editor
        if (vscode.window.activeTextEditor) {
            this.updateDiagnostics(vscode.window.activeTextEditor.document);
        }
        // Run diagnostics when document changes
        context.subscriptions.push(vscode.workspace.onDidChangeTextDocument(e => {
            if (e.document.languageId === 'python') {
                this.updateDiagnostics(e.document);
            }
        }));
        // Run diagnostics when active editor changes
        context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor && editor.document.languageId === 'python') {
                this.updateDiagnostics(editor.document);
            }
        }));
        // Clear diagnostics when document is closed
        context.subscriptions.push(vscode.workspace.onDidCloseTextDocument(doc => {
            this.diagnosticCollection.delete(doc.uri);
        }));
        context.subscriptions.push(this.diagnosticCollection);
    }
    updateDiagnostics(document) {
        if (document.languageId !== 'python') {
            return;
        }
        const text = document.getText();
        // Only analyze FlowMason component files
        if (!this.isFlowMasonFile(text)) {
            this.diagnosticCollection.delete(document.uri);
            return;
        }
        const diagnostics = [];
        // Check each line against rules
        for (let lineNum = 0; lineNum < document.lineCount; lineNum++) {
            const line = document.lineAt(lineNum);
            for (const rule of this.rules) {
                const match = line.text.match(rule.pattern);
                if (match) {
                    const diagnostic = rule.check(match, document, lineNum);
                    if (diagnostic) {
                        diagnostics.push(diagnostic);
                    }
                }
            }
        }
        // Run document-wide checks
        diagnostics.push(...this.runDocumentChecks(document, text));
        this.diagnosticCollection.set(document.uri, diagnostics);
    }
    isFlowMasonFile(text) {
        return text.includes('@node') ||
            text.includes('@operator') ||
            text.includes('from flowmason') ||
            text.includes('BaseNode') ||
            text.includes('BaseOperator');
    }
    createRules() {
        return [
            // Check for missing name in decorator
            {
                pattern: /@(node|operator)\s*\(\s*\)/,
                check: (match, document, line) => {
                    const range = new vscode.Range(line, 0, line, document.lineAt(line).text.length);
                    return createDiagnostic(range, `@${match[1]} decorator requires at least a 'name' parameter`, vscode.DiagnosticSeverity.Error);
                }
            },
            // Check for non-kebab-case name
            {
                pattern: /@(node|operator)\s*\(\s*name\s*=\s*["']([^"']+)["']/,
                check: (match, document, line) => {
                    const name = match[2];
                    if (!/^[a-z][a-z0-9-]*$/.test(name)) {
                        const startCol = document.lineAt(line).text.indexOf(name);
                        const range = new vscode.Range(line, startCol, line, startCol + name.length);
                        return createDiagnostic(range, `Component name '${name}' should be kebab-case (lowercase letters, numbers, hyphens)`, vscode.DiagnosticSeverity.Warning);
                    }
                    return null;
                }
            },
            // Check for missing Input class
            {
                pattern: /class\s+(\w+)\s*\(\s*Base(Node|Operator)\s*\)/,
                check: (match, document, line) => {
                    const className = match[1];
                    const text = document.getText();
                    // Check if there's an Input class defined before this class
                    const classPos = document.offsetAt(new vscode.Position(line, 0));
                    const textBefore = text.substring(0, classPos);
                    if (!textBefore.includes('class Input')) {
                        const range = new vscode.Range(line, 0, line, document.lineAt(line).text.length);
                        return createDiagnostic(range, `Component '${className}' should have an Input class defined`, vscode.DiagnosticSeverity.Warning);
                    }
                    return null;
                }
            },
            // Check for missing Output class
            {
                pattern: /class\s+(\w+)\s*\(\s*Base(Node|Operator)\s*\)/,
                check: (match, document, line) => {
                    const className = match[1];
                    const text = document.getText();
                    // Check if there's an Output class defined before this class
                    const classPos = document.offsetAt(new vscode.Position(line, 0));
                    const textBefore = text.substring(0, classPos);
                    if (!textBefore.includes('class Output')) {
                        const range = new vscode.Range(line, 0, line, document.lineAt(line).text.length);
                        return createDiagnostic(range, `Component '${className}' should have an Output class defined`, vscode.DiagnosticSeverity.Warning);
                    }
                    return null;
                }
            },
            // Check for async execute without await
            {
                pattern: /async\s+def\s+execute\s*\(/,
                check: (match, document, line) => {
                    // Look ahead to find the function body and check for await
                    let hasAwait = false;
                    let inFunction = false;
                    for (let i = line; i < Math.min(line + 50, document.lineCount); i++) {
                        const lineText = document.lineAt(i).text;
                        if (i === line) {
                            inFunction = true;
                            continue;
                        }
                        if (!inFunction)
                            continue;
                        // Check for await
                        if (lineText.includes('await ')) {
                            hasAwait = true;
                            break;
                        }
                        // Check for end of function (next def/class at same or lower indentation)
                        if (/^(class |def |@)/.test(lineText.trim()) && !lineText.startsWith('        ')) {
                            break;
                        }
                    }
                    if (!hasAwait) {
                        const range = new vscode.Range(line, 0, line, document.lineAt(line).text.length);
                        return createDiagnostic(range, 'Async execute method should contain at least one await expression', vscode.DiagnosticSeverity.Information);
                    }
                    return null;
                }
            },
            // Check for hardcoded API keys
            {
                pattern: /(api_key|apikey|secret|password|token)\s*=\s*["'][^"']{10,}["']/i,
                check: (match, document, line) => {
                    const range = new vscode.Range(line, 0, line, document.lineAt(line).text.length);
                    return createDiagnostic(range, 'Possible hardcoded secret detected. Use environment variables instead.', vscode.DiagnosticSeverity.Warning);
                }
            },
            // Check for missing description in decorator
            {
                pattern: /@(node|operator)\s*\([^)]*\)/,
                check: (match, document, line) => {
                    const decoratorText = match[0];
                    if (!decoratorText.includes('description')) {
                        const range = new vscode.Range(line, 0, line, document.lineAt(line).text.length);
                        return createDiagnostic(range, 'Consider adding a description to your component', vscode.DiagnosticSeverity.Hint);
                    }
                    return null;
                }
            },
            // Check for Field without description
            {
                pattern: /:\s*\w+\s*=\s*Field\s*\([^)]*\)/,
                check: (match, document, line) => {
                    const fieldText = match[0];
                    if (!fieldText.includes('description')) {
                        const startCol = document.lineAt(line).text.indexOf('Field');
                        const range = new vscode.Range(line, startCol, line, startCol + 5);
                        return createDiagnostic(range, 'Consider adding a description to this field', vscode.DiagnosticSeverity.Hint);
                    }
                    return null;
                }
            }
        ];
    }
    runDocumentChecks(document, text) {
        const diagnostics = [];
        // Check for decorator without corresponding class
        const decoratorMatches = text.matchAll(/@(node|operator)\s*\([^)]*\)\s*\n\s*class\s+(\w+)/g);
        const classMatches = text.matchAll(/class\s+(\w+)\s*\(\s*Base(Node|Operator)\s*\)/g);
        const decoratedClasses = new Set();
        const baseClasses = new Map();
        for (const match of decoratorMatches) {
            decoratedClasses.add(match[2]);
        }
        for (const match of classMatches) {
            const className = match[1];
            const line = document.positionAt(match.index || 0).line;
            baseClasses.set(className, line);
        }
        // Find classes that extend Base* but don't have decorator
        for (const [className, line] of baseClasses) {
            if (!decoratedClasses.has(className)) {
                const range = new vscode.Range(line, 0, line, document.lineAt(line).text.length);
                diagnostics.push(createDiagnostic(range, `Class '${className}' extends BaseNode/BaseOperator but is missing @node/@operator decorator`, vscode.DiagnosticSeverity.Error));
            }
        }
        // Check for execute method signature
        const executeMatch = text.match(/def\s+execute\s*\(\s*self\s*,\s*(\w+)\s*:/);
        if (executeMatch) {
            const paramName = executeMatch[1];
            if (paramName !== 'input' && paramName !== 'inputs') {
                const line = document.positionAt(executeMatch.index || 0).line;
                const range = new vscode.Range(line, 0, line, document.lineAt(line).text.length);
                diagnostics.push(createDiagnostic(range, `Execute method parameter should be named 'input' or 'inputs', found '${paramName}'`, vscode.DiagnosticSeverity.Information));
            }
        }
        // Check for return type annotation on execute
        const executeReturnMatch = text.match(/def\s+execute\s*\([^)]+\)\s*(->\s*\w+)?:/);
        if (executeReturnMatch && !executeReturnMatch[1]) {
            const line = document.positionAt(executeReturnMatch.index || 0).line;
            const range = new vscode.Range(line, 0, line, document.lineAt(line).text.length);
            diagnostics.push(createDiagnostic(range, 'Consider adding return type annotation to execute method (-> Output)', vscode.DiagnosticSeverity.Hint));
        }
        return diagnostics;
    }
    dispose() {
        this.diagnosticCollection.dispose();
    }
}
exports.FlowMasonDiagnosticsProvider = FlowMasonDiagnosticsProvider;
//# sourceMappingURL=diagnosticsProvider.js.map