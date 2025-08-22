// Split View Component Exports
export { SplitViewContainer } from './SplitViewContainer'
export { SplitPane } from './SplitPane'
export { SplitResizer } from './SplitResizer'
export { SplitViewToolbar } from './SplitViewToolbar'
export { TabBar } from './TabBar'
export { SplitViewProvider, useSplitView } from './SplitViewContext'

// Type exports
export type {
  SplitLayout,
  SplitOrientation,
  FileTab,
  PaneConfig,
  SplitViewState,
  SplitViewSettings,
  SplitViewActions,
  SplitViewContextType,
  ResizeHandle,
  DragDropData,
  SnapZone,
  KeyboardShortcut
} from './types'

// Constants and defaults
export {
  DEFAULT_PANE_CONFIG,
  DEFAULT_SPLIT_VIEW_SETTINGS,
  KEYBOARD_SHORTCUTS
} from './types'