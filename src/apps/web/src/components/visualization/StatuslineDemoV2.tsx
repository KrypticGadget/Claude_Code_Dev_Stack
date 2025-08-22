import React, { useState, useEffect } from 'react'
import { StatuslineV2 } from './StatuslineV2'
import { useSystemMetrics } from '../hooks/useSystemMetrics'
import { useGitStatus } from '../hooks/useGitStatus'
import { useClaudeSession } from '../hooks/useClaudeSession'
import { useWebSocket } from '../hooks/useWebSocket'
import './StatuslineDemoV2.css'

// Mock agent data
const mockAgents = [
  {
    id: 'frontend-architect',
    name: 'Frontend Architect',
    status: 'active' as const,
    progress: 75,
    lastAction: 'Designing component hierarchy',
    performance: 92
  },
  {
    id: 'backend-services',
    name: 'Backend Services',
    status: 'idle' as const,
    progress: 100,
    lastAction: 'API endpoints configured',
    performance: 88
  },
  {
    id: 'ui-ux-design',
    name: 'UI/UX Design',
    status: 'active' as const,
    progress: 45,
    lastAction: 'Creating responsive layouts',
    performance: 95
  },
  {
    id: 'production-frontend',
    name: 'Production Frontend',
    status: 'error' as const,
    progress: 30,
    lastAction: 'Build failed - fixing dependencies',
    performance: 67
  },
  {
    id: 'database-architecture',
    name: 'Database Architecture',
    status: 'loading' as const,
    progress: 20,
    lastAction: 'Optimizing queries',
    performance: 84
  }
]

export const StatuslineDemoV2: React.FC = () => {
  // Real-time data hooks
  const { metrics: systemMetrics, isLoading: systemLoading } = useSystemMetrics({
    updateInterval: 1000,
    enableDetailedMetrics: true,
    enableNetworkLatency: true
  })
  
  const { gitStatus, isLoading: gitLoading } = useGitStatus({
    updateInterval: 2000,
    maxCommits: 10,
    watchFileChanges: true
  })
  
  const { session: claudeSession, isLoading: sessionLoading } = useClaudeSession({
    updateInterval: 1000,
    trackPerformance: true,
    enableCostTracking: true
  })
  
  const { isConnected } = useWebSocket('ws://localhost:8081/ws', {
    reconnectInterval: 1000,
    heartbeatInterval: 5000
  })

  // Demo state
  const [agents, setAgents] = useState(mockAgents)
  const [demoConfig, setDemoConfig] = useState({
    theme: 'powerline' as const,
    updateInterval: 100,
    animations: true,
    sounds: false,
    tooltips: true
  })

  // Simulate agent activity
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents(prev => prev.map(agent => {
        // Randomly update agent status and progress
        const shouldUpdate = Math.random() > 0.7
        if (!shouldUpdate) return agent

        const statuses = ['active', 'idle', 'error', 'loading'] as const
        const newStatus = statuses[Math.floor(Math.random() * statuses.length)]
        
        let newProgress = agent.progress
        if (newStatus === 'active') {
          newProgress = Math.min(100, agent.progress + Math.random() * 5)
        } else if (newStatus === 'error') {
          newProgress = Math.max(0, agent.progress - Math.random() * 10)
        }

        const actions = [
          'Processing user request',
          'Updating component state',
          'Optimizing performance',
          'Running tests',
          'Deploying changes',
          'Analyzing metrics',
          'Handling errors',
          'Syncing with backend'
        ]

        return {
          ...agent,
          status: newStatus,
          progress: Math.round(newProgress),
          lastAction: actions[Math.floor(Math.random() * actions.length)],
          performance: Math.max(60, Math.min(100, agent.performance + (Math.random() - 0.5) * 5))
        }
      }))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  // Handle segment clicks
  const handleSegmentClick = (segmentId: string, data: any) => {
    console.log(`Segment clicked: ${segmentId}`, data)
    
    // In a real app, this could:
    // - Open detailed modal
    // - Navigate to specific page
    // - Trigger actions
    // - Show context menus
  }

  // Handle configuration changes
  const handleConfigChange = (newConfig: any) => {
    setDemoConfig(prev => ({ ...prev, ...newConfig }))
    console.log('Configuration updated:', newConfig)
  }

  return (
    <div className="statusline-demo-v2">
      {/* Enhanced Statusline */}
      <StatuslineV2
        systemMetrics={systemMetrics || undefined}
        gitStatus={gitStatus || undefined}
        claudeSession={claudeSession || undefined}
        agents={agents}
        isConnected={isConnected}
        config={demoConfig}
        onSegmentClick={handleSegmentClick}
        onConfigChange={handleConfigChange}
      />

      {/* Demo Content */}
      <div className="demo-content">
        <div className="demo-header">
          <h1>Enhanced Statusline V2 Demo</h1>
          <p>Real-time system monitoring with configurable segments</p>
        </div>

        <div className="demo-grid">
          {/* System Metrics Card */}
          <div className="demo-card">
            <h3>System Metrics</h3>
            <div className="card-content">
              {systemLoading ? (
                <div className="loading">Loading system metrics...</div>
              ) : systemMetrics ? (
                <div className="metrics-summary">
                  <div className="metric">
                    <span className="label">CPU:</span>
                    <span className="value">{systemMetrics.cpu.usage.toFixed(1)}%</span>
                  </div>
                  <div className="metric">
                    <span className="label">Memory:</span>
                    <span className="value">{systemMetrics.memory.percentage.toFixed(1)}%</span>
                  </div>
                  <div className="metric">
                    <span className="label">Disk:</span>
                    <span className="value">{systemMetrics.disk.percentage.toFixed(1)}%</span>
                  </div>
                  <div className="metric">
                    <span className="label">Network:</span>
                    <span className="value">{systemMetrics.network.latency}ms</span>
                  </div>
                </div>
              ) : (
                <div className="error">Failed to load system metrics</div>
              )}
            </div>
          </div>

          {/* Git Status Card */}
          <div className="demo-card">
            <h3>Git Repository</h3>
            <div className="card-content">
              {gitLoading ? (
                <div className="loading">Loading Git status...</div>
              ) : gitStatus ? (
                <div className="git-summary">
                  <div className="metric">
                    <span className="label">Branch:</span>
                    <span className="value">{gitStatus.branch}</span>
                  </div>
                  <div className="metric">
                    <span className="label">Status:</span>
                    <span className={`value status-${gitStatus.status}`}>
                      {gitStatus.status}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="label">Changes:</span>
                    <span className="value">
                      {gitStatus.staged + gitStatus.unstaged + gitStatus.untracked}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="label">Commits:</span>
                    <span className="value">{gitStatus.totalCommits}</span>
                  </div>
                </div>
              ) : (
                <div className="error">Failed to load Git status</div>
              )}
            </div>
          </div>

          {/* Claude Session Card */}
          <div className="demo-card">
            <h3>Claude Session</h3>
            <div className="card-content">
              {sessionLoading ? (
                <div className="loading">Loading session data...</div>
              ) : claudeSession ? (
                <div className="session-summary">
                  <div className="metric">
                    <span className="label">Model:</span>
                    <span className="value">{claudeSession.model.displayName}</span>
                  </div>
                  <div className="metric">
                    <span className="label">Tokens:</span>
                    <span className="value">
                      {claudeSession.tokens.percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="label">Cost:</span>
                    <span className="value">
                      ${claudeSession.billing.sessionCost.toFixed(3)}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="label">Quality:</span>
                    <span className={`value quality-${claudeSession.metrics.quality}`}>
                      {claudeSession.metrics.quality}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="error">Failed to load session data</div>
              )}
            </div>
          </div>

          {/* Agents Card */}
          <div className="demo-card">
            <h3>Active Agents</h3>
            <div className="card-content">
              <div className="agents-list">
                {agents.map(agent => (
                  <div key={agent.id} className="agent-item">
                    <div className="agent-header">
                      <span className="agent-name">{agent.name}</span>
                      <span className={`agent-status status-${agent.status}`}>
                        {agent.status}
                      </span>
                    </div>
                    <div className="agent-progress">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ width: `${agent.progress}%` }}
                        />
                      </div>
                      <span className="progress-text">{agent.progress}%</span>
                    </div>
                    <div className="agent-action">{agent.lastAction}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Configuration Card */}
          <div className="demo-card">
            <h3>Configuration</h3>
            <div className="card-content">
              <div className="config-options">
                <div className="config-group">
                  <label>Theme:</label>
                  <select 
                    value={demoConfig.theme}
                    onChange={e => handleConfigChange({ theme: e.target.value })}
                  >
                    <option value="powerline">Powerline</option>
                    <option value="minimal">Minimal</option>
                    <option value="classic">Classic</option>
                    <option value="compact">Compact</option>
                  </select>
                </div>
                
                <div className="config-group">
                  <label>Update Interval:</label>
                  <select 
                    value={demoConfig.updateInterval}
                    onChange={e => handleConfigChange({ updateInterval: parseInt(e.target.value) })}
                  >
                    <option value={100}>100ms</option>
                    <option value={500}>500ms</option>
                    <option value={1000}>1s</option>
                    <option value={2000}>2s</option>
                  </select>
                </div>
                
                <div className="config-group">
                  <label>
                    <input 
                      type="checkbox"
                      checked={demoConfig.animations}
                      onChange={e => handleConfigChange({ animations: e.target.checked })}
                    />
                    Animations
                  </label>
                </div>
                
                <div className="config-group">
                  <label>
                    <input 
                      type="checkbox"
                      checked={demoConfig.tooltips}
                      onChange={e => handleConfigChange({ tooltips: e.target.checked })}
                    />
                    Tooltips
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Features Card */}
          <div className="demo-card">
            <h3>Features</h3>
            <div className="card-content">
              <div className="features-list">
                <div className="feature">✅ Real-time system metrics</div>
                <div className="feature">✅ Git repository status</div>
                <div className="feature">✅ Claude session tracking</div>
                <div className="feature">✅ Agent activity monitoring</div>
                <div className="feature">✅ WebSocket live updates</div>
                <div className="feature">✅ Configurable segments</div>
                <div className="feature">✅ Multiple themes</div>
                <div className="feature">✅ Click interactions</div>
                <div className="feature">✅ Responsive design</div>
                <div className="feature">✅ Accessibility support</div>
                <div className="feature">✅ Performance optimized</div>
                <div className="feature">✅ Notification system</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatuslineDemoV2