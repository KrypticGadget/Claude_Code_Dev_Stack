import React from 'react'
import '../styles/tab-scroll-controls.css'

export interface TabScrollControlsProps {
  onScrollLeft: () => void
  onScrollRight: () => void
  canScrollLeft: boolean
  canScrollRight: boolean
}

export const TabScrollControls: React.FC<TabScrollControlsProps> = ({
  onScrollLeft,
  onScrollRight,
  canScrollLeft,
  canScrollRight
}) => {
  return (
    <div className="tab-scroll-controls">
      <button
        className={`scroll-button scroll-left ${!canScrollLeft ? 'disabled' : ''}`}
        onClick={onScrollLeft}
        disabled={!canScrollLeft}
        title="Scroll tabs left"
        aria-label="Scroll tabs left"
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
          <path d="M8 2L4 6l4 4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
      
      <button
        className={`scroll-button scroll-right ${!canScrollRight ? 'disabled' : ''}`}
        onClick={onScrollRight}
        disabled={!canScrollRight}
        title="Scroll tabs right"
        aria-label="Scroll tabs right"
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
          <path d="M4 2l4 4-4 4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </div>
  )
}

export default TabScrollControls