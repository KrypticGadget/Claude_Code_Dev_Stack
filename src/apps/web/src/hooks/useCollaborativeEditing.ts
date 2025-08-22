import { useState, useCallback, useRef, useEffect } from 'react'
import { Monaco } from '@monaco-editor/react'
import { editor } from 'monaco-editor'
import * as Y from 'yjs'
import { WebsocketProvider } from 'y-websocket'
import { MonacoBinding } from 'y-monaco'

export interface Collaborator {
  id: string
  name: string
  color: string
  cursor?: {
    line: number
    column: number
  }
  selection?: {
    startLine: number
    startColumn: number
    endLine: number
    endColumn: number
  }
  avatar?: string
  isActive: boolean
  lastSeen: Date
}

export interface CollaborativeSession {
  id: string
  name: string
  documentId: string
  participants: Collaborator[]
  isOwner: boolean
  permissions: 'read' | 'write' | 'admin'
}

export const useCollaborativeEditing = (enabled: boolean = false) => {
  const [isConnected, setIsConnected] = useState(false)
  const [collaborators, setCollaborators] = useState<Collaborator[]>([])
  const [currentSession, setCurrentSession] = useState<CollaborativeSession | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')

  const ydocRef = useRef<Y.Doc | null>(null)
  const providerRef = useRef<WebsocketProvider | null>(null)
  const bindingRef = useRef<MonacoBinding | null>(null)
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)
  const monacoRef = useRef<Monaco | null>(null)

  const setupCollaboration = useCallback(async (
    editorInstance: editor.IStandaloneCodeEditor,
    monacoInstance: Monaco,
    sessionId?: string,
    websocketUrl: string = 'ws://localhost:1234'
  ) => {
    if (!enabled) return

    try {
      setConnectionStatus('connecting')
      
      editorRef.current = editorInstance
      monacoRef.current = monacoInstance

      // Create Yjs document
      const ydoc = new Y.Doc()
      ydocRef.current = ydoc

      // Create WebSocket provider
      const provider = new WebsocketProvider(websocketUrl, sessionId || 'default-session', ydoc)
      providerRef.current = provider

      // Get the text type from the Yjs document
      const ytext = ydoc.getText('monaco')

      // Create Monaco binding
      const binding = new MonacoBinding(
        ytext,
        editorInstance.getModel()!,
        new Set([editorInstance]),
        provider.awareness
      )
      bindingRef.current = binding

      // Setup awareness (cursor and selection sharing)
      setupAwareness(provider, editorInstance, monacoInstance)

      // Setup connection event listeners
      provider.on('status', (event: { status: string }) => {
        setConnectionStatus(event.status as any)
        setIsConnected(event.status === 'connected')
      })

      provider.on('connection-close', () => {
        setConnectionStatus('disconnected')
        setIsConnected(false)
      })

      provider.on('connection-error', () => {
        setConnectionStatus('error')
        setIsConnected(false)
      })

      // Initialize session
      const session: CollaborativeSession = {
        id: sessionId || 'default-session',
        name: 'Collaborative Session',
        documentId: 'monaco-document',
        participants: [],
        isOwner: true, // This would be determined by the server
        permissions: 'admin'
      }
      setCurrentSession(session)

    } catch (error) {
      console.error('Failed to setup collaboration:', error)
      setConnectionStatus('error')
    }
  }, [enabled])

  const setupAwareness = (
    provider: WebsocketProvider,
    editorInstance: editor.IStandaloneCodeEditor,
    monacoInstance: Monaco
  ) => {
    const awareness = provider.awareness

    // Set local user info
    const localUser: Collaborator = {
      id: generateUserId(),
      name: 'You',
      color: generateUserColor(),
      isActive: true,
      lastSeen: new Date()
    }

    awareness.setLocalStateField('user', localUser)

    // Track cursor position
    editorInstance.onDidChangeCursorPosition((e) => {
      awareness.setLocalStateField('cursor', {
        line: e.position.lineNumber,
        column: e.position.column
      })
    })

    // Track selection
    editorInstance.onDidChangeCursorSelection((e) => {
      if (!e.selection.isEmpty()) {
        awareness.setLocalStateField('selection', {
          startLine: e.selection.startLineNumber,
          startColumn: e.selection.startColumn,
          endLine: e.selection.endLineNumber,
          endColumn: e.selection.endColumn
        })
      } else {
        awareness.setLocalStateField('selection', null)
      }
    })

    // Listen for awareness changes (other users)
    awareness.on('change', () => {
      const states = Array.from(awareness.getStates().values())
      const collaboratorsList: Collaborator[] = states
        .filter(state => state.user && state.user.id !== localUser.id)
        .map(state => ({
          ...state.user,
          cursor: state.cursor,
          selection: state.selection,
          lastSeen: new Date()
        }))

      setCollaborators(collaboratorsList)
      renderCollaboratorCursors(editorInstance, monacoInstance, collaboratorsList)
    })
  }

  const renderCollaboratorCursors = (
    editorInstance: editor.IStandaloneCodeEditor,
    monacoInstance: Monaco,
    collaboratorsList: Collaborator[]
  ) => {
    // Clear existing decorations
    const existingDecorations = editorInstance.getModel()?.getAllDecorations()
      ?.filter(d => d.options.className?.includes('collaborator'))
      ?.map(d => d.id) || []

    // Remove old decorations
    editorInstance.removeDecorations(existingDecorations)

    const newDecorations: editor.IModelDeltaDecoration[] = []

    collaboratorsList.forEach(collaborator => {
      // Render cursor
      if (collaborator.cursor) {
        newDecorations.push({
          range: new monacoInstance.Range(
            collaborator.cursor.line,
            collaborator.cursor.column,
            collaborator.cursor.line,
            collaborator.cursor.column
          ),
          options: {
            className: `collaborator-cursor-${collaborator.id}`,
            beforeContentClassName: `collaborator-cursor-line`,
            afterContentClassName: `collaborator-cursor-name`,
            after: {
              content: collaborator.name,
              inlineClassName: `collaborator-name-${collaborator.id}`
            },
            zIndex: 1000
          }
        })
      }

      // Render selection
      if (collaborator.selection) {
        newDecorations.push({
          range: new monacoInstance.Range(
            collaborator.selection.startLine,
            collaborator.selection.startColumn,
            collaborator.selection.endLine,
            collaborator.selection.endColumn
          ),
          options: {
            className: `collaborator-selection-${collaborator.id}`,
            inlineClassName: `collaborator-selection-inline`,
            backgroundColor: `${collaborator.color}33`, // 20% opacity
            borderColor: collaborator.color,
            borderWidth: '1px',
            borderStyle: 'solid'
          }
        })
      }
    })

    // Apply new decorations
    editorInstance.deltaDecorations([], newDecorations)

    // Inject CSS for collaborator styles
    injectCollaboratorStyles(collaboratorsList)
  }

  const injectCollaboratorStyles = (collaboratorsList: Collaborator[]) => {
    const styleId = 'collaborator-styles'
    let existingStyle = document.getElementById(styleId)
    
    if (existingStyle) {
      existingStyle.remove()
    }

    const style = document.createElement('style')
    style.id = styleId

    let css = `
      .collaborator-cursor-line {
        border-left: 2px solid;
        position: absolute;
        height: 1.2em;
        z-index: 1000;
      }
      
      .collaborator-selection-inline {
        position: relative;
        z-index: 999;
      }
    `

    collaboratorsList.forEach(collaborator => {
      css += `
        .collaborator-cursor-${collaborator.id} .collaborator-cursor-line {
          border-color: ${collaborator.color};
        }
        
        .collaborator-name-${collaborator.id} {
          background-color: ${collaborator.color};
          color: white;
          padding: 2px 4px;
          font-size: 11px;
          border-radius: 3px;
          position: absolute;
          top: -20px;
          left: 0;
          white-space: nowrap;
          z-index: 1001;
        }
        
        .collaborator-selection-${collaborator.id} {
          background-color: ${collaborator.color}33 !important;
        }
      `
    })

    style.textContent = css
    document.head.appendChild(style)
  }

  const joinSession = useCallback(async (sessionId: string, userInfo?: Partial<Collaborator>) => {
    if (!editorRef.current || !monacoRef.current) return

    await setupCollaboration(editorRef.current, monacoRef.current, sessionId)
    
    if (userInfo && providerRef.current) {
      const updatedUser = {
        ...userInfo,
        id: userInfo.id || generateUserId(),
        color: userInfo.color || generateUserColor(),
        isActive: true,
        lastSeen: new Date()
      }
      providerRef.current.awareness.setLocalStateField('user', updatedUser)
    }
  }, [setupCollaboration])

  const leaveSession = useCallback(() => {
    if (bindingRef.current) {
      bindingRef.current.destroy()
      bindingRef.current = null
    }

    if (providerRef.current) {
      providerRef.current.destroy()
      providerRef.current = null
    }

    if (ydocRef.current) {
      ydocRef.current.destroy()
      ydocRef.current = null
    }

    setIsConnected(false)
    setCollaborators([])
    setCurrentSession(null)
    setConnectionStatus('disconnected')
  }, [])

  const updateUserInfo = useCallback((userInfo: Partial<Collaborator>) => {
    if (providerRef.current) {
      const currentUser = providerRef.current.awareness.getLocalState()?.user || {}
      const updatedUser = {
        ...currentUser,
        ...userInfo,
        lastSeen: new Date()
      }
      providerRef.current.awareness.setLocalStateField('user', updatedUser)
    }
  }, [])

  const sendChatMessage = useCallback((message: string) => {
    if (providerRef.current && ydocRef.current) {
      const chatArray = ydocRef.current.getArray('chat')
      chatArray.push([{
        id: generateMessageId(),
        userId: providerRef.current.awareness.getLocalState()?.user?.id,
        message,
        timestamp: new Date().toISOString()
      }])
    }
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      leaveSession()
    }
  }, [leaveSession])

  return {
    setupCollaboration,
    joinSession,
    leaveSession,
    updateUserInfo,
    sendChatMessage,
    isConnected,
    collaborators,
    currentSession,
    connectionStatus,
    isCollaborationEnabled: enabled
  }
}

// Helper functions
const generateUserId = (): string => {
  return `user-${Math.random().toString(36).substr(2, 9)}`
}

const generateUserColor = (): string => {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

const generateMessageId = (): string => {
  return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}