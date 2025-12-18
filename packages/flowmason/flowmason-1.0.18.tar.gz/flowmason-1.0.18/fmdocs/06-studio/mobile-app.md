# Mobile Companion App

Monitor and trigger FlowMason pipelines from your iOS or Android device.

## Overview

```
┌─────────────────────────┐
│  FlowMason Mobile       │
├─────────────────────────┤
│                         │
│  Active Pipelines    ▼  │
│  ┌─────────────────────┐│
│  │ data-processor      ││
│  │ ● Running (45%)     ││
│  │ Started 2m ago      ││
│  └─────────────────────┘│
│  ┌─────────────────────┐│
│  │ daily-report        ││
│  │ ○ Scheduled 6:00 AM ││
│  │ Last: Success       ││
│  └─────────────────────┘│
│                         │
│  Quick Actions          │
│  ┌────┐ ┌────┐ ┌────┐  │
│  │Run │ │Stop│ │View│  │
│  └────┘ └────┘ └────┘  │
│                         │
│  [📊 Dashboard]         │
└─────────────────────────┘
```

## Installation

### iOS

Download from the App Store (coming soon) or build from source:

```bash
cd mobile/flowmason-mobile
npm install
npx expo run:ios
```

### Android

Download from Google Play (coming soon) or build from source:

```bash
cd mobile/flowmason-mobile
npm install
npx expo run:android
```

### Development

```bash
# Install dependencies
npm install

# Start Expo dev server
npm start

# Scan QR code with Expo Go app
```

## Features

### Dashboard

The dashboard shows:
- **Active Pipelines**: Currently running executions
- **Pipeline Stats**: Success rate, total runs, failures
- **Recent Activity**: Latest execution events
- **Quick Actions**: Run, stop, view most-used pipelines

### Pipeline Management

Browse and manage your pipelines:
- View all pipelines in your organization
- Filter by status (running, scheduled, idle)
- Search by name or tag
- Favorite frequently used pipelines

### Run History

View execution history:
- Filter by date range
- Filter by status (success, failed, running)
- View execution details and logs
- Compare run durations

### Settings

Configure the app:
- Server URL
- API key (stored securely)
- Push notifications
- Theme preferences

## Configuration

### Connecting to Studio

1. Open the Settings screen
2. Enter your FlowMason Studio URL
3. Enter your API key
4. Tap "Test Connection"
5. Save settings

```
Server URL: https://studio.flowmason.io
API Key: fm_xxxxxxxxxxxxx
```

### API Key Storage

API keys are stored securely using:
- **iOS**: Keychain Services
- **Android**: EncryptedSharedPreferences

## Push Notifications

Get notified when pipelines complete or fail.

### Enabling Notifications

1. Go to Settings
2. Toggle "Push Notifications" on
3. Allow notifications when prompted

### Notification Types

| Type | Description |
|------|-------------|
| Run Complete | Pipeline finished successfully |
| Run Failed | Pipeline failed with error |
| Run Started | Pipeline started (if subscribed) |
| Schedule Reminder | Upcoming scheduled run |

### Subscribing to Pipelines

1. Open pipeline details
2. Tap the bell icon
3. Select notification preferences

## API Integration

The mobile app uses the Studio REST API:

```typescript
// src/services/api.ts

const api = {
  // Pipeline operations
  getPipelines: () => GET('/api/v1/pipelines'),
  getPipeline: (id) => GET(`/api/v1/pipelines/${id}`),
  runPipeline: (id, inputs) => POST(`/api/v1/run`, { pipeline_id: id, inputs }),

  // Run operations
  getRuns: (filters) => GET('/api/v1/runs', filters),
  getRun: (id) => GET(`/api/v1/runs/${id}`),
  cancelRun: (id) => POST(`/api/v1/runs/${id}/cancel`),

  // Stats
  getStats: () => GET('/api/v1/stats'),

  // Health
  checkHealth: () => GET('/api/v1/health'),
};
```

## Screen Reference

### DashboardScreen

```typescript
// Main dashboard showing stats and activity
<DashboardScreen />

// Features:
// - Pipeline stats cards
// - Active runs list
// - Recent activity feed
// - Pull-to-refresh
```

### PipelinesScreen

```typescript
// Pipeline list and management
<PipelinesScreen />

// Features:
// - Searchable list
// - Filter by status
// - Tap to view details
// - Long-press for actions
```

### HistoryScreen

```typescript
// Execution history
<HistoryScreen />

// Features:
// - Date range filter
// - Status filter
// - Infinite scroll
// - Tap for details
```

### SettingsScreen

```typescript
// App configuration
<SettingsScreen />

// Features:
// - Server configuration
// - Connection test
// - Notification settings
// - Clear data option
```

## Building for Production

### iOS

```bash
# Build for iOS
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

### Android

```bash
# Build for Android
eas build --platform android --profile production

# Submit to Play Store
eas submit --platform android
```

### Configuration

Update `app.json` for your deployment:

```json
{
  "expo": {
    "name": "FlowMason",
    "slug": "flowmason-mobile",
    "version": "1.0.0",
    "ios": {
      "bundleIdentifier": "com.yourcompany.flowmason"
    },
    "android": {
      "package": "com.yourcompany.flowmason"
    }
  }
}
```

## Offline Support

The app provides limited offline functionality:
- View cached pipelines
- View cached run history
- Queue runs for when online
- Automatic sync when connected

## Security

- API keys stored in secure device storage
- HTTPS-only communication
- Session timeout after inactivity
- Biometric authentication (optional)

## Troubleshooting

### Connection Issues

1. Verify server URL is correct
2. Check API key is valid
3. Ensure server is accessible from mobile network
4. Try "Test Connection" in settings

### Notification Issues

1. Check notification permissions
2. Verify push tokens in Studio
3. Check notification settings in-app
4. Restart the app

### Data Not Updating

1. Pull down to refresh
2. Check connection status
3. Clear cache in settings
4. Log out and log back in
