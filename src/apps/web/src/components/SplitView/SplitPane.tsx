import React, { useRef, useCallback, useState, useEffect } from 'react'
import { PaneConfig, SplitOrientation, FileTab } from './types'
import { TabBar } from './TabBar'
import { MonacoEditor } from '../MonacoEditor'
import { useSplitView } from './SplitViewContext'

interface SplitPaneProps {
  pane: PaneConfig
  size: number
  orientation: SplitOrientation
  isDragTarget: boolean
  onResize: (newSize: number, direction: 'left' | 'right' | 'up' | 'down') => void
  onDragStart: (event: React.DragEvent, tabId: string) => void
  onDragOver: (event: React.DragEvent) => void
  onDrop: (event: React.DragEvent) => void
  onDragEnd: () => void
  onClose: () => void
}

export const SplitPane: React.FC<SplitPaneProps> = ({
  pane,
  size,
  orientation,
  isDragTarget,
  onResize,
  onDragStart,
  onDragOver,
  onDrop,
  onDragEnd,
  onClose
}) => {
  const paneRef = useRef<HTMLDivElement>(null)
  const {
    activePaneId,
    setActivePane,
    setActiveTab,
    removeTab,
    updateTabContent,
    addTab,
    settings,
    synchronizedScrolling,
    compareMode
  } = useSplitView()
  
  const [isResizing, setIsResizing] = useState(false)
  const [startSize, setStartSize] = useState(0)
  const [startPosition, setStartPosition] = useState(0)

  const isActive = activePaneId === pane.id
  const activeTab = pane.tabs.find(tab => tab.id === pane.activeTabId)

  // Handle pane activation
  const handlePaneClick = useCallback(() => {
    setActivePane(pane.id)
  }, [setActivePane, pane.id])

  // Handle tab selection
  const handleTabSelect = useCallback((tabId: string) => {
    setActiveTab(pane.id, tabId)
  }, [setActiveTab, pane.id])

  // Handle tab close
  const handleTabClose = useCallback((tabId: string) => {
    removeTab(pane.id, tabId)
  }, [removeTab, pane.id])

  // Handle new tab
  const handleNewTab = useCallback(() => {
    addTab(pane.id, {
      title: 'Untitled',
      filePath: '',
      language: 'plaintext',
      content: '',
      isDirty: false,
      isActive: true,
      canClose: true
    })
  }, [addTab, pane.id])

  // Handle editor content change
  const handleContentChange = useCallback((content: string) => {
    if (activeTab) {
      updateTabContent(pane.id, activeTab.id, content)
    }
  }, [updateTabContent, pane.id, activeTab])

  // Handle editor save
  const handleSave = useCallback((content: string) => {
    if (activeTab) {
      // In a real implementation, this would save to file system
      console.log(`Saving ${activeTab.filePath}:`, content.substring(0, 100) + '...')
    }
  }, [activeTab])

  // Calculate pane style
  const paneStyle: React.CSSProperties = {
    width: orientation === 'horizontal' ? `${size}px` : '100%',
    height: orientation === 'vertical' ? `${size}px` : '100%',
    minWidth: orientation === 'horizontal' ? `${pane.minSize || 200}px` : undefined,
    minHeight: orientation === 'vertical' ? `${pane.minSize || 200}px` : undefined,
    maxWidth: orientation === 'horizontal' ? `${pane.maxSize || 'none'}px` : undefined,
    maxHeight: orientation === 'vertical' ? `${pane.maxSize || 'none'}px` : undefined,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    backgroundColor: settings.theme === 'dark' ? '#1e1e1e' : '#ffffff',
    border: `1px solid ${isActive ? '#007acc' : '#e0e0e0'}`,
    borderRadius: '4px',
    boxShadow: isActive ? '0 0 0 2px rgba(0, 122, 204, 0.2)' : undefined,
    transition: 'border-color 0.2s ease, box-shadow 0.2s ease'
  }

  // Drag target styling
  if (isDragTarget) {
    paneStyle.backgroundColor = settings.theme === 'dark' ? '#2d2d2d' : '#f0f8ff'
    paneStyle.borderColor = '#007acc'
    paneStyle.borderStyle = 'dashed'
  }

  // Handle drag events
  const handleDragOverPane = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    onDragOver(event)
  }, [onDragOver])

  const handleDropOnPane = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    onDrop(event)
  }, [onDrop])

  // Focus management
  useEffect(() => {
    if (isActive && paneRef.current) {
      paneRef.current.focus()
    }
  }, [isActive])

  // Keyboard shortcuts
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (!isActive) return

    const { ctrlKey, shiftKey, key } = event

    if (ctrlKey && !shiftKey) {
      switch (key) {
        case 't':
          event.preventDefault()
          handleNewTab()
          break
        case 'w':
          event.preventDefault()
          if (activeTab && activeTab.canClose) {
            handleTabClose(activeTab.id)
          }
          break
        case 's':
          event.preventDefault()
          if (activeTab) {
            handleSave(activeTab.content)
          }
          break
        case 'Tab':
          event.preventDefault()
          // Cycle through tabs
          const currentIndex = pane.tabs.findIndex(tab => tab.id === pane.activeTabId)
          const nextIndex = (currentIndex + 1) % pane.tabs.length
          if (pane.tabs[nextIndex]) {
            handleTabSelect(pane.tabs[nextIndex].id)
          }
          break
      }
    }

    if (ctrlKey && shiftKey) {
      switch (key) {
        case 'Tab':
          event.preventDefault()
          // Cycle through tabs backwards
          const currentIndex = pane.tabs.findIndex(tab => tab.id === pane.activeTabId)
          const prevIndex = currentIndex === 0 ? pane.tabs.length - 1 : currentIndex - 1
          if (pane.tabs[prevIndex]) {
            handleTabSelect(pane.tabs[prevIndex].id)
          }
          break
      }
    }
  }, [isActive, activeTab, pane.tabs, pane.activeTabId, handleNewTab, handleTabClose, handleSave, handleTabSelect])

  return (
    <div
      ref={paneRef}
      className={`split-pane ${isActive ? 'active' : ''} ${isDragTarget ? 'drag-target' : ''}`}
      style={paneStyle}
      onClick={handlePaneClick}
      onKeyDown={handleKeyDown}
      onDragOver={handleDragOverPane}
      onDrop={handleDropOnPane}
      tabIndex={0}
    >
      {/* Tab Bar */}
      <TabBar
        tabs={pane.tabs}
        activeTabId={pane.activeTabId}
        onTabSelect={handleTabSelect}
        onTabClose={handleTabClose}
        onNewTab={handleNewTab}
        onDragStart={onDragStart}
        onDragEnd={onDragEnd}
        onPaneClose={pane.tabs.length === 0 ? onClose : undefined}
        showCloseButton={Object.keys(pane.tabs).length > 1 || pane.tabs.length === 0}
      />

      {/* Editor Content */}
      <div className="pane-content" style={{ flex: 1, overflow: 'hidden' }}>
        {activeTab ? (
          <MonacoEditor
            language={activeTab.language}
            value={activeTab.content}
            onChange={handleContentChange}
            onSave={handleSave}
            theme={settings.theme}
            height="100%"
            width="100%"
            filePath={activeTab.filePath}
            options={{
              fontSize: settings.fontSize,
              fontFamily: settings.fontFamily,
              tabSize: settings.tabSize,
              insertSpaces: settings.insertSpaces,
              wordWrap: settings.wordWrap ? 'on' : 'off',
              minimap: { enabled: settings.showMinimap },
              scrollBeyondLastLine: false,
              automaticLayout: true,
              readOnly: false
            }}
          />
        ) : (
          <div className="empty-pane">
            <div className="empty-pane-content">
              <h3>No files open</h3>
              <p>Create a new file or open an existing one to start editing.</p>
              <button 
                className="new-file-button"
                onClick={handleNewTab}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#007acc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                New File
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Compare Mode Overlay */}
      {compareMode && pane.tabs.length > 1 && (
        <div className="compare-mode-overlay">
          <div className="compare-mode-indicator">
            Compare Mode
          </div>
        </div>
      )}

      {/* Synchronized Scrolling Indicator */}
      {synchronizedScrolling && (
        <div className="sync-indicator">
          <span title="Synchronized scrolling enabled">⚡</span>
        </div>
      )}
    </div>
  )
}

export default SplitPane