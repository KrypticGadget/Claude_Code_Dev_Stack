/**
 * Search Routes
 * 
 * API endpoints for semantic search, cross-language search, and intelligent code discovery.
 */

import { Router, Request, Response } from 'express';
import { body, query, validationResult } from 'express-validator';

export function setupSearchRoutes(router: Router): void {

  // General symbol search
  router.get('/search/symbols',
    [
      query('q').notEmpty().withMessage('Query is required'),
      query('type').optional().isIn(['exact', 'fuzzy', 'semantic', 'regex']),
      query('language').optional().isString(),
      query('kind').optional().isString(),
      query('scope').optional().isIn(['local', 'project', 'global']),
      query('limit').optional().isInt({ min: 1, max: 500 }),
      query('offset').optional().isInt({ min: 0 }),
      query('includeReferences').optional().isBoolean(),
      query('includeDefinitions').optional().isBoolean(),
      query('caseSensitive').optional().isBoolean()
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
          q: query,
          type = 'fuzzy',
          language,
          kind,
          scope = 'project',
          limit = 50,
          offset = 0,
          includeReferences = false,
          includeDefinitions = true,
          caseSensitive = false
        } = req.query;

        const { cache, searchEngine } = req.semanticContext;
        const startTime = performance.now();

        // Build search query
        const searchQuery = {
          text: query as string,
          type: type as 'exact' | 'fuzzy' | 'semantic' | 'regex',
          filters: {
            language: language ? [language as string] : undefined,
            symbolKind: kind ? [kind as string] : undefined,
            scope: scope as 'local' | 'project' | 'global'
          },
          options: {
            maxResults: (limit as number) + (offset as number),
            includeReferences: includeReferences as boolean,
            includeDefinitions: includeDefinitions as boolean,
            caseSensitive: caseSensitive as boolean
          }
        };

        // Perform search
        const allResults = await searchEngine.searchSymbols(searchQuery);
        
        // Apply pagination
        const results = allResults.slice(offset as number, (offset as number) + (limit as number));
        
        const processingTime = performance.now() - startTime;

        res.json({
          query: {
            text: query,
            type,
            filters: searchQuery.filters,
            options: searchQuery.options
          },
          results,
          pagination: {
            offset: offset as number,
            limit: limit as number,
            total: allResults.length,
            hasMore: (offset as number) + (limit as number) < allResults.length
          },
          metadata: {
            processingTime: Math.round(processingTime),
            resultCount: results.length
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Symbol search error:', error);
        res.status(500).json({
          error: 'Search failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Advanced search with complex criteria
  router.post('/search/advanced',
    [
      body('query').notEmpty().withMessage('Query is required'),
      body('filters').optional().isObject(),
      body('options').optional().isObject(),
      body('sortBy').optional().isIn(['relevance', 'name', 'kind', 'language', 'file']),
      body('sortOrder').optional().isIn(['asc', 'desc'])
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
          query,
          filters = {},
          options = {},
          sortBy = 'relevance',
          sortOrder = 'desc'
        } = req.body;

        const { cache, searchEngine } = req.semanticContext;
        const startTime = performance.now();

        // Build advanced search query
        const searchQuery = {
          text: query,
          type: query.type || 'semantic',
          filters: {
            language: filters.languages,
            symbolKind: filters.kinds,
            filePattern: filters.filePattern,
            scope: filters.scope || 'project',
            includeDocumentation: filters.includeDocumentation,
            includeComments: filters.includeComments
          },
          options: {
            maxResults: options.maxResults || 100,
            includeReferences: options.includeReferences || false,
            includeDefinitions: options.includeDefinitions || true,
            crossLanguage: options.crossLanguage || false,
            caseSensitive: options.caseSensitive || false,
            wholeWord: options.wholeWord || false
          }
        };

        // Perform search
        let results = await searchEngine.searchSymbols(searchQuery);

        // Apply sorting
        results = sortResults(results, sortBy, sortOrder);

        const processingTime = performance.now() - startTime;

        res.json({
          query: searchQuery,
          results,
          metadata: {
            processingTime: Math.round(processingTime),
            resultCount: results.length,
            sortBy,
            sortOrder
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Advanced search error:', error);
        res.status(500).json({
          error: 'Advanced search failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Cross-language search
  router.get('/search/cross-language',
    [
      query('q').notEmpty().withMessage('Query is required'),
      query('languages').optional().isString(), // Comma-separated list
      query('similarity').optional().isFloat({ min: 0, max: 1 }),
      query('includeEquivalents').optional().isBoolean()
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
          q: query,
          languages,
          similarity = 0.7,
          includeEquivalents = true
        } = req.query;

        const { searchEngine } = req.semanticContext;
        const startTime = performance.now();

        // Parse languages
        const targetLanguages = languages 
          ? (languages as string).split(',').map(l => l.trim())
          : undefined;

        // Build cross-language query
        const searchQuery = {
          text: query as string,
          type: 'semantic' as const,
          filters: {
            language: targetLanguages
          },
          options: {
            maxResults: 200,
            crossLanguage: true,
            includeReferences: false,
            includeDefinitions: true
          }
        };

        // Perform cross-language search
        const resultsByLanguage = await searchEngine.searchCrossLanguage(searchQuery);

        // Find equivalents if requested
        let equivalents: any[] = [];
        if (includeEquivalents) {
          equivalents = await findLanguageEquivalents(query as string, targetLanguages);
        }

        const processingTime = performance.now() - startTime;

        res.json({
          query: {
            text: query,
            languages: targetLanguages,
            similarity
          },
          resultsByLanguage: Object.fromEntries(resultsByLanguage),
          equivalents,
          metadata: {
            processingTime: Math.round(processingTime),
            languageCount: resultsByLanguage.size,
            totalResults: Array.from(resultsByLanguage.values()).reduce((sum, results) => sum + results.length, 0)
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Cross-language search error:', error);
        res.status(500).json({
          error: 'Cross-language search failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Semantic similarity search
  router.get('/search/similar/:symbolId',
    [
      query('threshold').optional().isFloat({ min: 0, max: 1 }),
      query('maxResults').optional().isInt({ min: 1, max: 100 }),
      query('includeContext').optional().isBoolean()
    ],
    async (req: Request, res: Response) => {
      try {
        const { symbolId } = req.params;
        const {
          threshold = 0.7,
          maxResults = 20,
          includeContext = true
        } = req.query;

        const { cache, searchEngine } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('similar-search', symbolId, {
          threshold, maxResults, includeContext
        });

        // Check cache first
        let results = cache.get(cacheKey, 'search');

        if (!results) {
          // Find similar symbols
          results = await searchEngine.findSimilar(symbolId, threshold as number);
          
          // Limit results
          results = results.slice(0, maxResults as number);

          // Add context if requested
          if (includeContext) {
            results = await enrichWithContext(results);
          }

          // Cache the result
          cache.set(cacheKey, results, {
            category: 'search',
            ttl: 20 * 60 * 1000, // 20 minutes
            tags: ['similarity', symbolId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          symbolId,
          threshold,
          results,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!results.cached,
            resultCount: results.length
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Similarity search error:', error);
        res.status(500).json({
          error: 'Similarity search failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Text-based code search
  router.post('/search/code',
    [
      body('query').notEmpty().withMessage('Query is required'),
      body('type').optional().isIn(['text', 'regex', 'ast']),
      body('files').optional().isArray(),
      body('languages').optional().isArray(),
      body('context').optional().isObject()
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
          query,
          type = 'text',
          files,
          languages,
          context = {}
        } = req.body;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('code-search', query, type, files, languages, context);

        // Check cache first
        let results = cache.get(cacheKey, 'search');

        if (!results) {
          // Perform code search
          results = await performCodeSearch({
            query,
            type,
            files,
            languages,
            context
          });

          // Cache the result
          cache.set(cacheKey, results, {
            category: 'search',
            ttl: 15 * 60 * 1000, // 15 minutes
            tags: ['code-search', ...(languages || [])]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          query: {
            text: query,
            type,
            files,
            languages,
            context
          },
          results,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!results.cached,
            matchCount: results.matches?.length || 0
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Code search error:', error);
        res.status(500).json({
          error: 'Code search failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Search suggestions and autocomplete
  router.get('/search/suggestions',
    [
      query('q').notEmpty().withMessage('Query is required'),
      query('type').optional().isIn(['symbols', 'files', 'patterns']),
      query('limit').optional().isInt({ min: 1, max: 50 })
    ],
    async (req: Request, res: Response) => {
      try {
        const {
          q: query,
          type = 'symbols',
          limit = 10
        } = req.query;

        const { cache, searchEngine } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('search-suggestions', query, type, limit);

        // Check cache first
        let suggestions = cache.get(cacheKey, 'search');

        if (!suggestions) {
          // Generate suggestions
          suggestions = await generateSearchSuggestions({
            query: query as string,
            type: type as string,
            limit: limit as number
          });

          // Cache the result
          cache.set(cacheKey, suggestions, {
            category: 'search',
            ttl: 5 * 60 * 1000, // 5 minutes
            tags: ['suggestions', type as string]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          query,
          type,
          suggestions,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!suggestions.cached,
            suggestionCount: suggestions.length
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Search suggestions error:', error);
        res.status(500).json({
          error: 'Search suggestions failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Search history and analytics
  router.get('/search/history',
    [
      query('limit').optional().isInt({ min: 1, max: 100 }),
      query('offset').optional().isInt({ min: 0 })
    ],
    async (req: Request, res: Response) => {
      try {
        const {
          limit = 20,
          offset = 0
        } = req.query;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Get search history (would be stored per user/session)
        const history = await getSearchHistory({
          limit: limit as number,
          offset: offset as number
        });

        const processingTime = performance.now() - startTime;

        res.json({
          history,
          pagination: {
            offset: offset as number,
            limit: limit as number,
            total: history.total
          },
          metadata: {
            processingTime: Math.round(processingTime)
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Search history error:', error);
        res.status(500).json({
          error: 'Search history failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Search analytics and statistics
  router.get('/search/analytics',
    [
      query('period').optional().isIn(['hour', 'day', 'week', 'month']),
      query('groupBy').optional().isIn(['language', 'type', 'user'])
    ],
    async (req: Request, res: Response) => {
      try {
        const {
          period = 'day',
          groupBy = 'language'
        } = req.query;

        const { cache, searchEngine } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('search-analytics', period, groupBy);

        // Check cache first
        let analytics = cache.get(cacheKey, 'search');

        if (!analytics) {
          // Calculate analytics
          analytics = await calculateSearchAnalytics({
            period: period as string,
            groupBy: groupBy as string
          });

          // Add engine stats
          analytics.engineStats = searchEngine.getStats();

          // Cache the result
          cache.set(cacheKey, analytics, {
            category: 'search',
            ttl: 30 * 60 * 1000, // 30 minutes
            tags: ['analytics', period as string]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          period,
          groupBy,
          analytics,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!analytics.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Search analytics error:', error);
        res.status(500).json({
          error: 'Search analytics failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );
}

// Helper functions
function sortResults(results: any[], sortBy: string, sortOrder: string): any[] {
  return results.sort((a, b) => {
    let valueA, valueB;

    switch (sortBy) {
      case 'name':
        valueA = a.symbol.name;
        valueB = b.symbol.name;
        break;
      case 'kind':
        valueA = a.symbol.kind;
        valueB = b.symbol.kind;
        break;
      case 'language':
        valueA = a.context.language;
        valueB = b.context.language;
        break;
      case 'file':
        valueA = a.location.filePath;
        valueB = b.location.filePath;
        break;
      case 'relevance':
      default:
        valueA = a.match.score;
        valueB = b.match.score;
        break;
    }

    if (sortOrder === 'asc') {
      return valueA < valueB ? -1 : valueA > valueB ? 1 : 0;
    } else {
      return valueA > valueB ? -1 : valueA < valueB ? 1 : 0;
    }
  });
}

// Backend integration functions
async function findLanguageEquivalents(query: string, languages?: string[]): Promise<any[]> {
  // This would find equivalent symbols across languages
  return [
    {
      concept: query,
      equivalents: {
        javascript: 'function',
        python: 'def',
        rust: 'fn',
        java: 'method'
      }
    }
  ];
}

async function enrichWithContext(results: any[]): Promise<any[]> {
  // This would add contextual information to results
  return results.map(result => ({
    ...result,
    context: {
      ...result.context,
      similarityReason: 'Same functionality pattern',
      usageFrequency: Math.random() * 100
    }
  }));
}

async function performCodeSearch(params: any): Promise<any> {
  // This would perform text/regex/AST based code search
  return {
    matches: [
      {
        file: 'example.ts',
        line: 42,
        column: 10,
        match: params.query,
        context: 'function example() { return "hello"; }'
      }
    ],
    total: 1
  };
}

async function generateSearchSuggestions(params: any): Promise<string[]> {
  // This would generate intelligent search suggestions
  const { query, type, limit } = params;
  
  if (type === 'symbols') {
    return [
      `${query}Function`,
      `${query}Class`,
      `${query}Interface`,
      `${query}Type`
    ].slice(0, limit);
  }
  
  return [];
}

async function getSearchHistory(params: any): Promise<any> {
  // This would retrieve search history from storage
  return {
    searches: [
      {
        query: 'function example',
        timestamp: Date.now() - 3600000,
        resultCount: 25,
        type: 'fuzzy'
      }
    ],
    total: 1
  };
}

async function calculateSearchAnalytics(params: any): Promise<any> {
  // This would calculate search analytics
  return {
    totalSearches: 1250,
    uniqueQueries: 800,
    averageResultCount: 15.5,
    topQueries: [
      { query: 'function', count: 45 },
      { query: 'class', count: 32 },
      { query: 'interface', count: 28 }
    ],
    byLanguage: {
      typescript: 450,
      javascript: 320,
      python: 280,
      rust: 200
    }
  };
}