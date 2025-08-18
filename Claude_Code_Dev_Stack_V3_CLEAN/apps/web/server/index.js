import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';

const app = express();
const server = createServer(app);

// Configure CORS for Socket.IO
const io = new Server(server, {
  cors: {
    origin: "http://localhost:3001",
    methods: ["GET", "POST"],
    credentials: true
  }
});

// Enable CORS for Express
app.use(cors({
  origin: "http://localhost:3001",
  credentials: true
}));

const PORT = 8080;

// Mock data generators
const generateAgentData = (agentId) => ({
  id: agentId,
  name: `Agent-${agentId}`,
  status: ['active', 'idle', 'processing', 'error'][Math.floor(Math.random() * 4)],
  cpu: Math.floor(Math.random() * 100),
  memory: Math.floor(Math.random() * 100),
  tasks: Math.floor(Math.random() * 50),
  uptime: Math.floor(Math.random() * 86400),
  lastActivity: new Date().toISOString(),
  performance: {
    throughput: Math.floor(Math.random() * 1000),
    latency: Math.floor(Math.random() * 500),
    errorRate: Math.random() * 0.1
  }
});

const generateTaskData = () => ({
  id: Math.random().toString(36).substr(2, 9),
  type: ['api-call', 'data-processing', 'file-operation', 'computation'][Math.floor(Math.random() * 4)],
  status: ['pending', 'running', 'completed', 'failed'][Math.floor(Math.random() * 4)],
  agentId: Math.floor(Math.random() * 29),
  priority: ['low', 'medium', 'high', 'urgent'][Math.floor(Math.random() * 4)],
  progress: Math.floor(Math.random() * 101),
  startTime: new Date(Date.now() - Math.random() * 3600000).toISOString(),
  estimatedCompletion: new Date(Date.now() + Math.random() * 3600000).toISOString(),
  resource: {
    cpu: Math.floor(Math.random() * 50),
    memory: Math.floor(Math.random() * 50)
  }
});

const generateHookData = (hookId) => ({
  id: hookId,
  name: `Hook-${hookId}`,
  type: ['pre-process', 'post-process', 'validation', 'notification'][Math.floor(Math.random() * 4)],
  status: ['active', 'inactive', 'triggered', 'error'][Math.floor(Math.random() * 4)],
  triggerCount: Math.floor(Math.random() * 1000),
  lastTriggered: new Date(Date.now() - Math.random() * 86400000).toISOString(),
  executionTime: Math.floor(Math.random() * 5000),
  successRate: Math.random() * 100,
  config: {
    enabled: Math.random() > 0.2,
    timeout: Math.floor(Math.random() * 30000),
    retryCount: Math.floor(Math.random() * 5)
  }
});

const generateAudioEvent = () => ({
  id: Math.random().toString(36).substr(2, 9),
  type: ['system-alert', 'notification', 'error-sound', 'completion-chime'][Math.floor(Math.random() * 4)],
  source: `agent-${Math.floor(Math.random() * 29)}`,
  volume: Math.floor(Math.random() * 100),
  duration: Math.floor(Math.random() * 5000),
  frequency: Math.floor(Math.random() * 2000) + 100,
  timestamp: new Date().toISOString(),
  metadata: {
    priority: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
    category: ['system', 'user', 'process'][Math.floor(Math.random() * 3)]
  }
});

// Store connected clients
const connectedClients = new Set();

io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`);
  connectedClients.add(socket);

  // Send initial data
  socket.emit('initial-data', {
    agents: Array.from({ length: 29 }, (_, i) => generateAgentData(i)),
    tasks: Array.from({ length: 10 }, () => generateTaskData()),
    hooks: Array.from({ length: 29 }, (_, i) => generateHookData(i)),
    timestamp: new Date().toISOString()
  });

  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
    connectedClients.delete(socket);
  });

  // Handle client requests for specific data
  socket.on('request-agent-data', (agentId) => {
    socket.emit('agent-update', generateAgentData(agentId));
  });

  socket.on('request-hook-data', (hookId) => {
    socket.emit('hook-update', generateHookData(hookId));
  });
});

// Real-time data updates every 100ms
setInterval(() => {
  if (connectedClients.size === 0) return;

  // Agent updates - randomly update 3-5 agents
  const agentUpdates = Math.floor(Math.random() * 3) + 3;
  for (let i = 0; i < agentUpdates; i++) {
    const agentId = Math.floor(Math.random() * 29);
    io.emit('agent-update', generateAgentData(agentId));
  }

  // Task updates - randomly create/update 1-3 tasks
  const taskUpdates = Math.floor(Math.random() * 3) + 1;
  for (let i = 0; i < taskUpdates; i++) {
    io.emit('task-update', generateTaskData());
  }

  // Hook updates - randomly update 1-2 hooks
  const hookUpdates = Math.floor(Math.random() * 2) + 1;
  for (let i = 0; i < hookUpdates; i++) {
    const hookId = Math.floor(Math.random() * 29);
    io.emit('hook-update', generateHookData(hookId));
  }

  // Audio events - occasionally emit audio events
  if (Math.random() < 0.3) { // 30% chance
    io.emit('audio-event', generateAudioEvent());
  }
}, 100);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    connectedClients: connectedClients.size,
    uptime: process.uptime()
  });
});

// Stats endpoint
app.get('/stats', (req, res) => {
  res.json({
    connectedClients: connectedClients.size,
    uptime: process.uptime(),
    memoryUsage: process.memoryUsage(),
    platform: process.platform,
    nodeVersion: process.version
  });
});

server.listen(PORT, () => {
  console.log(`🚀 Claude Code Dev Stack WebSocket Server v3.0`);
  console.log(`📡 Server running on http://localhost:${PORT}`);
  console.log(`🔌 Socket.IO endpoint: ws://localhost:${PORT}`);
  console.log(`🌐 CORS enabled for: http://localhost:3001`);
  console.log(`⚡ Real-time updates every 100ms`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`📈 Stats endpoint: http://localhost:${PORT}/stats`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});