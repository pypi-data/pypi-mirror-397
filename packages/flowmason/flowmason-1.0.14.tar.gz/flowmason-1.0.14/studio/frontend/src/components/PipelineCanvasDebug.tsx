/**
 * Pipeline Canvas Debug Extensions
 *
 * Enhanced node and edge components for debug mode with:
 * - Breakpoint indicators
 * - Current execution highlight
 * - Data flow visualization
 * - Input/Output preview on hover
 * - Performance metrics overlay
 */

import { memo, useMemo } from 'react';
import {
  Handle,
  Position,
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
} from '@xyflow/react';
import {
  Box,
  Zap,
  Sparkles,
  CheckCircle,
  XCircle,
  Loader2,
  Clock,
  Eye,
  CircleDot,
  Pause,
  AlertTriangle,
  Zap as Lightning,
} from 'lucide-react';
import { Badge } from '@/components/ui';
import { cn } from '../lib/utils';
import type { ExecutionStatus } from './PipelineCanvas';

// Extended node data with debug info
export interface DebugNodeData extends Record<string, unknown> {
  label: string;
  componentType: string;
  kind: 'node' | 'operator';
  color: string;
  config: Record<string, unknown>;
  requiresLLM?: boolean;
  description?: string;
  showNotes?: boolean;
  // Execution state
  executionStatus?: ExecutionStatus;
  hasExecutionData?: boolean;
  onInspect?: () => void;
  // Debug mode
  isDebugMode?: boolean;
  hasBreakpoint?: boolean;
  isBreakpointActive?: boolean;
  isPaused?: boolean;
  // Performance
  duration?: number;
  tokens?: number;
  cost?: number;
  // Data preview
  inputPreview?: string;
  outputPreview?: string;
}

// Status styling configurations
const executionStatusConfig: Record<ExecutionStatus, {
  borderClass: string;
  ringClass: string;
  icon: typeof CheckCircle | null;
  iconClass: string;
  animate?: boolean;
  glowClass?: string;
  pulseClass?: string;
}> = {
  idle: { borderClass: '', ringClass: '', icon: null, iconClass: '' },
  pending: {
    borderClass: 'border-slate-400 dark:border-slate-500',
    ringClass: 'ring-2 ring-slate-200 dark:ring-slate-700',
    icon: Clock,
    iconClass: 'text-slate-400 dark:text-slate-500',
  },
  running: {
    borderClass: 'border-blue-500 dark:border-blue-400',
    ringClass: 'ring-4 ring-blue-200 dark:ring-blue-900',
    icon: Loader2,
    iconClass: 'text-blue-500 dark:text-blue-400',
    animate: true,
    glowClass: 'shadow-blue-300/50 dark:shadow-blue-500/30 shadow-xl',
    pulseClass: 'animate-pulse',
  },
  completed: {
    borderClass: 'border-green-500 dark:border-green-400',
    ringClass: 'ring-2 ring-green-200 dark:ring-green-900',
    icon: CheckCircle,
    iconClass: 'text-green-500 dark:text-green-400',
  },
  success: {
    borderClass: 'border-green-500 dark:border-green-400',
    ringClass: 'ring-2 ring-green-200 dark:ring-green-900',
    icon: CheckCircle,
    iconClass: 'text-green-500 dark:text-green-400',
  },
  failed: {
    borderClass: 'border-red-500 dark:border-red-400',
    ringClass: 'ring-2 ring-red-200 dark:ring-red-900',
    icon: XCircle,
    iconClass: 'text-red-500 dark:text-red-400',
  },
};

/**
 * Debug-enhanced Stage Node
 */
export const DebugStageNode = memo(function DebugStageNode({
  data,
  selected,
}: { data: DebugNodeData; selected?: boolean }) {
  const Icon = data.kind === 'node' ? Box : Zap;
  const execStatus = data.executionStatus || 'idle';
  const statusConfig = executionStatusConfig[execStatus];
  const StatusIcon = statusConfig.icon;

  const isExecuting = execStatus !== 'idle';
  const isDebugMode = data.isDebugMode;
  const hasBreakpoint = data.hasBreakpoint;
  const isPaused = data.isPaused;

  // Determine border styling
  const borderClass = useMemo(() => {
    if (isPaused) return 'border-amber-500 dark:border-amber-400';
    if (isExecuting) return statusConfig.borderClass;
    if (selected) return 'border-primary-500';
    return 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600';
  }, [isPaused, isExecuting, statusConfig.borderClass, selected]);

  const ringClass = useMemo(() => {
    if (isPaused) return 'ring-4 ring-amber-200 dark:ring-amber-800';
    if (isExecuting) return statusConfig.ringClass;
    if (selected) return 'ring-4 ring-primary-200 dark:ring-primary-800';
    return '';
  }, [isPaused, isExecuting, statusConfig.ringClass, selected]);

  return (
    <div
      className={cn(
        'relative min-w-[220px] p-4 rounded-xl border-2 shadow-lg transition-all',
        'bg-white dark:bg-slate-800',
        borderClass,
        ringClass,
        statusConfig.glowClass,
        !isExecuting && !selected && !isPaused && 'hover:shadow-xl',
        statusConfig.pulseClass
      )}
    >
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Top}
        className={cn(
          '!w-4 !h-4 !border-2 !border-white dark:!border-slate-800 !-top-2 transition-colors',
          isDebugMode
            ? '!bg-purple-400 hover:!bg-purple-500'
            : '!bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500'
        )}
      />

      <div className="flex items-start gap-3">
        {/* Component icon */}
        <div
          className={cn(
            'w-10 h-10 rounded-xl flex items-center justify-center text-white flex-shrink-0 shadow-md relative',
            execStatus === 'running' && 'animate-pulse'
          )}
          style={{ backgroundColor: data.color }}
        >
          <Icon className="w-5 h-5" />
          {/* Running indicator overlay */}
          {execStatus === 'running' && (
            <div className="absolute inset-0 rounded-xl bg-white/30 animate-ping" />
          )}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-900 dark:text-slate-100 truncate">
              {data.label}
            </span>
            {data.requiresLLM && (
              <Sparkles className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
            )}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 font-mono truncate mt-0.5">
            {data.componentType}
          </div>

          {/* Description */}
          {data.showNotes && data.description && (
            <div className="text-xs text-slate-400 dark:text-slate-500 line-clamp-2 mt-1">
              {data.description}
            </div>
          )}

          {/* Performance metrics in debug mode */}
          {isDebugMode && (data.duration || data.tokens) && (
            <div className="flex items-center gap-2 mt-2 text-xs text-slate-500">
              {data.duration && (
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {data.duration}ms
                </span>
              )}
              {data.tokens && (
                <span className="flex items-center gap-1">
                  <Lightning className="w-3 h-3" />
                  {data.tokens}
                </span>
              )}
              {data.cost && (
                <span className="font-medium text-green-600">
                  ${data.cost.toFixed(4)}
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Execution status indicator */}
      {StatusIcon && (
        <div className="absolute -top-2 -left-2 bg-white dark:bg-slate-800 rounded-full p-0.5 shadow-md">
          <StatusIcon
            className={cn(
              'w-5 h-5',
              statusConfig.iconClass,
              statusConfig.animate && 'animate-spin'
            )}
          />
        </div>
      )}

      {/* Breakpoint indicator */}
      {hasBreakpoint && (
        <div
          className={cn(
            'absolute -top-2 -right-2 rounded-full p-0.5 shadow-md',
            data.isBreakpointActive
              ? 'bg-red-500'
              : 'bg-white dark:bg-slate-800 border-2 border-red-500'
          )}
        >
          <CircleDot
            className={cn(
              'w-4 h-4',
              data.isBreakpointActive ? 'text-white' : 'text-red-500'
            )}
          />
        </div>
      )}

      {/* Paused indicator */}
      {isPaused && (
        <div className="absolute -top-2 right-6 bg-amber-500 rounded-full p-0.5 shadow-md">
          <Pause className="w-4 h-4 text-white" />
        </div>
      )}

      {/* Kind badge */}
      {!hasBreakpoint && (
        <div className="absolute -top-2 -right-2">
          <Badge
            variant={data.kind === 'node' ? 'default' : 'warning'}
            className="text-xs px-1.5 py-0 shadow-sm"
          >
            {data.kind}
          </Badge>
        </div>
      )}

      {/* Inspect button */}
      {data.hasExecutionData && data.onInspect && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            data.onInspect?.();
          }}
          className={cn(
            'absolute -bottom-3 left-1/2 -translate-x-1/2 rounded-full p-1.5 shadow-lg transition-all hover:scale-110 z-10',
            execStatus === 'failed'
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'bg-primary-500 hover:bg-primary-600 text-white'
          )}
          title={execStatus === 'failed' ? 'View Error' : 'View Input/Output'}
        >
          {execStatus === 'failed' ? (
            <AlertTriangle className="w-3.5 h-3.5" />
          ) : (
            <Eye className="w-3.5 h-3.5" />
          )}
        </button>
      )}

      {/* Data preview tooltip (shown on hover in debug mode) */}
      {isDebugMode && (data.inputPreview || data.outputPreview) && (
        <div className="absolute left-full ml-2 top-0 hidden group-hover:block z-50">
          <div className="bg-slate-900 text-white text-xs rounded-lg p-2 shadow-xl max-w-xs">
            {data.inputPreview && (
              <div className="mb-2">
                <div className="text-slate-400 mb-1">Input:</div>
                <div className="font-mono truncate">{data.inputPreview}</div>
              </div>
            )}
            {data.outputPreview && (
              <div>
                <div className="text-slate-400 mb-1">Output:</div>
                <div className="font-mono truncate">{data.outputPreview}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        className={cn(
          '!w-4 !h-4 !border-2 !border-white dark:!border-slate-800 !-bottom-2 transition-colors',
          isDebugMode
            ? '!bg-purple-400 hover:!bg-purple-500'
            : '!bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500'
        )}
      />
    </div>
  );
});

/**
 * Debug-enhanced Data Flow Edge
 */
export interface DebugEdgeData {
  sourceStage?: string;
  targetStage?: string;
  isDataFlowing?: boolean;
  isCompleted?: boolean;
  isDebugMode?: boolean;
  dataSize?: number;
  transferTime?: number;
  [key: string]: unknown;
}

interface DebugDataFlowEdgeProps {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  sourcePosition: Position;
  targetPosition: Position;
  data?: DebugEdgeData;
  selected?: boolean;
}

export const DebugDataFlowEdge = memo(function DebugDataFlowEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}: DebugDataFlowEdgeProps) {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const isDataFlowing = data?.isDataFlowing;
  const isCompleted = data?.isCompleted;
  const isDebugMode = data?.isDebugMode;

  // Determine edge color based on state
  const strokeColor = useMemo(() => {
    if (isCompleted) return '#22c55e'; // green
    if (isDataFlowing) return '#3b82f6'; // blue
    if (isDebugMode) return '#a855f7'; // purple
    return '#0ea5e9'; // cyan
  }, [isCompleted, isDataFlowing, isDebugMode]);

  const strokeWidth = useMemo(() => {
    if (isDataFlowing) return 3;
    if (selected) return 3;
    return 2;
  }, [isDataFlowing, selected]);

  return (
    <>
      {/* Shadow/glow effect for active edges */}
      {isDataFlowing && (
        <BaseEdge
          id={`${id}-glow`}
          path={edgePath}
          style={{
            stroke: strokeColor,
            strokeWidth: 8,
            strokeOpacity: 0.2,
            filter: 'blur(4px)',
          }}
        />
      )}

      {/* Main edge */}
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          stroke: strokeColor,
          strokeWidth,
          transition: 'stroke 0.3s, stroke-width 0.3s',
        }}
        markerEnd={`url(#arrow-${isCompleted ? 'completed' : isDataFlowing ? 'flowing' : 'default'})`}
      />

      {/* Animated data particles for active flow */}
      {isDataFlowing && (
        <>
          <circle r="4" fill={strokeColor}>
            <animateMotion dur="0.8s" repeatCount="indefinite" path={edgePath} />
          </circle>
          <circle r="3" fill={strokeColor} opacity="0.6">
            <animateMotion dur="0.8s" repeatCount="indefinite" path={edgePath} begin="0.3s" />
          </circle>
          <circle r="2" fill={strokeColor} opacity="0.3">
            <animateMotion dur="0.8s" repeatCount="indefinite" path={edgePath} begin="0.6s" />
          </circle>
        </>
      )}

      {/* Completion checkmark */}
      {isCompleted && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'all',
            }}
            className="flex items-center justify-center w-5 h-5 bg-green-500 rounded-full shadow-md"
          >
            <CheckCircle className="w-3 h-3 text-white" />
          </div>
        </EdgeLabelRenderer>
      )}

      {/* Data size indicator in debug mode */}
      {isDebugMode && data?.dataSize && isCompleted && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY + 16}px)`,
              pointerEvents: 'none',
            }}
            className="text-xs text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-800 px-1.5 py-0.5 rounded shadow-sm"
          >
            {data.dataSize > 1000 ? `${(data.dataSize / 1000).toFixed(1)}KB` : `${data.dataSize}B`}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
});

/**
 * SVG Marker definitions for edge arrows
 */
export function EdgeMarkerDefinitions() {
  return (
    <svg style={{ position: 'absolute', top: 0, left: 0, width: 0, height: 0 }}>
      <defs>
        <marker
          id="arrow-default"
          markerWidth="12"
          markerHeight="12"
          refX="10"
          refY="6"
          orient="auto"
        >
          <path d="M2,2 L10,6 L2,10" fill="none" stroke="#0ea5e9" strokeWidth="1.5" />
        </marker>
        <marker
          id="arrow-flowing"
          markerWidth="12"
          markerHeight="12"
          refX="10"
          refY="6"
          orient="auto"
        >
          <path d="M2,2 L10,6 L2,10" fill="none" stroke="#3b82f6" strokeWidth="1.5" />
        </marker>
        <marker
          id="arrow-completed"
          markerWidth="12"
          markerHeight="12"
          refX="10"
          refY="6"
          orient="auto"
        >
          <path d="M2,2 L10,6 L2,10" fill="none" stroke="#22c55e" strokeWidth="1.5" />
        </marker>
      </defs>
    </svg>
  );
}

export default DebugStageNode;
