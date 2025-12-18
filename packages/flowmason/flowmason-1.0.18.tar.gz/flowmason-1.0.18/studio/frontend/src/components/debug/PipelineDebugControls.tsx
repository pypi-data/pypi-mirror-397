/**
 * FlowMason Pipeline Debug Controls
 *
 * Provides debug mode controls for pipeline execution:
 * - Start/Stop debug mode
 * - Pause/Resume execution
 * - Step through execution
 * - Visual status indicator
 */

import { cn } from '../../lib/utils';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import type { DebugMode } from '../../types';

interface PipelineDebugControlsProps {
  mode: DebugMode;
  isDebugEnabled: boolean;
  onToggleDebug: () => void;
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
  onStep: () => void;
  className?: string;
}

const MODE_STYLES: Record<DebugMode, { bg: string; text: string; label: string }> = {
  stopped: { bg: 'bg-slate-500/20', text: 'text-slate-400', label: 'Stopped' },
  running: { bg: 'bg-green-500/20', text: 'text-green-400', label: 'Running' },
  paused: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'Paused' },
  stepping: { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Stepping' },
};

export function PipelineDebugControls({
  mode,
  isDebugEnabled,
  onToggleDebug,
  onStart,
  onPause,
  onResume,
  onStop,
  onStep,
  className,
}: PipelineDebugControlsProps) {
  const modeStyle = MODE_STYLES[mode];
  const isActive = mode !== 'stopped';
  const isPaused = mode === 'paused';
  const isRunning = mode === 'running';

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {/* Debug mode toggle */}
      <Button
        variant={isDebugEnabled ? 'default' : 'outline'}
        size="sm"
        onClick={onToggleDebug}
        className={cn(
          'h-7 text-xs px-2',
          isDebugEnabled && 'bg-purple-600 hover:bg-purple-700'
        )}
      >
        <BugIcon className="h-3 w-3 mr-1" />
        Debug
      </Button>

      {isDebugEnabled && (
        <>
          {/* Separator */}
          <div className="w-px h-5 bg-border" />

          {/* Status indicator */}
          <Badge
            variant="outline"
            className={cn('text-[10px] h-5', modeStyle.bg, modeStyle.text)}
          >
            {modeStyle.label}
          </Badge>

          {/* Control buttons */}
          <div className="flex items-center gap-1">
            {/* Start/Restart */}
            {!isActive ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={onStart}
                className="h-7 w-7 p-0"
                title="Start (F5)"
              >
                <PlayIcon className="h-3.5 w-3.5 text-green-500" />
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                onClick={onStop}
                className="h-7 w-7 p-0"
                title="Stop (Shift+F5)"
              >
                <RestartIcon className="h-3.5 w-3.5 text-orange-500" />
              </Button>
            )}

            {/* Pause/Resume */}
            {isRunning ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={onPause}
                className="h-7 w-7 p-0"
                title="Pause (F6)"
              >
                <PauseIcon className="h-3.5 w-3.5 text-yellow-500" />
              </Button>
            ) : isPaused ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={onResume}
                className="h-7 w-7 p-0"
                title="Resume (F5)"
              >
                <PlayIcon className="h-3.5 w-3.5 text-green-500" />
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                disabled
                className="h-7 w-7 p-0"
              >
                <PauseIcon className="h-3.5 w-3.5 text-muted-foreground" />
              </Button>
            )}

            {/* Step */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onStep}
              disabled={!isActive || mode === 'stepping'}
              className="h-7 w-7 p-0"
              title="Step Over (F10)"
            >
              <StepIcon className="h-3.5 w-3.5 text-blue-500" />
            </Button>

            {/* Stop */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onStop}
              disabled={!isActive}
              className="h-7 w-7 p-0"
              title="Stop (Shift+F5)"
            >
              <StopIcon className="h-3.5 w-3.5 text-red-500" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

// Icons
function BugIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m8 2 1.88 1.88" />
      <path d="M14.12 3.88 16 2" />
      <path d="M9 7.13v-1a3.003 3.003 0 1 1 6 0v1" />
      <path d="M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6" />
      <path d="M12 20v-9" />
      <path d="M6.53 9C4.6 8.8 3 7.1 3 5" />
      <path d="M6 13H2" />
      <path d="M3 21c0-2.1 1.7-3.9 3.8-4" />
      <path d="M20.97 5c0 2.1-1.6 3.8-3.5 4" />
      <path d="M22 13h-4" />
      <path d="M17.2 17c2.1.1 3.8 1.9 3.8 4" />
    </svg>
  );
}

function PlayIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M8 5v14l11-7z" />
    </svg>
  );
}

function PauseIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
    </svg>
  );
}

function StopIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <rect x="6" y="6" width="12" height="12" />
    </svg>
  );
}

function StepIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M5 4h4v16H5V4zm6 0l10 8-10 8V4z" />
    </svg>
  );
}

function RestartIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
      <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
      <path d="M16 16h5v5" />
    </svg>
  );
}

export default PipelineDebugControls;
