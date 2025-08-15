/**
 * WebSocket Hook for Dev Stack Integration
 * =======================================
 * 
 * Provides WebSocket connectivity to the Claude Code Browser adapter
 * and Dev Stack API for real-time monitoring and updates.
 */

import { useState, useEffect, useRef, useCallback } from 'react';

interface WebSocketOptions {
  reconnectInterval?: number;
  heartbeatInterval?: number;
  maxReconnectAttempts?: number;
}

interface WebSocketData {
  type: string;
  payload: any;
  timestamp?: number;
}

interface UseWebSocketReturn {
  data: WebSocketData | null;
  isConnected: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  send: (data: any) => void;
  reconnect: () => void;
}

export const useWebSocket = (
  url: string, 
  options: WebSocketOptions = {}
): UseWebSocketReturn => {
  const {
    reconnectInterval = 1000,
    heartbeatInterval = 30000,
    maxReconnectAttempts = 10
  } = options;

  const [data, setData] = useState<WebSocketData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  
  const websocketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const mountedRef = useRef(true);

  const clearTimeouts = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
  }, []);

  const startHeartbeat = useCallback(() => {
    if (heartbeatInterval > 0) {
      heartbeatTimeoutRef.current = setTimeout(() => {
        if (websocketRef.current?.readyState === WebSocket.OPEN) {
          websocketRef.current.send(JSON.stringify({ type: 'ping' }));
          startHeartbeat(); // Schedule next heartbeat
        }
      }, heartbeatInterval);
    }
  }, [heartbeatInterval]);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    try {
      setConnectionState('connecting');
      websocketRef.current = new WebSocket(url);

      websocketRef.current.onopen = () => {
        if (!mountedRef.current) return;
        
        console.log('🔌 WebSocket connected to', url);
        setIsConnected(true);
        setConnectionState('connected');
        reconnectAttemptsRef.current = 0;
        startHeartbeat();
      };

      websocketRef.current.onmessage = (event) => {
        if (!mountedRef.current) return;
        
        try {
          const parsedData = JSON.parse(event.data);
          
          // Handle pong responses
          if (parsedData.type === 'pong') {
            return;
          }
          
          setData(parsedData);
        } catch (error) {
          console.warn('Failed to parse WebSocket message:', event.data);
        }
      };

      websocketRef.current.onclose = (event) => {
        if (!mountedRef.current) return;
        
        console.log('🔌 WebSocket disconnected from', url, event.code, event.reason);
        setIsConnected(false);
        setConnectionState('disconnected');
        clearTimeouts();
        
        // Auto-reconnect if not a manual close
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1), 30000);
          
          console.log(`🔄 Attempting to reconnect in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              connect();
            }
          }, delay);
        }
      };

      websocketRef.current.onerror = (error) => {
        if (!mountedRef.current) return;
        
        console.error('🔌 WebSocket error:', error);
        setConnectionState('error');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionState('error');
    }
  }, [url, reconnectInterval, maxReconnectAttempts, startHeartbeat, clearTimeouts]);

  const disconnect = useCallback(() => {
    clearTimeouts();
    
    if (websocketRef.current) {
      websocketRef.current.close(1000, 'Manual disconnect');
      websocketRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionState('disconnected');
  }, [clearTimeouts]);

  const send = useCallback((data: any) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        websocketRef.current.send(message);
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
      }
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setTimeout(connect, 100); // Small delay before reconnecting
  }, [disconnect, connect]);

  // Initial connection
  useEffect(() => {
    connect();
    
    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return {
    data,
    isConnected,
    connectionState,
    send,
    reconnect
  };
};