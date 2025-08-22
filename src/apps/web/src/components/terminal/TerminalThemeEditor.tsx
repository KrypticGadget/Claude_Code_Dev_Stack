// Terminal Theme Editor - Terminal Color Scheme Customization
// Provides interface for customizing terminal color schemes with live preview

import React, { useState, useCallback } from 'react'
import { TerminalTheme } from '../types/theme'
import { ColorPicker } from './ColorPicker'

interface TerminalThemeEditorProps {
  terminalTheme: TerminalTheme
  onChange: (terminalTheme: TerminalTheme) => void
}

const colorGroups = [
  {
    name: 'Basic Colors',
    colors: [
      { key: 'background', label: 'Background', description: 'Terminal background color' },
      { key: 'foreground', label: 'Foreground', description: 'Default text color' },
      { key: 'cursor', label: 'Cursor', description: 'Cursor color' },
      { key: 'cursorAccent', label: 'Cursor Accent', description: 'Cursor accent/outline color' },
      { key: 'selection', label: 'Selection', description: 'Selected text background' }
    ]
  },
  {
    name: 'ANSI Colors',
    colors: [
      { key: 'black', label: 'Black', description: 'ANSI color 0' },
      { key: 'red', label: 'Red', description: 'ANSI color 1' },
      { key: 'green', label: 'Green', description: 'ANSI color 2' },
      { key: 'yellow', label: 'Yellow', description: 'ANSI color 3' },
      { key: 'blue', label: 'Blue', description: 'ANSI color 4' },
      { key: 'magenta', label: 'Magenta', description: 'ANSI color 5' },
      { key: 'cyan', label: 'Cyan', description: 'ANSI color 6' },
      { key: 'white', label: 'White', description: 'ANSI color 7' }
    ]
  },
  {
    name: 'Bright ANSI Colors',
    colors: [
      { key: 'brightBlack', label: 'Bright Black', description: 'ANSI color 8' },
      { key: 'brightRed', label: 'Bright Red', description: 'ANSI color 9' },
      { key: 'brightGreen', label: 'Bright Green', description: 'ANSI color 10' },
      { key: 'brightYellow', label: 'Bright Yellow', description: 'ANSI color 11' },
      { key: 'brightBlue', label: 'Bright Blue', description: 'ANSI color 12' },
      { key: 'brightMagenta', label: 'Bright Magenta', description: 'ANSI color 13' },
      { key: 'brightCyan', label: 'Bright Cyan', description: 'ANSI color 14' },
      { key: 'brightWhite', label: 'Bright White', description: 'ANSI color 15' }
    ]
  }
]

const terminalCommands = [
  { command: 'ls -la', description: 'List directory contents', colors: ['white', 'blue', 'green'] },
  { command: 'git status', description: 'Git repository status', colors: ['red', 'green', 'yellow'] },
  { command: 'npm install', description: 'Install dependencies', colors: ['cyan', 'yellow', 'green'] },
  { command: 'docker ps', description: 'List containers', colors: ['blue', 'magenta', 'white'] },
  { command: 'tail -f /var/log/nginx/error.log', description: 'Follow log file', colors: ['red', 'yellow'] },
  { command: 'grep -r "TODO" src/', description: 'Search for TODO comments', colors: ['yellow', 'white'] }
]

export const TerminalThemeEditor: React.FC<TerminalThemeEditorProps> = ({
  terminalTheme,
  onChange
}) => {
  const [activeSection, setActiveSection] = useState<'colors' | 'preview'>('colors')

  const updateColor = useCallback((key: keyof TerminalTheme, value: string) => {
    onChange({
      ...terminalTheme,
      [key]: value
    })
  }, [terminalTheme, onChange])

  const generateColorVariations = useCallback((baseColor: string, colorKey: keyof TerminalTheme) => {
    // Auto-generate bright version for ANSI colors
    if (colorKey.startsWith('bright')) return
    
    const brightKey = `bright${colorKey.charAt(0).toUpperCase() + colorKey.slice(1)}` as keyof TerminalTheme
    if (brightKey in terminalTheme) {
      // Generate a brighter version
      const rgb = hexToRgb(baseColor)
      if (rgb) {
        const [r, g, b] = rgb
        const brightR = Math.min(255, Math.round(r * 1.3))
        const brightG = Math.min(255, Math.round(g * 1.3))
        const brightB = Math.min(255, Math.round(b * 1.3))
        const brightColor = rgbToHex(brightR, brightG, brightB)
        
        updateColor(brightKey, brightColor)
      }
    }
  }, [terminalTheme, updateColor])

  const resetToClassicColors = useCallback(() => {
    const classicColors: TerminalTheme = {
      background: '#000000',
      foreground: '#ffffff',
      cursor: '#ffffff',
      cursorAccent: '#000000',
      selection: '#ffffff40',
      black: '#000000',
      red: '#cd0000',
      green: '#00cd00',
      yellow: '#cdcd00',
      blue: '#0000ee',
      magenta: '#cd00cd',
      cyan: '#00cdcd',
      white: '#e5e5e5',
      brightBlack: '#7f7f7f',
      brightRed: '#ff0000',
      brightGreen: '#00ff00',
      brightYellow: '#ffff00',
      brightBlue: '#5c5cff',
      brightMagenta: '#ff00ff',
      brightCyan: '#00ffff',
      brightWhite: '#ffffff'
    }
    onChange(classicColors)
  }, [onChange])

  const resetToSolarizedDark = useCallback(() => {
    const solarizedColors: TerminalTheme = {
      background: '#002b36',
      foreground: '#839496',
      cursor: '#93a1a1',
      cursorAccent: '#002b36',
      selection: '#073642',
      black: '#073642',
      red: '#dc322f',
      green: '#859900',
      yellow: '#b58900',
      blue: '#268bd2',
      magenta: '#d33682',
      cyan: '#2aa198',
      white: '#eee8d5',
      brightBlack: '#002b36',
      brightRed: '#cb4b16',
      brightGreen: '#586e75',
      brightYellow: '#657b83',
      brightBlue: '#839496',
      brightMagenta: '#6c71c4',
      brightCyan: '#93a1a1',
      brightWhite: '#fdf6e3'
    }
    onChange(solarizedColors)
  }, [onChange])

  return (
    <div className="terminal-theme-editor">
      <div className="terminal-header">
        <h3>Terminal Theme</h3>
        
        <div className="preset-actions">
          <button
            className="btn btn-sm btn-secondary"
            onClick={resetToClassicColors}
          >
            Classic Colors
          </button>
          <button
            className="btn btn-sm btn-secondary"
            onClick={resetToSolarizedDark}
          >
            Solarized Dark
          </button>
        </div>
      </div>

      <div className="terminal-nav">
        <button
          className={`nav-btn ${activeSection === 'colors' ? 'active' : ''}`}
          onClick={() => setActiveSection('colors')}
        >
          Colors
        </button>
        <button
          className={`nav-btn ${activeSection === 'preview' ? 'active' : ''}`}
          onClick={() => setActiveSection('preview')}
        >
          Preview
        </button>
      </div>

      <div className="terminal-content">
        {activeSection === 'colors' && (
          <div className="colors-section">
            {colorGroups.map(group => (
              <div key={group.name} className="color-group">
                <h4>{group.name}</h4>
                
                <div className="color-grid">
                  {group.colors.map(color => (
                    <div key={color.key} className="color-item">
                      <div className="color-header">
                        <label>{color.label}</label>
                        <span className="color-description">{color.description}</span>
                      </div>
                      
                      <div className="color-controls">
                        <ColorPicker
                          value={terminalTheme[color.key as keyof TerminalTheme]}
                          onChange={(value) => updateColor(color.key as keyof TerminalTheme, value)}
                          onGenerateVariations={group.name === 'ANSI Colors' ? 
                            (value) => generateColorVariations(value, color.key as keyof TerminalTheme) : 
                            undefined
                          }
                          showVariationButton={group.name === 'ANSI Colors'}
                          showAccessibilityInfo={false}
                        />
                        
                        <div 
                          className="color-sample"
                          style={{ 
                            backgroundColor: terminalTheme[color.key as keyof TerminalTheme],
                            border: `1px solid ${terminalTheme.foreground}`
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeSection === 'preview' && (
          <div className="preview-section">
            <h4>Terminal Preview</h4>
            
            <div 
              className="terminal-preview"
              style={{
                backgroundColor: terminalTheme.background,
                color: terminalTheme.foreground
              }}
            >
              <div className="terminal-header-bar">
                <div className="terminal-controls">
                  <div className="control-btn close" />
                  <div className="control-btn minimize" />
                  <div className="control-btn maximize" />
                </div>
                <div className="terminal-title">Terminal</div>
              </div>
              
              <div className="terminal-body">
                <div className="terminal-line">
                  <span style={{ color: terminalTheme.green }}>user@localhost</span>
                  <span style={{ color: terminalTheme.white }}>:</span>
                  <span style={{ color: terminalTheme.blue }}>~/project</span>
                  <span style={{ color: terminalTheme.white }}>$ </span>
                  <span 
                    className="cursor"
                    style={{ backgroundColor: terminalTheme.cursor }}
                  />
                </div>
                
                {terminalCommands.map((cmd, index) => (
                  <div key={index} className="command-example">
                    <div className="terminal-line">
                      <span style={{ color: terminalTheme.green }}>user@localhost</span>
                      <span style={{ color: terminalTheme.white }}>:</span>
                      <span style={{ color: terminalTheme.blue }}>~/project</span>
                      <span style={{ color: terminalTheme.white }}>$ {cmd.command}</span>
                    </div>
                    
                    <div className="command-output">
                      <div style={{ color: terminalTheme.brightBlack }}>
                        # {cmd.description}
                      </div>
                      {cmd.colors.map((colorName, i) => (
                        <div key={i} style={{ color: terminalTheme[colorName as keyof TerminalTheme] }}>
                          Sample output in {colorName} color
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
                
                <div className="ansi-color-test">
                  <div style={{ color: terminalTheme.brightBlack }}>
                    # ANSI Color Test
                  </div>
                  <div className="color-row">
                    <span style={{ color: terminalTheme.black }}>■ Black</span>
                    <span style={{ color: terminalTheme.red }}>■ Red</span>
                    <span style={{ color: terminalTheme.green }}>■ Green</span>
                    <span style={{ color: terminalTheme.yellow }}>■ Yellow</span>
                  </div>
                  <div className="color-row">
                    <span style={{ color: terminalTheme.blue }}>■ Blue</span>
                    <span style={{ color: terminalTheme.magenta }}>■ Magenta</span>
                    <span style={{ color: terminalTheme.cyan }}>■ Cyan</span>
                    <span style={{ color: terminalTheme.white }}>■ White</span>
                  </div>
                  <div className="color-row">
                    <span style={{ color: terminalTheme.brightBlack }}>■ Bright Black</span>
                    <span style={{ color: terminalTheme.brightRed }}>■ Bright Red</span>
                    <span style={{ color: terminalTheme.brightGreen }}>■ Bright Green</span>
                    <span style={{ color: terminalTheme.brightYellow }}>■ Bright Yellow</span>
                  </div>
                  <div className="color-row">
                    <span style={{ color: terminalTheme.brightBlue }}>■ Bright Blue</span>
                    <span style={{ color: terminalTheme.brightMagenta }}>■ Bright Magenta</span>
                    <span style={{ color: terminalTheme.brightCyan }}>■ Bright Cyan</span>
                    <span style={{ color: terminalTheme.brightWhite }}>■ Bright White</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .terminal-theme-editor {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }

        .terminal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .terminal-header h3 {
          margin: 0;
          color: var(--color-text-primary);
        }

        .preset-actions {
          display: flex;
          gap: var(--spacing-xs);
        }

        .terminal-nav {
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

        .color-group {
          margin-bottom: var(--spacing-xl);
        }

        .color-group h4 {
          margin: 0 0 var(--spacing-md) 0;
          color: var(--color-text-primary);
          font-size: var(--font-size-base);
        }

        .color-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: var(--spacing-md);
        }

        .color-item {
          padding: var(--spacing-md);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background-secondary);
        }

        .color-header {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
          margin-bottom: var(--spacing-sm);
        }

        .color-header label {
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
          font-size: var(--font-size-sm);
        }

        .color-description {
          font-size: var(--font-size-xs);
          color: var(--color-text-muted);
        }

        .color-controls {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
        }

        .color-sample {
          width: 32px;
          height: 32px;
          border-radius: var(--radius-sm);
          flex-shrink: 0;
        }

        .terminal-preview {
          border-radius: var(--radius-lg);
          overflow: hidden;
          font-family: var(--font-family-mono);
          font-size: var(--font-size-sm);
          box-shadow: var(--shadow-lg);
        }

        .terminal-header-bar {
          display: flex;
          align-items: center;
          padding: var(--spacing-sm) var(--spacing-md);
          background: rgba(255, 255, 255, 0.1);
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .terminal-controls {
          display: flex;
          gap: var(--spacing-xs);
          margin-right: var(--spacing-md);
        }

        .control-btn {
          width: 12px;
          height: 12px;
          border-radius: 50%;
        }

        .control-btn.close { background: #ff5f56; }
        .control-btn.minimize { background: #ffbd2e; }
        .control-btn.maximize { background: #27ca3f; }

        .terminal-title {
          font-size: var(--font-size-xs);
          opacity: 0.8;
        }

        .terminal-body {
          padding: var(--spacing-md);
          height: 400px;
          overflow-y: auto;
          line-height: 1.4;
        }

        .terminal-line {
          display: flex;
          align-items: center;
          margin-bottom: var(--spacing-xs);
        }

        .cursor {
          width: 8px;
          height: 16px;
          margin-left: 2px;
          animation: blink 1s infinite;
        }

        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }

        .command-example {
          margin: var(--spacing-md) 0;
        }

        .command-output {
          margin-left: var(--spacing-md);
          margin-bottom: var(--spacing-sm);
        }

        .ansi-color-test {
          margin-top: var(--spacing-lg);
          padding-top: var(--spacing-lg);
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .color-row {
          display: flex;
          gap: var(--spacing-md);
          margin: var(--spacing-xs) 0;
        }

        .color-row span {
          font-weight: var(--font-weight-medium);
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