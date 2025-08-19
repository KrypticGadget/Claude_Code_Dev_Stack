/**
 * Semantic Analysis API Server
 * 
 * High-performance REST and WebSocket API server for semantic analysis operations.
 * Supports 16+ programming languages with Tree-sitter integration.
 * 
 * Features:
 * - REST endpoints for semantic operations
 * - WebSocket for real-time analysis
 * - Multi-language support with caching
 * - Pattern matching and code intelligence
 * - Cross-file and cross-language references
 * - Performance optimization with intelligent caching
 */

import express, { Express, Request, Response } from 'express';
import http from 'http';
import cors from 'cors';
import compression from 'compression';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { WebSocketServer } from 'ws';
import { v4 as uuidv4 } from 'uuid';

import { SemanticCache } from './cache';
import { SemanticWebSocket } from './websocket';
import { SemanticSearchEngine } from './search';
import { PatternMatcher } from './patterns';

// Route handlers
import { setupAnalysisRoutes } from './routes/analysis';
import { setupSymbolRoutes } from './routes/symbols';
import { setupSearchRoutes } from './routes/search';
import { setupPatternRoutes } from './routes/patterns';
import { setupLanguageRoutes } from './routes/languages';
import { setupHealthRoutes } from './routes/health';

export interface ServerConfig {
  port: number;
  host: string;
  enableWebSocket: boolean;
  enableCaching: boolean;
  enableRateLimit: boolean;
  maxCacheSize: number;
  rateLimitWindow: number;
  rateLimitMax: number;
  corsOrigins: string[];
}

export class SemanticAnalysisServer {
  private app: Express;
  private server: http.Server;
  private wsServer?: WebSocketServer;
  private cache: SemanticCache;
  private searchEngine: SemanticSearchEngine;
  private patternMatcher: PatternMatcher;
  private semanticWebSocket?: SemanticWebSocket;
  private config: ServerConfig;
  private isRunning = false;

  constructor(config: Partial<ServerConfig> = {}) {
    this.config = {
      port: 3001,
      host: '0.0.0.0',
      enableWebSocket: true,
      enableCaching: true,
      enableRateLimit: true,
      maxCacheSize: 1000,
      rateLimitWindow: 15 * 60 * 1000, // 15 minutes
      rateLimitMax: 1000, // requests per window
      corsOrigins: ['*'],
      ...config
    };

    this.app = express();
    this.server = http.createServer(this.app);
    
    // Initialize core components
    this.cache = new SemanticCache(this.config.maxCacheSize);
    this.searchEngine = new SemanticSearchEngine(this.cache);
    this.patternMatcher = new PatternMatcher(this.cache);

    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
  }

  private setupMiddleware(): void {
    // Security and performance middleware
    this.app.use(helmet());
    this.app.use(compression());
    
    // CORS configuration
    this.app.use(cors({
      origin: this.config.corsOrigins,
      credentials: true,
      optionsSuccessStatus: 200
    }));

    // Rate limiting
    if (this.config.enableRateLimit) {
      const limiter = rateLimit({
        windowMs: this.config.rateLimitWindow,
        max: this.config.rateLimitMax,
        message: {
          error: 'Too many requests',
          retryAfter: Math.ceil(this.config.rateLimitWindow / 1000)
        },
        standardHeaders: true,
        legacyHeaders: false,
      });
      this.app.use('/api/', limiter);
    }

    // Body parsing
    this.app.use(express.json({ limit: '50mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '50mb' }));

    // Request logging and correlation
    this.app.use((req, res, next) => {
      req.id = uuidv4();
      req.startTime = Date.now();
      
      console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - Request ID: ${req.id}`);
      
      res.on('finish', () => {
        const duration = Date.now() - req.startTime;
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`);
      });
      
      next();
    });

    // Add semantic context to requests
    this.app.use((req, res, next) => {
      req.semanticContext = {
        cache: this.cache,
        searchEngine: this.searchEngine,
        patternMatcher: this.patternMatcher,
        requestId: req.id
      };
      next();
    });
  }

  private setupRoutes(): void {
    // API version prefix
    const apiRouter = express.Router();
    
    // Setup route handlers
    setupHealthRoutes(apiRouter);
    setupAnalysisRoutes(apiRouter);
    setupSymbolRoutes(apiRouter);
    setupSearchRoutes(apiRouter);
    setupPatternRoutes(apiRouter);
    setupLanguageRoutes(apiRouter);

    // Mount API routes
    this.app.use('/api/v1', apiRouter);

    // Root endpoint
    this.app.get('/', (req: Request, res: Response) => {
      res.json({
        name: 'Semantic Analysis API',
        version: '1.0.0',
        description: 'Tree-sitter based semantic analysis for 16+ programming languages',
        endpoints: {
          health: '/api/v1/health',
          analysis: '/api/v1/analysis',
          symbols: '/api/v1/symbols',
          search: '/api/v1/search',
          patterns: '/api/v1/patterns',
          languages: '/api/v1/languages',
          websocket: this.config.enableWebSocket ? `ws://${this.config.host}:${this.config.port}/ws` : null
        },
        features: {
          languages: '16+ programming languages',
          realtime: this.config.enableWebSocket,
          caching: this.config.enableCaching,
          search: 'Cross-language semantic search',
          patterns: 'AST-based pattern matching'
        }
      });
    });

    // OpenAPI/Swagger documentation
    this.app.get('/api/docs', (req: Request, res: Response) => {
      res.json(this.generateOpenAPISpec());
    });

    // Catch-all error handler
    this.app.use((err: Error, req: Request, res: Response, next: any) => {
      console.error(`[${new Date().toISOString()}] Error in ${req.method} ${req.path}:`, err);
      
      res.status(500).json({
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong',
        requestId: req.id,
        timestamp: new Date().toISOString()
      });
    });

    // 404 handler
    this.app.use((req: Request, res: Response) => {
      res.status(404).json({
        error: 'Not found',
        message: `Endpoint ${req.method} ${req.path} not found`,
        requestId: req.id,
        timestamp: new Date().toISOString()
      });
    });
  }

  private setupWebSocket(): void {
    if (!this.config.enableWebSocket) return;

    this.wsServer = new WebSocketServer({ 
      server: this.server,
      path: '/ws'
    });

    this.semanticWebSocket = new SemanticWebSocket(
      this.wsServer,
      this.cache,
      this.searchEngine,
      this.patternMatcher
    );

    console.log('WebSocket server configured for real-time semantic analysis');
  }

  public async start(): Promise<void> {
    if (this.isRunning) {
      throw new Error('Server is already running');
    }

    return new Promise((resolve, reject) => {
      this.server.listen(this.config.port, this.config.host, () => {
        this.isRunning = true;
        console.log(`🚀 Semantic Analysis API Server started`);
        console.log(`   - Host: ${this.config.host}`);
        console.log(`   - Port: ${this.config.port}`);
        console.log(`   - WebSocket: ${this.config.enableWebSocket ? 'Enabled' : 'Disabled'}`);
        console.log(`   - Caching: ${this.config.enableCaching ? 'Enabled' : 'Disabled'}`);
        console.log(`   - Environment: ${process.env.NODE_ENV || 'development'}`);
        console.log(`   - API Base: http://${this.config.host}:${this.config.port}/api/v1`);
        
        if (this.config.enableWebSocket) {
          console.log(`   - WebSocket: ws://${this.config.host}:${this.config.port}/ws`);
        }

        resolve();
      });

      this.server.on('error', (error) => {
        this.isRunning = false;
        reject(error);
      });
    });
  }

  public async stop(): Promise<void> {
    if (!this.isRunning) {
      return;
    }

    return new Promise((resolve, reject) => {
      // Close WebSocket server
      if (this.wsServer) {
        this.wsServer.close();
      }

      // Close HTTP server
      this.server.close((error) => {
        if (error) {
          reject(error);
        } else {
          this.isRunning = false;
          console.log('Semantic Analysis API Server stopped');
          resolve();
        }
      });
    });
  }

  public getStatus() {
    return {
      running: this.isRunning,
      config: this.config,
      stats: {
        cache: this.cache.getStats(),
        search: this.searchEngine.getStats(),
        patterns: this.patternMatcher.getStats()
      }
    };
  }

  private generateOpenAPISpec() {
    return {
      openapi: '3.0.0',
      info: {
        title: 'Semantic Analysis API',
        version: '1.0.0',
        description: 'Tree-sitter based semantic analysis for multiple programming languages',
        contact: {
          name: 'Claude Code Dev Stack',
        }
      },
      servers: [
        {
          url: `http://${this.config.host}:${this.config.port}/api/v1`,
          description: 'Development server'
        }
      ],
      paths: {
        '/health': {
          get: {
            summary: 'Health check endpoint',
            responses: {
              '200': {
                description: 'Server is healthy',
                content: {
                  'application/json': {
                    schema: {
                      type: 'object',
                      properties: {
                        status: { type: 'string' },
                        timestamp: { type: 'string' },
                        uptime: { type: 'number' }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        '/analysis/parse': {
          post: {
            summary: 'Parse source code and extract symbols',
            requestBody: {
              required: true,
              content: {
                'application/json': {
                  schema: {
                    type: 'object',
                    required: ['code', 'language'],
                    properties: {
                      code: { type: 'string' },
                      language: { type: 'string' },
                      fileId: { type: 'string' },
                      includeRelationships: { type: 'boolean' }
                    }
                  }
                }
              }
            },
            responses: {
              '200': {
                description: 'Parsed symbols and relationships',
                content: {
                  'application/json': {
                    schema: {
                      type: 'object',
                      properties: {
                        symbols: { type: 'array' },
                        relationships: { type: 'array' },
                        metadata: { type: 'object' }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        '/search/symbols': {
          get: {
            summary: 'Search for symbols across files',
            parameters: [
              {
                name: 'query',
                in: 'query',
                required: true,
                schema: { type: 'string' }
              },
              {
                name: 'language',
                in: 'query',
                schema: { type: 'string' }
              },
              {
                name: 'kind',
                in: 'query',
                schema: { type: 'string' }
              }
            ],
            responses: {
              '200': {
                description: 'Search results',
                content: {
                  'application/json': {
                    schema: {
                      type: 'object',
                      properties: {
                        results: { type: 'array' },
                        total: { type: 'number' },
                        query: { type: 'object' }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      components: {
        schemas: {
          Symbol: {
            type: 'object',
            properties: {
              id: { type: 'string' },
              name: { type: 'string' },
              kind: { type: 'string' },
              range: {
                type: 'object',
                properties: {
                  startLine: { type: 'number' },
                  startCol: { type: 'number' },
                  endLine: { type: 'number' },
                  endCol: { type: 'number' }
                }
              }
            }
          }
        }
      }
    };
  }
}

// Type extensions for Express
declare global {
  namespace Express {
    interface Request {
      id: string;
      startTime: number;
      semanticContext: {
        cache: SemanticCache;
        searchEngine: SemanticSearchEngine;
        patternMatcher: PatternMatcher;
        requestId: string;
      };
    }
  }
}

// Export for use in other modules
export { SemanticCache, SemanticSearchEngine, PatternMatcher };