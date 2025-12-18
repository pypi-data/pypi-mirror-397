"use strict";
/**
 * Private Package Registry Commands
 *
 * Commands for interacting with the organization's private package registry.
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
exports.registerPrivateRegistryCommands = registerPrivateRegistryCommands;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
function registerPrivateRegistryCommands(context, flowmasonService, outputChannel) {
    // Publish to private registry
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.publishToRegistry', async () => {
        // Find .fmpkg file in workspace
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }
        // Find package files
        const packageFiles = await vscode.workspace.findFiles('**/*.fmpkg');
        if (packageFiles.length === 0) {
            // Offer to build first
            const buildFirst = await vscode.window.showWarningMessage('No .fmpkg package files found. Build a package first?', 'Build Package', 'Cancel');
            if (buildFirst === 'Build Package') {
                await vscode.commands.executeCommand('flowmason.buildPackage');
            }
            return;
        }
        // Select package to publish
        const packageItems = packageFiles.map(file => ({
            label: path.basename(file.fsPath),
            description: path.dirname(file.fsPath).replace(workspaceFolder.uri.fsPath, ''),
            uri: file,
        }));
        const selected = await vscode.window.showQuickPick(packageItems, {
            placeHolder: 'Select package to publish',
            title: 'Publish to Private Registry',
        });
        if (!selected) {
            return;
        }
        // Select visibility
        const visibility = await vscode.window.showQuickPick([
            { label: 'Public', description: 'Anyone can download', value: 'public' },
            { label: 'Private', description: 'Only organization members', value: 'private' },
            { label: 'Unlisted', description: 'Anyone with link can download', value: 'unlisted' },
        ], {
            placeHolder: 'Select package visibility',
            title: 'Package Visibility',
        });
        if (!visibility) {
            return;
        }
        // Publish
        outputChannel.show();
        outputChannel.appendLine(`Publishing ${selected.label} to private registry...`);
        try {
            const result = await flowmasonService.publishToPrivateRegistry(selected.uri.fsPath, visibility.value);
            outputChannel.appendLine(`✓ Published ${result.name}@${result.version}`);
            outputChannel.appendLine(`  Visibility: ${result.visibility}`);
            outputChannel.appendLine(`  Components: ${result.components.join(', ')}`);
            vscode.window.showInformationMessage(`Published ${result.name}@${result.version} to private registry`);
        }
        catch (error) {
            outputChannel.appendLine(`✗ Failed to publish: ${error.message}`);
            vscode.window.showErrorMessage(`Failed to publish: ${error.message}`);
        }
    }));
    // Browse private registry
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.browsePrivateRegistry', async () => {
        outputChannel.appendLine('Fetching packages from private registry...');
        try {
            const response = await flowmasonService.listPrivatePackages();
            const packages = response.packages;
            if (packages.length === 0) {
                vscode.window.showInformationMessage('No packages in private registry. Use "FlowMason: Publish to Registry" to add packages.');
                return;
            }
            // Show quick pick with packages
            const items = packages.map(pkg => ({
                label: `${pkg.name}@${pkg.version}`,
                description: `${pkg.visibility} • ${pkg.downloads} downloads`,
                detail: pkg.description || pkg.components.join(', '),
                package: pkg,
            }));
            const selected = await vscode.window.showQuickPick(items, {
                placeHolder: 'Select a package',
                title: `Private Registry (${packages.length} packages)`,
                matchOnDescription: true,
                matchOnDetail: true,
            });
            if (selected) {
                // Show package details or download options
                const action = await vscode.window.showQuickPick([
                    { label: '$(cloud-download) Download', value: 'download' },
                    { label: '$(info) View Details', value: 'details' },
                    { label: '$(versions) View Versions', value: 'versions' },
                ], {
                    placeHolder: `${selected.package.name}@${selected.package.version}`,
                });
                if (action?.value === 'download') {
                    await downloadPackage(selected.package, flowmasonService, outputChannel);
                }
                else if (action?.value === 'details') {
                    showPackageDetails(selected.package);
                }
                else if (action?.value === 'versions') {
                    await showPackageVersions(selected.package.name, flowmasonService);
                }
            }
        }
        catch (error) {
            outputChannel.appendLine(`✗ Failed to fetch packages: ${error.message}`);
            vscode.window.showErrorMessage(`Failed to fetch packages: ${error.message}`);
        }
    }));
    // Download from private registry
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.downloadFromRegistry', async () => {
        // Get package name from user
        const packageName = await vscode.window.showInputBox({
            prompt: 'Enter package name (optionally with @version)',
            placeHolder: 'my-package or my-package@1.0.0',
        });
        if (!packageName) {
            return;
        }
        // Parse name and version
        const [name, version] = packageName.split('@');
        try {
            const pkgInfo = await flowmasonService.getPrivatePackage(name, version);
            await downloadPackage(pkgInfo, flowmasonService, outputChannel);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Package not found: ${packageName}`);
        }
    }));
    // Registry statistics
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.registryStats', async () => {
        try {
            const stats = await flowmasonService.getPrivateRegistryStats();
            const message = [
                `📦 Packages: ${stats.packages_count}`,
                `🧩 Components: ${stats.components_count}`,
                `📊 Total Downloads: ${stats.total_downloads}`,
                `📁 Categories: ${Object.keys(stats.categories || {}).join(', ') || 'None'}`,
            ].join('\n');
            vscode.window.showInformationMessage(message, { modal: true });
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to get stats: ${error.message}`);
        }
    }));
}
async function downloadPackage(pkg, flowmasonService, outputChannel) {
    // Ask where to save
    const saveUri = await vscode.window.showSaveDialog({
        defaultUri: vscode.Uri.file(`${pkg.name}-${pkg.version}.fmpkg`),
        filters: { 'FlowMason Package': ['fmpkg'] },
        title: 'Save Package',
    });
    if (!saveUri) {
        return;
    }
    outputChannel.show();
    outputChannel.appendLine(`Downloading ${pkg.name}@${pkg.version}...`);
    try {
        const content = await flowmasonService.downloadPrivatePackage(pkg.name, pkg.version);
        // Write to file
        fs.writeFileSync(saveUri.fsPath, content);
        outputChannel.appendLine(`✓ Downloaded to ${saveUri.fsPath}`);
        vscode.window.showInformationMessage(`Downloaded ${pkg.name}@${pkg.version}`);
        // Ask to install
        const install = await vscode.window.showQuickPick(['Yes, install now', 'No, just download'], { placeHolder: 'Install the package to your project?' });
        if (install === 'Yes, install now') {
            await vscode.commands.executeCommand('flowmason.importPackage', saveUri);
        }
    }
    catch (error) {
        outputChannel.appendLine(`✗ Download failed: ${error.message}`);
        vscode.window.showErrorMessage(`Download failed: ${error.message}`);
    }
}
function showPackageDetails(pkg) {
    const panel = vscode.window.createWebviewPanel('flowmasonPackageDetails', `${pkg.name}@${pkg.version}`, vscode.ViewColumn.One, { enableScripts: false });
    panel.webview.html = `<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
        }
        h1 { margin-bottom: 5px; }
        .version { color: var(--vscode-descriptionForeground); margin-bottom: 20px; }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 8px;
        }
        .badge-public { background: #22c55e; color: white; }
        .badge-private { background: #f97316; color: white; }
        .badge-unlisted { background: #6366f1; color: white; }
        .section { margin: 20px 0; }
        .section-title { font-weight: bold; margin-bottom: 8px; }
        .tag {
            display: inline-block;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 2px 8px;
            border-radius: 10px;
            margin-right: 6px;
            font-size: 11px;
        }
        ul { margin: 0; padding-left: 20px; }
    </style>
</head>
<body>
    <h1>${escapeHtml(pkg.name)}</h1>
    <div class="version">v${escapeHtml(pkg.version)}</div>

    <span class="badge badge-${pkg.visibility}">${pkg.visibility}</span>
    ${pkg.category ? `<span class="badge">${escapeHtml(pkg.category)}</span>` : ''}

    ${pkg.description ? `<div class="section"><p>${escapeHtml(pkg.description)}</p></div>` : ''}

    <div class="section">
        <div class="section-title">Components (${pkg.components.length})</div>
        <ul>
            ${pkg.components.map(c => `<li>${escapeHtml(c)}</li>`).join('')}
        </ul>
    </div>

    ${pkg.tags.length > 0 ? `
        <div class="section">
            <div class="section-title">Tags</div>
            ${pkg.tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
        </div>
    ` : ''}

    <div class="section">
        <div class="section-title">Statistics</div>
        <p>📊 Downloads: ${pkg.downloads}</p>
        ${pkg.author ? `<p>👤 Author: ${escapeHtml(pkg.author)}</p>` : ''}
    </div>
</body>
</html>`;
}
async function showPackageVersions(name, flowmasonService) {
    try {
        const versionsResp = await flowmasonService.getPrivatePackageVersions(name);
        const selected = await vscode.window.showQuickPick(versionsResp.versions.map(v => ({
            label: v,
            description: v === versionsResp.latest ? '(latest)' : '',
        })), { placeHolder: `Versions of ${name}` });
        if (selected) {
            vscode.window.showInformationMessage(`Selected ${name}@${selected.label}`);
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to get versions: ${error.message}`);
    }
}
function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
//# sourceMappingURL=privateRegistry.js.map