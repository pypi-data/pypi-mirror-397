"use strict";
/**
 * Open Docs Command
 *
 * Opens FlowMason documentation.
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
exports.registerOpenDocsCommand = registerOpenDocsCommand;
const vscode = __importStar(require("vscode"));
function registerOpenDocsCommand(context) {
    const command = vscode.commands.registerCommand('flowmason.openDocs', async () => {
        const options = [
            { label: 'Component Development Guide', url: 'docs/component-development-guide.md' },
            { label: 'Package Format', url: 'docs/package-format.md' },
            { label: 'API Reference', url: 'docs/api-reference.md' },
            { label: 'Architecture Rules', url: 'docs/architecture-rules.md' },
            { label: 'Studio User Guide', url: 'docs/studio-user-guide.md' },
        ];
        const selection = await vscode.window.showQuickPick(options, {
            placeHolder: 'Select documentation to open',
        });
        if (!selection)
            return;
        // Try to find the doc in the workspace first
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders) {
            const files = await vscode.workspace.findFiles(`**/${selection.url}`);
            if (files.length > 0) {
                const doc = await vscode.workspace.openTextDocument(files[0]);
                await vscode.window.showTextDocument(doc);
                return;
            }
        }
        // Open online documentation (fallback)
        vscode.window.showInformationMessage(`Documentation: ${selection.label}. Check the docs folder in the FlowMason repository.`);
    });
    context.subscriptions.push(command);
}
//# sourceMappingURL=openDocs.js.map