/**
 * Marketplace Tree View Provider
 *
 * Provides a tree view for browsing the FlowMason pipeline marketplace.
 */
import * as vscode from 'vscode';
import { FlowMasonService } from '../services/flowmasonService';
interface MarketplaceListing {
    id: string;
    slug: string;
    name: string;
    tagline: string;
    category: string;
    publisher: {
        name: string;
        username: string;
        verified: boolean;
    };
    pricing: {
        model: string;
        price: number;
    };
    stats: {
        downloads: number;
        average_rating: number;
        reviews: number;
    };
    tags: string[];
    current_version: string;
    featured: boolean;
}
interface MarketplaceCategory {
    id: string;
    name: string;
    description: string;
    icon: string;
    listing_count: number;
}
type TreeItemType = 'section' | 'category' | 'listing' | 'loading' | 'error' | 'empty';
declare class MarketplaceTreeItem extends vscode.TreeItem {
    readonly label: string;
    readonly collapsibleState: vscode.TreeItemCollapsibleState;
    readonly itemType: TreeItemType;
    readonly data?: (MarketplaceListing | MarketplaceCategory | null) | undefined;
    readonly sectionId?: string | undefined;
    constructor(label: string, collapsibleState: vscode.TreeItemCollapsibleState, itemType: TreeItemType, data?: (MarketplaceListing | MarketplaceCategory | null) | undefined, sectionId?: string | undefined);
    private getSectionIcon;
    private getCategoryIcon;
    private getListingIcon;
    private getListingDescription;
    private formatDownloads;
    private getListingTooltip;
}
export declare class MarketplaceTreeProvider implements vscode.TreeDataProvider<MarketplaceTreeItem> {
    private readonly service;
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: vscode.Event<void | MarketplaceTreeItem | null | undefined>;
    private cachedFeatured;
    private cachedTrending;
    private cachedNew;
    private cachedCategories;
    private searchResults;
    private currentSearchQuery;
    private isLoading;
    private lastError;
    constructor(service: FlowMasonService);
    refresh(): void;
    search(query: string): Promise<void>;
    clearSearch(): void;
    private loadData;
    getTreeItem(element: MarketplaceTreeItem): vscode.TreeItem;
    getChildren(element?: MarketplaceTreeItem): Promise<MarketplaceTreeItem[]>;
    private createListingItems;
}
export declare function registerMarketplaceCommands(context: vscode.ExtensionContext, service: FlowMasonService, outputChannel: vscode.OutputChannel): MarketplaceTreeProvider;
export {};
//# sourceMappingURL=marketplaceTree.d.ts.map