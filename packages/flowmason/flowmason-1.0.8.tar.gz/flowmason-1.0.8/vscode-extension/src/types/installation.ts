/**
 * Shared types for FlowMason installation configuration
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';

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

// Constants
export const CONFIG_DIR = path.join(os.homedir(), '.flowmason');
export const INSTALLATION_FILE = path.join(CONFIG_DIR, 'installation.json');
export const DEFAULT_BACKEND_PORT = 8999;
export const DEFAULT_FRONTEND_PORT = 8199;
export const DEFAULT_HOST = '127.0.0.1';

/**
 * Read installation info from config file
 */
export function getInstallationInfo(): InstallationInfo | null {
    try {
        if (fs.existsSync(INSTALLATION_FILE)) {
            const content = fs.readFileSync(INSTALLATION_FILE, 'utf-8');
            return JSON.parse(content);
        }
    } catch {
        // File doesn't exist or is invalid
    }
    return null;
}

/**
 * Update installation info
 */
export function updateInstallationInfo(updates: Partial<InstallationInfo>): void {
    let info = getInstallationInfo() || {
        install_path: '',
        python_path: 'python',
        version: '0.0.0',
        studio_pid: null,
        studio_port: DEFAULT_BACKEND_PORT,
        studio_host: DEFAULT_HOST,
        studio_started_at: null,
        frontend_pid: null,
        frontend_port: DEFAULT_FRONTEND_PORT,
        frontend_started_at: null,
        last_updated: null,
    };

    info = { ...info, ...updates, last_updated: new Date().toISOString() };

    // Ensure config directory exists
    if (!fs.existsSync(CONFIG_DIR)) {
        fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }

    fs.writeFileSync(INSTALLATION_FILE, JSON.stringify(info, null, 2));
}

/**
 * Get the configured frontend port (from settings or installation.json)
 */
export function getFrontendPort(): number {
    const config = vscode.workspace.getConfiguration('flowmason');
    const configPort = config.get<number>('frontendPort');
    if (configPort) return configPort;

    const info = getInstallationInfo();
    return info?.frontend_port || DEFAULT_FRONTEND_PORT;
}

/**
 * Get the configured backend port (from settings or installation.json)
 */
export function getBackendPort(): number {
    const info = getInstallationInfo();
    return info?.studio_port || DEFAULT_BACKEND_PORT;
}

/**
 * Get the configured host
 */
export function getHost(): string {
    const info = getInstallationInfo();
    return info?.studio_host || DEFAULT_HOST;
}

/**
 * Check if a process is running by PID
 */
export function isProcessRunning(pid: number): boolean {
    try {
        process.kill(pid, 0);
        return true;
    } catch {
        return false;
    }
}

/**
 * Check if backend is running
 */
export async function isBackendRunning(): Promise<boolean> {
    const info = getInstallationInfo();
    const port = info?.studio_port || DEFAULT_BACKEND_PORT;
    const host = info?.studio_host || DEFAULT_HOST;

    // Check by PID first
    if (info?.studio_pid && isProcessRunning(info.studio_pid)) {
        return true;
    }

    // Try health endpoint
    try {
        const response = await fetch(`http://${host}:${port}/health`, {
            signal: AbortSignal.timeout(2000)
        });
        return response.ok;
    } catch {
        return false;
    }
}

/**
 * Check if frontend is running
 */
export async function isFrontendRunning(): Promise<boolean> {
    const info = getInstallationInfo();
    const port = info?.frontend_port || DEFAULT_FRONTEND_PORT;

    // Check by PID first
    if (info?.frontend_pid && isProcessRunning(info.frontend_pid)) {
        return true;
    }

    // Try to connect
    try {
        const response = await fetch(`http://${DEFAULT_HOST}:${port}/`, {
            signal: AbortSignal.timeout(2000)
        });
        return response.ok || response.status === 304;
    } catch {
        return false;
    }
}
