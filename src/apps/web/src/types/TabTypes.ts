export interface EditorFile {
  id: string
  name: string
  path: string
  content?: string
  language?: string
  lastModified?: Date
}

export interface Tab {
  id: string
  fileId: string
  title: string
  filePath: string
  language: string
  content: string
  isDirty: boolean
  isPinned: boolean
  isActive: boolean
  lastModified: Date
  groupId: string | null
  thumbnail?: string
}

export interface TabGroup {
  id: string
  name: string
  color: string
  isCollapsed: boolean
  tabIds: string[]
}

export interface SplitPanel {
  id: string
  tabs: string[]
  activeTabId: string | null
}

export interface TabManagerState {
  tabs: Tab[]
  tabGroups: TabGroup[]
  splitPanels: SplitPanel[]
  activeTabId: string | null
  activePanelId: string
  recentFiles: string[]
  unsavedChanges: Set<string>
  pinnedTabs: Set<string>
  searchQuery: string
}

export interface TabContextMenuAction {
  id: string
  label: string
  icon?: string
  shortcut?: string
  separator?: boolean
  disabled?: boolean
  onClick: () => void
}

export interface TabDragData {
  tabId: string
  panelId: string
  index: number
}

export interface TabSearchResult {
  tab: Tab
  score: number
  matchedFields: string[]
}

export interface TabKeyboardShortcuts {
  onNextTab: () => void
  onPreviousTab: () => void
  onCloseTab: () => void
  onNewTab: () => void
  onToggleSearch: () => void
  onSave: () => void
  onCloseAll: () => void
  onGoToTab: (index: number) => void
}

export interface TabDragCallbacks {
  onTabMove: (tabId: string, targetIndex: number, targetPanelId?: string) => void
  onTabToPanel: (tabId: string, targetPanelId: string) => void
  onCreatePanel: (direction: 'horizontal' | 'vertical', tabId?: string) => void
  onReorderTabs: (tabIds: string[], panelId: string) => void
}

export interface TabSessionData {
  version: string
  timestamp: number
  state: Partial<TabManagerState>
}

export interface TabPreferences {
  maxTabs: number
  enablePersistence: boolean
  enableKeyboardNavigation: boolean
  enableDragAndDrop: boolean
  enableSplitView: boolean
  enableTabGroups: boolean
  enableTabPreviews: boolean
  enableAutoSave: boolean
  autoSaveInterval: number
  tabScrolling: 'auto' | 'manual'
  tabLayout: 'compact' | 'standard' | 'wide'
}

export type TabChangeEvent = {
  type: 'create' | 'close' | 'activate' | 'update' | 'move' | 'pin' | 'unpin'
  tabId: string
  previousTabId?: string
  data?: any
}

export type TabValidationError = {
  type: 'max_tabs_exceeded' | 'invalid_file' | 'permission_denied' | 'file_not_found'
  message: string
  tabId?: string
}

export interface TabThumbnailOptions {
  width: number
  height: number
  scale: number
  includeLineNumbers: boolean
  maxLines: number
}

export interface TabPerformanceMetrics {
  totalTabs: number
  activeTabs: number
  memoryUsage: number
  renderTime: number
  interactionLatency: number
}

export interface TabAccessibilityOptions {
  enableScreenReader: boolean
  enableHighContrast: boolean
  fontSize: 'small' | 'medium' | 'large'
  keyboardOnly: boolean
  announceChanges: boolean
}

export interface TabFilterOptions {
  includeUnsaved: boolean
  includePinned: boolean
  includeGroups: string[]
  language: string[]
  modifiedAfter?: Date
  modifiedBefore?: Date
}

export interface TabSortOptions {
  field: 'name' | 'lastModified' | 'size' | 'language' | 'path'
  direction: 'asc' | 'desc'
  groupBy?: 'language' | 'directory' | 'group'
}

export interface TabExportOptions {
  format: 'json' | 'csv' | 'xml'
  includeContent: boolean
  includeMetadata: boolean
  compress: boolean
}

export interface TabImportOptions {
  format: 'json' | 'csv' | 'xml'
  mergeStrategy: 'replace' | 'merge' | 'append'
  validateFiles: boolean
  createGroups: boolean
}