/**
 * FlowMason Debug Panel
 *
 * Multi-tab debug panel providing:
 * - Console: Log output with filtering by level
 * - Variables: Inspection of current variable values
 * - Trace: Execution trace with timing info
 * - Breakpoints: Manage debug breakpoints
 * - Network: API and LLM call monitoring
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  ChevronDown,
  ChevronRight,
  Copy,
  Check,
  RotateCcw,
  Eye,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';
import { Badge } from '../ui/badge';
import type {
  LogLevel,
  LogEntry,
  Breakpoint,
  VariableInfo,
  ExecutionStep,
  NetworkCall,
} from '../../types';

interface DebugPanelProps {
  logs: LogEntry[];
  variables: Record<string, VariableInfo>;
  executionTrace: ExecutionStep[];
  breakpoints: Breakpoint[];
  networkCalls: NetworkCall[];
  logCounts: { debug: number; info: number; warn: number; error: number };
  onClearLogs: () => void;
  onClearTrace: () => void;
  onToggleBreakpoint: (id: string) => void;
  onRemoveBreakpoint: (id: string) => void;
  onClearBreakpoints: () => void;
  onClearNetworkCalls: () => void;
  onRetryStep?: (step: ExecutionStep) => void;
  onSelectStep?: (step: ExecutionStep) => void;
  onClose?: () => void;
  height?: number;
  onHeightChange?: (height: number) => void;
}

const LOG_LEVEL_STYLES: Record<LogLevel, { bg: string; text: string; label: string }> = {
  debug: { bg: 'bg-slate-500/20', text: 'text-slate-400', label: 'DEBUG' },
  info: { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'INFO' },
  warn: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'WARN' },
  error: { bg: 'bg-red-500/20', text: 'text-red-400', label: 'ERROR' },
};

const STATUS_STYLES = {
  pending: 'bg-slate-500/20 text-slate-400',
  running: 'bg-blue-500/20 text-blue-400',
  completed: 'bg-green-500/20 text-green-400',
  failed: 'bg-red-500/20 text-red-400',
  skipped: 'bg-yellow-500/20 text-yellow-400',
  success: 'bg-green-500/20 text-green-400',
  error: 'bg-red-500/20 text-red-400',
};

export function DebugPanel({
  logs,
  variables,
  executionTrace,
  breakpoints,
  networkCalls,
  logCounts,
  onClearLogs,
  onClearTrace,
  onToggleBreakpoint,
  onRemoveBreakpoint,
  onClearBreakpoints: _onClearBreakpoints,
  onClearNetworkCalls: _onClearNetworkCalls,
  onRetryStep,
  onSelectStep,
  onClose: _onClose,
  height = 250,
  onHeightChange,
}: DebugPanelProps) {
  const [activeTab, setActiveTab] = useState('console');
  const [filterLevels, setFilterLevels] = useState<LogLevel[]>(['debug', 'info', 'warn', 'error']);
  const [autoScroll, setAutoScroll] = useState(true);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [copiedStepId, setCopiedStepId] = useState<string | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [isResizing, setIsResizing] = useState(false);

  const toggleStepExpanded = (stepId: string) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(stepId)) {
        next.delete(stepId);
      } else {
        next.add(stepId);
      }
      return next;
    });
  };

  const copyStepData = async (stepId: string, data: unknown) => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopiedStepId(stepId);
      setTimeout(() => setCopiedStepId(null), 2000);
    } catch {
      // Ignore clipboard errors
    }
  };

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

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
        const newHeight = Math.max(100, Math.min(500, rect.bottom - e.clientY));
        onHeightChange?.(newHeight);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, onHeightChange]);

  const toggleFilter = (level: LogLevel) => {
    setFilterLevels((prev) =>
      prev.includes(level) ? prev.filter((l) => l !== level) : [...prev, level]
    );
  };

  const filteredLogs = logs.filter((log) => filterLevels.includes(log.level));

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const time = date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
    const ms = date.getMilliseconds().toString().padStart(3, '0');
    return `${time}.${ms}`;
  };

  const copyLogsToClipboard = () => {
    const text = filteredLogs
      .map((log) => `[${formatTimestamp(log.timestamp)}] [${log.level.toUpperCase()}] ${log.message}`)
      .join('\n');
    navigator.clipboard.writeText(text);
  };

  return (
    <div
      ref={panelRef}
      className="border-t bg-background"
      style={{ height }}
    >
      {/* Resize handle */}
      <div
        className={cn(
          'h-1 cursor-ns-resize hover:bg-primary/50 transition-colors',
          isResizing && 'bg-primary/50'
        )}
        onMouseDown={handleMouseDown}
      />

      <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
        <div className="flex items-center justify-between px-2 border-b">
          <TabsList className="h-8">
            <TabsTrigger value="console" className="text-xs h-7 px-2">
              Console
              {logCounts.error > 0 && (
                <Badge variant="destructive" className="ml-1 h-4 px-1 text-[10px]">
                  {logCounts.error}
                </Badge>
              )}
              {logCounts.warn > 0 && logCounts.error === 0 && (
                <Badge className="ml-1 h-4 px-1 text-[10px] bg-yellow-500">
                  {logCounts.warn}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="variables" className="text-xs h-7 px-2">
              Variables
              <Badge variant="secondary" className="ml-1 h-4 px-1 text-[10px]">
                {Object.keys(variables).length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="trace" className="text-xs h-7 px-2">
              Trace
              <Badge variant="secondary" className="ml-1 h-4 px-1 text-[10px]">
                {executionTrace.length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="breakpoints" className="text-xs h-7 px-2">
              Breakpoints
              <Badge variant="secondary" className="ml-1 h-4 px-1 text-[10px]">
                {breakpoints.length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="network" className="text-xs h-7 px-2">
              Network
              <Badge variant="secondary" className="ml-1 h-4 px-1 text-[10px]">
                {networkCalls.length}
              </Badge>
            </TabsTrigger>
          </TabsList>

          {/* Status bar */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            {logCounts.error > 0 && (
              <span className="text-red-400">{logCounts.error} errors</span>
            )}
            {logCounts.warn > 0 && (
              <span className="text-yellow-400">{logCounts.warn} warnings</span>
            )}
          </div>
        </div>

        {/* Console Tab */}
        <TabsContent value="console" className="flex-1 m-0 overflow-hidden">
          <div className="flex flex-col h-full">
            {/* Filter bar */}
            <div className="flex items-center gap-2 px-2 py-1 border-b bg-muted/30">
              {(['debug', 'info', 'warn', 'error'] as LogLevel[]).map((level) => (
                <Button
                  key={level}
                  variant={filterLevels.includes(level) ? 'secondary' : 'ghost'}
                  size="sm"
                  className="h-6 text-xs px-2"
                  onClick={() => toggleFilter(level)}
                >
                  {LOG_LEVEL_STYLES[level].label}
                </Button>
              ))}
              <div className="flex-1" />
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs px-2"
                onClick={() => setAutoScroll(!autoScroll)}
              >
                {autoScroll ? 'Auto-scroll: On' : 'Auto-scroll: Off'}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs px-2"
                onClick={copyLogsToClipboard}
              >
                Copy
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs px-2"
                onClick={onClearLogs}
              >
                Clear
              </Button>
            </div>

            {/* Log output */}
            <ScrollArea className="flex-1">
              <div className="font-mono text-xs p-2 space-y-0.5">
                {filteredLogs.length === 0 ? (
                  <div className="text-muted-foreground py-4 text-center">
                    No logs to display
                  </div>
                ) : (
                  filteredLogs.map((log) => {
                    const style = LOG_LEVEL_STYLES[log.level];
                    return (
                      <div
                        key={log.id}
                        className={cn(
                          'flex items-start gap-2 px-1 py-0.5 rounded',
                          style.bg
                        )}
                      >
                        <span className="text-muted-foreground shrink-0">
                          {formatTimestamp(log.timestamp)}
                        </span>
                        <span className={cn('shrink-0 w-12', style.text)}>
                          [{style.label}]
                        </span>
                        {log.source && (
                          <span className="text-purple-400 shrink-0">
                            [{log.source}]
                          </span>
                        )}
                        <span className="flex-1 break-words">{log.message}</span>
                      </div>
                    );
                  })
                )}
                <div ref={logEndRef} />
              </div>
            </ScrollArea>
          </div>
        </TabsContent>

        {/* Variables Tab */}
        <TabsContent value="variables" className="flex-1 m-0 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-2">
              {Object.keys(variables).length === 0 ? (
                <div className="text-muted-foreground text-xs py-4 text-center">
                  No variables to display
                </div>
              ) : (
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-1 px-2 font-medium">Name</th>
                      <th className="text-left py-1 px-2 font-medium">Value</th>
                      <th className="text-left py-1 px-2 font-medium">Type</th>
                      <th className="text-left py-1 px-2 font-medium">Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.values(variables).map((variable) => (
                      <tr
                        key={variable.name}
                        className={cn(
                          'border-b border-muted/50',
                          variable.changed && 'bg-yellow-500/10'
                        )}
                      >
                        <td className="py-1 px-2 font-mono">{variable.name}</td>
                        <td className="py-1 px-2 font-mono truncate max-w-[200px]">
                          {JSON.stringify(variable.value)}
                        </td>
                        <td className="py-1 px-2 text-muted-foreground">
                          {variable.type}
                        </td>
                        <td className="py-1 px-2 text-muted-foreground">
                          {variable.source}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Trace Tab - Enhanced with expandable step inspection */}
        <TabsContent value="trace" className="flex-1 m-0 overflow-hidden">
          <div className="flex flex-col h-full">
            <div className="flex items-center gap-2 px-2 py-1 border-b bg-muted/30">
              <span className="text-xs text-muted-foreground">
                {executionTrace.length} steps
              </span>
              <div className="flex-1" />
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs px-2"
                onClick={() => setExpandedSteps(new Set(executionTrace.map(s => s.stepId)))}
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
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs px-2"
                onClick={onClearTrace}
              >
                Clear
              </Button>
            </div>
            <ScrollArea className="flex-1">
              <div className="p-2 space-y-2">
                {executionTrace.length === 0 ? (
                  <div className="text-muted-foreground text-xs py-4 text-center">
                    No execution trace. Run your pipeline to see step-by-step execution details.
                  </div>
                ) : (
                  executionTrace.map((step, index) => {
                    const isExpanded = expandedSteps.has(step.stepId);
                    const hasInput = step.input && Object.keys(step.input).length > 0;
                    const hasOutput = step.output && Object.keys(step.output).length > 0;

                    return (
                      <div
                        key={step.stepId}
                        className="rounded border bg-muted/20"
                      >
                        {/* Step header - clickable to expand */}
                        <div
                          className={cn(
                            "flex items-center gap-2 px-3 py-2 text-xs cursor-pointer hover:bg-muted/40 transition-colors",
                            step.status === 'failed' && 'border-l-2 border-l-red-500',
                            step.status === 'completed' && 'border-l-2 border-l-green-500',
                            step.status === 'running' && 'border-l-2 border-l-blue-500'
                          )}
                          onClick={() => toggleStepExpanded(step.stepId)}
                        >
                          <button className="text-muted-foreground hover:text-foreground transition-colors">
                            {isExpanded ? (
                              <ChevronDown className="w-4 h-4" />
                            ) : (
                              <ChevronRight className="w-4 h-4" />
                            )}
                          </button>
                          <span className="text-muted-foreground w-6 shrink-0">{index + 1}</span>
                          <span className="font-medium">{step.stageName}</span>
                          <span className="text-muted-foreground">({step.componentType})</span>
                          <div className="flex-1" />

                          {/* Action buttons */}
                          <div className="flex items-center gap-1">
                            {onSelectStep && (
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onSelectStep(step);
                                }}
                                title="View in canvas"
                              >
                                <Eye className="w-3.5 h-3.5" />
                              </Button>
                            )}
                            {onRetryStep && step.status !== 'running' && step.input && (
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0 text-muted-foreground hover:text-blue-500"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onRetryStep(step);
                                }}
                                title="Retry this step with same input"
                              >
                                <RotateCcw className="w-3.5 h-3.5" />
                              </Button>
                            )}
                          </div>

                          <Badge
                            variant="outline"
                            className={cn('text-[10px] shrink-0', STATUS_STYLES[step.status])}
                          >
                            {step.status}
                          </Badge>
                          {step.duration !== undefined && (
                            <span className="text-muted-foreground shrink-0">
                              {step.duration}ms
                            </span>
                          )}
                        </div>

                        {/* Expanded content - Input/Output inspection */}
                        {isExpanded && (
                          <div className="border-t px-3 py-2 space-y-3 text-xs bg-background/50">
                            {/* Error display */}
                            {step.error && (
                              <div className="bg-red-500/10 border border-red-500/30 rounded p-2">
                                <div className="font-medium text-red-400 mb-1">Error</div>
                                <pre className="whitespace-pre-wrap text-red-300 font-mono text-[11px]">
                                  {step.error}
                                </pre>
                              </div>
                            )}

                            {/* Input section */}
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-medium text-muted-foreground">Input</span>
                                {hasInput && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-5 px-1.5 text-[10px]"
                                    onClick={() => copyStepData(`${step.stepId}-input`, step.input)}
                                  >
                                    {copiedStepId === `${step.stepId}-input` ? (
                                      <Check className="w-3 h-3 text-green-500" />
                                    ) : (
                                      <Copy className="w-3 h-3" />
                                    )}
                                  </Button>
                                )}
                              </div>
                              {hasInput ? (
                                <pre className="bg-muted/50 rounded p-2 font-mono text-[11px] max-h-40 overflow-auto whitespace-pre-wrap">
                                  {JSON.stringify(step.input, null, 2)}
                                </pre>
                              ) : (
                                <div className="text-muted-foreground italic">No input data</div>
                              )}
                            </div>

                            {/* Output section */}
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-medium text-muted-foreground">Output</span>
                                {hasOutput && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-5 px-1.5 text-[10px]"
                                    onClick={() => copyStepData(`${step.stepId}-output`, step.output)}
                                  >
                                    {copiedStepId === `${step.stepId}-output` ? (
                                      <Check className="w-3 h-3 text-green-500" />
                                    ) : (
                                      <Copy className="w-3 h-3" />
                                    )}
                                  </Button>
                                )}
                              </div>
                              {hasOutput ? (
                                <pre className="bg-muted/50 rounded p-2 font-mono text-[11px] max-h-40 overflow-auto whitespace-pre-wrap">
                                  {JSON.stringify(step.output, null, 2)}
                                </pre>
                              ) : step.status === 'running' ? (
                                <div className="text-muted-foreground italic">Running...</div>
                              ) : step.status === 'pending' ? (
                                <div className="text-muted-foreground italic">Pending</div>
                              ) : (
                                <div className="text-muted-foreground italic">No output data</div>
                              )}
                            </div>

                            {/* Logs for this step */}
                            {step.logs && step.logs.length > 0 && (
                              <div>
                                <div className="font-medium text-muted-foreground mb-1">Logs ({step.logs.length})</div>
                                <div className="bg-muted/50 rounded p-2 space-y-0.5 max-h-32 overflow-auto">
                                  {step.logs.map((log) => {
                                    const style = LOG_LEVEL_STYLES[log.level];
                                    return (
                                      <div
                                        key={log.id}
                                        className={cn('flex items-start gap-2 px-1 py-0.5 rounded text-[11px]', style.bg)}
                                      >
                                        <span className={cn('shrink-0', style.text)}>[{style.label}]</span>
                                        <span className="break-words">{log.message}</span>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </ScrollArea>
          </div>
        </TabsContent>

        {/* Breakpoints Tab */}
        <TabsContent value="breakpoints" className="flex-1 m-0 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-2 space-y-1">
              {breakpoints.length === 0 ? (
                <div className="text-muted-foreground text-xs py-4 text-center">
                  No breakpoints set
                </div>
              ) : (
                breakpoints.map((bp) => (
                  <div
                    key={bp.id}
                    className={cn(
                      'flex items-center gap-2 px-2 py-1 rounded text-xs',
                      bp.enabled ? 'bg-red-500/10' : 'bg-muted/30 opacity-50'
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={bp.enabled}
                      onChange={() => onToggleBreakpoint(bp.id)}
                      className="h-3 w-3"
                    />
                    <span className="font-mono">{bp.stageId}</span>
                    {bp.condition && (
                      <span className="text-muted-foreground">
                        when: {bp.condition}
                      </span>
                    )}
                    <div className="flex-1" />
                    <span className="text-muted-foreground">
                      hits: {bp.hitCount}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-5 w-5 p-0 text-muted-foreground hover:text-destructive"
                      onClick={() => onRemoveBreakpoint(bp.id)}
                    >
                      x
                    </Button>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Network Tab */}
        <TabsContent value="network" className="flex-1 m-0 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-2 space-y-1">
              {networkCalls.length === 0 ? (
                <div className="text-muted-foreground text-xs py-4 text-center">
                  No network calls
                </div>
              ) : (
                networkCalls.map((call) => (
                  <div
                    key={call.id}
                    className="flex items-center gap-2 px-2 py-1 rounded bg-muted/30 text-xs"
                  >
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
                        <span className="text-muted-foreground truncate max-w-[200px]">
                          {call.url}
                        </span>
                      </>
                    )}
                    <div className="flex-1" />
                    <Badge
                      variant="outline"
                      className={cn('text-[10px]', STATUS_STYLES[call.status])}
                    >
                      {call.status}
                    </Badge>
                    {call.tokens && (
                      <span className="text-muted-foreground">
                        {call.tokens.total} tokens
                      </span>
                    )}
                    {call.duration !== undefined && (
                      <span className="text-muted-foreground">
                        {call.duration}ms
                      </span>
                    )}
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default DebugPanel;
