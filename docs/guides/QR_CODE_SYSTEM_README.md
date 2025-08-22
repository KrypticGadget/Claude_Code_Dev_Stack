# QR Code Generation System for Claude Code Mobile Access

A comprehensive QR code generation and management system that enables seamless mobile access to Claude Code development environments through NGROK tunnels and secure token-based authentication.

## Features Overview

### 1. Tunnel URL QR Codes
- Automatically generates QR codes for all active NGROK tunnels
- Real-time monitoring and QR code updates when tunnels change
- Secure token-based authentication with expiration
- Mobile-optimized landing pages for seamless connection

### 2. Connection Instructions QR Codes
- Embedded connection information and step-by-step instructions
- Platform-specific guidance (iOS, Android, Web)
- Deep-linking support for native app integration
- Customizable instruction sets for different service types

### 3. Mobile-Optimized Access Codes
- Deep-linking for mobile apps with fallback URLs
- Platform detection and automatic redirection
- Progressive Web App (PWA) integration
- Offline capability and sync mechanisms

### 4. Session-Specific QR Codes
- Unique session identifiers for tracking and security
- Temporary access tokens with configurable expiration
- Session state management and persistence
- Multi-device session coordination

### 5. Time-Limited Access
- Configurable expiration times (minutes to days)
- Automatic cleanup of expired tokens
- Warning notifications before expiration
- Grace period handling for active connections

### 6. Secure Access Tokens
- JWT-based authentication with strong encryption
- Token validation and revocation capabilities
- Biometric authentication integration (mobile)
- Certificate pinning for enhanced security

### 7. Multi-Service QR Codes
- Single QR code for accessing multiple services
- Service selection interface on mobile
- Batch operations for service management
- Load balancing and failover support

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │  Mobile App     │    │  Backend API    │
│                 │    │                 │    │                 │
│ QRCodeGenerator │◄──►│ QRCodeScanner   │◄──►│ QRCodeService   │
│ QRCodeDashboard │    │ DeepLinkHandler │    │ NGROKIntegration│
│ MobileLanding   │    │ ConnectionSvc   │    │ TokenValidator  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        ┌─────────────────┐
                        │  NGROK Tunnels  │
                        │                 │
                        │ Auto-Discovery  │
                        │ QR Generation   │
                        │ Health Monitor  │
                        └─────────────────┘
```

## Installation and Setup

### Backend Dependencies

```bash
cd apps/backend
npm install qrcode uuid jsonwebtoken crypto
```

### Web App Dependencies

```bash
cd apps/web
npm install react-qr-code qrcode.js
```

### Mobile App Dependencies

```bash
cd apps/mobile
npm install react-native-qrcode-scanner react-native-camera react-native-permissions react-native-qrcode-svg react-native-svg
```

### iOS Configuration

Add to `Info.plist`:
```xml
<key>NSCameraUsageDescription</key>
<string>Camera access is required to scan QR codes for connecting to Claude Code services.</string>
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLName</key>
        <string>claudecode</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>claudecode</string>
        </array>
    </dict>
</array>
```

### Android Configuration

Add to `AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.INTERNET" />

<activity
    android:name=".MainActivity"
    android:launchMode="singleTop">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="claudecode" />
    </intent-filter>
</activity>
```

## Usage Examples

### 1. Generate Tunnel QR Code (Backend)

```javascript
// Auto-generate QR codes for all active tunnels
const ngrokQR = new NGROKQRIntegration();
await ngrokQR.startMonitoring({
  interval: 30000, // 30 seconds
  autoGenerate: true,
  expiration: 24 * 60 * 60 * 1000, // 24 hours
  customization: {
    size: 512,
    color: { dark: '#000000', light: '#FFFFFF' }
  }
});

// Generate QR code for specific tunnel
const qrResult = await qrCodeService.generateTunnelQRCode(
  'https://abc123.ngrok.io',
  {
    serviceName: 'Claude Code Dev Server',
    description: 'Access development environment',
    expiration: 2 * 60 * 60 * 1000 // 2 hours
  }
);
```

### 2. Display QR Code (React Web)

```tsx
import QRCodeGenerator from './components/QRCodeGenerator';

function App() {
  return (
    <QRCodeGenerator
      type="tunnel"
      data={{
        tunnelUrl: 'https://abc123.ngrok.io',
        serviceName: 'Claude Code',
        description: 'Development Environment Access'
      }}
      autoRefresh={true}
      refreshInterval={300000} // 5 minutes
      onGenerate={(qrData) => console.log('QR generated:', qrData)}
      onError={(error) => console.error('QR error:', error)}
    />
  );
}
```

### 3. QR Code Dashboard (React Web)

```tsx
import QRCodeDashboard from './components/QRCodeDashboard';

function Dashboard() {
  const [tunnels, setTunnels] = useState([]);
  
  useEffect(() => {
    fetch('/api/ngrok/tunnels')
      .then(res => res.json())
      .then(setTunnels);
  }, []);

  return (
    <QRCodeDashboard
      tunnels={tunnels}
      onTunnelChange={setTunnels}
    />
  );
}
```

### 4. Scan QR Code (React Native)

```tsx
import QRCodeScanner from './components/QRCodeScanner';
import DeepLinkManager from './utils/DeepLinkHandler';

function ScannerScreen() {
  const deepLinkManager = new DeepLinkManager();
  
  useEffect(() => {
    deepLinkManager.initialize({
      onConnect: (connectionData) => {
        console.log('Connected:', connectionData);
        // Navigate to appropriate screen
      },
      onError: (error) => {
        Alert.alert('Connection Error', error);
      }
    });
    
    return () => deepLinkManager.cleanup();
  }, []);

  return (
    <QRCodeScanner
      autoConnect={true}
      onScanSuccess={(data) => console.log('Scanned:', data)}
      onConnectionEstablished={(info) => console.log('Connected:', info)}
    />
  );
}
```

### 5. Mobile Landing Page (React Web)

```tsx
import MobileLanding from './components/MobileLanding';

// This component is automatically rendered when mobile users scan QR codes
function MobileLandingPage() {
  return <MobileLanding className="mobile-optimized" />;
}
```

## API Reference

### Backend Endpoints

#### QR Code Generation
- `POST /api/qr/generate` - Generate QR code
- `POST /api/qr/batch` - Batch generate QR codes
- `POST /api/qr/validate` - Validate QR token
- `GET /api/qr/stats` - Get QR statistics
- `GET /api/qr/list` - List active QR codes
- `DELETE /api/qr/:sessionId` - Revoke QR code

#### NGROK Integration
- `GET /api/ngrok/tunnels` - Get active tunnels
- `GET /api/ngrok/qr-codes` - Get tunnel QR codes
- `GET /api/ngrok/stats` - Get tunnel statistics
- `POST /api/ngrok/scan` - Trigger tunnel scan

### QR Code Data Format

```typescript
interface QRCodeData {
  type: 'tunnel_access' | 'mobile_access' | 'session_access' | 'time_limited_access' | 'multi_service_access';
  sessionId: string;
  token?: string;
  tunnelUrl?: string;
  appUrl?: string;
  deepLink?: string;
  serviceName?: string;
  description?: string;
  expiresAt?: number;
  connectionInfo?: any;
}
```

### Deep Link URL Schemes

```
claudecode://connect?token=<jwt_token>
claudecode://session?token=<session_token>&session=<session_id>
claudecode://instructions?session=<session_id>
claudecode://multiservice?token=<master_token>
claudecode://mobile?token=<mobile_token>
claudecode://access?token=<access_token>&expires=<timestamp>
```

## Security Considerations

### Token Security
- JWT tokens with strong encryption (256-bit keys)
- Configurable expiration times
- Token revocation capabilities
- Secure storage in mobile apps (Keychain/Keystore)

### Network Security
- HTTPS enforcement for all communications
- Certificate pinning in mobile apps
- Request validation and rate limiting
- CORS configuration for web clients

### Mobile Security
- Camera permissions properly requested
- Biometric authentication support
- Secure deep link handling
- App integrity verification

## Performance Optimization

### Backend
- Token caching with TTL
- Batch QR code generation
- Async tunnel monitoring
- Connection pooling

### Frontend
- QR code image caching
- Lazy loading of QR components
- Optimized re-renders
- Progressive loading

### Mobile
- Camera resource management
- Background processing limitations
- Battery optimization
- Memory leak prevention

## Troubleshooting

### Common Issues

1. **QR Code Not Scanning**
   - Check camera permissions
   - Ensure adequate lighting
   - Verify QR code is not expired
   - Check deep link configuration

2. **Connection Failures**
   - Verify tunnel is active
   - Check token validity
   - Confirm network connectivity
   - Review CORS settings

3. **Deep Link Not Working**
   - Verify URL scheme registration
   - Check app installation
   - Review manifest configuration
   - Test fallback URLs

### Debug Commands

```bash
# Check active tunnels
curl http://localhost:8080/api/ngrok/tunnels

# Validate QR token
curl -X POST http://localhost:8080/api/qr/validate \
  -H "Content-Type: application/json" \
  -d '{"token":"<jwt_token>"}'

# Get QR statistics
curl http://localhost:8080/api/qr/stats

# Force tunnel scan
curl -X POST http://localhost:8080/api/ngrok/scan
```

## File Structure

```
apps/
├── backend/
│   ├── services/
│   │   ├── qrCodeService.js
│   │   └── ngrokQRIntegration.js
│   └── server.js
├── web/
│   └── src/
│       └── components/
│           ├── QRCodeGenerator.tsx
│           ├── QRCodeDashboard.tsx
│           └── MobileLanding.tsx
└── mobile/
    └── src/
        ├── components/
        │   ├── QRCodeScanner.tsx
        │   └── QRCodeGenerator.tsx
        ├── services/
        │   └── QRConnectionService.ts
        └── utils/
            └── DeepLinkHandler.ts
```

## Contributing

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure mobile compatibility across platforms
5. Test deep link functionality thoroughly

## License

This QR code system is part of the Claude Code Dev Stack v3.6.9 and follows the same licensing terms as the main project.