import React, { useCallback, useState, useRef } from 'react'
import { SplitLayout, SplitOrientation } from './types'

interface SplitViewToolbarProps {
  layout: SplitLayout
  orientation: SplitOrientation
  onLayoutChange: (layout: SplitLayout) => void
  onOrientationChange: (orientation: SplitOrientation) => void
  onSplitHorizontal: () => void
  onSplitVertical: () => void
  onSplitGrid: () => void
  onShowSettings?: () => void
  showLabels?: boolean
  size?: 'small' | 'medium' | 'large'
}

export const SplitViewToolbar: React.FC<SplitViewToolbarProps> = ({
  layout,
  orientation,
  onLayoutChange,
  onOrientationChange,
  onSplitHorizontal,
  onSplitVertical,
  onSplitGrid,
  onShowSettings,
  showLabels = false,
  size = 'medium'
}) => {
  const [showLayoutMenu, setShowLayoutMenu] = useState(false)
  const layoutMenuRef = useRef<HTMLDivElement>(null)

  // Layout options
  const layoutOptions: Array<{ value: SplitLayout; label: string; icon: string; description: string }> = [
    { value: 'single', label: 'Single', icon: '▢', description: 'Single pane view' },
    { value: 'two-pane', label: 'Two Pane', icon: '▢▢', description: 'Side by side' },
    { value: 'three-pane-horizontal', label: 'Three Horizontal', icon: '▢▢▢', description: 'Three panes horizontally' },
    { value: 'three-pane-vertical', label: 'Three Vertical', icon: '⚏', description: 'Three panes vertically' },
    { value: 'four-pane-grid', label: 'Grid', icon: '⊞', description: 'Four pane grid' },
    { value: 'four-pane-horizontal', label: 'Four Horizontal', icon: '▢▢▢▢', description: 'Four panes horizontally' },
    { value: 'four-pane-vertical', label: 'Four Vertical', icon: '⚏⚏', description: 'Four panes vertically' }
  ]

  const currentLayoutOption = layoutOptions.find(opt => opt.value === layout) || layoutOptions[1]

  // Handle layout menu toggle
  const handleLayoutMenuToggle = useCallback(() => {
    setShowLayoutMenu(!showLayoutMenu)
  }, [showLayoutMenu])

  // Handle layout selection
  const handleLayoutSelect = useCallback((newLayout: SplitLayout) => {
    onLayoutChange(newLayout)
    setShowLayoutMenu(false)
  }, [onLayoutChange])

  // Handle orientation toggle
  const handleOrientationToggle = useCallback(() => {
    onOrientationChange(orientation === 'horizontal' ? 'vertical' : 'horizontal')
  }, [orientation, onOrientationChange])

  // Close layout menu when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (layoutMenuRef.current && !layoutMenuRef.current.contains(event.target as Node)) {
        setShowLayoutMenu(false)
      }
    }

    if (showLayoutMenu) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showLayoutMenu])

  // Button size styles
  const buttonSizes = {
    small: { padding: '4px 8px', fontSize: '12px' },
    medium: { padding: '6px 12px', fontSize: '14px' },
    large: { padding: '8px 16px', fontSize: '16px' }
  }

  const buttonStyle = {
    ...buttonSizes[size],
    backgroundColor: 'transparent',
    border: '1px solid #ddd',
    borderRadius: '4px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    transition: 'all 0.2s ease',
    color: '#333'
  }

  const activeButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#007acc',
    color: 'white',
    borderColor: '#007acc'
  }

  return (
    <div 
      className="split-view-toolbar"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px',
        backgroundColor: '#f8f8f8',
        borderBottom: '1px solid #ddd',
        flexWrap: 'wrap'
      }}
    >
      {/* Layout Selector */}
      <div className="layout-selector" style={{ position: 'relative' }} ref={layoutMenuRef}>
        <button
          style={buttonStyle}
          onClick={handleLayoutMenuToggle}
          title={`Current layout: ${currentLayoutOption.label}`}
          onMouseEnter={(e) => {
            if (layout !== currentLayoutOption.value) {
              (e.target as HTMLElement).style.backgroundColor = '#f0f0f0'
            }
          }}
          onMouseLeave={(e) => {
            if (layout !== currentLayoutOption.value) {
              (e.target as HTMLElement).style.backgroundColor = 'transparent'
            }
          }}
        >
          <span style={{ fontSize: size === 'small' ? '10px' : '12px' }}>
            {currentLayoutOption.icon}
          </span>
          {showLabels && <span>{currentLayoutOption.label}</span>}
          <span style={{ fontSize: '10px' }}>▼</span>
        </button>

        {/* Layout Dropdown */}
        {showLayoutMenu && (
          <div
            className="layout-menu"
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              backgroundColor: 'white',
              border: '1px solid #ddd',
              borderRadius: '4px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
              zIndex: 1000,
              minWidth: '200px',
              maxHeight: '300px',
              overflowY: 'auto'
            }}
          >
            {layoutOptions.map(option => (
              <div
                key={option.value}
                className="layout-option"
                style={{
                  padding: '8px 12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  backgroundColor: option.value === layout ? '#f0f8ff' : 'transparent',
                  borderLeft: option.value === layout ? '3px solid #007acc' : '3px solid transparent'
                }}
                onClick={() => handleLayoutSelect(option.value)}
                onMouseEnter={(e) => {
                  if (option.value !== layout) {
                    (e.target as HTMLElement).style.backgroundColor = '#f8f8f8'
                  }
                }}
                onMouseLeave={(e) => {
                  if (option.value !== layout) {
                    (e.target as HTMLElement).style.backgroundColor = 'transparent'
                  }
                }}
              >
                <span style={{ fontSize: '12px', minWidth: '20px' }}>{option.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '13px', fontWeight: option.value === layout ? 'bold' : 'normal' }}>
                    {option.label}
                  </div>
                  <div style={{ fontSize: '11px', color: '#666' }}>
                    {option.description}
                  </div>
                </div>
                {option.value === layout && (
                  <span style={{ color: '#007acc', fontSize: '12px' }}>✓</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Orientation Toggle */}
      <button
        style={buttonStyle}
        onClick={handleOrientationToggle}
        title={`Toggle orientation (current: ${orientation})`}
        onMouseEnter={(e) => {
          (e.target as HTMLElement).style.backgroundColor = '#f0f0f0'
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLElement).style.backgroundColor = 'transparent'
        }}
      >
        <span style={{ fontSize: size === 'small' ? '10px' : '12px' }}>
          {orientation === 'horizontal' ? '⟷' : '↕'}
        </span>
        {showLabels && <span>{orientation === 'horizontal' ? 'Horizontal' : 'Vertical'}</span>}
      </button>

      {/* Divider */}
      <div 
        style={{ 
          width: '1px', 
          height: '20px', 
          backgroundColor: '#ddd',
          margin: '0 4px' 
        }} 
      />

      {/* Quick Split Actions */}
      <button
        style={buttonStyle}
        onClick={onSplitHorizontal}
        title="Split pane horizontally (Ctrl+H)"
        onMouseEnter={(e) => {
          (e.target as HTMLElement).style.backgroundColor = '#f0f0f0'
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLElement).style.backgroundColor = 'transparent'
        }}
      >
        <span style={{ fontSize: size === 'small' ? '10px' : '12px' }}>⚋</span>
        {showLabels && <span>Split H</span>}
      </button>

      <button
        style={buttonStyle}
        onClick={onSplitVertical}
        title="Split pane vertically (Ctrl+V)"
        onMouseEnter={(e) => {
          (e.target as HTMLElement).style.backgroundColor = '#f0f0f0'
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLElement).style.backgroundColor = 'transparent'
        }}
      >
        <span style={{ fontSize: size === 'small' ? '10px' : '12px' }}>⚊</span>
        {showLabels && <span>Split V</span>}
      </button>

      <button
        style={buttonStyle}
        onClick={onSplitGrid}
        title="Create 4-pane grid layout"
        onMouseEnter={(e) => {
          (e.target as HTMLElement).style.backgroundColor = '#f0f0f0'
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLElement).style.backgroundColor = 'transparent'
        }}
      >
        <span style={{ fontSize: size === 'small' ? '10px' : '12px' }}>⊞</span>
        {showLabels && <span>Grid</span>}
      </button>

      {/* Divider */}
      <div 
        style={{ 
          width: '1px', 
          height: '20px', 
          backgroundColor: '#ddd',
          margin: '0 4px' 
        }} 
      />

      {/* Settings Button */}
      {onShowSettings && (
        <button
          style={buttonStyle}
          onClick={onShowSettings}
          title="Open split view settings"
          onMouseEnter={(e) => {
            (e.target as HTMLElement).style.backgroundColor = '#f0f0f0'
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLElement).style.backgroundColor = 'transparent'
          }}
        >
          <span style={{ fontSize: size === 'small' ? '10px' : '12px' }}>⚙</span>
          {showLabels && <span>Settings</span>}
        </button>
      )}

      {/* Responsive breakpoint indicator */}
      <div style={{ marginLeft: 'auto', fontSize: '11px', color: '#666' }}>
        <span className="hide-mobile">
          {layout} • {orientation}
        </span>
      </div>

      <style jsx>{`
        .split-view-toolbar {
          user-select: none;
        }

        .layout-menu {
          animation: slideDown 0.2s ease;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .layout-option {
          transition: background-color 0.15s ease;
        }

        /* Mobile responsiveness */
        @media (max-width: 768px) {
          .split-view-toolbar {
            gap: 4px;
            padding: 6px;
          }

          .hide-mobile {
            display: none;
          }

          button {
            padding: 4px 6px !important;
            font-size: 12px !important;
          }

          .layout-menu {
            left: -100px;
            right: 0;
            min-width: 180px;
          }
        }

        @media (max-width: 480px) {
          .split-view-toolbar {
            flex-direction: column;
            align-items: stretch;
            gap: 8px;
          }

          .layout-selector {
            order: 1;
          }

          button:not(.layout-selector button) {
            flex: 1;
            justify-content: center;
          }
        }

        /* Focus styles for accessibility */
        button:focus {
          outline: 2px solid #007acc;
          outline-offset: 2px;
        }

        .layout-option:focus {
          outline: 2px solid #007acc;
          outline-offset: -2px;
        }

        /* High contrast mode support */
        @media (prefers-contrast: high) {
          .split-view-toolbar {
            border-bottom-width: 2px;
          }

          button {
            border-width: 2px;
          }

          .layout-menu {
            border-width: 2px;
          }
        }

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
          button,
          .layout-option {
            transition: none;
          }

          .layout-menu {
            animation: none;
          }
        }
      `}</style>
    </div>
  )
}

export default SplitViewToolbar