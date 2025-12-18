/**
 * FlowMason Service
 *
 * Handles communication with FlowMason Studio API and local installation.
 */
/**
 * AI configuration for LLM-requiring nodes.
 * Contains recommended providers with their model configurations.
 */
export interface AIConfig {
    recommended_providers?: Record<string, {
        model: string;
        temperature?: number;
        max_tokens?: number;
        [key: string]: unknown;
    }>;
    default_provider?: string;
    required_capabilities?: string[];
    min_context_window?: number;
    require_vision?: boolean;
    require_function_calling?: boolean;
}
/**
 * Component summary (from list endpoint)
 */
export interface Component {
    component_type: string;
    component_kind: 'node' | 'operator' | 'control_flow';
    name: string;
    category: string;
    description: string;
    icon?: string;
    color?: string;
    version: string;
    requires_llm: boolean;
    input_schema?: Record<string, unknown>;
    output_schema?: Record<string, unknown>;
    control_flow_type?: string;
    package_name?: string;
    type?: string;
}
/**
 * Full component detail (from detail endpoint)
 * Includes complete AI configuration and runtime settings
 */
export interface ComponentDetail extends Component {
    author?: string;
    tags?: string[];
    ai_config?: AIConfig;
    recommended_providers?: string[];
    default_provider?: string;
    package_version?: string;
    registered_at?: string;
    timeout_seconds?: number;
    max_retries?: number;
    supports_streaming?: boolean;
}
/**
 * LLM Provider summary
 */
export interface Provider {
    name: string;
    default_model: string;
    available_models: string[];
    capabilities: string[];
    configured: boolean;
}
export interface Package {
    id: string;
    name: string;
    version: string;
    description: string;
    author?: string;
    components: Component[];
    path: string;
}
export interface Pipeline {
    id: string;
    name: string;
    description: string;
    status: string;
    stage_count: number;
    created_at?: string;
    updated_at?: string;
}
export interface TestResult {
    success: boolean;
    output?: unknown;
    error?: string;
    duration_ms?: number;
    usage?: {
        input_tokens?: number;
        output_tokens?: number;
    };
}
export declare class FlowMasonService {
    private client;
    private packagesDir;
    private componentDetailCache;
    private providersCache;
    private readonly CACHE_TTL_MS;
    constructor();
    /**
     * Clear all caches (useful after config changes)
     */
    clearCache(): void;
    /**
     * Check if FlowMason Studio is running
     */
    checkConnection(): Promise<boolean>;
    /**
     * Get all registered components from the API
     */
    getComponents(): Promise<Component[]>;
    /**
     * Get component details by type (basic info)
     */
    getComponent(componentType: string): Promise<Component | null>;
    /**
     * Get full component detail including AI config (with caching)
     * This is the preferred method for the StageConfigEditor
     */
    getComponentDetail(componentType: string): Promise<ComponentDetail | null>;
    /**
     * Get all available LLM providers (with caching)
     */
    getProviders(): Promise<Provider[]>;
    /**
     * Get available models for a specific provider
     */
    getProviderModels(providerName: string): Promise<{
        models: string[];
        default_model: string;
    } | null>;
    /**
     * Test a provider connection
     */
    testProvider(providerName: string): Promise<{
        success: boolean;
        message: string;
    }>;
    /**
     * Get all pipelines
     */
    getPipelines(): Promise<Pipeline[]>;
    /**
     * Test a component with sample input
     */
    testComponent(componentType: string, config: Record<string, unknown>, input: Record<string, unknown>): Promise<TestResult>;
    /**
     * Get installed packages from the local packages directory
     */
    getLocalPackages(): Promise<Package[]>;
    /**
     * Deploy a package to the local packages directory
     */
    deployPackage(packagePath: string): Promise<{
        success: boolean;
        error?: string;
    }>;
    /**
     * Helper to copy a directory recursively
     */
    private copyDirectory;
    /**
     * Open FlowMason Studio in browser
     */
    openStudio(): void;
    /**
     * Get the packages directory path
     */
    getPackagesDirectory(): string;
    /**
     * Publish a package to the private registry
     */
    publishToPrivateRegistry(packagePath: string, visibility?: string): Promise<PrivatePackageInfo>;
    /**
     * List packages in the private registry
     */
    listPrivatePackages(options?: {
        category?: string;
        query?: string;
        includePrivate?: boolean;
    }): Promise<{
        packages: PrivatePackageInfo[];
        total: number;
    }>;
    /**
     * Get a specific package from the private registry
     */
    getPrivatePackage(name: string, version?: string): Promise<PrivatePackageInfo>;
    /**
     * Get all versions of a package
     */
    getPrivatePackageVersions(name: string): Promise<{
        name: string;
        versions: string[];
        latest: string;
    }>;
    /**
     * Download a package from the private registry
     */
    downloadPrivatePackage(name: string, version: string): Promise<Buffer>;
    /**
     * Delete a package from the private registry
     */
    deletePrivatePackage(name: string, version: string): Promise<void>;
    /**
     * Get private registry statistics
     */
    getPrivateRegistryStats(): Promise<{
        packages_count: number;
        components_count: number;
        total_downloads: number;
        categories: Record<string, number>;
    }>;
    /**
     * Grant access to a private package
     */
    grantPackageAccess(name: string, userId: string, accessLevel: 'read' | 'write' | 'admin'): Promise<void>;
    /**
     * Revoke access to a private package
     */
    revokePackageAccess(name: string, userId: string): Promise<void>;
    /**
     * Change package visibility
     */
    setPackageVisibility(name: string, visibility: 'public' | 'private' | 'unlisted'): Promise<void>;
    /**
     * Search the marketplace
     */
    searchMarketplace(query: string, options?: {
        category?: string;
        pricing?: string;
        minRating?: number;
        sortBy?: string;
        page?: number;
        perPage?: number;
    }): Promise<{
        listings: MarketplaceListing[];
        total: number;
    }>;
    /**
     * Get featured marketplace listings
     */
    getMarketplaceFeatured(limit?: number): Promise<MarketplaceListing[]>;
    /**
     * Get trending marketplace listings
     */
    getMarketplaceTrending(limit?: number): Promise<MarketplaceListing[]>;
    /**
     * Get new marketplace listings
     */
    getMarketplaceNew(limit?: number): Promise<MarketplaceListing[]>;
    /**
     * Get marketplace categories
     */
    getMarketplaceCategories(): Promise<MarketplaceCategory[]>;
    /**
     * Get listings by category
     */
    getMarketplaceByCategory(categoryId: string, limit?: number): Promise<MarketplaceListing[]>;
    /**
     * Get a specific marketplace listing
     */
    getMarketplaceListing(listingId: string): Promise<MarketplaceListing | null>;
    /**
     * Get marketplace listing by slug
     */
    getMarketplaceListingBySlug(slug: string): Promise<MarketplaceListing | null>;
    /**
     * Install a marketplace listing
     */
    installMarketplaceListing(listingId: string, options?: {
        version?: string;
        pipeline_name?: string;
        create_pipeline?: boolean;
        customizations?: Record<string, unknown>;
    }): Promise<MarketplaceInstallResult>;
    /**
     * Get a publisher profile
     */
    getMarketplacePublisher(publisherId: string): Promise<MarketplacePublisher | null>;
    /**
     * Add listing to favorites
     */
    addMarketplaceFavorite(listingId: string): Promise<void>;
    /**
     * Remove listing from favorites
     */
    removeMarketplaceFavorite(listingId: string): Promise<void>;
    /**
     * Get user's marketplace library
     */
    getMarketplaceLibrary(): Promise<{
        purchased: string[];
        favorites: string[];
        installed: string[];
    }>;
    /**
     * Get marketplace statistics
     */
    getMarketplaceStats(): Promise<MarketplaceStats>;
    /**
     * Get reviews for a listing
     */
    getMarketplaceReviews(listingId: string, options?: {
        limit?: number;
        offset?: number;
    }): Promise<MarketplaceReview[]>;
    /**
     * Submit a review for a listing
     */
    submitMarketplaceReview(listingId: string, review: {
        rating: number;
        title: string;
        content: string;
    }): Promise<MarketplaceReview>;
    /**
     * Get execution timeline for a run
     */
    getTimeTravelTimeline(runId: string): Promise<TimeTravelTimeline | null>;
    /**
     * Get all snapshots for a run
     */
    getTimeTravelSnapshots(runId: string, snapshotType?: string): Promise<TimeTravelSnapshot[]>;
    /**
     * Get a specific snapshot
     */
    getTimeTravelSnapshot(snapshotId: string): Promise<TimeTravelSnapshot | null>;
    /**
     * Get diff between two snapshots
     */
    getTimeTravelDiff(fromSnapshotId: string, toSnapshotId: string): Promise<TimeTravelDiff | null>;
    /**
     * Step back in time travel
     */
    timeTravelStepBack(runId: string, fromSnapshotId?: string): Promise<TimeTravelSnapshot | null>;
    /**
     * Step forward in time travel
     */
    timeTravelStepForward(runId: string, fromSnapshotId?: string): Promise<TimeTravelSnapshot | null>;
    /**
     * Start a replay from a snapshot
     */
    startTimeTravelReplay(snapshotId: string, modifiedInputs?: Record<string, unknown>): Promise<{
        replayId: string;
        message: string;
    }>;
    /**
     * Start what-if analysis
     */
    startWhatIfAnalysis(snapshotId: string, modifications: Record<string, unknown>): Promise<{
        whatIfId: string;
        message: string;
    }>;
    /**
     * Delete snapshots for a run
     */
    deleteTimeTravelSnapshots(runId: string): Promise<number>;
}
export interface MarketplaceListing {
    id: string;
    slug: string;
    name: string;
    tagline: string;
    description: string;
    category: string;
    tags: string[];
    status: string;
    publisher: MarketplacePublisher;
    pipeline_template: Record<string, unknown>;
    readme?: string;
    screenshots: Array<{
        id: string;
        url: string;
        caption?: string;
    }>;
    current_version: string;
    pricing: {
        model: string;
        price: number;
        currency: string;
    };
    stats: {
        views: number;
        downloads: number;
        favorites: number;
        reviews: number;
        average_rating: number;
    };
    created_at: string;
    updated_at: string;
    published_at?: string;
    featured: boolean;
}
export interface MarketplacePublisher {
    id: string;
    name: string;
    username: string;
    email?: string;
    avatar_url?: string;
    website?: string;
    verified: boolean;
    member_since: string;
    total_listings: number;
    total_downloads: number;
    average_rating: number;
}
export interface MarketplaceCategory {
    id: string;
    name: string;
    description: string;
    icon: string;
    listing_count: number;
}
export interface MarketplaceReview {
    id: string;
    listing_id: string;
    user_id: string;
    username: string;
    avatar_url?: string;
    rating: number;
    title: string;
    content: string;
    helpful_count: number;
    created_at: string;
    updated_at?: string;
    verified_purchase: boolean;
}
export interface MarketplaceInstallResult {
    id: string;
    listing_id: string;
    user_id: string;
    version: string;
    installed_at: string;
    pipeline_id?: string;
    customizations: Record<string, unknown>;
}
export interface MarketplaceStats {
    total_listings: number;
    total_publishers: number;
    total_downloads: number;
    total_reviews: number;
    categories: Record<string, number>;
    trending: string[];
    new_this_week: number;
}
export interface TimeTravelTimeline {
    run_id: string;
    pipeline_name: string;
    total_snapshots: number;
    current_position: number;
    stages: Array<{
        stage_id: string;
        stage_name: string;
        snapshot_count: number;
        status: string;
    }>;
    start_time: string;
    end_time?: string;
}
export interface TimeTravelSnapshot {
    id: string;
    run_id: string;
    stage_id: string;
    stage_name: string;
    snapshot_type: string;
    timestamp: string;
    sequence_number: number;
    state: {
        variables: Record<string, unknown>;
        outputs: Record<string, unknown>;
        completed_stages: string[];
    };
    metadata?: Record<string, unknown>;
}
export interface TimeTravelDiff {
    from_snapshot_id: string;
    to_snapshot_id: string;
    changes: {
        variables: {
            added: Record<string, unknown>;
            removed: string[];
            modified: Record<string, {
                old: unknown;
                new: unknown;
            }>;
        };
        outputs: {
            added: Record<string, unknown>;
            removed: string[];
            modified: Record<string, {
                old: unknown;
                new: unknown;
            }>;
        };
        stages_completed: string[];
    };
}
/**
 * Private package info (from private registry API)
 */
export interface PrivatePackageInfo {
    name: string;
    version: string;
    description: string;
    author?: string;
    author_email?: string;
    license?: string;
    homepage?: string;
    repository?: string;
    tags: string[];
    category?: string;
    org_id?: string;
    visibility: string;
    downloads: number;
    published_at?: string;
    published_by?: string;
    components: string[];
    component_count: number;
    download_url: string;
    checksum: string;
}
//# sourceMappingURL=flowmasonService.d.ts.map