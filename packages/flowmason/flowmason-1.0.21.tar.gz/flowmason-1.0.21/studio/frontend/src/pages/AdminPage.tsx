/**
 * Admin Panel Page
 *
 * Administrative interface for managing API keys, users, organizations,
 * system health, and viewing audit logs.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  Key,
  Shield,
  Server,
  Activity,
  Plus,
  Trash2,
  Copy,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Loader2,
  Settings2
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
// Dialog imports available for future modal implementations
// import {
//   Dialog,
//   DialogContent,
//   DialogDescription,
//   DialogFooter,
//   DialogHeader,
//   DialogTitle,
//   DialogTrigger,
// } from '@/components/ui/dialog';

// Types
interface APIKey {
  id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  rate_limit: number;
  is_active: boolean;
  expires_at: string | null;
  last_used_at: string | null;
  created_at: string;
}

// User interface for future user management tab
// interface User {
//   id: string;
//   email: string;
//   name: string;
//   email_verified: boolean;
//   is_active: boolean;
//   created_at: string;
//   last_login: string | null;
// }

// Organization interface for future org management tab
// interface Organization {
//   id: string;
//   name: string;
//   slug: string;
//   plan: string;
//   max_users: number;
//   max_pipelines: number;
//   max_executions_per_day: number;
//   created_at: string;
// }

interface AuditLogEntry {
  id: string;
  timestamp: string;
  user_id: string | null;
  api_key_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details: Record<string, unknown>;
  success: boolean;
  error_message: string | null;
}

interface HealthStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  message?: string;
  latency_ms?: number;
}

interface SystemHealth {
  status: string;
  version: string;
  uptime_seconds?: number;
  components: HealthStatus[];
  timestamp: string;
}

interface DiagnosticsReport {
  health: SystemHealth;
  system: {
    version: string;
    python_version: string;
    platform: string;
    environment: string;
  };
  database: {
    type: string;
    connected: boolean;
    pipeline_count: number;
    run_count: number;
  };
  providers: {
    name: string;
    configured: boolean;
    available: boolean;
    default: boolean;
  }[];
  resources: {
    memory_mb?: number;
    cpu_percent?: number;
    disk_usage_percent?: number;
  };
}

// Status indicator component
function StatusIndicator({ status }: { status: 'healthy' | 'degraded' | 'unhealthy' | boolean }) {
  const isHealthy = status === 'healthy' || status === true;
  const isDegraded = status === 'degraded';

  return (
    <span
      className={`inline-flex h-2 w-2 rounded-full ${
        isHealthy ? 'bg-green-500' : isDegraded ? 'bg-yellow-500' : 'bg-red-500'
      }`}
    />
  );
}

// API Keys Tab
function APIKeysTab() {
  const [keys, setKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyScopes, setNewKeyScopes] = useState('full');
  const [showNewKey, setShowNewKey] = useState<string | null>(null);
  // const [dialogOpen, setDialogOpen] = useState(false); // For future dialog modals

  const fetchKeys = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/auth/api-keys');
      if (response.ok) {
        const data = await response.json();
        setKeys(data.keys || data || []);
      }
    } catch (error) {
      console.error('Failed to fetch API keys:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchKeys();
  }, [fetchKeys]);

  const createKey = async () => {
    setCreating(true);
    try {
      const response = await fetch('/api/v1/auth/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newKeyName,
          scopes: [newKeyScopes],
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setShowNewKey(data.raw_key);
        setNewKeyName('');
        setNewKeyScopes('full');
        fetchKeys();
      }
    } catch (error) {
      console.error('Failed to create API key:', error);
    } finally {
      setCreating(false);
    }
  };

  const deleteKey = async (id: string) => {
    if (!confirm('Are you sure you want to delete this API key?')) return;

    try {
      await fetch(`/api/v1/auth/api-keys/${id}`, { method: 'DELETE' });
      fetchKeys();
    } catch (error) {
      console.error('Failed to delete API key:', error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* New key created dialog */}
      {showNewKey && (
        <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-green-700 dark:text-green-400">
                API Key Created Successfully
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Copy this key now. You won't be able to see it again!
              </p>
              <div className="flex items-center gap-2 mt-2">
                <code className="flex-1 bg-muted px-3 py-2 rounded text-sm font-mono break-all">
                  {showNewKey}
                </code>
                <Button size="sm" variant="outline" onClick={() => copyToClipboard(showNewKey)}>
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="mt-2"
                onClick={() => setShowNewKey(null)}
              >
                Dismiss
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Create new key */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Create API Key</CardTitle>
          <CardDescription>Generate a new API key for accessing FlowMason APIs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Label htmlFor="key-name">Name</Label>
              <Input
                id="key-name"
                placeholder="My API Key"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
              />
            </div>
            <div className="w-40">
              <Label htmlFor="key-scope">Scope</Label>
              <Select value={newKeyScopes} onValueChange={setNewKeyScopes}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full">Full Access</SelectItem>
                  <SelectItem value="read">Read Only</SelectItem>
                  <SelectItem value="execute">Execute Only</SelectItem>
                  <SelectItem value="deploy">Deploy Only</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button onClick={createKey} disabled={!newKeyName || creating}>
                {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                <span className="ml-2">Create</span>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Existing keys */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">API Keys</CardTitle>
          <CardDescription>{keys.length} key(s) configured</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {keys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Key className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="font-medium text-sm">{key.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {key.key_prefix}••••••••
                      {key.last_used_at && ` • Last used ${new Date(key.last_used_at).toLocaleDateString()}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {key.scopes.map((scope) => (
                    <Badge key={scope} variant="outline" className="text-xs">
                      {scope}
                    </Badge>
                  ))}
                  <StatusIndicator status={key.is_active ? 'healthy' : 'unhealthy'} />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-red-500 hover:text-red-600 hover:bg-red-500/10"
                    onClick={() => deleteKey(key.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
            {keys.length === 0 && (
              <p className="text-center text-muted-foreground py-8">
                No API keys configured. Create one above.
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// System Health Tab
function SystemHealthTab() {
  const [diagnostics, setDiagnostics] = useState<DiagnosticsReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDiagnostics = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/system/diagnostics');
      if (response.ok) {
        setDiagnostics(await response.json());
        setError(null);
      } else {
        setError('Failed to fetch diagnostics');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDiagnostics();
    const interval = setInterval(fetchDiagnostics, 30000);
    return () => clearInterval(interval);
  }, [fetchDiagnostics]);

  if (loading && !diagnostics) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error && !diagnostics) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <AlertTriangle className="h-12 w-12 text-yellow-500" />
        <p className="text-muted-foreground">{error}</p>
        <Button onClick={fetchDiagnostics}>Retry</Button>
      </div>
    );
  }

  const formatUptime = (seconds?: number) => {
    if (!seconds) return 'Unknown';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${mins}m`;
    return `${mins}m`;
  };

  return (
    <div className="space-y-4">
      {/* Overall Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="text-2xl font-bold capitalize">{diagnostics?.health.status}</p>
              </div>
              <StatusIndicator status={diagnostics?.health.status as any || 'unhealthy'} />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Version</p>
                <p className="text-2xl font-bold">{diagnostics?.system.version || '-'}</p>
              </div>
              <Server className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Uptime</p>
                <p className="text-2xl font-bold">{formatUptime(diagnostics?.health.uptime_seconds)}</p>
              </div>
              <Clock className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Environment</p>
                <p className="text-2xl font-bold capitalize">{diagnostics?.system.environment || '-'}</p>
              </div>
              <Settings2 className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Components Health */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Component Health</CardTitle>
            <Button variant="ghost" size="sm" onClick={fetchDiagnostics}>
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {diagnostics?.health.components.map((component) => (
              <div
                key={component.name}
                className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
              >
                <div className="flex items-center gap-3">
                  <StatusIndicator status={component.status} />
                  <span className="font-medium">{component.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  {component.latency_ms && (
                    <span className="text-sm text-muted-foreground">
                      {component.latency_ms.toFixed(0)}ms
                    </span>
                  )}
                  {component.message && (
                    <span className="text-sm text-muted-foreground">{component.message}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Database & Providers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Database</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Type</span>
                <span className="font-medium">{diagnostics?.database.type || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Status</span>
                <span className="flex items-center gap-2">
                  <StatusIndicator status={diagnostics?.database.connected || false} />
                  {diagnostics?.database.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Pipelines</span>
                <span className="font-medium">{diagnostics?.database.pipeline_count || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Runs</span>
                <span className="font-medium">{diagnostics?.database.run_count || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">LLM Providers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {diagnostics?.providers.map((provider) => (
                <div
                  key={provider.name}
                  className="flex items-center justify-between p-2 rounded bg-muted/50"
                >
                  <span className="font-medium capitalize">{provider.name}</span>
                  <div className="flex items-center gap-2">
                    {provider.default && (
                      <Badge variant="secondary" className="text-xs">Default</Badge>
                    )}
                    <StatusIndicator status={provider.available ? 'healthy' : 'unhealthy'} />
                  </div>
                </div>
              ))}
              {(!diagnostics?.providers || diagnostics.providers.length === 0) && (
                <p className="text-muted-foreground text-center py-4">No providers configured</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Audit Logs Tab
function AuditLogsTab() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/auth/audit?limit=50')
      .then((r) => r.json())
      .then((data) => setLogs(data.entries || data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Audit Log</CardTitle>
        <CardDescription>Recent security and access events</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {logs.map((log) => (
            <div
              key={log.id}
              className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
            >
              <div className="flex items-center gap-3">
                {log.success ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <XCircle className="h-4 w-4 text-red-500" />
                )}
                <div>
                  <p className="font-medium text-sm">{log.action}</p>
                  <p className="text-xs text-muted-foreground">
                    {log.resource_type}
                    {log.resource_id && ` • ${log.resource_id.substring(0, 8)}...`}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground">
                  {new Date(log.timestamp).toLocaleString()}
                </p>
                {log.error_message && (
                  <p className="text-xs text-red-500">{log.error_message}</p>
                )}
              </div>
            </div>
          ))}
          {logs.length === 0 && (
            <p className="text-center text-muted-foreground py-8">
              No audit logs available
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// Main Admin Page
export function AdminPage() {
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Shield className="h-6 w-6" />
          Admin Panel
        </h1>
        <p className="text-muted-foreground">
          Manage API keys, system health, and security settings
        </p>
      </div>

      <Tabs defaultValue="keys" className="space-y-4">
        <TabsList>
          <TabsTrigger value="keys" className="flex items-center gap-2">
            <Key className="h-4 w-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="health" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            System Health
          </TabsTrigger>
          <TabsTrigger value="audit" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Audit Logs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="keys">
          <APIKeysTab />
        </TabsContent>

        <TabsContent value="health">
          <SystemHealthTab />
        </TabsContent>

        <TabsContent value="audit">
          <AuditLogsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
