/**
 * History Screen
 *
 * Shows pipeline run history with filtering.
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { api } from '../services/api';
import { PipelineRun, RunStatus } from '../types';

type FilterStatus = 'all' | RunStatus;

interface FilterButtonProps {
  label: string;
  active: boolean;
  onPress: () => void;
}

const FilterButton: React.FC<FilterButtonProps> = ({ label, active, onPress }) => (
  <TouchableOpacity
    style={[styles.filterButton, active && styles.filterButtonActive]}
    onPress={onPress}
  >
    <Text style={[styles.filterText, active && styles.filterTextActive]}>
      {label}
    </Text>
  </TouchableOpacity>
);

interface RunItemProps {
  run: PipelineRun;
  onPress: () => void;
}

const RunItem: React.FC<RunItemProps> = ({ run, onPress }) => {
  const statusConfig: Record<string, { color: string; icon: keyof typeof Ionicons.glyphMap }> = {
    completed: { color: '#10B981', icon: 'checkmark-circle' },
    failed: { color: '#EF4444', icon: 'close-circle' },
    running: { color: '#F59E0B', icon: 'sync' },
    pending: { color: '#6B7280', icon: 'time' },
    cancelled: { color: '#9CA3AF', icon: 'stop-circle' },
  };

  const config = statusConfig[run.status] || statusConfig.pending;
  const startDate = new Date(run.started_at);
  const isToday = new Date().toDateString() === startDate.toDateString();

  return (
    <TouchableOpacity style={styles.runItem} onPress={onPress}>
      <View style={[styles.statusIndicator, { backgroundColor: config.color }]}>
        <Ionicons name={config.icon} size={16} color="white" />
      </View>
      <View style={styles.runInfo}>
        <Text style={styles.runName}>{run.pipeline_name}</Text>
        <View style={styles.runMeta}>
          <Text style={styles.runTime}>
            {isToday
              ? startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              : startDate.toLocaleDateString([], { month: 'short', day: 'numeric' })}
          </Text>
          {run.duration_ms && (
            <Text style={styles.runDuration}>
              {run.duration_ms < 1000
                ? `${run.duration_ms}ms`
                : `${(run.duration_ms / 1000).toFixed(1)}s`}
            </Text>
          )}
        </View>
        {run.error && (
          <Text style={styles.runError} numberOfLines={1}>
            {run.error}
          </Text>
        )}
      </View>
      <Ionicons name="chevron-forward" size={20} color="#D1D5DB" />
    </TouchableOpacity>
  );
};

export const HistoryScreen: React.FC = () => {
  const navigation = useNavigation();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [filteredRuns, setFilteredRuns] = useState<PipelineRun[]>([]);
  const [filter, setFilter] = useState<FilterStatus>('all');
  const [error, setError] = useState<string | null>(null);

  const fetchRuns = useCallback(async () => {
    const response = await api.listRuns(undefined, 50);
    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      setRuns(response.data);
      setError(null);
    }
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchRuns();
    setRefreshing(false);
  }, [fetchRuns]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await fetchRuns();
      setLoading(false);
    };
    load();
  }, [fetchRuns]);

  useEffect(() => {
    if (filter === 'all') {
      setFilteredRuns(runs);
    } else {
      setFilteredRuns(runs.filter((r) => r.status === filter));
    }
  }, [filter, runs]);

  // Group runs by date
  const groupedRuns = React.useMemo(() => {
    const groups: { title: string; data: PipelineRun[] }[] = [];
    const today = new Date().toDateString();
    const yesterday = new Date(Date.now() - 86400000).toDateString();

    filteredRuns.forEach((run) => {
      const runDate = new Date(run.started_at).toDateString();
      let title: string;

      if (runDate === today) {
        title = 'Today';
      } else if (runDate === yesterday) {
        title = 'Yesterday';
      } else {
        title = new Date(run.started_at).toLocaleDateString([], {
          weekday: 'long',
          month: 'short',
          day: 'numeric',
        });
      }

      const existing = groups.find((g) => g.title === title);
      if (existing) {
        existing.data.push(run);
      } else {
        groups.push({ title, data: [run] });
      }
    });

    return groups;
  }, [filteredRuns]);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#6366F1" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Filters */}
      <View style={styles.filterContainer}>
        <FilterButton
          label="All"
          active={filter === 'all'}
          onPress={() => setFilter('all')}
        />
        <FilterButton
          label="Completed"
          active={filter === 'completed'}
          onPress={() => setFilter('completed')}
        />
        <FilterButton
          label="Failed"
          active={filter === 'failed'}
          onPress={() => setFilter('failed')}
        />
        <FilterButton
          label="Running"
          active={filter === 'running'}
          onPress={() => setFilter('running')}
        />
      </View>

      {/* Run List */}
      {error ? (
        <View style={styles.centered}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={groupedRuns}
          keyExtractor={(item) => item.title}
          renderItem={({ item: group }) => (
            <View>
              <Text style={styles.sectionHeader}>{group.title}</Text>
              {group.data.map((run) => (
                <RunItem
                  key={run.id}
                  run={run}
                  onPress={() =>
                    navigation.navigate('RunDetail' as never, { runId: run.id } as never)
                  }
                />
              ))}
            </View>
          )}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="documents" size={48} color="#D1D5DB" />
              <Text style={styles.emptyText}>No runs found</Text>
            </View>
          }
        />
      )}
    </View>
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
  },
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: 'white',
  },
  filterButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#F3F4F6',
    marginRight: 8,
  },
  filterButtonActive: {
    backgroundColor: '#6366F1',
  },
  filterText: {
    fontSize: 13,
    color: '#6B7280',
  },
  filterTextActive: {
    color: 'white',
    fontWeight: '500',
  },
  listContent: {
    paddingVertical: 8,
  },
  sectionHeader: {
    fontSize: 13,
    fontWeight: '600',
    color: '#6B7280',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#F3F4F6',
  },
  runItem: {
    backgroundColor: 'white',
    paddingVertical: 12,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  statusIndicator: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  runInfo: {
    flex: 1,
    marginLeft: 12,
  },
  runName: {
    fontSize: 15,
    fontWeight: '500',
    color: '#1F2937',
  },
  runMeta: {
    flexDirection: 'row',
    marginTop: 2,
  },
  runTime: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  runDuration: {
    fontSize: 12,
    color: '#9CA3AF',
    marginLeft: 8,
  },
  runError: {
    fontSize: 11,
    color: '#EF4444',
    marginTop: 2,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingTop: 48,
  },
  emptyText: {
    color: '#9CA3AF',
    marginTop: 8,
  },
  errorText: {
    color: '#EF4444',
    marginBottom: 16,
  },
  retryButton: {
    backgroundColor: '#6366F1',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontWeight: '600',
  },
});

export default HistoryScreen;
