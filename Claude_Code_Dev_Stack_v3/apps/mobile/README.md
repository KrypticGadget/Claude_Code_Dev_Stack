# Claude Code Mobile App (React Native)

A React Native mobile application for Claude Code Dev Stack v3.0, ported from the original Flutter app by @9cat.

## Features

- **Server Connection**: Connect to Claude Code proxy servers via WebSocket
- **Real-time Chat**: Interactive chat interface with Claude-Code
- **Voice Commands**: Speech-to-text input for hands-free operation
- **Terminal-style UI**: Dark theme with terminal aesthetics
- **Cross-platform**: Runs on both iOS and Android

## Attribution

- Original Flutter mobile app by **@9cat** (MIT License)
- React Native port by **Claude Code Dev Stack v3.0**
- Backend integration by **@zainhoda** (AGPL-3.0)

## Installation

### Prerequisites

- Node.js >= 16
- React Native development environment
- Android Studio (for Android)
- Xcode (for iOS)

### Setup

1. Install dependencies:
```bash
cd apps/mobile
npm install
```

2. Install iOS dependencies (if targeting iOS):
```bash
cd ios && pod install && cd ..
```

3. Start Metro bundler:
```bash
npm start
```

4. Run on Android:
```bash
npm run android
```

5. Run on iOS:
```bash
npm run ios
```

## Architecture

### Core Components

- **ConnectionScreen**: Server connection and authentication
- **ChatScreen**: Main chat interface with terminal styling
- **AppStateContext**: Global state management using React Context
- **WebSocketService**: Real-time communication with Claude Code servers
- **VoiceService**: Speech recognition using @react-native-voice/voice

### Models

- **ConnectionConfig**: Server connection configuration
- **ChatMessage**: Chat message structure with type system

### Services

- **WebSocketService**: Singleton service for WebSocket communication
- **VoiceService**: Voice recognition and speech-to-text

## Configuration

### Default Connection Settings

- **Server URL**: `http://192.168.2.178:64008`
- **Default Credentials**:
  - admin/password123
  - developer/dev2024
  - user/user123

### Voice Recognition

The app includes voice recognition capabilities using `@react-native-voice/voice`:

- **Supported Languages**: English (en-US) by default
- **Permissions**: Requires microphone access
- **Platform Support**: iOS and Android

## Development

### Project Structure

```
src/
├── components/          # Reusable UI components
├── context/            # React Context providers
├── models/             # Data models and interfaces
├── screens/            # Screen components
├── services/           # Business logic services
└── utils/              # Utility functions
```

### Key Technologies

- **React Native**: Cross-platform mobile framework
- **React Navigation**: Navigation system
- **WebSocket**: Real-time communication
- **@react-native-voice/voice**: Speech recognition
- **Socket.IO Client**: Backend monitoring integration

## Backend Integration

The mobile app integrates with the Claude Code Dev Stack v3.0 backend:

- **WebSocket Connection**: Direct connection to Claude Code servers
- **Socket.IO Monitoring**: Real-time updates from backend services
- **Agent Communication**: Bidirectional communication with AI agents

## Testing

```bash
# Run tests
npm test

# Run linting
npm run lint
```

## Building for Production

### Android

```bash
# Generate signed APK
cd android
./gradlew assembleRelease
```

### iOS

```bash
# Build for App Store
npx react-native run-ios --configuration Release
```

## Troubleshooting

### Common Issues

1. **Metro bundler not starting**: Clear cache with `npx react-native start --reset-cache`
2. **Voice recognition not working**: Check microphone permissions
3. **WebSocket connection fails**: Verify server URL and network connectivity
4. **Build errors**: Clean and rebuild: `npx react-native clean && npm install`

### Platform-specific Issues

#### Android
- Ensure Android SDK is properly configured
- Check that device/emulator has internet access
- For voice recognition, ensure Google Speech Services are installed

#### iOS
- Run `pod install` in the ios directory
- Check code signing configuration
- Ensure device has microphone permissions

## License

MIT License (inherited from original Flutter app by @9cat)

## Contributing

This mobile app is part of the Claude Code Dev Stack v3.0 ecosystem. For contributions and issues, please refer to the main project repository.

## Support

For support and issues:
1. Check the troubleshooting section above
2. Review the main Claude Code Dev Stack documentation
3. Submit issues to the main project repository

---

**Original Flutter App**: Created by @9cat under MIT License  
**React Native Port**: Part of Claude Code Dev Stack v3.0  
**Version**: 3.0.0