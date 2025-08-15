# Claude Code Dev Stack v3.0 - Progressive Web App

A comprehensive Progressive Web App (PWA) for the Claude Code Dev Stack, featuring real-time agent monitoring, task management, and audio control.

## 🚀 Features

- **Progressive Web App**: Installable on desktop and mobile devices
- **Real-time Monitoring**: WebSocket-based live updates every 100ms
- **Agent Dashboard**: Monitor 28+ AI agents with real-time status
- **Task Management**: Track tasks across all agents
- **Audio Controller**: Voice feedback and audio management
- **MCP Manager**: Manage Model Context Protocol services
- **Offline Support**: Full offline functionality with service workers
- **Push Notifications**: Background updates and notifications

## 🛠 Technologies

- **Frontend**: React 18 + TypeScript + Vite
- **PWA**: Workbox + Service Workers + Web App Manifest
- **State Management**: Zustand + React Query
- **UI Framework**: Custom CSS with design system
- **Real-time**: WebSocket connections
- **Testing**: Vitest + React Testing Library
- **Build**: Vite with PWA plugin

## 📦 Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Lint code
npm run lint
```

## 🔧 PWA Configuration

### Service Worker Features

- **Caching Strategies**:
  - Static assets: Cache First
  - API requests: Network First with offline fallback
  - Navigation: Network First with app shell fallback
  - Dynamic content: Stale While Revalidate

- **Offline Support**:
  - Offline page with retry functionality
  - Background sync for offline actions
  - Cached content available offline

- **Push Notifications**:
  - Background updates
  - Task completion notifications
  - Agent status alerts

### Manifest Configuration

```json
{
  "name": "Claude Code Dev Stack v3.0",
  "short_name": "DevStack",
  "display": "standalone",
  "start_url": "/",
  "theme_color": "#1a1b26",
  "background_color": "#1a1b26"
}
```

## 📱 Installation as PWA

### Desktop (Chrome/Edge/Firefox)
1. Visit the app in your browser
2. Look for the install icon in the address bar
3. Click "Install" when prompted
4. The app will be added to your desktop and app menu

### Mobile (iOS Safari)
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. Confirm installation

### Mobile (Android Chrome)
1. Open the app in Chrome
2. Tap the menu (three dots)
3. Select "Add to Home screen"
4. Confirm installation

## 🧪 Testing PWA Features

### Lighthouse PWA Audit
```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run PWA audit
lighthouse http://localhost:3000 --view --chrome-flags="--headless"
```

### Manual Testing Checklist

- [ ] App installs correctly on desktop/mobile
- [ ] Service worker registers without errors
- [ ] Offline mode works (disconnect network and test)
- [ ] Push notifications work (if permissions granted)
- [ ] App shell loads instantly on repeat visits
- [ ] Manifest validation passes
- [ ] Lighthouse PWA score > 90

### Test Commands
```bash
# Run unit tests
npm run test

# Run tests with coverage
npm run test -- --coverage

# Run tests in watch mode
npm run test -- --watch
```

## 🏗 Project Structure

```
src/
├── components/          # React components
│   ├── AgentDashboard.tsx
│   ├── TaskMonitor.tsx
│   ├── AudioController.tsx
│   ├── MCPManager.tsx
│   └── Statusline.tsx
├── hooks/              # Custom React hooks
│   └── useWebSocket.ts
├── test/               # Test utilities
│   └── setup.ts
├── App.tsx            # Main application component
├── main.tsx           # Application entry point
└── index.css          # Global styles

public/
├── manifest.json      # PWA manifest
├── sw.js             # Service worker
├── browserconfig.xml # Microsoft tiles config
├── robots.txt        # SEO robots file
└── icons/            # PWA icons (various sizes)
```

## 🔄 Real-time Features

### WebSocket Connection
- Connects to `ws://localhost:8080/ws`
- 100ms heartbeat for ultra-responsive updates
- Automatic reconnection with exponential backoff
- Handles agent status, task progress, and audio events

### Status Updates
- **Agents**: Active/total count with individual status
- **Tasks**: Completion progress across all agents
- **Hooks**: Triggered hooks for automation
- **Audio**: Last played audio file/event
- **Connection**: Real-time connection status

## 🎨 Design System

### Color Palette
- **Primary**: `#1a1b26` (Dark background)
- **Secondary**: `#24283b` (Card background)
- **Accent**: `#7aa2f7` (Primary accent)
- **Success**: `#9ece6a`
- **Warning**: `#e0af68`
- **Error**: `#f7768e`

### Typography
- **Sans**: Inter (UI text)
- **Mono**: JetBrains Mono (Code/data)

## 🔐 Security Features

- Content Security Policy (CSP) headers
- HTTPS enforcement in production
- Secure service worker registration
- XSS protection in data handling

## 📊 Performance Optimizations

- Code splitting by route and vendor
- Lazy loading of non-critical components
- Image optimization and lazy loading
- Bundle size analysis and optimization
- Service worker caching strategies

## 🌐 Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **PWA Features**: Full support in Chrome/Edge, partial in Firefox/Safari
- **Service Workers**: Supported in all modern browsers
- **Offline**: Full offline support with graceful degradation

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Deployment Targets
- **Vercel**: Recommended for automatic PWA optimization
- **Netlify**: Good PWA support with \_headers and \_redirects
- **GitHub Pages**: Basic support (requires manual PWA setup)
- **Self-hosted**: Full control over PWA features

### Environment Variables
```env
VITE_API_URL=https://your-api.com
VITE_WS_URL=wss://your-websocket.com
VITE_VAPID_PUBLIC_KEY=your-vapid-key
```

## 📈 Monitoring

### PWA Metrics
- Installation rate
- Offline usage
- Service worker cache hit rate
- Push notification engagement

### Performance Monitoring
- Core Web Vitals tracking
- Service worker performance
- Offline/online state transitions
- Real-time connection stability

## 🤝 Contributing

This PWA integrates components from multiple open-source projects:

- **@zainhoda** (Claude Code Browser)
- **@9cat** (Mobile App)
- **@qdhenry** (MCP Manager)
- **@cnoe-io** (OpenAPI Codegen)
- **@harsha-iiiv** (MCP Generator)
- **@Owloops** (Claude Powerline)
- **@chongdashu** (CC-Statusline)

See `CREDITS.md` for full attribution.

## 📄 License

AGPL-3.0 - See LICENSE file for details.

---

**Claude Code Dev Stack v3.0** - The ultimate AI development environment as a Progressive Web App.