/**
 * Pipeline Canvas
 *
 * Visual DAG editor for pipeline composition using ReactFlow.
 * Supports drag-and-drop from component palette.
 *
 * Key features:
 * - Drag components from palette to canvas
 * - Connect stages with edges (dependencies)
 * - Select nodes/edges for configuration
 * - Visual feedback for valid/invalid connections
 * - Dark mode support
 */

import { useCallback, useRef, useState, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  Connection,
  NodeTypes,
  EdgeTypes,
  useReactFlow,
  ReactFlowProvider,
  Handle,
  Position,
  BackgroundVariant,
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Box, Zap, GitBranch, Sparkles, Trash2, AlignVerticalSpaceAround, CheckCircle, XCircle, Loader2, Clock, Eye, CircleDot,
  // Additional icons used by components
  Globe, Code, Filter, Repeat, ShieldCheck, FileText, Variable, Share2, AlertTriangle, GitMerge, CornerDownLeft, Shield, ClipboardCheck, ArrowUpCircle,
  type LucideIcon,
} from 'lucide-react';

/**
 * Map of Lucide icon names to their components.
 */
const ICON_MAP: Record<string, LucideIcon> = {
  'box': Box, 'zap': Zap, 'git-branch': GitBranch, 'sparkles': Sparkles,
  'code': Code, 'filter': Filter, 'variable': Variable, 'globe': Globe, 'share-2': Share2,
  'git-merge': GitMerge, 'repeat': Repeat, 'corner-down-left': CornerDownLeft, 'shield': Shield,
  'shield-check': ShieldCheck, 'clipboard-check': ClipboardCheck, 'check-circle': CheckCircle,
  'file-text': FileText, 'arrow-up-circle': ArrowUpCircle, 'alert-triangle': AlertTriangle,
};

function getIconComponent(iconName?: string, componentKind?: string): LucideIcon {
  if (iconName && ICON_MAP[iconName]) return ICON_MAP[iconName];
  return componentKind === 'node' ? Box : componentKind === 'control_flow' ? GitBranch : Zap;
}
import type { ComponentInfo, PipelineStage, ControlFlowType } from '../types';
import { Badge, Button } from '@/components/ui';
import { ControlFlowNode, type ControlFlowNodeData } from './nodes';

// Execution status type for stages
export type ExecutionStatus = 'idle' | 'pending' | 'running' | 'completed' | 'success' | 'failed';

// Execution status styling configurations
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

// Custom edge data interface - using index signature for ReactFlow compatibility
interface DataFlowEdgeData {
  sourceStage?: string;
  targetStage?: string;
  isDataFlowing?: boolean;
  isCompleted?: boolean;
  [key: string]: unknown;
}

// Custom edge component showing data flow status
function DataFlowEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
}: {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  sourcePosition: Position;
  targetPosition: Position;
  data?: DataFlowEdgeData;
}) {
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

  // Determine edge color based on state
  const strokeColor = isCompleted
    ? '#22c55e' // green for completed data transfer
    : isDataFlowing
      ? '#3b82f6' // blue for active data flow
      : '#0ea5e9'; // default cyan

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          stroke: strokeColor,
          strokeWidth: isDataFlowing ? 3 : 2,
          transition: 'stroke 0.3s, stroke-width 0.3s',
        }}
        markerEnd={`url(#arrow-${isCompleted ? 'completed' : isDataFlowing ? 'flowing' : 'default'})`}
      />
      {/* Animated dots for active data flow */}
      {isDataFlowing && (
        <circle r="4" fill="#3b82f6">
          <animateMotion dur="1s" repeatCount="indefinite" path={edgePath} />
        </circle>
      )}
      {/* Show checkmark when data transfer is complete */}
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
    </>
  );
}

const edgeTypes: EdgeTypes = {
  dataFlow: DataFlowEdge,
};

// Custom node component with connection handles
function StageNode({ data, selected }: { data: StageNodeData; selected?: boolean }) {
  const Icon = getIconComponent(data.icon, data.kind);
  const execStatus = data.executionStatus || 'idle';
  const statusConfig = executionStatusConfig[execStatus];
  const StatusIcon = statusConfig.icon;

  // Determine border and ring styling based on execution status (takes precedence) or selection
  const isExecuting = execStatus !== 'idle';
  const borderClass = isExecuting
    ? statusConfig.borderClass
    : (selected
        ? 'border-primary-500'
        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600');

  const ringClass = isExecuting
    ? statusConfig.ringClass
    : (selected ? 'ring-4 ring-primary-200 dark:ring-primary-800' : '');

  return (
    <div
      className={`
        relative min-w-[200px] p-4 rounded-xl border-2 shadow-lg transition-all
        bg-white dark:bg-slate-800
        ${borderClass}
        ${ringClass}
        ${statusConfig.glowClass || ''}
        ${!isExecuting && !selected ? 'hover:shadow-xl' : ''}
        ${execStatus === 'running' ? 'animate-pulse' : ''}
      `}
    >
      {/* Input handle (top) - receives connections from other nodes */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-top-2 transition-colors"
      />

      <div className="flex items-start gap-3">
        <div
          className={`w-10 h-10 rounded-xl flex items-center justify-center text-white flex-shrink-0 shadow-md relative ${
            execStatus === 'running' ? 'animate-pulse' : ''
          }`}
          style={{ backgroundColor: data.color }}
        >
          <Icon className="w-5 h-5" />
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
          {data.showNotes && data.description && (
            <div className="text-xs text-slate-400 dark:text-slate-500 line-clamp-2 mt-1">
              {data.description}
            </div>
          )}
        </div>
      </div>

      {/* Execution status indicator (top-left) */}
      {StatusIcon && (
        <div className="absolute -top-2 -left-2 bg-white dark:bg-slate-800 rounded-full p-0.5 shadow-md">
          <StatusIcon className={`w-5 h-5 ${statusConfig.iconClass} ${statusConfig.animate ? 'animate-spin' : ''}`} />
        </div>
      )}

      {/* Breakpoint indicator (top-right, shown when breakpoint is set) */}
      {data.hasBreakpoint && (
        <div className="absolute -top-2 -right-2 bg-red-500 rounded-full p-0.5 shadow-md z-10" title="Breakpoint set">
          <CircleDot className="w-4 h-4 text-white" />
        </div>
      )}

      {/* Kind badge (top-right, hidden when breakpoint is shown) */}
      {!data.hasBreakpoint && (
        <div className="absolute -top-2 -right-2">
          <Badge
            variant={data.kind === 'node' ? 'default' : 'warning'}
            className="text-xs px-1.5 py-0 shadow-sm"
          >
            {data.kind}
          </Badge>
        </div>
      )}

      {/* Inspect button - shown when has execution data */}
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

      {/* Output handle (bottom) - sends connections to other nodes */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-4 !h-4 !bg-slate-300 dark:!bg-slate-600 hover:!bg-primary-500 !border-2 !border-white dark:!border-slate-800 !-bottom-2 transition-colors"
      />
    </div>
  );
}

interface StageNodeData extends Record<string, unknown> {
  label: string;
  componentType: string;
  kind: 'node' | 'operator' | 'control_flow';
  color: string;
  icon?: string;
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
  // Control flow specific
  controlFlowType?: ControlFlowType;
}

// Wrapper component that delegates to ControlFlowNode for control flow types
function ControlFlowNodeWrapper({ data, selected }: { data: StageNodeData; selected?: boolean }) {
  // Convert StageNodeData to ControlFlowNodeData
  const controlFlowData: ControlFlowNodeData = {
    label: data.label,
    componentType: data.componentType,
    controlFlowType: data.controlFlowType || 'conditional',
    color: data.color,
    config: data.config,
    description: data.description,
    showNotes: data.showNotes,
    executionStatus: data.executionStatus,
    hasExecutionData: data.hasExecutionData,
    onInspect: data.onInspect,
    isDebugMode: data.isDebugMode,
    hasBreakpoint: data.hasBreakpoint,
  };

  return <ControlFlowNode data={controlFlowData} selected={selected} />;
}

const nodeTypes: NodeTypes = {
  stage: StageNode,
  controlFlow: ControlFlowNodeWrapper,
};

// Stage execution state with I/O data
export interface StageExecutionState {
  status: ExecutionStatus;
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
  startTime?: number;
  endTime?: number;
}

interface PipelineCanvasProps {
  stages: PipelineStage[];
  onStagesChange: (stages: PipelineStage[]) => void;
  onStageSelect: (stageId: string | null) => void;
  selectedStageId: string | null;
  components: ComponentInfo[];
  showNotes?: boolean;
  // Execution visualization
  stageExecutionStates?: Record<string, StageExecutionState>;
  onStageInspect?: (stageId: string) => void;
  // Debug mode
  isDebugMode?: boolean;
  breakpoints?: string[]; // Stage IDs with breakpoints
  onNodeContextMenu?: (stageId: string, event: React.MouseEvent) => void;
}

function PipelineCanvasInner({
  stages,
  onStagesChange,
  onStageSelect,
  selectedStageId,
  components,
  showNotes = false,
  stageExecutionStates = {},
  onStageInspect,
  isDebugMode = false,
  breakpoints = [],
  onNodeContextMenu,
}: PipelineCanvasProps) {
  const reactFlow = useReactFlow();
  const [isDragOver, setIsDragOver] = useState(false);
  const dragCounter = useRef(0);

  // Convert stages to ReactFlow nodes
  const initialNodes: Node<StageNodeData>[] = stages.map((stage) => {
    const component = components.find(
      (c) => c.component_type === stage.component_type
    );
    const execState = stageExecutionStates[stage.id];
    const hasExecutionData = execState && (execState.input || execState.output);
    const isControlFlow = component?.component_kind === 'control_flow';

    return {
      id: stage.id,
      type: isControlFlow ? 'controlFlow' : 'stage',
      position: stage.position || { x: 100, y: 100 },
      selected: stage.id === selectedStageId,
      data: {
        label: stage.name,
        componentType: stage.component_type,
        kind: component?.component_kind || 'node',
        color: component?.color || '#6B7280',
        icon: component?.icon,
        config: stage.config,
        requiresLLM: component?.requires_llm,
        description: component?.description,
        showNotes,
        // Execution state
        executionStatus: execState?.status,
        hasExecutionData: !!hasExecutionData,
        onInspect: hasExecutionData ? () => onStageInspect?.(stage.id) : undefined,
        // Debug mode
        isDebugMode,
        hasBreakpoint: breakpoints.includes(stage.id),
        // Control flow specific
        controlFlowType: component?.control_flow_type,
      },
    };
  });

  // Convert dependencies to edges with data flow visualization
  const initialEdges: Edge<DataFlowEdgeData>[] = stages.flatMap((stage) =>
    stage.depends_on.map((depId) => {
      const sourceExecState = stageExecutionStates[depId];
      const targetExecState = stageExecutionStates[stage.id];

      // Data is flowing when source is completed/success and target is running
      const isDataFlowing =
        (sourceExecState?.status === 'completed' || sourceExecState?.status === 'success') &&
        targetExecState?.status === 'running';

      // Data transfer is completed when both source and target are done
      const isCompleted =
        (sourceExecState?.status === 'completed' || sourceExecState?.status === 'success') &&
        (targetExecState?.status === 'completed' || targetExecState?.status === 'success');

      return {
        id: `${depId}-${stage.id}`,
        source: depId,
        target: stage.id,
        type: 'dataFlow',
        animated: !isCompleted && !isDataFlowing,
        data: {
          sourceStage: depId,
          targetStage: stage.id,
          isDataFlowing,
          isCompleted,
        },
      };
    })
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when execution state or debug mode changes
  useEffect(() => {
    setNodes((currentNodes) =>
      currentNodes.map((node) => {
        const execState = stageExecutionStates[node.id];
        const hasExecutionData = execState && (execState.input || execState.output);
        return {
          ...node,
          data: {
            ...node.data,
            executionStatus: execState?.status,
            hasExecutionData: !!hasExecutionData,
            onInspect: hasExecutionData ? () => onStageInspect?.(node.id) : undefined,
            isDebugMode,
            hasBreakpoint: breakpoints.includes(node.id),
          },
        };
      })
    );
  }, [stageExecutionStates, setNodes, onStageInspect, isDebugMode, breakpoints]);

  // Update edges when execution state changes
  useEffect(() => {
    setEdges((currentEdges) =>
      currentEdges.map((edge) => {
        const sourceExecState = stageExecutionStates[edge.source];
        const targetExecState = stageExecutionStates[edge.target];

        const isDataFlowing =
          (sourceExecState?.status === 'completed' || sourceExecState?.status === 'success') &&
          targetExecState?.status === 'running';

        const isCompleted =
          (sourceExecState?.status === 'completed' || sourceExecState?.status === 'success') &&
          (targetExecState?.status === 'completed' || targetExecState?.status === 'success');

        return {
          ...edge,
          animated: !isCompleted && !isDataFlowing,
          data: {
            ...edge.data,
            isDataFlowing,
            isCompleted,
          },
        };
      })
    );
  }, [stageExecutionStates, setEdges]);

  // Handle new connections
  const onConnect = useCallback(
    (connection: Connection) => {
      const newEdge: Edge<DataFlowEdgeData> = {
        ...connection,
        id: `${connection.source}-${connection.target}`,
        type: 'dataFlow',
        animated: true,
        data: {
          sourceStage: connection.source ?? undefined,
          targetStage: connection.target ?? undefined,
          isDataFlowing: false,
          isCompleted: false,
        },
      };
      setEdges((eds) => addEdge(newEdge, eds));

      // Update stages with new dependency
      const updatedStages = stages.map((stage) => {
        if (stage.id === connection.target && connection.source) {
          return {
            ...stage,
            depends_on: [...stage.depends_on, connection.source],
          };
        }
        return stage;
      });
      onStagesChange(updatedStages);
    },
    [stages, onStagesChange, setEdges]
  );

  // Handle node selection
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      onStageSelect(node.id);
    },
    [onStageSelect]
  );

  // Handle node right-click (context menu for breakpoints)
  const handleNodeContextMenu = useCallback(
    (event: React.MouseEvent, node: Node) => {
      if (onNodeContextMenu) {
        event.preventDefault();
        onNodeContextMenu(node.id, event);
      }
    },
    [onNodeContextMenu]
  );

  // Handle canvas click (deselect)
  const onPaneClick = useCallback(() => {
    onStageSelect(null);
  }, [onStageSelect]);

  // Handle node position changes
  const onNodeDragStop = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const updatedStages = stages.map((stage) => {
        if (stage.id === node.id) {
          return { ...stage, position: node.position };
        }
        return stage;
      });
      onStagesChange(updatedStages);
    },
    [stages, onStagesChange]
  );

  // Handle drop from palette
  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      dragCounter.current = 0;
      setIsDragOver(false);

      const data = event.dataTransfer.getData('application/fm-component');
      if (!data) return;

      try {
        const component: ComponentInfo = JSON.parse(data);
        const position = reactFlow.screenToFlowPosition({
          x: event.clientX,
          y: event.clientY,
        });

        // Extract default values from component input schema
        const defaultConfig: Record<string, unknown> = {};
        const inputSchema = component.input_schema;
        if (inputSchema?.properties) {
          for (const [key, prop] of Object.entries(inputSchema.properties)) {
            if (prop.default !== undefined) {
              defaultConfig[key] = prop.default;
            }
          }
        }

        // Create new stage with default values pre-populated
        const newStage: PipelineStage = {
          id: `${component.component_type}-${Date.now()}`,
          component_type: component.component_type,
          name: component.name,
          config: defaultConfig,
          depends_on: [],
          position,
        };

        // Add node to canvas
        const isControlFlow = component.component_kind === 'control_flow';
        const newNode: Node<StageNodeData> = {
          id: newStage.id,
          type: isControlFlow ? 'controlFlow' : 'stage',
          position,
          data: {
            label: newStage.name,
            componentType: component.component_type,
            kind: component.component_kind,
            color: component.color,
            icon: component.icon,
            config: defaultConfig,
            requiresLLM: component.requires_llm,
            description: component.description,
            // Control flow specific
            controlFlowType: component.control_flow_type,
          },
        };

        setNodes((nds) => [...nds, newNode]);
        onStagesChange([...stages, newStage]);
        onStageSelect(newStage.id);
      } catch {
        // Ignore malformed drops
      }
    },
    [reactFlow, stages, onStagesChange, onStageSelect, setNodes]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
  }, []);

  const onDragEnter = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    dragCounter.current++;
    if (event.dataTransfer.types.includes('application/fm-component')) {
      setIsDragOver(true);
    }
  }, []);

  const onDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setIsDragOver(false);
    }
  }, []);

  // Handle node deletion
  const onNodesDelete = useCallback(
    (deletedNodes: Node[]) => {
      const deletedIds = new Set(deletedNodes.map((n) => n.id));
      const updatedStages = stages
        .filter((stage) => !deletedIds.has(stage.id))
        .map((stage) => ({
          ...stage,
          depends_on: stage.depends_on.filter((id) => !deletedIds.has(id)),
        }));
      onStagesChange(updatedStages);

      if (selectedStageId && deletedIds.has(selectedStageId)) {
        onStageSelect(null);
      }
    },
    [stages, onStagesChange, selectedStageId, onStageSelect]
  );

  // Auto-layout: arrange nodes vertically based on dependency order
  const handleAutoLayout = useCallback(() => {
    if (stages.length === 0) return;

    // Build adjacency list and in-degree map for topological sort
    const inDegree = new Map<string, number>();
    const children = new Map<string, string[]>();

    stages.forEach((stage) => {
      inDegree.set(stage.id, stage.depends_on.length);
      if (!children.has(stage.id)) {
        children.set(stage.id, []);
      }
      stage.depends_on.forEach((depId) => {
        if (!children.has(depId)) {
          children.set(depId, []);
        }
        children.get(depId)!.push(stage.id);
      });
    });

    // Kahn's algorithm for topological sort with level assignment
    const levels: string[][] = [];
    let currentLevel: string[] = [];

    // Start with nodes that have no dependencies
    stages.forEach((stage) => {
      if (stage.depends_on.length === 0) {
        currentLevel.push(stage.id);
      }
    });

    while (currentLevel.length > 0) {
      levels.push([...currentLevel]);
      const nextLevel: string[] = [];

      currentLevel.forEach((nodeId) => {
        const nodeChildren = children.get(nodeId) || [];
        nodeChildren.forEach((childId) => {
          const newDegree = (inDegree.get(childId) || 0) - 1;
          inDegree.set(childId, newDegree);
          if (newDegree === 0) {
            nextLevel.push(childId);
          }
        });
      });

      currentLevel = nextLevel;
    }

    // Calculate positions - center horizontally, space vertically
    const nodeWidth = 240;
    const nodeHeight = 100;
    const verticalSpacing = 120;
    const horizontalSpacing = 280;

    const newPositions = new Map<string, { x: number; y: number }>();

    levels.forEach((levelNodes, levelIndex) => {
      const totalWidth = levelNodes.length * nodeWidth + (levelNodes.length - 1) * (horizontalSpacing - nodeWidth);
      const startX = 400 - totalWidth / 2;

      levelNodes.forEach((nodeId, nodeIndex) => {
        newPositions.set(nodeId, {
          x: startX + nodeIndex * horizontalSpacing,
          y: 100 + levelIndex * (nodeHeight + verticalSpacing),
        });
      });
    });

    // Update stages with new positions
    const updatedStages = stages.map((stage) => ({
      ...stage,
      position: newPositions.get(stage.id) || stage.position || { x: 100, y: 100 },
    }));

    // Update nodes state
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        position: newPositions.get(node.id) || node.position,
      }))
    );

    onStagesChange(updatedStages);

    // Fit view after layout
    setTimeout(() => {
      reactFlow.fitView({ padding: 0.2, duration: 300 });
    }, 50);
  }, [stages, onStagesChange, setNodes, reactFlow]);

  return (
    <div
      className={`flex-1 h-full relative transition-colors ${
        isDragOver
          ? 'bg-primary-50 dark:bg-primary-900/20'
          : 'bg-slate-50 dark:bg-slate-900'
      }`}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragEnter={onDragEnter}
      onDragLeave={onDragLeave}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onNodeContextMenu={handleNodeContextMenu}
        onPaneClick={onPaneClick}
        onNodeDragStop={onNodeDragStop}
        onNodesDelete={onNodesDelete}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        snapToGrid
        snapGrid={[16, 16]}
        deleteKeyCode={['Backspace', 'Delete']}
        className="bg-slate-50 dark:bg-slate-900"
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={16}
          size={1}
          className="!bg-slate-50 dark:!bg-slate-900"
          color="rgb(148 163 184)"
        />
        <Controls
          className="!bg-white dark:!bg-slate-800 !border-slate-200 dark:!border-slate-700 !shadow-lg !rounded-lg overflow-hidden [&>button]:!bg-white dark:[&>button]:!bg-slate-800 [&>button]:!border-slate-200 dark:[&>button]:!border-slate-700 [&>button]:hover:!bg-slate-50 dark:[&>button]:hover:!bg-slate-700 [&>button]:!text-slate-600 dark:[&>button]:!text-slate-300"
        />

        {/* Auto-layout button */}
        <div className="absolute top-4 right-4 z-10">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleAutoLayout}
            disabled={stages.length === 0}
            className="shadow-lg gap-2"
            title="Auto-arrange nodes vertically"
          >
            <AlignVerticalSpaceAround className="w-4 h-4" />
            Auto Layout
          </Button>
        </div>

        <MiniMap
          className="!bg-white dark:!bg-slate-800 !border-slate-200 dark:!border-slate-700 !shadow-lg !rounded-lg"
          nodeColor={(node) => (node.data as StageNodeData).color}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>

      {/* Empty state */}
      {stages.length === 0 && !isDragOver && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center p-8 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-600 shadow-lg">
            <Box className="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600 mb-4" />
            <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-2">
              Start Building Your Pipeline
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-xs">
              Drag components from the palette on the left to create stages.
              Connect them to define the execution flow.
            </p>
          </div>
        </div>
      )}

      {/* Drop hint overlay */}
      {isDragOver && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-primary-500 text-white px-6 py-3 rounded-xl shadow-2xl flex items-center gap-3 animate-pulse">
            <Box className="w-5 h-5" />
            <span className="font-medium">Drop component here</span>
          </div>
        </div>
      )}

      {/* Delete hint */}
      {selectedStageId && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 pointer-events-none">
          <div className="bg-slate-800/90 dark:bg-slate-700/90 text-white text-sm px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
            <Trash2 className="w-4 h-4 text-red-400" />
            <span>Press <kbd className="px-1.5 py-0.5 bg-slate-700 dark:bg-slate-600 rounded text-xs">Delete</kbd> to remove</span>
          </div>
        </div>
      )}
    </div>
  );
}

// Wrap with provider
export function PipelineCanvas(props: PipelineCanvasProps) {
  return (
    <ReactFlowProvider>
      <PipelineCanvasInner {...props} />
    </ReactFlowProvider>
  );
}

export default PipelineCanvas;
