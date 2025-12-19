/**
 * Suggested Prompts Component
 *
 * Welcome screen with example prompts for the AI Pipeline Chat.
 * Displays when the conversation is empty.
 */

import {
  Sparkles,
  FileCheck,
  GitBranch,
  Repeat,
  Globe,
  Brain,
  Filter,
  ArrowRight,
} from 'lucide-react';

interface ExamplePrompt {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  prompt: string;
  gradient: string;
}

const EXAMPLE_PROMPTS: ExamplePrompt[] = [
  {
    id: 'data-validation',
    icon: <FileCheck className="w-6 h-6" />,
    title: 'Data Validation Pipeline',
    description: 'Validate and clean incoming data records',
    prompt:
      'Create a pipeline that validates customer records, checks required fields (id, email, name), filters out invalid entries, and outputs a summary with valid/invalid counts.',
    gradient: 'from-emerald-500 to-teal-600',
  },
  {
    id: 'content-classification',
    icon: <Brain className="w-6 h-6" />,
    title: 'AI Content Classification',
    description: 'Classify and route content using AI',
    prompt:
      'Build a pipeline that takes support ticket text, uses AI to classify priority (low/medium/high) and category (billing/technical/general), then routes based on priority.',
    gradient: 'from-violet-500 to-purple-600',
  },
  {
    id: 'batch-processing',
    icon: <Repeat className="w-6 h-6" />,
    title: 'Batch Processing',
    description: 'Process multiple items with foreach loop',
    prompt:
      'Create a pipeline that takes a list of documents, processes each one through an AI summarizer using foreach, then aggregates all summaries into a final report.',
    gradient: 'from-blue-500 to-indigo-600',
  },
  {
    id: 'api-integration',
    icon: <Globe className="w-6 h-6" />,
    title: 'API Data Transform',
    description: 'Fetch, transform, and forward API data',
    prompt:
      'Build a pipeline that fetches data from an external API, transforms the response to extract specific fields, validates the schema, and sends the result to another endpoint.',
    gradient: 'from-orange-500 to-red-600',
  },
  {
    id: 'conditional-routing',
    icon: <GitBranch className="w-6 h-6" />,
    title: 'Conditional Routing',
    description: 'Route data based on conditions',
    prompt:
      'Create a pipeline that takes an order, checks if the total exceeds $1000, routes high-value orders to a manager approval step, and standard orders directly to fulfillment.',
    gradient: 'from-cyan-500 to-blue-600',
  },
  {
    id: 'data-enrichment',
    icon: <Filter className="w-6 h-6" />,
    title: 'Data Enrichment',
    description: 'Enrich records with AI analysis',
    prompt:
      'Build a pipeline that takes customer feedback, uses AI to extract sentiment and key topics, enriches the original record with this analysis, and outputs the enhanced data.',
    gradient: 'from-pink-500 to-rose-600',
  },
];

interface SuggestedPromptsProps {
  onSelectPrompt: (prompt: string) => void;
}

export function SuggestedPrompts({ onSelectPrompt }: SuggestedPromptsProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-6 py-12">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-xl mb-6">
          <Sparkles className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-3">
          AI Pipeline Generator
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-lg mx-auto">
          Describe what you want to build in natural language and I'll create a pipeline for you.
        </p>
      </div>

      {/* Example Prompts Grid */}
      <div className="w-full max-w-4xl">
        <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4 text-center">
          Try one of these examples or type your own
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {EXAMPLE_PROMPTS.map((example) => (
            <button
              key={example.id}
              onClick={() => onSelectPrompt(example.prompt)}
              className="group relative flex flex-col items-start p-5 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-violet-300 dark:hover:border-violet-600 hover:shadow-lg transition-all text-left"
            >
              {/* Icon */}
              <div
                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${example.gradient} flex items-center justify-center text-white shadow-md mb-4`}
              >
                {example.icon}
              </div>

              {/* Content */}
              <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100 mb-1">
                {example.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                {example.description}
              </p>

              {/* Hover Arrow */}
              <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <ArrowRight className="w-5 h-5 text-violet-500" />
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Tips Section */}
      <div className="mt-12 max-w-2xl text-center">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          <span className="font-medium">Tip:</span> Be specific about your data inputs, processing
          steps, and desired outputs. Mention if you need AI processing, validation, loops, or
          conditional routing.
        </p>
      </div>
    </div>
  );
}

/**
 * Compact suggestions shown above the input area
 */
interface QuickSuggestionsProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
}

export function QuickSuggestions({ suggestions, onSelect }: QuickSuggestionsProps) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="flex items-center gap-2 px-4 py-2 overflow-x-auto">
      <span className="text-xs text-muted-foreground whitespace-nowrap">Suggestions:</span>
      {suggestions.map((suggestion, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(suggestion)}
          className="flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-violet-50 dark:hover:bg-violet-900/20 hover:border-violet-300 dark:hover:border-violet-600 hover:text-violet-700 dark:hover:text-violet-300 transition-all"
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}
