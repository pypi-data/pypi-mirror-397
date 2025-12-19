/**
 * Chat Message Components
 *
 * Rich message components for the AI chat interface.
 * Supports user messages, AI responses, and system notifications.
 */

import { useState } from 'react';
import { User, Sparkles, Info, AlertCircle, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PipelinePreviewCard } from './PipelinePreviewCard';
import { AnalysisCard } from './AnalysisCard';
import { ClarificationCard, type ClarificationQuestion } from './ClarificationCard';

// Message content types
export interface PipelineData {
  id?: string;
  name: string;
  version: string;
  description: string;
  stages: Array<{
    id: string;
    name: string;
    component_type: string;
    config?: Record<string, unknown>;
    depends_on?: string[];
    rationale?: string;
  }>;
  output_stage_id?: string;
  is_fallback?: boolean;
}

export interface AnalysisData {
  intent?: string;
  actions?: string[];
  data_sources?: string[];
  outputs?: string[];
  constraints?: string[];
  ambiguities?: string[];
  suggested_patterns?: string[];
  _generation_status?: string;
  _pipeline_source?: string;
  _dry_run_summary?: {
    stage_count: number;
    uses_llm: boolean;
    uses_external_io: boolean;
    estimated_complexity: string;
  };
}

export interface ChatMessageData {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  pipeline?: PipelineData;
  analysis?: AnalysisData;
  suggestions?: string[];
  clarificationQuestions?: ClarificationQuestion[];
  originalRequest?: string;
  isError?: boolean;
}

interface ChatMessageProps {
  message: ChatMessageData;
  onSavePipeline?: (pipeline: PipelineData) => void;
  onRunPipeline?: (pipeline: PipelineData) => void;
  onSuggestionClick?: (suggestion: string) => void;
  saving?: boolean;
}

/**
 * Renders markdown-like content with basic formatting
 */
function MessageContent({ content }: { content: string }) {
  // Simple markdown-ish rendering
  const lines = content.split('\n');

  return (
    <div className="space-y-2">
      {lines.map((line, idx) => {
        // Code block
        if (line.startsWith('```')) {
          return null; // Skip code fence markers for now
        }

        // Heading
        if (line.startsWith('### ')) {
          return (
            <h4 key={idx} className="font-semibold text-lg mt-4 mb-2">
              {line.slice(4)}
            </h4>
          );
        }
        if (line.startsWith('## ')) {
          return (
            <h3 key={idx} className="font-semibold text-xl mt-4 mb-2">
              {line.slice(3)}
            </h3>
          );
        }

        // Bullet list
        if (line.startsWith('• ') || line.startsWith('- ')) {
          return (
            <li key={idx} className="ml-4 list-disc">
              {line.slice(2)}
            </li>
          );
        }

        // Numbered list
        const numberedMatch = line.match(/^(\d+)\.\s/);
        if (numberedMatch) {
          return (
            <li key={idx} className="ml-4 list-decimal">
              {line.slice(numberedMatch[0].length)}
            </li>
          );
        }

        // Empty line
        if (!line.trim()) {
          return <div key={idx} className="h-2" />;
        }

        // Bold text
        const parts = line.split(/(\*\*[^*]+\*\*)/g);
        const formattedLine = parts.map((part, partIdx) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return (
              <strong key={partIdx} className="font-semibold">
                {part.slice(2, -2)}
              </strong>
            );
          }
          // Inline code
          const codeParts = part.split(/(`[^`]+`)/g);
          return codeParts.map((codePart, codeIdx) => {
            if (codePart.startsWith('`') && codePart.endsWith('`')) {
              return (
                <code
                  key={`${partIdx}-${codeIdx}`}
                  className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-sm font-mono"
                >
                  {codePart.slice(1, -1)}
                </code>
              );
            }
            return codePart;
          });
        });

        return (
          <p key={idx} className="leading-relaxed">
            {formattedLine}
          </p>
        );
      })}
    </div>
  );
}

/**
 * User Message Component
 */
export function UserMessage({ message }: { message: ChatMessageData }) {
  return (
    <div className="flex justify-end px-4 py-3">
      <div className="flex items-start gap-3 max-w-2xl">
        <div className="flex-1 text-right">
          <div className="inline-block rounded-2xl rounded-tr-md px-5 py-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white shadow-md">
            <p className="text-base leading-relaxed text-left">{message.content}</p>
          </div>
          <p className="text-xs text-muted-foreground mt-1.5 mr-2">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
          <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        </div>
      </div>
    </div>
  );
}

/**
 * Assistant (AI) Message Component
 */
export function AssistantMessage({
  message,
  onSavePipeline,
  onRunPipeline,
  onSuggestionClick,
  saving,
}: ChatMessageProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="px-4 py-4 hover:bg-gray-50 dark:hover:bg-gray-900/30 transition-colors">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0 space-y-4">
            {/* Header */}
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-900 dark:text-gray-100">FlowMason</span>
              <span className="text-sm text-muted-foreground">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="ml-auto h-7 w-7 p-0 opacity-0 group-hover:opacity-100 hover:opacity-100"
                onClick={handleCopy}
              >
                {copied ? (
                  <Check className="w-3.5 h-3.5 text-green-500" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </Button>
            </div>

            {/* Text Content */}
            <div className="text-base text-gray-800 dark:text-gray-200">
              <MessageContent content={message.content} />
            </div>

            {/* Analysis Card */}
            {message.analysis && (
              <AnalysisCard analysis={message.analysis} />
            )}

            {/* Clarification Questions */}
            {message.clarificationQuestions && message.clarificationQuestions.length > 0 && (
              <ClarificationCard
                questions={message.clarificationQuestions}
                originalRequest={message.originalRequest}
                onAnswer={(answer) => onSuggestionClick?.(answer)}
              />
            )}

            {/* Pipeline Preview */}
            {message.pipeline && (
              <PipelinePreviewCard
                pipeline={message.pipeline}
                analysis={message.analysis}
                onSave={onSavePipeline ? () => onSavePipeline(message.pipeline!) : undefined}
                onRun={onRunPipeline ? () => onRunPipeline(message.pipeline!) : undefined}
                saving={saving}
              />
            )}

            {/* Suggestions */}
            {message.suggestions && message.suggestions.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-2">
                {message.suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSuggestionClick?.(suggestion)}
                    className="px-4 py-2 rounded-full text-sm font-medium border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-violet-300 dark:hover:border-violet-600 transition-all shadow-sm hover:shadow"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * System Message Component (notifications, errors, etc.)
 */
export function SystemMessage({ message }: { message: ChatMessageData }) {
  const isError = message.isError;

  return (
    <div className="px-4 py-3">
      <div className="max-w-2xl mx-auto">
        <div
          className={`flex items-start gap-3 p-4 rounded-xl ${
            isError
              ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
              : 'bg-gray-100 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700'
          }`}
        >
          {isError ? (
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          ) : (
            <Info className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
          )}
          <div className="flex-1">
            <p
              className={`text-sm ${
                isError ? 'text-red-700 dark:text-red-300' : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              {message.content}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Main ChatMessage component that delegates to the appropriate type
 */
export function ChatMessage(props: ChatMessageProps) {
  const { message } = props;

  switch (message.role) {
    case 'user':
      return <UserMessage message={message} />;
    case 'assistant':
      return <AssistantMessage {...props} />;
    case 'system':
      return <SystemMessage message={message} />;
    default:
      return null;
  }
}
