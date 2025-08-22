import React, { useState, useCallback, useRef, useEffect } from 'react'
import { SplitPane } from './SplitPane'
import { SplitResizer } from './SplitResizer'
import { SplitViewToolbar } from './SplitViewToolbar'
import { SplitViewKeyboardHandler } from './SplitViewKeyboardHandler'
import { SplitViewSettings } from './SplitViewSettings'
import { SplitViewProvider, useSplitView } from './SplitViewContext'
import { SplitLayout, SplitOrientation, PaneConfig } from './types'

interface SplitViewContainerProps {
  children?: React.ReactNode
  defaultLayout?: SplitLayout
  defaultOrientation?: SplitOrientation
  minPaneSize?: number
  maxPaneSize?: number
  className?: string
  onLayoutChange?: (layout: SplitLayout) => void
  onPaneResize?: (paneId: string, size: number) => void
}

const SplitViewContainerInner: React.FC<SplitViewContainerProps> = ({
  children,
  defaultLayout = 'two-pane',
  defaultOrientation = 'horizontal',
  minPaneSize = 200,
  maxPaneSize = Infinity,
  className = '',
  onLayoutChange,
  onPaneResize
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const {
    layout,
    orientation,
    panes,
    setLayout,
    setOrientation,
    updatePaneSize,
    resizePane,
    splitPane,
    closePanePanel,
    swapPanes
  } = useSplitView()

  const [isDragging, setIsDragging] = useState(false)
  const [dragTarget, setDragTarget] = useState<string | null>(null)
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 })
  const [showSettings, setShowSettings] = useState(false)

  // Update container size on resize
  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        setContainerSize({ width: rect.width, height: rect.height })
      }
    }

    updateSize()
    window.addEventListener('resize', updateSize)
    return () => window.removeEventListener('resize', updateSize)
  }, [])

  // Handle layout changes
  useEffect(() => {
    if (onLayoutChange) {
      onLayoutChange(layout)
    }
  }, [layout, onLayoutChange])

  // Calculate pane sizes based on orientation and layout
  const calculatePaneSizes = useCallback(() => {
    const totalSize = orientation === 'horizontal' ? containerSize.width : containerSize.height
    const activePanes = Object.values(panes).filter(pane => pane.visible)
    const paneCount = activePanes.length

    if (paneCount === 0) return {}

    const sizes: Record<string, number> = {}
    let remainingSize = totalSize

    // Account for resizers (assuming 4px each)
    const resizerSize = 4
    const totalResizerSize = Math.max(0, (paneCount - 1) * resizerSize)
    remainingSize -= totalResizerSize

    activePanes.forEach((pane, index) => {
      if (pane.size && pane.size > 0) {
        // Use explicit size if set
        sizes[pane.id] = Math.min(Math.max(pane.size, minPaneSize), maxPaneSize)
      } else {
        // Distribute remaining space equally
        const defaultSize = remainingSize / paneCount
        sizes[pane.id] = Math.min(Math.max(defaultSize, minPaneSize), maxPaneSize)
      }
    })

    return sizes
  }, [panes, orientation, containerSize, minPaneSize, maxPaneSize])

  // Handle pane resize
  const handlePaneResize = useCallback((paneId: string, newSize: number, direction: 'left' | 'right' | 'up' | 'down') => {
    const clampedSize = Math.min(Math.max(newSize, minPaneSize), maxPaneSize)
    updatePaneSize(paneId, clampedSize)
    
    if (onPaneResize) {
      onPaneResize(paneId, clampedSize)
    }
  }, [updatePaneSize, onPaneResize, minPaneSize, maxPaneSize])

  // Handle drag and drop for tab management
  const handleDragStart = useCallback((event: React.DragEvent, paneId: string, tabId: string) => {
    setIsDragging(true)
    event.dataTransfer.setData('text/plain', JSON.stringify({ paneId, tabId }))
    event.dataTransfer.effectAllowed = 'move'
  }, [])

  const handleDragOver = useCallback((event: React.DragEvent, targetPaneId: string) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
    setDragTarget(targetPaneId)
  }, [])

  const handleDrop = useCallback((event: React.DragEvent, targetPaneId: string) => {
    event.preventDefault()
    setIsDragging(false)
    setDragTarget(null)

    try {
      const data = JSON.parse(event.dataTransfer.getData('text/plain'))
      const { paneId: sourcePaneId, tabId } = data

      if (sourcePaneId !== targetPaneId) {
        // Move tab between panes
        swapPanes(sourcePaneId, targetPaneId, tabId)
      }
    } catch (error) {
      console.error('Error handling tab drop:', error)
    }
  }, [swapPanes])

  const handleDragEnd = useCallback(() => {
    setIsDragging(false)
    setDragTarget(null)
  }, [])

  // Get visible panes for rendering
  const visiblePanes = Object.values(panes).filter(pane => pane.visible)
  const paneSizes = calculatePaneSizes()

  // Handle layout change
  const handleLayoutChange = useCallback((newLayout: SplitLayout) => {
    setLayout(newLayout)
  }, [setLayout])

  // Handle orientation change
  const handleOrientationChange = useCallback((newOrientation: SplitOrientation) => {
    setOrientation(newOrientation)
  }, [setOrientation])

  // Handle split actions
  const handleSplitHorizontal = useCallback(() => {
    splitPane('horizontal')
  }, [splitPane])

  const handleSplitVertical = useCallback(() => {
    splitPane('vertical')
  }, [splitPane])

  const handleSplitGrid = useCallback(() => {
    setLayout('four-pane-grid')
  }, [setLayout])

  return (
    <SplitViewKeyboardHandler enabled={true}>
      <div 
        ref={containerRef}
        className={`split-view-container ${className} ${isDragging ? 'dragging' : ''}`}
        style={{
          display: 'flex',
          flexDirection: orientation === 'horizontal' ? 'row' : 'column',
          height: '100%',
          width: '100%',
          overflow: 'hidden'
        }}
      >
        <SplitViewToolbar
          layout={layout}
          orientation={orientation}
          onLayoutChange={handleLayoutChange}
          onOrientationChange={handleOrientationChange}
          onSplitHorizontal={handleSplitHorizontal}
          onSplitVertical={handleSplitVertical}
          onSplitGrid={handleSplitGrid}
          onShowSettings={() => setShowSettings(true)}
        />

        <div className="split-view-content" style={{ flex: 1, display: 'flex', flexDirection: orientation === 'horizontal' ? 'row' : 'column' }}>
          {visiblePanes.map((pane, index) => (
            <React.Fragment key={pane.id}>
              <SplitPane
                pane={pane}
                size={paneSizes[pane.id] || 300}
                orientation={orientation}
                isDragTarget={dragTarget === pane.id}
                onResize={(newSize, direction) => handlePaneResize(pane.id, newSize, direction)}
                onDragStart={(event, tabId) => handleDragStart(event, pane.id, tabId)}
                onDragOver={(event) => handleDragOver(event, pane.id)}
                onDrop={(event) => handleDrop(event, pane.id)}
                onDragEnd={handleDragEnd}
                onClose={() => closePanePanel(pane.id)}
              />
              
              {index < visiblePanes.length - 1 && (
                <SplitResizer
                  orientation={orientation}
                  onResize={(delta) => {
                    const currentPane = visiblePanes[index]
                    const nextPane = visiblePanes[index + 1]
                    const currentSize = paneSizes[currentPane.id] || 300
                    const nextSize = paneSizes[nextPane.id] || 300
                    
                    const newCurrentSize = currentSize + delta
                    const newNextSize = nextSize - delta
                    
                    if (newCurrentSize >= minPaneSize && newNextSize >= minPaneSize) {
                      handlePaneResize(currentPane.id, newCurrentSize, orientation === 'horizontal' ? 'right' : 'down')
                      handlePaneResize(nextPane.id, newNextSize, orientation === 'horizontal' ? 'left' : 'up')
                    }
                  }}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Settings Panel */}
        <SplitViewSettings
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
        />

        {children}
      </div>
    </SplitViewKeyboardHandler>
  )
}

export const SplitViewContainer: React.FC<SplitViewContainerProps> = (props) => {
  return (
    <SplitViewProvider>
      <SplitViewContainerInner {...props} />
    </SplitViewProvider>
  )
}

export default SplitViewContainer