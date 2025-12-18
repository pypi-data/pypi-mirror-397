/**
 * Pipelines Page
 *
 * List and manage pipelines with a polished card-based UI.
 */

import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { NewPipelineModal } from '../components/NewPipelineModal';
import {
  Plus,
  GitBranch,
  MoreVertical,
  Edit,
  Copy,
  Trash2,
  Play,
  Loader2,
  Calendar,
  Layers,
  CheckCircle,
  FileEdit,
} from 'lucide-react';
import { usePipelines } from '../hooks/usePipelines';
import { pipelines as pipelinesApi } from '../services/api';
import type { Pipeline } from '../types';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Badge,
} from '@/components/ui';

export function PipelinesPage() {
  const navigate = useNavigate();
  const { pipelines, loading, error, refetch } = usePipelines();
  const [showNewPipelineModal, setShowNewPipelineModal] = useState(false);

  const handleDelete = useCallback(
    async (id: string, name: string) => {
      if (!confirm(`Delete "${name}"?`)) return;

      try {
        await pipelinesApi.delete(id);
        refetch();
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to delete');
      }
    },
    [refetch]
  );

  const handleClone = useCallback(
    async (id: string) => {
      try {
        const cloned = await pipelinesApi.clone(id);
        refetch();
        navigate(`/pipelines/${cloned.id}`);
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to clone');
      }
    },
    [refetch, navigate]
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <GitBranch className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">Pipelines</h1>
                <p className="text-sm text-slate-500">Create and manage your AI workflows</p>
              </div>
            </div>

            <Button onClick={() => setShowNewPipelineModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              New Pipeline
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-primary-500 mb-4" />
            <p className="text-slate-500">Loading pipelines...</p>
          </div>
        )}

        {error && (
          <Card className="max-w-md mx-auto mt-12 border-red-200 bg-red-50">
            <CardContent className="pt-6 text-center">
              <p className="text-red-600">{error}</p>
              <Button variant="outline" className="mt-4" onClick={() => refetch()}>
                Retry
              </Button>
            </CardContent>
          </Card>
        )}

        {!loading && !error && pipelines.length === 0 && (
          <div className="text-center py-20">
            <div className="inline-flex p-4 bg-slate-100 rounded-full mb-6">
              <GitBranch className="w-12 h-12 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              No pipelines yet
            </h3>
            <p className="text-slate-500 mb-6 max-w-sm mx-auto">
              Create your first pipeline to start building AI workflows with connected components
            </p>
            <Button onClick={() => setShowNewPipelineModal(true)} size="lg">
              <Plus className="w-5 h-5 mr-2" />
              Create Your First Pipeline
            </Button>
          </div>
        )}

        {!loading && !error && pipelines.length > 0 && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {pipelines.map((pipeline) => (
              <PipelineCard
                key={pipeline.id}
                pipeline={pipeline}
                onEdit={() => navigate(`/pipelines/${pipeline.id}`)}
                onClone={() => handleClone(pipeline.id)}
                onDelete={() => handleDelete(pipeline.id, pipeline.name)}
              />
            ))}
          </div>
        )}
      </div>

      <NewPipelineModal
        open={showNewPipelineModal}
        onOpenChange={setShowNewPipelineModal}
      />
    </div>
  );
}

interface PipelineCardProps {
  pipeline: Pipeline;
  onEdit: () => void;
  onClone: () => void;
  onDelete: () => void;
}

function PipelineCard({ pipeline, onEdit, onClone, onDelete }: PipelineCardProps) {
  const [showMenu, setShowMenu] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <Card className="group hover:shadow-lg hover:shadow-slate-200/50 transition-all duration-200 hover:-translate-y-0.5">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg truncate">{pipeline.name}</CardTitle>
            <CardDescription className="line-clamp-2 mt-1">
              {pipeline.description || 'No description'}
            </CardDescription>
          </div>

          <div className="relative ml-2">
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={() => setShowMenu(!showMenu)}
            >
              <MoreVertical className="w-4 h-4" />
            </Button>

            {showMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowMenu(false)}
                />
                <div className="absolute right-0 top-full mt-1 w-40 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-20">
                  <button
                    onClick={() => {
                      setShowMenu(false);
                      onEdit();
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      setShowMenu(false);
                      onClone();
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                  >
                    <Copy className="w-4 h-4" />
                    Duplicate
                  </button>
                  <div className="border-t border-slate-100 my-1" />
                  <button
                    onClick={() => {
                      setShowMenu(false);
                      onDelete();
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pb-3">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Status badge - prominent placement */}
          {pipeline.status === 'published' ? (
            <Badge className="bg-green-100 text-green-700 border-green-200 hover:bg-green-100">
              <CheckCircle className="w-3 h-3 mr-1" />
              Published
            </Badge>
          ) : (
            <Badge className="bg-amber-100 text-amber-700 border-amber-200 hover:bg-amber-100">
              <FileEdit className="w-3 h-3 mr-1" />
              Draft
            </Badge>
          )}
          <Badge variant="secondary">{pipeline.category}</Badge>
          <Badge variant="outline">v{pipeline.version}</Badge>
        </div>
      </CardContent>

      <CardFooter className="pt-3 border-t border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-4 text-sm text-slate-500">
          <span className="flex items-center gap-1">
            <Layers className="w-4 h-4" />
            {pipeline.stage_count ?? pipeline.stages?.length ?? 0} stage{(pipeline.stage_count ?? pipeline.stages?.length ?? 0) !== 1 ? 's' : ''}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {formatDate(pipeline.updated_at)}
          </span>
        </div>

        <Button variant="secondary" size="sm" onClick={onEdit}>
          <Play className="w-4 h-4 mr-1" />
          Open
        </Button>
      </CardFooter>
    </Card>
  );
}

export default PipelinesPage;
