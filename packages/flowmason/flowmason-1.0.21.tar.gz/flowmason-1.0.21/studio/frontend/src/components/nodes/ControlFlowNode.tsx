/**
 * Control Flow Node Components
 *
 * Visual representations for control flow components:
 * - Diamond shape: Conditional, Router (branching decisions)
 * - Container shape: ForEach, TryCatch (nested execution)
 * - Box shape: SubPipeline (function call)
 * - Arrow shape: Return (early exit)
 */

import { Handle, Position } from '@xyflow/react';
import {
  GitBranch,
  GitMerge,
  Repeat,
  Shield,
  Box,
  CornerDownLeft,
  CheckCircle,
  XCircle,
  Loader2,
  Clock,
  CircleDot,
} from 'lucide-react';
import { Badge } from '@/components/ui';
import type { ControlFlowType } from '../../types';
import type { ExecutionStatus } from '../PipelineCanvas';

// Execution status styling (shared with StageNode)
const executionStatusConfig: Record<ExecutionStatus, {
  borderClass: string;
  ringClass: string;
  icon: typeof CheckCircle | null;
  iconClass: string;
  animate?: boolean;
  glowClass?: string;
}> = {
  idle: { borderClass: '', ringClass: '', icon: null, iconClass: '' },
  pending: {
    borderClass: 'border-slate-400 dark:border-slate-500',
    ringClass: 'ring-2 ring-slate-200 dark:ring-slate-700',
    icon: Clock,
    iconClass: 'text-slate-400 dark:text-slate-500'
  },
  running: {
    borderClass: 'border-blue-500 dark:border-blue-400',
    ringClass: 'ring-4 ring-blue-200 dark:ring-blue-900',
    icon: Loader2,
    iconClass: 'text-blue-500 dark:text-blue-400',
    animate: true,
    glowClass: 'shadow-blue-300/50 dark:shadow-blue-500/30 shadow-xl'
  },
  completed: {
    borderClass: 'border-green-500 dark:border-green-400',
    ringClass: 'ring-2 ring-green-200 dark:ring-green-900',
    icon: CheckCircle,
    iconClass: 'text-green-500 dark:text-green-400'
  },
  success: {
    borderClass: 'border-green-500 dark:border-green-400',
    ringClass: 'ring-2 ring-green-200 dark:ring-green-900',
    icon: CheckCircle,
    iconClass: 'text-green-500 dark:text-green-400'
  },
  failed: {
    borderClass: 'border-red-500 dark:border-red-400',
    ringClass: 'ring-2 ring-red-200 dark:ring-red-900',
    icon: XCircle,
    iconClass: 'text-red-500 dark:text-red-400'
  },
};

// Icon mapping for control flow types
const controlFlowIcons: Record<ControlFlowType, typeof GitBranch> = {
  conditional: GitBranch,
  router: GitMerge,
  foreach: Repeat,
  trycatch: Shield,
  subpipeline: Box,
  return: CornerDownLeft,
};

export interface ControlFlowNodeData extends Record<string, unknown> {
  label: string;
  componentType: string;
  controlFlowType: ControlFlowType;
  color: string;
  config: Record<string, unknown>;
  description?: string;
  showNotes?: boolean;
  // Path highlighting
  isOnPath?: boolean;
  // Heatmap (latency/usage) bucket
  heatLevel?: 'low' | 'medium' | 'high';
  // Execution state
  executionStatus?: ExecutionStatus;
  hasExecutionData?: boolean;
  onInspect?: () => void;
  // Debug mode
  isDebugMode?: boolean;
  hasBreakpoint?: boolean;
  // Control flow specific
  branchTaken?: string;  // For conditional/router
  iterationCount?: number;  // For foreach
  errorOccurred?: boolean;  // For trycatch
}

interface ControlFlowNodeProps {
  data: ControlFlowNodeData;
  selected?: boolean;
}

function getHeatClass(heatLevel?: 'low' | 'medium' | 'high'): string {
  if (!heatLevel) return '';
  if (heatLevel === 'high') {
    return 'shadow-red-200/50 dark:shadow-red-500/30';
  }
  if (heatLevel === 'medium') {
    return 'shadow-amber-200/40 dark:shadow-amber-500/25';
  }
  return 'shadow-emerald-200/40 dark:shadow-emerald-500/25';
}

/**
 * Diamond Node - for Conditional and Router (branching decisions)
 */
export function DiamondNode({ data, selected }: ControlFlowNodeProps) {
  const Icon = controlFlowIcons[data.controlFlowType] || GitBranch;
  const execStatus = data.executionStatus || 'idle';
  const statusConfig = executionStatusConfig[execStatus];
  const StatusIcon = statusConfig.icon;
  const isExecuting = execStatus !== 'idle';
  const isOnPath = data.isOnPath !== false;
  const heatClass = !isExecuting && !selected ? getHeatClass(data.heatLevel) : '';

  const borderClass = isExecuting
    ? statusConfig.borderClass
    : (selected
        ? 'border-primary-500'
        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600');

  return (
    <div className="relative">
      {/* Input handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-top-2 transition-colors z-10"
        style={{ left: '50%', transform: 'translateX(-50%)' }}
      />

      {/* Diamond shape container */}
      <div
        className={`
          relative w-[180px] h-[100px]
          ${statusConfig.glowClass || ''}
          ${execStatus === 'running' ? 'animate-pulse' : ''}
          ${heatClass}
          ${!isOnPath ? 'opacity-40' : ''}
        `}
      >
        {/* Diamond shape using CSS transform */}
        <div
          className={`
            absolute inset-0 rounded-lg border-2 shadow-lg transition-all
            bg-white dark:bg-slate-800
            ${borderClass}
            ${statusConfig.ringClass}
          `}
          style={{
            transform: 'rotate(45deg) scale(0.707)',
            transformOrigin: 'center',
          }}
        />

        {/* Content (not rotated) */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-2">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white shadow-md mb-1"
            style={{ backgroundColor: data.color }}
          >
            <Icon className="w-4 h-4" />
          </div>
          <span className="font-semibold text-slate-900 dark:text-slate-100 text-sm truncate max-w-[140px]">
            {data.label}
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-mono truncate max-w-[140px]">
            {data.componentType}
          </span>
          {data.branchTaken && (
            <Badge variant="secondary" className="text-xs mt-1">
              {data.branchTaken}
            </Badge>
          )}
        </div>

        {/* Execution status indicator */}
        {StatusIcon && (
          <div className="absolute -top-1 -left-1 bg-white dark:bg-slate-800 rounded-full p-0.5 shadow-md z-10">
            <StatusIcon className={`w-4 h-4 ${statusConfig.iconClass} ${statusConfig.animate ? 'animate-spin' : ''}`} />
          </div>
        )}

        {/* Breakpoint indicator */}
        {data.hasBreakpoint && (
          <div className="absolute -top-1 -right-1 bg-red-500 rounded-full p-0.5 shadow-md z-10">
            <CircleDot className="w-3 h-3 text-white" />
          </div>
        )}
      </div>

      {/* Output handles (left and right for branches) */}
      <Handle
        type="source"
        position={Position.Left}
        id="false"
        className="!w-4 !h-4 !bg-red-400 dark:!bg-red-500 hover:!bg-red-500 !border-2 !border-white dark:!border-slate-800 transition-colors"
        style={{ top: '50%', transform: 'translateY(-50%)' }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="true"
        className="!w-4 !h-4 !bg-green-400 dark:!bg-green-500 hover:!bg-green-500 !border-2 !border-white dark:!border-slate-800 transition-colors"
        style={{ top: '50%', transform: 'translateY(-50%)' }}
      />
      {/* Default bottom output */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="default"
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-bottom-2 transition-colors"
        style={{ left: '50%', transform: 'translateX(-50%)' }}
      />
    </div>
  );
}

/**
 * Container Node - for ForEach and TryCatch (nested execution)
 */
export function ContainerNode({ data, selected }: ControlFlowNodeProps) {
  const Icon = controlFlowIcons[data.controlFlowType] || Repeat;
  const execStatus = data.executionStatus || 'idle';
  const statusConfig = executionStatusConfig[execStatus];
  const StatusIcon = statusConfig.icon;
  const isExecuting = execStatus !== 'idle';
  const isTryCatch = data.controlFlowType === 'trycatch';
   const isOnPath = data.isOnPath !== false;
   const heatClass = !isExecuting && !selected ? getHeatClass(data.heatLevel) : '';

  const borderClass = isExecuting
    ? statusConfig.borderClass
    : (selected
        ? 'border-primary-500'
        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600');

  return (
    <div className="relative">
      {/* Input handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-top-2 transition-colors"
      />

      {/* Container with dashed inner border */}
      <div
        className={`
          relative min-w-[220px] rounded-xl border-2 shadow-lg transition-all
          bg-white dark:bg-slate-800
          ${borderClass}
          ${statusConfig.ringClass}
          ${statusConfig.glowClass || ''}
          ${execStatus === 'running' ? 'animate-pulse' : ''}
          ${heatClass}
          ${!isOnPath ? 'opacity-40' : ''}
        `}
      >
        {/* Header */}
        <div className="flex items-center gap-2 p-3 border-b border-slate-200 dark:border-slate-700">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white shadow-md"
            style={{ backgroundColor: data.color }}
          >
            <Icon className="w-4 h-4" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="font-semibold text-slate-900 dark:text-slate-100 text-sm truncate block">
              {data.label}
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-mono truncate block">
              {data.componentType}
            </span>
          </div>
          {data.iterationCount !== undefined && (
            <Badge variant="secondary" className="text-xs">
              {data.iterationCount} items
            </Badge>
          )}
          {data.errorOccurred && (
            <Badge variant="destructive" className="text-xs">
              Error
            </Badge>
          )}
        </div>

        {/* Inner container (represents nested stages) */}
        <div className="p-3">
          <div className="min-h-[60px] rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-900/50 flex items-center justify-center">
            <span className="text-xs text-slate-400 dark:text-slate-500">
              {isTryCatch ? 'try / catch / finally' : 'loop body'}
            </span>
          </div>
        </div>

        {/* Execution status indicator */}
        {StatusIcon && (
          <div className="absolute -top-2 -left-2 bg-white dark:bg-slate-800 rounded-full p-0.5 shadow-md z-10">
            <StatusIcon className={`w-5 h-5 ${statusConfig.iconClass} ${statusConfig.animate ? 'animate-spin' : ''}`} />
          </div>
        )}

        {/* Breakpoint indicator */}
        {data.hasBreakpoint && (
          <div className="absolute -top-2 -right-2 bg-red-500 rounded-full p-0.5 shadow-md z-10">
            <CircleDot className="w-4 h-4 text-white" />
          </div>
        )}

        {/* Kind badge */}
        {!data.hasBreakpoint && (
          <div className="absolute -top-2 -right-2">
            <Badge
              variant="default"
              className="text-xs px-1.5 py-0 shadow-sm bg-purple-500"
            >
              control
            </Badge>
          </div>
        )}
      </div>

      {/* Output handle (bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-bottom-2 transition-colors"
      />

      {/* Error output for TryCatch */}
      {isTryCatch && (
        <Handle
          type="source"
          position={Position.Right}
          id="error"
          className="!w-4 !h-4 !bg-red-400 dark:!bg-red-500 hover:!bg-red-500 !border-2 !border-white dark:!border-slate-800 transition-colors"
          style={{ top: '50%', transform: 'translateY(-50%)' }}
        />
      )}
    </div>
  );
}

/**
 * SubPipeline Node - for calling other pipelines (function call style)
 */
export function SubPipelineNode({ data, selected }: ControlFlowNodeProps) {
  const Icon = controlFlowIcons.subpipeline;
  const execStatus = data.executionStatus || 'idle';
  const statusConfig = executionStatusConfig[execStatus];
  const StatusIcon = statusConfig.icon;
  const isExecuting = execStatus !== 'idle';
  const isOnPath = data.isOnPath !== false;
  const heatClass = !isExecuting && !selected ? getHeatClass(data.heatLevel) : '';

  const borderClass = isExecuting
    ? statusConfig.borderClass
    : (selected
        ? 'border-primary-500'
        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600');

  return (
    <div className="relative">
      {/* Input handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-top-2 transition-colors"
      />

      {/* Double-bordered box to indicate nested pipeline */}
      <div
        className={`
          relative min-w-[200px] p-1 rounded-xl border-2 shadow-lg transition-all
          bg-slate-100 dark:bg-slate-900
          ${borderClass}
          ${statusConfig.ringClass}
          ${statusConfig.glowClass || ''}
          ${execStatus === 'running' ? 'animate-pulse' : ''}
          ${heatClass}
          ${!isOnPath ? 'opacity-40' : ''}
        `}
      >
        {/* Inner box */}
        <div className="p-3 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
          <div className="flex items-start gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-md"
              style={{ backgroundColor: data.color }}
            >
              <Icon className="w-5 h-5" />
            </div>
            <div className="min-w-0 flex-1">
              <span className="font-semibold text-slate-900 dark:text-slate-100 truncate block">
                {data.label}
              </span>
              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono truncate block">
                {data.componentType}
              </span>
              {data.showNotes && data.description && (
                <span className="text-xs text-slate-400 dark:text-slate-500 line-clamp-2 mt-1 block">
                  {data.description}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Execution status indicator */}
        {StatusIcon && (
          <div className="absolute -top-2 -left-2 bg-white dark:bg-slate-800 rounded-full p-0.5 shadow-md z-10">
            <StatusIcon className={`w-5 h-5 ${statusConfig.iconClass} ${statusConfig.animate ? 'animate-spin' : ''}`} />
          </div>
        )}

        {/* Kind badge */}
        {!data.hasBreakpoint && (
          <div className="absolute -top-2 -right-2">
            <Badge
              variant="default"
              className="text-xs px-1.5 py-0 shadow-sm bg-violet-500"
            >
              pipeline
            </Badge>
          </div>
        )}

        {/* Breakpoint indicator */}
        {data.hasBreakpoint && (
          <div className="absolute -top-2 -right-2 bg-red-500 rounded-full p-0.5 shadow-md z-10">
            <CircleDot className="w-4 h-4 text-white" />
          </div>
        )}
      </div>

      {/* Output handle (bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-bottom-2 transition-colors"
      />
    </div>
  );
}

/**
 * Return Node - for early pipeline exit (arrow/stop style)
 */
export function ReturnNode({ data, selected }: ControlFlowNodeProps) {
  const Icon = controlFlowIcons.return;
  const execStatus = data.executionStatus || 'idle';
  const statusConfig = executionStatusConfig[execStatus];
  const StatusIcon = statusConfig.icon;
  const isExecuting = execStatus !== 'idle';
  const isOnPath = data.isOnPath !== false;
  const heatClass = !isExecuting && !selected ? getHeatClass(data.heatLevel) : '';

  const borderClass = isExecuting
    ? statusConfig.borderClass
    : (selected
        ? 'border-primary-500'
        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600');

  return (
    <div className="relative">
      {/* Input handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-top-2 transition-colors"
      />

      {/* Hexagonal-ish shape using clip-path */}
      <div
        className={`
          relative min-w-[160px] p-4 rounded-xl border-2 shadow-lg transition-all
          bg-white dark:bg-slate-800
          ${borderClass}
          ${statusConfig.ringClass}
          ${statusConfig.glowClass || ''}
          ${execStatus === 'running' ? 'animate-pulse' : ''}
          ${heatClass}
          ${!isOnPath ? 'opacity-40' : ''}
        `}
        style={{
          clipPath: 'polygon(10% 0%, 90% 0%, 100% 50%, 90% 100%, 10% 100%, 0% 50%)',
        }}
      >
        <div className="flex items-center gap-3 justify-center">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white shadow-md"
            style={{ backgroundColor: data.color }}
          >
            <Icon className="w-4 h-4" />
          </div>
          <div className="text-center">
            <span className="font-semibold text-slate-900 dark:text-slate-100 text-sm block">
              {data.label}
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              Early Exit
            </span>
          </div>
        </div>

        {/* Execution status indicator */}
        {StatusIcon && (
          <div className="absolute -top-2 left-4 bg-white dark:bg-slate-800 rounded-full p-0.5 shadow-md z-10">
            <StatusIcon className={`w-4 h-4 ${statusConfig.iconClass} ${statusConfig.animate ? 'animate-spin' : ''}`} />
          </div>
        )}
      </div>

      {/* No output handle - return terminates flow */}
    </div>
  );
}

/**
 * Main ControlFlowNode component that delegates to specific shapes
 */
export function ControlFlowNode({ data, selected }: ControlFlowNodeProps) {
  switch (data.controlFlowType) {
    case 'conditional':
    case 'router':
      return <DiamondNode data={data} selected={selected} />;
    case 'foreach':
    case 'trycatch':
      return <ContainerNode data={data} selected={selected} />;
    case 'subpipeline':
      return <SubPipelineNode data={data} selected={selected} />;
    case 'return':
      return <ReturnNode data={data} selected={selected} />;
    default:
      // Fallback to container for unknown types
      return <ContainerNode data={data} selected={selected} />;
  }
}

export default ControlFlowNode;
