#!/usr/bin/env node
/**
 * Webhook Testing Server for Claude Code Dev Stack
 * Provides endpoints for webhook development and testing with NGROK integration
 */

const express = require('express');
const { createServer } = require('http');
const cors = require('cors');
const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

class WebhookServer {
  constructor(options = {}) {
    this.config = {
      port: options.port || process.env.CLAUDE_WEBHOOK_PORT || 4000,
      logPath: options.logPath || path.join(__dirname, '../logs/webhooks.log'),
      secretsPath: options.secretsPath || path.join(__dirname, '../config/webhook-secrets.json'),
      maxLogSize: options.maxLogSize || 10 * 1024 * 1024, // 10MB
      enableSecurity: options.enableSecurity !== false,
      rateLimitWindow: options.rateLimitWindow || 60000, // 1 minute
      rateLimitMax: options.rateLimitMax || 100
    };
    
    this.app = express();
    this.server = createServer(this.app);
    this.webhookLogs = [];
    this.secrets = new Map();
    this.rateLimitStore = new Map();
    
    this.setupMiddleware();
    this.setupRoutes();
  }

  /**
   * Setup Express middleware
   */
  setupMiddleware() {
    // CORS
    this.app.use(cors({
      origin: true,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'X-Hub-Signature', 'X-Hub-Signature-256']
    }));

    // Raw body parsing for webhook signature verification
    this.app.use('/webhook', express.raw({ type: '*/*', limit: '10mb' }));
    
    // JSON parsing for other routes
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Request logging
    this.app.use((req, res, next) => {
      const startTime = Date.now();
      
      res.on('finish', () => {
        const duration = Date.now() - startTime;
        const logEntry = {
          timestamp: new Date().toISOString(),
          method: req.method,
          path: req.path,
          statusCode: res.statusCode,
          duration: `${duration}ms`,
          ip: req.ip || req.connection.remoteAddress,
          userAgent: req.get('User-Agent') || 'unknown',
          contentLength: req.get('Content-Length') || 0
        };
        
        this.logRequest(logEntry);
      });
      
      next();
    });

    // Rate limiting
    if (this.config.enableSecurity) {
      this.app.use(this.rateLimitMiddleware.bind(this));
    }
  }

  /**
   * Rate limiting middleware
   */
  rateLimitMiddleware(req, res, next) {
    const clientIP = req.ip || req.connection.remoteAddress;
    const now = Date.now();
    const windowStart = now - this.config.rateLimitWindow;
    
    // Clean old entries
    for (const [ip, requests] of this.rateLimitStore.entries()) {
      this.rateLimitStore.set(ip, requests.filter(time => time > windowStart));
      if (this.rateLimitStore.get(ip).length === 0) {
        this.rateLimitStore.delete(ip);
      }
    }
    
    // Check current IP
    const clientRequests = this.rateLimitStore.get(clientIP) || [];
    
    if (clientRequests.length >= this.config.rateLimitMax) {
      return res.status(429).json({
        error: 'Rate limit exceeded',
        limit: this.config.rateLimitMax,
        window: this.config.rateLimitWindow,
        retryAfter: Math.ceil((clientRequests[0] + this.config.rateLimitWindow - now) / 1000)
      });
    }
    
    // Add current request
    clientRequests.push(now);
    this.rateLimitStore.set(clientIP, clientRequests);
    
    // Add rate limit headers
    res.set({
      'X-RateLimit-Limit': this.config.rateLimitMax,
      'X-RateLimit-Remaining': this.config.rateLimitMax - clientRequests.length,
      'X-RateLimit-Reset': Math.ceil((windowStart + this.config.rateLimitWindow) / 1000)
    });
    
    next();
  }

  /**
   * Setup routes
   */
  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        webhooks: {
          received: this.webhookLogs.length,
          lastReceived: this.webhookLogs.length > 0 ? this.webhookLogs[this.webhookLogs.length - 1].timestamp : null
        }
      });
    });

    // Webhook endpoint - accepts any method
    ['get', 'post', 'put', 'patch', 'delete'].forEach(method => {
      this.app[method]('/webhook/:service?', this.handleWebhook.bind(this));
    });

    // GitHub webhook
    this.app.post('/webhook/github', this.handleGitHubWebhook.bind(this));

    // Discord webhook
    this.app.post('/webhook/discord', this.handleDiscordWebhook.bind(this));

    // Slack webhook
    this.app.post('/webhook/slack', this.handleSlackWebhook.bind(this));

    // Generic webhook with custom validation
    this.app.post('/webhook/custom/:id', this.handleCustomWebhook.bind(this));

    // Webhook logs
    this.app.get('/logs', (req, res) => {
      const { limit = 100, service, method } = req.query;
      
      let logs = [...this.webhookLogs];
      
      if (service) {
        logs = logs.filter(log => log.service === service);
      }
      
      if (method) {
        logs = logs.filter(log => log.method.toLowerCase() === method.toLowerCase());
      }
      
      logs = logs.slice(-parseInt(limit));
      
      res.json({
        logs,
        total: logs.length,
        filters: { service, method, limit }
      });
    });

    // Clear logs
    this.app.delete('/logs', (req, res) => {
      const previousCount = this.webhookLogs.length;
      this.webhookLogs = [];
      
      res.json({
        message: 'Logs cleared',
        previousCount,
        timestamp: new Date().toISOString()
      });
    });

    // Webhook replay
    this.app.post('/replay/:id', this.replayWebhook.bind(this));

    // Webhook secrets management
    this.app.get('/secrets', (req, res) => {
      const secretsList = Array.from(this.secrets.keys());
      res.json({ secrets: secretsList });
    });

    this.app.post('/secrets', async (req, res) => {
      const { service, secret } = req.body;
      
      if (!service || !secret) {
        return res.status(400).json({ error: 'Service and secret are required' });
      }
      
      this.secrets.set(service, secret);
      await this.saveSecrets();
      
      res.json({ message: 'Secret saved', service });
    });

    // Testing utilities
    this.app.get('/test/generate', (req, res) => {
      const { service = 'test', method = 'POST' } = req.query;
      
      const testPayload = {
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        event: 'test_event',
        data: {
          test: true,
          message: 'This is a test webhook',
          service: service,
          method: method
        }
      };
      
      res.json({
        message: 'Test webhook payload generated',
        payload: testPayload,
        endpoint: `/webhook/${service}`,
        method: method.toUpperCase()
      });
    });

    // Statistics
    this.app.get('/stats', (req, res) => {
      const stats = this.generateStats();
      res.json(stats);
    });

    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        error: 'Endpoint not found',
        path: req.path,
        method: req.method,
        availableEndpoints: [
          'GET /health',
          'POST /webhook/:service',
          'POST /webhook/github',
          'POST /webhook/discord',
          'POST /webhook/slack',
          'GET /logs',
          'DELETE /logs',
          'GET /stats'
        ]
      });
    });
  }

  /**
   * Handle generic webhook
   */
  async handleWebhook(req, res) {
    const service = req.params.service || 'generic';
    const webhookId = crypto.randomUUID();
    
    try {
      const webhookData = {
        id: webhookId,
        timestamp: new Date().toISOString(),
        service: service,
        method: req.method,
        path: req.path,
        headers: req.headers,
        query: req.query,
        body: this.parseBody(req),
        ip: req.ip || req.connection.remoteAddress,
        verified: false
      };

      // Verify signature if secret exists
      if (this.secrets.has(service)) {
        webhookData.verified = this.verifySignature(req, this.secrets.get(service));
      }

      // Store webhook
      this.webhookLogs.push(webhookData);
      await this.saveWebhookLog(webhookData);

      // Respond
      res.status(200).json({
        message: 'Webhook received',
        id: webhookId,
        service: service,
        timestamp: webhookData.timestamp,
        verified: webhookData.verified
      });

      console.log(`📨 Webhook received: ${service} (${req.method}) - ID: ${webhookId}`);

    } catch (error) {
      console.error('Webhook handling error:', error);
      
      res.status(500).json({
        error: 'Webhook processing failed',
        message: error.message,
        id: webhookId
      });
    }
  }

  /**
   * Handle GitHub webhook
   */
  async handleGitHubWebhook(req, res) {
    const event = req.get('X-GitHub-Event');
    const signature = req.get('X-Hub-Signature-256');
    const webhookId = crypto.randomUUID();
    
    try {
      const webhookData = {
        id: webhookId,
        timestamp: new Date().toISOString(),
        service: 'github',
        event: event,
        signature: signature,
        method: req.method,
        headers: req.headers,
        body: this.parseBody(req),
        verified: false
      };

      // Verify GitHub signature
      if (this.secrets.has('github')) {
        webhookData.verified = this.verifyGitHubSignature(req, this.secrets.get('github'));
      }

      this.webhookLogs.push(webhookData);
      await this.saveWebhookLog(webhookData);

      res.status(200).json({
        message: 'GitHub webhook received',
        id: webhookId,
        event: event,
        verified: webhookData.verified
      });

      console.log(`🐙 GitHub webhook: ${event} - ID: ${webhookId}`);

    } catch (error) {
      console.error('GitHub webhook error:', error);
      res.status(500).json({ error: 'GitHub webhook processing failed' });
    }
  }

  /**
   * Handle Discord webhook
   */
  async handleDiscordWebhook(req, res) {
    const webhookId = crypto.randomUUID();
    
    try {
      const webhookData = {
        id: webhookId,
        timestamp: new Date().toISOString(),
        service: 'discord',
        method: req.method,
        headers: req.headers,
        body: this.parseBody(req),
        verified: true // Discord webhooks are verified via URL
      };

      this.webhookLogs.push(webhookData);
      await this.saveWebhookLog(webhookData);

      res.status(200).json({
        message: 'Discord webhook received',
        id: webhookId
      });

      console.log(`💬 Discord webhook received - ID: ${webhookId}`);

    } catch (error) {
      console.error('Discord webhook error:', error);
      res.status(500).json({ error: 'Discord webhook processing failed' });
    }
  }

  /**
   * Handle Slack webhook
   */
  async handleSlackWebhook(req, res) {
    const webhookId = crypto.randomUUID();
    
    try {
      const body = this.parseBody(req);
      
      // Handle Slack URL verification
      if (body.type === 'url_verification') {
        return res.status(200).json({ challenge: body.challenge });
      }

      const webhookData = {
        id: webhookId,
        timestamp: new Date().toISOString(),
        service: 'slack',
        method: req.method,
        headers: req.headers,
        body: body,
        verified: true
      };

      this.webhookLogs.push(webhookData);
      await this.saveWebhookLog(webhookData);

      res.status(200).json({
        message: 'Slack webhook received',
        id: webhookId
      });

      console.log(`💼 Slack webhook received - ID: ${webhookId}`);

    } catch (error) {
      console.error('Slack webhook error:', error);
      res.status(500).json({ error: 'Slack webhook processing failed' });
    }
  }

  /**
   * Handle custom webhook with ID
   */
  async handleCustomWebhook(req, res) {
    const customId = req.params.id;
    const webhookId = crypto.randomUUID();
    
    try {
      const webhookData = {
        id: webhookId,
        customId: customId,
        timestamp: new Date().toISOString(),
        service: 'custom',
        method: req.method,
        headers: req.headers,
        body: this.parseBody(req),
        verified: false
      };

      // Verify signature if secret exists for this custom ID
      if (this.secrets.has(`custom-${customId}`)) {
        webhookData.verified = this.verifySignature(req, this.secrets.get(`custom-${customId}`));
      }

      this.webhookLogs.push(webhookData);
      await this.saveWebhookLog(webhookData);

      res.status(200).json({
        message: 'Custom webhook received',
        id: webhookId,
        customId: customId,
        verified: webhookData.verified
      });

      console.log(`🔧 Custom webhook (${customId}) received - ID: ${webhookId}`);

    } catch (error) {
      console.error('Custom webhook error:', error);
      res.status(500).json({ error: 'Custom webhook processing failed' });
    }
  }

  /**
   * Replay a webhook
   */
  async replayWebhook(req, res) {
    const id = req.params.id;
    const webhook = this.webhookLogs.find(w => w.id === id);
    
    if (!webhook) {
      return res.status(404).json({ error: 'Webhook not found' });
    }

    try {
      // Create a new webhook entry for the replay
      const replayData = {
        ...webhook,
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        replayOf: id,
        isReplay: true
      };

      this.webhookLogs.push(replayData);
      await this.saveWebhookLog(replayData);

      res.status(200).json({
        message: 'Webhook replayed',
        originalId: id,
        replayId: replayData.id,
        timestamp: replayData.timestamp
      });

      console.log(`🔄 Webhook replayed: ${id} -> ${replayData.id}`);

    } catch (error) {
      console.error('Webhook replay error:', error);
      res.status(500).json({ error: 'Webhook replay failed' });
    }
  }

  /**
   * Parse request body
   */
  parseBody(req) {
    if (Buffer.isBuffer(req.body)) {
      try {
        return JSON.parse(req.body.toString());
      } catch (error) {
        return req.body.toString();
      }
    }
    return req.body;
  }

  /**
   * Verify webhook signature
   */
  verifySignature(req, secret) {
    const signature = req.get('X-Hub-Signature') || req.get('X-Signature');
    
    if (!signature || !secret) {
      return false;
    }

    const payload = Buffer.isBuffer(req.body) ? req.body : Buffer.from(JSON.stringify(req.body));
    const expectedSignature = 'sha1=' + crypto.createHmac('sha1', secret).update(payload).digest('hex');
    
    return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
  }

  /**
   * Verify GitHub webhook signature
   */
  verifyGitHubSignature(req, secret) {
    const signature = req.get('X-Hub-Signature-256');
    
    if (!signature || !secret) {
      return false;
    }

    const payload = Buffer.isBuffer(req.body) ? req.body : Buffer.from(JSON.stringify(req.body));
    const expectedSignature = 'sha256=' + crypto.createHmac('sha256', secret).update(payload).digest('hex');
    
    return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
  }

  /**
   * Log request
   */
  async logRequest(logEntry) {
    try {
      const logLine = JSON.stringify(logEntry) + '\\n';
      await fs.appendFile(this.config.logPath, logLine);
      
      // Rotate log if too large
      const stats = await fs.stat(this.config.logPath);
      if (stats.size > this.config.maxLogSize) {
        await this.rotateLog();
      }
    } catch (error) {
      console.error('Failed to write log:', error);
    }
  }

  /**
   * Save webhook log
   */
  async saveWebhookLog(webhookData) {
    try {
      const logPath = path.join(path.dirname(this.config.logPath), 'webhook-data.jsonl');
      const logLine = JSON.stringify(webhookData) + '\\n';
      await fs.appendFile(logPath, logLine);
    } catch (error) {
      console.error('Failed to save webhook log:', error);
    }
  }

  /**
   * Rotate log file
   */
  async rotateLog() {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const rotatedPath = this.config.logPath.replace('.log', `-${timestamp}.log`);
      
      await fs.rename(this.config.logPath, rotatedPath);
      console.log(`📁 Log rotated to: ${rotatedPath}`);
    } catch (error) {
      console.error('Failed to rotate log:', error);
    }
  }

  /**
   * Generate statistics
   */
  generateStats() {
    const now = Date.now();
    const hour = 60 * 60 * 1000;
    const day = 24 * hour;
    
    const recentWebhooks = this.webhookLogs.filter(w => (now - new Date(w.timestamp).getTime()) < hour);
    const todayWebhooks = this.webhookLogs.filter(w => (now - new Date(w.timestamp).getTime()) < day);
    
    const serviceStats = {};
    this.webhookLogs.forEach(webhook => {
      if (!serviceStats[webhook.service]) {
        serviceStats[webhook.service] = 0;
      }
      serviceStats[webhook.service]++;
    });

    return {
      total: this.webhookLogs.length,
      recentHour: recentWebhooks.length,
      today: todayWebhooks.length,
      services: serviceStats,
      verified: this.webhookLogs.filter(w => w.verified).length,
      unverified: this.webhookLogs.filter(w => !w.verified).length,
      rateLimitActive: this.rateLimitStore.size,
      uptime: process.uptime()
    };
  }

  /**
   * Save secrets to file
   */
  async saveSecrets() {
    try {
      const secretsObj = Object.fromEntries(this.secrets);
      await fs.writeFile(this.config.secretsPath, JSON.stringify(secretsObj, null, 2));
    } catch (error) {
      console.error('Failed to save secrets:', error);
    }
  }

  /**
   * Load secrets from file
   */
  async loadSecrets() {
    try {
      const secretsData = await fs.readFile(this.config.secretsPath, 'utf8');
      const secretsObj = JSON.parse(secretsData);
      
      for (const [service, secret] of Object.entries(secretsObj)) {
        this.secrets.set(service, secret);
      }
      
      console.log(`🔐 Loaded ${this.secrets.size} webhook secrets`);
    } catch (error) {
      // File doesn't exist, start with empty secrets
      console.log('📝 No existing secrets file, starting fresh');
    }
  }

  /**
   * Start the webhook server
   */
  async start() {
    try {
      // Ensure directories exist
      await fs.mkdir(path.dirname(this.config.logPath), { recursive: true });
      await fs.mkdir(path.dirname(this.config.secretsPath), { recursive: true });
      
      // Load secrets
      await this.loadSecrets();
      
      // Start server
      this.server.listen(this.config.port, () => {
        console.log(`
╔══════════════════════════════════════════════════════╗
║          Claude Code Webhook Server v3.6.9          ║
╠══════════════════════════════════════════════════════╣
║  Server running at: http://localhost:${this.config.port}           ║
║                                                      ║
║  Endpoints:                                          ║
║  • POST /webhook/:service    - Generic webhooks     ║
║  • POST /webhook/github      - GitHub webhooks      ║
║  • POST /webhook/discord     - Discord webhooks     ║
║  • POST /webhook/slack       - Slack webhooks       ║
║  • GET  /logs               - View webhook logs     ║
║  • GET  /stats              - View statistics       ║
║  • GET  /health             - Health check          ║
║                                                      ║
║  Status: Ready to receive webhooks                   ║
╚══════════════════════════════════════════════════════╝
        `);
      });
      
      return this.server;
    } catch (error) {
      console.error('Failed to start webhook server:', error);
      throw error;
    }
  }

  /**
   * Stop the webhook server
   */
  async stop() {
    return new Promise((resolve) => {
      this.server.close(() => {
        console.log('🛑 Webhook server stopped');
        resolve();
      });
    });
  }
}

// CLI interface
if (require.main === module) {
  const server = new WebhookServer();
  
  server.start().catch(console.error);
  
  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\\n🛑 Received SIGINT, shutting down...');
    await server.stop();
    process.exit(0);
  });
  
  process.on('SIGTERM', async () => {
    console.log('\\n🛑 Received SIGTERM, shutting down...');
    await server.stop();
    process.exit(0);
  });
}

module.exports = WebhookServer;