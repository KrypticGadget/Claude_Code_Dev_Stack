import React from 'react'
import '../styles/split-handle.css'

export interface SplitHandleProps {
  direction: 'horizontal' | 'vertical'
  onResizeStart: (e: React.MouseEvent) => void
  style?: React.CSSProperties
}

export const SplitHandle: React.FC<SplitHandleProps> = ({
  direction,
  onResizeStart,
  style
}) => {
  return (
    <div
      className={`split-handle split-handle-${direction}`}
      style={style}
      onMouseDown={onResizeStart}
      role="separator"
      aria-orientation={direction === 'horizontal' ? 'vertical' : 'horizontal'}
      title={`Resize ${direction === 'horizontal' ? 'horizontally' : 'vertically'}`}
    >
      <div className="split-handle-bar">
        {direction === 'horizontal' ? (
          <svg width="4" height="16" viewBox="0 0 4 16" fill="currentColor">
            <circle cx="2" cy="4" r="1"/>
            <circle cx="2" cy="8" r="1"/>
            <circle cx="2" cy="12" r="1"/>
          </svg>
        ) : (
          <svg width="16" height="4" viewBox="0 0 16 4" fill="currentColor">
            <circle cx="4" cy="2" r="1"/>
            <circle cx="8" cy="2" r="1"/>
            <circle cx="12" cy="2" r="1"/>
          </svg>
        )}
      </div>
    </div>
  )
}

export default SplitHandle