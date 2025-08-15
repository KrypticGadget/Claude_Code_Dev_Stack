/**
 * WebSocket service for Claude Code communication
 * Ported from Flutter WebSocketService (@9cat) - MIT License
 */

import { ConnectionConfig } from '../models/ConnectionConfig';

export interface WebSocketMessage {
  type: string;
  message?: string;
  data?: any;
  timestamp?: string;
  [key: string]: any;
}

export class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private currentConnection: ConnectionConfig | null = null;
  private authToken: string | null = null;
  private isConnected: boolean = false;
  private messageListeners: Set<(message: WebSocketMessage) => void> = new Set();
  private connectionListeners: Set<(connected: boolean) => void> = new Set();

  private constructor() {}

  static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  get connected(): boolean {
    return this.isConnected;
  }

  get connection(): ConnectionConfig | null {
    return this.currentConnection;
  }

  // Add message listener
  addMessageListener(listener: (message: WebSocketMessage) => void): void {
    this.messageListeners.add(listener);
  }

  // Remove message listener
  removeMessageListener(listener: (message: WebSocketMessage) => void): void {
    this.messageListeners.delete(listener);
  }

  // Add connection status listener
  addConnectionListener(listener: (connected: boolean) => void): void {
    this.connectionListeners.add(listener);
  }

  // Remove connection status listener
  removeConnectionListener(listener: (connected: boolean) => void): void {
    this.connectionListeners.delete(listener);
  }

  async connect(config: ConnectionConfig): Promise<boolean> {
    try {
      this.disconnect();

      // Create WebSocket URL
      let wsUrl = config.serverUrl.replace(/^http/, 'ws') + '/ws';
      
      // For development, handle localhost
      if (__DEV__ && wsUrl.includes('localhost')) {
        // Use the device's IP for real device testing
        wsUrl = wsUrl.replace('localhost', '10.0.2.2'); // Android emulator
      }

      console.log('🔗 WebSocketService: Connecting to', wsUrl);

      this.ws = new WebSocket(wsUrl);

      return new Promise((resolve, reject) => {
        if (!this.ws) {
          reject(new Error('Failed to create WebSocket'));
          return;
        }

        this.ws.onopen = () => {
          console.log('🔗 WebSocket connected');
          this.authenticateAndSetup(config, resolve, reject);
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            console.log('📨 WebSocketService: Received message:', message);
            this.handleIncomingMessage(message);
          } catch (error) {
            console.error('❌ WebSocketService: Error parsing message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('💥 WebSocket error:', error);
          this.handleConnectionError(error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('🔌 WebSocket connection closed');
          this.handleDisconnection();
        };

        // Connection timeout
        setTimeout(() => {
          if (!this.isConnected) {
            reject(new Error('Connection timeout'));
          }
        }, 10000);
      });
    } catch (error) {
      console.error('Connection failed:', error);
      this.disconnect();
      return false;
    }
  }

  private async authenticateAndSetup(
    config: ConnectionConfig,
    resolve: (value: boolean) => void,
    reject: (reason?: any) => void
  ): Promise<void> {
    const authTimeout = setTimeout(() => {
      reject(new Error('Authentication timeout'));
    }, 10000);

    // Listen for auth response
    const authListener = (message: WebSocketMessage) => {
      if (message.type === 'auth-success') {
        clearTimeout(authTimeout);
        this.removeMessageListener(authListener);
        this.authToken = message.token;
        this.currentConnection = { ...config, isConnected: true };
        this.isConnected = true;
        this.notifyConnectionListeners(true);
        resolve(true);
      } else if (message.type === 'error') {
        clearTimeout(authTimeout);
        this.removeMessageListener(authListener);
        console.error('Auth error:', message.message);
        reject(new Error(message.message || 'Authentication failed'));
      }
    };

    this.addMessageListener(authListener);

    // Wait a bit for WebSocket to be ready
    setTimeout(() => {
      // Send auth request
      console.log('🔐 Sending auth request for user:', config.username);
      this.sendMessage({
        type: 'auth',
        username: config.username,
        password: config.password,
      });
    }, 100);
  }

  private handleIncomingMessage(message: WebSocketMessage): void {
    // Add timestamp if not present
    if (!message.timestamp) {
      message.timestamp = new Date().toISOString();
    }

    // Notify all listeners
    this.messageListeners.forEach(listener => {
      try {
        listener(message);
      } catch (error) {
        console.error('Error in message listener:', error);
      }
    });
  }

  private handleConnectionError(error: any): void {
    const errorMessage: WebSocketMessage = {
      type: 'error',
      message: `Connection error: ${error}`,
      timestamp: new Date().toISOString(),
    };

    this.handleIncomingMessage(errorMessage);
  }

  private handleDisconnection(): void {
    this.isConnected = false;
    
    if (this.currentConnection) {
      this.currentConnection = { ...this.currentConnection, isConnected: false };
    }

    this.notifyConnectionListeners(false);

    const disconnectMessage: WebSocketMessage = {
      type: 'system',
      message: 'Disconnected from server',
      timestamp: new Date().toISOString(),
    };

    this.handleIncomingMessage(disconnectMessage);
  }

  private notifyConnectionListeners(connected: boolean): void {
    this.connectionListeners.forEach(listener => {
      try {
        listener(connected);
      } catch (error) {
        console.error('Error in connection listener:', error);
      }
    });
  }

  async sendCommand(command: string): Promise<void> {
    console.log('📤 WebSocketService: Sending command:', command);

    if (!this.isConnected || !this.ws) {
      throw new Error('Not connected to server');
    }

    const message: WebSocketMessage = {
      type: 'command',
      command: command,
    };

    this.sendMessage(message);
  }

  async startClaudeSession(): Promise<void> {
    if (!this.isConnected || !this.ws) {
      throw new Error('Not connected to server');
    }

    this.sendMessage({
      type: 'claude-start',
    });
  }

  private sendMessage(message: WebSocketMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('❌ Cannot send message: WebSocket not open');
      return;
    }

    try {
      const jsonString = JSON.stringify(message);
      this.ws.send(jsonString);
      console.log('📋 Message sent:', message);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }

  sendPing(): void {
    this.sendMessage({
      type: 'ping',
      timestamp: new Date().toISOString(),
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.authToken = null;
    this.isConnected = false;

    if (this.currentConnection) {
      this.currentConnection = { ...this.currentConnection, isConnected: false };
    }

    this.notifyConnectionListeners(false);
  }

  // Health check
  async checkHealth(serverUrl: string): Promise<boolean> {
    try {
      // Would implement actual HTTP health check here
      const response = await fetch(`${serverUrl}/health`, {
        method: 'GET',
        timeout: 5000,
      } as any);
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}