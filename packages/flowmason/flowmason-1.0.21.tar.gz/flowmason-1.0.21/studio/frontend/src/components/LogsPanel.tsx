/**
 * Logs Panel Component
 *
 * A floating/dockable panel for viewing backend logs, similar to Salesforce Developer Console.
 * Can be opened from anywhere in the app and persists across navigation.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  X,
  Minimize2,
  Maximize2,
  Filter,
  RefreshCw,
  Trash2,
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
  GripHorizontal,
} from 'lucide-react';
import { logs as logsApi } from '../services/api';
import type { BackendLogEntry, BackendLogLevel, LogConfigResponse } from '../types';
import {
  Button,
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
  DEBUG: { color: 'text-slate-500', bgColor: 'bg-slate-100 dark:bg-slate-800', icon: Bug },
  INFO: { color: 'text-blue-600 dark:text-blue-400', bgColor: 'bg-blue-50 dark:bg-blue-900/30', icon: Info },
  WARNING: { color: 'text-amber-600 dark:text-amber-400', bgColor: 'bg-amber-50 dark:bg-amber-900/30', icon: AlertTriangle },
  ERROR: { color: 'text-red-600 dark:text-red-400', bgColor: 'bg-red-50 dark:bg-red-900/30', icon: AlertCircle },
  CRITICAL: { color: 'text-red-800 dark:text-red-300', bgColor: 'bg-red-100 dark:bg-red-900/50', icon: Zap },
};

// Category colors
const CATEGORY_COLORS: Record<string, string> = {
  SYSTEM: 'bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300',
  API: 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300',
  EXECUTION: 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300',
  PROVIDER: 'bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-300',
  REGISTRY: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/50 dark:text-cyan-300',
  STORAGE: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
  DATABASE: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300',
  VALIDATION: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-300',
  CALLOUT: 'bg-pink-100 text-pink-700 dark:bg-pink-900/50 dark:text-pink-300',
};

interface LogsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

function LogEntryRow({ entry, expanded, onToggle }: {
  entry: BackendLogEntry;
  expanded: boolean;
  onToggle: () => void;
}) {
  const levelConfig = LOG_LEVEL_CONFIG[entry.level] || LOG_LEVEL_CONFIG.INFO;
  const LevelIcon = levelConfig.icon;
  const categoryColor = CATEGORY_COLORS[entry.category] || 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';

  const timestamp = new Date(entry.timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });

  return (
    <div className={`border-b border-slate-100 dark:border-slate-700 ${levelConfig.bgColor}`}>
      <div
        className="flex items-start gap-2 p-1.5 cursor-pointer hover:bg-white/50 dark:hover:bg-white/5 transition-colors"
        onClick={onToggle}
      >
        <button className="mt-0.5 text-slate-400">
          {expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
        </button>
        <LevelIcon className={`w-3 h-3 mt-0.5 shrink-0 ${levelConfig.color}`} />
        <span className="text-[10px] text-slate-400 font-mono w-16 shrink-0">{timestamp}</span>
        <Badge variant="secondary" className={`text-[10px] px-1 py-0 shrink-0 ${categoryColor}`}>
          {entry.category}
        </Badge>
        <span className={`text-xs flex-1 truncate ${levelConfig.color}`}>{entry.message}</span>
        {entry.duration_ms && (
          <span className="text-[10px] text-slate-400">{entry.duration_ms.toFixed(1)}ms</span>
        )}
      </div>
      {expanded && (
        <div className="pl-8 pr-3 pb-2 text-[10px] space-y-1">
          <div className="flex gap-3 text-slate-500">
            <span>Logger: {entry.logger_name}</span>
            <span>ID: {entry.id}</span>
          </div>
          {entry.details && (
            <pre className="bg-slate-800 text-slate-100 p-1.5 rounded text-[10px] overflow-x-auto max-h-32">
              {JSON.stringify(entry.details, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

export function LogsPanel({ isOpen, onClose }: LogsPanelProps) {
  const [entries, setEntries] = useState<BackendLogEntry[]>([]);
  const [config, setConfig] = useState<LogConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [filterLevel, setFilterLevel] = useState<BackendLogLevel | 'all'>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [total, setTotal] = useState(0);
  const [isMinimized, setIsMinimized] = useState(false);
  const [panelHeight, setPanelHeight] = useState(350);
  const [isDragging, setIsDragging] = useState(false);

  const refreshIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const dragStartY = useRef(0);
  const dragStartHeight = useRef(0);

  const loadLogs = useCallback(async () => {
    try {
      const result = await logsApi.list({
        limit: 100,
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
    if (!isOpen) return;

    const init = async () => {
      setLoading(true);
      await Promise.all([loadLogs(), loadConfig()]);
      setLoading(false);
    };
    init();
  }, [isOpen, loadLogs]);

  useEffect(() => {
    if (!isOpen) {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
        refreshIntervalRef.current = null;
      }
      return;
    }

    if (autoRefresh && !isMinimized) {
      refreshIntervalRef.current = setInterval(loadLogs, 2000);
    } else if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
      refreshIntervalRef.current = null;
    }
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [autoRefresh, isOpen, isMinimized, loadLogs]);

  const handleClear = async () => {
    if (!confirm('Clear all log entries?')) return;
    await logsApi.clear();
    await loadLogs();
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

  // Drag to resize
  const handleDragStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    dragStartY.current = e.clientY;
    dragStartHeight.current = panelHeight;
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      const delta = dragStartY.current - e.clientY;
      const newHeight = Math.max(150, Math.min(800, dragStartHeight.current + delta));
      setPanelHeight(newHeight);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  if (!isOpen) return null;

  const levels: BackendLogLevel[] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];
  const categories = config?.categories || [];

  return (
    <div
      ref={panelRef}
      className="fixed bottom-0 left-0 right-0 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700 shadow-2xl z-50"
      style={{ height: isMinimized ? 40 : panelHeight }}
    >
      {/* Resize handle */}
      {!isMinimized && (
        <div
          className="absolute -top-1 left-0 right-0 h-2 cursor-ns-resize flex items-center justify-center group"
          onMouseDown={handleDragStart}
        >
          <div className="w-12 h-1 bg-slate-300 dark:bg-slate-600 rounded-full group-hover:bg-slate-400" />
        </div>
      )}

      {/* Header */}
      <div className="h-10 px-3 flex items-center justify-between border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
        <div className="flex items-center gap-2">
          <GripHorizontal className="w-4 h-4 text-slate-400" />
          <span className="text-sm font-medium text-slate-700 dark:text-slate-200">
            Developer Console
          </span>
          <span className="text-xs text-slate-400">
            {total} entries • {config?.global_level || 'INFO'}
          </span>
          {autoRefresh && !isMinimized && (
            <span className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              Live
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          {!isMinimized && (
            <>
              <Button
                variant={autoRefresh ? 'default' : 'ghost'}
                size="sm"
                className="h-7 px-2 text-xs"
                onClick={() => setAutoRefresh(!autoRefresh)}
              >
                {autoRefresh ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
              </Button>
              <Button variant="ghost" size="sm" className="h-7 px-2" onClick={loadLogs}>
                <RefreshCw className="w-3 h-3" />
              </Button>
              <Button variant="ghost" size="sm" className="h-7 px-2" onClick={handleClear}>
                <Trash2 className="w-3 h-3" />
              </Button>
            </>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-7 px-2"
            onClick={() => setIsMinimized(!isMinimized)}
          >
            {isMinimized ? <Maximize2 className="w-3 h-3" /> : <Minimize2 className="w-3 h-3" />}
          </Button>
          <Button variant="ghost" size="sm" className="h-7 px-2" onClick={onClose}>
            <X className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {/* Content */}
      {!isMinimized && (
        <div className="flex flex-col" style={{ height: panelHeight - 40 }}>
          {/* Filters */}
          <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-100 dark:border-slate-700">
            <Filter className="w-3 h-3 text-slate-400" />
            <Select
              value={filterLevel}
              onValueChange={(v) => setFilterLevel(v as BackendLogLevel | 'all')}
            >
              <SelectTrigger className="w-24 h-7 text-xs">
                <SelectValue placeholder="Level" />
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
              <SelectTrigger className="w-28 h-7 text-xs">
                <SelectValue placeholder="Category" />
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
            <div className="relative flex-1 max-w-xs">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-400" />
              <Input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-7 h-7 text-xs"
              />
            </div>
          </div>

          {/* Log Entries */}
          <div className="flex-1 overflow-y-auto font-mono text-xs">
            {loading ? (
              <div className="flex items-center justify-center h-full gap-2 text-slate-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                Loading logs...
              </div>
            ) : error ? (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            ) : entries.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-slate-500">
                <Info className="w-8 h-8 mb-2 text-slate-300" />
                <p>No log entries</p>
                <p className="text-[10px]">Logs will appear as the backend processes requests</p>
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
        </div>
      )}
    </div>
  );
}

export default LogsPanel;
