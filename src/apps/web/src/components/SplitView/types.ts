export type SplitLayout = 
  | 'single'
  | 'two-pane'
  | 'three-pane-horizontal'
  | 'three-pane-vertical'
  | 'four-pane-grid'
  | 'four-pane-vertical'
  | 'four-pane-horizontal'

export type SplitOrientation = 'horizontal' | 'vertical'

export interface FileTab {
  id: string
  title: string
  filePath: string
  language: string
  content: string
  isDirty: boolean
  isActive: boolean
  canClose: boolean
}

export interface PaneConfig {
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

export interface SplitViewState {
  layout: SplitLayout
  orientation: SplitOrientation
  panes: Record<string, PaneConfig>
  activePaneId: string | null
  synchronizedScrolling: boolean
  compareMode: boolean
  snapToGrid: boolean
  settings: SplitViewSettings
}

export interface SplitViewSettings {
  theme: 'light' | 'dark' | 'auto'
  showMinimap: boolean
  wordWrap: boolean
  fontSize: number
  fontFamily: string
  tabSize: number
  insertSpaces: boolean
  resizerSize: number
  snapDistance: number
  enableKeyboardShortcuts: boolean
  persistLayout: boolean
  autoSave: boolean
  autoSaveDelay: number
}

export interface SplitViewActions {
  // Layout actions
  setLayout: (layout: SplitLayout) => void
  setOrientation: (orientation: SplitOrientation) => void
  resetLayout: () => void
  
  // Pane actions
  addPane: (config?: Partial<PaneConfig>) => string
  removePane: (paneId: string) => void
  resizePane: (paneId: string, size: number) => void
  updatePaneSize: (paneId: string, size: number) => void
  splitPane: (direction: 'horizontal' | 'vertical', sourcePaneId?: string) => void
  closePanePanel: (paneId: string) => void
  swapPanes: (paneId1: string, paneId2: string, tabId?: string) => void
  
  // Tab actions
  addTab: (paneId: string, tab: Partial<FileTab>) => string
  removeTab: (paneId: string, tabId: string) => void
  updateTab: (paneId: string, tabId: string, updates: Partial<FileTab>) => void
  setActiveTab: (paneId: string, tabId: string) => void
  moveTab: (fromPaneId: string, toPaneId: string, tabId: string) => void
  duplicateTab: (paneId: string, tabId: string) => void
  
  // Content actions
  updateTabContent: (paneId: string, tabId: string, content: string) => void
  saveTab: (paneId: string, tabId: string) => void
  saveAllTabs: () => void
  revertTab: (paneId: string, tabId: string) => void
  
  // Navigation actions
  setActivePane: (paneId: string) => void
  focusNextPane: () => void
  focusPreviousPane: () => void
  focusPane: (direction: 'up' | 'down' | 'left' | 'right') => void
  
  // View actions
  toggleSynchronizedScrolling: () => void
  toggleCompareMode: () => void
  toggleSnapToGrid: () => void
  
  // Settings actions
  updateSettings: (settings: Partial<SplitViewSettings>) => void
  
  // Persistence actions
  saveSession: (name: string) => void
  loadSession: (name: string) => void
  getSavedSessions: () => string[]
  deleteSavedSession: (name: string) => void
}

export interface ResizeHandle {
  orientation: SplitOrientation
  position: number
  onResize: (delta: number) => void
  onResizeEnd: () => void
}

export interface DragDropData {
  type: 'tab' | 'pane'
  sourceId: string
  data: any
}

export interface SnapZone {
  id: string
  bounds: DOMRect
  type: 'pane' | 'split-horizontal' | 'split-vertical' | 'tab-header'
  targetId: string
}

export interface KeyboardShortcut {
  key: string
  ctrlKey?: boolean
  shiftKey?: boolean
  altKey?: boolean
  metaKey?: boolean
  action: string
  description: string
}

export interface SplitViewContextType extends SplitViewState, SplitViewActions {}

// Default configurations
export const DEFAULT_PANE_CONFIG: Omit<PaneConfig, 'id'> = {
  tabs: [],
  activeTabId: null,
  size: 400,
  minSize: 200,
  maxSize: Infinity,
  visible: true,
  position: {
    row: 0,
    col: 0,
    rowSpan: 1,
    colSpan: 1
  }
}

export const DEFAULT_SPLIT_VIEW_SETTINGS: SplitViewSettings = {
  theme: 'auto',
  showMinimap: true,
  wordWrap: true,
  fontSize: 14,
  fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
  tabSize: 2,
  insertSpaces: true,
  resizerSize: 4,
  snapDistance: 20,
  enableKeyboardShortcuts: true,
  persistLayout: true,
  autoSave: true,
  autoSaveDelay: 2000
}

export const KEYBOARD_SHORTCUTS: KeyboardShortcut[] = [
  { key: 'h', ctrlKey: true, action: 'split-horizontal', description: 'Split pane horizontally' },
  { key: 'v', ctrlKey: true, action: 'split-vertical', description: 'Split pane vertically' },
  { key: 'w', ctrlKey: true, action: 'close-tab', description: 'Close current tab' },
  { key: 'w', ctrlKey: true, shiftKey: true, action: 'close-pane', description: 'Close current pane' },
  { key: 't', ctrlKey: true, action: 'new-tab', description: 'New tab' },
  { key: 'Tab', ctrlKey: true, action: 'next-tab', description: 'Next tab' },
  { key: 'Tab', ctrlKey: true, shiftKey: true, action: 'previous-tab', description: 'Previous tab' },
  { key: 'ArrowLeft', ctrlKey: true, shiftKey: true, action: 'focus-left-pane', description: 'Focus left pane' },
  { key: 'ArrowRight', ctrlKey: true, shiftKey: true, action: 'focus-right-pane', description: 'Focus right pane' },
  { key: 'ArrowUp', ctrlKey: true, shiftKey: true, action: 'focus-up-pane', description: 'Focus up pane' },
  { key: 'ArrowDown', ctrlKey: true, shiftKey: true, action: 'focus-down-pane', description: 'Focus down pane' },
  { key: 's', ctrlKey: true, action: 'save-tab', description: 'Save current tab' },
  { key: 's', ctrlKey: true, shiftKey: true, action: 'save-all', description: 'Save all tabs' },
  { key: 'z', ctrlKey: true, action: 'undo', description: 'Undo' },
  { key: 'z', ctrlKey: true, shiftKey: true, action: 'redo', description: 'Redo' },
  { key: 'f', ctrlKey: true, action: 'find', description: 'Find' },
  { key: 'h', ctrlKey: true, action: 'replace', description: 'Find and replace' },
  { key: 'g', ctrlKey: true, action: 'go-to-line', description: 'Go to line' },
  { key: '/', ctrlKey: true, action: 'toggle-comment', description: 'Toggle comment' },
  { key: 'd', ctrlKey: true, action: 'duplicate-line', description: 'Duplicate line' },
  { key: 'l', ctrlKey: true, action: 'select-line', description: 'Select line' }
]