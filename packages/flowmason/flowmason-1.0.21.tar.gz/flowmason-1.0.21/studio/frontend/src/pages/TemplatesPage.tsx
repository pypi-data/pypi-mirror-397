/**
 * Templates Page
 *
 * Browse and use pipeline templates with a gallery-style UI.
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookTemplate,
  Loader2,
  Search,
  Rocket,
  FileEdit,
  Cloud,
  Search as SearchIcon,
  Link,
  CheckCircle,
  Layers,
  ArrowRight,
  Sparkles,
  User,
} from 'lucide-react';
import { templates as templatesApi, TemplateSummary } from '../services/api';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Badge,
  Input,
} from '@/components/ui';

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

export function TemplatesPage() {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<TemplateSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string | null>(null);
  const [instantiating, setInstantiating] = useState<string | null>(null);

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await templatesApi.list({
        category: selectedCategory || undefined,
        difficulty: selectedDifficulty || undefined,
      });
      setTemplates(response.templates);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, selectedDifficulty]);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  const handleUseTemplate = useCallback(async (templateId: string) => {
    setInstantiating(templateId);
    try {
      const pipeline = await templatesApi.instantiate(templateId);
      navigate(`/pipelines/${pipeline.id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create pipeline from template');
    } finally {
      setInstantiating(null);
    }
  }, [navigate]);

  // Filter templates by search query
  const filteredTemplates = templates.filter(template => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      template.name.toLowerCase().includes(query) ||
      template.description.toLowerCase().includes(query) ||
      template.tags.some(tag => tag.toLowerCase().includes(query))
    );
  });

  // Group templates by category
  const templatesByCategory: Record<string, TemplateSummary[]> = {};
  filteredTemplates.forEach(template => {
    const cat = template.category || 'custom';
    if (!templatesByCategory[cat]) {
      templatesByCategory[cat] = [];
    }
    templatesByCategory[cat].push(template);
  });

  const categories = Object.keys(CATEGORY_INFO);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <BookTemplate className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">Templates</h1>
                <p className="text-sm text-slate-500">Start with pre-built pipeline examples</p>
              </div>
            </div>

            {/* Search */}
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          {/* Category tabs */}
          <div className="flex items-center gap-2 mt-4 overflow-x-auto pb-2">
            <Button
              variant={selectedCategory === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(null)}
            >
              All
            </Button>
            {categories.map((cat) => {
              const info = CATEGORY_INFO[cat];
              return (
                <Button
                  key={cat}
                  variant={selectedCategory === cat ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(cat === selectedCategory ? null : cat)}
                  className="whitespace-nowrap"
                >
                  {info.icon}
                  <span className="ml-1">{info.name}</span>
                </Button>
              );
            })}
          </div>

          {/* Difficulty filter */}
          <div className="flex items-center gap-2 mt-2">
            <span className="text-sm text-slate-500">Difficulty:</span>
            {['beginner', 'intermediate', 'advanced'].map((diff) => (
              <button
                key={diff}
                onClick={() => setSelectedDifficulty(diff === selectedDifficulty ? null : diff)}
                className={`px-2 py-0.5 rounded text-xs font-medium transition-all ${
                  selectedDifficulty === diff
                    ? DIFFICULTY_COLORS[diff]
                    : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                }`}
              >
                {diff.charAt(0).toUpperCase() + diff.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-primary-500 mb-4" />
            <p className="text-slate-500">Loading templates...</p>
          </div>
        )}

        {error && (
          <Card className="max-w-md mx-auto mt-12 border-red-200 bg-red-50">
            <CardContent className="pt-6 text-center">
              <p className="text-red-600">{error}</p>
              <Button variant="outline" className="mt-4" onClick={fetchTemplates}>
                Retry
              </Button>
            </CardContent>
          </Card>
        )}

        {!loading && !error && filteredTemplates.length === 0 && (
          <div className="text-center py-20">
            <div className="inline-flex p-4 bg-slate-100 rounded-full mb-6">
              <BookTemplate className="w-12 h-12 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              No templates found
            </h3>
            <p className="text-slate-500 mb-6 max-w-sm mx-auto">
              {searchQuery
                ? 'Try adjusting your search or filters'
                : 'No templates are available in this category'}
            </p>
            {(searchQuery || selectedCategory || selectedDifficulty) && (
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory(null);
                  setSelectedDifficulty(null);
                }}
              >
                Clear filters
              </Button>
            )}
          </div>
        )}

        {!loading && !error && filteredTemplates.length > 0 && (
          <div className="space-y-10">
            {/* Show by category if no category filter, otherwise flat list */}
            {selectedCategory ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {filteredTemplates.map((template) => (
                  <TemplateCard
                    key={template.id}
                    template={template}
                    onUse={() => handleUseTemplate(template.id)}
                    loading={instantiating === template.id}
                  />
                ))}
              </div>
            ) : (
              Object.entries(templatesByCategory).map(([category, categoryTemplates]) => {
                const info = CATEGORY_INFO[category] || CATEGORY_INFO['custom'];
                return (
                  <div key={category}>
                    <div className="flex items-center gap-2 mb-4">
                      <div className={`p-2 rounded-lg ${info.color} text-white`}>
                        {info.icon}
                      </div>
                      <h2 className="text-lg font-semibold text-slate-900">{info.name}</h2>
                      <Badge variant="secondary" className="ml-2">
                        {categoryTemplates.length}
                      </Badge>
                    </div>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                      {categoryTemplates.map((template) => (
                        <TemplateCard
                          key={template.id}
                          template={template}
                          onUse={() => handleUseTemplate(template.id)}
                          loading={instantiating === template.id}
                        />
                      ))}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
}

interface TemplateCardProps {
  template: TemplateSummary;
  onUse: () => void;
  loading: boolean;
}

function TemplateCard({ template, onUse, loading }: TemplateCardProps) {
  const difficultyColor = DIFFICULTY_COLORS[template.difficulty] || DIFFICULTY_COLORS['custom'];

  return (
    <Card className="group hover:shadow-lg hover:shadow-slate-200/50 transition-all duration-200 hover:-translate-y-0.5 flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <CardTitle className="text-lg truncate">{template.name}</CardTitle>
              {template.source === 'user' && (
                <span title="User-created template">
                  <User className="w-3.5 h-3.5 text-slate-400" />
                </span>
              )}
            </div>
            <CardDescription className="line-clamp-2">
              {template.description || 'No description'}
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pb-3 flex-1">
        <div className="flex items-center gap-2 flex-wrap mb-3">
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${difficultyColor}`}>
            {template.difficulty.charAt(0).toUpperCase() + template.difficulty.slice(1)}
          </span>
          <Badge variant="outline">
            <Layers className="w-3 h-3 mr-1" />
            {template.stage_count} stages
          </Badge>
        </div>

        {template.use_cases && template.use_cases.length > 0 && (
          <ul className="text-sm text-slate-500 space-y-1">
            {template.use_cases.slice(0, 2).map((useCase, i) => (
              <li key={i} className="flex items-start gap-1.5">
                <span className="text-primary-500 mt-0.5">•</span>
                <span className="line-clamp-1">{useCase}</span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>

      <CardFooter className="pt-3 border-t border-slate-100">
        <Button
          className="w-full"
          onClick={onUse}
          disabled={loading}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <ArrowRight className="w-4 h-4 mr-2" />
          )}
          Use Template
        </Button>
      </CardFooter>
    </Card>
  );
}

export default TemplatesPage;
