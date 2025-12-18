"use strict";
/**
 * Pipelines Tree View Provider
 *
 * Shows FlowMason pipelines in the sidebar.
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
exports.PipelineTreeItem = exports.PipelinesTreeProvider = void 0;
const vscode = __importStar(require("vscode"));
class PipelinesTreeProvider {
    constructor(flowmasonService) {
        this.flowmasonService = flowmasonService;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren(element) {
        if (!element) {
            return this.getPipelines();
        }
        return [];
    }
    async getPipelines() {
        try {
            const pipelines = await this.flowmasonService.getPipelines();
            if (pipelines.length === 0) {
                const item = new PipelineTreeItem('No pipelines', vscode.TreeItemCollapsibleState.None, 'empty');
                item.iconPath = new vscode.ThemeIcon('info');
                item.command = {
                    command: 'flowmason.openStudio',
                    title: 'Open Studio',
                };
                return [item];
            }
            return pipelines.map(pipeline => {
                const item = new PipelineTreeItem(pipeline.name, vscode.TreeItemCollapsibleState.None, 'pipeline');
                item.description = pipeline.status === 'published' ? 'Published' : 'Draft';
                item.tooltip = `${pipeline.description || pipeline.name}\n\nStatus: ${pipeline.status}\nStages: ${pipeline.stage_count}`;
                // Icon based on status
                if (pipeline.status === 'published') {
                    item.iconPath = new vscode.ThemeIcon('check-all', new vscode.ThemeColor('charts.green'));
                }
                else {
                    item.iconPath = new vscode.ThemeIcon('git-merge', new vscode.ThemeColor('charts.yellow'));
                }
                item.pipeline = pipeline;
                return item;
            });
        }
        catch {
            const item = new PipelineTreeItem('Unable to load pipelines', vscode.TreeItemCollapsibleState.None, 'error');
            item.iconPath = new vscode.ThemeIcon('warning');
            item.description = 'Studio may not be running';
            return [item];
        }
    }
}
exports.PipelinesTreeProvider = PipelinesTreeProvider;
class PipelineTreeItem extends vscode.TreeItem {
    constructor(label, collapsibleState, contextValue) {
        super(label, collapsibleState);
        this.label = label;
        this.collapsibleState = collapsibleState;
        this.contextValue = contextValue;
        this.contextValue = contextValue;
    }
}
exports.PipelineTreeItem = PipelineTreeItem;
//# sourceMappingURL=pipelinesTree.js.map