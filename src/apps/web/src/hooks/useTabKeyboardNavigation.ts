import { useCallback, useEffect, useRef } from 'react'
import { TabKeyboardShortcuts } from '../types/TabTypes'

export interface KeyboardNavigationOptions {
  enableGlobalShortcuts?: boolean
  enableTabSwitching?: boolean
  enableTabOperations?: boolean
  customShortcuts?: Record<string, () => void>
}

export function useTabKeyboardNavigation(
  enabled: boolean = true,
  options: KeyboardNavigationOptions = {}
) {
  const {
    enableGlobalShortcuts = true,
    enableTabSwitching = true,
    enableTabOperations = true,
    customShortcuts = {}
  } = options

  const handlersRef = useRef<TabKeyboardShortcuts | null>(null)
  const isHandlingRef = useRef(false)

  const setupKeyboardNavigation = useCallback((handlers: TabKeyboardShortcuts) => {
    if (!enabled) return () => {}

    handlersRef.current = handlers

    const handleKeyDown = (event: KeyboardEvent) => {
      // Prevent handling if already processing an event
      if (isHandlingRef.current) return

      // Don't intercept if user is typing in an input
      const target = event.target as HTMLElement
      if (target?.tagName === 'INPUT' || 
          target?.tagName === 'TEXTAREA' || 
          target?.contentEditable === 'true') {
        return
      }

      isHandlingRef.current = true

      try {
        // Handle custom shortcuts first
        const shortcutKey = getShortcutKey(event)
        if (customShortcuts[shortcutKey]) {
          event.preventDefault()
          customShortcuts[shortcutKey]()
          return
        }

        // Global shortcuts
        if (enableGlobalShortcuts) {
          // Ctrl+T - New tab
          if (event.ctrlKey && event.key === 't' && !event.shiftKey && !event.altKey) {
            event.preventDefault()
            handlers.onNewTab()
            return
          }

          // Ctrl+Shift+T - Reopen closed tab (future feature)
          if (event.ctrlKey && event.shiftKey && event.key === 'T') {
            event.preventDefault()
            // Future: reopen last closed tab
            return
          }

          // Ctrl+W - Close current tab
          if (event.ctrlKey && event.key === 'w' && !event.shiftKey && !event.altKey) {
            event.preventDefault()
            handlers.onCloseTab()
            return
          }

          // Ctrl+Shift+W - Close all tabs
          if (event.ctrlKey && event.shiftKey && event.key === 'W') {
            event.preventDefault()
            handlers.onCloseAll()
            return
          }

          // Ctrl+S - Save current tab
          if (event.ctrlKey && event.key === 's' && !event.shiftKey && !event.altKey) {
            event.preventDefault()
            handlers.onSave()
            return
          }

          // Ctrl+P or Ctrl+Shift+P - Command palette / Quick open
          if (event.ctrlKey && event.key === 'p') {
            event.preventDefault()
            handlers.onToggleSearch()
            return
          }
        }

        // Tab switching shortcuts
        if (enableTabSwitching) {
          // Ctrl+Tab - Next tab
          if (event.ctrlKey && event.key === 'Tab' && !event.shiftKey) {
            event.preventDefault()
            handlers.onNextTab()
            return
          }

          // Ctrl+Shift+Tab - Previous tab
          if (event.ctrlKey && event.shiftKey && event.key === 'Tab') {
            event.preventDefault()
            handlers.onPreviousTab()
            return
          }

          // Ctrl+PageDown - Next tab (alternative)
          if (event.ctrlKey && event.key === 'PageDown') {
            event.preventDefault()
            handlers.onNextTab()
            return
          }

          // Ctrl+PageUp - Previous tab (alternative)
          if (event.ctrlKey && event.key === 'PageUp') {
            event.preventDefault()
            handlers.onPreviousTab()
            return
          }

          // Ctrl+1-9 - Go to tab by index
          if (event.ctrlKey && /^[1-9]$/.test(event.key)) {
            event.preventDefault()
            const index = parseInt(event.key) - 1
            handlers.onGoToTab(index)
            return
          }

          // Ctrl+0 - Go to last tab
          if (event.ctrlKey && event.key === '0') {
            event.preventDefault()
            handlers.onGoToTab(-1) // -1 indicates last tab
            return
          }
        }

        // Tab operations
        if (enableTabOperations) {
          // Alt+Left Arrow - Previous tab
          if (event.altKey && event.key === 'ArrowLeft') {
            event.preventDefault()
            handlers.onPreviousTab()
            return
          }

          // Alt+Right Arrow - Next tab
          if (event.altKey && event.key === 'ArrowRight') {
            event.preventDefault()
            handlers.onNextTab()
            return
          }

          // Ctrl+D - Duplicate tab (future feature)
          if (event.ctrlKey && event.key === 'd' && !event.shiftKey && !event.altKey) {
            event.preventDefault()
            // Future: duplicate current tab
            return
          }
        }
      } finally {
        isHandlingRef.current = false
      }
    }

    // Handle mousewheel on tab bar for tab switching
    const handleTabBarWheel = (event: WheelEvent) => {
      const target = event.target as HTMLElement
      if (target?.closest('.tab-bar')) {
        if (event.ctrlKey) {
          event.preventDefault()
          if (event.deltaY > 0) {
            handlers.onNextTab()
          } else {
            handlers.onPreviousTab()
          }
        }
      }
    }

    // Add event listeners
    document.addEventListener('keydown', handleKeyDown, true)
    document.addEventListener('wheel', handleTabBarWheel, { passive: false })

    // Cleanup function
    return () => {
      document.removeEventListener('keydown', handleKeyDown, true)
      document.removeEventListener('wheel', handleTabBarWheel)
      handlersRef.current = null
    }
  }, [enabled, enableGlobalShortcuts, enableTabSwitching, enableTabOperations, customShortcuts])

  // Helper function to create shortcut key string
  const getShortcutKey = (event: KeyboardEvent): string => {
    const parts = []
    if (event.ctrlKey) parts.push('ctrl')
    if (event.shiftKey) parts.push('shift')
    if (event.altKey) parts.push('alt')
    if (event.metaKey) parts.push('meta')
    parts.push(event.key.toLowerCase())
    return parts.join('+')
  }

  // Handle focus management for accessibility
  useEffect(() => {
    if (!enabled) return

    const handleFocusManagement = (event: FocusEvent) => {
      const target = event.target as HTMLElement
      
      // If focus moves to a tab, ensure it's visible
      if (target?.closest('.tab-item')) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'nearest'
        })
      }
    }

    document.addEventListener('focusin', handleFocusManagement)
    return () => document.removeEventListener('focusin', handleFocusManagement)
  }, [enabled])

  return { setupKeyboardNavigation }
}

// Predefined shortcut configurations
export const SHORTCUT_PRESETS = {
  vscode: {
    'ctrl+t': () => console.log('New tab'),
    'ctrl+w': () => console.log('Close tab'),
    'ctrl+shift+t': () => console.log('Reopen tab'),
    'ctrl+p': () => console.log('Quick open'),
    'ctrl+shift+p': () => console.log('Command palette'),
    'ctrl+tab': () => console.log('Next tab'),
    'ctrl+shift+tab': () => console.log('Previous tab'),
    'ctrl+pagedown': () => console.log('Next tab'),
    'ctrl+pageup': () => console.log('Previous tab')
  },
  
  browser: {
    'ctrl+t': () => console.log('New tab'),
    'ctrl+w': () => console.log('Close tab'),
    'ctrl+shift+t': () => console.log('Reopen tab'),
    'ctrl+l': () => console.log('Focus address bar'),
    'ctrl+tab': () => console.log('Next tab'),
    'ctrl+shift+tab': () => console.log('Previous tab'),
    'ctrl+shift+a': () => console.log('Tab groups'),
    'f6': () => console.log('Next pane')
  },

  custom: {
    'ctrl+alt+n': () => console.log('New panel'),
    'ctrl+alt+w': () => console.log('Close panel'),
    'ctrl+alt+tab': () => console.log('Next panel'),
    'ctrl+shift+d': () => console.log('Split right'),
    'ctrl+shift+s': () => console.log('Split down'),
    'f1': () => console.log('Help'),
    'f11': () => console.log('Toggle fullscreen')
  }
}

export default useTabKeyboardNavigation