import React, { useEffect, useRef, useCallback } from 'react'
import { Tab, TabContextMenuAction } from '../types/TabTypes'
import '../styles/tab-context-menu.css'

export interface TabContextMenuProps {
  x: number
  y: number
  tabId: string
  tab: Tab
  isPinned: boolean
  hasUnsavedChanges: boolean
  onClose: () => void
  onCloseTab: (tabId: string) => void
  onPinTab: (tabId: string) => void
  onDuplicateTab: (tabId: string) => void
  onMoveToNewPanel: (tabId: string) => void
  onCreateGroup: (tabId: string) => void
}

export const TabContextMenu: React.FC<TabContextMenuProps> = ({
  x,
  y,
  tabId,
  tab,
  isPinned,
  hasUnsavedChanges,
  onClose,
  onCloseTab,
  onPinTab,
  onDuplicateTab,
  onMoveToNewPanel,
  onCreateGroup
}) => {
  const menuRef = useRef<HTMLDivElement>(null)

  // Close menu on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose()
      }
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [onClose])

  // Position menu within viewport
  const menuStyle = React.useMemo(() => {
    const style: React.CSSProperties = {
      position: 'fixed',
      left: x,
      top: y,
      zIndex: 10000
    }

    // Adjust position if menu would go off-screen
    if (typeof window !== 'undefined') {
      const menuWidth = 200
      const menuHeight = 300

      if (x + menuWidth > window.innerWidth) {
        style.left = x - menuWidth
      }

      if (y + menuHeight > window.innerHeight) {
        style.top = y - menuHeight
      }
    }

    return style
  }, [x, y])

  const actions: TabContextMenuAction[] = [
    {
      id: 'close',
      label: 'Close',
      shortcut: 'Ctrl+W',
      onClick: () => {
        onCloseTab(tabId)
        onClose()
      }
    },
    {
      id: 'close-others',
      label: 'Close Others',
      onClick: () => {
        // This would need to be implemented in the parent component
        console.log('Close others not implemented')
        onClose()
      }
    },
    {
      id: 'close-to-right',
      label: 'Close to the Right',
      onClick: () => {
        // This would need to be implemented in the parent component
        console.log('Close to right not implemented')
        onClose()
      }
    },
    {
      id: 'separator1',
      label: '',
      separator: true,
      onClick: () => {}
    },
    {
      id: 'pin',
      label: isPinned ? 'Unpin' : 'Pin',
      icon: '📌',
      onClick: () => {
        onPinTab(tabId)
        onClose()
      }
    },
    {
      id: 'duplicate',
      label: 'Duplicate',
      icon: '📋',
      shortcut: 'Ctrl+D',
      onClick: () => {
        onDuplicateTab(tabId)
        onClose()
      }
    },
    {
      id: 'separator2',
      label: '',
      separator: true,
      onClick: () => {}
    },
    {
      id: 'move-to-new-panel',
      label: 'Move to New Panel',
      icon: '🪟',
      onClick: () => {
        onMoveToNewPanel(tabId)
        onClose()
      }
    },
    {
      id: 'create-group',
      label: 'Create Group',
      icon: '📁',
      onClick: () => {
        onCreateGroup(tabId)
        onClose()
      }
    },
    {
      id: 'separator3',
      label: '',
      separator: true,
      onClick: () => {}
    },
    {
      id: 'copy-path',
      label: 'Copy Path',
      icon: '📄',
      shortcut: 'Ctrl+Shift+C',
      onClick: () => {
        navigator.clipboard.writeText(tab.filePath || tab.title)
        onClose()
      }
    },
    {
      id: 'copy-filename',
      label: 'Copy Filename',
      onClick: () => {
        navigator.clipboard.writeText(tab.title)
        onClose()
      }
    },
    {
      id: 'separator4',
      label: '',
      separator: true,
      onClick: () => {}
    },
    {
      id: 'reveal-in-explorer',
      label: 'Reveal in Explorer',
      icon: '🗂️',
      disabled: !tab.filePath,
      onClick: () => {
        if (tab.filePath) {
          // This would need platform-specific implementation
          console.log('Reveal in explorer:', tab.filePath)
        }
        onClose()
      }
    },
    {
      id: 'open-in-new-window',
      label: 'Open in New Window',
      icon: '🪟',
      onClick: () => {
        // This would open the file in a new window
        console.log('Open in new window:', tab.title)
        onClose()
      }
    }
  ]

  const handleKeyDown = useCallback((e: React.KeyboardEvent, action: TabContextMenuAction) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      if (!action.disabled) {
        action.onClick()
      }
    }
  }, [])

  return (
    <div
      ref={menuRef}
      className="tab-context-menu"
      style={menuStyle}
      role="menu"
      aria-label="Tab context menu"
    >
      <div className="context-menu-header">
        <div className="tab-info">
          <div className="tab-icon">
            {tab.language === 'typescript' ? '📘' : 
             tab.language === 'javascript' ? '📙' :
             tab.language === 'python' ? '🐍' :
             tab.language === 'go' ? '🔷' :
             tab.language === 'rust' ? '🦀' : '📄'}
          </div>
          <div className="tab-details">
            <div className="tab-name" title={tab.title}>{tab.title}</div>
            {tab.filePath && (
              <div className="tab-path" title={tab.filePath}>
                {tab.filePath.length > 30 
                  ? '...' + tab.filePath.substring(tab.filePath.length - 27)
                  : tab.filePath
                }
              </div>
            )}
          </div>
        </div>
        {hasUnsavedChanges && (
          <div className="unsaved-indicator" title="Unsaved changes">●</div>
        )}
      </div>

      <div className="context-menu-items">
        {actions.map((action) => {
          if (action.separator) {
            return <div key={action.id} className="context-menu-separator" />
          }

          return (
            <div
              key={action.id}
              className={`context-menu-item ${action.disabled ? 'disabled' : ''}`}
              role="menuitem"
              tabIndex={action.disabled ? -1 : 0}
              onClick={action.disabled ? undefined : action.onClick}
              onKeyDown={(e) => handleKeyDown(e, action)}
              aria-disabled={action.disabled}
            >
              <div className="menu-item-content">
                {action.icon && (
                  <span className="menu-item-icon" aria-hidden="true">
                    {action.icon}
                  </span>
                )}
                <span className="menu-item-label">{action.label}</span>
                {action.shortcut && (
                  <span className="menu-item-shortcut" aria-hidden="true">
                    {action.shortcut}
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="context-menu-footer">
        <div className="file-stats">
          <span>Modified: {tab.lastModified.toLocaleString()}</span>
          <span>Language: {tab.language}</span>
        </div>
      </div>
    </div>
  )
}

export default TabContextMenu