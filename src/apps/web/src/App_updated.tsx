import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from './contexts/ThemeContext'
import { Statusline } from './components/Statusline'
import { StatuslineDemoV2 } from './components/StatuslineDemoV2'
import { AgentDashboard } from './components/AgentDashboard'
import { TaskMonitor } from './components/TaskMonitor'
import { AudioController } from './components/AudioController'
import { MCPManager } from './components/MCPManager'
import { BrowserMonitor } from './components/BrowserMonitor'
import { SessionManager } from './components/SessionManager'
import { EditorDemo } from './pages/EditorDemo'
import { SplitViewEditorDemo } from './pages/SplitViewEditorDemo'
import { ThemeSelector } from './components/ThemeSelector'
import { ThemeBuilder } from './components/ThemeBuilder'
import { ThemeManager } from './pages/ThemeManager'
import { useWebSocket } from './hooks/useWebSocket'
import './App.css'
import './styles/editor-demo.css'

// Claude Code Dev Stack v3.6.9
// Main PWA Application with Comprehensive Theme System
// Integrates:
// - Claude Powerline (@Owloops) for statusline
// - Claude Code Browser (@zainhoda) for monitoring
// - MCP Manager (@qdhenry) for service orchestration
// - Advanced Theme System with runtime switching and accessibility
// See CREDITS.md for full attribution

const queryClient = new QueryClient()

function AppContent() {
  const [agents, setAgents] = useState({ active: 0, total: 28 })
  const [tasks, setTasks] = useState({ completed: 0, total: 0 })
  const [hooks, setHooks] = useState({ triggered: 0, total: 28 })
  const [sessions, setSessions] = useState({ active: 0, total: 0, status: 'idle' })
  const [lastAudio, setLastAudio] = useState<string>('')
  const [showThemeBuilder, setShowThemeBuilder] = useState(false)

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
      } else if (data.type === 'session-update') {
        setSessions(data.payload)
      } else if (data.type === 'audio-event') {
        setLastAudio(data.payload.file)
      }
    }
  }, [data])

  // Simulate session updates for demo
  useEffect(() => {
    const interval = setInterval(() => {
      setSessions(prev => ({
        ...prev,
        active: Math.floor(Math.random() * 5) + 1,
        total: Math.floor(Math.random() * 10) + 5,
        status: Math.random() > 0.8 ? 'active' : 'idle'
      }))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app">
      {/* Theme Builder Modal */}
      <ThemeBuilder
        isOpen={showThemeBuilder}
        onClose={() => setShowThemeBuilder(false)}
      />
      
      {/* Ultimate Statusline - Powerline + Dev Stack + Sessions + Theme Selector */}
      <Statusline 
        agents={agents}
        tasks={tasks}
        hooks={hooks}
        sessions={sessions}
        lastAudio={lastAudio}
        isConnected={isConnected}
      />
      
      {/* Theme Selector in Header */}
      <header className="app-header">
        <div className="app-title">
          <h1>Claude Code Dev Stack</h1>
          <span className="app-subtitle">v3.6.9 - Comprehensive Development Environment</span>
        </div>
        
        <div className="header-actions">
          <ThemeSelector 
            onCreateTheme={() => setShowThemeBuilder(true)}
            showCreateButton={true}
          />
        </div>
      </header>
      
      <main className="main-content">
        <Routes>
          <Route path="/" element={<AgentDashboard agents={agents} />} />
          <Route path="/statusline-v2" element={<StatuslineDemoV2 />} />
          <Route path="/sessions" element={<SessionManager />} />
          <Route path="/tasks" element={<TaskMonitor tasks={tasks} />} />
          <Route path="/audio" element={<AudioController lastAudio={lastAudio} />} />
          <Route path="/mcp" element={<MCPManager />} />
          <Route path="/browser" element={<BrowserMonitor />} />
          <Route path="/editor" element={<EditorDemo />} />
          <Route path="/split-editor" element={<SplitViewEditorDemo />} />
          <Route path="/themes" element={<ThemeManager />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider 
        defaultTheme="tokyo-night"
        enableSystemPreference={true}
        enableAutoSwitch={true}
      >
        <Router>
          <AppContent />
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App