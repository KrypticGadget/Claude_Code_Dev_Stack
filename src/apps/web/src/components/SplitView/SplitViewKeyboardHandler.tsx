import React, { useEffect, useCallback } from 'react'
import { useSplitView } from './SplitViewContext'
import { KEYBOARD_SHORTCUTS } from './types'

interface SplitViewKeyboardHandlerProps {
  children: React.ReactNode
  enabled?: boolean
}

export const SplitViewKeyboardHandler: React.FC<SplitViewKeyboardHandlerProps> = ({
  children,
  enabled = true
}) => {
  const {
    panes,
    activePaneId,
    settings,
    splitPane,
    addTab,
    removeTab,
    setActiveTab,
    closePanePanel,
    focusNextPane,
    focusPreviousPane,
    focusPane,
    saveTab,
    saveAllTabs,
    toggleSynchronizedScrolling,
    toggleCompareMode
  } = useSplitView()

  // Handle keyboard shortcuts
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled || !settings.enableKeyboardShortcuts) {
      return
    }

    // Don't handle shortcuts when typing in inputs
    const target = event.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      return
    }

    const { ctrlKey, shiftKey, altKey, metaKey, key } = event
    const isModifierKey = ctrlKey || metaKey // Support both Ctrl and Cmd

    // Find matching shortcut
    const shortcut = KEYBOARD_SHORTCUTS.find(s => {
      return s.key === key &&
             (s.ctrlKey === isModifierKey) &&
             (s.shiftKey === shiftKey) &&
             (s.altKey === altKey) &&
             (s.metaKey === metaKey)
    })

    if (!shortcut) {
      return
    }

    event.preventDefault()
    event.stopPropagation()

    const activePane = activePaneId ? panes[activePaneId] : null
    const activeTab = activePane?.tabs.find(tab => tab.id === activePane.activeTabId)

    // Execute shortcut action
    switch (shortcut.action) {
      case 'split-horizontal':
        splitPane('horizontal')
        break

      case 'split-vertical':
        splitPane('vertical')
        break

      case 'new-tab':
        if (activePaneId) {
          addTab(activePaneId, {
            title: 'Untitled',
            filePath: '',
            language: 'plaintext',
            content: '',
            isDirty: false,
            isActive: true,
            canClose: true
          })
        }
        break

      case 'close-tab':
        if (activePane && activeTab && activeTab.canClose) {
          removeTab(activePaneId!, activeTab.id)
        }
        break

      case 'close-pane':
        if (activePaneId && Object.keys(panes).length > 1) {
          closePanePanel(activePaneId)
        }
        break

      case 'next-tab':
        if (activePane && activePane.tabs.length > 1) {
          const currentIndex = activePane.tabs.findIndex(tab => tab.id === activePane.activeTabId)
          const nextIndex = (currentIndex + 1) % activePane.tabs.length
          setActiveTab(activePaneId!, activePane.tabs[nextIndex].id)
        }
        break

      case 'previous-tab':
        if (activePane && activePane.tabs.length > 1) {
          const currentIndex = activePane.tabs.findIndex(tab => tab.id === activePane.activeTabId)
          const prevIndex = currentIndex === 0 ? activePane.tabs.length - 1 : currentIndex - 1
          setActiveTab(activePaneId!, activePane.tabs[prevIndex].id)
        }
        break

      case 'focus-left-pane':
        focusPane('left')
        break

      case 'focus-right-pane':
        focusPane('right')
        break

      case 'focus-up-pane':
        focusPane('up')
        break

      case 'focus-down-pane':
        focusPane('down')
        break

      case 'save-tab':
        if (activePane && activeTab) {
          saveTab(activePaneId!, activeTab.id)
        }
        break

      case 'save-all':
        saveAllTabs()
        break

      case 'toggle-sync-scroll':
        toggleSynchronizedScrolling()
        break

      case 'toggle-compare':
        toggleCompareMode()
        break

      // Editor-specific shortcuts (these would be handled by Monaco)
      case 'undo':
      case 'redo':
      case 'find':
      case 'replace':
      case 'go-to-line':
      case 'toggle-comment':
      case 'duplicate-line':
      case 'select-line':
        // These are handled by Monaco editor itself
        break

      default:
        console.warn(`Unknown shortcut action: ${shortcut.action}`)
    }
  }, [
    enabled,
    settings.enableKeyboardShortcuts,
    panes,
    activePaneId,
    splitPane,
    addTab,
    removeTab,
    setActiveTab,
    closePanePanel,
    focusPane,
    saveTab,
    saveAllTabs,
    toggleSynchronizedScrolling,
    toggleCompareMode
  ])

  // Set up global keyboard event listeners
  useEffect(() => {
    if (enabled && settings.enableKeyboardShortcuts) {
      document.addEventListener('keydown', handleKeyDown, true)
      return () => {
        document.removeEventListener('keydown', handleKeyDown, true)
      }
    }
  }, [enabled, settings.enableKeyboardShortcuts, handleKeyDown])

  // Create keyboard shortcut help text
  const getShortcutHelp = useCallback(() => {
    return KEYBOARD_SHORTCUTS.map(shortcut => {
      const modifiers = []
      if (shortcut.ctrlKey) modifiers.push('Ctrl')
      if (shortcut.shiftKey) modifiers.push('Shift')
      if (shortcut.altKey) modifiers.push('Alt')
      if (shortcut.metaKey) modifiers.push('Cmd')
      
      const keyCombo = [...modifiers, shortcut.key].join(' + ')
      return {
        combo: keyCombo,
        description: shortcut.description
      }
    })
  }, [])

  // Provide keyboard shortcuts context to children
  return (
    <div className="split-view-keyboard-handler">
      {children}
      
      {/* Hidden element for screen readers */}
      <div 
        aria-live="polite" 
        aria-atomic="true" 
        className="sr-only"
        role="status"
      >
        {/* Screen reader announcements for keyboard actions */}
      </div>
    </div>
  )
}

// Hook to get keyboard shortcuts help
export const useKeyboardShortcuts = () => {
  const { settings } = useSplitView()
  
  const getShortcutHelp = useCallback(() => {
    if (!settings.enableKeyboardShortcuts) {
      return []
    }
    
    return KEYBOARD_SHORTCUTS.map(shortcut => {
      const modifiers = []
      if (shortcut.ctrlKey) modifiers.push('Ctrl')
      if (shortcut.shiftKey) modifiers.push('Shift')
      if (shortcut.altKey) modifiers.push('Alt')
      if (shortcut.metaKey) modifiers.push('Cmd')
      
      const keyCombo = [...modifiers, shortcut.key].join(' + ')
      return {
        combo: keyCombo,
        description: shortcut.description,
        action: shortcut.action
      }
    })
  }, [settings.enableKeyboardShortcuts])

  const isShortcutActive = useCallback((action: string) => {
    return settings.enableKeyboardShortcuts && 
           KEYBOARD_SHORTCUTS.some(s => s.action === action)
  }, [settings.enableKeyboardShortcuts])

  return {
    shortcuts: getShortcutHelp(),
    isActive: settings.enableKeyboardShortcuts,
    isShortcutActive
  }
}

export default SplitViewKeyboardHandler