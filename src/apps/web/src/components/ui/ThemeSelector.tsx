// Theme Selector - Quick Theme Switching Interface
// Provides theme selection, preview, and management capabilities

import React, { useState, useRef, useEffect } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { ThemeConfig } from '../types/theme'

interface ThemeSelectorProps {
  size?: 'small' | 'medium' | 'large'
  orientation?: 'horizontal' | 'vertical'
  showPreview?: boolean
  showCreateButton?: boolean
  onCreateTheme?: () => void
  className?: string
}

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({
  size = 'medium',
  orientation = 'horizontal',
  showPreview = true,
  showCreateButton = true,
  onCreateTheme,
  className = ''
}) => {
  const {
    currentTheme,
    availableThemes,
    setTheme,
    toggleTheme,
    userPreferences,
    updateUserPreferences,
    deleteCustomTheme,
    exportTheme
  } = useTheme()

  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'built-in' | 'custom' | 'light' | 'dark'>('all')
  const [hoveredTheme, setHoveredTheme] = useState<ThemeConfig | null>(null)
  const selectorRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectorRef.current && !selectorRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  // Filter themes based on search and category
  const filteredThemes = availableThemes.filter(theme => {
    const matchesSearch = theme.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         theme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (theme.tags && theme.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))

    const matchesCategory = selectedCategory === 'all' ||
                           (selectedCategory === 'built-in' && !userPreferences.customThemes.includes(theme.id)) ||
                           (selectedCategory === 'custom' && userPreferences.customThemes.includes(theme.id)) ||
                           (selectedCategory === 'light' && theme.type === 'light') ||
                           (selectedCategory === 'dark' && theme.type === 'dark')

    return matchesSearch && matchesCategory
  })

  // Group themes by type
  const groupedThemes = {
    light: filteredThemes.filter(theme => theme.type === 'light'),
    dark: filteredThemes.filter(theme => theme.type === 'dark')
  }

  const handleThemeSelect = (theme: ThemeConfig) => {
    setTheme(theme.id)
    setIsOpen(false)
  }

  const handleDeleteTheme = async (theme: ThemeConfig, event: React.MouseEvent) => {
    event.stopPropagation()
    
    if (confirm(`Are you sure you want to delete the theme "${theme.displayName}"?`)) {
      try {
        await deleteCustomTheme(theme.id)
      } catch (error) {
        console.error('Failed to delete theme:', error)
      }
    }
  }

  const handleExportTheme = async (theme: ThemeConfig, event: React.MouseEvent) => {
    event.stopPropagation()
    
    try {
      const exportData = await exportTheme(theme.id)
      const blob = new Blob([exportData], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${theme.name}-theme.json`
      link.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export theme:', error)
    }
  }

  const handleAutoSwitchChange = (mode: 'system' | 'time' | 'manual') => {
    updateUserPreferences({ autoSwitchMode: mode })
  }

  return (
    <div className={`theme-selector ${className}`} ref={selectorRef}>
      <div className="theme-selector-current" onClick={() => setIsOpen(!isOpen)}>
        <div className="current-theme-preview">
          <div 
            className="theme-color-dots"
            style={{
              background: `linear-gradient(45deg, 
                ${currentTheme.colors.primary} 0%, 
                ${currentTheme.colors.secondary} 50%, 
                ${currentTheme.colors.accent} 100%)`
            }}
          />
          <div className="current-theme-info">
            <span className="theme-name">{currentTheme.displayName}</span>
            <span className="theme-type">{currentTheme.type}</span>
          </div>
        </div>
        
        <div className="theme-selector-actions">
          <button
            className="btn btn-sm btn-secondary"
            onClick={(e) => {
              e.stopPropagation()
              toggleTheme()
            }}
            title="Toggle theme"
          >
            {currentTheme.type === 'dark' ? '☀️' : '🌙'}
          </button>
          
          <button
            className="btn btn-sm btn-secondary"
            onClick={(e) => {
              e.stopPropagation()
              setIsOpen(!isOpen)
            }}
            title="Theme settings"
          >
            ⚙️
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="theme-selector-dropdown">
          <div className="theme-selector-header">
            <h3>Choose Theme</h3>
            
            <div className="theme-search">
              <input
                type="text"
                placeholder="Search themes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
            </div>

            <div className="theme-categories">
              <button
                className={`category-btn ${selectedCategory === 'all' ? 'active' : ''}`}
                onClick={() => setSelectedCategory('all')}
              >
                All
              </button>
              <button
                className={`category-btn ${selectedCategory === 'light' ? 'active' : ''}`}
                onClick={() => setSelectedCategory('light')}
              >
                Light
              </button>
              <button
                className={`category-btn ${selectedCategory === 'dark' ? 'active' : ''}`}
                onClick={() => setSelectedCategory('dark')}
              >
                Dark
              </button>
              <button
                className={`category-btn ${selectedCategory === 'custom' ? 'active' : ''}`}
                onClick={() => setSelectedCategory('custom')}
              >
                Custom
              </button>
            </div>
          </div>

          <div className="theme-selector-content">
            <div className="auto-switch-settings">
              <h4>Auto Switch</h4>
              <div className="auto-switch-options">
                <label>
                  <input
                    type="radio"
                    name="autoSwitch"
                    value="manual"
                    checked={userPreferences.autoSwitchMode === 'manual'}
                    onChange={() => handleAutoSwitchChange('manual')}
                  />
                  Manual
                </label>
                <label>
                  <input
                    type="radio"
                    name="autoSwitch"
                    value="system"
                    checked={userPreferences.autoSwitchMode === 'system'}
                    onChange={() => handleAutoSwitchChange('system')}
                  />
                  System
                </label>
                <label>
                  <input
                    type="radio"
                    name="autoSwitch"
                    value="time"
                    checked={userPreferences.autoSwitchMode === 'time'}
                    onChange={() => handleAutoSwitchChange('time')}
                  />
                  Time-based
                </label>
              </div>
            </div>

            {userPreferences.autoSwitchMode === 'time' && (
              <div className="time-schedule">
                <h4>Schedule</h4>
                <div className="schedule-inputs">
                  <label>
                    Dark mode start:
                    <input
                      type="time"
                      value={userPreferences.scheduleStart || '18:00'}
                      onChange={(e) => updateUserPreferences({ scheduleStart: e.target.value })}
                    />
                  </label>
                  <label>
                    Light mode start:
                    <input
                      type="time"
                      value={userPreferences.scheduleEnd || '06:00'}
                      onChange={(e) => updateUserPreferences({ scheduleEnd: e.target.value })}
                    />
                  </label>
                </div>
              </div>
            )}

            <div className="theme-grid">
              {['light', 'dark'].map(type => {
                const themes = groupedThemes[type as 'light' | 'dark']
                if (themes.length === 0) return null

                return (
                  <div key={type} className="theme-group">
                    <h4>{type.charAt(0).toUpperCase() + type.slice(1)} Themes</h4>
                    
                    <div className="theme-list">
                      {themes.map(theme => (
                        <div
                          key={theme.id}
                          className={`theme-option ${currentTheme.id === theme.id ? 'active' : ''}`}
                          onClick={() => handleThemeSelect(theme)}
                          onMouseEnter={() => showPreview && setHoveredTheme(theme)}
                          onMouseLeave={() => showPreview && setHoveredTheme(null)}
                        >
                          <div className="theme-preview">
                            <div 
                              className="theme-colors"
                              style={{
                                background: `linear-gradient(135deg, 
                                  ${theme.colors.background} 0%, 
                                  ${theme.colors.backgroundSecondary} 50%, 
                                  ${theme.colors.backgroundTertiary} 100%)`
                              }}
                            >
                              <div className="color-sample primary" style={{ backgroundColor: theme.colors.primary }} />
                              <div className="color-sample secondary" style={{ backgroundColor: theme.colors.secondary }} />
                              <div className="color-sample accent" style={{ backgroundColor: theme.colors.accent }} />
                            </div>
                          </div>
                          
                          <div className="theme-info">
                            <div className="theme-title">
                              <span className="name">{theme.displayName}</span>
                              {theme.author && (
                                <span className="author">by {theme.author}</span>
                              )}
                            </div>
                            
                            {theme.tags && (
                              <div className="theme-tags">
                                {theme.tags.slice(0, 3).map(tag => (
                                  <span key={tag} className="tag">{tag}</span>
                                ))}
                              </div>
                            )}
                          </div>
                          
                          <div className="theme-actions">
                            {userPreferences.customThemes.includes(theme.id) && (
                              <>
                                <button
                                  className="action-btn export"
                                  onClick={(e) => handleExportTheme(theme, e)}
                                  title="Export theme"
                                >
                                  📤
                                </button>
                                <button
                                  className="action-btn delete"
                                  onClick={(e) => handleDeleteTheme(theme, e)}
                                  title="Delete theme"
                                >
                                  🗑️
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>

            {showCreateButton && (
              <div className="theme-actions-footer">
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    onCreateTheme?.()
                    setIsOpen(false)
                  }}
                >
                  Create Custom Theme
                </button>
              </div>
            )}
          </div>

          {showPreview && hoveredTheme && (
            <div className="theme-preview-panel">
              <h4>Preview: {hoveredTheme.displayName}</h4>
              
              <div className="preview-content" data-theme-preview={hoveredTheme.id}>
                <div className="preview-ui">
                  <div className="preview-header" style={{ backgroundColor: hoveredTheme.colors.backgroundSecondary }}>
                    <div className="preview-title" style={{ color: hoveredTheme.colors.textPrimary }}>
                      Sample UI
                    </div>
                    <button 
                      className="preview-btn"
                      style={{ 
                        backgroundColor: hoveredTheme.colors.primary,
                        color: hoveredTheme.colors.textInverse
                      }}
                    >
                      Button
                    </button>
                  </div>
                  
                  <div className="preview-body" style={{ backgroundColor: hoveredTheme.colors.background }}>
                    <p style={{ color: hoveredTheme.colors.textPrimary }}>
                      Primary text content
                    </p>
                    <p style={{ color: hoveredTheme.colors.textSecondary }}>
                      Secondary text content
                    </p>
                    
                    <div className="preview-states">
                      <span className="state success" style={{ color: hoveredTheme.colors.success }}>
                        Success
                      </span>
                      <span className="state warning" style={{ color: hoveredTheme.colors.warning }}>
                        Warning
                      </span>
                      <span className="state error" style={{ color: hoveredTheme.colors.error }}>
                        Error
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        .theme-selector {
          position: relative;
          display: inline-block;
        }

        .theme-selector-current {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm);
          background: var(--color-background-secondary);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all var(--transition-fast);
          min-width: 200px;
        }

        .theme-selector-current:hover {
          background: var(--color-background-tertiary);
          border-color: var(--color-primary);
        }

        .current-theme-preview {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          flex: 1;
        }

        .theme-color-dots {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          border: 2px solid var(--color-border);
        }

        .current-theme-info {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .theme-name {
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
        }

        .theme-type {
          font-size: var(--font-size-xs);
          color: var(--color-text-muted);
          text-transform: capitalize;
        }

        .theme-selector-actions {
          display: flex;
          gap: var(--spacing-xs);
        }

        .theme-selector-dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          z-index: var(--z-dropdown);
          background: var(--color-background);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-lg);
          margin-top: var(--spacing-xs);
          max-height: 600px;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .theme-selector-header {
          padding: var(--spacing-md);
          border-bottom: 1px solid var(--color-border);
        }

        .theme-selector-header h3 {
          margin: 0 0 var(--spacing-md) 0;
          font-size: var(--font-size-lg);
          color: var(--color-text-primary);
        }

        .theme-search {
          margin-bottom: var(--spacing-md);
        }

        .search-input {
          width: 100%;
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background-secondary);
          color: var(--color-text-primary);
          font-size: var(--font-size-sm);
        }

        .theme-categories {
          display: flex;
          gap: var(--spacing-xs);
        }

        .category-btn {
          padding: var(--spacing-xs) var(--spacing-sm);
          border: 1px solid var(--color-border);
          background: var(--color-background-secondary);
          color: var(--color-text-secondary);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all var(--transition-fast);
          font-size: var(--font-size-xs);
        }

        .category-btn:hover {
          background: var(--color-background-tertiary);
          color: var(--color-text-primary);
        }

        .category-btn.active {
          background: var(--color-primary);
          color: white;
          border-color: var(--color-primary);
        }

        .theme-selector-content {
          flex: 1;
          overflow-y: auto;
          padding: var(--spacing-md);
        }

        .auto-switch-settings {
          margin-bottom: var(--spacing-lg);
        }

        .auto-switch-settings h4 {
          margin: 0 0 var(--spacing-sm) 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .auto-switch-options {
          display: flex;
          gap: var(--spacing-md);
        }

        .auto-switch-options label {
          display: flex;
          align-items: center;
          gap: var(--spacing-xs);
          font-size: var(--font-size-sm);
          color: var(--color-text-primary);
          cursor: pointer;
        }

        .time-schedule {
          margin-bottom: var(--spacing-lg);
          padding: var(--spacing-md);
          background: var(--color-background-secondary);
          border-radius: var(--radius-md);
        }

        .time-schedule h4 {
          margin: 0 0 var(--spacing-sm) 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .schedule-inputs {
          display: flex;
          gap: var(--spacing-md);
        }

        .schedule-inputs label {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
          font-size: var(--font-size-sm);
          color: var(--color-text-primary);
        }

        .schedule-inputs input {
          padding: var(--spacing-xs);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background: var(--color-background);
          color: var(--color-text-primary);
        }

        .theme-grid {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }

        .theme-group h4 {
          margin: 0 0 var(--spacing-md) 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .theme-list {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
        }

        .theme-option {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all var(--transition-fast);
          position: relative;
        }

        .theme-option:hover {
          border-color: var(--color-primary);
          background: var(--color-background-secondary);
        }

        .theme-option.active {
          border-color: var(--color-primary);
          background: var(--color-primary-light);
        }

        .theme-preview {
          flex-shrink: 0;
        }

        .theme-colors {
          width: 48px;
          height: 32px;
          border-radius: var(--radius-md);
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 2px;
          border: 1px solid var(--color-border);
        }

        .color-sample {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .theme-info {
          flex: 1;
        }

        .theme-title {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .theme-title .name {
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
        }

        .theme-title .author {
          font-size: var(--font-size-xs);
          color: var(--color-text-muted);
        }

        .theme-tags {
          display: flex;
          gap: var(--spacing-xs);
          margin-top: var(--spacing-xs);
        }

        .tag {
          padding: 2px var(--spacing-xs);
          background: var(--color-background-tertiary);
          color: var(--color-text-muted);
          border-radius: var(--radius-sm);
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .theme-actions {
          display: flex;
          gap: var(--spacing-xs);
          opacity: 0;
          transition: opacity var(--transition-fast);
        }

        .theme-option:hover .theme-actions {
          opacity: 1;
        }

        .action-btn {
          padding: var(--spacing-xs);
          border: none;
          background: none;
          cursor: pointer;
          border-radius: var(--radius-sm);
          transition: background var(--transition-fast);
          font-size: var(--font-size-xs);
        }

        .action-btn:hover {
          background: var(--color-background-tertiary);
        }

        .action-btn.delete:hover {
          background: var(--color-error-light);
        }

        .theme-actions-footer {
          margin-top: var(--spacing-lg);
          padding-top: var(--spacing-lg);
          border-top: 1px solid var(--color-border);
        }

        .theme-preview-panel {
          position: absolute;
          left: 100%;
          top: 0;
          width: 300px;
          background: var(--color-background);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-lg);
          padding: var(--spacing-md);
          margin-left: var(--spacing-sm);
        }

        .theme-preview-panel h4 {
          margin: 0 0 var(--spacing-md) 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-primary);
        }

        .preview-ui {
          border-radius: var(--radius-md);
          overflow: hidden;
          border: 1px solid var(--color-border);
        }

        .preview-header {
          padding: var(--spacing-sm);
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .preview-title {
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
        }

        .preview-btn {
          padding: var(--spacing-xs) var(--spacing-sm);
          border: none;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-xs);
          cursor: pointer;
        }

        .preview-body {
          padding: var(--spacing-sm);
        }

        .preview-body p {
          margin: 0 0 var(--spacing-xs) 0;
          font-size: var(--font-size-sm);
        }

        .preview-states {
          display: flex;
          gap: var(--spacing-sm);
          margin-top: var(--spacing-sm);
        }

        .state {
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-medium);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
      `}</style>
    </div>
  )
}