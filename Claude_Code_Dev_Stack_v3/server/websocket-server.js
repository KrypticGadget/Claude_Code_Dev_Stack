/**
 * Claude Code Dev Stack v3.0 - WebSocket Backend Server
 * Port: 8080
 * 
 * Credits:
 * - Based on patterns from @zainhoda/claude-code-browser
 * - Extended for real-time agent orchestration
 * - Original orchestration system by Zach
 */

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: ["http://localhost:3000", "http://localhost:5173"],
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// State Management for 28 Agents
let agentStates = {};
let taskProgress = {};
let hookStatus = {};
let audioEvents = [];

// Initialize 28 agents
for (let i = 1; i <= 28; i++) {
  agentStates[`agent-${i}`] = {
    id: i,
    status: 'idle',
    currentTask: null,
    lastActivity: Date.now()
  };
}

// API Routes
app.get('/api/agents', (req, res) => {
  res.json({
    agents: agentStates,
    totalAgents: 28,
    activeAgents: Object.values(agentStates).filter(a => a.status === 'active').length
  });
});

app.get('/api/tasks', (req, res) => {
  res.json({
    tasks: taskProgress,
    completed: Object.values(taskProgress).filter(t => t.status === 'completed').length,
    total: Object.keys(taskProgress).length
  });
});

app.get('/api/hooks', (req, res) => {
  res.json({
    hooks: hookStatus,
    triggered: Object.values(hookStatus).filter(h => h.triggered).length,
    total: 28
  });
});

app.get('/api/audio', (req, res) => {
  res.json({
    events: audioEvents.slice(-10), // Last 10 events
    lastEvent: audioEvents[audioEvents.length - 1] || null
  });
});

app.post('/api/agents/:id/activate', (req, res) => {
  const { id } = req.params;
  const { task } = req.body;
  
  if (agentStates[`agent-${id}`]) {
    agentStates[`agent-${id}`] = {
      ...agentStates[`agent-${id}`],
      status: 'active',
      currentTask: task,
      lastActivity: Date.now()
    };
    
    // Broadcast update
    io.emit('agent:activated', {
      agentId: id,
      status: agentStates[`agent-${id}`]
    });
    
    res.json({ success: true, agent: agentStates[`agent-${id}`] });
  } else {
    res.status(404).json({ error: 'Agent not found' });
  }
});

app.post('/api/tasks', (req, res) => {
  const { name, description, priority = 'medium' } = req.body;
  const taskId = `task-${Date.now()}`;
  
  taskProgress[taskId] = {
    id: taskId,
    name,
    description,
    priority,
    status: 'pending',
    progress: 0,
    createdAt: Date.now()
  };
  
  io.emit('task:created', taskProgress[taskId]);
  res.json({ success: true, task: taskProgress[taskId] });
});

app.post('/api/audio/play', (req, res) => {
  const { soundFile, context = 'system' } = req.body;
  
  const audioEvent = {
    id: Date.now(),
    soundFile,
    context,
    timestamp: Date.now()
  };
  
  audioEvents.push(audioEvent);
  
  // Keep only last 100 events
  if (audioEvents.length > 100) {
    audioEvents = audioEvents.slice(-100);
  }
  
  io.emit('audio:played', audioEvent);
  res.json({ success: true, event: audioEvent });
});

// WebSocket Connection Handling
io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`);
  
  // Send initial state
  socket.emit('initial:state', {
    agents: agentStates,
    tasks: taskProgress,
    hooks: hookStatus,
    audio: audioEvents.slice(-5)
  });
  
  // Agent operations
  socket.on('agent:subscribe', (agentId) => {
    socket.join(`agent-${agentId}`);
    console.log(`Socket ${socket.id} subscribed to agent-${agentId}`);
  });
  
  socket.on('agent:status:update', (data) => {
    const { agentId, status, task } = data;
    
    if (agentStates[`agent-${agentId}`]) {
      agentStates[`agent-${agentId}`] = {
        ...agentStates[`agent-${agentId}`],
        status,
        currentTask: task,
        lastActivity: Date.now()
      };
      
      io.emit('agent:updated', {
        agentId,
        agent: agentStates[`agent-${agentId}`]
      });
    }
  });
  
  // Task operations
  socket.on('task:progress:update', (data) => {
    const { taskId, progress, status } = data;
    
    if (taskProgress[taskId]) {
      taskProgress[taskId] = {
        ...taskProgress[taskId],
        progress,
        status,
        updatedAt: Date.now()
      };
      
      io.emit('task:updated', {
        taskId,
        task: taskProgress[taskId]
      });
    }
  });
  
  // Hook operations
  socket.on('hook:triggered', (data) => {
    const { hookId, context } = data;
    
    hookStatus[hookId] = {
      id: hookId,
      triggered: true,
      context,
      lastTriggered: Date.now()
    };
    
    io.emit('hook:activated', {
      hookId,
      hook: hookStatus[hookId]
    });
  });
  
  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: Date.now(),
    services: {
      agents: '28 initialized',
      websocket: 'active',
      api: 'ready'
    }
  });
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`🚀 Claude Code Dev Stack v3.0 WebSocket Server running on port ${PORT}`);
  console.log(`📊 Managing 28 agents with real-time coordination`);
  console.log(`🔗 WebSocket endpoint: ws://localhost:${PORT}`);
  console.log(`📡 REST API: http://localhost:${PORT}/api`);
});