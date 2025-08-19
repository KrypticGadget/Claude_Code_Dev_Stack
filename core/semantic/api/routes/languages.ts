/**
 * Language Routes
 * 
 * API endpoints for language support, configuration, and language-specific operations.
 */

import { Router, Request, Response } from 'express';
import { query, param, body, validationResult } from 'express-validator';

export function setupLanguageRoutes(router: Router): void {

  // Get supported languages
  router.get('/languages',
    [
      query('enabled').optional().isBoolean(),
      query('includeMetadata').optional().isBoolean()
    ],
    async (req: Request, res: Response) => {
      try {
        const {
          enabled,
          includeMetadata = false
        } = req.query;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('languages', enabled, includeMetadata);

        // Check cache first
        let languages = cache.get(cacheKey, 'symbol');

        if (!languages) {
          // Get supported languages
          languages = await getSupportedLanguages({
            enabled: enabled as boolean,
            includeMetadata: includeMetadata as boolean
          });

          // Cache the result
          cache.set(cacheKey, languages, {
            category: 'symbol',
            ttl: 60 * 60 * 1000, // 1 hour
            tags: ['languages']
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          languages,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!languages.cached,
            languageCount: languages.length
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Languages list error:', error);
        res.status(500).json({
          error: 'Languages list failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Get specific language information
  router.get('/languages/:languageId',
    [
      param('languageId').notEmpty().withMessage('Language ID is required'),
      query('includeParser').optional().isBoolean(),
      query('includeGrammar').optional().isBoolean(),
      query('includeExamples').optional().isBoolean()
    ],
    async (req: Request, res: Response) => {
      try {
        const { languageId } = req.params;
        const {
          includeParser = false,
          includeGrammar = false,
          includeExamples = false
        } = req.query;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('language-detail', languageId, {
          includeParser, includeGrammar, includeExamples
        });

        // Check cache first
        let language = cache.get(cacheKey, 'symbol');

        if (!language) {
          // Get language details
          language = await getLanguageDetails({
            languageId,
            includeParser: includeParser as boolean,
            includeGrammar: includeGrammar as boolean,
            includeExamples: includeExamples as boolean
          });

          if (!language) {
            return res.status(404).json({
              error: 'Language not found',
              languageId,
              requestId: req.id
            });
          }

          // Cache the result
          cache.set(cacheKey, language, {
            category: 'symbol',
            ttl: 2 * 60 * 60 * 1000, // 2 hours
            tags: ['language-detail', languageId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          language,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!language.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Language detail error:', error);
        res.status(500).json({
          error: 'Language detail failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Get language features and capabilities
  router.get('/languages/:languageId/features',
    [
      param('languageId').notEmpty().withMessage('Language ID is required')
    ],
    async (req: Request, res: Response) => {
      try {
        const { languageId } = req.params;
        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('language-features', languageId);

        // Check cache first
        let features = cache.get(cacheKey, 'symbol');

        if (!features) {
          // Get language features
          features = await getLanguageFeatures(languageId);

          if (!features) {
            return res.status(404).json({
              error: 'Language not found',
              languageId,
              requestId: req.id
            });
          }

          // Cache the result
          cache.set(cacheKey, features, {
            category: 'symbol',
            ttl: 4 * 60 * 60 * 1000, // 4 hours
            tags: ['language-features', languageId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          languageId,
          features,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!features.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Language features error:', error);
        res.status(500).json({
          error: 'Language features failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Parse code with specific language
  router.post('/languages/:languageId/parse',
    [
      param('languageId').notEmpty().withMessage('Language ID is required'),
      body('code').notEmpty().withMessage('Code is required'),
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

        const { languageId } = req.params;
        const { code, options = {} } = req.body;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('language-parse', languageId, code, options);

        // Check cache first
        let result = cache.get(cacheKey, 'symbol');

        if (!result) {
          // Parse with specific language
          result = await parseWithLanguage({
            languageId,
            code,
            options
          });

          // Cache the result
          cache.set(cacheKey, result, {
            category: 'symbol',
            ttl: 30 * 60 * 1000, // 30 minutes
            tags: ['language-parse', languageId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          languageId,
          result,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!result.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Language parse error:', error);
        res.status(500).json({
          error: 'Language parse failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Get language statistics
  router.get('/languages/:languageId/stats',
    [
      param('languageId').notEmpty().withMessage('Language ID is required'),
      query('period').optional().isIn(['day', 'week', 'month']),
      query('includeUsage').optional().isBoolean()
    ],
    async (req: Request, res: Response) => {
      try {
        const { languageId } = req.params;
        const {
          period = 'week',
          includeUsage = true
        } = req.query;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('language-stats', languageId, period, includeUsage);

        // Check cache first
        let stats = cache.get(cacheKey, 'symbol');

        if (!stats) {
          // Calculate language statistics
          stats = await calculateLanguageStatistics({
            languageId,
            period: period as string,
            includeUsage: includeUsage as boolean
          });

          // Cache the result
          cache.set(cacheKey, stats, {
            category: 'symbol',
            ttl: 20 * 60 * 1000, // 20 minutes
            tags: ['language-stats', languageId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          languageId,
          period,
          stats,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!stats.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Language statistics error:', error);
        res.status(500).json({
          error: 'Language statistics failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Detect language from code sample
  router.post('/languages/detect',
    [
      body('code').notEmpty().withMessage('Code is required'),
      body('filename').optional().isString(),
      body('confidence').optional().isFloat({ min: 0, max: 1 })
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
          filename,
          confidence = 0.8 
        } = req.body;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('language-detect', code, filename);

        // Check cache first
        let detection = cache.get(cacheKey, 'symbol');

        if (!detection) {
          // Detect language
          detection = await detectLanguage({
            code,
            filename,
            minimumConfidence: confidence
          });

          // Cache the result
          cache.set(cacheKey, detection, {
            category: 'symbol',
            ttl: 10 * 60 * 1000, // 10 minutes
            tags: ['language-detect']
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          detection,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!detection.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Language detection error:', error);
        res.status(500).json({
          error: 'Language detection failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Compare languages
  router.post('/languages/compare',
    [
      body('languages').isArray().withMessage('Languages array is required'),
      body('languages').custom((languages) => {
        if (languages.length < 2) {
          throw new Error('At least 2 languages are required for comparison');
        }
        return true;
      }),
      body('criteria').optional().isArray()
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
          languages, 
          criteria = ['features', 'performance', 'ecosystem'] 
        } = req.body;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('language-compare', languages, criteria);

        // Check cache first
        let comparison = cache.get(cacheKey, 'symbol');

        if (!comparison) {
          // Compare languages
          comparison = await compareLanguages({
            languages,
            criteria
          });

          // Cache the result
          cache.set(cacheKey, comparison, {
            category: 'symbol',
            ttl: 60 * 60 * 1000, // 1 hour
            tags: ['language-compare', ...languages]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          languages,
          criteria,
          comparison,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!comparison.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Language comparison error:', error);
        res.status(500).json({
          error: 'Language comparison failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Get language configuration
  router.get('/languages/:languageId/config',
    [
      param('languageId').notEmpty().withMessage('Language ID is required')
    ],
    async (req: Request, res: Response) => {
      try {
        const { languageId } = req.params;
        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('language-config', languageId);

        // Check cache first
        let config = cache.get(cacheKey, 'symbol');

        if (!config) {
          // Get language configuration
          config = await getLanguageConfiguration(languageId);

          if (!config) {
            return res.status(404).json({
              error: 'Language not found',
              languageId,
              requestId: req.id
            });
          }

          // Cache the result
          cache.set(cacheKey, config, {
            category: 'symbol',
            ttl: 2 * 60 * 60 * 1000, // 2 hours
            tags: ['language-config', languageId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          languageId,
          config,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!config.cached
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Language configuration error:', error);
        res.status(500).json({
          error: 'Language configuration failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Update language configuration
  router.put('/languages/:languageId/config',
    [
      param('languageId').notEmpty().withMessage('Language ID is required'),
      body('config').isObject().withMessage('Configuration object is required')
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

        const { languageId } = req.params;
        const { config } = req.body;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Update language configuration
        const updatedConfig = await updateLanguageConfiguration(languageId, config);

        if (!updatedConfig) {
          return res.status(404).json({
            error: 'Language not found',
            languageId,
            requestId: req.id
          });
        }

        // Invalidate related caches
        cache.clearByTag(`language-config`);
        cache.clearByTag(languageId);

        const processingTime = performance.now() - startTime;

        res.json({
          languageId,
          config: updatedConfig,
          metadata: {
            processingTime: Math.round(processingTime),
            operation: 'updated'
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Language configuration update error:', error);
        res.status(500).json({
          error: 'Language configuration update failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );

  // Get language examples
  router.get('/languages/:languageId/examples',
    [
      param('languageId').notEmpty().withMessage('Language ID is required'),
      query('category').optional().isIn(['basic', 'advanced', 'patterns', 'idioms']),
      query('limit').optional().isInt({ min: 1, max: 50 })
    ],
    async (req: Request, res: Response) => {
      try {
        const { languageId } = req.params;
        const {
          category = 'basic',
          limit = 10
        } = req.query;

        const { cache } = req.semanticContext;
        const startTime = performance.now();

        // Generate cache key
        const cacheKey = cache.generateKey('language-examples', languageId, category, limit);

        // Check cache first
        let examples = cache.get(cacheKey, 'symbol');

        if (!examples) {
          // Get language examples
          examples = await getLanguageExamples({
            languageId,
            category: category as string,
            limit: limit as number
          });

          // Cache the result
          cache.set(cacheKey, examples, {
            category: 'symbol',
            ttl: 4 * 60 * 60 * 1000, // 4 hours
            tags: ['language-examples', languageId]
          });
        }

        const processingTime = performance.now() - startTime;

        res.json({
          languageId,
          category,
          examples,
          metadata: {
            processingTime: Math.round(processingTime),
            cached: !!examples.cached,
            exampleCount: examples.length
          },
          requestId: req.id
        });

      } catch (error) {
        console.error('Language examples error:', error);
        res.status(500).json({
          error: 'Language examples failed',
          message: error.message,
          requestId: req.id
        });
      }
    }
  );
}

// Backend integration functions
async function getSupportedLanguages(params: any): Promise<any[]> {
  // This would integrate with the language registry
  return [
    {
      id: 'typescript',
      name: 'TypeScript',
      extensions: ['ts', 'tsx'],
      enabled: true,
      version: '1.0.0',
      features: ['ast-parsing', 'symbol-extraction', 'type-inference']
    },
    {
      id: 'javascript',
      name: 'JavaScript',
      extensions: ['js', 'jsx', 'mjs'],
      enabled: true,
      version: '1.0.0',
      features: ['ast-parsing', 'symbol-extraction']
    },
    {
      id: 'python',
      name: 'Python',
      extensions: ['py', 'pyi'],
      enabled: true,
      version: '1.0.0',
      features: ['ast-parsing', 'symbol-extraction', 'type-hints']
    },
    {
      id: 'rust',
      name: 'Rust',
      extensions: ['rs'],
      enabled: true,
      version: '1.0.0',
      features: ['ast-parsing', 'symbol-extraction', 'ownership-analysis']
    }
  ];
}

async function getLanguageDetails(params: any): Promise<any> {
  const { languageId } = params;
  
  // Mock language details
  const languages: Record<string, any> = {
    typescript: {
      id: 'typescript',
      name: 'TypeScript',
      description: 'A typed superset of JavaScript',
      extensions: ['ts', 'tsx'],
      enabled: true,
      version: '1.0.0',
      treeSitterGrammar: 'tree-sitter-typescript',
      features: {
        astParsing: true,
        symbolExtraction: true,
        typeInference: true,
        semanticAnalysis: true
      },
      statistics: {
        filesAnalyzed: 1250,
        symbolsExtracted: 15680,
        averageParseTime: 45
      }
    }
  };

  return languages[languageId] || null;
}

async function getLanguageFeatures(languageId: string): Promise<any> {
  // Mock language features
  const features: Record<string, any> = {
    typescript: {
      parsing: {
        ast: true,
        symbols: true,
        references: true,
        types: true
      },
      analysis: {
        complexity: true,
        patterns: true,
        antiPatterns: true,
        suggestions: true
      },
      intelligence: {
        autocompletion: true,
        hover: true,
        gotoDefinition: true,
        findReferences: true
      }
    }
  };

  return features[languageId] || null;
}

async function parseWithLanguage(params: any): Promise<any> {
  // This would use the language-specific parser
  return {
    languageId: params.languageId,
    ast: {
      type: 'program',
      children: []
    },
    symbols: [],
    relationships: [],
    metadata: {
      parseTime: 45,
      nodeCount: 150
    }
  };
}

async function calculateLanguageStatistics(params: any): Promise<any> {
  const { languageId, period } = params;
  
  return {
    languageId,
    period,
    usage: {
      filesAnalyzed: 1250,
      totalSymbols: 15680,
      totalQueries: 8500,
      averageParseTime: 45
    },
    symbolTypes: {
      function: 5200,
      class: 1800,
      interface: 950,
      variable: 4200,
      constant: 1850,
      module: 480,
      enum: 1200
    },
    complexity: {
      averageCyclomatic: 3.2,
      averageLines: 25,
      mostComplex: 'processUserData',
      complexityDistribution: {
        low: 8500,
        medium: 5200,
        high: 1980
      }
    }
  };
}

async function detectLanguage(params: any): Promise<any> {
  const { code, filename } = params;
  
  // Simple mock detection based on patterns
  const detections = [];
  
  if (code.includes('function') || code.includes('=>')) {
    detections.push({
      language: 'javascript',
      confidence: 0.85,
      features: ['arrow-functions', 'function-keyword']
    });
  }
  
  if (code.includes('def ') || code.includes('import ')) {
    detections.push({
      language: 'python',
      confidence: 0.90,
      features: ['def-keyword', 'import-statements']
    });
  }

  if (filename) {
    const ext = filename.split('.').pop();
    if (ext === 'ts') {
      detections.push({
        language: 'typescript',
        confidence: 0.95,
        features: ['file-extension']
      });
    }
  }

  return {
    primary: detections[0] || null,
    alternatives: detections.slice(1),
    confidence: detections[0]?.confidence || 0
  };
}

async function compareLanguages(params: any): Promise<any> {
  const { languages, criteria } = params;
  
  return {
    summary: {
      mostSimilar: [languages[0], languages[1]],
      mostDifferent: [languages[0], languages[2]],
      overallSimilarity: 0.75
    },
    detailed: languages.map((lang: string) => ({
      language: lang,
      scores: {
        features: Math.random() * 100,
        performance: Math.random() * 100,
        ecosystem: Math.random() * 100
      }
    })),
    matrix: languages.map((lang1: string) => 
      languages.map((lang2: string) => ({
        from: lang1,
        to: lang2,
        similarity: Math.random()
      }))
    )
  };
}

async function getLanguageConfiguration(languageId: string): Promise<any> {
  // Mock configuration
  return {
    enabled: true,
    features: {
      parsing: true,
      analysis: true,
      intelligence: true
    },
    settings: {
      maxFileSize: 1024 * 1024, // 1MB
      timeout: 30000, // 30 seconds
      caching: true
    },
    extensions: ['ts', 'tsx'],
    treeSitterGrammar: 'tree-sitter-typescript'
  };
}

async function updateLanguageConfiguration(languageId: string, config: any): Promise<any> {
  // Mock update
  return {
    ...config,
    updated: Date.now()
  };
}

async function getLanguageExamples(params: any): Promise<any[]> {
  const { languageId, category, limit } = params;
  
  // Mock examples
  const examples = [
    {
      title: 'Basic Function',
      code: 'function hello(name: string): string {\n  return `Hello, ${name}!`;\n}',
      description: 'A simple function with type annotations',
      tags: ['function', 'string', 'template-literal']
    },
    {
      title: 'Class Definition',
      code: 'class User {\n  constructor(public name: string) {}\n  \n  greet(): string {\n    return `Hello, ${this.name}!`;\n  }\n}',
      description: 'A basic class with constructor and method',
      tags: ['class', 'constructor', 'method']
    }
  ];

  return examples.slice(0, limit);
}