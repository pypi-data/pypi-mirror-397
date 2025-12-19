/**
 * Analysis Card Component
 *
 * Displays what the AI understood from the user's request.
 * Shows intent, actions, patterns, and any ambiguities.
 */

import {
  Brain,
  Lightbulb,
  AlertTriangle,
  Target,
  Workflow,
  Database,
  FileOutput,
  Layers,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface AnalysisCardProps {
  analysis: {
    intent?: string;
    actions?: string[];
    data_sources?: string[];
    outputs?: string[];
    constraints?: string[];
    ambiguities?: string[];
    suggested_patterns?: string[];
    _generation_status?: string;
    _pipeline_source?: string;
  };
}

export function AnalysisCard({ analysis }: AnalysisCardProps) {
  const hasContent =
    analysis.intent ||
    (analysis.actions && analysis.actions.length > 0) ||
    (analysis.data_sources && analysis.data_sources.length > 0) ||
    (analysis.suggested_patterns && analysis.suggested_patterns.length > 0) ||
    (analysis.ambiguities && analysis.ambiguities.length > 0);

  if (!hasContent) return null;

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800/50 dark:to-gray-900/50 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
          <Brain className="w-4 h-4 text-white" />
        </div>
        <span className="font-medium text-gray-900 dark:text-gray-100">
          What I understood
        </span>
        {analysis._pipeline_source && (
          <Badge variant="outline" className="ml-auto text-xs">
            via {analysis._pipeline_source}
          </Badge>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Intent */}
        {analysis.intent && (
          <div className="flex items-start gap-3">
            <Target className="w-4 h-4 text-violet-500 mt-1 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Intent</p>
              <p className="text-base text-gray-900 dark:text-gray-100">{analysis.intent}</p>
            </div>
          </div>
        )}

        {/* Actions */}
        {analysis.actions && analysis.actions.length > 0 && (
          <div className="flex items-start gap-3">
            <Workflow className="w-4 h-4 text-blue-500 mt-1 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Actions</p>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {analysis.actions.map((action, idx) => (
                  <Badge
                    key={idx}
                    variant="secondary"
                    className="text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                  >
                    {action}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Data Sources */}
        {analysis.data_sources && analysis.data_sources.length > 0 && (
          <div className="flex items-start gap-3">
            <Database className="w-4 h-4 text-cyan-500 mt-1 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Data Sources</p>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {analysis.data_sources.map((source, idx) => (
                  <Badge
                    key={idx}
                    variant="secondary"
                    className="text-sm bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300"
                  >
                    {source}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Outputs */}
        {analysis.outputs && analysis.outputs.length > 0 && (
          <div className="flex items-start gap-3">
            <FileOutput className="w-4 h-4 text-green-500 mt-1 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Outputs</p>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {analysis.outputs.map((output, idx) => (
                  <Badge
                    key={idx}
                    variant="secondary"
                    className="text-sm bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                  >
                    {output}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Patterns */}
        {analysis.suggested_patterns && analysis.suggested_patterns.length > 0 && (
          <div className="flex items-start gap-3">
            <Layers className="w-4 h-4 text-purple-500 mt-1 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Detected Patterns
              </p>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {analysis.suggested_patterns.map((pattern, idx) => (
                  <Badge
                    key={idx}
                    variant="secondary"
                    className="text-sm bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300"
                  >
                    {pattern}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Ambiguities / Notes */}
        {analysis.ambiguities && analysis.ambiguities.length > 0 && (
          <div className="flex items-start gap-3 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
            <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
                Ambiguities
              </p>
              <ul className="mt-1 space-y-1">
                {analysis.ambiguities.map((ambiguity, idx) => (
                  <li key={idx} className="text-sm text-amber-700 dark:text-amber-300">
                    {ambiguity}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Compact inline analysis display
 */
export function AnalysisInline({ analysis }: AnalysisCardProps) {
  return (
    <div className="flex items-center gap-2 flex-wrap text-sm text-muted-foreground">
      {analysis.intent && (
        <span className="flex items-center gap-1">
          <Lightbulb className="w-3.5 h-3.5" />
          {analysis.intent}
        </span>
      )}
      {analysis.suggested_patterns && analysis.suggested_patterns.length > 0 && (
        <>
          <span className="text-gray-300 dark:text-gray-600">•</span>
          <span>Using: {analysis.suggested_patterns.join(', ')}</span>
        </>
      )}
    </div>
  );
}
