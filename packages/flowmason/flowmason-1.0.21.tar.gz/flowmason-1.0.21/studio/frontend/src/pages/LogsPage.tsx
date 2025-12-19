/**
 * Logs Page
 *
 * View and configure backend logs with Salesforce-style log levels.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  FileText,
  Filter,
  RefreshCw,
  Trash2,
  Settings2,
  AlertCircle,
  Info,
  AlertTriangle,
  Bug,
  Zap,
  Loader2,
  ChevronDown,
  ChevronRight,
  Search,
  Pause,
  Play,
} from 'lucide-react';
import { logs as logsApi } from '../services/api';
import type { BackendLogEntry, BackendLogLevel, LogConfigResponse } from '../types';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Input,
  Badge,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui';

// Log level colors and icons
const LOG_LEVEL_CONFIG: Record<BackendLogLevel, { color: string; bgColor: string; icon: typeof Info }> = {
  DEBUG: { color: 'text-slate-500', bgColor: 'bg-slate-100', icon: Bug },
  INFO: { color: 'text-blue-600', bgColor: 'bg-blue-50', icon: Info },
  WARNING: { color: 'text-amber-600', bgColor: 'bg-amber-50', icon: AlertTriangle },
  ERROR: { color: 'text-red-600', bgColor: 'bg-red-50', icon: AlertCircle },
  CRITICAL: { color: 'text-red-800', bgColor: 'bg-red-100', icon: Zap },
};

// Category colors
const CATEGORY_COLORS: Record<string, string> = {
  SYSTEM: 'bg-purple-100 text-purple-700',
  API: 'bg-blue-100 text-blue-700',
  EXECUTION: 'bg-green-100 text-green-700',
  PROVIDER: 'bg-orange-100 text-orange-700',
  REGISTRY: 'bg-cyan-100 text-cyan-700',
  STORAGE: 'bg-slate-100 text-slate-700',
  DATABASE: 'bg-indigo-100 text-indigo-700',
  VALIDATION: 'bg-yellow-100 text-yellow-700',
  CALLOUT: 'bg-pink-100 text-pink-700',
};

interface LogEntryRowProps {
  entry: BackendLogEntry;
  expanded: boolean;
  onToggle: () => void;
}

function LogEntryRow({ entry, expanded, onToggle }: LogEntryRowProps) {
  const levelConfig = LOG_LEVEL_CONFIG[entry.level] || LOG_LEVEL_CONFIG.INFO;
  const LevelIcon = levelConfig.icon;
  const categoryColor = CATEGORY_COLORS[entry.category] || 'bg-gray-100 text-gray-700';

  const timestamp = new Date(entry.timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });

  return (
    <div className={`border-b border-slate-100 ${levelConfig.bgColor}`}>
      <div
        className="flex items-start gap-2 p-2 cursor-pointer hover:bg-white/50 transition-colors"
        onClick={onToggle}
      >
        <button className="mt-0.5 text-slate-400">
          {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
        <LevelIcon className={`w-4 h-4 mt-0.5 shrink-0 ${levelConfig.color}`} />
        <span className="text-xs text-slate-400 font-mono w-20 shrink-0">{timestamp}</span>
        <Badge variant="secondary" className={`text-xs shrink-0 ${categoryColor}`}>
          {entry.category}
        </Badge>
        <span className={`text-sm flex-1 ${levelConfig.color}`}>{entry.message}</span>
        {entry.duration_ms && (
          <span className="text-xs text-slate-400">{entry.duration_ms.toFixed(1)}ms</span>
        )}
      </div>
      {expanded && (
        <div className="pl-10 pr-4 pb-3 text-xs space-y-2">
          <div className="flex gap-4 text-slate-500">
            <span>Logger: {entry.logger_name}</span>
            <span>ID: {entry.id}</span>
          </div>
          {entry.details && (
            <pre className="bg-slate-800 text-slate-100 p-2 rounded overflow-x-auto">
              {JSON.stringify(entry.details, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

function LogConfigPanel({
  config,
  onUpdate,
  onClose,
}: {
  config: LogConfigResponse;
  onUpdate: (config: Partial<LogConfigResponse>) => Promise<void>;
  onClose: () => void;
}) {
  const [globalLevel, setGlobalLevel] = useState(config.global_level);
  const [categoryLevels, setCategoryLevels] = useState(config.category_levels);
  const [maxEntries, setMaxEntries] = useState(config.max_entries);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onUpdate({
        global_level: globalLevel,
        category_levels: categoryLevels,
        max_entries: maxEntries,
      });
      onClose();
    } finally {
      setSaving(false);
    }
  };

  const levels: BackendLogLevel[] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-[600px] max-h-[80vh] overflow-hidden">
        <CardHeader className="border-b">
          <CardTitle className="flex items-center gap-2">
            <Settings2 className="w-5 h-5" />
            Log Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 space-y-6 overflow-y-auto max-h-[60vh]">
          <div>
            <label className="block text-sm font-medium mb-2">Global Log Level</label>
            <Select value={globalLevel} onValueChange={(v) => setGlobalLevel(v as BackendLogLevel)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {levels.map((level) => (
                  <SelectItem key={level} value={level}>
                    {level}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-500 mt-1">
              Only log entries at this level or higher will be captured
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Max Entries</label>
            <Input
              type="number"
              value={maxEntries}
              onChange={(e) => setMaxEntries(parseInt(e.target.value) || 1000)}
              min={100}
              max={10000}
            />
            <p className="text-xs text-slate-500 mt-1">
              Maximum log entries to keep in memory (100-10000)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Category Levels</label>
            <p className="text-xs text-slate-500 mb-3">
              Override log level for specific categories (like Salesforce log categories)
            </p>
            <div className="space-y-2">
              {config.categories.map((category) => (
                <div key={category} className="flex items-center justify-between gap-4">
                  <Badge
                    variant="secondary"
                    className={CATEGORY_COLORS[category] || 'bg-gray-100 text-gray-700'}
                  >
                    {category}
                  </Badge>
                  <Select
                    value={categoryLevels[category] || globalLevel}
                    onValueChange={(v) =>
                      setCategoryLevels({ ...categoryLevels, [category]: v as BackendLogLevel })
                    }
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {levels.map((level) => (
                        <SelectItem key={level} value={level}>
                          {level}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
        <div className="border-t p-4 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
            Save Configuration
          </Button>
        </div>
      </Card>
    </div>
  );
}

export function LogsPage() {
  const [entries, setEntries] = useState<BackendLogEntry[]>([]);
  const [config, setConfig] = useState<LogConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [showConfig, setShowConfig] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [filterLevel, setFilterLevel] = useState<BackendLogLevel | 'all'>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [total, setTotal] = useState(0);

  const refreshIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadLogs = useCallback(async () => {
    try {
      const result = await logsApi.list({
        limit: 200,
        level: filterLevel === 'all' ? undefined : filterLevel,
        category: filterCategory === 'all' ? undefined : filterCategory,
        search: searchQuery || undefined,
      });
      setEntries(result.entries);
      setTotal(result.total);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load logs');
    }
  }, [filterLevel, filterCategory, searchQuery]);

  const loadConfig = async () => {
    try {
      const cfg = await logsApi.getConfig();
      setConfig(cfg);
    } catch (e) {
      console.error('Failed to load log config:', e);
    }
  };

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([loadLogs(), loadConfig()]);
      setLoading(false);
    };
    init();
  }, [loadLogs]);

  useEffect(() => {
    if (autoRefresh) {
      refreshIntervalRef.current = setInterval(loadLogs, 2000);
    } else if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
    }
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [autoRefresh, loadLogs]);

  const handleClear = async () => {
    if (!confirm('Clear all log entries?')) return;
    await logsApi.clear();
    await loadLogs();
  };

  const handleConfigUpdate = async (updates: Partial<LogConfigResponse>) => {
    await logsApi.updateConfig(updates as Parameters<typeof logsApi.updateConfig>[0]);
    await loadConfig();
  };

  const toggleExpanded = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        <p className="text-slate-500">Loading logs...</p>
      </div>
    );
  }

  const levels: BackendLogLevel[] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];
  const categories = config?.categories || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-slate-100 rounded-lg">
                <FileText className="w-6 h-6 text-slate-700" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">Backend Logs</h1>
                <p className="text-sm text-slate-500">
                  {total} entries • {config?.global_level || 'INFO'} level
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={autoRefresh ? 'default' : 'outline'}
                size="sm"
                onClick={() => setAutoRefresh(!autoRefresh)}
              >
                {autoRefresh ? (
                  <Pause className="w-4 h-4 mr-1" />
                ) : (
                  <Play className="w-4 h-4 mr-1" />
                )}
                {autoRefresh ? 'Pause' : 'Resume'}
              </Button>
              <Button variant="outline" size="sm" onClick={loadLogs}>
                <RefreshCw className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={() => setShowConfig(true)}>
                <Settings2 className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleClear}>
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-4">
        {/* Filters */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <Select
              value={filterLevel}
              onValueChange={(v) => setFilterLevel(v as BackendLogLevel | 'all')}
            >
              <SelectTrigger className="w-32">
                <SelectValue placeholder="All Levels" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                {levels.map((level) => (
                  <SelectItem key={level} value={level}>
                    {level}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterCategory} onValueChange={setFilterCategory}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {cat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              type="text"
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        {/* Log Entries */}
        <Card>
          <div className="divide-y divide-slate-100 max-h-[70vh] overflow-y-auto font-mono text-sm">
            {error && (
              <div className="p-4 bg-red-50 text-red-600 flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
            {entries.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                <FileText className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                <p>No log entries found</p>
                <p className="text-sm">Logs will appear here as the backend processes requests</p>
              </div>
            ) : (
              entries.map((entry) => (
                <LogEntryRow
                  key={entry.id}
                  entry={entry}
                  expanded={expandedIds.has(entry.id)}
                  onToggle={() => toggleExpanded(entry.id)}
                />
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Config Modal */}
      {showConfig && config && (
        <LogConfigPanel
          config={config}
          onUpdate={handleConfigUpdate}
          onClose={() => setShowConfig(false)}
        />
      )}
    </div>
  );
}

export default LogsPage;
