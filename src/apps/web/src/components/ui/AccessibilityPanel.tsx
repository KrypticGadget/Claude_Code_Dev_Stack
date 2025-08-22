// Accessibility Panel - Comprehensive Accessibility Configuration
// Provides interface for configuring accessibility options and testing theme compliance

import React, { useState, useCallback, useMemo } from 'react'
import { AccessibilityOptions, ColorPalette } from '../types/theme'
import { ThemeValidator } from '../utils/theme-validator'

interface AccessibilityPanelProps {
  accessibility: AccessibilityOptions
  onChange: (accessibility: AccessibilityOptions) => void
  themeColors: ColorPalette
}

const colorBlindModeOptions = [
  { value: 'none', label: 'No Color Blind Support', description: 'Standard colors for typical vision' },
  { value: 'protanopia', label: 'Protanopia Support', description: 'Red-blind friendly colors (1% of males)' },
  { value: 'deuteranopia', label: 'Deuteranopia Support', description: 'Green-blind friendly colors (1% of males)' },
  { value: 'tritanopia', label: 'Tritanopia Support', description: 'Blue-blind friendly colors (0.003% of population)' }
]

const accessibilityTests = [
  {
    name: 'Text Contrast',
    description: 'Tests if text colors meet WCAG contrast requirements',
    requirement: 'WCAG 2.1 AA: 4.5:1 minimum contrast ratio'
  },
  {
    name: 'Large Text Contrast',
    description: 'Tests contrast for large text (18pt+ or 14pt+ bold)',
    requirement: 'WCAG 2.1 AA: 3:1 minimum contrast ratio'
  },
  {
    name: 'Interactive Elements',
    description: 'Tests contrast for buttons, links, and form controls',
    requirement: 'WCAG 2.1 AA: 3:1 minimum for UI components'
  },
  {
    name: 'Color Differentiation',
    description: 'Ensures information is not conveyed by color alone',
    requirement: 'WCAG 2.1 A: No reliance on color alone'
  },
  {
    name: 'Focus Indicators',
    description: 'Tests visibility of keyboard focus indicators',
    requirement: 'WCAG 2.1 AA: 3:1 contrast with adjacent colors'
  }
]

export const AccessibilityPanel: React.FC<AccessibilityPanelProps> = ({
  accessibility,
  onChange,
  themeColors
}) => {
  const [activeSection, setActiveSection] = useState<'settings' | 'testing' | 'preview'>('settings')
  const validator = useMemo(() => new ThemeValidator(), [])

  const updateAccessibilityOption = useCallback(<K extends keyof AccessibilityOptions>(
    key: K,
    value: AccessibilityOptions[K]
  ) => {
    onChange({
      ...accessibility,
      [key]: value
    })
  }, [accessibility, onChange])

  // Calculate contrast ratios for testing
  const contrastTests = useMemo(() => {
    const calculateContrast = (bg: string, fg: string): number => {
      const getLuminance = (color: string): number => {
        const rgb = hexToRgb(color)
        if (!rgb) return 0

        const [r, g, b] = rgb.map(c => {
          const normalized = c / 255
          return normalized <= 0.03928
            ? normalized / 12.92
            : Math.pow((normalized + 0.055) / 1.055, 2.4)
        })

        return 0.2126 * r + 0.7152 * g + 0.0722 * b
      }

      const bgLuminance = getLuminance(bg)
      const fgLuminance = getLuminance(fg)
      
      const lighter = Math.max(bgLuminance, fgLuminance)
      const darker = Math.min(bgLuminance, fgLuminance)
      
      return (lighter + 0.05) / (darker + 0.05)
    }

    return [
      {
        name: 'Primary Text on Background',
        background: themeColors.background,
        foreground: themeColors.textPrimary,
        contrast: calculateContrast(themeColors.background, themeColors.textPrimary),
        requirement: 4.5,
        type: 'text'
      },
      {
        name: 'Secondary Text on Background',
        background: themeColors.background,
        foreground: themeColors.textSecondary,
        contrast: calculateContrast(themeColors.background, themeColors.textSecondary),
        requirement: 4.5,
        type: 'text'
      },
      {
        name: 'Primary Button',
        background: themeColors.primary,
        foreground: themeColors.textInverse,
        contrast: calculateContrast(themeColors.primary, themeColors.textInverse),
        requirement: 4.5,
        type: 'button'
      },
      {
        name: 'Success Color on Background',
        background: themeColors.background,
        foreground: themeColors.success,
        contrast: calculateContrast(themeColors.background, themeColors.success),
        requirement: 3.0,
        type: 'ui'
      },
      {
        name: 'Error Color on Background',
        background: themeColors.background,
        foreground: themeColors.error,
        contrast: calculateContrast(themeColors.background, themeColors.error),
        requirement: 3.0,
        type: 'ui'
      },
      {
        name: 'Warning Color on Background',
        background: themeColors.background,
        foreground: themeColors.warning,
        contrast: calculateContrast(themeColors.background, themeColors.warning),
        requirement: 3.0,
        type: 'ui'
      }
    ]
  }, [themeColors])

  const overallAccessibilityScore = useMemo(() => {
    const passingTests = contrastTests.filter(test => test.contrast >= test.requirement).length
    return Math.round((passingTests / contrastTests.length) * 100)
  }, [contrastTests])

  return (
    <div className="accessibility-panel">
      <h3>Accessibility Configuration</h3>
      
      <div className="accessibility-nav">
        <button
          className={`nav-btn ${activeSection === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveSection('settings')}
        >
          Settings
        </button>
        <button
          className={`nav-btn ${activeSection === 'testing' ? 'active' : ''}`}
          onClick={() => setActiveSection('testing')}
        >
          Testing
        </button>
        <button
          className={`nav-btn ${activeSection === 'preview' ? 'active' : ''}`}
          onClick={() => setActiveSection('preview')}
        >
          Preview
        </button>
      </div>

      <div className="accessibility-content">
        {activeSection === 'settings' && (
          <div className="settings-section">
            <div className="setting-group">
              <h4>Visual Accessibility</h4>
              
              <div className="setting-item">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={accessibility.highContrast}
                    onChange={(e) => updateAccessibilityOption('highContrast', e.target.checked)}
                  />
                  <span>High Contrast Mode</span>
                </label>
                <p className="setting-description">
                  Increases contrast ratios for enhanced visibility. Forces maximum contrast
                  between text and backgrounds for users with low vision.
                </p>
              </div>

              <div className="setting-item">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={accessibility.largeText}
                    onChange={(e) => updateAccessibilityOption('largeText', e.target.checked)}
                  />
                  <span>Large Text Mode</span>
                </label>
                <p className="setting-description">
                  Increases font sizes and ensures minimum 44px touch targets for better
                  usability on mobile devices and for users with motor impairments.
                </p>
              </div>

              <div className="setting-item">
                <label className="setting-label">Color Blind Support</label>
                <div className="colorblind-options">
                  {colorBlindModeOptions.map(option => (
                    <label key={option.value} className="radio-label">
                      <input
                        type="radio"
                        name="colorBlindMode"
                        value={option.value}
                        checked={accessibility.colorBlindMode === option.value}
                        onChange={(e) => updateAccessibilityOption('colorBlindMode', e.target.value as any)}
                      />
                      <div className="radio-content">
                        <span className="radio-title">{option.label}</span>
                        <span className="radio-description">{option.description}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="setting-group">
              <h4>Motion & Animation</h4>
              
              <div className="setting-item">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={accessibility.reducedMotion}
                    onChange={(e) => updateAccessibilityOption('reducedMotion', e.target.checked)}
                  />
                  <span>Reduced Motion</span>
                </label>
                <p className="setting-description">
                  Minimizes or disables animations and transitions for users with vestibular
                  disorders or those who find motion distracting.
                </p>
              </div>
            </div>

            <div className="setting-group">
              <h4>Interaction & Navigation</h4>
              
              <div className="setting-item">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={accessibility.focusVisible}
                    onChange={(e) => updateAccessibilityOption('focusVisible', e.target.checked)}
                  />
                  <span>Enhanced Focus Indicators</span>
                </label>
                <p className="setting-description">
                  Shows prominent focus outlines for keyboard navigation. Essential for
                  users who navigate without a mouse.
                </p>
              </div>

              <div className="setting-item">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={accessibility.screenReaderOptimized}
                    onChange={(e) => updateAccessibilityOption('screenReaderOptimized', e.target.checked)}
                  />
                  <span>Screen Reader Optimizations</span>
                </label>
                <p className="setting-description">
                  Enhances compatibility with screen readers and other assistive technologies
                  by adding additional semantic markup and ARIA labels.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeSection === 'testing' && (
          <div className="testing-section">
            <div className="accessibility-score">
              <h4>Accessibility Score</h4>
              <div className={`score ${overallAccessibilityScore >= 80 ? 'good' : overallAccessibilityScore >= 60 ? 'warning' : 'poor'}`}>
                {overallAccessibilityScore}%
              </div>
              <p>
                {overallAccessibilityScore >= 80 
                  ? 'Excellent accessibility compliance'
                  : overallAccessibilityScore >= 60
                  ? 'Good accessibility with room for improvement'
                  : 'Accessibility improvements needed'
                }
              </p>
            </div>

            <div className="contrast-tests">
              <h4>Contrast Tests</h4>
              <div className="test-grid">
                {contrastTests.map((test, index) => (
                  <div key={index} className={`test-item ${test.contrast >= test.requirement ? 'pass' : 'fail'}`}>
                    <div className="test-header">
                      <span className="test-name">{test.name}</span>
                      <span className={`test-result ${test.contrast >= test.requirement ? 'pass' : 'fail'}`}>
                        {test.contrast >= test.requirement ? 'PASS' : 'FAIL'}
                      </span>
                    </div>
                    
                    <div className="test-details">
                      <div className="contrast-ratio">
                        <span>Contrast: {test.contrast.toFixed(2)}:1</span>
                        <span>Required: {test.requirement}:1</span>
                      </div>
                      
                      <div className="color-preview">
                        <div 
                          className="color-sample"
                          style={{ 
                            backgroundColor: test.background,
                            color: test.foreground,
                            border: `1px solid ${test.foreground}`
                          }}
                        >
                          Sample Text
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="accessibility-guidelines">
              <h4>Accessibility Guidelines</h4>
              <div className="guidelines-grid">
                {accessibilityTests.map((guideline, index) => (
                  <div key={index} className="guideline-item">
                    <h5>{guideline.name}</h5>
                    <p>{guideline.description}</p>
                    <div className="requirement">
                      <strong>Requirement:</strong> {guideline.requirement}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeSection === 'preview' && (
          <div className="preview-section">
            <h4>Accessibility Preview</h4>
            
            <div className="preview-container">
              <div className={`preview-ui ${accessibility.highContrast ? 'high-contrast' : ''} ${accessibility.largeText ? 'large-text' : ''}`}>
                <div className="preview-header">
                  <h2>Sample Interface</h2>
                  <p>This preview shows how your theme appears with accessibility settings applied.</p>
                </div>

                <div className="preview-content">
                  <div className="form-section">
                    <h3>Form Elements</h3>
                    <div className="form-group">
                      <label htmlFor="sample-input">Sample Input</label>
                      <input 
                        id="sample-input" 
                        type="text" 
                        placeholder="Enter text here..."
                        className={accessibility.focusVisible ? 'enhanced-focus' : ''}
                      />
                    </div>
                    
                    <div className="button-group">
                      <button className="btn btn-primary">Primary Action</button>
                      <button className="btn btn-secondary">Secondary Action</button>
                      <button className="btn btn-success">Success Action</button>
                      <button className="btn btn-error">Danger Action</button>
                    </div>
                  </div>

                  <div className="status-section">
                    <h3>Status Messages</h3>
                    <div className="status-success">
                      <span className="status-icon">✓</span>
                      Operation completed successfully
                    </div>
                    <div className="status-warning">
                      <span className="status-icon">⚠</span>
                      Please review your input
                    </div>
                    <div className="status-error">
                      <span className="status-icon">✗</span>
                      An error occurred
                    </div>
                    <div className="status-info">
                      <span className="status-icon">ℹ</span>
                      Additional information available
                    </div>
                  </div>

                  <div className="navigation-section">
                    <h3>Navigation Elements</h3>
                    <nav className="sample-nav">
                      <a href="#" className={accessibility.focusVisible ? 'enhanced-focus' : ''}>Home</a>
                      <a href="#" className={accessibility.focusVisible ? 'enhanced-focus' : ''}>About</a>
                      <a href="#" className={accessibility.focusVisible ? 'enhanced-focus' : ''}>Services</a>
                      <a href="#" className={accessibility.focusVisible ? 'enhanced-focus' : ''}>Contact</a>
                    </nav>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .accessibility-panel {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }

        .accessibility-panel h3 {
          margin: 0;
          color: var(--color-text-primary);
        }

        .accessibility-nav {
          display: flex;
          gap: var(--spacing-xs);
          border-bottom: 1px solid var(--color-border);
          padding-bottom: var(--spacing-sm);
        }

        .nav-btn {
          padding: var(--spacing-sm) var(--spacing-md);
          border: none;
          background: none;
          color: var(--color-text-secondary);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all var(--transition-fast);
          font-size: var(--font-size-sm);
        }

        .nav-btn:hover {
          background: var(--color-background-tertiary);
          color: var(--color-text-primary);
        }

        .nav-btn.active {
          background: var(--color-primary);
          color: white;
        }

        .setting-group {
          margin-bottom: var(--spacing-xl);
          padding: var(--spacing-lg);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
        }

        .setting-group h4 {
          margin: 0 0 var(--spacing-md) 0;
          color: var(--color-text-primary);
          font-size: var(--font-size-base);
        }

        .setting-item {
          margin-bottom: var(--spacing-lg);
        }

        .setting-item:last-child {
          margin-bottom: 0;
        }

        .setting-label {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
          cursor: pointer;
          margin-bottom: var(--spacing-xs);
        }

        .setting-description {
          margin: 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          line-height: var(--line-height-relaxed);
        }

        .colorblind-options {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
          margin-top: var(--spacing-sm);
        }

        .radio-label {
          display: flex;
          align-items: flex-start;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all var(--transition-fast);
        }

        .radio-label:hover {
          background: var(--color-background-secondary);
        }

        .radio-content {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
        }

        .radio-title {
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
        }

        .radio-description {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .accessibility-score {
          text-align: center;
          padding: var(--spacing-lg);
          background: var(--color-background-secondary);
          border-radius: var(--radius-lg);
          margin-bottom: var(--spacing-xl);
        }

        .accessibility-score h4 {
          margin: 0 0 var(--spacing-md) 0;
          color: var(--color-text-primary);
        }

        .score {
          font-size: var(--font-size-4xl);
          font-weight: var(--font-weight-bold);
          margin-bottom: var(--spacing-sm);
        }

        .score.good { color: var(--color-success); }
        .score.warning { color: var(--color-warning); }
        .score.poor { color: var(--color-error); }

        .test-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: var(--spacing-md);
        }

        .test-item {
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          border: 1px solid var(--color-border);
        }

        .test-item.pass {
          background: var(--color-success-light);
          border-color: var(--color-success);
        }

        .test-item.fail {
          background: var(--color-error-light);
          border-color: var(--color-error);
        }

        .test-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-sm);
        }

        .test-name {
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
        }

        .test-result {
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-bold);
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-sm);
        }

        .test-result.pass {
          background: var(--color-success);
          color: white;
        }

        .test-result.fail {
          background: var(--color-error);
          color: white;
        }

        .contrast-ratio {
          display: flex;
          justify-content: space-between;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          margin-bottom: var(--spacing-sm);
        }

        .color-sample {
          padding: var(--spacing-sm);
          text-align: center;
          border-radius: var(--radius-sm);
          font-weight: var(--font-weight-medium);
        }

        .guidelines-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: var(--spacing-md);
        }

        .guideline-item {
          padding: var(--spacing-md);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background-secondary);
        }

        .guideline-item h5 {
          margin: 0 0 var(--spacing-sm) 0;
          color: var(--color-text-primary);
        }

        .guideline-item p {
          margin: 0 0 var(--spacing-sm) 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .requirement {
          font-size: var(--font-size-xs);
          color: var(--color-info);
        }

        .preview-container {
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          overflow: hidden;
        }

        .preview-ui {
          padding: var(--spacing-lg);
          background: var(--color-background);
        }

        .preview-ui.high-contrast {
          background: #000000;
          color: #ffffff;
        }

        .preview-ui.large-text {
          font-size: 1.25em;
        }

        .preview-ui.large-text .btn {
          min-height: 52px;
          font-size: 1.125em;
        }

        .preview-header h2 {
          color: var(--color-text-primary);
        }

        .preview-content {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: var(--spacing-xl);
        }

        .form-section,
        .status-section,
        .navigation-section {
          padding: var(--spacing-md);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background-secondary);
        }

        .form-group {
          margin-bottom: var(--spacing-md);
        }

        .form-group label {
          display: block;
          margin-bottom: var(--spacing-xs);
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
        }

        .button-group {
          display: flex;
          gap: var(--spacing-sm);
          flex-wrap: wrap;
        }

        .status-success { color: var(--color-success); }
        .status-warning { color: var(--color-warning); }
        .status-error { color: var(--color-error); }
        .status-info { color: var(--color-info); }

        .status-section > div {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          margin-bottom: var(--spacing-sm);
          padding: var(--spacing-sm);
          border-radius: var(--radius-sm);
          background: var(--color-background);
        }

        .sample-nav {
          display: flex;
          gap: var(--spacing-md);
          flex-wrap: wrap;
        }

        .sample-nav a {
          padding: var(--spacing-sm) var(--spacing-md);
          color: var(--color-primary);
          text-decoration: none;
          border-radius: var(--radius-md);
          transition: all var(--transition-fast);
        }

        .sample-nav a:hover {
          background: var(--color-background);
        }

        .enhanced-focus:focus {
          outline: 3px solid var(--color-primary) !important;
          outline-offset: 2px !important;
        }
      `}</style>
    </div>
  )
}

// Helper function
function hexToRgb(hex: string): [number, number, number] | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16)
  ] : null
}