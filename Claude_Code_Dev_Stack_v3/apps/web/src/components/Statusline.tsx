import React, { useEffect, useState } from 'react'
import { GitBranch, DollarSign, Cpu, Volume2, Zap, Settings, WifiOff, Wifi } from 'lucide-react'
import './Statusline.css'

// Ultimate Statusline Component
// Combines:
// - Claude Powerline (@Owloops) metrics
// - Dev Stack monitoring (original work)
// Real-time updates every 100ms

interface StatuslineProps {
  agents: { active: number; total: number }
  tasks: { completed: number; total: number }
  hooks: { triggered: number; total: number }
  lastAudio: string
  isConnected: boolean
}

export const Statusline: React.FC<StatuslineProps> = ({
  agents,
  tasks,
  hooks,
  lastAudio,
  isConnected
}) => {
  const [powerlineData, setPowerlineData] = useState({
    directory: 'Claude_Code_Dev_Stack_v3',
    branch: 'main',
    model: 'claude-3-opus',
    sessionCost: 0.45,
    todayCost: 2.35,
    contextUsage: 45
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
        </div>
        
        <div className="segment model">
          <Cpu size={14} />
          <span className="value">{powerlineData.model}</span>
        </div>
        
        <div className={`segment cost ${getCostColor(powerlineData.sessionCost, 10)}`}>
          <DollarSign size={14} />
          <span className="value">Session: ${powerlineData.sessionCost.toFixed(2)}</span>
        </div>
        
        <div className={`segment cost ${getCostColor(powerlineData.todayCost, 25)}`}>
          <DollarSign size={14} />
          <span className="value">Today: ${powerlineData.todayCost.toFixed(2)}</span>
        </div>
        
        <div className="segment context">
          <span className="value">{powerlineData.contextUsage}k tokens</span>
        </div>
      </div>

      {/* Line 2: Dev Stack Monitoring (Agents, Tasks, Hooks, Audio) */}
      <div className="statusline-row devstack">
        <div className="segment agents">
          <span className="icon">🤖</span>
          <span className={`value ${agents.active > 0 ? 'text-green-500' : 'text-gray-500'}`}>
            {agents.active}/{agents.total}
          </span>
        </div>
        
        <div className="segment tasks">
          <Zap size={14} />
          <span className={`value ${getProgressColor(tasks.completed, tasks.total)}`}>
            {tasks.completed}/{tasks.total}
          </span>
        </div>
        
        <div className="segment hooks">
          <Settings size={14} />
          <span className={`value ${hooks.triggered > 0 ? 'text-purple-500' : 'text-gray-500'}`}>
            {hooks.triggered}/{hooks.total}
          </span>
        </div>
        
        <div className="segment audio">
          <Volume2 size={14} />
          <span className="value">
            {lastAudio || 'Silent'}
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