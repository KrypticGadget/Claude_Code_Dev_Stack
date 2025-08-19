/**
 * Semantic Analysis WebSocket Server
 * 
 * Real-time semantic analysis with WebSocket support.
 * Enables live code analysis, incremental updates, and collaborative features.
 */

import { WebSocketServer, WebSocket } from 'ws';
import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';

import { SemanticCache } from './cache';
import { SemanticSearchEngine } from './search';
import { PatternMatcher } from './patterns';

export interface WebSocketMessage {
  id: string;
  type: string;
  payload: any;
  timestamp: number;
  clientId?: string;
}

export interface ClientConnection {
  id: string;
  ws: WebSocket;
  subscriptions: Set<string>;
  lastActivity: number;
  metadata: {
    userAgent?: string;
    language?: string;
    project?: string;
    capabilities: string[];
  };
}

export interface AnalysisSubscription {
  id: string;
  clientId: string;
  fileId: string;
  language: string;
  options: {
    realtime: boolean;
    includeRelationships: boolean;
    includePatterns: boolean;
    debounceMs: number;
  };
}

export class SemanticWebSocket extends EventEmitter {
  private wss: WebSocketServer;
  private clients: Map<string, ClientConnection> = new Map();
  private subscriptions: Map<string, AnalysisSubscription> = new Map();
  private cache: SemanticCache;
  private searchEngine: SemanticSearchEngine;
  private patternMatcher: PatternMatcher;
  private heartbeatInterval: NodeJS.Timeout;
  private analysisDebounce: Map<string, NodeJS.Timeout> = new Map();

  constructor(
    wss: WebSocketServer,
    cache: SemanticCache,
    searchEngine: SemanticSearchEngine,
    patternMatcher: PatternMatcher
  ) {
    super();
    
    this.wss = wss;
    this.cache = cache;
    this.searchEngine = searchEngine;
    this.patternMatcher = patternMatcher;

    this.setupWebSocketHandlers();
    this.startHeartbeat();
  }

  private setupWebSocketHandlers(): void {
    this.wss.on('connection', (ws: WebSocket, request) => {
      const clientId = uuidv4();
      const client: ClientConnection = {
        id: clientId,
        ws,
        subscriptions: new Set(),
        lastActivity: Date.now(),
        metadata: {
          userAgent: request.headers['user-agent'],
          capabilities: []
        }
      };

      this.clients.set(clientId, client);
      console.log(`WebSocket client connected: ${clientId}`);

      // Send welcome message
      this.sendMessage(client, {
        type: 'welcome',
        payload: {
          clientId,
          capabilities: [
            'real-time-analysis',
            'incremental-updates',
            'cross-file-references',
            'pattern-matching',
            'symbol-search',
            'collaboration'
          ]
        }
      });

      // Setup message handler
      ws.on('message', (data: Buffer) => {
        try {
          const message: WebSocketMessage = JSON.parse(data.toString());
          this.handleMessage(client, message);
          client.lastActivity = Date.now();
        } catch (error) {
          console.error('WebSocket message parse error:', error);
          this.sendError(client, 'Invalid message format');
        }
      });

      // Handle disconnection
      ws.on('close', () => {
        this.handleDisconnection(clientId);
      });

      // Handle errors
      ws.on('error', (error) => {
        console.error(`WebSocket error for client ${clientId}:`, error);
        this.handleDisconnection(clientId);
      });

      this.emit('client-connected', client);
    });
  }

  private handleMessage(client: ClientConnection, message: WebSocketMessage): void {
    message.clientId = client.id;
    
    switch (message.type) {
      case 'ping':
        this.handlePing(client, message);
        break;
      
      case 'subscribe-analysis':
        this.handleAnalysisSubscription(client, message);
        break;
      
      case 'unsubscribe-analysis':
        this.handleAnalysisUnsubscription(client, message);
        break;
      
      case 'analyze-code':
        this.handleCodeAnalysis(client, message);
        break;
      
      case 'incremental-update':
        this.handleIncrementalUpdate(client, message);
        break;
      
      case 'search-symbols':
        this.handleSymbolSearch(client, message);
        break;
      
      case 'match-patterns':
        this.handlePatternMatching(client, message);
        break;
      
      case 'get-references':
        this.handleGetReferences(client, message);
        break;
      
      case 'collaboration-join':
        this.handleCollaborationJoin(client, message);
        break;
      
      case 'collaboration-leave':
        this.handleCollaborationLeave(client, message);
        break;
      
      default:
        this.sendError(client, `Unknown message type: ${message.type}`);
    }

    this.emit('message', client, message);
  }

  private handlePing(client: ClientConnection, message: WebSocketMessage): void {
    this.sendMessage(client, {
      type: 'pong',
      payload: {
        timestamp: Date.now(),
        requestId: message.id
      }
    });
  }

  private handleAnalysisSubscription(client: ClientConnection, message: WebSocketMessage): void {
    const { fileId, language, options = {} } = message.payload;
    
    if (!fileId || !language) {
      this.sendError(client, 'Missing fileId or language for subscription');
      return;
    }

    const subscriptionId = uuidv4();
    const subscription: AnalysisSubscription = {
      id: subscriptionId,
      clientId: client.id,
      fileId,
      language,
      options: {
        realtime: true,
        includeRelationships: true,
        includePatterns: false,
        debounceMs: 300,
        ...options
      }
    };

    this.subscriptions.set(subscriptionId, subscription);
    client.subscriptions.add(subscriptionId);

    this.sendMessage(client, {
      type: 'subscription-created',
      payload: {
        subscriptionId,
        fileId,
        language,
        options: subscription.options
      }
    });

    console.log(`Analysis subscription created: ${subscriptionId} for file ${fileId}`);
  }

  private handleAnalysisUnsubscription(client: ClientConnection, message: WebSocketMessage): void {
    const { subscriptionId } = message.payload;
    
    if (this.subscriptions.has(subscriptionId)) {
      this.subscriptions.delete(subscriptionId);
      client.subscriptions.delete(subscriptionId);
      
      this.sendMessage(client, {
        type: 'subscription-removed',
        payload: { subscriptionId }
      });
    }
  }

  private async handleCodeAnalysis(client: ClientConnection, message: WebSocketMessage): void {
    const { code, language, fileId, options = {} } = message.payload;
    
    if (!code || !language) {
      this.sendError(client, 'Missing code or language for analysis');
      return;
    }

    try {
      // Check cache first
      const cacheKey = this.cache.generateKey('analysis', code, language, options);
      let result = this.cache.get(cacheKey, 'symbol');

      if (!result) {
        // Perform analysis (this would integrate with the Python semantic engine)
        result = await this.performSemanticAnalysis(code, language, fileId, options);
        
        // Cache the result
        this.cache.set(cacheKey, result, {
          category: 'symbol',
          ttl: 30 * 60 * 1000, // 30 minutes
          tags: [language, fileId].filter(Boolean)
        });
      }

      this.sendMessage(client, {
        type: 'analysis-result',
        payload: {
          requestId: message.id,
          fileId,
          language,
          result,
          cached: !!result
        }
      });

      // Notify subscribers
      this.notifySubscribers(fileId, 'analysis-update', result);

    } catch (error) {
      console.error('Code analysis error:', error);
      this.sendError(client, `Analysis failed: ${error.message}`, message.id);
    }
  }

  private handleIncrementalUpdate(client: ClientConnection, message: WebSocketMessage): void {
    const { fileId, changes, language } = message.payload;
    
    // Handle debounced incremental updates
    if (this.analysisDebounce.has(fileId)) {
      clearTimeout(this.analysisDebounce.get(fileId)!);
    }

    const subscription = Array.from(this.subscriptions.values())
      .find(sub => sub.fileId === fileId && sub.clientId === client.id);

    const debounceMs = subscription?.options.debounceMs || 300;

    this.analysisDebounce.set(fileId, setTimeout(async () => {
      try {
        // Apply incremental changes and re-analyze
        const result = await this.performIncrementalAnalysis(fileId, changes, language);
        
        // Notify all subscribers to this file
        this.notifySubscribers(fileId, 'incremental-update', {
          changes,
          analysis: result,
          timestamp: Date.now()
        });

        // Invalidate cache for this file
        this.cache.clearByTag(fileId);

      } catch (error) {
        console.error('Incremental update error:', error);
        this.sendError(client, `Incremental update failed: ${error.message}`);
      }
    }, debounceMs));
  }

  private async handleSymbolSearch(client: ClientConnection, message: WebSocketMessage): void {
    const { query, options = {} } = message.payload;
    
    try {
      const searchResults = await this.searchEngine.searchSymbols(query, {
        includeReferences: true,
        includeDefinitions: true,
        crossLanguage: true,
        ...options
      });

      this.sendMessage(client, {
        type: 'search-results',
        payload: {
          requestId: message.id,
          query,
          results: searchResults,
          total: searchResults.length
        }
      });

    } catch (error) {
      console.error('Symbol search error:', error);
      this.sendError(client, `Search failed: ${error.message}`, message.id);
    }
  }

  private async handlePatternMatching(client: ClientConnection, message: WebSocketMessage): void {
    const { pattern, scope, options = {} } = message.payload;
    
    try {
      const matches = await this.patternMatcher.findMatches(pattern, scope, options);

      this.sendMessage(client, {
        type: 'pattern-matches',
        payload: {
          requestId: message.id,
          pattern,
          matches,
          total: matches.length
        }
      });

    } catch (error) {
      console.error('Pattern matching error:', error);
      this.sendError(client, `Pattern matching failed: ${error.message}`, message.id);
    }
  }

  private async handleGetReferences(client: ClientConnection, message: WebSocketMessage): void {
    const { symbolId, fileId, position } = message.payload;
    
    try {
      // Find references across files
      const references = await this.findSymbolReferences(symbolId, fileId, position);

      this.sendMessage(client, {
        type: 'references-result',
        payload: {
          requestId: message.id,
          symbolId,
          references,
          total: references.length
        }
      });

    } catch (error) {
      console.error('Get references error:', error);
      this.sendError(client, `Get references failed: ${error.message}`, message.id);
    }
  }

  private handleCollaborationJoin(client: ClientConnection, message: WebSocketMessage): void {
    const { projectId, userId } = message.payload;
    
    client.metadata.project = projectId;
    
    // Notify other clients in the same project
    this.broadcastToProject(projectId, {
      type: 'collaboration-user-joined',
      payload: {
        userId,
        clientId: client.id,
        timestamp: Date.now()
      }
    }, client.id);

    this.sendMessage(client, {
      type: 'collaboration-joined',
      payload: {
        projectId,
        userId,
        activeUsers: this.getActiveUsersInProject(projectId)
      }
    });
  }

  private handleCollaborationLeave(client: ClientConnection, message: WebSocketMessage): void {
    const { projectId, userId } = message.payload;
    
    this.broadcastToProject(projectId, {
      type: 'collaboration-user-left',
      payload: {
        userId,
        clientId: client.id,
        timestamp: Date.now()
      }
    }, client.id);
  }

  private handleDisconnection(clientId: string): void {
    const client = this.clients.get(clientId);
    if (!client) return;

    // Clean up subscriptions
    for (const subscriptionId of client.subscriptions) {
      this.subscriptions.delete(subscriptionId);
    }

    // Clean up debounced operations
    for (const [fileId, timeout] of this.analysisDebounce) {
      const subscription = Array.from(this.subscriptions.values())
        .find(sub => sub.fileId === fileId && sub.clientId === clientId);
      
      if (subscription) {
        clearTimeout(timeout);
        this.analysisDebounce.delete(fileId);
      }
    }

    // Notify collaboration partners
    if (client.metadata.project) {
      this.broadcastToProject(client.metadata.project, {
        type: 'collaboration-user-disconnected',
        payload: {
          clientId,
          timestamp: Date.now()
        }
      }, clientId);
    }

    this.clients.delete(clientId);
    console.log(`WebSocket client disconnected: ${clientId}`);
    
    this.emit('client-disconnected', client);
  }

  private sendMessage(client: ClientConnection, message: Omit<WebSocketMessage, 'id' | 'timestamp'>): void {
    if (client.ws.readyState === WebSocket.OPEN) {
      const fullMessage: WebSocketMessage = {
        id: uuidv4(),
        timestamp: Date.now(),
        ...message
      };

      client.ws.send(JSON.stringify(fullMessage));
    }
  }

  private sendError(client: ClientConnection, error: string, requestId?: string): void {
    this.sendMessage(client, {
      type: 'error',
      payload: {
        error,
        requestId,
        timestamp: Date.now()
      }
    });
  }

  private notifySubscribers(fileId: string, type: string, payload: any): void {
    for (const subscription of this.subscriptions.values()) {
      if (subscription.fileId === fileId) {
        const client = this.clients.get(subscription.clientId);
        if (client) {
          this.sendMessage(client, {
            type,
            payload: {
              subscriptionId: subscription.id,
              fileId,
              ...payload
            }
          });
        }
      }
    }
  }

  private broadcastToProject(projectId: string, message: Omit<WebSocketMessage, 'id' | 'timestamp'>, excludeClientId?: string): void {
    for (const client of this.clients.values()) {
      if (client.metadata.project === projectId && client.id !== excludeClientId) {
        this.sendMessage(client, message);
      }
    }
  }

  private getActiveUsersInProject(projectId: string): string[] {
    return Array.from(this.clients.values())
      .filter(client => client.metadata.project === projectId)
      .map(client => client.id);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      const now = Date.now();
      const staleThreshold = 60 * 1000; // 60 seconds

      for (const [clientId, client] of this.clients) {
        if (now - client.lastActivity > staleThreshold) {
          if (client.ws.readyState === WebSocket.OPEN) {
            client.ws.ping();
          } else {
            this.handleDisconnection(clientId);
          }
        }
      }
    }, 30 * 1000); // Check every 30 seconds
  }

  // These methods would integrate with the Python semantic analysis engine
  private async performSemanticAnalysis(code: string, language: string, fileId: string, options: any): Promise<any> {
    // This would call the Python semantic analysis engine
    // For now, return a mock result
    return {
      symbols: [],
      relationships: [],
      metadata: {
        language,
        fileId,
        timestamp: Date.now()
      }
    };
  }

  private async performIncrementalAnalysis(fileId: string, changes: any, language: string): Promise<any> {
    // This would perform incremental analysis based on changes
    return {
      symbols: [],
      relationships: [],
      changes,
      metadata: {
        fileId,
        language,
        timestamp: Date.now()
      }
    };
  }

  private async findSymbolReferences(symbolId: string, fileId: string, position: any): Promise<any[]> {
    // This would find references across the codebase
    return [];
  }

  public getStats() {
    return {
      connectedClients: this.clients.size,
      activeSubscriptions: this.subscriptions.size,
      pendingAnalysis: this.analysisDebounce.size
    };
  }

  public destroy(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    // Clear all debounced operations
    for (const timeout of this.analysisDebounce.values()) {
      clearTimeout(timeout);
    }
    this.analysisDebounce.clear();

    // Close all client connections
    for (const client of this.clients.values()) {
      if (client.ws.readyState === WebSocket.OPEN) {
        client.ws.close();
      }
    }

    this.clients.clear();
    this.subscriptions.clear();
    this.removeAllListeners();
  }
}