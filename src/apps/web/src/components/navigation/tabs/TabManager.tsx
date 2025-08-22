import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Tab, TabGroup, TabManagerState, EditorFile } from '../types/TabTypes'
import { TabBar } from './TabBar'
import { TabGroupBar } from './TabGroupBar'
import { SplitView } from './SplitView'
import { TabContextMenu } from './TabContextMenu'
import { TabSearchDialog } from './TabSearchDialog'
import { MonacoEditor } from './MonacoEditor'
import { useTabPersistence } from '../hooks/useTabPersistence'
import { useTabKeyboardNavigation } from '../hooks/useTabKeyboardNavigation'
import { useTabDragAndDrop } from '../hooks/useTabDragAndDrop'
import '../styles/tab-manager.css'

export interface TabManagerProps {
  initialFiles?: EditorFile[]
  onFileChange?: (file: EditorFile) => void
  onTabClose?: (tabId: string) => void
  maxTabs?: number
  enablePersistence?: boolean
  enableKeyboardNavigation?: boolean
  enableDragAndDrop?: boolean
  enableSplitView?: boolean
  enableTabGroups?: boolean
}

export const TabManager: React.FC<TabManagerProps> = ({
  initialFiles = [],
  onFileChange,
  onTabClose,
  maxTabs = 50,
  enablePersistence = true,
  enableKeyboardNavigation = true,
  enableDragAndDrop = true,
  enableSplitView = true,
  enableTabGroups = true
}) => {
  const [state, setState] = useState<TabManagerState>({
    tabs: [],
    tabGroups: [],
    splitPanels: [{ id: 'main', tabs: [], activeTabId: null }],
    activeTabId: null,
    activePanelId: 'main',
    recentFiles: [],
    unsavedChanges: new Set(),
    pinnedTabs: new Set(),
    searchQuery: ''
  })

  const [showSearch, setShowSearch] = useState(false)
  const [contextMenu, setContextMenu] = useState<{
    visible: boolean
    x: number
    y: number
    tabId: string | null
  }>({ visible: false, x: 0, y: 0, tabId: null })

  const containerRef = useRef<HTMLDivElement>(null)

  // Custom hooks
  const { saveTabState, loadTabState } = useTabPersistence(enablePersistence)
  const { setupKeyboardNavigation } = useTabKeyboardNavigation(enableKeyboardNavigation)
  const { setupDragAndDrop } = useTabDragAndDrop(enableDragAndDrop)

  // Initialize with files
  useEffect(() => {
    if (initialFiles.length > 0) {
      const tabs: Tab[] = initialFiles.map((file, index) => ({
        id: `tab-${Date.now()}-${index}`,
        fileId: file.id,
        title: file.name,
        filePath: file.path,
        language: file.language || 'plaintext',
        content: file.content || '',
        isDirty: false,
        isPinned: false,
        isActive: index === 0,
        lastModified: new Date(),
        groupId: null
      }))

      setState(prev => ({
        ...prev,
        tabs,
        activeTabId: tabs[0]?.id || null,
        splitPanels: [{
          id: 'main',
          tabs: tabs.map(t => t.id),
          activeTabId: tabs[0]?.id || null
        }]
      }))
    }
  }, [initialFiles])

  // Load persisted state
  useEffect(() => {
    if (enablePersistence) {
      const persistedState = loadTabState()
      if (persistedState) {
        setState(prev => ({ ...prev, ...persistedState }))
      }
    }
  }, [enablePersistence, loadTabState])

  // Save state on changes
  useEffect(() => {
    if (enablePersistence) {
      saveTabState(state)
    }
  }, [state, enablePersistence, saveTabState])

  // Setup keyboard navigation
  useEffect(() => {
    if (enableKeyboardNavigation) {
      const cleanup = setupKeyboardNavigation({
        onNextTab: () => navigateTab('next'),
        onPreviousTab: () => navigateTab('previous'),
        onCloseTab: () => closeActiveTab(),
        onNewTab: () => createNewTab(),
        onToggleSearch: () => setShowSearch(prev => !prev),
        onSave: () => saveActiveTab(),
        onCloseAll: () => closeAllTabs(),
        onGoToTab: (index: number) => goToTabByIndex(index)
      })
      return cleanup
    }
  }, [enableKeyboardNavigation, setupKeyboardNavigation])

  // Setup drag and drop
  useEffect(() => {
    if (enableDragAndDrop && containerRef.current) {
      const cleanup = setupDragAndDrop(containerRef.current, {
        onTabMove: moveTab,
        onTabToPanel: moveTabToPanel,
        onCreatePanel: createSplitPanel,
        onReorderTabs: reorderTabs
      })
      return cleanup
    }
  }, [enableDragAndDrop, setupDragAndDrop])

  // Tab operations
  const createNewTab = useCallback((file?: EditorFile) => {
    if (state.tabs.length >= maxTabs) {
      console.warn(`Maximum tabs (${maxTabs}) reached`)
      return
    }

    const newTab: Tab = {
      id: `tab-${Date.now()}`,
      fileId: file?.id || `new-${Date.now()}`,
      title: file?.name || 'Untitled',
      filePath: file?.path || '',
      language: file?.language || 'plaintext',
      content: file?.content || '',
      isDirty: false,
      isPinned: false,
      isActive: true,
      lastModified: new Date(),
      groupId: null
    }

    setState(prev => {
      const newTabs = prev.tabs.map(t => ({ ...t, isActive: false }))
      newTabs.push(newTab)

      const activePanel = prev.splitPanels.find(p => p.id === prev.activePanelId)
      const updatedPanels = prev.splitPanels.map(panel => 
        panel.id === prev.activePanelId
          ? { ...panel, tabs: [...panel.tabs, newTab.id], activeTabId: newTab.id }
          : panel
      )

      return {
        ...prev,
        tabs: newTabs,
        activeTabId: newTab.id,
        splitPanels: updatedPanels,
        recentFiles: [newTab.fileId, ...prev.recentFiles.slice(0, 9)]
      }
    })
  }, [state.tabs.length, maxTabs])

  const closeTab = useCallback((tabId: string, force = false) => {
    const tab = state.tabs.find(t => t.id === tabId)
    if (!tab) return

    // Check for unsaved changes
    if (!force && state.unsavedChanges.has(tabId)) {
      const confirmed = window.confirm(`File "${tab.title}" has unsaved changes. Close anyway?`)
      if (!confirmed) return
    }

    setState(prev => {
      const newTabs = prev.tabs.filter(t => t.id !== tabId)
      const newUnsavedChanges = new Set(prev.unsavedChanges)
      newUnsavedChanges.delete(tabId)
      
      const newPinnedTabs = new Set(prev.pinnedTabs)
      newPinnedTabs.delete(tabId)

      // Update panels
      const updatedPanels = prev.splitPanels.map(panel => {
        const tabIndex = panel.tabs.indexOf(tabId)
        if (tabIndex === -1) return panel

        const newPanelTabs = panel.tabs.filter(t => t !== tabId)
        let newActiveTabId = panel.activeTabId

        // If closing active tab, find next active tab
        if (panel.activeTabId === tabId) {
          if (newPanelTabs.length > 0) {
            const nextIndex = Math.min(tabIndex, newPanelTabs.length - 1)
            newActiveTabId = newPanelTabs[nextIndex]
          } else {
            newActiveTabId = null
          }
        }

        return {
          ...panel,
          tabs: newPanelTabs,
          activeTabId: newActiveTabId
        }
      })

      // Find new global active tab
      let newActiveTabId = prev.activeTabId
      if (prev.activeTabId === tabId) {
        const activePanel = updatedPanels.find(p => p.id === prev.activePanelId)
        newActiveTabId = activePanel?.activeTabId || null
      }

      return {
        ...prev,
        tabs: newTabs,
        activeTabId: newActiveTabId,
        splitPanels: updatedPanels,
        unsavedChanges: newUnsavedChanges,
        pinnedTabs: newPinnedTabs
      }
    })

    onTabClose?.(tabId)
  }, [state.tabs, state.unsavedChanges, onTabClose])

  const closeActiveTab = useCallback(() => {
    if (state.activeTabId) {
      closeTab(state.activeTabId)
    }
  }, [state.activeTabId, closeTab])

  const closeAllTabs = useCallback((force = false) => {
    if (!force && state.unsavedChanges.size > 0) {
      const confirmed = window.confirm(`${state.unsavedChanges.size} files have unsaved changes. Close all anyway?`)
      if (!confirmed) return
    }

    setState(prev => ({
      ...prev,
      tabs: [],
      activeTabId: null,
      splitPanels: [{ id: 'main', tabs: [], activeTabId: null }],
      activePanelId: 'main',
      unsavedChanges: new Set(),
      pinnedTabs: new Set()
    }))
  }, [state.unsavedChanges])

  const activateTab = useCallback((tabId: string, panelId?: string) => {
    setState(prev => {
      const targetPanelId = panelId || prev.activePanelId
      const updatedPanels = prev.splitPanels.map(panel =>
        panel.id === targetPanelId
          ? { ...panel, activeTabId: tabId }
          : panel
      )

      // Update recent files
      const tab = prev.tabs.find(t => t.id === tabId)
      const newRecentFiles = tab 
        ? [tab.fileId, ...prev.recentFiles.filter(f => f !== tab.fileId).slice(0, 9)]
        : prev.recentFiles

      return {
        ...prev,
        activeTabId: tabId,
        activePanelId: targetPanelId,
        splitPanels: updatedPanels,
        recentFiles: newRecentFiles
      }
    })
  }, [])

  const navigateTab = useCallback((direction: 'next' | 'previous') => {
    const activePanel = state.splitPanels.find(p => p.id === state.activePanelId)
    if (!activePanel || activePanel.tabs.length === 0) return

    const currentIndex = activePanel.tabs.indexOf(state.activeTabId || '')
    let nextIndex: number

    if (direction === 'next') {
      nextIndex = currentIndex >= activePanel.tabs.length - 1 ? 0 : currentIndex + 1
    } else {
      nextIndex = currentIndex <= 0 ? activePanel.tabs.length - 1 : currentIndex - 1
    }

    const nextTabId = activePanel.tabs[nextIndex]
    if (nextTabId) {
      activateTab(nextTabId)
    }
  }, [state.splitPanels, state.activePanelId, state.activeTabId, activateTab])

  const goToTabByIndex = useCallback((index: number) => {
    const activePanel = state.splitPanels.find(p => p.id === state.activePanelId)
    if (!activePanel || index < 0 || index >= activePanel.tabs.length) return

    const tabId = activePanel.tabs[index]
    if (tabId) {
      activateTab(tabId)
    }
  }, [state.splitPanels, state.activePanelId, activateTab])

  const pinTab = useCallback((tabId: string) => {
    setState(prev => {
      const newPinnedTabs = new Set(prev.pinnedTabs)
      if (newPinnedTabs.has(tabId)) {
        newPinnedTabs.delete(tabId)
      } else {
        newPinnedTabs.add(tabId)
      }
      return { ...prev, pinnedTabs: newPinnedTabs }
    })
  }, [])

  const duplicateTab = useCallback((tabId: string) => {
    const tab = state.tabs.find(t => t.id === tabId)
    if (!tab) return

    const duplicatedTab: Tab = {
      ...tab,
      id: `tab-${Date.now()}`,
      title: `${tab.title} (Copy)`,
      isActive: true,
      isDirty: false,
      isPinned: false
    }

    setState(prev => {
      const newTabs = prev.tabs.map(t => ({ ...t, isActive: false }))
      newTabs.push(duplicatedTab)

      const updatedPanels = prev.splitPanels.map(panel =>
        panel.id === prev.activePanelId
          ? { ...panel, tabs: [...panel.tabs, duplicatedTab.id], activeTabId: duplicatedTab.id }
          : panel
      )

      return {
        ...prev,
        tabs: newTabs,
        activeTabId: duplicatedTab.id,
        splitPanels: updatedPanels
      }
    })
  }, [state.tabs])

  const moveTab = useCallback((tabId: string, targetIndex: number, targetPanelId?: string) => {
    setState(prev => {
      const sourcePanelId = prev.splitPanels.find(p => p.tabs.includes(tabId))?.id
      const targetPanel = targetPanelId || prev.activePanelId

      if (!sourcePanelId) return prev

      // Remove from source panel
      const updatedPanels = prev.splitPanels.map(panel => {
        if (panel.id === sourcePanelId) {
          const newTabs = panel.tabs.filter(t => t !== tabId)
          return {
            ...panel,
            tabs: newTabs,
            activeTabId: panel.activeTabId === tabId 
              ? (newTabs.length > 0 ? newTabs[0] : null)
              : panel.activeTabId
          }
        }
        return panel
      })

      // Add to target panel
      const finalPanels = updatedPanels.map(panel => {
        if (panel.id === targetPanel) {
          const newTabs = [...panel.tabs]
          newTabs.splice(targetIndex, 0, tabId)
          return {
            ...panel,
            tabs: newTabs,
            activeTabId: tabId
          }
        }
        return panel
      })

      return {
        ...prev,
        splitPanels: finalPanels,
        activeTabId: tabId,
        activePanelId: targetPanel
      }
    })
  }, [])

  const moveTabToPanel = useCallback((tabId: string, targetPanelId: string) => {
    moveTab(tabId, 0, targetPanelId)
  }, [moveTab])

  const reorderTabs = useCallback((tabIds: string[], panelId: string) => {
    setState(prev => {
      const updatedPanels = prev.splitPanels.map(panel =>
        panel.id === panelId
          ? { ...panel, tabs: tabIds }
          : panel
      )
      return { ...prev, splitPanels: updatedPanels }
    })
  }, [])

  const createSplitPanel = useCallback((direction: 'horizontal' | 'vertical', tabId?: string) => {
    if (!enableSplitView) return

    const newPanelId = `panel-${Date.now()}`
    const newPanel = {
      id: newPanelId,
      tabs: tabId ? [tabId] : [],
      activeTabId: tabId || null
    }

    setState(prev => {
      // If moving a tab, remove it from current panel
      let updatedPanels = prev.splitPanels
      if (tabId) {
        updatedPanels = prev.splitPanels.map(panel => ({
          ...panel,
          tabs: panel.tabs.filter(t => t !== tabId),
          activeTabId: panel.activeTabId === tabId 
            ? (panel.tabs.filter(t => t !== tabId)[0] || null)
            : panel.activeTabId
        }))
      }

      return {
        ...prev,
        splitPanels: [...updatedPanels, newPanel],
        activePanelId: newPanelId
      }
    })
  }, [enableSplitView])

  const createTabGroup = useCallback((name: string, color: string, tabIds: string[] = []) => {
    if (!enableTabGroups) return

    const newGroup: TabGroup = {
      id: `group-${Date.now()}`,
      name,
      color,
      isCollapsed: false,
      tabIds
    }

    setState(prev => {
      // Update tabs to belong to this group
      const updatedTabs = prev.tabs.map(tab =>
        tabIds.includes(tab.id) ? { ...tab, groupId: newGroup.id } : tab
      )

      return {
        ...prev,
        tabs: updatedTabs,
        tabGroups: [...prev.tabGroups, newGroup]
      }
    })
  }, [enableTabGroups])

  const updateTabContent = useCallback((tabId: string, content: string) => {
    setState(prev => {
      const tab = prev.tabs.find(t => t.id === tabId)
      if (!tab) return prev

      const isDirty = content !== tab.content
      const updatedTabs = prev.tabs.map(t =>
        t.id === tabId
          ? { ...t, content, isDirty, lastModified: new Date() }
          : t
      )

      const newUnsavedChanges = new Set(prev.unsavedChanges)
      if (isDirty) {
        newUnsavedChanges.add(tabId)
      } else {
        newUnsavedChanges.delete(tabId)
      }

      return {
        ...prev,
        tabs: updatedTabs,
        unsavedChanges: newUnsavedChanges
      }
    })

    // Notify parent component
    const tab = state.tabs.find(t => t.id === tabId)
    if (tab && onFileChange) {
      onFileChange({
        id: tab.fileId,
        name: tab.title,
        path: tab.filePath,
        content,
        language: tab.language
      })
    }
  }, [state.tabs, onFileChange])

  const saveActiveTab = useCallback(() => {
    if (!state.activeTabId) return

    setState(prev => {
      const newUnsavedChanges = new Set(prev.unsavedChanges)
      newUnsavedChanges.delete(state.activeTabId!)
      
      const updatedTabs = prev.tabs.map(t =>
        t.id === state.activeTabId ? { ...t, isDirty: false } : t
      )

      return {
        ...prev,
        tabs: updatedTabs,
        unsavedChanges: newUnsavedChanges
      }
    })
  }, [state.activeTabId])

  const handleContextMenu = useCallback((e: React.MouseEvent, tabId: string) => {
    e.preventDefault()
    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      tabId
    })
  }, [])

  const closeContextMenu = useCallback(() => {
    setContextMenu(prev => ({ ...prev, visible: false, tabId: null }))
  }, [])

  // Get active tab
  const activeTab = state.tabs.find(t => t.id === state.activeTabId)

  return (
    <div ref={containerRef} className="tab-manager" onContextMenu={e => e.preventDefault()}>
      {/* Tab Groups Bar */}
      {enableTabGroups && state.tabGroups.length > 0 && (
        <TabGroupBar
          groups={state.tabGroups}
          tabs={state.tabs}
          onGroupCollapse={(groupId) => {
            setState(prev => ({
              ...prev,
              tabGroups: prev.tabGroups.map(g =>
                g.id === groupId ? { ...g, isCollapsed: !g.isCollapsed } : g
              )
            }))
          }}
          onGroupDelete={(groupId) => {
            setState(prev => ({
              ...prev,
              tabGroups: prev.tabGroups.filter(g => g.id !== groupId),
              tabs: prev.tabs.map(t => t.groupId === groupId ? { ...t, groupId: null } : t)
            }))
          }}
        />
      )}

      {/* Split View Container */}
      <SplitView
        panels={state.splitPanels}
        tabs={state.tabs}
        activeTabId={state.activeTabId}
        activePanelId={state.activePanelId}
        pinnedTabs={state.pinnedTabs}
        unsavedChanges={state.unsavedChanges}
        tabGroups={state.tabGroups}
        onTabSelect={activateTab}
        onTabClose={closeTab}
        onTabPin={pinTab}
        onTabContextMenu={handleContextMenu}
        onPanelSelect={(panelId) => setState(prev => ({ ...prev, activePanelId: panelId }))}
        onTabMove={moveTab}
        onCreatePanel={createSplitPanel}
        enableDragAndDrop={enableDragAndDrop}
      />

      {/* Editor Content */}
      {activeTab && (
        <div className="editor-content">
          <MonacoEditor
            key={activeTab.id}
            language={activeTab.language}
            value={activeTab.content}
            onChange={(value) => updateTabContent(activeTab.id, value)}
            onSave={() => saveActiveTab()}
            filePath={activeTab.filePath}
            height="calc(100vh - 200px)"
            enableLSP={true}
            enableGitIntegration={true}
            enableDebugger={true}
          />
        </div>
      )}

      {/* Tab Search Dialog */}
      {showSearch && (
        <TabSearchDialog
          tabs={state.tabs}
          recentFiles={state.recentFiles}
          onTabSelect={(tabId) => {
            activateTab(tabId)
            setShowSearch(false)
          }}
          onClose={() => setShowSearch(false)}
        />
      )}

      {/* Context Menu */}
      {contextMenu.visible && contextMenu.tabId && (
        <TabContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          tabId={contextMenu.tabId}
          tab={state.tabs.find(t => t.id === contextMenu.tabId)!}
          isPinned={state.pinnedTabs.has(contextMenu.tabId)}
          hasUnsavedChanges={state.unsavedChanges.has(contextMenu.tabId)}
          onClose={closeContextMenu}
          onCloseTab={closeTab}
          onPinTab={pinTab}
          onDuplicateTab={duplicateTab}
          onMoveToNewPanel={(tabId) => createSplitPanel('horizontal', tabId)}
          onCreateGroup={(tabId) => {
            const tab = state.tabs.find(t => t.id === tabId)
            if (tab) {
              createTabGroup(`Group for ${tab.title}`, '#007acc', [tabId])
            }
          }}
        />
      )}
    </div>
  )
}

export default TabManager