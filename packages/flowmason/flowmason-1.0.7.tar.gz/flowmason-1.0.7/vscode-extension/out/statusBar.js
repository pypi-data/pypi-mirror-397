"use strict";
/**
 * FlowMason Status Bar
 *
 * Shows Studio status and provides quick actions for start/stop/restart.
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
exports.createStudioStatusBar = createStudioStatusBar;
const vscode = __importStar(require("vscode"));
const installation_1 = require("./types/installation");
function createStudioStatusBar(context) {
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    // Initial state
    statusBarItem.text = '$(loading~spin) FlowMason';
    statusBarItem.tooltip = 'Checking FlowMason Studio status...';
    statusBarItem.command = 'flowmason.studioQuickPick';
    statusBarItem.show();
    // Register the quick pick command
    const quickPickCommand = vscode.commands.registerCommand('flowmason.studioQuickPick', async () => {
        const backendRunning = await (0, installation_1.isBackendRunning)();
        const frontendPort = (0, installation_1.getFrontendPort)();
        const backendPort = (0, installation_1.getBackendPort)();
        const items = [];
        if (backendRunning) {
            items.push({ label: '$(browser) Open Frontend', description: `http://127.0.0.1:${frontendPort}` }, { label: '$(link-external) Open API Docs', description: `http://127.0.0.1:${backendPort}/docs` }, { label: '$(debug-restart) Restart Studio', description: 'Stop and start Studio' }, { label: '$(stop-circle) Stop Studio', description: 'Stop both backend and frontend' });
        }
        else {
            items.push({ label: '$(play) Start Studio', description: 'Start backend and frontend servers' });
        }
        items.push({ label: '$(info) Show Status', description: 'View detailed Studio status' });
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'FlowMason Studio Actions'
        });
        if (selected) {
            switch (selected.label) {
                case '$(browser) Open Frontend':
                    vscode.env.openExternal(vscode.Uri.parse(`http://127.0.0.1:${frontendPort}`));
                    break;
                case '$(link-external) Open API Docs':
                    vscode.env.openExternal(vscode.Uri.parse(`http://127.0.0.1:${backendPort}/docs`));
                    break;
                case '$(play) Start Studio':
                    vscode.commands.executeCommand('flowmason.startStudio');
                    break;
                case '$(debug-restart) Restart Studio':
                    vscode.commands.executeCommand('flowmason.restartStudio');
                    break;
                case '$(stop-circle) Stop Studio':
                    vscode.commands.executeCommand('flowmason.stopStudio');
                    break;
                case '$(info) Show Status':
                    vscode.commands.executeCommand('flowmason.studioStatus');
                    break;
            }
        }
    });
    context.subscriptions.push(quickPickCommand);
    context.subscriptions.push(statusBarItem);
    // Function to update status
    async function updateStatus() {
        const running = await (0, installation_1.isBackendRunning)();
        if (running) {
            statusBarItem.text = '$(check) FlowMason';
            statusBarItem.tooltip = 'FlowMason Studio is running - Click for actions';
            statusBarItem.backgroundColor = undefined;
        }
        else {
            statusBarItem.text = '$(circle-slash) FlowMason';
            statusBarItem.tooltip = 'FlowMason Studio is stopped - Click to start';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        }
    }
    // Initial update
    updateStatus();
    // Periodic update every 10 seconds
    const interval = setInterval(updateStatus, 10000);
    context.subscriptions.push({ dispose: () => clearInterval(interval) });
    return statusBarItem;
}
//# sourceMappingURL=statusBar.js.map