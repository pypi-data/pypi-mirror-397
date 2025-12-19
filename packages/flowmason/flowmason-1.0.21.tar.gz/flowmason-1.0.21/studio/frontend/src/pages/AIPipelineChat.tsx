/**
 * AI Pipeline Studio
 *
 * Unified AI-powered pipeline creation interface combining:
 * - Natural language chat for pipeline generation
 * - Visual pipeline preview with mini DAG
 * - Generation settings and options
 * - Multi-turn conversation with context
 * - Direct commands (run, explain, debug, etc.)
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Send,
  ArrowDown,
  Trash2,
  Settings2,
  X,
  Sliders,
  Zap,
  Brain,
  FileCode,
  Play,
  Eye,
  HelpCircle,
  RotateCcw,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  ChatMessage,
  ChatMessageData,
  PipelineData,
  AnalysisData,
  TypingIndicator,
  SuggestedPrompts,
  QuickSuggestions,
  ClarificationQuestion,
} from '@/components/chat';

// Session storage key
const CHAT_STORAGE_KEY = 'flowmason-ai-studio-v3';

// Generate unique ID
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

// Generate session ID
function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

// Generation settings
interface GenerationSettings {
  useAiInterpreter: boolean;
  includeValidation: boolean;
  includeLogging: boolean;
  dryRunOnly: boolean;
  temperature: number;
}

const DEFAULT_SETTINGS: GenerationSettings = {
  useAiInterpreter: true,
  includeValidation: true,
  includeLogging: true,
  dryRunOnly: false,
  temperature: 0.7,
};

// Pending clarification state
interface PendingClarification {
  originalRequest: string;
  questions: Array<{
    id: string;
    question: string;
    choices?: Array<{ label: string; value: string }>;
  }>;
}

// Quick command buttons
interface QuickCommand {
  id: string;
  label: string;
  icon: React.ReactNode;
  description: string;
  action: string;
}

const QUICK_COMMANDS: QuickCommand[] = [
  {
    id: 'run',
    label: 'Run',
    icon: <Play className="w-4 h-4" />,
    description: 'Test run the current pipeline',
    action: 'run the current pipeline with sample data',
  },
  {
    id: 'explain',
    label: 'Explain',
    icon: <Eye className="w-4 h-4" />,
    description: 'Explain how the pipeline works',
    action: 'explain how this pipeline works step by step',
  },
  {
    id: 'optimize',
    label: 'Optimize',
    icon: <Zap className="w-4 h-4" />,
    description: 'Suggest optimizations',
    action: 'analyze this pipeline and suggest optimizations',
  },
  {
    id: 'help',
    label: 'Help',
    icon: <HelpCircle className="w-4 h-4" />,
    description: 'Show available commands',
    action: 'help',
  },
];

// Settings Panel Component
function SettingsPanel({
  settings,
  onChange,
  onClose,
}: {
  settings: GenerationSettings;
  onChange: (settings: GenerationSettings) => void;
  onClose: () => void;
}) {
  return (
    <div className="absolute top-14 right-4 w-80 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-violet-500" />
          <span className="font-semibold text-gray-900 dark:text-gray-100">Generation Settings</span>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0">
          <X className="w-4 h-4" />
        </Button>
      </div>

      <div className="p-4 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <Label className="text-sm font-medium text-gray-900 dark:text-gray-100">AI Interpreter</Label>
            <p className="text-xs text-muted-foreground mt-0.5">Use advanced AI for deeper understanding</p>
          </div>
          <button
            onClick={() => onChange({ ...settings, useAiInterpreter: !settings.useAiInterpreter })}
            className={`relative w-11 h-6 rounded-full transition-colors ${settings.useAiInterpreter ? 'bg-violet-500' : 'bg-gray-300 dark:bg-gray-600'}`}
          >
            <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${settings.useAiInterpreter ? 'translate-x-5' : ''}`} />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex-1">
            <Label className="text-sm font-medium text-gray-900 dark:text-gray-100">Auto Validation</Label>
            <p className="text-xs text-muted-foreground mt-0.5">Add schema validation stages</p>
          </div>
          <button
            onClick={() => onChange({ ...settings, includeValidation: !settings.includeValidation })}
            className={`relative w-11 h-6 rounded-full transition-colors ${settings.includeValidation ? 'bg-violet-500' : 'bg-gray-300 dark:bg-gray-600'}`}
          >
            <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${settings.includeValidation ? 'translate-x-5' : ''}`} />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex-1">
            <Label className="text-sm font-medium text-gray-900 dark:text-gray-100">Auto Logging</Label>
            <p className="text-xs text-muted-foreground mt-0.5">Add logging stages for debugging</p>
          </div>
          <button
            onClick={() => onChange({ ...settings, includeLogging: !settings.includeLogging })}
            className={`relative w-11 h-6 rounded-full transition-colors ${settings.includeLogging ? 'bg-violet-500' : 'bg-gray-300 dark:bg-gray-600'}`}
          >
            <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${settings.includeLogging ? 'translate-x-5' : ''}`} />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex-1">
            <Label className="text-sm font-medium text-gray-900 dark:text-gray-100">Dry Run Mode</Label>
            <p className="text-xs text-muted-foreground mt-0.5">Preview structure without execution</p>
          </div>
          <button
            onClick={() => onChange({ ...settings, dryRunOnly: !settings.dryRunOnly })}
            className={`relative w-11 h-6 rounded-full transition-colors ${settings.dryRunOnly ? 'bg-violet-500' : 'bg-gray-300 dark:bg-gray-600'}`}
          >
            <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${settings.dryRunOnly ? 'translate-x-5' : ''}`} />
          </button>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <Label className="text-sm font-medium text-gray-900 dark:text-gray-100">Creativity</Label>
            <span className="text-sm text-muted-foreground">{settings.temperature.toFixed(1)}</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={settings.temperature}
            onChange={(e) => onChange({ ...settings, temperature: parseFloat(e.target.value) })}
            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-violet-500"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>Precise</span>
            <span>Creative</span>
          </div>
        </div>

        <Button variant="outline" size="sm" onClick={() => onChange(DEFAULT_SETTINGS)} className="w-full">
          <RotateCcw className="w-3.5 h-3.5 mr-2" />
          Reset to Defaults
        </Button>
      </div>
    </div>
  );
}

// Pipeline Context Indicator
function PipelineContextBar({
  pipelineId,
  pipelineName,
  onClear,
  onView,
}: {
  pipelineId: string;
  pipelineName?: string;
  onClear: () => void;
  onView: () => void;
}) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-violet-50 dark:bg-violet-900/20 border-b border-violet-200 dark:border-violet-800">
      <Brain className="w-4 h-4 text-violet-600 dark:text-violet-400" />
      <span className="text-sm text-violet-700 dark:text-violet-300">
        Working on: <strong>{pipelineName || pipelineId}</strong>
      </span>
      <div className="flex-1" />
      <Button variant="ghost" size="sm" onClick={onView} className="h-7 text-xs text-violet-600 dark:text-violet-400">
        <Eye className="w-3.5 h-3.5 mr-1" />
        View
      </Button>
      <Button variant="ghost" size="sm" onClick={onClear} className="h-7 text-xs text-violet-600 dark:text-violet-400">
        <X className="w-3.5 h-3.5 mr-1" />
        Clear
      </Button>
    </div>
  );
}

export function AIPipelineChat() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState<'thinking' | 'understanding' | 'designing' | 'validating'>('thinking');
  const [sessionId] = useState(() => generateSessionId());
  const [currentPipelineId, setCurrentPipelineId] = useState<string | null>(null);
  const [currentPipelineName, setCurrentPipelineName] = useState<string | null>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [savingPipeline, setSavingPipeline] = useState(false);
  const [contextSuggestions, setContextSuggestions] = useState<string[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<GenerationSettings>(DEFAULT_SETTINGS);
  const [pendingClarification, setPendingClarification] = useState<PendingClarification | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback((behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  }, []);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      setShowScrollButton(scrollHeight - scrollTop - clientHeight > 100);
    };
    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    if (!showScrollButton) scrollToBottom();
  }, [messages, showScrollButton, scrollToBottom]);

  useEffect(() => {
    try {
      const saved = sessionStorage.getItem(CHAT_STORAGE_KEY);
      if (saved) {
        const data = JSON.parse(saved);
        if (data.messages) setMessages(data.messages.map((m: any) => ({ ...m, timestamp: new Date(m.timestamp) })));
        if (data.currentPipelineId) setCurrentPipelineId(data.currentPipelineId);
        if (data.currentPipelineName) setCurrentPipelineName(data.currentPipelineName);
        if (data.settings) setSettings({ ...DEFAULT_SETTINGS, ...data.settings });
        if (data.pendingClarification) setPendingClarification(data.pendingClarification);
      }
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    try {
      sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify({ messages, currentPipelineId, currentPipelineName, settings, pendingClarification }));
    } catch { /* ignore */ }
  }, [messages, currentPipelineId, currentPipelineName, settings, pendingClarification]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [input]);

  const addMessage = useCallback((message: Omit<ChatMessageData, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessageData = { ...message, id: generateId(), timestamp: new Date() };
    setMessages((prev) => [...prev, newMessage]);
    return newMessage;
  }, []);

  // Build conversation history for API
  const buildHistory = useCallback(() => {
    return messages.slice(-10).map((m) => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.content,
    }));
  }, [messages]);

  // Send message to AI backend
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      addMessage({ role: 'user', content });
      setInput('');
      setIsLoading(true);
      setLoadingStatus('understanding');
      setContextSuggestions([]);

      try {
        const statusTimeout1 = setTimeout(() => setLoadingStatus('designing'), 1500);
        const statusTimeout2 = setTimeout(() => setLoadingStatus('validating'), 3000);

        // Build the full request with conversation history
        const history = buildHistory();

        // If we have a pending clarification, include the original request context
        // Note: This is sent to the AI, so we phrase it from the user's perspective for clarity
        const fullMessage = pendingClarification
          ? `Original request: "${pendingClarification.originalRequest}"\n\nUser's answer to your clarification question: ${content}`
          : content;

        // Try AI console endpoint first
        let response = await fetch('/api/v1/console/ai', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            version: 'v1',
            session_id: sessionId,
            message: fullMessage,
            history: history,
            context: currentPipelineId ? { pipeline_id: currentPipelineId } : undefined,
            clarification_answers: pendingClarification ? { answer: content } : undefined,
            options: {
              use_ai_interpreter: settings.useAiInterpreter,
              include_validation: settings.includeValidation,
              include_logging: settings.includeLogging,
              dry_run: settings.dryRunOnly,
            },
          }),
        });

        let data: any = null;
        let pipeline: PipelineData | undefined;
        let analysis: AnalysisData | undefined;

        // Clear pending clarification after sending
        setPendingClarification(null);

        if (response.ok) {
          data = await response.json();

          // Check if backend needs clarification
          if (data.needs_clarification && data.clarification_questions?.length > 0) {
            const questions: ClarificationQuestion[] = data.clarification_questions.map((q: any) => ({
              id: q.id || `q-${Math.random().toString(36).slice(2)}`,
              question: q.question,
              choices: q.choices,
            }));

            // Store original request for context
            const originalRequest = pendingClarification?.originalRequest || content;

            setPendingClarification({
              originalRequest,
              questions,
            });

            // Simple introductory message - the ClarificationCard will show the actual questions
            const clarificationContent =
              data.console_messages?.[0]?.content ||
              "I'd like to understand your requirements better before creating the pipeline.";

            addMessage({
              role: 'assistant',
              content: clarificationContent,
              clarificationQuestions: questions,
              originalRequest,
            });

            clearTimeout(statusTimeout1);
            clearTimeout(statusTimeout2);
            setIsLoading(false);
            setLoadingStatus('thinking');
            return;
          }

          // Extract pipeline if present
          if (data.pipeline_summary) {
            try {
              const pipelineRes = await fetch(`/api/v1/pipelines/${data.pipeline_summary.pipeline_id}`);
              if (pipelineRes.ok) {
                const pipelineData = await pipelineRes.json();
                pipeline = pipelineData;
                setCurrentPipelineId(pipelineData.id);
                setCurrentPipelineName(pipelineData.name);
              }
            } catch {
              pipeline = {
                id: data.pipeline_summary.pipeline_id,
                name: data.pipeline_summary.name,
                version: '1.0.0',
                description: data.pipeline_summary.description || '',
                stages: data.pipeline_summary.stages || [],
                output_stage_id: data.pipeline_summary.output_stage_id,
              };
              setCurrentPipelineId(data.pipeline_summary.pipeline_id);
              setCurrentPipelineName(data.pipeline_summary.name);
            }
          }
        } else {
          // Fallback to generate endpoint with the full context
          const generateDescription = pendingClarification
            ? `${pendingClarification.originalRequest}. Additional context: ${content}`
            : content;

          response = await fetch('/api/v1/generate/pipeline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              description: generateDescription,
              options: {
                include_validation: settings.includeValidation,
                include_logging: settings.includeLogging,
                use_ai_interpreter: settings.useAiInterpreter,
                dry_run: settings.dryRunOnly,
              },
            }),
          });

          if (response.ok) {
            data = await response.json();
            pipeline = data.pipeline;
            analysis = data.analysis;

            if (pipeline) {
              const saveRes = await fetch('/api/v1/pipelines', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(pipeline),
              });
              if (saveRes.ok) {
                const saved = await saveRes.json();
                pipeline.id = saved.id;
                setCurrentPipelineId(saved.id);
                setCurrentPipelineName(pipeline.name);
              }
            }
          }
        }

        clearTimeout(statusTimeout1);
        clearTimeout(statusTimeout2);

        // Build response content - clean and user-friendly
        let responseContent = '';

        // If we have a pipeline, generate a nice response rather than using raw backend messages
        if (pipeline) {
          const stageTypes = [...new Set(pipeline.stages.map((s) => s.component_type))];
          const hasAI = stageTypes.some((t) => ['generator', 'critic', 'improver', 'synthesizer', 'selector'].includes(t));
          const hasLoop = stageTypes.some((t) => ['foreach', 'loop'].includes(t));

          responseContent = `I've created **${pipeline.name}** for you!\n\n`;
          responseContent += `${pipeline.description}\n\n`;

          // Add highlights about the pipeline
          const highlights: string[] = [];
          if (hasAI) highlights.push('AI-powered processing');
          if (hasLoop) highlights.push('iterative processing for each item');
          if (stageTypes.includes('http_request')) highlights.push('external API integration');
          if (stageTypes.includes('schema_validate')) highlights.push('input validation');

          if (highlights.length > 0) {
            responseContent += `This pipeline includes ${highlights.join(', ')}.\n\n`;
          }

          responseContent += `Click **Open in Editor** to customize it further, or **Test Run** to try it with sample data.`;
        } else if (data?.console_messages?.length > 0) {
          // For non-pipeline responses, use backend messages but clean them up
          responseContent = data.console_messages
            .filter((m: any) => m.role === 'assistant')
            .map((m: any) => m.content)
            .join('\n\n');

          // Remove internal context formatting that shouldn't be shown to users
          responseContent = responseContent
            .replace(/Original request:.*?\n\n/gs, '')
            .replace(/User's answer to your clarification question:.*?\n\n/gs, '')
            .replace(/Additional details provided by the user:\n\n/g, '')
            .trim();
        }

        if (!responseContent) {
          responseContent = "I've processed your request. Let me know if you'd like to make any changes.";
        }

        // Generate smart suggestions
        const suggestions: string[] = [];
        if (pipeline) {
          suggestions.push('Add error handling');
          if (!pipeline.stages.some((s) => s.component_type === 'logger')) suggestions.push('Add logging');
          if (pipeline.stages.some((s) => s.component_type === 'foreach')) suggestions.push('Make foreach parallel');
          if (!pipeline.stages.some((s) => s.component_type === 'schema_validate')) suggestions.push('Add input validation');
          if (pipeline.stages.some((s) => s.component_type === 'http_request')) suggestions.push('Add retry logic');
          suggestions.push('Explain this pipeline');
        }

        addMessage({
          role: 'assistant',
          content: responseContent,
          pipeline,
          analysis,
          suggestions: suggestions.slice(0, 4),
        });

        setContextSuggestions(suggestions.slice(0, 4));
      } catch (error) {
        addMessage({
          role: 'system',
          content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
          isError: true,
        });
      } finally {
        setIsLoading(false);
        setLoadingStatus('thinking');
      }
    },
    [addMessage, buildHistory, currentPipelineId, isLoading, pendingClarification, sessionId, settings]
  );

  const handleSubmit = useCallback(
    (e?: React.FormEvent) => {
      e?.preventDefault();
      sendMessage(input);
    },
    [input, sendMessage]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const handlePromptSelect = useCallback(
    (prompt: string) => {
      setInput(prompt);
      setTimeout(() => sendMessage(prompt), 100);
    },
    [sendMessage]
  );

  const handleSuggestionClick = useCallback(
    (suggestion: string) => {
      sendMessage(suggestion);
    },
    [sendMessage]
  );

  const handleQuickCommand = useCallback(
    (command: QuickCommand) => {
      if (command.id === 'run' && !currentPipelineId) {
        addMessage({ role: 'system', content: 'No pipeline loaded. Create a pipeline first.', isError: true });
        return;
      }
      sendMessage(command.action);
    },
    [currentPipelineId, sendMessage, addMessage]
  );

  const handleSavePipeline = useCallback(
    async (pipeline: PipelineData) => {
      setSavingPipeline(true);
      try {
        if (pipeline.id) {
          navigate(`/pipelines/${pipeline.id}`);
          return;
        }
        const response = await fetch('/api/v1/pipelines', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(pipeline),
        });
        if (response.ok) {
          const saved = await response.json();
          setCurrentPipelineId(saved.id);
          setCurrentPipelineName(pipeline.name);
          addMessage({ role: 'system', content: 'Pipeline saved! Opening in editor...' });
          navigate(`/pipelines/${saved.id}`);
        } else {
          throw new Error('Failed to save');
        }
      } catch (error) {
        addMessage({ role: 'system', content: `Failed to save: ${error instanceof Error ? error.message : 'Unknown error'}`, isError: true });
      } finally {
        setSavingPipeline(false);
      }
    },
    [addMessage, navigate]
  );

  const handleRunPipeline = useCallback(
    async (pipeline: PipelineData) => {
      if (!pipeline.id) {
        addMessage({ role: 'system', content: 'Save the pipeline first before running.', isError: true });
        return;
      }
      addMessage({ role: 'system', content: `Starting test run for **${pipeline.name}**...` });
      try {
        const response = await fetch(`/api/v1/pipelines/${pipeline.id}/test`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sample_input: {} }),
        });
        const result = await response.json();
        addMessage({
          role: 'assistant',
          content: result.is_success
            ? `Test completed successfully! All ${pipeline.stages.length} stages executed.`
            : `Test completed with issues: ${result.error || 'See details'}`,
        });
      } catch (error) {
        addMessage({ role: 'system', content: `Test failed: ${error instanceof Error ? error.message : 'Unknown error'}`, isError: true });
      }
    },
    [addMessage]
  );

  const handleClear = useCallback(() => {
    setMessages([]);
    setCurrentPipelineId(null);
    setCurrentPipelineName(null);
    setContextSuggestions([]);
    setPendingClarification(null);
    sessionStorage.removeItem(CHAT_STORAGE_KEY);
  }, []);

  const handleClearContext = useCallback(() => {
    setCurrentPipelineId(null);
    setCurrentPipelineName(null);
    setPendingClarification(null);
    addMessage({ role: 'system', content: 'Context cleared. Ready for a new pipeline.' });
  }, [addMessage]);

  const handleViewPipeline = useCallback(() => {
    if (currentPipelineId) navigate(`/pipelines/${currentPipelineId}`);
  }, [currentPipelineId, navigate]);

  return (
    <div className="flex flex-col h-screen bg-white dark:bg-gray-950 relative">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-md">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">AI Pipeline Studio</h1>
              <p className="text-xs text-muted-foreground">Create, modify, and run pipelines with AI</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {currentPipelineId && (
              <div className="hidden md:flex items-center gap-1 mr-2">
                {QUICK_COMMANDS.slice(0, 3).map((cmd) => (
                  <Button key={cmd.id} variant="ghost" size="sm" onClick={() => handleQuickCommand(cmd)} className="text-muted-foreground hover:text-gray-900 dark:hover:text-gray-100" title={cmd.description}>
                    {cmd.icon}
                    <span className="ml-1.5 text-xs">{cmd.label}</span>
                  </Button>
                ))}
              </div>
            )}
            <Button variant="ghost" size="sm" onClick={handleClear} className="text-muted-foreground hover:text-gray-900 dark:hover:text-gray-100">
              <Trash2 className="w-4 h-4" />
              <span className="ml-1.5 hidden sm:inline">Clear</span>
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setShowSettings(!showSettings)} className={`text-muted-foreground hover:text-gray-900 dark:hover:text-gray-100 ${showSettings ? 'bg-gray-100 dark:bg-gray-800' : ''}`}>
              <Settings2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {showSettings && <SettingsPanel settings={settings} onChange={setSettings} onClose={() => setShowSettings(false)} />}

      {currentPipelineId && (
        <PipelineContextBar pipelineId={currentPipelineId} pipelineName={currentPipelineName || undefined} onClear={handleClearContext} onView={handleViewPipeline} />
      )}

      {/* Messages Area */}
      <div ref={messagesContainerRef} className="flex-1 overflow-y-auto scroll-smooth">
        {messages.length === 0 ? (
          <SuggestedPrompts onSelectPrompt={handlePromptSelect} />
        ) : (
          <div className="pb-32">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} onSavePipeline={handleSavePipeline} onRunPipeline={handleRunPipeline} onSuggestionClick={handleSuggestionClick} saving={savingPipeline} />
            ))}
            {isLoading && <TypingIndicator status={loadingStatus} />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {showScrollButton && (
        <div className="absolute bottom-36 left-1/2 -translate-x-1/2 z-10">
          <Button variant="outline" size="sm" onClick={() => scrollToBottom()} className="rounded-full shadow-lg bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600">
            <ArrowDown className="w-4 h-4 mr-1.5" />
            New messages
          </Button>
        </div>
      )}

      {contextSuggestions.length > 0 && !isLoading && (
        <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50">
          <QuickSuggestions suggestions={contextSuggestions} onSelect={handleSuggestionClick} />
        </div>
      )}

      {/* Input Area */}
      <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto p-4">
          <div className="relative flex items-end gap-3 rounded-2xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-3 focus-within:border-violet-400 dark:focus-within:border-violet-500 focus-within:ring-2 focus-within:ring-violet-100 dark:focus-within:ring-violet-900/50 transition-all shadow-sm">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                pendingClarification
                  ? 'Type your answer...'
                  : currentPipelineId
                  ? 'Describe changes to make, or ask a question...'
                  : 'Describe the pipeline you want to create...'
              }
              disabled={isLoading}
              rows={1}
              className="flex-1 resize-none bg-transparent border-0 outline-none text-base text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 max-h-[200px] overflow-y-auto leading-relaxed"
            />
            <Button type="submit" size="sm" disabled={!input.trim() || isLoading} className="flex-shrink-0 h-10 w-10 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-md disabled:opacity-50 p-0">
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex items-center justify-between mt-2 px-1">
            <p className="text-xs text-muted-foreground">
              Press <kbd className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-xs">Enter</kbd> to send
            </p>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              {settings.useAiInterpreter && <span className="flex items-center gap-1"><Brain className="w-3 h-3" /> AI Interpreter</span>}
              {settings.dryRunOnly && <span className="flex items-center gap-1"><FileCode className="w-3 h-3" /> Dry Run</span>}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
