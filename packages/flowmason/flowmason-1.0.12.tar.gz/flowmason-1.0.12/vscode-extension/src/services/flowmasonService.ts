/**
 * FlowMason Service
 *
 * Handles communication with FlowMason Studio API and local installation.
 */

import * as vscode from 'vscode';
import axios, { AxiosInstance } from 'axios';
import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';

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
    // Deprecated - use type for backwards compatibility
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
    // Backwards compatible fields
    recommended_providers?: string[];
    default_provider?: string;
    package_version?: string;
    registered_at?: string;
    // Runtime configuration
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

export class FlowMasonService {
    private client: AxiosInstance;
    private packagesDir: string;

    // Caches with TTL
    private componentDetailCache: Map<string, { data: ComponentDetail; timestamp: number }> = new Map();
    private providersCache: { data: Provider[]; timestamp: number } | null = null;
    private readonly CACHE_TTL_MS = 60000; // 1 minute cache

    constructor() {
        const config = vscode.workspace.getConfiguration('flowmason');
        const studioUrl = config.get<string>('studioUrl') || 'http://localhost:8999';

        this.client = axios.create({
            baseURL: studioUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Resolve packages directory
        const packagesPath = config.get<string>('packagesDirectory') || '~/.flowmason/packages';
        this.packagesDir = packagesPath.replace(/^~/, os.homedir());
    }

    /**
     * Clear all caches (useful after config changes)
     */
    clearCache(): void {
        this.componentDetailCache.clear();
        this.providersCache = null;
    }

    /**
     * Check if FlowMason Studio is running
     */
    async checkConnection(): Promise<boolean> {
        try {
            const response = await this.client.get('/health');
            return response.status === 200;
        } catch {
            return false;
        }
    }

    /**
     * Get all registered components from the API
     */
    async getComponents(): Promise<Component[]> {
        try {
            const response = await this.client.get('/api/v1/registry/components');
            return response.data.components || [];
        } catch (error) {
            console.error('Failed to fetch components:', error);
            return [];
        }
    }

    /**
     * Get component details by type (basic info)
     */
    async getComponent(componentType: string): Promise<Component | null> {
        try {
            const response = await this.client.get(`/api/v1/registry/components/${componentType}`);
            return response.data;
        } catch {
            return null;
        }
    }

    /**
     * Get full component detail including AI config (with caching)
     * This is the preferred method for the StageConfigEditor
     */
    async getComponentDetail(componentType: string): Promise<ComponentDetail | null> {
        // Check cache
        const cached = this.componentDetailCache.get(componentType);
        if (cached && (Date.now() - cached.timestamp) < this.CACHE_TTL_MS) {
            return cached.data;
        }

        try {
            const response = await this.client.get(`/api/v1/registry/components/${componentType}`);
            const data: ComponentDetail = response.data;

            // Cache the result
            this.componentDetailCache.set(componentType, {
                data,
                timestamp: Date.now()
            });

            return data;
        } catch (error) {
            console.error(`Failed to fetch component detail for ${componentType}:`, error);
            return null;
        }
    }

    /**
     * Get all available LLM providers (with caching)
     */
    async getProviders(): Promise<Provider[]> {
        // Check cache
        if (this.providersCache && (Date.now() - this.providersCache.timestamp) < this.CACHE_TTL_MS) {
            return this.providersCache.data;
        }

        try {
            const response = await this.client.get('/api/v1/providers');
            const providers: Provider[] = response.data.providers || [];

            // Cache the result
            this.providersCache = {
                data: providers,
                timestamp: Date.now()
            };

            return providers;
        } catch (error) {
            console.error('Failed to fetch providers:', error);
            return [];
        }
    }

    /**
     * Get available models for a specific provider
     */
    async getProviderModels(providerName: string): Promise<{ models: string[]; default_model: string } | null> {
        try {
            const response = await this.client.get(`/api/v1/providers/${providerName}/models`);
            return {
                models: response.data.models || [],
                default_model: response.data.default_model || ''
            };
        } catch (error) {
            console.error(`Failed to fetch models for provider ${providerName}:`, error);
            return null;
        }
    }

    /**
     * Test a provider connection
     */
    async testProvider(providerName: string): Promise<{ success: boolean; message: string }> {
        try {
            const response = await this.client.post(`/api/v1/providers/${providerName}/test`, {});
            return {
                success: response.data.success,
                message: response.data.message
            };
        } catch (error) {
            const axiosError = error as { response?: { data?: { detail?: string } }; message?: string };
            return {
                success: false,
                message: axiosError.response?.data?.detail || axiosError.message || 'Connection failed'
            };
        }
    }

    /**
     * Get all pipelines
     */
    async getPipelines(): Promise<Pipeline[]> {
        try {
            const response = await this.client.get('/api/v1/pipelines');
            return response.data.pipelines || [];
        } catch (error) {
            console.error('Failed to fetch pipelines:', error);
            return [];
        }
    }

    /**
     * Test a component with sample input
     */
    async testComponent(
        componentType: string,
        config: Record<string, unknown>,
        input: Record<string, unknown>
    ): Promise<TestResult> {
        try {
            const response = await this.client.post('/api/v1/components/test', {
                component_type: componentType,
                config,
                input,
            });
            return {
                success: true,
                output: response.data.output,
                duration_ms: response.data.duration_ms,
                usage: response.data.usage,
            };
        } catch (error: unknown) {
            const axiosError = error as { response?: { data?: { detail?: string } }; message?: string };
            return {
                success: false,
                error: axiosError.response?.data?.detail || axiosError.message || 'Unknown error',
            };
        }
    }

    /**
     * Get installed packages from the local packages directory
     */
    async getLocalPackages(): Promise<Package[]> {
        const packages: Package[] = [];

        if (!fs.existsSync(this.packagesDir)) {
            return packages;
        }

        const entries = fs.readdirSync(this.packagesDir, { withFileTypes: true });

        for (const entry of entries) {
            if (entry.isDirectory()) {
                const packagePath = path.join(this.packagesDir, entry.name);
                const manifestPath = path.join(packagePath, 'flowmason-package.json');

                if (fs.existsSync(manifestPath)) {
                    try {
                        const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
                        packages.push({
                            id: manifest.id || entry.name,
                            name: manifest.name || entry.name,
                            version: manifest.version || '1.0.0',
                            description: manifest.description || '',
                            author: manifest.author,
                            components: manifest.components || [],
                            path: packagePath,
                        });
                    } catch {
                        // Skip invalid packages
                    }
                }
            }
        }

        return packages;
    }

    /**
     * Deploy a package to the local packages directory
     */
    async deployPackage(packagePath: string): Promise<{ success: boolean; error?: string }> {
        try {
            // Read the package manifest
            const manifestPath = path.join(packagePath, 'flowmason-package.json');
            if (!fs.existsSync(manifestPath)) {
                return { success: false, error: 'Package manifest not found' };
            }

            const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
            const packageId = manifest.id || path.basename(packagePath);
            const targetDir = path.join(this.packagesDir, packageId);

            // Create packages directory if it doesn't exist
            if (!fs.existsSync(this.packagesDir)) {
                fs.mkdirSync(this.packagesDir, { recursive: true });
            }

            // Remove existing package if present
            if (fs.existsSync(targetDir)) {
                fs.rmSync(targetDir, { recursive: true });
            }

            // Copy package to target directory
            this.copyDirectory(packagePath, targetDir);

            return { success: true };
        } catch (error: unknown) {
            const err = error as { message?: string };
            return { success: false, error: err.message || 'Failed to deploy package' };
        }
    }

    /**
     * Helper to copy a directory recursively
     */
    private copyDirectory(src: string, dest: string): void {
        fs.mkdirSync(dest, { recursive: true });
        const entries = fs.readdirSync(src, { withFileTypes: true });

        for (const entry of entries) {
            const srcPath = path.join(src, entry.name);
            const destPath = path.join(dest, entry.name);

            if (entry.isDirectory()) {
                this.copyDirectory(srcPath, destPath);
            } else {
                fs.copyFileSync(srcPath, destPath);
            }
        }
    }

    /**
     * Open FlowMason Studio in browser
     */
    openStudio(): void {
        const config = vscode.workspace.getConfiguration('flowmason');
        const studioUrl = config.get<string>('studioUrl') || 'http://localhost:8999';
        vscode.env.openExternal(vscode.Uri.parse(studioUrl));
    }

    /**
     * Get the packages directory path
     */
    getPackagesDirectory(): string {
        return this.packagesDir;
    }

    // =========================================================================
    // Private Package Registry
    // =========================================================================

    /**
     * Publish a package to the private registry
     */
    async publishToPrivateRegistry(
        packagePath: string,
        visibility: string = 'public'
    ): Promise<PrivatePackageInfo> {
        const formData = new FormData();
        const fileBuffer = fs.readFileSync(packagePath);
        const fileName = path.basename(packagePath);

        // Create a Blob from the buffer
        const blob = new Blob([fileBuffer], { type: 'application/octet-stream' });
        formData.append('file', blob, fileName);
        formData.append('visibility', visibility);

        const response = await this.client.post<PrivatePackageInfo>(
            '/private-registry/packages/publish',
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );
        return response.data;
    }

    /**
     * List packages in the private registry
     */
    async listPrivatePackages(
        options: {
            category?: string;
            query?: string;
            includePrivate?: boolean;
        } = {}
    ): Promise<{ packages: PrivatePackageInfo[]; total: number }> {
        const params = new URLSearchParams();
        if (options.category) params.append('category', options.category);
        if (options.query) params.append('q', options.query);
        if (options.includePrivate) params.append('include_private', 'true');

        const response = await this.client.get<{ packages: PrivatePackageInfo[]; total: number }>(
            `/private-registry/packages?${params.toString()}`
        );
        return response.data;
    }

    /**
     * Get a specific package from the private registry
     */
    async getPrivatePackage(name: string, version?: string): Promise<PrivatePackageInfo> {
        const url = version
            ? `/private-registry/packages/${name}/${version}`
            : `/private-registry/packages/${name}`;
        const response = await this.client.get<PrivatePackageInfo>(url);
        return response.data;
    }

    /**
     * Get all versions of a package
     */
    async getPrivatePackageVersions(name: string): Promise<{ name: string; versions: string[]; latest: string }> {
        const response = await this.client.get<{ name: string; versions: string[]; latest: string }>(
            `/private-registry/packages/${name}/versions`
        );
        return response.data;
    }

    /**
     * Download a package from the private registry
     */
    async downloadPrivatePackage(name: string, version: string): Promise<Buffer> {
        const response = await this.client.get<ArrayBuffer>(
            `/private-registry/packages/${name}/${version}/download`,
            { responseType: 'arraybuffer' }
        );
        return Buffer.from(response.data);
    }

    /**
     * Delete a package from the private registry
     */
    async deletePrivatePackage(name: string, version: string): Promise<void> {
        await this.client.delete(`/private-registry/packages/${name}/${version}`);
    }

    /**
     * Get private registry statistics
     */
    async getPrivateRegistryStats(): Promise<{
        packages_count: number;
        components_count: number;
        total_downloads: number;
        categories: Record<string, number>;
    }> {
        const response = await this.client.get<{
            packages_count: number;
            components_count: number;
            total_downloads: number;
            categories: Record<string, number>;
        }>('/private-registry/stats');
        return response.data;
    }

    /**
     * Grant access to a private package
     */
    async grantPackageAccess(
        name: string,
        userId: string,
        accessLevel: 'read' | 'write' | 'admin'
    ): Promise<void> {
        await this.client.post(`/private-registry/packages/${name}/access`, {
            user_id: userId,
            access_level: accessLevel,
        });
    }

    /**
     * Revoke access to a private package
     */
    async revokePackageAccess(name: string, userId: string): Promise<void> {
        await this.client.delete(`/private-registry/packages/${name}/access/${userId}`);
    }

    /**
     * Change package visibility
     */
    async setPackageVisibility(
        name: string,
        visibility: 'public' | 'private' | 'unlisted'
    ): Promise<void> {
        await this.client.patch(`/private-registry/packages/${name}/visibility`, {
            visibility,
        });
    }

    // =========================================================================
    // Public Marketplace
    // =========================================================================

    /**
     * Search the marketplace
     */
    async searchMarketplace(
        query: string,
        options: {
            category?: string;
            pricing?: string;
            minRating?: number;
            sortBy?: string;
            page?: number;
            perPage?: number;
        } = {}
    ): Promise<{ listings: MarketplaceListing[]; total: number }> {
        try {
            const params = new URLSearchParams();
            if (query) params.append('query', query);
            if (options.category) params.append('category', options.category);
            if (options.pricing) params.append('pricing', options.pricing);
            if (options.minRating) params.append('min_rating', options.minRating.toString());
            if (options.sortBy) params.append('sort_by', options.sortBy);
            if (options.page) params.append('page', options.page.toString());
            if (options.perPage) params.append('per_page', options.perPage.toString());

            const response = await this.client.get(`/api/v1/marketplace/search?${params.toString()}`);
            return {
                listings: response.data.listings || [],
                total: response.data.total || 0,
            };
        } catch (error) {
            console.error('Failed to search marketplace:', error);
            return { listings: [], total: 0 };
        }
    }

    /**
     * Get featured marketplace listings
     */
    async getMarketplaceFeatured(limit: number = 10): Promise<MarketplaceListing[]> {
        try {
            const response = await this.client.get(`/api/v1/marketplace/featured?limit=${limit}`);
            return response.data || [];
        } catch (error) {
            console.error('Failed to fetch featured listings:', error);
            return [];
        }
    }

    /**
     * Get trending marketplace listings
     */
    async getMarketplaceTrending(limit: number = 10): Promise<MarketplaceListing[]> {
        try {
            const response = await this.client.get(`/api/v1/marketplace/trending?limit=${limit}`);
            return response.data || [];
        } catch (error) {
            console.error('Failed to fetch trending listings:', error);
            return [];
        }
    }

    /**
     * Get new marketplace listings
     */
    async getMarketplaceNew(limit: number = 10): Promise<MarketplaceListing[]> {
        try {
            const response = await this.client.get(`/api/v1/marketplace/new?limit=${limit}`);
            return response.data || [];
        } catch (error) {
            console.error('Failed to fetch new listings:', error);
            return [];
        }
    }

    /**
     * Get marketplace categories
     */
    async getMarketplaceCategories(): Promise<MarketplaceCategory[]> {
        try {
            const response = await this.client.get('/api/v1/marketplace/categories');
            return response.data || [];
        } catch (error) {
            console.error('Failed to fetch marketplace categories:', error);
            return [];
        }
    }

    /**
     * Get listings by category
     */
    async getMarketplaceByCategory(categoryId: string, limit: number = 20): Promise<MarketplaceListing[]> {
        try {
            const response = await this.client.get(`/api/v1/marketplace/categories/${categoryId}?limit=${limit}`);
            return response.data || [];
        } catch (error) {
            console.error('Failed to fetch category listings:', error);
            return [];
        }
    }

    /**
     * Get a specific marketplace listing
     */
    async getMarketplaceListing(listingId: string): Promise<MarketplaceListing | null> {
        try {
            const response = await this.client.get(`/api/v1/marketplace/listings/${listingId}`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch listing:', error);
            return null;
        }
    }

    /**
     * Get marketplace listing by slug
     */
    async getMarketplaceListingBySlug(slug: string): Promise<MarketplaceListing | null> {
        try {
            const response = await this.client.get(`/api/v1/marketplace/listings/by-slug/${slug}`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch listing by slug:', error);
            return null;
        }
    }

    /**
     * Install a marketplace listing
     */
    async installMarketplaceListing(
        listingId: string,
        options: {
            version?: string;
            pipeline_name?: string;
            create_pipeline?: boolean;
            customizations?: Record<string, unknown>;
        } = {}
    ): Promise<MarketplaceInstallResult> {
        const response = await this.client.post(`/api/v1/marketplace/listings/${listingId}/install`, {
            version: options.version,
            pipeline_name: options.pipeline_name,
            create_pipeline: options.create_pipeline ?? true,
            customizations: options.customizations || {},
        });
        return response.data;
    }

    /**
     * Get a publisher profile
     */
    async getMarketplacePublisher(publisherId: string): Promise<MarketplacePublisher | null> {
        try {
            const response = await this.client.get(`/api/v1/marketplace/publishers/${publisherId}`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch publisher:', error);
            return null;
        }
    }

    /**
     * Add listing to favorites
     */
    async addMarketplaceFavorite(listingId: string): Promise<void> {
        await this.client.post(`/api/v1/marketplace/library/favorites/${listingId}`);
    }

    /**
     * Remove listing from favorites
     */
    async removeMarketplaceFavorite(listingId: string): Promise<void> {
        await this.client.delete(`/api/v1/marketplace/library/favorites/${listingId}`);
    }

    /**
     * Get user's marketplace library
     */
    async getMarketplaceLibrary(): Promise<{
        purchased: string[];
        favorites: string[];
        installed: string[];
    }> {
        try {
            const response = await this.client.get('/api/v1/marketplace/library');
            return response.data;
        } catch (error) {
            console.error('Failed to fetch library:', error);
            return { purchased: [], favorites: [], installed: [] };
        }
    }

    /**
     * Get marketplace statistics
     */
    async getMarketplaceStats(): Promise<MarketplaceStats> {
        try {
            const response = await this.client.get('/api/v1/marketplace/stats');
            return response.data;
        } catch (error) {
            console.error('Failed to fetch marketplace stats:', error);
            return {
                total_listings: 0,
                total_publishers: 0,
                total_downloads: 0,
                total_reviews: 0,
                categories: {},
                trending: [],
                new_this_week: 0,
            };
        }
    }

    /**
     * Get reviews for a listing
     */
    async getMarketplaceReviews(
        listingId: string,
        options: { limit?: number; offset?: number } = {}
    ): Promise<MarketplaceReview[]> {
        try {
            const params = new URLSearchParams();
            if (options.limit) params.append('limit', options.limit.toString());
            if (options.offset) params.append('offset', options.offset.toString());

            const response = await this.client.get(
                `/api/v1/marketplace/listings/${listingId}/reviews?${params.toString()}`
            );
            return response.data || [];
        } catch (error) {
            console.error('Failed to fetch reviews:', error);
            return [];
        }
    }

    /**
     * Submit a review for a listing
     */
    async submitMarketplaceReview(
        listingId: string,
        review: { rating: number; title: string; content: string }
    ): Promise<MarketplaceReview> {
        const response = await this.client.post(
            `/api/v1/marketplace/listings/${listingId}/reviews`,
            review
        );
        return response.data;
    }

    // =========================================================================
    // Time Travel Debugging
    // =========================================================================

    /**
     * Get execution timeline for a run
     */
    async getTimeTravelTimeline(runId: string): Promise<TimeTravelTimeline | null> {
        try {
            const response = await this.client.get(`/api/v1/debug/time-travel/runs/${runId}/timeline`);
            return response.data.timeline;
        } catch (error) {
            console.error('Failed to fetch timeline:', error);
            return null;
        }
    }

    /**
     * Get all snapshots for a run
     */
    async getTimeTravelSnapshots(
        runId: string,
        snapshotType?: string
    ): Promise<TimeTravelSnapshot[]> {
        try {
            const params = new URLSearchParams();
            if (snapshotType) params.append('snapshot_type', snapshotType);

            const response = await this.client.get(
                `/api/v1/debug/time-travel/runs/${runId}/snapshots?${params.toString()}`
            );
            return response.data.snapshots || [];
        } catch (error) {
            console.error('Failed to fetch snapshots:', error);
            return [];
        }
    }

    /**
     * Get a specific snapshot
     */
    async getTimeTravelSnapshot(snapshotId: string): Promise<TimeTravelSnapshot | null> {
        try {
            const response = await this.client.get(`/api/v1/debug/time-travel/snapshots/${snapshotId}`);
            return response.data.snapshot;
        } catch (error) {
            console.error('Failed to fetch snapshot:', error);
            return null;
        }
    }

    /**
     * Get diff between two snapshots
     */
    async getTimeTravelDiff(
        fromSnapshotId: string,
        toSnapshotId: string
    ): Promise<TimeTravelDiff | null> {
        try {
            const response = await this.client.get(
                `/api/v1/debug/time-travel/diff?from_snapshot=${fromSnapshotId}&to_snapshot=${toSnapshotId}`
            );
            return response.data.diff;
        } catch (error) {
            console.error('Failed to get diff:', error);
            return null;
        }
    }

    /**
     * Step back in time travel
     */
    async timeTravelStepBack(
        runId: string,
        fromSnapshotId?: string
    ): Promise<TimeTravelSnapshot | null> {
        try {
            const params = fromSnapshotId ? `?from_snapshot=${fromSnapshotId}` : '';
            const response = await this.client.get(`/api/v1/debug/time-travel/runs/${runId}/step-back${params}`);
            return response.data.snapshot;
        } catch (error) {
            console.error('Failed to step back:', error);
            return null;
        }
    }

    /**
     * Step forward in time travel
     */
    async timeTravelStepForward(
        runId: string,
        fromSnapshotId?: string
    ): Promise<TimeTravelSnapshot | null> {
        try {
            const params = fromSnapshotId ? `?from_snapshot=${fromSnapshotId}` : '';
            const response = await this.client.get(`/api/v1/debug/time-travel/runs/${runId}/step-forward${params}`);
            return response.data.snapshot;
        } catch (error) {
            console.error('Failed to step forward:', error);
            return null;
        }
    }

    /**
     * Start a replay from a snapshot
     */
    async startTimeTravelReplay(
        snapshotId: string,
        modifiedInputs?: Record<string, unknown>
    ): Promise<{ replayId: string; message: string }> {
        const response = await this.client.post('/api/v1/debug/time-travel/replay', {
            snapshot_id: snapshotId,
            modified_inputs: modifiedInputs,
        });
        return {
            replayId: response.data.result?.whatif_run_id || response.data.result?.replay_run_id,
            message: response.data.message,
        };
    }

    /**
     * Start what-if analysis
     */
    async startWhatIfAnalysis(
        snapshotId: string,
        modifications: Record<string, unknown>
    ): Promise<{ whatIfId: string; message: string }> {
        const response = await this.client.post('/api/v1/debug/time-travel/whatif', {
            snapshot_id: snapshotId,
            modifications,
        });
        return {
            whatIfId: response.data.result?.whatif_run_id,
            message: response.data.message,
        };
    }

    /**
     * Delete snapshots for a run
     */
    async deleteTimeTravelSnapshots(runId: string): Promise<number> {
        const response = await this.client.delete(`/api/v1/debug/time-travel/runs/${runId}/snapshots`);
        return response.data.deleted_count || 0;
    }
}

// =========================================================================
// Marketplace Types
// =========================================================================

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
    screenshots: Array<{ id: string; url: string; caption?: string }>;
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

// =========================================================================
// Time Travel Types
// =========================================================================

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
            modified: Record<string, { old: unknown; new: unknown }>;
        };
        outputs: {
            added: Record<string, unknown>;
            removed: string[];
            modified: Record<string, { old: unknown; new: unknown }>;
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
