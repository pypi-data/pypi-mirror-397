/**
 * Pipeline Runner
 *
 * Integrated component for running and debugging pipelines with:
 * - Input form with validation
 * - Execution controls (play, pause, step, stop)
 * - Real-time execution timeline
 * - Results display with stage inspection
 * - Debug mode with breakpoints
 */

import { useState, useMemo, useEffect } from 'react';
import {
  Play,
  Pause,
  Square,
  SkipForward,
  RotateCcw,
  Bug,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  Zap,
  AlertTriangle,
  Copy,
  Check,
  Sparkles,
  Eye,
  EyeOff,
} from 'lucide-react';
import {
  Button,
  Badge,
  Card,
  CardContent,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
  ScrollArea,
} from '@/components/ui';
import { cn } from '../../lib/utils';
import { RunInputPanel } from './RunInputPanel';
import { ExecutionTimeline } from './ExecutionTimeline';
import type {
  Pipeline,
  PipelineRun,
  PipelineStage,
  ExecutionStep,
  DebugMode,
} from '../../types';
import type { StageExecutionState } from '../../contexts/DebugContext';

interface PipelineRunnerProps {
  pipeline: Pipeline;
  stages: PipelineStage[];
  configuredProviders: string[];
  defaultProvider?: string;

  // Debug context
  debugMode: DebugMode;
  currentRun: PipelineRun | null;
  executionTrace: ExecutionStep[];
  stageExecutionStates?: Record<string, StageExecutionState>;
  isDebugEnabled: boolean;
  breakpointCount: number;

  // Actions
  onStartExecution: (inputs: Record<string, unknown>) => void;
  onPauseExecution: () => void;
  onResumeExecution: () => void;
  onStepExecution: () => void;
  onStopExecution: () => void;
  onRestartExecution: () => void;
  onToggleDebugMode: () => void;
  onSelectStage: (stageId: string) => void;
  onInspectStage: (stageId: string) => void;
}

export function PipelineRunner({
  pipeline,
  stages,
  configuredProviders,
  defaultProvider,
  debugMode,
  currentRun,
  executionTrace,
  isDebugEnabled,
  breakpointCount,
  onStartExecution,
  onPauseExecution,
  onResumeExecution,
  onStepExecution,
  onStopExecution,
  onRestartExecution,
  onToggleDebugMode,
  onSelectStage,
  onInspectStage,
}: PipelineRunnerProps) {
  const [isResultExpanded, setIsResultExpanded] = useState(true);
  const [isTimelineExpanded, setIsTimelineExpanded] = useState(true);
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showRawOutput, setShowRawOutput] = useState(false);

  const isRunning = debugMode === 'running' || debugMode === 'stepping';
  const isPaused = debugMode === 'paused';
  const isStopped = debugMode === 'stopped';
  const hasRun = currentRun !== null;

  // Auto-expand failed stages
  useEffect(() => {
    if (currentRun?.status === 'failed' && currentRun.trace?.stages) {
      const failedStage = currentRun.trace.stages.find((s) => s.status === 'failed');
      if (failedStage) {
        setExpandedStages((prev) => new Set([...prev, failedStage.stage_id]));
      }
    }
  }, [currentRun?.status, currentRun?.trace?.stages]);

  // Toggle stage expansion
  const toggleStage = (stageId: string) => {
    setExpandedStages((prev) => {
      const next = new Set(prev);
      if (next.has(stageId)) next.delete(stageId);
      else next.add(stageId);
      return next;
    });
  };

  // Copy to clipboard
  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // Ignore
    }
  };

  // Status configuration
  const runStatusConfig = useMemo(() => {
    if (!currentRun) return null;

    switch (currentRun.status) {
      case 'pending':
        return {
          icon: Clock,
          label: 'Pending',
          color: 'text-slate-500',
          bgColor: 'bg-slate-100 dark:bg-slate-800',
        };
      case 'running':
        return {
          icon: Loader2,
          label: 'Running',
          color: 'text-blue-500',
          bgColor: 'bg-blue-100 dark:bg-blue-900/30',
          animate: true,
        };
      case 'completed':
        return {
          icon: CheckCircle2,
          label: 'Completed',
          color: 'text-green-500',
          bgColor: 'bg-green-100 dark:bg-green-900/30',
        };
      case 'failed':
        return {
          icon: XCircle,
          label: 'Failed',
          color: 'text-red-500',
          bgColor: 'bg-red-100 dark:bg-red-900/30',
        };
      case 'cancelled':
        return {
          icon: Square,
          label: 'Cancelled',
          color: 'text-amber-500',
          bgColor: 'bg-amber-100 dark:bg-amber-900/30',
        };
      default:
        return null;
    }
  }, [currentRun?.status]);

  const RunStatusIcon = runStatusConfig?.icon;

  return (
    <TooltipProvider>
      <div className="h-full flex flex-col bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800">
        {/* Header with controls */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900">
          <h3 className="font-semibold text-slate-900 dark:text-slate-100">Run Pipeline</h3>

          <div className="flex-1" />

          {/* Debug toggle */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={isDebugEnabled ? 'default' : 'outline'}
                size="sm"
                className={cn(
                  'h-8 gap-1.5',
                  isDebugEnabled && 'bg-purple-600 hover:bg-purple-700'
                )}
                onClick={onToggleDebugMode}
              >
                <Bug className="w-4 h-4" />
                Debug
                {breakpointCount > 0 && (
                  <Badge
                    variant="secondary"
                    className={cn(
                      'h-5 px-1.5 text-xs',
                      isDebugEnabled && 'bg-purple-800 text-purple-100'
                    )}
                  >
                    {breakpointCount}
                  </Badge>
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {isDebugEnabled ? 'Disable debug mode' : 'Enable debug mode (stops at breakpoints)'}
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Execution controls */}
        <div className="flex items-center gap-1 px-4 py-2 border-b border-slate-200 dark:border-slate-800 bg-muted/30">
          <div className="flex items-center gap-1 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-0.5">
            {/* Play/Pause */}
            {isRunning ? (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={onPauseExecution}>
                    <Pause className="h-4 w-4 text-amber-600" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Pause</TooltipContent>
              </Tooltip>
            ) : isPaused ? (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={onResumeExecution}>
                    <Play className="h-4 w-4 text-green-600" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Resume</TooltipContent>
              </Tooltip>
            ) : null}

            {/* Step */}
            {(isPaused || (isStopped && hasRun)) && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={onStepExecution}>
                    <SkipForward className="h-4 w-4 text-purple-600" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Step</TooltipContent>
              </Tooltip>
            )}

            {/* Stop */}
            {!isStopped && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={onStopExecution}>
                    <Square className="h-4 w-4 text-red-600" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Stop</TooltipContent>
              </Tooltip>
            )}

            {/* Restart */}
            {hasRun && isStopped && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={onRestartExecution}>
                    <RotateCcw className="h-4 w-4 text-blue-600" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Restart</TooltipContent>
              </Tooltip>
            )}
          </div>

          {/* Status indicator */}
          {runStatusConfig && RunStatusIcon && (
            <div
              className={cn(
                'flex items-center gap-2 px-2.5 py-1 rounded-md ml-2',
                runStatusConfig.bgColor
              )}
            >
              <RunStatusIcon
                className={cn(
                  'h-4 w-4',
                  runStatusConfig.color,
                  runStatusConfig.animate && 'animate-spin'
                )}
              />
              <span className={cn('text-sm font-medium', runStatusConfig.color)}>
                {runStatusConfig.label}
              </span>
            </div>
          )}

          <div className="flex-1" />

          {/* Usage metrics */}
          {currentRun?.usage && (
            <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
              <span className="flex items-center gap-1">
                <Zap className="h-3.5 w-3.5" />
                {currentRun.usage.total_tokens.toLocaleString()}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" />
                {(currentRun.usage.execution_time_ms / 1000).toFixed(2)}s
              </span>
              <span className="font-medium text-slate-700 dark:text-slate-300">
                ${currentRun.usage.total_cost.toFixed(4)}
              </span>
            </div>
          )}
        </div>

        {/* Content */}
        <ScrollArea className="flex-1">
          <div className="p-4 space-y-4">
            {/* Input Section */}
            <RunInputPanel
              inputSchema={pipeline.input_schema || null}
              sampleInput={pipeline.sample_input}
              stages={stages}
              isRunning={isRunning}
              onRun={onStartExecution}
              configuredProviders={configuredProviders}
              defaultProvider={defaultProvider}
            />

            {/* Timeline Section */}
            {executionTrace.length > 0 && (
              <Card className="border-slate-200 dark:border-slate-700">
                <button
                  className="w-full flex items-center justify-between p-3 hover:bg-muted/50 transition-colors"
                  onClick={() => setIsTimelineExpanded(!isTimelineExpanded)}
                >
                  <div className="flex items-center gap-2">
                    {isTimelineExpanded ? (
                      <ChevronDown className="w-4 h-4 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    )}
                    <span className="font-medium">Execution Timeline</span>
                    <Badge variant="secondary" className="text-xs">
                      {executionTrace.filter((s) => s.status === 'completed').length}/{executionTrace.length}
                    </Badge>
                  </div>
                </button>
                {isTimelineExpanded && (
                  <CardContent className="pt-0">
                    <ExecutionTimeline
                      steps={executionTrace}
                      currentStageId={null}
                      onStageClick={onSelectStage}
                      compact
                    />
                  </CardContent>
                )}
              </Card>
            )}

            {/* Results Section */}
            {currentRun && (
              <Card className="border-slate-200 dark:border-slate-700">
                <button
                  className="w-full flex items-center justify-between p-3 hover:bg-muted/50 transition-colors"
                  onClick={() => setIsResultExpanded(!isResultExpanded)}
                >
                  <div className="flex items-center gap-2">
                    {isResultExpanded ? (
                      <ChevronDown className="w-4 h-4 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    )}
                    <span className="font-medium">Results</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowRawOutput(!showRawOutput);
                          }}
                        >
                          {showRawOutput ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>{showRawOutput ? 'Show formatted' : 'Show raw JSON'}</TooltipContent>
                    </Tooltip>
                  </div>
                </button>

                {isResultExpanded && (
                  <CardContent className="pt-0 space-y-4">
                    {/* Error display */}
                    {currentRun.error && (
                      <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertTriangle className="w-4 h-4 text-red-500" />
                          <span className="font-medium text-red-700 dark:text-red-400">Error</span>
                        </div>
                        <pre className="text-xs text-red-600 dark:text-red-300 whitespace-pre-wrap font-mono">
                          {currentRun.error}
                        </pre>
                      </div>
                    )}

                    {/* Stage traces */}
                    {currentRun.trace?.stages && currentRun.trace.stages.length > 0 && (
                      <div className="space-y-2">
                        <div className="text-sm font-medium text-muted-foreground">Stage Results</div>
                        {currentRun.trace.stages.map((stage, index) => {
                          const isExpanded = expandedStages.has(stage.stage_id);
                          const pipelineStage = stages.find((s) => s.id === stage.stage_id);
                          const hasOutput = stage.output && Object.keys(stage.output).length > 0;

                          return (
                            <div
                              key={stage.stage_id}
                              className={cn(
                                'rounded-lg border',
                                stage.status === 'failed'
                                  ? 'border-red-200 dark:border-red-800'
                                  : 'border-slate-200 dark:border-slate-700'
                              )}
                            >
                              <button
                                className={cn(
                                  'w-full flex items-center gap-2 p-2.5 text-sm text-left hover:bg-muted/50',
                                  stage.status === 'failed' && 'bg-red-50 dark:bg-red-900/10'
                                )}
                                onClick={() => toggleStage(stage.stage_id)}
                              >
                                {isExpanded ? (
                                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                                ) : (
                                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                                )}
                                <span className="text-muted-foreground w-5">{index + 1}</span>
                                <span className="font-medium flex-1">
                                  {pipelineStage?.name || stage.stage_id}
                                </span>
                                <Badge
                                  variant="outline"
                                  className={cn(
                                    'text-xs',
                                    stage.status === 'completed' && 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
                                    stage.status === 'failed' && 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
                                    stage.status === 'running' && 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                                  )}
                                >
                                  {stage.status}
                                </Badge>
                                {stage.usage?.execution_time_ms && (
                                  <span className="text-xs text-muted-foreground">
                                    {stage.usage.execution_time_ms}ms
                                  </span>
                                )}
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-6 w-6 p-0"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    onInspectStage(stage.stage_id);
                                  }}
                                >
                                  <Eye className="w-3.5 h-3.5" />
                                </Button>
                              </button>

                              {isExpanded && (
                                <div className="p-3 border-t border-slate-200 dark:border-slate-700 space-y-3 text-xs bg-muted/20">
                                  {stage.error && (
                                    <div className="p-2 rounded bg-red-100 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                                      <div className="font-medium text-red-700 dark:text-red-400 mb-1">Error</div>
                                      <pre className="whitespace-pre-wrap text-red-600 dark:text-red-300 font-mono">
                                        {stage.error}
                                      </pre>
                                    </div>
                                  )}

                                  {stage.input && Object.keys(stage.input).length > 0 && (
                                    <div>
                                      <div className="flex items-center justify-between mb-1">
                                        <span className="font-medium text-muted-foreground">Input</span>
                                        <Button
                                          variant="ghost"
                                          size="sm"
                                          className="h-5 px-1.5"
                                          onClick={() => copyToClipboard(JSON.stringify(stage.input, null, 2), `${stage.stage_id}-input`)}
                                        >
                                          {copiedId === `${stage.stage_id}-input` ? (
                                            <Check className="w-3 h-3 text-green-500" />
                                          ) : (
                                            <Copy className="w-3 h-3" />
                                          )}
                                        </Button>
                                      </div>
                                      <pre className="p-2 rounded bg-slate-100 dark:bg-slate-800 font-mono text-[11px] max-h-32 overflow-auto whitespace-pre-wrap">
                                        {JSON.stringify(stage.input, null, 2)}
                                      </pre>
                                    </div>
                                  )}

                                  {hasOutput && (
                                    <div>
                                      <div className="flex items-center justify-between mb-1">
                                        <span className="font-medium text-muted-foreground">Output</span>
                                        <Button
                                          variant="ghost"
                                          size="sm"
                                          className="h-5 px-1.5"
                                          onClick={() => copyToClipboard(JSON.stringify(stage.output, null, 2), `${stage.stage_id}-output`)}
                                        >
                                          {copiedId === `${stage.stage_id}-output` ? (
                                            <Check className="w-3 h-3 text-green-500" />
                                          ) : (
                                            <Copy className="w-3 h-3" />
                                          )}
                                        </Button>
                                      </div>
                                      <pre className="p-2 rounded bg-slate-100 dark:bg-slate-800 font-mono text-[11px] max-h-32 overflow-auto whitespace-pre-wrap">
                                        {JSON.stringify(stage.output, null, 2)}
                                      </pre>
                                    </div>
                                  )}

                                  {stage.usage && (
                                    <div className="flex items-center gap-4 text-muted-foreground pt-2 border-t">
                                      <span>{stage.usage.total_tokens} tokens</span>
                                      <span>{stage.usage.execution_time_ms}ms</span>
                                      <span className="font-medium">${stage.usage.total_cost.toFixed(4)}</span>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* Final output */}
                    {currentRun.output && (
                      <div className="mt-4 pt-4 border-t">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-green-700 dark:text-green-400 flex items-center gap-2">
                            <Sparkles className="w-4 h-4" />
                            Final Output
                          </span>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2"
                            onClick={() => copyToClipboard(JSON.stringify(currentRun.output, null, 2), 'final-output')}
                          >
                            {copiedId === 'final-output' ? (
                              <Check className="w-3 h-3 text-green-500 mr-1" />
                            ) : (
                              <Copy className="w-3 h-3 mr-1" />
                            )}
                            Copy
                          </Button>
                        </div>
                        {showRawOutput ? (
                          <pre className="p-3 rounded-lg bg-slate-100 dark:bg-slate-800 font-mono text-xs max-h-64 overflow-auto whitespace-pre-wrap">
                            {JSON.stringify(currentRun.output, null, 2)}
                          </pre>
                        ) : (
                          <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                            {'content' in currentRun.output && typeof currentRun.output.content === 'string' ? (
                              <div className="whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300">
                                {currentRun.output.content}
                              </div>
                            ) : (
                              <pre className="font-mono text-xs whitespace-pre-wrap">
                                {JSON.stringify(currentRun.output, null, 2)}
                              </pre>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            )}
          </div>
        </ScrollArea>
      </div>
    </TooltipProvider>
  );
}

export default PipelineRunner;
