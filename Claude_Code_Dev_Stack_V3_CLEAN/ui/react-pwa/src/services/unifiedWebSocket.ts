// Unified WebSocket Service for Real-time Updates
// Consolidates all WebSocket connections into one service

import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'

export interface WebSocketMessage {
  type: string
  payload: any
  timestamp: Date
}

export interface WebSocketState {
  connected: boolean
  reconnecting: boolean
  messages: WebSocketMessage[]
  agents: { active: number; total: number }
  tasks: { completed: number; total: number }
  hooks: { triggered: number; total: number }
  audio: { lastFile: string; playing: boolean }
  statusline: any
  diagnostics: any[]
}

interface WebSocketStore extends WebSocketState {
  ws: WebSocket | null
  connect: (url?: string) => void
  disconnect: () => void
  sendMessage: (type: string, payload: any) => void
  updateState: (updates: Partial<WebSocketState>) => void
}

const DEFAULT_WS_URL = 'ws://localhost:8000/ws'

export const useWebSocketStore = create<WebSocketStore>(
  subscribeWithSelector((set, get) => ({
    // Initial state
    connected: false,
    reconnecting: false,
    messages: [],
    agents: { active: 0, total: 28 },
    tasks: { completed: 0, total: 0 },
    hooks: { triggered: 0, total: 37 },
    audio: { lastFile: '', playing: false },
    statusline: null,
    diagnostics: [],
    ws: null,

    // Connect to WebSocket
    connect: (url = DEFAULT_WS_URL) => {
      const state = get()
      
      // Don't reconnect if already connected
      if (state.ws?.readyState === WebSocket.OPEN) {
        return
      }

      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('WebSocket connected')
        set({ connected: true, reconnecting: false, ws })
        
        // Send initial handshake
        ws.send(JSON.stringify({
          type: 'handshake',
          payload: {
            client: 'unified-pwa',
            version: '3.0.0',
            features: ['agents', 'hooks', 'audio', 'statusline', 'lsp', 'semantic']
          }
        }))
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          const timestamp = new Date()
          
          // Store message
          set(state => ({
            messages: [...state.messages.slice(-99), { ...message, timestamp }]
          }))

          // Update specific state based on message type
          switch (message.type) {
            case 'agent-update':
              set({ agents: message.payload })
              break
            case 'task-update':
              set({ tasks: message.payload })
              break
            case 'hook-update':
              set({ hooks: message.payload })
              break
            case 'audio-event':
              set({ audio: message.payload })
              break
            case 'statusline-update':
              set({ statusline: message.payload })
              break
            case 'diagnostic-update':
              set({ diagnostics: message.payload })
              break
            default:
              console.log('Unknown message type:', message.type)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        set({ connected: false, ws: null })
        
        // Auto-reconnect after 3 seconds
        if (!get().reconnecting) {
          set({ reconnecting: true })
          setTimeout(() => {
            get().connect(url)
          }, 3000)
        }
      }

      set({ ws })
    },

    // Disconnect from WebSocket
    disconnect: () => {
      const { ws } = get()
      if (ws) {
        ws.close()
        set({ ws: null, connected: false })
      }
    },

    // Send message through WebSocket
    sendMessage: (type: string, payload: any) => {
      const { ws, connected } = get()
      if (ws && connected) {
        ws.send(JSON.stringify({ type, payload }))
      } else {
        console.warn('Cannot send message: WebSocket not connected')
      }
    },

    // Update state manually
    updateState: (updates: Partial<WebSocketState>) => {
      set(updates)
    }
  }))
)

// Auto-connect on module load
if (typeof window !== 'undefined') {
  useWebSocketStore.getState().connect()
}

// Hooks for specific data
export const useAgents = () => useWebSocketStore(state => state.agents)
export const useTasks = () => useWebSocketStore(state => state.tasks)
export const useHooks = () => useWebSocketStore(state => state.hooks)
export const useAudio = () => useWebSocketStore(state => state.audio)
export const useStatusline = () => useWebSocketStore(state => state.statusline)
export const useDiagnostics = () => useWebSocketStore(state => state.diagnostics)
export const useWebSocketConnection = () => useWebSocketStore(state => ({
  connected: state.connected,
  reconnecting: state.reconnecting
}))