/**
 * Typing Indicator Component
 *
 * Animated indicator showing AI is processing/thinking.
 * Features sparkle icon with pulsing animation and status text.
 */

import { Sparkles } from 'lucide-react';

interface TypingIndicatorProps {
  status?: 'thinking' | 'understanding' | 'designing' | 'validating';
}

const STATUS_TEXT: Record<string, string> = {
  thinking: 'Thinking...',
  understanding: 'Understanding your request...',
  designing: 'Designing pipeline...',
  validating: 'Validating structure...',
};

export function TypingIndicator({ status = 'thinking' }: TypingIndicatorProps) {
  return (
    <div className="flex items-start gap-4 px-4 py-6 max-w-3xl mx-auto">
      {/* AI Avatar */}
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
        <Sparkles className="w-5 h-5 text-white animate-pulse" />
      </div>

      {/* Typing Animation */}
      <div className="flex-1 pt-2">
        <div className="flex items-center gap-3">
          {/* Bouncing Dots */}
          <div className="flex items-center gap-1">
            <span
              className="w-2.5 h-2.5 bg-violet-500 rounded-full animate-bounce"
              style={{ animationDelay: '0ms', animationDuration: '600ms' }}
            />
            <span
              className="w-2.5 h-2.5 bg-violet-500 rounded-full animate-bounce"
              style={{ animationDelay: '150ms', animationDuration: '600ms' }}
            />
            <span
              className="w-2.5 h-2.5 bg-violet-500 rounded-full animate-bounce"
              style={{ animationDelay: '300ms', animationDuration: '600ms' }}
            />
          </div>

          {/* Status Text */}
          <span className="text-base text-muted-foreground animate-pulse">
            {STATUS_TEXT[status] || STATUS_TEXT.thinking}
          </span>
        </div>
      </div>
    </div>
  );
}

/**
 * Compact typing indicator for inline use
 */
export function TypingIndicatorInline() {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span
        className="w-1.5 h-1.5 bg-violet-500 rounded-full animate-bounce"
        style={{ animationDelay: '0ms', animationDuration: '600ms' }}
      />
      <span
        className="w-1.5 h-1.5 bg-violet-500 rounded-full animate-bounce"
        style={{ animationDelay: '150ms', animationDuration: '600ms' }}
      />
      <span
        className="w-1.5 h-1.5 bg-violet-500 rounded-full animate-bounce"
        style={{ animationDelay: '300ms', animationDuration: '600ms' }}
      />
    </span>
  );
}
