/**
 * Enhanced Debug Panel
 *
 * Professional multi-tab debug panel with:
 * - Console: Real-time log output with filtering and search
 * - Variables: Live variable inspection with change highlighting
 * - Trace: Step-by-step execution trace with I/O inspection
 * - Breakpoints: Breakpoint management with conditions
 * - Network: API and LLM call monitoring with details
 * - Timeline: Visual execution timeline
 */

import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import {
  ChevronDown,
  ChevronRight,
  Copy,
  Check,
  RotateCcw,
  Eye,
  Trash2,
  Search,
  Download,
  Maximize2,
  Minimize2,
  X,
  Terminal,
  Variable,
  GitBranch,
  CircleDot,
  Network,
  Clock,
  Plus,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Badge } from '../ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../ui/tooltip';
import { ExecutionTimelineVertical } from './ExecutionTimeline';
import type {
  LogLevel,
  LogEntry,
  Breakpoint,
  VariableInfo,
  ExecutionStep,
  NetworkCall,
  PipelineStage,
} from '../../types';

interface EnhancedDebugPanelProps {
  // Data
  logs: LogEntry[];
  variables: Record<string, VariableInfo>;
  executionTrace: ExecutionStep[];
  breakpoints: Breakpoint[];
  networkCalls: NetworkCall[];
  logCounts: { debug: number; info: number; warn: number; error: number };
  stages: PipelineStage[];
  currentStageId: string | null;

  // Actions
  onClearLogs: () => void;
  onClearTrace: () => void;
  onClearVariables: () => void;
  onToggleBreakpoint: (id: string) => void;
  onRemoveBreakpoint: (id: string) => void;
  onAddBreakpoint: (stageId: string, condition?: string) => void;
  onClearBreakpoints: () => void;
  onClearNetworkCalls: () => void;
  onRetryStep?: (step: ExecutionStep) => void;
  onSelectStage?: (stageId: string) => void;

  // Panel state
  isOpen: boolean;
  onClose: () => void;
  height?: number;
  onHeightChange?: (height: number) => void;
  isMaximized?: boolean;
  onToggleMaximize?: () => void;
}

const LOG_LEVEL_STYLES: Record<LogLevel, { bg: string; text: string; label: string; border: string }> = {
  debug: { bg: 'bg-slate-500/10', text: 'text-slate-400', label: 'DBG', border: 'border-l-slate-400' },
  info: { bg: 'bg-blue-500/10', text: 'text-blue-400', label: 'INF', border: 'border-l-blue-400' },
  warn: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', label: 'WRN', border: 'border-l-yellow-400' },
  error: { bg: 'bg-red-500/10', text: 'text-red-400', label: 'ERR', border: 'border-l-red-400' },
};

const NETWORK_STATUS_STYLES = {
  pending: 'bg-slate-500/20 text-slate-400',
  success: 'bg-green-500/20 text-green-400',
  error: 'bg-red-500/20 text-red-400',
};

export function EnhancedDebugPanel({
  logs,
  variables,
  executionTrace,
  breakpoints,
  networkCalls,
  logCounts,
  stages,
  currentStageId,
  onClearLogs,
  onClearTrace,
  onClearVariables,
  onToggleBreakpoint,
  onRemoveBreakpoint,
  onAddBreakpoint,
  onClearBreakpoints,
  onClearNetworkCalls,
  onRetryStep,
  onSelectStage,
  isOpen,
  onClose,
  height = 300,
  onHeightChange,
  isMaximized = false,
  onToggleMaximize,
}: EnhancedDebugPanelProps) {
  const [activeTab, setActiveTab] = useState('console');
  const [filterLevels, setFilterLevels] = useState<LogLevel[]>(['debug', 'info', 'warn', 'error']);
  const [logSearch, setLogSearch] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [expandedCalls, setExpandedCalls] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showAddBreakpoint, setShowAddBreakpoint] = useState(false);
  const [newBreakpointStage, setNewBreakpointStage] = useState('');
  const [newBreakpointCondition, setNewBreakpointCondition] = useState('');
  const logEndRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [isResizing, setIsResizing] = useState(false);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logEndRef.current && activeTab === 'console') {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll, activeTab]);

  // Handle resize
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (panelRef.current) {
        const rect = panelRef.current.getBoundingClientRect();
        const newHeight = Math.max(150, Math.min(600, rect.bottom - e.clientY));
        onHeightChange?.(newHeight);
      }
    };

    const handleMouseUp = () => setIsResizing(false);

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, onHeightChange]);

  // Filter logs
  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      if (!filterLevels.includes(log.level)) return false;
      if (logSearch && !log.message.toLowerCase().includes(logSearch.toLowerCase())) return false;
      return true;
    });
  }, [logs, filterLevels, logSearch]);

  // Toggle helpers
  const toggleFilter = (level: LogLevel) => {
    setFilterLevels((prev) =>
      prev.includes(level) ? prev.filter((l) => l !== level) : [...prev, level]
    );
  };

  const toggleStepExpanded = (stepId: string) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(stepId)) next.delete(stepId);
      else next.add(stepId);
      return next;
    });
  };

  const toggleCallExpanded = (callId: string) => {
    setExpandedCalls((prev) => {
      const next = new Set(prev);
      if (next.has(callId)) next.delete(callId);
      else next.add(callId);
      return next;
    });
  };

  // Copy helpers
  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // Ignore
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }) + '.' + date.getMilliseconds().toString().padStart(3, '0');
  };

  const handleAddBreakpoint = () => {
    if (newBreakpointStage) {
      onAddBreakpoint(newBreakpointStage, newBreakpointCondition || undefined);
      setNewBreakpointStage('');
      setNewBreakpointCondition('');
      setShowAddBreakpoint(false);
    }
  };

  const exportLogs = () => {
    const text = filteredLogs
      .map((log) => `[${formatTimestamp(log.timestamp)}] [${log.level.toUpperCase()}] ${log.source ? `[${log.source}] ` : ''}${log.message}`)
      .join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `flowmason-logs-${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  const panelHeight = isMaximized ? '100vh' : height;

  return (
    <TooltipProvider>
      <div
        ref={panelRef}
        className={cn(
          'border-t bg-background flex flex-col',
          isMaximized && 'fixed inset-0 z-50'
        )}
        style={{ height: panelHeight }}
      >
        {/* Resize handle */}
        {!isMaximized && (
          <div
            className={cn(
              'h-1 cursor-ns-resize hover:bg-primary/50 transition-colors flex-shrink-0',
              isResizing && 'bg-primary/50'
            )}
            onMouseDown={handleMouseDown}
          />
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col min-h-0">
          {/* Tab header */}
          <div className="flex items-center justify-between px-2 py-1 border-b bg-muted/30 flex-shrink-0">
            <TabsList className="h-8 bg-transparent">
              <TabsTrigger value="console" className="text-xs h-7 px-2.5 gap-1.5 data-[state=active]:bg-background">
                <Terminal className="w-3.5 h-3.5" />
                Console
                {(logCounts.error > 0 || logCounts.warn > 0) && (
                  <Badge
                    variant="destructive"
                    className={cn(
                      'h-4 px-1 text-[10px] ml-1',
                      logCounts.error === 0 && 'bg-yellow-500'
                    )}
                  >
                    {logCounts.error || logCounts.warn}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="variables" className="text-xs h-7 px-2.5 gap-1.5 data-[state=active]:bg-background">
                <Variable className="w-3.5 h-3.5" />
                Variables
                <Badge variant="secondary" className="h-4 px-1 text-[10px] ml-1">
                  {Object.keys(variables).length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="trace" className="text-xs h-7 px-2.5 gap-1.5 data-[state=active]:bg-background">
                <GitBranch className="w-3.5 h-3.5" />
                Trace
                <Badge variant="secondary" className="h-4 px-1 text-[10px] ml-1">
                  {executionTrace.length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="breakpoints" className="text-xs h-7 px-2.5 gap-1.5 data-[state=active]:bg-background">
                <CircleDot className="w-3.5 h-3.5" />
                Breakpoints
                {breakpoints.length > 0 && (
                  <Badge variant="secondary" className="h-4 px-1 text-[10px] ml-1 bg-red-500/20 text-red-400">
                    {breakpoints.length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="network" className="text-xs h-7 px-2.5 gap-1.5 data-[state=active]:bg-background">
                <Network className="w-3.5 h-3.5" />
                Network
                <Badge variant="secondary" className="h-4 px-1 text-[10px] ml-1">
                  {networkCalls.length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="timeline" className="text-xs h-7 px-2.5 gap-1.5 data-[state=active]:bg-background">
                <Clock className="w-3.5 h-3.5" />
                Timeline
              </TabsTrigger>
            </TabsList>

            <div className="flex items-center gap-1">
              {onToggleMaximize && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={onToggleMaximize}>
                      {isMaximized ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>{isMaximized ? 'Restore' : 'Maximize'}</TooltipContent>
                </Tooltip>
              )}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={onClose}>
                    <X className="w-3.5 h-3.5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Close Panel</TooltipContent>
              </Tooltip>
            </div>
          </div>

          {/* Console Tab */}
          <TabsContent value="console" className="flex-1 m-0 flex flex-col min-h-0">
            {/* Console toolbar */}
            <div className="flex items-center gap-2 px-2 py-1 border-b bg-muted/20 flex-shrink-0">
              <div className="flex items-center gap-1">
                {(['error', 'warn', 'info', 'debug'] as LogLevel[]).map((level) => {
                  const style = LOG_LEVEL_STYLES[level];
                  const count = logCounts[level];
                  return (
                    <Button
                      key={level}
                      variant={filterLevels.includes(level) ? 'secondary' : 'ghost'}
                      size="sm"
                      className={cn('h-6 text-xs px-2 gap-1', filterLevels.includes(level) && style.bg)}
                      onClick={() => toggleFilter(level)}
                    >
                      <span className={style.text}>{style.label}</span>
                      {count > 0 && <span className="text-muted-foreground">{count}</span>}
                    </Button>
                  );
                })}
              </div>

              <div className="h-4 w-px bg-border" />

              <div className="relative flex-1 max-w-xs">
                <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <Input
                  placeholder="Search logs..."
                  value={logSearch}
                  onChange={(e) => setLogSearch(e.target.value)}
                  className="h-6 text-xs pl-7 pr-2"
                />
              </div>

              <div className="flex-1" />

              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs px-2"
                onClick={() => setAutoScroll(!autoScroll)}
              >
                {autoScroll ? 'Auto-scroll: On' : 'Auto-scroll: Off'}
              </Button>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 text-xs px-2"
                    onClick={() => {
                      const text = filteredLogs
                        .map((log) => `[${formatTimestamp(log.timestamp)}] [${log.level.toUpperCase()}] ${log.source ? `[${log.source}] ` : ''}${log.message}`)
                        .join('\n');
                      copyToClipboard(text, 'all-logs');
                    }}
                  >
                    {copiedId === 'all-logs' ? <Check className="w-3 h-3 mr-1 text-green-500" /> : <Copy className="w-3 h-3 mr-1" />}
                    Copy All
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Copy all logs to clipboard</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-6 text-xs px-2" onClick={exportLogs}>
                    <Download className="w-3 h-3 mr-1" />
                    Export
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Export logs to file</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-6 text-xs px-2" onClick={onClearLogs}>
                    <Trash2 className="w-3 h-3 mr-1" />
                    Clear
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Clear all logs</TooltipContent>
              </Tooltip>
            </div>

            {/* Console output */}
            <ScrollArea className="flex-1">
              <div className="font-mono text-xs p-2 space-y-px">
                {filteredLogs.length === 0 ? (
                  <div className="text-muted-foreground py-8 text-center">
                    <Terminal className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    No logs to display
                  </div>
                ) : (
                  filteredLogs.map((log) => {
                    const style = LOG_LEVEL_STYLES[log.level];
                    return (
                      <div
                        key={log.id}
                        className={cn(
                          'flex items-start gap-2 px-2 py-1 rounded border-l-2 group',
                          style.bg,
                          style.border
                        )}
                      >
                        <span className="text-muted-foreground shrink-0 w-20">
                          {formatTimestamp(log.timestamp)}
                        </span>
                        <span className={cn('shrink-0 w-8 font-semibold', style.text)}>
                          {style.label}
                        </span>
                        {log.source && (
                          <span className="text-purple-400 shrink-0 font-medium">
                            [{log.source}]
                          </span>
                        )}
                        <span className="flex-1 break-words whitespace-pre-wrap">{log.message}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-5 w-5 p-0 opacity-0 group-hover:opacity-100"
                          onClick={() => copyToClipboard(log.message, log.id)}
                        >
                          {copiedId === log.id ? (
                            <Check className="w-3 h-3 text-green-500" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </Button>
                      </div>
                    );
                  })
                )}
                <div ref={logEndRef} />
              </div>
            </ScrollArea>
          </TabsContent>

          {/* Variables Tab */}
          <TabsContent value="variables" className="flex-1 m-0 flex flex-col min-h-0">
            <div className="flex items-center justify-between px-2 py-1 border-b bg-muted/20 flex-shrink-0">
              <span className="text-xs text-muted-foreground">
                {Object.keys(variables).length} variables
              </span>
              <Button variant="ghost" size="sm" className="h-6 text-xs px-2" onClick={onClearVariables}>
                <Trash2 className="w-3 h-3 mr-1" />
                Clear
              </Button>
            </div>
            <ScrollArea className="flex-1">
              {Object.keys(variables).length === 0 ? (
                <div className="text-muted-foreground text-xs py-8 text-center">
                  <Variable className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  No variables captured yet
                </div>
              ) : (
                <div className="p-2 space-y-1">
                  {Object.values(variables).map((variable) => (
                    <div
                      key={variable.name}
                      className={cn(
                        'flex items-start gap-3 p-2 rounded text-xs border',
                        variable.changed
                          ? 'bg-yellow-500/10 border-yellow-500/30'
                          : 'bg-muted/30 border-transparent'
                      )}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-medium text-foreground">{variable.name}</span>
                          <Badge variant="outline" className="text-[10px] h-4 px-1">
                            {variable.type}
                          </Badge>
                          {variable.changed && (
                            <Badge className="text-[10px] h-4 px-1 bg-yellow-500/20 text-yellow-500">
                              changed
                            </Badge>
                          )}
                        </div>
                        <div className="mt-1 font-mono text-muted-foreground truncate">
                          {typeof variable.value === 'object'
                            ? JSON.stringify(variable.value)
                            : String(variable.value)}
                        </div>
                        <div className="mt-1 text-muted-foreground/70">
                          from: {variable.source}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={() => copyToClipboard(JSON.stringify(variable.value, null, 2), variable.name)}
                      >
                        {copiedId === variable.name ? (
                          <Check className="w-3 h-3 text-green-500" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          {/* Trace Tab */}
          <TabsContent value="trace" className="flex-1 m-0 flex flex-col min-h-0">
            <div className="flex items-center justify-between px-2 py-1 border-b bg-muted/20 flex-shrink-0">
              <span className="text-xs text-muted-foreground">
                {executionTrace.length} steps
              </span>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 text-xs px-2"
                  onClick={() => setExpandedSteps(new Set(executionTrace.map((s) => s.stepId)))}
                >
                  Expand All
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 text-xs px-2"
                  onClick={() => setExpandedSteps(new Set())}
                >
                  Collapse All
                </Button>
                <Button variant="ghost" size="sm" className="h-6 text-xs px-2" onClick={onClearTrace}>
                  <Trash2 className="w-3 h-3 mr-1" />
                  Clear
                </Button>
              </div>
            </div>
            <ScrollArea className="flex-1">
              {executionTrace.length === 0 ? (
                <div className="text-muted-foreground text-xs py-8 text-center">
                  <GitBranch className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  No execution trace yet
                  <div className="mt-1 text-muted-foreground/70">
                    Run your pipeline to see step-by-step details
                  </div>
                </div>
              ) : (
                <div className="p-2 space-y-2">
                  {executionTrace.map((step, index) => {
                    const isExpanded = expandedSteps.has(step.stepId);
                    const hasData = step.input || step.output;

                    return (
                      <div
                        key={step.stepId}
                        className={cn(
                          'rounded border bg-card',
                          step.status === 'failed' && 'border-red-500/50',
                          step.status === 'completed' && 'border-green-500/50',
                          step.status === 'running' && 'border-blue-500/50 shadow-lg shadow-blue-500/10'
                        )}
                      >
                        <button
                          className="flex items-center gap-2 w-full p-2 text-xs text-left hover:bg-muted/50"
                          onClick={() => toggleStepExpanded(step.stepId)}
                        >
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-muted-foreground" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-muted-foreground" />
                          )}
                          <span className="text-muted-foreground w-5">{index + 1}</span>
                          <span className="font-medium flex-1">{step.stageName}</span>
                          <span className="text-muted-foreground font-mono">{step.componentType}</span>
                          <Badge
                            variant="outline"
                            className={cn(
                              'text-[10px]',
                              step.status === 'completed' && 'bg-green-500/20 text-green-500',
                              step.status === 'failed' && 'bg-red-500/20 text-red-500',
                              step.status === 'running' && 'bg-blue-500/20 text-blue-500'
                            )}
                          >
                            {step.status}
                          </Badge>
                          {step.duration !== undefined && (
                            <span className="text-muted-foreground">{step.duration}ms</span>
                          )}
                          <div className="flex items-center gap-1">
                            {onSelectStage && (
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onSelectStage(step.stageId);
                                }}
                              >
                                <Eye className="w-3 h-3" />
                              </Button>
                            )}
                            {onRetryStep && step.status !== 'running' && step.input && (
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onRetryStep(step);
                                }}
                              >
                                <RotateCcw className="w-3 h-3" />
                              </Button>
                            )}
                          </div>
                        </button>

                        {isExpanded && hasData && (
                          <div className="border-t p-2 space-y-2 text-xs bg-muted/20">
                            {step.error && (
                              <div className="p-2 rounded bg-red-500/10 border border-red-500/30">
                                <div className="font-medium text-red-400 mb-1">Error</div>
                                <pre className="whitespace-pre-wrap text-red-300 font-mono text-[11px]">
                                  {step.error}
                                </pre>
                              </div>
                            )}
                            {step.input && Object.keys(step.input).length > 0 && (
                              <div>
                                <div className="flex items-center justify-between mb-1">
                                  <span className="font-medium text-muted-foreground">Input</span>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-5 px-1.5"
                                    onClick={() => copyToClipboard(JSON.stringify(step.input, null, 2), `${step.stepId}-input`)}
                                  >
                                    {copiedId === `${step.stepId}-input` ? (
                                      <Check className="w-3 h-3 text-green-500" />
                                    ) : (
                                      <Copy className="w-3 h-3" />
                                    )}
                                  </Button>
                                </div>
                                <pre className="p-2 rounded bg-muted font-mono text-[11px] max-h-32 overflow-auto whitespace-pre-wrap">
                                  {JSON.stringify(step.input, null, 2)}
                                </pre>
                              </div>
                            )}
                            {step.output && Object.keys(step.output).length > 0 && (
                              <div>
                                <div className="flex items-center justify-between mb-1">
                                  <span className="font-medium text-muted-foreground">Output</span>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-5 px-1.5"
                                    onClick={() => copyToClipboard(JSON.stringify(step.output, null, 2), `${step.stepId}-output`)}
                                  >
                                    {copiedId === `${step.stepId}-output` ? (
                                      <Check className="w-3 h-3 text-green-500" />
                                    ) : (
                                      <Copy className="w-3 h-3" />
                                    )}
                                  </Button>
                                </div>
                                <pre className="p-2 rounded bg-muted font-mono text-[11px] max-h-32 overflow-auto whitespace-pre-wrap">
                                  {JSON.stringify(step.output, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          {/* Breakpoints Tab */}
          <TabsContent value="breakpoints" className="flex-1 m-0 flex flex-col min-h-0">
            <div className="flex items-center justify-between px-2 py-1 border-b bg-muted/20 flex-shrink-0">
              <span className="text-xs text-muted-foreground">
                {breakpoints.filter((bp) => bp.enabled).length} active / {breakpoints.length} total
              </span>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 text-xs px-2"
                  onClick={() => setShowAddBreakpoint(!showAddBreakpoint)}
                >
                  <Plus className="w-3 h-3 mr-1" />
                  Add
                </Button>
                <Button variant="ghost" size="sm" className="h-6 text-xs px-2" onClick={onClearBreakpoints}>
                  <Trash2 className="w-3 h-3 mr-1" />
                  Clear All
                </Button>
              </div>
            </div>

            {showAddBreakpoint && (
              <div className="p-2 border-b bg-muted/10 flex items-center gap-2">
                <select
                  value={newBreakpointStage}
                  onChange={(e) => setNewBreakpointStage(e.target.value)}
                  className="h-7 text-xs rounded border bg-background px-2"
                >
                  <option value="">Select stage...</option>
                  {stages.map((stage) => (
                    <option key={stage.id} value={stage.id}>
                      {stage.name}
                    </option>
                  ))}
                </select>
                <Input
                  placeholder="Condition (optional)"
                  value={newBreakpointCondition}
                  onChange={(e) => setNewBreakpointCondition(e.target.value)}
                  className="h-7 text-xs flex-1"
                />
                <Button size="sm" className="h-7 text-xs" onClick={handleAddBreakpoint} disabled={!newBreakpointStage}>
                  Add
                </Button>
                <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => setShowAddBreakpoint(false)}>
                  <X className="w-3 h-3" />
                </Button>
              </div>
            )}

            <ScrollArea className="flex-1">
              {breakpoints.length === 0 ? (
                <div className="text-muted-foreground text-xs py-8 text-center">
                  <CircleDot className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  No breakpoints set
                  <div className="mt-1 text-muted-foreground/70">
                    Click on a stage node to add a breakpoint
                  </div>
                </div>
              ) : (
                <div className="p-2 space-y-1">
                  {breakpoints.map((bp) => (
                    <div
                      key={bp.id}
                      className={cn(
                        'flex items-center gap-2 p-2 rounded border text-xs',
                        bp.enabled ? 'bg-red-500/10 border-red-500/30' : 'bg-muted/30 border-transparent opacity-60'
                      )}
                    >
                      <input
                        type="checkbox"
                        checked={bp.enabled}
                        onChange={() => onToggleBreakpoint(bp.id)}
                        className="h-3.5 w-3.5 rounded border-red-500 text-red-500 focus:ring-red-500"
                      />
                      <CircleDot className={cn('w-4 h-4', bp.enabled ? 'text-red-500' : 'text-muted-foreground')} />
                      <span className="font-mono font-medium flex-1">{bp.stageId}</span>
                      {bp.condition && (
                        <span className="text-muted-foreground">when: {bp.condition}</span>
                      )}
                      <span className="text-muted-foreground">hits: {bp.hitCount}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-5 w-5 p-0 text-muted-foreground hover:text-destructive"
                        onClick={() => onRemoveBreakpoint(bp.id)}
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          {/* Network Tab */}
          <TabsContent value="network" className="flex-1 m-0 flex flex-col min-h-0">
            <div className="flex items-center justify-between px-2 py-1 border-b bg-muted/20 flex-shrink-0">
              <span className="text-xs text-muted-foreground">
                {networkCalls.length} calls
              </span>
              <Button variant="ghost" size="sm" className="h-6 text-xs px-2" onClick={onClearNetworkCalls}>
                <Trash2 className="w-3 h-3 mr-1" />
                Clear
              </Button>
            </div>
            <ScrollArea className="flex-1">
              {networkCalls.length === 0 ? (
                <div className="text-muted-foreground text-xs py-8 text-center">
                  <Network className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  No network calls recorded
                </div>
              ) : (
                <div className="p-2 space-y-1">
                  {networkCalls.map((call) => {
                    const isExpanded = expandedCalls.has(call.id);

                    return (
                      <div key={call.id} className="rounded border bg-card text-xs">
                        <button
                          className="flex items-center gap-2 w-full p-2 text-left hover:bg-muted/50"
                          onClick={() => toggleCallExpanded(call.id)}
                        >
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-muted-foreground" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-muted-foreground" />
                          )}
                          <Badge
                            variant="outline"
                            className={cn(
                              'text-[10px]',
                              call.type === 'llm' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'
                            )}
                          >
                            {call.type.toUpperCase()}
                          </Badge>
                          {call.type === 'llm' ? (
                            <>
                              <span className="font-medium">{call.provider}</span>
                              <span className="text-muted-foreground">{call.model}</span>
                            </>
                          ) : (
                            <>
                              <span className="font-medium">{call.method}</span>
                              <span className="text-muted-foreground truncate max-w-[200px]">{call.url}</span>
                            </>
                          )}
                          <div className="flex-1" />
                          <Badge variant="outline" className={cn('text-[10px]', NETWORK_STATUS_STYLES[call.status])}>
                            {call.status}
                          </Badge>
                          {call.tokens && (
                            <span className="text-muted-foreground">{call.tokens.total} tokens</span>
                          )}
                          {call.duration !== undefined && (
                            <span className="text-muted-foreground">{call.duration}ms</span>
                          )}
                        </button>

                        {isExpanded && (
                          <div className="border-t p-2 space-y-2 bg-muted/20">
                            {call.error && (
                              <div className="p-2 rounded bg-red-500/10 border border-red-500/30">
                                <div className="font-medium text-red-400 mb-1">Error</div>
                                <pre className="whitespace-pre-wrap text-red-300 font-mono text-[11px]">
                                  {call.error}
                                </pre>
                              </div>
                            )}
                            {call.tokens && (
                              <div className="flex items-center gap-4 text-muted-foreground">
                                <span>Input: {call.tokens.input}</span>
                                <span>Output: {call.tokens.output}</span>
                                <span>Total: {call.tokens.total}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          {/* Timeline Tab */}
          <TabsContent value="timeline" className="flex-1 m-0 flex flex-col min-h-0">
            <ScrollArea className="flex-1">
              <div className="p-2">
                <ExecutionTimelineVertical
                  steps={executionTrace}
                  currentStageId={currentStageId}
                  onStageClick={onSelectStage}
                />
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>
    </TooltipProvider>
  );
}

export default EnhancedDebugPanel;
