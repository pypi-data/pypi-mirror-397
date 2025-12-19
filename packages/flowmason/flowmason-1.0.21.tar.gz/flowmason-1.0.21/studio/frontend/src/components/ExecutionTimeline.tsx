/**
 * Execution Timeline
 *
 * A horizontal timeline component showing the execution order and status
 * of pipeline stages. Displays each stage with its status, timing, and
 * allows clicking to jump to a stage on the canvas.
 */

import { useMemo } from 'react';
import {
  CheckCircle,
  XCircle,
  Loader2,
  Clock,
  ChevronRight,
} from 'lucide-react';
import type { ExecutionStatus, StageExecutionState } from './PipelineCanvas';
import type { PipelineStage } from '../types';

interface ExecutionTimelineProps {
  stages: PipelineStage[];
  stageExecutionStates: Record<string, StageExecutionState>;
  onStageClick?: (stageId: string) => void;
}

const statusConfig: Record<ExecutionStatus, {
  icon: typeof CheckCircle;
  iconClass: string;
  bgClass: string;
  borderClass: string;
  textClass: string;
}> = {
  idle: {
    icon: Clock,
    iconClass: 'text-slate-400',
    bgClass: 'bg-slate-100 dark:bg-slate-800',
    borderClass: 'border-slate-200 dark:border-slate-700',
    textClass: 'text-slate-500 dark:text-slate-400',
  },
  pending: {
    icon: Clock,
    iconClass: 'text-slate-500',
    bgClass: 'bg-slate-100 dark:bg-slate-800',
    borderClass: 'border-slate-300 dark:border-slate-600',
    textClass: 'text-slate-600 dark:text-slate-400',
  },
  running: {
    icon: Loader2,
    iconClass: 'text-blue-500 animate-spin',
    bgClass: 'bg-blue-50 dark:bg-blue-900/30',
    borderClass: 'border-blue-300 dark:border-blue-700',
    textClass: 'text-blue-600 dark:text-blue-400',
  },
  completed: {
    icon: CheckCircle,
    iconClass: 'text-green-500',
    bgClass: 'bg-green-50 dark:bg-green-900/30',
    borderClass: 'border-green-300 dark:border-green-700',
    textClass: 'text-green-600 dark:text-green-400',
  },
  success: {
    icon: CheckCircle,
    iconClass: 'text-green-500',
    bgClass: 'bg-green-50 dark:bg-green-900/30',
    borderClass: 'border-green-300 dark:border-green-700',
    textClass: 'text-green-600 dark:text-green-400',
  },
  failed: {
    icon: XCircle,
    iconClass: 'text-red-500',
    bgClass: 'bg-red-50 dark:bg-red-900/30',
    borderClass: 'border-red-300 dark:border-red-700',
    textClass: 'text-red-600 dark:text-red-400',
  },
};

export function ExecutionTimeline({
  stages,
  stageExecutionStates,
  onStageClick,
}: ExecutionTimelineProps) {
  // Sort stages in topological order based on dependencies
  const sortedStages = useMemo(() => {
    const sorted: PipelineStage[] = [];
    const visited = new Set<string>();
    const visiting = new Set<string>();

    function visit(stage: PipelineStage) {
      if (visited.has(stage.id)) return;
      if (visiting.has(stage.id)) return; // Cycle detected, skip

      visiting.add(stage.id);

      // Visit dependencies first
      for (const depId of stage.depends_on) {
        const depStage = stages.find(s => s.id === depId);
        if (depStage) {
          visit(depStage);
        }
      }

      visiting.delete(stage.id);
      visited.add(stage.id);
      sorted.push(stage);
    }

    for (const stage of stages) {
      visit(stage);
    }

    return sorted;
  }, [stages]);

  // Check if there's any execution activity
  const hasExecutionData = useMemo(() => {
    return Object.values(stageExecutionStates).some(
      state => state.status !== 'idle'
    );
  }, [stageExecutionStates]);

  // Calculate total time (sum of all completed stages)
  const totalTime = useMemo(() => {
    let total = 0;
    for (const state of Object.values(stageExecutionStates)) {
      if (state.startTime && state.endTime) {
        total += state.endTime - state.startTime;
      }
    }
    return total;
  }, [stageExecutionStates]);

  if (sortedStages.length === 0) {
    return null;
  }

  return (
    <div className="w-full bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700 px-4 py-3">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
          Execution Timeline
        </span>
        {totalTime > 0 && (
          <span className="text-xs text-slate-500 dark:text-slate-400">
            Total: {formatDuration(totalTime)}
          </span>
        )}
      </div>

      {/* Timeline */}
      <div className="flex items-center gap-1 overflow-x-auto pb-2">
        {sortedStages.map((stage, index) => {
          const execState = stageExecutionStates[stage.id];
          const status = execState?.status || 'idle';
          const config = statusConfig[status];
          const StatusIcon = config.icon;

          const duration = execState?.startTime && execState?.endTime
            ? execState.endTime - execState.startTime
            : null;

          return (
            <div key={stage.id} className="flex items-center">
              {/* Stage card */}
              <button
                onClick={() => onStageClick?.(stage.id)}
                className={`
                  flex flex-col items-center px-3 py-2 rounded-lg border transition-all
                  hover:shadow-md cursor-pointer min-w-[100px]
                  ${config.bgClass} ${config.borderClass}
                  ${!hasExecutionData && status === 'idle' ? 'opacity-60' : ''}
                `}
              >
                <StatusIcon className={`w-4 h-4 mb-1 ${config.iconClass}`} />
                <span className={`text-xs font-medium truncate max-w-[80px] ${config.textClass}`}>
                  {stage.name}
                </span>
                {duration !== null && (
                  <span className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                    {formatDuration(duration)}
                  </span>
                )}
                {status === 'running' && (
                  <span className="text-xs text-blue-400 dark:text-blue-500 mt-0.5">
                    running...
                  </span>
                )}
              </button>

              {/* Connector arrow (not after last item) */}
              {index < sortedStages.length - 1 && (
                <ChevronRight className="w-4 h-4 text-slate-300 dark:text-slate-600 mx-1 flex-shrink-0" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatDuration(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`;
  }
  const seconds = ms / 1000;
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
}

export default ExecutionTimeline;
