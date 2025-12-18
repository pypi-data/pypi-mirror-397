/**
 * Settings Screen
 *
 * App configuration and server settings.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as SecureStore from 'expo-secure-store';
import { api } from '../services/api';
import { notifications } from '../services/notifications';

interface SettingRowProps {
  icon: keyof typeof Ionicons.glyphMap;
  title: string;
  description?: string;
  children?: React.ReactNode;
  onPress?: () => void;
}

const SettingRow: React.FC<SettingRowProps> = ({
  icon,
  title,
  description,
  children,
  onPress,
}) => {
  const Wrapper = onPress ? TouchableOpacity : View;
  return (
    <Wrapper style={styles.settingRow} onPress={onPress}>
      <Ionicons name={icon} size={22} color="#6366F1" style={styles.settingIcon} />
      <View style={styles.settingContent}>
        <Text style={styles.settingTitle}>{title}</Text>
        {description && (
          <Text style={styles.settingDescription}>{description}</Text>
        )}
      </View>
      {children}
      {onPress && !children && (
        <Ionicons name="chevron-forward" size={20} color="#D1D5DB" />
      )}
    </Wrapper>
  );
};

export const SettingsScreen: React.FC = () => {
  const [serverUrl, setServerUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const url = await SecureStore.getItemAsync('server_url');
      const key = await SecureStore.getItemAsync('api_key');
      const notifs = await SecureStore.getItemAsync('notifications_enabled');

      if (url) setServerUrl(url);
      if (key) setApiKey(key);
      if (notifs !== null) setNotificationsEnabled(notifs === 'true');

      // Check connection
      if (url && key) {
        api.configure({ url, apiKey: key });
        const response = await api.checkHealth();
        setIsConnected(!response.error);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const saveSettings = async () => {
    try {
      await SecureStore.setItemAsync('server_url', serverUrl);
      await SecureStore.setItemAsync('api_key', apiKey);
      await SecureStore.setItemAsync(
        'notifications_enabled',
        notificationsEnabled.toString(),
      );

      api.configure({ url: serverUrl, apiKey });
      Alert.alert('Saved', 'Settings saved successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to save settings');
    }
  };

  const testConnection = async () => {
    if (!serverUrl || !apiKey) {
      Alert.alert('Error', 'Please enter server URL and API key');
      return;
    }

    setTesting(true);
    api.configure({ url: serverUrl, apiKey });

    const response = await api.checkHealth();

    setTesting(false);

    if (response.error) {
      setIsConnected(false);
      Alert.alert('Connection Failed', response.error);
    } else {
      setIsConnected(true);
      Alert.alert('Success', 'Connected to FlowMason server');
    }
  };

  const toggleNotifications = async (enabled: boolean) => {
    setNotificationsEnabled(enabled);
    await SecureStore.setItemAsync('notifications_enabled', enabled.toString());

    if (enabled) {
      await notifications.initialize();
    }
  };

  const clearData = () => {
    Alert.alert(
      'Clear All Data',
      'This will clear all saved settings and cached data. Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            await SecureStore.deleteItemAsync('server_url');
            await SecureStore.deleteItemAsync('api_key');
            await SecureStore.deleteItemAsync('notifications_enabled');
            setServerUrl('');
            setApiKey('');
            setIsConnected(false);
            Alert.alert('Cleared', 'All data has been cleared');
          },
        },
      ],
    );
  };

  return (
    <ScrollView style={styles.container}>
      {/* Server Configuration */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Server Configuration</Text>

        <View style={styles.inputContainer}>
          <Text style={styles.inputLabel}>Server URL</Text>
          <TextInput
            style={styles.input}
            placeholder="https://studio.flowmason.io"
            placeholderTextColor="#9CA3AF"
            value={serverUrl}
            onChangeText={setServerUrl}
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="url"
          />
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.inputLabel}>API Key</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter your API key"
            placeholderTextColor="#9CA3AF"
            value={apiKey}
            onChangeText={setApiKey}
            autoCapitalize="none"
            autoCorrect={false}
            secureTextEntry
          />
        </View>

        <View style={styles.connectionStatus}>
          <View
            style={[
              styles.statusDot,
              { backgroundColor: isConnected ? '#10B981' : '#EF4444' },
            ]}
          />
          <Text style={styles.statusText}>
            {isConnected ? 'Connected' : 'Not Connected'}
          </Text>
        </View>

        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.button, styles.testButton]}
            onPress={testConnection}
            disabled={testing}
          >
            <Text style={styles.testButtonText}>
              {testing ? 'Testing...' : 'Test Connection'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.button} onPress={saveSettings}>
            <Text style={styles.saveButtonText}>Save</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Notifications */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>

        <SettingRow
          icon="notifications"
          title="Push Notifications"
          description="Get notified when pipelines complete or fail"
        >
          <Switch
            value={notificationsEnabled}
            onValueChange={toggleNotifications}
            trackColor={{ false: '#D1D5DB', true: '#A5B4FC' }}
            thumbColor={notificationsEnabled ? '#6366F1' : '#F3F4F6'}
          />
        </SettingRow>
      </View>

      {/* About */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>

        <SettingRow
          icon="information-circle"
          title="Version"
          description="FlowMason Mobile v0.1.0"
        />

        <SettingRow
          icon="document-text"
          title="Documentation"
          description="View online documentation"
          onPress={() => {
            // Open docs URL
          }}
        />

        <SettingRow
          icon="logo-github"
          title="GitHub"
          description="View source code"
          onPress={() => {
            // Open GitHub URL
          }}
        />
      </View>

      {/* Danger Zone */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, styles.dangerTitle]}>Danger Zone</Text>

        <TouchableOpacity style={styles.dangerButton} onPress={clearData}>
          <Ionicons name="trash" size={20} color="#EF4444" />
          <Text style={styles.dangerButtonText}>Clear All Data</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>FlowMason</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  section: {
    backgroundColor: 'white',
    marginTop: 16,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#6B7280',
    textTransform: 'uppercase',
    marginBottom: 12,
  },
  inputContainer: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
    color: '#1F2937',
  },
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 13,
    color: '#6B7280',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  testButton: {
    backgroundColor: '#F3F4F6',
    marginRight: 8,
  },
  testButtonText: {
    color: '#374151',
    fontWeight: '500',
  },
  saveButtonText: {
    color: 'white',
    fontWeight: '600',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  settingIcon: {
    marginRight: 12,
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 15,
    color: '#1F2937',
  },
  settingDescription: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 2,
  },
  dangerTitle: {
    color: '#EF4444',
  },
  dangerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: '#EF4444',
    borderRadius: 8,
  },
  dangerButtonText: {
    color: '#EF4444',
    fontWeight: '500',
    marginLeft: 8,
  },
  footer: {
    alignItems: 'center',
    padding: 24,
  },
  footerText: {
    fontSize: 12,
    color: '#9CA3AF',
  },
});

export default SettingsScreen;
