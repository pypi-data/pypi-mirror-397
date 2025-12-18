/**
 * New Pipeline Modal
 *
 * Modal for creating a new pipeline - either blank or from a template.
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Plus,
  BookTemplate,
  Loader2,
  Search,
  ArrowRight,
  Layers,
  Rocket,
  FileEdit,
  Cloud,
  Search as SearchIcon,
  Link,
  CheckCircle,
  Sparkles,
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  Button,
  Input,
  Badge,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from '@/components/ui';
import { pipelines as pipelinesApi, templates as templatesApi, TemplateSummary } from '../services/api';

interface NewPipelineModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const CATEGORY_INFO: Record<string, { name: string; icon: React.ReactNode; color: string }> = {
  'getting-started': { name: 'Getting Started', icon: <Rocket className="w-4 h-4" />, color: 'bg-blue-500' },
  'content': { name: 'Content Creation', icon: <FileEdit className="w-4 h-4" />, color: 'bg-purple-500' },
  'salesforce': { name: 'Salesforce & CRM', icon: <Cloud className="w-4 h-4" />, color: 'bg-cyan-500' },
  'analysis': { name: 'Analysis & Research', icon: <SearchIcon className="w-4 h-4" />, color: 'bg-amber-500' },
  'integration': { name: 'Data & Integration', icon: <Link className="w-4 h-4" />, color: 'bg-green-500' },
  'quality': { name: 'Quality Assurance', icon: <CheckCircle className="w-4 h-4" />, color: 'bg-rose-500' },
  'custom': { name: 'Custom', icon: <Sparkles className="w-4 h-4" />, color: 'bg-slate-500' },
};

const DIFFICULTY_COLORS: Record<string, string> = {
  'beginner': 'bg-green-100 text-green-700',
  'intermediate': 'bg-yellow-100 text-yellow-700',
  'advanced': 'bg-red-100 text-red-700',
  'custom': 'bg-slate-100 text-slate-700',
};

export function NewPipelineModal({ open, onOpenChange }: NewPipelineModalProps) {
  const navigate = useNavigate();
  const [tab, setTab] = useState<'blank' | 'template'>('blank');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('custom');
  const [creating, setCreating] = useState(false);

  // Template state
  const [templates, setTemplates] = useState<TemplateSummary[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);

  // Load templates when template tab is selected
  useEffect(() => {
    if (tab === 'template' && templates.length === 0) {
      setLoadingTemplates(true);
      templatesApi.list()
        .then(response => setTemplates(response.templates))
        .catch(console.error)
        .finally(() => setLoadingTemplates(false));
    }
  }, [tab, templates.length]);

  // Reset form when modal closes
  useEffect(() => {
    if (!open) {
      setName('');
      setDescription('');
      setCategory('custom');
      setSelectedTemplate(null);
      setSearchQuery('');
      setTab('blank');
    }
  }, [open]);

  const handleCreateBlank = useCallback(async () => {
    if (!name.trim()) return;
    setCreating(true);
    try {
      const pipeline = await pipelinesApi.create({
        name: name.trim(),
        description: description.trim(),
        category,
        version: '1.0.0',
        status: 'draft',
        stages: [],
        input_schema: { type: 'object', properties: {} },
        output_stage_id: '',
      });
      onOpenChange(false);
      navigate(`/pipelines/${pipeline.id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create pipeline');
    } finally {
      setCreating(false);
    }
  }, [name, description, category, navigate, onOpenChange]);

  const handleCreateFromTemplate = useCallback(async () => {
    if (!selectedTemplate) return;
    setCreating(true);
    try {
      const pipeline = await templatesApi.instantiate(
        selectedTemplate,
        name.trim() || undefined
      );
      onOpenChange(false);
      navigate(`/pipelines/${pipeline.id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create pipeline from template');
    } finally {
      setCreating(false);
    }
  }, [selectedTemplate, name, navigate, onOpenChange]);

  // Filter templates by search
  const filteredTemplates = templates.filter(template => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      template.name.toLowerCase().includes(query) ||
      template.description.toLowerCase().includes(query) ||
      template.tags.some(tag => tag.toLowerCase().includes(query))
    );
  });

  // Group by category
  const templatesByCategory: Record<string, TemplateSummary[]> = {};
  filteredTemplates.forEach(template => {
    const cat = template.category || 'custom';
    if (!templatesByCategory[cat]) {
      templatesByCategory[cat] = [];
    }
    templatesByCategory[cat].push(template);
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Create New Pipeline</DialogTitle>
          <DialogDescription>
            Start with a blank pipeline or choose from a template
          </DialogDescription>
        </DialogHeader>

        <Tabs value={tab} onValueChange={(v) => setTab(v as 'blank' | 'template')} className="flex-1 overflow-hidden flex flex-col">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="blank">
              <Plus className="w-4 h-4 mr-2" />
              Blank Pipeline
            </TabsTrigger>
            <TabsTrigger value="template">
              <BookTemplate className="w-4 h-4 mr-2" />
              From Template
            </TabsTrigger>
          </TabsList>

          <TabsContent value="blank" className="flex-1 overflow-auto mt-4">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Pipeline Name *
                </label>
                <Input
                  placeholder="My Pipeline"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Description
                </label>
                <Input
                  placeholder="What does this pipeline do?"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="custom">Custom</option>
                  <option value="content">Content Creation</option>
                  <option value="salesforce">Salesforce & CRM</option>
                  <option value="analysis">Analysis & Research</option>
                  <option value="integration">Data & Integration</option>
                  <option value="quality">Quality Assurance</option>
                </select>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="template" className="flex-1 overflow-hidden flex flex-col mt-4">
            {/* Search */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>

            {/* Optional custom name */}
            {selectedTemplate && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Custom Name (optional)
                </label>
                <Input
                  placeholder="Leave blank to use template name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            )}

            {/* Templates list */}
            <div className="flex-1 overflow-auto">
              {loadingTemplates ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-primary-500" />
                </div>
              ) : filteredTemplates.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  No templates found
                </div>
              ) : (
                <div className="space-y-4">
                  {Object.entries(templatesByCategory).map(([cat, catTemplates]) => {
                    const info = CATEGORY_INFO[cat] || CATEGORY_INFO['custom'];
                    return (
                      <div key={cat}>
                        <div className="flex items-center gap-2 mb-2">
                          <div className={`p-1.5 rounded ${info.color} text-white`}>
                            {info.icon}
                          </div>
                          <span className="text-sm font-medium text-slate-700">{info.name}</span>
                        </div>
                        <div className="grid gap-2">
                          {catTemplates.map((template) => (
                            <button
                              key={template.id}
                              onClick={() => setSelectedTemplate(template.id === selectedTemplate ? null : template.id)}
                              className={`w-full text-left p-3 rounded-lg border transition-all ${
                                selectedTemplate === template.id
                                  ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-500'
                                  : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                  <div className="font-medium text-slate-900 truncate">
                                    {template.name}
                                  </div>
                                  <div className="text-sm text-slate-500 line-clamp-1 mt-0.5">
                                    {template.description}
                                  </div>
                                </div>
                                <div className="flex items-center gap-2 ml-2">
                                  <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${DIFFICULTY_COLORS[template.difficulty] || DIFFICULTY_COLORS['custom']}`}>
                                    {template.difficulty}
                                  </span>
                                  <Badge variant="outline" className="text-xs">
                                    <Layers className="w-3 h-3 mr-1" />
                                    {template.stage_count}
                                  </Badge>
                                </div>
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          {tab === 'blank' ? (
            <Button onClick={handleCreateBlank} disabled={!name.trim() || creating}>
              {creating ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <ArrowRight className="w-4 h-4 mr-2" />
              )}
              Create Pipeline
            </Button>
          ) : (
            <Button onClick={handleCreateFromTemplate} disabled={!selectedTemplate || creating}>
              {creating ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <ArrowRight className="w-4 h-4 mr-2" />
              )}
              Use Template
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default NewPipelineModal;
