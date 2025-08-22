#!/usr/bin/env node
/**
 * Cross-Agent Context Preservation System
 * Provides robust context sharing, persistence, and management
 */

const { Pool } = require('pg');
const Redis = require('redis');
const crypto = require('crypto');
const EventEmitter = require('events');
const compression = require('compression');

class ContextManager extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.config = {
      postgres: {
        host: options.pgHost || process.env.POSTGRES_HOST || 'localhost',
        port: options.pgPort || process.env.POSTGRES_PORT || 5432,
        database: options.pgDatabase || process.env.POSTGRES_DB || 'claude_dev_stack',
        user: options.pgUser || process.env.POSTGRES_USER || 'claude',
        password: options.pgPassword || process.env.POSTGRES_PASSWORD || 'claude_dev_db',
        max: 20,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000,
      },
      redis: {
        url: options.redisUrl || process.env.REDIS_URL || 'redis://localhost:6379',
        password: options.redisPassword || process.env.REDIS_PASSWORD || 'claude_dev_redis',
        keyPrefix: 'context:',
        ttl: options.redisTtl || 3600, // 1 hour default
      },
      encryption: {
        algorithm: 'aes-256-gcm',
        keyLength: 32,
        ivLength: 16,
        tagLength: 16,
        secretKey: options.encryptionKey || process.env.CONTEXT_ENCRYPTION_KEY
      },
      compression: {
        threshold: 1024, // Compress contexts larger than 1KB
        algorithm: 'gzip'
      },
      versioning: {
        maxVersions: 10,
        autoCleanup: true
      },
      expiration: {
        defaultTtl: 86400, // 24 hours
        maxTtl: 604800, // 7 days
        cleanupInterval: 3600 // 1 hour
      }
    };

    this.pgPool = null;
    this.redisClient = null;
    this.isInitialized = false;
    this.stats = {
      reads: 0,
      writes: 0,
      cacheHits: 0,
      cacheMisses: 0,
      compressions: 0,
      encryptions: 0
    };
  }

  /**
   * Initialize the context manager
   */
  async initialize() {
    try {
      await this.initializePostgreSQL();
      await this.initializeRedis();
      await this.setupSchema();
      await this.startCleanupScheduler();
      
      this.isInitialized = true;
      this.emit('initialized');
      console.log('Context Manager initialized successfully');
      
      return true;
    } catch (error) {
      console.error('Failed to initialize Context Manager:', error);
      throw error;
    }
  }

  /**
   * Initialize PostgreSQL connection
   */
  async initializePostgreSQL() {
    this.pgPool = new Pool(this.config.postgres);
    
    this.pgPool.on('error', (err) => {
      console.error('PostgreSQL pool error:', err);
      this.emit('error', err);
    });

    // Test connection
    const client = await this.pgPool.connect();
    await client.query('SELECT NOW()');
    client.release();
    
    console.log('PostgreSQL connection established');
  }

  /**
   * Initialize Redis connection
   */
  async initializeRedis() {
    this.redisClient = Redis.createClient({
      url: this.config.redis.url,
      password: this.config.redis.password
    });

    this.redisClient.on('error', (err) => {
      console.error('Redis error:', err);
      this.emit('error', err);
    });

    this.redisClient.on('connect', () => {
      console.log('Redis connection established');
    });

    await this.redisClient.connect();
  }

  /**
   * Setup database schema
   */
  async setupSchema() {
    const client = await this.pgPool.connect();
    
    try {
      await client.query('BEGIN');

      // Context storage table
      await client.query(`
        CREATE TABLE IF NOT EXISTS context_storage (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          context_key VARCHAR(255) NOT NULL,
          session_id VARCHAR(255),
          agent_id VARCHAR(255),
          version INTEGER DEFAULT 1,
          context_data JSONB NOT NULL,
          metadata JSONB DEFAULT '{}',
          tags TEXT[],
          is_encrypted BOOLEAN DEFAULT false,
          is_compressed BOOLEAN DEFAULT false,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          expires_at TIMESTAMP WITH TIME ZONE,
          access_count INTEGER DEFAULT 0,
          last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
      `);

      // Context versioning table
      await client.query(`
        CREATE TABLE IF NOT EXISTS context_versions (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          context_id UUID REFERENCES context_storage(id) ON DELETE CASCADE,
          version INTEGER NOT NULL,
          context_data JSONB NOT NULL,
          metadata JSONB DEFAULT '{}',
          change_type VARCHAR(50) DEFAULT 'update',
          changed_by VARCHAR(255),
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
      `);

      // Context relationships table
      await client.query(`
        CREATE TABLE IF NOT EXISTS context_relationships (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          parent_context_id UUID REFERENCES context_storage(id) ON DELETE CASCADE,
          child_context_id UUID REFERENCES context_storage(id) ON DELETE CASCADE,
          relationship_type VARCHAR(50) NOT NULL,
          strength DECIMAL(3,2) DEFAULT 1.0,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          UNIQUE(parent_context_id, child_context_id, relationship_type)
        )
      `);

      // Context search table for full-text search
      await client.query(`
        CREATE TABLE IF NOT EXISTS context_search (
          context_id UUID PRIMARY KEY REFERENCES context_storage(id) ON DELETE CASCADE,
          search_vector tsvector,
          content_hash VARCHAR(64) UNIQUE,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
      `);

      // Create indexes
      await client.query(`
        CREATE INDEX IF NOT EXISTS idx_context_key ON context_storage(context_key);
        CREATE INDEX IF NOT EXISTS idx_session_agent ON context_storage(session_id, agent_id);
        CREATE INDEX IF NOT EXISTS idx_context_expires ON context_storage(expires_at);
        CREATE INDEX IF NOT EXISTS idx_context_tags ON context_storage USING gin(tags);
        CREATE INDEX IF NOT EXISTS idx_context_search_vector ON context_search USING gin(search_vector);
        CREATE INDEX IF NOT EXISTS idx_context_versions_context_id ON context_versions(context_id, version);
      `);

      await client.query('COMMIT');
      console.log('Database schema setup completed');
      
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Store context data
   */
  async storeContext(key, data, options = {}) {
    if (!this.isInitialized) {
      throw new Error('Context Manager not initialized');
    }

    try {
      const contextData = {
        key,
        sessionId: options.sessionId,
        agentId: options.agentId,
        data,
        metadata: options.metadata || {},
        tags: options.tags || [],
        ttl: options.ttl || this.config.expiration.defaultTtl,
        encrypt: options.encrypt || false,
        compress: options.compress || (JSON.stringify(data).length > this.config.compression.threshold)
      };

      // Process data (compression/encryption)
      const processedData = await this.processContextData(contextData);
      
      // Store in PostgreSQL
      const contextId = await this.storeInPostgreSQL(processedData);
      
      // Cache in Redis
      await this.cacheInRedis(key, processedData, contextData.ttl);
      
      // Update search index
      await this.updateSearchIndex(contextId, data);
      
      this.stats.writes++;
      this.emit('contextStored', { key, contextId, options });
      
      return {
        contextId,
        key,
        version: processedData.version,
        stored: true
      };
      
    } catch (error) {
      console.error('Error storing context:', error);
      throw error;
    }
  }

  /**
   * Retrieve context data
   */
  async getContext(key, options = {}) {
    if (!this.isInitialized) {
      throw new Error('Context Manager not initialized');
    }

    try {
      // Try Redis cache first
      let contextData = await this.getFromRedis(key);
      let fromCache = false;

      if (contextData) {
        this.stats.cacheHits++;
        fromCache = true;
      } else {
        // Fallback to PostgreSQL
        contextData = await this.getFromPostgreSQL(key, options);
        this.stats.cacheMisses++;
        
        if (contextData) {
          // Cache for future reads
          await this.cacheInRedis(key, contextData, this.config.redis.ttl);
        }
      }

      if (!contextData) {
        return null;
      }

      // Process data (decompression/decryption)
      const processedData = await this.unprocessContextData(contextData);
      
      // Update access statistics
      await this.updateAccessStats(contextData.id || key);
      
      this.stats.reads++;
      this.emit('contextRetrieved', { key, fromCache, options });
      
      return {
        ...processedData,
        fromCache,
        accessCount: contextData.access_count || 0
      };
      
    } catch (error) {
      console.error('Error retrieving context:', error);
      throw error;
    }
  }

  /**
   * Update existing context
   */
  async updateContext(key, data, options = {}) {
    if (!this.isInitialized) {
      throw new Error('Context Manager not initialized');
    }

    try {
      // Get current context for versioning
      const existingContext = await this.getFromPostgreSQL(key);
      
      if (!existingContext) {
        throw new Error(`Context with key '${key}' not found`);
      }

      // Create new version
      const newVersion = (existingContext.version || 1) + 1;
      
      const contextData = {
        ...existingContext,
        data,
        version: newVersion,
        metadata: { ...existingContext.metadata, ...options.metadata },
        tags: options.tags || existingContext.tags,
        updatedAt: new Date()
      };

      // Process data
      const processedData = await this.processContextData(contextData);
      
      // Update in PostgreSQL
      await this.updateInPostgreSQL(existingContext.id, processedData);
      
      // Store version history
      await this.storeVersion(existingContext.id, existingContext.version, existingContext.data, {
        changeType: options.changeType || 'update',
        changedBy: options.changedBy || options.agentId
      });
      
      // Update Redis cache
      await this.cacheInRedis(key, processedData, contextData.ttl);
      
      // Update search index
      await this.updateSearchIndex(existingContext.id, data);
      
      this.stats.writes++;
      this.emit('contextUpdated', { key, version: newVersion, options });
      
      return {
        contextId: existingContext.id,
        key,
        version: newVersion,
        updated: true
      };
      
    } catch (error) {
      console.error('Error updating context:', error);
      throw error;
    }
  }

  /**
   * Delete context
   */
  async deleteContext(key, options = {}) {
    if (!this.isInitialized) {
      throw new Error('Context Manager not initialized');
    }

    try {
      // Remove from PostgreSQL
      const deleted = await this.deleteFromPostgreSQL(key);
      
      // Remove from Redis
      await this.deleteFromRedis(key);
      
      this.emit('contextDeleted', { key, deleted, options });
      
      return { deleted };
      
    } catch (error) {
      console.error('Error deleting context:', error);
      throw error;
    }
  }

  /**
   * Search contexts
   */
  async searchContexts(query, options = {}) {
    if (!this.isInitialized) {
      throw new Error('Context Manager not initialized');
    }

    try {
      const client = await this.pgPool.connect();
      
      const searchQuery = `
        SELECT 
          cs.id,
          cs.context_key,
          cs.session_id,
          cs.agent_id,
          cs.version,
          cs.metadata,
          cs.tags,
          cs.created_at,
          cs.updated_at,
          cs.access_count,
          ts_rank(css.search_vector, plainto_tsquery($1)) as rank
        FROM context_storage cs
        JOIN context_search css ON cs.id = css.context_id
        WHERE css.search_vector @@ plainto_tsquery($1)
        ${options.sessionId ? 'AND cs.session_id = $2' : ''}
        ${options.agentId ? `AND cs.agent_id = $${options.sessionId ? 3 : 2}` : ''}
        ORDER BY rank DESC, cs.updated_at DESC
        LIMIT $${options.sessionId && options.agentId ? 4 : options.sessionId || options.agentId ? 3 : 2}
        OFFSET $${options.sessionId && options.agentId ? 5 : options.sessionId || options.agentId ? 4 : 3}
      `;

      const params = [query];
      if (options.sessionId) params.push(options.sessionId);
      if (options.agentId) params.push(options.agentId);
      params.push(options.limit || 20);
      params.push(options.offset || 0);

      const result = await client.query(searchQuery, params);
      client.release();

      this.emit('contextSearched', { query, resultCount: result.rows.length, options });
      
      return {
        results: result.rows,
        total: result.rows.length,
        query,
        options
      };
      
    } catch (error) {
      console.error('Error searching contexts:', error);
      throw error;
    }
  }

  /**
   * Get context analytics
   */
  async getAnalytics(options = {}) {
    if (!this.isInitialized) {
      throw new Error('Context Manager not initialized');
    }

    try {
      const client = await this.pgPool.connect();
      
      const analyticsQuery = `
        SELECT 
          COUNT(*) as total_contexts,
          COUNT(DISTINCT session_id) as unique_sessions,
          COUNT(DISTINCT agent_id) as unique_agents,
          AVG(access_count) as avg_access_count,
          SUM(access_count) as total_accesses,
          MAX(created_at) as latest_context,
          MIN(created_at) as earliest_context
        FROM context_storage
        WHERE expires_at > NOW() OR expires_at IS NULL
        ${options.sessionId ? 'AND session_id = $1' : ''}
        ${options.agentId ? `AND agent_id = $${options.sessionId ? 2 : 1}` : ''}
      `;

      const params = [];
      if (options.sessionId) params.push(options.sessionId);
      if (options.agentId) params.push(options.agentId);

      const result = await client.query(analyticsQuery, params);
      client.release();

      return {
        ...result.rows[0],
        system_stats: this.stats,
        cache_hit_ratio: this.stats.reads > 0 ? (this.stats.cacheHits / this.stats.reads).toFixed(2) : 0
      };
      
    } catch (error) {
      console.error('Error getting analytics:', error);
      throw error;
    }
  }

  /**
   * Process context data (compression/encryption)
   */
  async processContextData(contextData) {
    let processedData = { ...contextData };
    
    // Compress if needed
    if (contextData.compress) {
      processedData.data = await this.compressData(contextData.data);
      processedData.is_compressed = true;
      this.stats.compressions++;
    }
    
    // Encrypt if needed
    if (contextData.encrypt && this.config.encryption.secretKey) {
      processedData.data = await this.encryptData(processedData.data);
      processedData.is_encrypted = true;
      this.stats.encryptions++;
    }
    
    return processedData;
  }

  /**
   * Unprocess context data (decompression/decryption)
   */
  async unprocessContextData(contextData) {
    let processedData = { ...contextData };
    
    // Decrypt if needed
    if (contextData.is_encrypted && this.config.encryption.secretKey) {
      processedData.data = await this.decryptData(contextData.data);
    }
    
    // Decompress if needed
    if (contextData.is_compressed) {
      processedData.data = await this.decompressData(processedData.data);
    }
    
    return processedData;
  }

  /**
   * Compress data
   */
  async compressData(data) {
    const zlib = require('zlib');
    const jsonString = JSON.stringify(data);
    return new Promise((resolve, reject) => {
      zlib.gzip(jsonString, (err, compressed) => {
        if (err) reject(err);
        else resolve(compressed.toString('base64'));
      });
    });
  }

  /**
   * Decompress data
   */
  async decompressData(compressedData) {
    const zlib = require('zlib');
    const buffer = Buffer.from(compressedData, 'base64');
    return new Promise((resolve, reject) => {
      zlib.gunzip(buffer, (err, decompressed) => {
        if (err) reject(err);
        else resolve(JSON.parse(decompressed.toString()));
      });
    });
  }

  /**
   * Encrypt data
   */
  async encryptData(data) {
    const jsonString = JSON.stringify(data);
    const iv = crypto.randomBytes(this.config.encryption.ivLength);
    const cipher = crypto.createCipher(this.config.encryption.algorithm, this.config.encryption.secretKey);
    cipher.setAutoPadding(true);
    
    let encrypted = cipher.update(jsonString, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const tag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      tag: tag.toString('hex')
    };
  }

  /**
   * Decrypt data
   */
  async decryptData(encryptedData) {
    const decipher = crypto.createDecipher(this.config.encryption.algorithm, this.config.encryption.secretKey);
    decipher.setAuthTag(Buffer.from(encryptedData.tag, 'hex'));
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return JSON.parse(decrypted);
  }

  /**
   * Store context in PostgreSQL
   */
  async storeInPostgreSQL(contextData) {
    const client = await this.pgPool.connect();
    
    try {
      const query = `
        INSERT INTO context_storage (
          context_key, session_id, agent_id, version, context_data, 
          metadata, tags, is_encrypted, is_compressed, expires_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id
      `;
      
      const expiresAt = contextData.ttl ? 
        new Date(Date.now() + contextData.ttl * 1000) : null;
      
      const values = [
        contextData.key,
        contextData.sessionId,
        contextData.agentId,
        contextData.version || 1,
        JSON.stringify(contextData.data),
        JSON.stringify(contextData.metadata),
        contextData.tags,
        contextData.is_encrypted || false,
        contextData.is_compressed || false,
        expiresAt
      ];
      
      const result = await client.query(query, values);
      return result.rows[0].id;
      
    } finally {
      client.release();
    }
  }

  /**
   * Get context from PostgreSQL
   */
  async getFromPostgreSQL(key, options = {}) {
    const client = await this.pgPool.connect();
    
    try {
      const query = `
        SELECT * FROM context_storage 
        WHERE context_key = $1 
        AND (expires_at IS NULL OR expires_at > NOW())
        ${options.version ? 'AND version = $2' : ''}
        ORDER BY version DESC 
        LIMIT 1
      `;
      
      const values = options.version ? [key, options.version] : [key];
      const result = await client.query(query, values);
      
      if (result.rows.length === 0) {
        return null;
      }
      
      const row = result.rows[0];
      return {
        id: row.id,
        key: row.context_key,
        sessionId: row.session_id,
        agentId: row.agent_id,
        version: row.version,
        data: JSON.parse(row.context_data),
        metadata: row.metadata,
        tags: row.tags,
        is_encrypted: row.is_encrypted,
        is_compressed: row.is_compressed,
        created_at: row.created_at,
        updated_at: row.updated_at,
        access_count: row.access_count
      };
      
    } finally {
      client.release();
    }
  }

  /**
   * Update context in PostgreSQL
   */
  async updateInPostgreSQL(contextId, contextData) {
    const client = await this.pgPool.connect();
    
    try {
      const query = `
        UPDATE context_storage 
        SET context_data = $2, version = $3, metadata = $4, tags = $5,
            is_encrypted = $6, is_compressed = $7, updated_at = NOW()
        WHERE id = $1
      `;
      
      const values = [
        contextId,
        JSON.stringify(contextData.data),
        contextData.version,
        JSON.stringify(contextData.metadata),
        contextData.tags,
        contextData.is_encrypted || false,
        contextData.is_compressed || false
      ];
      
      await client.query(query, values);
      
    } finally {
      client.release();
    }
  }

  /**
   * Delete context from PostgreSQL
   */
  async deleteFromPostgreSQL(key) {
    const client = await this.pgPool.connect();
    
    try {
      const query = 'DELETE FROM context_storage WHERE context_key = $1';
      const result = await client.query(query, [key]);
      return result.rowCount > 0;
      
    } finally {
      client.release();
    }
  }

  /**
   * Cache context in Redis
   */
  async cacheInRedis(key, contextData, ttl) {
    const redisKey = this.config.redis.keyPrefix + key;
    const cacheData = JSON.stringify(contextData);
    
    if (ttl) {
      await this.redisClient.setEx(redisKey, ttl, cacheData);
    } else {
      await this.redisClient.set(redisKey, cacheData);
    }
  }

  /**
   * Get context from Redis
   */
  async getFromRedis(key) {
    const redisKey = this.config.redis.keyPrefix + key;
    const cached = await this.redisClient.get(redisKey);
    
    if (cached) {
      try {
        return JSON.parse(cached);
      } catch (error) {
        console.error('Error parsing cached context:', error);
        return null;
      }
    }
    
    return null;
  }

  /**
   * Delete context from Redis
   */
  async deleteFromRedis(key) {
    const redisKey = this.config.redis.keyPrefix + key;
    return await this.redisClient.del(redisKey);
  }

  /**
   * Update search index
   */
  async updateSearchIndex(contextId, data) {
    const client = await this.pgPool.connect();
    
    try {
      const searchContent = this.extractSearchableContent(data);
      const contentHash = crypto.createHash('sha256').update(searchContent).digest('hex');
      
      const query = `
        INSERT INTO context_search (context_id, search_vector, content_hash)
        VALUES ($1, to_tsvector('english', $2), $3)
        ON CONFLICT (context_id) 
        DO UPDATE SET 
          search_vector = to_tsvector('english', $2),
          content_hash = $3,
          created_at = NOW()
      `;
      
      await client.query(query, [contextId, searchContent, contentHash]);
      
    } finally {
      client.release();
    }
  }

  /**
   * Extract searchable content from context data
   */
  extractSearchableContent(data) {
    if (typeof data === 'string') {
      return data;
    }
    
    if (typeof data === 'object') {
      return JSON.stringify(data).replace(/[{}",\[\]]/g, ' ');
    }
    
    return String(data);
  }

  /**
   * Store version history
   */
  async storeVersion(contextId, version, data, options = {}) {
    const client = await this.pgPool.connect();
    
    try {
      const query = `
        INSERT INTO context_versions (context_id, version, context_data, metadata, change_type, changed_by)
        VALUES ($1, $2, $3, $4, $5, $6)
      `;
      
      const values = [
        contextId,
        version,
        JSON.stringify(data),
        JSON.stringify(options.metadata || {}),
        options.changeType || 'update',
        options.changedBy
      ];
      
      await client.query(query, values);
      
      // Cleanup old versions if needed
      if (this.config.versioning.autoCleanup) {
        await this.cleanupOldVersions(contextId);
      }
      
    } finally {
      client.release();
    }
  }

  /**
   * Cleanup old versions
   */
  async cleanupOldVersions(contextId) {
    const client = await this.pgPool.connect();
    
    try {
      const query = `
        DELETE FROM context_versions 
        WHERE context_id = $1 
        AND version NOT IN (
          SELECT version FROM context_versions 
          WHERE context_id = $1 
          ORDER BY version DESC 
          LIMIT $2
        )
      `;
      
      await client.query(query, [contextId, this.config.versioning.maxVersions]);
      
    } finally {
      client.release();
    }
  }

  /**
   * Update access statistics
   */
  async updateAccessStats(contextId) {
    const client = await this.pgPool.connect();
    
    try {
      const query = `
        UPDATE context_storage 
        SET access_count = access_count + 1, last_accessed_at = NOW()
        WHERE id = $1 OR context_key = $1
      `;
      
      await client.query(query, [contextId]);
      
    } finally {
      client.release();
    }
  }

  /**
   * Start cleanup scheduler
   */
  async startCleanupScheduler() {
    setInterval(async () => {
      try {
        await this.cleanupExpiredContexts();
      } catch (error) {
        console.error('Cleanup scheduler error:', error);
      }
    }, this.config.expiration.cleanupInterval * 1000);
  }

  /**
   * Cleanup expired contexts
   */
  async cleanupExpiredContexts() {
    const client = await this.pgPool.connect();
    
    try {
      const query = 'DELETE FROM context_storage WHERE expires_at < NOW()';
      const result = await client.query(query);
      
      if (result.rowCount > 0) {
        console.log(`Cleaned up ${result.rowCount} expired contexts`);
        this.emit('contextsExpired', { count: result.rowCount });
      }
      
    } finally {
      client.release();
    }
  }

  /**
   * Shutdown the context manager
   */
  async shutdown() {
    try {
      if (this.redisClient) {
        await this.redisClient.quit();
      }
      
      if (this.pgPool) {
        await this.pgPool.end();
      }
      
      this.emit('shutdown');
      console.log('Context Manager shutdown completed');
      
    } catch (error) {
      console.error('Error during shutdown:', error);
      throw error;
    }
  }
}

module.exports = ContextManager;