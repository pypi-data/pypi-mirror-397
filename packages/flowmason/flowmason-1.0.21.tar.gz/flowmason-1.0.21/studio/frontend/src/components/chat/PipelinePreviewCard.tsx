/**
 * Pipeline Preview Card Component
 *
 * Rich, interactive preview of a generated pipeline shown inline in chat.
 * Features visual flow diagram, sequence view, and action buttons.
 * Designed for a class-A user experience.
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Workflow,
  Play,
  ExternalLink,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Cpu,
  Zap,
  Clock,
  Filter,
  Code2,
  Globe,
  LayoutList,
  Brain,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  GitBranch,
  Repeat,
  FileOutput,
  Database,
  Settings2,
  ArrowDown,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

// Stage type from generated pipeline
interface PipelineStage {
  id: string;
  name: string;
  component_type: string;
  config?: Record<string, unknown>;
  depends_on?: string[];
  rationale?: string;
}

// Pipeline structure
interface Pipeline {
  id?: string;
  name: string;
  version: string;
  description: string;
  stages: PipelineStage[];
  output_stage_id?: string;
  is_fallback?: boolean;
}

interface PipelinePreviewCardProps {
  pipeline: Pipeline;
  analysis?: {
    intent?: string;
    actions?: string[];
    patterns?: string[];
    _dry_run_summary?: {
      stage_count: number;
      uses_llm: boolean;
      uses_external_io: boolean;
      estimated_complexity: string;
    };
  };
  onSave?: () => void;
  onRun?: () => void;
  saving?: boolean;
}

// Icon mapping for component types
const COMPONENT_ICONS: Record<string, React.ReactNode> = {
  generator: <Brain className="w-4 h-4" />,
  critic: <Sparkles className="w-4 h-4" />,
  improver: <Zap className="w-4 h-4" />,
  synthesizer: <Cpu className="w-4 h-4" />,
  filter: <Filter className="w-4 h-4" />,
  json_transform: <Code2 className="w-4 h-4" />,
  http_request: <Globe className="w-4 h-4" />,
  schema_validate: <LayoutList className="w-4 h-4" />,
  logger: <FileOutput className="w-4 h-4" />,
  selector: <Filter className="w-4 h-4" />,
  foreach: <Repeat className="w-4 h-4" />,
  conditional: <GitBranch className="w-4 h-4" />,
  variable_set: <Database className="w-4 h-4" />,
  loop: <Repeat className="w-4 h-4" />,
};

// Color mapping for component types
const COMPONENT_COLORS: Record<string, { bg: string; text: string; border: string; gradient: string }> = {
  generator: { bg: 'bg-purple-100 dark:bg-purple-900/40', text: 'text-purple-700 dark:text-purple-300', border: 'border-purple-300 dark:border-purple-700', gradient: 'from-purple-400 to-purple-600' },
  critic: { bg: 'bg-amber-100 dark:bg-amber-900/40', text: 'text-amber-700 dark:text-amber-300', border: 'border-amber-300 dark:border-amber-700', gradient: 'from-amber-400 to-amber-600' },
  improver: { bg: 'bg-blue-100 dark:bg-blue-900/40', text: 'text-blue-700 dark:text-blue-300', border: 'border-blue-300 dark:border-blue-700', gradient: 'from-blue-400 to-blue-600' },
  synthesizer: { bg: 'bg-green-100 dark:bg-green-900/40', text: 'text-green-700 dark:text-green-300', border: 'border-green-300 dark:border-green-700', gradient: 'from-green-400 to-green-600' },
  filter: { bg: 'bg-orange-100 dark:bg-orange-900/40', text: 'text-orange-700 dark:text-orange-300', border: 'border-orange-300 dark:border-orange-700', gradient: 'from-orange-400 to-orange-600' },
  json_transform: { bg: 'bg-cyan-100 dark:bg-cyan-900/40', text: 'text-cyan-700 dark:text-cyan-300', border: 'border-cyan-300 dark:border-cyan-700', gradient: 'from-cyan-400 to-cyan-600' },
  http_request: { bg: 'bg-indigo-100 dark:bg-indigo-900/40', text: 'text-indigo-700 dark:text-indigo-300', border: 'border-indigo-300 dark:border-indigo-700', gradient: 'from-indigo-400 to-indigo-600' },
  schema_validate: { bg: 'bg-teal-100 dark:bg-teal-900/40', text: 'text-teal-700 dark:text-teal-300', border: 'border-teal-300 dark:border-teal-700', gradient: 'from-teal-400 to-teal-600' },
  logger: { bg: 'bg-gray-100 dark:bg-gray-800/60', text: 'text-gray-700 dark:text-gray-300', border: 'border-gray-300 dark:border-gray-600', gradient: 'from-gray-400 to-gray-600' },
  foreach: { bg: 'bg-rose-100 dark:bg-rose-900/40', text: 'text-rose-700 dark:text-rose-300', border: 'border-rose-300 dark:border-rose-700', gradient: 'from-rose-400 to-rose-600' },
  conditional: { bg: 'bg-sky-100 dark:bg-sky-900/40', text: 'text-sky-700 dark:text-sky-300', border: 'border-sky-300 dark:border-sky-700', gradient: 'from-sky-400 to-sky-600' },
};

function getComponentColors(type: string) {
  return COMPONENT_COLORS[type] || { bg: 'bg-gray-100 dark:bg-gray-800', text: 'text-gray-700 dark:text-gray-300', border: 'border-gray-300 dark:border-gray-700', gradient: 'from-gray-400 to-gray-600' };
}

function getComponentIcon(type: string): React.ReactNode {
  return COMPONENT_ICONS[type] || <Settings2 className="w-4 h-4" />;
}

/**
 * Sequence Diagram - Vertical flow showing data transformation
 */
function SequenceDiagram({ stages, outputStageId }: { stages: PipelineStage[]; outputStageId?: string }) {
  return (
    <div className="relative py-4">
      {/* Input */}
      <div className="flex items-center gap-4 mb-2">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400 to-green-500 flex items-center justify-center shadow-lg">
          <Database className="w-6 h-6 text-white" />
        </div>
        <div>
          <p className="font-semibold text-gray-900 dark:text-gray-100">Input Data</p>
          <p className="text-sm text-muted-foreground">Pipeline receives data</p>
        </div>
      </div>

      {/* Connector line */}
      <div className="ml-6 w-0.5 h-4 bg-gradient-to-b from-emerald-400 to-gray-300 dark:to-gray-600" />

      {/* Stages */}
      {stages.map((stage, idx) => {
        const colors = getComponentColors(stage.component_type);
        const isOutput = stage.id === outputStageId || idx === stages.length - 1;

        return (
          <div key={stage.id}>
            {/* Stage card */}
            <div className="flex items-start gap-4 group">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colors.gradient} flex items-center justify-center shadow-md transition-transform group-hover:scale-105`}>
                <div className="text-white">{getComponentIcon(stage.component_type)}</div>
              </div>
              <div className="flex-1 min-w-0 py-1">
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-gray-900 dark:text-gray-100">{stage.name}</p>
                  <Badge variant="outline" className={`text-xs ${colors.text} ${colors.border}`}>
                    {stage.component_type}
                  </Badge>
                  {isOutput && (
                    <Badge className="text-xs bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300 border-violet-300 dark:border-violet-700">
                      Output
                    </Badge>
                  )}
                </div>
                {stage.rationale && (
                  <p className="text-sm text-muted-foreground mt-0.5">{stage.rationale}</p>
                )}
                {stage.depends_on && stage.depends_on.length > 0 && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Depends on: {stage.depends_on.join(', ')}
                  </p>
                )}
              </div>
            </div>

            {/* Connector */}
            {idx < stages.length - 1 && (
              <div className="ml-6 flex items-center gap-2 py-1">
                <div className="w-0.5 h-6 bg-gray-300 dark:bg-gray-600" />
                <ArrowDown className="w-3 h-3 text-gray-400" />
              </div>
            )}
          </div>
        );
      })}

      {/* Final connector */}
      <div className="ml-6 w-0.5 h-4 bg-gradient-to-b from-gray-300 dark:from-gray-600 to-violet-400" />

      {/* Output */}
      <div className="flex items-center gap-4 mt-2">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center shadow-lg">
          <FileOutput className="w-6 h-6 text-white" />
        </div>
        <div>
          <p className="font-semibold text-gray-900 dark:text-gray-100">Output Result</p>
          <p className="text-sm text-muted-foreground">Pipeline returns processed data</p>
        </div>
      </div>
    </div>
  );
}

/**
 * Compact horizontal flow visualization
 */
function FlowDiagram({ stages }: { stages: PipelineStage[] }) {
  const maxDisplay = 6;
  const displayStages = stages.slice(0, maxDisplay);
  const hasMore = stages.length > maxDisplay;

  return (
    <div className="flex items-center gap-2 overflow-x-auto py-4 px-2">
      {/* Input node */}
      <div className="flex-shrink-0 flex flex-col items-center gap-1.5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-green-500 flex items-center justify-center shadow-md">
          <Database className="w-5 h-5 text-white" />
        </div>
        <span className="text-xs font-medium text-muted-foreground">Input</span>
      </div>

      {/* Connector */}
      <ArrowRight className="flex-shrink-0 w-5 h-5 text-gray-400" />

      {/* Stage nodes */}
      {displayStages.map((stage, idx) => {
        const colors = getComponentColors(stage.component_type);
        return (
          <div key={stage.id} className="flex items-center gap-2">
            <div className="flex flex-col items-center gap-1.5 group">
              <div
                className={`flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br ${colors.gradient} flex items-center justify-center shadow-md transition-transform group-hover:scale-110 cursor-pointer`}
                title={`${stage.name}\n${stage.component_type}${stage.rationale ? `\n${stage.rationale}` : ''}`}
              >
                <div className="text-white">{getComponentIcon(stage.component_type)}</div>
              </div>
              <span className="text-xs font-medium text-muted-foreground max-w-[70px] truncate text-center">
                {stage.name}
              </span>
            </div>
            {idx < displayStages.length - 1 && (
              <ArrowRight className="flex-shrink-0 w-4 h-4 text-gray-400" />
            )}
          </div>
        );
      })}

      {/* More indicator */}
      {hasMore && (
        <>
          <ArrowRight className="flex-shrink-0 w-4 h-4 text-gray-400" />
          <div className="flex flex-col items-center gap-1.5">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-sm font-medium text-gray-600 dark:text-gray-300">
              +{stages.length - maxDisplay}
            </div>
            <span className="text-xs text-muted-foreground">more</span>
          </div>
        </>
      )}

      {/* Connector to output */}
      <ArrowRight className="flex-shrink-0 w-5 h-5 text-gray-400" />

      {/* Output node */}
      <div className="flex-shrink-0 flex flex-col items-center gap-1.5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center shadow-md">
          <FileOutput className="w-5 h-5 text-white" />
        </div>
        <span className="text-xs font-medium text-muted-foreground">Output</span>
      </div>
    </div>
  );
}

export function PipelinePreviewCard({
  pipeline,
  analysis,
  onSave,
  onRun,
  saving = false,
}: PipelinePreviewCardProps) {
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<'flow' | 'sequence'>('flow');
  const [expanded, setExpanded] = useState(false);

  const usesAI = pipeline.stages.some((s) =>
    ['generator', 'critic', 'improver', 'synthesizer', 'selector'].includes(s.component_type)
  );
  const usesHTTP = pipeline.stages.some((s) => s.component_type === 'http_request');
  const usesLoop = pipeline.stages.some((s) => ['foreach', 'loop'].includes(s.component_type));

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(pipeline, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOpenEditor = () => {
    if (pipeline.id) {
      navigate(`/pipelines/${pipeline.id}`);
    }
  };

  return (
    <div className="rounded-2xl border-2 border-emerald-200 dark:border-emerald-800 bg-gradient-to-br from-white to-emerald-50/30 dark:from-gray-900 dark:to-emerald-950/20 shadow-lg overflow-hidden transition-all hover:shadow-xl">
      {/* Success Header */}
      <div className="px-5 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
          <CheckCircle2 className="w-6 h-6 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-lg text-white">Pipeline Created Successfully</h3>
          <p className="text-sm text-white/80">Your pipeline is ready to use</p>
        </div>
        {pipeline.id && (
          <Link
            to={`/pipelines/${pipeline.id}`}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 backdrop-blur text-white font-medium text-sm transition-all"
          >
            <ExternalLink className="w-4 h-4" />
            Open in Editor
          </Link>
        )}
      </div>

      {/* Pipeline Info */}
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-md">
              <Workflow className="w-6 h-6 text-white" />
            </div>
            <div>
              <h4 className="font-bold text-xl text-gray-900 dark:text-gray-100">
                {pipeline.name}
              </h4>
              <p className="text-sm text-muted-foreground">v{pipeline.version}</p>
            </div>
          </div>
          {pipeline.is_fallback && (
            <Badge variant="outline" className="text-amber-600 border-amber-300 dark:border-amber-700">
              Fallback
            </Badge>
          )}
        </div>

        {/* Description */}
        <p className="mt-4 text-base text-gray-700 dark:text-gray-300 leading-relaxed">
          {pipeline.description}
        </p>

        {/* Stats Badges */}
        <div className="mt-4 flex items-center gap-3 flex-wrap">
          <Badge variant="secondary" className="text-sm py-1 px-3">
            <LayoutList className="w-4 h-4 mr-1.5" />
            {pipeline.stages.length} stages
          </Badge>
          {usesAI && (
            <Badge className="text-sm py-1 px-3 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800">
              <Brain className="w-4 h-4 mr-1.5" />
              AI-Powered
            </Badge>
          )}
          {usesHTTP && (
            <Badge className="text-sm py-1 px-3 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800">
              <Globe className="w-4 h-4 mr-1.5" />
              External API
            </Badge>
          )}
          {usesLoop && (
            <Badge className="text-sm py-1 px-3 bg-rose-100 dark:bg-rose-900/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800">
              <Repeat className="w-4 h-4 mr-1.5" />
              Iteration
            </Badge>
          )}
          {analysis?._dry_run_summary && (
            <Badge variant="outline" className="text-sm py-1 px-3">
              <Clock className="w-4 h-4 mr-1.5" />
              ~{analysis._dry_run_summary.estimated_complexity}
            </Badge>
          )}
        </div>
      </div>

      {/* Visualization Toggle */}
      <div className="px-5 py-3 border-t border-gray-100 dark:border-gray-800 flex items-center gap-2">
        <span className="text-sm font-medium text-gray-600 dark:text-gray-400 mr-2">View:</span>
        <Button
          variant={viewMode === 'flow' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setViewMode('flow')}
          className="h-8 text-sm"
        >
          <GitBranch className="w-4 h-4 mr-1.5" />
          Flow
        </Button>
        <Button
          variant={viewMode === 'sequence' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setViewMode('sequence')}
          className="h-8 text-sm"
        >
          <LayoutList className="w-4 h-4 mr-1.5" />
          Sequence
        </Button>
      </div>

      {/* Visualization */}
      <div className="px-5 py-3 bg-gray-50/50 dark:bg-gray-800/30 border-y border-gray-100 dark:border-gray-800">
        {viewMode === 'flow' ? (
          <FlowDiagram stages={pipeline.stages} />
        ) : (
          <SequenceDiagram stages={pipeline.stages} outputStageId={pipeline.output_stage_id} />
        )}
      </div>

      {/* Expanded Stage Details */}
      {expanded && (
        <div className="px-5 py-4 border-t border-gray-100 dark:border-gray-800">
          <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
            All Pipeline Stages
          </p>
          <div className="space-y-3">
            {pipeline.stages.map((stage, idx) => {
              const colors = getComponentColors(stage.component_type);
              return (
                <div
                  key={stage.id}
                  className="flex items-start gap-3 p-4 rounded-xl bg-white dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700 shadow-sm"
                >
                  <span className="w-7 h-7 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-sm font-bold text-gray-600 dark:text-gray-400">
                    {idx + 1}
                  </span>
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${colors.gradient} flex items-center justify-center shadow-sm`}>
                    <div className="text-white">{getComponentIcon(stage.component_type)}</div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-gray-900 dark:text-gray-100">{stage.name}</p>
                      <Badge variant="outline" className={`text-xs ${colors.text} ${colors.border}`}>
                        {stage.component_type}
                      </Badge>
                    </div>
                    {stage.rationale && (
                      <p className="text-sm text-muted-foreground mt-1">{stage.rationale}</p>
                    )}
                    {stage.depends_on && stage.depends_on.length > 0 && (
                      <p className="text-xs text-muted-foreground mt-2">
                        <span className="font-medium">Dependencies:</span> {stage.depends_on.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-5 py-4 border-t border-gray-100 dark:border-gray-800 flex items-center gap-3 flex-wrap">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setExpanded(!expanded)}
          className="text-sm"
        >
          {expanded ? (
            <>
              <ChevronUp className="w-4 h-4 mr-1.5" />
              Hide Details
            </>
          ) : (
            <>
              <ChevronDown className="w-4 h-4 mr-1.5" />
              Show All Stages
            </>
          )}
        </Button>

        <Button variant="outline" size="sm" onClick={handleCopy} className="text-sm">
          {copied ? (
            <>
              <Check className="w-4 h-4 mr-1.5 text-green-500" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 mr-1.5" />
              Copy JSON
            </>
          )}
        </Button>

        <div className="flex-1" />

        {onRun && (
          <Button variant="outline" size="sm" onClick={onRun} className="text-sm">
            <Play className="w-4 h-4 mr-1.5" />
            Test Run
          </Button>
        )}

        {pipeline.id && (
          <Button
            size="sm"
            onClick={handleOpenEditor}
            className="text-sm bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
          >
            <ExternalLink className="w-4 h-4 mr-1.5" />
            Open in Editor
          </Button>
        )}

        {onSave && !pipeline.id && (
          <Button
            size="sm"
            onClick={onSave}
            disabled={saving}
            className="text-sm bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 mr-1.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Check className="w-4 h-4 mr-1.5" />
                Save Pipeline
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
