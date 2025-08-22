const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const pty = require('node-pty');
const cors = require('cors');
const path = require('path');
const os = require('os');

const app = express();
const server = http.createServer(app);

// Enable CORS
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? process.env.FRONTEND_URL || 'https://localhost:3000'
    : 'http://localhost:3000',
  credentials: true
}));

app.use(express.json());

// Store active terminal sessions
const sessions = new Map();
const processes = new Map();

// WebSocket server for terminal communication
const wss = new WebSocket.Server({ 
  server,
  path: '/terminal'
});

// Determine default shell based on platform
const getDefaultShell = () => {
  if (process.platform === 'win32') {
    return process.env.SHELL || 'powershell.exe';
  } else {
    return process.env.SHELL || '/bin/bash';
  }
};

// Get shell arguments
const getShellArgs = (shell) => {
  if (process.platform === 'win32') {
    if (shell.includes('powershell')) {
      return ['-NoExit', '-Command', '& {Clear-Host}'];
    } else if (shell.includes('cmd')) {
      return ['/k', 'cls'];
    }
  }
  return [];
};

// Terminal session class
class TerminalSession {
  constructor(sessionId, options = {}) {
    this.sessionId = sessionId;
    this.shell = options.shell || getDefaultShell();
    this.cwd = options.cwd || os.homedir();
    this.env = { ...process.env, ...options.env };
    this.cols = options.cols || 80;
    this.rows = options.rows || 24;
    this.ptyProcess = null;
    this.isAlive = false;
    this.createTime = new Date();
    this.lastActivity = new Date();
  }

  create() {
    try {
      const shellArgs = getShellArgs(this.shell);
      
      this.ptyProcess = pty.spawn(this.shell, shellArgs, {
        name: 'xterm-256color',
        cols: this.cols,
        rows: this.rows,
        cwd: this.cwd,
        env: this.env,
        encoding: 'utf8'
      });

      this.isAlive = true;
      console.log(`Created terminal session ${this.sessionId} with PID ${this.ptyProcess.pid}`);

      // Store process info
      processes.set(this.sessionId, {
        pid: this.ptyProcess.pid,
        shell: this.shell,
        cwd: this.cwd,
        startTime: this.createTime
      });

      return true;
    } catch (error) {
      console.error(`Failed to create terminal session ${this.sessionId}:`, error);
      return false;
    }
  }

  write(data) {
    if (this.ptyProcess && this.isAlive) {
      this.ptyProcess.write(data);
      this.lastActivity = new Date();
    }
  }

  resize(cols, rows) {
    if (this.ptyProcess && this.isAlive) {
      try {
        this.ptyProcess.resize(cols, rows);
        this.cols = cols;
        this.rows = rows;
        console.log(`Resized terminal session ${this.sessionId} to ${cols}x${rows}`);
      } catch (error) {
        console.error(`Failed to resize terminal session ${this.sessionId}:`, error);
      }
    }
  }

  kill() {
    if (this.ptyProcess && this.isAlive) {
      try {
        this.ptyProcess.kill();
        this.isAlive = false;
        processes.delete(this.sessionId);
        console.log(`Killed terminal session ${this.sessionId}`);
      } catch (error) {
        console.error(`Failed to kill terminal session ${this.sessionId}:`, error);
      }
    }
  }

  getProcessInfo() {
    return processes.get(this.sessionId);
  }
}

// Handle WebSocket connections
wss.on('connection', (ws, req) => {
  console.log('New terminal WebSocket connection');
  
  const clientSessions = new Set();

  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      const { type, sessionId } = message;

      switch (type) {
        case 'create':
          handleCreateSession(ws, message, clientSessions);
          break;
        
        case 'data':
          handleData(ws, message);
          break;
        
        case 'resize':
          handleResize(ws, message);
          break;
        
        case 'process-list':
          handleProcessList(ws, message);
          break;
        
        case 'kill':
          handleKill(ws, message);
          break;
        
        default:
          console.warn(`Unknown message type: ${type}`);
      }
    } catch (error) {
      console.error('Error processing WebSocket message:', error);
      ws.send(JSON.stringify({
        type: 'error',
        sessionId: 'system',
        error: 'Invalid message format'
      }));
    }
  });

  ws.on('close', () => {
    console.log('Terminal WebSocket connection closed');
    
    // Clean up sessions for this client
    clientSessions.forEach(sessionId => {
      const session = sessions.get(sessionId);
      if (session) {
        session.kill();
        sessions.delete(sessionId);
      }
    });
  });

  ws.on('error', (error) => {
    console.error('Terminal WebSocket error:', error);
  });
});

// Handle session creation
function handleCreateSession(ws, message, clientSessions) {
  const { sessionId, shell, cwd, env, cols, rows } = message;
  
  if (sessions.has(sessionId)) {
    ws.send(JSON.stringify({
      type: 'error',
      sessionId,
      error: 'Session already exists'
    }));
    return;
  }

  const session = new TerminalSession(sessionId, {
    shell,
    cwd,
    env,
    cols,
    rows
  });

  if (session.create()) {
    sessions.set(sessionId, session);
    clientSessions.add(sessionId);

    // Set up data listeners
    session.ptyProcess.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'data',
          sessionId,
          data
        }));
      }
    });

    session.ptyProcess.onExit((exitCode, signal) => {
      console.log(`Terminal session ${sessionId} exited with code ${exitCode}, signal ${signal}`);
      
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'exit',
          sessionId,
          exitCode,
          signal
        }));
      }

      sessions.delete(sessionId);
      clientSessions.delete(sessionId);
    });

    ws.send(JSON.stringify({
      type: 'created',
      sessionId,
      pid: session.ptyProcess.pid
    }));
  } else {
    ws.send(JSON.stringify({
      type: 'error',
      sessionId,
      error: 'Failed to create terminal session'
    }));
  }
}

// Handle data input
function handleData(ws, message) {
  const { sessionId, data } = message;
  const session = sessions.get(sessionId);
  
  if (session) {
    session.write(data);
  } else {
    ws.send(JSON.stringify({
      type: 'error',
      sessionId,
      error: 'Session not found'
    }));
  }
}

// Handle terminal resize
function handleResize(ws, message) {
  const { sessionId, cols, rows } = message;
  const session = sessions.get(sessionId);
  
  if (session) {
    session.resize(cols, rows);
  } else {
    ws.send(JSON.stringify({
      type: 'error',
      sessionId,
      error: 'Session not found'
    }));
  }
}

// Handle process list request
function handleProcessList(ws, message) {
  const { sessionId } = message;
  const processList = Array.from(processes.entries()).map(([id, info]) => ({
    sessionId: id,
    ...info
  }));
  
  ws.send(JSON.stringify({
    type: 'process-list',
    sessionId,
    processes: processList
  }));
}

// Handle process kill request
function handleKill(ws, message) {
  const { sessionId, pid } = message;
  
  if (pid) {
    try {
      process.kill(pid, 'SIGTERM');
      ws.send(JSON.stringify({
        type: 'killed',
        sessionId,
        pid
      }));
    } catch (error) {
      ws.send(JSON.stringify({
        type: 'error',
        sessionId,
        error: `Failed to kill process ${pid}: ${error.message}`
      }));
    }
  } else {
    const session = sessions.get(sessionId);
    if (session) {
      session.kill();
      ws.send(JSON.stringify({
        type: 'killed',
        sessionId
      }));
    }
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    uptime: process.uptime(),
    sessions: sessions.size,
    processes: processes.size,
    platform: process.platform,
    nodeVersion: process.version,
    timestamp: new Date().toISOString()
  });
});

// Session status endpoint
app.get('/sessions', (req, res) => {
  const sessionList = Array.from(sessions.entries()).map(([id, session]) => ({
    sessionId: id,
    isAlive: session.isAlive,
    shell: session.shell,
    cwd: session.cwd,
    cols: session.cols,
    rows: session.rows,
    createTime: session.createTime,
    lastActivity: session.lastActivity,
    processInfo: session.getProcessInfo()
  }));
  
  res.json({
    sessions: sessionList,
    total: sessionList.length
  });
});

// Kill session endpoint
app.delete('/sessions/:sessionId', (req, res) => {
  const { sessionId } = req.params;
  const session = sessions.get(sessionId);
  
  if (session) {
    session.kill();
    sessions.delete(sessionId);
    res.json({ message: `Session ${sessionId} terminated` });
  } else {
    res.status(404).json({ error: 'Session not found' });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Express error:', error);
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? error.message : undefined
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Received SIGTERM, shutting down gracefully');
  
  // Close all terminal sessions
  sessions.forEach((session, sessionId) => {
    console.log(`Closing session ${sessionId}`);
    session.kill();
  });
  
  server.close(() => {
    console.log('Terminal server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('Received SIGINT, shutting down gracefully');
  
  // Close all terminal sessions
  sessions.forEach((session, sessionId) => {
    console.log(`Closing session ${sessionId}`);
    session.kill();
  });
  
  server.close(() => {
    console.log('Terminal server closed');
    process.exit(0);
  });
});

// Start the server
const PORT = process.env.TERMINAL_PORT || 3001;
server.listen(PORT, () => {
  console.log(`Terminal server running on port ${PORT}`);
  console.log(`WebSocket endpoint: ws://localhost:${PORT}/terminal`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`Sessions API: http://localhost:${PORT}/sessions`);
});