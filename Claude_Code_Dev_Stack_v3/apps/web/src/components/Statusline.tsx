import React, { useEffect, useState, useCallback } from 'react'
import { GitBranch, DollarSign, Cpu, Volume2, Zap, Settings, WifiOff, Wifi, AlertTriangle, Activity, Clock, Server } from 'lucide-react'
import './Statusline.css'

// Ultimate Statusline Component v3.0 - PERFORMANCE OPTIMIZED
// 
// Integrates with Ultimate Statusline Manager for real-time updates
// Combines:
// - Claude Powerline (@Owloops) metrics: Cost/Git/Model tracking
// - Dev Stack monitoring (Zach): Agent/Task/Hook orchestration
// - Performance monitoring: 100ms real-time updates
// - WebSocket integration for instant updates
// 
// Attribution:
// - Powerline by @Owloops: https://github.com/owloops/claude-powerline
// - Dev Stack orchestration by Zach
// - Ultimate integration for Claude Code v3.0

// Interface matching Ultimate Statusline Manager output
interface UltimateStatuslineData {
  powerline: {
    directory: string;
    git: {
      branch: string;
      dirty: boolean;
      ahead: number;
      behind: number;
      stash: number;
      operation?: string;
      upstreamBranch?: string;
    };
    model: {
      id: string;
      displayName: string;
      provider?: string;
      version?: string;
    };
    cost: {
      session: number;
      today: number;
      budget: number;
      remaining: number;
      percentage: number;
    };
    context: {
      tokens: number;
      maxTokens: number;
      percentage: number;
    };
    performance: {
      responseTime: number;
      throughput: number;
      avgResponseTime: number;
    };
  };
  devStack: {
    agents: {
      active: number;
      total: number;
      status: 'idle' | 'working' | 'error';
      byType: { [key: string]: number };
      performance: {
        avgResponseTime: number;
        successRate: number;
        errorCount: number;
      };
    };
    tasks: {
      active: number;
      completed: number;
      total: number;
      queued: number;
      failed: number;
      status: 'none' | 'running' | 'complete' | 'error';
      performance: {
        avgExecutionTime: number;
        throughput: number;
        queueDepth: number;
      };
    };
    hooks: {
      triggered: number;
      total: number;
      errors: number;
      active: number;
      status: 'ready' | 'busy' | 'error';
      performance: {
        avgLatency: number;
        successRate: number;
        concurrentHooks: number;
      };
    };
    audio: {
      enabled: boolean;
      volume: number;
      lastEvent: string;
      status: 'silent' | 'playing' | 'error';
      queue: number;
      performance: {
        latency: number;
        queuedEvents: number;
        eventRate: number;
      };
    };
    system: {
      cpu: number;
      memory: number;
      disk: number;
      network: {
        bytesIn: number;
        bytesOut: number;
        latency: number;
      };
    };
  };
  performance: {
    updateLatency: number;
    dataCollectionTime: number;
    renderTime: number;
    wsLatency: number;
    memoryUsage: number;
    cpuUsage: number;
  };
  timestamp: number;
  updateId: string;
  connectionId?: string;
}

interface StatuslineProps {
  // Legacy props for backward compatibility
  agents?: { active: number; total: number; status?: string }
  tasks?: { completed: number; total: number; active?: number; status?: string }
  hooks?: { triggered: number; total: number; errors?: number; status?: string }
  lastAudio?: string
  isConnected?: boolean
  
  // Enhanced Ultimate Statusline integration
  enableWebSocket?: boolean
  wsUrl?: string
  theme?: 'light' | 'dark' | 'tokyo-night' | 'nord'
  showPerformanceMetrics?: boolean
  compactMode?: boolean
}

export const Statusline: React.FC<StatuslineProps> = ({
  // Legacy props (backward compatibility)
  agents,
  tasks,
  hooks,
  lastAudio,
  isConnected: legacyIsConnected,
  
  // Enhanced props
  enableWebSocket = true,
  wsUrl = 'ws://localhost:8087',
  theme = 'tokyo-night',
  showPerformanceMetrics = true,
  compactMode = false
}) => {
  // Ultimate Statusline state
  const [statuslineData, setStatuslineData] = useState<UltimateStatuslineData | null>(null)
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const [lastUpdateTime, setLastUpdateTime] = useState<number>(0)
  const [renderStartTime, setRenderStartTime] = useState<number>(0)

  // Connection management
  const connectWebSocket = useCallback(() => {
    if (!enableWebSocket) return

    try {
      setConnectionStatus('connecting')
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('🔗 Ultimate Statusline WebSocket connected')
        setConnectionStatus('connected')
        setWsConnection(ws)
        
        // Request initial data
        ws.send(JSON.stringify({ type: 'request_update' }))
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          
          if (message.type === 'statusline_update' || message.type === 'statusline_initial') {
            const data = message.data as UltimateStatuslineData
            setStatuslineData(data)
            setLastUpdateTime(Date.now())
            
            // Update render performance metric
            if (data.performance && renderStartTime > 0) {
              data.performance.renderTime = Date.now() - renderStartTime
            }
          }
        } catch (error) {
          console.error('Error parsing statusline message:', error)
        }
      }

      ws.onclose = () => {
        console.log('🔌 Ultimate Statusline WebSocket disconnected')
        setConnectionStatus('disconnected')
        setWsConnection(null)
        
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000)
      }

      ws.onerror = (error) => {
        console.error('🚨 Ultimate Statusline WebSocket error:', error)
        setConnectionStatus('disconnected')
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionStatus('disconnected')
    }
  }, [enableWebSocket, wsUrl])

  // Connect WebSocket on mount
  useEffect(() => {
    connectWebSocket()
    
    return () => {
      if (wsConnection) {
        wsConnection.close()
      }
    }
  }, [connectWebSocket])

  // Track render performance
  useEffect(() => {
    setRenderStartTime(Date.now())
  })

  // Fallback to legacy props if no WebSocket data
  const isConnected = connectionStatus === 'connected'
  const effectiveData = statuslineData || createFallbackData()

  // Helper function to create fallback data when WebSocket is not available
  function createFallbackData(): UltimateStatuslineData {
    return {
      powerline: {
        directory: 'Claude_Code_Dev_Stack_v3',
        git: {
          branch: 'main',
          dirty: false,
          ahead: 0,
          behind: 0,
          stash: 0,
        },
        model: {
          id: 'claude-3-5-sonnet',
          displayName: 'Claude 3.5 Sonnet',
          provider: 'Anthropic',
        },
        cost: {
          session: agents ? 2.45 : 0,
          today: agents ? 8.32 : 0,
          budget: 25.00,
          remaining: 16.68,
          percentage: 33.28,
        },
        context: {
          tokens: 45000,
          maxTokens: 200000,
          percentage: 22.5,
        },
        performance: {
          responseTime: 0,
          throughput: 0,
          avgResponseTime: 0,
        },
      },
      devStack: {
        agents: {
          active: agents?.active || 0,
          total: agents?.total || 28,
          status: (agents?.status as any) || 'idle',
          byType: {},
          performance: {
            avgResponseTime: 0,
            successRate: 100,
            errorCount: 0,
          },
        },
        tasks: {
          active: tasks?.active || 0,
          completed: tasks?.completed || 0,
          total: tasks?.total || 0,
          queued: 0,
          failed: 0,
          status: (tasks?.status as any) || 'none',
          performance: {
            avgExecutionTime: 0,
            throughput: 0,
            queueDepth: 0,
          },
        },
        hooks: {
          triggered: hooks?.triggered || 0,
          total: hooks?.total || 28,
          errors: hooks?.errors || 0,
          active: 0,
          status: (hooks?.status as any) || 'ready',
          performance: {
            avgLatency: 0,
            successRate: 100,
            concurrentHooks: 0,
          },
        },
        audio: {
          enabled: lastAudio !== 'none',
          volume: 0.5,
          lastEvent: lastAudio || 'none',
          status: 'silent',
          queue: 0,
          performance: {
            latency: 0,
            queuedEvents: 0,
            eventRate: 0,
          },
        },
        system: {
          cpu: 0,
          memory: 0,
          disk: 0,
          network: {
            bytesIn: 0,
            bytesOut: 0,
            latency: 0,
          },
        },
      },
      performance: {
        updateLatency: 0,
        dataCollectionTime: 0,
        renderTime: 0,
        wsLatency: 0,
        memoryUsage: 0,
        cpuUsage: 0,
      },
      timestamp: Date.now(),
      updateId: 'fallback',
    }
  }

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working':
      case 'running':
      case 'busy':
        return 'text-green-500'
      case 'error':
        return 'text-red-500'
      case 'playing':
        return 'text-blue-500'
      case 'idle':
      case 'ready':
      case 'silent':
      case 'none':
      default:
        return 'text-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'working':
      case 'running':
      case 'busy':
        return '●'
      case 'error':
        return '⚠'
      case 'playing':
        return '▶'
      case 'idle':
      case 'ready':
      case 'silent':
      case 'none':
      default:
        return '○'
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  return (
    <div className={`statusline statusline-theme-${theme} ${compactMode ? 'compact' : ''}`}>
      {/* Line 1: Powerline-style (@Owloops) - Directory, Git, Model, Costs */}
      <div className="statusline-row powerline">
        <div className="segment directory">
          <span className="icon">📁</span>
          <span className="value">{effectiveData.powerline.directory}</span>
        </div>
        
        <div className="segment git">
          <GitBranch size={14} />
          <span className="value">{effectiveData.powerline.git.branch}</span>
          {effectiveData.powerline.git.dirty && <span className="status-indicator text-yellow-500">●</span>}
          {(effectiveData.powerline.git.ahead > 0 || effectiveData.powerline.git.behind > 0) && (
            <span className="status-indicator text-blue-500">
              {effectiveData.powerline.git.ahead > 0 && `↑${effectiveData.powerline.git.ahead}`}
              {effectiveData.powerline.git.behind > 0 && `↓${effectiveData.powerline.git.behind}`}
            </span>
          )}
          {effectiveData.powerline.git.stash > 0 && (
            <span className="status-indicator text-purple-500">⧇{effectiveData.powerline.git.stash}</span>
          )}
        </div>
        
        <div className="segment model">
          <Cpu size={14} />
          <span className="value">{effectiveData.powerline.model.displayName}</span>
          {effectiveData.powerline.model.provider && (
            <span className="provider text-xs text-gray-400">({effectiveData.powerline.model.provider})</span>
          )}
        </div>
        
        <div className={`segment cost ${getCostColor(effectiveData.powerline.cost.session, effectiveData.powerline.cost.budget * 0.4)}`}>
          <DollarSign size={14} />
          <span className="value">Session: ${effectiveData.powerline.cost.session.toFixed(2)}</span>
        </div>
        
        <div className={`segment cost ${getCostColor(effectiveData.powerline.cost.today, effectiveData.powerline.cost.budget)}`}>
          <DollarSign size={14} />
          <span className="value">Today: ${effectiveData.powerline.cost.today.toFixed(2)}/${effectiveData.powerline.cost.budget}</span>
          <div className="progress-bar mini">
            <div 
              className="progress-fill" 
              style={{ width: `${effectiveData.powerline.cost.percentage}%` }}
            ></div>
          </div>
        </div>
        
        <div className="segment context">
          <Activity size={14} />
          <span className="value">{(effectiveData.powerline.context.tokens / 1000).toFixed(1)}k tokens</span>
          <div className="progress-bar mini">
            <div 
              className="progress-fill" 
              style={{ width: `${effectiveData.powerline.context.percentage}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Line 2: Dev Stack Monitoring (Zach) - Agents, Tasks, Hooks, Audio */}
      <div className="statusline-row devstack">
        <div className="segment agents">
          <span className="icon">🤖</span>
          <span className={`value ${getStatusColor(effectiveData.devStack.agents.status)}`}>
            {effectiveData.devStack.agents.active}/{effectiveData.devStack.agents.total}
          </span>
          <span className={`status-indicator ${getStatusColor(effectiveData.devStack.agents.status)}`}>
            {getStatusIcon(effectiveData.devStack.agents.status)}
          </span>
          {effectiveData.devStack.agents.performance.errorCount > 0 && (
            <span className="error-count text-red-500">⚠{effectiveData.devStack.agents.performance.errorCount}</span>
          )}
        </div>
        
        <div className="segment tasks">
          <Zap size={14} />
          <span className={`value ${getStatusColor(effectiveData.devStack.tasks.status)}`}>
            {effectiveData.devStack.tasks.active}/{effectiveData.devStack.tasks.total} 
            ({effectiveData.devStack.tasks.completed} done)
          </span>
          {effectiveData.devStack.tasks.queued > 0 && (
            <span className="queue-indicator text-orange-500">Q:{effectiveData.devStack.tasks.queued}</span>
          )}
          <span className={`status-indicator ${getStatusColor(effectiveData.devStack.tasks.status)}`}>
            {getStatusIcon(effectiveData.devStack.tasks.status)}
          </span>
        </div>
        
        <div className="segment hooks">
          <Settings size={14} />
          <span className={`value ${getStatusColor(effectiveData.devStack.hooks.status)}`}>
            {effectiveData.devStack.hooks.triggered}/{effectiveData.devStack.hooks.total}
          </span>
          {effectiveData.devStack.hooks.errors > 0 && (
            <span className="status-indicator text-red-500">
              <AlertTriangle size={12} />
              {effectiveData.devStack.hooks.errors}
            </span>
          )}
          <span className={`status-indicator ${getStatusColor(effectiveData.devStack.hooks.status)}`}>
            {getStatusIcon(effectiveData.devStack.hooks.status)}
          </span>
        </div>
        
        <div className="segment audio">
          <Volume2 size={14} />
          <span className={`value ${getStatusColor(effectiveData.devStack.audio.status)}`}>
            {effectiveData.devStack.audio.enabled ? `${Math.round(effectiveData.devStack.audio.volume * 100)}%` : 'Off'}
            {effectiveData.devStack.audio.queue > 0 && ` (Q:${effectiveData.devStack.audio.queue})`}
          </span>
          <span className={`status-indicator ${getStatusColor(effectiveData.devStack.audio.status)}`}>
            {effectiveData.devStack.audio.enabled ? '🔊' : '🔇'}
          </span>
          <span className="last-event text-xs text-gray-400">{effectiveData.devStack.audio.lastEvent}</span>
        </div>
        
        <div className="segment system">
          <Server size={14} />
          <span className="value text-gray-600">
            CPU:{effectiveData.devStack.system.cpu.toFixed(1)}% 
            MEM:{effectiveData.devStack.system.memory.toFixed(1)}%
          </span>
        </div>
        
        <div className="segment connection">
          {isConnected ? (
            <>
              <Wifi size={14} className="text-green-500" />
              <span className="value text-green-500">{effectiveData.performance.updateLatency}ms</span>
            </>
          ) : (
            <>
              <WifiOff size={14} className="text-red-500" />
              <span className="value text-red-500">{connectionStatus}</span>
            </>
          )}
        </div>
        
        <div className="segment timestamp">
          <Clock size={14} />
          <span className="value text-gray-400">
            {new Date(effectiveData.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Performance Metrics Row (Optional) */}
      {showPerformanceMetrics && (
        <div className="statusline-row performance">
          <div className="segment perf-update">
            <Activity size={12} />
            <span className="label">Update:</span>
            <span className="value">{effectiveData.performance.updateLatency}ms</span>
          </div>
          
          <div className="segment perf-data">
            <span className="label">Data:</span>
            <span className="value">{effectiveData.performance.dataCollectionTime}ms</span>
          </div>
          
          <div className="segment perf-render">
            <span className="label">Render:</span>
            <span className="value">{effectiveData.performance.renderTime}ms</span>
          </div>
          
          <div className="segment perf-memory">
            <span className="label">Memory:</span>
            <span className="value">{formatBytes(effectiveData.performance.memoryUsage * 1024 * 1024)}</span>
          </div>
          
          <div className="segment update-id">
            <span className="label">ID:</span>
            <span className="value text-xs font-mono">{effectiveData.updateId.slice(-8)}</span>
          </div>
          
          <div className="segment attribution">
            <span className="value text-xs text-gray-500">
              @Owloops/claude-powerline + Dev Stack v3.0 by Zach
            </span>
          </div>
        </div>
      )}
    </div>
  )
}