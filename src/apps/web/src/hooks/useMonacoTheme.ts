import { useState, useEffect, useMemo } from 'react'
import { editor } from 'monaco-editor'

export interface ThemeConfig {
  name: string
  displayName: string
  type: 'light' | 'dark'
  colors: {
    'editor.background': string
    'editor.foreground': string
    'editor.lineHighlightBackground': string
    'editor.selectionBackground': string
    'editorCursor.foreground': string
    'editorLineNumber.foreground': string
    'editorIndentGuide.background': string
    'editorWhitespace.foreground': string
  }
  rules: Array<{
    token: string
    foreground?: string
    background?: string
    fontStyle?: string
  }>
}

const lightTheme: ThemeConfig = {
  name: 'claude-light',
  displayName: 'Claude Light',
  type: 'light',
  colors: {
    'editor.background': '#ffffff',
    'editor.foreground': '#333333',
    'editor.lineHighlightBackground': '#f5f5f5',
    'editor.selectionBackground': '#add6ff',
    'editorCursor.foreground': '#0066cc',
    'editorLineNumber.foreground': '#999999',
    'editorIndentGuide.background': '#e8e8e8',
    'editorWhitespace.foreground': '#cccccc'
  },
  rules: [
    { token: 'comment', foreground: '008000', fontStyle: 'italic' },
    { token: 'keyword', foreground: '0000ff', fontStyle: 'bold' },
    { token: 'string', foreground: 'a31515' },
    { token: 'number', foreground: '098658' },
    { token: 'type', foreground: '267f99' },
    { token: 'function', foreground: '795e26' },
    { token: 'variable', foreground: '001080' }
  ]
}

const darkTheme: ThemeConfig = {
  name: 'claude-dark',
  displayName: 'Claude Dark',
  type: 'dark',
  colors: {
    'editor.background': '#1e1e1e',
    'editor.foreground': '#d4d4d4',
    'editor.lineHighlightBackground': '#2d2d30',
    'editor.selectionBackground': '#264f78',
    'editorCursor.foreground': '#aeafad',
    'editorLineNumber.foreground': '#858585',
    'editorIndentGuide.background': '#404040',
    'editorWhitespace.foreground': '#404040'
  },
  rules: [
    { token: 'comment', foreground: '6a9955', fontStyle: 'italic' },
    { token: 'keyword', foreground: '569cd6', fontStyle: 'bold' },
    { token: 'string', foreground: 'ce9178' },
    { token: 'number', foreground: 'b5cea8' },
    { token: 'type', foreground: '4ec9b0' },
    { token: 'function', foreground: 'dcdcaa' },
    { token: 'variable', foreground: '9cdcfe' }
  ]
}

const highContrastTheme: ThemeConfig = {
  name: 'claude-high-contrast',
  displayName: 'Claude High Contrast',
  type: 'dark',
  colors: {
    'editor.background': '#000000',
    'editor.foreground': '#ffffff',
    'editor.lineHighlightBackground': '#1f1f1f',
    'editor.selectionBackground': '#ffffff',
    'editorCursor.foreground': '#ffff00',
    'editorLineNumber.foreground': '#ffffff',
    'editorIndentGuide.background': '#ffffff',
    'editorWhitespace.foreground': '#ffffff'
  },
  rules: [
    { token: 'comment', foreground: '00ff00', fontStyle: 'italic' },
    { token: 'keyword', foreground: 'ffff00', fontStyle: 'bold' },
    { token: 'string', foreground: 'ff00ff' },
    { token: 'number', foreground: '00ffff' },
    { token: 'type', foreground: 'ff8000' },
    { token: 'function', foreground: 'ff0000' },
    { token: 'variable', foreground: 'ffffff' }
  ]
}

export const useMonacoTheme = (initialTheme: 'light' | 'dark' | 'auto' | 'high-contrast' = 'auto') => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'high-contrast'>(() => {
    if (initialTheme === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return initialTheme as 'light' | 'dark' | 'high-contrast'
  })

  const themeConfig = useMemo(() => {
    switch (theme) {
      case 'light':
        return lightTheme
      case 'dark':
        return darkTheme
      case 'high-contrast':
        return highContrastTheme
      default:
        return darkTheme
    }
  }, [theme])

  const currentTheme = useMemo(() => {
    switch (theme) {
      case 'light':
        return 'claude-light'
      case 'dark':
        return 'claude-dark'
      case 'high-contrast':
        return 'claude-high-contrast'
      default:
        return 'claude-dark'
    }
  }, [theme])

  // Register themes with Monaco
  useEffect(() => {
    const registerThemes = async () => {
      const monaco = await import('monaco-editor')
      
      // Define and register themes
      monaco.editor.defineTheme('claude-light', {
        base: 'vs',
        inherit: true,
        rules: lightTheme.rules.map(rule => ({
          token: rule.token,
          foreground: rule.foreground,
          fontStyle: rule.fontStyle
        })),
        colors: lightTheme.colors
      })

      monaco.editor.defineTheme('claude-dark', {
        base: 'vs-dark',
        inherit: true,
        rules: darkTheme.rules.map(rule => ({
          token: rule.token,
          foreground: rule.foreground,
          fontStyle: rule.fontStyle
        })),
        colors: darkTheme.colors
      })

      monaco.editor.defineTheme('claude-high-contrast', {
        base: 'hc-black',
        inherit: true,
        rules: highContrastTheme.rules.map(rule => ({
          token: rule.token,
          foreground: rule.foreground,
          fontStyle: rule.fontStyle
        })),
        colors: highContrastTheme.colors
      })
    }

    registerThemes()
  }, [])

  // Listen for system theme changes
  useEffect(() => {
    if (initialTheme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handleChange = (e: MediaQueryListEvent) => {
        setTheme(e.matches ? 'dark' : 'light')
      }

      mediaQuery.addEventListener('change', handleChange)
      return () => mediaQuery.removeEventListener('change', handleChange)
    }
  }, [initialTheme])

  const switchTheme = (newTheme: 'light' | 'dark' | 'high-contrast') => {
    setTheme(newTheme)
  }

  const toggleTheme = () => {
    setTheme(current => {
      switch (current) {
        case 'light':
          return 'dark'
        case 'dark':
          return 'high-contrast'
        case 'high-contrast':
          return 'light'
        default:
          return 'dark'
      }
    })
  }

  return {
    theme,
    currentTheme,
    themeConfig,
    switchTheme,
    toggleTheme,
    availableThemes: [
      { value: 'light', label: 'Light' },
      { value: 'dark', label: 'Dark' },
      { value: 'high-contrast', label: 'High Contrast' }
    ]
  }
}