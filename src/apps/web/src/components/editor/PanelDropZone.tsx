import React from 'react'
import '../styles/panel-drop-zone.css'

export interface PanelDropZoneProps {
  panelId: string
  onDrop: (e: React.DragEvent, targetPanelId: string, position?: 'top' | 'bottom' | 'left' | 'right') => void
}

export const PanelDropZone: React.FC<PanelDropZoneProps> = ({
  panelId,
  onDrop
}) => {
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  return (
    <div className="panel-drop-zones">
      {/* Center drop zone - add to existing panel */}
      <div
        className="drop-zone drop-zone-center"
        onDragOver={handleDragOver}
        onDrop={(e) => onDrop(e, panelId)}
      >
        <div className="drop-zone-indicator">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L22 12L12 22L2 12Z" stroke="currentColor" strokeWidth="2" fill="none"/>
            <path d="M8 12H16M12 8V16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <span>Add to panel</span>
        </div>
      </div>

      {/* Split drop zones */}
      <div
        className="drop-zone drop-zone-top"
        onDragOver={handleDragOver}
        onDrop={(e) => onDrop(e, panelId, 'top')}
      >
        <div className="drop-zone-indicator">
          <svg width="20" height="8" viewBox="0 0 20 8" fill="currentColor">
            <rect x="0" y="0" width="20" height="3" rx="1"/>
            <rect x="0" y="5" width="20" height="3" rx="1" opacity="0.5"/>
          </svg>
          <span>Split top</span>
        </div>
      </div>

      <div
        className="drop-zone drop-zone-bottom"
        onDragOver={handleDragOver}
        onDrop={(e) => onDrop(e, panelId, 'bottom')}
      >
        <div className="drop-zone-indicator">
          <svg width="20" height="8" viewBox="0 0 20 8" fill="currentColor">
            <rect x="0" y="0" width="20" height="3" rx="1" opacity="0.5"/>
            <rect x="0" y="5" width="20" height="3" rx="1"/>
          </svg>
          <span>Split bottom</span>
        </div>
      </div>

      <div
        className="drop-zone drop-zone-left"
        onDragOver={handleDragOver}
        onDrop={(e) => onDrop(e, panelId, 'left')}
      >
        <div className="drop-zone-indicator">
          <svg width="8" height="20" viewBox="0 0 8 20" fill="currentColor">
            <rect x="0" y="0" width="3" height="20" rx="1"/>
            <rect x="5" y="0" width="3" height="20" rx="1" opacity="0.5"/>
          </svg>
          <span>Split left</span>
        </div>
      </div>

      <div
        className="drop-zone drop-zone-right"
        onDragOver={handleDragOver}
        onDrop={(e) => onDrop(e, panelId, 'right')}
      >
        <div className="drop-zone-indicator">
          <svg width="8" height="20" viewBox="0 0 8 20" fill="currentColor">
            <rect x="0" y="0" width="3" height="20" rx="1" opacity="0.5"/>
            <rect x="5" y="0" width="3" height="20" rx="1"/>
          </svg>
          <span>Split right</span>
        </div>
      </div>
    </div>
  )
}

export default PanelDropZone