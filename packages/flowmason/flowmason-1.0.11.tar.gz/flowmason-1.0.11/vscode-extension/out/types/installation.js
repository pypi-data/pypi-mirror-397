"use strict";
/**
 * Shared types for FlowMason installation configuration
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
exports.DEFAULT_HOST = exports.DEFAULT_FRONTEND_PORT = exports.DEFAULT_BACKEND_PORT = exports.INSTALLATION_FILE = exports.CONFIG_DIR = void 0;
exports.getInstallationInfo = getInstallationInfo;
exports.updateInstallationInfo = updateInstallationInfo;
exports.getFrontendPort = getFrontendPort;
exports.getBackendPort = getBackendPort;
exports.getHost = getHost;
exports.isProcessRunning = isProcessRunning;
exports.isBackendRunning = isBackendRunning;
exports.isFrontendRunning = isFrontendRunning;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const os = __importStar(require("os"));
// Constants
exports.CONFIG_DIR = path.join(os.homedir(), '.flowmason');
exports.INSTALLATION_FILE = path.join(exports.CONFIG_DIR, 'installation.json');
exports.DEFAULT_BACKEND_PORT = 8999;
exports.DEFAULT_FRONTEND_PORT = 8199;
exports.DEFAULT_HOST = '127.0.0.1';
/**
 * Read installation info from config file
 */
function getInstallationInfo() {
    try {
        if (fs.existsSync(exports.INSTALLATION_FILE)) {
            const content = fs.readFileSync(exports.INSTALLATION_FILE, 'utf-8');
            return JSON.parse(content);
        }
    }
    catch {
        // File doesn't exist or is invalid
    }
    return null;
}
/**
 * Update installation info
 */
function updateInstallationInfo(updates) {
    let info = getInstallationInfo() || {
        install_path: '',
        python_path: 'python',
        version: '0.0.0',
        studio_pid: null,
        studio_port: exports.DEFAULT_BACKEND_PORT,
        studio_host: exports.DEFAULT_HOST,
        studio_started_at: null,
        frontend_pid: null,
        frontend_port: exports.DEFAULT_FRONTEND_PORT,
        frontend_started_at: null,
        last_updated: null,
    };
    info = { ...info, ...updates, last_updated: new Date().toISOString() };
    // Ensure config directory exists
    if (!fs.existsSync(exports.CONFIG_DIR)) {
        fs.mkdirSync(exports.CONFIG_DIR, { recursive: true });
    }
    fs.writeFileSync(exports.INSTALLATION_FILE, JSON.stringify(info, null, 2));
}
/**
 * Get the configured frontend port (from settings or installation.json)
 */
function getFrontendPort() {
    const config = vscode.workspace.getConfiguration('flowmason');
    const configPort = config.get('frontendPort');
    if (configPort)
        return configPort;
    const info = getInstallationInfo();
    return info?.frontend_port || exports.DEFAULT_FRONTEND_PORT;
}
/**
 * Get the configured backend port (from settings or installation.json)
 */
function getBackendPort() {
    const info = getInstallationInfo();
    return info?.studio_port || exports.DEFAULT_BACKEND_PORT;
}
/**
 * Get the configured host
 */
function getHost() {
    const info = getInstallationInfo();
    return info?.studio_host || exports.DEFAULT_HOST;
}
/**
 * Check if a process is running by PID
 */
function isProcessRunning(pid) {
    try {
        process.kill(pid, 0);
        return true;
    }
    catch {
        return false;
    }
}
/**
 * Check if backend is running
 */
async function isBackendRunning() {
    const info = getInstallationInfo();
    const port = info?.studio_port || exports.DEFAULT_BACKEND_PORT;
    const host = info?.studio_host || exports.DEFAULT_HOST;
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
    }
    catch {
        return false;
    }
}
/**
 * Check if frontend is running
 */
async function isFrontendRunning() {
    const info = getInstallationInfo();
    const port = info?.frontend_port || exports.DEFAULT_FRONTEND_PORT;
    // Check by PID first
    if (info?.frontend_pid && isProcessRunning(info.frontend_pid)) {
        return true;
    }
    // Try to connect
    try {
        const response = await fetch(`http://${exports.DEFAULT_HOST}:${port}/`, {
            signal: AbortSignal.timeout(2000)
        });
        return response.ok || response.status === 304;
    }
    catch {
        return false;
    }
}
//# sourceMappingURL=installation.js.map