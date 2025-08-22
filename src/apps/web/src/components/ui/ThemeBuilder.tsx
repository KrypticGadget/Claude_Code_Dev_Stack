// Theme Builder - Interactive Theme Customization Tool
// Comprehensive theme builder with live preview and real-time validation

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { ThemeConfig, ColorPalette, ThemeBuilderState, ColorGroup } from '../types/theme'
import { ThemeValidator } from '../utils/theme-validator'
import { ColorPicker } from './ColorPicker'
import { Typography } from './Typography'
import { MonacoThemeEditor } from './MonacoThemeEditor'
import { TerminalThemeEditor } from './TerminalThemeEditor'
import { AccessibilityPanel } from './AccessibilityPanel'

interface ThemeBuilderProps {
  isOpen: boolean
  onClose: () => void
  baseThemeId?: string
}

export const ThemeBuilder: React.FC<ThemeBuilderProps> = ({
  isOpen,
  onClose,
  baseThemeId
}) => {
  const { currentTheme, availableThemes, createCustomTheme, updateCustomTheme } = useTheme()
  const [builderState, setBuilderState] = useState<ThemeBuilderState>({
    baseTheme: currentTheme,
    modifiedTheme: currentTheme,
    previewMode: false,
    activeSection: 'colors',
    unsavedChanges: false
  })

  const validator = useMemo(() => new ThemeValidator(), [])
  const validation = useMemo(() => validator.validateTheme(builderState.modifiedTheme), [builderState.modifiedTheme, validator])

  // Initialize with base theme
  useEffect(() => {
    if (baseThemeId) {
      const baseTheme = availableThemes.find(t => t.id === baseThemeId) || currentTheme
      setBuilderState(prev => ({
        ...prev,
        baseTheme,
        modifiedTheme: { ...baseTheme }
      }))
    }
  }, [baseThemeId, availableThemes, currentTheme])

  // Color groups for organized editing
  const colorGroups: ColorGroup[] = [
    {
      name: 'Primary Colors',
      colors: [
        { key: 'primary', label: 'Primary', value: builderState.modifiedTheme.colors.primary },
        { key: 'primaryLight', label: 'Primary Light', value: builderState.modifiedTheme.colors.primaryLight },
        { key: 'primaryDark', label: 'Primary Dark', value: builderState.modifiedTheme.colors.primaryDark },
        { key: 'secondary', label: 'Secondary', value: builderState.modifiedTheme.colors.secondary },
        { key: 'secondaryLight', label: 'Secondary Light', value: builderState.modifiedTheme.colors.secondaryLight },
        { key: 'secondaryDark', label: 'Secondary Dark', value: builderState.modifiedTheme.colors.secondaryDark },
        { key: 'accent', label: 'Accent', value: builderState.modifiedTheme.colors.accent },
        { key: 'accentLight', label: 'Accent Light', value: builderState.modifiedTheme.colors.accentLight },
        { key: 'accentDark', label: 'Accent Dark', value: builderState.modifiedTheme.colors.accentDark }
      ]
    },
    {
      name: 'Background Colors',
      colors: [
        { key: 'background', label: 'Background', value: builderState.modifiedTheme.colors.background },
        { key: 'backgroundSecondary', label: 'Secondary Background', value: builderState.modifiedTheme.colors.backgroundSecondary },
        { key: 'backgroundTertiary', label: 'Tertiary Background', value: builderState.modifiedTheme.colors.backgroundTertiary },
        { key: 'backgroundElevated', label: 'Elevated Background', value: builderState.modifiedTheme.colors.backgroundElevated }
      ]
    },
    {
      name: 'Text Colors',
      colors: [
        { key: 'textPrimary', label: 'Primary Text', value: builderState.modifiedTheme.colors.textPrimary },
        { key: 'textSecondary', label: 'Secondary Text', value: builderState.modifiedTheme.colors.textSecondary },
        { key: 'textMuted', label: 'Muted Text', value: builderState.modifiedTheme.colors.textMuted },
        { key: 'textInverse', label: 'Inverse Text', value: builderState.modifiedTheme.colors.textInverse }
      ]
    },
    {
      name: 'State Colors',
      colors: [
        { key: 'success', label: 'Success', value: builderState.modifiedTheme.colors.success },
        { key: 'successLight', label: 'Success Light', value: builderState.modifiedTheme.colors.successLight },
        { key: 'successDark', label: 'Success Dark', value: builderState.modifiedTheme.colors.successDark },
        { key: 'warning', label: 'Warning', value: builderState.modifiedTheme.colors.warning },
        { key: 'warningLight', label: 'Warning Light', value: builderState.modifiedTheme.colors.warningLight },
        { key: 'warningDark', label: 'Warning Dark', value: builderState.modifiedTheme.colors.warningDark },
        { key: 'error', label: 'Error', value: builderState.modifiedTheme.colors.error },
        { key: 'errorLight', label: 'Error Light', value: builderState.modifiedTheme.colors.errorLight },
        { key: 'errorDark', label: 'Error Dark', value: builderState.modifiedTheme.colors.errorDark },
        { key: 'info', label: 'Info', value: builderState.modifiedTheme.colors.info },
        { key: 'infoLight', label: 'Info Light', value: builderState.modifiedTheme.colors.infoLight },
        { key: 'infoDark', label: 'Info Dark', value: builderState.modifiedTheme.colors.infoDark }
      ]
    }
  ]

  const updateColor = useCallback((colorKey: keyof ColorPalette, value: string) => {
    setBuilderState(prev => ({
      ...prev,
      modifiedTheme: {
        ...prev.modifiedTheme,
        colors: {
          ...prev.modifiedTheme.colors,
          [colorKey]: value
        }
      },
      unsavedChanges: true
    }))
  }, [])

  const updateThemeProperty = useCallback((property: keyof ThemeConfig, value: any) => {
    setBuilderState(prev => ({
      ...prev,
      modifiedTheme: {
        ...prev.modifiedTheme,
        [property]: value
      },
      unsavedChanges: true
    }))
  }, [])

  const resetToBase = useCallback(() => {
    setBuilderState(prev => ({
      ...prev,
      modifiedTheme: { ...prev.baseTheme },
      unsavedChanges: false
    }))
  }, [])

  const togglePreview = useCallback(() => {
    setBuilderState(prev => ({
      ...prev,
      previewMode: !prev.previewMode
    }))
  }, [])

  const saveTheme = useCallback(async () => {
    try {
      const themeToSave: ThemeConfig = {
        ...builderState.modifiedTheme,
        id: `custom-${Date.now()}`,
        name: `custom-${Date.now()}`,
        displayName: builderState.modifiedTheme.displayName || 'Custom Theme',
        author: 'User',
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }

      await createCustomTheme(themeToSave)
      
      setBuilderState(prev => ({
        ...prev,
        unsavedChanges: false
      }))

      onClose()
    } catch (error) {
      console.error('Failed to save theme:', error)
    }
  }, [builderState.modifiedTheme, createCustomTheme, onClose])

  const generateColorVariations = useCallback((baseColor: string, colorKey: keyof ColorPalette) => {
    // Auto-generate light and dark variations
    const rgb = hexToRgb(baseColor)
    if (!rgb) return

    const [r, g, b] = rgb
    
    // Generate lighter version (mix with white)
    const lightR = Math.round(r + (255 - r) * 0.3)
    const lightG = Math.round(g + (255 - g) * 0.3)
    const lightB = Math.round(b + (255 - b) * 0.3)
    const lightColor = rgbToHex(lightR, lightG, lightB)
    
    // Generate darker version (multiply by factor)
    const darkR = Math.round(r * 0.7)
    const darkG = Math.round(g * 0.7)
    const darkB = Math.round(b * 0.7)
    const darkColor = rgbToHex(darkR, darkG, darkB)

    // Update related colors
    const baseName = colorKey.replace(/Light|Dark/, '') as keyof ColorPalette
    
    updateColor(baseName, baseColor)
    updateColor(`${baseName}Light` as keyof ColorPalette, lightColor)
    updateColor(`${baseName}Dark` as keyof ColorPalette, darkColor)
  }, [updateColor])

  if (!isOpen) return null

  return (
    <div className="theme-builder-overlay">
      <div className="theme-builder">
        <div className="theme-builder-header">
          <div className="theme-builder-title">
            <h2>Theme Builder</h2>
            <p>Customize and create your perfect theme</p>
          </div>
          
          <div className="theme-builder-actions">
            <button
              className={`btn btn-secondary ${builderState.previewMode ? 'active' : ''}`}
              onClick={togglePreview}
            >
              {builderState.previewMode ? 'Exit Preview' : 'Preview'}
            </button>
            
            <button
              className="btn btn-secondary"
              onClick={resetToBase}
              disabled={!builderState.unsavedChanges}
            >
              Reset
            </button>
            
            <button
              className="btn btn-primary"
              onClick={saveTheme}
              disabled={!validation.isValid || !builderState.unsavedChanges}
            >
              Save Theme
            </button>
            
            <button
              className="btn btn-secondary"
              onClick={onClose}
            >
              Close
            </button>
          </div>
        </div>

        <div className="theme-builder-content">
          <div className="theme-builder-sidebar">
            <nav className="theme-builder-nav">
              <button
                className={`nav-item ${builderState.activeSection === 'colors' ? 'active' : ''}`}
                onClick={() => setBuilderState(prev => ({ ...prev, activeSection: 'colors' }))}
              >
                <span className="nav-icon">🎨</span>
                Colors
              </button>
              
              <button
                className={`nav-item ${builderState.activeSection === 'typography' ? 'active' : ''}`}
                onClick={() => setBuilderState(prev => ({ ...prev, activeSection: 'typography' }))}
              >
                <span className="nav-icon">📝</span>
                Typography
              </button>
              
              <button
                className={`nav-item ${builderState.activeSection === 'spacing' ? 'active' : ''}`}
                onClick={() => setBuilderState(prev => ({ ...prev, activeSection: 'spacing' }))}
              >
                <span className="nav-icon">📐</span>
                Spacing
              </button>
              
              <button
                className={`nav-item ${builderState.activeSection === 'monaco' ? 'active' : ''}`}
                onClick={() => setBuilderState(prev => ({ ...prev, activeSection: 'monaco' }))}
              >
                <span className="nav-icon">💻</span>
                Editor
              </button>
              
              <button
                className={`nav-item ${builderState.activeSection === 'terminal' ? 'active' : ''}`}
                onClick={() => setBuilderState(prev => ({ ...prev, activeSection: 'terminal' }))}
              >
                <span className="nav-icon">⌨️</span>
                Terminal
              </button>
              
              <button
                className={`nav-item ${builderState.activeSection === 'accessibility' ? 'active' : ''}`}
                onClick={() => setBuilderState(prev => ({ ...prev, activeSection: 'accessibility' }))}
              >
                <span className="nav-icon">♿</span>
                Accessibility
              </button>
            </nav>

            {/* Validation Panel */}
            <div className="validation-panel">
              <h3>Validation</h3>
              
              <div className={`validation-status ${validation.isValid ? 'valid' : 'invalid'}`}>
                {validation.isValid ? '✅ Valid Theme' : '❌ Invalid Theme'}
              </div>
              
              {validation.errors.length > 0 && (
                <div className="validation-errors">
                  <h4>Errors:</h4>
                  <ul>
                    {validation.errors.map((error, index) => (
                      <li key={index} className="error">{error}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {validation.warnings.length > 0 && (
                <div className="validation-warnings">
                  <h4>Warnings:</h4>
                  <ul>
                    {validation.warnings.map((warning, index) => (
                      <li key={index} className="warning">{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {validation.accessibilityIssues.length > 0 && (
                <div className="validation-accessibility">
                  <h4>Accessibility Issues:</h4>
                  <ul>
                    {validation.accessibilityIssues.map((issue, index) => (
                      <li key={index} className="accessibility-issue">{issue}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          <div className="theme-builder-main">
            {builderState.activeSection === 'colors' && (
              <div className="colors-section">
                <h3>Color Palette</h3>
                
                {colorGroups.map(group => (
                  <div key={group.name} className="color-group">
                    <h4>{group.name}</h4>
                    
                    <div className="color-grid">
                      {group.colors.map(color => (
                        <div key={color.key} className="color-item">
                          <label>{color.label}</label>
                          <ColorPicker
                            value={color.value}
                            onChange={(value) => updateColor(color.key, value)}
                            onGenerateVariations={(value) => generateColorVariations(value, color.key)}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {builderState.activeSection === 'typography' && (
              <Typography
                typography={builderState.modifiedTheme.typography}
                onChange={(typography) => updateThemeProperty('typography', typography)}
              />
            )}

            {builderState.activeSection === 'spacing' && (
              <div className="spacing-section">
                <h3>Spacing & Layout</h3>
                <div className="spacing-controls">
                  {Object.entries(builderState.modifiedTheme.spacing).map(([key, value]) => (
                    <div key={key} className="spacing-item">
                      <label>{key}</label>
                      <input
                        type="text"
                        value={value}
                        onChange={(e) => updateThemeProperty('spacing', {
                          ...builderState.modifiedTheme.spacing,
                          [key]: e.target.value
                        })}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {builderState.activeSection === 'monaco' && (
              <MonacoThemeEditor
                monacoTheme={builderState.modifiedTheme.monaco}
                onChange={(monaco) => updateThemeProperty('monaco', monaco)}
              />
            )}

            {builderState.activeSection === 'terminal' && (
              <TerminalThemeEditor
                terminalTheme={builderState.modifiedTheme.terminal}
                onChange={(terminal) => updateThemeProperty('terminal', terminal)}
              />
            )}

            {builderState.activeSection === 'accessibility' && (
              <AccessibilityPanel
                accessibility={builderState.modifiedTheme.accessibility}
                onChange={(accessibility) => updateThemeProperty('accessibility', accessibility)}
                themeColors={builderState.modifiedTheme.colors}
              />
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        .theme-builder-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          z-index: var(--z-modal);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: var(--spacing-lg);
        }

        .theme-builder {
          background: var(--color-background);
          border-radius: var(--radius-xl);
          box-shadow: var(--shadow-2xl);
          width: 100%;
          max-width: 1400px;
          max-height: 90vh;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .theme-builder-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: var(--spacing-lg);
          border-bottom: 1px solid var(--color-border);
        }

        .theme-builder-title h2 {
          margin: 0;
          color: var(--color-text-primary);
        }

        .theme-builder-title p {
          margin: 0;
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
        }

        .theme-builder-actions {
          display: flex;
          gap: var(--spacing-sm);
        }

        .theme-builder-content {
          display: flex;
          flex: 1;
          overflow: hidden;
        }

        .theme-builder-sidebar {
          width: 300px;
          background: var(--color-background-secondary);
          border-right: 1px solid var(--color-border);
          overflow-y: auto;
        }

        .theme-builder-nav {
          padding: var(--spacing-md);
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          width: 100%;
          padding: var(--spacing-sm) var(--spacing-md);
          border: none;
          background: none;
          color: var(--color-text-secondary);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all var(--transition-fast);
          font-size: var(--font-size-sm);
          margin-bottom: var(--spacing-xs);
        }

        .nav-item:hover {
          background: var(--color-background-tertiary);
          color: var(--color-text-primary);
        }

        .nav-item.active {
          background: var(--color-primary);
          color: white;
        }

        .nav-icon {
          font-size: var(--font-size-base);
        }

        .validation-panel {
          padding: var(--spacing-md);
          border-top: 1px solid var(--color-border);
        }

        .validation-panel h3 {
          margin: 0 0 var(--spacing-sm) 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .validation-status {
          padding: var(--spacing-sm);
          border-radius: var(--radius-md);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          margin-bottom: var(--spacing-sm);
        }

        .validation-status.valid {
          background: var(--color-success-light);
          color: var(--color-success-dark);
        }

        .validation-status.invalid {
          background: var(--color-error-light);
          color: var(--color-error-dark);
        }

        .validation-errors,
        .validation-warnings,
        .validation-accessibility {
          margin-bottom: var(--spacing-sm);
        }

        .validation-errors h4,
        .validation-warnings h4,
        .validation-accessibility h4 {
          font-size: var(--font-size-xs);
          margin: 0 0 var(--spacing-xs) 0;
          text-transform: uppercase;
        }

        .validation-errors ul,
        .validation-warnings ul,
        .validation-accessibility ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .validation-errors li,
        .validation-warnings li,
        .validation-accessibility li {
          font-size: var(--font-size-xs);
          padding: var(--spacing-xs);
          border-radius: var(--radius-sm);
          margin-bottom: var(--spacing-xs);
        }

        .error {
          background: var(--color-error-light);
          color: var(--color-error-dark);
        }

        .warning {
          background: var(--color-warning-light);
          color: var(--color-warning-dark);
        }

        .accessibility-issue {
          background: var(--color-info-light);
          color: var(--color-info-dark);
        }

        .theme-builder-main {
          flex: 1;
          padding: var(--spacing-lg);
          overflow-y: auto;
        }

        .colors-section h3 {
          margin: 0 0 var(--spacing-lg) 0;
          color: var(--color-text-primary);
        }

        .color-group {
          margin-bottom: var(--spacing-xl);
        }

        .color-group h4 {
          margin: 0 0 var(--spacing-md) 0;
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .color-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: var(--spacing-md);
        }

        .color-item {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
        }

        .color-item label {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          font-weight: var(--font-weight-medium);
        }

        .spacing-section h3 {
          margin: 0 0 var(--spacing-lg) 0;
          color: var(--color-text-primary);
        }

        .spacing-controls {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: var(--spacing-md);
        }

        .spacing-item {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
        }

        .spacing-item label {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          font-weight: var(--font-weight-medium);
        }

        .spacing-item input {
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background);
          color: var(--color-text-primary);
          font-family: var(--font-family-mono);
          font-size: var(--font-size-sm);
        }
      `}</style>
    </div>
  )
}

// Helper functions
function hexToRgb(hex: string): [number, number, number] | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16)
  ] : null
}

function rgbToHex(r: number, g: number, b: number): string {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
}