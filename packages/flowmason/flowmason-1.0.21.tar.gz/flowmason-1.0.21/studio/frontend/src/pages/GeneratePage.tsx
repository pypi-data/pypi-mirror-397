/**
 * AI Pipeline Generation Page
 *
 * Interactive interface for generating pipelines from natural language descriptions.
 * Uses LLM to understand user intent and generate valid FlowMason pipeline JSON.
 */

import { useState, useCallback } from 'react';
import {
  Wand2,
  Sparkles,
  RefreshCw,
  Download,
  Copy,
  Check,
  ChevronRight,
  Loader2,
  AlertCircle,
  Info,
  Lightbulb,
  Code,
  FileJson,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useNavigate } from 'react-router-dom';

// Example prompts for quick start
const EXAMPLE_PROMPTS = [
  {
    title: 'Data Validation',
    description: 'Validate incoming JSON records against a schema',
    prompt: 'Create a pipeline that takes a list of customer records, validates each one has required fields (id, email, name), filters out invalid records, and outputs a summary with valid/invalid counts.',
  },
  {
    title: 'Content Triage',
    description: 'Classify and route support tickets',
    prompt: 'Build a pipeline that takes a support ticket text, uses AI to classify its priority (low/medium/high) and category (billing/technical/general), then routes it to the appropriate output based on priority.',
  },
  {
    title: 'Data Transformation',
    description: 'Transform and enrich API data',
    prompt: 'Create a pipeline that fetches data from an API endpoint, transforms the response to extract specific fields, filters for active items only, and formats the output as a report.',
  },
  {
    title: 'Batch Processing',
    description: 'Process items in parallel with aggregation',
    prompt: 'Build a pipeline that takes a list of items, processes each one through an AI summarizer using a foreach loop, then aggregates all summaries into a final report.',
  },
];

// Pipeline structure for preview
interface GeneratedPipeline {
  name: string;
  version: string;
  description: string;
  input_schema: {
    type: string;
    properties: Record<string, unknown>;
    required?: string[];
  };
  stages: Array<{
    id: string;
    name: string;
    component_type: string;
    config: Record<string, unknown>;
    depends_on: string[];
    rationale?: string;
  }>;
  output_stage_id: string;
  is_fallback?: boolean;
}

interface GenerationAnalysis {
  intent: string;
  actions: string[];
  data_sources: string[];
  outputs: string[];
  constraints: string[];
  ambiguities: string[];
  suggested_patterns?: string[];
  _generation_status?: string;
  _generation_error?: string | null;
  _validation_errors?: string[];
  _validation_warnings?: string[];
  _interpreter_used?: boolean;
  _interpreter_error?: string | null;
  _pipeline_source?: string;
  _is_fallback_pipeline?: boolean;
  _dry_run_summary?: {
    stage_count: number;
    uses_llm: boolean;
    uses_external_io: boolean;
    estimated_complexity: string;
  } | null;
}

type PreviewView = 'flow' | 'sequence' | 'structure' | 'json' | 'mermaid';
type StageChangeKind = 'added' | 'removed' | 'modified';

export function GeneratePage() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedPipeline, setGeneratedPipeline] = useState<GeneratedPipeline | null>(null);
  const [copied, setCopied] = useState(false);
  const [useAiInterpreter, setUseAiInterpreter] = useState(true);
  const [dryRunOnly, setDryRunOnly] = useState(false);
  const [analysis, setAnalysis] = useState<GenerationAnalysis | null>(null);
  const [feedbackSending, setFeedbackSending] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState<null | -1 | 1>(null);
  const [previewView, setPreviewView] = useState<PreviewView>('flow');
  const [refineStageId, setRefineStageId] = useState<string | null>(null);
  const [refineText, setRefineText] = useState('');
  const [refining, setRefining] = useState(false);
  const [stageChanges, setStageChanges] = useState<Record<string, StageChangeKind>>({});
  const [mermaidInput, setMermaidInput] = useState('');

  const computeStageDiff = (
    previous: GeneratedPipeline | null,
    next: GeneratedPipeline | null
  ): Record<string, StageChangeKind> => {
    const changes: Record<string, StageChangeKind> = {};
    if (!previous || !next) return changes;

    const prevById: Record<string, GeneratedPipeline['stages'][number]> = {};
    previous.stages.forEach((s) => {
      prevById[s.id] = s;
    });

    const nextById: Record<string, GeneratedPipeline['stages'][number]> = {};
    next.stages.forEach((s) => {
      nextById[s.id] = s;
    });

    // Added / modified
    next.stages.forEach((s) => {
      const prev = prevById[s.id];
      if (!prev) {
        changes[s.id] = 'added';
      } else {
        const depsChanged =
          prev.depends_on.join(',') !== s.depends_on.join(',');
        const typeChanged = prev.component_type !== s.component_type;
        const configChanged =
          JSON.stringify(prev.config || {}) !== JSON.stringify(s.config || {});
        if (depsChanged || typeChanged || configChanged) {
          changes[s.id] = 'modified';
        }
      }
    });

    // Removed
    previous.stages.forEach((s) => {
      if (!nextById[s.id]) {
        changes[s.id] = 'removed';
      }
    });

    return changes;
  };

  // Generate pipeline from prompt
  const handleGenerate = useCallback(async () => {
    if (!prompt.trim()) return;

    setGenerating(true);
    setError(null);

    try {
      // Call the backend generation endpoint
      const response = await fetch('/api/v1/generate/pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: prompt,
          mermaid: mermaidInput || undefined,
          options: {
            include_validation: true,
            include_logging: true,
            use_ai_interpreter: useAiInterpreter,
            dry_run: dryRunOnly,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || 'Failed to generate pipeline');
      }

      const data = await response.json();
      const nextPipeline = (data.pipeline || data) as GeneratedPipeline;
      const diff = computeStageDiff(generatedPipeline, nextPipeline);
      setStageChanges(diff);
      setGeneratedPipeline(nextPipeline);
      setAnalysis(data.analysis || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');

      // Generate a mock pipeline for demo purposes if API fails
      const mockPipeline = generateMockPipeline(prompt);
      setStageChanges({});
      setGeneratedPipeline(mockPipeline);
      setAnalysis(null);
    } finally {
      setGenerating(false);
    }
  }, [prompt, useAiInterpreter, dryRunOnly, generatedPipeline]);

  const handleRefineStage = useCallback(async () => {
    if (!generatedPipeline || !refineStageId || !refineText.trim()) {
      return;
    }

    const basePrompt = prompt.trim()
      ? prompt.trim()
      : generatedPipeline.description || generatedPipeline.name || 'Refine pipeline';

    const refinementPrompt = `${basePrompt}

Refine the pipeline around stage '${refineStageId}' based on this instruction:
${refineText.trim()}

Return a complete updated pipeline JSON.`;

    setRefining(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/generate/pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: refinementPrompt,
          mermaid: mermaidInput || undefined,
          options: {
            include_validation: true,
            include_logging: true,
            use_ai_interpreter: useAiInterpreter,
            dry_run: dryRunOnly,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || 'Failed to refine pipeline');
      }

      const data = await response.json();
      const nextPipeline = (data.pipeline || data) as GeneratedPipeline;
      const diff = computeStageDiff(generatedPipeline, nextPipeline);
      setStageChanges(diff);
      setGeneratedPipeline(nextPipeline);
      setAnalysis(data.analysis || null);
      setPreviewView('flow');
      setRefineText('');
      setRefineStageId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while refining');
    } finally {
      setRefining(false);
    }
  }, [generatedPipeline, refineStageId, refineText, prompt, useAiInterpreter, dryRunOnly]);

  const handleFeedback = useCallback(
    async (rating: -1 | 1) => {
      if (!generatedPipeline) return;
      setFeedbackSending(true);
      setFeedbackRating(rating);
      try {
        await fetch('/api/v1/generate/pipeline/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            pipeline_name: generatedPipeline.name,
            rating,
            source: 'generate_page',
          }),
        });
      } catch {
        // Ignore feedback failures
      } finally {
        setFeedbackSending(false);
      }
    },
    [generatedPipeline]
  );

  // Generate a simple mock pipeline based on keywords
  const generateMockPipeline = (description: string): GeneratedPipeline => {
    const hasValidation = description.toLowerCase().includes('validat');
    const hasFilter = description.toLowerCase().includes('filter');
    const hasAI = description.toLowerCase().includes('ai') || description.toLowerCase().includes('classify');
    const hasTransform = description.toLowerCase().includes('transform');

    const stages: GeneratedPipeline['stages'] = [];

    // Start with logging
    stages.push({
      id: 'log-start',
      name: 'Log Start',
      component_type: 'logger',
      config: {
        message: 'Pipeline execution started',
        level: 'info',
        data: '{{input}}',
      },
      depends_on: [],
    });

    // Add validation if mentioned
    if (hasValidation) {
      stages.push({
        id: 'validate-input',
        name: 'Validate Input',
        component_type: 'schema_validate',
        config: {
          data: '{{input.data}}',
          json_schema: {
            type: 'object',
            required: ['id'],
            properties: {
              id: { type: 'string' },
            },
          },
          strict: false,
        },
        depends_on: ['log-start'],
      });
    }

    // Add AI classification if mentioned
    if (hasAI) {
      stages.push({
        id: 'classify',
        name: 'AI Classification',
        component_type: 'generator',
        config: {
          prompt: `Analyze and classify: {{${hasValidation ? 'upstream.validate-input.result' : 'input.data'}}}`,
          output_format: { type: 'object', properties: { category: { type: 'string' }, priority: { type: 'string' } } },
        },
        depends_on: [hasValidation ? 'validate-input' : 'log-start'],
      });
    }

    // Add filter if mentioned
    if (hasFilter) {
      const lastStage = stages[stages.length - 1];
      stages.push({
        id: 'filter-data',
        name: 'Filter Data',
        component_type: 'filter',
        config: {
          data: `{{upstream.${lastStage.id}.result}}`,
          condition: "item.get('active', True)",
          filter_mode: 'filter_array',
        },
        depends_on: [lastStage.id],
      });
    }

    // Add transform if mentioned
    if (hasTransform) {
      const lastStage = stages[stages.length - 1];
      stages.push({
        id: 'transform-data',
        name: 'Transform Data',
        component_type: 'json_transform',
        config: {
          data: `{{upstream.${lastStage.id}.result}}`,
          jmespath_expression: '@',
        },
        depends_on: [lastStage.id],
      });
    }

    // Add final logging
    const lastStage = stages[stages.length - 1];
    stages.push({
      id: 'log-complete',
      name: 'Log Complete',
      component_type: 'logger',
      config: {
        message: 'Pipeline execution completed',
        level: 'info',
        data: `{{upstream.${lastStage.id}.result}}`,
      },
      depends_on: [lastStage.id],
    });

    return {
      name: 'Generated Pipeline',
      version: '1.0.0',
      description: description.slice(0, 200),
      input_schema: {
        type: 'object',
        properties: {
          data: { type: 'object', description: 'Input data to process' },
        },
        required: ['data'],
      },
      stages,
      output_stage_id: 'log-complete',
    };
  };

  // Copy pipeline JSON to clipboard
  const handleCopy = useCallback(() => {
    if (generatedPipeline) {
      navigator.clipboard.writeText(JSON.stringify(generatedPipeline, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [generatedPipeline]);

  // Save pipeline and navigate to editor
  const handleSave = useCallback(async () => {
    if (!generatedPipeline) return;

    try {
      const response = await fetch('/api/v1/pipelines', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatedPipeline),
      });

      if (response.ok) {
        const saved = await response.json();
        navigate(`/pipelines/${saved.id}`);
      } else {
        throw new Error('Failed to save pipeline');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save pipeline');
    }
  }, [generatedPipeline, navigate]);

  // Use example prompt
  const handleExampleClick = (example: typeof EXAMPLE_PROMPTS[0]) => {
    setPrompt(example.prompt);
    setGeneratedPipeline(null);
    setError(null);
  };

  const getDownstreamCounts = (pipeline: GeneratedPipeline | null): Record<string, number> => {
    const counts: Record<string, number> = {};
    if (!pipeline) return counts;
    pipeline.stages.forEach((s) => {
      counts[s.id] = 0;
    });
    pipeline.stages.forEach((s) => {
      s.depends_on.forEach((dep) => {
        counts[dep] = (counts[dep] || 0) + 1;
      });
    });
    return counts;
  };

  const renderFlowView = (pipeline: GeneratedPipeline) => {
    const downstreamCounts = getDownstreamCounts(pipeline);
    return (
      <div className="space-y-2 max-h-64 overflow-auto pr-1">
        {pipeline.stages.map((stage) => {
          const isStart = stage.depends_on.length === 0;
          const dependents = downstreamCounts[stage.id] || 0;
          const isJunction = dependents > 1 || stage.depends_on.length > 1;
          const changeKind = stageChanges[stage.id];
          const borderClass =
            changeKind === 'added'
              ? 'border-green-400'
              : changeKind === 'modified'
              ? 'border-amber-400'
              : changeKind === 'removed'
              ? 'border-red-400'
              : 'border-slate-200 dark:border-slate-700';
          const bgClass =
            changeKind === 'added'
              ? 'bg-green-50 dark:bg-green-900/30'
              : changeKind === 'modified'
              ? 'bg-amber-50 dark:bg-amber-900/30'
              : changeKind === 'removed'
              ? 'bg-red-50 dark:bg-red-900/30'
              : 'bg-slate-50 dark:bg-slate-900/40';
          return (
            <div
              key={stage.id}
              className={`rounded-md border ${borderClass} ${bgClass} p-2 text-xs flex flex-col gap-1`}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[11px] px-1.5 py-0.5 rounded bg-slate-200/80 dark:bg-slate-800">
                    {stage.id}
                  </span>
                  <span className="font-medium">{stage.name}</span>
                  <Badge variant="secondary" className="text-[10px] px-1 py-0">
                    {stage.component_type}
                  </Badge>
                  {isStart && (
                    <Badge variant="outline" className="text-[10px] px-1 py-0">
                      start
                    </Badge>
                  )}
                  {dependents === 0 && (
                    <Badge variant="outline" className="text-[10px] px-1 py-0">
                      end
                    </Badge>
                  )}
                  {changeKind && (
                    <Badge
                      variant="outline"
                      className="text-[10px] px-1 py-0"
                    >
                      {changeKind}
                    </Badge>
                  )}
                </div>
              </div>
              <div className="flex items-center justify-between gap-2">
                <div className="text-[11px] text-muted-foreground">
                  depends on:{' '}
                  {stage.depends_on.length > 0 ? stage.depends_on.join(', ') : 'none'}
                </div>
                {isJunction && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-[11px] h-6"
                    onClick={() => {
                      setRefineStageId(stage.id);
                      setPreviewView('flow');
                    }}
                  >
                    <Sparkles className="w-3 h-3 mr-1" />
                    AI refine here
                  </Button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderSequenceView = (pipeline: GeneratedPipeline) => {
    return (
      <div className="space-y-1 max-h-64 overflow-auto pr-1 text-xs">
        <div className="flex items-center gap-4 text-[11px] font-medium text-muted-foreground mb-1">
          <span className="w-24 text-right">Pipeline</span>
          <span className="flex-1">→ Component</span>
        </div>
        {pipeline.stages.map((stage, idx) => (
          <div key={stage.id} className="flex items-start gap-4">
            <span className="w-24 text-right text-[11px] text-muted-foreground">
              {idx === 0 ? 'start' : ''}
            </span>
            <div className="flex-1 flex items-center gap-2">
              <ChevronRight className="w-3 h-3 text-muted-foreground" />
              <span className="font-mono text-[11px] px-1.5 py-0.5 rounded bg-slate-200/80 dark:bg-slate-800">
                {stage.component_type}
              </span>
              <span className="text-[11px]">
                {stage.name} <span className="text-muted-foreground">({stage.id})</span>
              </span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderStructureView = (pipeline: GeneratedPipeline) => {
    const byType: Record<string, GeneratedPipeline['stages']> = {};
    pipeline.stages.forEach((s) => {
      if (!byType[s.component_type]) byType[s.component_type] = [];
      byType[s.component_type].push(s);
    });
    return (
      <div className="space-y-2 max-h-64 overflow-auto pr-1 text-xs">
        {Object.entries(byType).map(([type, stages]) => (
          <div
            key={type}
            className="border border-slate-200 dark:border-slate-700 rounded-md p-2 bg-slate-50 dark:bg-slate-900/40"
          >
            <div className="font-semibold mb-1 flex items-center gap-2">
              <span className="font-mono text-[11px] px-1.5 py-0.5 rounded bg-slate-200/80 dark:bg-slate-800">
                {type}
              </span>
              <span className="text-[11px] text-muted-foreground">
                {stages.length} stage{stages.length !== 1 ? 's' : ''}
              </span>
            </div>
            <div className="space-y-1 pl-2">
              {stages.map((s) => (
                <div key={s.id} className="flex flex-col gap-0.5">
                  <span className="font-mono text-[11px]">{s.id}</span>
                  <span className="text-[11px] text-muted-foreground">
                    fields: {Object.keys(s.config || {}).join(', ') || '—'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const buildMermaidFlow = (pipeline: GeneratedPipeline): string => {
    const lines: string[] = ['flowchart TD'];
    lines.push('  IN((Input))');

    pipeline.stages.forEach((stage) => {
      const label = `${stage.name}\\n[${stage.component_type}]`;
      lines.push(`  ${stage.id}["${label}"]`);
    });

    pipeline.stages.forEach((stage) => {
      if (stage.depends_on.length === 0) {
        lines.push(`  IN --> ${stage.id}`);
      } else {
        stage.depends_on.forEach((dep) => {
          lines.push(`  ${dep} --> ${stage.id}`);
        });
      }
    });

    if (pipeline.output_stage_id) {
      lines.push(`  ${pipeline.output_stage_id} --> OUT((Output))`);
    }

    return lines.join('\n');
  };

  const buildMermaidSequence = (pipeline: GeneratedPipeline): string => {
    const lines: string[] = ['sequenceDiagram', '  participant User', '  participant Pipeline'];
    const seenTypes = new Set<string>();

    pipeline.stages.forEach((stage) => {
      const actor = stage.component_type || stage.id;
      if (!seenTypes.has(actor)) {
        lines.push(`  participant ${actor}`);
        seenTypes.add(actor);
      }
      lines.push(`  Pipeline->>${actor}: ${stage.name}`);
    });

    return lines.join('\n');
  };

  const buildMermaidClass = (pipeline: GeneratedPipeline): string => {
    const lines: string[] = ['classDiagram'];
    const byType: Record<string, GeneratedPipeline['stages']> = {};
    pipeline.stages.forEach((s) => {
      if (!byType[s.component_type]) byType[s.component_type] = [];
      byType[s.component_type].push(s);
    });

    Object.entries(byType).forEach(([type, stages]) => {
      const safeType = type || 'UnknownComponent';
      lines.push(`  class ${safeType} {`);
      lines.push('    <<component>>');
      lines.push('    +id');
      const fields = new Set<string>();
      stages.forEach((s) => {
        Object.keys(s.config || {}).forEach((key) => fields.add(key));
      });
      Array.from(fields).forEach((f) => {
        lines.push(`    +${f}`);
      });
      lines.push('  }');
    });

    return lines.join('\n');
  };

  const renderMermaidView = (pipeline: GeneratedPipeline) => {
    const flow = buildMermaidFlow(pipeline);
    const seq = buildMermaidSequence(pipeline);
    const cls = buildMermaidClass(pipeline);
    return (
      <div className="space-y-3 max-h-64 overflow-auto pr-1 text-xs">
        <div>
          <div className="font-medium mb-1 text-muted-foreground">Flowchart</div>
          <pre className="bg-slate-900 text-slate-100 p-2 rounded whitespace-pre overflow-auto">
{`\`\`\`mermaid
${flow}
\`\`\``}
          </pre>
        </div>
        <div>
          <div className="font-medium mb-1 text-muted-foreground">Sequence</div>
          <pre className="bg-slate-900 text-slate-100 p-2 rounded whitespace-pre overflow-auto">
{`\`\`\`mermaid
${seq}
\`\`\``}
          </pre>
        </div>
        <div>
          <div className="font-medium mb-1 text-muted-foreground">Class / Structure</div>
          <pre className="bg-slate-900 text-slate-100 p-2 rounded whitespace-pre overflow-auto">
{`\`\`\`mermaid
${cls}
\`\`\``}
          </pre>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Wand2 className="h-6 w-6" />
          AI Pipeline Generator
        </h1>
        <p className="text-muted-foreground mt-1">
          Describe what you want to build in natural language and let AI generate the pipeline for you
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-6">
          {/* Prompt Input */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Describe Your Pipeline
              </CardTitle>
              <CardDescription>
                Tell us what you want the pipeline to do. Be as specific as possible.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 gap-3">
                <div className="space-y-2">
                  <Label className="text-xs text-muted-foreground">Natural language description</Label>
                  <Textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe the intent and data flow of your pipeline..."
                    className="min-h-[120px] resize-y"
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label className="text-xs text-muted-foreground">
                      Optional Mermaid diagram (flowchart / sequence / class)
                    </Label>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 px-2 text-[11px]"
                      disabled={!generatedPipeline}
                      onClick={() => {
                        if (!generatedPipeline) return;
                        const flow = buildMermaidFlow(generatedPipeline);
                        setMermaidInput(`\`\`\`mermaid\n${flow}\n\`\`\``);
                      }}
                    >
                      Sync from pipeline
                    </Button>
                  </div>
                  <Textarea
                    value={mermaidInput}
                    onChange={(e) => setMermaidInput(e.target.value)}
                    placeholder={`Example:
\`\`\`mermaid
flowchart TD
  IN((Input)) --> A[Validate]
  A --> B[AI Summarize]
  B --> OUT((Output))
\`\`\`
`}
                    className="min-h-[140px] resize-y font-mono text-xs"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useAiInterpreter}
                    onChange={(e) => setUseAiInterpreter(e.target.checked)}
                    className="h-3 w-3"
                  />
                  <span>Use AI interpreter pipeline for deeper understanding</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={dryRunOnly}
                    onChange={(e) => setDryRunOnly(e.target.checked)}
                    className="h-3 w-3"
                  />
                  <span>Dry run only (analyze structure)</span>
                </label>
              </div>

              <Button
                onClick={handleGenerate}
                disabled={!prompt.trim() || generating}
                className="w-full"
              >
                {generating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="mr-2 h-4 w-4" />
                    Generate Pipeline
                  </>
                )}
              </Button>

              {error && (
                <div className="flex items-start gap-2 text-sm text-amber-600 bg-amber-50 dark:bg-amber-900/20 p-3 rounded-lg">
                  <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                  <div>
                    <p className="font-medium">Note</p>
                    <p>{error}</p>
                    <p className="mt-1 text-xs">Showing a demo pipeline based on your description.</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Example Prompts */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-amber-500" />
                Example Prompts
              </CardTitle>
              <CardDescription>
                Click an example to get started quickly
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {EXAMPLE_PROMPTS.map((example, i) => (
                  <button
                    key={i}
                    onClick={() => handleExampleClick(example)}
                    className="w-full text-left p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{example.title}</span>
                      <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {example.description}
                    </p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Output Section */}
        <div className="space-y-6">
          {/* Generated Pipeline Preview */}
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FileJson className="h-5 w-5" />
                Generated Pipeline
              </CardTitle>
              {generatedPipeline && (
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="secondary">{generatedPipeline.stages.length} stages</Badge>
                  <Badge variant="outline">{generatedPipeline.version}</Badge>
                  {generatedPipeline.is_fallback && (
                    <Badge variant="destructive">Fallback</Badge>
                  )}
                  <div className="ml-auto flex items-center gap-1 text-xs">
                    <span className="text-muted-foreground">Rate:</span>
                    <Button
                      variant={feedbackRating === 1 ? 'default' : 'outline'}
                      size="sm"
                      className="h-6 px-2 text-xs"
                      disabled={feedbackSending}
                      onClick={() => handleFeedback(1)}
                    >
                      👍
                    </Button>
                    <Button
                      variant={feedbackRating === -1 ? 'default' : 'outline'}
                      size="sm"
                      className="h-6 px-2 text-xs"
                      disabled={feedbackSending}
                      onClick={() => handleFeedback(-1)}
                    >
                      👎
                    </Button>
                  </div>
                </div>
              )}
            </CardHeader>
            <CardContent>
              {generatedPipeline ? (
                <div className="space-y-4">
                  {/* Pipeline info */}
                  <div className="space-y-2">
                    <div>
                      <Label className="text-xs text-muted-foreground">Name</Label>
                      <p className="font-medium">{generatedPipeline.name}</p>
                    </div>
                    <div>
                      <Label className="text-xs text-muted-foreground">Description</Label>
                      <p className="text-sm text-muted-foreground">
                        {generatedPipeline.description}
                      </p>
                    </div>
                  </div>

                  {/* Stages list */}
                  <div>
                    <Label className="text-xs text-muted-foreground">Stages</Label>
                    <div className="mt-2 space-y-1">
                      {generatedPipeline.stages.map((stage, i) => (
                        <div
                          key={stage.id}
                          className="flex items-center gap-2 text-sm p-2 bg-muted/50 rounded"
                        >
                          <span className="w-5 h-5 rounded bg-primary/10 text-primary flex items-center justify-center text-xs font-medium">
                            {i + 1}
                          </span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="font-medium truncate">{stage.name}</span>
                              <Badge variant="outline" className="ml-auto text-xs">
                                {stage.component_type}
                              </Badge>
                            </div>
                            {stage.rationale && (
                              <p className="mt-0.5 text-[11px] text-muted-foreground line-clamp-2">
                                {stage.rationale}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* AI Understanding */}
                  {analysis && (
                    <div>
                      <Label className="text-xs text-muted-foreground">What the AI understood</Label>
                      <div className="mt-2 text-xs text-muted-foreground space-y-1">
                        {analysis._generation_status && (
                          <p>
                            <span className="font-semibold">Generation status:</span>{' '}
                            {analysis._generation_status}
                          </p>
                        )}
                        {analysis._pipeline_source && (
                          <p>
                            <span className="font-semibold">Pipeline source:</span>{' '}
                            {analysis._pipeline_source}
                          </p>
                        )}
                        <p>
                          <span className="font-semibold">Intent:</span>{' '}
                          {analysis.intent || 'unknown'}
                        </p>
                        {analysis.actions?.length > 0 && (
                          <p>
                            <span className="font-semibold">Actions:</span>{' '}
                            {analysis.actions.join(', ')}
                          </p>
                        )}
                        {analysis.data_sources?.length > 0 && (
                          <p>
                            <span className="font-semibold">Data sources:</span>{' '}
                            {analysis.data_sources.join(', ')}
                          </p>
                        )}
                        {analysis.outputs?.length > 0 && (
                          <p>
                            <span className="font-semibold">Outputs:</span>{' '}
                            {analysis.outputs.join(', ')}
                          </p>
                        )}
                        {analysis.suggested_patterns && analysis.suggested_patterns.length > 0 && (
                          <p>
                            <span className="font-semibold">Patterns:</span>{' '}
                            {analysis.suggested_patterns.join(', ')}
                          </p>
                        )}
                        {analysis.ambiguities?.length > 0 && (
                          <p>
                            <span className="font-semibold">Ambiguities:</span>{' '}
                            {analysis.ambiguities.join('; ')}
                          </p>
                        )}
                        {analysis._validation_errors && analysis._validation_errors.length > 0 && (
                          <p className="text-red-600 dark:text-red-400">
                            <span className="font-semibold">Validation errors:</span>{' '}
                            {analysis._validation_errors.join('; ')}
                          </p>
                        )}
                        {analysis._validation_warnings &&
                          analysis._validation_warnings.length > 0 && (
                            <p>
                              <span className="font-semibold">Validation warnings:</span>{' '}
                              {analysis._validation_warnings.join('; ')}
                            </p>
                          )}
                        {analysis._interpreter_error && (
                          <p>
                            <span className="font-semibold">Interpreter note:</span>{' '}
                            {analysis._interpreter_error}
                          </p>
                        )}
                        {analysis._dry_run_summary && (
                          <p>
                            <span className="font-semibold">Dry-run summary:</span>{' '}
                            {analysis._dry_run_summary.stage_count} stages,{' '}
                            {analysis._dry_run_summary.estimated_complexity} complexity,{' '}
                            {analysis._dry_run_summary.uses_llm ? 'uses LLM' : 'no LLM'},{' '}
                            {analysis._dry_run_summary.uses_external_io
                              ? 'uses external I/O'
                              : 'no external I/O'}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Visualization Views */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1 text-xs">
                        <Button
                          variant={previewView === 'flow' ? 'default' : 'outline'}
                          size="sm"
                          className="h-6 px-2 text-[11px]"
                          onClick={() => setPreviewView('flow')}
                        >
                          Flow
                        </Button>
                        <Button
                          variant={previewView === 'sequence' ? 'default' : 'outline'}
                          size="sm"
                          className="h-6 px-2 text-[11px]"
                          onClick={() => setPreviewView('sequence')}
                        >
                          Sequence
                        </Button>
                        <Button
                          variant={previewView === 'structure' ? 'default' : 'outline'}
                          size="sm"
                          className="h-6 px-2 text-[11px]"
                          onClick={() => setPreviewView('structure')}
                        >
                          Structure
                        </Button>
                        <Button
                          variant={previewView === 'json' ? 'default' : 'outline'}
                          size="sm"
                          className="h-6 px-2 text-[11px]"
                          onClick={() => setPreviewView('json')}
                        >
                          JSON
                        </Button>
                        <Button
                          variant={previewView === 'mermaid' ? 'default' : 'outline'}
                          size="sm"
                          className="h-6 px-2 text-[11px]"
                          onClick={() => setPreviewView('mermaid')}
                        >
                          Mermaid
                        </Button>
                      </div>
                      <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                        {Object.keys(stageChanges).length > 0 && (
                          <span>
                            AI refinement changed {Object.keys(stageChanges).length} stage
                            {Object.keys(stageChanges).length !== 1 ? 's' : ''}
                          </span>
                        )}
                        {previewView === 'json' && (
                          <Button variant="ghost" size="sm" onClick={handleCopy}>
                            {copied ? (
                              <>
                                <Check className="h-3 w-3 mr-1" /> Copied
                              </>
                            ) : (
                              <>
                                <Copy className="h-3 w-3 mr-1" /> Copy
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                    </div>

                    {previewView === 'flow' && renderFlowView(generatedPipeline)}
                    {previewView === 'sequence' && renderSequenceView(generatedPipeline)}
                    {previewView === 'structure' && renderStructureView(generatedPipeline)}
                    {previewView === 'json' && (
                      <pre className="text-xs bg-muted p-3 rounded-lg overflow-auto max-h-64 font-mono">
                        {JSON.stringify(generatedPipeline, null, 2)}
                      </pre>
                    )}
                    {previewView === 'mermaid' && (
                      renderMermaidView(generatedPipeline)
                    )}
                  </div>

                  {/* AI refinement for selected stage */}
                  {refineStageId && (
                    <div className="mt-3 border border-slate-200 dark:border-slate-700 rounded-md p-2 bg-slate-50 dark:bg-slate-900/40 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs font-medium">
                          <Sparkles className="w-3 h-3 text-primary" />
                          <span>AI refinement at stage '{refineStageId}'</span>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 text-[11px]"
                          onClick={() => {
                            setRefineStageId(null);
                            setRefineText('');
                          }}
                        >
                          Clear
                        </Button>
                      </div>
                      <Textarea
                        value={refineText}
                        onChange={(e) => setRefineText(e.target.value)}
                        placeholder="Describe how you want to adjust the flow here (e.g., make this foreach parallel, add retry on errors, route failures to a logger stage)..."
                        className="text-xs min-h-[60px]"
                      />
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          size="sm"
                          disabled={!refineText.trim() || refining}
                          onClick={handleRefineStage}
                          className="text-xs h-7 px-3"
                        >
                          {refining ? (
                            <>
                              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                              Refining...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-3 h-3 mr-1" />
                              Apply AI refinement
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button onClick={handleSave} className="flex-1">
                      <Download className="mr-2 h-4 w-4" />
                      Save & Open in Editor
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setGeneratedPipeline(null);
                        setPrompt('');
                      }}
                    >
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                  <Code className="h-12 w-12 mb-4 opacity-50" />
                  <p>Enter a description and click Generate</p>
                  <p className="text-sm mt-1">to create your pipeline</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Tips */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-start gap-3">
            <Info className="h-5 w-5 text-primary shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium">Tips for better results:</p>
              <ul className="list-disc list-inside mt-1 text-muted-foreground space-y-1">
                <li>Be specific about input and output data formats</li>
                <li>Mention if you need validation, filtering, or AI processing</li>
                <li>Describe the flow of data through the pipeline</li>
                <li>Include any business logic or conditional routing needs</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
