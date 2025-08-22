/**
 * NGROK QR Code Integration Service
 * Automatically generates QR codes for NGROK tunnels and manages mobile access
 */

const QRCodeService = require('./qrCodeService');
const { exec } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

class NGROKQRIntegration {
  constructor() {
    this.qrCodeService = new QRCodeService();
    this.activeTunnels = new Map();
    this.qrCodes = new Map();
    this.monitoringInterval = null;
    this.updateListeners = new Set();
  }

  /**
   * Start monitoring NGROK tunnels and auto-generate QR codes
   */
  async startMonitoring(options = {}) {
    const {
      interval = 30000, // 30 seconds
      autoGenerate = true,
      expiration = 24 * 60 * 60 * 1000, // 24 hours
      customization = {}
    } = options;

    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }

    // Initial scan
    await this.scanTunnels(autoGenerate, expiration, customization);

    // Set up periodic monitoring
    this.monitoringInterval = setInterval(async () => {
      await this.scanTunnels(autoGenerate, expiration, customization);
    }, interval);

    console.log('🔍 NGROK QR monitoring started');
  }

  /**
   * Stop monitoring
   */
  stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      console.log('⏹️ NGROK QR monitoring stopped');
    }
  }

  /**
   * Scan for active NGROK tunnels
   */
  async scanTunnels(autoGenerate = true, expiration = 24 * 60 * 60 * 1000, customization = {}) {
    try {
      const tunnels = await this.getTunnels();
      const previousTunnels = new Set(this.activeTunnels.keys());
      const currentTunnels = new Set();

      // Process each tunnel
      for (const tunnel of tunnels) {
        const tunnelKey = `${tunnel.proto}_${tunnel.local_port}`;
        currentTunnels.add(tunnelKey);

        // Check if this is a new tunnel
        if (!this.activeTunnels.has(tunnelKey)) {
          this.activeTunnels.set(tunnelKey, tunnel);
          
          if (autoGenerate) {
            await this.generateTunnelQR(tunnel, expiration, customization);
          }

          console.log(`🆕 New tunnel detected: ${tunnel.public_url}`);
          this.notifyListeners('tunnel_added', tunnel);
        } else {
          // Update existing tunnel info
          const existing = this.activeTunnels.get(tunnelKey);
          if (existing.public_url !== tunnel.public_url) {
            this.activeTunnels.set(tunnelKey, tunnel);
            
            // Regenerate QR code for URL change
            if (autoGenerate) {
              await this.generateTunnelQR(tunnel, expiration, customization);
            }

            console.log(`🔄 Tunnel URL updated: ${tunnel.public_url}`);
            this.notifyListeners('tunnel_updated', tunnel);
          }
        }
      }

      // Handle removed tunnels
      for (const tunnelKey of previousTunnels) {
        if (!currentTunnels.has(tunnelKey)) {
          const tunnel = this.activeTunnels.get(tunnelKey);
          this.activeTunnels.delete(tunnelKey);
          
          // Revoke QR codes for removed tunnels
          const qrData = this.qrCodes.get(tunnelKey);
          if (qrData) {
            this.qrCodeService.revokeToken(qrData.sessionId);
            this.qrCodes.delete(tunnelKey);
          }

          console.log(`🗑️ Tunnel removed: ${tunnel?.public_url}`);
          this.notifyListeners('tunnel_removed', tunnel);
        }
      }

    } catch (error) {
      console.error('Error scanning tunnels:', error);
    }
  }

  /**
   * Get active NGROK tunnels via API
   */
  async getTunnels() {
    try {
      // Try NGROK API first
      const response = await fetch('http://localhost:4040/api/tunnels');
      if (response.ok) {
        const data = await response.json();
        return data.tunnels || [];
      }
    } catch (error) {
      // Fallback to command line if API not available
      console.warn('NGROK API not available, falling back to CLI');
    }

    // Fallback to parsing ngrok output
    return new Promise((resolve) => {
      exec('ngrok status', (error, stdout, stderr) => {
        if (error) {
          console.warn('Could not get NGROK status:', error.message);
          resolve([]);
          return;
        }

        try {
          const tunnels = this.parseNgrokStatus(stdout);
          resolve(tunnels);
        } catch (parseError) {
          console.warn('Could not parse NGROK status:', parseError);
          resolve([]);
        }
      });
    });
  }

  /**
   * Parse ngrok status output
   */
  parseNgrokStatus(output) {
    const tunnels = [];
    const lines = output.split('\n');
    
    for (const line of lines) {
      // Look for tunnel lines (this is a simplified parser)
      const match = line.match(/(\w+):\/\/([^\.]+\.ngrok\.io)\s+\->\s+localhost:(\d+)/);
      if (match) {
        tunnels.push({
          name: `tunnel_${match[3]}`,
          proto: match[1],
          public_url: `${match[1]}://${match[2]}`,
          local_port: parseInt(match[3]),
          config: {
            addr: `localhost:${match[3]}`,
            inspect: true
          }
        });
      }
    }
    
    return tunnels;
  }

  /**
   * Generate QR code for a tunnel
   */
  async generateTunnelQR(tunnel, expiration = 24 * 60 * 60 * 1000, customization = {}) {
    try {
      const tunnelKey = `${tunnel.proto}_${tunnel.local_port}`;
      
      const qrResult = await this.qrCodeService.generateTunnelQRCode(
        tunnel.public_url,
        {
          serviceName: tunnel.name || `${tunnel.proto.toUpperCase()} Tunnel`,
          description: `Access ${tunnel.proto} service on port ${tunnel.local_port}`,
          expiration,
          customization: {
            size: 512,
            color: {
              dark: '#000000',
              light: '#FFFFFF'
            },
            ...customization
          }
        }
      );

      this.qrCodes.set(tunnelKey, qrResult);
      
      // Save QR code image to file
      await this.saveQRCodeImage(tunnelKey, qrResult);

      console.log(`📱 QR code generated for tunnel: ${tunnel.public_url}`);
      this.notifyListeners('qr_generated', { tunnel, qrResult });

      return qrResult;
    } catch (error) {
      console.error('Error generating tunnel QR code:', error);
      throw error;
    }
  }

  /**
   * Save QR code image to file system
   */
  async saveQRCodeImage(tunnelKey, qrResult) {
    try {
      const qrDir = path.join(__dirname, '../qr-codes');
      await fs.mkdir(qrDir, { recursive: true });

      const filename = `tunnel_${tunnelKey}_${qrResult.sessionId}.png`;
      const filepath = path.join(qrDir, filename);

      // Convert data URL to buffer and save
      const base64Data = qrResult.qrCode.replace(/^data:image\/png;base64,/, '');
      await fs.writeFile(filepath, base64Data, 'base64');

      console.log(`💾 QR code saved: ${filepath}`);
      return filepath;
    } catch (error) {
      console.error('Error saving QR code image:', error);
    }
  }

  /**
   * Generate batch QR codes for all active tunnels
   */
  async generateBatchQRCodes(options = {}) {
    const results = [];
    
    for (const [tunnelKey, tunnel] of this.activeTunnels) {
      try {
        const qrResult = await this.generateTunnelQR(tunnel, options.expiration, options.customization);
        results.push({ tunnel, qrResult, success: true });
      } catch (error) {
        results.push({ tunnel, error: error.message, success: false });
      }
    }

    return results;
  }

  /**
   * Get QR code for specific tunnel
   */
  getTunnelQR(port, protocol = 'http') {
    const tunnelKey = `${protocol}_${port}`;
    return this.qrCodes.get(tunnelKey);
  }

  /**
   * Get all tunnel QR codes
   */
  getAllTunnelQRs() {
    const result = {};
    for (const [tunnelKey, qrData] of this.qrCodes) {
      const tunnel = this.activeTunnels.get(tunnelKey);
      if (tunnel) {
        result[tunnelKey] = {
          tunnel,
          qrData
        };
      }
    }
    return result;
  }

  /**
   * Create mobile-optimized landing page URLs
   */
  createMobileLandingURLs() {
    const urls = {};
    
    for (const [tunnelKey, qrData] of this.qrCodes) {
      const tunnel = this.activeTunnels.get(tunnelKey);
      if (tunnel) {
        const landingUrl = `${tunnel.public_url}/mobile?token=${qrData.token}&session=${qrData.sessionId}`;
        urls[tunnelKey] = landingUrl;
      }
    }

    return urls;
  }

  /**
   * Generate multi-service QR code for all tunnels
   */
  async generateMultiServiceQR(options = {}) {
    const services = Array.from(this.activeTunnels.values()).map(tunnel => ({
      name: tunnel.name || `${tunnel.proto.toUpperCase()} Service`,
      url: tunnel.public_url,
      description: `Access via port ${tunnel.local_port}`,
      icon: tunnel.proto === 'https' ? 'secure' : 'web',
      permissions: ['read', 'connect']
    }));

    if (services.length === 0) {
      throw new Error('No active tunnels found');
    }

    return await this.qrCodeService.generateMultiServiceQR(services, {
      title: 'Claude Code Services',
      expiration: options.expiration || 24 * 60 * 60 * 1000,
      customization: options.customization || {}
    });
  }

  /**
   * Add update listener
   */
  addListener(listener) {
    this.updateListeners.add(listener);
  }

  /**
   * Remove update listener
   */
  removeListener(listener) {
    this.updateListeners.delete(listener);
  }

  /**
   * Notify listeners of updates
   */
  notifyListeners(event, data) {
    this.updateListeners.forEach(listener => {
      try {
        listener(event, data);
      } catch (error) {
        console.error('Listener error:', error);
      }
    });
  }

  /**
   * Get tunnel statistics
   */
  getStatistics() {
    return {
      activeTunnels: this.activeTunnels.size,
      qrCodes: this.qrCodes.size,
      protocols: Array.from(this.activeTunnels.values()).reduce((acc, tunnel) => {
        acc[tunnel.proto] = (acc[tunnel.proto] || 0) + 1;
        return acc;
      }, {}),
      ports: Array.from(this.activeTunnels.values()).map(t => t.local_port)
    };
  }

  /**
   * Cleanup expired QR codes
   */
  async cleanup() {
    const cleaned = this.qrCodeService.cleanupExpiredTokens();
    
    // Clean up local storage
    for (const [tunnelKey, qrData] of this.qrCodes) {
      if (Date.now() > qrData.expiresAt) {
        this.qrCodes.delete(tunnelKey);
      }
    }

    return cleaned;
  }

  /**
   * Export configuration
   */
  exportConfig() {
    return {
      tunnels: Object.fromEntries(this.activeTunnels),
      qrCodes: Object.fromEntries(this.qrCodes),
      statistics: this.getStatistics(),
      timestamp: Date.now()
    };
  }
}

module.exports = NGROKQRIntegration;