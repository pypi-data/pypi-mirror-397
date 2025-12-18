/**
 * Execution Panel
 *
 * Panel for running pipelines and viewing execution results.
 *
 * Key features:
 * - Input form for pipeline input
 * - Run button with loading state
 * - Execution trace visualization with intermediate outputs
 * - Expandable stage outputs for debugging
 * - Usage metrics (tokens, cost, time)
 * - Visual timeline of execution
 * - Test mode with sample input and publish functionality
 * - Dark mode support
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import {
  Play,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  Coins,
  Hash,
  ChevronDown,
  ChevronRight,
  Eye,
  ArrowRight,
  AlertTriangle,
  Copy,
  Check,
  Sparkles,
  FlaskConical,
  UploadCloud,
  Undo2,
  FileJson,
} from 'lucide-react';
import { pipelines as pipelinesApi, runs as runsApi } from '../services/api';
import type { Pipeline, PipelineRun, PipelineStage, StageTrace, JsonSchemaProperty, TestPipelineResponse } from '../types';
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Badge,
  Label,
} from '@/components/ui';

type ExecutionMode = 'run' | 'test';

// Stage execution state for visualization
export interface StageExecutionInfo {
  status: 'pending' | 'running' | 'completed' | 'success' | 'failed';
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
}

interface ExecutionPanelProps {
  pipeline: Pipeline | null;
  stages?: PipelineStage[];
  onRunComplete?: (run: PipelineRun) => void;
  onPublish?: () => void;
  onRefreshPipeline?: () => void;
  onExecutionStateChange?: (stageStates: Record<string, StageExecutionInfo>) => void;
}

export function ExecutionPanel({ pipeline, stages, onRunComplete, onPublish, onRefreshPipeline, onExecutionStateChange }: ExecutionPanelProps) {
  const [mode, setMode] = useState<ExecutionMode>('run');
  const [input, setInput] = useState<Record<string, unknown>>({});
  const [running, setRunning] = useState(false);
  const [currentRun, setCurrentRun] = useState<PipelineRun | null>(null);
  const [testResult, setTestResult] = useState<TestPipelineResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedStageOutput, setSelectedStageOutput] = useState<string | null>(null);
  const [publishing, setPublishing] = useState(false);
  const [unpublishing, setUnpublishing] = useState(false);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Poll for run status updates when run is pending or running
  useEffect(() => {
    const shouldPoll = currentRun && (currentRun.status === 'pending' || currentRun.status === 'running');

    if (shouldPoll) {
      const pollInterval = 500; // Poll every 500ms

      const pollStatus = async () => {
        try {
          const updatedRun = await runsApi.get(currentRun.id);
          setCurrentRun(updatedRun);

          // Stop polling if run completed
          if (updatedRun.status !== 'pending' && updatedRun.status !== 'running') {
            setRunning(false);
            onRunComplete?.(updatedRun);

            // Auto-expand first failed stage if any
            if (updatedRun.trace?.stages) {
              const failedStage = updatedRun.trace.stages.find(s => s.status === 'failed');
              if (failedStage) {
                setSelectedStageOutput(failedStage.stage_id);
              }
            }
          }
        } catch (err) {
          console.error('Failed to poll run status:', err);
        }
      };

      pollingRef.current = setInterval(pollStatus, pollInterval);

      return () => {
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
      };
    }
  }, [currentRun?.id, currentRun?.status, onRunComplete]);

  // Notify parent of execution state changes for canvas visualization
  useEffect(() => {
    if (!onExecutionStateChange || !currentRun?.trace?.stages) {
      return;
    }

    // Build stage execution states from the run trace
    const stageStates: Record<string, StageExecutionInfo> = {};

    // If run is pending/running and we have stages defined, set all as pending initially
    if (stages && currentRun.status === 'pending') {
      stages.forEach((stage) => {
        stageStates[stage.id] = { status: 'pending' };
      });
    }

    // Update states from trace
    for (const stageTrace of currentRun.trace.stages) {
      stageStates[stageTrace.stage_id] = {
        status: stageTrace.status as StageExecutionInfo['status'],
        input: stageTrace.input as Record<string, unknown> | undefined,
        output: stageTrace.output as Record<string, unknown> | undefined,
        error: stageTrace.error,
      };
    }

    onExecutionStateChange(stageStates);
  }, [currentRun?.trace?.stages, currentRun?.status, stages, onExecutionStateChange]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  // Auto-load sample_input when pipeline changes (e.g., new pipeline from template)
  useEffect(() => {
    if (pipeline?.sample_input && Object.keys(pipeline.sample_input).length > 0) {
      setInput(pipeline.sample_input);
    }
  }, [pipeline?.id, pipeline?.sample_input]);

  // Build provider overrides from stage LLM settings
  const buildProviderOverrides = useCallback(() => {
    if (!stages) return undefined;
    const overrides: Record<string, { provider?: string; model?: string; temperature?: number; max_tokens?: number }> = {};

    stages.forEach((stage) => {
      if (stage.llm_settings && Object.keys(stage.llm_settings).length > 0) {
        overrides[stage.id] = stage.llm_settings;
      }
    });

    return Object.keys(overrides).length > 0 ? overrides : undefined;
  }, [stages]);

  const handleRun = useCallback(async () => {
    if (!pipeline) return;

    setRunning(true);
    setError(null);
    setSelectedStageOutput(null);

    try {
      // Build provider overrides from stages' LLM settings
      const providerOverrides = buildProviderOverrides();

      // Start the run - polling will update status
      const run = await pipelinesApi.run(pipeline.id, input, providerOverrides);
      setCurrentRun(run);
      // Note: Don't setRunning(false) here - polling will do that when complete
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
      setRunning(false);
    }
  }, [pipeline, input, buildProviderOverrides]);

  // Handle Test run (for publishing)
  const handleTest = useCallback(async () => {
    if (!pipeline) return;

    setRunning(true);
    setError(null);
    setTestResult(null);
    setSelectedStageOutput(null);

    try {
      // Use sample_input from pipeline if no input is set
      const testInput = Object.keys(input).length > 0 ? input : pipeline.sample_input;
      const result = await pipelinesApi.test(pipeline.id, testInput);
      setTestResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Test failed');
    } finally {
      setRunning(false);
    }
  }, [pipeline, input]);

  // Handle Publish
  const handlePublish = useCallback(async () => {
    if (!pipeline || !testResult?.run_id || !testResult.can_publish) return;

    setPublishing(true);
    setError(null);

    try {
      await pipelinesApi.publish(pipeline.id, testResult.run_id);
      onRefreshPipeline?.();
      onPublish?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Publish failed');
    } finally {
      setPublishing(false);
    }
  }, [pipeline, testResult, onPublish, onRefreshPipeline]);

  // Handle Unpublish
  const handleUnpublish = useCallback(async () => {
    if (!pipeline) return;

    setUnpublishing(true);
    setError(null);

    try {
      await pipelinesApi.unpublish(pipeline.id);
      onRefreshPipeline?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unpublish failed');
    } finally {
      setUnpublishing(false);
    }
  }, [pipeline, onRefreshPipeline]);

  // Load sample input when switching to test mode
  const loadSampleInput = useCallback(() => {
    if (pipeline?.sample_input) {
      setInput(pipeline.sample_input);
    }
  }, [pipeline]);

  if (!pipeline) {
    return (
      <div className="h-full flex items-center justify-center bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800">
        <div className="text-center p-8">
          <Play className="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600 mb-4" />
          <p className="text-slate-500 dark:text-slate-400">Select a pipeline to run</p>
        </div>
      </div>
    );
  }

  const inputSchema = pipeline.input_schema ?? { type: 'object', properties: {} };
  const properties = inputSchema.properties ?? {};

  return (
    <div className="h-full flex flex-col bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {mode === 'run' ? (
              <Play className="w-5 h-5 text-primary-500" />
            ) : (
              <FlaskConical className="w-5 h-5 text-amber-500" />
            )}
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              {mode === 'run' ? 'Run Pipeline' : 'Test & Publish'}
            </h2>
          </div>

          {/* Pipeline Status Badge */}
          {pipeline.status === 'published' && (
            <Badge variant="success" className="gap-1">
              <CheckCircle className="w-3 h-3" />
              Published
            </Badge>
          )}
        </div>

        {/* Mode Toggle */}
        <div className="flex gap-1 mt-3">
          <button
            onClick={() => setMode('run')}
            className={`flex-1 px-3 py-1.5 text-xs font-medium rounded-md flex items-center justify-center gap-1 transition-colors ${
              mode === 'run'
                ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <Play className="w-3 h-3" />
            Run
          </button>
          <button
            onClick={() => {
              setMode('test');
              loadSampleInput();
            }}
            className={`flex-1 px-3 py-1.5 text-xs font-medium rounded-md flex items-center justify-center gap-1 transition-colors ${
              mode === 'test'
                ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <FlaskConical className="w-3 h-3" />
            Test & Publish
          </button>
        </div>
      </div>

      {/* Published Pipeline Actions */}
      {mode === 'test' && pipeline.status === 'published' && (
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-green-50 dark:bg-green-900/20">
          <div className="flex items-center gap-2 text-green-700 dark:text-green-300 mb-2">
            <CheckCircle className="w-4 h-4" />
            <span className="font-medium text-sm">Pipeline is Published</span>
          </div>
          <p className="text-xs text-green-600 dark:text-green-400 mb-3">
            This pipeline is live and available for use. You can unpublish it to make changes.
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={handleUnpublish}
            disabled={unpublishing}
            className="gap-1.5"
          >
            {unpublishing ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Unpublishing...
              </>
            ) : (
              <>
                <Undo2 className="w-3.5 h-3.5" />
                Unpublish to Draft
              </>
            )}
          </Button>
        </div>
      )}

      {/* Input Form */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium text-slate-900 dark:text-slate-100">
            {mode === 'test' ? 'Test Input' : 'Pipeline Input'}
          </h3>
          {mode === 'test' && pipeline.sample_input && (
            <Button
              variant="ghost"
              size="sm"
              onClick={loadSampleInput}
              className="gap-1 text-xs h-7"
            >
              <FileJson className="w-3 h-3" />
              Load Sample
            </Button>
          )}
        </div>

        {Object.keys(properties).length === 0 ? (
          <p className="text-sm text-slate-500 dark:text-slate-400 italic">No input required</p>
        ) : (
          <div className="space-y-3">
            {Object.entries(properties).map(([key, prop]) => (
              <InputField
                key={key}
                name={key}
                schema={prop as JsonSchemaProperty}
                value={input[key]}
                onChange={(value) =>
                  setInput((prev) => ({ ...prev, [key]: value }))
                }
              />
            ))}
          </div>
        )}

        {/* LLM Settings Summary */}
        {stages && stages.some(s => s.llm_settings && Object.keys(s.llm_settings).length > 0) && (
          <Card className="mt-3 bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800">
            <CardContent className="p-3">
              <div className="flex items-center gap-1.5 text-xs text-primary-700 dark:text-primary-300 font-medium">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Custom LLM Settings Active</span>
              </div>
              <div className="mt-2 space-y-1">
                {stages.filter(s => s.llm_settings && Object.keys(s.llm_settings).length > 0).map(s => (
                  <div key={s.id} className="flex items-center gap-2 text-xs text-primary-600 dark:text-primary-400">
                    <span className="font-medium">{s.name}:</span>
                    <Badge variant="secondary" className="text-xs py-0">
                      {s.llm_settings?.provider || 'default'}
                      {s.llm_settings?.model && ` / ${s.llm_settings.model}`}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Run or Test Button */}
        {mode === 'run' ? (
          <Button
            onClick={handleRun}
            disabled={running}
            className="w-full mt-4"
            size="lg"
          >
            {running ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Run Pipeline
              </>
            )}
          </Button>
        ) : (
          <div className="mt-4 space-y-3">
            <Button
              onClick={handleTest}
              disabled={running || pipeline.status === 'published'}
              className="w-full"
              variant={testResult?.can_publish ? 'outline' : 'default'}
              size="lg"
            >
              {running ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Testing...
                </>
              ) : (
                <>
                  <FlaskConical className="w-4 h-4 mr-2" />
                  Run Test
                </>
              )}
            </Button>

            {/* Test Result */}
            {testResult && (
              <Card className={testResult.is_success
                ? 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20'
                : 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20'
              }>
                <CardContent className="p-3">
                  <div className="flex items-center gap-2 mb-2">
                    {testResult.is_success ? (
                      <>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="font-medium text-green-700 dark:text-green-300">Test Passed</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="w-4 h-4 text-red-500" />
                        <span className="font-medium text-red-700 dark:text-red-300">Test Failed</span>
                      </>
                    )}
                  </div>
                  {testResult.error && (
                    <p className="text-xs text-red-600 dark:text-red-400 mt-1">{testResult.error}</p>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Publish Button */}
            {testResult?.can_publish && pipeline.status !== 'published' && (
              <Button
                onClick={handlePublish}
                disabled={publishing}
                className="w-full bg-green-600 hover:bg-green-700"
                size="lg"
              >
                {publishing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <UploadCloud className="w-4 h-4 mr-2" />
                    Publish Pipeline
                  </>
                )}
              </Button>
            )}
          </div>
        )}

        {error && (
          <Card className="mt-3 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
            <CardContent className="p-3 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Results */}
      {currentRun && mode === 'run' && (
        <div className="flex-1 overflow-y-auto">
          <RunResult
            run={currentRun}
            selectedStageOutput={selectedStageOutput}
            onSelectStage={setSelectedStageOutput}
          />
        </div>
      )}

      {/* Test Result Details */}
      {testResult?.result && mode === 'test' && (
        <div className="flex-1 overflow-y-auto p-4">
          <Card className="border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-900/10">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2 text-green-700 dark:text-green-300">
                <ArrowRight className="w-4 h-4" />
                Test Output
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="p-3 bg-green-100/50 dark:bg-green-900/30 rounded-lg border border-green-200 dark:border-green-800">
                <pre className="text-xs text-slate-700 dark:text-slate-300 overflow-x-auto whitespace-pre-wrap font-mono">
                  {JSON.stringify(testResult.result, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

interface InputFieldProps {
  name: string;
  schema: JsonSchemaProperty;
  value: unknown;
  onChange: (value: unknown) => void;
}

function InputField({ name, schema, value, onChange }: InputFieldProps) {
  const isTextArea =
    schema.type === 'string' &&
    (schema.maxLength === undefined || schema.maxLength > 200);

  return (
    <div className="space-y-1.5">
      <Label className="text-sm font-medium text-slate-700 dark:text-slate-300">{name}</Label>
      {isTextArea ? (
        <textarea
          className="w-full rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent placeholder:text-slate-400 dark:placeholder:text-slate-500"
          rows={3}
          value={String(value ?? '')}
          onChange={(e) => onChange(e.target.value)}
          placeholder={schema.description}
        />
      ) : (
        <Input
          type={schema.type === 'number' || schema.type === 'integer' ? 'number' : 'text'}
          value={String(value ?? '')}
          onChange={(e) => {
            const v = e.target.value;
            if (schema.type === 'number') onChange(Number(v));
            else if (schema.type === 'integer') onChange(parseInt(v, 10));
            else onChange(v);
          }}
          placeholder={schema.description}
          className="bg-white dark:bg-slate-800"
        />
      )}
    </div>
  );
}

interface RunResultProps {
  run: PipelineRun;
  selectedStageOutput: string | null;
  onSelectStage: (stageId: string | null) => void;
}

function RunResult({ run, selectedStageOutput, onSelectStage }: RunResultProps) {
  const statusConfig: Record<string, { icon: typeof CheckCircle; color: string; bg: string; border: string; animate?: boolean }> = {
    completed: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-50 dark:bg-green-900/20', border: 'border-green-200 dark:border-green-800' },
    failed: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-200 dark:border-red-800' },
    running: { icon: Loader2, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-900/20', border: 'border-blue-200 dark:border-blue-800', animate: true },
    pending: { icon: Clock, color: 'text-slate-400', bg: 'bg-slate-50 dark:bg-slate-800', border: 'border-slate-200 dark:border-slate-700' },
    cancelled: { icon: XCircle, color: 'text-amber-500', bg: 'bg-amber-50 dark:bg-amber-900/20', border: 'border-amber-200 dark:border-amber-800' },
  };

  const status = statusConfig[run.status];
  const StatusIcon = status.icon;

  return (
    <div className="p-4 space-y-4">
      {/* Status header */}
      <Card className={`${status.bg} ${status.border}`}>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <StatusIcon className={`w-6 h-6 ${status.color} ${status.animate ? 'animate-spin' : ''}`} />
            <div>
              <div className="font-semibold text-slate-900 dark:text-slate-100 capitalize">{run.status}</div>
              <div className="text-xs text-slate-500 dark:text-slate-400 font-mono">Run: {run.id.slice(0, 8)}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Usage metrics */}
      {run.usage && (
        <div className="grid grid-cols-3 gap-3">
          <MetricCard
            icon={<Hash className="w-4 h-4" />}
            value={run.usage.total_tokens.toLocaleString()}
            label="Tokens"
          />
          <MetricCard
            icon={<Coins className="w-4 h-4" />}
            value={`$${run.usage.total_cost.toFixed(4)}`}
            label="Cost"
          />
          <MetricCard
            icon={<Clock className="w-4 h-4" />}
            value={`${(run.usage.execution_time_ms / 1000).toFixed(2)}s`}
            label="Time"
          />
        </div>
      )}

      {/* Error message */}
      {run.error && (
        <Card className="border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-red-700 dark:text-red-300 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Pipeline Error
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <pre className="text-xs text-red-600 dark:text-red-400 whitespace-pre-wrap font-mono bg-red-100/50 dark:bg-red-900/30 p-2 rounded">
              {run.error}
            </pre>
          </CardContent>
        </Card>
      )}

      {/* Execution trace with intermediate outputs */}
      {run.trace && run.trace.stages && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2 text-slate-700 dark:text-slate-300">
              <Eye className="w-4 h-4" />
              Execution Trace
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0 space-y-2">
            {run.trace.stages.map((stage, idx) => (
              <StageTraceItem
                key={stage.stage_id}
                stage={stage}
                isLast={idx === run.trace!.stages.length - 1}
                isSelected={selectedStageOutput === stage.stage_id}
                onSelect={() => onSelectStage(
                  selectedStageOutput === stage.stage_id ? null : stage.stage_id
                )}
              />
            ))}
          </CardContent>
        </Card>
      )}

      {/* Final Output - Highlighted */}
      {run.output && Object.keys(run.output).length > 0 && (
        <Card className="border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-900/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2 text-green-700 dark:text-green-300">
              <ArrowRight className="w-4 h-4" />
              Final Output
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="p-3 bg-green-100/50 dark:bg-green-900/30 rounded-lg border border-green-200 dark:border-green-800">
              <OutputDisplay data={run.output} />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

interface MetricCardProps {
  icon: React.ReactNode;
  value: string;
  label: string;
}

function MetricCard({ icon, value, label }: MetricCardProps) {
  return (
    <Card className="bg-slate-50 dark:bg-slate-800/50">
      <CardContent className="p-3 text-center">
        <div className="text-slate-400 dark:text-slate-500 mb-1 flex justify-center">{icon}</div>
        <div className="text-lg font-bold text-slate-900 dark:text-slate-100">{value}</div>
        <div className="text-xs text-slate-500 dark:text-slate-400">{label}</div>
      </CardContent>
    </Card>
  );
}

interface StageTraceItemProps {
  stage: StageTrace;
  isLast: boolean;
  isSelected: boolean;
  onSelect: () => void;
}

function StageTraceItem({ stage, isLast, isSelected, onSelect }: StageTraceItemProps) {
  const statusConfig: Record<string, { bg: string; border: string; icon: typeof CheckCircle; iconColor: string; animate?: boolean }> = {
    completed: { bg: 'bg-green-50 dark:bg-green-900/20', border: 'border-green-200 dark:border-green-800', icon: CheckCircle, iconColor: 'text-green-500' },
    success: { bg: 'bg-green-50 dark:bg-green-900/20', border: 'border-green-200 dark:border-green-800', icon: CheckCircle, iconColor: 'text-green-500' },
    failed: { bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-200 dark:border-red-800', icon: XCircle, iconColor: 'text-red-500' },
    running: { bg: 'bg-blue-50 dark:bg-blue-900/20', border: 'border-blue-200 dark:border-blue-800', icon: Loader2, iconColor: 'text-blue-500', animate: true },
    pending: { bg: 'bg-slate-50 dark:bg-slate-800', border: 'border-slate-200 dark:border-slate-700', icon: Clock, iconColor: 'text-slate-400' },
  };

  const status = statusConfig[stage.status] || statusConfig.pending;
  const StatusIcon = status.icon;

  return (
    <div className={`rounded-lg border ${status.border} ${status.bg} overflow-hidden`}>
      <button
        onClick={onSelect}
        className="flex items-center gap-2 w-full text-left p-3 hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
      >
        {isSelected ? (
          <ChevronDown className="w-4 h-4 text-slate-400 dark:text-slate-500" />
        ) : (
          <ChevronRight className="w-4 h-4 text-slate-400 dark:text-slate-500" />
        )}
        <StatusIcon className={`w-4 h-4 ${status.iconColor} ${status.animate ? 'animate-spin' : ''}`} />
        <span className="font-medium text-slate-900 dark:text-slate-100 text-sm">{stage.stage_id}</span>
        <Badge variant="secondary" className="text-xs py-0">{stage.component_type}</Badge>
        {stage.usage && (
          <span className="text-xs text-slate-400 dark:text-slate-500 ml-auto">
            {stage.usage.total_tokens} tokens
          </span>
        )}
      </button>

      {isSelected && (
        <div className="border-t border-slate-200 dark:border-slate-700 p-3 space-y-3 bg-white dark:bg-slate-800/50">
          {/* Stage Input */}
          {stage.input && Object.keys(stage.input).length > 0 && (
            <div>
              <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 flex items-center gap-1">
                <ArrowRight className="w-3 h-3 rotate-180" />
                Input
              </div>
              <div className="p-2 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
                <OutputDisplay data={stage.input} compact />
              </div>
            </div>
          )}

          {/* Stage Output */}
          {stage.output && Object.keys(stage.output).length > 0 && (
            <div>
              <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 flex items-center gap-1">
                <ArrowRight className="w-3 h-3" />
                Output
              </div>
              <div className={`p-2 rounded-lg border ${
                isLast
                  ? 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800'
                  : 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800'
              }`}>
                <OutputDisplay data={stage.output} />
              </div>
            </div>
          )}

          {/* Stage Error */}
          {stage.error && (
            <div>
              <div className="text-xs font-medium text-red-600 dark:text-red-400 mb-1 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Error
              </div>
              <pre className="p-2 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-xs rounded-lg border border-red-200 dark:border-red-800 whitespace-pre-wrap font-mono">
                {stage.error}
              </pre>
            </div>
          )}

          {/* Stage Usage */}
          {stage.usage && (
            <div className="flex gap-4 text-xs text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-200 dark:border-slate-700">
              <span className="flex items-center gap-1">
                <Hash className="w-3 h-3" />
                {stage.usage.total_tokens} tokens
              </span>
              <span className="flex items-center gap-1">
                <Coins className="w-3 h-3" />
                ${stage.usage.total_cost.toFixed(4)}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {(stage.usage.execution_time_ms / 1000).toFixed(2)}s
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface OutputDisplayProps {
  data: Record<string, unknown>;
  compact?: boolean;
}

function OutputDisplay({ data, compact }: OutputDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // For compact mode or simple outputs, show inline
  const keys = Object.keys(data);

  if (compact && keys.length === 1) {
    const value = data[keys[0]];
    if (typeof value === 'string' && value.length < 200) {
      return <div className="text-sm text-slate-700 dark:text-slate-300">{value}</div>;
    }
  }

  // Check if output has a 'content' field (common for LLM outputs)
  if ('content' in data && typeof data.content === 'string') {
    return (
      <div className="space-y-2">
        <div className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">{data.content}</div>
        {keys.length > 1 && (
          <details className="text-xs">
            <summary className="text-slate-500 dark:text-slate-400 cursor-pointer hover:text-slate-700 dark:hover:text-slate-300">
              Show all fields
            </summary>
            <pre className="mt-1 p-2 bg-slate-100 dark:bg-slate-800 rounded overflow-x-auto text-slate-600 dark:text-slate-400">
              {JSON.stringify(data, null, 2)}
            </pre>
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
        className="absolute top-2 right-2 p-1.5 rounded-md bg-slate-200/80 dark:bg-slate-700/80 text-slate-500 dark:text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-300 dark:hover:bg-slate-600"
      >
        {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
      </button>
      <pre className="text-xs text-slate-700 dark:text-slate-300 overflow-x-auto whitespace-pre-wrap font-mono">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}

export default ExecutionPanel;
