/**
 * Enhanced Stage Node
 *
 * Visual node component with:
 * - Category-colored header bars
 * - Input/output port indicators
 * - Schema-aware field ports
 * - Different shapes for different component kinds
 * - Rich visual feedback for execution status
 */

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import {
  Box, Zap, GitBranch, Sparkles, CheckCircle, XCircle, Loader2, Clock, Eye, CircleDot,
  ArrowRightCircle, ArrowLeftCircle, type LucideIcon,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

// Category colors matching the design spec
const CATEGORY_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  core: { bg: 'bg-indigo-500', border: 'border-indigo-500', text: 'text-indigo-500' },
  control_flow: { bg: 'bg-pink-500', border: 'border-pink-500', text: 'text-pink-500' },
  ai: { bg: 'bg-amber-500', border: 'border-amber-500', text: 'text-amber-500' },
  integration: { bg: 'bg-blue-500', border: 'border-blue-500', text: 'text-blue-500' },
  data: { bg: 'bg-teal-500', border: 'border-teal-500', text: 'text-teal-500' },
  workspace: { bg: 'bg-stone-500', border: 'border-stone-500', text: 'text-stone-500' },
  default: { bg: 'bg-gray-500', border: 'border-gray-500', text: 'text-gray-500' },
};

// Execution status styling
const STATUS_STYLES: Record<string, { ring: string; icon: LucideIcon | null; iconClass: string; animate?: boolean }> = {
  idle: { ring: '', icon: null, iconClass: '' },
  pending: { ring: 'ring-2 ring-slate-200 dark:ring-slate-700', icon: Clock, iconClass: 'text-slate-400' },
  running: { ring: 'ring-4 ring-blue-300 dark:ring-blue-800', icon: Loader2, iconClass: 'text-blue-500', animate: true },
  completed: { ring: 'ring-2 ring-green-300 dark:ring-green-800', icon: CheckCircle, iconClass: 'text-green-500' },
  success: { ring: 'ring-2 ring-green-300 dark:ring-green-800', icon: CheckCircle, iconClass: 'text-green-500' },
  failed: { ring: 'ring-2 ring-red-300 dark:ring-red-800', icon: XCircle, iconClass: 'text-red-500' },
};

// Shape configurations based on component kind
const SHAPE_STYLES: Record<string, string> = {
  node: 'rounded-xl',
  operator: 'rounded-lg',
  control_flow: 'rounded-2xl',
};

interface PortInfo {
  name: string;
  type: string;
  required?: boolean;
}

interface EnhancedStageNodeData {
  label: string;
  componentType: string;
  kind: 'node' | 'operator' | 'control_flow';
  category: string;
  color: string;
  icon?: string;
  config: Record<string, unknown>;
  requiresLLM?: boolean;
  description?: string;
  showNotes?: boolean;
  // Schema ports
  inputPorts?: PortInfo[];
  outputPorts?: PortInfo[];
  // Execution state
  executionStatus?: string;
  hasExecutionData?: boolean;
  onInspect?: () => void;
  // Debug mode
  hasBreakpoint?: boolean;
}

interface Props {
  data: EnhancedStageNodeData;
  selected?: boolean;
}

// Port indicator component
function PortIndicator({
  port,
  side,
}: {
  port: PortInfo;
  side: 'input' | 'output';
}) {
  const Icon = side === 'input' ? ArrowRightCircle : ArrowLeftCircle;
  const colorClass = port.required ? 'text-orange-500' : 'text-slate-400';

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex items-center gap-1 px-1.5 py-0.5 text-xs">
            <Icon className={`h-3 w-3 ${colorClass}`} />
            <span className="font-mono truncate max-w-16">{port.name}</span>
          </div>
        </TooltipTrigger>
        <TooltipContent side={side === 'input' ? 'left' : 'right'}>
          <div>
            <p className="font-medium">{port.name}</p>
            <p className="text-xs text-muted-foreground">Type: {port.type}</p>
            {port.required && <p className="text-xs text-orange-500">Required</p>}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export const EnhancedStageNode = memo(function EnhancedStageNode({ data, selected }: Props) {
  const category = data.category || 'default';
  const categoryStyle = CATEGORY_COLORS[category] || CATEGORY_COLORS.default;
  const shapeStyle = SHAPE_STYLES[data.kind] || SHAPE_STYLES.operator;
  const status = data.executionStatus || 'idle';
  const statusStyle = STATUS_STYLES[status] || STATUS_STYLES.idle;
  const StatusIcon = statusStyle.icon;

  // Determine icon based on kind
  const IconComponent = data.kind === 'node' ? Box : data.kind === 'control_flow' ? GitBranch : Zap;

  return (
    <div
      className={`
        relative min-w-[220px] shadow-lg transition-all
        bg-white dark:bg-slate-800
        border-2 overflow-hidden
        ${shapeStyle}
        ${selected ? 'border-primary-500 ring-4 ring-primary-200 dark:ring-primary-800' : 'border-slate-200 dark:border-slate-700'}
        ${statusStyle.ring}
        ${status === 'running' ? 'animate-pulse' : ''}
      `}
    >
      {/* Category color bar at top */}
      <div className={`h-1.5 w-full ${categoryStyle.bg}`} />

      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-top-2 transition-colors z-10"
      />

      {/* Main content */}
      <div className="p-3">
        {/* Header row */}
        <div className="flex items-start gap-3">
          {/* Icon with category color */}
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center text-white flex-shrink-0 shadow-md ${categoryStyle.bg}`}
          >
            <IconComponent className="w-5 h-5" />
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
          </div>
        </div>

        {/* Description */}
        {data.showNotes && data.description && (
          <div className="text-xs text-slate-400 dark:text-slate-500 line-clamp-2 mt-2 border-t border-slate-100 dark:border-slate-700 pt-2">
            {data.description}
          </div>
        )}

        {/* Port indicators */}
        {(data.inputPorts?.length || data.outputPorts?.length) && (
          <div className="mt-2 border-t border-slate-100 dark:border-slate-700 pt-2 grid grid-cols-2 gap-1">
            {/* Input ports */}
            <div className="space-y-0.5">
              {data.inputPorts?.slice(0, 3).map((port) => (
                <PortIndicator key={port.name} port={port} side="input" />
              ))}
              {(data.inputPorts?.length || 0) > 3 && (
                <div className="text-xs text-slate-400 px-1.5">
                  +{(data.inputPorts?.length || 0) - 3} more
                </div>
              )}
            </div>

            {/* Output ports */}
            <div className="space-y-0.5">
              {data.outputPorts?.slice(0, 3).map((port) => (
                <PortIndicator key={port.name} port={port} side="output" />
              ))}
              {(data.outputPorts?.length || 0) > 3 && (
                <div className="text-xs text-slate-400 px-1.5">
                  +{(data.outputPorts?.length || 0) - 3} more
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Status indicator */}
      {StatusIcon && (
        <div className="absolute -top-2 -left-2 bg-white dark:bg-slate-800 rounded-full p-0.5 shadow-md z-10">
          <StatusIcon className={`w-5 h-5 ${statusStyle.iconClass} ${statusStyle.animate ? 'animate-spin' : ''}`} />
        </div>
      )}

      {/* Breakpoint indicator */}
      {data.hasBreakpoint && (
        <div className="absolute -top-2 -right-2 bg-red-500 rounded-full p-0.5 shadow-md z-10">
          <CircleDot className="w-4 h-4 text-white" />
        </div>
      )}

      {/* Kind/Category badge */}
      {!data.hasBreakpoint && (
        <div className="absolute -top-2 -right-2 z-10">
          <Badge
            className={`text-[10px] px-1.5 py-0 shadow-sm ${categoryStyle.bg} text-white border-0`}
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
          className="absolute -bottom-3 left-1/2 -translate-x-1/2 bg-primary-500 hover:bg-primary-600 text-white rounded-full p-1.5 shadow-lg transition-all hover:scale-110 z-10"
          title="View Input/Output"
        >
          <Eye className="w-3.5 h-3.5" />
        </button>
      )}

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-bottom-2 transition-colors z-10"
      />
    </div>
  );
});

export default EnhancedStageNode;
