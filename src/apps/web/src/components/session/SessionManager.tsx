import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Settings, BarChart3, Download, Upload, Search, FolderOpen, Play, Pause, Copy, Trash2, Edit3, Save, X, CheckCircle, AlertCircle, Clock, Zap, HardDrive, Activity } from 'lucide-react';
import { useLocalStorage } from '../hooks/useLocalStorage';
import './SessionManager.css';

// Types for session management
interface ClaudeSession {
  id: string;
  name: string;
  path: string;
  created: Date;
  lastAccessed: Date;
  status: 'active' | 'paused' | 'stopped' | 'error';
  tokenUsage: {
    input: number;
    output: number;
    total: number;
  };
  performance: {
    avgResponseTime: number;
    successRate: number;
    requestCount: number;
  };
  context: {
    fileCount: number;
    projectType: string;
    lastActivity: string;
  };
  settings: {
    model: 'opus' | 'sonnet' | 'haiku';
    temperature: number;
    maxTokens: number;
    contextWindow: number;
  };
}

interface SessionAnalytics {
  totalSessions: number;
  activeSessions: number;
  totalTokens: number;
  avgSessionDuration: number;
  topPaths: Array<{ path: string; count: number }>;
  modelUsage: Record<string, number>;
}

export const SessionManager: React.FC = () => {
  const [sessions, setSessions] = useLocalStorage<ClaudeSession[]>('claude-sessions', []);
  const [analytics, setAnalytics] = useState<SessionAnalytics | null>(null);
  const [selectedSession, setSelectedSession] = useState<ClaudeSession | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [pathInput, setPathInput] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'created' | 'accessed' | 'name' | 'tokens'>('accessed');
  const [showAnalytics, setShowAnalytics] = useState(false);

  // Session creation form state
  const [newSession, setNewSession] = useState<Partial<ClaudeSession>>({
    name: '',
    path: '',
    settings: {
      model: 'sonnet',
      temperature: 0.7,
      maxTokens: 4000,
      contextWindow: 200000
    }
  });

  // Calculate analytics
  useEffect(() => {
    const calculateAnalytics = () => {
      const totalSessions = sessions.length;
      const activeSessions = sessions.filter(s => s.status === 'active').length;
      const totalTokens = sessions.reduce((sum, s) => sum + s.tokenUsage.total, 0);
      const avgSessionDuration = sessions.length > 0 
        ? sessions.reduce((sum, s) => sum + (s.lastAccessed.getTime() - s.created.getTime()), 0) / sessions.length 
        : 0;

      const pathCounts = sessions.reduce((acc, s) => {
        const basePath = s.path.split('\\').slice(0, -1).join('\\');
        acc[basePath] = (acc[basePath] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      const topPaths = Object.entries(pathCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([path, count]) => ({ path, count }));

      const modelUsage = sessions.reduce((acc, s) => {
        acc[s.settings.model] = (acc[s.settings.model] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      setAnalytics({
        totalSessions,
        activeSessions,
        totalTokens,
        avgSessionDuration,
        topPaths,
        modelUsage
      });
    };

    calculateAnalytics();
  }, [sessions]);

  // Create new session
  const createSession = useCallback(async () => {
    if (!newSession.name || !newSession.path) return;

    const session: ClaudeSession = {
      id: `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: newSession.name,
      path: newSession.path,
      created: new Date(),
      lastAccessed: new Date(),
      status: 'active',
      tokenUsage: { input: 0, output: 0, total: 0 },
      performance: { avgResponseTime: 0, successRate: 100, requestCount: 0 },
      context: {
        fileCount: 0,
        projectType: detectProjectType(newSession.path),
        lastActivity: 'Session created'
      },
      settings: newSession.settings as ClaudeSession['settings']
    };

    setSessions(prev => [session, ...prev]);
    setNewSession({
      name: '',
      path: '',
      settings: { model: 'sonnet', temperature: 0.7, maxTokens: 4000, contextWindow: 200000 }
    });
    setIsCreating(false);

    // Simulate session initialization
    simulateSessionActivity(session.id);
  }, [newSession, setSessions]);

  // Clone session
  const cloneSession = useCallback((session: ClaudeSession) => {
    const clonedSession: ClaudeSession = {
      ...session,
      id: `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: `${session.name} (Copy)`,
      created: new Date(),
      lastAccessed: new Date(),
      status: 'paused',
      tokenUsage: { input: 0, output: 0, total: 0 },
      performance: { avgResponseTime: 0, successRate: 100, requestCount: 0 },
      context: {
        ...session.context,
        lastActivity: 'Session cloned'
      }
    };

    setSessions(prev => [clonedSession, ...prev]);
  }, [setSessions]);

  // Update session
  const updateSession = useCallback((id: string, updates: Partial<ClaudeSession>) => {
    setSessions(prev => prev.map(session => 
      session.id === id 
        ? { ...session, ...updates, lastAccessed: new Date() }
        : session
    ));
  }, [setSessions]);

  // Delete session
  const deleteSession = useCallback((id: string) => {
    setSessions(prev => prev.filter(session => session.id !== id));
    if (selectedSession?.id === id) {
      setSelectedSession(null);
    }
  }, [setSessions, selectedSession]);

  // Export sessions
  const exportSessions = useCallback(() => {
    const exportData = {
      sessions,
      exportDate: new Date().toISOString(),
      version: '1.0'
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `claude-sessions-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [sessions]);

  // Import sessions
  const importSessions = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        if (data.sessions && Array.isArray(data.sessions)) {
          setSessions(prev => [...prev, ...data.sessions]);
        }
      } catch (error) {
        console.error('Failed to import sessions:', error);
      }
    };
    reader.readAsText(file);
  }, [setSessions]);

  // Navigate to path
  const navigateToPath = useCallback((path: string) => {
    setPathInput(path);
    // Auto-create session at path if requested
    if (path && !sessions.find(s => s.path === path)) {
      setNewSession(prev => ({
        ...prev,
        path,
        name: `Session at ${path.split('\\').pop() || path}`
      }));
      setIsCreating(true);
    }
  }, [sessions]);

  // Simulate session activity
  const simulateSessionActivity = useCallback((sessionId: string) => {
    const updateSessionActivity = () => {
      setSessions(prev => prev.map(session => {
        if (session.id === sessionId && session.status === 'active') {
          return {
            ...session,
            tokenUsage: {
              input: session.tokenUsage.input + Math.floor(Math.random() * 100),
              output: session.tokenUsage.output + Math.floor(Math.random() * 200),
              total: session.tokenUsage.total + Math.floor(Math.random() * 300)
            },
            performance: {
              ...session.performance,
              requestCount: session.performance.requestCount + 1,
              avgResponseTime: Math.random() * 2000 + 500,
              successRate: Math.max(85, Math.random() * 100)
            },
            context: {
              ...session.context,
              lastActivity: new Date().toLocaleTimeString()
            }
          };
        }
        return session;
      }));
    };

    const interval = setInterval(updateSessionActivity, 5000);
    return () => clearInterval(interval);
  }, [setSessions]);

  // Detect project type from path
  const detectProjectType = (path: string): string => {
    const pathLower = path.toLowerCase();
    if (pathLower.includes('react') || pathLower.includes('next')) return 'React';
    if (pathLower.includes('vue')) return 'Vue';
    if (pathLower.includes('angular')) return 'Angular';
    if (pathLower.includes('node') || pathLower.includes('express')) return 'Node.js';
    if (pathLower.includes('python') || pathLower.includes('django') || pathLower.includes('flask')) return 'Python';
    if (pathLower.includes('java') || pathLower.includes('spring')) return 'Java';
    if (pathLower.includes('go') || pathLower.includes('golang')) return 'Go';
    if (pathLower.includes('rust')) return 'Rust';
    return 'General';
  };

  // Filter and sort sessions
  const filteredSessions = sessions
    .filter(session => 
      session.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      session.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
      session.context.projectType.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'created':
          return new Date(b.created).getTime() - new Date(a.created).getTime();
        case 'accessed':
          return new Date(b.lastAccessed).getTime() - new Date(a.lastAccessed).getTime();
        case 'name':
          return a.name.localeCompare(b.name);
        case 'tokens':
          return b.tokenUsage.total - a.tokenUsage.total;
        default:
          return 0;
      }
    });

  return (
    <div className="session-manager">
      {/* Header */}
      <div className="session-manager-header">
        <div className="header-title">
          <h1>Claude Session Manager</h1>
          <p>Manage your Claude instances across different project paths</p>
        </div>
        
        <div className="header-actions">
          <button 
            className="btn btn-primary"
            onClick={() => setIsCreating(true)}
          >
            <Plus size={16} />
            New Session
          </button>
          
          <button 
            className="btn btn-secondary"
            onClick={() => setShowAnalytics(!showAnalytics)}
          >
            <BarChart3 size={16} />
            Analytics
          </button>
          
          <div className="import-export-buttons">
            <button className="btn btn-secondary" onClick={exportSessions}>
              <Download size={16} />
              Export
            </button>
            
            <label className="btn btn-secondary">
              <Upload size={16} />
              Import
              <input
                type="file"
                accept=".json"
                onChange={importSessions}
                style={{ display: 'none' }}
              />
            </label>
          </div>
        </div>
      </div>

      {/* Analytics Dashboard */}
      {showAnalytics && analytics && (
        <div className="analytics-dashboard">
          <div className="analytics-grid">
            <div className="analytics-card">
              <div className="analytics-card-header">
                <h3>Sessions Overview</h3>
                <Activity size={20} />
              </div>
              <div className="analytics-stats">
                <div className="stat">
                  <span className="stat-value">{analytics.totalSessions}</span>
                  <span className="stat-label">Total Sessions</span>
                </div>
                <div className="stat">
                  <span className="stat-value text-success">{analytics.activeSessions}</span>
                  <span className="stat-label">Active</span>
                </div>
              </div>
            </div>

            <div className="analytics-card">
              <div className="analytics-card-header">
                <h3>Token Usage</h3>
                <Zap size={20} />
              </div>
              <div className="analytics-stats">
                <div className="stat">
                  <span className="stat-value">{analytics.totalTokens.toLocaleString()}</span>
                  <span className="stat-label">Total Tokens</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{Math.round(analytics.totalTokens / Math.max(analytics.totalSessions, 1)).toLocaleString()}</span>
                  <span className="stat-label">Avg per Session</span>
                </div>
              </div>
            </div>

            <div className="analytics-card">
              <div className="analytics-card-header">
                <h3>Top Paths</h3>
                <HardDrive size={20} />
              </div>
              <div className="top-paths">
                {analytics.topPaths.map((path, index) => (
                  <div key={index} className="top-path">
                    <span className="path-name">{path.path}</span>
                    <span className="path-count">{path.count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="analytics-card">
              <div className="analytics-card-header">
                <h3>Model Usage</h3>
                <Settings size={20} />
              </div>
              <div className="model-usage">
                {Object.entries(analytics.modelUsage).map(([model, count]) => (
                  <div key={model} className="model-stat">
                    <span className="model-name">{model}</span>
                    <div className="model-bar">
                      <div 
                        className="model-bar-fill"
                        style={{ 
                          width: `${(count / analytics.totalSessions) * 100}%`,
                          backgroundColor: model === 'opus' ? '#7aa2f7' : model === 'sonnet' ? '#bb9af7' : '#9ece6a'
                        }}
                      />
                    </div>
                    <span className="model-count">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search and Controls */}
      <div className="session-controls">
        <div className="search-section">
          <div className="search-input-wrapper">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search sessions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="path-navigation">
            <div className="path-input-wrapper">
              <FolderOpen size={16} />
              <input
                type="text"
                placeholder="Navigate to path..."
                value={pathInput}
                onChange={(e) => setPathInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && navigateToPath(pathInput)}
                className="path-input"
              />
            </div>
            <button 
              className="btn btn-secondary"
              onClick={() => navigateToPath(pathInput)}
            >
              Go
            </button>
          </div>
        </div>

        <div className="view-controls">
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value as any)}
            className="sort-select"
          >
            <option value="accessed">Last Accessed</option>
            <option value="created">Date Created</option>
            <option value="name">Name</option>
            <option value="tokens">Token Usage</option>
          </select>

          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              Grid
            </button>
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              List
            </button>
          </div>
        </div>
      </div>

      {/* Sessions Grid/List */}
      <div className={`sessions-container ${viewMode}`}>
        {filteredSessions.map(session => (
          <SessionCard
            key={session.id}
            session={session}
            onSelect={setSelectedSession}
            onUpdate={updateSession}
            onClone={cloneSession}
            onDelete={deleteSession}
            isSelected={selectedSession?.id === session.id}
            viewMode={viewMode}
          />
        ))}
        
        {filteredSessions.length === 0 && (
          <div className="empty-state">
            <h3>No sessions found</h3>
            <p>Create a new session to get started</p>
            <button 
              className="btn btn-primary"
              onClick={() => setIsCreating(true)}
            >
              <Plus size={16} />
              Create Session
            </button>
          </div>
        )}
      </div>

      {/* Session Creation Modal */}
      {isCreating && (
        <SessionCreationWizard
          session={newSession}
          onUpdate={setNewSession}
          onCreate={createSession}
          onCancel={() => setIsCreating(false)}
        />
      )}

      {/* Session Details Panel */}
      {selectedSession && (
        <SessionDetailsPanel
          session={selectedSession}
          onUpdate={(updates) => updateSession(selectedSession.id, updates)}
          onClose={() => setSelectedSession(null)}
        />
      )}
    </div>
  );
};

// Session Card Component
interface SessionCardProps {
  session: ClaudeSession;
  onSelect: (session: ClaudeSession) => void;
  onUpdate: (id: string, updates: Partial<ClaudeSession>) => void;
  onClone: (session: ClaudeSession) => void;
  onDelete: (id: string) => void;
  isSelected: boolean;
  viewMode: 'grid' | 'list';
}

const SessionCard: React.FC<SessionCardProps> = ({
  session,
  onSelect,
  onUpdate,
  onClone,
  onDelete,
  isSelected,
  viewMode
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(session.name);

  const getStatusIcon = (status: ClaudeSession['status']) => {
    switch (status) {
      case 'active':
        return <CheckCircle size={16} className="text-success" />;
      case 'paused':
        return <Pause size={16} className="text-warning" />;
      case 'stopped':
        return <Clock size={16} className="text-muted" />;
      case 'error':
        return <AlertCircle size={16} className="text-error" />;
    }
  };

  const toggleStatus = () => {
    const newStatus = session.status === 'active' ? 'paused' : 'active';
    onUpdate(session.id, { status: newStatus });
  };

  const saveName = () => {
    onUpdate(session.id, { name: editName });
    setIsEditing(false);
  };

  return (
    <div className={`session-card ${isSelected ? 'selected' : ''} ${viewMode}`}>
      <div className="session-card-header">
        <div className="session-info">
          {isEditing ? (
            <div className="edit-name">
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && saveName()}
                className="name-input"
                autoFocus
              />
              <button onClick={saveName} className="save-btn">
                <Save size={14} />
              </button>
              <button onClick={() => setIsEditing(false)} className="cancel-btn">
                <X size={14} />
              </button>
            </div>
          ) : (
            <div className="session-name" onClick={() => onSelect(session)}>
              <h3>{session.name}</h3>
              <button 
                onClick={(e) => { e.stopPropagation(); setIsEditing(true); }}
                className="edit-name-btn"
              >
                <Edit3 size={14} />
              </button>
            </div>
          )}
          
          <div className="session-meta">
            <span className="session-path">{session.path}</span>
            <span className="session-type">{session.context.projectType}</span>
          </div>
        </div>

        <div className="session-status">
          {getStatusIcon(session.status)}
          <span className="status-text">{session.status}</span>
        </div>
      </div>

      <div className="session-metrics">
        <div className="metric">
          <span className="metric-label">Tokens</span>
          <span className="metric-value">{session.tokenUsage.total.toLocaleString()}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Requests</span>
          <span className="metric-value">{session.performance.requestCount}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Success Rate</span>
          <span className="metric-value">{session.performance.successRate.toFixed(1)}%</span>
        </div>
        <div className="metric">
          <span className="metric-label">Model</span>
          <span className="metric-value">{session.settings.model}</span>
        </div>
      </div>

      <div className="session-activity">
        <span className="last-activity">Last: {session.context.lastActivity}</span>
        <span className="last-accessed">{new Date(session.lastAccessed).toLocaleString()}</span>
      </div>

      <div className="session-actions">
        <button 
          onClick={toggleStatus}
          className={`action-btn ${session.status === 'active' ? 'pause' : 'play'}`}
          title={session.status === 'active' ? 'Pause Session' : 'Resume Session'}
        >
          {session.status === 'active' ? <Pause size={16} /> : <Play size={16} />}
        </button>
        
        <button 
          onClick={() => onClone(session)}
          className="action-btn clone"
          title="Clone Session"
        >
          <Copy size={16} />
        </button>
        
        <button 
          onClick={() => onSelect(session)}
          className="action-btn settings"
          title="Session Settings"
        >
          <Settings size={16} />
        </button>
        
        <button 
          onClick={() => onDelete(session.id)}
          className="action-btn delete"
          title="Delete Session"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
};

// Session Creation Wizard Component
interface SessionCreationWizardProps {
  session: Partial<ClaudeSession>;
  onUpdate: (session: Partial<ClaudeSession>) => void;
  onCreate: () => void;
  onCancel: () => void;
}

const SessionCreationWizard: React.FC<SessionCreationWizardProps> = ({
  session,
  onUpdate,
  onCreate,
  onCancel
}) => {
  return (
    <div className="modal-overlay">
      <div className="session-wizard">
        <div className="wizard-header">
          <h2>Create New Claude Session</h2>
          <button onClick={onCancel} className="close-btn">
            <X size={20} />
          </button>
        </div>

        <div className="wizard-content">
          <div className="form-group">
            <label htmlFor="session-name">Session Name</label>
            <input
              id="session-name"
              type="text"
              value={session.name || ''}
              onChange={(e) => onUpdate({ ...session, name: e.target.value })}
              placeholder="Enter session name..."
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="session-path">Project Path</label>
            <input
              id="session-path"
              type="text"
              value={session.path || ''}
              onChange={(e) => onUpdate({ ...session, path: e.target.value })}
              placeholder="C:\path\to\your\project"
              className="form-input"
            />
            <small className="form-help">The file system path where this Claude instance will operate</small>
          </div>

          <div className="form-group">
            <label htmlFor="session-model">Model</label>
            <select
              id="session-model"
              value={session.settings?.model || 'sonnet'}
              onChange={(e) => onUpdate({ 
                ...session, 
                settings: { 
                  ...session.settings, 
                  model: e.target.value as ClaudeSession['settings']['model'] 
                } 
              })}
              className="form-select"
            >
              <option value="haiku">Claude 3 Haiku (Fast & Efficient)</option>
              <option value="sonnet">Claude 3.5 Sonnet (Balanced)</option>
              <option value="opus">Claude 3 Opus (Most Capable)</option>
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="session-temperature">Temperature</label>
              <input
                id="session-temperature"
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={session.settings?.temperature || 0.7}
                onChange={(e) => onUpdate({ 
                  ...session, 
                  settings: { 
                    ...session.settings, 
                    temperature: parseFloat(e.target.value) 
                  } 
                })}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="session-max-tokens">Max Tokens</label>
              <input
                id="session-max-tokens"
                type="number"
                min="1"
                max="8192"
                value={session.settings?.maxTokens || 4000}
                onChange={(e) => onUpdate({ 
                  ...session, 
                  settings: { 
                    ...session.settings, 
                    maxTokens: parseInt(e.target.value) 
                  } 
                })}
                className="form-input"
              />
            </div>
          </div>
        </div>

        <div className="wizard-footer">
          <button onClick={onCancel} className="btn btn-secondary">
            Cancel
          </button>
          <button 
            onClick={onCreate} 
            className="btn btn-primary"
            disabled={!session.name || !session.path}
          >
            <Plus size={16} />
            Create Session
          </button>
        </div>
      </div>
    </div>
  );
};

// Session Details Panel Component
interface SessionDetailsPanelProps {
  session: ClaudeSession;
  onUpdate: (updates: Partial<ClaudeSession>) => void;
  onClose: () => void;
}

const SessionDetailsPanel: React.FC<SessionDetailsPanelProps> = ({
  session,
  onUpdate,
  onClose
}) => {
  return (
    <div className="session-details-panel">
      <div className="panel-header">
        <h2>{session.name}</h2>
        <button onClick={onClose} className="close-btn">
          <X size={20} />
        </button>
      </div>

      <div className="panel-content">
        <div className="details-section">
          <h3>Session Information</h3>
          <div className="details-grid">
            <div className="detail-item">
              <span className="detail-label">Path</span>
              <span className="detail-value">{session.path}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Created</span>
              <span className="detail-value">{new Date(session.created).toLocaleString()}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Last Accessed</span>
              <span className="detail-value">{new Date(session.lastAccessed).toLocaleString()}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Status</span>
              <span className={`detail-value status-${session.status}`}>{session.status}</span>
            </div>
          </div>
        </div>

        <div className="details-section">
          <h3>Performance Metrics</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-title">Token Usage</span>
              <div className="metric-breakdown">
                <div className="metric-item">
                  <span>Input:</span>
                  <span>{session.tokenUsage.input.toLocaleString()}</span>
                </div>
                <div className="metric-item">
                  <span>Output:</span>
                  <span>{session.tokenUsage.output.toLocaleString()}</span>
                </div>
                <div className="metric-item total">
                  <span>Total:</span>
                  <span>{session.tokenUsage.total.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <div className="metric-card">
              <span className="metric-title">Performance</span>
              <div className="metric-breakdown">
                <div className="metric-item">
                  <span>Requests:</span>
                  <span>{session.performance.requestCount}</span>
                </div>
                <div className="metric-item">
                  <span>Success Rate:</span>
                  <span>{session.performance.successRate.toFixed(1)}%</span>
                </div>
                <div className="metric-item">
                  <span>Avg Response:</span>
                  <span>{session.performance.avgResponseTime.toFixed(0)}ms</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="details-section">
          <h3>Settings</h3>
          <div className="settings-form">
            <div className="form-group">
              <label>Model</label>
              <select
                value={session.settings.model}
                onChange={(e) => onUpdate({ 
                  settings: { 
                    ...session.settings, 
                    model: e.target.value as ClaudeSession['settings']['model'] 
                  } 
                })}
                className="form-select"
              >
                <option value="haiku">Claude 3 Haiku</option>
                <option value="sonnet">Claude 3.5 Sonnet</option>
                <option value="opus">Claude 3 Opus</option>
              </select>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Temperature</label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={session.settings.temperature}
                  onChange={(e) => onUpdate({ 
                    settings: { 
                      ...session.settings, 
                      temperature: parseFloat(e.target.value) 
                    } 
                  })}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>Max Tokens</label>
                <input
                  type="number"
                  min="1"
                  max="8192"
                  value={session.settings.maxTokens}
                  onChange={(e) => onUpdate({ 
                    settings: { 
                      ...session.settings, 
                      maxTokens: parseInt(e.target.value) 
                    } 
                  })}
                  className="form-input"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionManager;