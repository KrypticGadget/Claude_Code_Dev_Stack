import React, { useState, useEffect, useMemo } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  Zap, 
  HardDrive, 
  Activity, 
  Users, 
  Target,
  ChevronUp,
  ChevronDown,
  Download,
  RefreshCw
} from 'lucide-react';
import './SessionAnalytics.css';

interface SessionMetrics {
  sessionId: string;
  name: string;
  path: string;
  model: string;
  tokenUsage: {
    input: number;
    output: number;
    total: number;
  };
  performance: {
    avgResponseTime: number;
    successRate: number;
    requestCount: number;
    uptime: number;
  };
  timeline: Array<{
    timestamp: Date;
    tokens: number;
    responseTime: number;
    success: boolean;
  }>;
  created: Date;
  lastActive: Date;
}

interface SessionAnalyticsProps {
  sessions: SessionMetrics[];
  timeRange?: '1h' | '24h' | '7d' | '30d' | 'all';
  onTimeRangeChange?: (range: string) => void;
  className?: string;
}

export const SessionAnalytics: React.FC<SessionAnalyticsProps> = ({
  sessions,
  timeRange = '24h',
  onTimeRangeChange,
  className
}) => {
  const [selectedMetric, setSelectedMetric] = useState<'tokens' | 'performance' | 'usage'>('tokens');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [sortBy, setSortBy] = useState<'name' | 'tokens' | 'performance' | 'activity'>('activity');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Calculate aggregate metrics
  const aggregateMetrics = useMemo(() => {
    const totalSessions = sessions.length;
    const activeSessions = sessions.filter(s => {
      const lastActive = new Date(s.lastActive);
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
      return lastActive > oneHourAgo;
    }).length;

    const totalTokens = sessions.reduce((sum, s) => sum + s.tokenUsage.total, 0);
    const totalRequests = sessions.reduce((sum, s) => sum + s.performance.requestCount, 0);
    
    const avgResponseTime = sessions.length > 0
      ? sessions.reduce((sum, s) => sum + s.performance.avgResponseTime, 0) / sessions.length
      : 0;

    const avgSuccessRate = sessions.length > 0
      ? sessions.reduce((sum, s) => sum + s.performance.successRate, 0) / sessions.length
      : 0;

    const totalUptime = sessions.reduce((sum, s) => sum + s.performance.uptime, 0);

    // Model distribution
    const modelDistribution = sessions.reduce((acc, s) => {
      acc[s.model] = (acc[s.model] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Token usage over time
    const tokenTimeline = sessions.flatMap(s => 
      s.timeline.map(t => ({
        ...t,
        sessionId: s.sessionId,
        sessionName: s.name
      }))
    ).sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());

    return {
      totalSessions,
      activeSessions,
      totalTokens,
      totalRequests,
      avgResponseTime,
      avgSuccessRate,
      totalUptime,
      modelDistribution,
      tokenTimeline
    };
  }, [sessions]);

  // Filter sessions by time range
  const filteredSessions = useMemo(() => {
    if (timeRange === 'all') return sessions;

    const now = new Date();
    const timeRangeMap = {
      '1h': 60 * 60 * 1000,
      '24h': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000,
      '30d': 30 * 24 * 60 * 60 * 1000
    };

    const cutoff = new Date(now.getTime() - timeRangeMap[timeRange]);
    
    return sessions.filter(session => {
      return session.timeline.some(t => new Date(t.timestamp) > cutoff);
    });
  }, [sessions, timeRange]);

  // Sort sessions
  const sortedSessions = useMemo(() => {
    return [...filteredSessions].sort((a, b) => {
      let aValue: number | string;
      let bValue: number | string;

      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'tokens':
          aValue = a.tokenUsage.total;
          bValue = b.tokenUsage.total;
          break;
        case 'performance':
          aValue = a.performance.successRate;
          bValue = b.performance.successRate;
          break;
        case 'activity':
          aValue = a.lastActive.getTime();
          bValue = b.lastActive.getTime();
          break;
        default:
          return 0;
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        const result = aValue.localeCompare(bValue);
        return sortOrder === 'asc' ? result : -result;
      }

      const result = (aValue as number) - (bValue as number);
      return sortOrder === 'asc' ? result : -result;
    });
  }, [filteredSessions, sortBy, sortOrder]);

  // Handle refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate refresh delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsRefreshing(false);
  };

  // Export analytics data
  const exportAnalytics = () => {
    const data = {
      timestamp: new Date().toISOString(),
      timeRange,
      aggregateMetrics,
      sessions: filteredSessions,
      generatedBy: 'Claude Code Session Manager'
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `session-analytics-${timeRange}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Format numbers
  const formatNumber = (num: number, decimals = 0) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(decimals) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(decimals) + 'K';
    }
    return num.toFixed(decimals);
  };

  // Format duration
  const formatDuration = (ms: number) => {
    const hours = Math.floor(ms / (1000 * 60 * 60));
    const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  return (
    <div className={`session-analytics ${className || ''}`}>
      {/* Header */}
      <div className="analytics-header">
        <div className="header-title">
          <h2>Session Analytics</h2>
          <p>Performance insights and usage metrics</p>
        </div>

        <div className="header-controls">
          <select 
            value={timeRange}
            onChange={(e) => onTimeRangeChange?.(e.target.value)}
            className="time-range-select"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="all">All Time</option>
          </select>

          <button 
            onClick={handleRefresh}
            className="btn btn-secondary"
            disabled={isRefreshing}
          >
            <RefreshCw size={16} className={isRefreshing ? 'spinning' : ''} />
            Refresh
          </button>

          <button 
            onClick={exportAnalytics}
            className="btn btn-secondary"
          >
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="overview-cards">
        <div className="overview-card">
          <div className="card-header">
            <h3>Total Sessions</h3>
            <Users size={24} className="card-icon" />
          </div>
          <div className="card-value">
            {aggregateMetrics.totalSessions}
          </div>
          <div className="card-subtitle">
            {aggregateMetrics.activeSessions} active now
          </div>
        </div>

        <div className="overview-card">
          <div className="card-header">
            <h3>Token Usage</h3>
            <Zap size={24} className="card-icon" />
          </div>
          <div className="card-value">
            {formatNumber(aggregateMetrics.totalTokens)}
          </div>
          <div className="card-subtitle">
            {formatNumber(aggregateMetrics.totalRequests)} requests
          </div>
        </div>

        <div className="overview-card">
          <div className="card-header">
            <h3>Avg Response Time</h3>
            <Clock size={24} className="card-icon" />
          </div>
          <div className="card-value">
            {aggregateMetrics.avgResponseTime.toFixed(0)}ms
          </div>
          <div className="card-subtitle">
            {aggregateMetrics.avgSuccessRate.toFixed(1)}% success rate
          </div>
        </div>

        <div className="overview-card">
          <div className="card-header">
            <h3>Total Uptime</h3>
            <Activity size={24} className="card-icon" />
          </div>
          <div className="card-value">
            {formatDuration(aggregateMetrics.totalUptime)}
          </div>
          <div className="card-subtitle">
            Across all sessions
          </div>
        </div>
      </div>

      {/* Metric Selector */}
      <div className="metric-selector">
        <button 
          className={`metric-btn ${selectedMetric === 'tokens' ? 'active' : ''}`}
          onClick={() => setSelectedMetric('tokens')}
        >
          <Zap size={16} />
          Token Usage
        </button>
        <button 
          className={`metric-btn ${selectedMetric === 'performance' ? 'active' : ''}`}
          onClick={() => setSelectedMetric('performance')}
        >
          <TrendingUp size={16} />
          Performance
        </button>
        <button 
          className={`metric-btn ${selectedMetric === 'usage' ? 'active' : ''}`}
          onClick={() => setSelectedMetric('usage')}
        >
          <BarChart3 size={16} />
          Usage Patterns
        </button>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        {selectedMetric === 'tokens' && (
          <div className="chart-container">
            <h3>Token Usage Distribution</h3>
            <div className="token-chart">
              {Object.entries(aggregateMetrics.modelDistribution).map(([model, count]) => (
                <div key={model} className="model-bar">
                  <div className="model-info">
                    <span className="model-name">{model}</span>
                    <span className="model-count">{count} sessions</span>
                  </div>
                  <div className="bar-container">
                    <div 
                      className="bar-fill"
                      style={{ 
                        width: `${(count / aggregateMetrics.totalSessions) * 100}%`,
                        backgroundColor: getModelColor(model)
                      }}
                    />
                  </div>
                  <span className="percentage">
                    {((count / aggregateMetrics.totalSessions) * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {selectedMetric === 'performance' && (
          <div className="chart-container">
            <h3>Performance Metrics</h3>
            <div className="performance-grid">
              {sortedSessions.slice(0, 10).map(session => (
                <div key={session.sessionId} className="performance-item">
                  <div className="session-info">
                    <span className="session-name">{session.name}</span>
                    <span className="session-model">{session.model}</span>
                  </div>
                  <div className="performance-metrics">
                    <div className="metric">
                      <span className="metric-label">Response Time</span>
                      <span className="metric-value">
                        {session.performance.avgResponseTime.toFixed(0)}ms
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Success Rate</span>
                      <span className="metric-value">
                        {session.performance.successRate.toFixed(1)}%
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Requests</span>
                      <span className="metric-value">
                        {session.performance.requestCount}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {selectedMetric === 'usage' && (
          <div className="chart-container">
            <h3>Usage Patterns</h3>
            <div className="usage-timeline">
              {aggregateMetrics.tokenTimeline
                .slice(-20)
                .map((entry, index) => (
                <div key={index} className="timeline-entry">
                  <div className="timeline-time">
                    {entry.timestamp.toLocaleTimeString()}
                  </div>
                  <div className="timeline-bar">
                    <div 
                      className="timeline-fill"
                      style={{ 
                        width: `${(entry.tokens / Math.max(...aggregateMetrics.tokenTimeline.map(t => t.tokens))) * 100}%`,
                        backgroundColor: entry.success ? 'var(--success)' : 'var(--error)'
                      }}
                    />
                  </div>
                  <div className="timeline-value">
                    {entry.tokens} tokens
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Session List */}
      <div className="session-list">
        <div className="list-header">
          <h3>Session Details</h3>
          <div className="sort-controls">
            <select 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="sort-select"
            >
              <option value="activity">Last Activity</option>
              <option value="name">Name</option>
              <option value="tokens">Token Usage</option>
              <option value="performance">Performance</option>
            </select>
            <button 
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="sort-order-btn"
            >
              {sortOrder === 'asc' ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
          </div>
        </div>

        <div className="session-table">
          <div className="table-header">
            <div className="col-name">Session</div>
            <div className="col-model">Model</div>
            <div className="col-tokens">Tokens</div>
            <div className="col-performance">Performance</div>
            <div className="col-activity">Last Activity</div>
          </div>
          
          {sortedSessions.map(session => (
            <div key={session.sessionId} className="table-row">
              <div className="col-name">
                <div className="session-info">
                  <span className="name">{session.name}</span>
                  <span className="path">{session.path}</span>
                </div>
              </div>
              <div className="col-model">
                <span className={`model-badge ${session.model}`}>
                  {session.model}
                </span>
              </div>
              <div className="col-tokens">
                <div className="token-info">
                  <span className="total">{formatNumber(session.tokenUsage.total)}</span>
                  <span className="breakdown">
                    {formatNumber(session.tokenUsage.input)}↑ {formatNumber(session.tokenUsage.output)}↓
                  </span>
                </div>
              </div>
              <div className="col-performance">
                <div className="performance-info">
                  <span className="response-time">{session.performance.avgResponseTime.toFixed(0)}ms</span>
                  <span className="success-rate">{session.performance.successRate.toFixed(1)}%</span>
                </div>
              </div>
              <div className="col-activity">
                {session.lastActive.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Helper function to get model color
const getModelColor = (model: string): string => {
  switch (model.toLowerCase()) {
    case 'opus':
      return 'var(--accent-primary)';
    case 'sonnet':
      return 'var(--accent-secondary)';
    case 'haiku':
      return 'var(--success)';
    default:
      return 'var(--text-muted)';
  }
};

export default SessionAnalytics;