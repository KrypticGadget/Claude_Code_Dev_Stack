import { useState, useCallback, useRef } from 'react'
import { Monaco } from '@monaco-editor/react'
import { editor } from 'monaco-editor'

export interface Breakpoint {
  id: string
  line: number
  column?: number
  condition?: string
  hitCondition?: string
  logMessage?: string
  enabled: boolean
  verified: boolean
}

export interface DebugSession {
  id: string
  name: string
  type: 'node' | 'browser' | 'python' | 'go' | 'rust'
  status: 'stopped' | 'running' | 'paused' | 'terminated'
  currentLine?: number
  currentFrame?: StackFrame
  callStack: StackFrame[]
  variables: Variable[]
  threads: Thread[]
}

export interface StackFrame {
  id: string
  name: string
  source: string
  line: number
  column: number
}

export interface Variable {
  name: string
  value: string
  type: string
  variablesReference?: number
  evaluateName?: string
  children?: Variable[]
}

export interface Thread {
  id: number
  name: string
  running: boolean
}

export const useDebugger = (enabled: boolean = false) => {
  const [breakpoints, setBreakpoints] = useState<Map<string, Breakpoint[]>>(new Map())
  const [currentSession, setCurrentSession] = useState<DebugSession | null>(null)
  const [isDebugging, setIsDebugging] = useState(false)
  const [debugOutput, setDebugOutput] = useState<string[]>([])

  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)
  const monacoRef = useRef<Monaco | null>(null)
  const debugAdapterRef = useRef<WebSocket | null>(null)

  const setupDebugger = useCallback(async (
    editorInstance: editor.IStandaloneCodeEditor,
    monacoInstance: Monaco,
    debugAdapterUrl?: string
  ) => {
    if (!enabled) return

    editorRef.current = editorInstance
    monacoRef.current = monacoInstance

    // Setup breakpoint decorations
    setupBreakpointDecorations(editorInstance, monacoInstance)

    // Setup debug adapter connection
    if (debugAdapterUrl) {
      await setupDebugAdapter(debugAdapterUrl)
    }

    // Add debug-specific key bindings
    setupDebugKeyBindings(editorInstance, monacoInstance)

  }, [enabled])

  const setupBreakpointDecorations = (
    editorInstance: editor.IStandaloneCodeEditor,
    monacoInstance: Monaco
  ) => {
    // Add breakpoint gutter click handler
    editorInstance.onMouseDown((e) => {
      if (e.target.type === monacoInstance.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        const line = e.target.position?.lineNumber
        if (line) {
          toggleBreakpoint(line)
        }
      }
    })

    // Add context menu for breakpoints
    editorInstance.addAction({
      id: 'toggle-breakpoint',
      label: 'Toggle Breakpoint',
      contextMenuGroupId: 'debug',
      contextMenuOrder: 1,
      run: () => {
        const position = editorInstance.getPosition()
        if (position) {
          toggleBreakpoint(position.lineNumber)
        }
      }
    })

    editorInstance.addAction({
      id: 'add-conditional-breakpoint',
      label: 'Add Conditional Breakpoint',
      contextMenuGroupId: 'debug',
      contextMenuOrder: 2,
      run: () => {
        const position = editorInstance.getPosition()
        if (position) {
          addConditionalBreakpoint(position.lineNumber)
        }
      }
    })

    editorInstance.addAction({
      id: 'add-logpoint',
      label: 'Add Logpoint',
      contextMenuGroupId: 'debug',
      contextMenuOrder: 3,
      run: () => {
        const position = editorInstance.getPosition()
        if (position) {
          addLogpoint(position.lineNumber)
        }
      }
    })
  }

  const setupDebugAdapter = async (debugAdapterUrl: string) => {
    try {
      const ws = new WebSocket(debugAdapterUrl)
      debugAdapterRef.current = ws

      ws.onopen = () => {
        console.log('Debug adapter connected')
        // Initialize debug adapter
        sendDebugRequest('initialize', {
          clientID: 'monaco-editor',
          clientName: 'Monaco Editor',
          adapterID: 'node',
          pathFormat: 'path',
          linesStartAt1: true,
          columnsStartAt1: true,
          supportsVariableType: true,
          supportsVariablePaging: true,
          supportsRunInTerminalRequest: true
        })
      }

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        handleDebugMessage(message)
      }

      ws.onerror = (error) => {
        console.error('Debug adapter error:', error)
      }

      ws.onclose = () => {
        console.log('Debug adapter disconnected')
        setCurrentSession(null)
        setIsDebugging(false)
      }

    } catch (error) {
      console.error('Failed to connect to debug adapter:', error)
    }
  }

  const setupDebugKeyBindings = (
    editorInstance: editor.IStandaloneCodeEditor,
    monacoInstance: Monaco
  ) => {
    // F5 - Start/Continue debugging
    editorInstance.addCommand(monacoInstance.KeyCode.F5, () => {
      if (isDebugging) {
        continueExecution()
      } else {
        startDebugging()
      }
    })

    // F9 - Toggle breakpoint
    editorInstance.addCommand(monacoInstance.KeyCode.F9, () => {
      const position = editorInstance.getPosition()
      if (position) {
        toggleBreakpoint(position.lineNumber)
      }
    })

    // F10 - Step over
    editorInstance.addCommand(monacoInstance.KeyCode.F10, () => {
      stepOver()
    })

    // F11 - Step into
    editorInstance.addCommand(monacoInstance.KeyCode.F11, () => {
      stepInto()
    })

    // Shift+F11 - Step out
    editorInstance.addCommand(monacoInstance.KeyMod.Shift | monacoInstance.KeyCode.F11, () => {
      stepOut()
    })

    // Shift+F5 - Stop debugging
    editorInstance.addCommand(monacoInstance.KeyMod.Shift | monacoInstance.KeyCode.F5, () => {
      stopDebugging()
    })
  }

  const toggleBreakpoint = useCallback((line: number) => {
    if (!editorRef.current || !monacoRef.current) return

    const model = editorRef.current.getModel()
    if (!model) return

    const uri = model.uri.toString()
    const currentBreakpoints = breakpoints.get(uri) || []
    const existingIndex = currentBreakpoints.findIndex(bp => bp.line === line)

    let newBreakpoints: Breakpoint[]
    
    if (existingIndex >= 0) {
      // Remove existing breakpoint
      newBreakpoints = currentBreakpoints.filter((_, index) => index !== existingIndex)
    } else {
      // Add new breakpoint
      const newBreakpoint: Breakpoint = {
        id: `bp-${Date.now()}`,
        line,
        enabled: true,
        verified: false
      }
      newBreakpoints = [...currentBreakpoints, newBreakpoint]
    }

    setBreakpoints(prev => new Map(prev.set(uri, newBreakpoints)))
    updateBreakpointDecorations(uri, newBreakpoints)

    // Send breakpoint update to debug adapter
    if (debugAdapterRef.current && debugAdapterRef.current.readyState === WebSocket.OPEN) {
      sendDebugRequest('setBreakpoints', {
        source: { path: uri },
        breakpoints: newBreakpoints.map(bp => ({
          line: bp.line,
          condition: bp.condition,
          hitCondition: bp.hitCondition,
          logMessage: bp.logMessage
        }))
      })
    }
  }, [breakpoints])

  const addConditionalBreakpoint = useCallback((line: number) => {
    const condition = prompt('Enter breakpoint condition:')
    if (condition && editorRef.current) {
      const model = editorRef.current.getModel()
      if (!model) return

      const uri = model.uri.toString()
      const currentBreakpoints = breakpoints.get(uri) || []
      const newBreakpoint: Breakpoint = {
        id: `bp-${Date.now()}`,
        line,
        condition,
        enabled: true,
        verified: false
      }

      const newBreakpoints = [...currentBreakpoints.filter(bp => bp.line !== line), newBreakpoint]
      setBreakpoints(prev => new Map(prev.set(uri, newBreakpoints)))
      updateBreakpointDecorations(uri, newBreakpoints)
    }
  }, [breakpoints])

  const addLogpoint = useCallback((line: number) => {
    const logMessage = prompt('Enter log message (use {} for variable substitution):')
    if (logMessage && editorRef.current) {
      const model = editorRef.current.getModel()
      if (!model) return

      const uri = model.uri.toString()
      const currentBreakpoints = breakpoints.get(uri) || []
      const newBreakpoint: Breakpoint = {
        id: `bp-${Date.now()}`,
        line,
        logMessage,
        enabled: true,
        verified: false
      }

      const newBreakpoints = [...currentBreakpoints.filter(bp => bp.line !== line), newBreakpoint]
      setBreakpoints(prev => new Map(prev.set(uri, newBreakpoints)))
      updateBreakpointDecorations(uri, newBreakpoints)
    }
  }, [breakpoints])

  const updateBreakpointDecorations = (uri: string, fileBreakpoints: Breakpoint[]) => {
    if (!editorRef.current || !monacoRef.current) return

    const model = editorRef.current.getModel()
    if (!model || model.uri.toString() !== uri) return

    // Clear existing breakpoint decorations
    const existingDecorations = model.getAllDecorations()
      .filter(d => d.options.glyphMarginClassName?.includes('breakpoint'))
      .map(d => d.id)

    // Create new decorations
    const newDecorations: editor.IModelDeltaDecoration[] = fileBreakpoints.map(bp => ({
      range: new monacoRef.current!.Range(bp.line, 1, bp.line, 1),
      options: {
        glyphMarginClassName: bp.enabled 
          ? (bp.verified ? 'breakpoint-enabled' : 'breakpoint-unverified')
          : 'breakpoint-disabled',
        glyphMarginHoverMessage: {
          value: getBreakpointHoverMessage(bp)
        }
      }
    }))

    editorRef.current.deltaDecorations(existingDecorations, newDecorations)
  }

  const startDebugging = useCallback(async (config?: any) => {
    if (!debugAdapterRef.current) return

    setIsDebugging(true)
    setDebugOutput([])

    const debugConfig = config || {
      type: 'node',
      request: 'launch',
      name: 'Debug Current File',
      program: '${workspaceFolder}/app.js',
      console: 'integratedTerminal'
    }

    sendDebugRequest('launch', debugConfig)
  }, [])

  const stopDebugging = useCallback(() => {
    if (debugAdapterRef.current && currentSession) {
      sendDebugRequest('disconnect', {})
    }
    setIsDebugging(false)
    setCurrentSession(null)
    clearDebugDecorations()
  }, [currentSession])

  const continueExecution = useCallback(() => {
    if (currentSession) {
      sendDebugRequest('continue', { threadId: currentSession.threads[0]?.id })
    }
  }, [currentSession])

  const stepOver = useCallback(() => {
    if (currentSession) {
      sendDebugRequest('next', { threadId: currentSession.threads[0]?.id })
    }
  }, [currentSession])

  const stepInto = useCallback(() => {
    if (currentSession) {
      sendDebugRequest('stepIn', { threadId: currentSession.threads[0]?.id })
    }
  }, [currentSession])

  const stepOut = useCallback(() => {
    if (currentSession) {
      sendDebugRequest('stepOut', { threadId: currentSession.threads[0]?.id })
    }
  }, [currentSession])

  const evaluateExpression = useCallback(async (expression: string): Promise<string> => {
    if (!currentSession) return 'No active debug session'

    return new Promise((resolve) => {
      const requestId = Date.now()
      sendDebugRequest('evaluate', {
        expression,
        frameId: currentSession.currentFrame?.id,
        context: 'watch'
      }, requestId)

      // Store resolver for response handling
      // This would typically be managed by a request/response mapping
      setTimeout(() => resolve('Evaluation timeout'), 5000)
    })
  }, [currentSession])

  const sendDebugRequest = (command: string, args?: any, seq?: number) => {
    if (!debugAdapterRef.current) return

    const request = {
      seq: seq || Date.now(),
      type: 'request',
      command,
      arguments: args
    }

    debugAdapterRef.current.send(JSON.stringify(request))
  }

  const handleDebugMessage = (message: any) => {
    switch (message.type) {
      case 'response':
        handleDebugResponse(message)
        break
      case 'event':
        handleDebugEvent(message)
        break
    }
  }

  const handleDebugResponse = (response: any) => {
    if (response.success) {
      switch (response.command) {
        case 'initialize':
          sendDebugRequest('configurationDone')
          break
        case 'setBreakpoints':
          // Update breakpoint verification status
          const breakpointResponses = response.body?.breakpoints || []
          // Update breakpoints with verification status
          break
      }
    } else {
      console.error('Debug response error:', response.message)
    }
  }

  const handleDebugEvent = (event: any) => {
    switch (event.event) {
      case 'stopped':
        handleStoppedEvent(event)
        break
      case 'continued':
        clearDebugDecorations()
        break
      case 'terminated':
        stopDebugging()
        break
      case 'output':
        setDebugOutput(prev => [...prev, event.body.output])
        break
    }
  }

  const handleStoppedEvent = (event: any) => {
    const { threadId, reason } = event.body

    // Request stack trace
    sendDebugRequest('stackTrace', { threadId })
    
    // Request variable information
    sendDebugRequest('scopes', { frameId: 0 })

    // Update current line decoration
    updateCurrentLineDecoration(event.body.line)
  }

  const updateCurrentLineDecoration = (line: number) => {
    if (!editorRef.current || !monacoRef.current) return

    const decorations: editor.IModelDeltaDecoration[] = [{
      range: new monacoRef.current.Range(line, 1, line, 1),
      options: {
        isWholeLine: true,
        className: 'debug-current-line',
        glyphMarginClassName: 'debug-current-line-glyph'
      }
    }]

    editorRef.current.deltaDecorations([], decorations)
  }

  const clearDebugDecorations = () => {
    if (!editorRef.current) return

    const decorations = editorRef.current.getModel()?.getAllDecorations()
      ?.filter(d => 
        d.options.className?.includes('debug-current-line') ||
        d.options.glyphMarginClassName?.includes('debug-current-line')
      )
      ?.map(d => d.id) || []

    editorRef.current.deltaDecorations(decorations, [])
  }

  const getBreakpointHoverMessage = (breakpoint: Breakpoint): string => {
    let message = `Breakpoint - Line ${breakpoint.line}`
    
    if (breakpoint.condition) {
      message += `\nCondition: ${breakpoint.condition}`
    }
    
    if (breakpoint.logMessage) {
      message += `\nLog Message: ${breakpoint.logMessage}`
    }
    
    if (!breakpoint.verified) {
      message += '\n⚠️ Unverified breakpoint'
    }
    
    return message
  }

  return {
    setupDebugger,
    breakpoints,
    currentSession,
    isDebugging,
    debugOutput,
    toggleBreakpoint,
    addConditionalBreakpoint,
    addLogpoint,
    startDebugging,
    stopDebugging,
    continueExecution,
    stepOver,
    stepInto,
    stepOut,
    evaluateExpression,
    isDebuggerEnabled: enabled
  }
}