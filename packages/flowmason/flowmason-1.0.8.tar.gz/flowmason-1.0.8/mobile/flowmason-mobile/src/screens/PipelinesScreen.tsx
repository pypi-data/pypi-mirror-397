/**
 * Pipelines Screen
 *
 * Lists all available pipelines with search and filtering.
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { api } from '../services/api';
import { Pipeline } from '../types';

interface PipelineItemProps {
  pipeline: Pipeline;
  onPress: () => void;
  onRun: () => void;
}

const PipelineItem: React.FC<PipelineItemProps> = ({ pipeline, onPress, onRun }) => {
  const lastRunStatus = pipeline.lastRun?.status;
  const statusColors: Record<string, string> = {
    completed: '#10B981',
    failed: '#EF4444',
    running: '#F59E0B',
  };

  return (
    <TouchableOpacity style={styles.pipelineItem} onPress={onPress}>
      <View style={styles.pipelineIcon}>
        <Ionicons name="git-network" size={24} color="#6366F1" />
      </View>
      <View style={styles.pipelineInfo}>
        <View style={styles.pipelineHeader}>
          <Text style={styles.pipelineName}>{pipeline.name}</Text>
          {lastRunStatus && (
            <View
              style={[
                styles.statusDot,
                { backgroundColor: statusColors[lastRunStatus] || '#6B7280' },
              ]}
            />
          )}
        </View>
        {pipeline.description && (
          <Text style={styles.pipelineDescription} numberOfLines={1}>
            {pipeline.description}
          </Text>
        )}
        <View style={styles.pipelineMeta}>
          <Text style={styles.pipelineVersion}>v{pipeline.version}</Text>
          <Text style={styles.pipelineStages}>
            {pipeline.stages.length} stages
          </Text>
          {pipeline.schedule && (
            <View style={styles.scheduleBadge}>
              <Ionicons name="time" size={10} color="#6B7280" />
              <Text style={styles.scheduleText}>Scheduled</Text>
            </View>
          )}
        </View>
      </View>
      <TouchableOpacity style={styles.runButton} onPress={onRun}>
        <Ionicons name="play" size={20} color="#6366F1" />
      </TouchableOpacity>
    </TouchableOpacity>
  );
};

export const PipelinesScreen: React.FC = () => {
  const navigation = useNavigation();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [filteredPipelines, setFilteredPipelines] = useState<Pipeline[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  const fetchPipelines = useCallback(async () => {
    const response = await api.listPipelines();
    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      setPipelines(response.data);
      setFilteredPipelines(response.data);
      setError(null);
    }
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchPipelines();
    setRefreshing(false);
  }, [fetchPipelines]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await fetchPipelines();
      setLoading(false);
    };
    load();
  }, [fetchPipelines]);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredPipelines(pipelines);
    } else {
      const query = searchQuery.toLowerCase();
      setFilteredPipelines(
        pipelines.filter(
          (p) =>
            p.name.toLowerCase().includes(query) ||
            p.description?.toLowerCase().includes(query),
        ),
      );
    }
  }, [searchQuery, pipelines]);

  const handleRunPipeline = useCallback(
    async (pipeline: Pipeline) => {
      Alert.alert(
        'Run Pipeline',
        `Run ${pipeline.name} now?`,
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Run',
            onPress: async () => {
              const response = await api.runPipeline(pipeline.name);
              if (response.error) {
                Alert.alert('Error', response.error);
              } else if (response.data) {
                Alert.alert('Started', `Run ${response.data.id} started`);
                navigation.navigate(
                  'RunDetail' as never,
                  { runId: response.data.id } as never,
                );
              }
            },
          },
        ],
      );
    },
    [navigation],
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#6366F1" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#9CA3AF" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search pipelines..."
          placeholderTextColor="#9CA3AF"
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity onPress={() => setSearchQuery('')}>
            <Ionicons name="close-circle" size={20} color="#9CA3AF" />
          </TouchableOpacity>
        )}
      </View>

      {/* Pipeline List */}
      {error ? (
        <View style={styles.centered}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={filteredPipelines}
          keyExtractor={(item) => item.name}
          renderItem={({ item }) => (
            <PipelineItem
              pipeline={item}
              onPress={() =>
                navigation.navigate(
                  'PipelineDetail' as never,
                  { name: item.name } as never,
                )
              }
              onRun={() => handleRunPipeline(item)}
            />
          )}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="folder-open" size={48} color="#D1D5DB" />
              <Text style={styles.emptyText}>
                {searchQuery ? 'No matching pipelines' : 'No pipelines found'}
              </Text>
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
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    margin: 16,
    paddingHorizontal: 12,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1F2937',
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 24,
  },
  pipelineItem: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  pipelineIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  pipelineInfo: {
    flex: 1,
    marginLeft: 12,
  },
  pipelineHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  pipelineName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginLeft: 8,
  },
  pipelineDescription: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 2,
  },
  pipelineMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  pipelineVersion: {
    fontSize: 11,
    color: '#9CA3AF',
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginRight: 8,
  },
  pipelineStages: {
    fontSize: 11,
    color: '#9CA3AF',
  },
  scheduleBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 8,
  },
  scheduleText: {
    fontSize: 10,
    color: '#6B7280',
    marginLeft: 2,
  },
  runButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
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

export default PipelinesScreen;
