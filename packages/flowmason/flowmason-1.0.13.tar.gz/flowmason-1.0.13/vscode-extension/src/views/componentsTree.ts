/**
 * Components Tree View Provider
 *
 * Shows FlowMason components in the sidebar.
 */

import * as vscode from 'vscode';
import { FlowMasonService, Component } from '../services/flowmasonService';
import { ComponentParser } from '../services/componentParser';

/**
 * Map Lucide icon names to VSCode codicon names.
 * VSCode uses codicons (https://microsoft.github.io/vscode-codicons/dist/codicon.html)
 * FlowMason operators use Lucide icons (https://lucide.dev/icons)
 */
const LUCIDE_TO_CODICON: Record<string, string> = {
    // AI/ML
    'sparkles': 'sparkle',
    'wand': 'wand',
    'brain': 'symbol-misc',

    // Control Flow
    'git-branch': 'git-branch',
    'git-merge': 'git-merge',
    'repeat': 'sync',
    'corner-down-left': 'arrow-left',
    'shield': 'shield',

    // Data
    'code': 'code',
    'filter': 'filter',
    'variable': 'symbol-variable',
    'database': 'database',

    // Network
    'globe': 'globe',
    'share-2': 'export',
    'link': 'link',

    // Utility
    'file-text': 'file',
    'clipboard-check': 'checklist',
    'check-circle': 'check',
    'arrow-up-circle': 'arrow-up',
    'alert-triangle': 'warning',
    'shield-check': 'verified',
    'box': 'package',
    'zap': 'zap',

    // Default fallbacks
    'folder': 'folder',
    'settings': 'settings-gear',
};

export class ComponentsTreeProvider implements vscode.TreeDataProvider<ComponentTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ComponentTreeItem | undefined | null | void> = new vscode.EventEmitter<ComponentTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ComponentTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(
        private flowmasonService: FlowMasonService,
        private componentParser: ComponentParser
    ) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ComponentTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: ComponentTreeItem): Promise<ComponentTreeItem[]> {
        if (!element) {
            // Root level - show categories
            return this.getCategories();
        }

        if (element.contextValue === 'category') {
            // Category level - show components
            return this.getComponentsInCategory(element.label as string);
        }

        return [];
    }

    private async getCategories(): Promise<ComponentTreeItem[]> {
        const categories = new Map<string, number>();

        // Get components from API
        const apiComponents = await this.flowmasonService.getComponents();
        for (const comp of apiComponents) {
            const count = categories.get(comp.category) || 0;
            categories.set(comp.category, count + 1);
        }

        // Get components from workspace
        const workspaceComponents = await this.getWorkspaceComponents();
        for (const comp of workspaceComponents) {
            const count = categories.get(comp.category) || 0;
            categories.set(comp.category, count + 1);
        }

        // Convert to tree items
        const items: ComponentTreeItem[] = [];
        for (const [category, count] of categories) {
            const item = new ComponentTreeItem(
                category,
                vscode.TreeItemCollapsibleState.Collapsed,
                'category'
            );
            item.description = `${count} components`;
            item.iconPath = new vscode.ThemeIcon('folder');
            items.push(item);
        }

        // Add workspace category if there are local components
        if (workspaceComponents.length > 0) {
            const existingWorkspace = items.find(i => i.label === 'workspace');
            if (!existingWorkspace) {
                const item = new ComponentTreeItem(
                    'workspace',
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'category'
                );
                item.description = `${workspaceComponents.length} components`;
                item.iconPath = new vscode.ThemeIcon('folder-library');
                items.push(item);
            }
        }

        return items.sort((a, b) => (a.label as string).localeCompare(b.label as string));
    }

    private async getComponentsInCategory(category: string): Promise<ComponentTreeItem[]> {
        const items: ComponentTreeItem[] = [];

        // Get from API
        const apiComponents = await this.flowmasonService.getComponents();
        for (const comp of apiComponents) {
            if (comp.category === category) {
                items.push(this.componentToTreeItem(comp, 'api'));
            }
        }

        // Get from workspace
        if (category === 'workspace') {
            const workspaceComponents = await this.getWorkspaceComponents();
            for (const comp of workspaceComponents) {
                items.push(this.componentToTreeItem(comp, 'workspace'));
            }
        }

        return items.sort((a, b) => (a.label as string).localeCompare(b.label as string));
    }

    private componentToTreeItem(comp: Component, source: string): ComponentTreeItem {
        const item = new ComponentTreeItem(
            comp.name,
            vscode.TreeItemCollapsibleState.None,
            'component'
        );

        // Description based on component kind
        const kindLabel = comp.component_kind === 'node' ? 'Node' :
                         comp.component_kind === 'control_flow' ? 'Control Flow' : 'Operator';
        item.description = kindLabel;
        item.tooltip = `${comp.description}\n\nVersion: ${comp.version}\nType: ${kindLabel}\nLLM: ${comp.requires_llm ? 'Required' : 'Not needed'}`;

        // Use actual icon from component, with fallback
        const lucideIcon = comp.icon || 'box';
        const codiconName = LUCIDE_TO_CODICON[lucideIcon] || 'symbol-misc';

        // Map color to VSCode theme color
        const themeColor = this.hexToThemeColor(comp.color);
        item.iconPath = new vscode.ThemeIcon(codiconName, themeColor);

        // Store component data
        item.component = comp;

        return item;
    }

    /**
     * Map hex color to nearest VSCode theme color.
     * VSCode has limited theme colors for icons, so we map to the closest one.
     */
    private hexToThemeColor(hexColor?: string): vscode.ThemeColor | undefined {
        if (!hexColor) {
            return undefined;
        }

        // Map common colors to VSCode chart colors
        // These are the available icon colors in VSCode
        const colorMap: Record<string, string> = {
            // Purples
            '#8B5CF6': 'charts.purple',
            '#6366F1': 'charts.purple',
            '#9333EA': 'charts.purple',

            // Blues
            '#3B82F6': 'charts.blue',
            '#06B6D4': 'charts.blue',

            // Greens
            '#10B981': 'charts.green',
            '#14B8A6': 'charts.green',

            // Yellows/Oranges
            '#F59E0B': 'charts.yellow',
            '#F97316': 'charts.orange',

            // Reds/Pinks
            '#EF4444': 'charts.red',
            '#EC4899': 'charts.red',

            // Grays
            '#78716C': 'descriptionForeground',
            '#6B7280': 'descriptionForeground',
        };

        // Try exact match first
        if (colorMap[hexColor.toUpperCase()] || colorMap[hexColor]) {
            return new vscode.ThemeColor(colorMap[hexColor.toUpperCase()] || colorMap[hexColor]);
        }

        // Fallback: determine color family from hex
        const hex = hexColor.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);

        // Simple heuristic based on dominant channel
        if (r > g && r > b) {
            return new vscode.ThemeColor(r > 200 ? 'charts.red' : 'charts.orange');
        } else if (g > r && g > b) {
            return new vscode.ThemeColor('charts.green');
        } else if (b > r && b > g) {
            return new vscode.ThemeColor('charts.blue');
        } else if (r > 100 && b > 100 && g < 100) {
            return new vscode.ThemeColor('charts.purple');
        }

        return undefined;
    }

    private async getWorkspaceComponents(): Promise<Component[]> {
        const components: Component[] = [];

        // Find Python files in workspace
        const files = await vscode.workspace.findFiles('**/*.py', '**/node_modules/**');

        for (const file of files) {
            try {
                const doc = await vscode.workspace.openTextDocument(file);
                const parsed = this.componentParser.parseDocument(doc);

                for (const comp of parsed) {
                    components.push({
                        component_type: comp.name, // Use name as component_type
                        component_kind: comp.type === 'node' ? 'node' : 'operator',
                        type: comp.type, // Backwards compatible
                        name: comp.name,
                        category: 'workspace',
                        description: comp.description,
                        icon: comp.icon,
                        color: comp.color,
                        version: comp.version,
                        requires_llm: comp.requires_llm,
                    });
                }
            } catch {
                // Skip files that can't be parsed
            }
        }

        return components;
    }
}

export class ComponentTreeItem extends vscode.TreeItem {
    component?: Component;

    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue: string
    ) {
        super(label, collapsibleState);
        this.contextValue = contextValue;
    }
}
