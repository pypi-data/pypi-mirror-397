/**
 * Pipeline Builder Page
 *
 * Main page for composing pipelines.
 * Combines Component Palette, Canvas, and Configuration Panel.
 * Modern UI with dark mode support.
 */

import { useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Save,
  Play,
  ArrowLeft,
  Settings,
  AlertTriangle,
  CheckCircle,
  Key,
  Loader2,
  Workflow,
  PanelRightClose,
  PanelRightOpen,
  Clock,
  Code,
  X,
  Copy,
  Check,
  Pencil,
  StickyNote,
  FileEdit,
} from 'lucide-react';
import { ComponentPalette } from '../components/ComponentPalette';
import { PipelineCanvas, type StageExecutionState } from '../components/PipelineCanvas';
import { StageConfigPanel } from '../components/StageConfigPanel';
import { ExecutionPanel, type StageExecutionInfo } from '../components/ExecutionPanel';
import { StageInspector } from '../components/StageInspector';
import { SavePipelineDialog, type SavePipelineData } from '../components/SavePipelineDialog';
import { useComponents } from '../hooks/useComponents';
import { usePipeline } from '../hooks/usePipelines';
import { useSettings } from '../hooks/useSettings';
import { useAutosave } from '../hooks/useAutosave';
import type { PipelineStage, ComponentInfo, LLMSettings } from '../types';
import { Button, Badge } from '@/components/ui';

export function PipelineBuilder() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { components } = useComponents();
  const { pipeline, loading, updatePipeline } = usePipeline(id || null);
  const { hasConfiguredProvider, configuredProviders } = useSettings();

  const [stages, setStages] = useState<PipelineStage[]>([]);
  const [selectedStageId, setSelectedStageId] = useState<string | null>(null);
  const [showExecution, setShowExecution] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [showJsonPanel, setShowJsonPanel] = useState(false);
  const [jsonCopied, setJsonCopied] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showNodeNotes, setShowNodeNotes] = useState(false);

  // Execution visualization state
  const [stageExecutionStates, setStageExecutionStates] = useState<Record<string, StageExecutionState>>({});
  const [inspectedStageId, setInspectedStageId] = useState<string | null>(null);

  // Autosave
  const autosave = useAutosave(
    stages,
    async (stagesData) => {
      if (!pipeline) return;
      await updatePipeline({ stages: stagesData });
      setHasChanges(false);
    },
    hasChanges,
    {
      delay: 3000,
      enabled: true,
    }
  );

  // Initialize stages from pipeline
  useMemo(() => {
    if (pipeline?.stages) {
      setStages(pipeline.stages);
    }
  }, [pipeline]);

  const selectedStage = useMemo(
    () => stages.find((s) => s.id === selectedStageId) || null,
    [stages, selectedStageId]
  );

  const selectedComponent = useMemo(
    () =>
      selectedStage
        ? components.find((c) => c.component_type === selectedStage.component_type) ||
          null
        : null,
    [selectedStage, components]
  );

  const upstreamStages = useMemo(() => {
    if (!selectedStage) return [];
    return stages.filter((s) => selectedStage.depends_on.includes(s.id));
  }, [selectedStage, stages]);

  const handleStagesChange = useCallback((newStages: PipelineStage[]) => {
    setStages(newStages);
    setHasChanges(true);
  }, []);

  const handleConfigChange = useCallback(
    (stageId: string, config: Record<string, unknown>) => {
      setStages((prev) =>
        prev.map((s) => (s.id === stageId ? { ...s, config } : s))
      );
      setHasChanges(true);
    },
    []
  );

  const handleLLMSettingsChange = useCallback(
    (stageId: string, llm_settings: LLMSettings) => {
      setStages((prev) =>
        prev.map((s) => (s.id === stageId ? { ...s, llm_settings } : s))
      );
      setHasChanges(true);
    },
    []
  );

  const handleSave = useCallback(async () => {
    if (!pipeline) return;

    setSaving(true);
    try {
      await updatePipeline({ stages });
      setHasChanges(false);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error
        ? err.message
        : typeof err === 'object' && err !== null && 'message' in err
          ? String((err as {message: unknown}).message)
          : 'Failed to save';
      alert(errorMessage);
    } finally {
      setSaving(false);
    }
  }, [pipeline, stages, updatePipeline]);

  const handleSaveWithDialog = useCallback(async (data: SavePipelineData) => {
    if (!pipeline) return;

    setSaving(true);
    try {
      await updatePipeline({
        name: data.name,
        description: data.description,
        category: data.category,
        tags: data.tags,
        is_template: data.isTemplate,
        stages,
      });
      setHasChanges(false);
      setShowSaveDialog(false);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error
        ? err.message
        : typeof err === 'object' && err !== null && 'message' in err
          ? String((err as {message: unknown}).message)
          : 'Failed to save';
      alert(errorMessage);
    } finally {
      setSaving(false);
    }
  }, [pipeline, stages, updatePipeline]);

  const handleComponentSelect = useCallback((component: ComponentInfo) => {
    // Just log for now - actual add happens via drag-and-drop
    console.log('Component selected:', component.component_type);
  }, []);

  // Handle execution state changes from ExecutionPanel
  const handleExecutionStateChange = useCallback((stageStates: Record<string, StageExecutionInfo>) => {
    // Convert StageExecutionInfo to StageExecutionState (they have the same shape)
    const converted: Record<string, StageExecutionState> = {};
    for (const [stageId, info] of Object.entries(stageStates)) {
      converted[stageId] = {
        status: info.status,
        input: info.input,
        output: info.output,
        error: info.error,
      };
    }
    setStageExecutionStates(converted);
  }, []);

  // Get inspected stage for the inspector panel
  const inspectedStage = useMemo(
    () => (inspectedStageId ? stages.find((s) => s.id === inspectedStageId) : null),
    [stages, inspectedStageId]
  );

  const inspectedStageUpstream = useMemo(() => {
    if (!inspectedStage) return [];
    return stages.filter((s) => inspectedStage.depends_on.includes(s.id));
  }, [inspectedStage, stages]);

  const inspectedStageDownstream = useMemo(() => {
    if (!inspectedStage) return [];
    return stages.filter((s) => s.depends_on.includes(inspectedStage.id));
  }, [inspectedStage, stages]);

  // Compute pipeline JSON for debugging (includes current stages)
  const pipelineJson = useMemo(() => {
    if (!pipeline) return '{}';
    return JSON.stringify(
      {
        ...pipeline,
        stages, // Use current stages state
      },
      null,
      2
    );
  }, [pipeline, stages]);

  const handleCopyJson = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(pipelineJson);
      setJsonCopied(true);
      setTimeout(() => setJsonCopied(false), 2000);
    } catch {
      alert('Failed to copy to clipboard');
    }
  }, [pipelineJson]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-slate-50 dark:bg-slate-900">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary-500" />
          <p className="text-slate-500 dark:text-slate-400">Loading pipeline...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-slate-100 dark:bg-slate-950">
      {/* Header */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-800 px-4 py-3 flex items-center justify-between sticky top-0 z-20">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/pipelines')}
            className="text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back
          </Button>

          <div className="h-6 w-px bg-slate-200 dark:bg-slate-700" />

          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 dark:bg-primary-900/50 rounded-lg">
              <Workflow className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-semibold text-slate-900 dark:text-slate-100">
                  {pipeline?.name || 'New Pipeline'}
                </h1>
                {/* Status badge */}
                {pipeline?.status === 'published' ? (
                  <Badge className="bg-green-100 text-green-700 border-green-200 hover:bg-green-100 text-xs">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Published
                  </Badge>
                ) : (
                  <Badge className="bg-amber-100 text-amber-700 border-amber-200 hover:bg-amber-100 text-xs">
                    <FileEdit className="w-3 h-3 mr-1" />
                    Draft
                  </Badge>
                )}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs truncate">
                {pipeline?.description || 'Configure your pipeline stages'}
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Provider Status Indicator */}
          {hasConfiguredProvider ? (
            <Badge variant="success" className="gap-1.5">
              <CheckCircle className="w-3.5 h-3.5" />
              {configuredProviders.length} provider{configuredProviders.length !== 1 ? 's' : ''}
            </Badge>
          ) : (
            <Link to="/settings">
              <Badge variant="warning" className="gap-1.5 cursor-pointer hover:opacity-80">
                <AlertTriangle className="w-3.5 h-3.5" />
                No API keys
                <Key className="w-3 h-3" />
              </Badge>
            </Link>
          )}

          {/* Autosave indicator */}
          {autosave.isPending && (
            <Badge variant="outline" className="gap-1.5 text-slate-500">
              <Clock className="w-3 h-3" />
              Saving...
            </Badge>
          )}
          {autosave.lastSaved && !autosave.isPending && !hasChanges && (
            <Badge variant="outline" className="gap-1.5 text-green-600 dark:text-green-400">
              <CheckCircle className="w-3 h-3" />
              Saved
            </Badge>
          )}

          <div className="h-6 w-px bg-slate-200 dark:bg-slate-700" />

          {/* JSON View Toggle */}
          <Button
            variant={showJsonPanel ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowJsonPanel(!showJsonPanel)}
            title="View Pipeline JSON"
          >
            <Code className="w-4 h-4" />
          </Button>

          {/* Show/Hide Node Notes Toggle */}
          <Button
            variant={showNodeNotes ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowNodeNotes(!showNodeNotes)}
            title={showNodeNotes ? 'Hide node descriptions' : 'Show node descriptions'}
          >
            <StickyNote className="w-4 h-4" />
          </Button>

          <div className="h-6 w-px bg-slate-200 dark:bg-slate-700" />

          <Button
            variant={showExecution ? 'default' : 'outline'}
            onClick={() => setShowExecution(!showExecution)}
          >
            {showExecution ? (
              <>
                <PanelRightClose className="w-4 h-4 mr-2" />
                Hide Runner
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Run
              </>
            )}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSaveDialog(true)}
            title="Edit pipeline details"
          >
            <Pencil className="w-4 h-4" />
          </Button>

          <Button
            onClick={handleSave}
            disabled={saving || autosave.isSaving || !hasChanges}
            className="relative"
          >
            {saving || autosave.isSaving ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save
              </>
            )}
            {hasChanges && !saving && !autosave.isSaving && (
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-amber-500 rounded-full border-2 border-white dark:border-slate-900 animate-pulse" />
            )}
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 flex overflow-hidden">
          {/* Component Palette */}
          <ComponentPalette
            onComponentSelect={handleComponentSelect}
            collapsed={sidebarCollapsed}
            onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
          />

          {/* Canvas */}
          <div className="flex-1 relative">
            <PipelineCanvas
              stages={stages}
              onStagesChange={handleStagesChange}
              onStageSelect={setSelectedStageId}
              selectedStageId={selectedStageId}
              components={components}
              showNotes={showNodeNotes}
              stageExecutionStates={stageExecutionStates}
              onStageInspect={setInspectedStageId}
            />
          </div>

          {/* Right panel: Config or Execution */}
          {showExecution ? (
            <div className="w-96">
              <ExecutionPanel
                pipeline={pipeline}
                stages={stages}
                onExecutionStateChange={handleExecutionStateChange}
              />
            </div>
          ) : selectedStage ? (
            <StageConfigPanel
              stage={selectedStage}
              component={selectedComponent}
              upstreamStages={upstreamStages}
              pipelineInputSchema={pipeline?.input_schema?.properties || {}}
              onConfigChange={handleConfigChange}
              onLLMSettingsChange={handleLLMSettingsChange}
              onClose={() => setSelectedStageId(null)}
            />
          ) : (
            <div className="w-80 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 flex flex-col">
              <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <Settings className="w-5 h-5 text-slate-400 dark:text-slate-500" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Configuration</h2>
                </div>
              </div>
              <div className="flex-1 flex items-center justify-center p-8">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                    <PanelRightOpen className="w-8 h-8 text-slate-300 dark:text-slate-600" />
                  </div>
                  <h3 className="font-medium text-slate-700 dark:text-slate-300 mb-1">
                    No stage selected
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 max-w-[200px]">
                    Click on a stage in the canvas to configure its inputs and settings
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>

      {/* JSON View Modal */}
      {showJsonPanel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl w-[800px] max-w-[90vw] max-h-[80vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-2">
                <Code className="w-5 h-5 text-slate-500" />
                <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                  Pipeline JSON
                </h2>
                {hasChanges && (
                  <Badge variant="warning" className="text-xs">
                    Unsaved Changes
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopyJson}
                  className="gap-1.5"
                >
                  {jsonCopied ? (
                    <>
                      <Check className="w-4 h-4 text-green-500" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy
                    </>
                  )}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowJsonPanel(false)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
            {/* Modal Body */}
            <div className="flex-1 overflow-auto p-4">
              <pre className="text-xs font-mono text-slate-800 dark:text-slate-200 whitespace-pre-wrap break-words">
                {pipelineJson}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Stage Inspector (floating panel) */}
      {inspectedStage && inspectedStageId && stageExecutionStates[inspectedStageId] && (
        <StageInspector
          stage={inspectedStage}
          executionState={stageExecutionStates[inspectedStageId]}
          upstreamStages={inspectedStageUpstream}
          downstreamStages={inspectedStageDownstream}
          onClose={() => setInspectedStageId(null)}
        />
      )}

      {/* Save Pipeline Dialog */}
      <SavePipelineDialog
        open={showSaveDialog}
        onOpenChange={setShowSaveDialog}
        initialData={{
          name: pipeline?.name || '',
          description: pipeline?.description || '',
          category: pipeline?.category || 'custom',
          tags: pipeline?.tags || [],
          isTemplate: pipeline?.is_template || false,
        }}
        onSave={handleSaveWithDialog}
        saving={saving}
      />
    </div>
  );
}

export default PipelineBuilder;
