#!/usr/bin/env node
/**
 * Unified Backend Server for Claude Code Dev Stack v3.0
 * Consolidates all backend services into one server
 */

const express = require('express');
const { createServer } = require('http');
const { WebSocketServer } = require('ws');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

// Configuration
const PORT = process.env.PORT || 8000;
const SERVICES = {
  websocket: `ws://localhost:${PORT}/ws`,
  api: `http://localhost:${PORT}/api`,
  generators: `http://localhost:${PORT}/generators`,
  lsp: `http://localhost:${PORT}/lsp`,
  semantic: `http://localhost:${PORT}/semantic`,
  patterns: `http://localhost:${PORT}/patterns`,
  visual: `http://localhost:${PORT}/visual`
};

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// WebSocket connection management
const clients = new Set();
const broadcastMessage = (type, payload) => {
  const message = JSON.stringify({ type, payload, timestamp: new Date() });
  clients.forEach(client => {
    if (client.readyState === 1) { // OPEN
      client.send(message);
    }
  });
};

// WebSocket server
wss.on('connection', (ws, req) => {
  console.log('New WebSocket connection from:', req.socket.remoteAddress);
  clients.add(ws);

  // Send initial state
  ws.send(JSON.stringify({
    type: 'connection',
    payload: {
      services: SERVICES,
      agents: { active: 0, total: 28 },
      hooks: { triggered: 0, total: 37 },
      tasks: { completed: 0, total: 0 }
    }
  }));

  // Handle messages
  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      console.log('Received:', data.type);

      switch (data.type) {
        case 'handshake':
          ws.send(JSON.stringify({
            type: 'handshake-ack',
            payload: { status: 'connected', services: SERVICES }
          }));
          break;

        case 'agent-invoke':
          handleAgentInvoke(data.payload, ws);
          break;

        case 'hook-trigger':
          handleHookTrigger(data.payload, ws);
          break;

        case 'audio-play':
          handleAudioPlay(data.payload, ws);
          break;

        case 'generator-request':
          handleGeneratorRequest(data.payload, ws);
          break;

        case 'lsp-request':
          handleLSPRequest(data.payload, ws);
          break;

        case 'semantic-analyze':
          handleSemanticAnalysis(data.payload, ws);
          break;

        default:
          console.log('Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('Message processing error:', error);
      ws.send(JSON.stringify({
        type: 'error',
        payload: { message: error.message }
      }));
    }
  });

  ws.on('close', () => {
    clients.delete(ws);
    console.log('Client disconnected');
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

// REST API Routes

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    uptime: process.uptime(),
    services: SERVICES,
    connections: clients.size
  });
});

// Agent management
app.get('/api/agents', async (req, res) => {
  try {
    const agentsPath = path.join(__dirname, '../core/agents/agents');
    const files = await fs.readdir(agentsPath);
    const agents = files
      .filter(f => f.endsWith('.py'))
      .map(f => ({
        id: f.replace('.py', ''),
        name: f.replace(/_/g, ' ').replace('.py', ''),
        status: 'ready'
      }));
    
    res.json({ agents, total: agents.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/agents/invoke', async (req, res) => {
  const { agentId, prompt } = req.body;
  
  try {
    const result = await invokeAgent(agentId, prompt);
    res.json({ success: true, result });
    
    // Broadcast update
    broadcastMessage('agent-update', {
      active: 1,
      total: 28,
      lastAgent: agentId
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Hook management
app.get('/api/hooks', async (req, res) => {
  try {
    const hooksPath = path.join(__dirname, '../core/hooks/hooks');
    const files = await fs.readdir(hooksPath);
    const hooks = files
      .filter(f => f.endsWith('.py'))
      .map(f => ({
        id: f.replace('.py', ''),
        name: f.replace(/_/g, ' ').replace('.py', ''),
        enabled: true
      }));
    
    res.json({ hooks, total: hooks.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/hooks/trigger', async (req, res) => {
  const { hookId, data } = req.body;
  
  try {
    const result = await triggerHook(hookId, data);
    res.json({ success: true, result });
    
    // Broadcast update
    broadcastMessage('hook-update', {
      triggered: 1,
      total: 37,
      lastHook: hookId
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// MCP Generator endpoint
app.post('/api/generators/generate', async (req, res) => {
  const { spec, generator, options } = req.body;
  
  try {
    const result = await generateMCPCode(spec, generator, options);
    res.json({ success: true, code: result });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// LSP endpoint
app.post('/api/lsp/analyze', async (req, res) => {
  const { file, language } = req.body;
  
  try {
    const diagnostics = await analyzeLSP(file, language);
    res.json({ success: true, diagnostics });
    
    // Broadcast diagnostics
    broadcastMessage('diagnostic-update', diagnostics);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Semantic analysis endpoint
app.post('/api/semantic/analyze', async (req, res) => {
  const { code, language } = req.body;
  
  try {
    const analysis = await analyzeSemantics(code, language);
    res.json({ success: true, analysis });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Helper functions

async function invokeAgent(agentId, prompt) {
  return new Promise((resolve, reject) => {
    const agentPath = path.join(__dirname, `../core/agents/agents/${agentId}.py`);
    const python = spawn('python', [agentPath, prompt]);
    
    let output = '';
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      console.error(`Agent error: ${data}`);
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`Agent exited with code ${code}`));
      }
    });
  });
}

async function triggerHook(hookId, data) {
  return new Promise((resolve, reject) => {
    const hookPath = path.join(__dirname, `../core/hooks/hooks/${hookId}.py`);
    const python = spawn('python', [hookPath], {
      env: { ...process.env, HOOK_DATA: JSON.stringify(data) }
    });
    
    let output = '';
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`Hook exited with code ${code}`));
      }
    });
  });
}

async function generateMCPCode(spec, generator = 'auto', options = {}) {
  // Determine which generator to use
  const useGenerator = generator === 'auto' 
    ? (spec.includes('python') ? 'python' : 'nodejs')
    : generator;
  
  if (useGenerator === 'python') {
    const genPath = path.join(__dirname, '../core/generators/python/mcp_codegen.py');
    // Implementation would call Python generator
    return `# Generated Python MCP code\nclass MCPServer:\n    pass`;
  } else {
    const genPath = path.join(__dirname, '../core/generators/nodejs/index.js');
    // Implementation would call Node.js generator
    return `// Generated Node.js MCP code\nclass MCPServer { }`;
  }
}

async function analyzeLSP(file, language) {
  // Mock LSP analysis - would integrate with actual LSP daemon
  return [
    {
      severity: 'warning',
      line: 10,
      column: 5,
      message: 'Unused variable',
      source: 'lsp'
    }
  ];
}

async function analyzeSemantics(code, language) {
  // Mock semantic analysis - would integrate with actual semantic API
  return {
    complexity: 5,
    patterns: ['singleton', 'factory'],
    symbols: ['class', 'function', 'variable'],
    quality: 'good'
  };
}

// Handler functions for WebSocket messages
async function handleAgentInvoke(payload, ws) {
  const { agentId, prompt } = payload;
  try {
    const result = await invokeAgent(agentId, prompt);
    ws.send(JSON.stringify({
      type: 'agent-response',
      payload: { agentId, result }
    }));
  } catch (error) {
    ws.send(JSON.stringify({
      type: 'agent-error',
      payload: { agentId, error: error.message }
    }));
  }
}

async function handleHookTrigger(payload, ws) {
  const { hookId, data } = payload;
  try {
    const result = await triggerHook(hookId, data);
    ws.send(JSON.stringify({
      type: 'hook-response',
      payload: { hookId, result }
    }));
  } catch (error) {
    ws.send(JSON.stringify({
      type: 'hook-error',
      payload: { hookId, error: error.message }
    }));
  }
}

async function handleAudioPlay(payload, ws) {
  const { file } = payload;
  // Broadcast to all clients
  broadcastMessage('audio-event', {
    lastFile: file,
    playing: true
  });
}

async function handleGeneratorRequest(payload, ws) {
  const { spec, generator, options } = payload;
  try {
    const code = await generateMCPCode(spec, generator, options);
    ws.send(JSON.stringify({
      type: 'generator-response',
      payload: { code }
    }));
  } catch (error) {
    ws.send(JSON.stringify({
      type: 'generator-error',
      payload: { error: error.message }
    }));
  }
}

async function handleLSPRequest(payload, ws) {
  const { file, language } = payload;
  try {
    const diagnostics = await analyzeLSP(file, language);
    ws.send(JSON.stringify({
      type: 'lsp-response',
      payload: { diagnostics }
    }));
  } catch (error) {
    ws.send(JSON.stringify({
      type: 'lsp-error',
      payload: { error: error.message }
    }));
  }
}

async function handleSemanticAnalysis(payload, ws) {
  const { code, language } = payload;
  try {
    const analysis = await analyzeSemantics(code, language);
    ws.send(JSON.stringify({
      type: 'semantic-response',
      payload: { analysis }
    }));
  } catch (error) {
    ws.send(JSON.stringify({
      type: 'semantic-error',
      payload: { error: error.message }
    }));
  }
}

// Start server
server.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════╗
║   Claude Code Dev Stack v3.0 - Unified Server     ║
╠════════════════════════════════════════════════════╣
║   Server running at: http://localhost:${PORT}        ║
║   WebSocket at:      ws://localhost:${PORT}/ws       ║
║                                                    ║
║   Services:                                        ║
║   • API:        http://localhost:${PORT}/api         ║
║   • Generators: http://localhost:${PORT}/generators  ║
║   • LSP:        http://localhost:${PORT}/lsp         ║
║   • Semantic:   http://localhost:${PORT}/semantic    ║
║                                                    ║
║   Status: Ready to accept connections              ║
╚════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});