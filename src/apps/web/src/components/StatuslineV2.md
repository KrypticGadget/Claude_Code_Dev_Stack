# Enhanced Statusline V2 Component

A comprehensive React-based statusline component with real-time system monitoring, configurable segments, and advanced interactive features.

## Features

### 🚀 Real-time Updates
- **System Metrics**: Live CPU, memory, disk, and network monitoring
- **Git Status**: Repository health, branch tracking, commit history
- **Claude Session**: Token usage, costs, performance metrics
- **Agent Activity**: Multi-agent status and progress tracking
- **WebSocket Integration**: 100ms update intervals for live data

### 🎨 Multiple Themes
- **Powerline**: Terminal-inspired with arrow separators
- **Minimal**: Clean, modern design
- **Classic**: Traditional status bar appearance
- **Compact**: Space-efficient layout

### ⚙️ Configurable Segments
- **Drag & Drop**: Reorder segments by priority
- **Toggle Visibility**: Enable/disable specific segments
- **Responsive Hiding**: Smart segment hiding on smaller screens
- **Custom Actions**: Click handlers for each segment type

### 🎯 Interactive Features
- **Click Actions**: Modal dialogs with detailed information
- **Tooltips**: Contextual help and status information
- **Notifications**: Real-time alerts and warnings
- **Configuration Panel**: Live settings adjustment

### ♿ Accessibility Support
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: ARIA labels and semantic markup
- **High Contrast**: Automatic contrast adjustments
- **Reduced Motion**: Respects user motion preferences

## Component Structure

```
StatuslineV2/
├── StatuslineV2.tsx        # Main component
├── StatuslineV2.css        # Comprehensive styles
├── StatuslineDemoV2.tsx    # Demo implementation
├── StatuslineDemoV2.css    # Demo styles
└── hooks/
    ├── useSystemMetrics.ts # System monitoring
    ├── useGitStatus.ts     # Git integration
    ├── useClaudeSession.ts # Claude session tracking
    └── useWebSocket.ts     # Real-time updates
```

## Usage

### Basic Implementation

```tsx
import { StatuslineV2 } from './components/StatuslineV2'
import { useSystemMetrics } from './hooks/useSystemMetrics'
import { useGitStatus } from './hooks/useGitStatus'
import { useClaudeSession } from './hooks/useClaudeSession'

function App() {
  const { metrics } = useSystemMetrics()
  const { gitStatus } = useGitStatus()
  const { session } = useClaudeSession()
  
  return (
    <StatuslineV2
      systemMetrics={metrics}
      gitStatus={gitStatus}
      claudeSession={session}
      agents={agents}
      isConnected={isConnected}
      onSegmentClick={handleSegmentClick}
      onConfigChange={handleConfigChange}
    />
  )
}
```

### Advanced Configuration

```tsx
const statuslineConfig = {
  theme: 'powerline',
  updateInterval: 100,
  animations: true,
  sounds: false,
  tooltips: true,
  segments: [
    { id: 'path', enabled: true, priority: 1, responsive: false },
    { id: 'git', enabled: true, priority: 2, responsive: true },
    { id: 'claude', enabled: true, priority: 3, responsive: true },
    { id: 'agents', enabled: true, priority: 4, responsive: true },
    { id: 'system', enabled: true, priority: 5, responsive: true },
    { id: 'time', enabled: true, priority: 6, responsive: false }
  ],
  colors: {
    primary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#6366f1'
  }
}

<StatuslineV2 config={statuslineConfig} />
```

## Segments

### 1. Path Segment
- **Purpose**: Display current working directory
- **Data**: File system path information
- **Click Action**: File browser or directory details

### 2. Git Segment
- **Purpose**: Repository status and branch information
- **Data**: Branch name, changes, commit history
- **Click Action**: Git details modal with recent commits

### 3. Claude Segment
- **Purpose**: AI session monitoring
- **Data**: Model info, token usage, costs, performance
- **Click Action**: Session details with metrics

### 4. Agents Segment
- **Purpose**: Multi-agent system status
- **Data**: Active agents, progress, error states
- **Click Action**: Agent grid with individual statuses

### 5. System Segment
- **Purpose**: Hardware performance monitoring
- **Data**: CPU, memory, disk, network metrics
- **Click Action**: Detailed system metrics dashboard

### 6. Connection Segment
- **Purpose**: Network connectivity status
- **Data**: WebSocket connection, latency
- **Click Action**: Connection diagnostics

### 7. Time Segment
- **Purpose**: Current timestamp
- **Data**: Real-time clock
- **Click Action**: Calendar and time zone info

## Real-time Data Hooks

### useSystemMetrics
```tsx
const { metrics, isLoading, error, refresh } = useSystemMetrics({
  updateInterval: 1000,
  enableDetailedMetrics: true,
  enableNetworkLatency: true,
  networkTestHost: 'claude.ai'
})
```

**Features:**
- Browser-based performance monitoring
- Memory usage via Performance API
- Network latency testing
- Mock data for unavailable metrics

### useGitStatus
```tsx
const { gitStatus, isLoading, error, refresh, executeGitCommand } = useGitStatus({
  updateInterval: 2000,
  maxCommits: 10,
  watchFileChanges: true
})
```

**Features:**
- Repository detection
- Branch tracking
- Commit history parsing
- File change monitoring
- Git command execution

### useClaudeSession
```tsx
const { session, isLoading, error, updateTokenUsage, logMessage } = useClaudeSession({
  updateInterval: 1000,
  trackPerformance: true,
  enableCostTracking: true,
  sessionId: 'session-123'
})
```

**Features:**
- Token usage tracking
- Cost calculation
- Performance metrics
- Session quality assessment
- Model information

## Styling and Themes

### CSS Custom Properties
```css
:root {
  --statusline-height: 28px;
  --statusline-spacing: 8px;
  --statusline-border-radius: 4px;
  --statusline-animation-duration: 0.2s;
  --statusline-z-index: 1000;
}
```

### Theme Variants
- **Powerline**: Angular separators, terminal aesthetics
- **Minimal**: Clean lines, subtle backgrounds
- **Classic**: Traditional status bar styling
- **Compact**: Reduced height and spacing

### Responsive Breakpoints
- **Desktop**: Full feature set, all segments visible
- **Tablet**: Adaptive layout, some segments hidden
- **Mobile**: Essential segments only, compact design

## Performance Optimizations

### React Optimizations
- `React.memo` for segment components
- `useCallback` for event handlers
- `useMemo` for computed values
- Lazy loading for heavy components

### CSS Optimizations
- `contain` property for layout isolation
- `will-change` for animation performance
- Minimal reflows and repaints
- Hardware acceleration where beneficial

### WebSocket Efficiency
- Heartbeat mechanism for connection health
- Automatic reconnection with exponential backoff
- Message throttling and batching
- Connection state management

## Accessibility Features

### Keyboard Support
- Tab navigation through segments
- Enter/Space for activation
- Escape for modal dismissal
- Arrow keys for configuration

### Screen Reader Support
- Semantic HTML structure
- ARIA labels and roles
- Live regions for updates
- Descriptive link text

### Visual Accessibility
- High contrast mode support
- Respects reduced motion preferences
- Color-blind friendly indicators
- Scalable font sizes

## Browser Compatibility

### Supported Browsers
- Chrome 90+ (full feature set)
- Firefox 88+ (full feature set)
- Safari 14+ (limited Performance API)
- Edge 90+ (full feature set)

### Graceful Degradation
- Mock data for unsupported APIs
- Progressive enhancement approach
- Fallback styling for older browsers
- Polyfills where necessary

## Integration Examples

### With Existing Applications
```tsx
// Replace existing statusline
import { StatuslineV2 } from './components/StatuslineV2'

// Use as overlay
<div className="app-with-statusline">
  <StatuslineV2 />
  <main>{children}</main>
</div>

// Integrate with routing
<Route path="/dashboard" element={
  <>
    <StatuslineV2 />
    <Dashboard />
  </>
} />
```

### With Monitoring Systems
```tsx
// Prometheus integration
const metrics = usePrometheusMetrics()

// Custom WebSocket endpoint
const { data } = useWebSocket(MONITORING_WS_URL)

// External Git service
const gitData = await fetchGitHubStatus()

<StatuslineV2 
  systemMetrics={metrics}
  gitStatus={gitData}
  customSegments={customSegments}
/>
```

## Development

### Local Development
```bash
npm install
npm run dev
```

### Testing
```bash
npm run test
npm run test:coverage
npm run test:e2e
```

### Building
```bash
npm run build
npm run build:analyze
```

## Configuration Options

### StatuslineConfig Interface
```typescript
interface StatuslineConfig {
  theme: 'powerline' | 'minimal' | 'classic' | 'compact'
  updateInterval: number
  segments: SegmentConfig[]
  colors: {
    primary: string
    success: string
    warning: string
    error: string
    info: string
  }
  animations: boolean
  sounds: boolean
  tooltips: boolean
}
```

### Segment Configuration
```typescript
interface SegmentConfig {
  id: string
  type: 'git' | 'claude' | 'system' | 'agents' | 'time' | 'custom'
  enabled: boolean
  priority: number
  minWidth?: number
  responsive: boolean
  clickAction?: 'modal' | 'navigate' | 'toggle' | 'custom'
  customAction?: () => void
}
```

## API Reference

### StatuslineV2 Props
```typescript
interface StatuslineV2Props {
  systemMetrics?: SystemMetrics
  gitStatus?: GitStatus
  claudeSession?: ClaudeSession
  agents?: AgentStatus[]
  isConnected: boolean
  config?: Partial<StatuslineConfig>
  onSegmentClick?: (segmentId: string, data: any) => void
  onConfigChange?: (config: StatuslineConfig) => void
}
```

### Event Handlers
```typescript
// Segment click handling
const handleSegmentClick = (segmentId: string, data: any) => {
  switch (segmentId) {
    case 'git':
      showGitModal(data)
      break
    case 'system':
      navigateToMetrics()
      break
    default:
      console.log('Segment clicked:', segmentId, data)
  }
}

// Configuration changes
const handleConfigChange = (newConfig: StatuslineConfig) => {
  localStorage.setItem('statusline-config', JSON.stringify(newConfig))
  updateStatusline(newConfig)
}
```

## Future Enhancements

### Planned Features
- [ ] Plugin system for custom segments
- [ ] Drag & drop segment reordering
- [ ] Export/import configuration
- [ ] Historical data visualization
- [ ] Alert rules and notifications
- [ ] Multi-language support
- [ ] Custom color schemes
- [ ] Keyboard shortcuts
- [ ] Voice commands integration
- [ ] Mobile app companion

### Performance Improvements
- [ ] Virtual scrolling for large datasets
- [ ] Web Workers for heavy computations
- [ ] Service Worker for offline functionality
- [ ] IndexedDB for data persistence
- [ ] WebAssembly for performance-critical code

### Integration Enhancements
- [ ] Docker container monitoring
- [ ] Kubernetes cluster status
- [ ] CI/CD pipeline integration
- [ ] Issue tracker connectivity
- [ ] Code quality metrics
- [ ] Security vulnerability alerts

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`
4. Open http://localhost:3000/statusline-v2

### Code Style
- TypeScript for type safety
- ESLint + Prettier for code formatting
- Conventional commits for changelog
- Jest + Testing Library for tests

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

## License

MIT License - see LICENSE file for details.

## Credits

- **Frontend Architecture**: Claude Code Frontend Architect Agent
- **Design System**: Based on modern web standards
- **Icons**: Lucide React icon library
- **Inspiration**: VS Code statusline, tmux, and powerline

---

*This component is part of the Claude Code Agents V3.6.9 development stack.*