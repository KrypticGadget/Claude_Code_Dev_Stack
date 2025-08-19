/**
 * AST Pattern Matching Engine
 * 
 * Advanced pattern matching capabilities for semantic analysis.
 * Supports structural patterns, behavioral patterns, and code intelligence features.
 */

import { EventEmitter } from 'events';
import { SemanticCache } from './cache';

export interface Pattern {
  id: string;
  name: string;
  description: string;
  type: 'structural' | 'behavioral' | 'semantic' | 'anti-pattern';
  languages: string[];
  definition: {
    query: string;
    constraints?: Record<string, any>;
    variables?: Record<string, string>;
  };
  metadata: {
    category: string;
    severity?: 'info' | 'warning' | 'error';
    tags: string[];
    examples?: string[];
  };
}

export interface PatternMatch {
  id: string;
  pattern: Pattern;
  location: {
    fileId: string;
    filePath: string;
    range: {
      startLine: number;
      startCol: number;
      endLine: number;
      endCol: number;
    };
  };
  context: {
    language: string;
    parentSymbol?: string;
    surroundingCode: string;
  };
  bindings: Record<string, any>;
  confidence: number;
  metadata: {
    matched: string;
    suggestions?: string[];
    explanation?: string;
  };
}

export interface PatternQuery {
  patterns?: string[];
  languages?: string[];
  files?: string[];
  categories?: string[];
  severity?: ('info' | 'warning' | 'error')[];
  excludePatterns?: string[];
  options: {
    maxMatches?: number;
    includeContext?: boolean;
    includeSuggestions?: boolean;
    confidenceThreshold?: number;
  };
}

export interface PatternStats {
  totalPatterns: number;
  totalMatches: number;
  matchesByLanguage: Record<string, number>;
  matchesByCategory: Record<string, number>;
  averageMatchTime: number;
  cacheHitRate: number;
}

export class PatternMatcher extends EventEmitter {
  private cache: SemanticCache;
  private patterns: Map<string, Pattern> = new Map();
  private compiledPatterns: Map<string, any> = new Map();
  private stats: PatternStats;
  private matchCache: Map<string, PatternMatch[]> = new Map();

  // Built-in pattern categories
  private readonly builtInPatterns = {
    // Code quality patterns
    LONG_PARAMETER_LIST: {
      id: 'long-parameter-list',
      name: 'Long Parameter List',
      description: 'Functions with too many parameters',
      type: 'anti-pattern' as const,
      languages: ['*'],
      definition: {
        query: 'function_declaration parameters: (parameter_list (parameter) @param)',
        constraints: { minParams: 5 }
      },
      metadata: {
        category: 'code-quality',
        severity: 'warning' as const,
        tags: ['maintainability', 'complexity']
      }
    },

    // Security patterns
    SQL_INJECTION: {
      id: 'sql-injection',
      name: 'Potential SQL Injection',
      description: 'Direct string concatenation in SQL queries',
      type: 'anti-pattern' as const,
      languages: ['javascript', 'typescript', 'python', 'java'],
      definition: {
        query: 'call_expression function: (identifier) @func arguments: (arguments (binary_expression) @expr)',
        constraints: { sqlFunctions: ['query', 'execute', 'exec'] }
      },
      metadata: {
        category: 'security',
        severity: 'error' as const,
        tags: ['security', 'sql-injection']
      }
    },

    // Performance patterns
    NESTED_LOOPS: {
      id: 'nested-loops',
      name: 'Deeply Nested Loops',
      description: 'Multiple levels of nested loops that may impact performance',
      type: 'anti-pattern' as const,
      languages: ['*'],
      definition: {
        query: 'for_statement body: (block (for_statement body: (block (for_statement) @inner_loop) @middle_loop) @outer_loop)',
        constraints: { maxDepth: 3 }
      },
      metadata: {
        category: 'performance',
        severity: 'warning' as const,
        tags: ['performance', 'complexity']
      }
    },

    // Design patterns
    SINGLETON_PATTERN: {
      id: 'singleton-pattern',
      name: 'Singleton Pattern',
      description: 'Implementation of the Singleton design pattern',
      type: 'structural' as const,
      languages: ['java', 'csharp', 'typescript'],
      definition: {
        query: 'class_declaration body: (class_body (field_declaration (variable_declarator (identifier) @instance)) (method_declaration (identifier) @method))',
        constraints: { staticInstance: true, privateConstructor: true }
      },
      metadata: {
        category: 'design-patterns',
        severity: 'info' as const,
        tags: ['design-pattern', 'singleton']
      }
    },

    // Functional programming patterns
    HIGHER_ORDER_FUNCTION: {
      id: 'higher-order-function',
      name: 'Higher-Order Function',
      description: 'Functions that take or return other functions',
      type: 'behavioral' as const,
      languages: ['javascript', 'typescript', 'python', 'haskell'],
      definition: {
        query: 'function_declaration parameters: (parameter_list (parameter type: (function_type) @func_param))',
        constraints: {}
      },
      metadata: {
        category: 'functional',
        severity: 'info' as const,
        tags: ['functional-programming', 'higher-order']
      }
    }
  };

  constructor(cache: SemanticCache) {
    super();
    
    this.cache = cache;
    this.stats = {
      totalPatterns: 0,
      totalMatches: 0,
      matchesByLanguage: {},
      matchesByCategory: {},
      averageMatchTime: 0,
      cacheHitRate: 0
    };

    this.initializeBuiltInPatterns();
  }

  /**
   * Register a new pattern
   */
  public registerPattern(pattern: Pattern): void {
    this.patterns.set(pattern.id, pattern);
    this.compilePattern(pattern);
    this.stats.totalPatterns = this.patterns.size;
    
    console.log(`Registered pattern: ${pattern.name} (${pattern.id})`);
    this.emit('pattern-registered', pattern);
  }

  /**
   * Remove a pattern
   */
  public unregisterPattern(patternId: string): boolean {
    const removed = this.patterns.delete(patternId);
    if (removed) {
      this.compiledPatterns.delete(patternId);
      this.stats.totalPatterns = this.patterns.size;
      this.emit('pattern-unregistered', patternId);
    }
    return removed;
  }

  /**
   * Find pattern matches in code
   */
  public async findMatches(query: PatternQuery, code?: string, language?: string): Promise<PatternMatch[]> {
    const startTime = performance.now();
    
    try {
      // Generate cache key
      const cacheKey = this.cache.generateKey('pattern-matches', query, code, language);
      
      // Check cache first
      let matches = this.matchCache.get(cacheKey);
      if (matches) {
        this.updateStats(performance.now() - startTime, true, matches.length);
        return matches;
      }

      // Check semantic cache
      matches = this.cache.get(cacheKey, 'pattern');
      if (matches) {
        this.matchCache.set(cacheKey, matches);
        this.updateStats(performance.now() - startTime, true, matches.length);
        return matches;
      }

      // Perform pattern matching
      matches = await this.performPatternMatching(query, code, language);

      // Cache the results
      this.cache.set(cacheKey, matches, {
        category: 'pattern',
        ttl: 20 * 60 * 1000, // 20 minutes
        tags: ['patterns', ...(query.languages || []), ...(query.categories || [])]
      });

      this.matchCache.set(cacheKey, matches);
      this.updateStats(performance.now() - startTime, false, matches.length);

      return matches;

    } catch (error) {
      console.error('Pattern matching error:', error);
      this.updateStats(performance.now() - startTime, false, 0);
      throw error;
    }
  }

  /**
   * Find matches for a specific pattern
   */
  public async findPatternMatches(patternId: string, scope: string, options: any = {}): Promise<PatternMatch[]> {
    const pattern = this.patterns.get(patternId);
    if (!pattern) {
      throw new Error(`Pattern not found: ${patternId}`);
    }

    const query: PatternQuery = {
      patterns: [patternId],
      options: {
        maxMatches: 100,
        includeContext: true,
        includeSuggestions: true,
        confidenceThreshold: 0.7,
        ...options
      }
    };

    return this.findMatches(query);
  }

  /**
   * Get all available patterns
   */
  public getPatterns(filter?: {
    type?: Pattern['type'];
    language?: string;
    category?: string;
  }): Pattern[] {
    let patterns = Array.from(this.patterns.values());

    if (filter) {
      if (filter.type) {
        patterns = patterns.filter(p => p.type === filter.type);
      }
      if (filter.language) {
        patterns = patterns.filter(p => 
          p.languages.includes('*') || p.languages.includes(filter.language!)
        );
      }
      if (filter.category) {
        patterns = patterns.filter(p => p.metadata.category === filter.category);
      }
    }

    return patterns;
  }

  /**
   * Validate a pattern definition
   */
  public validatePattern(pattern: Pattern): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!pattern.id) {
      errors.push('Pattern ID is required');
    }

    if (!pattern.name) {
      errors.push('Pattern name is required');
    }

    if (!pattern.definition?.query) {
      errors.push('Pattern query is required');
    }

    if (!pattern.languages || pattern.languages.length === 0) {
      errors.push('At least one supported language is required');
    }

    if (!['structural', 'behavioral', 'semantic', 'anti-pattern'].includes(pattern.type)) {
      errors.push('Invalid pattern type');
    }

    // Validate query syntax
    try {
      this.validateQuerySyntax(pattern.definition.query);
    } catch (error) {
      errors.push(`Invalid query syntax: ${error.message}`);
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Create a custom pattern from examples
   */
  public async createPatternFromExamples(
    name: string,
    examples: Array<{ code: string; language: string; shouldMatch: boolean }>,
    options: {
      type?: Pattern['type'];
      category?: string;
      description?: string;
    } = {}
  ): Promise<Pattern> {
    // Analyze examples to extract common patterns
    const extractedPattern = await this.extractPatternFromExamples(examples);

    const pattern: Pattern = {
      id: `custom-${Date.now()}`,
      name,
      description: options.description || `Custom pattern: ${name}`,
      type: options.type || 'structural',
      languages: [...new Set(examples.map(e => e.language))],
      definition: extractedPattern,
      metadata: {
        category: options.category || 'custom',
        tags: ['custom', 'generated'],
        examples: examples.filter(e => e.shouldMatch).map(e => e.code)
      }
    };

    // Validate the generated pattern
    const validation = this.validatePattern(pattern);
    if (!validation.valid) {
      throw new Error(`Generated pattern is invalid: ${validation.errors.join(', ')}`);
    }

    this.registerPattern(pattern);
    return pattern;
  }

  /**
   * Get pattern matching statistics
   */
  public getStats(): PatternStats {
    return { ...this.stats };
  }

  /**
   * Clear pattern cache
   */
  public clearCache(): void {
    this.matchCache.clear();
    this.cache.clearByTag('patterns');
    this.emit('cache-cleared');
  }

  /**
   * Export patterns for backup
   */
  public exportPatterns(): any {
    return {
      timestamp: Date.now(),
      patterns: Array.from(this.patterns.entries()),
      stats: this.stats
    };
  }

  /**
   * Import patterns from backup
   */
  public importPatterns(data: any): void {
    if (data.patterns) {
      for (const [id, pattern] of data.patterns) {
        this.registerPattern(pattern);
      }
    }
    
    this.emit('patterns-imported', data.timestamp);
  }

  /**
   * Initialize built-in patterns
   */
  private initializeBuiltInPatterns(): void {
    for (const pattern of Object.values(this.builtInPatterns)) {
      this.registerPattern(pattern);
    }
    
    console.log(`Initialized ${Object.keys(this.builtInPatterns).length} built-in patterns`);
  }

  /**
   * Compile a pattern for efficient matching
   */
  private compilePattern(pattern: Pattern): void {
    try {
      // This would compile the Tree-sitter query for efficient execution
      const compiled = {
        id: pattern.id,
        query: pattern.definition.query,
        constraints: pattern.definition.constraints || {},
        variables: pattern.definition.variables || {},
        compiledQuery: this.compileTreeSitterQuery(pattern.definition.query)
      };

      this.compiledPatterns.set(pattern.id, compiled);
    } catch (error) {
      console.error(`Failed to compile pattern ${pattern.id}:`, error);
    }
  }

  /**
   * Perform the actual pattern matching
   */
  private async performPatternMatching(
    query: PatternQuery,
    code?: string,
    language?: string
  ): Promise<PatternMatch[]> {
    const matches: PatternMatch[] = [];
    
    // Determine which patterns to apply
    const applicablePatterns = this.getApplicablePatterns(query, language);

    for (const pattern of applicablePatterns) {
      try {
        const patternMatches = await this.matchPattern(pattern, code, language, query.options);
        matches.push(...patternMatches);
      } catch (error) {
        console.error(`Error matching pattern ${pattern.id}:`, error);
      }
    }

    // Filter by confidence threshold
    const threshold = query.options.confidenceThreshold || 0.7;
    const filteredMatches = matches.filter(match => match.confidence >= threshold);

    // Sort by confidence
    filteredMatches.sort((a, b) => b.confidence - a.confidence);

    // Apply limit
    const maxMatches = query.options.maxMatches || 100;
    return filteredMatches.slice(0, maxMatches);
  }

  /**
   * Get patterns applicable to the query
   */
  private getApplicablePatterns(query: PatternQuery, language?: string): Pattern[] {
    let patterns = Array.from(this.patterns.values());

    // Filter by specified patterns
    if (query.patterns && query.patterns.length > 0) {
      patterns = patterns.filter(p => query.patterns!.includes(p.id));
    }

    // Filter by language
    if (query.languages && query.languages.length > 0) {
      patterns = patterns.filter(p => 
        p.languages.includes('*') || 
        query.languages!.some(lang => p.languages.includes(lang))
      );
    } else if (language) {
      patterns = patterns.filter(p => 
        p.languages.includes('*') || p.languages.includes(language)
      );
    }

    // Filter by categories
    if (query.categories && query.categories.length > 0) {
      patterns = patterns.filter(p => query.categories!.includes(p.metadata.category));
    }

    // Filter by severity
    if (query.severity && query.severity.length > 0) {
      patterns = patterns.filter(p => 
        p.metadata.severity && query.severity!.includes(p.metadata.severity)
      );
    }

    // Exclude patterns
    if (query.excludePatterns && query.excludePatterns.length > 0) {
      patterns = patterns.filter(p => !query.excludePatterns!.includes(p.id));
    }

    return patterns;
  }

  /**
   * Match a specific pattern against code
   */
  private async matchPattern(
    pattern: Pattern,
    code?: string,
    language?: string,
    options: PatternQuery['options'] = {}
  ): Promise<PatternMatch[]> {
    const compiled = this.compiledPatterns.get(pattern.id);
    if (!compiled) {
      return [];
    }

    // This would execute the Tree-sitter query against the AST
    const rawMatches = await this.executeCompiledQuery(compiled, code, language);

    // Convert raw matches to PatternMatch objects
    const matches: PatternMatch[] = [];
    for (const rawMatch of rawMatches) {
      const confidence = this.calculateMatchConfidence(pattern, rawMatch);
      
      const match: PatternMatch = {
        id: `${pattern.id}-${Date.now()}-${Math.random()}`,
        pattern,
        location: {
          fileId: rawMatch.fileId || 'unknown',
          filePath: rawMatch.filePath || 'unknown',
          range: rawMatch.range
        },
        context: {
          language: language || rawMatch.language || 'unknown',
          parentSymbol: rawMatch.parentSymbol,
          surroundingCode: rawMatch.surroundingCode || ''
        },
        bindings: rawMatch.bindings || {},
        confidence,
        metadata: {
          matched: rawMatch.matchedText || '',
          suggestions: this.generateSuggestions(pattern, rawMatch),
          explanation: this.generateExplanation(pattern, rawMatch)
        }
      };

      matches.push(match);
    }

    return matches;
  }

  /**
   * Compile Tree-sitter query
   */
  private compileTreeSitterQuery(query: string): any {
    // This would use the Tree-sitter query system
    // For now, return a mock compiled query
    return {
      original: query,
      compiled: true,
      timestamp: Date.now()
    };
  }

  /**
   * Execute compiled query against AST
   */
  private async executeCompiledQuery(compiled: any, code?: string, language?: string): Promise<any[]> {
    // This would execute the Tree-sitter query against the parsed AST
    // For now, return mock matches
    return [];
  }

  /**
   * Calculate confidence score for a match
   */
  private calculateMatchConfidence(pattern: Pattern, rawMatch: any): number {
    let confidence = 0.8; // Base confidence

    // Adjust based on pattern type
    switch (pattern.type) {
      case 'structural':
        confidence *= 0.95; // High confidence for structural matches
        break;
      case 'behavioral':
        confidence *= 0.85; // Medium confidence for behavioral patterns
        break;
      case 'semantic':
        confidence *= 0.75; // Lower confidence for semantic patterns
        break;
      case 'anti-pattern':
        confidence *= 0.9; // High confidence for anti-patterns
        break;
    }

    // Adjust based on constraints satisfaction
    if (rawMatch.constraintsSatisfied) {
      confidence *= 1.1;
    } else {
      confidence *= 0.8;
    }

    return Math.min(confidence, 1.0);
  }

  /**
   * Generate suggestions for improvement
   */
  private generateSuggestions(pattern: Pattern, rawMatch: any): string[] {
    const suggestions: string[] = [];

    switch (pattern.id) {
      case 'long-parameter-list':
        suggestions.push('Consider using a parameter object or builder pattern');
        suggestions.push('Break the function into smaller, more focused functions');
        break;
      case 'sql-injection':
        suggestions.push('Use parameterized queries or prepared statements');
        suggestions.push('Validate and sanitize all user inputs');
        break;
      case 'nested-loops':
        suggestions.push('Consider using more efficient algorithms');
        suggestions.push('Look for opportunities to break or continue early');
        break;
    }

    return suggestions;
  }

  /**
   * Generate explanation for the match
   */
  private generateExplanation(pattern: Pattern, rawMatch: any): string {
    return `Found ${pattern.name}: ${pattern.description}`;
  }

  /**
   * Validate query syntax
   */
  private validateQuerySyntax(query: string): void {
    // This would validate Tree-sitter query syntax
    // For now, just check basic format
    if (!query || typeof query !== 'string') {
      throw new Error('Query must be a non-empty string');
    }

    if (!query.includes('(') || !query.includes(')')) {
      throw new Error('Query must contain valid S-expression syntax');
    }
  }

  /**
   * Extract pattern from examples using machine learning
   */
  private async extractPatternFromExamples(
    examples: Array<{ code: string; language: string; shouldMatch: boolean }>
  ): Promise<Pattern['definition']> {
    // This would use ML to extract common patterns from examples
    // For now, return a simple pattern based on the first positive example
    const positiveExamples = examples.filter(e => e.shouldMatch);
    
    if (positiveExamples.length === 0) {
      throw new Error('At least one positive example is required');
    }

    // Generate a basic structural pattern
    const firstExample = positiveExamples[0];
    
    return {
      query: `(identifier) @name`, // Simplified pattern
      constraints: {},
      variables: { name: 'string' }
    };
  }

  /**
   * Update pattern matching statistics
   */
  private updateStats(matchTime: number, cacheHit: boolean, matchCount: number): void {
    this.stats.totalMatches += matchCount;
    
    // Update average match time
    const totalQueries = this.stats.totalMatches > 0 ? this.stats.totalMatches : 1;
    this.stats.averageMatchTime = (this.stats.averageMatchTime * (totalQueries - 1) + matchTime) / totalQueries;
    
    // Update cache hit rate
    if (cacheHit) {
      const totalHits = this.stats.cacheHitRate * (totalQueries - 1) + 1;
      this.stats.cacheHitRate = totalHits / totalQueries;
    } else {
      this.stats.cacheHitRate = (this.stats.cacheHitRate * (totalQueries - 1)) / totalQueries;
    }
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    this.patterns.clear();
    this.compiledPatterns.clear();
    this.matchCache.clear();
    this.removeAllListeners();
  }
}