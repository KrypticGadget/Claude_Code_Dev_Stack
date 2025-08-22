import React, { useState, useCallback, useEffect } from 'react'
import { SplitViewContainer, useSplitView, SplitViewProvider } from '../components/SplitView'
import { MonacoEditor } from '../components/MonacoEditor'
import '../styles/split-view-editor.css'

const DEMO_CODE_SAMPLES = {
  typescript: `// TypeScript Demo - Advanced React Component with Hooks
import React, { useState, useEffect, useCallback } from 'react'
import { debounce } from 'lodash'

interface User {
  id: number
  name: string
  email: string
  avatar?: string
}

interface SearchProps {
  onUserSelect: (user: User) => void
  placeholder?: string
}

const UserSearch: React.FC<SearchProps> = ({ 
  onUserSelect, 
  placeholder = "Search users..." 
}) => {
  const [query, setQuery] = useState<string>('')
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce(async (searchQuery: string) => {
      if (!searchQuery.trim()) {
        setUsers([])
        return
      }

      setLoading(true)
      setError(null)

      try {
        const response = await fetch(\`/api/users?q=\${encodeURIComponent(searchQuery)}\`)
        if (!response.ok) {
          throw new Error('Failed to fetch users')
        }
        
        const data: User[] = await response.json()
        setUsers(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setUsers([])
      } finally {
        setLoading(false)
      }
    }, 300),
    []
  )

  useEffect(() => {
    debouncedSearch(query)
    return () => debouncedSearch.cancel()
  }, [query, debouncedSearch])

  const handleUserClick = useCallback((user: User) => {
    onUserSelect(user)
    setQuery('')
    setUsers([])
  }, [onUserSelect])

  return (
    <div className="user-search">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="search-input"
      />
      
      {loading && <div className="loading">Searching...</div>}
      {error && <div className="error">{error}</div>}
      
      {users.length > 0 && (
        <div className="search-results">
          {users.map((user) => (
            <div
              key={user.id}
              className="user-item"
              onClick={() => handleUserClick(user)}
            >
              {user.avatar && (
                <img src={user.avatar} alt={user.name} className="avatar" />
              )}
              <div className="user-info">
                <div className="user-name">{user.name}</div>
                <div className="user-email">{user.email}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default UserSearch`,

  python: `# Python Demo - Advanced Data Processing with Type Hints
from typing import List, Dict, Optional, Callable, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class DataPoint:
    """Represents a single data point with timestamp and value."""
    timestamp: datetime
    value: float
    metadata: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class DataProcessor(Generic[T]):
    """Generic data processor with filtering and aggregation capabilities."""
    
    def __init__(self, data_source: str):
        self.data_source = data_source
        self.data_points: List[DataPoint] = []
        self.processors: List[Callable[[List[DataPoint]], List[DataPoint]]] = []
    
    async def load_data(self, start_date: datetime, end_date: datetime) -> None:
        """Load data from the specified date range."""
        logger.info(f"Loading data from {start_date} to {end_date}")
        
        try:
            # Simulate async data loading
            await asyncio.sleep(0.1)
            
            # Generate sample data
            current_date = start_date
            while current_date <= end_date:
                data_point = DataPoint(
                    timestamp=current_date,
                    value=hash(current_date.isoformat()) % 100,
                    metadata={"source": self.data_source}
                )
                self.data_points.append(data_point)
                current_date += timedelta(hours=1)
                
            logger.info(f"Loaded {len(self.data_points)} data points")
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise`,

  javascript: `// JavaScript Demo - Modern Web Development
class ModernWebApp {
  constructor(config = {}) {
    this.config = {
      apiUrl: '/api',
      timeout: 5000,
      retries: 3,
      ...config
    }
    
    this.cache = new Map()
    this.eventListeners = new Map()
    this.abortController = new AbortController()
  }

  // Advanced fetch with retries and caching
  async apiCall(endpoint, options = {}) {
    const url = \`\${this.config.apiUrl}\${endpoint}\`
    const cacheKey = \`\${url}-\${JSON.stringify(options)}\`
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)
    }

    let lastError
    for (let attempt = 1; attempt <= this.config.retries; attempt++) {
      try {
        const response = await fetch(url, {
          ...options,
          signal: this.abortController.signal,
          timeout: this.config.timeout
        })

        if (!response.ok) {
          throw new Error(\`HTTP \${response.status}: \${response.statusText}\`)
        }

        const data = await response.json()
        this.cache.set(cacheKey, data)
        return data
      } catch (error) {
        lastError = error
        if (attempt < this.config.retries) {
          await this.delay(1000 * attempt) // Exponential backoff
        }
      }
    }

    throw lastError
  }

  // Event system
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event).push(callback)
  }

  emit(event, data) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Event listener error:', error)
        }
      })
    }
  }

  // Utility methods
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  cleanup() {
    this.abortController.abort()
    this.cache.clear()
    this.eventListeners.clear()
  }
}

// Usage example
const app = new ModernWebApp({
  apiUrl: 'https://api.example.com',
  retries: 2
})

app.on('dataLoaded', (data) => {
  console.log('Data received:', data)
})

// Load user data
app.apiCall('/users')
  .then(users => app.emit('dataLoaded', users))
  .catch(error => console.error('Failed to load users:', error))`,

  css: `/* Modern CSS with Advanced Features */

/* CSS Custom Properties (Variables) */
:root {
  /* Color Palette */
  --primary-color: #007acc;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --warning-color: #ffc107;
  --error-color: #dc3545;
  
  /* Typography Scale */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;
  --font-size-2xl: 2rem;
  
  /* Spacing Scale */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --space-2xl: 3rem;
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 1rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  
  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;
}

/* Modern Reset */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
  color: #1f2937;
  background-color: #ffffff;
}

/* Container Query for Responsive Components */
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: var(--space-lg);
  }
}

/* CSS Grid Layout System */
.grid {
  display: grid;
  gap: var(--space-md);
}

.grid-cols-1 { grid-template-columns: 1fr; }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

/* Responsive Grid */
.grid-responsive {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* Modern Button Component */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
  
  /* Focus ring */
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.btn:focus-visible {
  outline-color: var(--primary-color);
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: color-mix(in srgb, var(--primary-color) 85%, black);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* CSS Logical Properties */
.card {
  padding-block: var(--space-lg);
  padding-inline: var(--space-lg);
  margin-block-end: var(--space-md);
  border-radius: var(--radius-lg);
  background-color: white;
  box-shadow: var(--shadow-md);
}

/* Advanced Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp var(--transition-normal) ease-out;
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
  :root {
    --primary-color: #3b82f6;
  }
  
  body {
    background-color: #111827;
    color: #f9fafb;
  }
  
  .card {
    background-color: #1f2937;
    border: 1px solid #374151;
  }
}

/* Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* High Contrast Support */
@media (prefers-contrast: high) {
  .btn {
    border-width: 3px;
  }
  
  .card {
    border: 2px solid currentColor;
  }
}

/* Modern CSS Features */
.feature-showcase {
  /* CSS Nesting */
  & .title {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    
    & span {
      color: var(--primary-color);
    }
  }
  
  /* CSS Layers */
  @layer utilities {
    .text-center { text-align: center; }
    .text-left { text-align: left; }
    .text-right { text-align: right; }
  }
}

/* Subgrid Support */
.product-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
}

.product-card {
  display: grid;
  grid-template-rows: subgrid;
  grid-row: span 3;
}

/* CSS Scroll Snap */
.scroll-container {
  scroll-snap-type: x mandatory;
  overflow-x: auto;
  display: flex;
  gap: var(--space-md);
}

.scroll-item {
  scroll-snap-align: start;
  flex: 0 0 300px;
}`
}

interface SplitViewEditorDemoProps {
  initialLayout?: 'single' | 'two-pane' | 'three-pane-horizontal' | 'four-pane-grid'
}

const SplitViewEditorDemoInner: React.FC<SplitViewEditorDemoProps> = ({
  initialLayout = 'two-pane'
}) => {
  const {
    panes,
    activePaneId,
    addTab,
    setActivePane,
    updateTabContent,
    settings,
    synchronizedScrolling,
    toggleSynchronizedScrolling,
    compareMode,
    toggleCompareMode
  } = useSplitView()

  const [enableCollaboration, setEnableCollaboration] = useState(false)
  const [enableDebugger, setEnableDebugger] = useState(true)
  const [enableGit, setEnableGit] = useState(true)
  const [enableVim, setEnableVim] = useState(false)

  // Initialize demo tabs when component mounts
  useEffect(() => {
    const paneIds = Object.keys(panes)
    
    if (paneIds.length >= 1 && panes[paneIds[0]].tabs.length === 0) {
      // Add initial tabs to first pane
      addTab(paneIds[0], {
        title: 'UserSearch.tsx',
        filePath: '/src/components/UserSearch.tsx',
        language: 'typescript',
        content: DEMO_CODE_SAMPLES.typescript,
        isDirty: false,
        isActive: true,
        canClose: true
      })
    }

    if (paneIds.length >= 2 && panes[paneIds[1]].tabs.length === 0) {
      // Add different file to second pane
      addTab(paneIds[1], {
        title: 'data_processor.py',
        filePath: '/src/utils/data_processor.py',
        language: 'python',
        content: DEMO_CODE_SAMPLES.python,
        isDirty: false,
        isActive: true,
        canClose: true
      })
    }

    if (paneIds.length >= 3 && panes[paneIds[2]].tabs.length === 0) {
      // Add third file
      addTab(paneIds[2], {
        title: 'app.js',
        filePath: '/src/app.js',
        language: 'javascript',
        content: DEMO_CODE_SAMPLES.javascript,
        isDirty: false,
        isActive: true,
        canClose: true
      })
    }

    if (paneIds.length >= 4 && panes[paneIds[3]].tabs.length === 0) {
      // Add fourth file
      addTab(paneIds[3], {
        title: 'styles.css',
        filePath: '/src/styles/styles.css',
        language: 'css',
        content: DEMO_CODE_SAMPLES.css,
        isDirty: false,
        isActive: true,
        canClose: true
      })
    }
  }, [panes, addTab])

  // Handle adding new demo files
  const handleAddDemoFile = useCallback((language: keyof typeof DEMO_CODE_SAMPLES) => {
    const activePanes = Object.values(panes).filter(pane => pane.visible)
    const targetPaneId = activePaneId || activePanes[0]?.id

    if (targetPaneId) {
      const extensions = {
        typescript: 'tsx',
        python: 'py',
        javascript: 'js',
        css: 'css'
      }

      addTab(targetPaneId, {
        title: `demo.${extensions[language]}`,
        filePath: `/demo/demo.${extensions[language]}`,
        language,
        content: DEMO_CODE_SAMPLES[language],
        isDirty: false,
        isActive: true,
        canClose: true
      })
    }
  }, [panes, activePaneId, addTab])

  return (
    <div className="split-view-editor-demo">
      {/* Demo Header */}
      <div className="demo-header">
        <div className="demo-title">
          <h1>Split View Editor Demo</h1>
          <p>Advanced multi-pane code editor with side-by-side editing, synchronized scrolling, and cross-panel operations.</p>
        </div>

        <div className="demo-controls">
          <div className="control-section">
            <h3>Editor Features</h3>
            <div className="control-group">
              <label>
                <input 
                  type="checkbox" 
                  checked={enableCollaboration}
                  onChange={(e) => setEnableCollaboration(e.target.checked)}
                />
                Collaborative Editing
              </label>
            </div>
            
            <div className="control-group">
              <label>
                <input 
                  type="checkbox" 
                  checked={enableDebugger}
                  onChange={(e) => setEnableDebugger(e.target.checked)}
                />
                Debugging
              </label>
            </div>
            
            <div className="control-group">
              <label>
                <input 
                  type="checkbox" 
                  checked={enableGit}
                  onChange={(e) => setEnableGit(e.target.checked)}
                />
                Git Integration
              </label>
            </div>
            
            <div className="control-group">
              <label>
                <input 
                  type="checkbox" 
                  checked={enableVim}
                  onChange={(e) => setEnableVim(e.target.checked)}
                />
                Vim Mode
              </label>
            </div>
          </div>

          <div className="control-section">
            <h3>Split View Features</h3>
            <div className="control-group">
              <label>
                <input 
                  type="checkbox" 
                  checked={synchronizedScrolling}
                  onChange={toggleSynchronizedScrolling}
                />
                Synchronized Scrolling
              </label>
            </div>
            
            <div className="control-group">
              <label>
                <input 
                  type="checkbox" 
                  checked={compareMode}
                  onChange={toggleCompareMode}
                />
                Compare Mode
              </label>
            </div>
          </div>

          <div className="control-section">
            <h3>Demo Files</h3>
            <div className="demo-file-buttons">
              <button 
                className="demo-file-btn typescript"
                onClick={() => handleAddDemoFile('typescript')}
              >
                + TypeScript
              </button>
              <button 
                className="demo-file-btn python"
                onClick={() => handleAddDemoFile('python')}
              >
                + Python
              </button>
              <button 
                className="demo-file-btn javascript"
                onClick={() => handleAddDemoFile('javascript')}
              >
                + JavaScript
              </button>
              <button 
                className="demo-file-btn css"
                onClick={() => handleAddDemoFile('css')}
              >
                + CSS
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Split View Container */}
      <div className="demo-editor-container">
        <SplitViewContainer
          defaultLayout={initialLayout}
          defaultOrientation="horizontal"
          minPaneSize={300}
          className="demo-split-view"
        />
      </div>

      {/* Demo Features Info */}
      <div className="demo-features">
        <h2>Split View Features Demonstrated</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>🔀 Flexible Layouts</h3>
            <p>Switch between single, dual, triple, and quad-pane layouts. Support for both horizontal and vertical orientations.</p>
          </div>
          
          <div className="feature-card">
            <h3>📐 Resizable Panes</h3>
            <p>Drag resize handles between panes with snap zones and keyboard navigation support.</p>
          </div>
          
          <div className="feature-card">
            <h3>📑 Tab Management</h3>
            <p>Independent tab sets per pane with drag-and-drop support to move tabs between panes.</p>
          </div>
          
          <div className="feature-card">
            <h3>🔄 Synchronized Scrolling</h3>
            <p>Optional synchronized scrolling between files for side-by-side comparison.</p>
          </div>
          
          <div className="feature-card">
            <h3>🔍 Compare Mode</h3>
            <p>Enhanced diff view for comparing different versions of files or related code.</p>
          </div>
          
          <div className="feature-card">
            <h3>⌨️ Keyboard Shortcuts</h3>
            <p>Full keyboard navigation with customizable shortcuts for all split operations.</p>
          </div>

          <div className="feature-card">
            <h3>💾 Session Persistence</h3>
            <p>Save and restore split configurations, maintaining your workspace layout across sessions.</p>
          </div>
          
          <div className="feature-card">
            <h3>📱 Mobile Responsive</h3>
            <p>Adaptive behavior on mobile devices, collapsing to tab-based navigation when needed.</p>
          </div>
        </div>
      </div>

      {/* Keyboard Shortcuts Reference */}
      <div className="keyboard-shortcuts">
        <h3>Keyboard Shortcuts</h3>
        <div className="shortcuts-grid">
          <div className="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>H</kbd>
            <span>Split Horizontal</span>
          </div>
          <div className="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>V</kbd>
            <span>Split Vertical</span>
          </div>
          <div className="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>T</kbd>
            <span>New Tab</span>
          </div>
          <div className="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>W</kbd>
            <span>Close Tab</span>
          </div>
          <div className="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>W</kbd>
            <span>Close Pane</span>
          </div>
          <div className="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>Tab</kbd>
            <span>Next Tab</span>
          </div>
          <div className="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>→</kbd>
            <span>Focus Right Pane</span>
          </div>
          <div className="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>←</kbd>
            <span>Focus Left Pane</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export const SplitViewEditorDemo: React.FC<SplitViewEditorDemoProps> = (props) => {
  return (
    <SplitViewProvider>
      <SplitViewEditorDemoInner {...props} />
    </SplitViewProvider>
  )
}

export default SplitViewEditorDemo