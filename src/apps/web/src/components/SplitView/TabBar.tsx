import React, { useCallback, useState, useRef, useEffect } from 'react'
import { FileTab } from './types'

interface TabBarProps {
  tabs: FileTab[]
  activeTabId: string | null
  onTabSelect: (tabId: string) => void
  onTabClose: (tabId: string) => void
  onNewTab: () => void
  onDragStart: (event: React.DragEvent, tabId: string) => void
  onDragEnd: () => void
  onPaneClose?: () => void
  showCloseButton?: boolean
}

export const TabBar: React.FC<TabBarProps> = ({
  tabs,
  activeTabId,
  onTabSelect,
  onTabClose,
  onNewTab,
  onDragStart,
  onDragEnd,
  onPaneClose,
  showCloseButton = false
}) => {
  const [draggedTabId, setDraggedTabId] = useState<string | null>(null)
  const [dragOverTabId, setDragOverTabId] = useState<string | null>(null)
  const [contextMenuTab, setContextMenuTab] = useState<string | null>(null)
  const [contextMenuPosition, setContextMenuPosition] = useState<{ x: number; y: number } | null>(null)
  const tabBarRef = useRef<HTMLDivElement>(null)

  // Handle tab drag start
  const handleTabDragStart = useCallback((event: React.DragEvent, tabId: string) => {
    setDraggedTabId(tabId)
    onDragStart(event, tabId)
    event.dataTransfer.effectAllowed = 'move'
  }, [onDragStart])

  // Handle tab drag end
  const handleTabDragEnd = useCallback(() => {
    setDraggedTabId(null)
    setDragOverTabId(null)
    onDragEnd()
  }, [onDragEnd])

  // Handle tab drag over
  const handleTabDragOver = useCallback((event: React.DragEvent, tabId: string) => {
    if (draggedTabId && draggedTabId !== tabId) {
      event.preventDefault()
      setDragOverTabId(tabId)
    }
  }, [draggedTabId])

  // Handle tab drop
  const handleTabDrop = useCallback((event: React.DragEvent, targetTabId: string) => {
    event.preventDefault()
    setDragOverTabId(null)
    
    if (draggedTabId && draggedTabId !== targetTabId) {
      // Reorder tabs logic would go here
      // For now, just prevent default behavior
    }
  }, [draggedTabId])

  // Handle context menu
  const handleTabContextMenu = useCallback((event: React.MouseEvent, tabId: string) => {
    event.preventDefault()
    setContextMenuTab(tabId)
    setContextMenuPosition({ x: event.clientX, y: event.clientY })
  }, [])

  // Close context menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setContextMenuTab(null)
      setContextMenuPosition(null)
    }

    if (contextMenuTab) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [contextMenuTab])

  // Handle middle click to close tab
  const handleTabMouseDown = useCallback((event: React.MouseEvent, tabId: string) => {
    if (event.button === 1) { // Middle mouse button
      event.preventDefault()
      const tab = tabs.find(t => t.id === tabId)
      if (tab && tab.canClose) {
        onTabClose(tabId)
      }
    }
  }, [tabs, onTabClose])

  // Get file icon based on language/extension
  const getFileIcon = useCallback((tab: FileTab) => {
    const extension = tab.filePath.split('.').pop()?.toLowerCase()
    const language = tab.language.toLowerCase()

    // Map file types to icons (using emoji for simplicity)
    const iconMap: Record<string, string> = {
      // Languages
      javascript: '🟨',
      typescript: '🔷',
      python: '🐍',
      java: '☕',
      go: '🐹',
      rust: '🦀',
      cpp: '⚙️',
      c: '⚙️',
      csharp: '🔷',
      php: '🐘',
      ruby: '💎',
      swift: '🐦',
      kotlin: '🟪',
      scala: '🔺',
      
      // Extensions
      js: '🟨',
      ts: '🔷',
      tsx: '⚛️',
      jsx: '⚛️',
      py: '🐍',
      java: '☕',
      go: '🐹',
      rs: '🦀',
      cpp: '⚙️',
      c: '⚙️',
      cs: '🔷',
      php: '🐘',
      rb: '💎',
      swift: '🐦',
      kt: '🟪',
      scala: '🔺',
      html: '🌐',
      css: '🎨',
      scss: '🎨',
      less: '🎨',
      json: '📋',
      xml: '📄',
      md: '📝',
      txt: '📄',
      yaml: '📋',
      yml: '📋',
      sql: '🗃️',
      sh: '⚫',
      bash: '⚫',
      dockerfile: '🐳',
      makefile: '🔨'
    }

    return iconMap[language] || iconMap[extension || ''] || '📄'
  }, [])

  // Get tab title with dirty indicator
  const getTabTitle = useCallback((tab: FileTab) => {
    const baseName = tab.filePath ? tab.filePath.split('/').pop() || tab.title : tab.title
    return tab.isDirty ? `● ${baseName}` : baseName
  }, [])

  return (
    <div className="tab-bar" ref={tabBarRef}>
      <div className="tab-list">
        {tabs.map(tab => (
          <div
            key={tab.id}
            className={`tab ${tab.id === activeTabId ? 'active' : ''} ${draggedTabId === tab.id ? 'dragging' : ''} ${dragOverTabId === tab.id ? 'drag-over' : ''}`}
            onClick={() => onTabSelect(tab.id)}
            onMouseDown={(e) => handleTabMouseDown(e, tab.id)}
            onContextMenu={(e) => handleTabContextMenu(e, tab.id)}
            onDragStart={(e) => handleTabDragStart(e, tab.id)}
            onDragEnd={handleTabDragEnd}
            onDragOver={(e) => handleTabDragOver(e, tab.id)}
            onDrop={(e) => handleTabDrop(e, tab.id)}
            draggable
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '6px 12px',
              backgroundColor: tab.id === activeTabId ? '#007acc' : '#f0f0f0',
              color: tab.id === activeTabId ? 'white' : '#333',
              borderRadius: '4px 4px 0 0',
              margin: '0 1px',
              cursor: 'pointer',
              userSelect: 'none',
              minWidth: '120px',
              maxWidth: '200px',
              border: '1px solid',
              borderColor: tab.id === activeTabId ? '#007acc' : '#ddd',
              borderBottom: 'none',
              position: 'relative',
              opacity: draggedTabId === tab.id ? 0.5 : 1,
              transform: dragOverTabId === tab.id ? 'translateX(5px)' : 'none',
              transition: 'all 0.2s ease'
            }}
          >
            <span className="tab-icon" style={{ marginRight: '6px', fontSize: '14px' }}>
              {getFileIcon(tab)}
            </span>
            
            <span 
              className="tab-title" 
              style={{ 
                flex: 1, 
                overflow: 'hidden', 
                textOverflow: 'ellipsis', 
                whiteSpace: 'nowrap',
                fontSize: '13px'
              }}
              title={tab.filePath || tab.title}
            >
              {getTabTitle(tab)}
            </span>
            
            {tab.canClose && (
              <button
                className="tab-close"
                onClick={(e) => {
                  e.stopPropagation()
                  onTabClose(tab.id)
                }}
                style={{
                  marginLeft: '6px',
                  background: 'none',
                  border: 'none',
                  color: 'inherit',
                  cursor: 'pointer',
                  padding: '2px',
                  borderRadius: '2px',
                  fontSize: '12px',
                  lineHeight: 1,
                  opacity: 0.7,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                onMouseEnter={(e) => {
                  (e.target as HTMLElement).style.opacity = '1'
                  (e.target as HTMLElement).style.backgroundColor = 'rgba(255, 255, 255, 0.2)'
                }}
                onMouseLeave={(e) => {
                  (e.target as HTMLElement).style.opacity = '0.7'
                  (e.target as HTMLElement).style.backgroundColor = 'transparent'
                }}
                title="Close tab (Ctrl+W)"
              >
                ×
              </button>
            )}

            {tab.isDirty && (
              <div
                className="dirty-indicator"
                style={{
                  position: 'absolute',
                  top: '4px',
                  left: '4px',
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  backgroundColor: tab.id === activeTabId ? 'white' : '#007acc'
                }}
                title="Unsaved changes"
              />
            )}
          </div>
        ))}
        
        {/* New Tab Button */}
        <button
          className="new-tab-button"
          onClick={onNewTab}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '6px 8px',
            backgroundColor: 'transparent',
            border: '1px solid #ddd',
            borderRadius: '4px',
            margin: '0 2px',
            cursor: 'pointer',
            fontSize: '16px',
            color: '#666',
            minWidth: '24px',
            height: '24px'
          }}
          onMouseEnter={(e) => {
            (e.target as HTMLElement).style.backgroundColor = '#f0f0f0'
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLElement).style.backgroundColor = 'transparent'
          }}
          title="New tab (Ctrl+T)"
        >
          +
        </button>
      </div>

      {/* Pane Controls */}
      <div className="pane-controls">
        {showCloseButton && onPaneClose && (
          <button
            className="close-pane-button"
            onClick={onPaneClose}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '4px',
              backgroundColor: 'transparent',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
              color: '#666',
              marginLeft: '8px'
            }}
            onMouseEnter={(e) => {
              (e.target as HTMLElement).style.backgroundColor = '#ff4444'
              ;(e.target as HTMLElement).style.color = 'white'
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLElement).style.backgroundColor = 'transparent'
              ;(e.target as HTMLElement).style.color = '#666'
            }}
            title="Close pane (Ctrl+Shift+W)"
          >
            ×
          </button>
        )}
      </div>

      {/* Context Menu */}
      {contextMenuTab && contextMenuPosition && (
        <div
          className="tab-context-menu"
          style={{
            position: 'fixed',
            top: contextMenuPosition.y,
            left: contextMenuPosition.x,
            backgroundColor: 'white',
            border: '1px solid #ddd',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
            zIndex: 1000,
            minWidth: '150px'
          }}
        >
          <div className="context-menu-item" onClick={() => onTabClose(contextMenuTab)}>
            Close Tab
          </div>
          <div className="context-menu-item" onClick={() => {
            tabs.forEach(tab => {
              if (tab.id !== contextMenuTab && tab.canClose) {
                onTabClose(tab.id)
              }
            })
          }}>
            Close Others
          </div>
          <div className="context-menu-item" onClick={() => {
            const tabIndex = tabs.findIndex(t => t.id === contextMenuTab)
            tabs.slice(tabIndex + 1).forEach(tab => {
              if (tab.canClose) {
                onTabClose(tab.id)
              }
            })
          }}>
            Close to the Right
          </div>
          <div className="context-menu-separator" />
          <div className="context-menu-item">
            Copy Path
          </div>
          <div className="context-menu-item">
            Reveal in Explorer
          </div>
        </div>
      )}

      <style jsx>{`
        .tab-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background-color: #f8f8f8;
          border-bottom: 1px solid #ddd;
          padding: 4px;
          min-height: 36px;
        }

        .tab-list {
          display: flex;
          align-items: center;
          flex: 1;
          overflow-x: auto;
          overflow-y: hidden;
          scrollbar-width: none;
          -ms-overflow-style: none;
        }

        .tab-list::-webkit-scrollbar {
          display: none;
        }

        .pane-controls {
          display: flex;
          align-items: center;
          margin-left: 8px;
        }

        .context-menu-item {
          padding: 8px 12px;
          cursor: pointer;
          font-size: 13px;
        }

        .context-menu-item:hover {
          background-color: #f0f0f0;
        }

        .context-menu-separator {
          height: 1px;
          background-color: #ddd;
          margin: 4px 0;
        }

        .tab.dragging {
          opacity: 0.5;
          transform: rotate(5deg);
        }

        .tab.drag-over {
          transform: translateX(5px);
          box-shadow: 2px 0 4px rgba(0, 122, 204, 0.3);
        }
      `}</style>
    </div>
  )
}

export default TabBar