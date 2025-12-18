/**
 * FlowMason Mobile App
 *
 * Monitor and trigger pipelines from your mobile device.
 */

import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import * as SecureStore from 'expo-secure-store';

import { api } from './src/services/api';
import { notifications } from './src/services/notifications';
import DashboardScreen from './src/screens/DashboardScreen';
import PipelinesScreen from './src/screens/PipelinesScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// Tab Navigator
function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'grid' : 'grid-outline';
          } else if (route.name === 'Pipelines') {
            iconName = focused ? 'layers' : 'layers-outline';
          } else if (route.name === 'History') {
            iconName = focused ? 'time' : 'time-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          } else {
            iconName = 'help-circle-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6366F1',
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarStyle: {
          backgroundColor: 'white',
          borderTopColor: '#E5E7EB',
        },
        headerStyle: {
          backgroundColor: 'white',
        },
        headerTitleStyle: {
          fontWeight: '600',
        },
        headerShadowVisible: false,
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          headerTitle: 'FlowMason',
        }}
      />
      <Tab.Screen
        name="Pipelines"
        component={PipelinesScreen}
        options={{
          headerTitle: 'Pipelines',
        }}
      />
      <Tab.Screen
        name="History"
        component={HistoryScreen}
        options={{
          headerTitle: 'Run History',
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          headerTitle: 'Settings',
        }}
      />
    </Tab.Navigator>
  );
}

// Main App
export default function App() {
  useEffect(() => {
    // Initialize app
    const init = async () => {
      try {
        // Load saved settings
        const serverUrl = await SecureStore.getItemAsync('server_url');
        const apiKey = await SecureStore.getItemAsync('api_key');

        if (serverUrl && apiKey) {
          api.configure({ url: serverUrl, apiKey });
        }

        // Initialize notifications
        const notificationsEnabled = await SecureStore.getItemAsync(
          'notifications_enabled',
        );
        if (notificationsEnabled !== 'false') {
          await notifications.initialize();
        }

        // Set up notification response handler
        notifications.addResponseListener((response) => {
          const data = response.notification.request.content.data;
          if (data?.runId) {
            // Navigate to run detail
            // This would need a navigation ref in production
            console.log('Navigate to run:', data.runId);
          }
        });
      } catch (error) {
        console.error('Initialization error:', error);
      }
    };

    init();

    return () => {
      notifications.cleanup();
    };
  }, []);

  return (
    <NavigationContainer>
      <StatusBar style="dark" />
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Main" component={TabNavigator} />
        {/* Add detail screens here */}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
