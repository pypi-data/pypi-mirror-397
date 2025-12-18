/**
 * Execution Timeline
 *
 * Visual timeline showing stage execution progress with:
 * - Horizontal timeline with stage markers
 * - Real-time progress indication
 * - Duration and timing info
 * - Click to inspect stage
 * - Animated execution flow
 */

import { useMemo } from 'react';
import {
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  ChevronRight,
  AlertTriangle,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../ui/tooltip';
import { Badge } from '../ui/badge';
import type { ExecutionStep } from '../../types';

interface ExecutionTimelineProps {
  steps: ExecutionStep[];
  currentStageId: string | null;
  onStageClick?: (stageId: string) => void;
  compact?: boolean;
}

type StatusType = 'pending' | 'running' | 'completed' | 'failed' | 'skipped' | 'success';

interface StatusConfig {
  icon: typeof Clock;
  color: string;
  bgColor: string;
  borderColor: string;
  connectorColor: string;
  animate?: boolean;
}

const STATUS_CONFIG: Record<StatusType, StatusConfig> = {
  pending: {
    icon: Clock,
    color: 'text-slate-400',
    bgColor: 'bg-slate-100 dark:bg-slate-800',
    borderColor: 'border-slate-300 dark:border-slate-600',
    connectorColor: 'bg-slate-300 dark:bg-slate-600',
  },
  running: {
    icon: Loader2,
    color: 'text-blue-500',
    bgColor: 'bg-blue-100 dark:bg-blue-900/30',
    borderColor: 'border-blue-500',
    connectorColor: 'bg-blue-500',
    animate: true,
  },
  completed: {
    icon: CheckCircle2,
    color: 'text-green-500',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
    borderColor: 'border-green-500',
    connectorColor: 'bg-green-500',
  },
  failed: {
    icon: XCircle,
    color: 'text-red-500',
    bgColor: 'bg-red-100 dark:bg-red-900/30',
    borderColor: 'border-red-500',
    connectorColor: 'bg-red-500',
  },
  skipped: {
    icon: AlertTriangle,
    color: 'text-amber-500',
    bgColor: 'bg-amber-100 dark:bg-amber-900/30',
    borderColor: 'border-amber-500',
    connectorColor: 'bg-amber-500',
  },
  success: {
    icon: CheckCircle2,
    color: 'text-green-500',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
    borderColor: 'border-green-500',
    connectorColor: 'bg-green-500',
  },
};

export function ExecutionTimeline({
  steps,
  currentStageId,
  onStageClick,
  compact = false,
}: ExecutionTimelineProps) {
  // Calculate total duration
  const totalDuration = useMemo(() => {
    return steps.reduce((sum, step) => sum + (step.duration || 0), 0);
  }, [steps]);

  // Calculate relative widths based on duration
  const stepsWithWidth = useMemo(() => {
    if (totalDuration === 0) {
      // Equal width for all steps if no duration info
      const equalWidth = 100 / Math.max(steps.length, 1);
      return steps.map((step) => ({ ...step, widthPercent: equalWidth }));
    }

    return steps.map((step) => ({
      ...step,
      widthPercent: Math.max(((step.duration || 1) / totalDuration) * 100, 5),
    }));
  }, [steps, totalDuration]);

  if (steps.length === 0) {
    return (
      <div className="flex items-center justify-center py-4 text-sm text-slate-400 dark:text-slate-500">
        <Clock className="w-4 h-4 mr-2" />
        No execution steps yet
      </div>
    );
  }

  if (compact) {
    return (
      <TooltipProvider>
        <div className="flex items-center gap-1 py-2">
          {stepsWithWidth.map((step) => {
            const config = STATUS_CONFIG[step.status as StatusType] || STATUS_CONFIG.pending;
            const Icon = config.icon;
            const isCurrent = step.stageId === currentStageId;

            return (
              <Tooltip key={step.stepId}>
                <TooltipTrigger asChild>
                  <button
                    onClick={() => onStageClick?.(step.stageId)}
                    className={cn(
                      'flex items-center justify-center rounded-full transition-all',
                      config.bgColor,
                      config.borderColor,
                      'border-2',
                      isCurrent && 'ring-2 ring-offset-2 ring-blue-500',
                      'w-7 h-7 hover:scale-110'
                    )}
                  >
                    <Icon
                      className={cn(
                        'w-4 h-4',
                        config.color,
                        config.animate && 'animate-spin'
                      )}
                    />
                  </button>
                </TooltipTrigger>
                <TooltipContent>
                  <div className="text-center">
                    <div className="font-medium">{step.stageName}</div>
                    <div className="text-xs text-slate-400">
                      {step.status}
                      {step.duration && ` - ${step.duration}ms`}
                    </div>
                  </div>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>
    );
  }

  return (
    <TooltipProvider>
      <div className="py-4">
        {/* Timeline bar */}
        <div className="relative">
          {/* Background track */}
          <div className="absolute top-5 left-4 right-4 h-1 bg-slate-200 dark:bg-slate-700 rounded-full" />

          {/* Progress track */}
          <div className="absolute top-5 left-4 h-1 bg-gradient-to-r from-green-500 via-blue-500 to-blue-500 rounded-full transition-all duration-300">
            {/* Width based on completed steps */}
          </div>

          {/* Steps */}
          <div className="relative flex items-start">
            {stepsWithWidth.map((step, index) => {
              const config = STATUS_CONFIG[step.status as StatusType] || STATUS_CONFIG.pending;
              const Icon = config.icon;
              const isCurrent = step.stageId === currentStageId;
              const isLast = index === stepsWithWidth.length - 1;

              return (
                <div
                  key={step.stepId}
                  className="relative flex flex-col items-center"
                  style={{ width: `${step.widthPercent}%`, minWidth: '80px' }}
                >
                  {/* Connector line */}
                  {!isLast && (
                    <div
                      className={cn(
                        'absolute top-5 left-1/2 h-1 transition-colors duration-300',
                        step.status === 'completed'
                          ? config.connectorColor
                          : 'bg-slate-200 dark:bg-slate-700'
                      )}
                      style={{ width: 'calc(100% - 24px)', marginLeft: '12px' }}
                    />
                  )}

                  {/* Step marker */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => onStageClick?.(step.stageId)}
                        className={cn(
                          'relative z-10 flex items-center justify-center rounded-full border-2 transition-all',
                          config.bgColor,
                          config.borderColor,
                          isCurrent && 'ring-4 ring-blue-200 dark:ring-blue-800 scale-110',
                          'w-10 h-10 hover:scale-105',
                          step.status === 'running' && 'shadow-lg shadow-blue-500/30'
                        )}
                      >
                        <Icon
                          className={cn(
                            'w-5 h-5',
                            config.color,
                            config.animate && 'animate-spin'
                          )}
                        />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="max-w-xs">
                      <div className="space-y-1">
                        <div className="font-medium">{step.stageName}</div>
                        <div className="text-xs text-slate-400 font-mono">
                          {step.componentType}
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                          <Badge
                            variant="outline"
                            className={cn('text-xs', config.color)}
                          >
                            {step.status}
                          </Badge>
                          {step.duration && (
                            <span className="text-slate-400">
                              {step.duration}ms
                            </span>
                          )}
                        </div>
                        {step.error && (
                          <div className="text-xs text-red-400 mt-1">
                            {step.error.slice(0, 100)}
                            {step.error.length > 100 && '...'}
                          </div>
                        )}
                      </div>
                    </TooltipContent>
                  </Tooltip>

                  {/* Step label */}
                  <div className="mt-2 text-center max-w-full px-1">
                    <div
                      className={cn(
                        'text-xs font-medium truncate',
                        isCurrent
                          ? 'text-blue-600 dark:text-blue-400'
                          : 'text-slate-700 dark:text-slate-300'
                      )}
                    >
                      {step.stageName}
                    </div>
                    {step.duration !== undefined && (
                      <div className="text-xs text-slate-400 dark:text-slate-500">
                        {step.duration < 1000
                          ? `${step.duration}ms`
                          : `${(step.duration / 1000).toFixed(1)}s`}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Summary bar */}
        <div className="mt-4 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 px-4">
          <div className="flex items-center gap-4">
            <span>
              {steps.filter((s) => s.status === 'completed').length}/
              {steps.length} completed
            </span>
            {steps.some((s) => s.status === 'failed') && (
              <span className="text-red-500">
                {steps.filter((s) => s.status === 'failed').length} failed
              </span>
            )}
          </div>
          {totalDuration > 0 && (
            <span className="font-mono">
              Total: {totalDuration < 1000 ? `${totalDuration}ms` : `${(totalDuration / 1000).toFixed(2)}s`}
            </span>
          )}
        </div>
      </div>
    </TooltipProvider>
  );
}

/**
 * Vertical timeline variant for sidebar display
 */
export function ExecutionTimelineVertical({
  steps,
  currentStageId,
  onStageClick,
}: ExecutionTimelineProps) {
  if (steps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-sm text-slate-400 dark:text-slate-500">
        <Clock className="w-8 h-8 mb-2 opacity-50" />
        <span>No execution steps yet</span>
        <span className="text-xs mt-1">Run your pipeline to see the timeline</span>
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {steps.map((step, index) => {
        const config = STATUS_CONFIG[step.status as StatusType] || STATUS_CONFIG.pending;
        const Icon = config.icon;
        const isCurrent = step.stageId === currentStageId;
        const isLast = index === steps.length - 1;

        return (
          <div key={step.stepId} className="relative">
            {/* Vertical connector */}
            {!isLast && (
              <div
                className={cn(
                  'absolute left-5 top-10 w-0.5 h-full -translate-x-1/2',
                  step.status === 'completed'
                    ? config.connectorColor
                    : 'bg-slate-200 dark:bg-slate-700'
                )}
              />
            )}

            {/* Step row */}
            <button
              onClick={() => onStageClick?.(step.stageId)}
              className={cn(
                'relative flex items-start gap-3 w-full p-2 rounded-lg text-left transition-colors',
                isCurrent && 'bg-blue-50 dark:bg-blue-900/20',
                'hover:bg-slate-50 dark:hover:bg-slate-800/50'
              )}
            >
              {/* Step marker */}
              <div
                className={cn(
                  'relative z-10 flex items-center justify-center rounded-full border-2 flex-shrink-0',
                  config.bgColor,
                  config.borderColor,
                  'w-8 h-8',
                  isCurrent && 'ring-2 ring-blue-400 dark:ring-blue-500'
                )}
              >
                <Icon
                  className={cn(
                    'w-4 h-4',
                    config.color,
                    config.animate && 'animate-spin'
                  )}
                />
              </div>

              {/* Step content */}
              <div className="flex-1 min-w-0 py-0.5">
                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      'font-medium text-sm truncate',
                      isCurrent
                        ? 'text-blue-600 dark:text-blue-400'
                        : 'text-slate-700 dark:text-slate-300'
                    )}
                  >
                    {step.stageName}
                  </span>
                  <ChevronRight className="w-3 h-3 text-slate-400 flex-shrink-0" />
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-slate-400 dark:text-slate-500 font-mono truncate">
                    {step.componentType}
                  </span>
                  {step.duration !== undefined && (
                    <span className="text-xs text-slate-400 dark:text-slate-500">
                      {step.duration < 1000
                        ? `${step.duration}ms`
                        : `${(step.duration / 1000).toFixed(1)}s`}
                    </span>
                  )}
                </div>
                {step.error && (
                  <div className="text-xs text-red-500 mt-1 truncate">
                    {step.error}
                  </div>
                )}
              </div>
            </button>
          </div>
        );
      })}
    </div>
  );
}

export default ExecutionTimeline;
