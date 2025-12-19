/**
 * Execution Controls
 *
 * Professional execution control toolbar with:
 * - Play/Pause/Stop/Step controls
 * - Execution status indicator
 * - Timing display
 * - Breakpoint toggle
 * - Quick actions
 */

import { useState, useEffect, useMemo } from 'react';
import {
  Play,
  Pause,
  Square,
  SkipForward,
  RotateCcw,
  Bug,
  Zap,
  Clock,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Loader2,
  ChevronDown,
  Settings2,
  Trash2,
} from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../ui/tooltip';
import { cn } from '../../lib/utils';
import type { DebugMode, PipelineRun } from '../../types';

interface ExecutionControlsProps {
  mode: DebugMode;
  currentRun: PipelineRun | null;
  breakpointCount: number;
  hasBreakpointsEnabled: boolean;
  isDebugMode: boolean;
  canRun: boolean;
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onStep: () => void;
  onRestart: () => void;
  onToggleDebugMode: () => void;
  onClearBreakpoints: () => void;
  onOpenSettings?: () => void;
}

export function ExecutionControls({
  mode,
  currentRun,
  breakpointCount,
  hasBreakpointsEnabled,
  isDebugMode,
  canRun,
  onPlay,
  onPause,
  onStop,
  onStep,
  onRestart,
  onToggleDebugMode,
  onClearBreakpoints,
  onOpenSettings,
}: ExecutionControlsProps) {
  const [elapsedTime, setElapsedTime] = useState(0);

  // Track elapsed time
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;

    if (mode === 'running' || mode === 'stepping') {
      const startTime = currentRun?.started_at
        ? new Date(currentRun.started_at).getTime()
        : Date.now();

      interval = setInterval(() => {
        setElapsedTime(Date.now() - startTime);
      }, 100);
    } else if (mode === 'stopped') {
      setElapsedTime(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [mode, currentRun?.started_at]);

  // Format elapsed time
  const formattedTime = useMemo(() => {
    const seconds = Math.floor(elapsedTime / 1000);
    const ms = elapsedTime % 1000;
    if (seconds < 60) {
      return `${seconds}.${Math.floor(ms / 100)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }, [elapsedTime]);

  // Status configuration
  const statusConfig = useMemo(() => {
    switch (mode) {
      case 'running':
        return {
          icon: Loader2,
          label: 'Running',
          color: 'text-blue-500',
          bgColor: 'bg-blue-500/10',
          borderColor: 'border-blue-500/30',
          animate: true,
        };
      case 'paused':
        return {
          icon: Pause,
          label: 'Paused',
          color: 'text-amber-500',
          bgColor: 'bg-amber-500/10',
          borderColor: 'border-amber-500/30',
          animate: false,
        };
      case 'stepping':
        return {
          icon: SkipForward,
          label: 'Stepping',
          color: 'text-purple-500',
          bgColor: 'bg-purple-500/10',
          borderColor: 'border-purple-500/30',
          animate: true,
        };
      case 'stopped':
      default:
        if (currentRun?.status === 'completed') {
          return {
            icon: CheckCircle2,
            label: 'Completed',
            color: 'text-green-500',
            bgColor: 'bg-green-500/10',
            borderColor: 'border-green-500/30',
            animate: false,
          };
        }
        if (currentRun?.status === 'failed') {
          return {
            icon: XCircle,
            label: 'Failed',
            color: 'text-red-500',
            bgColor: 'bg-red-500/10',
            borderColor: 'border-red-500/30',
            animate: false,
          };
        }
        return {
          icon: Square,
          label: 'Ready',
          color: 'text-slate-400',
          bgColor: 'bg-slate-500/10',
          borderColor: 'border-slate-500/30',
          animate: false,
        };
    }
  }, [mode, currentRun?.status]);

  const StatusIcon = statusConfig.icon;
  const isRunning = mode === 'running' || mode === 'stepping';
  const isPaused = mode === 'paused';
  const isStopped = mode === 'stopped';

  return (
    <TooltipProvider>
      <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
        {/* Main control buttons */}
        <div className="flex items-center gap-1 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-1 shadow-sm">
          {/* Play/Pause */}
          {isRunning ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onPause}
                  className="h-8 w-8 p-0 hover:bg-amber-100 dark:hover:bg-amber-900/30"
                >
                  <Pause className="h-4 w-4 text-amber-600" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Pause (F8)</TooltipContent>
            </Tooltip>
          ) : isPaused ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onPlay}
                  className="h-8 w-8 p-0 hover:bg-green-100 dark:hover:bg-green-900/30"
                >
                  <Play className="h-4 w-4 text-green-600" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Resume (F5)</TooltipContent>
            </Tooltip>
          ) : (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onPlay}
                  disabled={!canRun}
                  className="h-8 w-8 p-0 hover:bg-green-100 dark:hover:bg-green-900/30 disabled:opacity-50"
                >
                  <Play className="h-4 w-4 text-green-600" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Run Pipeline (F5)</TooltipContent>
            </Tooltip>
          )}

          {/* Step */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={onStep}
                disabled={!isPaused && !isStopped}
                className="h-8 w-8 p-0 hover:bg-purple-100 dark:hover:bg-purple-900/30 disabled:opacity-50"
              >
                <SkipForward className="h-4 w-4 text-purple-600" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Step Over (F10)</TooltipContent>
          </Tooltip>

          {/* Stop */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={onStop}
                disabled={isStopped}
                className="h-8 w-8 p-0 hover:bg-red-100 dark:hover:bg-red-900/30 disabled:opacity-50"
              >
                <Square className="h-4 w-4 text-red-600" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Stop (Shift+F5)</TooltipContent>
          </Tooltip>

          {/* Restart */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={onRestart}
                disabled={isStopped && !currentRun}
                className="h-8 w-8 p-0 hover:bg-blue-100 dark:hover:bg-blue-900/30 disabled:opacity-50"
              >
                <RotateCcw className="h-4 w-4 text-blue-600" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Restart (Ctrl+Shift+F5)</TooltipContent>
          </Tooltip>
        </div>

        {/* Separator */}
        <div className="h-6 w-px bg-slate-200 dark:bg-slate-700" />

        {/* Status indicator */}
        <div
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-md border',
            statusConfig.bgColor,
            statusConfig.borderColor
          )}
        >
          <StatusIcon
            className={cn(
              'h-4 w-4',
              statusConfig.color,
              statusConfig.animate && 'animate-spin'
            )}
          />
          <span className={cn('text-sm font-medium', statusConfig.color)}>
            {statusConfig.label}
          </span>
          {(isRunning || isPaused) && (
            <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
              {formattedTime}
            </span>
          )}
        </div>

        {/* Separator */}
        <div className="h-6 w-px bg-slate-200 dark:bg-slate-700" />

        {/* Debug mode toggle */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={isDebugMode ? 'default' : 'outline'}
              size="sm"
              onClick={onToggleDebugMode}
              className={cn(
                'h-8 gap-1.5',
                isDebugMode && 'bg-purple-600 hover:bg-purple-700'
              )}
            >
              <Bug className="h-4 w-4" />
              Debug
              {hasBreakpointsEnabled && (
                <Badge
                  variant="secondary"
                  className={cn(
                    'ml-1 h-5 px-1.5 text-xs',
                    isDebugMode && 'bg-purple-800 text-purple-100'
                  )}
                >
                  {breakpointCount}
                </Badge>
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            {isDebugMode ? 'Disable Debug Mode' : 'Enable Debug Mode'}
          </TooltipContent>
        </Tooltip>

        {/* Breakpoints dropdown */}
        {breakpointCount > 0 && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="h-8 gap-1.5">
                <AlertCircle className="h-4 w-4 text-red-500" />
                <span className="text-xs">{breakpointCount} breakpoints</span>
                <ChevronDown className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              <DropdownMenuItem onClick={onClearBreakpoints}>
                <Trash2 className="h-4 w-4 mr-2" />
                Clear All Breakpoints
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        {/* Spacer */}
        <div className="flex-1" />

        {/* Usage metrics (when run completed) */}
        {currentRun?.usage && mode === 'stopped' && (
          <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1">
              <Zap className="h-3.5 w-3.5" />
              {currentRun.usage.total_tokens.toLocaleString()} tokens
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

        {/* Settings button */}
        {onOpenSettings && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={onOpenSettings}
                className="h-8 w-8 p-0"
              >
                <Settings2 className="h-4 w-4 text-slate-500" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Execution Settings</TooltipContent>
          </Tooltip>
        )}
      </div>
    </TooltipProvider>
  );
}

export default ExecutionControls;
