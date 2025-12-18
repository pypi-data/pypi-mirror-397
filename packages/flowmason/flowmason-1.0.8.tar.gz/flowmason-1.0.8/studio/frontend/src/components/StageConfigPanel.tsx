/**
 * Stage Configuration Panel
 *
 * Allows users to configure a selected stage's inputs.
 * Supports template variables for dynamic input mapping.
 *
 * Key features:
 * - Dynamic form based on component input schema
 * - Template variable autocomplete ({{input.x}}, {{upstream.y}})
 * - Provider/model selection for LLM stages
 * - LLM parameters (temperature, max_tokens, etc.)
 * - Type validation feedback
 * - Default value handling
 */

import { useState, useMemo, useCallback } from 'react';
import {
  X,
  Info,
  ChevronDown,
  ChevronRight,
  Cpu,
  Sliders,
  Sparkles,
  Copy,
  Check,
  Link2,
} from 'lucide-react';
import { FieldMappingEditor } from './FieldMappingEditor';
import { useSettings } from '../hooks/useSettings';
import type { ComponentInfo, PipelineStage, JsonSchemaProperty, LLMSettings } from '../types';
import {
  Button,
  Card,
  CardContent,
  Input,
  Badge,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Slider,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui';

// Model lists per provider
const PROVIDER_MODELS: Record<string, string[]> = {
  anthropic: [
    'claude-sonnet-4-20250514',
    'claude-opus-4-20250514',
    'claude-3-5-sonnet-20241022',
    'claude-3-5-haiku-20241022',
    'claude-3-opus-20240229',
  ],
  openai: [
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-4-turbo',
    'gpt-4',
    'gpt-3.5-turbo',
    'o1',
    'o1-mini',
  ],
  google: [
    'gemini-2.0-flash-exp',
    'gemini-1.5-pro',
    'gemini-1.5-flash',
    'gemini-1.0-pro',
  ],
  groq: [
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'mixtral-8x7b-32768',
    'gemma2-9b-it',
  ],
};

interface StageConfigPanelProps {
  stage: PipelineStage;
  component: ComponentInfo | null;
  upstreamStages: PipelineStage[];
  pipelineInputSchema: Record<string, JsonSchemaProperty>;
  onConfigChange: (stageId: string, config: Record<string, unknown>) => void;
  onLLMSettingsChange?: (stageId: string, settings: LLMSettings) => void;
  onClose: () => void;
}

export function StageConfigPanel({
  stage,
  component,
  upstreamStages,
  pipelineInputSchema,
  onConfigChange,
  onLLMSettingsChange,
  onClose,
}: StageConfigPanelProps) {
  const { settings, configuredProviders } = useSettings();
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['inputs', 'llm'])
  );

  if (!component) {
    return (
      <div className="w-80 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 flex flex-col h-full">
        <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <h3 className="font-medium text-slate-900 dark:text-slate-100">Configuration</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
        <div className="p-4 text-slate-500 dark:text-slate-400 text-sm">
          Component not found
        </div>
      </div>
    );
  }

  const inputSchema = component.input_schema || {};
  const properties = inputSchema.properties || {};
  const required = new Set(inputSchema.required || []);
  const requiresLLM = component.requires_llm;

  const toggleSection = (section: string) => {
    const next = new Set(expandedSections);
    if (next.has(section)) {
      next.delete(section);
    } else {
      next.add(section);
    }
    setExpandedSections(next);
  };

  const handleFieldChange = (field: string, value: unknown) => {
    onConfigChange(stage.id, {
      ...stage.config,
      [field]: value,
    });
  };

  const handleLLMSettingChange = useCallback(
    (key: keyof LLMSettings, value: unknown) => {
      const currentSettings = stage.llm_settings || {};
      const newSettings = { ...currentSettings, [key]: value };
      // Remove undefined/null values
      Object.keys(newSettings).forEach((k) => {
        if (newSettings[k as keyof LLMSettings] === undefined || newSettings[k as keyof LLMSettings] === null || newSettings[k as keyof LLMSettings] === '') {
          delete newSettings[k as keyof LLMSettings];
        }
      });
      onLLMSettingsChange?.(stage.id, newSettings);
    },
    [stage.id, stage.llm_settings, onLLMSettingsChange]
  );

  // Get available models for selected provider
  const selectedProvider = stage.llm_settings?.provider || settings?.default_provider || 'anthropic';
  const availableModels = PROVIDER_MODELS[selectedProvider] || [];

  // Build available template variables
  const templateVariables = useMemo(() => {
    const vars: { label: string; value: string; description: string }[] = [];

    // Pipeline input variables
    Object.entries(pipelineInputSchema).forEach(([key, prop]) => {
      vars.push({
        label: `input.${key}`,
        value: `{{input.${key}}}`,
        description: prop.description || `Pipeline input: ${key}`,
      });
    });

    // Upstream stage output variables
    upstreamStages.forEach((upstream) => {
      vars.push({
        label: `upstream.${upstream.id}`,
        value: `{{upstream.${upstream.id}}}`,
        description: `Output from ${upstream.name}`,
      });
    });

    // Context variables
    vars.push(
      { label: 'context.run_id', value: '{{context.run_id}}', description: 'Current run ID' },
      { label: 'context.timestamp', value: '{{context.timestamp}}', description: 'Execution timestamp' }
    );

    return vars;
  }, [pipelineInputSchema, upstreamStages]);

  return (
    <div className="w-80 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div className="min-w-0">
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 truncate">{stage.name}</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-mono truncate">{component.component_type}</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} className="shrink-0">
          <X className="w-4 h-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Component description */}
        <Card className="bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
          <CardContent className="p-3">
            <p className="text-sm text-slate-600 dark:text-slate-300">{component.description}</p>
            {requiresLLM && (
              <div className="mt-2 flex items-center gap-1.5">
                <Badge variant="warning" className="text-xs">
                  <Sparkles className="w-3 h-3 mr-1" />
                  Requires LLM
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>

        {/* LLM Settings section - only for components that require LLM */}
        {requiresLLM && (
          <div>
            <button
              onClick={() => toggleSection('llm')}
              className="flex items-center gap-2 w-full text-left font-medium text-slate-700 dark:text-slate-300 mb-2 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
            >
              {expandedSections.has('llm') ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
              <Cpu className="w-4 h-4 text-primary-500" />
              LLM Settings
            </button>

            {expandedSections.has('llm') && (
              <Card className="bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800">
                <CardContent className="p-3 space-y-4">
                  {/* Provider Selection */}
                  <div className="space-y-1.5">
                    <Label className="text-xs font-medium text-slate-600 dark:text-slate-400">Provider</Label>
                    <Select
                      value={stage.llm_settings?.provider || '__default__'}
                      onValueChange={(value) => handleLLMSettingChange('provider', value === '__default__' ? undefined : value)}
                    >
                      <SelectTrigger className="h-9 bg-white dark:bg-slate-800">
                        <SelectValue placeholder={`Default (${settings?.default_provider || 'anthropic'})`} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__default__">Default ({settings?.default_provider || 'anthropic'})</SelectItem>
                        {(configuredProviders.length > 0 ? configuredProviders : Object.keys(PROVIDER_MODELS)).map((p) => (
                          <SelectItem key={p} value={p}>
                            {p.charAt(0).toUpperCase() + p.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {configuredProviders.length === 0 && (
                      <p className="text-xs text-amber-600 dark:text-amber-400">
                        No providers configured. Go to Settings to add API keys.
                      </p>
                    )}
                  </div>

                  {/* Model Selection */}
                  <div className="space-y-1.5">
                    <Label className="text-xs font-medium text-slate-600 dark:text-slate-400">Model</Label>
                    <Select
                      value={stage.llm_settings?.model || '__default__'}
                      onValueChange={(value) => handleLLMSettingChange('model', value === '__default__' ? undefined : value)}
                    >
                      <SelectTrigger className="h-9 bg-white dark:bg-slate-800">
                        <SelectValue placeholder="Default" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__default__">Default</SelectItem>
                        {availableModels.map((m) => (
                          <SelectItem key={m} value={m}>
                            {m}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Advanced LLM Parameters */}
                  <div className="border-t border-primary-200 dark:border-primary-700 pt-3">
                    <button
                      onClick={() => toggleSection('llm-advanced')}
                      className="flex items-center gap-2 w-full text-left text-sm text-slate-600 dark:text-slate-400 mb-2 hover:text-slate-900 dark:hover:text-slate-200"
                    >
                      {expandedSections.has('llm-advanced') ? (
                        <ChevronDown className="w-3 h-3" />
                      ) : (
                        <ChevronRight className="w-3 h-3" />
                      )}
                      <Sliders className="w-3 h-3" />
                      Advanced Parameters
                    </button>

                    {expandedSections.has('llm-advanced') && (
                      <div className="space-y-4 mt-3">
                        {/* Temperature */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <Label className="text-xs font-medium text-slate-600 dark:text-slate-400">Temperature</Label>
                            <Badge variant="secondary" className="text-xs font-mono">
                              {stage.llm_settings?.temperature ?? 0.7}
                            </Badge>
                          </div>
                          <Slider
                            value={[stage.llm_settings?.temperature ?? 0.7]}
                            min={0}
                            max={1}
                            step={0.1}
                            onValueChange={([value]) => handleLLMSettingChange('temperature', value)}
                            className="w-full"
                          />
                          <div className="flex justify-between text-xs text-slate-400 dark:text-slate-500">
                            <span>Precise</span>
                            <span>Creative</span>
                          </div>
                        </div>

                        {/* Max Tokens */}
                        <div className="space-y-1.5">
                          <Label className="text-xs font-medium text-slate-600 dark:text-slate-400">Max Tokens</Label>
                          <Input
                            type="number"
                            placeholder="4096"
                            min={1}
                            max={128000}
                            value={stage.llm_settings?.max_tokens || ''}
                            onChange={(e) =>
                              handleLLMSettingChange(
                                'max_tokens',
                                e.target.value ? parseInt(e.target.value, 10) : undefined
                              )
                            }
                            className="h-9 bg-white dark:bg-slate-800"
                          />
                        </div>

                        {/* Top P */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <Label className="text-xs font-medium text-slate-600 dark:text-slate-400">Top P</Label>
                            <Badge variant="secondary" className="text-xs font-mono">
                              {stage.llm_settings?.top_p ?? 1.0}
                            </Badge>
                          </div>
                          <Slider
                            value={[stage.llm_settings?.top_p ?? 1.0]}
                            min={0}
                            max={1}
                            step={0.05}
                            onValueChange={([value]) => handleLLMSettingChange('top_p', value)}
                            className="w-full"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Input fields section */}
        <div>
          <button
            onClick={() => toggleSection('inputs')}
            className="flex items-center gap-2 w-full text-left font-medium text-slate-700 dark:text-slate-300 mb-2 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
          >
            {expandedSections.has('inputs') ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            Input Fields
            <Badge variant="secondary" className="text-xs ml-auto">
              {Object.keys(properties).length}
            </Badge>
          </button>

          {expandedSections.has('inputs') && (
            <div className="space-y-4">
              {Object.entries(properties).map(([fieldName, fieldSchema]) => (
                <FieldInput
                  key={fieldName}
                  name={fieldName}
                  schema={fieldSchema as JsonSchemaProperty}
                  value={stage.config[fieldName]}
                  isRequired={required.has(fieldName)}
                  templateVariables={templateVariables}
                  onChange={(value) => handleFieldChange(fieldName, value)}
                />
              ))}

              {Object.keys(properties).length === 0 && (
                <p className="text-sm text-slate-500 dark:text-slate-400 italic">
                  No input fields required
                </p>
              )}
            </div>
          )}
        </div>

        {/* Template variables section */}
        <div>
          <button
            onClick={() => toggleSection('variables')}
            className="flex items-center gap-2 w-full text-left font-medium text-slate-700 dark:text-slate-300 mb-2 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
          >
            {expandedSections.has('variables') ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            Available Variables
            <Badge variant="secondary" className="text-xs ml-auto">
              {templateVariables.length}
            </Badge>
          </button>

          {expandedSections.has('variables') && (
            <div className="space-y-2">
              {templateVariables.map((v) => (
                <TemplateVariableItem key={v.value} variable={v} />
              ))}
            </div>
          )}
        </div>

        {/* Visual Field Mapping section */}
        <div>
          <button
            onClick={() => toggleSection('mapping')}
            className="flex items-center gap-2 w-full text-left font-medium text-slate-700 dark:text-slate-300 mb-2 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
          >
            {expandedSections.has('mapping') ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            <Link2 className="w-4 h-4 text-primary-500" />
            Visual Field Mapping
            <Badge variant="secondary" className="text-xs ml-auto">
              Drag & Drop
            </Badge>
          </button>

          {expandedSections.has('mapping') && (
            <Card className="bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
              <CardContent className="p-3">
                <FieldMappingEditor
                  currentStageId={stage.id}
                  inputSchema={properties as Record<string, any>}
                  requiredFields={Array.from(required)}
                  upstreamStages={upstreamStages.map(s => ({
                    id: s.id,
                    name: s.name,
                    component_type: s.component_type,
                    output_schema: {},
                  }))}
                  pipelineInputs={pipelineInputSchema as Record<string, any>}
                  currentMappings={stage.config}
                  onMappingChange={handleFieldChange}
                />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

interface TemplateVariableItemProps {
  variable: { label: string; value: string; description: string };
}

function TemplateVariableItem({ variable }: TemplateVariableItemProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(variable.value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={handleCopy}
            className="w-full p-2 bg-slate-50 dark:bg-slate-800 rounded-lg text-left hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors group"
          >
            <div className="flex items-center gap-2">
              <code className="text-sm text-primary-600 dark:text-primary-400 font-mono flex-1">
                {variable.value}
              </code>
              {copied ? (
                <Check className="w-3.5 h-3.5 text-green-500" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
              )}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{variable.description}</p>
          </button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Click to copy</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

interface FieldInputProps {
  name: string;
  schema: JsonSchemaProperty;
  value: unknown;
  isRequired: boolean;
  templateVariables: { label: string; value: string; description: string }[];
  onChange: (value: unknown) => void;
}

function FieldInput({
  name,
  schema,
  value,
  isRequired,
  onChange,
}: FieldInputProps) {
  const [showInfo, setShowInfo] = useState(false);

  // Determine input type based on schema
  const inputType = useMemo(() => {
    if (schema.enum) return 'select';
    switch (schema.type) {
      case 'boolean':
        return 'checkbox';
      case 'integer':
      case 'number':
        return 'number';
      case 'array':
      case 'object':
        return 'textarea';
      default:
        return schema.description?.includes('multi') ? 'textarea' : 'text';
    }
  }, [schema]);

  const displayValue = useMemo(() => {
    if (value === undefined || value === null) {
      return schema.default !== undefined ? String(schema.default) : '';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  }, [value, schema.default]);

  return (
    <Card className="border-slate-200 dark:border-slate-700">
      <CardContent className="p-3 space-y-2">
        <div className="flex items-center gap-2">
          <Label className="text-sm font-medium text-slate-700 dark:text-slate-300">
            {name}
            {isRequired && <span className="text-red-500 ml-1">*</span>}
          </Label>
          {schema.description && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    onClick={() => setShowInfo(!showInfo)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                  >
                    <Info className="w-4 h-4" />
                  </button>
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs">{schema.description}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>

        {showInfo && schema.description && (
          <p className="text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 p-2 rounded">
            {schema.description}
          </p>
        )}

        {inputType === 'select' && schema.enum ? (
          <Select
            value={displayValue || '__none__'}
            onValueChange={(value) => onChange(value === '__none__' ? undefined : value)}
          >
            <SelectTrigger className="h-9 bg-white dark:bg-slate-800">
              <SelectValue placeholder="-- Select --" />
            </SelectTrigger>
            <SelectContent>
              {!isRequired && <SelectItem value="__none__">-- Select --</SelectItem>}
              {schema.enum.map((opt) => (
                <SelectItem key={String(opt)} value={String(opt)}>
                  {String(opt)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ) : inputType === 'checkbox' ? (
          <div className="flex items-center">
            <input
              type="checkbox"
              className="rounded border-slate-300 dark:border-slate-600 text-primary-600 focus:ring-primary-500 dark:bg-slate-800"
              checked={Boolean(value ?? schema.default)}
              onChange={(e) => onChange(e.target.checked)}
            />
          </div>
        ) : inputType === 'number' ? (
          <Input
            type="number"
            value={displayValue}
            min={schema.minimum}
            max={schema.maximum}
            onChange={(e) => onChange(Number(e.target.value))}
            placeholder={schema.default !== undefined ? `Default: ${schema.default}` : undefined}
            className="h-9 bg-white dark:bg-slate-800"
          />
        ) : inputType === 'textarea' ? (
          <textarea
            className="w-full rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            rows={4}
            value={displayValue}
            onChange={(e) => {
              try {
                // Try to parse as JSON for objects/arrays
                const parsed = JSON.parse(e.target.value);
                onChange(parsed);
              } catch {
                onChange(e.target.value);
              }
            }}
            placeholder={
              schema.examples?.[0]
                ? `Example: ${JSON.stringify(schema.examples[0])}`
                : undefined
            }
          />
        ) : (
          <Input
            type="text"
            value={displayValue}
            onChange={(e) => onChange(e.target.value)}
            placeholder={
              schema.examples?.[0]
                ? `Example: ${String(schema.examples[0])}`
                : schema.default !== undefined
                ? `Default: ${schema.default}`
                : 'Use {{input.field}} for dynamic values'
            }
            className="h-9 bg-white dark:bg-slate-800"
          />
        )}

        {/* Type hint */}
        <p className="text-xs text-slate-400 dark:text-slate-500">
          Type: {schema.type}
          {schema.minimum !== undefined && ` (min: ${schema.minimum})`}
          {schema.maximum !== undefined && ` (max: ${schema.maximum})`}
        </p>
      </CardContent>
    </Card>
  );
}

export default StageConfigPanel;
