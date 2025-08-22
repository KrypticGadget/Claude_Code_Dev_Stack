#!/usr/bin/env node
/**
 * Context Preservation Client Library
 * Easy-to-use client for cross-agent context sharing
 */

const axios = require('axios');
const WebSocket = require('ws');
const EventEmitter = require('events');

class ContextClient extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.config = {
      baseUrl: options.baseUrl || process.env.CONTEXT_API_URL || 'http://localhost:3100',
      wsUrl: options.wsUrl || process.env.CONTEXT_WS_URL || 'ws://localhost:3100/context-ws',
      timeout: options.timeout || 30000,
      retries: options.retries || 3,
      retryDelay: options.retryDelay || 1000,
      autoReconnect: options.autoReconnect !== false,
      heartbeatInterval: options.heartbeatInterval || 30000
    };

    this.client = axios.create({
      baseURL: `${this.config.baseUrl}/api/context`,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    this.ws = null;
    this.isConnected = false;
    this.clientId = null;
    this.subscriptions = new Set();
    this.heartbeatTimer = null;
    this.reconnectTimer = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
  }

  /**
   * Initialize the client
   */
  async initialize() {
    try {
      // Test HTTP connection
      await this.healthCheck();
      
      // Initialize WebSocket if enabled
      if (this.config.wsUrl) {
        await this.connectWebSocket();
      }
      
      this.emit('initialized');
      return true;
      
    } catch (error) {
      console.error('Failed to initialize context client:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      throw new Error(`Context API health check failed: ${error.message}`);
    }
  }

  /**
   * Store context data
   */
  async store(key, data, options = {}) {
    try {
      const response = await this.retryRequest(() =>
        this.client.post('/store', { key, data, options })
      );
      
      this.emit('contextStored', { key, ...response.data });
      return response.data;
      
    } catch (error) {
      console.error('Failed to store context:', error);
      throw error;
    }
  }

  /**
   * Retrieve context data
   */
  async get(key, options = {}) {
    try {
      const response = await this.retryRequest(() =>
        this.client.get(`/get/${encodeURIComponent(key)}`, { params: options })
      );
      
      this.emit('contextRetrieved', { key, ...response.data });
      return response.data;
      
    } catch (error) {
      if (error.response?.status === 404) {
        return null;
      }
      console.error('Failed to get context:', error);
      throw error;
    }
  }

  /**
   * Update context data
   */
  async update(key, data, options = {}) {
    try {
      const response = await this.retryRequest(() =>
        this.client.put(`/update/${encodeURIComponent(key)}`, { data, options })
      );
      
      this.emit('contextUpdated', { key, ...response.data });
      return response.data;
      
    } catch (error) {
      console.error('Failed to update context:', error);
      throw error;
    }
  }

  /**
   * Delete context data
   */
  async delete(key) {
    try {
      const response = await this.retryRequest(() =>
        this.client.delete(`/delete/${encodeURIComponent(key)}`)
      );
      
      this.emit('contextDeleted', { key, ...response.data });
      return response.data;
      
    } catch (error) {
      console.error('Failed to delete context:', error);
      throw error;
    }
  }

  /**
   * Search contexts
   */
  async search(query, options = {}) {
    try {
      const response = await this.retryRequest(() =>
        this.client.post('/search', { query, options })
      );
      
      this.emit('contextSearched', { query, ...response.data });
      return response.data;
      
    } catch (error) {
      console.error('Failed to search contexts:', error);
      throw error;
    }
  }

  /**
   * Get analytics
   */
  async getAnalytics(options = {}) {
    try {
      const response = await this.retryRequest(() =>
        this.client.get('/analytics', { params: options })
      );
      
      return response.data.analytics;
      
    } catch (error) {
      console.error('Failed to get analytics:', error);
      throw error;
    }
  }

  /**
   * Batch operations
   */
  async batch(operations) {
    try {
      const response = await this.retryRequest(() =>
        this.client.post('/batch', { operations })
      );
      
      this.emit('batchCompleted', response.data);
      return response.data;
      
    } catch (error) {
      console.error('Failed to execute batch operations:', error);
      throw error;
    }
  }

  /**
   * Export contexts
   */
  async export(keys, format = 'json') {
    try {
      const response = await this.retryRequest(() =>
        this.client.post('/export', { keys, format })
      );
      
      return response.data.export;
      
    } catch (error) {
      console.error('Failed to export contexts:', error);
      throw error;
    }
  }

  /**
   * Import contexts
   */
  async import(contexts, overwrite = false) {
    try {
      const response = await this.retryRequest(() =>
        this.client.post('/import', { contexts, overwrite })
      );
      
      this.emit('contextsImported', response.data);
      return response.data;
      
    } catch (error) {
      console.error('Failed to import contexts:', error);
      throw error;
    }
  }

  /**
   * Connect to WebSocket
   */
  async connectWebSocket() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.wsUrl);

        this.ws.on('open', () => {
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          
          console.log('WebSocket connected');
          this.emit('connected');
          resolve();
        });

        this.ws.on('message', (data) => {
          try {
            const message = JSON.parse(data.toString());
            this.handleWebSocketMessage(message);
          } catch (error) {
            console.error('WebSocket message parsing error:', error);
          }
        });

        this.ws.on('close', () => {
          this.isConnected = false;
          this.stopHeartbeat();
          
          console.log('WebSocket disconnected');
          this.emit('disconnected');

          if (this.config.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        });

        this.ws.on('error', (error) => {
          console.error('WebSocket error:', error);
          this.emit('error', error);
          
          if (!this.isConnected) {
            reject(error);
          }
        });

        this.ws.on('pong', () => {
          // Heartbeat received
        });

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Handle WebSocket messages
   */
  handleWebSocketMessage(message) {
    switch (message.type) {
      case 'welcome':
        this.clientId = message.payload.clientId;
        console.log(`WebSocket client ID: ${this.clientId}`);
        break;

      case 'context-stored':
      case 'context-updated':
      case 'context-deleted':
        this.emit('contextChange', {
          type: message.type,
          ...message.payload
        });
        break;

      case 'context-data':
        this.emit('contextData', message.payload);
        break;

      case 'context-error':
        this.emit('contextError', message.payload);
        break;

      case 'heartbeat-ack':
        // Heartbeat acknowledged
        break;

      case 'subscription-ack':
        console.log(`Subscribed to context: ${message.payload.key}`);
        break;

      case 'unsubscription-ack':
        console.log(`Unsubscribed from context: ${message.payload.key}`);
        break;

      case 'error':
        console.error('WebSocket error:', message.payload);
        this.emit('error', new Error(message.payload.error));
        break;

      default:
        console.log('Unknown WebSocket message:', message);
    }
  }

  /**
   * Subscribe to context updates
   */
  subscribe(key) {
    if (!this.isConnected) {
      console.warn('WebSocket not connected, cannot subscribe');
      return false;
    }

    this.subscriptions.add(key);
    this.ws.send(JSON.stringify({
      type: 'subscribe-context',
      payload: { key }
    }));

    return true;
  }

  /**
   * Unsubscribe from context updates
   */
  unsubscribe(key) {
    if (!this.isConnected) {
      return false;
    }

    this.subscriptions.delete(key);
    this.ws.send(JSON.stringify({
      type: 'unsubscribe-context',
      payload: { key }
    }));

    return true;
  }

  /**
   * Get context via WebSocket
   */
  getViaWebSocket(key, options = {}) {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected');
    }

    this.ws.send(JSON.stringify({
      type: 'get-context',
      payload: { key, options }
    }));
  }

  /**
   * Start heartbeat
   */
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
        this.ws.ping();
        this.ws.send(JSON.stringify({
          type: 'heartbeat',
          payload: { timestamp: new Date().toISOString() }
        }));
      }
    }, this.config.heartbeatInterval);
  }

  /**
   * Stop heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * Schedule reconnection
   */
  scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    const delay = Math.min(
      this.config.retryDelay * Math.pow(2, this.reconnectAttempts),
      30000 // Max 30 seconds
    );

    this.reconnectTimer = setTimeout(async () => {
      this.reconnectAttempts++;
      console.log(`Attempting WebSocket reconnection (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

      try {
        await this.connectWebSocket();
        
        // Resubscribe to all contexts
        for (const key of this.subscriptions) {
          this.subscribe(key);
        }
        
      } catch (error) {
        console.error('Reconnection failed:', error);
      }
    }, delay);
  }

  /**
   * Retry HTTP requests
   */
  async retryRequest(requestFn, attempt = 1) {
    try {
      const response = await requestFn();
      return response;
    } catch (error) {
      if (attempt < this.config.retries && error.code !== 'ENOTFOUND') {
        const delay = this.config.retryDelay * Math.pow(2, attempt - 1);
        console.log(`Request failed, retrying in ${delay}ms (attempt ${attempt}/${this.config.retries})`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.retryRequest(requestFn, attempt + 1);
      }
      
      throw error;
    }
  }

  /**
   * Disconnect and cleanup
   */
  disconnect() {
    this.config.autoReconnect = false;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this.stopHeartbeat();

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.close();
    }

    this.isConnected = false;
    this.subscriptions.clear();
    
    this.emit('disconnected');
  }
}

/**
 * Convenience functions for quick operations
 */

// Create a default client instance
let defaultClient = null;

function getDefaultClient() {
  if (!defaultClient) {
    defaultClient = new ContextClient();
  }
  return defaultClient;
}

// Quick store function
async function storeContext(key, data, options = {}) {
  const client = getDefaultClient();
  if (!client.isConnected) {
    await client.initialize();
  }
  return client.store(key, data, options);
}

// Quick get function
async function getContext(key, options = {}) {
  const client = getDefaultClient();
  if (!client.isConnected) {
    await client.initialize();
  }
  return client.get(key, options);
}

// Quick update function
async function updateContext(key, data, options = {}) {
  const client = getDefaultClient();
  if (!client.isConnected) {
    await client.initialize();
  }
  return client.update(key, data, options);
}

// Quick delete function
async function deleteContext(key) {
  const client = getDefaultClient();
  if (!client.isConnected) {
    await client.initialize();
  }
  return client.delete(key);
}

// Quick search function
async function searchContexts(query, options = {}) {
  const client = getDefaultClient();
  if (!client.isConnected) {
    await client.initialize();
  }
  return client.search(query, options);
}

module.exports = {
  ContextClient,
  storeContext,
  getContext,
  updateContext,
  deleteContext,
  searchContexts,
  getDefaultClient
};

// CLI support
if (require.main === module) {
  const client = new ContextClient();
  
  // Example usage
  async function example() {
    try {
      await client.initialize();
      
      // Store some context
      await client.store('test-key', { 
        message: 'Hello from Context Client',
        timestamp: new Date().toISOString()
      });
      
      // Retrieve it
      const context = await client.get('test-key');
      console.log('Retrieved context:', context);
      
      // Subscribe to updates
      client.subscribe('test-key');
      
      // Listen for changes
      client.on('contextChange', (data) => {
        console.log('Context changed:', data);
      });
      
      // Update the context
      setTimeout(async () => {
        await client.update('test-key', {
          message: 'Updated message',
          timestamp: new Date().toISOString()
        });
      }, 2000);
      
    } catch (error) {
      console.error('Example failed:', error);
    }
  }
  
  example();
}