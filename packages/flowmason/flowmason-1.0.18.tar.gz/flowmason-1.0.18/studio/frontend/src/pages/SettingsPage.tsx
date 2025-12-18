/**
 * Settings Page
 *
 * Configure provider API keys and application settings with a polished UI.
 */

import { useState, useEffect } from 'react';
import {
  Settings,
  Key,
  Check,
  X,
  Loader2,
  Eye,
  EyeOff,
  TestTube,
  Trash2,
  ExternalLink,
  Sparkles,
  Shield,
  RefreshCw,
  Server,
  AlertTriangle,
} from 'lucide-react';
import { settings as settingsApi } from '../services/api';
import type { AppSettingsResponse, ProviderSettingsResponse, ProviderTestResponse } from '../types';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Input,
  Badge,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui';

// Provider display info
const PROVIDER_INFO: Record<string, { name: string; description: string; docsUrl: string; color: string }> = {
  anthropic: {
    name: 'Anthropic',
    description: 'Claude models (Claude 3.5 Sonnet, Claude 3 Opus, etc.)',
    docsUrl: 'https://console.anthropic.com/settings/keys',
    color: 'bg-orange-500',
  },
  openai: {
    name: 'OpenAI',
    description: 'GPT models (GPT-4o, GPT-4 Turbo, etc.)',
    docsUrl: 'https://platform.openai.com/api-keys',
    color: 'bg-emerald-500',
  },
  google: {
    name: 'Google AI',
    description: 'Gemini models (Gemini Pro, etc.)',
    docsUrl: 'https://aistudio.google.com/app/apikey',
    color: 'bg-blue-500',
  },
  groq: {
    name: 'Groq',
    description: 'Fast inference (Llama, Mixtral, etc.)',
    docsUrl: 'https://console.groq.com/keys',
    color: 'bg-purple-500',
  },
};

interface ProviderCardProps {
  provider: string;
  settings: ProviderSettingsResponse;
  onKeySet: (provider: string, key: string) => Promise<void>;
  onKeyRemove: (provider: string) => Promise<void>;
  onTest: (provider: string) => Promise<ProviderTestResponse>;
}

function ProviderCard({ provider, settings, onKeySet, onKeyRemove, onTest }: ProviderCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<ProviderTestResponse | null>(null);

  const info = PROVIDER_INFO[provider] || {
    name: provider,
    description: 'AI provider',
    docsUrl: '#',
    color: 'bg-gray-500',
  };

  const handleSave = async () => {
    if (!apiKey.trim()) return;
    setIsSaving(true);
    try {
      await onKeySet(provider, apiKey.trim());
      setApiKey('');
      setIsEditing(false);
    } finally {
      setIsSaving(false);
    }
  };

  const handleTest = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const result = await onTest(provider);
      setTestResult(result);
    } finally {
      setIsTesting(false);
    }
  };

  const handleRemove = async () => {
    if (!confirm(`Remove API key for ${info.name}?`)) return;
    await onKeyRemove(provider);
    setTestResult(null);
  };

  return (
    <Card className="group hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-2 h-10 rounded-full ${info.color}`} />
            <div>
              <CardTitle className="text-base">{info.name}</CardTitle>
              <CardDescription className="text-sm">{info.description}</CardDescription>
            </div>
          </div>
          {settings.has_key ? (
            <Badge variant="success" className="shrink-0">
              <Check className="w-3 h-3 mr-1" />
              Configured
            </Badge>
          ) : (
            <Badge variant="secondary" className="shrink-0">
              Not configured
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {settings.has_key && !isEditing && (
          <div className="flex items-center gap-2">
            <code className="flex-1 px-3 py-2 bg-slate-100 text-slate-600 rounded-md font-mono text-sm">
              {settings.key_preview}
            </code>
            <Button
              variant="outline"
              size="sm"
              onClick={handleTest}
              disabled={isTesting}
            >
              {isTesting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <TestTube className="w-4 h-4" />
              )}
              <span className="ml-1.5">Test</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(true)}
            >
              <Key className="w-4 h-4" />
              <span className="ml-1.5">Change</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRemove}
              className="text-red-500 hover:text-red-600 hover:bg-red-50"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        )}

        {testResult && (
          <div
            className={`flex items-center gap-2 p-3 rounded-lg text-sm ${
              testResult.success
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {testResult.success ? (
              <Check className="w-4 h-4 shrink-0" />
            ) : (
              <X className="w-4 h-4 shrink-0" />
            )}
            <span>{testResult.message}</span>
          </div>
        )}

        {(isEditing || !settings.has_key) && (
          <div className="space-y-3">
            <div className="relative">
              <Input
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={settings.has_key ? 'Enter new API key' : 'Enter API key'}
                className="pr-10 font-mono"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
              >
                {showKey ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>

            <div className="flex items-center gap-2">
              <Button
                onClick={handleSave}
                disabled={!apiKey.trim() || isSaving}
                size="sm"
              >
                {isSaving && <Loader2 className="w-4 h-4 animate-spin mr-1.5" />}
                Save Key
              </Button>
              {settings.has_key && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setIsEditing(false);
                    setApiKey('');
                  }}
                >
                  Cancel
                </Button>
              )}
              <a
                href={info.docsUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 ml-auto"
              >
                Get API key
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        )}

        {settings.available_models.length > 0 && (
          <div className="pt-3 border-t border-slate-100">
            <p className="text-xs text-slate-500">
              <span className="font-medium">Available models:</span>{' '}
              {settings.available_models.slice(0, 3).join(', ')}
              {settings.available_models.length > 3 && (
                <span className="text-slate-400"> +{settings.available_models.length - 3} more</span>
              )}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function SettingsPage() {
  const [appSettings, setAppSettings] = useState<AppSettingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRestarting, setIsRestarting] = useState(false);
  const [restartMessage, setRestartMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await settingsApi.get();
      setAppSettings(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleKeySet = async (provider: string, key: string) => {
    await settingsApi.setProviderKey(provider, key);
    await loadSettings();
  };

  const handleKeyRemove = async (provider: string) => {
    await settingsApi.removeProviderKey(provider);
    await loadSettings();
  };

  const handleTest = async (provider: string) => {
    return settingsApi.testProvider(provider);
  };

  const handleRestart = async () => {
    setIsRestarting(true);
    setRestartMessage(null);
    try {
      const result = await settingsApi.restartBackend();
      setRestartMessage({ type: 'success', text: result.message });
      // The backend will restart, so we might lose connection briefly
      // After a delay, try to reconnect
      setTimeout(async () => {
        try {
          await loadSettings();
          setRestartMessage({ type: 'success', text: 'Backend restarted successfully!' });
        } catch {
          // Still restarting, that's okay
        }
        setIsRestarting(false);
      }, 2000);
    } catch (e) {
      setRestartMessage({
        type: 'error',
        text: e instanceof Error ? e.message : 'Failed to restart backend'
      });
      setIsRestarting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        <p className="text-slate-500">Loading settings...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <Card className="max-w-md mx-auto border-red-200 bg-red-50">
          <CardContent className="pt-6 text-center">
            <p className="text-red-600">{error}</p>
            <Button variant="outline" className="mt-4" onClick={loadSettings}>
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const configuredCount = appSettings
    ? Object.values(appSettings.providers).filter(p => p.has_key).length
    : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-slate-100 rounded-lg">
              <Settings className="w-6 h-6 text-slate-700" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-slate-900">Settings</h1>
              <p className="text-sm text-slate-500">Configure providers and application preferences</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
        {/* API Keys Section */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <h2 className="text-lg font-semibold text-slate-900">LLM Provider API Keys</h2>
            </div>
            <Badge variant={configuredCount > 0 ? 'success' : 'warning'}>
              {configuredCount} of {Object.keys(PROVIDER_INFO).length} configured
            </Badge>
          </div>

          <div className="flex items-center gap-2 mb-4 p-3 bg-slate-100 rounded-lg text-sm text-slate-600">
            <Shield className="w-4 h-4 shrink-0" />
            <span>Keys are stored locally on your machine and never sent to external servers.</span>
          </div>

          <div className="grid gap-4">
            {appSettings &&
              Object.entries(appSettings.providers).map(([provider, provSettings]) => (
                <ProviderCard
                  key={provider}
                  provider={provider}
                  settings={provSettings}
                  onKeySet={handleKeySet}
                  onKeyRemove={handleKeyRemove}
                  onTest={handleTest}
                />
              ))}
          </div>
        </section>

        {/* Application Settings Section */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Settings className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-900">Application Settings</h2>
          </div>

          <Card>
            <CardContent className="pt-6 space-y-6">
              <div className="flex items-center justify-between gap-4">
                <div className="space-y-1">
                  <Label className="text-base font-medium">Default Provider</Label>
                  <p className="text-sm text-slate-500">
                    Provider to use when a node doesn't specify one
                  </p>
                </div>
                <Select
                  value={appSettings?.default_provider || 'anthropic'}
                  onValueChange={async (value) => {
                    await settingsApi.update({ default_provider: value });
                    await loadSettings();
                  }}
                >
                  <SelectTrigger className="w-44">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.keys(PROVIDER_INFO).map((provider) => (
                      <SelectItem key={provider} value={provider}>
                        {PROVIDER_INFO[provider].name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="border-t border-slate-100 pt-6">
                <div className="flex items-center justify-between gap-4">
                  <div className="space-y-1">
                    <Label className="text-base font-medium">Auto-save Pipelines</Label>
                    <p className="text-sm text-slate-500">
                      Automatically save changes to pipelines
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={appSettings?.auto_save ?? true}
                      onChange={async (e) => {
                        await settingsApi.update({ auto_save: e.target.checked });
                        await loadSettings();
                      }}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-100 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600 shadow-inner"></div>
                  </label>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* System Section */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Server className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-900">System</h2>
          </div>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between gap-4">
                <div className="space-y-1">
                  <Label className="text-base font-medium">Restart Backend</Label>
                  <p className="text-sm text-slate-500">
                    Restart the backend server to apply configuration changes or recover from errors
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={handleRestart}
                  disabled={isRestarting}
                  className="shrink-0"
                >
                  {isRestarting ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <RefreshCw className="w-4 h-4 mr-2" />
                  )}
                  {isRestarting ? 'Restarting...' : 'Restart'}
                </Button>
              </div>

              {restartMessage && (
                <div
                  className={`mt-4 flex items-center gap-2 p-3 rounded-lg text-sm ${
                    restartMessage.type === 'success'
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}
                >
                  {restartMessage.type === 'success' ? (
                    <Check className="w-4 h-4 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 shrink-0" />
                  )}
                  <span>{restartMessage.text}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </section>
      </div>
    </div>
  );
}

export default SettingsPage;
