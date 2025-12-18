"use strict";
/**
 * Development Webhook Server
 *
 * A built-in webhook server for testing pipeline output_config during development.
 * Received payloads are displayed in the VSCode Output panel.
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
exports.WebhookServer = void 0;
exports.registerWebhookServer = registerWebhookServer;
const vscode = __importStar(require("vscode"));
const http = __importStar(require("http"));
class WebhookServer {
    constructor(context) {
        this.context = context;
        this.server = null;
        this.requestCount = 0;
        this.payloads = [];
        this.maxPayloads = 100;
        this.outputChannel = vscode.window.createOutputChannel('FlowMason Webhook');
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 99);
        this.statusBarItem.command = 'flowmason.toggleWebhookServer';
        this.port = vscode.workspace.getConfiguration('flowmason').get('webhookPort', 9999);
        this.updateStatusBar();
    }
    get isRunning() {
        return this.server !== null;
    }
    get serverUrl() {
        return `http://localhost:${this.port}`;
    }
    async start() {
        if (this.server) {
            vscode.window.showWarningMessage('Webhook server is already running');
            return;
        }
        return new Promise((resolve, reject) => {
            this.server = http.createServer((req, res) => {
                this.handleRequest(req, res);
            });
            this.server.on('error', (err) => {
                if (err.code === 'EADDRINUSE') {
                    vscode.window.showErrorMessage(`Port ${this.port} is already in use. Change flowmason.webhookPort in settings.`);
                }
                else {
                    vscode.window.showErrorMessage(`Webhook server error: ${err.message}`);
                }
                this.server = null;
                this.updateStatusBar();
                reject(err);
            });
            this.server.listen(this.port, () => {
                this.requestCount = 0;
                this.payloads = [];
                this.outputChannel.clear();
                this.outputChannel.appendLine('='.repeat(60));
                this.outputChannel.appendLine('FlowMason Development Webhook Server');
                this.outputChannel.appendLine('='.repeat(60));
                this.outputChannel.appendLine(`Started at: ${new Date().toISOString()}`);
                this.outputChannel.appendLine(`Listening on: ${this.serverUrl}`);
                this.outputChannel.appendLine('');
                this.outputChannel.appendLine('Endpoints:');
                this.outputChannel.appendLine(`  POST ${this.serverUrl}/webhook  - Receive pipeline output`);
                this.outputChannel.appendLine(`  GET  ${this.serverUrl}/raw      - View raw JSON payloads`);
                this.outputChannel.appendLine(`  GET  ${this.serverUrl}/view     - View formatted webpage`);
                this.outputChannel.appendLine('');
                this.outputChannel.appendLine('Configure your pipeline output_config with:');
                this.outputChannel.appendLine(`  "url": "${this.serverUrl}/webhook"`);
                this.outputChannel.appendLine('');
                this.outputChannel.appendLine('Waiting for webhooks...');
                this.outputChannel.appendLine('-'.repeat(60));
                this.outputChannel.show(true);
                this.updateStatusBar();
                vscode.window.showInformationMessage(`Webhook server started on ${this.serverUrl}`);
                resolve();
            });
        });
    }
    async stop() {
        if (!this.server) {
            return;
        }
        return new Promise((resolve) => {
            this.server.close(() => {
                this.outputChannel.appendLine('');
                this.outputChannel.appendLine('-'.repeat(60));
                this.outputChannel.appendLine(`Server stopped at: ${new Date().toISOString()}`);
                this.outputChannel.appendLine(`Total requests received: ${this.requestCount}`);
                this.server = null;
                this.updateStatusBar();
                vscode.window.showInformationMessage('Webhook server stopped');
                resolve();
            });
        });
    }
    async toggle() {
        if (this.isRunning) {
            await this.stop();
        }
        else {
            await this.start();
        }
    }
    handleRequest(req, res) {
        const url = req.url || '/';
        const method = req.method || 'GET';
        // Route GET requests for viewing
        if (method === 'GET') {
            if (url === '/raw' || url === '/raw/') {
                this.handleRawView(req, res);
                return;
            }
            if (url === '/view' || url === '/view/') {
                this.handleWebView(req, res);
                return;
            }
            if (url === '/clear' || url === '/clear/') {
                this.handleClear(req, res);
                return;
            }
            if (url === '/' || url === '') {
                // Redirect root to view
                res.writeHead(302, { 'Location': '/view' });
                res.end();
                return;
            }
        }
        // Handle webhook POST
        let body = '';
        req.on('data', (chunk) => {
            body += chunk.toString();
        });
        req.on('end', () => {
            this.requestCount++;
            // Parse body
            let parsedBody = body;
            const contentType = req.headers['content-type'] || '';
            if (contentType.includes('application/json') && body) {
                try {
                    parsedBody = JSON.parse(body);
                }
                catch {
                    // Keep as string if not valid JSON
                }
            }
            // Create payload record
            const payload = {
                id: this.requestCount,
                timestamp: new Date().toISOString(),
                method: method,
                path: url,
                headers: req.headers,
                body: parsedBody,
            };
            // Store payload (keep last N)
            this.payloads.unshift(payload);
            if (this.payloads.length > this.maxPayloads) {
                this.payloads.pop();
            }
            // Log to output channel
            this.logPayload(payload);
            // Send response
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'received',
                request_id: this.requestCount,
                timestamp: payload.timestamp,
            }));
        });
        req.on('error', (err) => {
            this.outputChannel.appendLine(`[ERROR] Request error: ${err.message}`);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        });
    }
    handleRawView(req, res) {
        res.writeHead(200, {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        });
        res.end(JSON.stringify({
            server: 'FlowMason Webhook Server',
            total_received: this.requestCount,
            payloads: this.payloads
        }, null, 2));
    }
    handleClear(req, res) {
        this.payloads = [];
        this.outputChannel.appendLine('');
        this.outputChannel.appendLine('[INFO] Payloads cleared');
        this.outputChannel.appendLine('-'.repeat(60));
        res.writeHead(302, { 'Location': '/view' });
        res.end();
    }
    handleWebView(req, res) {
        const html = this.generateWebViewHtml();
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(html);
    }
    generateWebViewHtml() {
        const payloadCards = this.payloads.map(p => `
            <div class="card">
                <div class="card-header">
                    <span class="badge">#${p.id}</span>
                    <span class="method ${p.method.toLowerCase()}">${p.method}</span>
                    <span class="path">${this.escapeHtml(p.path)}</span>
                    <span class="timestamp">${p.timestamp}</span>
                </div>
                <div class="card-body">
                    <div class="section">
                        <div class="section-title">Headers</div>
                        <pre class="headers">${this.escapeHtml(this.formatHeaders(p.headers))}</pre>
                    </div>
                    <div class="section">
                        <div class="section-title">Body</div>
                        <pre class="body">${this.escapeHtml(typeof p.body === 'object' ? JSON.stringify(p.body, null, 2) : String(p.body || '(empty)'))}</pre>
                    </div>
                </div>
            </div>
        `).join('');
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="5">
    <title>FlowMason Webhook Viewer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #30363d;
        }
        h1 {
            font-size: 24px;
            font-weight: 600;
            color: #f0f6fc;
        }
        .logo { color: #58a6ff; }
        .stats {
            display: flex;
            gap: 16px;
            align-items: center;
        }
        .stat {
            background: #161b22;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
        }
        .stat-value { color: #58a6ff; font-weight: 600; }
        .actions {
            display: flex;
            gap: 8px;
        }
        .btn {
            padding: 8px 16px;
            border-radius: 6px;
            border: 1px solid #30363d;
            background: #21262d;
            color: #c9d1d9;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .btn:hover { background: #30363d; }
        .btn-danger { border-color: #f85149; color: #f85149; }
        .btn-danger:hover { background: #f8514922; }
        .empty {
            text-align: center;
            padding: 60px 20px;
            color: #8b949e;
        }
        .empty-icon { font-size: 48px; margin-bottom: 16px; }
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
        }
        .card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: #21262d;
            border-bottom: 1px solid #30363d;
            flex-wrap: wrap;
        }
        .badge {
            background: #388bfd;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .method {
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .method.post { background: #238636; color: white; }
        .method.get { background: #1f6feb; color: white; }
        .method.put { background: #9e6a03; color: white; }
        .method.delete { background: #da3633; color: white; }
        .path { color: #8b949e; font-family: monospace; font-size: 13px; }
        .timestamp { margin-left: auto; color: #8b949e; font-size: 12px; }
        .card-body { padding: 16px; }
        .section { margin-bottom: 16px; }
        .section:last-child { margin-bottom: 0; }
        .section-title {
            font-size: 12px;
            font-weight: 600;
            color: #8b949e;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        pre {
            background: #0d1117;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        }
        .headers { color: #8b949e; }
        .body { color: #7ee787; }
        .auto-refresh {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #21262d;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            color: #8b949e;
            border: 1px solid #30363d;
        }
        @media (max-width: 600px) {
            .timestamp { display: none; }
            .card-header { gap: 8px; }
        }
    </style>
</head>
<body>
    <header>
        <h1><span class="logo">◆</span> FlowMason Webhook Viewer</h1>
        <div class="stats">
            <div class="stat">Received: <span class="stat-value">${this.requestCount}</span></div>
            <div class="stat">Stored: <span class="stat-value">${this.payloads.length}</span></div>
        </div>
        <div class="actions">
            <a href="/raw" class="btn">{ } Raw JSON</a>
            <a href="/clear" class="btn btn-danger">Clear All</a>
        </div>
    </header>
    <main>
        ${this.payloads.length === 0 ? `
            <div class="empty">
                <div class="empty-icon">📭</div>
                <h2>No webhooks received yet</h2>
                <p style="margin-top: 8px;">Configure your pipeline to POST to:</p>
                <code style="display: block; margin-top: 12px; padding: 12px; background: #161b22; border-radius: 6px;">${this.serverUrl}/webhook</code>
            </div>
        ` : payloadCards}
    </main>
    <div class="auto-refresh">Auto-refresh: 5s</div>
</body>
</html>`;
    }
    formatHeaders(headers) {
        const relevantHeaders = [
            'content-type',
            'x-flowmason-run-id',
            'x-flowmason-pipeline',
            'x-flowmason-stage',
            'user-agent'
        ];
        const lines = [];
        for (const [key, value] of Object.entries(headers)) {
            if (relevantHeaders.includes(key.toLowerCase()) || key.startsWith('x-')) {
                lines.push(`${key}: ${value}`);
            }
        }
        return lines.length > 0 ? lines.join('\n') : '(none)';
    }
    escapeHtml(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
    logPayload(payload) {
        this.outputChannel.appendLine('');
        this.outputChannel.appendLine(`[#${payload.id}] ${payload.timestamp}`);
        this.outputChannel.appendLine(`${payload.method} ${payload.path}`);
        // Log relevant headers
        const relevantHeaders = ['content-type', 'x-flowmason-run-id', 'x-flowmason-pipeline', 'user-agent'];
        const headerLines = [];
        for (const header of relevantHeaders) {
            if (payload.headers[header]) {
                headerLines.push(`  ${header}: ${payload.headers[header]}`);
            }
        }
        if (headerLines.length > 0) {
            this.outputChannel.appendLine('Headers:');
            headerLines.forEach(line => this.outputChannel.appendLine(line));
        }
        // Log body
        this.outputChannel.appendLine('Body:');
        if (typeof payload.body === 'object') {
            const formatted = JSON.stringify(payload.body, null, 2);
            formatted.split('\n').forEach(line => {
                this.outputChannel.appendLine(`  ${line}`);
            });
        }
        else if (payload.body) {
            this.outputChannel.appendLine(`  ${payload.body}`);
        }
        else {
            this.outputChannel.appendLine('  (empty)');
        }
        this.outputChannel.appendLine('-'.repeat(60));
        // Update status bar with count
        this.updateStatusBar();
    }
    updateStatusBar() {
        if (this.isRunning) {
            this.statusBarItem.text = `$(radio-tower) Webhook: ${this.port} (${this.requestCount})`;
            this.statusBarItem.tooltip = `Webhook server running on port ${this.port}\n${this.requestCount} requests received\nClick to stop`;
            this.statusBarItem.backgroundColor = undefined;
        }
        else {
            this.statusBarItem.text = '$(radio-tower) Webhook: Off';
            this.statusBarItem.tooltip = 'Click to start webhook server';
            this.statusBarItem.backgroundColor = undefined;
        }
        this.statusBarItem.show();
    }
    copyUrl() {
        const url = `${this.serverUrl}/webhook`;
        vscode.env.clipboard.writeText(url);
        vscode.window.showInformationMessage(`Copied: ${url}`);
    }
    dispose() {
        if (this.server) {
            this.server.close();
        }
        this.outputChannel.dispose();
        this.statusBarItem.dispose();
    }
}
exports.WebhookServer = WebhookServer;
/**
 * Register webhook server commands
 */
function registerWebhookServer(context) {
    const server = new WebhookServer(context);
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.startWebhookServer', () => server.start()), vscode.commands.registerCommand('flowmason.stopWebhookServer', () => server.stop()), vscode.commands.registerCommand('flowmason.toggleWebhookServer', () => server.toggle()), vscode.commands.registerCommand('flowmason.copyWebhookUrl', () => server.copyUrl()));
    // Cleanup on deactivate
    context.subscriptions.push({
        dispose: () => server.dispose()
    });
    return server;
}
//# sourceMappingURL=webhookServer.js.map