/**
 * FlowMason WebSocket Service
 *
 * Handles real-time execution updates via WebSocket connection.
 * Features:
 * - Auto-reconnect with exponential backoff
 * - Subscription management
 * - Debug command sending
 * - Connection health monitoring
 */

export type WebSocketEventType =
  | 'connected'
  | 'subscribed'
  | 'unsubscribed'
  | 'error'
  | 'run_started'
  | 'stage_started'
  | 'stage_completed'
  | 'stage_failed'
  | 'run_completed'
  | 'run_failed'
  | 'execution_paused'
  | 'execution_resumed'
  | 'breakpoint_hit'
  | 'ping'
  | 'pong';

export interface WebSocketMessage {
  type: WebSocketEventType;
  run_id?: string;
  payload: Record<string, unknown>;
  timestamp: string;
}

export interface StageStartedPayload {
  run_id: string;
  stage_id: string;
  stage_name?: string;
  component_type: string;
  input?: Record<string, unknown>;
}

export interface StageCompletedPayload {
  run_id: string;
  stage_id: string;
  stage_name?: string;
  component_type: string;
  status: string;
  output?: unknown;
  duration_ms?: number;
  input_tokens?: number;
  output_tokens?: number;
}

export interface StageFailedPayload {
  run_id: string;
  stage_id: string;
  stage_name?: string;
  component_type: string;
  error: string;
}

export interface RunStartedPayload {
  run_id: string;
  pipeline_id: string;
  stage_ids: string[];
  inputs?: Record<string, unknown>;
}

export interface RunCompletedPayload {
  run_id: string;
  pipeline_id: string;
  status: string;
  output?: unknown;
  total_duration_ms?: number;
  total_input_tokens?: number;
  total_output_tokens?: number;
}

export interface RunFailedPayload {
  run_id: string;
  pipeline_id: string;
  error: string;
  failed_stage_id?: string;
}

export interface ExecutionPausedPayload {
  run_id: string;
  stage_id: string;
  stage_name?: string;
  reason: string;
  timeout_seconds: number;
  completed_stages: string[];
  pending_stages: string[];
}

export type WebSocketEventCallback = (message: WebSocketMessage) => void;

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting';

interface WebSocketOptions {
  /** Auto-reconnect on disconnect (default: true) */
  autoReconnect?: boolean;
  /** Initial reconnect delay in ms (default: 1000) */
  reconnectDelay?: number;
  /** Maximum reconnect delay in ms (default: 30000) */
  maxReconnectDelay?: number;
  /** Ping interval in ms (default: 30000) */
  pingInterval?: number;
  /** Connection timeout in ms (default: 5000) */
  connectionTimeout?: number;
}

const DEFAULT_OPTIONS: Required<WebSocketOptions> = {
  autoReconnect: true,
  reconnectDelay: 1000,
  maxReconnectDelay: 30000,
  pingInterval: 30000,
  connectionTimeout: 5000,
};

export class ExecutionWebSocket {
  private ws: WebSocket | null = null;
  private clientId: string | null = null;
  private options: Required<WebSocketOptions>;
  private status: ConnectionStatus = 'disconnected';
  private reconnectAttempts = 0;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private pingTimeout: ReturnType<typeof setTimeout> | null = null;
  private connectionTimeout: ReturnType<typeof setTimeout> | null = null;

  // Callbacks
  private eventCallbacks: Set<WebSocketEventCallback> = new Set();
  private statusCallbacks: Set<(status: ConnectionStatus) => void> = new Set();

  // Subscriptions to restore on reconnect
  private subscriptions: Set<string> = new Set();

  constructor(options: WebSocketOptions = {}) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
  }

  /**
   * Get current connection status
   */
  get connectionStatus(): ConnectionStatus {
    return this.status;
  }

  /**
   * Check if connected
   */
  get isConnected(): boolean {
    return this.status === 'connected' && this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get client ID (assigned by server)
   */
  get id(): string | null {
    return this.clientId;
  }

  /**
   * Connect to the WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.setStatus('connecting');

    // Build WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/api/v1/ws/runs`;

    try {
      this.ws = new WebSocket(url);
      this.setupEventHandlers();
      this.startConnectionTimeout();
    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      this.handleDisconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    this.options.autoReconnect = false;
    this.cleanup();
    this.setStatus('disconnected');
  }

  /**
   * Subscribe to events for a specific callback
   */
  onEvent(callback: WebSocketEventCallback): () => void {
    this.eventCallbacks.add(callback);
    return () => this.eventCallbacks.delete(callback);
  }

  /**
   * Subscribe to connection status changes
   */
  onStatusChange(callback: (status: ConnectionStatus) => void): () => void {
    this.statusCallbacks.add(callback);
    return () => this.statusCallbacks.delete(callback);
  }

  /**
   * Subscribe to updates for a specific run
   */
  subscribe(runId: string): void {
    this.subscriptions.add(runId);

    if (this.isConnected) {
      this.send({ type: 'subscribe', run_id: runId });
    }
  }

  /**
   * Unsubscribe from updates for a specific run
   */
  unsubscribe(runId: string): void {
    this.subscriptions.delete(runId);

    if (this.isConnected) {
      this.send({ type: 'unsubscribe', run_id: runId });
    }
  }

  /**
   * Send a pause command for a run
   */
  pause(runId: string): void {
    this.send({ type: 'pause', run_id: runId });
  }

  /**
   * Send a resume command for a run
   */
  resume(runId: string): void {
    this.send({ type: 'resume', run_id: runId });
  }

  /**
   * Send a step command for a run
   */
  step(runId: string): void {
    this.send({ type: 'step', run_id: runId });
  }

  /**
   * Send a stop command for a run
   */
  stop(runId: string): void {
    this.send({ type: 'stop', run_id: runId });
  }

  /**
   * Send a ping to keep the connection alive
   */
  ping(): void {
    this.send({ type: 'ping' });
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.clearConnectionTimeout();
      this.reconnectAttempts = 0;
      console.log('[WebSocket] Connected');

      // Note: Don't set status to connected yet - wait for 'connected' message from server
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('[WebSocket] Failed to parse message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('[WebSocket] Disconnected:', event.code, event.reason);
      this.handleDisconnect();
    };

    this.ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    // Handle connection confirmation
    if (message.type === 'connected') {
      this.clientId = message.payload.client_id as string;
      this.setStatus('connected');
      this.startPingInterval();

      // Restore subscriptions
      for (const runId of this.subscriptions) {
        this.send({ type: 'subscribe', run_id: runId });
      }

      console.log('[WebSocket] Received client ID:', this.clientId);
    }

    // Handle pong
    if (message.type === 'pong') {
      // Connection is healthy
      return;
    }

    // Notify all event callbacks
    for (const callback of this.eventCallbacks) {
      try {
        callback(message);
      } catch (error) {
        console.error('[WebSocket] Callback error:', error);
      }
    }
  }

  private handleDisconnect(): void {
    this.cleanup();

    if (this.options.autoReconnect) {
      this.scheduleReconnect();
    } else {
      this.setStatus('disconnected');
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeout) return;

    this.setStatus('reconnecting');
    this.reconnectAttempts++;

    // Exponential backoff
    const delay = Math.min(
      this.options.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.options.maxReconnectDelay
    );

    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      this.connect();
    }, delay);
  }

  private startPingInterval(): void {
    this.stopPingInterval();

    this.pingTimeout = setInterval(() => {
      if (this.isConnected) {
        this.ping();
      }
    }, this.options.pingInterval);
  }

  private stopPingInterval(): void {
    if (this.pingTimeout) {
      clearInterval(this.pingTimeout);
      this.pingTimeout = null;
    }
  }

  private startConnectionTimeout(): void {
    this.clearConnectionTimeout();

    this.connectionTimeout = setTimeout(() => {
      if (this.status === 'connecting') {
        console.warn('[WebSocket] Connection timeout');
        this.ws?.close();
        this.handleDisconnect();
      }
    }, this.options.connectionTimeout);
  }

  private clearConnectionTimeout(): void {
    if (this.connectionTimeout) {
      clearTimeout(this.connectionTimeout);
      this.connectionTimeout = null;
    }
  }

  private cleanup(): void {
    this.clearConnectionTimeout();
    this.stopPingInterval();

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onclose = null;
      this.ws.onerror = null;

      if (this.ws.readyState === WebSocket.OPEN) {
        this.ws.close();
      }

      this.ws = null;
    }

    this.clientId = null;
  }

  private setStatus(status: ConnectionStatus): void {
    if (this.status === status) return;

    this.status = status;

    for (const callback of this.statusCallbacks) {
      try {
        callback(status);
      } catch (error) {
        console.error('[WebSocket] Status callback error:', error);
      }
    }
  }

  private send(data: Record<string, unknown>): void {
    if (!this.isConnected) {
      console.warn('[WebSocket] Cannot send - not connected');
      return;
    }

    try {
      this.ws?.send(JSON.stringify(data));
    } catch (error) {
      console.error('[WebSocket] Send error:', error);
    }
  }
}

// Singleton instance
let _instance: ExecutionWebSocket | null = null;

/**
 * Get or create the global WebSocket instance
 */
export function getWebSocket(): ExecutionWebSocket {
  if (!_instance) {
    _instance = new ExecutionWebSocket();
  }
  return _instance;
}

/**
 * Create a new WebSocket instance (useful for testing)
 */
export function createWebSocket(options?: WebSocketOptions): ExecutionWebSocket {
  return new ExecutionWebSocket(options);
}
