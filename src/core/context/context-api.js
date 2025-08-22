#!/usr/bin/env node
/**
 * Context Preservation API Server
 * RESTful API with WebSocket support for context operations
 */

const express = require('express');
const { createServer } = require('http');
const { WebSocketServer } = require('ws');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const compression = require('compression');
const ContextManager = require('./context-manager');

class ContextAPI {
  constructor(options = {}) {
    this.app = express();
    this.server = createServer(this.app);
    this.wss = new WebSocketServer({ server: this.server, path: '/context-ws' });
    
    this.config = {
      port: options.port || process.env.CONTEXT_API_PORT || 3100,
      cors: {
        origin: options.corsOrigin || process.env.CORS_ORIGIN || '*',
        credentials: true
      },
      rateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 1000, // limit each IP to 1000 requests per windowMs
        standardHeaders: true,
        legacyHeaders: false
      },
      websocket: {
        heartbeatInterval: 30000, // 30 seconds
        maxConnections: 1000
      }
    };

    this.contextManager = new ContextManager(options);
    this.clients = new Map();
    this.isInitialized = false;
    
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
  }

  /**
   * Setup Express middleware
   */
  setupMiddleware() {
    // Security middleware
    this.app.use(helmet({
      contentSecurityPolicy: false,
      crossOriginEmbedderPolicy: false
    }));
    
    // CORS
    this.app.use(cors(this.config.cors));
    
    // Rate limiting
    this.app.use('/api/context', rateLimit(this.config.rateLimit));
    
    // Compression
    this.app.use(compression());
    
    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    
    // Request logging
    this.app.use((req, res, next) => {
      console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
      next();
    });
    
    // Error handling
    this.app.use((err, req, res, next) => {
      console.error('API Error:', err);
      res.status(500).json({
        success: false,
        error: 'Internal server error',
        message: err.message
      });
    });
  }

  /**
   * Setup API routes
   */
  setupRoutes() {
    const router = express.Router();

    // Health check
    router.get('/health', (req, res) => {
      res.json({
        success: true,
        status: 'healthy',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        connections: this.clients.size,
        initialized: this.isInitialized
      });
    });

    // Store context
    router.post('/store', async (req, res) => {
      try {
        const { key, data, options = {} } = req.body;
        
        if (!key || !data) {
          return res.status(400).json({
            success: false,
            error: 'Missing required fields: key, data'
          });
        }

        const result = await this.contextManager.storeContext(key, data, options);
        
        // Broadcast to WebSocket clients
        this.broadcast('context-stored', { key, contextId: result.contextId });
        
        res.json({
          success: true,
          ...result
        });
        
      } catch (error) {
        console.error('Store context error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Retrieve context
    router.get('/get/:key', async (req, res) => {
      try {
        const { key } = req.params;
        const options = {
          version: req.query.version ? parseInt(req.query.version) : undefined
        };

        const result = await this.contextManager.getContext(key, options);
        
        if (!result) {
          return res.status(404).json({
            success: false,
            error: 'Context not found'
          });
        }

        res.json({
          success: true,
          ...result
        });
        
      } catch (error) {
        console.error('Get context error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Update context
    router.put('/update/:key', async (req, res) => {
      try {
        const { key } = req.params;
        const { data, options = {} } = req.body;
        
        if (!data) {
          return res.status(400).json({
            success: false,
            error: 'Missing required field: data'
          });
        }

        const result = await this.contextManager.updateContext(key, data, options);
        
        // Broadcast to WebSocket clients
        this.broadcast('context-updated', { key, version: result.version });
        
        res.json({
          success: true,
          ...result
        });
        
      } catch (error) {
        console.error('Update context error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Delete context
    router.delete('/delete/:key', async (req, res) => {
      try {
        const { key } = req.params;
        const result = await this.contextManager.deleteContext(key);
        
        // Broadcast to WebSocket clients
        this.broadcast('context-deleted', { key });
        
        res.json({
          success: true,
          ...result
        });
        
      } catch (error) {
        console.error('Delete context error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Search contexts
    router.post('/search', async (req, res) => {
      try {
        const { query, options = {} } = req.body;
        
        if (!query) {
          return res.status(400).json({
            success: false,
            error: 'Missing required field: query'
          });
        }

        const result = await this.contextManager.searchContexts(query, options);
        
        res.json({
          success: true,
          ...result
        });
        
      } catch (error) {
        console.error('Search contexts error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get analytics
    router.get('/analytics', async (req, res) => {
      try {
        const options = {
          sessionId: req.query.sessionId,
          agentId: req.query.agentId
        };

        const result = await this.contextManager.getAnalytics(options);
        
        res.json({
          success: true,
          analytics: result
        });
        
      } catch (error) {
        console.error('Get analytics error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Batch operations
    router.post('/batch', async (req, res) => {
      try {
        const { operations } = req.body;
        
        if (!Array.isArray(operations)) {
          return res.status(400).json({
            success: false,
            error: 'Operations must be an array'
          });
        }

        const results = [];
        
        for (const operation of operations) {
          try {
            let result;
            
            switch (operation.type) {
              case 'store':
                result = await this.contextManager.storeContext(
                  operation.key, 
                  operation.data, 
                  operation.options
                );
                break;
                
              case 'get':
                result = await this.contextManager.getContext(
                  operation.key, 
                  operation.options
                );
                break;
                
              case 'update':
                result = await this.contextManager.updateContext(
                  operation.key, 
                  operation.data, 
                  operation.options
                );
                break;
                
              case 'delete':
                result = await this.contextManager.deleteContext(
                  operation.key, 
                  operation.options
                );
                break;
                
              default:
                result = { error: `Unknown operation type: ${operation.type}` };
            }
            
            results.push({
              operation: operation.type,
              key: operation.key,
              success: !result.error,
              ...result
            });
            
          } catch (error) {
            results.push({
              operation: operation.type,
              key: operation.key,
              success: false,
              error: error.message
            });
          }
        }

        res.json({
          success: true,
          results,
          completed: results.filter(r => r.success).length,
          failed: results.filter(r => !r.success).length
        });
        
      } catch (error) {
        console.error('Batch operations error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get context relationships
    router.get('/relationships/:key', async (req, res) => {
      try {
        const { key } = req.params;
        // Implementation would query context_relationships table
        res.json({
          success: true,
          relationships: []
        });
        
      } catch (error) {
        console.error('Get relationships error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Export contexts
    router.post('/export', async (req, res) => {
      try {
        const { keys, format = 'json' } = req.body;
        
        const contexts = [];
        for (const key of keys || []) {
          const context = await this.contextManager.getContext(key);
          if (context) {
            contexts.push(context);
          }
        }

        if (format === 'json') {
          res.json({
            success: true,
            export: {
              timestamp: new Date().toISOString(),
              contexts,
              count: contexts.length
            }
          });
        } else {
          res.status(400).json({
            success: false,
            error: 'Unsupported export format'
          });
        }
        
      } catch (error) {
        console.error('Export contexts error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Import contexts
    router.post('/import', async (req, res) => {
      try {
        const { contexts, overwrite = false } = req.body;
        
        if (!Array.isArray(contexts)) {
          return res.status(400).json({
            success: false,
            error: 'Contexts must be an array'
          });
        }

        const results = [];
        
        for (const context of contexts) {
          try {
            const existing = await this.contextManager.getContext(context.key);
            
            if (existing && !overwrite) {
              results.push({
                key: context.key,
                success: false,
                error: 'Context already exists'
              });
              continue;
            }
            
            const result = await this.contextManager.storeContext(
              context.key, 
              context.data, 
              context.options || {}
            );
            
            results.push({
              key: context.key,
              success: true,
              contextId: result.contextId
            });
            
          } catch (error) {
            results.push({
              key: context.key,
              success: false,
              error: error.message
            });
          }
        }

        res.json({
          success: true,
          results,
          imported: results.filter(r => r.success).length,
          failed: results.filter(r => !r.success).length
        });
        
      } catch (error) {
        console.error('Import contexts error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.use('/api/context', router);
  }

  /**
   * Setup WebSocket server
   */
  setupWebSocket() {
    this.wss.on('connection', (ws, req) => {
      const clientId = this.generateClientId();
      const clientInfo = {
        id: clientId,
        ws,
        ip: req.socket.remoteAddress,
        userAgent: req.headers['user-agent'],
        connectedAt: new Date(),
        lastHeartbeat: new Date()
      };

      this.clients.set(clientId, clientInfo);
      console.log(`WebSocket client connected: ${clientId}`);

      // Send welcome message
      ws.send(JSON.stringify({
        type: 'welcome',
        payload: {
          clientId,
          timestamp: new Date().toISOString(),
          features: ['real-time-updates', 'batch-operations', 'context-search']
        }
      }));

      // Handle messages
      ws.on('message', async (message) => {
        try {
          const data = JSON.parse(message.toString());
          await this.handleWebSocketMessage(clientId, data);
        } catch (error) {
          console.error('WebSocket message error:', error);
          ws.send(JSON.stringify({
            type: 'error',
            payload: { error: error.message }
          }));
        }
      });

      // Handle heartbeat
      ws.on('pong', () => {
        if (this.clients.has(clientId)) {
          this.clients.get(clientId).lastHeartbeat = new Date();
        }
      });

      // Handle disconnect
      ws.on('close', () => {
        this.clients.delete(clientId);
        console.log(`WebSocket client disconnected: ${clientId}`);
      });

      // Handle errors
      ws.on('error', (error) => {
        console.error(`WebSocket error for client ${clientId}:`, error);
        this.clients.delete(clientId);
      });
    });

    // Start heartbeat interval
    setInterval(() => {
      this.heartbeat();
    }, this.config.websocket.heartbeatInterval);
  }

  /**
   * Handle WebSocket messages
   */
  async handleWebSocketMessage(clientId, data) {
    const client = this.clients.get(clientId);
    if (!client) return;

    switch (data.type) {
      case 'heartbeat':
        client.ws.send(JSON.stringify({
          type: 'heartbeat-ack',
          payload: { timestamp: new Date().toISOString() }
        }));
        break;

      case 'subscribe-context':
        // Subscribe to context updates
        client.subscriptions = client.subscriptions || new Set();
        client.subscriptions.add(data.payload.key);
        client.ws.send(JSON.stringify({
          type: 'subscription-ack',
          payload: { key: data.payload.key }
        }));
        break;

      case 'unsubscribe-context':
        // Unsubscribe from context updates
        if (client.subscriptions) {
          client.subscriptions.delete(data.payload.key);
        }
        client.ws.send(JSON.stringify({
          type: 'unsubscription-ack',
          payload: { key: data.payload.key }
        }));
        break;

      case 'get-context':
        try {
          const result = await this.contextManager.getContext(data.payload.key, data.payload.options);
          client.ws.send(JSON.stringify({
            type: 'context-data',
            payload: { key: data.payload.key, result }
          }));
        } catch (error) {
          client.ws.send(JSON.stringify({
            type: 'context-error',
            payload: { key: data.payload.key, error: error.message }
          }));
        }
        break;

      default:
        client.ws.send(JSON.stringify({
          type: 'unknown-message',
          payload: { type: data.type }
        }));
    }
  }

  /**
   * Broadcast message to all or specific clients
   */
  broadcast(type, payload, filter = null) {
    const message = JSON.stringify({
      type,
      payload: {
        ...payload,
        timestamp: new Date().toISOString()
      }
    });

    this.clients.forEach((client, clientId) => {
      try {
        if (client.ws.readyState === 1) { // OPEN
          if (!filter || filter(client)) {
            client.ws.send(message);
          }
        }
      } catch (error) {
        console.error(`Broadcast error for client ${clientId}:`, error);
        this.clients.delete(clientId);
      }
    });
  }

  /**
   * Send heartbeat to all clients
   */
  heartbeat() {
    const now = new Date();
    const timeout = this.config.websocket.heartbeatInterval * 2;

    this.clients.forEach((client, clientId) => {
      if (client.ws.readyState === 1) { // OPEN
        // Check if client is still alive
        if (now - client.lastHeartbeat > timeout) {
          console.log(`Client ${clientId} heartbeat timeout, disconnecting`);
          client.ws.terminate();
          this.clients.delete(clientId);
          return;
        }

        // Send ping
        client.ws.ping();
      } else {
        this.clients.delete(clientId);
      }
    });
  }

  /**
   * Generate unique client ID
   */
  generateClientId() {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Initialize the API server
   */
  async initialize() {
    try {
      // Initialize context manager
      await this.contextManager.initialize();
      this.isInitialized = true;

      // Setup context manager event listeners
      this.contextManager.on('contextStored', (data) => {
        this.broadcast('context-stored', data);
      });

      this.contextManager.on('contextUpdated', (data) => {
        this.broadcast('context-updated', data);
      });

      this.contextManager.on('contextDeleted', (data) => {
        this.broadcast('context-deleted', data);
      });

      console.log('Context API initialized successfully');
      return true;
      
    } catch (error) {
      console.error('Failed to initialize Context API:', error);
      throw error;
    }
  }

  /**
   * Start the API server
   */
  async start() {
    if (!this.isInitialized) {
      await this.initialize();
    }

    return new Promise((resolve, reject) => {
      this.server.listen(this.config.port, (error) => {
        if (error) {
          reject(error);
          return;
        }

        console.log(`
╔══════════════════════════════════════════════════════════╗
║              Context Preservation API                   ║
╠══════════════════════════════════════════════════════════╣
║  HTTP API:    http://localhost:${this.config.port}/api/context     ║
║  WebSocket:   ws://localhost:${this.config.port}/context-ws        ║
║  Health:      http://localhost:${this.config.port}/api/context/health ║
║                                                          ║
║  Features:                                               ║
║  • Cross-agent context sharing                          ║
║  • Session state management                             ║
║  • Context versioning & rollback                        ║
║  • Real-time WebSocket updates                          ║
║  • Full-text search capabilities                        ║
║  • Context encryption & compression                     ║
║  • Analytics & usage tracking                           ║
║                                                          ║
║  Status: Ready for connections                           ║
╚══════════════════════════════════════════════════════════╝
        `);

        resolve();
      });
    });
  }

  /**
   * Stop the API server
   */
  async stop() {
    try {
      // Close all WebSocket connections
      this.clients.forEach((client) => {
        client.ws.close();
      });
      this.clients.clear();

      // Close HTTP server
      await new Promise((resolve) => {
        this.server.close(resolve);
      });

      // Shutdown context manager
      await this.contextManager.shutdown();

      console.log('Context API stopped successfully');
      
    } catch (error) {
      console.error('Error stopping Context API:', error);
      throw error;
    }
  }
}

module.exports = ContextAPI;

// CLI support
if (require.main === module) {
  const contextAPI = new ContextAPI();
  
  contextAPI.start().then(() => {
    console.log('Context API started successfully');
  }).catch((error) => {
    console.error('Failed to start Context API:', error);
    process.exit(1);
  });

  // Graceful shutdown
  process.on('SIGTERM', async () => {
    console.log('Received SIGTERM, shutting down...');
    await contextAPI.stop();
    process.exit(0);
  });

  process.on('SIGINT', async () => {
    console.log('Received SIGINT, shutting down...');
    await contextAPI.stop();
    process.exit(0);
  });
}