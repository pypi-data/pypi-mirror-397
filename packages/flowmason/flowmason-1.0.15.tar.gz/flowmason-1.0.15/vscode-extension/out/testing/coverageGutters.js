"use strict";
/**
 * FlowMason Coverage Gutters
 *
 * Provides visual coverage indicators in the editor gutter for pipeline files.
 * Shows which stages were executed during test runs with color-coded indicators.
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
exports.CoverageGuttersProvider = void 0;
exports.getCoverageGuttersProvider = getCoverageGuttersProvider;
exports.registerCoverageCommands = registerCoverageCommands;
const vscode = __importStar(require("vscode"));
/**
 * Coverage Gutters Provider
 *
 * Manages coverage decorations in the editor gutter.
 */
class CoverageGuttersProvider {
    constructor() {
        this.coverageData = new Map();
        this.disposables = [];
        this.enabled = true;
        // Create decoration types with gutter icons and line highlighting
        this.executedDecoration = vscode.window.createTextEditorDecorationType({
            gutterIconPath: this.createGutterIcon('#22c55e'), // Green
            gutterIconSize: 'contain',
            overviewRulerColor: '#22c55e',
            overviewRulerLane: vscode.OverviewRulerLane.Left,
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            isWholeLine: true,
        });
        this.failedDecoration = vscode.window.createTextEditorDecorationType({
            gutterIconPath: this.createGutterIcon('#ef4444'), // Red
            gutterIconSize: 'contain',
            overviewRulerColor: '#ef4444',
            overviewRulerLane: vscode.OverviewRulerLane.Left,
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            isWholeLine: true,
        });
        this.skippedDecoration = vscode.window.createTextEditorDecorationType({
            gutterIconPath: this.createGutterIcon('#f59e0b'), // Amber
            gutterIconSize: 'contain',
            overviewRulerColor: '#f59e0b',
            overviewRulerLane: vscode.OverviewRulerLane.Left,
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            isWholeLine: true,
        });
        this.notCoveredDecoration = vscode.window.createTextEditorDecorationType({
            gutterIconPath: this.createGutterIcon('#6b7280'), // Gray
            gutterIconSize: 'contain',
            overviewRulerColor: '#6b7280',
            overviewRulerLane: vscode.OverviewRulerLane.Left,
            backgroundColor: 'rgba(107, 114, 128, 0.05)',
            isWholeLine: true,
        });
        // Listen for editor changes
        this.disposables.push(vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor) {
                this.updateDecorations(editor);
            }
        }));
        // Listen for document changes
        this.disposables.push(vscode.workspace.onDidChangeTextDocument(event => {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document === event.document) {
                // Clear coverage on edit (it's now stale)
                this.clearCoverage(event.document.uri.fsPath);
            }
        }));
        // Update decorations for current editor
        if (vscode.window.activeTextEditor) {
            this.updateDecorations(vscode.window.activeTextEditor);
        }
    }
    /**
     * Create a simple colored circle icon for the gutter
     */
    createGutterIcon(color) {
        // Use a data URI for the SVG icon
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="5" fill="${color}"/>
        </svg>`;
        const encoded = Buffer.from(svg).toString('base64');
        return vscode.Uri.parse(`data:image/svg+xml;base64,${encoded}`);
    }
    /**
     * Update coverage data for a file
     */
    updateCoverage(filePath, stages) {
        const stageMap = new Map();
        let executed = 0;
        let failed = 0;
        let skipped = 0;
        for (const stage of stages) {
            stageMap.set(stage.stageId, {
                stageId: stage.stageId,
                status: stage.status,
                executionCount: stage.executionCount || 1,
                lastDuration: stage.duration,
                errorMessage: stage.error,
            });
            switch (stage.status) {
                case 'executed':
                    executed++;
                    break;
                case 'failed':
                    failed++;
                    break;
                case 'skipped':
                    skipped++;
                    break;
            }
        }
        const total = stages.length;
        const coverage = {
            filePath,
            stages: stageMap,
            summary: {
                total,
                executed,
                failed,
                skipped,
                coveragePercent: total > 0 ? ((executed + failed) / total) * 100 : 0,
            },
            timestamp: new Date(),
        };
        this.coverageData.set(filePath, coverage);
        // Update decorations if this file is currently open
        const editor = vscode.window.visibleTextEditors.find(e => e.document.uri.fsPath === filePath);
        if (editor) {
            this.updateDecorations(editor);
        }
    }
    /**
     * Clear coverage data for a file
     */
    clearCoverage(filePath) {
        this.coverageData.delete(filePath);
        const editor = vscode.window.visibleTextEditors.find(e => e.document.uri.fsPath === filePath);
        if (editor) {
            this.clearDecorations(editor);
        }
    }
    /**
     * Clear all coverage data
     */
    clearAllCoverage() {
        this.coverageData.clear();
        for (const editor of vscode.window.visibleTextEditors) {
            this.clearDecorations(editor);
        }
    }
    /**
     * Toggle coverage display
     */
    toggle() {
        this.enabled = !this.enabled;
        if (this.enabled) {
            if (vscode.window.activeTextEditor) {
                this.updateDecorations(vscode.window.activeTextEditor);
            }
        }
        else {
            for (const editor of vscode.window.visibleTextEditors) {
                this.clearDecorations(editor);
            }
        }
    }
    /**
     * Update decorations for an editor
     */
    updateDecorations(editor) {
        if (!this.enabled) {
            return;
        }
        const filePath = editor.document.uri.fsPath;
        // Only show coverage for pipeline files
        if (!filePath.endsWith('.pipeline.json')) {
            return;
        }
        const coverage = this.coverageData.get(filePath);
        if (!coverage) {
            this.clearDecorations(editor);
            return;
        }
        // Parse pipeline to get stage line numbers
        const stageLines = this.getStageLineNumbers(editor.document);
        const executedRanges = [];
        const failedRanges = [];
        const skippedRanges = [];
        const notCoveredRanges = [];
        for (const [stageId, lineRange] of stageLines) {
            const stageCoverage = coverage.stages.get(stageId);
            const hoverMessage = this.createHoverMessage(stageId, stageCoverage);
            const decoration = {
                range: lineRange,
                hoverMessage,
            };
            if (!stageCoverage) {
                notCoveredRanges.push(decoration);
            }
            else {
                switch (stageCoverage.status) {
                    case 'executed':
                        executedRanges.push(decoration);
                        break;
                    case 'failed':
                        failedRanges.push(decoration);
                        break;
                    case 'skipped':
                        skippedRanges.push(decoration);
                        break;
                    case 'not_covered':
                        notCoveredRanges.push(decoration);
                        break;
                }
            }
        }
        editor.setDecorations(this.executedDecoration, executedRanges);
        editor.setDecorations(this.failedDecoration, failedRanges);
        editor.setDecorations(this.skippedDecoration, skippedRanges);
        editor.setDecorations(this.notCoveredDecoration, notCoveredRanges);
    }
    /**
     * Clear decorations from an editor
     */
    clearDecorations(editor) {
        editor.setDecorations(this.executedDecoration, []);
        editor.setDecorations(this.failedDecoration, []);
        editor.setDecorations(this.skippedDecoration, []);
        editor.setDecorations(this.notCoveredDecoration, []);
    }
    /**
     * Get line numbers for each stage in a pipeline file
     */
    getStageLineNumbers(document) {
        const stageLines = new Map();
        try {
            const content = document.getText();
            const lines = content.split('\n');
            let inStages = false;
            let braceCount = 0;
            let currentStageId = null;
            let stageStartLine = -1;
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const trimmed = line.trim();
                // Track when we enter the stages array
                if (trimmed.includes('"stages"') && trimmed.includes('[')) {
                    inStages = true;
                    continue;
                }
                if (!inStages)
                    continue;
                // Track brace depth
                for (const char of line) {
                    if (char === '{') {
                        braceCount++;
                        if (braceCount === 1) {
                            stageStartLine = i;
                        }
                    }
                    else if (char === '}') {
                        braceCount--;
                        if (braceCount === 0 && currentStageId) {
                            // End of stage object
                            stageLines.set(currentStageId, new vscode.Range(new vscode.Position(stageStartLine, 0), new vscode.Position(i, line.length)));
                            currentStageId = null;
                            stageStartLine = -1;
                        }
                    }
                }
                // Look for stage ID
                const idMatch = trimmed.match(/"id"\s*:\s*"([^"]+)"/);
                if (idMatch && braceCount >= 1) {
                    currentStageId = idMatch[1];
                }
                // Check for end of stages array
                if (trimmed === ']' && braceCount === 0) {
                    inStages = false;
                }
            }
        }
        catch (error) {
            console.error('Failed to parse pipeline for coverage gutters:', error);
        }
        return stageLines;
    }
    /**
     * Create hover message for a stage
     */
    createHoverMessage(stageId, coverage) {
        const md = new vscode.MarkdownString();
        md.isTrusted = true;
        md.appendMarkdown(`### Stage: \`${stageId}\`\n\n`);
        if (!coverage) {
            md.appendMarkdown('**Status:** Not covered\n\n');
            md.appendMarkdown('_This stage has not been executed in any test._');
            return md;
        }
        // Status with emoji
        const statusEmoji = {
            executed: '$(pass-filled)',
            failed: '$(error)',
            skipped: '$(warning)',
            not_covered: '$(circle-outline)',
        };
        md.appendMarkdown(`**Status:** ${statusEmoji[coverage.status]} ${coverage.status}\n\n`);
        if (coverage.executionCount > 0) {
            md.appendMarkdown(`**Executions:** ${coverage.executionCount}\n\n`);
        }
        if (coverage.lastDuration !== undefined) {
            md.appendMarkdown(`**Last Duration:** ${coverage.lastDuration}ms\n\n`);
        }
        if (coverage.errorMessage) {
            md.appendMarkdown(`**Error:** ${coverage.errorMessage}\n\n`);
        }
        return md;
    }
    /**
     * Get coverage summary for status bar
     */
    getCoverageSummary(filePath) {
        const coverage = this.coverageData.get(filePath);
        if (!coverage) {
            return null;
        }
        const { executed, failed, total, coveragePercent } = coverage.summary;
        return `Coverage: ${coveragePercent.toFixed(0)}% (${executed + failed}/${total} stages)`;
    }
    /**
     * Dispose resources
     */
    dispose() {
        this.executedDecoration.dispose();
        this.failedDecoration.dispose();
        this.skippedDecoration.dispose();
        this.notCoveredDecoration.dispose();
        this.disposables.forEach(d => d.dispose());
    }
}
exports.CoverageGuttersProvider = CoverageGuttersProvider;
/**
 * Global coverage gutters instance
 */
let coverageGutters;
/**
 * Get the global coverage gutters provider
 */
function getCoverageGuttersProvider() {
    if (!coverageGutters) {
        coverageGutters = new CoverageGuttersProvider();
    }
    return coverageGutters;
}
/**
 * Register coverage gutters commands
 */
function registerCoverageCommands(context) {
    const provider = getCoverageGuttersProvider();
    context.subscriptions.push(provider);
    // Toggle coverage display
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.toggleCoverageGutters', () => {
        provider.toggle();
        const state = provider['enabled'] ? 'enabled' : 'disabled';
        vscode.window.showInformationMessage(`Coverage gutters ${state}`);
    }));
    // Clear coverage
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.clearCoverage', () => {
        provider.clearAllCoverage();
        vscode.window.showInformationMessage('Coverage data cleared');
    }));
}
//# sourceMappingURL=coverageGutters.js.map