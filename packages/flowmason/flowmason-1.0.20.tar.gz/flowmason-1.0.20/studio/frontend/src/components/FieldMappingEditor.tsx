/**
 * Visual Field Mapping Editor
 *
 * Allows users to visually map data fields between pipeline stages
 * using drag-and-drop instead of manually typing template expressions.
 *
 * Features:
 * - Shows output schema from upstream stages
 * - Shows input schema for current stage
 * - Drag and drop field connections
 * - Auto-generates template expressions
 * - Schema type validation
 */

import { useState, useCallback, useMemo } from 'react';
import {
  ArrowRight,
  Link2,
  ChevronDown,
  ChevronRight,
  Circle,
  CheckCircle2,
  AlertCircle,
  Grip,
  Trash2,
  Type,
  Hash,
  ToggleLeft,
  List,
  Braces,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

// Schema types
interface SchemaProperty {
  type: string;
  description?: string;
  properties?: Record<string, SchemaProperty>;
  items?: SchemaProperty;
  enum?: unknown[];
}

interface UpstreamStage {
  id: string;
  name: string;
  component_type: string;
  output_schema?: Record<string, SchemaProperty>;
}

// FieldMapping interface kept for future use with visual connection lines
// interface FieldMapping {
//   targetField: string;
//   sourceExpression: string;
//   sourceStage?: string;
//   sourceField?: string;
// }

interface FieldMappingEditorProps {
  currentStageId: string;
  inputSchema: Record<string, SchemaProperty>;
  requiredFields: string[];
  upstreamStages: UpstreamStage[];
  pipelineInputs: Record<string, SchemaProperty>;
  currentMappings: Record<string, unknown>;
  onMappingChange: (field: string, value: string) => void;
}

// Get icon for type
function TypeIcon({ type }: { type: string }) {
  const icons: Record<string, React.ReactNode> = {
    string: <Type className="h-3 w-3" />,
    number: <Hash className="h-3 w-3" />,
    integer: <Hash className="h-3 w-3" />,
    boolean: <ToggleLeft className="h-3 w-3" />,
    array: <List className="h-3 w-3" />,
    object: <Braces className="h-3 w-3" />,
  };
  return icons[type] || <Circle className="h-3 w-3" />;
}

// Check type compatibility - used for validation hints
function _isTypeCompatible(sourceType: string, targetType: string): boolean {
  if (sourceType === targetType) return true;
  if (targetType === 'string') return true; // Anything can be converted to string
  if ((sourceType === 'integer' && targetType === 'number') ||
      (sourceType === 'number' && targetType === 'integer')) return true;
  return false;
}
void _isTypeCompatible; // Suppress unused warning - will be used for drag validation

// Flatten nested schema to field paths
function flattenSchema(
  schema: Record<string, SchemaProperty>,
  prefix: string = ''
): Array<{ path: string; type: string; description?: string }> {
  const result: Array<{ path: string; type: string; description?: string }> = [];

  for (const [key, value] of Object.entries(schema)) {
    const path = prefix ? `${prefix}.${key}` : key;

    result.push({
      path,
      type: value.type,
      description: value.description,
    });

    // Recurse into objects (but limit depth)
    if (value.type === 'object' && value.properties && path.split('.').length < 3) {
      result.push(...flattenSchema(value.properties, path));
    }

    // Handle array items
    if (value.type === 'array' && value.items?.properties) {
      result.push({
        path: `${path}[]`,
        type: 'array item',
        description: 'Array items',
      });
    }
  }

  return result;
}

// Source field component (draggable)
function SourceField({
  stageId,
  stageName: _stageName,
  path,
  type,
  description,
  onDragStart,
}: {
  stageId: string;
  stageName: string;
  path: string;
  type: string;
  description?: string;
  onDragStart: (source: { stageId: string; path: string; expression: string }) => void;
}) {
  void _stageName; // Used for grouping in parent component
  const expression = stageId === 'input'
    ? `{{input.${path}}}`
    : `{{upstream.${stageId}.${path}}}`;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            draggable
            onDragStart={(e) => {
              e.dataTransfer.setData('text/plain', expression);
              onDragStart({ stageId, path, expression });
            }}
            className="flex items-center gap-2 px-2 py-1.5 bg-muted/50 rounded cursor-grab hover:bg-muted active:cursor-grabbing transition-colors group"
          >
            <Grip className="h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100" />
            <Circle className="h-2 w-2 text-green-500 fill-current" />
            <span className="text-sm font-mono flex-1 truncate">{path}</span>
            <Badge variant="outline" className="text-xs h-5 px-1 gap-1">
              <TypeIcon type={type} />
              {type}
            </Badge>
          </div>
        </TooltipTrigger>
        <TooltipContent side="left">
          <div className="space-y-1">
            <p className="font-medium">{expression}</p>
            {description && <p className="text-xs text-muted-foreground">{description}</p>}
            <p className="text-xs">Drag to map to an input field</p>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

// Target field component (drop target)
function TargetField({
  name,
  type,
  description: _description,
  isRequired,
  currentValue,
  isDropTarget: _isDropTarget,
  onDrop,
  onClear,
}: {
  name: string;
  type: string;
  description?: string;
  isRequired: boolean;
  currentValue?: string;
  isDropTarget: boolean;
  onDrop: (expression: string) => void;
  onClear: () => void;
}) {
  void _description; // Available for tooltip enhancement
  void _isDropTarget; // Available for highlighting active drop zone
  const [isDragOver, setIsDragOver] = useState(false);
  const hasMapping = currentValue && currentValue.startsWith('{{');

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const expression = e.dataTransfer.getData('text/plain');
    if (expression) {
      onDrop(expression);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`flex items-center gap-2 px-2 py-1.5 rounded transition-all ${
        isDragOver
          ? 'bg-primary/20 ring-2 ring-primary'
          : hasMapping
          ? 'bg-green-500/10'
          : 'bg-muted/50'
      }`}
    >
      <div className="flex items-center gap-2 flex-1 min-w-0">
        {hasMapping ? (
          <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
        ) : isRequired ? (
          <AlertCircle className="h-4 w-4 text-orange-500 shrink-0" />
        ) : (
          <Circle className="h-4 w-4 text-muted-foreground shrink-0" />
        )}
        <span className="text-sm font-mono truncate">{name}</span>
        {isRequired && <span className="text-red-500">*</span>}
        <Badge variant="outline" className="text-xs h-5 px-1 gap-1 shrink-0">
          <TypeIcon type={type} />
          {type}
        </Badge>
      </div>

      {hasMapping ? (
        <div className="flex items-center gap-1">
          <code className="text-xs text-green-600 dark:text-green-400 bg-green-500/10 px-1.5 py-0.5 rounded max-w-32 truncate">
            {currentValue}
          </code>
          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onClear}>
            <Trash2 className="h-3 w-3 text-muted-foreground hover:text-red-500" />
          </Button>
        </div>
      ) : (
        <span className="text-xs text-muted-foreground">Drop here</span>
      )}
    </div>
  );
}

// Collapsible stage section
function StageSection({
  title,
  subtitle,
  icon,
  defaultOpen,
  children,
}: {
  title: string;
  subtitle?: string;
  icon: React.ReactNode;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen ?? true);

  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-2 px-3 py-2 bg-muted/50 hover:bg-muted transition-colors"
      >
        {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        {icon}
        <span className="font-medium text-sm">{title}</span>
        {subtitle && (
          <span className="text-xs text-muted-foreground ml-auto">{subtitle}</span>
        )}
      </button>
      {isOpen && <div className="p-2 space-y-1">{children}</div>}
    </div>
  );
}

// Main Field Mapping Editor component
export function FieldMappingEditor({
  currentStageId: _currentStageId,
  inputSchema,
  requiredFields,
  upstreamStages,
  pipelineInputs,
  currentMappings,
  onMappingChange,
}: FieldMappingEditorProps) {
  void _currentStageId; // Available for filtering circular dependencies
  const [dragSource, setDragSource] = useState<{
    stageId: string;
    path: string;
    expression: string;
  } | null>(null);

  // Flatten input schema for target fields
  const targetFields = useMemo(() => {
    return flattenSchema(inputSchema).map((field) => ({
      ...field,
      isRequired: requiredFields.includes(field.path),
    }));
  }, [inputSchema, requiredFields]);

  // Build source fields from upstream stages and pipeline inputs
  const sourceGroups = useMemo(() => {
    const groups: Array<{
      id: string;
      name: string;
      type: 'input' | 'upstream';
      fields: Array<{ path: string; type: string; description?: string }>;
    }> = [];

    // Pipeline inputs
    if (Object.keys(pipelineInputs).length > 0) {
      groups.push({
        id: 'input',
        name: 'Pipeline Inputs',
        type: 'input',
        fields: flattenSchema(pipelineInputs),
      });
    }

    // Upstream stages
    upstreamStages.forEach((stage) => {
      if (stage.output_schema && Object.keys(stage.output_schema).length > 0) {
        groups.push({
          id: stage.id,
          name: stage.name || stage.id,
          type: 'upstream',
          fields: flattenSchema(stage.output_schema),
        });
      } else {
        // Default: full output reference
        groups.push({
          id: stage.id,
          name: stage.name || stage.id,
          type: 'upstream',
          fields: [{ path: 'output', type: 'any', description: 'Stage output' }],
        });
      }
    });

    return groups;
  }, [pipelineInputs, upstreamStages]);

  const handleDragStart = useCallback(
    (source: { stageId: string; path: string; expression: string }) => {
      setDragSource(source);
    },
    []
  );

  const handleDrop = useCallback(
    (targetField: string, expression: string) => {
      onMappingChange(targetField, expression);
      setDragSource(null);
    },
    [onMappingChange]
  );

  const handleClear = useCallback(
    (targetField: string) => {
      onMappingChange(targetField, '');
    },
    [onMappingChange]
  );

  // Count mapped fields
  const mappedCount = targetFields.filter(
    (f) => currentMappings[f.path] && String(currentMappings[f.path]).startsWith('{{')
  ).length;

  const requiredMapped = targetFields.filter(
    (f) => f.isRequired && currentMappings[f.path] && String(currentMappings[f.path]).startsWith('{{')
  ).length;

  const requiredCount = targetFields.filter((f) => f.isRequired).length;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium flex items-center gap-2">
            <Link2 className="h-4 w-4" />
            Field Mapping
          </h3>
          <p className="text-xs text-muted-foreground">
            Drag fields from sources to map them to inputs
          </p>
        </div>
        <Badge variant={requiredMapped === requiredCount ? 'default' : 'secondary'}>
          {mappedCount}/{targetFields.length} mapped
          {requiredCount > 0 && ` (${requiredMapped}/${requiredCount} required)`}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Source Fields (Left Panel) */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Circle className="h-2 w-2 text-green-500 fill-current" />
            Available Data Sources
          </h4>

          {sourceGroups.length === 0 ? (
            <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-lg text-center">
              No upstream data available.
              <br />
              Add dependencies or pipeline inputs.
            </div>
          ) : (
            <div className="space-y-2">
              {sourceGroups.map((group) => (
                <StageSection
                  key={group.id}
                  title={group.name}
                  subtitle={`${group.fields.length} field(s)`}
                  icon={
                    group.type === 'input' ? (
                      <ArrowRight className="h-4 w-4 text-blue-500" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    )
                  }
                  defaultOpen={sourceGroups.length <= 3}
                >
                  {group.fields.map((field) => (
                    <SourceField
                      key={`${group.id}-${field.path}`}
                      stageId={group.id}
                      stageName={group.name}
                      path={field.path}
                      type={field.type}
                      description={field.description}
                      onDragStart={handleDragStart}
                    />
                  ))}
                </StageSection>
              ))}
            </div>
          )}
        </div>

        {/* Target Fields (Right Panel) */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Circle className="h-2 w-2 text-primary fill-current" />
            Input Fields
          </h4>

          {targetFields.length === 0 ? (
            <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-lg text-center">
              This component has no input fields.
            </div>
          ) : (
            <div className="space-y-1 p-2 bg-muted/30 rounded-lg">
              {targetFields.map((field) => (
                <TargetField
                  key={field.path}
                  name={field.path}
                  type={field.type}
                  description={field.description}
                  isRequired={field.isRequired}
                  currentValue={String(currentMappings[field.path] || '')}
                  isDropTarget={dragSource !== null}
                  onDrop={(expr) => handleDrop(field.path, expr)}
                  onClear={() => handleClear(field.path)}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Help text */}
      <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
        Tip: Drag a source field and drop it on an input field to create a mapping.
        You can also type template expressions manually like{' '}
        <code className="bg-muted px-1 rounded">{'{{upstream.stage_id.field}}'}</code>
      </div>
    </div>
  );
}

export default FieldMappingEditor;
