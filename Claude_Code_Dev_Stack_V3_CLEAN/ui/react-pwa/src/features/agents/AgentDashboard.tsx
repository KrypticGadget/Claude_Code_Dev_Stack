import React from 'react'
import { Bot, Activity, Zap, Clock, CheckCircle, AlertCircle } from 'lucide-react'

interface AgentDashboardProps {
  agents: { active: number; total: number }
}

export const AgentDashboard: React.FC<AgentDashboardProps> = ({ agents }) => {
  // Mock agent data - in real implementation, this would come from props or API
  const agentList = [
    {
      id: 'agent-prod-frontend',
      name: 'Production Frontend Agent',
      status: 'active',
      description: 'Building production-grade React applications',
      tasksCompleted: 12,
      uptime: '2h 15m',
      performance: 95
    },
    {
      id: 'agent-testing-automation',
      name: 'Testing Automation Agent',
      status: 'active',
      description: 'Automated testing and quality assurance',
      tasksCompleted: 8,
      uptime: '1h 45m',
      performance: 98
    },
    {
      id: 'agent-ui-ux-design',
      name: 'UI/UX Design Agent',
      status: 'idle',
      description: 'User interface and experience design',
      tasksCompleted: 5,
      uptime: '30m',
      performance: 87
    },
    {
      id: 'agent-mobile-development',
      name: 'Mobile Development Agent',
      status: 'active',
      description: 'Cross-platform mobile app development',
      tasksCompleted: 15,
      uptime: '3h 20m',
      performance: 92
    },
    {
      id: 'agent-backend-development',
      name: 'Backend Development Agent',
      status: 'error',
      description: 'Server-side development and APIs',
      tasksCompleted: 3,
      uptime: '15m',
      performance: 45
    },
    {
      id: 'agent-devops-engineering',
      name: 'DevOps Engineering Agent',
      status: 'active',
      description: 'Infrastructure and deployment automation',
      tasksCompleted: 7,
      uptime: '1h 30m',
      performance: 89
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle size={16} className="text-green-500" />
      case 'idle':
        return <Clock size={16} className="text-yellow-500" />
      case 'error':
        return <AlertCircle size={16} className="text-red-500" />
      default:
        return <Activity size={16} className="text-gray-500" />
    }
  }

  const getPerformanceColor = (performance: number) => {
    if (performance >= 90) return 'text-green-500'
    if (performance >= 70) return 'text-yellow-500'
    return 'text-red-500'
  }

  return (
    <div className="agent-dashboard">
      {/* Dashboard Header */}
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <div className="card-header">
          <h2 className="card-title">
            <Bot size={20} />
            Agent Dashboard
          </h2>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-success">
              Active: {agents.active}
            </span>
            <span className="text-muted">
              Total: {agents.total}
            </span>
          </div>
        </div>
        <div className="card-content">
          <p>Real-time monitoring of all Claude Code Dev Stack agents</p>
        </div>
      </div>

      {/* Agent Cards */}
      {agentList.map((agent) => (
        <div key={agent.id} className="agent-card">
          <div className="agent-status">
            {getStatusIcon(agent.status)}
            <span className="font-medium">{agent.name}</span>
          </div>
          
          <p className="text-sm text-secondary mb-3">
            {agent.description}
          </p>
          
          <div className="agent-metrics">
            <div className="metric">
              <div className="metric-value">{agent.tasksCompleted}</div>
              <div className="metric-label">Tasks</div>
            </div>
            <div className="metric">
              <div className="metric-value">{agent.uptime}</div>
              <div className="metric-label">Uptime</div>
            </div>
            <div className="metric" style={{ gridColumn: '1 / -1' }}>
              <div className={`metric-value ${getPerformanceColor(agent.performance)}`}>
                {agent.performance}%
              </div>
              <div className="metric-label">Performance</div>
            </div>
          </div>
          
          {/* Performance Bar */}
          <div className="mt-3">
            <div className="task-progress">
              <div 
                className="task-progress-bar"
                style={{ width: `${agent.performance}%` }}
              />
            </div>
          </div>
        </div>
      ))}

      {/* System Overview */}
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <div className="card-header">
          <h3 className="card-title">
            <Activity size={18} />
            System Overview
          </h3>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-4 gap-4">
            <div className="metric">
              <div className="metric-value text-green-500">
                {agentList.filter(a => a.status === 'active').length}
              </div>
              <div className="metric-label">Active Agents</div>
            </div>
            <div className="metric">
              <div className="metric-value text-yellow-500">
                {agentList.filter(a => a.status === 'idle').length}
              </div>
              <div className="metric-label">Idle Agents</div>
            </div>
            <div className="metric">
              <div className="metric-value text-red-500">
                {agentList.filter(a => a.status === 'error').length}
              </div>
              <div className="metric-label">Error Agents</div>
            </div>
            <div className="metric">
              <div className="metric-value text-blue-500">
                {agentList.reduce((sum, agent) => sum + agent.tasksCompleted, 0)}
              </div>
              <div className="metric-label">Total Tasks</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}