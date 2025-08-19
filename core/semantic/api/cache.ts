/**
 * Semantic Analysis Caching Layer
 * 
 * High-performance caching system for semantic analysis results.
 * Supports intelligent cache invalidation, multi-level caching,
 * and performance optimization strategies.
 */

import { LRUCache } from 'lru-cache';
import crypto from 'crypto';
import { EventEmitter } from 'events';

export interface CacheEntry<T = any> {
  key: string;
  value: T;
  timestamp: number;
  accessCount: number;
  size: number;
  ttl?: number;
  tags: Set<string>;
  dependencies: Set<string>;
}

export interface CacheStats {
  hits: number;
  misses: number;
  evictions: number;
  size: number;
  maxSize: number;
  hitRate: number;
  averageAccessTime: number;
  totalRequests: number;
}

export interface CacheOptions {
  maxSize: number;
  defaultTTL: number;
  checkPeriod: number;
  enableStats: boolean;
  enableCompression: boolean;
  compressionThreshold: number;
}

export class SemanticCache extends EventEmitter {
  private cache: LRUCache<string, CacheEntry>;
  private stats: CacheStats;
  private options: CacheOptions;
  private compressionEnabled: boolean;
  private accessTimes: number[] = [];
  private cleanupInterval?: NodeJS.Timeout;

  // Specialized caches for different data types
  private symbolCache: LRUCache<string, any>;
  private astCache: LRUCache<string, any>;
  private relationshipCache: LRUCache<string, any>;
  private searchCache: LRUCache<string, any>;
  private patternCache: LRUCache<string, any>;

  constructor(options: Partial<CacheOptions> = {}) {
    super();

    this.options = {
      maxSize: 1000,
      defaultTTL: 30 * 60 * 1000, // 30 minutes
      checkPeriod: 5 * 60 * 1000, // 5 minutes
      enableStats: true,
      enableCompression: true,
      compressionThreshold: 1024, // 1KB
      ...options
    };

    this.compressionEnabled = this.options.enableCompression;

    // Initialize main cache
    this.cache = new LRUCache({
      max: this.options.maxSize,
      ttl: this.options.defaultTTL,
      updateAgeOnGet: true,
      allowStale: false,
      dispose: (value, key) => {
        this.stats.evictions++;
        this.emit('eviction', key, value);
      }
    });

    // Initialize specialized caches
    const cacheConfig = {
      max: Math.floor(this.options.maxSize / 5),
      ttl: this.options.defaultTTL,
      updateAgeOnGet: true
    };

    this.symbolCache = new LRUCache(cacheConfig);
    this.astCache = new LRUCache(cacheConfig);
    this.relationshipCache = new LRUCache(cacheConfig);
    this.searchCache = new LRUCache({ ...cacheConfig, ttl: 10 * 60 * 1000 }); // Shorter TTL for search
    this.patternCache = new LRUCache(cacheConfig);

    // Initialize stats
    this.stats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      size: 0,
      maxSize: this.options.maxSize,
      hitRate: 0,
      averageAccessTime: 0,
      totalRequests: 0
    };

    // Start cleanup interval
    if (this.options.checkPeriod > 0) {
      this.cleanupInterval = setInterval(() => {
        this.cleanup();
      }, this.options.checkPeriod);
    }
  }

  /**
   * Generate cache key from multiple parameters
   */
  public generateKey(...params: any[]): string {
    const content = JSON.stringify(params);
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Store value in cache with optional metadata
   */
  public set<T>(
    key: string, 
    value: T, 
    options: {
      ttl?: number;
      tags?: string[];
      dependencies?: string[];
      category?: 'symbol' | 'ast' | 'relationship' | 'search' | 'pattern';
    } = {}
  ): boolean {
    const startTime = performance.now();

    try {
      const serializedValue = this.serializeValue(value);
      const size = this.calculateSize(serializedValue);

      const entry: CacheEntry<T> = {
        key,
        value: serializedValue,
        timestamp: Date.now(),
        accessCount: 0,
        size,
        ttl: options.ttl || this.options.defaultTTL,
        tags: new Set(options.tags || []),
        dependencies: new Set(options.dependencies || [])
      };

      // Store in appropriate specialized cache
      if (options.category) {
        this.setInSpecializedCache(options.category, key, entry);
      }

      // Store in main cache
      const success = this.cache.set(key, entry);

      if (success) {
        this.updateStats('set', performance.now() - startTime);
        this.emit('set', key, value);
      }

      return success;
    } catch (error) {
      console.error('Cache set error:', error);
      return false;
    }
  }

  /**
   * Retrieve value from cache
   */
  public get<T>(key: string, category?: 'symbol' | 'ast' | 'relationship' | 'search' | 'pattern'): T | undefined {
    const startTime = performance.now();

    try {
      // Try specialized cache first
      let entry: CacheEntry<T> | undefined;
      
      if (category) {
        entry = this.getFromSpecializedCache(category, key);
      }

      // Fallback to main cache
      if (!entry) {
        entry = this.cache.get(key);
      }

      const accessTime = performance.now() - startTime;

      if (entry) {
        entry.accessCount++;
        this.stats.hits++;
        this.updateStats('hit', accessTime);
        this.emit('hit', key);
        return this.deserializeValue(entry.value);
      } else {
        this.stats.misses++;
        this.updateStats('miss', accessTime);
        this.emit('miss', key);
        return undefined;
      }
    } catch (error) {
      console.error('Cache get error:', error);
      this.stats.misses++;
      return undefined;
    }
  }

  /**
   * Check if key exists in cache
   */
  public has(key: string, category?: string): boolean {
    if (category) {
      return this.hasInSpecializedCache(category as any, key);
    }
    return this.cache.has(key);
  }

  /**
   * Delete entry from cache
   */
  public delete(key: string, category?: string): boolean {
    if (category) {
      this.deleteFromSpecializedCache(category as any, key);
    }
    
    const success = this.cache.delete(key);
    if (success) {
      this.emit('delete', key);
    }
    return success;
  }

  /**
   * Clear cache by tags
   */
  public clearByTag(tag: string): number {
    let cleared = 0;
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.tags.has(tag)) {
        this.cache.delete(key);
        cleared++;
      }
    }

    // Clear from specialized caches
    const caches = [this.symbolCache, this.astCache, this.relationshipCache, this.searchCache, this.patternCache];
    for (const cache of caches) {
      for (const [key, entry] of cache.entries()) {
        if (entry.tags.has(tag)) {
          cache.delete(key);
          cleared++;
        }
      }
    }

    this.emit('clearByTag', tag, cleared);
    return cleared;
  }

  /**
   * Clear cache by dependencies
   */
  public clearByDependency(dependency: string): number {
    let cleared = 0;
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.dependencies.has(dependency)) {
        this.cache.delete(key);
        cleared++;
      }
    }

    this.emit('clearByDependency', dependency, cleared);
    return cleared;
  }

  /**
   * Clear entire cache
   */
  public clear(): void {
    this.cache.clear();
    this.symbolCache.clear();
    this.astCache.clear();
    this.relationshipCache.clear();
    this.searchCache.clear();
    this.patternCache.clear();
    
    this.stats.evictions += this.stats.size;
    this.stats.size = 0;
    this.emit('clear');
  }

  /**
   * Get cache statistics
   */
  public getStats(): CacheStats {
    this.stats.size = this.cache.size;
    this.stats.hitRate = this.stats.totalRequests > 0 
      ? this.stats.hits / this.stats.totalRequests 
      : 0;
    
    this.stats.averageAccessTime = this.accessTimes.length > 0
      ? this.accessTimes.reduce((a, b) => a + b, 0) / this.accessTimes.length
      : 0;

    return { ...this.stats };
  }

  /**
   * Get cache entries by category
   */
  public getEntriesByCategory(category: 'symbol' | 'ast' | 'relationship' | 'search' | 'pattern'): Map<string, any> {
    const cache = this.getSpecializedCache(category);
    return new Map(cache.entries());
  }

  /**
   * Optimize cache performance
   */
  public optimize(): void {
    // Remove expired entries
    this.cleanup();

    // Promote frequently accessed items
    this.promoteFrequentlyAccessed();

    // Compress large entries
    if (this.compressionEnabled) {
      this.compressLargeEntries();
    }

    this.emit('optimize');
  }

  /**
   * Export cache contents for backup
   */
  public export(): any {
    return {
      timestamp: Date.now(),
      main: Array.from(this.cache.entries()),
      symbol: Array.from(this.symbolCache.entries()),
      ast: Array.from(this.astCache.entries()),
      relationship: Array.from(this.relationshipCache.entries()),
      search: Array.from(this.searchCache.entries()),
      pattern: Array.from(this.patternCache.entries()),
      stats: this.stats
    };
  }

  /**
   * Import cache contents from backup
   */
  public import(data: any): void {
    this.clear();

    if (data.main) {
      for (const [key, entry] of data.main) {
        this.cache.set(key, entry);
      }
    }

    if (data.symbol) {
      for (const [key, entry] of data.symbol) {
        this.symbolCache.set(key, entry);
      }
    }

    // Import other specialized caches...
    
    this.emit('import', data.timestamp);
  }

  /**
   * Cleanup expired and stale entries
   */
  private cleanup(): void {
    const now = Date.now();
    let cleaned = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (entry.ttl && (now - entry.timestamp) > entry.ttl) {
        this.cache.delete(key);
        cleaned++;
      }
    }

    if (cleaned > 0) {
      this.emit('cleanup', cleaned);
    }
  }

  /**
   * Promote frequently accessed items to prevent eviction
   */
  private promoteFrequentlyAccessed(): void {
    const entries = Array.from(this.cache.entries())
      .map(([key, entry]) => ({ key, entry }))
      .sort((a, b) => b.entry.accessCount - a.entry.accessCount)
      .slice(0, Math.floor(this.options.maxSize * 0.1)); // Top 10%

    for (const { key, entry } of entries) {
      // Move to front of LRU
      this.cache.delete(key);
      this.cache.set(key, entry);
    }
  }

  /**
   * Compress large entries to save memory
   */
  private compressLargeEntries(): void {
    // Implementation would use a compression library like zlib
    // This is a placeholder for the compression logic
  }

  /**
   * Serialize value for storage
   */
  private serializeValue<T>(value: T): any {
    if (this.compressionEnabled && this.calculateSize(value) > this.options.compressionThreshold) {
      // Implement compression here
      return value;
    }
    return value;
  }

  /**
   * Deserialize value from storage
   */
  private deserializeValue<T>(value: any): T {
    return value;
  }

  /**
   * Calculate approximate size of value
   */
  private calculateSize(value: any): number {
    try {
      return JSON.stringify(value).length;
    } catch {
      return 0;
    }
  }

  /**
   * Update statistics
   */
  private updateStats(operation: string, accessTime: number): void {
    if (!this.options.enableStats) return;

    this.stats.totalRequests++;
    this.accessTimes.push(accessTime);

    // Keep only recent access times for average calculation
    if (this.accessTimes.length > 1000) {
      this.accessTimes = this.accessTimes.slice(-1000);
    }
  }

  /**
   * Handle specialized cache operations
   */
  private setInSpecializedCache(category: string, key: string, entry: CacheEntry): void {
    const cache = this.getSpecializedCache(category as any);
    cache.set(key, entry);
  }

  private getFromSpecializedCache(category: string, key: string): CacheEntry | undefined {
    const cache = this.getSpecializedCache(category as any);
    return cache.get(key);
  }

  private hasInSpecializedCache(category: string, key: string): boolean {
    const cache = this.getSpecializedCache(category as any);
    return cache.has(key);
  }

  private deleteFromSpecializedCache(category: string, key: string): boolean {
    const cache = this.getSpecializedCache(category as any);
    return cache.delete(key);
  }

  private getSpecializedCache(category: 'symbol' | 'ast' | 'relationship' | 'search' | 'pattern'): LRUCache<string, any> {
    switch (category) {
      case 'symbol': return this.symbolCache;
      case 'ast': return this.astCache;
      case 'relationship': return this.relationshipCache;
      case 'search': return this.searchCache;
      case 'pattern': return this.patternCache;
      default: return this.cache;
    }
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.clear();
    this.removeAllListeners();
  }
}