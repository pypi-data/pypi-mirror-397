/**
 * Packages Page
 *
 * Manage installed packages and deploy new ones with a polished UI.
 */

import { useState, useCallback } from 'react';
import {
  Package,
  Upload,
  Trash2,
  RefreshCw,
  Box,
  Zap,
  Loader2,
  AlertCircle,
  CheckCircle,
  Tag,
  Shield,
} from 'lucide-react';
import { useComponents, useRegistryStats } from '../hooks/useComponents';
import { registry } from '../services/api';
import type { ComponentInfo } from '../types';
import {
  Button,
  Card,
  CardContent,
  Badge,
} from '@/components/ui';

export function PackagesPage() {
  const { components, loading, error, refetch } = useComponents();
  const { stats, refetch: refetchStats } = useRegistryStats();
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const handleUpload = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      if (!file.name.endsWith('.fmpkg')) {
        setUploadError('Invalid file type. Please upload a .fmpkg file.');
        return;
      }

      setUploading(true);
      setUploadError(null);
      setUploadSuccess(null);

      try {
        await registry.deployPackage(file);
        setUploadSuccess(`Successfully deployed ${file.name}`);
        refetch();
        refetchStats();
      } catch (err) {
        setUploadError(
          err instanceof Error ? err.message : 'Failed to deploy package'
        );
      } finally {
        setUploading(false);
        // Reset file input
        event.target.value = '';
      }
    },
    [refetch, refetchStats]
  );

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await registry.refresh();
      await refetch();
      await refetchStats();
    } finally {
      setRefreshing(false);
    }
  }, [refetch, refetchStats]);

  const handleUnregister = useCallback(
    async (type: string) => {
      if (!confirm(`Are you sure you want to unregister "${type}"?`)) {
        return;
      }

      try {
        await registry.unregister(type);
        refetch();
        refetchStats();
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to unregister');
      }
    },
    [refetch, refetchStats]
  );

  // Group components by type
  const nodeComponents = components.filter((c) => c.component_kind === 'node');
  const operatorComponents = components.filter(
    (c) => c.component_kind === 'operator'
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Package className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">
                  Package Manager
                </h1>
                <p className="text-sm text-slate-500">
                  Install and manage FlowMason component packages
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                <RefreshCw
                  className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`}
                />
                Refresh
              </Button>

              <label className="cursor-pointer">
                <span className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2">
                  <Upload className="w-4 h-4" />
                  Deploy Package
                </span>
                <input
                  type="file"
                  accept=".fmpkg"
                  onChange={handleUpload}
                  disabled={uploading}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-4 gap-4 mb-8">
            <StatCard
              label="Total Components"
              value={stats.total_components}
              icon={<Package className="w-5 h-5" />}
              color="bg-primary-500"
            />
            <StatCard
              label="Nodes"
              value={stats.total_nodes}
              icon={<Box className="w-5 h-5" />}
              color="bg-blue-500"
            />
            <StatCard
              label="Operators"
              value={stats.total_operators}
              icon={<Zap className="w-5 h-5" />}
              color="bg-amber-500"
            />
            <StatCard
              label="Core Packages"
              value={stats.core_packages}
              icon={<Shield className="w-5 h-5" />}
              color="bg-emerald-500"
            />
          </div>
        )}

        {/* Upload feedback */}
        {uploadError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="font-medium">Upload Failed</p>
              <p className="text-sm text-red-600">{uploadError}</p>
            </div>
          </div>
        )}
        {uploadSuccess && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg flex items-center gap-3">
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="font-medium">Success</p>
              <p className="text-sm text-green-600">{uploadSuccess}</p>
            </div>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-primary-500 mb-4" />
            <p className="text-slate-500">Loading components...</p>
          </div>
        )}

        {/* Error state */}
        {error && (
          <Card className="max-w-md mx-auto border-red-200 bg-red-50">
            <CardContent className="pt-6 text-center">
              <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
              <p className="text-red-600">{error}</p>
              <Button variant="outline" className="mt-4" onClick={() => refetch()}>
                Retry
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Components list */}
        {!loading && !error && (
          <div className="space-y-8">
            {/* Nodes section */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Box className="w-5 h-5 text-blue-500" />
                <h2 className="text-lg font-semibold text-slate-900">
                  Nodes
                </h2>
                <Badge variant="secondary">{nodeComponents.length}</Badge>
              </div>
              <Card>
                <CardContent className="p-0 divide-y divide-slate-100">
                  {nodeComponents.length === 0 ? (
                    <div className="p-6 text-center text-slate-500">
                      <Box className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                      <p>No nodes installed</p>
                    </div>
                  ) : (
                    nodeComponents.map((component) => (
                      <ComponentRow
                        key={component.component_type}
                        component={component}
                        onUnregister={handleUnregister}
                      />
                    ))
                  )}
                </CardContent>
              </Card>
            </section>

            {/* Operators section */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-5 h-5 text-amber-500" />
                <h2 className="text-lg font-semibold text-slate-900">
                  Operators
                </h2>
                <Badge variant="secondary">{operatorComponents.length}</Badge>
              </div>
              <Card>
                <CardContent className="p-0 divide-y divide-slate-100">
                  {operatorComponents.length === 0 ? (
                    <div className="p-6 text-center text-slate-500">
                      <Zap className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                      <p>No operators installed</p>
                    </div>
                  ) : (
                    operatorComponents.map((component) => (
                      <ComponentRow
                        key={component.component_type}
                        component={component}
                        onUnregister={handleUnregister}
                      />
                    ))
                  )}
                </CardContent>
              </Card>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

function StatCard({ label, value, icon, color }: StatCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-xl ${color} text-white`}>{icon}</div>
          <div>
            <div className="text-3xl font-bold text-slate-900">{value}</div>
            <div className="text-sm text-slate-500">{label}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface ComponentRowProps {
  component: ComponentInfo;
  onUnregister: (type: string) => void;
}

function ComponentRow({ component, onUnregister }: ComponentRowProps) {
  const Icon = component.component_kind === 'node' ? Box : Zap;

  return (
    <div className="p-4 flex items-center gap-4 hover:bg-slate-50/50 transition-colors">
      <div
        className="w-12 h-12 rounded-xl flex items-center justify-center text-white flex-shrink-0 shadow-sm"
        style={{ backgroundColor: component.color }}
      >
        <Icon className="w-6 h-6" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-900">{component.name}</span>
          <Badge variant="outline">v{component.version}</Badge>
          {component.is_core && (
            <Badge variant="secondary" className="bg-primary-100 text-primary-700 border-0">
              <Shield className="w-3 h-3 mr-1" />
              Core
            </Badge>
          )}
          {component.requires_llm && (
            <Badge variant="warning" className="bg-amber-100 text-amber-700 border-0">
              LLM
            </Badge>
          )}
        </div>
        <div className="text-sm text-slate-500 font-mono mt-0.5">
          {component.component_type}
        </div>
        <div className="text-sm text-slate-400 mt-1 line-clamp-1">
          {component.description}
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {(component.tags || []).slice(0, 2).map((tag) => (
          <Badge key={tag} variant="secondary" className="text-xs">
            <Tag className="w-3 h-3 mr-1" />
            {tag}
          </Badge>
        ))}
      </div>

      <Button
        variant="ghost"
        size="sm"
        onClick={() => onUnregister(component.component_type)}
        disabled={component.is_core}
        className={`shrink-0 ${
          component.is_core
            ? 'text-slate-300 cursor-not-allowed'
            : 'text-slate-400 hover:text-red-600 hover:bg-red-50'
        }`}
        title={component.is_core ? 'Core components cannot be removed' : 'Unregister'}
      >
        <Trash2 className="w-4 h-4" />
      </Button>
    </div>
  );
}

export default PackagesPage;
