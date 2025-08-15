import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Statusline } from './components/Statusline'
import { AgentDashboard } from './components/AgentDashboard'
import { TaskMonitor } from './components/TaskMonitor'
import { AudioController } from './components/AudioController'
import { MCPManager } from './components/MCPManager'
import { BrowserMonitor } from './components/BrowserMonitor'
import { useWebSocket } from './hooks/useWebSocket'
import './App.css'

// Claude Code Dev Stack v3.0
// Main PWA Application
// Integrates:
// - Claude Powerline (@Owloops) for statusline
// - Claude Code Browser (@zainhoda) for monitoring
// - MCP Manager (@qdhenry) for service orchestration
// See CREDITS.md for full attribution

const queryClient = new QueryClient()

function App() {
  const [agents, setAgents] = useState({ active: 0, total: 28 })
  const [tasks, setTasks] = useState({ completed: 0, total: 0 })
  const [hooks, setHooks] = useState({ triggered: 0, total: 28 })
  const [lastAudio, setLastAudio] = useState<string>('')

  // WebSocket connection for real-time updates (100ms)
  // Connect to Dev Stack API WebSocket (integrates with browser adapter)
  const { data, isConnected } = useWebSocket('ws://localhost:8081/ws', {
    reconnectInterval: 1000,
    heartbeatInterval: 100
  })

  useEffect(() => {
    if (data) {
      // Update metrics from WebSocket
      if (data.type === 'agent-update') {
        setAgents(data.payload)
      } else if (data.type === 'task-update') {
        setTasks(data.payload)
      } else if (data.type === 'hook-update') {
        setHooks(data.payload)
      } else if (data.type === 'audio-event') {
        setLastAudio(data.payload.file)
      }
    }
  }, [data])

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="app">
          {/* Ultimate Statusline - Powerline + Dev Stack */}
          <Statusline 
            agents={agents}
            tasks={tasks}
            hooks={hooks}
            lastAudio={lastAudio}
            isConnected={isConnected}
          />
          
          <main className="main-content">
            <Routes>
              <Route path="/" element={<AgentDashboard agents={agents} />} />
              <Route path="/tasks" element={<TaskMonitor tasks={tasks} />} />
              <Route path="/audio" element={<AudioController lastAudio={lastAudio} />} />
              <Route path="/mcp" element={<MCPManager />} />
              <Route path="/browser" element={<BrowserMonitor />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App