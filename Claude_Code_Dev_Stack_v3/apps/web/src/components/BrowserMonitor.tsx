/**
 * Claude Code Browser Monitor Component
 * ====================================
 * 
 * Integrates the Claude Code Browser (@zainhoda, AGPL-3.0) monitoring
 * capabilities into the Dev Stack v3.0 PWA while maintaining proper
 * attribution and license compliance.
 */

import React, { useState, useEffect } from 'react';
import { Monitor, Activity, Database, Users, Clock, Eye, ExternalLink } from 'lucide-react';

interface BrowserSession {
  uuid: string;
  filename: string;
  modTime: string;
  size: number;
  latestTodos: any;
}

interface BrowserProject {
  name: string;
  path: string;
  modTime: string;
  sessions: BrowserSession[];
}

interface BrowserMonitorProps {
  apiUrl?: string;
}

export const BrowserMonitor: React.FC<BrowserMonitorProps> = ({ 
  apiUrl = 'http://localhost:8081' 
}) => {
  const [projects, setProjects] = useState<BrowserProject[]>([]);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [sessions, setSessions] = useState<BrowserSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [attribution, setAttribution] = useState<any>(null);

  useEffect(() => {
    loadProjects();
    loadAttribution();
  }, []);

  const loadProjects = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch projects from the adapter API which proxies to original browser
      const response = await fetch(`${apiUrl}/api/browser/projects`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setProjects(data.projects || []);
      setIsConnected(true);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
      setIsConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  const loadAttribution = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/attribution`);
      if (response.ok) {
        const data = await response.json();
        setAttribution(data);
      }
    } catch (err) {
      console.warn('Failed to load attribution info:', err);
    }
  };

  const loadProjectSessions = async (projectName: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiUrl}/api/browser/project/${projectName}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setSessions(data.sessions || []);
      setSelectedProject(projectName);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setIsLoading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const openOriginalBrowser = () => {
    window.open('http://localhost:8080', '_blank');
  };

  const openSession = (projectName: string, sessionUuid: string) => {
    window.open(`http://localhost:8080/session/${projectName}/${sessionUuid}`, '_blank');
  };

  return (
    <div className="browser-monitor p-6 bg-white rounded-lg shadow-lg">
      {/* Header with Attribution */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Monitor className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">
            Claude Code Browser Monitor
          </h2>
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        </div>
        
        <button
          onClick={openOriginalBrowser}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          <span>Open Full Browser</span>
        </button>
      </div>

      {/* Attribution Notice */}
      {attribution && (
        <div className="mb-6 p-4 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg">
          <div className="flex items-start space-x-2">
            <Eye className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <p className="text-sm text-blue-800">
                <strong>Claude Code Browser</strong> by{' '}
                <a 
                  href="https://github.com/zainhoda" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="underline hover:text-blue-900"
                >
                  @zainhoda
                </a>
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Licensed under AGPL-3.0 • Integrated via adapter pattern
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg">
          <p className="text-red-800">
            <strong>Connection Error:</strong> {error}
          </p>
          <button
            onClick={loadProjects}
            className="mt-2 text-red-600 hover:text-red-800 underline text-sm"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading...</span>
        </div>
      )}

      {/* Projects List */}
      {!isLoading && !selectedProject && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <Database className="w-5 h-5" />
            <span>Claude Code Projects ({projects.length})</span>
          </h3>
          
          {projects.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Database className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No Claude Code projects found</p>
              <p className="text-sm">Projects are stored in ~/.claude/projects/</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {projects.map((project) => (
                <div
                  key={project.name}
                  onClick={() => loadProjectSessions(project.name)}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Users className="w-5 h-5 text-gray-500" />
                      <div>
                        <h4 className="font-medium text-gray-900">{project.name}</h4>
                        <p className="text-sm text-gray-500">
                          {project.sessions?.length || 0} sessions
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="flex items-center space-x-1 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        <span>{formatTimeAgo(project.modTime)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Sessions List */}
      {!isLoading && selectedProject && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>Sessions in {selectedProject}</span>
            </h3>
            
            <button
              onClick={() => {
                setSelectedProject(null);
                setSessions([]);
              }}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              ← Back to Projects
            </button>
          </div>
          
          {sessions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Activity className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No sessions found in this project</p>
            </div>
          ) : (
            <div className="space-y-3">
              {sessions.map((session) => (
                <div
                  key={session.uuid}
                  onClick={() => openSession(selectedProject, session.uuid)}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <div>
                        <h4 className="font-mono text-sm text-gray-900">
                          {session.uuid.substring(0, 8)}...
                        </h4>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(session.size)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="flex items-center space-x-1 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        <span>{formatTimeAgo(session.modTime)}</span>
                      </div>
                      <ExternalLink className="w-4 h-4 text-gray-400 mt-1" />
                    </div>
                  </div>
                  
                  {session.latestTodos && (
                    <div className="mt-2 text-xs text-gray-600">
                      Latest todos: {session.latestTodos.todos?.length || 0} items
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};