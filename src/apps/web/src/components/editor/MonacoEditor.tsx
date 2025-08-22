import React, { useEffect, useRef, useState, useCallback } from 'react'
import Editor, { Monaco } from '@monaco-editor/react'
import { editor } from 'monaco-editor'
import { useMonacoTheme } from '../hooks/useMonacoTheme'
import { useLanguageSupport } from '../hooks/useLanguageSupport'
import { useCollaborativeEditing } from '../hooks/useCollaborativeEditing'
import { useDebugger } from '../hooks/useDebugger'
import { useGitIntegration } from '../hooks/useGitIntegration'
import { MonacoEditorToolbar } from './MonacoEditorToolbar'
import { MonacoEditorMinimap } from './MonacoEditorMinimap'
import { MonacoEditorStatusBar } from './MonacoEditorStatusBar'
import { CommandPalette } from './CommandPalette'

export interface MonacoEditorProps {
  language?: string
  value?: string
  onChange?: (value: string) => void
  onSave?: (value: string) => void
  theme?: 'light' | 'dark' | 'auto'
  readOnly?: boolean
  height?: string | number
  width?: string | number
  options?: editor.IStandaloneEditorConstructionOptions
  enableVim?: boolean
  enableEmacs?: boolean
  enableCollaboration?: boolean
  enableDebugger?: boolean
  enableGitIntegration?: boolean
  enableLSP?: boolean
  filePath?: string
  workspaceRoot?: string
}

export const MonacoEditor: React.FC<MonacoEditorProps> = ({
  language = 'typescript',
  value = '',
  onChange,
  onSave,
  theme = 'auto',
  readOnly = false,
  height = '100vh',
  width = '100%',
  options = {},
  enableVim = false,
  enableEmacs = false,
  enableCollaboration = false,
  enableDebugger = false,
  enableGitIntegration = false,
  enableLSP = true,
  filePath,
  workspaceRoot
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)
  const monacoRef = useRef<Monaco | null>(null)
  const [isReady, setIsReady] = useState(false)
  const [showCommandPalette, setShowCommandPalette] = useState(false)
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 })
  const [selection, setSelection] = useState({ selected: 0, total: 0 })

  // Custom hooks for advanced features
  const { currentTheme, themeConfig } = useMonacoTheme(theme)
  const { setupLanguageSupport } = useLanguageSupport(enableLSP)
  const { setupCollaboration } = useCollaborativeEditing(enableCollaboration)
  const { setupDebugger, breakpoints } = useDebugger(enableDebugger)
  const { setupGitIntegration, gitStatus } = useGitIntegration(enableGitIntegration, filePath, workspaceRoot)

  // Enhanced editor options
  const editorOptions: editor.IStandaloneEditorConstructionOptions = {
    automaticLayout: true,
    fontSize: 14,
    fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
    fontLigatures: true,
    lineNumbers: 'on',
    rulers: [80, 120],
    wordWrap: 'on',
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    smoothScrolling: true,
    cursorBlinking: 'smooth',
    cursorSmoothCaretAnimation: 'on',
    renderWhitespace: 'boundary',
    renderControlCharacters: true,
    renderLineHighlight: 'all',
    overviewRulerBorder: true,
    overviewRulerLanes: 3,
    bracketPairColorization: { enabled: true },
    guides: {
      bracketPairs: true,
      bracketPairsHorizontal: true,
      highlightActiveBracketPair: true,
      indentation: true
    },
    suggest: {
      preview: true,
      showIcons: true,
      showSnippets: true,
      showWords: true,
      insertMode: 'replace'
    },
    quickSuggestions: {
      other: true,
      comments: true,
      strings: true
    },
    parameterHints: { enabled: true },
    hover: { enabled: true },
    lightbulb: { enabled: true },
    definitionLinkOpensInPeek: false,
    gotoLocation: {
      multipleReferences: 'peek',
      multipleDefinitions: 'peek',
      multipleDeclarations: 'peek',
      multipleImplementations: 'peek',
      multipleTypeDefinitions: 'peek'
    },
    folding: true,
    foldingStrategy: 'indentation',
    showFoldingControls: 'always',
    unfoldOnClickAfterEndOfLine: true,
    find: {
      addExtraSpaceOnTop: true,
      autoFindInSelection: 'multiline',
      seedSearchStringFromSelection: 'selection'
    },
    multiCursorModifier: 'ctrlCmd',
    selectionHighlight: true,
    occurrencesHighlight: true,
    codeLens: true,
    colorDecorators: true,
    contextmenu: true,
    mouseWheelZoom: true,
    links: true,
    readOnly,
    ...options
  }

  // Handle editor mount
  const handleEditorDidMount = useCallback(async (editor: editor.IStandaloneCodeEditor, monaco: Monaco) => {
    editorRef.current = editor
    monacoRef.current = monaco

    // Setup language support
    if (enableLSP) {
      await setupLanguageSupport(monaco, language, workspaceRoot)
    }

    // Setup collaboration
    if (enableCollaboration) {
      setupCollaboration(editor, monaco)
    }

    // Setup debugger
    if (enableDebugger) {
      setupDebugger(editor, monaco)
    }

    // Setup Git integration
    if (enableGitIntegration) {
      setupGitIntegration(editor, monaco)
    }

    // Setup vim/emacs bindings
    if (enableVim) {
      const { initVimMode } = await import('monaco-vim')
      initVimMode(editor, document.getElementById('vim-statusbar'))
    }

    if (enableEmacs) {
      const { EmacsExtension } = await import('monaco-emacs')
      const emacsMode = new EmacsExtension(editor)
      emacsMode.start()
    }

    // Custom key bindings
    setupKeyBindings(editor, monaco)

    // Track cursor position and selection
    editor.onDidChangeCursorPosition((e) => {
      setCursorPosition({ line: e.position.lineNumber, column: e.position.column })
    })

    editor.onDidChangeCursorSelection((e) => {
      const model = editor.getModel()
      if (model) {
        const selectedText = model.getValueInRange(e.selection)
        setSelection({
          selected: selectedText.length,
          total: model.getValueLength()
        })
      }
    })

    setIsReady(true)
  }, [language, enableLSP, enableCollaboration, enableDebugger, enableGitIntegration, enableVim, enableEmacs, workspaceRoot])

  // Setup custom key bindings
  const setupKeyBindings = useCallback((editor: editor.IStandaloneCodeEditor, monaco: Monaco) => {
    // Command Palette (Ctrl+Shift+P)
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyP, () => {
      setShowCommandPalette(true)
    })

    // Save (Ctrl+S)
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      const model = editor.getModel()
      if (model && onSave) {
        onSave(model.getValue())
      }
    })

    // Format Document (Shift+Alt+F)
    editor.addCommand(monaco.KeyMod.Shift | monaco.KeyMod.Alt | monaco.KeyCode.KeyF, () => {
      editor.getAction('editor.action.formatDocument')?.run()
    })

    // Go to Definition (F12)
    editor.addCommand(monaco.KeyCode.F12, () => {
      editor.getAction('editor.action.revealDefinition')?.run()
    })

    // Find References (Shift+F12)
    editor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.F12, () => {
      editor.getAction('editor.action.goToReferences')?.run()
    })

    // Rename Symbol (F2)
    editor.addCommand(monaco.KeyCode.F2, () => {
      editor.getAction('editor.action.rename')?.run()
    })

    // Toggle Breakpoint (F9)
    if (enableDebugger) {
      editor.addCommand(monaco.KeyCode.F9, () => {
        const position = editor.getPosition()
        if (position) {
          // Toggle breakpoint logic here
          console.log('Toggle breakpoint at line:', position.lineNumber)
        }
      })
    }
  }, [onSave, enableDebugger])

  // Handle value changes
  const handleEditorChange = useCallback((value: string | undefined) => {
    if (onChange && value !== undefined) {
      onChange(value)
    }
  }, [onChange])

  return (
    <div className="monaco-editor-container">
      <MonacoEditorToolbar
        editor={editorRef.current}
        monaco={monacoRef.current}
        language={language}
        readOnly={readOnly}
        onLanguageChange={(newLanguage) => {
          if (monacoRef.current && editorRef.current) {
            const model = editorRef.current.getModel()
            if (model) {
              monacoRef.current.editor.setModelLanguage(model, newLanguage)
            }
          }
        }}
        onThemeChange={(newTheme) => {
          if (monacoRef.current) {
            monacoRef.current.editor.setTheme(newTheme)
          }
        }}
        enableDebugger={enableDebugger}
        enableGitIntegration={enableGitIntegration}
      />

      <div className="monaco-editor-wrapper" style={{ height: typeof height === 'number' ? `${height}px` : height }}>
        <Editor
          height={height}
          width={width}
          language={language}
          value={value}
          theme={currentTheme}
          options={editorOptions}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
        />
        
        {isReady && (
          <MonacoEditorMinimap
            editor={editorRef.current}
            gitStatus={gitStatus}
            breakpoints={breakpoints}
          />
        )}
      </div>

      <MonacoEditorStatusBar
        cursorPosition={cursorPosition}
        selection={selection}
        language={language}
        readOnly={readOnly}
        gitStatus={gitStatus}
        isConnected={enableCollaboration}
      />

      {showCommandPalette && (
        <CommandPalette
          editor={editorRef.current}
          monaco={monacoRef.current}
          onClose={() => setShowCommandPalette(false)}
        />
      )}

      {enableVim && <div id="vim-statusbar" className="vim-statusbar" />}
    </div>
  )
}

export default MonacoEditor