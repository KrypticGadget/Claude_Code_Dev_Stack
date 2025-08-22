/**
 * QR Code Generation Service for Claude Code Mobile Access
 * Handles secure QR code generation for tunnels, sessions, and mobile access
 */

const QRCode = require('qrcode');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

class QRCodeService {
  constructor() {
    this.activeTokens = new Map();
    this.tunnelConfigs = new Map();
    this.secretKey = process.env.JWT_SECRET || crypto.randomBytes(64).toString('hex');
    this.defaultExpiration = 30 * 60 * 1000; // 30 minutes
  }

  /**
   * Generate QR code for NGROK tunnel URL
   */
  async generateTunnelQRCode(tunnelUrl, options = {}) {
    const {
      serviceName = 'Claude Code',
      description = 'Connect to Claude Code Dev Stack',
      expiration = this.defaultExpiration,
      customization = {}
    } = options;

    const sessionId = uuidv4();
    const expiresAt = Date.now() + expiration;

    // Create secure access token
    const token = jwt.sign(
      {
        tunnelUrl,
        serviceName,
        sessionId,
        type: 'tunnel_access',
        exp: Math.floor(expiresAt / 1000)
      },
      this.secretKey
    );

    // Store token for validation
    this.activeTokens.set(sessionId, {
      token,
      tunnelUrl,
      serviceName,
      expiresAt,
      createdAt: Date.now(),
      type: 'tunnel'
    });

    const qrData = {
      url: tunnelUrl,
      token,
      sessionId,
      serviceName,
      description,
      expiresAt,
      type: 'tunnel_access',
      deepLink: `claudecode://connect?token=${token}`
    };

    const qrCodeDataURL = await this.generateQRCodeImage(
      JSON.stringify(qrData),
      customization
    );

    return {
      qrCode: qrCodeDataURL,
      sessionId,
      token,
      expiresAt,
      tunnelUrl,
      deepLink: qrData.deepLink
    };
  }

  /**
   * Generate QR code with connection instructions
   */
  async generateConnectionInstructionsQR(connectionInfo, options = {}) {
    const {
      title = 'Claude Code Connection',
      instructions = [],
      expiration = this.defaultExpiration,
      customization = {}
    } = options;

    const sessionId = uuidv4();
    const expiresAt = Date.now() + expiration;

    const qrData = {
      type: 'connection_instructions',
      sessionId,
      title,
      connectionInfo,
      instructions,
      expiresAt,
      deepLink: `claudecode://instructions?session=${sessionId}`
    };

    const qrCodeDataURL = await this.generateQRCodeImage(
      JSON.stringify(qrData),
      customization
    );

    return {
      qrCode: qrCodeDataURL,
      sessionId,
      expiresAt,
      connectionInfo,
      instructions
    };
  }

  /**
   * Generate mobile-optimized access codes with deep-linking
   */
  async generateMobileAccessQR(appUrl, options = {}) {
    const {
      appName = 'Claude Code Mobile',
      features = [],
      platformUrls = {},
      expiration = this.defaultExpiration,
      customization = {}
    } = options;

    const sessionId = uuidv4();
    const expiresAt = Date.now() + expiration;

    const token = jwt.sign(
      {
        appUrl,
        appName,
        features,
        sessionId,
        type: 'mobile_access',
        exp: Math.floor(expiresAt / 1000)
      },
      this.secretKey
    );

    const qrData = {
      type: 'mobile_access',
      sessionId,
      token,
      appUrl,
      appName,
      features,
      platformUrls: {
        ios: platformUrls.ios || `https://apps.apple.com/app/claude-code`,
        android: platformUrls.android || `https://play.google.com/store/apps/details?id=com.claudecode`,
        web: appUrl,
        ...platformUrls
      },
      expiresAt,
      deepLinks: {
        ios: `claudecode://mobile?token=${token}`,
        android: `intent://mobile?token=${token}#Intent;scheme=claudecode;package=com.claudecode;end`,
        universal: `https://claudecode.app/mobile?token=${token}`
      }
    };

    const qrCodeDataURL = await this.generateQRCodeImage(
      JSON.stringify(qrData),
      customization
    );

    this.activeTokens.set(sessionId, {
      token,
      appUrl,
      appName,
      expiresAt,
      createdAt: Date.now(),
      type: 'mobile_access'
    });

    return {
      qrCode: qrCodeDataURL,
      sessionId,
      token,
      expiresAt,
      appUrl,
      deepLinks: qrData.deepLinks
    };
  }

  /**
   * Generate session-specific QR codes
   */
  async generateSessionQR(sessionData, options = {}) {
    const {
      sessionType = 'claude_session',
      permissions = [],
      expiration = this.defaultExpiration,
      customization = {}
    } = options;

    const sessionId = uuidv4();
    const expiresAt = Date.now() + expiration;

    const token = jwt.sign(
      {
        sessionData,
        sessionType,
        permissions,
        sessionId,
        type: 'session_access',
        exp: Math.floor(expiresAt / 1000)
      },
      this.secretKey
    );

    const qrData = {
      type: 'session_access',
      sessionId,
      token,
      sessionData,
      sessionType,
      permissions,
      expiresAt,
      deepLink: `claudecode://session?token=${token}`
    };

    const qrCodeDataURL = await this.generateQRCodeImage(
      JSON.stringify(qrData),
      customization
    );

    this.activeTokens.set(sessionId, {
      token,
      sessionData,
      sessionType,
      permissions,
      expiresAt,
      createdAt: Date.now(),
      type: 'session'
    });

    return {
      qrCode: qrCodeDataURL,
      sessionId,
      token,
      expiresAt,
      sessionData,
      deepLink: qrData.deepLink
    };
  }

  /**
   * Generate time-limited access QR codes
   */
  async generateTimeLimitedQR(resourceUrl, timeLimit, options = {}) {
    const {
      resourceType = 'service',
      accessLevel = 'read',
      customization = {}
    } = options;

    const sessionId = uuidv4();
    const expiresAt = Date.now() + timeLimit;

    const token = jwt.sign(
      {
        resourceUrl,
        resourceType,
        accessLevel,
        sessionId,
        type: 'time_limited_access',
        exp: Math.floor(expiresAt / 1000)
      },
      this.secretKey
    );

    const qrData = {
      type: 'time_limited_access',
      sessionId,
      token,
      resourceUrl,
      resourceType,
      accessLevel,
      expiresAt,
      timeLimit,
      deepLink: `claudecode://access?token=${token}`
    };

    const qrCodeDataURL = await this.generateQRCodeImage(
      JSON.stringify(qrData),
      customization
    );

    this.activeTokens.set(sessionId, {
      token,
      resourceUrl,
      resourceType,
      accessLevel,
      expiresAt,
      createdAt: Date.now(),
      type: 'time_limited'
    });

    return {
      qrCode: qrCodeDataURL,
      sessionId,
      token,
      expiresAt,
      timeLimit,
      resourceUrl,
      deepLink: qrData.deepLink
    };
  }

  /**
   * Generate secure access tokens with encryption
   */
  generateSecureAccessToken(payload, options = {}) {
    const {
      expiration = this.defaultExpiration,
      encryption = true
    } = options;

    const sessionId = uuidv4();
    const expiresAt = Date.now() + expiration;

    let tokenPayload = {
      ...payload,
      sessionId,
      type: 'secure_access',
      exp: Math.floor(expiresAt / 1000)
    };

    if (encryption) {
      const cipher = crypto.createCipher('aes-256-cbc', this.secretKey);
      let encrypted = cipher.update(JSON.stringify(payload), 'utf8', 'hex');
      encrypted += cipher.final('hex');
      tokenPayload.encrypted = encrypted;
    }

    const token = jwt.sign(tokenPayload, this.secretKey);

    this.activeTokens.set(sessionId, {
      token,
      payload,
      encrypted: encryption,
      expiresAt,
      createdAt: Date.now(),
      type: 'secure_access'
    });

    return {
      token,
      sessionId,
      expiresAt,
      encrypted: encryption
    };
  }

  /**
   * Generate multi-service QR code for accessing multiple services
   */
  async generateMultiServiceQR(services, options = {}) {
    const {
      title = 'Claude Code Services',
      expiration = this.defaultExpiration,
      customization = {}
    } = options;

    const sessionId = uuidv4();
    const expiresAt = Date.now() + expiration;

    const serviceTokens = {};
    for (const service of services) {
      const serviceToken = jwt.sign(
        {
          serviceName: service.name,
          serviceUrl: service.url,
          permissions: service.permissions || [],
          sessionId,
          type: 'service_access',
          exp: Math.floor(expiresAt / 1000)
        },
        this.secretKey
      );
      serviceTokens[service.name] = serviceToken;
    }

    const masterToken = jwt.sign(
      {
        services: services.map(s => ({ name: s.name, url: s.url })),
        serviceTokens,
        sessionId,
        type: 'multi_service_access',
        exp: Math.floor(expiresAt / 1000)
      },
      this.secretKey
    );

    const qrData = {
      type: 'multi_service_access',
      sessionId,
      masterToken,
      title,
      services: services.map(s => ({
        name: s.name,
        url: s.url,
        description: s.description,
        icon: s.icon
      })),
      serviceTokens,
      expiresAt,
      deepLink: `claudecode://multiservice?token=${masterToken}`
    };

    const qrCodeDataURL = await this.generateQRCodeImage(
      JSON.stringify(qrData),
      customization
    );

    this.activeTokens.set(sessionId, {
      masterToken,
      serviceTokens,
      services,
      expiresAt,
      createdAt: Date.now(),
      type: 'multi_service'
    });

    return {
      qrCode: qrCodeDataURL,
      sessionId,
      masterToken,
      serviceTokens,
      expiresAt,
      services,
      deepLink: qrData.deepLink
    };
  }

  /**
   * Generate QR code image with customization options
   */
  async generateQRCodeImage(data, customization = {}) {
    const {
      size = 512,
      margin = 4,
      color = {
        dark: '#000000',
        light: '#FFFFFF'
      },
      errorCorrectionLevel = 'M',
      logo = null
    } = customization;

    const options = {
      width: size,
      height: size,
      margin,
      color,
      errorCorrectionLevel
    };

    try {
      const qrCodeDataURL = await QRCode.toDataURL(data, options);
      
      // If logo is provided, we would need to composite it
      // For now, return the basic QR code
      return qrCodeDataURL;
    } catch (error) {
      throw new Error(`QR Code generation failed: ${error.message}`);
    }
  }

  /**
   * Batch generate QR codes for multiple services
   */
  async batchGenerateQRCodes(requests, options = {}) {
    const {
      concurrent = 5,
      customization = {}
    } = options;

    const results = [];
    const batches = [];
    
    // Split requests into batches
    for (let i = 0; i < requests.length; i += concurrent) {
      batches.push(requests.slice(i, i + concurrent));
    }

    for (const batch of batches) {
      const batchPromises = batch.map(async (request) => {
        try {
          switch (request.type) {
            case 'tunnel':
              return await this.generateTunnelQRCode(
                request.tunnelUrl,
                { ...request.options, customization }
              );
            case 'mobile_access':
              return await this.generateMobileAccessQR(
                request.appUrl,
                { ...request.options, customization }
              );
            case 'session':
              return await this.generateSessionQR(
                request.sessionData,
                { ...request.options, customization }
              );
            case 'time_limited':
              return await this.generateTimeLimitedQR(
                request.resourceUrl,
                request.timeLimit,
                { ...request.options, customization }
              );
            case 'multi_service':
              return await this.generateMultiServiceQR(
                request.services,
                { ...request.options, customization }
              );
            default:
              throw new Error(`Unknown QR code type: ${request.type}`);
          }
        } catch (error) {
          return {
            error: error.message,
            request
          };
        }
      });

      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults);
    }

    return results;
  }

  /**
   * Validate QR code token
   */
  validateToken(token) {
    try {
      const decoded = jwt.verify(token, this.secretKey);
      const tokenData = this.activeTokens.get(decoded.sessionId);

      if (!tokenData) {
        return { valid: false, error: 'Token not found' };
      }

      if (Date.now() > tokenData.expiresAt) {
        this.activeTokens.delete(decoded.sessionId);
        return { valid: false, error: 'Token expired' };
      }

      return {
        valid: true,
        data: decoded,
        tokenData
      };
    } catch (error) {
      return { valid: false, error: error.message };
    }
  }

  /**
   * Revoke token
   */
  revokeToken(sessionId) {
    const deleted = this.activeTokens.delete(sessionId);
    return { revoked: deleted };
  }

  /**
   * Get active tokens
   */
  getActiveTokens() {
    const now = Date.now();
    const active = [];

    for (const [sessionId, tokenData] of this.activeTokens.entries()) {
      if (now > tokenData.expiresAt) {
        this.activeTokens.delete(sessionId);
      } else {
        active.push({
          sessionId,
          type: tokenData.type,
          expiresAt: tokenData.expiresAt,
          createdAt: tokenData.createdAt
        });
      }
    }

    return active;
  }

  /**
   * Cleanup expired tokens
   */
  cleanupExpiredTokens() {
    const now = Date.now();
    let cleaned = 0;

    for (const [sessionId, tokenData] of this.activeTokens.entries()) {
      if (now > tokenData.expiresAt) {
        this.activeTokens.delete(sessionId);
        cleaned++;
      }
    }

    return { cleaned };
  }

  /**
   * Get QR code statistics
   */
  getStatistics() {
    const now = Date.now();
    const stats = {
      totalActive: 0,
      byType: {},
      expiringSoon: 0, // expiring in next 5 minutes
      totalGenerated: this.activeTokens.size
    };

    for (const [sessionId, tokenData] of this.activeTokens.entries()) {
      if (now <= tokenData.expiresAt) {
        stats.totalActive++;
        stats.byType[tokenData.type] = (stats.byType[tokenData.type] || 0) + 1;
        
        if (tokenData.expiresAt - now < 5 * 60 * 1000) {
          stats.expiringSoon++;
        }
      }
    }

    return stats;
  }
}

module.exports = QRCodeService;