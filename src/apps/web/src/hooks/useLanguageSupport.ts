import { useState, useCallback, useRef } from 'react'
import { Monaco } from '@monaco-editor/react'
import * as monaco from 'monaco-editor'
import { 
  MonacoLanguageClient, 
  CloseAction, 
  ErrorAction,
  MonacoServices,
  MessageTransports
} from 'monaco-languageclient'
import { WebSocketMessageReader, WebSocketMessageWriter } from 'vscode-ws-jsonrpc'

export interface LanguageServerConfig {
  language: string
  serverUrl: string
  documentSelector: string[]
  initializationOptions?: any
}

const languageServerConfigs: Record<string, LanguageServerConfig> = {
  typescript: {
    language: 'typescript',
    serverUrl: 'ws://localhost:3001/typescript',
    documentSelector: ['typescript', 'javascript', 'typescriptreact', 'javascriptreact'],
    initializationOptions: {
      preferences: {
        includeInlayParameterNameHints: 'all',
        includeInlayPropertyDeclarationTypeHints: true,
        includeInlayFunctionParameterTypeHints: true,
        includeInlayVariableTypeHints: true,
        includeInlayEnumMemberValueHints: true,
        includeInlayFunctionLikeReturnTypeHints: true,
        includeInlayParameterNameHintsWhenArgumentMatchesName: false
      }
    }
  },
  python: {
    language: 'python',
    serverUrl: 'ws://localhost:3001/python',
    documentSelector: ['python'],
    initializationOptions: {
      settings: {
        python: {
          analysis: {
            typeCheckingMode: 'basic',
            autoImportCompletions: true,
            autoSearchPaths: true
          }
        }
      }
    }
  },
  go: {
    language: 'go',
    serverUrl: 'ws://localhost:3001/go',
    documentSelector: ['go'],
    initializationOptions: {
      'build.buildFlags': [],
      'ui.completion.usePlaceholders': true,
      'ui.diagnostic.staticcheck': true
    }
  },
  rust: {
    language: 'rust',
    serverUrl: 'ws://localhost:3001/rust',
    documentSelector: ['rust'],
    initializationOptions: {
      cargo: {
        buildScripts: { enable: true },
        features: 'all'
      },
      checkOnSave: {
        command: 'clippy'
      }
    }
  },
  json: {
    language: 'json',
    serverUrl: 'ws://localhost:3001/json',
    documentSelector: ['json', 'jsonc'],
    initializationOptions: {
      provideFormatter: true,
      schemas: []
    }
  },
  html: {
    language: 'html',
    serverUrl: 'ws://localhost:3001/html',
    documentSelector: ['html'],
    initializationOptions: {
      embeddedLanguages: {
        css: true,
        javascript: true
      },
      configurationSection: ['html', 'css', 'javascript']
    }
  },
  css: {
    language: 'css',
    serverUrl: 'ws://localhost:3001/css',
    documentSelector: ['css', 'scss', 'less'],
    initializationOptions: {
      provideFormatter: true,
      customData: []
    }
  }
}

export const useLanguageSupport = (enableLSP: boolean = true) => {
  const [isLSPConnected, setIsLSPConnected] = useState(false)
  const [connectedLanguages, setConnectedLanguages] = useState<string[]>([])
  const languageClients = useRef<Map<string, MonacoLanguageClient>>(new Map())

  const setupLanguageSupport = useCallback(async (
    monacoInstance: Monaco,
    language: string,
    workspaceRoot?: string
  ) => {
    if (!enableLSP) return

    try {
      // Initialize Monaco services
      MonacoServices.install()

      // Setup language-specific features
      await setupIntelliSense(monacoInstance, language)
      await setupFormatting(monacoInstance, language)
      await setupLinting(monacoInstance, language)
      
      if (languageServerConfigs[language]) {
        await setupLanguageServer(monacoInstance, language, workspaceRoot)
      }

      // Setup code snippets
      await setupSnippets(monacoInstance, language)

    } catch (error) {
      console.error('Failed to setup language support:', error)
    }
  }, [enableLSP])

  const setupIntelliSense = async (monacoInstance: Monaco, language: string) => {
    // Enhanced completion provider
    monacoInstance.languages.registerCompletionItemProvider(language, {
      provideCompletionItems: (model, position) => {
        const word = model.getWordUntilPosition(position)
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn
        }

        return {
          suggestions: getLanguageCompletions(language, word.word, range)
        }
      }
    })

    // Hover provider
    monacoInstance.languages.registerHoverProvider(language, {
      provideHover: (model, position) => {
        const word = model.getWordAtPosition(position)
        if (!word) return null

        return {
          range: new monacoInstance.Range(
            position.lineNumber,
            word.startColumn,
            position.lineNumber,
            word.endColumn
          ),
          contents: [
            { value: `**${word.word}**` },
            { value: getHoverInformation(language, word.word) }
          ]
        }
      }
    })

    // Definition provider
    monacoInstance.languages.registerDefinitionProvider(language, {
      provideDefinition: (model, position) => {
        // This would typically query the language server
        return []
      }
    })

    // Reference provider
    monacoInstance.languages.registerReferenceProvider(language, {
      provideReferences: (model, position, context) => {
        // This would typically query the language server
        return []
      }
    })
  }

  const setupFormatting = async (monacoInstance: Monaco, language: string) => {
    // Document formatting provider
    monacoInstance.languages.registerDocumentFormattingEditProvider(language, {
      provideDocumentFormattingEdits: async (model, options) => {
        try {
          const formatted = await formatCode(model.getValue(), language, options)
          return [{
            range: model.getFullModelRange(),
            text: formatted
          }]
        } catch (error) {
          console.error('Formatting failed:', error)
          return []
        }
      }
    })

    // Range formatting provider
    monacoInstance.languages.registerDocumentRangeFormattingEditProvider(language, {
      provideDocumentRangeFormattingEdits: async (model, range, options) => {
        try {
          const selectedText = model.getValueInRange(range)
          const formatted = await formatCode(selectedText, language, options)
          return [{
            range,
            text: formatted
          }]
        } catch (error) {
          console.error('Range formatting failed:', error)
          return []
        }
      }
    })
  }

  const setupLinting = async (monacoInstance: Monaco, language: string) => {
    // Create linting worker
    const lintingWorker = new Worker(
      new URL('../workers/lintingWorker.ts', import.meta.url),
      { type: 'module' }
    )

    // Setup model markers for linting
    const updateMarkers = (model: monaco.editor.ITextModel) => {
      lintingWorker.postMessage({
        code: model.getValue(),
        language,
        uri: model.uri.toString()
      })
    }

    lintingWorker.onmessage = (event) => {
      const { markers, uri } = event.data
      const model = monacoInstance.editor.getModel(monacoInstance.Uri.parse(uri))
      if (model) {
        monacoInstance.editor.setModelMarkers(model, 'linting', markers)
      }
    }

    // Listen for model changes
    monacoInstance.editor.onDidCreateModel((model) => {
      if (model.getLanguageId() === language) {
        updateMarkers(model)
        model.onDidChangeContent(() => updateMarkers(model))
      }
    })
  }

  const setupLanguageServer = async (
    monacoInstance: Monaco,
    language: string,
    workspaceRoot?: string
  ) => {
    const config = languageServerConfigs[language]
    if (!config) return

    try {
      // Create WebSocket connection to language server
      const webSocket = new WebSocket(config.serverUrl)
      
      webSocket.onopen = () => {
        const reader = new WebSocketMessageReader(webSocket)
        const writer = new WebSocketMessageWriter(webSocket)
        const languageClient = new MonacoLanguageClient({
          name: `${language} Language Client`,
          clientOptions: {
            documentSelector: config.documentSelector,
            workspaceFolder: workspaceRoot ? {
              uri: monacoInstance.Uri.file(workspaceRoot).toString(),
              name: 'workspace'
            } : undefined,
            errorHandler: {
              error: () => ({ action: ErrorAction.Continue }),
              closed: () => ({ action: CloseAction.DoNotRestart })
            },
            initializationOptions: config.initializationOptions
          },
          messageTransports: { reader, writer } as MessageTransports
        })

        languageClient.start()
        languageClients.current.set(language, languageClient)
        setConnectedLanguages(prev => [...prev.filter(l => l !== language), language])
        setIsLSPConnected(true)
      }

      webSocket.onerror = (error) => {
        console.error(`Language server connection failed for ${language}:`, error)
      }

    } catch (error) {
      console.error(`Failed to setup language server for ${language}:`, error)
    }
  }

  const setupSnippets = async (monacoInstance: Monaco, language: string) => {
    const snippets = await getLanguageSnippets(language)
    
    monacoInstance.languages.registerCompletionItemProvider(language, {
      provideCompletionItems: (model, position) => {
        return {
          suggestions: snippets.map(snippet => ({
            label: snippet.prefix,
            kind: monacoInstance.languages.CompletionItemKind.Snippet,
            documentation: snippet.description,
            insertText: snippet.body,
            insertTextRules: monacoInstance.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            range: {
              startLineNumber: position.lineNumber,
              endLineNumber: position.lineNumber,
              startColumn: position.column,
              endColumn: position.column
            }
          }))
        }
      }
    })
  }

  const disconnectLanguageServer = useCallback((language: string) => {
    const client = languageClients.current.get(language)
    if (client) {
      client.stop()
      languageClients.current.delete(language)
      setConnectedLanguages(prev => prev.filter(l => l !== language))
    }
  }, [])

  const reconnectLanguageServer = useCallback(async (
    monacoInstance: Monaco,
    language: string,
    workspaceRoot?: string
  ) => {
    disconnectLanguageServer(language)
    await setupLanguageServer(monacoInstance, language, workspaceRoot)
  }, [disconnectLanguageServer])

  return {
    setupLanguageSupport,
    isLSPConnected,
    connectedLanguages,
    disconnectLanguageServer,
    reconnectLanguageServer,
    supportedLanguages: Object.keys(languageServerConfigs)
  }
}

// Helper functions
const getLanguageCompletions = (
  language: string,
  word: string,
  range: monaco.IRange
): monaco.languages.CompletionItem[] => {
  // This would typically be provided by the language server
  const commonCompletions: Record<string, string[]> = {
    typescript: ['console.log', 'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while'],
    python: ['print', 'def', 'class', 'if', 'else', 'for', 'while', 'import', 'from'],
    go: ['func', 'var', 'const', 'if', 'else', 'for', 'range', 'struct', 'interface'],
    rust: ['fn', 'let', 'mut', 'if', 'else', 'for', 'while', 'struct', 'enum', 'impl']
  }

  const completions = commonCompletions[language] || []
  
  return completions
    .filter(completion => completion.startsWith(word))
    .map(completion => ({
      label: completion,
      kind: monaco.languages.CompletionItemKind.Keyword,
      insertText: completion,
      range
    }))
}

const getHoverInformation = (language: string, word: string): string => {
  // This would typically query the language server for documentation
  const documentation: Record<string, Record<string, string>> = {
    typescript: {
      'console.log': 'Prints to stdout with newline. Multiple arguments can be passed.',
      'function': 'Declares a function',
      'const': 'Declares a read-only named constant'
    },
    python: {
      'print': 'Prints objects to the text stream file',
      'def': 'Defines a function',
      'class': 'Defines a class'
    }
  }

  return documentation[language]?.[word] || `No documentation available for ${word}`
}

const formatCode = async (
  code: string,
  language: string,
  options: monaco.languages.FormattingOptions
): Promise<string> => {
  // This would typically use prettier or language-specific formatters
  try {
    switch (language) {
      case 'typescript':
      case 'javascript':
        const prettier = await import('prettier/standalone')
        const parserTypeScript = await import('prettier/parser-typescript')
        return prettier.format(code, {
          parser: 'typescript',
          plugins: [parserTypeScript],
          tabWidth: options.tabSize,
          useTabs: !options.insertSpaces
        })
      default:
        return code
    }
  } catch (error) {
    console.error('Formatting error:', error)
    return code
  }
}

const getLanguageSnippets = async (language: string) => {
  // This would typically load from a snippets file or API
  const snippets: Record<string, Array<{ prefix: string; body: string; description: string }>> = {
    typescript: [
      {
        prefix: 'log',
        body: 'console.log(${1:message})',
        description: 'Log output to console'
      },
      {
        prefix: 'func',
        body: 'function ${1:name}(${2:params}) {\n\t${3:// body}\n}',
        description: 'Function declaration'
      },
      {
        prefix: 'arrow',
        body: 'const ${1:name} = (${2:params}) => {\n\t${3:// body}\n}',
        description: 'Arrow function'
      }
    ],
    python: [
      {
        prefix: 'def',
        body: 'def ${1:name}(${2:params}):\n\t${3:pass}',
        description: 'Function definition'
      },
      {
        prefix: 'class',
        body: 'class ${1:ClassName}:\n\tdef __init__(self${2:, params}):\n\t\t${3:pass}',
        description: 'Class definition'
      }
    ]
  }

  return snippets[language] || []
}