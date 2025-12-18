/**
 * Solutions Page
 *
 * Browse DevOps, Integration, and IT Operations solution templates.
 * Provides categorized access to pre-built pipelines for common infrastructure
 * and operational workflows.
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Briefcase,
  Loader2,
  Search,
  Rocket,
  Link,
  Server,
  ArrowRight,
  Layers,
  ExternalLink,
  BookOpen,
  Activity,
  Shield,
  RefreshCw,
  AlertTriangle,
  Zap,
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

// Solution categories with their metadata
const SOLUTION_CATEGORIES: Record<string, {
  name: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  description: string;
  tags: string[];
  docLink: string;
}> = {
  'devops': {
    name: 'DevOps & CI/CD',
    icon: <Rocket className="w-6 h-6" />,
    color: 'text-orange-600',
    bgColor: 'bg-orange-500',
    description: 'Deployment pipelines, infrastructure automation, and GitOps workflows',
    tags: ['devops', 'cicd', 'deployment', 'automation'],
    docLink: '/docs/12-devops-solutions/ci-cd-pipelines',
  },
  'integration': {
    name: 'Integration & APIs',
    icon: <Link className="w-6 h-6" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-500',
    description: 'REST API orchestration, webhooks, data sync, and ETL workflows',
    tags: ['integration', 'api', 'etl', 'orchestration'],
    docLink: '/docs/12-devops-solutions/api-integration',
  },
  'it-ops': {
    name: 'IT Operations',
    icon: <Server className="w-6 h-6" />,
    color: 'text-green-600',
    bgColor: 'bg-green-500',
    description: 'Monitoring, alerting, incident management, and health checks',
    tags: ['monitoring', 'alerting', 'incident-response', 'health-check', 'sre'],
    docLink: '/docs/12-devops-solutions/monitoring-alerting',
  },
};

const DIFFICULTY_COLORS: Record<string, string> = {
  'beginner': 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
  'intermediate': 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
  'advanced': 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  'custom': 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
};

export function SolutionsPage() {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<TemplateSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [instantiating, setInstantiating] = useState<string | null>(null);

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await templatesApi.list({});
      // Filter to only include templates that match solution categories
      const solutionTags = Object.values(SOLUTION_CATEGORIES).flatMap(c => c.tags);
      const filteredTemplates = response.templates.filter(template =>
        template.tags.some(tag => solutionTags.includes(tag.toLowerCase())) ||
        template.category === 'devops' ||
        template.category === 'integration' ||
        template.category === 'it-ops'
      );
      setTemplates(filteredTemplates);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load solutions');
    } finally {
      setLoading(false);
    }
  }, []);

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

  // Determine which category a template belongs to
  const getCategoryForTemplate = (template: TemplateSummary): string | null => {
    for (const [categoryKey, categoryInfo] of Object.entries(SOLUTION_CATEGORIES)) {
      if (template.category === categoryKey) return categoryKey;
      if (template.tags.some(tag => categoryInfo.tags.includes(tag.toLowerCase()))) {
        return categoryKey;
      }
    }
    return null;
  };

  // Filter templates by search query and category
  const filteredTemplates = templates.filter(template => {
    // Category filter
    if (selectedCategory) {
      const templateCategory = getCategoryForTemplate(template);
      if (templateCategory !== selectedCategory) return false;
    }

    // Search filter
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
    const category = getCategoryForTemplate(template) || 'other';
    if (!templatesByCategory[category]) {
      templatesByCategory[category] = [];
    }
    templatesByCategory[category].push(template);
  });

  // Count templates per category
  const getCategoryCount = (categoryKey: string): number => {
    return templates.filter(t => getCategoryForTemplate(t) === categoryKey).length;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                <Briefcase className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Solutions</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">DevOps, Integration & IT Operations pipelines</p>
              </div>
            </div>

            {/* Search */}
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search solutions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Category Cards */}
        {!selectedCategory && !searchQuery && (
          <div className="mb-10">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">Solution Categories</h2>
            <div className="grid gap-6 md:grid-cols-3">
              {Object.entries(SOLUTION_CATEGORIES).map(([key, category]) => (
                <Card
                  key={key}
                  className="group cursor-pointer hover:shadow-lg hover:shadow-slate-200/50 dark:hover:shadow-slate-900/50 transition-all duration-200 hover:-translate-y-0.5"
                  onClick={() => setSelectedCategory(key)}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className={`p-3 rounded-xl ${category.bgColor} text-white`}>
                        {category.icon}
                      </div>
                      <Badge variant="secondary">
                        {getCategoryCount(key)} templates
                      </Badge>
                    </div>
                    <CardTitle className="mt-4">{category.name}</CardTitle>
                    <CardDescription>{category.description}</CardDescription>
                  </CardHeader>
                  <CardFooter className="pt-0">
                    <Button variant="ghost" className="w-full group-hover:bg-slate-100 dark:group-hover:bg-slate-800">
                      Explore
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Category Filter Pills (when browsing) */}
        {(selectedCategory || searchQuery) && (
          <div className="flex items-center gap-2 mb-6 flex-wrap">
            <Button
              variant={selectedCategory === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(null)}
            >
              All Solutions
            </Button>
            {Object.entries(SOLUTION_CATEGORIES).map(([key, category]) => (
              <Button
                key={key}
                variant={selectedCategory === key ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(key === selectedCategory ? null : key)}
                className="whitespace-nowrap"
              >
                <span className={selectedCategory === key ? '' : category.color}>
                  {category.icon}
                </span>
                <span className="ml-1">{category.name}</span>
                <Badge variant="secondary" className="ml-2 text-xs">
                  {getCategoryCount(key)}
                </Badge>
              </Button>
            ))}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-primary-500 mb-4" />
            <p className="text-slate-500 dark:text-slate-400">Loading solutions...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <Card className="max-w-md mx-auto mt-12 border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
            <CardContent className="pt-6 text-center">
              <AlertTriangle className="w-10 h-10 text-red-500 mx-auto mb-4" />
              <p className="text-red-600 dark:text-red-400">{error}</p>
              <Button variant="outline" className="mt-4" onClick={fetchTemplates}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {!loading && !error && filteredTemplates.length === 0 && (
          <div className="text-center py-20">
            <div className="inline-flex p-4 bg-slate-100 dark:bg-slate-800 rounded-full mb-6">
              <Briefcase className="w-12 h-12 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
              No solutions found
            </h3>
            <p className="text-slate-500 dark:text-slate-400 mb-6 max-w-sm mx-auto">
              {searchQuery
                ? 'Try adjusting your search or filters'
                : 'No solution templates are available in this category'}
            </p>
            {(searchQuery || selectedCategory) && (
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory(null);
                }}
              >
                Clear filters
              </Button>
            )}
          </div>
        )}

        {/* Templates Grid */}
        {!loading && !error && filteredTemplates.length > 0 && (
          <div className="space-y-10">
            {selectedCategory ? (
              // Single category view
              <div>
                {selectedCategory && SOLUTION_CATEGORIES[selectedCategory] && (
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${SOLUTION_CATEGORIES[selectedCategory].bgColor} text-white`}>
                        {SOLUTION_CATEGORIES[selectedCategory].icon}
                      </div>
                      <div>
                        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                          {SOLUTION_CATEGORIES[selectedCategory].name}
                        </h2>
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          {SOLUTION_CATEGORIES[selectedCategory].description}
                        </p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" asChild>
                      <a href={SOLUTION_CATEGORIES[selectedCategory].docLink} target="_blank" rel="noopener noreferrer">
                        <BookOpen className="w-4 h-4 mr-2" />
                        Documentation
                        <ExternalLink className="w-3 h-3 ml-1" />
                      </a>
                    </Button>
                  </div>
                )}
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {filteredTemplates.map((template) => (
                    <SolutionCard
                      key={template.id}
                      template={template}
                      onUse={() => handleUseTemplate(template.id)}
                      loading={instantiating === template.id}
                    />
                  ))}
                </div>
              </div>
            ) : (
              // All categories view (grouped)
              Object.entries(templatesByCategory)
                .filter(([category]) => SOLUTION_CATEGORIES[category])
                .map(([category, categoryTemplates]) => {
                  const info = SOLUTION_CATEGORIES[category];
                  return (
                    <div key={category}>
                      <div className="flex items-center gap-3 mb-4">
                        <div className={`p-2 rounded-lg ${info.bgColor} text-white`}>
                          {info.icon}
                        </div>
                        <div>
                          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{info.name}</h2>
                          <p className="text-sm text-slate-500 dark:text-slate-400">{info.description}</p>
                        </div>
                        <Badge variant="secondary" className="ml-auto">
                          {categoryTemplates.length}
                        </Badge>
                      </div>
                      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {categoryTemplates.map((template) => (
                          <SolutionCard
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

        {/* Documentation Links */}
        {!loading && !error && !selectedCategory && !searchQuery && (
          <div className="mt-12 pt-8 border-t border-slate-200 dark:border-slate-700">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">Documentation</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <DocLink
                icon={<Activity className="w-5 h-5" />}
                title="CI/CD Pipelines"
                description="Build, test, deploy automation"
                href="/docs/12-devops-solutions/ci-cd-pipelines"
              />
              <DocLink
                icon={<Shield className="w-5 h-5" />}
                title="Incident Response"
                description="Auto-remediation workflows"
                href="/docs/12-devops-solutions/incident-response"
              />
              <DocLink
                icon={<Zap className="w-5 h-5" />}
                title="Monitoring"
                description="Health checks & alerting"
                href="/docs/12-devops-solutions/monitoring-alerting"
              />
              <DocLink
                icon={<Link className="w-5 h-5" />}
                title="API Integration"
                description="REST API orchestration"
                href="/docs/12-devops-solutions/api-integration"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

interface SolutionCardProps {
  template: TemplateSummary;
  onUse: () => void;
  loading: boolean;
}

function SolutionCard({ template, onUse, loading }: SolutionCardProps) {
  const difficultyColor = DIFFICULTY_COLORS[template.difficulty] || DIFFICULTY_COLORS['custom'];

  return (
    <Card className="group hover:shadow-lg hover:shadow-slate-200/50 dark:hover:shadow-slate-900/50 transition-all duration-200 hover:-translate-y-0.5 flex flex-col">
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
          <ul className="text-sm text-slate-500 dark:text-slate-400 space-y-1">
            {template.use_cases.slice(0, 2).map((useCase, i) => (
              <li key={i} className="flex items-start gap-1.5">
                <span className="text-primary-500 mt-0.5">•</span>
                <span className="line-clamp-1">{useCase}</span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>

      <CardFooter className="pt-3 border-t border-slate-100 dark:border-slate-800">
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
          Use Solution
        </Button>
      </CardFooter>
    </Card>
  );
}

interface DocLinkProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  href: string;
}

function DocLink({ icon, title, description, href }: DocLinkProps) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-start gap-3 p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors group"
    >
      <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg text-slate-600 dark:text-slate-400 group-hover:bg-primary-100 dark:group-hover:bg-primary-900 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1">
          <span className="font-medium text-slate-900 dark:text-slate-100">{title}</span>
          <ExternalLink className="w-3 h-3 text-slate-400" />
        </div>
        <p className="text-sm text-slate-500 dark:text-slate-400 truncate">{description}</p>
      </div>
    </a>
  );
}

export default SolutionsPage;
