// Theme Manager - Comprehensive Theme Management Interface
// Advanced theme management with import/export, accessibility testing, and live preview

import React, { useState, useRef, useCallback } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { ThemeConfig, AccessibilityOptions } from '../types/theme'
import { ThemeValidator } from '../utils/theme-validator'
import { ColorPicker } from '../components/ColorPicker'
import { ThemeBuilder } from '../components/ThemeBuilder'

export const ThemeManager: React.FC = () => {
  const {
    currentTheme,
    availableThemes,
    userPreferences,
    setTheme,
    updateUserPreferences,
    deleteCustomTheme,
    importTheme,
    exportTheme,
    applyAccessibilityMode
  } = useTheme()

  const [activeTab, setActiveTab] = useState<'gallery' | 'builder' | 'accessibility' | 'import'>('gallery')
  const [showThemeBuilder, setShowThemeBuilder] = useState(false)
  const [selectedTheme, setSelectedTheme] = useState<ThemeConfig | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'light' | 'dark' | 'custom'>('all')
  const [importData, setImportData] = useState('')
  const [previewTheme, setPreviewTheme] = useState<ThemeConfig | null>(null)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const validator = new ThemeValidator()

  // Filter themes based on search and type
  const filteredThemes = availableThemes.filter(theme => {
    const matchesSearch = theme.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         theme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (theme.tags && theme.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))

    const matchesType = filterType === 'all' ||
                       (filterType === 'custom' && userPreferences.customThemes.includes(theme.id)) ||
                       (filterType !== 'custom' && theme.type === filterType)

    return matchesSearch && matchesType
  })

  const handleThemeSelect = useCallback((theme: ThemeConfig) => {
    setTheme(theme.id)
    setSelectedTheme(theme)
  }, [setTheme])

  const handleDeleteTheme = useCallback(async (themeId: string) => {
    if (confirm('Are you sure you want to delete this custom theme?')) {
      try {
        await deleteCustomTheme(themeId)
        if (selectedTheme?.id === themeId) {
          setSelectedTheme(null)
        }
      } catch (error) {
        console.error('Failed to delete theme:', error)
      }
    }
  }, [deleteCustomTheme, selectedTheme])

  const handleExportTheme = useCallback(async (themeId: string) => {
    try {
      const exportData = await exportTheme(themeId)
      const blob = new Blob([exportData], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      const theme = availableThemes.find(t => t.id === themeId)
      link.download = `${theme?.name || themeId}-theme.json`
      link.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export theme:', error)
    }
  }, [exportTheme, availableThemes])

  const handleFileImport = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const text = await file.text()
      setImportData(text)
      setActiveTab('import')
    } catch (error) {
      console.error('Failed to read file:', error)
    }
  }, [])

  const handleImportTheme = useCallback(async () => {
    if (!importData.trim()) return

    try {
      await importTheme(importData)
      setImportData('')
      alert('Theme imported successfully!')
    } catch (error) {
      console.error('Failed to import theme:', error)
      alert('Failed to import theme. Please check the format.')
    }
  }, [importTheme, importData])

  const handleAccessibilityChange = useCallback((option: keyof AccessibilityOptions, value: any) => {
    applyAccessibilityMode({ [option]: value })
  }, [applyAccessibilityMode])

  const getThemeValidation = useCallback((theme: ThemeConfig) => {
    return validator.validateTheme(theme)
  }, [validator])

  return (
    <div className="theme-manager">
      <ThemeBuilder
        isOpen={showThemeBuilder}
        onClose={() => setShowThemeBuilder(false)}
        baseThemeId={selectedTheme?.id}
      />

      <div className="theme-manager-header">
        <h1>Theme Manager</h1>
        <p>Manage, create, and customize themes for your development environment</p>
        
        <div className="header-actions">
          <button
            className="btn btn-primary"
            onClick={() => setShowThemeBuilder(true)}
          >
            Create New Theme
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            onChange={handleFileImport}
            style={{ display: 'none' }}
          />
          
          <button
            className="btn btn-secondary"
            onClick={() => fileInputRef.current?.click()}
          >
            Import Theme
          </button>
        </div>
      </div>

      <div className="theme-manager-content">
        <div className="theme-tabs">
          <button
            className={`tab ${activeTab === 'gallery' ? 'active' : ''}`}
            onClick={() => setActiveTab('gallery')}
          >
            Theme Gallery
          </button>
          <button
            className={`tab ${activeTab === 'accessibility' ? 'active' : ''}`}
            onClick={() => setActiveTab('accessibility')}
          >
            Accessibility
          </button>
          <button
            className={`tab ${activeTab === 'import' ? 'active' : ''}`}
            onClick={() => setActiveTab('import')}
          >
            Import/Export
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'gallery' && (
            <div className="theme-gallery">
              <div className="gallery-filters">
                <div className="search-bar">
                  <input
                    type="text"
                    placeholder="Search themes..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                  />
                </div>
                
                <div className="filter-buttons">
                  <button
                    className={`filter-btn ${filterType === 'all' ? 'active' : ''}`}
                    onClick={() => setFilterType('all')}
                  >
                    All ({availableThemes.length})
                  </button>
                  <button
                    className={`filter-btn ${filterType === 'light' ? 'active' : ''}`}
                    onClick={() => setFilterType('light')}
                  >
                    Light ({availableThemes.filter(t => t.type === 'light').length})
                  </button>
                  <button
                    className={`filter-btn ${filterType === 'dark' ? 'active' : ''}`}
                    onClick={() => setFilterType('dark')}
                  >
                    Dark ({availableThemes.filter(t => t.type === 'dark').length})
                  </button>
                  <button
                    className={`filter-btn ${filterType === 'custom' ? 'active' : ''}`}
                    onClick={() => setFilterType('custom')}
                  >
                    Custom ({userPreferences.customThemes.length})
                  </button>
                </div>
              </div>

              <div className="theme-grid">
                {filteredThemes.map(theme => {
                  const validation = getThemeValidation(theme)
                  const isCustom = userPreferences.customThemes.includes(theme.id)
                  const isCurrent = currentTheme.id === theme.id

                  return (
                    <div
                      key={theme.id}
                      className={`theme-card ${isCurrent ? 'current' : ''} ${previewTheme?.id === theme.id ? 'preview' : ''}`}
                      onMouseEnter={() => setPreviewTheme(theme)}
                      onMouseLeave={() => setPreviewTheme(null)}
                    >
                      <div className="theme-preview">
                        <div 
                          className="preview-background"
                          style={{ backgroundColor: theme.colors.background }}
                        >
                          <div 
                            className="preview-sidebar"
                            style={{ backgroundColor: theme.colors.backgroundSecondary }}
                          >
                            <div className="preview-nav-item" style={{ backgroundColor: theme.colors.primary }} />
                            <div className="preview-nav-item" style={{ backgroundColor: theme.colors.backgroundTertiary }} />
                            <div className="preview-nav-item" style={{ backgroundColor: theme.colors.backgroundTertiary }} />
                          </div>
                          
                          <div className="preview-main">
                            <div className="preview-header" style={{ backgroundColor: theme.colors.backgroundSecondary }}>
                              <div className="preview-text" style={{ backgroundColor: theme.colors.textPrimary }} />
                              <div className="preview-button" style={{ backgroundColor: theme.colors.primary }} />
                            </div>
                            
                            <div className="preview-content">
                              <div className="preview-line" style={{ backgroundColor: theme.colors.textPrimary }} />
                              <div className="preview-line short" style={{ backgroundColor: theme.colors.textSecondary }} />
                              <div className="preview-line" style={{ backgroundColor: theme.colors.textPrimary }} />
                              
                              <div className="preview-states">
                                <div className="state-dot success" style={{ backgroundColor: theme.colors.success }} />
                                <div className="state-dot warning" style={{ backgroundColor: theme.colors.warning }} />
                                <div className="state-dot error" style={{ backgroundColor: theme.colors.error }} />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="theme-info">
                        <div className="theme-header">
                          <div className="theme-title">
                            <h3>{theme.displayName}</h3>
                            {theme.author && (
                              <span className="theme-author">by {theme.author}</span>
                            )}
                          </div>
                          
                          <div className="theme-badges">
                            <span className={`badge type-${theme.type}`}>{theme.type}</span>
                            {isCustom && <span className="badge custom">Custom</span>}
                            {!validation.isValid && <span className="badge invalid">Invalid</span>}
                          </div>
                        </div>

                        {theme.description && (
                          <p className="theme-description">{theme.description}</p>
                        )}

                        {theme.tags && (
                          <div className="theme-tags">
                            {theme.tags.slice(0, 4).map(tag => (
                              <span key={tag} className="tag">{tag}</span>
                            ))}
                          </div>
                        )}

                        <div className="theme-actions">
                          <button
                            className={`btn btn-sm ${isCurrent ? 'btn-success' : 'btn-primary'}`}
                            onClick={() => handleThemeSelect(theme)}
                            disabled={!validation.isValid}
                          >
                            {isCurrent ? 'Current' : 'Apply'}
                          </button>
                          
                          <button
                            className="btn btn-sm btn-secondary"
                            onClick={() => handleExportTheme(theme.id)}
                          >
                            Export
                          </button>
                          
                          {isCustom && (
                            <button
                              className="btn btn-sm btn-error"
                              onClick={() => handleDeleteTheme(theme.id)}
                            >
                              Delete
                            </button>
                          )}
                        </div>

                        {!validation.isValid && validation.errors.length > 0 && (
                          <div className="validation-errors">
                            <h4>Validation Errors:</h4>
                            <ul>
                              {validation.errors.slice(0, 3).map((error, index) => (
                                <li key={index}>{error}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {activeTab === 'accessibility' && (
            <div className="accessibility-panel">
              <h2>Accessibility Settings</h2>
              <p>Configure accessibility features to enhance usability</p>

              <div className="accessibility-settings">
                <div className="setting-group">
                  <h3>Visual Accessibility</h3>
                  
                  <label className="setting-item">
                    <input
                      type="checkbox"
                      checked={userPreferences.accessibility.highContrast}
                      onChange={(e) => handleAccessibilityChange('highContrast', e.target.checked)}
                    />
                    <span>High Contrast Mode</span>
                    <p>Increases contrast for better visibility</p>
                  </label>

                  <label className="setting-item">
                    <input
                      type="checkbox"
                      checked={userPreferences.accessibility.largeText}
                      onChange={(e) => handleAccessibilityChange('largeText', e.target.checked)}
                    />
                    <span>Large Text</span>
                    <p>Increases font sizes and touch targets</p>
                  </label>

                  <div className="setting-item">
                    <label>Color Blind Support</label>
                    <select
                      value={userPreferences.accessibility.colorBlindMode}
                      onChange={(e) => handleAccessibilityChange('colorBlindMode', e.target.value)}
                    >
                      <option value="none">None</option>
                      <option value="protanopia">Protanopia (Red-blind)</option>
                      <option value="deuteranopia">Deuteranopia (Green-blind)</option>
                      <option value="tritanopia">Tritanopia (Blue-blind)</option>
                    </select>
                    <p>Adjusts colors for color vision deficiencies</p>
                  </div>
                </div>

                <div className="setting-group">
                  <h3>Motion & Animation</h3>
                  
                  <label className="setting-item">
                    <input
                      type="checkbox"
                      checked={userPreferences.accessibility.reducedMotion}
                      onChange={(e) => handleAccessibilityChange('reducedMotion', e.target.checked)}
                    />
                    <span>Reduced Motion</span>
                    <p>Minimizes animations and transitions</p>
                  </label>
                </div>

                <div className="setting-group">
                  <h3>Interaction</h3>
                  
                  <label className="setting-item">
                    <input
                      type="checkbox"
                      checked={userPreferences.accessibility.focusVisible}
                      onChange={(e) => handleAccessibilityChange('focusVisible', e.target.checked)}
                    />
                    <span>Enhanced Focus Indicators</span>
                    <p>Shows prominent focus outlines for keyboard navigation</p>
                  </label>

                  <label className="setting-item">
                    <input
                      type="checkbox"
                      checked={userPreferences.accessibility.screenReaderOptimized}
                      onChange={(e) => handleAccessibilityChange('screenReaderOptimized', e.target.checked)}
                    />
                    <span>Screen Reader Optimizations</span>
                    <p>Enhances compatibility with screen readers</p>
                  </label>
                </div>
              </div>

              <div className="accessibility-test">
                <h3>Current Theme Accessibility</h3>
                {(() => {
                  const validation = getThemeValidation(currentTheme)
                  return (
                    <div className="accessibility-results">
                      <div className={`result ${validation.isValid ? 'pass' : 'fail'}`}>
                        <strong>Overall:</strong> {validation.isValid ? 'Pass' : 'Fail'}
                      </div>
                      
                      {validation.accessibilityIssues.length > 0 && (
                        <div className="issues">
                          <h4>Accessibility Issues:</h4>
                          <ul>
                            {validation.accessibilityIssues.map((issue, index) => (
                              <li key={index}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )
                })()}
              </div>
            </div>
          )}

          {activeTab === 'import' && (
            <div className="import-export-panel">
              <h2>Import & Export Themes</h2>
              
              <div className="import-section">
                <h3>Import Theme</h3>
                <p>Paste theme JSON data or use the file import button above</p>
                
                <textarea
                  value={importData}
                  onChange={(e) => setImportData(e.target.value)}
                  placeholder="Paste theme JSON data here..."
                  className="import-textarea"
                  rows={10}
                />
                
                <div className="import-actions">
                  <button
                    className="btn btn-primary"
                    onClick={handleImportTheme}
                    disabled={!importData.trim()}
                  >
                    Import Theme
                  </button>
                  
                  <button
                    className="btn btn-secondary"
                    onClick={() => setImportData('')}
                  >
                    Clear
                  </button>
                </div>
              </div>

              <div className="export-section">
                <h3>Export Themes</h3>
                <p>Export your custom themes to share or backup</p>
                
                <div className="export-list">
                  {userPreferences.customThemes.map(themeId => {
                    const theme = availableThemes.find(t => t.id === themeId)
                    if (!theme) return null
                    
                    return (
                      <div key={themeId} className="export-item">
                        <div className="export-info">
                          <span className="export-name">{theme.displayName}</span>
                          <span className="export-type">{theme.type}</span>
                        </div>
                        <button
                          className="btn btn-sm btn-secondary"
                          onClick={() => handleExportTheme(themeId)}
                        >
                          Export
                        </button>
                      </div>
                    )
                  })}
                  
                  {userPreferences.customThemes.length === 0 && (
                    <p className="no-custom-themes">No custom themes to export</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .theme-manager {
          max-width: 1400px;
          margin: 0 auto;
          padding: var(--spacing-lg);
        }

        .theme-manager-header {
          margin-bottom: var(--spacing-xl);
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }

        .theme-manager-header h1 {
          margin: 0 0 var(--spacing-sm) 0;
          color: var(--color-text-primary);
        }

        .theme-manager-header p {
          margin: 0;
          color: var(--color-text-secondary);
        }

        .header-actions {
          display: flex;
          gap: var(--spacing-sm);
        }

        .theme-tabs {
          display: flex;
          gap: var(--spacing-xs);
          margin-bottom: var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
        }

        .tab {
          padding: var(--spacing-sm) var(--spacing-md);
          border: none;
          background: none;
          color: var(--color-text-secondary);
          border-bottom: 2px solid transparent;
          cursor: pointer;
          transition: all var(--transition-fast);
          font-weight: var(--font-weight-medium);
        }

        .tab:hover {
          color: var(--color-text-primary);
        }

        .tab.active {
          color: var(--color-primary);
          border-bottom-color: var(--color-primary);
        }

        .gallery-filters {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-lg);
          gap: var(--spacing-md);
        }

        .search-input {
          width: 300px;
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background-secondary);
          color: var(--color-text-primary);
        }

        .filter-buttons {
          display: flex;
          gap: var(--spacing-xs);
        }

        .filter-btn {
          padding: var(--spacing-xs) var(--spacing-sm);
          border: 1px solid var(--color-border);
          background: var(--color-background-secondary);
          color: var(--color-text-secondary);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all var(--transition-fast);
          font-size: var(--font-size-sm);
        }

        .filter-btn:hover {
          background: var(--color-background-tertiary);
          color: var(--color-text-primary);
        }

        .filter-btn.active {
          background: var(--color-primary);
          color: white;
          border-color: var(--color-primary);
        }

        .theme-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: var(--spacing-lg);
        }

        .theme-card {
          background: var(--color-background-secondary);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          overflow: hidden;
          transition: all var(--transition-fast);
          cursor: pointer;
        }

        .theme-card:hover {
          border-color: var(--color-primary);
          transform: translateY(-2px);
          box-shadow: var(--shadow-lg);
        }

        .theme-card.current {
          border-color: var(--color-success);
          background: var(--color-success-light);
        }

        .theme-card.preview {
          border-color: var(--color-primary);
          box-shadow: var(--shadow-md);
        }

        .theme-preview {
          height: 150px;
          overflow: hidden;
          position: relative;
        }

        .preview-background {
          width: 100%;
          height: 100%;
          display: flex;
          font-size: 8px;
        }

        .preview-sidebar {
          width: 30%;
          padding: 8px;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .preview-nav-item {
          height: 12px;
          border-radius: 2px;
        }

        .preview-main {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .preview-header {
          height: 24px;
          padding: 4px 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .preview-text {
          width: 40px;
          height: 8px;
          border-radius: 1px;
        }

        .preview-button {
          width: 20px;
          height: 8px;
          border-radius: 2px;
        }

        .preview-content {
          flex: 1;
          padding: 8px;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .preview-line {
          height: 6px;
          border-radius: 1px;
        }

        .preview-line.short {
          width: 60%;
        }

        .preview-states {
          display: flex;
          gap: 4px;
          margin-top: 8px;
        }

        .state-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        .theme-info {
          padding: var(--spacing-md);
        }

        .theme-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: var(--spacing-sm);
        }

        .theme-title h3 {
          margin: 0;
          font-size: var(--font-size-base);
          color: var(--color-text-primary);
        }

        .theme-author {
          font-size: var(--font-size-xs);
          color: var(--color-text-muted);
        }

        .theme-badges {
          display: flex;
          gap: var(--spacing-xs);
        }

        .badge {
          padding: 2px var(--spacing-xs);
          border-radius: var(--radius-sm);
          font-size: 10px;
          text-transform: uppercase;
          font-weight: var(--font-weight-medium);
          letter-spacing: 0.05em;
        }

        .badge.type-light {
          background: var(--color-warning-light);
          color: var(--color-warning-dark);
        }

        .badge.type-dark {
          background: var(--color-info-light);
          color: var(--color-info-dark);
        }

        .badge.custom {
          background: var(--color-primary-light);
          color: var(--color-primary-dark);
        }

        .badge.invalid {
          background: var(--color-error-light);
          color: var(--color-error-dark);
        }

        .theme-description {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          margin: var(--spacing-sm) 0;
          line-height: 1.4;
        }

        .theme-tags {
          display: flex;
          gap: var(--spacing-xs);
          margin: var(--spacing-sm) 0;
          flex-wrap: wrap;
        }

        .tag {
          padding: 2px var(--spacing-xs);
          background: var(--color-background-tertiary);
          color: var(--color-text-muted);
          border-radius: var(--radius-sm);
          font-size: 10px;
        }

        .theme-actions {
          display: flex;
          gap: var(--spacing-xs);
          margin-top: var(--spacing-md);
        }

        .validation-errors {
          margin-top: var(--spacing-sm);
          padding: var(--spacing-sm);
          background: var(--color-error-light);
          border-radius: var(--radius-md);
        }

        .validation-errors h4 {
          margin: 0 0 var(--spacing-xs) 0;
          font-size: var(--font-size-xs);
          color: var(--color-error-dark);
        }

        .validation-errors ul {
          margin: 0;
          padding-left: var(--spacing-md);
          font-size: var(--font-size-xs);
          color: var(--color-error-dark);
        }

        .accessibility-panel {
          max-width: 800px;
        }

        .accessibility-settings {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xl);
          margin-bottom: var(--spacing-xl);
        }

        .setting-group {
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--spacing-lg);
        }

        .setting-group h3 {
          margin: 0 0 var(--spacing-md) 0;
          color: var(--color-text-primary);
        }

        .setting-item {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
          margin-bottom: var(--spacing-md);
          cursor: pointer;
        }

        .setting-item:last-child {
          margin-bottom: 0;
        }

        .setting-item input,
        .setting-item select {
          margin-right: var(--spacing-sm);
        }

        .setting-item span {
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
        }

        .setting-item p {
          font-size: var(--font-size-sm);
          color: var(--color-text-muted);
          margin: 0;
        }

        .accessibility-test {
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--spacing-lg);
        }

        .accessibility-results .result {
          padding: var(--spacing-sm);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-md);
        }

        .accessibility-results .result.pass {
          background: var(--color-success-light);
          color: var(--color-success-dark);
        }

        .accessibility-results .result.fail {
          background: var(--color-error-light);
          color: var(--color-error-dark);
        }

        .issues h4 {
          margin: 0 0 var(--spacing-sm) 0;
          color: var(--color-text-primary);
        }

        .issues ul {
          margin: 0;
          padding-left: var(--spacing-md);
          color: var(--color-text-secondary);
        }

        .import-export-panel {
          max-width: 800px;
        }

        .import-section,
        .export-section {
          margin-bottom: var(--spacing-xl);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--spacing-lg);
        }

        .import-textarea {
          width: 100%;
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background);
          color: var(--color-text-primary);
          font-family: var(--font-family-mono);
          font-size: var(--font-size-sm);
          resize: vertical;
          margin: var(--spacing-md) 0;
        }

        .import-actions {
          display: flex;
          gap: var(--spacing-sm);
        }

        .export-list {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
        }

        .export-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--spacing-sm);
          background: var(--color-background-secondary);
          border-radius: var(--radius-md);
        }

        .export-info {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
        }

        .export-name {
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
        }

        .export-type {
          font-size: var(--font-size-sm);
          color: var(--color-text-muted);
          text-transform: capitalize;
        }

        .no-custom-themes {
          text-align: center;
          color: var(--color-text-muted);
          font-style: italic;
          padding: var(--spacing-lg);
        }
      `}</style>
    </div>
  )
}