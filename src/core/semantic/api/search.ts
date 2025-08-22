/**
 * Semantic Search Engine
 * 
 * Advanced semantic search capabilities for cross-language code analysis.
 * Supports fuzzy matching, semantic similarity, and intelligent ranking.
 */

import { EventEmitter } from 'events';
import { SemanticCache } from './cache';

export interface SearchQuery {
  text: string;
  type?: 'exact' | 'fuzzy' | 'semantic' | 'regex';
  filters: {
    language?: string[];
    symbolKind?: string[];
    filePattern?: string;
    scope?: 'local' | 'project' | 'global';
    includeDocumentation?: boolean;
    includeComments?: boolean;
  };
  options: {
    maxResults?: number;
    includeReferences?: boolean;
    includeDefinitions?: boolean;
    crossLanguage?: boolean;
    caseSensitive?: boolean;
    wholeWord?: boolean;
  };
}

export interface SearchResult {
  id: string;
  symbol: {
    id: string;
    name: string;
    kind: string;
    signature?: string;
    documentation?: string;
  };
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
    module?: string;
    namespace?: string;
  };
  match: {
    score: number;
    type: 'exact' | 'partial' | 'fuzzy' | 'semantic';
    highlightRanges: Array<{
      start: number;
      end: number;
    }>;
  };
  references?: SearchResult[];
}

export interface SearchStats {
  totalQueries: number;
  averageQueryTime: number;
  cacheHitRate: number;
  indexSize: number;
  lastIndexUpdate: number;
}

export interface SymbolIndex {
  symbols: Map<string, any>;
  byName: Map<string, string[]>;
  byKind: Map<string, string[]>;
  byLanguage: Map<string, string[]>;
  byFile: Map<string, string[]>;
  relationships: Map<string, string[]>;
  fullTextIndex: Map<string, Set<string>>;
}

export class SemanticSearchEngine extends EventEmitter {
  private cache: SemanticCache;
  private symbolIndex: SymbolIndex;
  private stats: SearchStats;
  private indexUpdateInterval?: NodeJS.Timeout;
  private queryCache: Map<string, SearchResult[]> = new Map();

  constructor(cache: SemanticCache) {
    super();
    
    this.cache = cache;
    this.symbolIndex = {
      symbols: new Map(),
      byName: new Map(),
      byKind: new Map(),
      byLanguage: new Map(),
      byFile: new Map(),
      relationships: new Map(),
      fullTextIndex: new Map()
    };

    this.stats = {
      totalQueries: 0,
      averageQueryTime: 0,
      cacheHitRate: 0,
      indexSize: 0,
      lastIndexUpdate: Date.now()
    };

    this.startIndexMaintenance();
  }

  /**
   * Search for symbols based on query criteria
   */
  public async searchSymbols(query: SearchQuery): Promise<SearchResult[]> {
    const startTime = performance.now();
    this.stats.totalQueries++;

    try {
      // Generate cache key for the query
      const cacheKey = this.cache.generateKey('search', query);
      
      // Check query cache first
      let results = this.queryCache.get(cacheKey);
      if (results) {
        this.updateStats(performance.now() - startTime, true);
        return results;
      }

      // Check semantic cache
      results = this.cache.get(cacheKey, 'search');
      if (results) {
        this.queryCache.set(cacheKey, results);
        this.updateStats(performance.now() - startTime, true);
        return results;
      }

      // Perform actual search
      results = await this.performSearch(query);

      // Cache the results
      this.cache.set(cacheKey, results, {
        category: 'search',
        ttl: 10 * 60 * 1000, // 10 minutes for search results
        tags: ['search', ...(query.filters.language || [])]
      });
      
      this.queryCache.set(cacheKey, results);
      this.updateStats(performance.now() - startTime, false);

      return results;

    } catch (error) {
      console.error('Search error:', error);
      this.updateStats(performance.now() - startTime, false);
      throw error;
    }
  }

  /**
   * Find references to a specific symbol
   */
  public async findReferences(symbolId: string): Promise<SearchResult[]> {
    const cacheKey = this.cache.generateKey('references', symbolId);
    
    let references = this.cache.get(cacheKey, 'search');
    if (references) {
      return references;
    }

    references = await this.performReferenceSearch(symbolId);
    
    this.cache.set(cacheKey, references, {
      category: 'search',
      ttl: 30 * 60 * 1000, // 30 minutes for references
      tags: ['references', symbolId]
    });

    return references;
  }

  /**
   * Find definitions of a symbol
   */
  public async findDefinitions(symbolName: string, options: Partial<SearchQuery> = {}): Promise<SearchResult[]> {
    const query: SearchQuery = {
      text: symbolName,
      type: 'exact',
      filters: {
        scope: 'project',
        ...options.filters
      },
      options: {
        includeDefinitions: true,
        includeReferences: false,
        maxResults: 50,
        ...options.options
      }
    };

    const results = await this.searchSymbols(query);
    return results.filter(result => result.symbol.name === symbolName);
  }

  /**
   * Semantic similarity search
   */
  public async findSimilar(symbolId: string, threshold: number = 0.7): Promise<SearchResult[]> {
    const symbol = this.symbolIndex.symbols.get(symbolId);
    if (!symbol) {
      return [];
    }

    const candidates = await this.findCandidateSymbols(symbol);
    const similarities = await this.calculateSimilarities(symbol, candidates);
    
    return similarities
      .filter(item => item.similarity >= threshold)
      .sort((a, b) => b.similarity - a.similarity)
      .map(item => item.result);
  }

  /**
   * Cross-language symbol search
   */
  public async searchCrossLanguage(query: SearchQuery): Promise<Map<string, SearchResult[]>> {
    const languages = query.filters.language || this.getSupportedLanguages();
    const resultsByLanguage = new Map<string, SearchResult[]>();

    for (const language of languages) {
      const languageQuery: SearchQuery = {
        ...query,
        filters: {
          ...query.filters,
          language: [language]
        }
      };

      const results = await this.searchSymbols(languageQuery);
      resultsByLanguage.set(language, results);
    }

    return resultsByLanguage;
  }

  /**
   * Advanced pattern-based search
   */
  public async searchByPattern(pattern: string, type: 'ast' | 'regex' | 'semantic'): Promise<SearchResult[]> {
    switch (type) {
      case 'regex':
        return this.searchByRegex(pattern);
      case 'ast':
        return this.searchByASTPattern(pattern);
      case 'semantic':
        return this.searchBySemanticPattern(pattern);
      default:
        throw new Error(`Unsupported pattern type: ${type}`);
    }
  }

  /**
   * Update symbol index with new data
   */
  public updateIndex(symbols: any[], relationships: any[]): void {
    const startTime = performance.now();

    // Clear existing index for incremental update
    this.clearIndex();

    // Index symbols
    for (const symbol of symbols) {
      this.indexSymbol(symbol);
    }

    // Index relationships
    for (const relationship of relationships) {
      this.indexRelationship(relationship);
    }

    // Update full-text index
    this.updateFullTextIndex();

    this.stats.indexSize = this.symbolIndex.symbols.size;
    this.stats.lastIndexUpdate = Date.now();

    console.log(`Index updated in ${performance.now() - startTime}ms - ${symbols.length} symbols, ${relationships.length} relationships`);
    this.emit('index-updated', { symbols: symbols.length, relationships: relationships.length });
  }

  /**
   * Get search statistics
   */
  public getStats(): SearchStats {
    return { ...this.stats };
  }

  /**
   * Clear all cached search results
   */
  public clearCache(): void {
    this.queryCache.clear();
    this.cache.clearByTag('search');
    this.emit('cache-cleared');
  }

  /**
   * Export search index for backup
   */
  public exportIndex(): any {
    return {
      timestamp: Date.now(),
      symbols: Array.from(this.symbolIndex.symbols.entries()),
      byName: Array.from(this.symbolIndex.byName.entries()),
      byKind: Array.from(this.symbolIndex.byKind.entries()),
      byLanguage: Array.from(this.symbolIndex.byLanguage.entries()),
      byFile: Array.from(this.symbolIndex.byFile.entries()),
      relationships: Array.from(this.symbolIndex.relationships.entries()),
      stats: this.stats
    };
  }

  /**
   * Import search index from backup
   */
  public importIndex(data: any): void {
    this.clearIndex();

    if (data.symbols) {
      this.symbolIndex.symbols = new Map(data.symbols);
    }
    if (data.byName) {
      this.symbolIndex.byName = new Map(data.byName);
    }
    if (data.byKind) {
      this.symbolIndex.byKind = new Map(data.byKind);
    }
    if (data.byLanguage) {
      this.symbolIndex.byLanguage = new Map(data.byLanguage);
    }
    if (data.byFile) {
      this.symbolIndex.byFile = new Map(data.byFile);
    }
    if (data.relationships) {
      this.symbolIndex.relationships = new Map(data.relationships);
    }

    this.updateFullTextIndex();
    this.stats.lastIndexUpdate = data.timestamp || Date.now();
    this.emit('index-imported', data);
  }

  /**
   * Perform the actual search operation
   */
  private async performSearch(query: SearchQuery): Promise<SearchResult[]> {
    let candidates: string[] = [];

    // Get initial candidates based on search type
    switch (query.type) {
      case 'exact':
        candidates = this.findExactMatches(query.text);
        break;
      case 'fuzzy':
        candidates = this.findFuzzyMatches(query.text);
        break;
      case 'semantic':
        candidates = await this.findSemanticMatches(query.text);
        break;
      case 'regex':
        candidates = this.findRegexMatches(query.text);
        break;
      default:
        candidates = this.findExactMatches(query.text);
    }

    // Apply filters
    candidates = this.applyFilters(candidates, query.filters);

    // Convert to search results and rank
    const results = this.convertToSearchResults(candidates, query);
    
    // Sort by relevance score
    results.sort((a, b) => b.match.score - a.match.score);

    // Apply limit
    const maxResults = query.options.maxResults || 100;
    return results.slice(0, maxResults);
  }

  private async performReferenceSearch(symbolId: string): Promise<SearchResult[]> {
    const referenceIds = this.symbolIndex.relationships.get(symbolId) || [];
    return this.convertToSearchResults(referenceIds, {
      text: '',
      filters: {},
      options: { includeReferences: true }
    });
  }

  private findExactMatches(text: string): string[] {
    const symbolIds = this.symbolIndex.byName.get(text) || [];
    return [...symbolIds];
  }

  private findFuzzyMatches(text: string): string[] {
    const matches: string[] = [];
    const normalizedQuery = text.toLowerCase();

    for (const [name, symbolIds] of this.symbolIndex.byName) {
      const similarity = this.calculateStringSimilarity(normalizedQuery, name.toLowerCase());
      if (similarity > 0.6) { // Threshold for fuzzy matching
        matches.push(...symbolIds);
      }
    }

    return matches;
  }

  private async findSemanticMatches(text: string): Promise<string[]> {
    // This would integrate with a semantic similarity model
    // For now, return fuzzy matches as a fallback
    return this.findFuzzyMatches(text);
  }

  private findRegexMatches(pattern: string): string[] {
    try {
      const regex = new RegExp(pattern, 'i');
      const matches: string[] = [];

      for (const [name, symbolIds] of this.symbolIndex.byName) {
        if (regex.test(name)) {
          matches.push(...symbolIds);
        }
      }

      return matches;
    } catch (error) {
      console.error('Invalid regex pattern:', pattern, error);
      return [];
    }
  }

  private applyFilters(candidates: string[], filters: SearchQuery['filters']): string[] {
    let filtered = candidates;

    if (filters.language && filters.language.length > 0) {
      filtered = filtered.filter(id => {
        const symbol = this.symbolIndex.symbols.get(id);
        return symbol && filters.language!.includes(symbol.language);
      });
    }

    if (filters.symbolKind && filters.symbolKind.length > 0) {
      filtered = filtered.filter(id => {
        const symbol = this.symbolIndex.symbols.get(id);
        return symbol && filters.symbolKind!.includes(symbol.kind);
      });
    }

    if (filters.filePattern) {
      const fileRegex = new RegExp(filters.filePattern, 'i');
      filtered = filtered.filter(id => {
        const symbol = this.symbolIndex.symbols.get(id);
        return symbol && fileRegex.test(symbol.filePath || '');
      });
    }

    return filtered;
  }

  private convertToSearchResults(symbolIds: string[], query: SearchQuery): SearchResult[] {
    const results: SearchResult[] = [];

    for (const symbolId of symbolIds) {
      const symbol = this.symbolIndex.symbols.get(symbolId);
      if (!symbol) continue;

      const result: SearchResult = {
        id: symbolId,
        symbol: {
          id: symbolId,
          name: symbol.name,
          kind: symbol.kind,
          signature: symbol.signature,
          documentation: symbol.documentation
        },
        location: {
          fileId: symbol.fileId,
          filePath: symbol.filePath,
          range: symbol.range
        },
        context: {
          language: symbol.language,
          parentSymbol: symbol.parentSymbol,
          module: symbol.module,
          namespace: symbol.namespace
        },
        match: {
          score: this.calculateRelevanceScore(symbol, query),
          type: this.getMatchType(symbol.name, query.text),
          highlightRanges: this.getHighlightRanges(symbol.name, query.text)
        }
      };

      // Add references if requested
      if (query.options.includeReferences) {
        result.references = this.getSymbolReferences(symbolId);
      }

      results.push(result);
    }

    return results;
  }

  private async searchByRegex(pattern: string): Promise<SearchResult[]> {
    const query: SearchQuery = {
      text: pattern,
      type: 'regex',
      filters: {},
      options: { maxResults: 100 }
    };

    return this.performSearch(query);
  }

  private async searchByASTPattern(pattern: string): Promise<SearchResult[]> {
    // This would integrate with AST pattern matching
    // For now, return empty results
    return [];
  }

  private async searchBySemanticPattern(pattern: string): Promise<SearchResult[]> {
    // This would use semantic understanding for pattern matching
    // For now, return fuzzy search results
    const query: SearchQuery = {
      text: pattern,
      type: 'semantic',
      filters: {},
      options: { maxResults: 100 }
    };

    return this.performSearch(query);
  }

  private indexSymbol(symbol: any): void {
    const symbolId = symbol.id;
    
    // Store symbol
    this.symbolIndex.symbols.set(symbolId, symbol);

    // Index by name
    if (!this.symbolIndex.byName.has(symbol.name)) {
      this.symbolIndex.byName.set(symbol.name, []);
    }
    this.symbolIndex.byName.get(symbol.name)!.push(symbolId);

    // Index by kind
    if (!this.symbolIndex.byKind.has(symbol.kind)) {
      this.symbolIndex.byKind.set(symbol.kind, []);
    }
    this.symbolIndex.byKind.get(symbol.kind)!.push(symbolId);

    // Index by language
    if (!this.symbolIndex.byLanguage.has(symbol.language)) {
      this.symbolIndex.byLanguage.set(symbol.language, []);
    }
    this.symbolIndex.byLanguage.get(symbol.language)!.push(symbolId);

    // Index by file
    if (!this.symbolIndex.byFile.has(symbol.fileId)) {
      this.symbolIndex.byFile.set(symbol.fileId, []);
    }
    this.symbolIndex.byFile.get(symbol.fileId)!.push(symbolId);
  }

  private indexRelationship(relationship: any): void {
    const sourceId = relationship.source;
    const targetId = relationship.target;

    if (!this.symbolIndex.relationships.has(sourceId)) {
      this.symbolIndex.relationships.set(sourceId, []);
    }
    this.symbolIndex.relationships.get(sourceId)!.push(targetId);
  }

  private updateFullTextIndex(): void {
    this.symbolIndex.fullTextIndex.clear();

    for (const [symbolId, symbol] of this.symbolIndex.symbols) {
      const tokens = this.tokenize(symbol.name + ' ' + (symbol.signature || '') + ' ' + (symbol.documentation || ''));
      
      for (const token of tokens) {
        if (!this.symbolIndex.fullTextIndex.has(token)) {
          this.symbolIndex.fullTextIndex.set(token, new Set());
        }
        this.symbolIndex.fullTextIndex.get(token)!.add(symbolId);
      }
    }
  }

  private tokenize(text: string): string[] {
    return text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(token => token.length > 2);
  }

  private calculateRelevanceScore(symbol: any, query: SearchQuery): number {
    let score = 0;

    // Exact name match
    if (symbol.name === query.text) {
      score += 100;
    } else if (symbol.name.toLowerCase() === query.text.toLowerCase()) {
      score += 80;
    } else if (symbol.name.toLowerCase().includes(query.text.toLowerCase())) {
      score += 60;
    }

    // Signature match
    if (symbol.signature && symbol.signature.toLowerCase().includes(query.text.toLowerCase())) {
      score += 30;
    }

    // Documentation match
    if (symbol.documentation && symbol.documentation.toLowerCase().includes(query.text.toLowerCase())) {
      score += 20;
    }

    // Symbol kind preferences (functions/methods are often more relevant)
    if (['function', 'method'].includes(symbol.kind)) {
      score += 10;
    }

    return score;
  }

  private getMatchType(symbolName: string, queryText: string): 'exact' | 'partial' | 'fuzzy' | 'semantic' {
    if (symbolName === queryText) return 'exact';
    if (symbolName.toLowerCase() === queryText.toLowerCase()) return 'exact';
    if (symbolName.toLowerCase().includes(queryText.toLowerCase())) return 'partial';
    return 'fuzzy';
  }

  private getHighlightRanges(symbolName: string, queryText: string): Array<{ start: number; end: number }> {
    const ranges: Array<{ start: number; end: number }> = [];
    const lowerSymbol = symbolName.toLowerCase();
    const lowerQuery = queryText.toLowerCase();
    
    let index = 0;
    while ((index = lowerSymbol.indexOf(lowerQuery, index)) !== -1) {
      ranges.push({
        start: index,
        end: index + queryText.length
      });
      index += queryText.length;
    }

    return ranges;
  }

  private getSymbolReferences(symbolId: string): SearchResult[] {
    // This would be implemented to find actual references
    return [];
  }

  private calculateStringSimilarity(str1: string, str2: string): number {
    // Simple Levenshtein distance based similarity
    const maxLen = Math.max(str1.length, str2.length);
    if (maxLen === 0) return 1;
    
    const distance = this.levenshteinDistance(str1, str2);
    return 1 - (distance / maxLen);
  }

  private levenshteinDistance(str1: string, str2: string): number {
    const matrix = Array(str2.length + 1).fill(null).map(() => Array(str1.length + 1).fill(null));

    for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
    for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;

    for (let j = 1; j <= str2.length; j++) {
      for (let i = 1; i <= str1.length; i++) {
        const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1,     // deletion
          matrix[j - 1][i] + 1,     // insertion
          matrix[j - 1][i - 1] + indicator  // substitution
        );
      }
    }

    return matrix[str2.length][str1.length];
  }

  private async findCandidateSymbols(targetSymbol: any): Promise<any[]> {
    // Find symbols of the same kind for similarity comparison
    const sameKindIds = this.symbolIndex.byKind.get(targetSymbol.kind) || [];
    return sameKindIds
      .map(id => this.symbolIndex.symbols.get(id))
      .filter(symbol => symbol && symbol.id !== targetSymbol.id);
  }

  private async calculateSimilarities(targetSymbol: any, candidates: any[]): Promise<Array<{ result: SearchResult; similarity: number }>> {
    const similarities: Array<{ result: SearchResult; similarity: number }> = [];

    for (const candidate of candidates) {
      const similarity = this.calculateSemanticSimilarity(targetSymbol, candidate);
      
      if (similarity > 0) {
        const result: SearchResult = {
          id: candidate.id,
          symbol: {
            id: candidate.id,
            name: candidate.name,
            kind: candidate.kind,
            signature: candidate.signature,
            documentation: candidate.documentation
          },
          location: {
            fileId: candidate.fileId,
            filePath: candidate.filePath,
            range: candidate.range
          },
          context: {
            language: candidate.language,
            parentSymbol: candidate.parentSymbol,
            module: candidate.module,
            namespace: candidate.namespace
          },
          match: {
            score: similarity * 100,
            type: 'semantic',
            highlightRanges: []
          }
        };

        similarities.push({ result, similarity });
      }
    }

    return similarities;
  }

  private calculateSemanticSimilarity(symbol1: any, symbol2: any): number {
    // Simple semantic similarity based on name, signature, and context
    let similarity = 0;

    // Name similarity
    similarity += this.calculateStringSimilarity(symbol1.name, symbol2.name) * 0.4;

    // Signature similarity
    if (symbol1.signature && symbol2.signature) {
      similarity += this.calculateStringSimilarity(symbol1.signature, symbol2.signature) * 0.3;
    }

    // Context similarity (same module/namespace)
    if (symbol1.module === symbol2.module) similarity += 0.2;
    if (symbol1.namespace === symbol2.namespace) similarity += 0.1;

    return Math.min(similarity, 1);
  }

  private getSupportedLanguages(): string[] {
    return Array.from(this.symbolIndex.byLanguage.keys());
  }

  private clearIndex(): void {
    this.symbolIndex.symbols.clear();
    this.symbolIndex.byName.clear();
    this.symbolIndex.byKind.clear();
    this.symbolIndex.byLanguage.clear();
    this.symbolIndex.byFile.clear();
    this.symbolIndex.relationships.clear();
    this.symbolIndex.fullTextIndex.clear();
  }

  private updateStats(queryTime: number, cacheHit: boolean): void {
    this.stats.averageQueryTime = (this.stats.averageQueryTime * (this.stats.totalQueries - 1) + queryTime) / this.stats.totalQueries;
    
    if (cacheHit) {
      const totalHits = this.stats.cacheHitRate * (this.stats.totalQueries - 1) + 1;
      this.stats.cacheHitRate = totalHits / this.stats.totalQueries;
    } else {
      this.stats.cacheHitRate = (this.stats.cacheHitRate * (this.stats.totalQueries - 1)) / this.stats.totalQueries;
    }
  }

  private startIndexMaintenance(): void {
    // Periodic index optimization
    this.indexUpdateInterval = setInterval(() => {
      this.optimizeIndex();
    }, 5 * 60 * 1000); // Every 5 minutes
  }

  private optimizeIndex(): void {
    // Clear stale entries
    this.queryCache.clear();
    
    // Emit maintenance event
    this.emit('index-optimized');
  }

  public destroy(): void {
    if (this.indexUpdateInterval) {
      clearInterval(this.indexUpdateInterval);
    }
    
    this.clearIndex();
    this.queryCache.clear();
    this.removeAllListeners();
  }
}