/**
 * API Console Page
 *
 * Interactive chat-like interface for testing APIs and running pipelines.
 * Supports natural commands, direct API calls, and real-time execution viewing.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  Send,
  Play,
  List,
  Heart,
  Box,
  Loader2,
  CheckCircle,
  XCircle,
  Copy,
  Trash2,
  Clock,
  ChevronDown,
  ChevronRight,
  Terminal,
  Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
// Badge and Textarea available for enhanced message display
// import { Badge } from '@/components/ui/badge';
// import { Textarea } from '@/components/ui/textarea';

// Message types
interface Message {
  id: string;
  type: 'user' | 'system' | 'result' | 'error';
  content: string;
  timestamp: Date;
  data?: unknown;
  stages?: StageExecution[];
  duration?: number;
}

interface StageExecution {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration?: number;
  output?: unknown;
}

interface Pipeline {
  id: string;
  name: string;
  version: string;
  description?: string;
}

interface Component {
  name: string;
  type: string;
  category: string;
  description?: string;
}

// AI Console response types (v1 subset)
interface ConsoleMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ConsoleDiagrams {
  flowchart?: string | null;
  sequence?: string | null;
  class?: string | null;
}

interface ConsolePipelineSummaryStage {
  id: string;
  name: string;
  component_type: string;
  depends_on?: string[];
  changed_by_ai?: boolean;
}

interface ConsolePipelineSummary {
  pipeline_id: string;
  name: string;
  description?: string | null;
  input_schema?: unknown;
  output_stage_id?: string | null;
  stages: ConsolePipelineSummaryStage[];
}

interface ConsoleClarificationQuestion {
  id: string;
  path: string;
  question: string;
  expected_type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'json';
  required: boolean;
  choices?: { value: string; label?: string }[] | null;
}

interface ConsoleRunStageResult {
  stage_id: string;
  component_type: string;
  status: string;
  duration_ms?: number | null;
  output_preview?: string | null;
  error?: string | null;
}

interface ConsoleRunResult {
  pipeline_id: string;
  run_id?: string | null;
  inputs_used: Record<string, unknown>;
  stage_results: ConsoleRunStageResult[];
  final_output?: unknown;
}

interface ConsoleActionResult {
  kind: 'pipeline_design' | 'pipeline_patch' | 'run_result' | 'explanation' | 'diagrams' | 'noop';
  run?: ConsoleRunResult;
}

interface ConsoleAction {
  id: string;
  type:
    | 'DESIGN_PIPELINE'
    | 'MODIFY_PIPELINE'
    | 'RUN_PIPELINE'
    | 'VIEW_PIPELINE'
    | 'EXPLAIN_PIPELINE'
    | 'SHOW_DIAGRAMS'
    | 'DEBUG_ERROR'
    | 'HELP'
    | 'UNKNOWN'
    | 'NOOP';
  status: 'pending' | 'done' | 'error' | 'skipped';
  error_code?: string | null;
  error_message?: string | null;
  result?: ConsoleActionResult;
}

interface ConsoleResponse {
  version: string;
  intent:
    | 'DESIGN_PIPELINE'
    | 'MODIFY_PIPELINE'
    | 'RUN_PIPELINE'
    | 'EXPLAIN_PIPELINE'
    | 'SHOW_DIAGRAMS'
    | 'DEBUG_ERROR'
    | 'HELP'
    | 'UNKNOWN';
  confidence: number;
  needs_clarification?: boolean;
  clarification_questions?: ConsoleClarificationQuestion[];
  actions?: ConsoleAction[];
  console_messages?: ConsoleMessage[];
  pipeline_summary?: ConsolePipelineSummary | null;
  diagrams?: ConsoleDiagrams | null;
}

const API_CONSOLE_STORAGE_KEY = 'flowmason-api-console-v1';

// Build a simple Mermaid flowchart for a pipeline
function buildMermaidFlowFromPipeline(pipeline: { id: string; name: string; stages?: any[]; output_stage_id?: string }) {
  const stages = Array.isArray(pipeline.stages) ? pipeline.stages : [];
  const stageIds = stages.map((s) => s.id);

  const lines: string[] = ['flowchart TD', '  IN((Input))'];

  stages.forEach((stage) => {
    const label = `${stage.name || stage.id}\\n[${stage.component_type}]`;
    lines.push(`  ${stage.id}["${label}"]`);
  });

  stages.forEach((stage) => {
    const depends = Array.isArray(stage.depends_on) ? stage.depends_on : [];
    if (depends.length > 0) {
      depends.forEach((dep: string) => {
        if (stageIds.includes(dep)) {
          lines.push(`  ${dep} --> ${stage.id}`);
        }
      });
    } else {
      lines.push(`  IN --> ${stage.id}`);
    }
  });

  const outputId = pipeline.output_stage_id;
  if (outputId && stageIds.includes(outputId)) {
    lines.push(`  ${outputId} --> OUT((Output))`);
  }

  return lines.join('\n');
}

// Format JSON for display
function formatJson(data: unknown): string {
  try {
    return JSON.stringify(data, null, 2);
  } catch {
    return String(data);
  }
}

// Collapsible JSON viewer
function JsonViewer({ data, maxHeight = 200 }: { data: unknown; maxHeight?: number }) {
  const [expanded, setExpanded] = useState(false);
  const json = formatJson(data);
  const lines = json.split('\n').length;
  const needsCollapse = lines > 10;

  return (
    <div className="relative">
      <pre
        className={`bg-muted/50 rounded-lg p-3 text-sm overflow-auto font-mono ${
          !expanded && needsCollapse ? 'max-h-40' : ''
        }`}
        style={{ maxHeight: expanded ? undefined : maxHeight }}
      >
        {json}
      </pre>
      {needsCollapse && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="absolute bottom-2 right-2 text-xs text-primary hover:underline flex items-center gap-1"
        >
          {expanded ? (
            <>
              <ChevronDown className="h-3 w-3" /> Show less
            </>
          ) : (
            <>
              <ChevronRight className="h-3 w-3" /> Show more ({lines} lines)
            </>
          )}
        </button>
      )}
    </div>
  );
}

// Stage execution display
function StageList({ stages }: { stages: StageExecution[] }) {
  return (
    <div className="space-y-1 my-2">
      {stages.map((stage) => (
        <div
          key={stage.id}
          className="flex items-center gap-2 text-sm py-1 px-2 rounded bg-muted/30"
        >
          {stage.status === 'completed' && <CheckCircle className="h-4 w-4 text-green-500" />}
          {stage.status === 'failed' && <XCircle className="h-4 w-4 text-red-500" />}
          {stage.status === 'running' && <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />}
          {stage.status === 'pending' && <Clock className="h-4 w-4 text-gray-400" />}
          <span className="flex-1">{stage.name || stage.id}</span>
          {stage.duration !== undefined && (
            <span className="text-muted-foreground text-xs">{stage.duration}ms</span>
          )}
        </div>
      ))}
    </div>
  );
}

// Message bubble component
function MessageBubble({ message, onCopy }: { message: Message; onCopy: (text: string) => void }) {
  const isUser = message.type === 'user';
  const isError = message.type === 'error';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[85%] rounded-lg p-3 ${
          isUser
            ? 'bg-primary text-primary-foreground'
            : isError
            ? 'bg-red-500/10 border border-red-500/20'
            : 'bg-muted'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between gap-4 mb-1">
          <span className="text-xs opacity-70 flex items-center gap-1">
            {isUser ? (
              'You'
            ) : (
              <>
                <Sparkles className="h-3 w-3" /> FlowMason
              </>
            )}
          </span>
          <span className="text-xs opacity-50">
            {message.timestamp.toLocaleTimeString()}
          </span>
        </div>

        {/* Content */}
        <div className="whitespace-pre-wrap text-[0.95rem]">
          {message.content.split('\n').map((line, idx) => {
            const match = line.match(/Open in Studio: (\/pipelines\/\S+)/);
            if (match) {
              const path = match[1];
              return (
                <div key={idx}>
                  <span>Open in Studio: </span>
                  <Link to={path} className="underline text-primary hover:text-primary-600">
                    {path}
                  </Link>
                </div>
              );
            }
            return <div key={idx}>{line}</div>;
          })}
        </div>

        {/* Stage executions */}
        {message.stages && message.stages.length > 0 && (
          <StageList stages={message.stages} />
        )}

        {/* Data output */}
        {message.data !== undefined && (
          <div className="mt-2">
            <JsonViewer data={message.data} />
            <div className="flex gap-2 mt-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onCopy(formatJson(message.data))}
              >
                <Copy className="h-3 w-3 mr-1" /> Copy
              </Button>
            </div>
          </div>
        )}

        {/* Duration */}
        {message.duration !== undefined && (
          <div className="mt-2 text-xs opacity-70">
            Completed in {message.duration}ms
          </div>
        )}
      </div>
    </div>
  );
}

// Quick action buttons
function QuickActions({
  onAction,
  pipelines,
}: {
  onAction: (command: string) => void;
  pipelines: Pipeline[];
}) {
  const [showPipelines, setShowPipelines] = useState(false);

  return (
    <div className="flex flex-wrap gap-2 p-2 border-t">
      <div className="relative">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowPipelines(!showPipelines)}
        >
          <Play className="h-3 w-3 mr-1" /> Run Pipeline
          <ChevronDown className="h-3 w-3 ml-1" />
        </Button>
        {showPipelines && (
          <div className="absolute bottom-full mb-1 left-0 bg-popover border rounded-lg shadow-lg p-1 min-w-48 z-10">
            {pipelines.length > 0 ? (
              pipelines.map((p) => (
                <button
                  key={p.id}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-muted rounded"
                  onClick={() => {
                    onAction(`run ${p.name}`);
                    setShowPipelines(false);
                  }}
                >
                  {p.name}
                  <span className="text-xs text-muted-foreground ml-2">v{p.version}</span>
                </button>
              ))
            ) : (
              <div className="px-3 py-2 text-sm text-muted-foreground">No pipelines available</div>
            )}
          </div>
        )}
      </div>
      <Button variant="outline" size="sm" onClick={() => onAction('pipelines')}>
        <List className="h-3 w-3 mr-1" /> List Pipelines
      </Button>
      <Button variant="outline" size="sm" onClick={() => onAction('health')}>
        <Heart className="h-3 w-3 mr-1" /> Health
      </Button>
      <Button variant="outline" size="sm" onClick={() => onAction('components')}>
        <Box className="h-3 w-3 mr-1" /> Components
      </Button>
    </div>
  );
}

// Parse and execute commands
async function executeCommand(
  command: string,
  addMessage: (msg: Omit<Message, 'id' | 'timestamp'>) => void,
  options?: {
    onClarification?: (payload: {
      message: string;
      questions: ConsoleClarificationQuestion[];
      pipelineId?: string;
    }) => void;
    pipelineId?: string | null;
    onPipelineSummary?: (pipelineId?: string) => void;
  }
): Promise<void> {
  const cmd = command.trim().toLowerCase();
  const parts = command.trim().split(/\s+/);
  const action = parts[0].toLowerCase();

  try {
    // Health check
    if (cmd === 'health' || cmd === 'status') {
      const response = await fetch('/health');
      const data = await response.json();
      addMessage({
        type: 'result',
        content: `Studio is ${data.status === 'healthy' ? '✓ healthy' : '✗ unhealthy'}`,
        data,
      });
      return;
    }

    // List pipelines
    if (cmd === 'pipelines' || cmd === 'list pipelines' || cmd === 'ls') {
      const response = await fetch('/api/v1/pipelines');
      const data = await response.json();
      const list = Array.isArray(data.items)
        ? data.items
        : Array.isArray(data.pipelines)
        ? data.pipelines
        : Array.isArray(data)
        ? data
        : [];
      addMessage({
        type: 'result',
        content: `Found ${list.length} pipeline(s):`,
        data: list.map((p: Pipeline) => ({ name: p.name, version: p.version, id: p.id })),
      });
      return;
    }

    // List components
    if (cmd === 'components' || cmd === 'list components') {
      const response = await fetch('/api/v1/registry/components');
      const data = await response.json();
      const components = Array.isArray(data.components)
        ? data.components
        : Array.isArray(data)
        ? data
        : [];
      const grouped: Record<string, string[]> = {};
      components.forEach((c: Component) => {
        const cat = c.category || 'other';
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(c.name);
      });
      addMessage({
        type: 'result',
        content: `Found ${components.length} component(s):`,
        data: grouped,
      });
      return;
    }

    // Run pipeline
    if (action === 'run') {
      const pipelineName = parts.slice(1).join(' ').split('{')[0].trim();

      // Extract JSON input if provided
      let inputs = {};
      const jsonMatch = command.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        try {
          inputs = JSON.parse(jsonMatch[0]);
        } catch {
          addMessage({
            type: 'error',
            content: 'Invalid JSON input. Use format: run pipeline-name {"key": "value"}',
          });
          return;
        }
      }

      // Find pipeline
      const pipelinesRes = await fetch('/api/v1/pipelines');
      const pipelinesData = await pipelinesRes.json();
      const list = Array.isArray(pipelinesData.items)
        ? pipelinesData.items
        : Array.isArray(pipelinesData.pipelines)
        ? pipelinesData.pipelines
        : Array.isArray(pipelinesData)
        ? pipelinesData
        : [];
      const pipeline = list.find(
        (p: Pipeline) =>
          p.name.toLowerCase() === pipelineName.toLowerCase() ||
          p.id === pipelineName
      );

      if (!pipeline) {
        addMessage({
          type: 'error',
          content: `Pipeline "${pipelineName}" not found. Use 'pipelines' to list available pipelines.`,
        });
        return;
      }

      addMessage({
        type: 'system',
        content: `Running pipeline: ${pipeline.name}...`,
      });

      // Execute pipeline
      const startTime = Date.now();
      const runRes = await fetch(`/api/v1/pipelines/${pipeline.id}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sample_input: inputs,
        }),
      });

      const result = await runRes.json();
      const duration = Date.now() - startTime;

      if (runRes.ok && result.is_success) {
        // Build stage list from debug_info if available
        const stageDetails = (result.debug_info?.stages ?? []) as any[];
        const stages: StageExecution[] = stageDetails.map((s) => ({
          id: s.stage_id,
          name: s.stage_name || s.stage_id,
          status:
            s.status === 'success' || s.status === 'completed'
              ? 'completed'
              : s.status === 'failed'
              ? 'failed'
              : 'pending',
          duration: s.duration_ms,
        }));

        addMessage({
          type: 'result',
          content: `✓ Pipeline completed successfully`,
          stages,
          data: result.result,
          duration,
        });
      } else {
        addMessage({
          type: 'error',
          content: `✗ Pipeline failed: ${result.error || result.message || 'Unknown error'}`,
          data: result,
          duration,
        });
      }
      return;
    }

    // Diagram: show Mermaid flowchart for a pipeline
    if (action === 'diagram') {
      const pipelineName = parts.slice(1).join(' ').trim();
      if (!pipelineName) {
        addMessage({
          type: 'error',
          content: 'Usage: diagram <pipeline-name-or-id>',
        });
        return;
      }

      const pipelinesRes = await fetch('/api/v1/pipelines');
      const pipelinesData = await pipelinesRes.json();
      const list = Array.isArray(pipelinesData.items)
        ? pipelinesData.items
        : Array.isArray(pipelinesData.pipelines)
        ? pipelinesData.pipelines
        : Array.isArray(pipelinesData)
        ? pipelinesData
        : [];
      const pipeline = list.find(
        (p: Pipeline) =>
          p.name.toLowerCase() === pipelineName.toLowerCase() ||
          p.id === pipelineName
      );

      if (!pipeline) {
        addMessage({
          type: 'error',
          content: `Pipeline "${pipelineName}" not found. Use 'pipelines' to list available pipelines.`,
        });
        return;
      }

      const mermaid = buildMermaidFlowFromPipeline(pipeline as any);
      addMessage({
        type: 'result',
        content: `Mermaid flow for ${pipeline.name}:\n\`\`\`mermaid\n${mermaid}\n\`\`\``,
      });
      return;
    }

    // Explain: structural explanation of a pipeline
    if (action === 'explain') {
      const pipelineName = parts.slice(1).join(' ').trim();
      if (!pipelineName) {
        addMessage({
          type: 'error',
          content: 'Usage: explain <pipeline-name-or-id>',
        });
        return;
      }

      const pipelinesRes = await fetch('/api/v1/pipelines');
      const pipelinesData = await pipelinesRes.json();
      const list = Array.isArray(pipelinesData.items)
        ? pipelinesData.items
        : Array.isArray(pipelinesData.pipelines)
        ? pipelinesData.pipelines
        : Array.isArray(pipelinesData)
        ? pipelinesData
        : [];
      const pipeline = list.find(
        (p: Pipeline) =>
          p.name.toLowerCase() === pipelineName.toLowerCase() ||
          p.id === pipelineName
      );

      if (!pipeline) {
        addMessage({
          type: 'error',
          content: `Pipeline "${pipelineName}" not found. Use 'pipelines' to list available pipelines.`,
        });
        return;
      }

      const explainRes = await fetch(`/api/v1/pipelines/${pipeline.id}/explain`);
      if (!explainRes.ok) {
        const err = await explainRes.json().catch(() => ({}));
        addMessage({
          type: 'error',
          content: `Failed to explain pipeline: ${err.detail || explainRes.statusText}`,
        });
        return;
      }
      const explainData = await explainRes.json();
      const contentLines: string[] = [];
      contentLines.push(explainData.explanation);
      if (explainData.mermaid_flow) {
        contentLines.push('');
        contentLines.push('Mermaid flowchart:');
        contentLines.push('```mermaid');
        contentLines.push(explainData.mermaid_flow);
        contentLines.push('```');
      }

      addMessage({
        type: 'system',
        content: contentLines.join('\n'),
      });
      return;
    }

    // View: unified views (JSON + explanation + Mermaid) for a pipeline
    if (action === 'view') {
      const pipelineName = parts.slice(1).join(' ').trim();
      if (!pipelineName) {
        addMessage({
          type: 'error',
          content: 'Usage: view <pipeline-name-or-id>',
        });
        return;
      }

      const pipelinesRes = await fetch('/api/v1/pipelines');
      const pipelinesData = await pipelinesRes.json();
      const list = Array.isArray(pipelinesData.items)
        ? pipelinesData.items
        : Array.isArray(pipelinesData.pipelines)
        ? pipelinesData.pipelines
        : Array.isArray(pipelinesData)
        ? pipelinesData
        : [];
      const pipeline = list.find(
        (p: Pipeline) =>
          p.name.toLowerCase() === pipelineName.toLowerCase() ||
          p.id === pipelineName
      );

      if (!pipeline) {
        addMessage({
          type: 'error',
          content: `Pipeline "${pipelineName}" not found. Use 'pipelines' to list available pipelines.`,
        });
        return;
      }

      const viewsRes = await fetch(`/api/v1/pipelines/${pipeline.id}/views`);
      if (!viewsRes.ok) {
        const err = await viewsRes.json().catch(() => ({}));
        addMessage({
          type: 'error',
          content: `Failed to load pipeline views: ${err.detail || viewsRes.statusText}`,
          data: err,
        });
        return;
      }

      const views = await viewsRes.json();
      const mermaid = views.mermaid_flow;
      const explanation = views.explanation;
      const detail = views.pipeline;

      const lines: string[] = [];
      lines.push(explanation);
      if (mermaid) {
        lines.push('');
        lines.push('Mermaid flowchart:');
        lines.push('```mermaid');
        lines.push(mermaid);
        lines.push('```');
      }

      addMessage({
        type: 'system',
        content: lines.join('\n'),
        data: detail,
      });
      return;
    }

    // Direct API call (GET /path or POST /path {...})
    if (action === 'get' || action === 'post' || action === 'put' || action === 'delete') {
      const method = action.toUpperCase();
      const path = parts[1];

      if (!path) {
        addMessage({
          type: 'error',
          content: `Usage: ${action} /api/path [{"json": "body"}]`,
        });
        return;
      }

      let body: string | undefined;
      if (method !== 'GET') {
        const jsonMatch = command.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          body = jsonMatch[0];
        }
      }

      const response = await fetch(path, {
        method,
        headers: body ? { 'Content-Type': 'application/json' } : undefined,
        body,
      });

      const data = await response.json().catch(() => response.text());

      addMessage({
        type: response.ok ? 'result' : 'error',
        content: `${method} ${path} → ${response.status} ${response.statusText}`,
        data,
      });
      return;
    }

    // Help
    if (cmd === 'help' || cmd === '?') {
      addMessage({
        type: 'system',
        content: `Available commands:

• health - Check studio health
• pipelines - List all pipelines
• components - List all components
• run <pipeline> [{"inputs": ...}] - Run a pipeline
• view <pipeline> - Show explanation + Mermaid + JSON
• debug <pipeline> - Summarize recent failures
• GET /api/path - Make GET request
• POST /api/path {"body": ...} - Make POST request
• clear - Clear console
• help - Show this help`,
      });
      return;
    }

    // Unknown command: first try AI Console (v1).
    // We no longer fall back to the legacy /natural/run endpoint here;
    // all natural-language behaviour is routed through the AI console.
    try {
      const body: any = {
        version: 'v1',
        message: command,
      };
      if (options?.pipelineId) {
        body.context = { pipeline_id: options.pipelineId };
      }

      const aiRes = await fetch('/api/v1/console/ai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (aiRes.ok) {
        const aiData: ConsoleResponse = await aiRes.json();

        // Render console messages from AI console
        (aiData.console_messages || []).forEach((m) => {
          addMessage({
            type: m.role === 'user' ? 'user' : 'system',
            content: m.content,
          });
        });

        // Track the current pipeline (if any) so later modifications
        // can be applied in context.
        if (aiData.pipeline_summary?.pipeline_id && options?.onPipelineSummary) {
          options.onPipelineSummary(aiData.pipeline_summary.pipeline_id);
        }

        // If a pipeline summary and diagram are available, show them as a result block
        if (aiData.pipeline_summary && aiData.diagrams?.flowchart) {
          const openUrl = `/pipelines/${aiData.pipeline_summary.pipeline_id}`;
          addMessage({
            type: 'result',
            content: `Mermaid flow for ${aiData.pipeline_summary.name}:\n\`\`\`mermaid\n${aiData.diagrams.flowchart}\n\`\`\`\n\nOpen in Studio: ${openUrl}`,
          });
        }

        // If AI console needs clarification, enter clarification mode
        if (
          aiData.needs_clarification &&
          aiData.clarification_questions &&
          aiData.clarification_questions.length > 0
        ) {
          // Let the caller decide how to enter clarification mode
          options?.onClarification?.({
            message: command,
            questions: aiData.clarification_questions,
            pipelineId: aiData.pipeline_summary?.pipeline_id,
          });

          const firstQuestion = aiData.clarification_questions[0];
          addMessage({
            type: 'system',
            content: `I need a bit more information: ${firstQuestion.question}`,
          });
          return;
        }

        // If AI console already executed a run, show results
        const actionRes = aiData.actions && aiData.actions[0];
        const runResult =
          actionRes && actionRes.result && actionRes.result.kind === 'run_result'
            ? actionRes.result.run
            : undefined;
        if (runResult) {
          const stageExecutions: StageExecution[] = runResult.stage_results.map((s) => ({
            id: s.stage_id,
            name: s.stage_id,
            status:
              s.status === 'completed' || s.status === 'success'
                ? 'completed'
                : s.status === 'failed'
                ? 'failed'
                : s.status === 'running'
                ? 'running'
                : 'pending',
            duration: s.duration_ms ?? undefined,
            output: s.output_preview,
          }));

          addMessage({
            type: 'result',
            content: `AI Console run of pipeline "${runResult.pipeline_id}" completed.`,
            stages: stageExecutions,
            data: {
              inputs_used: runResult.inputs_used,
              final_output: runResult.final_output,
            },
          });
        }

        // For HELP/EXPLAIN/SHOW_DIAGRAMS/DESIGN/DEBUG/VIEW intents, the
        // messages above are the final output; no further fallback.
        return;
      }
    } catch (err) {
      addMessage({
        type: 'error',
        content: `AI console error: ${
          err instanceof Error ? err.message : 'Unknown error'
        }`,
      });
      return;
    }
  } catch (error) {
    addMessage({
      type: 'error',
      content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
    });
  }
}

// Main API Console component
export function ApiConsolePage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const messageIdRef = useRef(0);
  const [interactiveRun, setInteractiveRun] = useState<{
    pipeline: Pipeline;
    fields: string[];
    currentIndex: number;
    inputs: Record<string, unknown>;
  } | null>(null);
  const [currentPipelineId, setCurrentPipelineId] = useState<string | null>(null);
  const [clarification, setClarification] = useState<{
    message: string;
    questions: ConsoleClarificationQuestion[];
    currentIndex: number;
    answers: Record<string, unknown>;
    pipelineId?: string;
  } | null>(null);

  const currentClarificationQuestion =
    clarification && clarification.questions[clarification.currentIndex];

  // Rehydrate console state from session storage so that navigating
  // away and back does not lose the conversation.
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(API_CONSOLE_STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw) as {
        messages?: Array<Omit<Message, 'timestamp'> & { timestamp: string }>;
        currentPipelineId?: string | null;
      };
      if (Array.isArray(parsed.messages) && parsed.messages.length > 0) {
        const rehydrated: Message[] = parsed.messages.map((m) => ({
          ...m,
          timestamp: new Date(m.timestamp),
        }));
        setMessages(rehydrated);
      }
      if (parsed.currentPipelineId) {
        setCurrentPipelineId(parsed.currentPipelineId);
      }
    } catch {
      // ignore parse errors
    }
  }, []);

  // Persist console state on every change so we can restore it later.
  useEffect(() => {
    try {
      const payload = JSON.stringify({ messages, currentPipelineId });
      sessionStorage.setItem(API_CONSOLE_STORAGE_KEY, payload);
    } catch {
      // ignore storage errors
    }
  }, [messages, currentPipelineId]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Fetch pipelines for quick actions
  useEffect(() => {
    fetch('/api/v1/pipelines')
      .then((r) => r.json())
      .then((data) => {
        const list = Array.isArray(data.items)
          ? data.items
          : Array.isArray(data.pipelines)
          ? data.pipelines
          : Array.isArray(data)
          ? data
          : [];
        setPipelines(list);
      })
      .catch(() => {});
  }, []);

  // Add welcome message when there is no prior session
  useEffect(() => {
    const hasStored = !!sessionStorage.getItem(API_CONSOLE_STORAGE_KEY);
    if (hasStored) return;
    if (messages.length === 0) {
      setMessages([
        {
          id: '0',
          type: 'system',
          content: `Welcome to FlowMason API Console!

Type commands to interact with the API:
• pipelines - List pipelines
• run <pipeline> - Execute a pipeline
• health - Check studio status
• help - Show all commands`,
          timestamp: new Date(),
        },
      ]);
    }
  }, [messages.length]);

  const addMessage = useCallback((msg: Omit<Message, 'id' | 'timestamp'>) => {
    const id = `${Date.now()}-${messageIdRef.current++}`;
    setMessages((prev) => [
      ...prev,
      {
        ...msg,
        id,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const command = input.trim();
    if (!command) return;

    // Clarification mode for AI console: treat input as answer to the next question
    if (clarification) {
      const { message, questions, currentIndex, answers, pipelineId } = clarification;
      const question = questions[currentIndex];

       // Echo the user's clarification answer in the conversation so the
       // flow feels like a normal chat exchange.
       addMessage({
         type: 'user',
         content: command,
       });

      // Try to parse as JSON for non-string types; otherwise keep as string
      let value: unknown = command;
      try {
        const trimmed = command.trim();
        if (
          question.expected_type !== 'string' &&
          ((trimmed.startsWith('{') && trimmed.endsWith('}')) ||
            (trimmed.startsWith('[') && trimmed.endsWith(']')) ||
            trimmed === 'true' ||
            trimmed === 'false' ||
            !Number.isNaN(Number(trimmed)))
        ) {
          value = JSON.parse(trimmed);
        }
      } catch {
        // keep as string
      }

      const newAnswers = { ...answers, [question.id]: value };
      const nextIndex = currentIndex + 1;

      setInput('');

      if (nextIndex < questions.length) {
        const nextQuestion = questions[nextIndex];
        setClarification({
          message,
          questions,
          currentIndex: nextIndex,
          answers: newAnswers,
          pipelineId,
        });
        addMessage({
          type: 'system',
          content: `Got it. ${nextQuestion.question}`,
        });
        return;
      }

      // All clarification answers collected: call AI console again with the answers
      setClarification(null);
      setLoading(true);
      addMessage({
        type: 'system',
        content: 'Thanks, running with your answers...',
      });

      try {
        const body: any = {
          version: 'v1',
          message,
          clarification_answers: newAnswers,
        };
        if (pipelineId) {
          body.context = { pipeline_id: pipelineId };
        }

        const aiRes = await fetch('/api/v1/console/ai', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });

        if (aiRes.ok) {
          const aiData: ConsoleResponse = await aiRes.json();

          // Render console messages
          (aiData.console_messages || []).forEach((m) => {
            addMessage({
              type: m.role === 'user' ? 'user' : 'system',
              content: m.content,
            });
          });

          // Show diagram if available
          if (aiData.pipeline_summary && aiData.diagrams?.flowchart) {
            addMessage({
              type: 'result',
              content: `Mermaid flow for ${aiData.pipeline_summary.name}:\n\`\`\`mermaid\n${aiData.diagrams.flowchart}\n\`\`\``,
            });
          }

          // Show run results if present
          const action = aiData.actions && aiData.actions[0];
          const runResult =
            action && action.result && action.result.kind === 'run_result'
              ? action.result.run
              : undefined;

          if (runResult) {
            const stageExecutions: StageExecution[] = runResult.stage_results.map((s) => ({
              id: s.stage_id,
              name: s.stage_id,
              status:
                s.status === 'completed' || s.status === 'success'
                  ? 'completed'
                  : s.status === 'failed'
                  ? 'failed'
                  : s.status === 'running'
                  ? 'running'
                  : 'pending',
              duration: s.duration_ms ?? undefined,
              output: s.output_preview,
            }));

            addMessage({
              type: 'result',
              content: `AI Console run of pipeline "${runResult.pipeline_id}" completed.`,
              stages: stageExecutions,
              data: {
                inputs_used: runResult.inputs_used,
                final_output: runResult.final_output,
              },
            });
          }
        } else {
          const err = await aiRes.json().catch(() => ({}));
          addMessage({
            type: 'error',
            content: `AI console error: ${err.detail || aiRes.statusText}`,
            data: err,
          });
        }
      } catch (err) {
        addMessage({
          type: 'error',
          content: `Error completing AI console run: ${
            err instanceof Error ? err.message : 'Unknown error'
          }`,
        });
      } finally {
        setLoading(false);
        inputRef.current?.focus();
      }
      return;
    }

    // Interactive run mode: treat input as answer for next field
    if (interactiveRun) {
      const { pipeline, fields, currentIndex, inputs } = interactiveRun;
      const fieldName = fields[currentIndex];

      // Try to parse as JSON, otherwise keep as string
      let value: unknown = command;
      try {
        const trimmed = command.trim();
        if (
          (trimmed.startsWith('{') && trimmed.endsWith('}')) ||
          (trimmed.startsWith('[') && trimmed.endsWith(']')) ||
          trimmed === 'true' ||
          trimmed === 'false' ||
          !Number.isNaN(Number(trimmed))
        ) {
          value = JSON.parse(trimmed);
        }
      } catch {
        // keep as string
      }

      const newInputs = { ...inputs, [fieldName]: value };
      const nextIndex = currentIndex + 1;

      setInput('');

      if (nextIndex < fields.length) {
        const nextField = fields[nextIndex];
        setInteractiveRun({
          pipeline,
          fields,
          currentIndex: nextIndex,
          inputs: newInputs,
        });
        addMessage({
          type: 'system',
          content: `Got value for "${fieldName}". Please provide value for "${nextField}":`,
        });
        return;
      }

      // All fields collected: run pipeline with inputs
      setInteractiveRun(null);
      setLoading(true);
      addMessage({
        type: 'system',
        content: `Running pipeline "${pipeline.name}" with collected inputs...`,
      });

      try {
        // Reuse the existing 'run' command path by constructing a synthetic command
        const syntheticCommand = `run ${pipeline.id} ${JSON.stringify(newInputs)}`;
        await executeCommand(syntheticCommand, addMessage, {
          onClarification: ({ message, questions, pipelineId }) =>
            setClarification({
              message,
              questions,
              currentIndex: 0,
              answers: {},
              pipelineId,
            }),
          pipelineId: currentPipelineId,
          onPipelineSummary: (id) => setCurrentPipelineId(id || null),
        });
      } finally {
        setLoading(false);
        inputRef.current?.focus();
      }
      return;
    }

    // Handle clear command locally
    if (command.toLowerCase() === 'clear') {
      setMessages([]);
      setInput('');
      return;
    }

    // Interactive "runi" command: run pipeline with guided inputs
    const lower = command.toLowerCase();
    if (lower.startsWith('runi ')) {
      const parts = command.trim().split(/\s+/);
      const pipelineName = parts.slice(1).join(' ').trim();
      if (!pipelineName) {
        addMessage({
          type: 'error',
          content: 'Usage: runi <pipeline-name-or-id>',
        });
        setInput('');
        return;
      }

      setInput('');
      setLoading(true);
      addMessage({ type: 'user', content: command });

      try {
        // Find pipeline
        const pipelinesRes = await fetch('/api/v1/pipelines');
        const pipelinesData = await pipelinesRes.json();
        const list = Array.isArray(pipelinesData.items)
          ? pipelinesData.items
          : Array.isArray(pipelinesData.pipelines)
          ? pipelinesData.pipelines
          : Array.isArray(pipelinesData)
          ? pipelinesData
          : [];
        const pipeline = list.find(
          (p: Pipeline) =>
            p.name.toLowerCase() === pipelineName.toLowerCase() ||
            p.id === pipelineName
        );

        if (!pipeline) {
          addMessage({
            type: 'error',
            content: `Pipeline "${pipelineName}" not found. Use 'pipelines' to list available pipelines.`,
          });
          setLoading(false);
          return;
        }

        // Fetch full pipeline detail to get input_schema
        const detailRes = await fetch(`/api/v1/pipelines/${pipeline.id}`);
        const detail = await detailRes.json();
        const schema = detail.input_schema || {};
        const required: string[] = Array.isArray(schema.required) ? schema.required : [];
        const properties = schema.properties || {};
        const fields =
          required.length > 0 ? required : Object.keys(properties ?? {});

        if (!fields || fields.length === 0) {
          addMessage({
            type: 'system',
            content: `Pipeline "${pipeline.name}" has no declared input fields; running without inputs...`,
          });
          const syntheticCommand = `run ${pipeline.id}`;
          await executeCommand(syntheticCommand, addMessage, {
            onClarification: ({ message, questions, pipelineId }) =>
              setClarification({
                message,
                questions,
                currentIndex: 0,
                answers: {},
                pipelineId,
              }),
            pipelineId: currentPipelineId,
            onPipelineSummary: (id) => setCurrentPipelineId(id || null),
          });
          setLoading(false);
          inputRef.current?.focus();
          return;
        }

        setInteractiveRun({
          pipeline,
          fields,
          currentIndex: 0,
          inputs: {},
        });

        const firstField = fields[0];
        const fieldSchema = properties[firstField] || {};
        const typeHint = fieldSchema.type ? ` (type: ${fieldSchema.type})` : '';
        const descriptionHint = fieldSchema.description
          ? ` - ${fieldSchema.description}`
          : '';

        addMessage({
          type: 'system',
          content: `Interactive run for "${pipeline.name}". Please provide value for "${firstField}"${typeHint}${descriptionHint}:`,
        });
      } catch (err) {
        addMessage({
          type: 'error',
          content: `Error starting interactive run: ${
            err instanceof Error ? err.message : 'Unknown error'
          }`,
        });
      } finally {
        setLoading(false);
        inputRef.current?.focus();
      }
      return;
    }

    // Normal command path
    addMessage({ type: 'user', content: command });
    setInput('');
    setLoading(true);

    await executeCommand(command, addMessage, {
      onClarification: ({ message, questions, pipelineId }) =>
        setClarification({
          message,
          questions,
          currentIndex: 0,
          answers: {},
          pipelineId,
        }),
      pipelineId: currentPipelineId,
      onPipelineSummary: (id) => setCurrentPipelineId(id || null),
    });
    setLoading(false);
    inputRef.current?.focus();
  };

  const handleQuickAction = (command: string) => {
    setInput(command);
    setTimeout(() => handleSubmit(), 0);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Terminal className="h-5 w-5" />
          API Console
        </h1>
        <p className="text-sm text-muted-foreground">
          Interactive API testing and pipeline execution
        </p>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-auto p-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} onCopy={copyToClipboard} />
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Processing...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick actions */}
      <QuickActions onAction={handleQuickAction} pipelines={pipelines} />

      {/* Clarification suggestions (if any) */}
      {currentClarificationQuestion?.choices &&
        currentClarificationQuestion.choices.length > 0 && (
          <div className="px-4 pb-2 flex flex-wrap items-center gap-2 border-t bg-muted/30">
            <span className="text-xs text-muted-foreground">Suggested answers:</span>
            {currentClarificationQuestion.choices.map((choice) => (
              <button
                key={choice.value}
                type="button"
                className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary hover:bg-primary/20"
                onClick={() => {
                  setInput(choice.value);
                  setTimeout(() => {
                    void handleSubmit();
                  }, 0);
                }}
              >
                {choice.label ?? choice.value}
              </button>
            ))}
          </div>
        )}

      {/* Input area */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a command or question..."
            disabled={loading}
            className="flex-1"
            autoFocus
          />
          <Button type="submit" disabled={loading || !input.trim()}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => setMessages([])}
            title="Clear console"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  );
}
