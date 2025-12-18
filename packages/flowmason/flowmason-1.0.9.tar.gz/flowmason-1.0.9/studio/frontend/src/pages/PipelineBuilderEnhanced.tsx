/**
 * Enhanced Pipeline Builder Page
 *
 * Professional pipeline composition and debugging interface with:
 * - Component Palette for drag-and-drop composition
 * - Visual Canvas with debug mode overlays
 * - Stage Configuration Panel
 * - Integrated Debug Panel with console, variables, trace, breakpoints, network
 * - Execution Controls with play/pause/step/stop
 * - Real-time execution visualization
 * - Stage Inspector for I/O inspection
 */

import { useState, useCallback, useMemo, useEffect } from 'react';
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
  Bug,
  Terminal,
} from 'lucide-react';
import { ComponentPalette } from '../components/ComponentPalette';
import { PipelineCanvas } from '../components/PipelineCanvas';
import { StageConfigPanel } from '../components/StageConfigPanel';
import { StageInspector } from '../components/StageInspector';
import { SavePipelineDialog, type SavePipelineData } from '../components/SavePipelineDialog';
import {
  EnhancedDebugPanel,
  ExecutionControls,
  PipelineRunner,
} from '../components/debug';
import { DebugProvider, useDebugContext } from '../contexts/DebugContext';
import { useComponents } from '../hooks/useComponents';
import { usePipeline } from '../hooks/usePipelines';
import { useSettings } from '../hooks/useSettings';
import { useAutosave } from '../hooks/useAutosave';
import type { PipelineStage, LLMSettings, ExecutionStep } from '../types';
import { Button, Badge } from '@/components/ui';
import { cn } from '../lib/utils';

/**
 * Inner component that uses the debug context
 */
function PipelineBuilderInner() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { components } = useComponents();
  const { pipeline, loading, updatePipeline } = usePipeline(id || null);
  const { hasConfiguredProvider, configuredProviders, settings } = useSettings();

  // Debug context
  const debug = useDebugContext();

  // Local state
  const [stages, setStages] = useState<PipelineStage[]>([]);
  const [selectedStageId, setSelectedStageId] = useState<string | null>(null);
  const [showRunner, setShowRunner] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [showJsonPanel, setShowJsonPanel] = useState(false);
  const [jsonCopied, setJsonCopied] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showNodeNotes, setShowNodeNotes] = useState(false);

  // Debug panel state
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [debugPanelHeight, setDebugPanelHeight] = useState(300);
  const [debugPanelMaximized, setDebugPanelMaximized] = useState(false);
  const [isDebugMode, setIsDebugMode] = useState(false);

  // Stage inspector
  const [inspectedStageId, setInspectedStageId] = useState<string | null>(null);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // F5 - Run/Resume
      if (e.key === 'F5' && !e.shiftKey && !e.ctrlKey) {
        e.preventDefault();
        if (debug.state.mode === 'paused') {
          debug.resumeExecution();
        } else if (debug.state.mode === 'stopped') {
          // Would need to trigger run with last inputs
        }
      }
      // Shift+F5 - Stop
      if (e.key === 'F5' && e.shiftKey) {
        e.preventDefault();
        debug.stopExecution();
      }
      // F8 - Pause
      if (e.key === 'F8') {
        e.preventDefault();
        if (debug.state.mode === 'running') {
          debug.pauseExecution();
        } else if (debug.state.mode === 'paused') {
          debug.resumeExecution();
        }
      }
      // F10 - Step
      if (e.key === 'F10') {
        e.preventDefault();
        if (debug.state.mode === 'paused') {
          debug.stepExecution();
        }
      }
      // Ctrl+` - Toggle debug panel
      if (e.key === '`' && e.ctrlKey) {
        e.preventDefault();
        setShowDebugPanel((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [debug]);

  // Autosave
  const autosave = useAutosave(
    stages,
    async (stagesData) => {
      if (!pipeline) return;
      await updatePipeline({ stages: stagesData });
      setHasChanges(false);
    },
    hasChanges,
    { delay: 3000, enabled: true }
  );

  // Initialize stages from pipeline
  useMemo(() => {
    if (pipeline?.stages) {
      setStages(pipeline.stages);
    }
  }, [pipeline]);

  // Derived state
  const selectedStage = useMemo(
    () => stages.find((s) => s.id === selectedStageId) || null,
    [stages, selectedStageId]
  );

  const selectedComponent = useMemo(
    () =>
      selectedStage
        ? components.find((c) => c.component_type === selectedStage.component_type) || null
        : null,
    [selectedStage, components]
  );

  const upstreamStages = useMemo(() => {
    if (!selectedStage) return [];
    return stages.filter((s) => selectedStage.depends_on.includes(s.id));
  }, [selectedStage, stages]);

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

  const pipelineJson = useMemo(() => {
    if (!pipeline) return '{}';
    return JSON.stringify({ ...pipeline, stages }, null, 2);
  }, [pipeline, stages]);

  // Convert debug state to canvas execution states
  const canvasExecutionStates = useMemo(() => {
    return debug.state.stageExecutionStates;
  }, [debug.state.stageExecutionStates]);

  // Breakpoint helpers
  const breakpointsEnabled = debug.state.breakpoints.filter((bp) => bp.enabled);

  // Event handlers
  const handleStagesChange = useCallback((newStages: PipelineStage[]) => {
    setStages(newStages);
    setHasChanges(true);
  }, []);

  const handleConfigChange = useCallback((stageId: string, config: Record<string, unknown>) => {
    setStages((prev) => prev.map((s) => (s.id === stageId ? { ...s, config } : s)));
    setHasChanges(true);
  }, []);

  const handleLLMSettingsChange = useCallback((stageId: string, llm_settings: LLMSettings) => {
    setStages((prev) => prev.map((s) => (s.id === stageId ? { ...s, llm_settings } : s)));
    setHasChanges(true);
  }, []);

  const handleSave = useCallback(async () => {
    if (!pipeline) return;
    setSaving(true);
    try {
      await updatePipeline({ stages });
      setHasChanges(false);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save';
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
      const errorMessage = err instanceof Error ? err.message : 'Failed to save';
      alert(errorMessage);
    } finally {
      setSaving(false);
    }
  }, [pipeline, stages, updatePipeline]);

  const handleCopyJson = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(pipelineJson);
      setJsonCopied(true);
      setTimeout(() => setJsonCopied(false), 2000);
    } catch {
      alert('Failed to copy to clipboard');
    }
  }, [pipelineJson]);

  // Execution handlers
  const handleStartExecution = useCallback(
    async (inputs: Record<string, unknown>) => {
      if (!pipeline) return;

      // Build provider overrides from stage LLM settings
      const providerOverrides: Record<string, { provider?: string; model?: string; temperature?: number; max_tokens?: number }> = {};
      stages.forEach((stage) => {
        if (stage.llm_settings) {
          providerOverrides[stage.id] = stage.llm_settings;
        }
      });

      await debug.startExecution(pipeline.id, inputs, stages, providerOverrides);

      // Auto-show debug panel when running in debug mode
      if (isDebugMode) {
        setShowDebugPanel(true);
      }
    },
    [pipeline, stages, debug, isDebugMode]
  );

  const handleRestartExecution = useCallback(() => {
    // Restart with last inputs if available
    if (debug.state.currentRun?.inputs) {
      handleStartExecution(debug.state.currentRun.inputs);
    }
  }, [debug.state.currentRun?.inputs, handleStartExecution]);

  const handleRetryStep = useCallback(
    (step: ExecutionStep) => {
      debug.retryStage(step.stageId);
    },
    [debug]
  );

  const handleSelectStage = useCallback((stageId: string) => {
    setSelectedStageId(stageId);
  }, []);

  const handleInspectStage = useCallback((stageId: string) => {
    setInspectedStageId(stageId);
  }, []);

  // Toggle breakpoint on stage via right-click
  const handleStageRightClick = useCallback(
    (stageId: string, _e: React.MouseEvent) => {
      if (isDebugMode) {
        if (debug.hasBreakpoint(stageId)) {
          const bp = debug.state.breakpoints.find((b) => b.stageId === stageId);
          if (bp) debug.removeBreakpoint(bp.id);
        } else {
          debug.addBreakpoint(stageId);
        }
      }
    },
    [isDebugMode, debug]
  );

  // Get list of stage IDs that have breakpoints
  const breakpointStageIds = useMemo(() => {
    return debug.state.breakpoints.filter((bp) => bp.enabled).map((bp) => bp.stageId);
  }, [debug.state.breakpoints]);

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

  const isRunning = debug.state.mode === 'running' || debug.state.mode === 'stepping';
  const isPaused = debug.state.mode === 'paused';

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
                {isRunning && (
                  <Badge className="bg-blue-100 text-blue-700 border-blue-200 animate-pulse text-xs">
                    <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                    Running
                  </Badge>
                )}
                {isPaused && (
                  <Badge className="bg-amber-100 text-amber-700 border-amber-200 text-xs">
                    Paused
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
          {/* Provider Status */}
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

          {/* Debug mode toggle */}
          <Button
            variant={isDebugMode ? 'default' : 'outline'}
            size="sm"
            onClick={() => setIsDebugMode(!isDebugMode)}
            className={cn(isDebugMode && 'bg-purple-600 hover:bg-purple-700')}
          >
            <Bug className="w-4 h-4 mr-1" />
            Debug
            {breakpointsEnabled.length > 0 && (
              <Badge
                variant="secondary"
                className={cn('ml-1 h-5 px-1.5 text-xs', isDebugMode && 'bg-purple-800 text-purple-100')}
              >
                {breakpointsEnabled.length}
              </Badge>
            )}
          </Button>

          {/* Debug panel toggle */}
          <Button
            variant={showDebugPanel ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowDebugPanel(!showDebugPanel)}
            title="Toggle Debug Panel (Ctrl+`)"
          >
            <Terminal className="w-4 h-4" />
          </Button>

          {/* JSON View */}
          <Button
            variant={showJsonPanel ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowJsonPanel(!showJsonPanel)}
            title="View Pipeline JSON"
          >
            <Code className="w-4 h-4" />
          </Button>

          {/* Node Notes */}
          <Button
            variant={showNodeNotes ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowNodeNotes(!showNodeNotes)}
            title={showNodeNotes ? 'Hide node descriptions' : 'Show node descriptions'}
          >
            <StickyNote className="w-4 h-4" />
          </Button>

          <div className="h-6 w-px bg-slate-200 dark:bg-slate-700" />

          {/* Runner toggle */}
          <Button variant={showRunner ? 'default' : 'outline'} onClick={() => setShowRunner(!showRunner)}>
            {showRunner ? (
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

          {/* Edit details */}
          <Button variant="outline" size="sm" onClick={() => setShowSaveDialog(true)} title="Edit pipeline details">
            <Pencil className="w-4 h-4" />
          </Button>

          {/* Save */}
          <Button onClick={handleSave} disabled={saving || autosave.isSaving || !hasChanges} className="relative">
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

      {/* Execution controls bar (shown when debug mode or running) */}
      {(isDebugMode || isRunning || isPaused || debug.state.currentRun) && (
        <ExecutionControls
          mode={debug.state.mode}
          currentRun={debug.state.currentRun}
          breakpointCount={breakpointsEnabled.length}
          hasBreakpointsEnabled={breakpointsEnabled.length > 0}
          isDebugMode={isDebugMode}
          canRun={hasConfiguredProvider && stages.length > 0}
          onPlay={() => {
            if (debug.state.mode === 'paused') {
              debug.resumeExecution();
            } else {
              setShowRunner(true);
            }
          }}
          onPause={debug.pauseExecution}
          onStop={debug.stopExecution}
          onStep={debug.stepExecution}
          onRestart={handleRestartExecution}
          onToggleDebugMode={() => setIsDebugMode(!isDebugMode)}
          onClearBreakpoints={debug.clearBreakpoints}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 flex overflow-hidden">
          {/* Component Palette */}
          <ComponentPalette
            onComponentSelect={(c) => console.log('Selected:', c.component_type)}
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
              stageExecutionStates={canvasExecutionStates}
              onStageInspect={handleInspectStage}
              isDebugMode={isDebugMode}
              breakpoints={breakpointStageIds}
              onNodeContextMenu={handleStageRightClick}
            />

            {/* Debug mode indicator overlay */}
            {isDebugMode && (
              <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-1.5 bg-purple-600 text-white rounded-full shadow-lg text-xs font-medium">
                <Bug className="w-3.5 h-3.5" />
                Debug Mode
                <span className="text-purple-200">• Right-click to add breakpoints</span>
              </div>
            )}
          </div>

          {/* Right panel: Runner or Config */}
          {showRunner ? (
            <div className="w-96">
              <PipelineRunner
                pipeline={pipeline!}
                stages={stages}
                configuredProviders={configuredProviders}
                defaultProvider={settings?.default_provider}
                debugMode={debug.state.mode}
                currentRun={debug.state.currentRun}
                executionTrace={debug.state.executionTrace}
                stageExecutionStates={debug.state.stageExecutionStates}
                isDebugEnabled={isDebugMode}
                breakpointCount={breakpointsEnabled.length}
                onStartExecution={handleStartExecution}
                onPauseExecution={debug.pauseExecution}
                onResumeExecution={debug.resumeExecution}
                onStepExecution={debug.stepExecution}
                onStopExecution={debug.stopExecution}
                onRestartExecution={handleRestartExecution}
                onToggleDebugMode={() => setIsDebugMode(!isDebugMode)}
                onSelectStage={handleSelectStage}
                onInspectStage={handleInspectStage}
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
                  <h3 className="font-medium text-slate-700 dark:text-slate-300 mb-1">No stage selected</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 max-w-[200px]">
                    Click on a stage in the canvas to configure its inputs and settings
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Debug Panel (bottom) */}
        {showDebugPanel && (
          <EnhancedDebugPanel
            logs={debug.state.logs}
            variables={debug.state.variables}
            executionTrace={debug.state.executionTrace}
            breakpoints={debug.state.breakpoints}
            networkCalls={debug.state.networkCalls}
            logCounts={debug.state.logCounts}
            stages={stages}
            currentStageId={debug.state.currentStageId}
            onClearLogs={debug.clearLogs}
            onClearTrace={debug.clearExecutionTrace}
            onClearVariables={debug.clearVariables}
            onToggleBreakpoint={debug.toggleBreakpoint}
            onRemoveBreakpoint={debug.removeBreakpoint}
            onAddBreakpoint={debug.addBreakpoint}
            onClearBreakpoints={debug.clearBreakpoints}
            onClearNetworkCalls={debug.clearNetworkCalls}
            onRetryStep={handleRetryStep}
            onSelectStage={handleSelectStage}
            isOpen={showDebugPanel}
            onClose={() => setShowDebugPanel(false)}
            height={debugPanelHeight}
            onHeightChange={setDebugPanelHeight}
            isMaximized={debugPanelMaximized}
            onToggleMaximize={() => setDebugPanelMaximized(!debugPanelMaximized)}
          />
        )}
      </div>

      {/* JSON View Modal */}
      {showJsonPanel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl w-[800px] max-w-[90vw] max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-2">
                <Code className="w-5 h-5 text-slate-500" />
                <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Pipeline JSON</h2>
                {hasChanges && <Badge variant="warning" className="text-xs">Unsaved Changes</Badge>}
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={handleCopyJson} className="gap-1.5">
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
                <Button variant="ghost" size="sm" onClick={() => setShowJsonPanel(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="flex-1 overflow-auto p-4">
              <pre className="text-xs font-mono text-slate-800 dark:text-slate-200 whitespace-pre-wrap break-words">
                {pipelineJson}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Stage Inspector (floating panel) */}
      {inspectedStage && inspectedStageId && debug.state.stageExecutionStates[inspectedStageId] && (
        <StageInspector
          stage={inspectedStage}
          executionState={debug.state.stageExecutionStates[inspectedStageId]}
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

/**
 * Wrapper component that provides the debug context
 */
export function PipelineBuilderEnhanced() {
  return (
    <DebugProvider>
      <PipelineBuilderInner />
    </DebugProvider>
  );
}

export default PipelineBuilderEnhanced;
