import React, { useState, useCallback } from 'react'
import { Monaco } from '@monaco-editor/react'
import { editor } from 'monaco-editor'
import { 
  Play, 
  Square, 
  RotateCcw, 
  Save, 
  Search, 
  Replace, 
  Palette, 
  Code, 
  Settings, 
  GitBranch, 
  Bug, 
  Users,
  FileText,
  Download,
  Upload,
  Maximize2,
  Minimize2
} from 'lucide-react'

export interface MonacoEditorToolbarProps {
  editor: editor.IStandaloneCodeEditor | null
  monaco: Monaco | null
  language: string
  readOnly: boolean
  onLanguageChange: (language: string) => void
  onThemeChange: (theme: string) => void
  enableDebugger?: boolean
  enableGitIntegration?: boolean
  enableCollaboration?: boolean
}

const SUPPORTED_LANGUAGES = [
  { value: 'typescript', label: 'TypeScript', icon: '🔷' },
  { value: 'javascript', label: 'JavaScript', icon: '🟨' },
  { value: 'python', label: 'Python', icon: '🐍' },
  { value: 'go', label: 'Go', icon: '🐹' },
  { value: 'rust', label: 'Rust', icon: '🦀' },
  { value: 'java', label: 'Java', icon: '☕' },
  { value: 'csharp', label: 'C#', icon: '🔵' },
  { value: 'cpp', label: 'C++', icon: '⚡' },
  { value: 'html', label: 'HTML', icon: '🌐' },
  { value: 'css', label: 'CSS', icon: '🎨' },
  { value: 'json', label: 'JSON', icon: '📄' },
  { value: 'yaml', label: 'YAML', icon: '📋' },
  { value: 'markdown', label: 'Markdown', icon: '📝' }
]

const THEMES = [
  { value: 'claude-light', label: 'Claude Light' },
  { value: 'claude-dark', label: 'Claude Dark' },
  { value: 'claude-high-contrast', label: 'High Contrast' },
  { value: 'vs', label: 'Visual Studio' },
  { value: 'vs-dark', label: 'Visual Studio Dark' },
  { value: 'hc-black', label: 'High Contrast Black' }
]

export const MonacoEditorToolbar: React.FC<MonacoEditorToolbarProps> = ({
  editor,
  monaco,
  language,
  readOnly,
  onLanguageChange,
  onThemeChange,
  enableDebugger = false,
  enableGitIntegration = false,
  enableCollaboration = false
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false)
  const [showThemeDropdown, setShowThemeDropdown] = useState(false)
  const [showSettingsPanel, setShowSettingsPanel] = useState(false)

  const handleFormat = useCallback(() => {
    if (editor) {
      editor.getAction('editor.action.formatDocument')?.run()
    }
  }, [editor])

  const handleSave = useCallback(() => {
    if (editor) {
      // Trigger save action
      const model = editor.getModel()
      if (model) {
        // Emit save event or call callback
        const saveEvent = new CustomEvent('monaco-save', {
          detail: { content: model.getValue() }
        })
        window.dispatchEvent(saveEvent)
      }
    }
  }, [editor])

  const handleFind = useCallback(() => {
    if (editor) {
      editor.getAction('actions.find')?.run()
    }
  }, [editor])

  const handleReplace = useCallback(() => {
    if (editor) {
      editor.getAction('editor.action.startFindReplaceAction')?.run()
    }
  }, [editor])

  const handleCommandPalette = useCallback(() => {
    if (editor) {
      editor.getAction('editor.action.quickCommand')?.run()
    }
  }, [editor])

  const toggleFullscreen = useCallback(() => {
    setIsFullscreen(!isFullscreen)
    // Implement fullscreen logic
    const container = editor?.getContainerDomNode()?.closest('.monaco-editor-container')
    if (container) {
      if (!isFullscreen) {
        container.classList.add('fullscreen')
      } else {
        container.classList.remove('fullscreen')
      }
    }
  }, [editor, isFullscreen])

  const exportCode = useCallback(() => {
    if (editor) {
      const model = editor.getModel()
      if (model) {
        const content = model.getValue()
        const blob = new Blob([content], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `code.${getFileExtension(language)}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    }
  }, [editor, language])

  const importCode = useCallback(() => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.js,.ts,.py,.go,.rs,.java,.cs,.cpp,.html,.css,.json,.yaml,.md'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file && editor) {
        const reader = new FileReader()
        reader.onload = (event) => {
          const content = event.target?.result as string
          const model = editor.getModel()
          if (model) {
            model.setValue(content)
          }
        }
        reader.readAsText(file)
      }
    }
    input.click()
  }, [editor])

  const getFileExtension = (lang: string): string => {
    const extensions: Record<string, string> = {
      typescript: 'ts',
      javascript: 'js',
      python: 'py',
      go: 'go',
      rust: 'rs',
      java: 'java',
      csharp: 'cs',
      cpp: 'cpp',
      html: 'html',
      css: 'css',
      json: 'json',
      yaml: 'yaml',
      markdown: 'md'
    }
    return extensions[lang] || 'txt'
  }

  return (
    <div className="monaco-toolbar">
      <div className="toolbar-section toolbar-main">
        {/* Language Selector */}
        <div className="toolbar-group">
          <div className="dropdown" data-active={showLanguageDropdown}>
            <button
              className="toolbar-button dropdown-trigger"
              onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
              title="Select Language"
            >
              <Code size={16} />
              <span>{SUPPORTED_LANGUAGES.find(l => l.value === language)?.label}</span>
            </button>
            {showLanguageDropdown && (
              <div className="dropdown-menu">
                {SUPPORTED_LANGUAGES.map(lang => (
                  <button
                    key={lang.value}
                    className={`dropdown-item ${language === lang.value ? 'active' : ''}`}
                    onClick={() => {
                      onLanguageChange(lang.value)
                      setShowLanguageDropdown(false)
                    }}
                  >
                    <span className="language-icon">{lang.icon}</span>
                    {lang.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* File Operations */}
        <div className="toolbar-group">
          <button
            className="toolbar-button"
            onClick={handleSave}
            title="Save (Ctrl+S)"
            disabled={readOnly}
          >
            <Save size={16} />
          </button>
          <button
            className="toolbar-button"
            onClick={exportCode}
            title="Export Code"
          >
            <Download size={16} />
          </button>
          <button
            className="toolbar-button"
            onClick={importCode}
            title="Import Code"
            disabled={readOnly}
          >
            <Upload size={16} />
          </button>
        </div>

        {/* Edit Operations */}
        <div className="toolbar-group">
          <button
            className="toolbar-button"
            onClick={handleFormat}
            title="Format Document (Shift+Alt+F)"
            disabled={readOnly}
          >
            <FileText size={16} />
          </button>
          <button
            className="toolbar-button"
            onClick={handleFind}
            title="Find (Ctrl+F)"
          >
            <Search size={16} />
          </button>
          <button
            className="toolbar-button"
            onClick={handleReplace}
            title="Replace (Ctrl+H)"
            disabled={readOnly}
          >
            <Replace size={16} />
          </button>
        </div>

        {/* Advanced Features */}
        <div className="toolbar-group">
          {enableDebugger && (
            <>
              <button
                className="toolbar-button"
                onClick={() => {
                  // Start debugging
                  const debugEvent = new CustomEvent('monaco-debug-start')
                  window.dispatchEvent(debugEvent)
                }}
                title="Start Debugging (F5)"
              >
                <Play size={16} />
              </button>
              <button
                className="toolbar-button"
                onClick={() => {
                  // Stop debugging
                  const debugEvent = new CustomEvent('monaco-debug-stop')
                  window.dispatchEvent(debugEvent)
                }}
                title="Stop Debugging (Shift+F5)"
              >
                <Square size={16} />
              </button>
              <button
                className="toolbar-button"
                onClick={() => {
                  // Toggle breakpoint
                  const position = editor?.getPosition()
                  if (position) {
                    const breakpointEvent = new CustomEvent('monaco-toggle-breakpoint', {
                      detail: { line: position.lineNumber }
                    })
                    window.dispatchEvent(breakpointEvent)
                  }
                }}
                title="Toggle Breakpoint (F9)"
              >
                <Bug size={16} />
              </button>
            </>
          )}

          {enableGitIntegration && (
            <button
              className="toolbar-button"
              onClick={() => {
                // Show Git panel
                const gitEvent = new CustomEvent('monaco-git-panel')
                window.dispatchEvent(gitEvent)
              }}
              title="Git Integration"
            >
              <GitBranch size={16} />
            </button>
          )}

          {enableCollaboration && (
            <button
              className="toolbar-button"
              onClick={() => {
                // Show collaboration panel
                const collabEvent = new CustomEvent('monaco-collaboration-panel')
                window.dispatchEvent(collabEvent)
              }}
              title="Collaboration"
            >
              <Users size={16} />
            </button>
          )}
        </div>
      </div>

      <div className="toolbar-section toolbar-right">
        {/* Theme Selector */}
        <div className="toolbar-group">
          <div className="dropdown" data-active={showThemeDropdown}>
            <button
              className="toolbar-button dropdown-trigger"
              onClick={() => setShowThemeDropdown(!showThemeDropdown)}
              title="Select Theme"
            >
              <Palette size={16} />
            </button>
            {showThemeDropdown && (
              <div className="dropdown-menu dropdown-menu-right">
                {THEMES.map(theme => (
                  <button
                    key={theme.value}
                    className="dropdown-item"
                    onClick={() => {
                      onThemeChange(theme.value)
                      setShowThemeDropdown(false)
                    }}
                  >
                    {theme.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Utility Buttons */}
        <div className="toolbar-group">
          <button
            className="toolbar-button"
            onClick={handleCommandPalette}
            title="Command Palette (Ctrl+Shift+P)"
          >
            <Settings size={16} />
          </button>
          <button
            className="toolbar-button"
            onClick={toggleFullscreen}
            title="Toggle Fullscreen"
          >
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettingsPanel && (
        <div className="settings-panel">
          <div className="settings-header">
            <h3>Editor Settings</h3>
            <button
              className="close-button"
              onClick={() => setShowSettingsPanel(false)}
            >
              ×
            </button>
          </div>
          <div className="settings-content">
            {/* Settings content would go here */}
            <p>Editor settings panel</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default MonacoEditorToolbar