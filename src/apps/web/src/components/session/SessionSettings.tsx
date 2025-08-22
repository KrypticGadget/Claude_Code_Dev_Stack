import React, { useState, useEffect, useCallback } from 'react';
import { 
  Settings, 
  Save, 
  RotateCcw, 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  Zap, 
  Brain, 
  Shield, 
  Clock,
  HardDrive,
  Network,
  Eye,
  EyeOff,
  Copy,
  Download,
  Upload
} from 'lucide-react';
import './SessionSettings.css';

interface SessionConfig {
  model: 'opus' | 'sonnet' | 'haiku';
  temperature: number;
  maxTokens: number;
  contextWindow: number;
  systemPrompt: string;
  stopSequences: string[];
  topP: number;
  topK: number;
  presencePenalty: number;
  frequencyPenalty: number;
  timeout: number;
  retryAttempts: number;
  streaming: boolean;
  logLevel: 'error' | 'warn' | 'info' | 'debug';
  saveHistory: boolean;
  autoSave: boolean;
  backupInterval: number;
  rateLimiting: {
    enabled: boolean;
    requestsPerMinute: number;
    tokensPerMinute: number;
  };
  security: {
    sanitizeInput: boolean;
    blockCodeExecution: boolean;
    allowFileAccess: boolean;
    allowNetworkAccess: boolean;
  };
  performance: {
    cacheResponses: boolean;
    preloadContext: boolean;
    optimizeMemory: boolean;
    parallelProcessing: boolean;
  };
  monitoring: {
    trackTokenUsage: boolean;
    trackPerformance: boolean;
    alertOnErrors: boolean;
    logConversations: boolean;
  };
}

interface SessionSettingsProps {
  sessionId: string;
  config: SessionConfig;
  onConfigChange: (config: SessionConfig) => void;
  onSave: () => void;
  onReset: () => void;
  className?: string;
}

const defaultConfig: SessionConfig = {
  model: 'sonnet',
  temperature: 0.7,
  maxTokens: 4000,
  contextWindow: 200000,
  systemPrompt: '',
  stopSequences: [],
  topP: 1.0,
  topK: 0,
  presencePenalty: 0,
  frequencyPenalty: 0,
  timeout: 30000,
  retryAttempts: 3,
  streaming: true,
  logLevel: 'info',
  saveHistory: true,
  autoSave: true,
  backupInterval: 300000,
  rateLimiting: {
    enabled: true,
    requestsPerMinute: 60,
    tokensPerMinute: 100000
  },
  security: {
    sanitizeInput: true,
    blockCodeExecution: false,
    allowFileAccess: true,
    allowNetworkAccess: false
  },
  performance: {
    cacheResponses: true,
    preloadContext: true,
    optimizeMemory: true,
    parallelProcessing: false
  },
  monitoring: {
    trackTokenUsage: true,
    trackPerformance: true,
    alertOnErrors: true,
    logConversations: true
  }
};

export const SessionSettings: React.FC<SessionSettingsProps> = ({
  sessionId,
  config,
  onConfigChange,
  onSave,
  onReset,
  className
}) => {
  const [activeTab, setActiveTab] = useState<'model' | 'behavior' | 'security' | 'performance' | 'monitoring'>('model');
  const [isDirty, setIsDirty] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);

  // Track config changes
  useEffect(() => {
    setIsDirty(JSON.stringify(config) !== JSON.stringify(defaultConfig));
  }, [config]);

  // Validate configuration
  const validateConfig = useCallback((cfg: SessionConfig): Record<string, string> => {
    const errors: Record<string, string> = {};

    if (cfg.temperature < 0 || cfg.temperature > 1) {
      errors.temperature = 'Temperature must be between 0 and 1';
    }

    if (cfg.maxTokens < 1 || cfg.maxTokens > 8192) {
      errors.maxTokens = 'Max tokens must be between 1 and 8192';
    }

    if (cfg.contextWindow < 1000 || cfg.contextWindow > 1000000) {
      errors.contextWindow = 'Context window must be between 1,000 and 1,000,000';
    }

    if (cfg.topP < 0 || cfg.topP > 1) {
      errors.topP = 'Top P must be between 0 and 1';
    }

    if (cfg.topK < 0 || cfg.topK > 100) {
      errors.topK = 'Top K must be between 0 and 100';
    }

    if (cfg.timeout < 1000 || cfg.timeout > 300000) {
      errors.timeout = 'Timeout must be between 1 and 300 seconds';
    }

    if (cfg.retryAttempts < 0 || cfg.retryAttempts > 10) {
      errors.retryAttempts = 'Retry attempts must be between 0 and 10';
    }

    return errors;
  }, []);

  // Update configuration
  const updateConfig = useCallback((updates: Partial<SessionConfig>) => {
    const newConfig = { ...config, ...updates };
    const errors = validateConfig(newConfig);
    setValidationErrors(errors);
    onConfigChange(newConfig);
  }, [config, onConfigChange, validateConfig]);

  // Update nested configuration
  const updateNestedConfig = useCallback((path: string, updates: any) => {
    const pathArray = path.split('.');
    const newConfig = { ...config };
    let current = newConfig as any;
    
    for (let i = 0; i < pathArray.length - 1; i++) {
      current[pathArray[i]] = { ...current[pathArray[i]] };
      current = current[pathArray[i]];
    }
    
    current[pathArray[pathArray.length - 1]] = { ...current[pathArray[pathArray.length - 1]], ...updates };
    
    const errors = validateConfig(newConfig);
    setValidationErrors(errors);
    onConfigChange(newConfig);
  }, [config, onConfigChange, validateConfig]);

  // Export configuration
  const exportConfig = () => {
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `session-config-${sessionId}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Import configuration
  const importConfig = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedConfig = JSON.parse(e.target?.result as string);
        onConfigChange(importedConfig);
      } catch (error) {
        console.error('Failed to import configuration:', error);
      }
    };
    reader.readAsText(file);
  };

  // Copy configuration to clipboard
  const copyConfig = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(config, null, 2));
    } catch (error) {
      console.error('Failed to copy configuration:', error);
    }
  };

  // Model options
  const modelOptions = [
    {
      value: 'haiku',
      label: 'Claude 3 Haiku',
      description: 'Fast and efficient for simple tasks',
      cost: 'Low',
      speed: 'Fast'
    },
    {
      value: 'sonnet',
      label: 'Claude 3.5 Sonnet',
      description: 'Balanced performance and capability',
      cost: 'Medium',
      speed: 'Medium'
    },
    {
      value: 'opus',
      label: 'Claude 3 Opus',
      description: 'Most capable for complex reasoning',
      cost: 'High',
      speed: 'Slow'
    }
  ];

  return (
    <div className={`session-settings ${className || ''}`}>
      {/* Header */}
      <div className="settings-header">
        <div className="header-title">
          <h2>Session Settings</h2>
          <p>Configure Claude behavior and performance</p>
        </div>

        <div className="header-actions">
          <button 
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="btn btn-secondary"
          >
            {showAdvanced ? <EyeOff size={16} /> : <Eye size={16} />}
            {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
          </button>

          <div className="config-actions">
            <button onClick={copyConfig} className="btn btn-secondary" title="Copy config">
              <Copy size={16} />
            </button>
            
            <button onClick={exportConfig} className="btn btn-secondary" title="Export config">
              <Download size={16} />
            </button>
            
            <label className="btn btn-secondary" title="Import config">
              <Upload size={16} />
              <input
                type="file"
                accept=".json"
                onChange={importConfig}
                style={{ display: 'none' }}
              />
            </label>
          </div>

          <button 
            onClick={onReset}
            className="btn btn-secondary"
            disabled={!isDirty}
          >
            <RotateCcw size={16} />
            Reset
          </button>

          <button 
            onClick={onSave}
            className="btn btn-primary"
            disabled={Object.keys(validationErrors).length > 0}
          >
            <Save size={16} />
            Save Changes
          </button>
        </div>
      </div>

      {/* Validation Errors */}
      {Object.keys(validationErrors).length > 0 && (
        <div className="validation-errors">
          <AlertTriangle size={16} />
          <span>Please fix the following errors:</span>
          <ul>
            {Object.entries(validationErrors).map(([field, error]) => (
              <li key={field}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Settings Tabs */}
      <div className="settings-tabs">
        <button 
          className={`tab-btn ${activeTab === 'model' ? 'active' : ''}`}
          onClick={() => setActiveTab('model')}
        >
          <Brain size={16} />
          Model & Behavior
        </button>
        <button 
          className={`tab-btn ${activeTab === 'behavior' ? 'active' : ''}`}
          onClick={() => setActiveTab('behavior')}
        >
          <Settings size={16} />
          Generation
        </button>
        <button 
          className={`tab-btn ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          <Shield size={16} />
          Security
        </button>
        <button 
          className={`tab-btn ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          <Zap size={16} />
          Performance
        </button>
        <button 
          className={`tab-btn ${activeTab === 'monitoring' ? 'active' : ''}`}
          onClick={() => setActiveTab('monitoring')}
        >
          <Activity size={16} />
          Monitoring
        </button>
      </div>

      {/* Settings Content */}
      <div className="settings-content">
        {activeTab === 'model' && (
          <div className="settings-section">
            <h3>Model Selection</h3>
            <div className="model-selector">
              {modelOptions.map(model => (
                <div 
                  key={model.value}
                  className={`model-option ${config.model === model.value ? 'selected' : ''}`}
                  onClick={() => updateConfig({ model: model.value as any })}
                >
                  <div className="model-info">
                    <h4>{model.label}</h4>
                    <p>{model.description}</p>
                  </div>
                  <div className="model-specs">
                    <span className="spec">Cost: {model.cost}</span>
                    <span className="spec">Speed: {model.speed}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="form-group">
              <label htmlFor="context-window">Context Window</label>
              <input
                id="context-window"
                type="number"
                min="1000"
                max="1000000"
                step="1000"
                value={config.contextWindow}
                onChange={(e) => updateConfig({ contextWindow: parseInt(e.target.value) })}
                className={`form-input ${validationErrors.contextWindow ? 'error' : ''}`}
              />
              <span className="form-help">Maximum tokens that can be processed in context</span>
              {validationErrors.contextWindow && (
                <span className="error-message">{validationErrors.contextWindow}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="system-prompt">System Prompt</label>
              <div className="textarea-wrapper">
                <textarea
                  id="system-prompt"
                  value={config.systemPrompt}
                  onChange={(e) => updateConfig({ systemPrompt: e.target.value })}
                  placeholder="Enter system instructions for Claude..."
                  className="form-textarea"
                  rows={showSystemPrompt ? 8 : 3}
                />
                <button
                  type="button"
                  onClick={() => setShowSystemPrompt(!showSystemPrompt)}
                  className="expand-btn"
                >
                  {showSystemPrompt ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
              <span className="form-help">Instructions that guide Claude's behavior throughout the session</span>
            </div>
          </div>
        )}

        {activeTab === 'behavior' && (
          <div className="settings-section">
            <h3>Generation Parameters</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="temperature">Temperature</label>
                <input
                  id="temperature"
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={config.temperature}
                  onChange={(e) => updateConfig({ temperature: parseFloat(e.target.value) })}
                  className={`form-input ${validationErrors.temperature ? 'error' : ''}`}
                />
                <span className="form-help">Controls randomness (0 = deterministic, 1 = creative)</span>
                {validationErrors.temperature && (
                  <span className="error-message">{validationErrors.temperature}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="max-tokens">Max Tokens</label>
                <input
                  id="max-tokens"
                  type="number"
                  min="1"
                  max="8192"
                  value={config.maxTokens}
                  onChange={(e) => updateConfig({ maxTokens: parseInt(e.target.value) })}
                  className={`form-input ${validationErrors.maxTokens ? 'error' : ''}`}
                />
                <span className="form-help">Maximum tokens in response</span>
                {validationErrors.maxTokens && (
                  <span className="error-message">{validationErrors.maxTokens}</span>
                )}
              </div>
            </div>

            {showAdvanced && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="top-p">Top P</label>
                    <input
                      id="top-p"
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={config.topP}
                      onChange={(e) => updateConfig({ topP: parseFloat(e.target.value) })}
                      className={`form-input ${validationErrors.topP ? 'error' : ''}`}
                    />
                    <span className="form-help">Nucleus sampling threshold</span>
                  </div>

                  <div className="form-group">
                    <label htmlFor="top-k">Top K</label>
                    <input
                      id="top-k"
                      type="number"
                      min="0"
                      max="100"
                      value={config.topK}
                      onChange={(e) => updateConfig({ topK: parseInt(e.target.value) })}
                      className={`form-input ${validationErrors.topK ? 'error' : ''}`}
                    />
                    <span className="form-help">Limit vocabulary to top K tokens (0 = disabled)</span>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="presence-penalty">Presence Penalty</label>
                    <input
                      id="presence-penalty"
                      type="number"
                      min="-2"
                      max="2"
                      step="0.1"
                      value={config.presencePenalty}
                      onChange={(e) => updateConfig({ presencePenalty: parseFloat(e.target.value) })}
                      className="form-input"
                    />
                    <span className="form-help">Penalize tokens based on presence in text</span>
                  </div>

                  <div className="form-group">
                    <label htmlFor="frequency-penalty">Frequency Penalty</label>
                    <input
                      id="frequency-penalty"
                      type="number"
                      min="-2"
                      max="2"
                      step="0.1"
                      value={config.frequencyPenalty}
                      onChange={(e) => updateConfig({ frequencyPenalty: parseFloat(e.target.value) })}
                      className="form-input"
                    />
                    <span className="form-help">Penalize tokens based on frequency in text</span>
                  </div>
                </div>
              </>
            )}

            <div className="form-group">
              <label htmlFor="stop-sequences">Stop Sequences</label>
              <input
                id="stop-sequences"
                type="text"
                value={config.stopSequences.join(', ')}
                onChange={(e) => updateConfig({ 
                  stopSequences: e.target.value.split(',').map(s => s.trim()).filter(s => s) 
                })}
                placeholder="Enter stop sequences separated by commas"
                className="form-input"
              />
              <span className="form-help">Sequences that will stop generation</span>
            </div>

            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.streaming}
                  onChange={(e) => updateConfig({ streaming: e.target.checked })}
                />
                <span>Enable streaming responses</span>
              </label>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="settings-section">
            <h3>Security Settings</h3>
            
            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.security.sanitizeInput}
                  onChange={(e) => updateNestedConfig('security', { sanitizeInput: e.target.checked })}
                />
                <span>Sanitize user input</span>
                <Info size={14} className="info-icon" title="Remove potentially harmful content from inputs" />
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.security.blockCodeExecution}
                  onChange={(e) => updateNestedConfig('security', { blockCodeExecution: e.target.checked })}
                />
                <span>Block code execution requests</span>
                <Info size={14} className="info-icon" title="Prevent Claude from executing code or system commands" />
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.security.allowFileAccess}
                  onChange={(e) => updateNestedConfig('security', { allowFileAccess: e.target.checked })}
                />
                <span>Allow file system access</span>
                <Info size={14} className="info-icon" title="Enable Claude to read and write files" />
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.security.allowNetworkAccess}
                  onChange={(e) => updateNestedConfig('security', { allowNetworkAccess: e.target.checked })}
                />
                <span>Allow network access</span>
                <Info size={14} className="info-icon" title="Enable Claude to make network requests" />
              </label>
            </div>

            <h4>Rate Limiting</h4>
            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.rateLimiting.enabled}
                  onChange={(e) => updateNestedConfig('rateLimiting', { enabled: e.target.checked })}
                />
                <span>Enable rate limiting</span>
              </label>
            </div>

            {config.rateLimiting.enabled && (
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="requests-per-minute">Requests per minute</label>
                  <input
                    id="requests-per-minute"
                    type="number"
                    min="1"
                    max="1000"
                    value={config.rateLimiting.requestsPerMinute}
                    onChange={(e) => updateNestedConfig('rateLimiting', { 
                      requestsPerMinute: parseInt(e.target.value) 
                    })}
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="tokens-per-minute">Tokens per minute</label>
                  <input
                    id="tokens-per-minute"
                    type="number"
                    min="1000"
                    max="1000000"
                    step="1000"
                    value={config.rateLimiting.tokensPerMinute}
                    onChange={(e) => updateNestedConfig('rateLimiting', { 
                      tokensPerMinute: parseInt(e.target.value) 
                    })}
                    className="form-input"
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="settings-section">
            <h3>Performance Optimization</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="timeout">Request timeout (ms)</label>
                <input
                  id="timeout"
                  type="number"
                  min="1000"
                  max="300000"
                  step="1000"
                  value={config.timeout}
                  onChange={(e) => updateConfig({ timeout: parseInt(e.target.value) })}
                  className={`form-input ${validationErrors.timeout ? 'error' : ''}`}
                />
                <span className="form-help">Maximum time to wait for response</span>
                {validationErrors.timeout && (
                  <span className="error-message">{validationErrors.timeout}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="retry-attempts">Retry attempts</label>
                <input
                  id="retry-attempts"
                  type="number"
                  min="0"
                  max="10"
                  value={config.retryAttempts}
                  onChange={(e) => updateConfig({ retryAttempts: parseInt(e.target.value) })}
                  className={`form-input ${validationErrors.retryAttempts ? 'error' : ''}`}
                />
                <span className="form-help">Number of retries on failure</span>
                {validationErrors.retryAttempts && (
                  <span className="error-message">{validationErrors.retryAttempts}</span>
                )}
              </div>
            </div>

            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.performance.cacheResponses}
                  onChange={(e) => updateNestedConfig('performance', { cacheResponses: e.target.checked })}
                />
                <span>Cache responses</span>
                <Info size={14} className="info-icon" title="Cache similar requests to improve response time" />
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.performance.preloadContext}
                  onChange={(e) => updateNestedConfig('performance', { preloadContext: e.target.checked })}
                />
                <span>Preload context</span>
                <Info size={14} className="info-icon" title="Load context in advance to reduce latency" />
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.performance.optimizeMemory}
                  onChange={(e) => updateNestedConfig('performance', { optimizeMemory: e.target.checked })}
                />
                <span>Optimize memory usage</span>
                <Info size={14} className="info-icon" title="Reduce memory footprint at the cost of some performance" />
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.performance.parallelProcessing}
                  onChange={(e) => updateNestedConfig('performance', { parallelProcessing: e.target.checked })}
                />
                <span>Parallel processing</span>
                <Info size={14} className="info-icon" title="Process multiple requests concurrently" />
              </label>
            </div>
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div className="settings-section">
            <h3>Monitoring & Logging</h3>
            
            <div className="form-group">
              <label htmlFor="log-level">Log Level</label>
              <select
                id="log-level"
                value={config.logLevel}
                onChange={(e) => updateConfig({ logLevel: e.target.value as any })}
                className="form-select"
              >
                <option value="error">Error</option>
                <option value="warn">Warning</option>
                <option value="info">Info</option>
                <option value="debug">Debug</option>
              </select>
              <span className="form-help">Minimum level for log messages</span>
            </div>

            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.monitoring.trackTokenUsage}
                  onChange={(e) => updateNestedConfig('monitoring', { trackTokenUsage: e.target.checked })}
                />
                <span>Track token usage</span>
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.monitoring.trackPerformance}
                  onChange={(e) => updateNestedConfig('monitoring', { trackPerformance: e.target.checked })}
                />
                <span>Track performance metrics</span>
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.monitoring.alertOnErrors}
                  onChange={(e) => updateNestedConfig('monitoring', { alertOnErrors: e.target.checked })}
                />
                <span>Alert on errors</span>
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.monitoring.logConversations}
                  onChange={(e) => updateNestedConfig('monitoring', { logConversations: e.target.checked })}
                />
                <span>Log conversations</span>
              </label>
            </div>

            <h4>Data Management</h4>
            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.saveHistory}
                  onChange={(e) => updateConfig({ saveHistory: e.target.checked })}
                />
                <span>Save conversation history</span>
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={config.autoSave}
                  onChange={(e) => updateConfig({ autoSave: e.target.checked })}
                />
                <span>Auto-save sessions</span>
              </label>
            </div>

            {config.autoSave && (
              <div className="form-group">
                <label htmlFor="backup-interval">Backup interval (ms)</label>
                <input
                  id="backup-interval"
                  type="number"
                  min="60000"
                  max="3600000"
                  step="60000"
                  value={config.backupInterval}
                  onChange={(e) => updateConfig({ backupInterval: parseInt(e.target.value) })}
                  className="form-input"
                />
                <span className="form-help">How often to save session backups</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Dirty State Indicator */}
      {isDirty && (
        <div className="dirty-indicator">
          <Info size={16} />
          <span>You have unsaved changes</span>
        </div>
      )}
    </div>
  );
};

export default SessionSettings;