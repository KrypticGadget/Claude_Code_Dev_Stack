import React, { useEffect, useState } from 'react'
import { GitBranch, DollarSign, Cpu, Volume2, Zap, Settings, WifiOff, Wifi, AlertTriangle } from 'lucide-react'
import './Statusline.css'

// Ultimate Statusline Component
// Combines:
// - Claude Powerline (@Owloops) metrics
// - Dev Stack monitoring (original work)
// Real-time updates every 100ms
// Enhanced with integrated statusline backend

interface StatuslineProps {
  agents: { active: number; total: number; status?: string }
  tasks: { completed: number; total: number; active?: number; status?: string }
  hooks: { triggered: number; total: number; errors?: number; status?: string }
  lastAudio: string
  isConnected: boolean
  // Enhanced props for integrated statusline
  audioStatus?: { enabled: boolean; volume: number; queue: number; status: string }
  gitInfo?: { branch: string; dirty: boolean; ahead: number; behind: number }
  costInfo?: { session: number; today: number; budget: number }
  modelInfo?: { id: string; displayName: string }
}

export const Statusline: React.FC<StatuslineProps> = ({
  agents,
  tasks,
  hooks,
  lastAudio,
  isConnected,
  audioStatus,
  gitInfo,
  costInfo,
  modelInfo
}) => {
  // Use enhanced data or fallback to defaults
  const currentBranch = gitInfo?.branch || 'main'
  const currentModel = modelInfo?.displayName || 'claude-3-opus'
  const sessionCost = costInfo?.session || 0.45
  const todayCost = costInfo?.today || 2.35
  const budgetLimit = costInfo?.budget || 25
  const contextUsage = 45 // TODO: Get from context info
  
  const [powerlineData, setPowerlineData] = useState({
    directory: 'Claude_Code_Dev_Stack_v3',
    branch: currentBranch,
    model: currentModel,
    sessionCost,
    todayCost,
    contextUsage
  })

  // Update timestamp for 100ms real-time indication
  const [updateTime, setUpdateTime] = useState(Date.now())

  useEffect(() => {
    const interval = setInterval(() => {
      setUpdateTime(Date.now())
    }, 100)
    return () => clearInterval(interval)
  }, [])

  const getProgressColor = (completed: number, total: number) => {
    if (total === 0) return 'text-gray-500'
    const percentage = (completed / total) * 100
    if (percentage >= 80) return 'text-green-500'
    if (percentage >= 50) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getCostColor = (cost: number, limit: number) => {
    const percentage = (cost / limit) * 100
    if (percentage >= 80) return 'text-red-500'
    if (percentage >= 60) return 'text-yellow-500'
    return 'text-green-500'
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'active': return 'text-green-500'
      case 'error': return 'text-red-500'
      case 'idle': 
      default: return 'text-gray-500'
    }
  }

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'active': return '●'
      case 'error': return '⚠'
      case 'idle':
      default: return '○'
    }
  }

  return (
    <div className="statusline">
      {/* Line 1: Powerline-style (Directory, Git, Model, Costs) */}
      <div className="statusline-row powerline">
        <div className="segment directory">
          <span className="icon">📁</span>
          <span className="value">{powerlineData.directory}</span>
        </div>
        
        <div className="segment git">
          <GitBranch size={14} />
          <span className="value">{powerlineData.branch}</span>
          {gitInfo?.dirty && <span className="status-indicator text-yellow-500">●</span>}
          {gitInfo && (gitInfo.ahead > 0 || gitInfo.behind > 0) && (
            <span className="status-indicator text-blue-500">
              {gitInfo.ahead > 0 && `↑${gitInfo.ahead}`}
              {gitInfo.behind > 0 && `↓${gitInfo.behind}`}
            </span>
          )}
        </div>
        
        <div className="segment model">
          <Cpu size={14} />
          <span className="value">{powerlineData.model}</span>
        </div>
        
        <div className={`segment cost ${getCostColor(sessionCost, budgetLimit * 0.4)}`}>
          <DollarSign size={14} />
          <span className="value">Session: ${sessionCost.toFixed(2)}</span>
        </div>
        
        <div className={`segment cost ${getCostColor(todayCost, budgetLimit)}`}>
          <DollarSign size={14} />
          <span className="value">Today: ${todayCost.toFixed(2)}/${budgetLimit}</span>
        </div>
        
        <div className="segment context">
          <span className="value">{powerlineData.contextUsage}k tokens</span>
        </div>
      </div>

      {/* Line 2: Dev Stack Monitoring (Agents, Tasks, Hooks, Audio) */}
      <div className="statusline-row devstack">
        <div className="segment agents">
          <span className="icon">🤖</span>
          <span className={`value ${getStatusColor(agents.status)}`}>
            {agents.active}/{agents.total}
          </span>
          <span className={`status-indicator ${getStatusColor(agents.status)}`}>
            {getStatusIcon(agents.status)}
          </span>
        </div>
        
        <div className="segment tasks">
          <Zap size={14} />
          <span className={`value ${getStatusColor(tasks.status)}`}>
            {tasks.active || 0}/{tasks.total} ({tasks.completed || 0} done)
          </span>
          <span className={`status-indicator ${getStatusColor(tasks.status)}`}>
            {getStatusIcon(tasks.status)}
          </span>
        </div>
        
        <div className="segment hooks">
          <Settings size={14} />
          <span className={`value ${getStatusColor(hooks.status)}`}>
            {hooks.triggered}/{hooks.total}
          </span>
          {hooks.errors && hooks.errors > 0 && (
            <span className="status-indicator text-red-500">
              <AlertTriangle size={12} />
              {hooks.errors}
            </span>
          )}
          <span className={`status-indicator ${getStatusColor(hooks.status)}`}>
            {getStatusIcon(hooks.status)}
          </span>
        </div>
        
        <div className="segment audio">
          <Volume2 size={14} />
          <span className={`value ${getStatusColor(audioStatus?.status)}`}>
            {audioStatus?.enabled ? `${audioStatus.volume}%` : 'Off'}
            {audioStatus?.queue && audioStatus.queue > 0 && ` (Q:${audioStatus.queue})`}
          </span>
          <span className={`status-indicator ${getStatusColor(audioStatus?.status)}`}>
            {audioStatus?.enabled ? '🔊' : '🔇'}
          </span>
        </div>
        
        <div className="segment connection">
          {isConnected ? (
            <>
              <Wifi size={14} className="text-green-500" />
              <span className="value text-green-500">100ms</span>
            </>
          ) : (
            <>
              <WifiOff size={14} className="text-red-500" />
              <span className="value text-red-500">Offline</span>
            </>
          )}
        </div>
        
        <div className="segment timestamp">
          <span className="value text-gray-400">
            {new Date(updateTime).toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  )
}