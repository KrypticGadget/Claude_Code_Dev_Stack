#!/usr/bin/env node

/**
 * Claude Code Dev Stack v3.0 - WebSocket Backend Server
 * Port: 8080
 * Integrates real-time updates for all 7 cloned projects
 * 
 * Attribution:
 * - Base architecture from claude-code-browser (@zainhoda) - AGPL-3.0
 * - Real-time monitoring concepts from cc-statusline (@chongdashu) - MIT
 * - MCP integration patterns from mcp-manager (@qdhenry) - MIT
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const QRCodeService = require('./services/qrCodeService');
const NGROKQRIntegration = require('./services/ngrokQRIntegration');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: ["http://localhost:3000", "http://localhost:3001"],
    methods: ["GET", "POST"],
    credentials: true
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// Initialize QR Code Service
const qrCodeService = new QRCodeService();

// Initialize NGROK QR Integration
const ngrokQR = new NGROKQRIntegration();

// Start NGROK monitoring with QR generation
ngrokQR.startMonitoring({
  interval: 30000, // 30 seconds
  autoGenerate: true,
  expiration: 24 * 60 * 60 * 1000, // 24 hours
  customization: {
    size: 512,
    color: { dark: '#000000', light: '#FFFFFF' }
  }
});

// Project monitoring state
const projectState = {
  browser: { status: 'idle', lastUpdate: Date.now() },
  mobile: { status: 'idle', lastUpdate: Date.now() },
  mcp: { status: 'idle', lastUpdate: Date.now() },
  powerline: { status: 'active', lastUpdate: Date.now() },
  statusline: { status: 'active', lastUpdate: Date.now() },
  codegen: { status: 'idle', lastUpdate: Date.now() },
  generator: { status: 'idle', lastUpdate: Date.now() }
};

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`);
  
  // Send initial state
  socket.emit('project-state', projectState);
  
  // Handle project updates
  socket.on('update-project', (data) => {
    const { project, status, metadata } = data;
    if (projectState[project]) {
      projectState[project] = {
        status,
        lastUpdate: Date.now(),
        metadata: metadata || {}
      };
      
      // Broadcast to all clients
      io.emit('project-updated', { project, ...projectState[project] });
    }
  });
  
  // Handle browser monitoring data (from claude-code-browser)
  socket.on('browser-activity', (data) => {
    projectState.browser = {
      status: 'active',
      lastUpdate: Date.now(),
      metadata: {
        tabs: data.tabs || 0,
        memory: data.memory || 0,
        cpu: data.cpu || 0
      }
    };
    io.emit('project-updated', { project: 'browser', ...projectState.browser });
  });
  
  // Handle mobile app status (from claude-code-app)
  socket.on('mobile-status', (data) => {
    projectState.mobile = {
      status: data.status || 'idle',
      lastUpdate: Date.now(),
      metadata: {
        platform: data.platform || 'unknown',
        version: data.version || '1.0.0'
      }
    };
    io.emit('project-updated', { project: 'mobile', ...projectState.mobile });
  });
  
  // Handle MCP manager updates (from mcp-manager)
  socket.on('mcp-update', (data) => {
    projectState.mcp = {
      status: data.status || 'idle',
      lastUpdate: Date.now(),
      metadata: {
        servers: data.servers || [],
        tools: data.tools || []
      }
    };
    io.emit('project-updated', { project: 'mcp', ...projectState.mcp });
  });
  
  // Handle powerline status updates (from claude-powerline)
  socket.on('powerline-status', (data) => {
    projectState.powerline = {
      status: 'active',
      lastUpdate: Date.now(),
      metadata: {
        segments: data.segments || [],
        theme: data.theme || 'default'
      }
    };
    io.emit('project-updated', { project: 'powerline', ...projectState.powerline });
  });
  
  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
  });
});

// QR Code API endpoints
app.post('/api/qr/generate', async (req, res) => {
  try {
    const { type, data, customization } = req.body;
    
    let result;
    switch (type) {
      case 'tunnel':
        result = await qrCodeService.generateTunnelQRCode(
          data.tunnelUrl,
          { ...data, customization }
        );
        break;
      case 'mobile_access':
        result = await qrCodeService.generateMobileAccessQR(
          data.appUrl,
          { ...data, customization }
        );
        break;
      case 'session':
        result = await qrCodeService.generateSessionQR(
          data.sessionData,
          { ...data, customization }
        );
        break;
      case 'time_limited':
        result = await qrCodeService.generateTimeLimitedQR(
          data.resourceUrl,
          data.timeLimit,
          { ...data, customization }
        );
        break;
      case 'multi_service':
        result = await qrCodeService.generateMultiServiceQR(
          data.services,
          { ...data, customization }
        );
        break;
      default:
        return res.status(400).json({ error: 'Invalid QR code type' });
    }
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/qr/batch', async (req, res) => {
  try {
    const { requests, options } = req.body;
    const results = await qrCodeService.batchGenerateQRCodes(requests, options);
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/qr/validate', async (req, res) => {
  try {
    const { token } = req.body;
    const validation = qrCodeService.validateToken(token);
    res.json(validation);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/qr/stats', (req, res) => {
  try {
    const stats = qrCodeService.getStatistics();
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/qr/list', (req, res) => {
  try {
    const activeTokens = qrCodeService.getActiveTokens();
    res.json(activeTokens);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/qr/:sessionId', (req, res) => {
  try {
    const { sessionId } = req.params;
    const result = qrCodeService.revokeToken(sessionId);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/qr/cleanup', (req, res) => {
  try {
    const result = qrCodeService.cleanupExpiredTokens();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Auto-generate tunnel QR codes
app.post('/api/qr/tunnels/auto-generate', async (req, res) => {
  try {
    const { tunnels } = req.body;
    const results = [];
    
    for (const tunnel of tunnels) {
      const qrResult = await qrCodeService.generateTunnelQRCode(tunnel.url, {
        serviceName: tunnel.name || `Tunnel ${tunnel.port}`,
        description: `NGROK tunnel access for port ${tunnel.port}`,
        expiration: 24 * 60 * 60 * 1000 // 24 hours
      });
      results.push({ tunnel, qr: qrResult });
    }
    
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// NGROK Integration API endpoints
app.get('/api/ngrok/tunnels', (req, res) => {
  try {
    const tunnels = Array.from(ngrokQR.activeTunnels.values());
    res.json(tunnels);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/ngrok/qr-codes', (req, res) => {
  try {
    const qrCodes = ngrokQR.getAllTunnelQRs();
    res.json(qrCodes);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/ngrok/stats', (req, res) => {
  try {
    const stats = ngrokQR.getStatistics();
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// REST API endpoints
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: Date.now(),
    projects: Object.keys(projectState).length
  });
});

app.get('/api/projects', (req, res) => {
  res.json(projectState);
});

app.post('/api/projects/:project/update', (req, res) => {
  const { project } = req.params;
  const { status, metadata } = req.body;
  
  if (projectState[project]) {
    projectState[project] = {
      status: status || projectState[project].status,
      lastUpdate: Date.now(),
      metadata: { ...projectState[project].metadata, ...metadata }
    };
    
    io.emit('project-updated', { project, ...projectState[project] });
    res.json({ success: true, project: projectState[project] });
  } else {
    res.status(404).json({ error: 'Project not found' });
  }
});

// File system monitoring for cloned repositories
const monitorClonedRepos = async () => {
  const clonesPath = path.join(__dirname, '../../clones');
  
  try {
    const repos = await fs.readdir(clonesPath);
    
    for (const repo of repos) {
      const repoPath = path.join(clonesPath, repo);
      const stats = await fs.stat(repoPath);
      
      if (stats.isDirectory()) {
        // Check if repo has recent activity
        const isActive = (Date.now() - stats.mtime.getTime()) < 3600000; // 1 hour
        
        const projectKey = repo.replace('claude-code-', '').replace('openapi-mcp-', '').replace('cc-', '');
        
        if (projectState[projectKey]) {
          projectState[projectKey].metadata = {
            ...projectState[projectKey].metadata,
            lastModified: stats.mtime.getTime(),
            recentActivity: isActive
          };
        }
      }
    }
  } catch (error) {
    console.warn('Could not monitor cloned repos:', error.message);
  }
};

// Monitor repos every 30 seconds
setInterval(monitorClonedRepos, 30000);

// Heartbeat to keep connections alive
setInterval(() => {
  io.emit('heartbeat', { timestamp: Date.now() });
}, 10000);

const PORT = process.env.PORT || 8080;

server.listen(PORT, () => {
  console.log(`🚀 Claude Code Dev Stack v3.0 Backend Server`);
  console.log(`📡 WebSocket server running on port ${PORT}`);
  console.log(`🔄 Real-time updates enabled for 7 integrated projects`);
  console.log(`🌐 CORS enabled for localhost:3000 and localhost:3001`);
  
  // Initial repo monitoring
  monitorClonedRepos();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🔄 Gracefully shutting down...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});