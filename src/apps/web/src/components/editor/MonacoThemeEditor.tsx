// Monaco Theme Editor - Visual Monaco Editor Theme Customization
// Provides interface for customizing Monaco editor themes with live preview

import React, { useState, useCallback, useMemo } from 'react'
import { MonacoTheme } from '../types/theme'
import { ColorPicker } from './ColorPicker'

interface MonacoThemeEditorProps {
  monacoTheme: MonacoTheme
  onChange: (monacoTheme: MonacoTheme) => void
}

const syntaxTokens = [
  { token: 'comment', label: 'Comments', example: '// This is a comment' },
  { token: 'keyword', label: 'Keywords', example: 'const function if else' },
  { token: 'string', label: 'Strings', example: '"Hello, World!"' },
  { token: 'number', label: 'Numbers', example: '42 3.14 0xFF' },
  { token: 'type', label: 'Types', example: 'string number boolean' },
  { token: 'function', label: 'Functions', example: 'myFunction()' },
  { token: 'variable', label: 'Variables', example: 'myVariable' },
  { token: 'constant', label: 'Constants', example: 'MY_CONSTANT' },
  { token: 'class', label: 'Classes', example: 'MyClass' },
  { token: 'interface', label: 'Interfaces', example: 'IMyInterface' },
  { token: 'namespace', label: 'Namespaces', example: 'MyNamespace' },
  { token: 'tag', label: 'HTML Tags', example: '<div> <span>' },
  { token: 'attribute', label: 'Attributes', example: 'className="..."' },
  { token: 'regexp', label: 'RegExp', example: '/pattern/gi' }
]

const editorColorKeys = [
  { key: 'editor.background', label: 'Background', description: 'Main editor background' },
  { key: 'editor.foreground', label: 'Foreground', description: 'Default text color' },
  { key: 'editor.lineHighlightBackground', label: 'Line Highlight', description: 'Current line background' },
  { key: 'editor.selectionBackground', label: 'Selection', description: 'Selected text background' },
  { key: 'editorCursor.foreground', label: 'Cursor', description: 'Cursor color' },
  { key: 'editorLineNumber.foreground', label: 'Line Numbers', description: 'Line number color' },
  { key: 'editorLineNumber.activeForeground', label: 'Active Line Number', description: 'Current line number' },
  { key: 'editorIndentGuide.background', label: 'Indent Guides', description: 'Indentation guide lines' },
  { key: 'editorWhitespace.foreground', label: 'Whitespace', description: 'Whitespace characters' },
  { key: 'editorGutter.background', label: 'Gutter Background', description: 'Line number area background' },
  { key: 'editorError.foreground', label: 'Error Squiggles', description: 'Error underline color' },
  { key: 'editorWarning.foreground', label: 'Warning Squiggles', description: 'Warning underline color' },
  { key: 'editorInfo.foreground', label: 'Info Squiggles', description: 'Info underline color' }
] as const

const terminalColorKeys = [
  { key: 'terminal.background', label: 'Terminal Background', description: 'Terminal background color' },
  { key: 'terminal.foreground', label: 'Terminal Text', description: 'Terminal text color' },
  { key: 'terminal.ansiBlack', label: 'ANSI Black', description: 'Terminal black color' },
  { key: 'terminal.ansiRed', label: 'ANSI Red', description: 'Terminal red color' },
  { key: 'terminal.ansiGreen', label: 'ANSI Green', description: 'Terminal green color' },
  { key: 'terminal.ansiYellow', label: 'ANSI Yellow', description: 'Terminal yellow color' },
  { key: 'terminal.ansiBlue', label: 'ANSI Blue', description: 'Terminal blue color' },
  { key: 'terminal.ansiMagenta', label: 'ANSI Magenta', description: 'Terminal magenta color' },
  { key: 'terminal.ansiCyan', label: 'ANSI Cyan', description: 'Terminal cyan color' },
  { key: 'terminal.ansiWhite', label: 'ANSI White', description: 'Terminal white color' }
] as const

export const MonacoThemeEditor: React.FC<MonacoThemeEditorProps> = ({
  monacoTheme,
  onChange
}) => {
  const [activeSection, setActiveSection] = useState<'syntax' | 'editor' | 'terminal' | 'preview'>('syntax')

  const updateSyntaxRule = useCallback((token: string, foreground?: string, fontStyle?: string) => {
    const existingRuleIndex = monacoTheme.rules.findIndex(rule => rule.token === token)
    const newRule = {
      token,
      ...(foreground && { foreground }),
      ...(fontStyle && { fontStyle })
    }

    let newRules
    if (existingRuleIndex >= 0) {
      newRules = [...monacoTheme.rules]
      newRules[existingRuleIndex] = newRule
    } else {
      newRules = [...monacoTheme.rules, newRule]
    }

    onChange({
      ...monacoTheme,
      rules: newRules
    })
  }, [monacoTheme, onChange])

  const updateEditorColor = useCallback((key: keyof MonacoTheme['colors'], value: string) => {
    onChange({
      ...monacoTheme,
      colors: {
        ...monacoTheme.colors,
        [key]: value
      }
    })
  }, [monacoTheme, onChange])

  const updateBaseTheme = useCallback((base: MonacoTheme['base']) => {
    onChange({
      ...monacoTheme,
      base
    })
  }, [monacoTheme, onChange])

  const getSyntaxRuleColor = useCallback((token: string): string => {
    const rule = monacoTheme.rules.find(rule => rule.token === token)
    return rule?.foreground ? `#${rule.foreground}` : '#ffffff'
  }, [monacoTheme.rules])

  const getSyntaxRuleStyle = useCallback((token: string): string => {
    const rule = monacoTheme.rules.find(rule => rule.token === token)
    return rule?.fontStyle || ''
  }, [monacoTheme.rules])

  const codePreview = useMemo(() => `// TypeScript Example
import React, { useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

/**
 * User profile component
 */
const UserProfile: React.FC<{ userId: number }> = ({ userId }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch(\`/api/users/\${userId}\`);
        const userData = await response.json();
        setUser(userData);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUser();
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div className="user-profile">
      <h1>{user.name}</h1>
      <p>Email: {user.email}</p>
    </div>
  );
};

export default UserProfile;`, [])

  return (
    <div className="monaco-theme-editor">
      <h3>Monaco Editor Theme</h3>
      
      <div className="base-theme-selector">
        <label>Base Theme:</label>
        <select
          value={monacoTheme.base}
          onChange={(e) => updateBaseTheme(e.target.value as MonacoTheme['base'])}
          className="base-theme-select"
        >
          <option value="vs">Visual Studio Light</option>
          <option value="vs-dark">Visual Studio Dark</option>
          <option value="hc-black">High Contrast Dark</option>
          <option value="hc-light">High Contrast Light</option>
        </select>
      </div>

      <div className="monaco-nav">
        <button
          className={`nav-btn ${activeSection === 'syntax' ? 'active' : ''}`}
          onClick={() => setActiveSection('syntax')}
        >
          Syntax Colors
        </button>
        <button
          className={`nav-btn ${activeSection === 'editor' ? 'active' : ''}`}
          onClick={() => setActiveSection('editor')}
        >
          Editor Colors
        </button>
        <button
          className={`nav-btn ${activeSection === 'terminal' ? 'active' : ''}`}
          onClick={() => setActiveSection('terminal')}
        >
          Terminal Colors
        </button>
        <button
          className={`nav-btn ${activeSection === 'preview' ? 'active' : ''}`}
          onClick={() => setActiveSection('preview')}
        >
          Preview
        </button>
      </div>

      <div className="monaco-content">
        {activeSection === 'syntax' && (
          <div className="syntax-section">
            <h4>Syntax Highlighting</h4>
            <div className="syntax-grid">
              {syntaxTokens.map(token => (
                <div key={token.token} className="syntax-item">
                  <div className="syntax-header">
                    <label>{token.label}</label>
                    <div className="syntax-controls">
                      <ColorPicker
                        value={getSyntaxRuleColor(token.token)}
                        onChange={(color) => updateSyntaxRule(token.token, color.replace('#', ''))}
                        showVariationButton={false}
                        showAccessibilityInfo={false}
                      />
                      <select
                        value={getSyntaxRuleStyle(token.token)}
                        onChange={(e) => updateSyntaxRule(token.token, undefined, e.target.value)}
                        className="style-select"
                      >
                        <option value="">Normal</option>
                        <option value="italic">Italic</option>
                        <option value="bold">Bold</option>
                        <option value="underline">Underline</option>
                      </select>
                    </div>
                  </div>
                  <div 
                    className="syntax-example"
                    style={{
                      color: getSyntaxRuleColor(token.token),
                      fontStyle: getSyntaxRuleStyle(token.token).includes('italic') ? 'italic' : 'normal',
                      fontWeight: getSyntaxRuleStyle(token.token).includes('bold') ? 'bold' : 'normal',
                      textDecoration: getSyntaxRuleStyle(token.token).includes('underline') ? 'underline' : 'none'
                    }}
                  >
                    {token.example}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === 'editor' && (
          <div className="editor-section">
            <h4>Editor Interface Colors</h4>
            <div className="editor-grid">
              {editorColorKeys.map(colorKey => (
                <div key={colorKey.key} className="editor-color-item">
                  <div className="color-header">
                    <label>{colorKey.label}</label>
                    <span className="color-description">{colorKey.description}</span>
                  </div>
                  <ColorPicker
                    value={monacoTheme.colors[colorKey.key] || '#000000'}
                    onChange={(color) => updateEditorColor(colorKey.key, color)}
                    showVariationButton={false}
                    showAccessibilityInfo={false}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === 'terminal' && (
          <div className="terminal-section">
            <h4>Integrated Terminal Colors</h4>
            <div className="terminal-grid">
              {terminalColorKeys.map(colorKey => (
                <div key={colorKey.key} className="terminal-color-item">
                  <div className="color-header">
                    <label>{colorKey.label}</label>
                    <span className="color-description">{colorKey.description}</span>
                  </div>
                  <ColorPicker
                    value={monacoTheme.colors[colorKey.key] || '#000000'}
                    onChange={(color) => updateEditorColor(colorKey.key, color)}
                    showVariationButton={false}
                    showAccessibilityInfo={false}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === 'preview' && (
          <div className="preview-section">
            <h4>Theme Preview</h4>
            <div 
              className="code-preview"
              style={{
                backgroundColor: monacoTheme.colors['editor.background'] || '#1e1e1e',
                color: monacoTheme.colors['editor.foreground'] || '#d4d4d4'
              }}
            >
              <div className="preview-header">
                <div className="preview-tabs">
                  <div className="preview-tab active">example.tsx</div>
                  <div className="preview-tab">styles.css</div>
                </div>
              </div>
              
              <div className="preview-editor">
                <div className="line-numbers">
                  {Array.from({ length: 30 }, (_, i) => (
                    <div 
                      key={i + 1} 
                      className="line-number"
                      style={{ 
                        color: monacoTheme.colors['editorLineNumber.foreground'] || '#858585',
                        backgroundColor: i === 5 ? monacoTheme.colors['editor.lineHighlightBackground'] || 'transparent' : 'transparent'
                      }}
                    >
                      {i + 1}
                    </div>
                  ))}
                </div>
                
                <div className="preview-code">
                  <pre>
                    <code dangerouslySetInnerHTML={{ __html: highlightCode(codePreview) }} />
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .monaco-theme-editor {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }

        .monaco-theme-editor h3 {
          margin: 0;
          color: var(--color-text-primary);
        }

        .base-theme-selector {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-md);
          background: var(--color-background-secondary);
          border-radius: var(--radius-md);
        }

        .base-theme-selector label {
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
        }

        .base-theme-select {
          padding: var(--spacing-xs) var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background: var(--color-background);
          color: var(--color-text-primary);
        }

        .monaco-nav {
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

        .syntax-grid,
        .editor-grid,
        .terminal-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: var(--spacing-md);
        }

        .syntax-item,
        .editor-color-item,
        .terminal-color-item {
          padding: var(--spacing-md);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background-secondary);
        }

        .syntax-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-sm);
        }

        .syntax-header label {
          font-weight: var(--font-weight-medium);
          color: var(--color-text-primary);
        }

        .syntax-controls {
          display: flex;
          gap: var(--spacing-xs);
          align-items: center;
        }

        .style-select {
          padding: var(--spacing-xs);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background: var(--color-background);
          color: var(--color-text-primary);
          font-size: var(--font-size-xs);
        }

        .syntax-example {
          font-family: var(--font-family-mono);
          font-size: var(--font-size-sm);
          padding: var(--spacing-sm);
          background: var(--color-background);
          border-radius: var(--radius-sm);
          border: 1px solid var(--color-border);
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

        .code-preview {
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          overflow: hidden;
          background: #1e1e1e;
          font-family: var(--font-family-mono);
          font-size: var(--font-size-sm);
        }

        .preview-header {
          padding: var(--spacing-sm) var(--spacing-md);
          background: rgba(255, 255, 255, 0.05);
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .preview-tabs {
          display: flex;
          gap: var(--spacing-xs);
        }

        .preview-tab {
          padding: var(--spacing-xs) var(--spacing-sm);
          background: rgba(255, 255, 255, 0.1);
          border-radius: var(--radius-sm);
          font-size: var(--font-size-xs);
          opacity: 0.7;
        }

        .preview-tab.active {
          opacity: 1;
          background: rgba(255, 255, 255, 0.2);
        }

        .preview-editor {
          display: flex;
          height: 400px;
          overflow: auto;
        }

        .line-numbers {
          padding: var(--spacing-md) var(--spacing-sm);
          background: rgba(0, 0, 0, 0.2);
          border-right: 1px solid rgba(255, 255, 255, 0.1);
          font-size: var(--font-size-xs);
          user-select: none;
        }

        .line-number {
          height: 1.4em;
          text-align: right;
          padding-right: var(--spacing-sm);
        }

        .preview-code {
          flex: 1;
          padding: var(--spacing-md);
          overflow: auto;
        }

        .preview-code pre {
          margin: 0;
          white-space: pre-wrap;
          line-height: 1.4;
        }

        .preview-code code {
          background: none;
          padding: 0;
          color: inherit;
        }
      `}</style>
    </div>
  )

  function highlightCode(code: string): string {
    // Simple syntax highlighting for preview
    return code
      .replace(/(\/\/.*$)/gm, `<span style="color: ${getSyntaxRuleColor('comment')}; font-style: italic;">$1</span>`)
      .replace(/\b(import|export|const|let|var|function|class|interface|type|async|await|if|else|for|while|return|try|catch|finally)\b/g, 
               `<span style="color: ${getSyntaxRuleColor('keyword')}; font-weight: bold;">$1</span>`)
      .replace(/(["'`])((?:\\.|(?!\1)[^\\])*?)\1/g, 
               `<span style="color: ${getSyntaxRuleColor('string')};">$1$2$1</span>`)
      .replace(/\b(\d+\.?\d*)\b/g, 
               `<span style="color: ${getSyntaxRuleColor('number')};">$1</span>`)
      .replace(/\b([A-Z][a-zA-Z0-9]*)\b/g, 
               `<span style="color: ${getSyntaxRuleColor('type')};">$1</span>`)
  }
}