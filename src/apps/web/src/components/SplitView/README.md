# Split View Editor System

A comprehensive split view editing system with side-by-side editing, drag-and-drop tab management, synchronized scrolling, and advanced workspace management features.

## Features

### 🔀 Layout Management
- **Multiple Layout Options**: Single, dual, triple, and quad-pane layouts
- **Flexible Orientations**: Horizontal and vertical split orientations
- **Grid Layouts**: 2x2 grid layout for four-pane editing
- **Dynamic Layout Switching**: Change layouts on-the-fly with toolbar controls

### 📐 Resizable Panes
- **Drag-to-Resize**: Intuitive resize handles between panes
- **Snap Zones**: Magnetic snap points for consistent sizing
- **Keyboard Resize**: Arrow key navigation for precise adjustments
- **Minimum/Maximum Constraints**: Prevent panes from becoming too small or large

### 📑 Advanced Tab Management
- **Independent Tab Sets**: Each pane manages its own set of tabs
- **Drag-and-Drop**: Move tabs between panes seamlessly
- **Context Menu**: Right-click for advanced tab operations
- **File Type Icons**: Visual file type indicators
- **Dirty State Indicators**: Visual indication of unsaved changes

### 🔄 Synchronized Features
- **Synchronized Scrolling**: Optional synchronized scrolling between files
- **Compare Mode**: Enhanced diff view for side-by-side comparison
- **Cross-Panel Operations**: Operations that work across multiple panes

### ⌨️ Keyboard Shortcuts
- **Global Shortcuts**: Full keyboard navigation support
- **Customizable Bindings**: Configurable keyboard shortcuts
- **Accessibility**: Screen reader compatible navigation

### 💾 Session Management
- **Layout Persistence**: Save and restore split configurations
- **Session Storage**: Named session management
- **Auto-Save**: Automatic session backup

### 📱 Mobile Responsive
- **Adaptive Behavior**: Responsive design for different screen sizes
- **Touch Support**: Touch-friendly resize handles and interactions
- **Mobile Optimization**: Optimized tab scrolling on mobile devices

## Components

### SplitViewContainer
The main container component that orchestrates the entire split view system.

```tsx
import { SplitViewContainer } from './components/SplitView'

<SplitViewContainer
  defaultLayout="two-pane"
  defaultOrientation="horizontal"
  minPaneSize={300}
  onLayoutChange={(layout) => console.log('Layout changed:', layout)}
/>
```

### SplitViewProvider
Context provider that manages split view state and actions.

```tsx
import { SplitViewProvider, useSplitView } from './components/SplitView'

// In your app root
<SplitViewProvider>
  <YourApp />
</SplitViewProvider>

// In components
const { addTab, splitPane, toggleSynchronizedScrolling } = useSplitView()
```

### SplitPane
Individual pane component with tab management and editor integration.

```tsx
<SplitPane
  pane={paneConfig}
  size={400}
  orientation="horizontal"
  onResize={(newSize) => console.log('Pane resized:', newSize)}
/>
```

### SplitResizer
Resize handle component for adjusting pane sizes.

```tsx
<SplitResizer
  orientation="horizontal"
  onResize={(delta) => handleResize(delta)}
  snapZones={[200, 400, 600]}
/>
```

### TabBar
Tab management component with drag-and-drop support.

```tsx
<TabBar
  tabs={tabs}
  activeTabId={activeTabId}
  onTabSelect={(id) => setActiveTab(id)}
  onTabClose={(id) => closeTab(id)}
/>
```

## API Reference

### SplitView Context

#### State
```typescript
interface SplitViewState {
  layout: SplitLayout
  orientation: SplitOrientation
  panes: Record<string, PaneConfig>
  activePaneId: string | null
  synchronizedScrolling: boolean
  compareMode: boolean
  settings: SplitViewSettings
}
```

#### Actions
```typescript
interface SplitViewActions {
  // Layout actions
  setLayout: (layout: SplitLayout) => void
  setOrientation: (orientation: SplitOrientation) => void
  splitPane: (direction: 'horizontal' | 'vertical') => void
  
  // Pane actions
  addPane: (config?: Partial<PaneConfig>) => string
  removePane: (paneId: string) => void
  resizePane: (paneId: string, size: number) => void
  
  // Tab actions
  addTab: (paneId: string, tab: Partial<FileTab>) => string
  removeTab: (paneId: string, tabId: string) => void
  setActiveTab: (paneId: string, tabId: string) => void
  moveTab: (fromPaneId: string, toPaneId: string, tabId: string) => void
  
  // View actions
  toggleSynchronizedScrolling: () => void
  toggleCompareMode: () => void
  
  // Session actions
  saveSession: (name: string) => void
  loadSession: (name: string) => void
}
```

### Types

#### Layouts
```typescript
type SplitLayout = 
  | 'single'
  | 'two-pane'
  | 'three-pane-horizontal'
  | 'three-pane-vertical'
  | 'four-pane-grid'
  | 'four-pane-vertical'
  | 'four-pane-horizontal'
```

#### File Tab
```typescript
interface FileTab {
  id: string
  title: string
  filePath: string
  language: string
  content: string
  isDirty: boolean
  isActive: boolean
  canClose: boolean
}
```

#### Pane Configuration
```typescript
interface PaneConfig {
  id: string
  tabs: FileTab[]
  activeTabId: string | null
  size?: number
  minSize?: number
  maxSize?: number
  visible: boolean
  position: {
    row: number
    col: number
    rowSpan: number
    colSpan: number
  }
}
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + H` | Split pane horizontally |
| `Ctrl + V` | Split pane vertically |
| `Ctrl + T` | New tab |
| `Ctrl + W` | Close tab |
| `Ctrl + Shift + W` | Close pane |
| `Ctrl + Tab` | Next tab |
| `Ctrl + Shift + Tab` | Previous tab |
| `Ctrl + Shift + →` | Focus right pane |
| `Ctrl + Shift + ←` | Focus left pane |
| `Ctrl + Shift + ↑` | Focus up pane |
| `Ctrl + Shift + ↓` | Focus down pane |
| `Ctrl + S` | Save current tab |
| `Ctrl + Shift + S` | Save all tabs |

## Usage Examples

### Basic Split View Setup

```tsx
import React from 'react'
import { SplitViewContainer, SplitViewProvider } from './components/SplitView'

function App() {
  return (
    <SplitViewProvider>
      <SplitViewContainer
        defaultLayout="two-pane"
        defaultOrientation="horizontal"
        minPaneSize={200}
        maxPaneSize={800}
      />
    </SplitViewProvider>
  )
}
```

### Custom Tab Management

```tsx
import { useSplitView } from './components/SplitView'

function FileExplorer() {
  const { addTab, panes } = useSplitView()

  const openFile = (filePath: string, content: string) => {
    const firstPaneId = Object.keys(panes)[0]
    
    addTab(firstPaneId, {
      title: filePath.split('/').pop() || 'Untitled',
      filePath,
      language: getLanguageFromExtension(filePath),
      content,
      isDirty: false,
      canClose: true
    })
  }

  return (
    <div>
      <button onClick={() => openFile('/src/App.tsx', 'import React...')}>
        Open App.tsx
      </button>
    </div>
  )
}
```

### Settings Integration

```tsx
import { useSplitView } from './components/SplitView'

function EditorSettings() {
  const { settings, updateSettings } = useSplitView()

  return (
    <div>
      <label>
        <input
          type="checkbox"
          checked={settings.synchronizedScrolling}
          onChange={(e) => updateSettings({ synchronizedScrolling: e.target.checked })}
        />
        Synchronized Scrolling
      </label>
      
      <label>
        Font Size:
        <input
          type="range"
          min="10"
          max="24"
          value={settings.fontSize}
          onChange={(e) => updateSettings({ fontSize: parseInt(e.target.value) })}
        />
      </label>
    </div>
  )
}
```

## Styling

The split view system includes comprehensive CSS with support for:
- Dark/light theme switching
- Mobile responsive design
- High contrast mode
- Reduced motion preferences
- Custom CSS properties for theming

### CSS Custom Properties

```css
:root {
  --split-view-bg: #ffffff;
  --split-view-border: #e0e0e0;
  --split-view-active: #007acc;
  --split-view-hover: #f0f0f0;
  --split-view-text: #333333;
  --split-view-resizer: #cccccc;
}
```

## Performance Considerations

- **Virtualized Rendering**: Large file lists are virtualized for performance
- **Lazy Loading**: Panes and tabs are loaded on demand
- **Memoization**: Components use React.memo and useMemo for optimization
- **Debounced Operations**: Resize and scroll operations are debounced
- **Local Storage**: Session data is efficiently stored and retrieved

## Accessibility

- **ARIA Support**: Full ARIA labels and roles
- **Keyboard Navigation**: Complete keyboard accessibility
- **Screen Reader Support**: Announcements for state changes
- **Focus Management**: Proper focus handling across panes
- **High Contrast**: Support for high contrast themes

## Browser Support

- Modern browsers (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)
- Progressive enhancement for older browsers
- Polyfills for missing features where needed
- Responsive design for mobile browsers

## Contributing

1. Follow the established component patterns
2. Add comprehensive TypeScript types
3. Include unit tests for new functionality
4. Ensure accessibility compliance
5. Update documentation for new features

## License

This component is part of the Claude Code Dev Stack and follows the project's licensing terms.