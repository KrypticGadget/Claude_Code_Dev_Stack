/**
 * Claude Code Browser Monitor Component
 * ====================================
 * 
 * Integrates the Claude Code Browser (@zainhoda, AGPL-3.0) monitoring
 * capabilities into the Dev Stack v3.0 PWA while maintaining proper
 * attribution and license compliance.
 */

import React, { useState, useEffect } from 'react';
import { Monitor, Activity, Database, Users, Clock, Eye, ExternalLink, Command, Zap, Code, Terminal } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

interface BrowserSession {
  uuid: string;
  filename: string;
  modTime: string;
  size: number;
  latestTodos: any;
  project_name?: string;
  content_preview?: string;
  session_type?: string;
  tags?: string[];
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
  const [devStackCommands, setDevStackCommands] = useState<any[]>([]);
  const [realTimeData, setRealTimeData] = useState<any>(null);
  const [commandInput, setCommandInput] = useState('');
  const [commandHistory, setCommandHistory] = useState<any[]>([]);
  
  // WebSocket connection for real-time updates
  const { data: wsData, isConnected: wsConnected, send: wsSend } = useWebSocket(
    `ws://localhost:8081/ws`, 
    {
      reconnectInterval: 2000,
      heartbeatInterval: 30000,
      maxReconnectAttempts: 5
    }
  );

  useEffect(() => {
    loadProjects();
    loadAttribution();
  }, []);

  // Handle WebSocket data updates
  useEffect(() => {
    if (wsData) {
      console.log('📡 WebSocket data received:', wsData);
      
      switch (wsData.type) {
        case 'projects_update':
          setProjects(wsData.projects || []);
          setRealTimeData(wsData);
          break;
        
        case 'project_sessions':
          setSessions(wsData.sessions || []);
          break;
        
        case 'session_content':
          if (wsData.dev_stack_commands) {
            setDevStackCommands(wsData.dev_stack_commands);
          }
          break;
        
        case 'command_executed':
          setCommandHistory(prev => [wsData, ...prev.slice(0, 49)]); // Keep last 50
          break;
        
        case 'data_update':
          setProjects(wsData.projects || []);
          setRealTimeData(wsData);
          break;
        
        case 'system_status':
          setRealTimeData(wsData);
          break;
      }
    }
  }, [wsData]);

  // Update connection status based on WebSocket
  useEffect(() => {
    setIsConnected(wsConnected);
  }, [wsConnected]);

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
      // Try WebSocket first for real-time data
      if (wsSend) {
        wsSend({
          type: 'get_project_sessions',
          project_name: projectName
        });
      }
      
      // Fallback to HTTP API
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

  const executeDevStackCommand = async (command: string, sessionUuid?: string) => {
    if (!command.trim()) return;
    
    try {
      // Send via WebSocket for real-time execution
      if (wsSend) {
        wsSend({
          type: 'execute_dev_stack_command',
          command: {
            command: command,
            agent_target: extractAgentTarget(command),
            parameters: parseCommandParameters(command),
            execution_context: {
              session_uuid: sessionUuid,
              source: 'browser_monitor_ui'
            }
          },
          session_uuid: sessionUuid
        });
      }
      
      // Also send via HTTP API for reliability
      const response = await fetch(`${apiUrl}/api/commands/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          command: command,
          agent_target: extractAgentTarget(command),
          parameters: parseCommandParameters(command),
          session_uuid: sessionUuid,
          execution_context: {
            source: 'browser_monitor_ui',
            timestamp: new Date().toISOString()
          }
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setCommandHistory(prev => [result, ...prev.slice(0, 49)]);
      }
      
    } catch (err) {
      console.error('Failed to execute command:', err);
      setError(`Command execution failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const extractAgentTarget = (command: string): string | null => {
    const agentMatch = command.match(/@agent-([a-z-]+)/i);
    return agentMatch ? agentMatch[1] : null;
  };

  const parseCommandParameters = (command: string): Record<string, any> => {
    const params: Record<string, any> = { raw_command: command };
    
    // Parse common patterns
    const orchestrateMatch = command.match(/!orchestrate\s+(.+)/i);
    if (orchestrateMatch) {
      params.orchestration_request = orchestrateMatch[1];
    }
    
    const statusMatch = command.match(/\?status\s+(.+)/i);
    if (statusMatch) {
      params.status_query = statusMatch[1];
    }
    
    const contextMatch = command.match(/@context\s+(\w+)\s*(.*)?/i);
    if (contextMatch) {
      params.context_operation = contextMatch[1];
      params.context_parameters = contextMatch[2] || '';
    }
    
    return params;
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
      {/* Header with Attribution and Real-time Status */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Monitor className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">
            Claude Code Browser Monitor
          </h2>
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          {wsConnected && (
            <div className="flex items-center space-x-2 bg-green-50 px-3 py-1 rounded-full">
              <Zap className="w-4 h-4 text-green-600" />
              <span className="text-sm text-green-700">Live</span>
            </div>
          )}
          {realTimeData && (
            <div className="text-sm text-gray-600">
              Last update: {new Date(realTimeData.timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => executeDevStackCommand('?status system')}
            className="flex items-center space-x-2 px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <Terminal className="w-4 h-4" />
            <span>System Status</span>
          </button>
          <button
            onClick={openOriginalBrowser}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            <span>Open Full Browser</span>
          </button>
        </div>
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

      {/* Dev Stack Command Interface */}
      <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <div className="flex items-center space-x-2 mb-3">
          <Command className="w-5 h-5 text-gray-700" />
          <h3 className="font-semibold text-gray-900">Dev Stack Command Interface</h3>
        </div>
        
        <div className="flex space-x-2">
          <input
            type="text"
            value={commandInput}
            onChange={(e) => setCommandInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                executeDevStackCommand(commandInput);
                setCommandInput('');
              }
            }}
            placeholder="Enter Dev Stack command (e.g., @agent-api-integration, !orchestrate, ?status)"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => {
              executeDevStackCommand(commandInput);
              setCommandInput('');
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Execute
          </button>
        </div>
        
        {/* Quick Command Buttons */}
        <div className="flex flex-wrap gap-2 mt-3">
          {[
            { label: 'API Integration', cmd: '@agent-api-integration analyze current project' },
            { label: 'System Status', cmd: '?status all' },
            { label: 'Orchestrate', cmd: '!orchestrate frontend and backend agents' },
            { label: 'Context Snapshot', cmd: '@context snapshot current' }
          ].map((quickCmd) => (
            <button
              key={quickCmd.label}
              onClick={() => executeDevStackCommand(quickCmd.cmd)}
              className="px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              {quickCmd.label}
            </button>
          ))}
        </div>
      </div>

      {/* Dev Stack Commands Found in Sessions */}
      {devStackCommands.length > 0 && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-3">
            <Code className="w-5 h-5 text-yellow-700" />
            <h3 className="font-semibold text-yellow-900">Dev Stack Commands Found</h3>
          </div>
          
          <div className="space-y-2">
            {devStackCommands.slice(0, 5).map((cmd, index) => (
              <div key={index} className="flex items-center justify-between bg-white p-2 rounded border">
                <span className="font-mono text-sm text-gray-700">{cmd.command}</span>
                <button
                  onClick={() => executeDevStackCommand(cmd.command, cmd.session_uuid)}
                  className="px-2 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-700"
                >
                  Execute
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Command History */}
      {commandHistory.length > 0 && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-3">
            <Activity className="w-5 h-5 text-green-700" />
            <h3 className="font-semibold text-green-900">Recent Command Executions</h3>
          </div>
          
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {commandHistory.slice(0, 10).map((execution, index) => (
              <div key={index} className="bg-white p-3 rounded border">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-sm text-gray-700">
                    {execution.command?.command || execution.result?.command || 'Unknown command'}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    execution.result?.success || execution.success 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {execution.result?.success || execution.success ? 'Success' : 'Failed'}
                  </span>
                </div>
                {execution.timestamp && (
                  <div className="text-xs text-gray-500">
                    {new Date(execution.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
            ))}
          </div>
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
                      <div className={`w-2 h-2 rounded-full ${
                        session.tags?.includes('dev_stack_commands') ? 'bg-purple-500' : 'bg-green-500'
                      }`}></div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h4 className="font-mono text-sm text-gray-900">
                            {session.uuid.substring(0, 8)}...
                          </h4>
                          {session.tags?.includes('dev_stack_commands') && (
                            <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                              Dev Stack
                            </span>
                          )}
                          {session.tags?.includes('orchestration_capable') && (
                            <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                              Orchestration
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(session.size)}
                        </p>
                        {session.content_preview && (
                          <p className="text-xs text-gray-600 mt-1 truncate max-w-md">
                            {session.content_preview.substring(0, 100)}...
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="flex items-center space-x-1 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        <span>{formatTimeAgo(session.modTime)}</span>
                      </div>
                      <div className="flex items-center space-x-1 mt-1">
                        <ExternalLink className="w-4 h-4 text-gray-400" />
                        {session.tags?.includes('dev_stack_commands') && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              // Load session content to get Dev Stack commands
                              if (wsSend) {
                                wsSend({
                                  type: 'get_session_content',
                                  session_uuid: session.uuid
                                });
                              }
                            }}
                            className="ml-2 px-2 py-1 text-xs bg-purple-600 text-white rounded hover:bg-purple-700"
                          >
                            <Command className="w-3 h-3" />
                          </button>
                        )}
                      </div>
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