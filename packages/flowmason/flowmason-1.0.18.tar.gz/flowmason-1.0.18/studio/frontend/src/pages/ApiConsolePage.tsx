/**
 * API Console Page
 *
 * Interactive chat-like interface for testing APIs and running pipelines.
 * Supports natural commands, direct API calls, and real-time execution viewing.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
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
        <div className="whitespace-pre-wrap text-sm">{message.content}</div>

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
  addMessage: (msg: Omit<Message, 'id' | 'timestamp'>) => void
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
      const pipelines = data.pipelines || data || [];
      addMessage({
        type: 'result',
        content: `Found ${pipelines.length} pipeline(s):`,
        data: pipelines.map((p: Pipeline) => ({ name: p.name, version: p.version, id: p.id })),
      });
      return;
    }

    // List components
    if (cmd === 'components' || cmd === 'list components') {
      const response = await fetch('/api/v1/registry/components');
      const data = await response.json();
      const components = data.components || data || [];
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
      const pipelines = pipelinesData.pipelines || pipelinesData || [];
      const pipeline = pipelines.find(
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
      const runRes = await fetch('/api/v1/debug/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pipeline_id: pipeline.id,
          inputs,
        }),
      });

      const result = await runRes.json();
      const duration = Date.now() - startTime;

      if (runRes.ok && result.status !== 'failed') {
        // Build stage list from results
        const stages: StageExecution[] = Object.entries(result.stage_results || {}).map(
          ([id, data]: [string, any]) => ({
            id,
            name: id,
            status: data.status === 'completed' ? 'completed' : 'failed',
            duration: data.duration_ms,
          })
        );

        addMessage({
          type: 'result',
          content: `✓ Pipeline completed successfully`,
          stages,
          data: result.output || result.result,
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
• GET /api/path - Make GET request
• POST /api/path {"body": ...} - Make POST request
• clear - Clear console
• help - Show this help`,
      });
      return;
    }

    // Unknown command
    addMessage({
      type: 'error',
      content: `Unknown command: "${action}". Type 'help' for available commands.`,
    });
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

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Fetch pipelines for quick actions
  useEffect(() => {
    fetch('/api/v1/pipelines')
      .then((r) => r.json())
      .then((data) => setPipelines(data.pipelines || data || []))
      .catch(() => {});
  }, []);

  // Add welcome message
  useEffect(() => {
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
  }, []);

  const addMessage = useCallback((msg: Omit<Message, 'id' | 'timestamp'>) => {
    setMessages((prev) => [
      ...prev,
      {
        ...msg,
        id: Date.now().toString(),
        timestamp: new Date(),
      },
    ]);
  }, []);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const command = input.trim();
    if (!command) return;

    // Handle clear command locally
    if (command.toLowerCase() === 'clear') {
      setMessages([]);
      setInput('');
      return;
    }

    // Add user message
    addMessage({ type: 'user', content: command });
    setInput('');
    setLoading(true);

    await executeCommand(command, addMessage);
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
