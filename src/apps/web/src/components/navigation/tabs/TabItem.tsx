import React, { useState, useRef, useCallback, useMemo } from 'react'
import { Tab } from '../types/TabTypes'
import { TabPreview } from './TabPreview'
import { getLanguageIcon, getFileIcon } from '../utils/iconUtils'
import '../styles/tab-item.css'

export interface TabItemProps {
  tab: Tab
  isActive?: boolean
  isPinned?: boolean
  hasUnsavedChanges?: boolean
  groupColor?: string
  enablePreview?: boolean
  isHovered?: boolean
  onSelect: () => void
  onClose: () => void
  onPin: () => void
  onContextMenu: (e: React.MouseEvent) => void
  onMouseEnter?: () => void
  onMouseLeave?: () => void
  onMouseUp?: (e: React.MouseEvent) => void
  onDragStart?: (e: React.DragEvent) => void
}

export const TabItem: React.FC<TabItemProps> = ({
  tab,
  isActive = false,
  isPinned = false,
  hasUnsavedChanges = false,
  groupColor,
  enablePreview = true,
  isHovered = false,
  onSelect,
  onClose,
  onPin,
  onContextMenu,
  onMouseEnter,
  onMouseLeave,
  onMouseUp,
  onDragStart
}) => {
  const [showPreview, setShowPreview] = useState(false)
  const [previewPosition, setPreviewPosition] = useState({ x: 0, y: 0 })
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const tabRef = useRef<HTMLDivElement>(null)

  // Get appropriate icon for the file
  const icon = useMemo(() => {
    return getLanguageIcon(tab.language) || getFileIcon(tab.filePath) || '📄'
  }, [tab.language, tab.filePath])

  // Format tab title
  const displayTitle = useMemo(() => {
    let title = tab.title
    
    // Truncate long titles
    if (title.length > 20) {
      title = title.substring(0, 17) + '...'
    }
    
    return title
  }, [tab.title])

  // Handle preview show/hide with delay
  const handleMouseEnter = useCallback((e: React.MouseEvent) => {
    onMouseEnter?.()
    
    if (enablePreview && !isActive) {
      // Clear any existing timeout
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
      
      // Show preview after delay
      hoverTimeoutRef.current = setTimeout(() => {
        const rect = e.currentTarget.getBoundingClientRect()
        setPreviewPosition({
          x: rect.left + rect.width / 2,
          y: rect.bottom + 10
        })
        setShowPreview(true)
      }, 1000) // 1 second delay
    }
  }, [enablePreview, isActive, onMouseEnter])

  const handleMouseLeave = useCallback(() => {
    onMouseLeave?.()
    
    // Clear timeout and hide preview
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current)
      hoverTimeoutRef.current = null
    }
    setShowPreview(false)
  }, [onMouseLeave])

  // Handle close button click
  const handleCloseClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    onClose()
  }, [onClose])

  // Handle pin button click
  const handlePinClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    onPin()
  }, [onPin])

  // Handle double-click to pin
  const handleDoubleClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    onPin()
  }, [onPin])

  // Cleanup timeouts on unmount
  React.useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
    }
  }, [])

  const tabClasses = [
    'tab-item',
    isActive && 'active',
    isPinned && 'pinned',
    hasUnsavedChanges && 'dirty',
    isHovered && 'hovered',
    groupColor && 'grouped'
  ].filter(Boolean).join(' ')

  return (
    <>
      <div
        ref={tabRef}
        className={tabClasses}
        style={{
          '--group-color': groupColor
        } as React.CSSProperties}
        data-tab-id={tab.id}
        onClick={onSelect}
        onDoubleClick={handleDoubleClick}
        onContextMenu={onContextMenu}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onMouseUp={onMouseUp}
        onDragStart={onDragStart}
        draggable={true}
        role="tab"
        tabIndex={isActive ? 0 : -1}
        aria-selected={isActive}
        aria-label={`${tab.title}${hasUnsavedChanges ? ' (unsaved)' : ''}${isPinned ? ' (pinned)' : ''}`}
        title={`${tab.filePath || tab.title}\n${hasUnsavedChanges ? 'Unsaved changes' : 'Saved'}\nLast modified: ${tab.lastModified.toLocaleString()}`}
      >
        {/* Group Indicator */}
        {groupColor && (
          <div 
            className="tab-group-indicator"
            style={{ backgroundColor: groupColor }}
            aria-hidden="true"
          />
        )}

        {/* File Icon */}
        <div className="tab-icon" aria-hidden="true">
          {typeof icon === 'string' ? (
            <span className="tab-icon-text">{icon}</span>
          ) : (
            icon
          )}
        </div>

        {/* Tab Title */}
        <span className="tab-title">
          {displayTitle}
        </span>

        {/* Dirty Indicator */}
        {hasUnsavedChanges && (
          <div 
            className="tab-dirty-indicator"
            aria-label="Unsaved changes"
            title="File has unsaved changes"
          >
            ●
          </div>
        )}

        {/* Pin Indicator */}
        {isPinned && (
          <button
            className="tab-pin-button pinned"
            onClick={handlePinClick}
            aria-label="Unpin tab"
            title="Click to unpin tab"
          >
            📌
          </button>
        )}

        {/* Actions */}
        <div className="tab-actions">
          {/* Pin Button (when not pinned) */}
          {!isPinned && (
            <button
              className="tab-pin-button"
              onClick={handlePinClick}
              aria-label="Pin tab"
              title="Pin tab (double-click tab to pin)"
            >
              📌
            </button>
          )}

          {/* Close Button */}
          <button
            className="tab-close-button"
            onClick={handleCloseClick}
            aria-label="Close tab"
            title="Close tab (middle-click to close)"
          >
            <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
              <path d="M1 1l8 8M9 1l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        {/* Loading/Processing Indicator */}
        {tab.content.length > 50000 && (
          <div className="tab-loading-indicator" title="Large file">
            ⚡
          </div>
        )}

        {/* Language Badge */}
        <div className="tab-language-badge" title={`Language: ${tab.language}`}>
          {tab.language.substring(0, 3).toUpperCase()}
        </div>
      </div>

      {/* Tab Preview */}
      {showPreview && enablePreview && (
        <TabPreview
          tab={tab}
          position={previewPosition}
          onClose={() => setShowPreview(false)}
        />
      )}
    </>
  )
}

export default TabItem