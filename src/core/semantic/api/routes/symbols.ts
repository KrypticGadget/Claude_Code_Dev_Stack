/**
 * Symbol Routes
 * 
 * API endpoints for symbol management, indexing, and relationship tracking.
 */

import { Router, Request, Response } from 'express';
import { body, query, param, validationResult } from 'express-validator';

export function setupSymbolRoutes(router: Router): void {

  // Get symbol information by ID
  router.get('/symbols/:symbolId',
    [
      param('symbolId').notEmpty().withMessage('Symbol ID is required'),
      query('includeReferences').optional().isBoolean(),
      query('includeDocumentation').optional().isBoolean(),
      query('includeContext').optional().isBoolean()
    ],
    async (req: Request, res: Response) => {
      try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({
            error: 'Validation failed',
            details: errors.array(),
            requestId: req.id
          });
        }

        const { symbolId } = req.params;
        const {
          includeReferences = false,
          includeDocumentation = true,
          includeContext = true
        } = req.query;

        const { cache, searchEngine } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('symbol-detail', symbolId, {
          includeReferences,
          includeDocumentation,
          includeContext
        });

        // Check cache first
        let symbol = cache.get(cacheKey, 'symbol');

        if (!symbol) {
          // Get symbol from search engine or backend
          symbol = await getSymbolById({
            symbolId,
            options: {
              includeReferences,
              includeDocumentation,
              includeContext
            }
          });

          if (!symbol) {
            return res.status(404).json({
              error: 'Symbol not found',
              symbolId,
              requestId: req.id
            });
          }

          // Cache the result
          cache.set(cacheKey, symbol, {
            category: 'symbol',
            ttl: 30 * 60 * 1000, // 30 minutes
            tags: ['symbol', symbolId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          symbol,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!symbol.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Symbol retrieval error:', error);
        res.status(500).json({
          error: 'Symbol retrieval failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // List symbols with filtering and pagination
  router.get('/symbols',
    [
      query('fileId').optional().isString(),
      query('language').optional().isString(),
      query('kind').optional().isString(),
      query('name').optional().isString(),
      query('page').optional().isInt({ min: 1 }),
      query('limit').optional().isInt({ min: 1, max: 1000 }),
      query('sortBy').optional().isIn(['name', 'kind', 'language', 'created']),
      query('sortOrder').optional().isIn(['asc', 'desc'])
    ],
    async (req: Request, res: Response) => {
      try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({
            error: 'Validation failed',
            details: errors.array(),
            requestId: req.id
          });
        }

        const {
          fileId,
          language,
          kind,
          name,
          page = 1,
          limit = 50,
          sortBy = 'name',
          sortOrder = 'asc'
        } = req.query;

        const { cache, searchEngine } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('symbol-list', {
          fileId, language, kind, name, page, limit, sortBy, sortOrder
        });

        // Check cache first
        let result = cache.get(cacheKey, 'symbol');

        if (!result) {
          // Search symbols
          const searchQuery = {
            text: name || '',
            type: 'fuzzy' as const,
            filters: {
              language: language ? [language] : undefined,
              symbolKind: kind ? [kind] : undefined,
              filePattern: fileId ? `*${fileId}*` : undefined
            },
            options: {
              maxResults: limit as number * (page as number),
              includeReferences: false,
              includeDefinitions: true
            }
          };

          const symbols = await searchEngine.searchSymbols(searchQuery);
          
          // Apply pagination
          const startIndex = ((page as number) - 1) * (limit as number);
          const endIndex = startIndex + (limit as number);
          const paginatedSymbols = symbols.slice(startIndex, endIndex);

          result = {
            symbols: paginatedSymbols,
            pagination: {
              page: page as number,
              limit: limit as number,
              total: symbols.length,
              pages: Math.ceil(symbols.length / (limit as number))
            },
            filters: {
              fileId,
              language,
              kind,
              name
            }
          };

          // Cache the result
          cache.set(cacheKey, result, {
            category: 'symbol',
            ttl: 15 * 60 * 1000, // 15 minutes
            tags: ['symbol-list', language, kind].filter(Boolean)
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          ...result,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!result.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Symbol list error:', error);
        res.status(500).json({
          error: 'Symbol list failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Create or update a symbol
  router.post('/symbols',
    [
      body('name').notEmpty().withMessage('Symbol name is required'),
      body('kind').notEmpty().withMessage('Symbol kind is required'),
      body('language').notEmpty().withMessage('Language is required'),
      body('fileId').notEmpty().withMessage('File ID is required'),
      body('range').isObject().withMessage('Range is required'),
      body('signature').optional().isString(),
      body('documentation').optional().isString(),
      body('visibility').optional().isIn(['public', 'private', 'protected', 'internal']),
      body('metadata').optional().isObject()
    ],
    async (req: Request, res: Response) => {
      try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({
            error: 'Validation failed',
            details: errors.array(),
            requestId: req.id
          });
        }

        const symbolData = req.body;
        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Create or update symbol
        const symbol = await createOrUpdateSymbol(symbolData);

        // Invalidate related caches
        cache.clearByTag(symbolData.fileId);
        cache.clearByTag(symbolData.language);

        const processingTime = performance.now() - startTime;

        res.status(201).json({
          symbol,
          metadata: {
            processingTime: Math.round(processingTime),
            operation: symbol.created ? 'created' : 'updated'
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Symbol creation error:', error);
        res.status(500).json({
          error: 'Symbol creation failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Update a symbol
  router.put('/symbols/:symbolId',
    [
      param('symbolId').notEmpty().withMessage('Symbol ID is required'),
      body('name').optional().notEmpty(),
      body('signature').optional().isString(),
      body('documentation').optional().isString(),
      body('visibility').optional().isIn(['public', 'private', 'protected', 'internal']),
      body('metadata').optional().isObject()
    ],
    async (req: Request, res: Response) => {
      try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({
            error: 'Validation failed',
            details: errors.array(),
            requestId: req.id
          });
        }

        const { symbolId } = req.params;
        const updates = req.body;
        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Update symbol
        const symbol = await updateSymbol(symbolId, updates);

        if (!symbol) {
          return res.status(404).json({
            error: 'Symbol not found',
            symbolId,
            requestId: req.id
          });
        }

        // Invalidate caches
        cache.clearByTag(symbolId);

        const processingTime = performance.now() - startTime;

        res.json({
          symbol,
          metadata: {
            processingTime: Math.round(processingTime)
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Symbol update error:', error);
        res.status(500).json({
          error: 'Symbol update failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Delete a symbol
  router.delete('/symbols/:symbolId',
    [
      param('symbolId').notEmpty().withMessage('Symbol ID is required')
    ],
    async (req: Request, res: Response) => {
      try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({
            error: 'Validation failed',
            details: errors.array(),
            requestId: req.id
          });
        }

        const { symbolId } = req.params;
        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Delete symbol
        const deleted = await deleteSymbol(symbolId);

        if (!deleted) {
          return res.status(404).json({
            error: 'Symbol not found',
            symbolId,
            requestId: req.id
          });
        }

        // Invalidate caches
        cache.clearByTag(symbolId);

        const processingTime = performance.now() - startTime;

        res.json({
          success: true,
          symbolId,
          metadata: {
            processingTime: Math.round(processingTime)
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Symbol deletion error:', error);
        res.status(500).json({
          error: 'Symbol deletion failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Get symbol relationships
  router.get('/symbols/:symbolId/relationships',
    [
      param('symbolId').notEmpty().withMessage('Symbol ID is required'),
      query('type').optional().isIn(['calls', 'extends', 'implements', 'uses', 'defines']),
      query('direction').optional().isIn(['incoming', 'outgoing', 'both']),
      query('depth').optional().isInt({ min: 1, max: 5 })
    ],
    async (req: Request, res: Response) => {
      try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({
            error: 'Validation failed',
            details: errors.array(),
            requestId: req.id
          });
        }

        const { symbolId } = req.params;
        const {
          type,
          direction = 'both',
          depth = 1
        } = req.query;

        const { cache, searchEngine } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('symbol-relationships', symbolId, {
          type, direction, depth
        });

        // Check cache first
        let relationships = cache.get(cacheKey, 'relationship');

        if (!relationships) {
          // Get relationships
          relationships = await getSymbolRelationships({
            symbolId,
            type,
            direction,
            depth: depth as number
          });

          // Cache the result
          cache.set(cacheKey, relationships, {
            category: 'relationship',
            ttl: 20 * 60 * 1000, // 20 minutes
            tags: ['relationships', symbolId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          symbolId,
          relationships,
          metadata: {
            type,
            direction,
            depth,
            processingTime: Math.round(processingTime),
            cached: !!relationships.cached,
            relationshipCount: relationships.relationships?.length || 0
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Symbol relationships error:', error);
        res.status(500).json({
          error: 'Symbol relationships failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Bulk symbol operations
  router.post('/symbols/bulk',
    [
      body('operation').isIn(['create', 'update', 'delete']).withMessage('Valid operation is required'),
      body('symbols').isArray().withMessage('Symbols array is required'),
      body('symbols').custom((symbols) => {
        if (symbols.length === 0) {
          throw new Error('At least one symbol is required');
        }
        if (symbols.length > 1000) {
          throw new Error('Maximum 1000 symbols per bulk operation');
        }
        return true;
      })
    ],
    async (req: Request, res: Response) => {
      try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({
            error: 'Validation failed',
            details: errors.array(),
            requestId: req.id
          });
        }

        const { operation, symbols } = req.body;
        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Perform bulk operation
        const results = await performBulkSymbolOperation({
          operation,
          symbols
        });

        // Invalidate relevant caches
        const fileIds = new Set(symbols.map((s: any) => s.fileId).filter(Boolean));
        const languages = new Set(symbols.map((s: any) => s.language).filter(Boolean));
        
        for (const fileId of fileIds) {
          cache.clearByTag(fileId);
        }
        for (const language of languages) {
          cache.clearByTag(language);
        }

        const processingTime = performance.now() - startTime;
        const successCount = results.filter((r: any) => r.success).length;
        const errorCount = results.filter((r: any) => !r.success).length;

        res.json({
          operation,
          results,
          metadata: {
            totalSymbols: symbols.length,
            successCount,
            errorCount,
            processingTime: Math.round(processingTime)
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Bulk symbol operation error:', error);
        res.status(500).json({
          error: 'Bulk operation failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Symbol statistics
  router.get('/symbols/stats',
    [
      query('fileId').optional().isString(),
      query('language').optional().isString(),
      query('groupBy').optional().isIn(['language', 'kind', 'file', 'visibility'])
    ],
    async (req: Request, res: Response) => {
      try {
        const {
          fileId,
          language,
          groupBy = 'kind'
        } = req.query;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('symbol-stats', {
          fileId, language, groupBy
        });

        // Check cache first
        let stats = cache.get(cacheKey, 'symbol');

        if (!stats) {
          // Calculate statistics
          stats = await calculateSymbolStatistics({
            fileId,
            language,
            groupBy
          });

          // Cache the result
          cache.set(cacheKey, stats, {
            category: 'symbol',
            ttl: 10 * 60 * 1000, // 10 minutes
            tags: ['stats', fileId, language].filter(Boolean)
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          stats,
          metadata: {
            filters: { fileId, language },
            groupBy,
            processingTime: Math.round(processingTime),
            cached: !!stats.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Symbol statistics error:', error);
        res.status(500).json({
          error: 'Statistics calculation failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );
}

// Backend integration functions
async function getSymbolById(params: any): Promise<any> {
  // This would integrate with the symbol index or database
  return {
    id: params.symbolId,
    name: 'exampleSymbol',
    kind: 'function',
    language: 'typescript',
    fileId: 'file-1',
    range: { startLine: 1, startCol: 0, endLine: 5, endCol: 1 },
    signature: 'function exampleSymbol(): void',
    documentation: 'Example symbol for testing',
    visibility: 'public',
    metadata: {
      created: Date.now(),
      updated: Date.now()
    }
  };
}

async function createOrUpdateSymbol(symbolData: any): Promise<any> {
  // This would create or update symbol in the database/index
  return {
    ...symbolData,
    id: `symbol-${Date.now()}`,
    created: true,
    metadata: {
      created: Date.now(),
      updated: Date.now()
    }
  };
}

async function updateSymbol(symbolId: string, updates: any): Promise<any> {
  // This would update symbol in the database/index
  return {
    id: symbolId,
    ...updates,
    metadata: {
      updated: Date.now()
    }
  };
}

async function deleteSymbol(symbolId: string): Promise<boolean> {
  // This would delete symbol from the database/index
  return true;
}

async function getSymbolRelationships(params: any): Promise<any> {
  // This would get relationships from the index
  return {
    symbolId: params.symbolId,
    relationships: [
      {
        id: 'rel-1',
        type: 'calls',
        source: params.symbolId,
        target: 'symbol-2',
        metadata: {
          strength: 1.0,
          frequency: 5
        }
      }
    ]
  };
}

async function performBulkSymbolOperation(params: any): Promise<any[]> {
  // This would perform bulk operations
  return params.symbols.map((symbol: any, index: number) => ({
    index,
    symbolId: symbol.id || `symbol-${Date.now()}-${index}`,
    success: true,
    operation: params.operation
  }));
}

async function calculateSymbolStatistics(params: any): Promise<any> {
  // This would calculate statistics from the symbol index
  return {
    total: 150,
    byKind: {
      function: 80,
      class: 25,
      interface: 15,
      variable: 20,
      constant: 10
    },
    byLanguage: {
      typescript: 90,
      javascript: 30,
      python: 20,
      rust: 10
    },
    byVisibility: {
      public: 100,
      private: 30,
      protected: 15,
      internal: 5
    }
  };
}