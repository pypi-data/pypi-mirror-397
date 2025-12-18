/**
 * Component Palette
 *
 * Displays available components from the registry with modern styling.
 * Components are loaded dynamically - NO hardcoded component types.
 * Supports collapsed mode to give more space to the canvas.
 */

import { useState, useMemo } from 'react';
import {
  Search,
  Box,
  Zap,
  GitBranch,
  ChevronDown,
  ChevronRight,
  Loader2,
  Sparkles,
  GripVertical,
  PanelLeftClose,
  PanelLeftOpen,
  // Additional icons used by components
  Globe,
  Code,
  Filter,
  Repeat,
  ShieldCheck,
  FileText,
  Variable,
  Share2,
  AlertTriangle,
  GitMerge,
  CornerDownLeft,
  Shield,
  ClipboardCheck,
  CheckCircle,
  ArrowUpCircle,
  type LucideIcon,
} from 'lucide-react';

/**
 * Map of Lucide icon names to their components.
 * Used to render the actual icon from component metadata.
 */
const ICON_MAP: Record<string, LucideIcon> = {
  // Default icons
  'box': Box,
  'zap': Zap,
  'git-branch': GitBranch,

  // AI/ML
  'sparkles': Sparkles,

  // Data transformation
  'code': Code,
  'filter': Filter,
  'variable': Variable,

  // Network
  'globe': Globe,
  'share-2': Share2,

  // Control flow
  'git-merge': GitMerge,
  'repeat': Repeat,
  'corner-down-left': CornerDownLeft,
  'shield': Shield,

  // Validation
  'shield-check': ShieldCheck,
  'clipboard-check': ClipboardCheck,
  'check-circle': CheckCircle,

  // Utility
  'file-text': FileText,
  'arrow-up-circle': ArrowUpCircle,
  'alert-triangle': AlertTriangle,
};

/**
 * Get the Lucide icon component for a given icon name.
 * Falls back to Box if the icon is not found.
 */
function getIconComponent(iconName?: string, componentKind?: string): LucideIcon {
  if (iconName && ICON_MAP[iconName]) {
    return ICON_MAP[iconName];
  }

  // Fallback based on component kind
  switch (componentKind) {
    case 'node':
      return Box;
    case 'control_flow':
      return GitBranch;
    case 'operator':
      return Zap;
    default:
      return Box;
  }
}
import { useComponents } from '../hooks/useComponents';
import type { ComponentInfo } from '../types';
import { Input, Badge, Button } from '@/components/ui';

interface ComponentPaletteProps {
  onComponentSelect?: (component: ComponentInfo) => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

export function ComponentPalette({ onComponentSelect, collapsed = false, onToggleCollapse }: ComponentPaletteProps) {
  const { components, loading, error } = useComponents();
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(['core'])
  );
  const [kindFilter, setKindFilter] = useState<'all' | 'node' | 'operator' | 'control_flow'>(
    'all'
  );

  // Group components by category
  const groupedComponents = useMemo(() => {
    const filtered = components.filter((c) => {
      // Filter by kind
      if (kindFilter !== 'all' && c.component_kind !== kindFilter) {
        return false;
      }

      // Filter by search term
      if (searchTerm) {
        const term = searchTerm.toLowerCase();
        return (
          c.name.toLowerCase().includes(term) ||
          c.component_type.toLowerCase().includes(term) ||
          c.description.toLowerCase().includes(term) ||
          c.tags.some((t) => t.toLowerCase().includes(term))
        );
      }

      return true;
    });

    // Group by category
    const groups: Record<string, ComponentInfo[]> = {};
    for (const component of filtered) {
      const category = component.category || 'uncategorized';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(component);
    }

    return groups;
  }, [components, searchTerm, kindFilter]);

  const toggleCategory = (category: string) => {
    const next = new Set(expandedCategories);
    if (next.has(category)) {
      next.delete(category);
    } else {
      next.add(category);
    }
    setExpandedCategories(next);
  };

  const handleDragStart = (
    e: React.DragEvent,
    component: ComponentInfo
  ) => {
    e.dataTransfer.setData(
      'application/fm-component',
      JSON.stringify(component)
    );
    e.dataTransfer.effectAllowed = 'copy';
  };

  // Collapsed sidebar - just show an expand button
  if (collapsed) {
    return (
      <div className="w-12 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full transition-all duration-200">
        <div className="p-2 border-b border-slate-200 dark:border-slate-800">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleCollapse}
            className="w-full p-2"
            title="Expand component palette"
          >
            <PanelLeftOpen className="w-5 h-5 text-slate-500" />
          </Button>
        </div>
        {/* Collapsed component list - just icons */}
        <div className="flex-1 overflow-y-auto p-1 space-y-1">
          {components.slice(0, 10).map((component) => {
            const Icon = getIconComponent(component.icon, component.component_kind);
            return (
              <div
                key={component.component_type}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 cursor-grab transition-colors"
                draggable
                onDragStart={(e) => {
                  e.dataTransfer.setData(
                    'application/fm-component',
                    JSON.stringify(component)
                  );
                  e.dataTransfer.effectAllowed = 'copy';
                }}
                title={`${component.name}: ${component.description}`}
              >
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-white"
                  style={{ backgroundColor: component.color }}
                >
                  <Icon className="w-4 h-4" />
                </div>
              </div>
            );
          })}
          {components.length > 10 && (
            <div className="text-xs text-slate-400 text-center py-2">
              +{components.length - 10}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full transition-all duration-200">
        <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Components</h2>
        </div>
        <div className="flex flex-col items-center justify-center p-8 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
          <span className="text-sm text-slate-500">Loading components...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full transition-all duration-200">
        <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Components</h2>
        </div>
        <div className="p-4 text-red-600 text-sm">{error}</div>
      </div>
    );
  }

  return (
    <div className="w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full transition-all duration-200">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary-500" />
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Components</h2>
          </div>
          {onToggleCollapse && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleCollapse}
              className="p-1.5 h-auto"
              title="Collapse component palette"
            >
              <PanelLeftClose className="w-4 h-4 text-slate-400 hover:text-slate-600" />
            </Button>
          )}
        </div>
        <p className="text-xs text-slate-500 mt-1">Drag components to the canvas</p>
      </div>

      {/* Search and filters */}
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            type="text"
            placeholder="Search components..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 h-9"
          />
        </div>

        <div className="flex gap-1 flex-wrap">
          <button
            onClick={() => setKindFilter('all')}
            className={`flex-1 min-w-[40px] px-2 py-1.5 text-xs font-medium rounded-md transition-colors ${
              kindFilter === 'all'
                ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setKindFilter('node')}
            className={`flex-1 min-w-[50px] px-2 py-1.5 text-xs font-medium rounded-md flex items-center justify-center gap-1 transition-colors ${
              kindFilter === 'node'
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <Box className="w-3 h-3" />
            Nodes
          </button>
          <button
            onClick={() => setKindFilter('operator')}
            className={`flex-1 min-w-[50px] px-2 py-1.5 text-xs font-medium rounded-md flex items-center justify-center gap-1 transition-colors ${
              kindFilter === 'operator'
                ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <Zap className="w-3 h-3" />
            Ops
          </button>
          <button
            onClick={() => setKindFilter('control_flow')}
            className={`flex-1 min-w-[50px] px-2 py-1.5 text-xs font-medium rounded-md flex items-center justify-center gap-1 transition-colors ${
              kindFilter === 'control_flow'
                ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <GitBranch className="w-3 h-3" />
            Flow
          </button>
        </div>
      </div>

      {/* Component list */}
      <div className="flex-1 overflow-y-auto p-3">
        {Object.keys(groupedComponents).length === 0 ? (
          <div className="text-center text-slate-500 text-sm py-8">
            <Box className="w-8 h-8 mx-auto mb-2 text-slate-300" />
            No components found
          </div>
        ) : (
          Object.entries(groupedComponents)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([category, categoryComponents]) => (
              <div key={category} className="mb-3">
                <button
                  onClick={() => toggleCategory(category)}
                  className="flex items-center gap-2 w-full text-left text-sm font-semibold text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-slate-100 mb-2 group"
                >
                  {expandedCategories.has(category) ? (
                    <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-slate-600" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600" />
                  )}
                  <span className="capitalize">{category}</span>
                  <Badge variant="secondary" className="text-xs px-1.5 py-0">
                    {categoryComponents.length}
                  </Badge>
                </button>

                {expandedCategories.has(category) && (
                  <div className="space-y-2 ml-1">
                    {categoryComponents.map((component) => (
                      <ComponentItem
                        key={component.component_type}
                        component={component}
                        onSelect={onComponentSelect}
                        onDragStart={handleDragStart}
                      />
                    ))}
                  </div>
                )}
              </div>
            ))
        )}
      </div>
    </div>
  );
}

interface ComponentItemProps {
  component: ComponentInfo;
  onSelect?: (component: ComponentInfo) => void;
  onDragStart: (e: React.DragEvent, component: ComponentInfo) => void;
}

function ComponentItem({
  component,
  onSelect,
  onDragStart,
}: ComponentItemProps) {
  const Icon = getIconComponent(component.icon, component.component_kind);

  return (
    <div
      className="group p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 cursor-grab hover:border-primary-300 dark:hover:border-primary-600 hover:shadow-md transition-all active:cursor-grabbing"
      draggable
      onDragStart={(e) => onDragStart(e, component)}
      onClick={() => onSelect?.(component)}
    >
      <div className="flex items-start gap-3">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center text-white flex-shrink-0 shadow-sm"
          style={{ backgroundColor: component.color }}
        >
          <Icon className="w-4 h-4" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <span className="font-medium text-slate-900 dark:text-slate-100 text-sm truncate">
              {component.name}
            </span>
            {component.requires_llm && (
              <Sparkles className="w-3 h-3 text-amber-500 flex-shrink-0" />
            )}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 font-mono truncate">
            {component.component_type}
          </div>
          <div className="text-xs text-slate-400 dark:text-slate-500 line-clamp-2 mt-1">
            {component.description}
          </div>
        </div>
        <GripVertical className="w-4 h-4 text-slate-300 dark:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
      </div>

      {/* Tags */}
      {component.tags && component.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2 pl-12">
          {component.tags.slice(0, 3).map((tag) => (
            <Badge
              key={tag}
              variant="secondary"
              className="text-xs px-1.5 py-0 bg-slate-100 dark:bg-slate-700"
            >
              {tag}
            </Badge>
          ))}
          {component.tags.length > 3 && (
            <span className="text-xs text-slate-400">
              +{component.tags.length - 3}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default ComponentPalette;
