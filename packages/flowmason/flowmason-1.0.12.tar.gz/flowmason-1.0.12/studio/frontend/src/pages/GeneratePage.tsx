/**
 * AI Pipeline Generation Page
 *
 * Interactive interface for generating pipelines from natural language descriptions.
 * Uses LLM to understand user intent and generate valid FlowMason pipeline JSON.
 */

import { useState, useCallback } from 'react';
import {
  Wand2,
  Sparkles,
  RefreshCw,
  Download,
  Copy,
  Check,
  ChevronRight,
  Loader2,
  AlertCircle,
  Info,
  Lightbulb,
  Code,
  FileJson,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useNavigate } from 'react-router-dom';

// Example prompts for quick start
const EXAMPLE_PROMPTS = [
  {
    title: 'Data Validation',
    description: 'Validate incoming JSON records against a schema',
    prompt: 'Create a pipeline that takes a list of customer records, validates each one has required fields (id, email, name), filters out invalid records, and outputs a summary with valid/invalid counts.',
  },
  {
    title: 'Content Triage',
    description: 'Classify and route support tickets',
    prompt: 'Build a pipeline that takes a support ticket text, uses AI to classify its priority (low/medium/high) and category (billing/technical/general), then routes it to the appropriate output based on priority.',
  },
  {
    title: 'Data Transformation',
    description: 'Transform and enrich API data',
    prompt: 'Create a pipeline that fetches data from an API endpoint, transforms the response to extract specific fields, filters for active items only, and formats the output as a report.',
  },
  {
    title: 'Batch Processing',
    description: 'Process items in parallel with aggregation',
    prompt: 'Build a pipeline that takes a list of items, processes each one through an AI summarizer using a foreach loop, then aggregates all summaries into a final report.',
  },
];

// Pipeline structure for preview
interface GeneratedPipeline {
  name: string;
  version: string;
  description: string;
  input_schema: {
    type: string;
    properties: Record<string, unknown>;
    required?: string[];
  };
  stages: Array<{
    id: string;
    name: string;
    component_type: string;
    config: Record<string, unknown>;
    depends_on: string[];
  }>;
  output_stage_id: string;
}

export function GeneratePage() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedPipeline, setGeneratedPipeline] = useState<GeneratedPipeline | null>(null);
  const [copied, setCopied] = useState(false);
   const [useAiInterpreter, setUseAiInterpreter] = useState(true);

  // Generate pipeline from prompt
  const handleGenerate = useCallback(async () => {
    if (!prompt.trim()) return;

    setGenerating(true);
    setError(null);

    try {
      // Call the backend generation endpoint
      const response = await fetch('/api/v1/generate/pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: prompt,
          options: {
            include_validation: true,
            include_logging: true,
            use_ai_interpreter: useAiInterpreter,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || 'Failed to generate pipeline');
      }

      const data = await response.json();
      setGeneratedPipeline(data.pipeline || data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');

      // Generate a mock pipeline for demo purposes if API fails
      const mockPipeline = generateMockPipeline(prompt);
      setGeneratedPipeline(mockPipeline);
    } finally {
      setGenerating(false);
    }
  }, [prompt, useAiInterpreter]);

  // Generate a simple mock pipeline based on keywords
  const generateMockPipeline = (description: string): GeneratedPipeline => {
    const hasValidation = description.toLowerCase().includes('validat');
    const hasFilter = description.toLowerCase().includes('filter');
    const hasAI = description.toLowerCase().includes('ai') || description.toLowerCase().includes('classify');
    const hasTransform = description.toLowerCase().includes('transform');

    const stages: GeneratedPipeline['stages'] = [];

    // Start with logging
    stages.push({
      id: 'log-start',
      name: 'Log Start',
      component_type: 'logger',
      config: {
        message: 'Pipeline execution started',
        level: 'info',
        data: '{{input}}',
      },
      depends_on: [],
    });

    // Add validation if mentioned
    if (hasValidation) {
      stages.push({
        id: 'validate-input',
        name: 'Validate Input',
        component_type: 'schema_validate',
        config: {
          data: '{{input.data}}',
          json_schema: {
            type: 'object',
            required: ['id'],
            properties: {
              id: { type: 'string' },
            },
          },
          strict: false,
        },
        depends_on: ['log-start'],
      });
    }

    // Add AI classification if mentioned
    if (hasAI) {
      stages.push({
        id: 'classify',
        name: 'AI Classification',
        component_type: 'generator',
        config: {
          prompt: `Analyze and classify: {{${hasValidation ? 'upstream.validate-input.result' : 'input.data'}}}`,
          output_format: { type: 'object', properties: { category: { type: 'string' }, priority: { type: 'string' } } },
        },
        depends_on: [hasValidation ? 'validate-input' : 'log-start'],
      });
    }

    // Add filter if mentioned
    if (hasFilter) {
      const lastStage = stages[stages.length - 1];
      stages.push({
        id: 'filter-data',
        name: 'Filter Data',
        component_type: 'filter',
        config: {
          data: `{{upstream.${lastStage.id}.result}}`,
          condition: "item.get('active', True)",
          filter_mode: 'filter_array',
        },
        depends_on: [lastStage.id],
      });
    }

    // Add transform if mentioned
    if (hasTransform) {
      const lastStage = stages[stages.length - 1];
      stages.push({
        id: 'transform-data',
        name: 'Transform Data',
        component_type: 'json_transform',
        config: {
          data: `{{upstream.${lastStage.id}.result}}`,
          jmespath_expression: '@',
        },
        depends_on: [lastStage.id],
      });
    }

    // Add final logging
    const lastStage = stages[stages.length - 1];
    stages.push({
      id: 'log-complete',
      name: 'Log Complete',
      component_type: 'logger',
      config: {
        message: 'Pipeline execution completed',
        level: 'info',
        data: `{{upstream.${lastStage.id}.result}}`,
      },
      depends_on: [lastStage.id],
    });

    return {
      name: 'Generated Pipeline',
      version: '1.0.0',
      description: description.slice(0, 200),
      input_schema: {
        type: 'object',
        properties: {
          data: { type: 'object', description: 'Input data to process' },
        },
        required: ['data'],
      },
      stages,
      output_stage_id: 'log-complete',
    };
  };

  // Copy pipeline JSON to clipboard
  const handleCopy = useCallback(() => {
    if (generatedPipeline) {
      navigator.clipboard.writeText(JSON.stringify(generatedPipeline, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [generatedPipeline]);

  // Save pipeline and navigate to editor
  const handleSave = useCallback(async () => {
    if (!generatedPipeline) return;

    try {
      const response = await fetch('/api/v1/pipelines', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatedPipeline),
      });

      if (response.ok) {
        const saved = await response.json();
        navigate(`/pipelines/${saved.id}`);
      } else {
        throw new Error('Failed to save pipeline');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save pipeline');
    }
  }, [generatedPipeline, navigate]);

  // Use example prompt
  const handleExampleClick = (example: typeof EXAMPLE_PROMPTS[0]) => {
    setPrompt(example.prompt);
    setGeneratedPipeline(null);
    setError(null);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Wand2 className="h-6 w-6" />
          AI Pipeline Generator
        </h1>
        <p className="text-muted-foreground mt-1">
          Describe what you want to build in natural language and let AI generate the pipeline for you
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-6">
          {/* Prompt Input */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Describe Your Pipeline
              </CardTitle>
              <CardDescription>
                Tell us what you want the pipeline to do. Be as specific as possible.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Example: Create a pipeline that takes customer data, validates the email format, classifies customers by spending tier using AI, and outputs a summary report..."
                className="min-h-[200px] resize-y"
              />

              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useAiInterpreter}
                    onChange={(e) => setUseAiInterpreter(e.target.checked)}
                    className="h-3 w-3"
                  />
                  <span>Use AI interpreter pipeline for deeper understanding</span>
                </label>
              </div>

              <Button
                onClick={handleGenerate}
                disabled={!prompt.trim() || generating}
                className="w-full"
              >
                {generating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="mr-2 h-4 w-4" />
                    Generate Pipeline
                  </>
                )}
              </Button>

              {error && (
                <div className="flex items-start gap-2 text-sm text-amber-600 bg-amber-50 dark:bg-amber-900/20 p-3 rounded-lg">
                  <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                  <div>
                    <p className="font-medium">Note</p>
                    <p>{error}</p>
                    <p className="mt-1 text-xs">Showing a demo pipeline based on your description.</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Example Prompts */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-amber-500" />
                Example Prompts
              </CardTitle>
              <CardDescription>
                Click an example to get started quickly
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {EXAMPLE_PROMPTS.map((example, i) => (
                  <button
                    key={i}
                    onClick={() => handleExampleClick(example)}
                    className="w-full text-left p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{example.title}</span>
                      <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {example.description}
                    </p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Output Section */}
        <div className="space-y-6">
          {/* Generated Pipeline Preview */}
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FileJson className="h-5 w-5" />
                Generated Pipeline
              </CardTitle>
              {generatedPipeline && (
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="secondary">{generatedPipeline.stages.length} stages</Badge>
                  <Badge variant="outline">{generatedPipeline.version}</Badge>
                </div>
              )}
            </CardHeader>
            <CardContent>
              {generatedPipeline ? (
                <div className="space-y-4">
                  {/* Pipeline info */}
                  <div className="space-y-2">
                    <div>
                      <Label className="text-xs text-muted-foreground">Name</Label>
                      <p className="font-medium">{generatedPipeline.name}</p>
                    </div>
                    <div>
                      <Label className="text-xs text-muted-foreground">Description</Label>
                      <p className="text-sm text-muted-foreground">
                        {generatedPipeline.description}
                      </p>
                    </div>
                  </div>

                  {/* Stages list */}
                  <div>
                    <Label className="text-xs text-muted-foreground">Stages</Label>
                    <div className="mt-2 space-y-1">
                      {generatedPipeline.stages.map((stage, i) => (
                        <div
                          key={stage.id}
                          className="flex items-center gap-2 text-sm p-2 bg-muted/50 rounded"
                        >
                          <span className="w-5 h-5 rounded bg-primary/10 text-primary flex items-center justify-center text-xs font-medium">
                            {i + 1}
                          </span>
                          <span className="font-medium">{stage.name}</span>
                          <Badge variant="outline" className="ml-auto text-xs">
                            {stage.component_type}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* JSON Preview */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label className="text-xs text-muted-foreground">Pipeline JSON</Label>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleCopy}
                      >
                        {copied ? (
                          <>
                            <Check className="h-3 w-3 mr-1" /> Copied
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3 mr-1" /> Copy
                          </>
                        )}
                      </Button>
                    </div>
                    <pre className="text-xs bg-muted p-3 rounded-lg overflow-auto max-h-64 font-mono">
                      {JSON.stringify(generatedPipeline, null, 2)}
                    </pre>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button onClick={handleSave} className="flex-1">
                      <Download className="mr-2 h-4 w-4" />
                      Save & Open in Editor
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setGeneratedPipeline(null);
                        setPrompt('');
                      }}
                    >
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                  <Code className="h-12 w-12 mb-4 opacity-50" />
                  <p>Enter a description and click Generate</p>
                  <p className="text-sm mt-1">to create your pipeline</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Tips */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-start gap-3">
            <Info className="h-5 w-5 text-primary shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium">Tips for better results:</p>
              <ul className="list-disc list-inside mt-1 text-muted-foreground space-y-1">
                <li>Be specific about input and output data formats</li>
                <li>Mention if you need validation, filtering, or AI processing</li>
                <li>Describe the flow of data through the pipeline</li>
                <li>Include any business logic or conditional routing needs</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
