import { useState, useEffect, useRef, useCallback } from 'react'

interface WebSocketOptions {
  reconnectInterval?: number
  heartbeatInterval?: number
  maxReconnectAttempts?: number
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
}

interface WebSocketReturn {
  data: any
  isConnected: boolean
  send: (data: any) => void
  close: () => void
  reconnect: () => void
}

export function useWebSocket(url: string, options: WebSocketOptions = {}): WebSocketReturn {
  const {
    reconnectInterval = 1000,
    heartbeatInterval = 30000,
    maxReconnectAttempts = 5,
    onOpen,
    onClose,
    onError
  } = options

  const [data, setData] = useState<any>(null)
  const [isConnected, setIsConnected] = useState(false)
  const websocketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url)
      websocketRef.current = ws

      ws.onopen = () => {
        console.log('✅ WebSocket connected')
        setIsConnected(true)
        reconnectAttemptsRef.current = 0
        onOpen?.()
        
        // Start heartbeat
        if (heartbeatInterval > 0) {
          heartbeatTimeoutRef.current = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: 'ping' }))
            }
          }, heartbeatInterval)
        }
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          setData(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
          setData(event.data)
        }
      }

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected')
        setIsConnected(false)
        onClose?.()
        
        // Clear heartbeat
        if (heartbeatTimeoutRef.current) {
          clearInterval(heartbeatTimeoutRef.current)
          heartbeatTimeoutRef.current = null
        }
        
        // Attempt reconnection if within max attempts
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++
          console.log(`🔄 Attempting reconnection ${reconnectAttemptsRef.current}/${maxReconnectAttempts}`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval * reconnectAttemptsRef.current) // Exponential backoff
        } else {
          console.error('❌ Max reconnection attempts reached')
        }
      }

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        onError?.(error)
      }

    } catch (error) {
      console.error('❌ Failed to create WebSocket connection:', error)
    }
  }, [url, reconnectInterval, heartbeatInterval, maxReconnectAttempts, onOpen, onClose, onError])

  const send = useCallback((message: any) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      const data = typeof message === 'string' ? message : JSON.stringify(message)
      websocketRef.current.send(data)
    } else {
      console.warn('⚠️ WebSocket is not connected. Message not sent:', message)
    }
  }, [])

  const close = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (heartbeatTimeoutRef.current) {
      clearInterval(heartbeatTimeoutRef.current)
      heartbeatTimeoutRef.current = null
    }
    
    websocketRef.current?.close()
    websocketRef.current = null
    reconnectAttemptsRef.current = maxReconnectAttempts // Prevent reconnection
  }, [maxReconnectAttempts])

  const reconnect = useCallback(() => {
    close()
    reconnectAttemptsRef.current = 0
    connect()
  }, [close, connect])

  useEffect(() => {
    connect()
    
    return () => {
      close()
    }
  }, [connect, close])

  return {
    data,
    isConnected,
    send,
    close,
    reconnect
  }
}