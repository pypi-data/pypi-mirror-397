/**
 * Dashboard Screen
 *
 * Main dashboard showing pipeline stats and recent activity.
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { api } from '../services/api';
import { DashboardStats, PipelineRun } from '../types';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: keyof typeof Ionicons.glyphMap;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color }) => (
  <View style={[styles.statCard, { borderLeftColor: color }]}>
    <Ionicons name={icon} size={24} color={color} />
    <Text style={styles.statValue}>{value}</Text>
    <Text style={styles.statTitle}>{title}</Text>
  </View>
);

interface RunItemProps {
  run: PipelineRun;
  onPress: () => void;
}

const RunItem: React.FC<RunItemProps> = ({ run, onPress }) => {
  const statusColors: Record<string, string> = {
    completed: '#10B981',
    failed: '#EF4444',
    running: '#F59E0B',
    pending: '#6B7280',
    cancelled: '#9CA3AF',
  };

  const statusIcons: Record<string, keyof typeof Ionicons.glyphMap> = {
    completed: 'checkmark-circle',
    failed: 'close-circle',
    running: 'sync',
    pending: 'time',
    cancelled: 'stop-circle',
  };

  return (
    <TouchableOpacity style={styles.runItem} onPress={onPress}>
      <Ionicons
        name={statusIcons[run.status] || 'help-circle'}
        size={20}
        color={statusColors[run.status] || '#6B7280'}
      />
      <View style={styles.runInfo}>
        <Text style={styles.runName}>{run.pipeline_name}</Text>
        <Text style={styles.runTime}>
          {new Date(run.started_at).toLocaleString()}
        </Text>
      </View>
      {run.duration_ms && (
        <Text style={styles.runDuration}>{run.duration_ms}ms</Text>
      )}
    </TouchableOpacity>
  );
};

export const DashboardScreen: React.FC = () => {
  const navigation = useNavigation();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    const response = await api.getDashboard();
    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      setStats(response.data);
      setError(null);
    }
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchDashboard();
    setRefreshing(false);
  }, [fetchDashboard]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await fetchDashboard();
      setLoading(false);
    };
    load();
  }, [fetchDashboard]);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#6366F1" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Ionicons name="cloud-offline" size={48} color="#EF4444" />
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <Text style={styles.header}>Dashboard</Text>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <StatCard
          title="Pipelines"
          value={stats?.totalPipelines || 0}
          icon="layers"
          color="#6366F1"
        />
        <StatCard
          title="Active"
          value={stats?.activePipelines || 0}
          icon="pulse"
          color="#10B981"
        />
        <StatCard
          title="Runs Today"
          value={stats?.runsToday || 0}
          icon="play"
          color="#F59E0B"
        />
        <StatCard
          title="Success Rate"
          value={`${Math.round((stats?.successRate || 0) * 100)}%`}
          icon="checkmark-done"
          color="#14B8A6"
        />
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionsRow}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Pipelines' as never)}
          >
            <Ionicons name="add-circle" size={24} color="#6366F1" />
            <Text style={styles.actionText}>Run Pipeline</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('History' as never)}
          >
            <Ionicons name="time" size={24} color="#6366F1" />
            <Text style={styles.actionText}>View History</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Recent Runs */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Runs</Text>
        {stats?.recentRuns && stats.recentRuns.length > 0 ? (
          stats.recentRuns.map((run) => (
            <RunItem
              key={run.id}
              run={run}
              onPress={() =>
                navigation.navigate('RunDetail' as never, { runId: run.id } as never)
              }
            />
          ))
        ) : (
          <Text style={styles.emptyText}>No recent runs</Text>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    padding: 16,
    paddingTop: 24,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
  },
  statCard: {
    width: '46%',
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    margin: '2%',
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 8,
  },
  statTitle: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    width: '45%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  actionText: {
    color: '#374151',
    marginTop: 8,
    fontSize: 14,
  },
  runItem: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 1,
    elevation: 1,
  },
  runInfo: {
    flex: 1,
    marginLeft: 12,
  },
  runName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1F2937',
  },
  runTime: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  runDuration: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  emptyText: {
    color: '#9CA3AF',
    textAlign: 'center',
    padding: 16,
  },
  errorText: {
    color: '#EF4444',
    marginTop: 8,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#6366F1',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 16,
  },
  retryButtonText: {
    color: 'white',
    fontWeight: '600',
  },
});

export default DashboardScreen;
