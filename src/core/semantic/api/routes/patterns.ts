/**
 * Pattern Matching Routes
 * 
 * API endpoints for AST pattern matching, code intelligence, and pattern-based analysis.
 */

import { Router, Request, Response } from 'express';
import { body, query, param, validationResult } from 'express-validator';

export function setupPatternRoutes(router: Router): void {

  // Get all available patterns
  router.get('/patterns',
    [
      query('type').optional().isIn(['structural', 'behavioral', 'semantic', 'anti-pattern']),
      query('language').optional().isString(),
      query('category').optional().isString(),
      query('severity').optional().isIn(['info', 'warning', 'error'])
    ],
    async (req: Request, res: Response) => {
      try {
        const {
          type,
          language,
          category,
          severity
        } = req.query;

        const { patternMatcher } = req.semanticContext;
        const startTime = performance.now();

        // Get patterns with filters
        const patterns = patternMatcher.getPatterns({
          type: type as any,
          language: language as string,
          category: category as string
        });

        // Filter by severity if specified
        const filteredPatterns = severity
          ? patterns.filter(p => p.metadata.severity === severity)
          : patterns;

        const processingTime = performance.now() - startTime;

        res.json({
          patterns: filteredPatterns,
          filters: {
            type,
            language,
            category,
            severity
          },
          metadata: {
            processingTime: Math.round(processingTime),
            patternCount: filteredPatterns.length,
            totalAvailable: patterns.length
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern list error:', error);
        res.status(500).json({
          error: 'Pattern list failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Get specific pattern details
  router.get('/patterns/:patternId',
    [
      param('patternId').notEmpty().withMessage('Pattern ID is required')
    ],
    async (req: Request, res: Response) => {
      try {
        const { patternId } = req.params;
        const { patternMatcher } = req.semanticContext;

        const patterns = patternMatcher.getPatterns();
        const pattern = patterns.find(p => p.id === patternId);

        if (!pattern) {
          return res.status(404).json({
            error: 'Pattern not found',
            patternId,
            requestId: req.id
          });
        }

        res.json({
          pattern,
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern detail error:', error);
        res.status(500).json({
          error: 'Pattern detail failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Register a new pattern
  router.post('/patterns',
    [
      body('name').notEmpty().withMessage('Pattern name is required'),
      body('description').notEmpty().withMessage('Pattern description is required'),
      body('type').isIn(['structural', 'behavioral', 'semantic', 'anti-pattern']).withMessage('Valid pattern type is required'),
      body('languages').isArray().withMessage('Languages array is required'),
      body('definition').isObject().withMessage('Pattern definition is required'),
      body('definition.query').notEmpty().withMessage('Pattern query is required'),
      body('metadata').isObject().withMessage('Pattern metadata is required'),
      body('metadata.category').notEmpty().withMessage('Pattern category is required')
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

        const patternData = {
          id: `custom-${Date.now()}`,
          ...req.body
        };

        const { patternMatcher } = req.semanticContext;
        const startTime = performance.now();

        // Validate pattern
        const validation = patternMatcher.validatePattern(patternData);
        if (!validation.valid) {
          return res.status(400).json({
            error: 'Pattern validation failed',
            details: validation.errors,
            requestId: req.id
          });
        }

        // Register pattern
        patternMatcher.registerPattern(patternData);

        const processingTime = performance.now() - startTime;

        res.status(201).json({
          pattern: patternData,
          metadata: {
            processingTime: Math.round(processingTime),
            operation: 'created'
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern creation error:', error);
        res.status(500).json({
          error: 'Pattern creation failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Delete a pattern
  router.delete('/patterns/:patternId',
    [
      param('patternId').notEmpty().withMessage('Pattern ID is required')
    ],
    async (req: Request, res: Response) => {
      try {
        const { patternId } = req.params;
        const { patternMatcher, cache } = req.semanticContext;

        const removed = patternMatcher.unregisterPattern(patternId);

        if (!removed) {
          return res.status(404).json({
            error: 'Pattern not found',
            patternId,
            requestId: req.id
          });
        }

        // Clear related caches
        cache.clearByTag('patterns');

        res.json({
          success: true,
          patternId,
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern deletion error:', error);
        res.status(500).json({
          error: 'Pattern deletion failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Find pattern matches in code
  router.post('/patterns/match',
    [
      body('code').optional().isString(),
      body('fileIds').optional().isArray(),
      body('patterns').optional().isArray(),
      body('languages').optional().isArray(),
      body('categories').optional().isArray(),
      body('severity').optional().isArray(),
      body('options').optional().isObject()
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
          code,
          fileIds,
          patterns,
          languages,
          categories,
          severity,
          options = {}
        } = req.body;

        const { cache, patternMatcher } = req.semanticContext;
        const startTime = performance.now();

        // Build pattern query
        const query = {
          patterns,
          languages,
          files: fileIds,
          categories,
          severity,
          options: {
            maxMatches: 100,
            includeContext: true,
            includeSuggestions: true,
            confidenceThreshold: 0.7,
            ...options
          }
        };

        // Generate cache key
        const cacheKey = cache.generateKey('pattern-matches', query, code);

        // Check cache first
        let matches = cache.get(cacheKey, 'pattern');

        if (!matches) {
          // Find matches
          matches = await patternMatcher.findMatches(query, code);

          // Cache the result
          cache.set(cacheKey, matches, {
            category: 'pattern',
            ttl: 20 * 60 * 1000, // 20 minutes
            tags: ['pattern-matches', ...(languages || []), ...(categories || [])]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          query,
          matches,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!matches.cached,
            matchCount: matches.length
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern matching error:', error);
        res.status(500).json({
          error: 'Pattern matching failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Find matches for a specific pattern
  router.post('/patterns/:patternId/match',
    [
      param('patternId').notEmpty().withMessage('Pattern ID is required'),
      body('scope').notEmpty().withMessage('Scope is required'),
      body('options').optional().isObject()
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

        const { patternId } = req.params;
        const { scope, options = {} } = req.body;

        const { cache, patternMatcher } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('pattern-specific-match', patternId, scope, options);

        // Check cache first
        let matches = cache.get(cacheKey, 'pattern');

        if (!matches) {
          // Find pattern-specific matches
          matches = await patternMatcher.findPatternMatches(patternId, scope, options);

          // Cache the result
          cache.set(cacheKey, matches, {
            category: 'pattern',
            ttl: 15 * 60 * 1000, // 15 minutes
            tags: ['pattern-specific', patternId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          patternId,
          scope,
          matches,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!matches.cached,
            matchCount: matches.length
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern-specific matching error:', error);
        res.status(500).json({
          error: 'Pattern-specific matching failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Create pattern from examples
  router.post('/patterns/create-from-examples',
    [
      body('name').notEmpty().withMessage('Pattern name is required'),
      body('examples').isArray().withMessage('Examples array is required'),
      body('examples').custom((examples) => {
        if (examples.length === 0) {
          throw new Error('At least one example is required');
        }
        return true;
      }),
      body('options').optional().isObject()
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

        const { name, examples, options = {} } = req.body;
        const { patternMatcher } = req.semanticContext;
        const startTime = performance.now();

        // Create pattern from examples
        const pattern = await patternMatcher.createPatternFromExamples(name, examples, options);

        const processingTime = performance.now() - startTime;

        res.status(201).json({
          pattern,
          metadata: {
            processingTime: Math.round(processingTime),
            exampleCount: examples.length,
            operation: 'generated'
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern generation error:', error);
        res.status(500).json({
          error: 'Pattern generation failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Validate a pattern
  router.post('/patterns/validate',
    [
      body('pattern').isObject().withMessage('Pattern object is required'),
      body('pattern.id').notEmpty().withMessage('Pattern ID is required'),
      body('pattern.name').notEmpty().withMessage('Pattern name is required'),
      body('pattern.definition').isObject().withMessage('Pattern definition is required')
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

        const { pattern } = req.body;
        const { patternMatcher } = req.semanticContext;
        const startTime = performance.now();

        // Validate pattern
        const validation = patternMatcher.validatePattern(pattern);

        const processingTime = performance.now() - startTime;

        res.json({
          pattern: {
            id: pattern.id,
            name: pattern.name
          },
          validation,
          metadata: {
            processingTime: Math.round(processingTime)
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern validation error:', error);
        res.status(500).json({
          error: 'Pattern validation failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Pattern statistics and analytics
  router.get('/patterns/stats',
    [
      query('groupBy').optional().isIn(['language', 'category', 'type', 'severity']),
      query('period').optional().isIn(['day', 'week', 'month'])
    ],
    async (req: Request, res: Response) => {
      try {
        const {
          groupBy = 'category',
          period = 'week'
        } = req.query;

        const { cache, patternMatcher } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('pattern-stats', groupBy, period);

        // Check cache first
        let stats = cache.get(cacheKey, 'pattern');

        if (!stats) {
          // Calculate statistics
          stats = await calculatePatternStatistics({
            groupBy: groupBy as string,
            period: period as string,
            patterns: patternMatcher.getPatterns()
          });

          // Add engine stats
          stats.engineStats = patternMatcher.getStats();

          // Cache the result
          cache.set(cacheKey, stats, {
            category: 'pattern',
            ttl: 30 * 60 * 1000, // 30 minutes
            tags: ['pattern-stats', groupBy as string]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          groupBy,
          period,
          stats,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!stats.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern statistics error:', error);
        res.status(500).json({
          error: 'Pattern statistics failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Export patterns
  router.get('/patterns/export',
    [
      query('format').optional().isIn(['json', 'yaml']),
      query('includeBuiltIn').optional().isBoolean()
    ],
    async (req: Request, res: Response) => {
      try {
        const {
          format = 'json',
          includeBuiltIn = true
        } = req.query;

        const { patternMatcher } = req.semanticContext;
        const startTime = performance.now();

        // Export patterns
        const exportData = patternMatcher.exportPatterns();

        // Filter built-in patterns if requested
        if (!includeBuiltIn) {
          exportData.patterns = exportData.patterns.filter(
            ([id, pattern]: [string, any]) => !pattern.metadata?.builtIn
          );
        }

        const processingTime = performance.now() - startTime;

        // Set appropriate content type
        const contentType = format === 'yaml' 
          ? 'application/x-yaml' 
          : 'application/json';

        res.setHeader('Content-Type', contentType);
        res.setHeader('Content-Disposition', `attachment; filename="patterns.${format}"`);

        if (format === 'yaml') {
          // Convert to YAML (would need a YAML library)
          const yamlData = convertToYaml(exportData);
          res.send(yamlData);
        } else {
          res.json({
            ...exportData,
            metadata: {
              exportTime: Date.now(),
              processingTime: Math.round(processingTime),
              format,
              includeBuiltIn,
              patternCount: exportData.patterns.length
            }
          });
        }

      } catch (error) {
        console.error('Pattern export error:', error);
        res.status(500).json({
          error: 'Pattern export failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Import patterns
  router.post('/patterns/import',
    [
      body('data').isObject().withMessage('Import data is required'),
      body('overwrite').optional().isBoolean()
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

        const { data, overwrite = false } = req.body;
        const { patternMatcher, cache } = req.semanticContext;
        const startTime = performance.now();

        // Import patterns
        const result = await importPatterns(patternMatcher, data, overwrite);

        // Clear pattern cache
        cache.clearByTag('patterns');

        const processingTime = performance.now() - startTime;

        res.json({
          result,
          metadata: {
            processingTime: Math.round(processingTime),
            overwrite
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Pattern import error:', error);
        res.status(500).json({
          error: 'Pattern import failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );
}

// Helper functions
async function calculatePatternStatistics(params: any): Promise<any> {
  const { groupBy, period, patterns } = params;
  
  const stats: any = {
    total: patterns.length,
    byType: {},
    byCategory: {},
    byLanguage: {},
    bySeverity: {}
  };

  // Group patterns
  for (const pattern of patterns) {
    // By type
    stats.byType[pattern.type] = (stats.byType[pattern.type] || 0) + 1;
    
    // By category
    const category = pattern.metadata.category;
    stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;
    
    // By language
    for (const lang of pattern.languages) {
      stats.byLanguage[lang] = (stats.byLanguage[lang] || 0) + 1;
    }
    
    // By severity
    if (pattern.metadata.severity) {
      const severity = pattern.metadata.severity;
      stats.bySeverity[severity] = (stats.bySeverity[severity] || 0) + 1;
    }
  }

  return stats;
}

function convertToYaml(data: any): string {
  // This would use a YAML library to convert JSON to YAML
  // For now, return JSON as a placeholder
  return JSON.stringify(data, null, 2);
}

async function importPatterns(patternMatcher: any, data: any, overwrite: boolean): Promise<any> {
  const results = {
    imported: 0,
    skipped: 0,
    errors: [] as string[]
  };

  if (!data.patterns || !Array.isArray(data.patterns)) {
    throw new Error('Invalid import data: patterns array not found');
  }

  for (const [id, pattern] of data.patterns) {
    try {
      // Check if pattern already exists
      const existing = patternMatcher.getPatterns().find((p: any) => p.id === id);
      
      if (existing && !overwrite) {
        results.skipped++;
        continue;
      }

      // Validate and register pattern
      const validation = patternMatcher.validatePattern(pattern);
      if (!validation.valid) {
        results.errors.push(`Pattern ${id}: ${validation.errors.join(', ')}`);
        continue;
      }

      patternMatcher.registerPattern(pattern);
      results.imported++;

    } catch (error) {
      results.errors.push(`Pattern ${id}: ${error.message}`);
    }
  }

  return results;
}