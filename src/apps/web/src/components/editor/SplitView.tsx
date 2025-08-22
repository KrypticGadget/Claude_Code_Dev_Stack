import React, { useState, useRef, useCallback, useEffect } from 'react'
import { SplitPanel, Tab, TabGroup } from '../types/TabTypes'
import { TabBar } from './TabBar'
import { SplitHandle } from './SplitHandle'
import { PanelDropZone } from './PanelDropZone'
import '../styles/split-view.css'

export interface SplitViewProps {
  panels: SplitPanel[]
  tabs: Tab[]
  activeTabId: string | null
  activePanelId: string
  pinnedTabs: Set<string>
  unsavedChanges: Set<string>
  tabGroups: TabGroup[]
  onTabSelect: (tabId: string, panelId?: string) => void
  onTabClose: (tabId: string) => void
  onTabPin: (tabId: string) => void
  onTabContextMenu: (e: React.MouseEvent, tabId: string) => void
  onPanelSelect: (panelId: string) => void
  onTabMove: (tabId: string, targetIndex: number, targetPanelId?: string) => void
  onCreatePanel: (direction: 'horizontal' | 'vertical', tabId?: string) => void
  enableDragAndDrop?: boolean
}

interface PanelLayout {
  id: string
  x: number
  y: number
  width: number
  height: number
  direction?: 'horizontal' | 'vertical'
  children?: string[]
}

export const SplitView: React.FC<SplitViewProps> = ({
  panels,
  tabs,
  activeTabId,
  activePanelId,
  pinnedTabs,
  unsavedChanges,
  tabGroups,
  onTabSelect,
  onTabClose,
  onTabPin,
  onTabContextMenu,
  onPanelSelect,
  onTabMove,
  onCreatePanel,
  enableDragAndDrop = true
}) => {
  const [panelSizes, setPanelSizes] = useState<Map<string, number>>(new Map())
  const [dragState, setDragState] = useState<{
    isDragging: boolean
    panelId: string | null
    direction: 'horizontal' | 'vertical' | null
    startX: number
    startY: number
    startSize: number
  }>({
    isDragging: false,
    panelId: null,
    direction: null,
    startX: 0,
    startY: 0,
    startSize: 0
  })

  const containerRef = useRef<HTMLDivElement>(null)
  const [showDropZones, setShowDropZones] = useState(false)

  // Calculate panel layout
  const panelLayout = React.useMemo((): PanelLayout[] => {
    if (panels.length === 1) {
      return [{
        id: panels[0].id,
        x: 0,
        y: 0,
        width: 100,
        height: 100
      }]
    }

    // For simplicity, arrange panels in a grid
    const cols = Math.ceil(Math.sqrt(panels.length))
    const rows = Math.ceil(panels.length / cols)
    const panelWidth = 100 / cols
    const panelHeight = 100 / rows

    return panels.map((panel, index) => {
      const col = index % cols
      const row = Math.floor(index / cols)

      return {
        id: panel.id,
        x: col * panelWidth,
        y: row * panelHeight,
        width: panelWidth,
        height: panelHeight
      }
    })
  }, [panels])

  // Handle panel resize
  const handleResizeStart = useCallback((
    panelId: string,
    direction: 'horizontal' | 'vertical',
    event: React.MouseEvent
  ) => {
    const size = panelSizes.get(panelId) || 50

    setDragState({
      isDragging: true,
      panelId,
      direction,
      startX: event.clientX,
      startY: event.clientY,
      startSize: size
    })

    event.preventDefault()
  }, [panelSizes])

  const handleResizeMove = useCallback((event: MouseEvent) => {
    if (!dragState.isDragging || !dragState.panelId) return

    const deltaX = event.clientX - dragState.startX
    const deltaY = event.clientY - dragState.startY
    const delta = dragState.direction === 'horizontal' ? deltaX : deltaY

    // Calculate new size as percentage
    const containerSize = dragState.direction === 'horizontal'
      ? containerRef.current?.clientWidth || 800
      : containerRef.current?.clientHeight || 600

    const deltaPercent = (delta / containerSize) * 100
    const newSize = Math.max(10, Math.min(90, dragState.startSize + deltaPercent))

    setPanelSizes(prev => new Map(prev).set(dragState.panelId!, newSize))
  }, [dragState])

  const handleResizeEnd = useCallback(() => {
    setDragState({
      isDragging: false,
      panelId: null,
      direction: null,
      startX: 0,
      startY: 0,
      startSize: 0
    })
  }, [])

  // Setup mouse event listeners for resizing
  useEffect(() => {
    if (dragState.isDragging) {
      document.addEventListener('mousemove', handleResizeMove)
      document.addEventListener('mouseup', handleResizeEnd)

      return () => {
        document.removeEventListener('mousemove', handleResizeMove)
        document.removeEventListener('mouseup', handleResizeEnd)
      }
    }
  }, [dragState.isDragging, handleResizeMove, handleResizeEnd])

  // Handle tab drag over panel
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    if (!enableDragAndDrop) return

    e.preventDefault()
    setShowDropZones(true)
  }, [enableDragAndDrop])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    if (!enableDragAndDrop) return

    // Only hide drop zones if we're leaving the container entirely
    if (!containerRef.current?.contains(e.relatedTarget as Node)) {
      setShowDropZones(false)
    }
  }, [enableDragAndDrop])

  const handleDrop = useCallback((e: React.DragEvent, targetPanelId: string, position?: 'top' | 'bottom' | 'left' | 'right') => {
    if (!enableDragAndDrop) return

    e.preventDefault()
    setShowDropZones(false)

    try {
      const data = JSON.parse(e.dataTransfer.getData('text/plain'))
      const { tabId } = data

      if (position) {
        // Create new panel in specified direction
        const direction = position === 'top' || position === 'bottom' ? 'vertical' : 'horizontal'
        onCreatePanel(direction, tabId)
      } else {
        // Move tab to existing panel
        onTabMove(tabId, 0, targetPanelId)
      }
    } catch (error) {
      console.error('Failed to parse drag data:', error)
    }
  }, [enableDragAndDrop, onTabMove, onCreatePanel])

  // Get tabs for a specific panel
  const getPanelTabs = useCallback((panelId: string) => {
    const panel = panels.find(p => p.id === panelId)
    if (!panel) return []

    return panel.tabs
      .map(tabId => tabs.find(tab => tab.id === tabId))
      .filter((tab): tab is Tab => tab !== undefined)
  }, [panels, tabs])

  return (
    <div
      ref={containerRef}
      className="split-view-container"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
    >
      {panelLayout.map((layout, index) => {
        const panel = panels.find(p => p.id === layout.id)
        if (!panel) return null

        const panelTabs = getPanelTabs(panel.id)
        const isActivePanel = panel.id === activePanelId

        return (
          <div
            key={panel.id}
            className={`split-panel ${isActivePanel ? 'active' : ''}`}
            style={{
              left: `${layout.x}%`,
              top: `${layout.y}%`,
              width: `${layout.width}%`,
              height: `${layout.height}%`
            }}
            onMouseDown={() => onPanelSelect(panel.id)}
          >
            {/* Panel Header */}
            <div className="panel-header">
              <TabBar
                tabs={panelTabs}
                activeTabId={panel.activeTabId}
                pinnedTabs={pinnedTabs}
                unsavedChanges={unsavedChanges}
                tabGroups={tabGroups}
                panelId={panel.id}
                isActive={isActivePanel}
                onTabSelect={(tabId) => onTabSelect(tabId, panel.id)}
                onTabClose={onTabClose}
                onTabPin={onTabPin}
                onTabContextMenu={onTabContextMenu}
                onTabMove={(tabId, targetIndex) => onTabMove(tabId, targetIndex, panel.id)}
                onNewTab={() => {
                  // Create new tab in this panel
                  const newTabId = `tab-${Date.now()}`
                  onTabSelect(newTabId, panel.id)
                }}
              />
            </div>

            {/* Panel Content */}
            <div className="panel-content">
              {panel.activeTabId ? (
                <div className="panel-editor-placeholder">
                  {/* The actual Monaco Editor will be rendered here by the parent component */}
                  <div className="editor-placeholder">
                    <span>Editor content for tab: {panel.activeTabId}</span>
                  </div>
                </div>
              ) : (
                <div className="panel-empty">
                  <div className="empty-state">
                    <h3>No file open</h3>
                    <p>Select a tab or create a new file to start editing</p>
                    <button
                      className="create-file-button"
                      onClick={() => {
                        const newTabId = `tab-${Date.now()}`
                        onTabSelect(newTabId, panel.id)
                      }}
                    >
                      Create New File
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Drop Zones */}
            {showDropZones && enableDragAndDrop && (
              <PanelDropZone
                panelId={panel.id}
                onDrop={handleDrop}
              />
            )}

            {/* Resize Handles */}
            {panels.length > 1 && index < panelLayout.length - 1 && (
              <>
                {/* Right resize handle */}
                {layout.x + layout.width < 100 && (
                  <SplitHandle
                    direction="horizontal"
                    onResizeStart={(e) => handleResizeStart(panel.id, 'horizontal', e)}
                    style={{
                      right: 0,
                      top: 0,
                      height: '100%',
                      transform: 'translateX(50%)'
                    }}
                  />
                )}

                {/* Bottom resize handle */}
                {layout.y + layout.height < 100 && (
                  <SplitHandle
                    direction="vertical"
                    onResizeStart={(e) => handleResizeStart(panel.id, 'vertical', e)}
                    style={{
                      bottom: 0,
                      left: 0,
                      width: '100%',
                      transform: 'translateY(50%)'
                    }}
                  />
                )}
              </>
            )}
          </div>
        )
      })}

      {/* Global Drop Zone for creating new panels */}
      {showDropZones && enableDragAndDrop && panels.length === 1 && (
        <div className="global-drop-zones">
          <div
            className="drop-zone drop-zone-top"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => handleDrop(e, panels[0].id, 'top')}
          >
            <span>Drop here to split horizontally</span>
          </div>
          <div
            className="drop-zone drop-zone-bottom"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => handleDrop(e, panels[0].id, 'bottom')}
          >
            <span>Drop here to split horizontally</span>
          </div>
          <div
            className="drop-zone drop-zone-left"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => handleDrop(e, panels[0].id, 'left')}
          >
            <span>Drop here to split vertically</span>
          </div>
          <div
            className="drop-zone drop-zone-right"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => handleDrop(e, panels[0].id, 'right')}
          >
            <span>Drop here to split vertically</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default SplitView