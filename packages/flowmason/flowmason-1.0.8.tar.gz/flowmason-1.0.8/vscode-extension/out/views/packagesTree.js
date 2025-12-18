"use strict";
/**
 * Packages Tree View Provider
 *
 * Shows FlowMason packages in the sidebar.
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
exports.PackageTreeItem = exports.PackagesTreeProvider = void 0;
const vscode = __importStar(require("vscode"));
class PackagesTreeProvider {
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
            // Root level - show packages
            return this.getPackages();
        }
        if (element.contextValue === 'package' && element.package) {
            // Package level - show components
            return this.getPackageComponents(element.package);
        }
        return [];
    }
    async getPackages() {
        const packages = await this.flowmasonService.getLocalPackages();
        if (packages.length === 0) {
            const item = new PackageTreeItem('No packages installed', vscode.TreeItemCollapsibleState.None, 'empty');
            item.iconPath = new vscode.ThemeIcon('info');
            return [item];
        }
        return packages.map(pkg => {
            const item = new PackageTreeItem(pkg.name, vscode.TreeItemCollapsibleState.Collapsed, 'package');
            item.description = `v${pkg.version}`;
            item.tooltip = `${pkg.description || pkg.name}\n\nPath: ${pkg.path}`;
            item.iconPath = new vscode.ThemeIcon('package');
            item.package = pkg;
            return item;
        });
    }
    getPackageComponents(pkg) {
        return pkg.components.map(comp => {
            const item = new PackageTreeItem(comp.name, vscode.TreeItemCollapsibleState.None, 'packageComponent');
            item.description = comp.type === 'node' ? 'Node' : 'Operator';
            item.tooltip = comp.description || comp.name;
            if (comp.type === 'node') {
                item.iconPath = new vscode.ThemeIcon('symbol-method');
            }
            else {
                item.iconPath = new vscode.ThemeIcon('symbol-function');
            }
            return item;
        });
    }
}
exports.PackagesTreeProvider = PackagesTreeProvider;
class PackageTreeItem extends vscode.TreeItem {
    constructor(label, collapsibleState, contextValue) {
        super(label, collapsibleState);
        this.label = label;
        this.collapsibleState = collapsibleState;
        this.contextValue = contextValue;
        this.contextValue = contextValue;
    }
}
exports.PackageTreeItem = PackageTreeItem;
//# sourceMappingURL=packagesTree.js.map