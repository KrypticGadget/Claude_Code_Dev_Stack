import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react'
import { 
  SplitViewState, 
  SplitViewContextType, 
  SplitLayout, 
  SplitOrientation, 
  PaneConfig, 
  FileTab,
  DEFAULT_PANE_CONFIG,
  DEFAULT_SPLIT_VIEW_SETTINGS
} from './types'

// Action types
type SplitViewAction =
  | { type: 'SET_LAYOUT'; payload: SplitLayout }
  | { type: 'SET_ORIENTATION'; payload: SplitOrientation }
  | { type: 'ADD_PANE'; payload: Partial<PaneConfig> }
  | { type: 'REMOVE_PANE'; payload: string }
  | { type: 'UPDATE_PANE_SIZE'; payload: { paneId: string; size: number } }
  | { type: 'RESIZE_PANE'; payload: { paneId: string; size: number } }
  | { type: 'SPLIT_PANE'; payload: { direction: 'horizontal' | 'vertical'; sourcePaneId?: string } }
  | { type: 'CLOSE_PANE'; payload: string }
  | { type: 'SWAP_PANES'; payload: { paneId1: string; paneId2: string; tabId?: string } }
  | { type: 'ADD_TAB'; payload: { paneId: string; tab: Partial<FileTab> } }
  | { type: 'REMOVE_TAB'; payload: { paneId: string; tabId: string } }
  | { type: 'UPDATE_TAB'; payload: { paneId: string; tabId: string; updates: Partial<FileTab> } }
  | { type: 'SET_ACTIVE_TAB'; payload: { paneId: string; tabId: string } }
  | { type: 'MOVE_TAB'; payload: { fromPaneId: string; toPaneId: string; tabId: string } }
  | { type: 'UPDATE_TAB_CONTENT'; payload: { paneId: string; tabId: string; content: string } }
  | { type: 'SET_ACTIVE_PANE'; payload: string }
  | { type: 'TOGGLE_SYNCHRONIZED_SCROLLING' }
  | { type: 'TOGGLE_COMPARE_MODE' }
  | { type: 'TOGGLE_SNAP_TO_GRID' }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<typeof DEFAULT_SPLIT_VIEW_SETTINGS> }
  | { type: 'RESET_LAYOUT' }
  | { type: 'LOAD_STATE'; payload: SplitViewState }

const generateId = () => Math.random().toString(36).substr(2, 9)

const initialState: SplitViewState = {
  layout: 'two-pane',
  orientation: 'horizontal',
  panes: {
    'pane-1': {
      ...DEFAULT_PANE_CONFIG,
      id: 'pane-1',
      tabs: [],
      position: { row: 0, col: 0, rowSpan: 1, colSpan: 1 }
    },
    'pane-2': {
      ...DEFAULT_PANE_CONFIG,
      id: 'pane-2',
      tabs: [],
      position: { row: 0, col: 1, rowSpan: 1, colSpan: 1 }
    }
  },
  activePaneId: 'pane-1',
  synchronizedScrolling: false,
  compareMode: false,
  snapToGrid: true,
  settings: DEFAULT_SPLIT_VIEW_SETTINGS
}

function splitViewReducer(state: SplitViewState, action: SplitViewAction): SplitViewState {
  switch (action.type) {
    case 'SET_LAYOUT': {
      const newPanes = { ...state.panes }
      
      // Adjust panes based on layout
      switch (action.payload) {
        case 'single':
          Object.keys(newPanes).forEach((paneId, index) => {
            newPanes[paneId].visible = index === 0
          })
          break
        case 'two-pane':
          Object.keys(newPanes).forEach((paneId, index) => {
            newPanes[paneId].visible = index < 2
            if (index < 2) {
              newPanes[paneId].position = {
                row: 0,
                col: index,
                rowSpan: 1,
                colSpan: 1
              }
            }
          })
          break
        case 'three-pane-horizontal':
          Object.keys(newPanes).forEach((paneId, index) => {
            newPanes[paneId].visible = index < 3
            if (index < 3) {
              newPanes[paneId].position = {
                row: 0,
                col: index,
                rowSpan: 1,
                colSpan: 1
              }
            }
          })
          break
        case 'three-pane-vertical':
          Object.keys(newPanes).forEach((paneId, index) => {
            newPanes[paneId].visible = index < 3
            if (index < 3) {
              newPanes[paneId].position = {
                row: index,
                col: 0,
                rowSpan: 1,
                colSpan: 1
              }
            }
          })
          break
        case 'four-pane-grid':
          Object.keys(newPanes).forEach((paneId, index) => {
            newPanes[paneId].visible = index < 4
            if (index < 4) {
              newPanes[paneId].position = {
                row: Math.floor(index / 2),
                col: index % 2,
                rowSpan: 1,
                colSpan: 1
              }
            }
          })
          break
      }
      
      return {
        ...state,
        layout: action.payload,
        panes: newPanes
      }
    }

    case 'SET_ORIENTATION':
      return {
        ...state,
        orientation: action.payload
      }

    case 'ADD_PANE': {
      const newPaneId = `pane-${generateId()}`
      const newPane: PaneConfig = {
        ...DEFAULT_PANE_CONFIG,
        id: newPaneId,
        ...action.payload
      }
      
      return {
        ...state,
        panes: {
          ...state.panes,
          [newPaneId]: newPane
        }
      }
    }

    case 'REMOVE_PANE': {
      const { [action.payload]: removedPane, ...remainingPanes } = state.panes
      return {
        ...state,
        panes: remainingPanes,
        activePaneId: state.activePaneId === action.payload 
          ? Object.keys(remainingPanes)[0] || null 
          : state.activePaneId
      }
    }

    case 'UPDATE_PANE_SIZE':
    case 'RESIZE_PANE': {
      const { paneId, size } = action.payload
      return {
        ...state,
        panes: {
          ...state.panes,
          [paneId]: {
            ...state.panes[paneId],
            size
          }
        }
      }
    }

    case 'SPLIT_PANE': {
      const { direction, sourcePaneId } = action.payload
      const sourcePane = sourcePaneId ? state.panes[sourcePaneId] : state.panes[state.activePaneId!]
      
      if (!sourcePane) return state

      const newPaneId = `pane-${generateId()}`
      const newPane: PaneConfig = {
        ...DEFAULT_PANE_CONFIG,
        id: newPaneId,
        tabs: [],
        size: sourcePane.size ? sourcePane.size / 2 : undefined
      }

      // Update source pane size
      const updatedSourcePane = {
        ...sourcePane,
        size: sourcePane.size ? sourcePane.size / 2 : undefined
      }

      return {
        ...state,
        panes: {
          ...state.panes,
          [sourcePane.id]: updatedSourcePane,
          [newPaneId]: newPane
        }
      }
    }

    case 'CLOSE_PANE': {
      const { [action.payload]: removedPane, ...remainingPanes } = state.panes
      return {
        ...state,
        panes: remainingPanes,
        activePaneId: state.activePaneId === action.payload 
          ? Object.keys(remainingPanes)[0] || null 
          : state.activePaneId
      }
    }

    case 'SWAP_PANES': {
      const { paneId1, paneId2, tabId } = action.payload
      
      if (tabId) {
        // Move specific tab between panes
        const sourcePane = state.panes[paneId1]
        const targetPane = state.panes[paneId2]
        const tab = sourcePane.tabs.find(t => t.id === tabId)
        
        if (!tab) return state

        return {
          ...state,
          panes: {
            ...state.panes,
            [paneId1]: {
              ...sourcePane,
              tabs: sourcePane.tabs.filter(t => t.id !== tabId),
              activeTabId: sourcePane.activeTabId === tabId 
                ? sourcePane.tabs.find(t => t.id !== tabId)?.id || null
                : sourcePane.activeTabId
            },
            [paneId2]: {
              ...targetPane,
              tabs: [...targetPane.tabs, tab],
              activeTabId: tab.id
            }
          }
        }
      } else {
        // Swap entire pane contents
        const pane1 = state.panes[paneId1]
        const pane2 = state.panes[paneId2]
        
        return {
          ...state,
          panes: {
            ...state.panes,
            [paneId1]: { ...pane1, tabs: pane2.tabs, activeTabId: pane2.activeTabId },
            [paneId2]: { ...pane2, tabs: pane1.tabs, activeTabId: pane1.activeTabId }
          }
        }
      }
    }

    case 'ADD_TAB': {
      const { paneId, tab } = action.payload
      const pane = state.panes[paneId]
      if (!pane) return state

      const newTabId = tab.id || `tab-${generateId()}`
      const newTab: FileTab = {
        id: newTabId,
        title: tab.title || 'Untitled',
        filePath: tab.filePath || '',
        language: tab.language || 'plaintext',
        content: tab.content || '',
        isDirty: tab.isDirty || false,
        isActive: true,
        canClose: tab.canClose !== false,
        ...tab
      }

      // Deactivate other tabs
      const updatedTabs = pane.tabs.map(t => ({ ...t, isActive: false }))

      return {
        ...state,
        panes: {
          ...state.panes,
          [paneId]: {
            ...pane,
            tabs: [...updatedTabs, newTab],
            activeTabId: newTabId
          }
        }
      }
    }

    case 'REMOVE_TAB': {
      const { paneId, tabId } = action.payload
      const pane = state.panes[paneId]
      if (!pane) return state

      const remainingTabs = pane.tabs.filter(t => t.id !== tabId)
      const newActiveTabId = pane.activeTabId === tabId 
        ? remainingTabs[remainingTabs.length - 1]?.id || null
        : pane.activeTabId

      return {
        ...state,
        panes: {
          ...state.panes,
          [paneId]: {
            ...pane,
            tabs: remainingTabs,
            activeTabId: newActiveTabId
          }
        }
      }
    }

    case 'UPDATE_TAB': {
      const { paneId, tabId, updates } = action.payload
      const pane = state.panes[paneId]
      if (!pane) return state

      return {
        ...state,
        panes: {
          ...state.panes,
          [paneId]: {
            ...pane,
            tabs: pane.tabs.map(tab => 
              tab.id === tabId ? { ...tab, ...updates } : tab
            )
          }
        }
      }
    }

    case 'SET_ACTIVE_TAB': {
      const { paneId, tabId } = action.payload
      const pane = state.panes[paneId]
      if (!pane) return state

      return {
        ...state,
        panes: {
          ...state.panes,
          [paneId]: {
            ...pane,
            tabs: pane.tabs.map(tab => ({ ...tab, isActive: tab.id === tabId })),
            activeTabId: tabId
          }
        }
      }
    }

    case 'MOVE_TAB': {
      const { fromPaneId, toPaneId, tabId } = action.payload
      const fromPane = state.panes[fromPaneId]
      const toPane = state.panes[toPaneId]
      const tab = fromPane?.tabs.find(t => t.id === tabId)
      
      if (!fromPane || !toPane || !tab) return state

      return {
        ...state,
        panes: {
          ...state.panes,
          [fromPaneId]: {
            ...fromPane,
            tabs: fromPane.tabs.filter(t => t.id !== tabId),
            activeTabId: fromPane.activeTabId === tabId 
              ? fromPane.tabs.find(t => t.id !== tabId)?.id || null
              : fromPane.activeTabId
          },
          [toPaneId]: {
            ...toPane,
            tabs: [...toPane.tabs, { ...tab, isActive: true }],
            activeTabId: tabId
          }
        }
      }
    }

    case 'UPDATE_TAB_CONTENT': {
      const { paneId, tabId, content } = action.payload
      const pane = state.panes[paneId]
      if (!pane) return state

      return {
        ...state,
        panes: {
          ...state.panes,
          [paneId]: {
            ...pane,
            tabs: pane.tabs.map(tab => 
              tab.id === tabId 
                ? { ...tab, content, isDirty: true }
                : tab
            )
          }
        }
      }
    }

    case 'SET_ACTIVE_PANE':
      return {
        ...state,
        activePaneId: action.payload
      }

    case 'TOGGLE_SYNCHRONIZED_SCROLLING':
      return {
        ...state,
        synchronizedScrolling: !state.synchronizedScrolling
      }

    case 'TOGGLE_COMPARE_MODE':
      return {
        ...state,
        compareMode: !state.compareMode
      }

    case 'TOGGLE_SNAP_TO_GRID':
      return {
        ...state,
        snapToGrid: !state.snapToGrid
      }

    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: {
          ...state.settings,
          ...action.payload
        }
      }

    case 'RESET_LAYOUT':
      return initialState

    case 'LOAD_STATE':
      return action.payload

    default:
      return state
  }
}

const SplitViewContext = createContext<SplitViewContextType | undefined>(undefined)

export const useSplitView = () => {
  const context = useContext(SplitViewContext)
  if (!context) {
    throw new Error('useSplitView must be used within a SplitViewProvider')
  }
  return context
}

interface SplitViewProviderProps {
  children: React.ReactNode
  initialState?: Partial<SplitViewState>
}

export const SplitViewProvider: React.FC<SplitViewProviderProps> = ({ 
  children, 
  initialState: initialStateOverride 
}) => {
  const [state, dispatch] = useReducer(splitViewReducer, {
    ...initialState,
    ...initialStateOverride
  })

  // Action creators
  const setLayout = useCallback((layout: SplitLayout) => {
    dispatch({ type: 'SET_LAYOUT', payload: layout })
  }, [])

  const setOrientation = useCallback((orientation: SplitOrientation) => {
    dispatch({ type: 'SET_ORIENTATION', payload: orientation })
  }, [])

  const addPane = useCallback((config?: Partial<PaneConfig>) => {
    const paneId = `pane-${generateId()}`
    dispatch({ type: 'ADD_PANE', payload: { ...config, id: paneId } })
    return paneId
  }, [])

  const removePane = useCallback((paneId: string) => {
    dispatch({ type: 'REMOVE_PANE', payload: paneId })
  }, [])

  const updatePaneSize = useCallback((paneId: string, size: number) => {
    dispatch({ type: 'UPDATE_PANE_SIZE', payload: { paneId, size } })
  }, [])

  const resizePane = useCallback((paneId: string, size: number) => {
    dispatch({ type: 'RESIZE_PANE', payload: { paneId, size } })
  }, [])

  const splitPane = useCallback((direction: 'horizontal' | 'vertical', sourcePaneId?: string) => {
    dispatch({ type: 'SPLIT_PANE', payload: { direction, sourcePaneId } })
  }, [])

  const closePanePanel = useCallback((paneId: string) => {
    dispatch({ type: 'CLOSE_PANE', payload: paneId })
  }, [])

  const swapPanes = useCallback((paneId1: string, paneId2: string, tabId?: string) => {
    dispatch({ type: 'SWAP_PANES', payload: { paneId1, paneId2, tabId } })
  }, [])

  const addTab = useCallback((paneId: string, tab: Partial<FileTab>) => {
    const tabId = tab.id || `tab-${generateId()}`
    dispatch({ type: 'ADD_TAB', payload: { paneId, tab: { ...tab, id: tabId } } })
    return tabId
  }, [])

  const removeTab = useCallback((paneId: string, tabId: string) => {
    dispatch({ type: 'REMOVE_TAB', payload: { paneId, tabId } })
  }, [])

  const updateTab = useCallback((paneId: string, tabId: string, updates: Partial<FileTab>) => {
    dispatch({ type: 'UPDATE_TAB', payload: { paneId, tabId, updates } })
  }, [])

  const setActiveTab = useCallback((paneId: string, tabId: string) => {
    dispatch({ type: 'SET_ACTIVE_TAB', payload: { paneId, tabId } })
  }, [])

  const moveTab = useCallback((fromPaneId: string, toPaneId: string, tabId: string) => {
    dispatch({ type: 'MOVE_TAB', payload: { fromPaneId, toPaneId, tabId } })
  }, [])

  const duplicateTab = useCallback((paneId: string, tabId: string) => {
    const pane = state.panes[paneId]
    const tab = pane?.tabs.find(t => t.id === tabId)
    if (tab) {
      const newTabId = `tab-${generateId()}`
      addTab(paneId, {
        ...tab,
        id: newTabId,
        title: `${tab.title} (Copy)`,
        isDirty: false
      })
    }
  }, [state.panes, addTab])

  const updateTabContent = useCallback((paneId: string, tabId: string, content: string) => {
    dispatch({ type: 'UPDATE_TAB_CONTENT', payload: { paneId, tabId, content } })
  }, [])

  const saveTab = useCallback((paneId: string, tabId: string) => {
    // Implementation would save to file system or API
    updateTab(paneId, tabId, { isDirty: false })
  }, [updateTab])

  const saveAllTabs = useCallback(() => {
    Object.entries(state.panes).forEach(([paneId, pane]) => {
      pane.tabs.forEach(tab => {
        if (tab.isDirty) {
          saveTab(paneId, tab.id)
        }
      })
    })
  }, [state.panes, saveTab])

  const revertTab = useCallback((paneId: string, tabId: string) => {
    // Implementation would revert to saved content
    updateTab(paneId, tabId, { isDirty: false })
  }, [updateTab])

  const setActivePane = useCallback((paneId: string) => {
    dispatch({ type: 'SET_ACTIVE_PANE', payload: paneId })
  }, [])

  const focusNextPane = useCallback(() => {
    const paneIds = Object.keys(state.panes).filter(id => state.panes[id].visible)
    const currentIndex = paneIds.indexOf(state.activePaneId || '')
    const nextIndex = (currentIndex + 1) % paneIds.length
    setActivePane(paneIds[nextIndex])
  }, [state.panes, state.activePaneId, setActivePane])

  const focusPreviousPane = useCallback(() => {
    const paneIds = Object.keys(state.panes).filter(id => state.panes[id].visible)
    const currentIndex = paneIds.indexOf(state.activePaneId || '')
    const prevIndex = currentIndex === 0 ? paneIds.length - 1 : currentIndex - 1
    setActivePane(paneIds[prevIndex])
  }, [state.panes, state.activePaneId, setActivePane])

  const focusPane = useCallback((direction: 'up' | 'down' | 'left' | 'right') => {
    // Implementation would focus pane based on spatial direction
    // For now, just cycle through panes
    if (direction === 'right' || direction === 'down') {
      focusNextPane()
    } else {
      focusPreviousPane()
    }
  }, [focusNextPane, focusPreviousPane])

  const toggleSynchronizedScrolling = useCallback(() => {
    dispatch({ type: 'TOGGLE_SYNCHRONIZED_SCROLLING' })
  }, [])

  const toggleCompareMode = useCallback(() => {
    dispatch({ type: 'TOGGLE_COMPARE_MODE' })
  }, [])

  const toggleSnapToGrid = useCallback(() => {
    dispatch({ type: 'TOGGLE_SNAP_TO_GRID' })
  }, [])

  const updateSettings = useCallback((settings: Partial<typeof DEFAULT_SPLIT_VIEW_SETTINGS>) => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: settings })
  }, [])

  const resetLayout = useCallback(() => {
    dispatch({ type: 'RESET_LAYOUT' })
  }, [])

  const saveSession = useCallback((name: string) => {
    if (state.settings.persistLayout) {
      localStorage.setItem(`splitview-session-${name}`, JSON.stringify(state))
    }
  }, [state])

  const loadSession = useCallback((name: string) => {
    if (state.settings.persistLayout) {
      const saved = localStorage.getItem(`splitview-session-${name}`)
      if (saved) {
        try {
          const parsedState = JSON.parse(saved)
          dispatch({ type: 'LOAD_STATE', payload: parsedState })
        } catch (error) {
          console.error('Failed to load session:', error)
        }
      }
    }
  }, [state.settings.persistLayout])

  const getSavedSessions = useCallback(() => {
    const sessions: string[] = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key?.startsWith('splitview-session-')) {
        sessions.push(key.replace('splitview-session-', ''))
      }
    }
    return sessions
  }, [])

  const deleteSavedSession = useCallback((name: string) => {
    localStorage.removeItem(`splitview-session-${name}`)
  }, [])

  // Auto-save session
  useEffect(() => {
    if (state.settings.persistLayout) {
      const timeoutId = setTimeout(() => {
        saveSession('auto-save')
      }, 1000)
      return () => clearTimeout(timeoutId)
    }
  }, [state, saveSession])

  const contextValue: SplitViewContextType = {
    ...state,
    setLayout,
    setOrientation,
    addPane,
    removePane,
    updatePaneSize,
    resizePane,
    splitPane,
    closePanePanel,
    swapPanes,
    addTab,
    removeTab,
    updateTab,
    setActiveTab,
    moveTab,
    duplicateTab,
    updateTabContent,
    saveTab,
    saveAllTabs,
    revertTab,
    setActivePane,
    focusNextPane,
    focusPreviousPane,
    focusPane,
    toggleSynchronizedScrolling,
    toggleCompareMode,
    toggleSnapToGrid,
    updateSettings,
    resetLayout,
    saveSession,
    loadSession,
    getSavedSessions,
    deleteSavedSession
  }

  return (
    <SplitViewContext.Provider value={contextValue}>
      {children}
    </SplitViewContext.Provider>
  )
}