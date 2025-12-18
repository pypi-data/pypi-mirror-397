/**
 * Run Input Panel
 *
 * Collapsible panel for entering pipeline run inputs with:
 * - Dynamic form based on input schema
 * - Sample input loading
 * - JSON editor mode
 * - Input validation
 * - History of previous inputs
 */

import { useState, useMemo, useEffect } from 'react';
import {
  Play,
  ChevronDown,
  ChevronRight,
  FileJson,
  History,
  RotateCcw,
  Trash2,
  AlertCircle,
  Info,
  Sparkles,
} from 'lucide-react';
import {
  Button,
  Input,
  Badge,
  Card,
  CardContent,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui';
import { cn } from '../../lib/utils';
import type { JsonSchema, JsonSchemaProperty, PipelineStage } from '../../types';

interface RunInputPanelProps {
  inputSchema: JsonSchema | null;
  sampleInput?: Record<string, unknown>;
  stages: PipelineStage[];
  isRunning: boolean;
  onRun: (inputs: Record<string, unknown>) => void;
  configuredProviders: string[];
  defaultProvider?: string;
}

// Local storage key for input history
const INPUT_HISTORY_KEY = 'flowmason:input-history';
const MAX_HISTORY = 10;

interface InputHistoryItem {
  inputs: Record<string, unknown>;
  timestamp: string;
  pipelineId?: string;
}

export function RunInputPanel({
  inputSchema,
  sampleInput,
  stages,
  isRunning,
  onRun,
  configuredProviders,
  defaultProvider,
}: RunInputPanelProps) {
  const [inputs, setInputs] = useState<Record<string, unknown>>({});
  const [isExpanded, setIsExpanded] = useState(true);
  const [isJsonMode, setIsJsonMode] = useState(false);
  const [jsonValue, setJsonValue] = useState('{}');
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<InputHistoryItem[]>([]);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Load history from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(INPUT_HISTORY_KEY);
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    } catch {
      // Ignore
    }
  }, []);

  // Get schema properties
  const properties = inputSchema?.properties || {};
  const required = new Set(inputSchema?.required || []);

  // Check if any stage requires LLM
  const hasLLMStages = useMemo(() => {
    return stages.some((s) => {
      // Would need component info to check - assume based on llm_settings
      return s.llm_settings?.provider || s.llm_settings?.model;
    });
  }, [stages]);

  // Initialize inputs with defaults
  useEffect(() => {
    if (sampleInput) {
      setInputs(sampleInput);
      setJsonValue(JSON.stringify(sampleInput, null, 2));
    } else {
      const defaults: Record<string, unknown> = {};
      Object.entries(properties).forEach(([key, prop]) => {
        if ((prop as JsonSchemaProperty).default !== undefined) {
          defaults[key] = (prop as JsonSchemaProperty).default;
        }
      });
      setInputs(defaults);
      setJsonValue(JSON.stringify(defaults, null, 2));
    }
  }, [sampleInput, properties]);

  // Validate inputs
  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    // Check required fields
    required.forEach((field) => {
      if (inputs[field] === undefined || inputs[field] === '' || inputs[field] === null) {
        errors[field] = 'This field is required';
      }
    });

    // Type validation
    Object.entries(inputs).forEach(([key, value]) => {
      const prop = properties[key] as JsonSchemaProperty;
      if (!prop) return;

      if (prop.type === 'number' || prop.type === 'integer') {
        if (typeof value !== 'number' && isNaN(Number(value))) {
          errors[key] = `Must be a ${prop.type}`;
        }
      }
    });

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form field change
  const handleFieldChange = (field: string, value: unknown) => {
    const newInputs = { ...inputs, [field]: value };
    setInputs(newInputs);
    setJsonValue(JSON.stringify(newInputs, null, 2));

    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  // Handle JSON mode change
  const handleJsonChange = (value: string) => {
    setJsonValue(value);
    try {
      const parsed = JSON.parse(value);
      setInputs(parsed);
      setJsonError(null);
    } catch (err) {
      setJsonError(err instanceof Error ? err.message : 'Invalid JSON');
    }
  };

  // Handle run
  const handleRun = () => {
    if (isJsonMode && jsonError) {
      return;
    }

    if (!validate()) {
      return;
    }

    // Save to history
    const newHistory: InputHistoryItem[] = [
      { inputs, timestamp: new Date().toISOString() },
      ...history.slice(0, MAX_HISTORY - 1),
    ];
    setHistory(newHistory);
    try {
      localStorage.setItem(INPUT_HISTORY_KEY, JSON.stringify(newHistory));
    } catch {
      // Ignore
    }

    onRun(inputs);
  };

  // Load from history
  const loadFromHistory = (item: InputHistoryItem) => {
    setInputs(item.inputs);
    setJsonValue(JSON.stringify(item.inputs, null, 2));
    setShowHistory(false);
  };

  // Load sample input
  const loadSampleInput = () => {
    if (sampleInput) {
      setInputs(sampleInput);
      setJsonValue(JSON.stringify(sampleInput, null, 2));
    }
  };

  // Clear inputs
  const clearInputs = () => {
    setInputs({});
    setJsonValue('{}');
    setValidationErrors({});
  };

  const hasInputs = Object.keys(properties).length > 0;

  return (
    <TooltipProvider>
      <Card className="border-slate-200 dark:border-slate-700">
        {/* Header */}
        <button
          className="w-full flex items-center justify-between p-3 hover:bg-muted/50 transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-2">
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="w-4 h-4 text-muted-foreground" />
            )}
            <span className="font-medium">Pipeline Inputs</span>
            {hasInputs && (
              <Badge variant="secondary" className="text-xs">
                {Object.keys(properties).length} fields
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            {Object.keys(validationErrors).length > 0 && (
              <Badge variant="destructive" className="text-xs">
                {Object.keys(validationErrors).length} errors
              </Badge>
            )}
          </div>
        </button>

        {isExpanded && (
          <CardContent className="pt-0 pb-4">
            {/* Toolbar */}
            <div className="flex items-center gap-2 mb-4 pb-3 border-b">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={isJsonMode ? 'secondary' : 'ghost'}
                    size="sm"
                    className="h-7"
                    onClick={() => setIsJsonMode(!isJsonMode)}
                  >
                    <FileJson className="w-3.5 h-3.5 mr-1" />
                    JSON
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Toggle JSON Editor</TooltipContent>
              </Tooltip>

              {sampleInput && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-7" onClick={loadSampleInput}>
                      <Sparkles className="w-3.5 h-3.5 mr-1" />
                      Sample
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Load Sample Input</TooltipContent>
                </Tooltip>
              )}

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={showHistory ? 'secondary' : 'ghost'}
                    size="sm"
                    className="h-7"
                    onClick={() => setShowHistory(!showHistory)}
                    disabled={history.length === 0}
                  >
                    <History className="w-3.5 h-3.5 mr-1" />
                    History
                    {history.length > 0 && (
                      <Badge variant="secondary" className="ml-1 text-xs h-4 px-1">
                        {history.length}
                      </Badge>
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Previous Inputs</TooltipContent>
              </Tooltip>

              <div className="flex-1" />

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={clearInputs}>
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Clear Inputs</TooltipContent>
              </Tooltip>
            </div>

            {/* History dropdown */}
            {showHistory && history.length > 0 && (
              <div className="mb-4 p-2 bg-muted/50 rounded-lg space-y-1">
                <div className="text-xs text-muted-foreground mb-2">Recent inputs:</div>
                {history.slice(0, 5).map((item, index) => (
                  <button
                    key={index}
                    className="w-full text-left p-2 rounded hover:bg-muted text-xs flex items-center gap-2"
                    onClick={() => loadFromHistory(item)}
                  >
                    <History className="w-3 h-3 text-muted-foreground" />
                    <span className="flex-1 truncate font-mono">
                      {JSON.stringify(item.inputs).slice(0, 50)}...
                    </span>
                    <span className="text-muted-foreground">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </span>
                  </button>
                ))}
              </div>
            )}

            {/* Provider status */}
            {configuredProviders.length === 0 && hasLLMStages && (
              <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5" />
                <div className="text-xs">
                  <div className="font-medium text-amber-700 dark:text-amber-400">
                    No LLM providers configured
                  </div>
                  <div className="text-amber-600 dark:text-amber-500 mt-0.5">
                    Go to Settings to add API keys for LLM providers.
                  </div>
                </div>
              </div>
            )}

            {configuredProviders.length > 0 && hasLLMStages && (
              <div className="mb-4 p-2 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg flex items-center gap-2 text-xs">
                <Sparkles className="w-3.5 h-3.5 text-primary-500" />
                <span className="text-primary-700 dark:text-primary-400">
                  Using: {defaultProvider || configuredProviders[0]}
                </span>
                <Badge variant="secondary" className="text-xs h-4 px-1">
                  {configuredProviders.length} provider{configuredProviders.length !== 1 ? 's' : ''} ready
                </Badge>
              </div>
            )}

            {/* Form or JSON editor */}
            {isJsonMode ? (
              <div>
                <textarea
                  value={jsonValue}
                  onChange={(e) => handleJsonChange(e.target.value)}
                  className={cn(
                    'w-full h-48 p-3 font-mono text-xs rounded-lg border resize-none',
                    'bg-slate-50 dark:bg-slate-900',
                    jsonError
                      ? 'border-red-300 dark:border-red-700 focus:ring-red-500'
                      : 'border-slate-200 dark:border-slate-700 focus:ring-primary-500',
                    'focus:outline-none focus:ring-2'
                  )}
                  placeholder='{"key": "value"}'
                />
                {jsonError && (
                  <div className="mt-1 text-xs text-red-500 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    {jsonError}
                  </div>
                )}
              </div>
            ) : hasInputs ? (
              <div className="space-y-4">
                {Object.entries(properties).map(([fieldName, fieldSchema]) => {
                  const prop = fieldSchema as JsonSchemaProperty;
                  const isRequired = required.has(fieldName);
                  const error = validationErrors[fieldName];

                  return (
                    <div key={fieldName}>
                      <div className="flex items-center gap-2 mb-1.5">
                        <Label className="text-sm font-medium">
                          {fieldName}
                          {isRequired && <span className="text-red-500 ml-1">*</span>}
                        </Label>
                        {prop.description && (
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Info className="w-3.5 h-3.5 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent className="max-w-xs">
                              {prop.description}
                            </TooltipContent>
                          </Tooltip>
                        )}
                      </div>
                      <InputField
                        schema={prop}
                        value={inputs[fieldName]}
                        onChange={(value) => handleFieldChange(fieldName, value)}
                        error={error}
                      />
                      {error && (
                        <div className="mt-1 text-xs text-red-500 flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" />
                          {error}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-6 text-sm text-muted-foreground">
                <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <div>This pipeline has no input parameters.</div>
                <div className="text-xs mt-1">Click Run to execute the pipeline.</div>
              </div>
            )}

            {/* Run button */}
            <div className="mt-4 pt-4 border-t">
              <Button
                className="w-full"
                onClick={handleRun}
                disabled={isRunning || (isJsonMode && !!jsonError) || configuredProviders.length === 0}
              >
                {isRunning ? (
                  <>
                    <RotateCcw className="w-4 h-4 mr-2 animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Run Pipeline
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        )}
      </Card>
    </TooltipProvider>
  );
}

/**
 * Dynamic input field based on schema type
 */
interface InputFieldProps {
  schema: JsonSchemaProperty;
  value: unknown;
  onChange: (value: unknown) => void;
  error?: string;
}

function InputField({ schema, value, onChange, error }: InputFieldProps) {
  const displayValue = value === undefined || value === null ? '' : String(value);

  if (schema.enum) {
    return (
      <Select
        value={displayValue || '__empty__'}
        onValueChange={(v) => onChange(v === '__empty__' ? undefined : v)}
      >
        <SelectTrigger className={cn('h-9', error && 'border-red-300 dark:border-red-700')}>
          <SelectValue placeholder="Select..." />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="__empty__">-- Select --</SelectItem>
          {schema.enum.map((opt) => (
            <SelectItem key={String(opt)} value={String(opt)}>
              {String(opt)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    );
  }

  switch (schema.type) {
    case 'boolean':
      return (
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(e) => onChange(e.target.checked)}
            className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
          />
        </div>
      );

    case 'number':
    case 'integer':
      return (
        <Input
          type="number"
          value={displayValue}
          onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
          min={schema.minimum}
          max={schema.maximum}
          step={schema.type === 'integer' ? 1 : 'any'}
          placeholder={schema.default !== undefined ? `Default: ${schema.default}` : undefined}
          className={cn('h-9', error && 'border-red-300 dark:border-red-700')}
        />
      );

    case 'array':
    case 'object':
      return (
        <textarea
          value={typeof value === 'object' ? JSON.stringify(value, null, 2) : displayValue}
          onChange={(e) => {
            try {
              onChange(JSON.parse(e.target.value));
            } catch {
              onChange(e.target.value);
            }
          }}
          placeholder={schema.examples?.[0] ? `Example: ${JSON.stringify(schema.examples[0])}` : undefined}
          className={cn(
            'w-full h-24 p-2 text-sm font-mono rounded-md border resize-none',
            'bg-white dark:bg-slate-800',
            error
              ? 'border-red-300 dark:border-red-700'
              : 'border-slate-200 dark:border-slate-700',
            'focus:outline-none focus:ring-2 focus:ring-primary-500'
          )}
        />
      );

    default:
      // Check if it should be multiline
      const isMultiline =
        schema.description?.toLowerCase().includes('multi') ||
        (schema.maxLength && schema.maxLength > 200);

      if (isMultiline) {
        return (
          <textarea
            value={displayValue}
            onChange={(e) => onChange(e.target.value)}
            placeholder={
              schema.examples?.[0]
                ? `Example: ${String(schema.examples[0])}`
                : schema.default !== undefined
                ? `Default: ${schema.default}`
                : undefined
            }
            className={cn(
              'w-full h-24 p-2 text-sm rounded-md border resize-none',
              'bg-white dark:bg-slate-800',
              error
                ? 'border-red-300 dark:border-red-700'
                : 'border-slate-200 dark:border-slate-700',
              'focus:outline-none focus:ring-2 focus:ring-primary-500'
            )}
          />
        );
      }

      return (
        <Input
          type="text"
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          placeholder={
            schema.examples?.[0]
              ? `Example: ${String(schema.examples[0])}`
              : schema.default !== undefined
              ? `Default: ${schema.default}`
              : undefined
          }
          className={cn('h-9', error && 'border-red-300 dark:border-red-700')}
        />
      );
  }
}

export default RunInputPanel;
