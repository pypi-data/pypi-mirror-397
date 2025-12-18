/**
 * Stage Inspector
 *
 * A floating panel that shows the input/output of a pipeline stage.
 * Opens when clicking the "inspect" button on a stage node during execution.
 */

import { useState } from 'react';
import {
  X,
  ArrowRight,
  CheckCircle,
  XCircle,
  Loader2,
  Clock,
  Copy,
  Check,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  GitBranch,
} from 'lucide-react';
import { Card, CardContent, Badge, Button } from '@/components/ui';
import type { StageExecutionState, ExecutionStatus } from './PipelineCanvas';
import type { PipelineStage } from '../types';

interface StageInspectorProps {
  stage: PipelineStage;
  executionState: StageExecutionState;
  upstreamStages: PipelineStage[];
  downstreamStages: PipelineStage[];
  onClose: () => void;
}

const statusConfig: Record<ExecutionStatus, {
  icon: typeof CheckCircle;
  color: string;
  bgColor: string;
  label: string;
}> = {
  idle: { icon: Clock, color: 'text-slate-400', bgColor: 'bg-slate-50', label: 'Idle' },
  pending: { icon: Clock, color: 'text-slate-500', bgColor: 'bg-slate-100', label: 'Pending' },
  running: { icon: Loader2, color: 'text-blue-500', bgColor: 'bg-blue-50', label: 'Running' },
  completed: { icon: CheckCircle, color: 'text-green-500', bgColor: 'bg-green-50', label: 'Completed' },
  success: { icon: CheckCircle, color: 'text-green-500', bgColor: 'bg-green-50', label: 'Success' },
  failed: { icon: XCircle, color: 'text-red-500', bgColor: 'bg-red-50', label: 'Failed' },
};

export function StageInspector({
  stage,
  executionState,
  upstreamStages,
  downstreamStages,
  onClose,
}: StageInspectorProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    input: true,
    output: true,
    connections: false,
  });

  const status = statusConfig[executionState.status] || statusConfig.idle;
  const StatusIcon = status.icon;

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="fixed bottom-4 right-4 w-96 max-h-[70vh] bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 z-50 flex flex-col overflow-hidden">
      {/* Header */}
      <div className={`px-4 py-3 border-b border-slate-200 dark:border-slate-700 ${status.bgColor} dark:bg-opacity-20`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <StatusIcon className={`w-5 h-5 ${status.color} ${executionState.status === 'running' ? 'animate-spin' : ''}`} />
            <div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">{stage.name}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-mono">{stage.component_type}</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0">
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Status Badge */}
        <div className="mt-2 flex items-center gap-2">
          <Badge variant={executionState.status === 'failed' ? 'destructive' : 'secondary'}>
            {status.label}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {/* Error Message */}
        {executionState.error && (
          <Card className="border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
            <CardContent className="p-3 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
              <pre className="text-xs text-red-700 dark:text-red-300 whitespace-pre-wrap font-mono">
                {executionState.error}
              </pre>
            </CardContent>
          </Card>
        )}

        {/* Input Section */}
        <CollapsibleSection
          title="Input"
          icon={<ArrowRight className="w-4 h-4 rotate-180" />}
          expanded={expandedSections.input}
          onToggle={() => toggleSection('input')}
          badge={executionState.input ? Object.keys(executionState.input).length : 0}
        >
          {executionState.input && Object.keys(executionState.input).length > 0 ? (
            <DataDisplay data={executionState.input} />
          ) : (
            <p className="text-sm text-slate-400 dark:text-slate-500 italic">No input data</p>
          )}
        </CollapsibleSection>

        {/* Output Section */}
        <CollapsibleSection
          title="Output"
          icon={<ArrowRight className="w-4 h-4" />}
          expanded={expandedSections.output}
          onToggle={() => toggleSection('output')}
          badge={executionState.output ? Object.keys(executionState.output).length : 0}
          highlight={executionState.status === 'completed' || executionState.status === 'success'}
        >
          {executionState.output && Object.keys(executionState.output).length > 0 ? (
            <DataDisplay data={executionState.output} />
          ) : (
            <p className="text-sm text-slate-400 dark:text-slate-500 italic">
              {executionState.status === 'running' ? 'Waiting for output...' : 'No output data'}
            </p>
          )}
        </CollapsibleSection>

        {/* Connections Section */}
        <CollapsibleSection
          title="Connections"
          icon={<GitBranch className="w-4 h-4" />}
          expanded={expandedSections.connections}
          onToggle={() => toggleSection('connections')}
          badge={upstreamStages.length + downstreamStages.length}
        >
          <div className="space-y-2">
            {upstreamStages.length > 0 && (
              <div>
                <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Receives from:</p>
                <div className="flex flex-wrap gap-1">
                  {upstreamStages.map((s) => (
                    <Badge key={s.id} variant="outline" className="text-xs">
                      {s.name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {downstreamStages.length > 0 && (
              <div>
                <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Sends to:</p>
                <div className="flex flex-wrap gap-1">
                  {downstreamStages.map((s) => (
                    <Badge key={s.id} variant="outline" className="text-xs">
                      {s.name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {upstreamStages.length === 0 && downstreamStages.length === 0 && (
              <p className="text-sm text-slate-400 dark:text-slate-500 italic">No connections</p>
            )}
          </div>
        </CollapsibleSection>
      </div>
    </div>
  );
}

interface CollapsibleSectionProps {
  title: string;
  icon: React.ReactNode;
  expanded: boolean;
  onToggle: () => void;
  badge?: number;
  highlight?: boolean;
  children: React.ReactNode;
}

function CollapsibleSection({
  title,
  icon,
  expanded,
  onToggle,
  badge,
  highlight,
  children,
}: CollapsibleSectionProps) {
  return (
    <div
      className={`rounded-lg border ${
        highlight
          ? 'border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-900/10'
          : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50'
      } overflow-hidden`}
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-2 px-3 py-2 hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
      >
        {expanded ? (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-slate-400" />
        )}
        <span className={`${highlight ? 'text-green-600 dark:text-green-400' : 'text-slate-500 dark:text-slate-400'}`}>
          {icon}
        </span>
        <span className={`text-sm font-medium ${highlight ? 'text-green-700 dark:text-green-300' : 'text-slate-700 dark:text-slate-300'}`}>
          {title}
        </span>
        {badge !== undefined && badge > 0 && (
          <Badge variant="secondary" className="ml-auto text-xs py-0">
            {badge} {badge === 1 ? 'field' : 'fields'}
          </Badge>
        )}
      </button>
      {expanded && <div className="px-3 pb-3">{children}</div>}
    </div>
  );
}

interface DataDisplayProps {
  data: Record<string, unknown>;
}

function DataDisplay({ data }: DataDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Check if output has a 'content' field (common for LLM outputs)
  const keys = Object.keys(data);
  if ('content' in data && typeof data.content === 'string') {
    return (
      <div className="space-y-2">
        <div className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap bg-white dark:bg-slate-800 p-2 rounded border border-slate-200 dark:border-slate-700">
          {data.content}
        </div>
        {keys.length > 1 && (
          <details className="text-xs">
            <summary className="text-slate-500 dark:text-slate-400 cursor-pointer hover:text-slate-700 dark:hover:text-slate-300">
              Show all fields ({keys.length})
            </summary>
            <div className="mt-2 relative group">
              <button
                onClick={handleCopy}
                className="absolute top-1 right-1 p-1 rounded bg-slate-200/80 dark:bg-slate-700/80 text-slate-500 dark:text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-300 dark:hover:bg-slate-600"
              >
                {copied ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3" />}
              </button>
              <pre className="p-2 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 overflow-x-auto text-slate-600 dark:text-slate-400 whitespace-pre-wrap">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </details>
        )}
      </div>
    );
  }

  // Default: show as JSON with copy button
  return (
    <div className="relative group">
      <button
        onClick={handleCopy}
        className="absolute top-1 right-1 p-1 rounded bg-slate-200/80 dark:bg-slate-700/80 text-slate-500 dark:text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-300 dark:hover:bg-slate-600"
      >
        {copied ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3" />}
      </button>
      <pre className="text-xs text-slate-700 dark:text-slate-300 overflow-x-auto whitespace-pre-wrap font-mono bg-white dark:bg-slate-800 p-2 rounded border border-slate-200 dark:border-slate-700">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}

export default StageInspector;
