import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import { Tab, TabGroup } from '../types/TabTypes'
import { TabItem } from './TabItem'
import { TabScrollControls } from './TabScrollControls'
import { TabOverflowMenu } from './TabOverflowMenu'
import '../styles/tab-bar.css'

export interface TabBarProps {
  tabs: Tab[]
  activeTabId: string | null
  pinnedTabs: Set<string>
  unsavedChanges: Set<string>
  tabGroups: TabGroup[]
  panelId: string
  isActive?: boolean
  maxVisibleTabs?: number
  enableVirtualScrolling?: boolean
  enableTabPreviews?: boolean
  onTabSelect: (tabId: string) => void
  onTabClose: (tabId: string) => void
  onTabPin: (tabId: string) => void
  onTabContextMenu: (e: React.MouseEvent, tabId: string) => void
  onTabMove?: (tabId: string, targetIndex: number) => void
  onNewTab?: () => void
}

export const TabBar: React.FC<TabBarProps> = ({
  tabs,
  activeTabId,
  pinnedTabs,
  unsavedChanges,
  tabGroups,
  panelId,
  isActive = true,
  maxVisibleTabs = 20,
  enableVirtualScrolling = true,
  enableTabPreviews = true,
  onTabSelect,
  onTabClose,
  onTabPin,
  onTabContextMenu,
  onTabMove,
  onNewTab
}) => {
  const [scrollPosition, setScrollPosition] = useState(0)
  const [showOverflow, setShowOverflow] = useState(false)
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null)
  const [hoveredTabId, setHoveredTabId] = useState<string | null>(null)
  
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const tabBarRef = useRef<HTMLDivElement>(null)
  const resizeObserverRef = useRef<ResizeObserver | null>(null)

  // Group tabs by their group membership
  const groupedTabs = useMemo(() => {
    const grouped: { group: TabGroup | null; tabs: Tab[] }[] = []
    const groupMap = new Map<string, TabGroup>()
    
    tabGroups.forEach(group => groupMap.set(group.id, group))
    
    // First, add pinned tabs (always at the beginning)
    const pinnedTabsList = tabs.filter(tab => pinnedTabs.has(tab.id))
    if (pinnedTabsList.length > 0) {
      grouped.push({ group: null, tabs: pinnedTabsList })
    }
    
    // Then group non-pinned tabs
    const nonPinnedTabs = tabs.filter(tab => !pinnedTabs.has(tab.id))
    const groupedByGroup = new Map<string | null, Tab[]>()
    
    nonPinnedTabs.forEach(tab => {
      const groupId = tab.groupId
      if (!groupedByGroup.has(groupId)) {
        groupedByGroup.set(groupId, [])
      }
      groupedByGroup.get(groupId)!.push(tab)
    })
    
    // Add ungrouped tabs first
    const ungroupedTabs = groupedByGroup.get(null) || []
    if (ungroupedTabs.length > 0) {
      grouped.push({ group: null, tabs: ungroupedTabs })
    }
    
    // Then add grouped tabs
    tabGroups.forEach(group => {
      const groupTabs = groupedByGroup.get(group.id) || []
      if (groupTabs.length > 0 && !group.isCollapsed) {
        grouped.push({ group, tabs: groupTabs })
      }
    })
    
    return grouped
  }, [tabs, pinnedTabs, tabGroups])

  // Calculate visible tabs for virtual scrolling
  const visibleTabs = useMemo(() => {
    if (!enableVirtualScrolling) {
      return groupedTabs.flatMap(g => g.tabs)
    }

    const allTabs = groupedTabs.flatMap(g => g.tabs)
    const startIndex = Math.floor(scrollPosition / 120) // Assuming 120px per tab
    return allTabs.slice(startIndex, startIndex + maxVisibleTabs)
  }, [groupedTabs, scrollPosition, maxVisibleTabs, enableVirtualScrolling])

  // Check if tabs overflow
  const checkOverflow = useCallback(() => {
    if (!tabBarRef.current || !scrollContainerRef.current) return

    const containerWidth = scrollContainerRef.current.clientWidth
    const contentWidth = tabBarRef.current.scrollWidth
    setShowOverflow(contentWidth > containerWidth)
  }, [])

  // Setup resize observer
  useEffect(() => {
    if (!scrollContainerRef.current) return

    resizeObserverRef.current = new ResizeObserver(checkOverflow)
    resizeObserverRef.current.observe(scrollContainerRef.current)

    return () => {
      if (resizeObserverRef.current) {
        resizeObserverRef.current.disconnect()
      }
    }
  }, [checkOverflow])

  // Check overflow when tabs change
  useEffect(() => {
    checkOverflow()
  }, [tabs, checkOverflow])

  // Auto-scroll to active tab
  useEffect(() => {
    if (!activeTabId || !tabBarRef.current || !scrollContainerRef.current) return

    const activeTabElement = tabBarRef.current.querySelector(`[data-tab-id="${activeTabId}"]`) as HTMLElement
    if (!activeTabElement) return

    const containerRect = scrollContainerRef.current.getBoundingClientRect()
    const tabRect = activeTabElement.getBoundingClientRect()

    if (tabRect.left < containerRect.left) {
      scrollContainerRef.current.scrollLeft -= (containerRect.left - tabRect.left) + 10
    } else if (tabRect.right > containerRect.right) {
      scrollContainerRef.current.scrollLeft += (tabRect.right - containerRect.right) + 10
    }
  }, [activeTabId])

  const handleScroll = useCallback((direction: 'left' | 'right') => {
    if (!scrollContainerRef.current) return

    const scrollAmount = 200
    const currentScroll = scrollContainerRef.current.scrollLeft
    const targetScroll = direction === 'left' 
      ? Math.max(0, currentScroll - scrollAmount)
      : currentScroll + scrollAmount

    scrollContainerRef.current.scrollTo({
      left: targetScroll,
      behavior: 'smooth'
    })
  }, [])

  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (!scrollContainerRef.current) return

    e.preventDefault()
    scrollContainerRef.current.scrollLeft += e.deltaY
  }, [])

  // Handle drag and drop
  const handleDragStart = useCallback((e: React.DragEvent, tabId: string) => {
    e.dataTransfer.setData('text/plain', JSON.stringify({ tabId, panelId }))
    e.dataTransfer.effectAllowed = 'move'
  }, [panelId])

  const handleDragOver = useCallback((e: React.DragEvent, index: number) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    setDragOverIndex(index)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent, targetIndex: number) => {
    e.preventDefault()
    setDragOverIndex(null)

    try {
      const data = JSON.parse(e.dataTransfer.getData('text/plain'))
      const { tabId } = data

      if (onTabMove) {
        onTabMove(tabId, targetIndex)
      }
    } catch (error) {
      console.error('Failed to parse drag data:', error)
    }
  }, [onTabMove])

  const handleDragLeave = useCallback(() => {
    setDragOverIndex(null)
  }, [])

  // Handle middle mouse click for tab close
  const handleMouseUp = useCallback((e: React.MouseEvent, tabId: string) => {
    if (e.button === 1) { // Middle mouse button
      e.preventDefault()
      onTabClose(tabId)
    }
  }, [onTabClose])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isActive) return

      // Ctrl+T for new tab
      if (e.ctrlKey && e.key === 't') {
        e.preventDefault()
        onNewTab?.()
      }
      // Ctrl+W for close tab
      else if (e.ctrlKey && e.key === 'w') {
        e.preventDefault()
        if (activeTabId) {
          onTabClose(activeTabId)
        }
      }
      // Ctrl+Tab for next tab
      else if (e.ctrlKey && e.key === 'Tab' && !e.shiftKey) {
        e.preventDefault()
        const currentIndex = tabs.findIndex(tab => tab.id === activeTabId)
        const nextIndex = (currentIndex + 1) % tabs.length
        if (tabs[nextIndex]) {
          onTabSelect(tabs[nextIndex].id)
        }
      }
      // Ctrl+Shift+Tab for previous tab
      else if (e.ctrlKey && e.shiftKey && e.key === 'Tab') {
        e.preventDefault()
        const currentIndex = tabs.findIndex(tab => tab.id === activeTabId)
        const prevIndex = currentIndex === 0 ? tabs.length - 1 : currentIndex - 1
        if (tabs[prevIndex]) {
          onTabSelect(tabs[prevIndex].id)
        }
      }
      // Ctrl+1-9 for tab by index
      else if (e.ctrlKey && /^[1-9]$/.test(e.key)) {
        e.preventDefault()
        const index = parseInt(e.key) - 1
        if (tabs[index]) {
          onTabSelect(tabs[index].id)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isActive, tabs, activeTabId, onTabSelect, onTabClose, onNewTab])

  return (
    <div className={`tab-bar ${isActive ? 'active' : ''}`}>
      {/* Scroll Controls */}
      {showOverflow && (
        <TabScrollControls
          onScrollLeft={() => handleScroll('left')}
          onScrollRight={() => handleScroll('right')}
          canScrollLeft={scrollPosition > 0}
          canScrollRight={true} // Will be calculated properly
        />
      )}

      {/* Tab Container */}
      <div
        ref={scrollContainerRef}
        className="tab-scroll-container"
        onWheel={handleWheel}
        onDragLeave={handleDragLeave}
      >
        <div ref={tabBarRef} className="tab-content">
          {groupedTabs.map((groupData, groupIndex) => (
            <div key={`group-${groupIndex}`} className="tab-group-section">
              {/* Group Header */}
              {groupData.group && (
                <div className="tab-group-header" style={{ borderColor: groupData.group.color }}>
                  <span className="tab-group-name">{groupData.group.name}</span>
                  <div className="tab-group-indicator" style={{ backgroundColor: groupData.group.color }} />
                </div>
              )}

              {/* Group Tabs */}
              <div className="tab-group-tabs">
                {groupData.tabs.map((tab, tabIndex) => {
                  const absoluteIndex = groupedTabs
                    .slice(0, groupIndex)
                    .reduce((acc, g) => acc + g.tabs.length, 0) + tabIndex

                  return (
                    <div
                      key={tab.id}
                      className={`tab-item-wrapper ${dragOverIndex === absoluteIndex ? 'drag-over' : ''}`}
                      onDragOver={(e) => handleDragOver(e, absoluteIndex)}
                      onDrop={(e) => handleDrop(e, absoluteIndex)}
                    >
                      <TabItem
                        tab={tab}
                        isActive={tab.id === activeTabId}
                        isPinned={pinnedTabs.has(tab.id)}
                        hasUnsavedChanges={unsavedChanges.has(tab.id)}
                        groupColor={groupData.group?.color}
                        enablePreview={enableTabPreviews}
                        isHovered={hoveredTabId === tab.id}
                        onSelect={() => onTabSelect(tab.id)}
                        onClose={() => onTabClose(tab.id)}
                        onPin={() => onTabPin(tab.id)}
                        onContextMenu={(e) => onTabContextMenu(e, tab.id)}
                        onMouseEnter={() => setHoveredTabId(tab.id)}
                        onMouseLeave={() => setHoveredTabId(null)}
                        onMouseUp={(e) => handleMouseUp(e, tab.id)}
                        onDragStart={(e) => handleDragStart(e, tab.id)}
                      />
                    </div>
                  )
                })}
              </div>
            </div>
          ))}

          {/* New Tab Button */}
          {onNewTab && (
            <button
              className="new-tab-button"
              onClick={onNewTab}
              title="New Tab (Ctrl+T)"
              aria-label="Create new tab"
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                <path d="M6 1v10M1 6h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Overflow Menu */}
      {showOverflow && (
        <TabOverflowMenu
          tabs={tabs}
          activeTabId={activeTabId}
          onTabSelect={onTabSelect}
        />
      )}
    </div>
  )
}

export default TabBar