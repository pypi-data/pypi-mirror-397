/**
 * Notifications Service
 *
 * Handles push notifications for pipeline events.
 */

import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import { PipelineRun } from '../types';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

class NotificationService {
  private expoPushToken: string | null = null;
  private notificationListeners: (() => void)[] = [];

  /**
   * Initialize notification service.
   */
  async initialize(): Promise<void> {
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('pipeline-updates', {
        name: 'Pipeline Updates',
        importance: Notifications.AndroidImportance.HIGH,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for notifications');
      return;
    }

    try {
      const tokenData = await Notifications.getExpoPushTokenAsync();
      this.expoPushToken = tokenData.data;
      console.log('Push token:', this.expoPushToken);
    } catch (error) {
      console.log('Error getting push token:', error);
    }
  }

  /**
   * Get the Expo push token.
   */
  getPushToken(): string | null {
    return this.expoPushToken;
  }

  /**
   * Add a listener for notifications.
   */
  addNotificationListener(
    callback: (notification: Notifications.Notification) => void,
  ): () => void {
    const subscription = Notifications.addNotificationReceivedListener(callback);

    const unsubscribe = () => {
      subscription.remove();
    };

    this.notificationListeners.push(unsubscribe);
    return unsubscribe;
  }

  /**
   * Add a listener for notification responses (taps).
   */
  addResponseListener(
    callback: (response: Notifications.NotificationResponse) => void,
  ): () => void {
    const subscription = Notifications.addNotificationResponseReceivedListener(callback);

    const unsubscribe = () => {
      subscription.remove();
    };

    this.notificationListeners.push(unsubscribe);
    return unsubscribe;
  }

  /**
   * Send a local notification for a pipeline run update.
   */
  async notifyRunUpdate(run: PipelineRun): Promise<void> {
    let title: string;
    let body: string;

    switch (run.status) {
      case 'completed':
        title = 'Pipeline Completed';
        body = `${run.pipeline_name} finished successfully in ${run.duration_ms}ms`;
        break;
      case 'failed':
        title = 'Pipeline Failed';
        body = `${run.pipeline_name} failed: ${run.error || 'Unknown error'}`;
        break;
      case 'running':
        title = 'Pipeline Started';
        body = `${run.pipeline_name} is now running`;
        break;
      default:
        return;
    }

    await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data: {
          runId: run.id,
          pipelineName: run.pipeline_name,
        },
      },
      trigger: null, // Immediate
    });
  }

  /**
   * Send a custom notification.
   */
  async notify(
    title: string,
    body: string,
    data?: Record<string, unknown>,
  ): Promise<void> {
    await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data,
      },
      trigger: null,
    });
  }

  /**
   * Get pending notifications count.
   */
  async getBadgeCount(): Promise<number> {
    return Notifications.getBadgeCountAsync();
  }

  /**
   * Set badge count.
   */
  async setBadgeCount(count: number): Promise<void> {
    await Notifications.setBadgeCountAsync(count);
  }

  /**
   * Clear all notifications.
   */
  async clearAll(): Promise<void> {
    await Notifications.dismissAllNotificationsAsync();
    await Notifications.setBadgeCountAsync(0);
  }

  /**
   * Cleanup listeners.
   */
  cleanup(): void {
    this.notificationListeners.forEach((unsubscribe) => unsubscribe());
    this.notificationListeners = [];
  }
}

// Export singleton instance
export const notifications = new NotificationService();

export default notifications;
