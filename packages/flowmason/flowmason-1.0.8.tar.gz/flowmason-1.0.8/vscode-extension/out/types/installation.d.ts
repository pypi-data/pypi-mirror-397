/**
 * Shared types for FlowMason installation configuration
 */
/**
 * Installation info stored in ~/.flowmason/installation.json
 */
export interface InstallationInfo {
    install_path: string;
    python_path: string;
    version: string;
    studio_pid: number | null;
    studio_port: number;
    studio_host: string;
    studio_started_at: string | null;
    frontend_pid: number | null;
    frontend_port: number;
    frontend_started_at: string | null;
    last_updated: string | null;
}
export declare const CONFIG_DIR: string;
export declare const INSTALLATION_FILE: string;
export declare const DEFAULT_BACKEND_PORT = 8999;
export declare const DEFAULT_FRONTEND_PORT = 8199;
export declare const DEFAULT_HOST = "127.0.0.1";
/**
 * Read installation info from config file
 */
export declare function getInstallationInfo(): InstallationInfo | null;
/**
 * Update installation info
 */
export declare function updateInstallationInfo(updates: Partial<InstallationInfo>): void;
/**
 * Get the configured frontend port (from settings or installation.json)
 */
export declare function getFrontendPort(): number;
/**
 * Get the configured backend port (from settings or installation.json)
 */
export declare function getBackendPort(): number;
/**
 * Get the configured host
 */
export declare function getHost(): string;
/**
 * Check if a process is running by PID
 */
export declare function isProcessRunning(pid: number): boolean;
/**
 * Check if backend is running
 */
export declare function isBackendRunning(): Promise<boolean>;
/**
 * Check if frontend is running
 */
export declare function isFrontendRunning(): Promise<boolean>;
//# sourceMappingURL=installation.d.ts.map