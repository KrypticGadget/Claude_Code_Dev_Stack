import React, { useCallback, useState, useRef, useEffect } from 'react'
import { SplitOrientation } from './types'

interface SplitResizerProps {
  orientation: SplitOrientation
  onResize: (delta: number) => void
  onResizeStart?: () => void
  onResizeEnd?: () => void
  minSize?: number
  maxSize?: number
  snapZones?: number[]
  snapDistance?: number
}

export const SplitResizer: React.FC<SplitResizerProps> = ({
  orientation,
  onResize,
  onResizeStart,
  onResizeEnd,
  minSize = 100,
  maxSize = Infinity,
  snapZones = [],
  snapDistance = 10
}) => {
  const [isResizing, setIsResizing] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [startPosition, setStartPosition] = useState(0)
  const [currentDelta, setCurrentDelta] = useState(0)
  const resizerRef = useRef<HTMLDivElement>(null)

  // Handle mouse down - start resizing
  const handleMouseDown = useCallback((event: React.MouseEvent) => {
    if (event.button !== 0) return // Only handle left mouse button

    event.preventDefault()
    setIsResizing(true)
    setIsDragging(true)
    setStartPosition(orientation === 'horizontal' ? event.clientX : event.clientY)
    setCurrentDelta(0)

    if (onResizeStart) {
      onResizeStart()
    }

    // Add global mouse move and mouse up listeners
    const handleMouseMove = (e: MouseEvent) => {
      const currentPosition = orientation === 'horizontal' ? e.clientX : e.clientY
      let delta = currentPosition - startPosition

      // Apply snapping
      if (snapZones.length > 0) {
        for (const snapZone of snapZones) {
          if (Math.abs(delta - snapZone) <= snapDistance) {
            delta = snapZone
            break
          }
        }
      }

      // Apply constraints
      if (delta < -minSize) delta = -minSize
      if (delta > maxSize) delta = maxSize

      setCurrentDelta(delta)
      onResize(delta)
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      setIsDragging(false)
      setCurrentDelta(0)

      if (onResizeEnd) {
        onResizeEnd()
      }

      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }, [orientation, startPosition, onResize, onResizeStart, onResizeEnd, minSize, maxSize, snapZones, snapDistance])

  // Handle double-click to reset
  const handleDoubleClick = useCallback(() => {
    onResize(0) // Reset to original size
  }, [onResize])

  // Handle touch events for mobile
  const handleTouchStart = useCallback((event: React.TouchEvent) => {
    if (event.touches.length !== 1) return

    const touch = event.touches[0]
    setIsResizing(true)
    setIsDragging(true)
    setStartPosition(orientation === 'horizontal' ? touch.clientX : touch.clientY)
    setCurrentDelta(0)

    if (onResizeStart) {
      onResizeStart()
    }

    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches.length !== 1) return
      
      e.preventDefault()
      const touch = e.touches[0]
      const currentPosition = orientation === 'horizontal' ? touch.clientX : touch.clientY
      let delta = currentPosition - startPosition

      // Apply snapping
      if (snapZones.length > 0) {
        for (const snapZone of snapZones) {
          if (Math.abs(delta - snapZone) <= snapDistance) {
            delta = snapZone
            break
          }
        }
      }

      // Apply constraints
      if (delta < -minSize) delta = -minSize
      if (delta > maxSize) delta = maxSize

      setCurrentDelta(delta)
      onResize(delta)
    }

    const handleTouchEnd = () => {
      setIsResizing(false)
      setIsDragging(false)
      setCurrentDelta(0)

      if (onResizeEnd) {
        onResizeEnd()
      }

      document.removeEventListener('touchmove', handleTouchMove)
      document.removeEventListener('touchend', handleTouchEnd)
    }

    document.addEventListener('touchmove', handleTouchMove, { passive: false })
    document.addEventListener('touchend', handleTouchEnd)
  }, [orientation, startPosition, onResize, onResizeStart, onResizeEnd, minSize, maxSize, snapZones, snapDistance])

  // Keyboard navigation support
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    const step = 10
    let delta = 0

    switch (event.key) {
      case 'ArrowLeft':
        if (orientation === 'horizontal') {
          delta = -step
        }
        break
      case 'ArrowRight':
        if (orientation === 'horizontal') {
          delta = step
        }
        break
      case 'ArrowUp':
        if (orientation === 'vertical') {
          delta = -step
        }
        break
      case 'ArrowDown':
        if (orientation === 'vertical') {
          delta = step
        }
        break
      case 'Home':
        delta = -minSize
        break
      case 'End':
        delta = maxSize
        break
      case 'Enter':
      case ' ':
        onResize(0) // Reset
        break
      default:
        return
    }

    if (delta !== 0) {
      event.preventDefault()
      onResize(delta)
    }
  }, [orientation, onResize, minSize, maxSize])

  // Style for the resizer
  const resizerStyle: React.CSSProperties = {
    position: 'relative',
    backgroundColor: isResizing ? '#007acc' : 'transparent',
    cursor: orientation === 'horizontal' ? 'col-resize' : 'row-resize',
    userSelect: 'none',
    zIndex: 10,
    transition: isResizing ? 'none' : 'background-color 0.2s ease',
    ...(orientation === 'horizontal' ? {
      width: '4px',
      height: '100%',
      borderLeft: '1px solid #e0e0e0',
      borderRight: '1px solid #e0e0e0'
    } : {
      height: '4px',
      width: '100%',
      borderTop: '1px solid #e0e0e0',
      borderBottom: '1px solid #e0e0e0'
    })
  }

  // Handle style on hover
  const [isHovered, setIsHovered] = useState(false)

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true)
  }, [])

  const handleMouseLeave = useCallback(() => {
    if (!isResizing) {
      setIsHovered(false)
    }
  }, [isResizing])

  // Apply hover styles
  if (isHovered || isResizing) {
    resizerStyle.backgroundColor = '#007acc'
    if (orientation === 'horizontal') {
      resizerStyle.borderLeft = '1px solid #007acc'
      resizerStyle.borderRight = '1px solid #007acc'
    } else {
      resizerStyle.borderTop = '1px solid #007acc'
      resizerStyle.borderBottom = '1px solid #007acc'
    }
  }

  // Snap indicator
  const showSnapIndicator = isResizing && snapZones.length > 0

  return (
    <div
      ref={resizerRef}
      className={`split-resizer ${orientation} ${isResizing ? 'resizing' : ''} ${isDragging ? 'dragging' : ''}`}
      style={resizerStyle}
      onMouseDown={handleMouseDown}
      onDoubleClick={handleDoubleClick}
      onTouchStart={handleTouchStart}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="separator"
      aria-orientation={orientation}
      aria-label={`Resize ${orientation} split`}
      title={`Drag to resize, double-click to reset, use arrow keys for fine adjustment`}
    >
      {/* Resizer handle - visible area for interaction */}
      <div
        className="resizer-handle"
        style={{
          position: 'absolute',
          backgroundColor: 'transparent',
          ...(orientation === 'horizontal' ? {
            width: '8px',
            height: '100%',
            left: '-2px',
            cursor: 'col-resize'
          } : {
            height: '8px',
            width: '100%',
            top: '-2px',
            cursor: 'row-resize'
          })
        }}
      />

      {/* Visual grip indicator */}
      <div
        className="resizer-grip"
        style={{
          position: 'absolute',
          backgroundColor: isHovered || isResizing ? '#007acc' : '#ccc',
          borderRadius: '2px',
          transition: 'background-color 0.2s ease',
          ...(orientation === 'horizontal' ? {
            width: '2px',
            height: '20px',
            left: '1px',
            top: '50%',
            transform: 'translateY(-50%)'
          } : {
            height: '2px',
            width: '20px',
            top: '1px',
            left: '50%',
            transform: 'translateX(-50%)'
          })
        }}
      />

      {/* Snap zones indicator */}
      {showSnapIndicator && snapZones.map((zone, index) => (
        <div
          key={index}
          className="snap-indicator"
          style={{
            position: 'absolute',
            backgroundColor: '#007acc',
            opacity: 0.3,
            pointerEvents: 'none',
            ...(orientation === 'horizontal' ? {
              width: '1px',
              height: '100%',
              left: `${zone}px`,
              top: 0
            } : {
              height: '1px',
              width: '100%',
              top: `${zone}px`,
              left: 0
            })
          }}
        />
      ))}

      {/* Current position indicator during resize */}
      {isResizing && (
        <div
          className="resize-indicator"
          style={{
            position: 'fixed',
            backgroundColor: '#007acc',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            pointerEvents: 'none',
            zIndex: 1000,
            ...(orientation === 'horizontal' ? {
              left: `${startPosition + currentDelta}px`,
              top: '50%',
              transform: 'translate(-50%, -50%)'
            } : {
              top: `${startPosition + currentDelta}px`,
              left: '50%',
              transform: 'translate(-50%, -50%)'
            })
          }}
        >
          {currentDelta > 0 ? '+' : ''}{currentDelta}px
        </div>
      )}

      <style jsx>{`
        .split-resizer {
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
        }

        .split-resizer:focus {
          outline: 2px solid #007acc;
          outline-offset: 1px;
        }

        .split-resizer.resizing {
          user-select: none;
          pointer-events: none;
        }

        .split-resizer.horizontal {
          min-width: 4px;
          max-width: 4px;
        }

        .split-resizer.vertical {
          min-height: 4px;
          max-height: 4px;
        }

        @media (max-width: 768px) {
          .split-resizer.horizontal {
            min-width: 8px;
            max-width: 8px;
          }

          .split-resizer.vertical {
            min-height: 8px;
            max-height: 8px;
          }

          .resizer-handle {
            width: 12px !important;
            left: -4px !important;
          }

          .resizer-handle {
            height: 12px !important;
            top: -4px !important;
          }
        }
      `}</style>
    </div>
  )
}

export default SplitResizer