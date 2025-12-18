"use strict";
/**
 * FlowMason Service
 *
 * Handles communication with FlowMason Studio API and local installation.
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowMasonService = void 0;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const os = __importStar(require("os"));
class FlowMasonService {
    constructor() {
        // Caches with TTL
        this.componentDetailCache = new Map();
        this.providersCache = null;
        this.CACHE_TTL_MS = 60000; // 1 minute cache
        const config = vscode.workspace.getConfiguration('flowmason');
        const studioUrl = config.get('studioUrl') || 'http://localhost:8999';
        this.client = axios_1.default.create({
            baseURL: studioUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });
        // Resolve packages directory
        const packagesPath = config.get('packagesDirectory') || '~/.flowmason/packages';
        this.packagesDir = packagesPath.replace(/^~/, os.homedir());
    }
    /**
     * Clear all caches (useful after config changes)
     */
    clearCache() {
        this.componentDetailCache.clear();
        this.providersCache = null;
    }
    /**
     * Check if FlowMason Studio is running
     */
    async checkConnection() {
        try {
            const response = await this.client.get('/health');
            return response.status === 200;
        }
        catch {
            return false;
        }
    }
    /**
     * Get all registered components from the API
     */
    async getComponents() {
        try {
            const response = await this.client.get('/api/v1/registry/components');
            return response.data.components || [];
        }
        catch (error) {
            console.error('Failed to fetch components:', error);
            return [];
        }
    }
    /**
     * Get component details by type (basic info)
     */
    async getComponent(componentType) {
        try {
            const response = await this.client.get(`/api/v1/registry/components/${componentType}`);
            return response.data;
        }
        catch {
            return null;
        }
    }
    /**
     * Get full component detail including AI config (with caching)
     * This is the preferred method for the StageConfigEditor
     */
    async getComponentDetail(componentType) {
        // Check cache
        const cached = this.componentDetailCache.get(componentType);
        if (cached && (Date.now() - cached.timestamp) < this.CACHE_TTL_MS) {
            return cached.data;
        }
        try {
            const response = await this.client.get(`/api/v1/registry/components/${componentType}`);
            const data = response.data;
            // Cache the result
            this.componentDetailCache.set(componentType, {
                data,
                timestamp: Date.now()
            });
            return data;
        }
        catch (error) {
            console.error(`Failed to fetch component detail for ${componentType}:`, error);
            return null;
        }
    }
    /**
     * Get all available LLM providers (with caching)
     */
    async getProviders() {
        // Check cache
        if (this.providersCache && (Date.now() - this.providersCache.timestamp) < this.CACHE_TTL_MS) {
            return this.providersCache.data;
        }
        try {
            const response = await this.client.get('/api/v1/providers');
            const providers = response.data.providers || [];
            // Cache the result
            this.providersCache = {
                data: providers,
                timestamp: Date.now()
            };
            return providers;
        }
        catch (error) {
            console.error('Failed to fetch providers:', error);
            return [];
        }
    }
    /**
     * Get available models for a specific provider
     */
    async getProviderModels(providerName) {
        try {
            const response = await this.client.get(`/api/v1/providers/${providerName}/models`);
            return {
                models: response.data.models || [],
                default_model: response.data.default_model || ''
            };
        }
        catch (error) {
            console.error(`Failed to fetch models for provider ${providerName}:`, error);
            return null;
        }
    }
    /**
     * Test a provider connection
     */
    async testProvider(providerName) {
        try {
            const response = await this.client.post(`/api/v1/providers/${providerName}/test`, {});
            return {
                success: response.data.success,
                message: response.data.message
            };
        }
        catch (error) {
            const axiosError = error;
            return {
                success: false,
                message: axiosError.response?.data?.detail || axiosError.message || 'Connection failed'
            };
        }
    }
    /**
     * Get all pipelines
     */
    async getPipelines() {
        try {
            const response = await this.client.get('/api/v1/pipelines');
            return response.data.pipelines || [];
        }
        catch (error) {
            console.error('Failed to fetch pipelines:', error);
            return [];
        }
    }
    /**
     * Test a component with sample input
     */
    async testComponent(componentType, config, input) {
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
        }
        catch (error) {
            const axiosError = error;
            return {
                success: false,
                error: axiosError.response?.data?.detail || axiosError.message || 'Unknown error',
            };
        }
    }
    /**
     * Get installed packages from the local packages directory
     */
    async getLocalPackages() {
        const packages = [];
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
                    }
                    catch {
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
    async deployPackage(packagePath) {
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
        }
        catch (error) {
            const err = error;
            return { success: false, error: err.message || 'Failed to deploy package' };
        }
    }
    /**
     * Helper to copy a directory recursively
     */
    copyDirectory(src, dest) {
        fs.mkdirSync(dest, { recursive: true });
        const entries = fs.readdirSync(src, { withFileTypes: true });
        for (const entry of entries) {
            const srcPath = path.join(src, entry.name);
            const destPath = path.join(dest, entry.name);
            if (entry.isDirectory()) {
                this.copyDirectory(srcPath, destPath);
            }
            else {
                fs.copyFileSync(srcPath, destPath);
            }
        }
    }
    /**
     * Open FlowMason Studio in browser
     */
    openStudio() {
        const config = vscode.workspace.getConfiguration('flowmason');
        const studioUrl = config.get('studioUrl') || 'http://localhost:8999';
        vscode.env.openExternal(vscode.Uri.parse(studioUrl));
    }
    /**
     * Get the packages directory path
     */
    getPackagesDirectory() {
        return this.packagesDir;
    }
    // =========================================================================
    // Private Package Registry
    // =========================================================================
    /**
     * Publish a package to the private registry
     */
    async publishToPrivateRegistry(packagePath, visibility = 'public') {
        const formData = new FormData();
        const fileBuffer = fs.readFileSync(packagePath);
        const fileName = path.basename(packagePath);
        // Create a Blob from the buffer
        const blob = new Blob([fileBuffer], { type: 'application/octet-stream' });
        formData.append('file', blob, fileName);
        formData.append('visibility', visibility);
        const response = await this.client.post('/private-registry/packages/publish', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }
    /**
     * List packages in the private registry
     */
    async listPrivatePackages(options = {}) {
        const params = new URLSearchParams();
        if (options.category)
            params.append('category', options.category);
        if (options.query)
            params.append('q', options.query);
        if (options.includePrivate)
            params.append('include_private', 'true');
        const response = await this.client.get(`/private-registry/packages?${params.toString()}`);
        return response.data;
    }
    /**
     * Get a specific package from the private registry
     */
    async getPrivatePackage(name, version) {
        const url = version
            ? `/private-registry/packages/${name}/${version}`
            : `/private-registry/packages/${name}`;
        const response = await this.client.get(url);
        return response.data;
    }
    /**
     * Get all versions of a package
     */
    async getPrivatePackageVersions(name) {
        const response = await this.client.get(`/private-registry/packages/${name}/versions`);
        return response.data;
    }
    /**
     * Download a package from the private registry
     */
    async downloadPrivatePackage(name, version) {
        const response = await this.client.get(`/private-registry/packages/${name}/${version}/download`, { responseType: 'arraybuffer' });
        return Buffer.from(response.data);
    }
    /**
     * Delete a package from the private registry
     */
    async deletePrivatePackage(name, version) {
        await this.client.delete(`/private-registry/packages/${name}/${version}`);
    }
    /**
     * Get private registry statistics
     */
    async getPrivateRegistryStats() {
        const response = await this.client.get('/private-registry/stats');
        return response.data;
    }
    /**
     * Grant access to a private package
     */
    async grantPackageAccess(name, userId, accessLevel) {
        await this.client.post(`/private-registry/packages/${name}/access`, {
            user_id: userId,
            access_level: accessLevel,
        });
    }
    /**
     * Revoke access to a private package
     */
    async revokePackageAccess(name, userId) {
        await this.client.delete(`/private-registry/packages/${name}/access/${userId}`);
    }
    /**
     * Change package visibility
     */
    async setPackageVisibility(name, visibility) {
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
    async searchMarketplace(query, options = {}) {
        try {
            const params = new URLSearchParams();
            if (query)
                params.append('query', query);
            if (options.category)
                params.append('category', options.category);
            if (options.pricing)
                params.append('pricing', options.pricing);
            if (options.minRating)
                params.append('min_rating', options.minRating.toString());
            if (options.sortBy)
                params.append('sort_by', options.sortBy);
            if (options.page)
                params.append('page', options.page.toString());
            if (options.perPage)
                params.append('per_page', options.perPage.toString());
            const response = await this.client.get(`/api/v1/marketplace/search?${params.toString()}`);
            return {
                listings: response.data.listings || [],
                total: response.data.total || 0,
            };
        }
        catch (error) {
            console.error('Failed to search marketplace:', error);
            return { listings: [], total: 0 };
        }
    }
    /**
     * Get featured marketplace listings
     */
    async getMarketplaceFeatured(limit = 10) {
        try {
            const response = await this.client.get(`/api/v1/marketplace/featured?limit=${limit}`);
            return response.data || [];
        }
        catch (error) {
            console.error('Failed to fetch featured listings:', error);
            return [];
        }
    }
    /**
     * Get trending marketplace listings
     */
    async getMarketplaceTrending(limit = 10) {
        try {
            const response = await this.client.get(`/api/v1/marketplace/trending?limit=${limit}`);
            return response.data || [];
        }
        catch (error) {
            console.error('Failed to fetch trending listings:', error);
            return [];
        }
    }
    /**
     * Get new marketplace listings
     */
    async getMarketplaceNew(limit = 10) {
        try {
            const response = await this.client.get(`/api/v1/marketplace/new?limit=${limit}`);
            return response.data || [];
        }
        catch (error) {
            console.error('Failed to fetch new listings:', error);
            return [];
        }
    }
    /**
     * Get marketplace categories
     */
    async getMarketplaceCategories() {
        try {
            const response = await this.client.get('/api/v1/marketplace/categories');
            return response.data || [];
        }
        catch (error) {
            console.error('Failed to fetch marketplace categories:', error);
            return [];
        }
    }
    /**
     * Get listings by category
     */
    async getMarketplaceByCategory(categoryId, limit = 20) {
        try {
            const response = await this.client.get(`/api/v1/marketplace/categories/${categoryId}?limit=${limit}`);
            return response.data || [];
        }
        catch (error) {
            console.error('Failed to fetch category listings:', error);
            return [];
        }
    }
    /**
     * Get a specific marketplace listing
     */
    async getMarketplaceListing(listingId) {
        try {
            const response = await this.client.get(`/api/v1/marketplace/listings/${listingId}`);
            return response.data;
        }
        catch (error) {
            console.error('Failed to fetch listing:', error);
            return null;
        }
    }
    /**
     * Get marketplace listing by slug
     */
    async getMarketplaceListingBySlug(slug) {
        try {
            const response = await this.client.get(`/api/v1/marketplace/listings/by-slug/${slug}`);
            return response.data;
        }
        catch (error) {
            console.error('Failed to fetch listing by slug:', error);
            return null;
        }
    }
    /**
     * Install a marketplace listing
     */
    async installMarketplaceListing(listingId, options = {}) {
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
    async getMarketplacePublisher(publisherId) {
        try {
            const response = await this.client.get(`/api/v1/marketplace/publishers/${publisherId}`);
            return response.data;
        }
        catch (error) {
            console.error('Failed to fetch publisher:', error);
            return null;
        }
    }
    /**
     * Add listing to favorites
     */
    async addMarketplaceFavorite(listingId) {
        await this.client.post(`/api/v1/marketplace/library/favorites/${listingId}`);
    }
    /**
     * Remove listing from favorites
     */
    async removeMarketplaceFavorite(listingId) {
        await this.client.delete(`/api/v1/marketplace/library/favorites/${listingId}`);
    }
    /**
     * Get user's marketplace library
     */
    async getMarketplaceLibrary() {
        try {
            const response = await this.client.get('/api/v1/marketplace/library');
            return response.data;
        }
        catch (error) {
            console.error('Failed to fetch library:', error);
            return { purchased: [], favorites: [], installed: [] };
        }
    }
    /**
     * Get marketplace statistics
     */
    async getMarketplaceStats() {
        try {
            const response = await this.client.get('/api/v1/marketplace/stats');
            return response.data;
        }
        catch (error) {
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
    async getMarketplaceReviews(listingId, options = {}) {
        try {
            const params = new URLSearchParams();
            if (options.limit)
                params.append('limit', options.limit.toString());
            if (options.offset)
                params.append('offset', options.offset.toString());
            const response = await this.client.get(`/api/v1/marketplace/listings/${listingId}/reviews?${params.toString()}`);
            return response.data || [];
        }
        catch (error) {
            console.error('Failed to fetch reviews:', error);
            return [];
        }
    }
    /**
     * Submit a review for a listing
     */
    async submitMarketplaceReview(listingId, review) {
        const response = await this.client.post(`/api/v1/marketplace/listings/${listingId}/reviews`, review);
        return response.data;
    }
    // =========================================================================
    // Time Travel Debugging
    // =========================================================================
    /**
     * Get execution timeline for a run
     */
    async getTimeTravelTimeline(runId) {
        try {
            const response = await this.client.get(`/api/v1/debug/time-travel/runs/${runId}/timeline`);
            return response.data.timeline;
        }
        catch (error) {
            console.error('Failed to fetch timeline:', error);
            return null;
        }
    }
    /**
     * Get all snapshots for a run
     */
    async getTimeTravelSnapshots(runId, snapshotType) {
        try {
            const params = new URLSearchParams();
            if (snapshotType)
                params.append('snapshot_type', snapshotType);
            const response = await this.client.get(`/api/v1/debug/time-travel/runs/${runId}/snapshots?${params.toString()}`);
            return response.data.snapshots || [];
        }
        catch (error) {
            console.error('Failed to fetch snapshots:', error);
            return [];
        }
    }
    /**
     * Get a specific snapshot
     */
    async getTimeTravelSnapshot(snapshotId) {
        try {
            const response = await this.client.get(`/api/v1/debug/time-travel/snapshots/${snapshotId}`);
            return response.data.snapshot;
        }
        catch (error) {
            console.error('Failed to fetch snapshot:', error);
            return null;
        }
    }
    /**
     * Get diff between two snapshots
     */
    async getTimeTravelDiff(fromSnapshotId, toSnapshotId) {
        try {
            const response = await this.client.get(`/api/v1/debug/time-travel/diff?from_snapshot=${fromSnapshotId}&to_snapshot=${toSnapshotId}`);
            return response.data.diff;
        }
        catch (error) {
            console.error('Failed to get diff:', error);
            return null;
        }
    }
    /**
     * Step back in time travel
     */
    async timeTravelStepBack(runId, fromSnapshotId) {
        try {
            const params = fromSnapshotId ? `?from_snapshot=${fromSnapshotId}` : '';
            const response = await this.client.get(`/api/v1/debug/time-travel/runs/${runId}/step-back${params}`);
            return response.data.snapshot;
        }
        catch (error) {
            console.error('Failed to step back:', error);
            return null;
        }
    }
    /**
     * Step forward in time travel
     */
    async timeTravelStepForward(runId, fromSnapshotId) {
        try {
            const params = fromSnapshotId ? `?from_snapshot=${fromSnapshotId}` : '';
            const response = await this.client.get(`/api/v1/debug/time-travel/runs/${runId}/step-forward${params}`);
            return response.data.snapshot;
        }
        catch (error) {
            console.error('Failed to step forward:', error);
            return null;
        }
    }
    /**
     * Start a replay from a snapshot
     */
    async startTimeTravelReplay(snapshotId, modifiedInputs) {
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
    async startWhatIfAnalysis(snapshotId, modifications) {
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
    async deleteTimeTravelSnapshots(runId) {
        const response = await this.client.delete(`/api/v1/debug/time-travel/runs/${runId}/snapshots`);
        return response.data.deleted_count || 0;
    }
}
exports.FlowMasonService = FlowMasonService;
//# sourceMappingURL=flowmasonService.js.map