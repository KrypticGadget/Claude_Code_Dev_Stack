import React, { useState } from 'react'
import { Settings, Server, Play, Square, RotateCcw, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

interface MCPService {
  id: string
  name: string
  status: 'running' | 'stopped' | 'error' | 'starting'
  description: string
  port: number
  uptime: string
  requests: number
  errors: number
  version: string
}

export const MCPManager: React.FC = () => {
  const [services, setServices] = useState<MCPService[]>([
    {
      id: 'mcp-core',
      name: 'MCP Core Service',
      status: 'running',
      description: 'Main Model Context Protocol service',
      port: 8080,
      uptime: '2h 15m',
      requests: 1247,
      errors: 3,
      version: '1.2.0'
    },
    {
      id: 'mcp-auth',
      name: 'Authentication Service',
      status: 'running',
      description: 'Handles authentication and authorization',
      port: 8081,
      uptime: '2h 10m',
      requests: 856,
      errors: 0,
      version: '1.1.5'
    },
    {
      id: 'mcp-storage',
      name: 'Storage Service',
      status: 'error',
      description: 'Manages data persistence and caching',
      port: 8082,
      uptime: '0m',
      requests: 0,
      errors: 12,
      version: '1.0.8'
    },
    {
      id: 'mcp-ai-proxy',
      name: 'AI Proxy Service',
      status: 'running',
      description: 'Proxies requests to AI models and services',
      port: 8083,
      uptime: '1h 45m',
      requests: 2103,
      errors: 1,
      version: '2.0.0'
    },
    {
      id: 'mcp-monitor',
      name: 'Monitoring Service',
      status: 'starting',
      description: 'Real-time monitoring and metrics collection',
      port: 8084,
      uptime: '0m',
      requests: 0,
      errors: 0,
      version: '1.3.1'
    }
  ])

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
      default:
        return 'text-gray-500'
    }
  }

  const handleServiceAction = (serviceId: string, action: 'start' | 'stop' | 'restart') => {
    setServices(prev => prev.map(service => {
      if (service.id === serviceId) {
        switch (action) {
          case 'start':
            return { ...service, status: 'starting' as const }
          case 'stop':
            return { ...service, status: 'stopped' as const, uptime: '0m' }
          case 'restart':
            return { ...service, status: 'starting' as const, uptime: '0m' }
          default:
            return service
        }
      }
      return service
    }))

    // Simulate async status change
    setTimeout(() => {
      setServices(prev => prev.map(service => {
        if (service.id === serviceId && service.status === 'starting') {
          return { ...service, status: 'running' as const }
        }
        return service
      }))
    }, 2000)
  }

  const runningServices = services.filter(s => s.status === 'running').length
  const errorServices = services.filter(s => s.status === 'error').length
  const totalRequests = services.reduce((sum, s) => sum + s.requests, 0)
  const totalErrors = services.reduce((sum, s) => sum + s.errors, 0)

  return (
    <div className="mcp-manager">
      {/* Header */}
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <div className="card-header">
          <h2 className="card-title">
            <Server size={20} />
            MCP Manager
          </h2>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-success">Running: {runningServices}</span>
            <span className="text-error">Errors: {errorServices}</span>
          </div>
        </div>
        <div className="card-content">
          <p>Manage Model Context Protocol services and microservices</p>
        </div>
      </div>

      {/* Service Cards */}
      {services.map((service) => (
        <div key={service.id} className={`mcp-service ${service.status === 'running' ? 'active' : ''}`}>
          <div className="mcp-header">
            <div>
              <div className="flex items-center gap-2 mb-1">
                {getStatusIcon(service.status)}
                <h3 className="font-medium">{service.name}</h3>
                <span className="text-xs bg-tertiary px-2 py-1 rounded">
                  v{service.version}
                </span>
              </div>
              <p className="text-sm text-secondary">{service.description}</p>
            </div>
            
            <div className="mcp-actions">
              {service.status === 'running' ? (
                <>
                  <button 
                    className="btn btn-secondary text-xs"
                    onClick={() => handleServiceAction(service.id, 'restart')}
                  >
                    <RotateCcw size={12} />
                  </button>
                  <button 
                    className="btn btn-secondary text-xs"
                    onClick={() => handleServiceAction(service.id, 'stop')}
                  >
                    <Square size={12} />
                  </button>
                </>
              ) : (
                <button 
                  className="btn btn-primary text-xs"
                  onClick={() => handleServiceAction(service.id, 'start')}
                  disabled={service.status === 'starting'}
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
              <div className="metric-value">{service.uptime}</div>
              <div className="metric-label">Uptime</div>
            </div>
            <div className="metric">
              <div className="metric-value text-blue-500">{service.requests.toLocaleString()}</div>
              <div className="metric-label">Requests</div>
            </div>
            <div className="metric">
              <div className={`metric-value ${service.errors > 0 ? 'text-red-500' : 'text-green-500'}`}>
                {service.errors}
              </div>
              <div className="metric-label">Errors</div>
            </div>
          </div>
          
          {/* Status Indicator */}
          <div className="mt-3 flex items-center justify-between">
            <span className={`text-sm font-medium ${getStatusColor(service.status)}`}>
              {service.status.charAt(0).toUpperCase() + service.status.slice(1)}
            </span>
            {service.status === 'running' && (
              <div className="flex items-center gap-1 text-xs text-muted">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                Live
              </div>
            )}
          </div>
        </div>
      ))}

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