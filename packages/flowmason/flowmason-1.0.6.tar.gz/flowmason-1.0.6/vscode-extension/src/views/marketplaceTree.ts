/**
 * Marketplace Tree View Provider
 *
 * Provides a tree view for browsing the FlowMason pipeline marketplace.
 */

import * as vscode from 'vscode';

import { FlowMasonService } from '../services/flowmasonService';

// Types for marketplace data
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

class MarketplaceTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly itemType: TreeItemType,
        public readonly data?: MarketplaceListing | MarketplaceCategory | null,
        public readonly sectionId?: string
    ) {
        super(label, collapsibleState);

        switch (itemType) {
            case 'section':
                this.iconPath = this.getSectionIcon(sectionId);
                this.contextValue = 'marketplaceSection';
                break;
            case 'category':
                const cat = data as MarketplaceCategory;
                this.iconPath = new vscode.ThemeIcon(this.getCategoryIcon(cat?.icon));
                this.contextValue = 'marketplaceCategory';
                this.description = `${cat?.listing_count || 0} pipelines`;
                break;
            case 'listing':
                const listing = data as MarketplaceListing;
                this.iconPath = new vscode.ThemeIcon(this.getListingIcon(listing));
                this.contextValue = listing?.pricing?.model === 'free' ? 'marketplaceListingFree' : 'marketplaceListingPaid';
                this.description = this.getListingDescription(listing);
                this.tooltip = this.getListingTooltip(listing);
                this.command = {
                    command: 'flowmason.marketplace.viewListing',
                    title: 'View Listing',
                    arguments: [listing?.id]
                };
                break;
            case 'loading':
                this.iconPath = new vscode.ThemeIcon('loading~spin');
                this.contextValue = 'loading';
                break;
            case 'error':
                this.iconPath = new vscode.ThemeIcon('error');
                this.contextValue = 'error';
                break;
            case 'empty':
                this.iconPath = new vscode.ThemeIcon('info');
                this.contextValue = 'empty';
                break;
        }
    }

    private getSectionIcon(sectionId?: string): vscode.ThemeIcon {
        switch (sectionId) {
            case 'featured':
                return new vscode.ThemeIcon('star-full');
            case 'trending':
                return new vscode.ThemeIcon('flame');
            case 'new':
                return new vscode.ThemeIcon('sparkle');
            case 'categories':
                return new vscode.ThemeIcon('symbol-class');
            case 'search':
                return new vscode.ThemeIcon('search');
            default:
                return new vscode.ThemeIcon('package');
        }
    }

    private getCategoryIcon(icon?: string): string {
        const iconMap: Record<string, string> = {
            'sparkles': 'sparkle',
            'database': 'database',
            'plug': 'plug',
            'cog': 'gear',
            'chart-bar': 'graph',
            'document-text': 'file-text',
            'server': 'server',
            'cube': 'package',
        };
        return iconMap[icon || ''] || 'folder';
    }

    private getListingIcon(listing?: MarketplaceListing): string {
        if (!listing) return 'package';
        if (listing.featured) return 'star-full';
        if (listing.publisher?.verified) return 'verified';
        if (listing.pricing?.model === 'free') return 'package';
        return 'tag';
    }

    private getListingDescription(listing?: MarketplaceListing): string {
        if (!listing) return '';
        const parts: string[] = [];

        if (listing.stats?.average_rating > 0) {
            parts.push(`★${listing.stats.average_rating.toFixed(1)}`);
        }
        if (listing.stats?.downloads > 0) {
            parts.push(`${this.formatDownloads(listing.stats.downloads)} downloads`);
        }
        if (listing.pricing?.model !== 'free' && listing.pricing?.price > 0) {
            parts.push(`$${listing.pricing.price}`);
        }

        return parts.join(' · ');
    }

    private formatDownloads(count: number): string {
        if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
        if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
        return count.toString();
    }

    private getListingTooltip(listing?: MarketplaceListing): string {
        if (!listing) return '';

        const lines = [
            listing.name,
            listing.tagline,
            '',
            `Publisher: ${listing.publisher?.username || 'Unknown'}${listing.publisher?.verified ? ' ✓' : ''}`,
            `Version: ${listing.current_version}`,
            `Category: ${listing.category}`,
        ];

        if (listing.tags?.length) {
            lines.push(`Tags: ${listing.tags.slice(0, 5).join(', ')}`);
        }

        if (listing.stats) {
            lines.push('');
            if (listing.stats.average_rating > 0) {
                lines.push(`Rating: ${'★'.repeat(Math.round(listing.stats.average_rating))} (${listing.stats.reviews} reviews)`);
            }
            lines.push(`Downloads: ${listing.stats.downloads.toLocaleString()}`);
        }

        return lines.join('\n');
    }
}

export class MarketplaceTreeProvider implements vscode.TreeDataProvider<MarketplaceTreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<MarketplaceTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private cachedFeatured: MarketplaceListing[] = [];
    private cachedTrending: MarketplaceListing[] = [];
    private cachedNew: MarketplaceListing[] = [];
    private cachedCategories: MarketplaceCategory[] = [];
    private searchResults: MarketplaceListing[] = [];
    private currentSearchQuery: string = '';
    private isLoading = false;
    private lastError: string | null = null;

    constructor(private readonly service: FlowMasonService) {
        // Initial load
        this.loadData();
    }

    refresh(): void {
        this.cachedFeatured = [];
        this.cachedTrending = [];
        this.cachedNew = [];
        this.cachedCategories = [];
        this.searchResults = [];
        this.lastError = null;
        this._onDidChangeTreeData.fire();
        this.loadData();
    }

    async search(query: string): Promise<void> {
        this.currentSearchQuery = query;
        this.isLoading = true;
        this._onDidChangeTreeData.fire();

        try {
            const results = await this.service.searchMarketplace(query);
            this.searchResults = results.listings || [];
            this.lastError = null;
        } catch (error) {
            this.lastError = `Search failed: ${error}`;
            this.searchResults = [];
        } finally {
            this.isLoading = false;
            this._onDidChangeTreeData.fire();
        }
    }

    clearSearch(): void {
        this.currentSearchQuery = '';
        this.searchResults = [];
        this._onDidChangeTreeData.fire();
    }

    private async loadData(): Promise<void> {
        this.isLoading = true;
        this._onDidChangeTreeData.fire();

        try {
            const [featured, trending, newListings, categories] = await Promise.all([
                this.service.getMarketplaceFeatured(),
                this.service.getMarketplaceTrending(),
                this.service.getMarketplaceNew(),
                this.service.getMarketplaceCategories(),
            ]);

            this.cachedFeatured = featured || [];
            this.cachedTrending = trending || [];
            this.cachedNew = newListings || [];
            this.cachedCategories = categories || [];
            this.lastError = null;
        } catch (error) {
            this.lastError = `Failed to load marketplace: ${error}`;
        } finally {
            this.isLoading = false;
            this._onDidChangeTreeData.fire();
        }
    }

    getTreeItem(element: MarketplaceTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: MarketplaceTreeItem): Promise<MarketplaceTreeItem[]> {
        // Root level
        if (!element) {
            if (this.isLoading) {
                return [new MarketplaceTreeItem('Loading marketplace...', vscode.TreeItemCollapsibleState.None, 'loading')];
            }

            if (this.lastError) {
                return [new MarketplaceTreeItem(this.lastError, vscode.TreeItemCollapsibleState.None, 'error')];
            }

            const items: MarketplaceTreeItem[] = [];

            // Show search results if searching
            if (this.currentSearchQuery) {
                items.push(new MarketplaceTreeItem(
                    `Search: "${this.currentSearchQuery}"`,
                    vscode.TreeItemCollapsibleState.Expanded,
                    'section',
                    null,
                    'search'
                ));
            } else {
                // Default sections
                if (this.cachedFeatured.length > 0) {
                    items.push(new MarketplaceTreeItem(
                        'Featured',
                        vscode.TreeItemCollapsibleState.Collapsed,
                        'section',
                        null,
                        'featured'
                    ));
                }

                if (this.cachedTrending.length > 0) {
                    items.push(new MarketplaceTreeItem(
                        'Trending',
                        vscode.TreeItemCollapsibleState.Collapsed,
                        'section',
                        null,
                        'trending'
                    ));
                }

                if (this.cachedNew.length > 0) {
                    items.push(new MarketplaceTreeItem(
                        'New This Week',
                        vscode.TreeItemCollapsibleState.Collapsed,
                        'section',
                        null,
                        'new'
                    ));
                }

                if (this.cachedCategories.length > 0) {
                    items.push(new MarketplaceTreeItem(
                        'Categories',
                        vscode.TreeItemCollapsibleState.Expanded,
                        'section',
                        null,
                        'categories'
                    ));
                }
            }

            if (items.length === 0) {
                return [new MarketplaceTreeItem('No marketplace data available', vscode.TreeItemCollapsibleState.None, 'empty')];
            }

            return items;
        }

        // Section children
        if (element.itemType === 'section') {
            switch (element.sectionId) {
                case 'featured':
                    return this.createListingItems(this.cachedFeatured);
                case 'trending':
                    return this.createListingItems(this.cachedTrending);
                case 'new':
                    return this.createListingItems(this.cachedNew);
                case 'categories':
                    return this.cachedCategories.map(cat =>
                        new MarketplaceTreeItem(
                            cat.name,
                            vscode.TreeItemCollapsibleState.Collapsed,
                            'category',
                            cat
                        )
                    );
                case 'search':
                    return this.createListingItems(this.searchResults);
            }
        }

        // Category children - load listings for this category
        if (element.itemType === 'category') {
            const category = element.data as MarketplaceCategory;
            if (category) {
                try {
                    const listings = await this.service.getMarketplaceByCategory(category.id);
                    return this.createListingItems(listings || []);
                } catch {
                    return [new MarketplaceTreeItem('Failed to load category', vscode.TreeItemCollapsibleState.None, 'error')];
                }
            }
        }

        return [];
    }

    private createListingItems(listings: MarketplaceListing[]): MarketplaceTreeItem[] {
        if (listings.length === 0) {
            return [new MarketplaceTreeItem('No pipelines found', vscode.TreeItemCollapsibleState.None, 'empty')];
        }

        return listings.map(listing =>
            new MarketplaceTreeItem(
                listing.name,
                vscode.TreeItemCollapsibleState.None,
                'listing',
                listing
            )
        );
    }
}

export function registerMarketplaceCommands(
    context: vscode.ExtensionContext,
    service: FlowMasonService,
    outputChannel: vscode.OutputChannel
): MarketplaceTreeProvider {
    const provider = new MarketplaceTreeProvider(service);

    // Register tree view
    vscode.window.registerTreeDataProvider('flowmason.marketplace', provider);

    // Refresh command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.refresh', () => {
            provider.refresh();
        })
    );

    // Search command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.search', async () => {
            const query = await vscode.window.showInputBox({
                prompt: 'Search the FlowMason Marketplace',
                placeHolder: 'Enter search terms...',
            });

            if (query) {
                await provider.search(query);
            }
        })
    );

    // Clear search command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.clearSearch', () => {
            provider.clearSearch();
        })
    );

    // View listing details
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.viewListing', async (listingId: string) => {
            try {
                const listing = await service.getMarketplaceListing(listingId);
                if (!listing) {
                    vscode.window.showErrorMessage('Listing not found');
                    return;
                }

                // Create a webview panel to show listing details
                const panel = vscode.window.createWebviewPanel(
                    'flowmasonMarketplaceListing',
                    listing.name,
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = getListingDetailHtml(listing);

                // Handle messages from the webview
                panel.webview.onDidReceiveMessage(
                    async message => {
                        switch (message.command) {
                            case 'install':
                                await vscode.commands.executeCommand('flowmason.marketplace.install', listingId);
                                break;
                            case 'openPublisher':
                                await vscode.commands.executeCommand('flowmason.marketplace.viewPublisher', message.publisherId);
                                break;
                        }
                    },
                    undefined,
                    context.subscriptions
                );
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to load listing: ${error}`);
            }
        })
    );

    // Install listing
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.install', async (listingId: string) => {
            try {
                const listing = await service.getMarketplaceListing(listingId);
                if (!listing) {
                    vscode.window.showErrorMessage('Listing not found');
                    return;
                }

                // Check if it's a paid listing
                if (listing.pricing?.model !== 'free' && listing.pricing?.price > 0) {
                    const result = await vscode.window.showWarningMessage(
                        `"${listing.name}" costs $${listing.pricing.price}. Continue to purchase?`,
                        'Purchase & Install',
                        'Cancel'
                    );
                    if (result !== 'Purchase & Install') {
                        return;
                    }
                }

                // Ask for pipeline name
                const pipelineName = await vscode.window.showInputBox({
                    prompt: 'Enter name for the new pipeline',
                    value: listing.name.toLowerCase().replace(/\s+/g, '-'),
                    validateInput: (value) => {
                        if (!value) return 'Pipeline name is required';
                        if (!/^[a-z0-9-]+$/.test(value)) return 'Use only lowercase letters, numbers, and hyphens';
                        return null;
                    }
                });

                if (!pipelineName) {
                    return;
                }

                outputChannel.appendLine(`Installing marketplace listing: ${listing.name}`);

                await vscode.window.withProgress(
                    {
                        location: vscode.ProgressLocation.Notification,
                        title: `Installing ${listing.name}...`,
                        cancellable: false,
                    },
                    async () => {
                        const result = await service.installMarketplaceListing(listingId, {
                            pipeline_name: pipelineName,
                            create_pipeline: true,
                        });

                        outputChannel.appendLine(`Installation complete: ${JSON.stringify(result)}`);

                        vscode.window.showInformationMessage(
                            `Successfully installed "${listing.name}" as "${pipelineName}"`,
                            'Open Pipeline'
                        ).then(async action => {
                            if (action === 'Open Pipeline' && result.pipeline_id) {
                                // Open the created pipeline file
                                const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
                                if (workspaceFolder) {
                                    const pipelineUri = vscode.Uri.joinPath(
                                        workspaceFolder.uri,
                                        'pipelines',
                                        `${pipelineName}.pipeline.json`
                                    );
                                    try {
                                        await vscode.commands.executeCommand('vscode.open', pipelineUri);
                                    } catch {
                                        // File might be elsewhere, try finding it
                                        const files = await vscode.workspace.findFiles(`**/${pipelineName}.pipeline.json`);
                                        if (files.length > 0) {
                                            await vscode.commands.executeCommand('vscode.open', files[0]);
                                        }
                                    }
                                }
                            }
                        });
                    }
                );
            } catch (error) {
                outputChannel.appendLine(`Installation failed: ${error}`);
                vscode.window.showErrorMessage(`Failed to install: ${error}`);
            }
        })
    );

    // View publisher profile
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.viewPublisher', async (publisherId: string) => {
            try {
                const publisher = await service.getMarketplacePublisher(publisherId);
                if (!publisher) {
                    vscode.window.showErrorMessage('Publisher not found');
                    return;
                }

                // Show publisher info
                const panel = vscode.window.createWebviewPanel(
                    'flowmasonMarketplacePublisher',
                    publisher.name,
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = getPublisherDetailHtml(publisher);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to load publisher: ${error}`);
            }
        })
    );

    // Browse by category
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.browseCategory', async () => {
            const categories = await service.getMarketplaceCategories();
            const selected = await vscode.window.showQuickPick(
                categories.map(c => ({
                    label: c.name,
                    description: `${c.listing_count} pipelines`,
                    detail: c.description,
                    id: c.id,
                })),
                { placeHolder: 'Select a category' }
            );

            if (selected) {
                await provider.search(`category:${selected.id}`);
            }
        })
    );

    // Add to favorites
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.addFavorite', async (listingId: string) => {
            try {
                await service.addMarketplaceFavorite(listingId);
                vscode.window.showInformationMessage('Added to favorites');
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to add to favorites: ${error}`);
            }
        })
    );

    // Remove from favorites
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.removeFavorite', async (listingId: string) => {
            try {
                await service.removeMarketplaceFavorite(listingId);
                vscode.window.showInformationMessage('Removed from favorites');
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to remove from favorites: ${error}`);
            }
        })
    );

    // Open marketplace in browser
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.marketplace.openInBrowser', async () => {
            const studioUrl = vscode.workspace.getConfiguration('flowmason').get<string>('studioUrl') || 'http://localhost:8999';
            vscode.env.openExternal(vscode.Uri.parse(`${studioUrl}/marketplace`));
        })
    );

    return provider;
}

function getListingDetailHtml(listing: any): string {
    const rating = listing.stats?.average_rating || 0;
    const stars = '★'.repeat(Math.round(rating)) + '☆'.repeat(5 - Math.round(rating));

    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: var(--vscode-font-family); padding: 20px; color: var(--vscode-foreground); }
        .header { display: flex; align-items: center; margin-bottom: 20px; }
        .icon { width: 64px; height: 64px; margin-right: 16px; background: var(--vscode-badge-background); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
        .title { flex: 1; }
        .title h1 { margin: 0; font-size: 24px; }
        .tagline { color: var(--vscode-descriptionForeground); margin-top: 4px; }
        .meta { display: flex; gap: 16px; margin: 16px 0; flex-wrap: wrap; }
        .meta-item { display: flex; align-items: center; gap: 4px; }
        .rating { color: #f5c518; }
        .section { margin: 24px 0; }
        .section h2 { font-size: 16px; margin-bottom: 12px; border-bottom: 1px solid var(--vscode-panel-border); padding-bottom: 8px; }
        .description { line-height: 1.6; }
        .tags { display: flex; gap: 8px; flex-wrap: wrap; }
        .tag { background: var(--vscode-badge-background); color: var(--vscode-badge-foreground); padding: 2px 8px; border-radius: 4px; font-size: 12px; }
        .install-btn { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 8px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .install-btn:hover { background: var(--vscode-button-hoverBackground); }
        .publisher { display: flex; align-items: center; gap: 8px; margin-top: 16px; }
        .publisher-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--vscode-badge-background); }
        .verified { color: #0a0; }
        .price { font-size: 20px; font-weight: bold; margin-right: 16px; }
        .free { color: #0a0; }
    </style>
</head>
<body>
    <div class="header">
        <div class="icon">📦</div>
        <div class="title">
            <h1>${listing.name}</h1>
            <div class="tagline">${listing.tagline || ''}</div>
        </div>
        <div>
            ${listing.pricing?.model === 'free'
                ? '<span class="price free">Free</span>'
                : `<span class="price">$${listing.pricing?.price || 0}</span>`
            }
            <button class="install-btn" onclick="install()">Install</button>
        </div>
    </div>

    <div class="meta">
        <div class="meta-item">
            <span class="rating">${stars}</span>
            <span>${rating.toFixed(1)} (${listing.stats?.reviews || 0} reviews)</span>
        </div>
        <div class="meta-item">
            <span>📥 ${(listing.stats?.downloads || 0).toLocaleString()} downloads</span>
        </div>
        <div class="meta-item">
            <span>📁 ${listing.category}</span>
        </div>
        <div class="meta-item">
            <span>v${listing.current_version}</span>
        </div>
    </div>

    <div class="publisher" onclick="openPublisher('${listing.publisher?.id}')">
        <div class="publisher-avatar"></div>
        <span>${listing.publisher?.username || 'Unknown'}</span>
        ${listing.publisher?.verified ? '<span class="verified">✓ Verified</span>' : ''}
    </div>

    <div class="section">
        <h2>Description</h2>
        <div class="description">${listing.description || 'No description available.'}</div>
    </div>

    ${listing.tags?.length ? `
    <div class="section">
        <h2>Tags</h2>
        <div class="tags">
            ${listing.tags.map((t: string) => `<span class="tag">${t}</span>`).join('')}
        </div>
    </div>
    ` : ''}

    ${listing.readme ? `
    <div class="section">
        <h2>Documentation</h2>
        <div class="description">${listing.readme}</div>
    </div>
    ` : ''}

    <script>
        const vscode = acquireVsCodeApi();
        function install() {
            vscode.postMessage({ command: 'install' });
        }
        function openPublisher(id) {
            vscode.postMessage({ command: 'openPublisher', publisherId: id });
        }
    </script>
</body>
</html>`;
}

function getPublisherDetailHtml(publisher: any): string {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: var(--vscode-font-family); padding: 20px; color: var(--vscode-foreground); }
        .header { display: flex; align-items: center; margin-bottom: 20px; }
        .avatar { width: 80px; height: 80px; border-radius: 50%; background: var(--vscode-badge-background); margin-right: 16px; display: flex; align-items: center; justify-content: center; font-size: 32px; }
        .info h1 { margin: 0; font-size: 24px; }
        .verified { color: #0a0; margin-left: 8px; }
        .username { color: var(--vscode-descriptionForeground); }
        .stats { display: flex; gap: 24px; margin: 20px 0; }
        .stat { text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; }
        .stat-label { color: var(--vscode-descriptionForeground); font-size: 12px; }
        .links { margin-top: 20px; }
        .links a { color: var(--vscode-textLink-foreground); margin-right: 16px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="avatar">👤</div>
        <div class="info">
            <h1>
                ${publisher.name}
                ${publisher.verified ? '<span class="verified">✓ Verified Publisher</span>' : ''}
            </h1>
            <div class="username">@${publisher.username}</div>
        </div>
    </div>

    <div class="stats">
        <div class="stat">
            <div class="stat-value">${publisher.total_listings || 0}</div>
            <div class="stat-label">Pipelines</div>
        </div>
        <div class="stat">
            <div class="stat-value">${(publisher.total_downloads || 0).toLocaleString()}</div>
            <div class="stat-label">Downloads</div>
        </div>
        <div class="stat">
            <div class="stat-value">${publisher.average_rating?.toFixed(1) || '-'}</div>
            <div class="stat-label">Avg Rating</div>
        </div>
    </div>

    ${publisher.website ? `
    <div class="links">
        <a href="${publisher.website}">🌐 Website</a>
    </div>
    ` : ''}

    <p>Member since ${publisher.member_since || 'Unknown'}</p>
</body>
</html>`;
}
