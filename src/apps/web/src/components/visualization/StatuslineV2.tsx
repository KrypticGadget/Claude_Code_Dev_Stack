import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { 
  GitBranch, DollarSign, Cpu, Volume2, Zap, Settings, WifiOff, Wifi, 
  AlertTriangle, Database, Users, Clock, HardDrive, Activity, 
  Eye, Monitor, Folder, Calendar, MoreHorizontal, X, ChevronDown
} from 'lucide-react'
import { Link } from 'react-router-dom'
import './StatuslineV2.css'

// Enhanced Status Types
interface SystemMetrics {
  cpu: { usage: number; cores: number; temperature?: number }
  memory: { used: number; total: number; percentage: number }
  disk: { used: number; total: number; percentage: number }
  network: { up: number; down: number; latency: number }
}

interface GitStatus {
  branch: string
  dirty: boolean
  ahead: number
  behind: number
  status: 'clean' | 'dirty' | 'conflict' | 'detached'
  lastCommit?: { hash: string; message: string; author: string; time: Date }
}

interface ClaudeSession {
  id: string
  model: string
  tokens: { used: number; limit: number; cost: number }
  duration: number
  active: boolean
  quality: 'excellent' | 'good' | 'fair' | 'poor'
}

interface AgentStatus {
  id: string
  name: string
  status: 'active' | 'idle' | 'error' | 'loading'
  progress?: number
  lastAction?: string
  performance: number
}

// Segment Configuration Types
interface SegmentConfig {
  id: string
  type: 'git' | 'claude' | 'system' | 'agents' | 'time' | 'custom'
  enabled: boolean
  priority: number
  minWidth?: number
  responsive: boolean
  clickAction?: 'modal' | 'navigate' | 'toggle' | 'custom'
  customAction?: () => void
}

interface StatuslineConfig {
  theme: 'powerline' | 'minimal' | 'classic' | 'compact'
  updateInterval: number
  segments: SegmentConfig[]
  colors: {
    primary: string
    success: string
    warning: string
    error: string
    info: string
  }
  animations: boolean
  sounds: boolean
  tooltips: boolean
}

// Component Props
interface StatuslineV2Props {
  // Core Status Data
  systemMetrics?: SystemMetrics
  gitStatus?: GitStatus
  claudeSession?: ClaudeSession
  agents?: AgentStatus[]
  isConnected: boolean
  
  // Configuration
  config?: Partial<StatuslineConfig>
  
  // Callbacks
  onSegmentClick?: (segmentId: string, data: any) => void
  onConfigChange?: (config: StatuslineConfig) => void
}

// Default Configuration
const defaultConfig: StatuslineConfig = {
  theme: 'powerline',
  updateInterval: 100,
  animations: true,
  sounds: false,
  tooltips: true,
  colors: {
    primary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#6366f1'
  },
  segments: [
    { id: 'path', type: 'custom', enabled: true, priority: 1, responsive: false },
    { id: 'git', type: 'git', enabled: true, priority: 2, responsive: true },
    { id: 'claude', type: 'claude', enabled: true, priority: 3, responsive: true },
    { id: 'agents', type: 'agents', enabled: true, priority: 4, responsive: true },
    { id: 'system', type: 'system', enabled: true, priority: 5, responsive: true },
    { id: 'time', type: 'time', enabled: true, priority: 6, responsive: false }
  ]
}

export const StatuslineV2: React.FC<StatuslineV2Props> = ({
  systemMetrics,
  gitStatus,
  claudeSession,
  agents = [],
  isConnected,
  config: userConfig,
  onSegmentClick,
  onConfigChange
}) => {
  // Configuration State
  const [config, setConfig] = useState<StatuslineConfig>(() => ({
    ...defaultConfig,
    ...userConfig
  }))
  
  // UI State
  const [currentTime, setCurrentTime] = useState(new Date())
  const [expandedSegment, setExpandedSegment] = useState<string | null>(null)
  const [showConfig, setShowConfig] = useState(false)
  const [notifications, setNotifications] = useState<Array<{
    id: string
    type: 'info' | 'warning' | 'error' | 'success'
    message: string
    timestamp: Date
  }>>([])

  // Update current time
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date())
    }, config.updateInterval)
    
    return () => clearInterval(interval)
  }, [config.updateInterval])

  // Handle config changes
  const handleConfigChange = useCallback((newConfig: Partial<StatuslineConfig>) => {
    const updatedConfig = { ...config, ...newConfig }
    setConfig(updatedConfig)
    onConfigChange?.(updatedConfig)
  }, [config, onConfigChange])

  // Handle segment clicks
  const handleSegmentClick = useCallback((segmentId: string, data: any) => {
    if (expandedSegment === segmentId) {
      setExpandedSegment(null)
    } else {
      setExpandedSegment(segmentId)
    }
    onSegmentClick?.(segmentId, data)
  }, [expandedSegment, onSegmentClick])

  // Add notification
  const addNotification = useCallback((type: 'info' | 'warning' | 'error' | 'success', message: string) => {
    const id = Math.random().toString(36).substr(2, 9)
    setNotifications(prev => [...prev, { id, type, message, timestamp: new Date() }])
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id))
    }, 5000)
  }, [])

  // Monitor for status changes and notifications
  useEffect(() => {
    if (systemMetrics) {
      if (systemMetrics.cpu.usage > 90) {
        addNotification('warning', `High CPU usage: ${systemMetrics.cpu.usage}%`)
      }
      if (systemMetrics.memory.percentage > 85) {
        addNotification('warning', `High memory usage: ${systemMetrics.memory.percentage}%`)
      }
    }
  }, [systemMetrics, addNotification])

  useEffect(() => {
    if (gitStatus?.status === 'conflict') {
      addNotification('error', 'Git merge conflict detected')
    }
  }, [gitStatus, addNotification])

  // Sort segments by priority
  const sortedSegments = useMemo(() => {
    return config.segments
      .filter(segment => segment.enabled)
      .sort((a, b) => a.priority - b.priority)
  }, [config.segments])

  // Responsive segment filtering
  const visibleSegments = useMemo(() => {
    // TODO: Add responsive logic based on viewport width
    return sortedSegments
  }, [sortedSegments])

  // Color helpers
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': case 'clean': case 'excellent': return config.colors.success
      case 'warning': case 'dirty': case 'good': return config.colors.warning
      case 'error': case 'conflict': case 'poor': return config.colors.error
      case 'loading': case 'fair': return config.colors.info
      default: return '#6b7280'
    }
  }

  // Path Segment
  const PathSegment = () => (
    <div 
      className="statusline-segment path-segment"
      onClick={() => handleSegmentClick('path', { path: process.cwd() })}
      title="Current working directory"
    >
      <Folder size={14} />
      <span className="segment-value">Claude_Code_Agents/V3.6.9</span>
    </div>
  )

  // Git Segment
  const GitSegment = () => {
    if (!gitStatus) return null
    
    return (
      <div 
        className="statusline-segment git-segment"
        onClick={() => handleSegmentClick('git', gitStatus)}
        title={`Git branch: ${gitStatus.branch} (${gitStatus.status})`}
        style={{ borderLeftColor: getStatusColor(gitStatus.status) }}
      >
        <GitBranch size={14} />
        <span className="segment-value">{gitStatus.branch}</span>
        {gitStatus.dirty && <span className="status-indicator">●</span>}
        {gitStatus.ahead > 0 && <span className="git-ahead">↑{gitStatus.ahead}</span>}
        {gitStatus.behind > 0 && <span className="git-behind">↓{gitStatus.behind}</span>}
      </div>
    )
  }

  // Claude Session Segment
  const ClaudeSegment = () => {
    if (!claudeSession) return null
    
    const tokenPercentage = (claudeSession.tokens.used / claudeSession.tokens.limit) * 100
    
    return (
      <div 
        className="statusline-segment claude-segment"
        onClick={() => handleSegmentClick('claude', claudeSession)}
        title={`Claude ${claudeSession.model} - ${claudeSession.tokens.used}/${claudeSession.tokens.limit} tokens`}
        style={{ borderLeftColor: getStatusColor(claudeSession.quality) }}
      >
        <Cpu size={14} />
        <span className="segment-value">{claudeSession.model}</span>
        <div className="token-bar">
          <div 
            className="token-fill" 
            style={{ 
              width: `${tokenPercentage}%`,
              backgroundColor: tokenPercentage > 80 ? config.colors.error : config.colors.success
            }}
          />
        </div>
        <span className="token-cost">${claudeSession.tokens.cost.toFixed(2)}</span>
      </div>
    )
  }

  // Agents Segment
  const AgentsSegment = () => {
    const activeAgents = agents.filter(agent => agent.status === 'active')
    const errorAgents = agents.filter(agent => agent.status === 'error')
    
    return (
      <div 
        className="statusline-segment agents-segment"
        onClick={() => handleSegmentClick('agents', agents)}
        title={`${activeAgents.length}/${agents.length} agents active`}
        style={{ borderLeftColor: errorAgents.length > 0 ? config.colors.error : config.colors.success }}
      >
        <Users size={14} />
        <span className="segment-value">{activeAgents.length}/{agents.length}</span>
        {errorAgents.length > 0 && (
          <span className="error-count" style={{ color: config.colors.error }}>
            <AlertTriangle size={12} />
            {errorAgents.length}
          </span>
        )}
      </div>
    )
  }

  // System Metrics Segment
  const SystemSegment = () => {
    if (!systemMetrics) return null
    
    const criticalLevel = Math.max(
      systemMetrics.cpu.usage,
      systemMetrics.memory.percentage,
      systemMetrics.disk.percentage
    )
    
    return (
      <div 
        className="statusline-segment system-segment"
        onClick={() => handleSegmentClick('system', systemMetrics)}
        title={`CPU: ${systemMetrics.cpu.usage}% | RAM: ${systemMetrics.memory.percentage}% | Disk: ${systemMetrics.disk.percentage}%`}
        style={{ borderLeftColor: getStatusColor(criticalLevel > 80 ? 'error' : criticalLevel > 60 ? 'warning' : 'active') }}
      >
        <Activity size={14} />
        <div className="system-metrics">
          <span className="cpu-usage">{systemMetrics.cpu.usage}%</span>
          <span className="memory-usage">{systemMetrics.memory.percentage}%</span>
          <span className="disk-usage">{systemMetrics.disk.percentage}%</span>
        </div>
      </div>
    )
  }

  // Connection Segment
  const ConnectionSegment = () => (
    <div 
      className="statusline-segment connection-segment"
      onClick={() => handleSegmentClick('connection', { isConnected })}
      title={isConnected ? 'Connected - Real-time updates' : 'Disconnected'}
    >
      {isConnected ? (
        <>
          <Wifi size={14} style={{ color: config.colors.success }} />
          <span className="segment-value ping">{systemMetrics?.network.latency || 0}ms</span>
        </>
      ) : (
        <>
          <WifiOff size={14} style={{ color: config.colors.error }} />
          <span className="segment-value">Offline</span>
        </>
      )}
    </div>
  )

  // Time Segment
  const TimeSegment = () => (
    <div 
      className="statusline-segment time-segment"
      onClick={() => handleSegmentClick('time', { currentTime })}
      title={currentTime.toLocaleString()}
    >
      <Clock size={14} />
      <span className="segment-value">{currentTime.toLocaleTimeString()}</span>
    </div>
  )

  // Render segment by type
  const renderSegment = (segment: SegmentConfig) => {
    switch (segment.id) {
      case 'path': return <PathSegment key="path" />
      case 'git': return <GitSegment key="git" />
      case 'claude': return <ClaudeSegment key="claude" />
      case 'agents': return <AgentsSegment key="agents" />
      case 'system': return <SystemSegment key="system" />
      case 'connection': return <ConnectionSegment key="connection" />
      case 'time': return <TimeSegment key="time" />
      default: return null
    }
  }

  // Expanded Detail Modal
  const ExpandedDetail = () => {
    if (!expandedSegment) return null
    
    const handleClose = () => setExpandedSegment(null)
    
    return (
      <div className="statusline-modal-overlay" onClick={handleClose}>
        <div className="statusline-modal" onClick={e => e.stopPropagation()}>
          <div className="modal-header">
            <h3>{expandedSegment.charAt(0).toUpperCase() + expandedSegment.slice(1)} Details</h3>
            <button onClick={handleClose} className="close-button">
              <X size={16} />
            </button>
          </div>
          <div className="modal-content">
            {expandedSegment === 'git' && gitStatus && (
              <div className="git-details">
                <div className="detail-row">
                  <span>Branch:</span>
                  <span>{gitStatus.branch}</span>
                </div>
                <div className="detail-row">
                  <span>Status:</span>
                  <span style={{ color: getStatusColor(gitStatus.status) }}>
                    {gitStatus.status}
                  </span>
                </div>
                <div className="detail-row">
                  <span>Changes:</span>
                  <span>{gitStatus.dirty ? 'Uncommitted changes' : 'Clean'}</span>
                </div>
                {gitStatus.lastCommit && (
                  <div className="last-commit">
                    <h4>Last Commit</h4>
                    <div className="commit-info">
                      <div>{gitStatus.lastCommit.message}</div>
                      <div className="commit-meta">
                        {gitStatus.lastCommit.author} • {gitStatus.lastCommit.time.toLocaleString()}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {expandedSegment === 'claude' && claudeSession && (
              <div className="claude-details">
                <div className="detail-row">
                  <span>Model:</span>
                  <span>{claudeSession.model}</span>
                </div>
                <div className="detail-row">
                  <span>Session Duration:</span>
                  <span>{Math.floor(claudeSession.duration / 60)}m {claudeSession.duration % 60}s</span>
                </div>
                <div className="detail-row">
                  <span>Tokens Used:</span>
                  <span>{claudeSession.tokens.used.toLocaleString()} / {claudeSession.tokens.limit.toLocaleString()}</span>
                </div>
                <div className="detail-row">
                  <span>Cost:</span>
                  <span>${claudeSession.tokens.cost.toFixed(4)}</span>
                </div>
                <div className="detail-row">
                  <span>Quality:</span>
                  <span style={{ color: getStatusColor(claudeSession.quality) }}>
                    {claudeSession.quality}
                  </span>
                </div>
              </div>
            )}
            
            {expandedSegment === 'agents' && (
              <div className="agents-details">
                <div className="agents-grid">
                  {agents.map(agent => (
                    <div key={agent.id} className="agent-card">
                      <div className="agent-header">
                        <span className="agent-name">{agent.name}</span>
                        <span 
                          className="agent-status"
                          style={{ color: getStatusColor(agent.status) }}
                        >
                          {agent.status}
                        </span>
                      </div>
                      {agent.progress !== undefined && (
                        <div className="agent-progress">
                          <div 
                            className="progress-bar"
                            style={{ width: `${agent.progress}%` }}
                          />
                        </div>
                      )}
                      {agent.lastAction && (
                        <div className="agent-action">{agent.lastAction}</div>
                      )}
                      <div className="agent-performance">
                        Performance: {agent.performance}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {expandedSegment === 'system' && systemMetrics && (
              <div className="system-details">
                <div className="metrics-grid">
                  <div className="metric-card">
                    <h4>CPU</h4>
                    <div className="metric-value">{systemMetrics.cpu.usage}%</div>
                    <div className="metric-info">{systemMetrics.cpu.cores} cores</div>
                    {systemMetrics.cpu.temperature && (
                      <div className="metric-temp">{systemMetrics.cpu.temperature}°C</div>
                    )}
                  </div>
                  
                  <div className="metric-card">
                    <h4>Memory</h4>
                    <div className="metric-value">{systemMetrics.memory.percentage}%</div>
                    <div className="metric-info">
                      {(systemMetrics.memory.used / 1024 / 1024 / 1024).toFixed(1)}GB / 
                      {(systemMetrics.memory.total / 1024 / 1024 / 1024).toFixed(1)}GB
                    </div>
                  </div>
                  
                  <div className="metric-card">
                    <h4>Disk</h4>
                    <div className="metric-value">{systemMetrics.disk.percentage}%</div>
                    <div className="metric-info">
                      {(systemMetrics.disk.used / 1024 / 1024 / 1024).toFixed(1)}GB / 
                      {(systemMetrics.disk.total / 1024 / 1024 / 1024).toFixed(1)}GB
                    </div>
                  </div>
                  
                  <div className="metric-card">
                    <h4>Network</h4>
                    <div className="metric-value">{systemMetrics.network.latency}ms</div>
                    <div className="metric-info">
                      ↑{(systemMetrics.network.up / 1024).toFixed(1)}KB/s 
                      ↓{(systemMetrics.network.down / 1024).toFixed(1)}KB/s
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Notifications
  const NotificationList = () => (
    <div className="statusline-notifications">
      {notifications.map(notification => (
        <div 
          key={notification.id}
          className={`notification notification-${notification.type}`}
          style={{ borderLeftColor: config.colors[notification.type] }}
        >
          <span className="notification-message">{notification.message}</span>
          <button 
            onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
            className="notification-close"
          >
            <X size={12} />
          </button>
        </div>
      ))}
    </div>
  )

  return (
    <div className={`statusline-v2 theme-${config.theme}`}>
      {/* Main Statusline */}
      <div className="statusline-main">
        <div className="statusline-segments">
          {visibleSegments.map(renderSegment)}
        </div>
        
        {/* Configuration Button */}
        <button 
          className="config-button"
          onClick={() => setShowConfig(!showConfig)}
          title="Configure statusline"
        >
          <Settings size={14} />
        </button>
      </div>

      {/* Notifications */}
      <NotificationList />

      {/* Expanded Detail Modal */}
      <ExpandedDetail />

      {/* Configuration Panel */}
      {showConfig && (
        <div className="statusline-config">
          <div className="config-header">
            <h3>Statusline Configuration</h3>
            <button onClick={() => setShowConfig(false)}>
              <X size={16} />
            </button>
          </div>
          
          <div className="config-content">
            <div className="config-section">
              <label>Theme</label>
              <select 
                value={config.theme}
                onChange={e => handleConfigChange({ theme: e.target.value as any })}
              >
                <option value="powerline">Powerline</option>
                <option value="minimal">Minimal</option>
                <option value="classic">Classic</option>
                <option value="compact">Compact</option>
              </select>
            </div>
            
            <div className="config-section">
              <label>Update Interval (ms)</label>
              <input 
                type="number"
                min="50"
                max="5000"
                value={config.updateInterval}
                onChange={e => handleConfigChange({ updateInterval: parseInt(e.target.value) })}
              />
            </div>
            
            <div className="config-section">
              <label>Segments</label>
              <div className="segments-config">
                {config.segments.map(segment => (
                  <div key={segment.id} className="segment-config">
                    <input 
                      type="checkbox"
                      checked={segment.enabled}
                      onChange={e => {
                        const updatedSegments = config.segments.map(s => 
                          s.id === segment.id ? { ...s, enabled: e.target.checked } : s
                        )
                        handleConfigChange({ segments: updatedSegments })
                      }}
                    />
                    <span>{segment.id}</span>
                    <input 
                      type="number"
                      min="1"
                      max="10"
                      value={segment.priority}
                      onChange={e => {
                        const updatedSegments = config.segments.map(s => 
                          s.id === segment.id ? { ...s, priority: parseInt(e.target.value) } : s
                        )
                        handleConfigChange({ segments: updatedSegments })
                      }}
                      title="Priority"
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default StatuslineV2