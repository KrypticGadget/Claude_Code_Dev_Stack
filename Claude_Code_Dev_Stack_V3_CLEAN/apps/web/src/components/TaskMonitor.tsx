import React, { useState } from 'react'
import { Zap, Clock, CheckCircle, XCircle, Play, Pause, RotateCcw } from 'lucide-react'

interface TaskMonitorProps {
  tasks: { completed: number; total: number }
}

interface Task {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'error'
  progress: number
  startTime: string
  estimatedDuration: string
  agent: string
}

export const TaskMonitor: React.FC<TaskMonitorProps> = ({ tasks }) => {
  const [filter, setFilter] = useState<string>('all')
  
  // Mock task data - in real implementation, this would come from WebSocket or API
  const taskList: Task[] = [
    {
      id: 'task-1',
      name: 'Build React Components',
      description: 'Creating reusable UI components for the dashboard',
      status: 'completed',
      progress: 100,
      startTime: '2 hours ago',
      estimatedDuration: '45 minutes',
      agent: 'agent-prod-frontend'
    },
    {
      id: 'task-2',
      name: 'Setup PWA Configuration',
      description: 'Configuring service worker and manifest for PWA support',
      status: 'running',
      progress: 75,
      startTime: '30 minutes ago',
      estimatedDuration: '20 minutes',
      agent: 'agent-prod-frontend'
    },
    {
      id: 'task-3',
      name: 'Generate Test Suite',
      description: 'Creating comprehensive unit and integration tests',
      status: 'running',
      progress: 45,
      startTime: '15 minutes ago',
      estimatedDuration: '1 hour',
      agent: 'agent-testing-automation'
    },
    {
      id: 'task-4',
      name: 'Design Mobile Layout',
      description: 'Creating responsive mobile-first design patterns',
      status: 'pending',
      progress: 0,
      startTime: 'Not started',
      estimatedDuration: '1.5 hours',
      agent: 'agent-ui-ux-design'
    },
    {
      id: 'task-5',
      name: 'API Integration',
      description: 'Connecting frontend with backend services',
      status: 'error',
      progress: 25,
      startTime: '1 hour ago',
      estimatedDuration: '30 minutes',
      agent: 'agent-backend-development'
    },
    {
      id: 'task-6',
      name: 'Deploy to Production',
      description: 'Setting up CI/CD pipeline and deployment',
      status: 'pending',
      progress: 0,
      startTime: 'Not started',
      estimatedDuration: '45 minutes',
      agent: 'agent-devops-engineering'
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="text-green-500" />
      case 'running':
        return <Play size={16} className="text-blue-500" />
      case 'pending':
        return <Clock size={16} className="text-yellow-500" />
      case 'error':
        return <XCircle size={16} className="text-red-500" />
      default:
        return <Pause size={16} className="text-gray-500" />
    }
  }

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'completed':
        return 'completed'
      case 'error':
        return 'error'
      default:
        return ''
    }
  }

  const filteredTasks = filter === 'all' 
    ? taskList 
    : taskList.filter(task => task.status === filter)

  const taskCounts = {
    all: taskList.length,
    running: taskList.filter(t => t.status === 'running').length,
    completed: taskList.filter(t => t.status === 'completed').length,
    pending: taskList.filter(t => t.status === 'pending').length,
    error: taskList.filter(t => t.status === 'error').length
  }

  return (
    <div className="task-monitor">
      {/* Header */}
      <div className="card-header">
        <h2 className="card-title">
          <Zap size={20} />
          Task Monitor
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted">
            {tasks.completed}/{tasks.total} completed
          </span>
          <button className="btn btn-secondary" onClick={() => window.location.reload()}>
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="mb-4">
        <div className="flex gap-2 flex-wrap">
          {Object.entries(taskCounts).map(([status, count]) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`btn ${filter === status ? 'btn-primary' : 'btn-secondary'} text-sm`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)} ({count})
            </button>
          ))}
        </div>
      </div>

      {/* Task List */}
      <div className="task-list">
        {filteredTasks.map((task) => (
          <div key={task.id} className={`task-item ${getStatusClass(task.status)}`}>
            <div className="task-info">
              <div className="flex items-center gap-2 mb-1">
                {getStatusIcon(task.status)}
                <span className="task-name">{task.name}</span>
                <span className="text-xs text-muted bg-tertiary px-2 py-1 rounded">
                  {task.agent.replace('agent-', '')}
                </span>
              </div>
              <p className="task-description">{task.description}</p>
              <div className="flex items-center gap-4 mt-2 text-xs text-muted">
                <span>Started: {task.startTime}</span>
                <span>Duration: {task.estimatedDuration}</span>
              </div>
            </div>
            
            <div className="flex flex-col items-end gap-2">
              <span className="text-sm font-medium">{task.progress}%</span>
              <div className="task-progress">
                <div 
                  className="task-progress-bar"
                  style={{ width: `${task.progress}%` }}
                />
              </div>
            </div>
          </div>
        ))}

        {filteredTasks.length === 0 && (
          <div className="text-center py-8 text-muted">
            <Zap size={48} className="mx-auto mb-2 opacity-50" />
            <p>No tasks found for the selected filter.</p>
          </div>
        )}
      </div>

      {/* Task Statistics */}
      <div className="mt-6 p-4 bg-secondary rounded-lg">
        <h3 className="font-medium mb-3">Task Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="metric">
            <div className="metric-value text-blue-500">{taskCounts.running}</div>
            <div className="metric-label">Running</div>
          </div>
          <div className="metric">
            <div className="metric-value text-green-500">{taskCounts.completed}</div>
            <div className="metric-label">Completed</div>
          </div>
          <div className="metric">
            <div className="metric-value text-yellow-500">{taskCounts.pending}</div>
            <div className="metric-label">Pending</div>
          </div>
          <div className="metric">
            <div className="metric-value text-red-500">{taskCounts.error}</div>
            <div className="metric-label">Errors</div>
          </div>
        </div>
      </div>
    </div>
  )
}