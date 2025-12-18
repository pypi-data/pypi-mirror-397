/**
 * Operations Dashboard Page
 *
 * Displays execution metrics, pipeline statistics, activity feed,
 * and charts for monitoring pipeline operations.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  Play,
  RefreshCw,
  AlertCircle,
  BarChart3,
  Calendar,
  Loader2
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

// Types matching the backend API
interface ExecutionMetrics {
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  cancelled_runs: number;
  running_runs: number;
  success_rate: number;
  avg_duration_seconds: number | null;
}

interface PipelineMetrics {
  pipeline_id: string;
  pipeline_name: string;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  success_rate: number;
  avg_duration_seconds: number | null;
  last_run_at: string | null;
}

interface DailyStats {
  date: string;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
}

interface RecentActivity {
  run_id: string;
  pipeline_id: string;
  pipeline_name: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
}

interface DashboardOverview {
  metrics: ExecutionMetrics;
  top_pipelines: PipelineMetrics[];
  daily_stats: DailyStats[];
  recent_activity: RecentActivity[];
}

// Metric card component
function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = 'default'
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ComponentType<{ className?: string }>;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'default' | 'success' | 'danger' | 'warning';
}) {
  const colorClasses = {
    default: 'text-foreground',
    success: 'text-green-500',
    danger: 'text-red-500',
    warning: 'text-yellow-500',
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${colorClasses[color]}`} />
      </CardHeader>
      <CardContent>
        <div className={`text-2xl font-bold ${colorClasses[color]}`}>{value}</div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
            {trend === 'up' && <TrendingUp className="h-3 w-3 text-green-500" />}
            {trend === 'down' && <TrendingUp className="h-3 w-3 text-red-500 rotate-180" />}
            {subtitle}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

// Status badge component
function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline'; label: string }> = {
    completed: { variant: 'default', label: 'Completed' },
    success: { variant: 'default', label: 'Success' },
    failed: { variant: 'destructive', label: 'Failed' },
    running: { variant: 'secondary', label: 'Running' },
    pending: { variant: 'outline', label: 'Pending' },
    cancelled: { variant: 'outline', label: 'Cancelled' },
  };

  const config = variants[status] || { variant: 'outline' as const, label: status };

  return (
    <Badge variant={config.variant} className="capitalize">
      {status === 'running' && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
      {status === 'completed' && <CheckCircle className="mr-1 h-3 w-3" />}
      {status === 'failed' && <XCircle className="mr-1 h-3 w-3" />}
      {config.label}
    </Badge>
  );
}

// Simple bar chart for daily stats
function DailyChart({ data }: { data: DailyStats[] }) {
  const maxValue = Math.max(...data.map(d => d.total_runs), 1);

  return (
    <div className="space-y-2">
      <div className="flex items-end justify-between h-32 gap-1">
        {data.slice(-14).map((day, i) => {
          const successHeight = (day.successful_runs / maxValue) * 100;
          const failedHeight = (day.failed_runs / maxValue) * 100;

          return (
            <div key={day.date} className="flex-1 flex flex-col items-center gap-0.5">
              <div className="w-full flex flex-col-reverse h-24">
                <div
                  className="bg-green-500 rounded-t-sm transition-all"
                  style={{ height: `${successHeight}%` }}
                />
                <div
                  className="bg-red-500 rounded-t-sm transition-all"
                  style={{ height: `${failedHeight}%` }}
                />
              </div>
              {i % 2 === 0 && (
                <span className="text-[10px] text-muted-foreground">
                  {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              )}
            </div>
          );
        })}
      </div>
      <div className="flex justify-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <div className="w-3 h-3 bg-green-500 rounded-sm" /> Success
        </span>
        <span className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-500 rounded-sm" /> Failed
        </span>
      </div>
    </div>
  );
}

// Activity feed component
function ActivityFeed({ activities }: { activities: RecentActivity[] }) {
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return '-';
    if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
  };

  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div
          key={activity.run_id}
          className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${
              activity.status === 'completed' ? 'bg-green-500/10' :
              activity.status === 'failed' ? 'bg-red-500/10' :
              activity.status === 'running' ? 'bg-blue-500/10' : 'bg-gray-500/10'
            }`}>
              {activity.status === 'completed' && <CheckCircle className="h-4 w-4 text-green-500" />}
              {activity.status === 'failed' && <XCircle className="h-4 w-4 text-red-500" />}
              {activity.status === 'running' && <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />}
              {!['completed', 'failed', 'running'].includes(activity.status) &&
                <Clock className="h-4 w-4 text-gray-500" />}
            </div>
            <div>
              <p className="font-medium text-sm">{activity.pipeline_name}</p>
              <p className="text-xs text-muted-foreground">
                {formatTime(activity.started_at)}
                {activity.duration_seconds !== null && ` • ${formatDuration(activity.duration_seconds)}`}
              </p>
            </div>
          </div>
          <StatusBadge status={activity.status} />
        </div>
      ))}
      {activities.length === 0 && (
        <div className="text-center text-muted-foreground py-8">
          <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>No recent activity</p>
        </div>
      )}
    </div>
  );
}

// Pipeline stats table
function PipelineStatsTable({ pipelines }: { pipelines: PipelineMetrics[] }) {
  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return '-';
    if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="text-left py-3 px-2 text-sm font-medium text-muted-foreground">Pipeline</th>
            <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Runs</th>
            <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Success Rate</th>
            <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Avg Duration</th>
          </tr>
        </thead>
        <tbody>
          {pipelines.map((pipeline) => (
            <tr key={pipeline.pipeline_id} className="border-b last:border-0 hover:bg-muted/50">
              <td className="py-3 px-2">
                <span className="font-medium text-sm">{pipeline.pipeline_name}</span>
              </td>
              <td className="text-right py-3 px-2">
                <span className="text-sm">{pipeline.total_runs}</span>
              </td>
              <td className="text-right py-3 px-2">
                <span className={`text-sm ${
                  pipeline.success_rate >= 0.9 ? 'text-green-500' :
                  pipeline.success_rate >= 0.7 ? 'text-yellow-500' : 'text-red-500'
                }`}>
                  {(pipeline.success_rate * 100).toFixed(0)}%
                </span>
              </td>
              <td className="text-right py-3 px-2">
                <span className="text-sm text-muted-foreground">
                  {formatDuration(pipeline.avg_duration_seconds)}
                </span>
              </td>
            </tr>
          ))}
          {pipelines.length === 0 && (
            <tr>
              <td colSpan={4} className="text-center py-8 text-muted-foreground">
                No pipeline data available
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

// Main Operations Page
export function OperationsPage() {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('7');
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setRefreshing(true);
      const response = await fetch(`/api/v1/analytics/overview?days=${timeRange}`);
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return '-';
    if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4">
        <AlertCircle className="h-12 w-12 text-red-500" />
        <p className="text-lg font-medium">Failed to load dashboard</p>
        <p className="text-muted-foreground">{error}</p>
        <Button onClick={fetchData}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </Button>
      </div>
    );
  }

  const metrics = data?.metrics;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Operations Dashboard</h1>
          <p className="text-muted-foreground">Monitor pipeline executions and performance</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[140px]">
              <Calendar className="mr-2 h-4 w-4" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Last 24 hours</SelectItem>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon" onClick={fetchData} disabled={refreshing}>
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Runs"
          value={metrics?.total_runs || 0}
          subtitle="All executions"
          icon={Play}
        />
        <MetricCard
          title="Success Rate"
          value={metrics ? `${(metrics.success_rate * 100).toFixed(1)}%` : '0%'}
          subtitle={`${metrics?.successful_runs || 0} successful`}
          icon={CheckCircle}
          color={metrics && metrics.success_rate >= 0.9 ? 'success' :
                 metrics && metrics.success_rate >= 0.7 ? 'warning' : 'danger'}
        />
        <MetricCard
          title="Failed Runs"
          value={metrics?.failed_runs || 0}
          subtitle={metrics?.running_runs ? `${metrics.running_runs} running` : undefined}
          icon={XCircle}
          color={metrics && metrics.failed_runs > 0 ? 'danger' : 'default'}
        />
        <MetricCard
          title="Avg Duration"
          value={formatDuration(metrics?.avg_duration_seconds || null)}
          subtitle="Per execution"
          icon={Clock}
        />
      </div>

      {/* Charts and Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Execution History
            </CardTitle>
            <CardDescription>Daily run counts over time</CardDescription>
          </CardHeader>
          <CardContent>
            <DailyChart data={data?.daily_stats || []} />
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Recent Activity
            </CardTitle>
            <CardDescription>Latest pipeline executions</CardDescription>
          </CardHeader>
          <CardContent>
            <ActivityFeed activities={data?.recent_activity || []} />
          </CardContent>
        </Card>
      </div>

      {/* Pipeline Stats Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Top Pipelines
          </CardTitle>
          <CardDescription>Performance metrics by pipeline</CardDescription>
        </CardHeader>
        <CardContent>
          <PipelineStatsTable pipelines={data?.top_pipelines || []} />
        </CardContent>
      </Card>
    </div>
  );
}
