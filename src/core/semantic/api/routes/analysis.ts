/**
 * Analysis Routes
 * 
 * Core semantic analysis endpoints for parsing, symbol extraction, and AST analysis.
 */

import { Router, Request, Response } from 'express';
import { body, query, validationResult } from 'express-validator';

export function setupAnalysisRoutes(router: Router): void {
  
  // Parse source code and extract symbols
  router.post('/analysis/parse',
    [
      body('code').notEmpty().withMessage('Code is required'),
      body('language').notEmpty().withMessage('Language is required'),
      body('fileId').optional().isString(),
      body('includeRelationships').optional().isBoolean(),
      body('includeDocumentation').optional().isBoolean(),
      body('includeAST').optional().isBoolean()
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
          language, 
          fileId = `temp-${Date.now()}`,
          includeRelationships = true,
          includeDocumentation = true,
          includeAST = false
        } = req.body;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('parse', code, language, {
          includeRelationships,
          includeDocumentation,
          includeAST
        });

        // Check cache first
        let result = cache.get(cacheKey, 'symbol');

        if (!result) {
          // Perform semantic analysis (integrate with Python backend)
          result = await performSemanticParsing({
            code,
            language,
            fileId,
            options: {
              includeRelationships,
              includeDocumentation,
              includeAST
            }
          });

          // Cache the result
          cache.set(cacheKey, result, {
            category: 'symbol',
            ttl: 30 * 60 * 1000, // 30 minutes
            tags: [language, fileId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          result,
          metadata: {
            language,
            fileId,
            processingTime: Math.round(processingTime),
            cached: !!result.cached,
            symbolCount: result.symbols?.length || 0,
            relationshipCount: result.relationships?.length || 0
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Analysis parse error:', error);
        res.status(500).json({
          error: 'Analysis failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Get AST for source code
  router.post('/analysis/ast',
    [
      body('code').notEmpty().withMessage('Code is required'),
      body('language').notEmpty().withMessage('Language is required'),
      body('includePositions').optional().isBoolean(),
      body('includeTypes').optional().isBoolean()
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
          language,
          includePositions = true,
          includeTypes = false
        } = req.body;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('ast', code, language, {
          includePositions,
          includeTypes
        });

        // Check cache first
        let ast = cache.get(cacheKey, 'ast');

        if (!ast) {
          // Generate AST (integrate with Python backend)
          ast = await generateAST({
            code,
            language,
            options: {
              includePositions,
              includeTypes
            }
          });

          // Cache the result
          cache.set(cacheKey, ast, {
            category: 'ast',
            ttl: 60 * 60 * 1000, // 1 hour
            tags: [language, 'ast']
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          ast,
          metadata: {
            language,
            processingTime: Math.round(processingTime),
            cached: !!ast.cached,
            nodeCount: ast.nodeCount || 0
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('AST generation error:', error);
        res.status(500).json({
          error: 'AST generation failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Analyze code complexity
  router.post('/analysis/complexity',
    [
      body('code').notEmpty().withMessage('Code is required'),
      body('language').notEmpty().withMessage('Language is required'),
      body('metrics').optional().isArray()
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
          language,
          metrics = ['cyclomatic', 'cognitive', 'lines', 'halstead']
        } = req.body;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('complexity', code, language, metrics);

        // Check cache first
        let complexity = cache.get(cacheKey, 'symbol');

        if (!complexity) {
          // Analyze complexity (integrate with Python backend)
          complexity = await analyzeComplexity({
            code,
            language,
            metrics
          });

          // Cache the result
          cache.set(cacheKey, complexity, {
            category: 'symbol',
            ttl: 45 * 60 * 1000, // 45 minutes
            tags: [language, 'complexity']
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          complexity,
          metadata: {
            language,
            metrics,
            processingTime: Math.round(processingTime),
            cached: !!complexity.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Complexity analysis error:', error);
        res.status(500).json({
          error: 'Complexity analysis failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Cross-reference analysis
  router.post('/analysis/references',
    [
      body('code').notEmpty().withMessage('Code is required'),
      body('language').notEmpty().withMessage('Language is required'),
      body('position').isObject().withMessage('Position is required'),
      body('includeDefinitions').optional().isBoolean(),
      body('includeDeclarations').optional().isBoolean()
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
          language,
          position,
          includeDefinitions = true,
          includeDeclarations = true
        } = req.body;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('references', code, language, position, {
          includeDefinitions,
          includeDeclarations
        });

        // Check cache first
        let references = cache.get(cacheKey, 'relationship');

        if (!references) {
          // Find references (integrate with Python backend)
          references = await findReferences({
            code,
            language,
            position,
            options: {
              includeDefinitions,
              includeDeclarations
            }
          });

          // Cache the result
          cache.set(cacheKey, references, {
            category: 'relationship',
            ttl: 20 * 60 * 1000, // 20 minutes
            tags: [language, 'references']
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          references,
          metadata: {
            language,
            position,
            processingTime: Math.round(processingTime),
            cached: !!references.cached,
            referenceCount: references.references?.length || 0,
            definitionCount: references.definitions?.length || 0
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Reference analysis error:', error);
        res.status(500).json({
          error: 'Reference analysis failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Batch analysis
  router.post('/analysis/batch',
    [
      body('files').isArray().withMessage('Files array is required'),
      body('files.*.code').notEmpty().withMessage('Code is required for each file'),
      body('files.*.language').notEmpty().withMessage('Language is required for each file'),
      body('files.*.fileId').optional().isString(),
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

        const { files, options = {} } = req.body;
        const startTime = performance.now();

        // Process files in parallel
        const results = await Promise.all(
          files.map(async (file: any, index: number) => {
            try {
              const fileId = file.fileId || `batch-${Date.now()}-${index}`;
              
              const result = await performSemanticParsing({
                code: file.code,
                language: file.language,
                fileId,
                options
              });

              return {
                fileId,
                language: file.language,
                result,
                success: true
              };
            } catch (error) {
              return {
                fileId: file.fileId || `batch-${Date.now()}-${index}`,
                language: file.language,
                error: error.message,
                success: false
              };
            }
          })
        );

        const processingTime = performance.now() - startTime;
        const successCount = results.filter(r => r.success).length;
        const errorCount = results.filter(r => !r.success).length;

        res.json({
          results,
          metadata: {
            totalFiles: files.length,
            successCount,
            errorCount,
            processingTime: Math.round(processingTime),
            averageTimePerFile: Math.round(processingTime / files.length)
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Batch analysis error:', error);
        res.status(500).json({
          error: 'Batch analysis failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Analysis status and progress
  router.get('/analysis/status/:analysisId',
    async (req: Request, res: Response) => {
      try {
        const { analysisId } = req.params;
        const { cache } = req.semanticContext;

        // Get analysis status from cache
        const status = cache.get(`analysis-status-${analysisId}`, 'symbol');

        if (!status) {
          return res.status(404).json({
            error: 'Analysis not found',
            analysisId,
            requestId: req.id
          });
        }

        res.json({
          analysisId,
          status,
          requestId: req.id
        });

      } catch (error) {
        console.error('Status check error:', error);
        res.status(500).json({
          error: 'Status check failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );
}

// Integration functions with Python semantic analysis backend
async function performSemanticParsing(params: any): Promise<any> {
  // This would integrate with the Python semantic analysis engine
  // For now, return mock data
  return {
    symbols: [
      {
        id: 'symbol-1',
        name: 'exampleFunction',
        kind: 'function',
        range: { startLine: 1, startCol: 0, endLine: 5, endCol: 1 },
        signature: 'function exampleFunction(param: string): void',
        documentation: 'Example function for testing'
      }
    ],
    relationships: [
      {
        source: 'symbol-1',
        target: 'symbol-2',
        type: 'calls',
        range: { startLine: 3, startCol: 2, endLine: 3, endCol: 15 }
      }
    ],
    metadata: {
      language: params.language,
      fileId: params.fileId,
      timestamp: Date.now(),
      symbolCount: 1,
      relationshipCount: 1
    }
  };
}

async function generateAST(params: any): Promise<any> {
  // This would integrate with Tree-sitter to generate AST
  return {
    type: 'program',
    children: [
      {
        type: 'function_declaration',
        name: 'exampleFunction',
        parameters: [],
        body: {
          type: 'block',
          children: []
        }
      }
    ],
    nodeCount: 3,
    language: params.language,
    timestamp: Date.now()
  };
}

async function analyzeComplexity(params: any): Promise<any> {
  // This would integrate with complexity analysis tools
  return {
    cyclomatic: 2,
    cognitive: 3,
    lines: {
      total: 10,
      code: 8,
      comments: 1,
      blank: 1
    },
    halstead: {
      difficulty: 2.5,
      effort: 125.3,
      volume: 50.1
    },
    functions: [
      {
        name: 'exampleFunction',
        complexity: 2,
        lines: 5
      }
    ],
    language: params.language,
    timestamp: Date.now()
  };
}

async function findReferences(params: any): Promise<any> {
  // This would find references across the codebase
  return {
    symbol: {
      name: 'exampleSymbol',
      kind: 'function',
      position: params.position
    },
    references: [
      {
        location: {
          file: 'example.ts',
          range: { startLine: 10, startCol: 5, endLine: 10, endCol: 18 }
        },
        context: 'function call'
      }
    ],
    definitions: [
      {
        location: {
          file: 'example.ts',
          range: { startLine: 1, startCol: 0, endLine: 5, endCol: 1 }
        },
        context: 'function definition'
      }
    ],
    language: params.language,
    timestamp: Date.now()
  };
}