// Typography Component - Font and Text Configuration
// Provides typography customization interface for theme builder

import React, { useState, useCallback } from 'react'
import { Typography as TypographyType } from '../types/theme'

interface TypographyProps {
  typography: TypographyType
  onChange: (typography: TypographyType) => void
}

const fontFamilyOptions = [
  { value: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', label: 'Inter (Recommended)' },
  { value: '"Roboto", "Helvetica Neue", Arial, sans-serif', label: 'Roboto' },
  { value: '"Poppins", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif', label: 'Poppins' },
  { value: '"Nunito", "Helvetica Neue", Arial, sans-serif', label: 'Nunito' },
  { value: '"Open Sans", "Helvetica Neue", Arial, sans-serif', label: 'Open Sans' },
  { value: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', label: 'System UI' }
]

const monoFontOptions = [
  { value: '"JetBrains Mono", "Fira Code", Monaco, Consolas, monospace', label: 'JetBrains Mono (Recommended)' },
  { value: '"Fira Code", Monaco, Consolas, "Ubuntu Mono", monospace', label: 'Fira Code' },
  { value: '"Source Code Pro", Monaco, Consolas, "Ubuntu Mono", monospace', label: 'Source Code Pro' },
  { value: '"Cascadia Code", Monaco, Consolas, "Ubuntu Mono", monospace', label: 'Cascadia Code' },
  { value: '"SF Mono", Monaco, Consolas, "Ubuntu Mono", monospace', label: 'SF Mono' },
  { value: 'Monaco, Consolas, "Ubuntu Mono", monospace', label: 'Monaco' }
]

const serifFontOptions = [
  { value: '"Merriweather", Georgia, serif', label: 'Merriweather (Recommended)' },
  { value: '"Playfair Display", Georgia, serif', label: 'Playfair Display' },
  { value: '"Crimson Text", Georgia, serif', label: 'Crimson Text' },
  { value: 'Georgia, "Times New Roman", serif', label: 'Georgia' },
  { value: '"Times New Roman", Times, serif', label: 'Times New Roman' }
]

export const Typography: React.FC<TypographyProps> = ({
  typography,
  onChange
}) => {
  const [activeSection, setActiveSection] = useState<'fonts' | 'sizes' | 'weights' | 'spacing'>('fonts')

  const updateFontFamily = useCallback((key: keyof Pick<TypographyType, 'fontFamily' | 'fontFamilyMono' | 'fontFamilySerif'>, value: string) => {
    onChange({
      ...typography,
      [key]: value
    })
  }, [typography, onChange])

  const updateFontSize = useCallback((key: keyof TypographyType['fontSize'], value: string) => {
    onChange({
      ...typography,
      fontSize: {
        ...typography.fontSize,
        [key]: value
      }
    })
  }, [typography, onChange])

  const updateFontWeight = useCallback((key: keyof TypographyType['fontWeight'], value: number) => {
    onChange({
      ...typography,
      fontWeight: {
        ...typography.fontWeight,
        [key]: value
      }
    })
  }, [typography, onChange])

  const updateLineHeight = useCallback((key: keyof TypographyType['lineHeight'], value: number) => {
    onChange({
      ...typography,
      lineHeight: {
        ...typography.lineHeight,
        [key]: value
      }
    })
  }, [typography, onChange])

  const updateLetterSpacing = useCallback((key: keyof TypographyType['letterSpacing'], value: string) => {
    onChange({
      ...typography,
      letterSpacing: {
        ...typography.letterSpacing,
        [key]: value
      }
    })
  }, [typography, onChange])

  return (
    <div className="typography-editor">
      <h3>Typography Configuration</h3>
      
      <div className="typography-nav">
        <button
          className={`nav-btn ${activeSection === 'fonts' ? 'active' : ''}`}
          onClick={() => setActiveSection('fonts')}
        >
          Font Families
        </button>
        <button
          className={`nav-btn ${activeSection === 'sizes' ? 'active' : ''}`}
          onClick={() => setActiveSection('sizes')}
        >
          Font Sizes
        </button>
        <button
          className={`nav-btn ${activeSection === 'weights' ? 'active' : ''}`}
          onClick={() => setActiveSection('weights')}
        >
          Font Weights
        </button>
        <button
          className={`nav-btn ${activeSection === 'spacing' ? 'active' : ''}`}
          onClick={() => setActiveSection('spacing')}
        >
          Spacing
        </button>
      </div>

      <div className="typography-content">
        {activeSection === 'fonts' && (
          <div className="font-families-section">
            <div className="font-group">
              <h4>Primary Font (UI)</h4>
              <select
                value={typography.fontFamily}
                onChange={(e) => updateFontFamily('fontFamily', e.target.value)}
                className="font-select"
              >
                {fontFamilyOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <div 
                className="font-preview"
                style={{ fontFamily: typography.fontFamily }}
              >
                The quick brown fox jumps over the lazy dog
              </div>
            </div>

            <div className="font-group">
              <h4>Monospace Font (Code)</h4>
              <select
                value={typography.fontFamilyMono}
                onChange={(e) => updateFontFamily('fontFamilyMono', e.target.value)}
                className="font-select"
              >
                {monoFontOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <div 
                className="font-preview code"
                style={{ fontFamily: typography.fontFamilyMono }}
              >
                const greeting = "Hello, World!";
              </div>
            </div>

            <div className="font-group">
              <h4>Serif Font (Headings)</h4>
              <select
                value={typography.fontFamilySerif}
                onChange={(e) => updateFontFamily('fontFamilySerif', e.target.value)}
                className="font-select"
              >
                {serifFontOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <div 
                className="font-preview serif"
                style={{ fontFamily: typography.fontFamilySerif }}
              >
                Elegant Typography for Headlines
              </div>
            </div>
          </div>
        )}

        {activeSection === 'sizes' && (
          <div className="font-sizes-section">
            <h4>Font Size Scale</h4>
            <div className="size-grid">
              {Object.entries(typography.fontSize).map(([key, value]) => (
                <div key={key} className="size-item">
                  <label>{key}</label>
                  <input
                    type="text"
                    value={value}
                    onChange={(e) => updateFontSize(key as keyof TypographyType['fontSize'], e.target.value)}
                    className="size-input"
                  />
                  <div 
                    className="size-preview"
                    style={{ fontSize: value }}
                  >
                    Sample Text
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === 'weights' && (
          <div className="font-weights-section">
            <h4>Font Weight Scale</h4>
            <div className="weight-grid">
              {Object.entries(typography.fontWeight).map(([key, value]) => (
                <div key={key} className="weight-item">
                  <label>{key}</label>
                  <input
                    type="number"
                    min="100"
                    max="900"
                    step="100"
                    value={value}
                    onChange={(e) => updateFontWeight(key as keyof TypographyType['fontWeight'], Number(e.target.value))}
                    className="weight-input"
                  />
                  <div 
                    className="weight-preview"
                    style={{ fontWeight: value }}
                  >
                    Font Weight {value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === 'spacing' && (
          <div className="spacing-section">
            <div className="spacing-group">
              <h4>Line Heights</h4>
              <div className="spacing-grid">
                {Object.entries(typography.lineHeight).map(([key, value]) => (
                  <div key={key} className="spacing-item">
                    <label>{key}</label>
                    <input
                      type="number"
                      min="0.8"
                      max="3"
                      step="0.125"
                      value={value}
                      onChange={(e) => updateLineHeight(key as keyof TypographyType['lineHeight'], Number(e.target.value))}
                      className="spacing-input"
                    />
                    <div 
                      className="spacing-preview"
                      style={{ lineHeight: value }}
                    >
                      Line height affects the vertical spacing between lines of text. This example shows how different line heights impact readability.
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="spacing-group">
              <h4>Letter Spacing</h4>
              <div className="spacing-grid">
                {Object.entries(typography.letterSpacing).map(([key, value]) => (
                  <div key={key} className="spacing-item">
                    <label>{key}</label>
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => updateLetterSpacing(key as keyof TypographyType['letterSpacing'], e.target.value)}
                      className="spacing-input"
                    />
                    <div 
                      className="spacing-preview"
                      style={{ letterSpacing: value }}
                    >
                      Letter spacing example
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .typography-editor {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }

        .typography-editor h3 {
          margin: 0;
          color: var(--color-text-primary);
        }

        .typography-nav {
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

        .typography-content {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }

        .font-group {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
          padding: var(--spacing-md);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
        }

        .font-group h4 {
          margin: 0;
          color: var(--color-text-primary);
          font-size: var(--font-size-sm);
        }

        .font-select {
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background);
          color: var(--color-text-primary);
          font-size: var(--font-size-sm);
        }

        .font-preview {
          padding: var(--spacing-md);
          background: var(--color-background-secondary);
          border-radius: var(--radius-md);
          color: var(--color-text-primary);
          font-size: var(--font-size-base);
        }

        .font-preview.code {
          font-family: var(--font-family-mono);
          background: var(--color-background-tertiary);
        }

        .font-preview.serif {
          font-size: var(--font-size-lg);
          font-weight: var(--font-weight-semibold);
        }

        .size-grid,
        .weight-grid,
        .spacing-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: var(--spacing-md);
        }

        .size-item,
        .weight-item,
        .spacing-item {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
        }

        .size-item label,
        .weight-item label,
        .spacing-item label {
          font-size: var(--font-size-xs);
          color: var(--color-text-secondary);
          font-weight: var(--font-weight-medium);
          text-transform: capitalize;
        }

        .size-input,
        .weight-input,
        .spacing-input {
          padding: var(--spacing-xs) var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background: var(--color-background);
          color: var(--color-text-primary);
          font-family: var(--font-family-mono);
          font-size: var(--font-size-xs);
        }

        .size-preview,
        .weight-preview {
          padding: var(--spacing-xs);
          color: var(--color-text-primary);
          background: var(--color-background-secondary);
          border-radius: var(--radius-sm);
          text-align: center;
        }

        .spacing-preview {
          padding: var(--spacing-sm);
          color: var(--color-text-primary);
          background: var(--color-background-secondary);
          border-radius: var(--radius-sm);
          font-size: var(--font-size-sm);
          line-height: 1.4;
        }

        .spacing-group {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-md);
        }

        .spacing-group h4 {
          margin: 0;
          color: var(--color-text-primary);
          font-size: var(--font-size-base);
        }
      `}</style>
    </div>
  )
}