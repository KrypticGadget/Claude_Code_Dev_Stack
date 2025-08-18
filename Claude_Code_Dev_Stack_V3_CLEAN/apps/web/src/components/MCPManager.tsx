import React, { useState, useEffect, useCallback } from 'react'
import { Settings, Server, Play, Square, RotateCcw, CheckCircle, XCircle, AlertTriangle, Wifi, WifiOff, RefreshCw } from 'lucide-react'

interface MCPService {
  id: string
  name: string
  type: string
  status: 'running' | 'stopped' | 'error' | 'starting' | 'unknown'
  description: string
  host: string
  port: number
  url: string
  version: string
  is_healthy: boolean
  metrics: {
    requests_total: number
    error_count: number
    response_time_avg: number
    cpu_usage: number
    memory_usage: number
    uptime: number
  }
  last_seen?: string
  tags: string[]
}

interface MCPManagerStatus {
  total_services: number
  status_breakdown: Record<string, number>
  healthy_services: number
  service_types: string[]
}

interface MCPManagerConfig {
  health_check_interval: number
  load_balancing: {
    default_algorithm: string
    health_check_timeout: number
  }
  logging: {
    level: string
    file: string
  }
}

// MCP Manager API configuration
const MCP_API_BASE = process.env.NEXT_PUBLIC_MCP_API_URL || 'http://localhost:8000'

export const MCPManager: React.FC = () => {
  const [services, setServices] = useState<MCPService[]>([])
  const [status, setStatus] = useState<MCPManagerStatus | null>(null)
  const [config, setConfig] = useState<MCPManagerConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null)

  // API functions
  const fetchServices = useCallback(async () => {
    try {
      const response = await fetch(`${MCP_API_BASE}/mcp/services`)
      if (!response.ok) throw new Error('Failed to fetch services')
      const data = await response.json()
      setServices(data.services || [])
      setIsConnected(true)
      setError(null)
      setLastUpdated(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch services')
      setIsConnected(false)
    }
  }, [])

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`${MCP_API_BASE}/mcp/status`)
      if (!response.ok) throw new Error('Failed to fetch status')
      const data = await response.json()
      setStatus(data)
    } catch (err) {
      console.error('Failed to fetch status:', err)
    }
  }, [])

  const fetchConfig = useCallback(async () => {
    try {
      const response = await fetch(`${MCP_API_BASE}/mcp/config`)
      if (!response.ok) throw new Error('Failed to fetch config')
      const data = await response.json()
      setConfig(data)
    } catch (err) {
      console.error('Failed to fetch config:', err)
    }
  }, [])

  const performServiceAction = async (serviceId: string, action: 'start' | 'stop' | 'restart') => {
    try {
      setServices(prev => prev.map(service => 
        service.id === serviceId 
          ? { ...service, status: action === 'stop' ? 'stopped' : 'starting' }
          : service
      ))

      const response = await fetch(`${MCP_API_BASE}/mcp/services/${serviceId}/actions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      })

      if (!response.ok) throw new Error(`Failed to ${action} service`)

      // Refresh services after action
      setTimeout(fetchServices, 1000)
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to ${action} service`)
      fetchServices() // Refresh to get correct state
    }
  }

  const discoverServices = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${MCP_API_BASE}/mcp/discover`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('Failed to discover services')
      setTimeout(() => {
        fetchServices()
        fetchStatus()
      }, 1000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to discover services')
    } finally {
      setLoading(false)
    }
  }

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback(() => {
    if (wsConnection) return

    try {
      const ws = new WebSocket(`${MCP_API_BASE.replace('http', 'ws')}/mcp/ws`)
      
      ws.onopen = () => {
        console.log('MCP WebSocket connected')
        setIsConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          switch (data.type) {
            case 'initial_status':
              setStatus(data.status)
              break
            case 'service_registered':
            case 'service_unregistered':
            case 'service_action':
              fetchServices()
              fetchStatus()
              break
            case 'config_updated':
              setConfig(data.config)
              break
            case 'services_discovered':
              fetchServices()
              fetchStatus()
              break
          }
          
          setLastUpdated(new Date())
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onclose = () => {
        console.log('MCP WebSocket disconnected')
        setIsConnected(false)
        setWsConnection(null)
        // Attempt reconnection after 5 seconds
        setTimeout(connectWebSocket, 5000)
      }

      ws.onerror = (error) => {
        console.error('MCP WebSocket error:', error)
        setIsConnected(false)
      }

      setWsConnection(ws)
    } catch (err) {
      console.error('Failed to connect WebSocket:', err)
      setIsConnected(false)
    }
  }, [wsConnection, fetchServices, fetchStatus])

  // Initial data loading
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await Promise.all([
        fetchServices(),
        fetchStatus(),
        fetchConfig()
      ])
      setLoading(false)
    }

    loadData()
    connectWebSocket()

    // Cleanup on unmount
    return () => {
      if (wsConnection) {
        wsConnection.close()
      }
    }
  }, [fetchServices, fetchStatus, fetchConfig, connectWebSocket])

  // Periodic refresh fallback
  useEffect(() => {
    const interval = setInterval(() => {
      if (!isConnected) {
        fetchServices()
        fetchStatus()
      }
    }, 30000) // 30 seconds

    return () => clearInterval(interval)
  }, [isConnected, fetchServices, fetchStatus])

  const formatUptime = (seconds: number): string => {
    if (seconds < 60) return `${Math.floor(seconds)}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
    return `${Math.floor(seconds / 86400)}d ${Math.floor((seconds % 86400) / 3600)}h`
  }

  const getServiceTypeColor = (type: string): string => {
    switch (type) {
      case 'playwright': return 'bg-purple-100 text-purple-700'
      case 'github': return 'bg-blue-100 text-blue-700'
      case 'websearch': return 'bg-green-100 text-green-700'
      case 'proxy': return 'bg-orange-100 text-orange-700'
      case 'gateway': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircle size={16} className="text-green-500" />
      case 'stopped':
        return <Square size={16} className="text-gray-500" />
      case 'error':
        return <XCircle size={16} className="text-red-500" />
      case 'starting':
        return <AlertTriangle size={16} className="text-yellow-500" />
      case 'unknown':
        return <AlertTriangle size={16} className="text-gray-400" />
      default:
        return <Square size={16} className="text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-green-500'
      case 'stopped':
        return 'text-gray-500'
      case 'error':
        return 'text-red-500'
      case 'starting':
        return 'text-yellow-500'
      case 'unknown':
        return 'text-gray-400'
      default:
        return 'text-gray-500'
    }
  }

  // Calculate summary statistics
  const runningServices = services.filter(s => s.status === 'running').length
  const errorServices = services.filter(s => s.status === 'error').length
  const totalRequests = services.reduce((sum, s) => sum + s.metrics.requests_total, 0)
  const totalErrors = services.reduce((sum, s) => sum + s.metrics.error_count, 0)
  const healthyServices = services.filter(s => s.is_healthy).length

  if (loading && services.length === 0) {
    return (
      <div className="mcp-manager">
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <div className="card-content">
            <div className="flex items-center justify-center py-8">
              <RefreshCw size={24} className="animate-spin text-blue-500 mr-3" />
              <span>Loading MCP Manager...</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mcp-manager">
      {/* Header */}
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <div className="card-header">
          <h2 className="card-title">
            <Server size={20} />
            MCP Manager
            <span className={`ml-2 text-xs px-2 py-1 rounded ${isConnected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {isConnected ? <Wifi size={12} className="inline mr-1" /> : <WifiOff size={12} className="inline mr-1" />}
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </h2>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-success">Running: {runningServices}</span>
            <span className="text-error">Errors: {errorServices}</span>
            <span className="text-blue-500">Healthy: {healthyServices}</span>
            {lastUpdated && (
              <span className="text-gray-500">
                Updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
        <div className="card-content">
          <div className="flex items-center justify-between">
            <p>Manage Model Context Protocol services and microservices</p>
            <div className="flex gap-2">
              <button 
                className="btn btn-secondary text-xs"
                onClick={discoverServices}
                disabled={loading}
              >
                <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                Discover Services
              </button>
              <button 
                className="btn btn-secondary text-xs"
                onClick={fetchServices}
              >
                <RefreshCw size={12} />
                Refresh
              </button>
            </div>
          </div>
          {error && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              <div className="flex items-center">
                <XCircle size={16} className="mr-2" />
                {error}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Service Cards */}
      {services.length === 0 ? (
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <div className="card-content">
            <div className="text-center py-8 text-gray-500">
              <Server size={48} className="mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium mb-2">No MCP Services Found</p>
              <p className="text-sm mb-4">
                {isConnected 
                  ? "Click 'Discover Services' to scan for available MCP services"
                  : "Unable to connect to MCP Manager API"
                }
              </p>
              {isConnected && (
                <button 
                  className="btn btn-primary"
                  onClick={discoverServices}
                  disabled={loading}
                >
                  <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                  Discover Services
                </button>
              )}
            </div>
          </div>
        </div>
      ) : (
        services.map((service) => (
          <div key={service.id} className={`mcp-service ${service.is_healthy ? 'active' : ''}`}>
            <div className="mcp-header">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  {getStatusIcon(service.status)}
                  <h3 className="font-medium">{service.name}</h3>
                  <span className="text-xs bg-tertiary px-2 py-1 rounded">
                    v{service.version}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${getServiceTypeColor(service.type)}`}>
                    {service.type}
                  </span>
                </div>
                <p className="text-sm text-secondary">{service.description}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-gray-500">{service.url}</span>
                  {service.tags.length > 0 && (
                    <div className="flex gap-1">
                      {service.tags.slice(0, 3).map(tag => (
                        <span key={tag} className="text-xs bg-gray-100 text-gray-600 px-1 py-0.5 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              
              <div className="mcp-actions">
                {service.status === 'running' ? (
                  <>
                    <button 
                      className="btn btn-secondary text-xs"
                      onClick={() => performServiceAction(service.id, 'restart')}
                      title="Restart service"
                    >
                      <RotateCcw size={12} />
                    </button>
                    <button 
                      className="btn btn-secondary text-xs"
                      onClick={() => performServiceAction(service.id, 'stop')}
                      title="Stop service"
                    >
                      <Square size={12} />
                    </button>
                  </>
                ) : (
                  <button 
                    className="btn btn-primary text-xs"
                    onClick={() => performServiceAction(service.id, 'start')}
                    disabled={service.status === 'starting'}
                    title="Start service"
                  >
                    <Play size={12} />
                    {service.status === 'starting' ? 'Starting...' : 'Start'}
                  </button>
                )}
              </div>
            </div>
            
            <div className="mcp-stats">
              <div className="metric">
                <div className="metric-value">{service.port}</div>
                <div className="metric-label">Port</div>
              </div>
              <div className="metric">
                <div className="metric-value">{formatUptime(service.metrics.uptime)}</div>
                <div className="metric-label">Uptime</div>
              </div>
              <div className="metric">
                <div className="metric-value text-blue-500">{service.metrics.requests_total.toLocaleString()}</div>
                <div className="metric-label">Requests</div>
              </div>
              <div className="metric">
                <div className={`metric-value ${service.metrics.error_count > 0 ? 'text-red-500' : 'text-green-500'}`}>
                  {service.metrics.error_count}
                </div>
                <div className="metric-label">Errors</div>
              </div>
            </div>
            
            {/* Additional metrics */}
            <div className="mcp-stats mt-2 pt-2 border-t">
              <div className="metric">
                <div className="metric-value text-purple-500">{service.metrics.response_time_avg.toFixed(0)}ms</div>
                <div className="metric-label">Avg Response</div>
              </div>
              <div className="metric">
                <div className="metric-value text-orange-500">{service.metrics.cpu_usage.toFixed(1)}%</div>
                <div className="metric-label">CPU Usage</div>
              </div>
              <div className="metric">
                <div className="metric-value text-cyan-500">{service.metrics.memory_usage.toFixed(1)}%</div>
                <div className="metric-label">Memory</div>
              </div>
              <div className="metric">
                <div className={`metric-value ${service.is_healthy ? 'text-green-500' : 'text-red-500'}`}>
                  {service.is_healthy ? 'Yes' : 'No'}
                </div>
                <div className="metric-label">Healthy</div>
              </div>
            </div>
            
            {/* Status Indicator */}
            <div className="mt-3 flex items-center justify-between">
              <span className={`text-sm font-medium ${getStatusColor(service.status)}`}>
                {service.status.charAt(0).toUpperCase() + service.status.slice(1)}
              </span>
              {service.status === 'running' && service.is_healthy && (
                <div className="flex items-center gap-1 text-xs text-muted">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  Live
                </div>
              )}
              {service.last_seen && (
                <span className="text-xs text-gray-400">
                  Last seen: {new Date(service.last_seen).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        ))
      )}

      {/* System Overview */}
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <div className="card-header">
          <h3 className="card-title">
            <Settings size={18} />
            System Overview
          </h3>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="metric">
              <div className="metric-value text-green-500">{runningServices}</div>
              <div className="metric-label">Running Services</div>
            </div>
            <div className="metric">
              <div className="metric-value text-red-500">{errorServices}</div>
              <div className="metric-label">Failed Services</div>
            </div>
            <div className="metric">
              <div className="metric-value text-blue-500">{totalRequests.toLocaleString()}</div>
              <div className="metric-label">Total Requests</div>
            </div>
            <div className="metric">
              <div className="metric-value text-yellow-500">{totalErrors}</div>
              <div className="metric-label">Total Errors</div>
            </div>
          </div>
          
          {/* Actions */}
          <div className="mt-6 flex gap-2 flex-wrap">
            <button className="btn btn-primary">
              Start All Services
            </button>
            <button className="btn btn-secondary">
              Restart All
            </button>
            <button className="btn btn-secondary">
              View Logs
            </button>
            <button className="btn btn-secondary">
              Export Config
            </button>
          </div>
        </div>
      </div>

      {/* Configuration Panel */}
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <div className="card-header">
          <h3 className="card-title">Configuration</h3>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Default Port Range</label>
              <input 
                type="text" 
                defaultValue="8080-8090" 
                className="w-full"
                placeholder="8080-8090"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Health Check Interval</label>
              <select className="w-full">
                <option value="30">30 seconds</option>
                <option value="60" selected>1 minute</option>
                <option value="300">5 minutes</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Auto-restart on failure</label>
              <input type="checkbox" defaultChecked className="mt-1" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Log Level</label>
              <select className="w-full">
                <option value="error">Error</option>
                <option value="warn">Warning</option>
                <option value="info" selected>Info</option>
                <option value="debug">Debug</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}