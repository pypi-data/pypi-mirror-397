# FlowMason Mobile

Monitor and trigger FlowMason pipelines from your mobile device.

## Features

- **Dashboard** - View pipeline stats and recent activity
- **Pipeline Management** - Browse and run pipelines
- **Run History** - View execution history with filtering
- **Push Notifications** - Get notified on pipeline completion/failure
- **Secure Configuration** - API keys stored in device secure storage

## Getting Started

### Prerequisites

- Node.js 18+
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator or Android Emulator (or physical device with Expo Go)

### Installation

```bash
# Install dependencies
npm install

# Start the development server
npm start
```

### Running on Device

1. Install Expo Go on your iOS or Android device
2. Scan the QR code from the terminal
3. Configure your FlowMason server in Settings

## Configuration

In the Settings screen:

1. Enter your FlowMason Studio server URL
2. Enter your API key
3. Test the connection
4. Save settings

## Project Structure

```
src/
├── components/      # Reusable UI components
├── context/         # React context providers
├── hooks/           # Custom React hooks
├── screens/         # App screens
│   ├── DashboardScreen.tsx
│   ├── PipelinesScreen.tsx
│   ├── HistoryScreen.tsx
│   └── SettingsScreen.tsx
├── services/        # API and notification services
│   ├── api.ts
│   └── notifications.ts
├── types/           # TypeScript types
└── utils/           # Utility functions
```

## Building for Production

### iOS

```bash
# Build for iOS
eas build --platform ios
```

### Android

```bash
# Build for Android
eas build --platform android
```

## License

MIT
