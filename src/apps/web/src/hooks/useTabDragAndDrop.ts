import { useCallback, useRef } from 'react'
import { TabDragCallbacks, TabDragData } from '../types/TabTypes'

export interface DragAndDropOptions {
  enableTabReordering?: boolean
  enableTabMoving?: boolean
  enablePanelCreation?: boolean
  enableFileDrops?: boolean
  dragThreshold?: number
  dropZoneSize?: number
}

export function useTabDragAndDrop(
  enabled: boolean = true,
  options: DragAndDropOptions = {}
) {
  const {
    enableTabReordering = true,
    enableTabMoving = true,
    enablePanelCreation = true,
    enableFileDrops = true,
    dragThreshold = 5,
    dropZoneSize = 20
  } = options

  const dragStateRef = useRef<{
    isDragging: boolean
    draggedTabId: string | null
    draggedFromPanelId: string | null
    startX: number
    startY: number
    ghostElement: HTMLElement | null
    dropIndicator: HTMLElement | null
  }>({
    isDragging: false,
    draggedTabId: null,
    draggedFromPanelId: null,
    startX: 0,
    startY: 0,
    ghostElement: null,
    dropIndicator: null
  })

  const setupDragAndDrop = useCallback((
    container: HTMLElement,
    callbacks: TabDragCallbacks
  ) => {
    if (!enabled || !container) return () => {}

    let dragStartTimer: NodeJS.Timeout | null = null

    // Handle drag start
    const handleDragStart = (event: DragEvent) => {
      const target = event.target as HTMLElement
      const tabElement = target.closest('.tab-item') as HTMLElement
      
      if (!tabElement) return

      const tabId = tabElement.dataset.tabId
      const panelElement = tabElement.closest('.split-panel')
      const panelId = panelElement?.id || 'main'

      if (!tabId) return

      dragStateRef.current = {
        isDragging: true,
        draggedTabId: tabId,
        draggedFromPanelId: panelId,
        startX: event.clientX,
        startY: event.clientY,
        ghostElement: null,
        dropIndicator: null
      }

      // Create custom drag data
      const dragData: TabDragData = {
        tabId,
        panelId,
        index: Array.from(tabElement.parentElement?.children || []).indexOf(tabElement)
      }

      event.dataTransfer?.setData('application/json', JSON.stringify(dragData))
      event.dataTransfer?.setData('text/plain', JSON.stringify(dragData))

      // Create ghost element
      const ghost = createGhostElement(tabElement)
      if (ghost) {
        dragStateRef.current.ghostElement = ghost
        document.body.appendChild(ghost)
        event.dataTransfer?.setDragImage(ghost, 0, 0)
      }

      // Add dragging class
      tabElement.classList.add('dragging')
      container.classList.add('drag-active')
    }

    // Handle drag over
    const handleDragOver = (event: DragEvent) => {
      if (!dragStateRef.current.isDragging) return

      event.preventDefault()
      event.dataTransfer!.dropEffect = 'move'

      const target = event.target as HTMLElement
      updateDropIndicator(event, target, container)
    }

    // Handle drag enter
    const handleDragEnter = (event: DragEvent) => {
      event.preventDefault()
      const target = event.target as HTMLElement
      const dropZone = target.closest('.drop-zone')
      
      if (dropZone) {
        dropZone.classList.add('drag-over')
      }
    }

    // Handle drag leave
    const handleDragLeave = (event: DragEvent) => {
      const target = event.target as HTMLElement
      const dropZone = target.closest('.drop-zone')
      
      if (dropZone && !dropZone.contains(event.relatedTarget as Node)) {
        dropZone.classList.remove('drag-over')
      }
    }

    // Handle drop
    const handleDrop = (event: DragEvent) => {
      event.preventDefault()
      
      if (!dragStateRef.current.isDragging) return

      try {
        const dragData = JSON.parse(event.dataTransfer?.getData('application/json') || '{}') as TabDragData
        const target = event.target as HTMLElement

        // Handle drop on tab bar (reordering)
        if (enableTabReordering) {
          const tabBar = target.closest('.tab-bar')
          if (tabBar) {
            const targetTab = target.closest('.tab-item') as HTMLElement
            if (targetTab && targetTab.dataset.tabId !== dragData.tabId) {
              const targetIndex = Array.from(targetTab.parentElement?.children || []).indexOf(targetTab)
              const targetPanelId = targetTab.closest('.split-panel')?.id || 'main'
              callbacks.onTabMove(dragData.tabId, targetIndex, targetPanelId)
            }
            return
          }
        }

        // Handle drop on panel (moving between panels)
        if (enableTabMoving) {
          const panel = target.closest('.split-panel')
          if (panel && panel.id !== dragData.panelId) {
            callbacks.onTabToPanel(dragData.tabId, panel.id)
            return
          }
        }

        // Handle drop on drop zones (creating new panels)
        if (enablePanelCreation) {
          const dropZone = target.closest('.drop-zone')
          if (dropZone) {
            const direction = dropZone.classList.contains('drop-zone-top') || dropZone.classList.contains('drop-zone-bottom')
              ? 'vertical' as const
              : 'horizontal' as const
            callbacks.onCreatePanel(direction, dragData.tabId)
            return
          }
        }

      } catch (error) {
        console.warn('Failed to handle tab drop:', error)
      }
    }

    // Handle drag end
    const handleDragEnd = (event: DragEvent) => {
      const target = event.target as HTMLElement
      const tabElement = target.closest('.tab-item')

      // Clean up drag state
      if (dragStateRef.current.ghostElement) {
        document.body.removeChild(dragStateRef.current.ghostElement)
      }
      
      if (dragStateRef.current.dropIndicator) {
        document.body.removeChild(dragStateRef.current.dropIndicator)
      }

      // Remove drag classes
      tabElement?.classList.remove('dragging')
      container.classList.remove('drag-active')
      
      // Clear drop zones
      container.querySelectorAll('.drop-zone').forEach(zone => {
        zone.classList.remove('drag-over')
      })

      // Reset state
      dragStateRef.current = {
        isDragging: false,
        draggedTabId: null,
        draggedFromPanelId: null,
        startX: 0,
        startY: 0,
        ghostElement: null,
        dropIndicator: null
      }
    }

    // Handle file drops
    const handleFileDrop = (event: DragEvent) => {
      if (!enableFileDrops) return

      event.preventDefault()
      const files = Array.from(event.dataTransfer?.files || [])
      
      if (files.length > 0) {
        // This would need to be handled by parent component
        console.log('Files dropped:', files.map(f => f.name))
      }
    }

    // Mouse event handlers for better drag detection
    const handleMouseDown = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      const tabElement = target.closest('.tab-item')
      
      if (!tabElement) return

      dragStartTimer = setTimeout(() => {
        // Initiate drag after delay to distinguish from clicks
        tabElement.draggable = true
      }, 100)
    }

    const handleMouseUp = () => {
      if (dragStartTimer) {
        clearTimeout(dragStartTimer)
      }
    }

    // Touch event handlers for mobile support
    const handleTouchStart = (event: TouchEvent) => {
      const target = event.target as HTMLElement
      const tabElement = target.closest('.tab-item')
      
      if (!tabElement) return

      // Prevent scrolling during drag
      event.preventDefault()
    }

    // Add event listeners
    container.addEventListener('dragstart', handleDragStart)
    container.addEventListener('dragover', handleDragOver)
    container.addEventListener('dragenter', handleDragEnter)
    container.addEventListener('dragleave', handleDragLeave)
    container.addEventListener('drop', handleDrop)
    container.addEventListener('dragend', handleDragEnd)
    container.addEventListener('mousedown', handleMouseDown)
    container.addEventListener('mouseup', handleMouseUp)
    container.addEventListener('touchstart', handleTouchStart, { passive: false })

    // Handle file drops on window
    if (enableFileDrops) {
      window.addEventListener('drop', handleFileDrop)
      window.addEventListener('dragover', (e) => e.preventDefault())
    }

    // Cleanup function
    return () => {
      container.removeEventListener('dragstart', handleDragStart)
      container.removeEventListener('dragover', handleDragOver)
      container.removeEventListener('dragenter', handleDragEnter)
      container.removeEventListener('dragleave', handleDragLeave)
      container.removeEventListener('drop', handleDrop)
      container.removeEventListener('dragend', handleDragEnd)
      container.removeEventListener('mousedown', handleMouseDown)
      container.removeEventListener('mouseup', handleMouseUp)
      container.removeEventListener('touchstart', handleTouchStart)

      if (enableFileDrops) {
        window.removeEventListener('drop', handleFileDrop)
        window.removeEventListener('dragover', (e) => e.preventDefault())
      }

      if (dragStartTimer) {
        clearTimeout(dragStartTimer)
      }

      // Clean up any remaining elements
      if (dragStateRef.current.ghostElement) {
        document.body.removeChild(dragStateRef.current.ghostElement)
      }
      if (dragStateRef.current.dropIndicator) {
        document.body.removeChild(dragStateRef.current.dropIndicator)
      }
    }
  }, [enabled, enableTabReordering, enableTabMoving, enablePanelCreation, enableFileDrops])

  // Create ghost element for drag preview
  const createGhostElement = (tabElement: HTMLElement): HTMLElement | null => {
    try {
      const ghost = tabElement.cloneNode(true) as HTMLElement
      ghost.style.position = 'absolute'
      ghost.style.top = '-1000px'
      ghost.style.left = '-1000px'
      ghost.style.pointerEvents = 'none'
      ghost.style.opacity = '0.8'
      ghost.style.transform = 'rotate(5deg)'
      ghost.style.zIndex = '10000'
      ghost.classList.add('drag-ghost')
      return ghost
    } catch (error) {
      console.warn('Failed to create ghost element:', error)
      return null
    }
  }

  // Update drop indicator position
  const updateDropIndicator = (event: DragEvent, target: HTMLElement, container: HTMLElement) => {
    // Remove existing indicator
    if (dragStateRef.current.dropIndicator) {
      document.body.removeChild(dragStateRef.current.dropIndicator)
      dragStateRef.current.dropIndicator = null
    }

    // Find target tab
    const targetTab = target.closest('.tab-item') as HTMLElement
    if (!targetTab) return

    // Create drop indicator
    const indicator = document.createElement('div')
    indicator.className = 'drop-indicator'
    indicator.style.position = 'absolute'
    indicator.style.width = '2px'
    indicator.style.height = `${targetTab.offsetHeight}px`
    indicator.style.backgroundColor = '#007acc'
    indicator.style.zIndex = '9999'
    indicator.style.pointerEvents = 'none'

    // Position indicator
    const rect = targetTab.getBoundingClientRect()
    const mouseX = event.clientX
    const isAfter = mouseX > rect.left + rect.width / 2

    indicator.style.left = `${isAfter ? rect.right : rect.left}px`
    indicator.style.top = `${rect.top}px`

    document.body.appendChild(indicator)
    dragStateRef.current.dropIndicator = indicator
  }

  return { setupDragAndDrop }
}

export default useTabDragAndDrop