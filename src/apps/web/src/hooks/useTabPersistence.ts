import { useCallback, useRef } from 'react'
import { TabManagerState, TabSessionData } from '../types/TabTypes'

const STORAGE_KEY = 'tab-manager-state'
const STORAGE_VERSION = '1.0'
const MAX_STORED_SESSIONS = 10

export interface TabPersistenceHook {
  saveTabState: (state: TabManagerState) => void
  loadTabState: () => Partial<TabManagerState> | null
  clearTabState: () => void
  exportTabSession: (state: TabManagerState) => string
  importTabSession: (data: string) => Partial<TabManagerState> | null
  getSavedSessions: () => TabSessionData[]
  deleteSession: (timestamp: number) => void
}

export function useTabPersistence(enabled: boolean = true): TabPersistenceHook {
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Save tab state to localStorage with debouncing
  const saveTabState = useCallback((state: TabManagerState) => {
    if (!enabled || typeof window === 'undefined') return

    // Debounce saves to avoid excessive localStorage writes
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }

    saveTimeoutRef.current = setTimeout(() => {
      try {
        const sessionData: TabSessionData = {
          version: STORAGE_VERSION,
          timestamp: Date.now(),
          state: {
            tabs: state.tabs.map(tab => ({
              ...tab,
              // Don't persist large content to avoid localStorage limits
              content: tab.content.length > 10000 ? '' : tab.content
            })),
            tabGroups: state.tabGroups,
            splitPanels: state.splitPanels,
            activeTabId: state.activeTabId,
            activePanelId: state.activePanelId,
            recentFiles: state.recentFiles,
            pinnedTabs: Array.from(state.pinnedTabs),
            searchQuery: state.searchQuery
          }
        }

        localStorage.setItem(STORAGE_KEY, JSON.stringify(sessionData))

        // Also save to session history
        const sessions = getSavedSessions()
        sessions.unshift(sessionData)
        
        // Keep only recent sessions
        const recentSessions = sessions.slice(0, MAX_STORED_SESSIONS)
        localStorage.setItem(`${STORAGE_KEY}-history`, JSON.stringify(recentSessions))

      } catch (error) {
        console.warn('Failed to save tab state:', error)
        
        // If storage is full, try to clear old data
        try {
          localStorage.removeItem(`${STORAGE_KEY}-history`)
          localStorage.setItem(STORAGE_KEY, JSON.stringify({
            version: STORAGE_VERSION,
            timestamp: Date.now(),
            state: {
              tabs: [],
              tabGroups: [],
              splitPanels: [{ id: 'main', tabs: [], activeTabId: null }],
              activeTabId: null,
              activePanelId: 'main',
              recentFiles: [],
              pinnedTabs: [],
              searchQuery: ''
            }
          }))
        } catch (clearError) {
          console.error('Failed to clear storage:', clearError)
        }
      }
    }, 1000) // 1 second debounce
  }, [enabled])

  // Load tab state from localStorage
  const loadTabState = useCallback((): Partial<TabManagerState> | null => {
    if (!enabled || typeof window === 'undefined') return null

    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (!stored) return null

      const sessionData: TabSessionData = JSON.parse(stored)
      
      // Check version compatibility
      if (sessionData.version !== STORAGE_VERSION) {
        console.warn('Tab state version mismatch, clearing state')
        clearTabState()
        return null
      }

      // Validate and restore state
      const state = sessionData.state
      if (!state || !Array.isArray(state.tabs)) return null

      return {
        ...state,
        // Convert arrays back to Sets where needed
        unsavedChanges: new Set(),
        pinnedTabs: new Set(state.pinnedTabs || []),
        // Ensure splitPanels has at least one panel
        splitPanels: state.splitPanels && state.splitPanels.length > 0 
          ? state.splitPanels 
          : [{ id: 'main', tabs: [], activeTabId: null }]
      }
    } catch (error) {
      console.warn('Failed to load tab state:', error)
      clearTabState()
      return null
    }
  }, [enabled])

  // Clear all saved state
  const clearTabState = useCallback(() => {
    if (typeof window === 'undefined') return

    try {
      localStorage.removeItem(STORAGE_KEY)
      localStorage.removeItem(`${STORAGE_KEY}-history`)
    } catch (error) {
      console.warn('Failed to clear tab state:', error)
    }
  }, [])

  // Export current session as JSON
  const exportTabSession = useCallback((state: TabManagerState): string => {
    const sessionData: TabSessionData = {
      version: STORAGE_VERSION,
      timestamp: Date.now(),
      state: {
        tabs: state.tabs,
        tabGroups: state.tabGroups,
        splitPanels: state.splitPanels,
        activeTabId: state.activeTabId,
        activePanelId: state.activePanelId,
        recentFiles: state.recentFiles,
        pinnedTabs: Array.from(state.pinnedTabs),
        searchQuery: state.searchQuery
      }
    }

    return JSON.stringify(sessionData, null, 2)
  }, [])

  // Import session from JSON
  const importTabSession = useCallback((data: string): Partial<TabManagerState> | null => {
    try {
      const sessionData: TabSessionData = JSON.parse(data)
      
      if (sessionData.version !== STORAGE_VERSION) {
        console.warn('Imported session version mismatch')
        return null
      }

      const state = sessionData.state
      if (!state || !Array.isArray(state.tabs)) {
        console.warn('Invalid session data structure')
        return null
      }

      return {
        ...state,
        unsavedChanges: new Set(),
        pinnedTabs: new Set(state.pinnedTabs || []),
        splitPanels: state.splitPanels && state.splitPanels.length > 0 
          ? state.splitPanels 
          : [{ id: 'main', tabs: [], activeTabId: null }]
      }
    } catch (error) {
      console.warn('Failed to import tab session:', error)
      return null
    }
  }, [])

  // Get saved session history
  const getSavedSessions = useCallback((): TabSessionData[] => {
    if (typeof window === 'undefined') return []

    try {
      const stored = localStorage.getItem(`${STORAGE_KEY}-history`)
      if (!stored) return []

      const sessions = JSON.parse(stored)
      return Array.isArray(sessions) ? sessions : []
    } catch (error) {
      console.warn('Failed to load session history:', error)
      return []
    }
  }, [])

  // Delete a specific session
  const deleteSession = useCallback((timestamp: number) => {
    if (typeof window === 'undefined') return

    try {
      const sessions = getSavedSessions()
      const filteredSessions = sessions.filter(session => session.timestamp !== timestamp)
      localStorage.setItem(`${STORAGE_KEY}-history`, JSON.stringify(filteredSessions))
    } catch (error) {
      console.warn('Failed to delete session:', error)
    }
  }, [getSavedSessions])

  // Cleanup timeout on unmount
  React.useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [])

  return {
    saveTabState,
    loadTabState,
    clearTabState,
    exportTabSession,
    importTabSession,
    getSavedSessions,
    deleteSession
  }
}

export default useTabPersistence