import React, { useState, useCallback } from 'react'
import { useSplitView } from './SplitViewContext'
import { SplitViewSettings as SettingsType } from './types'

interface SplitViewSettingsProps {
  isOpen: boolean
  onClose: () => void
}

export const SplitViewSettings: React.FC<SplitViewSettingsProps> = ({
  isOpen,
  onClose
}) => {
  const { settings, updateSettings, saveSession, loadSession, getSavedSessions, deleteSavedSession } = useSplitView()
  const [activeTab, setActiveTab] = useState<'general' | 'editor' | 'sessions'>('general')
  const [sessionName, setSessionName] = useState('')
  const [savedSessions, setSavedSessions] = useState<string[]>([])

  // Load saved sessions when component mounts
  React.useEffect(() => {
    if (isOpen) {
      setSavedSessions(getSavedSessions())
    }
  }, [isOpen, getSavedSessions])

  // Handle settings changes
  const handleSettingChange = useCallback(<K extends keyof SettingsType>(
    key: K,
    value: SettingsType[K]
  ) => {
    updateSettings({ [key]: value })
  }, [updateSettings])

  // Handle session save
  const handleSaveSession = useCallback(() => {
    if (sessionName.trim()) {
      saveSession(sessionName.trim())
      setSessionName('')
      setSavedSessions(getSavedSessions())
    }
  }, [sessionName, saveSession, getSavedSessions])

  // Handle session load
  const handleLoadSession = useCallback((name: string) => {
    loadSession(name)
    onClose()
  }, [loadSession, onClose])

  // Handle session delete
  const handleDeleteSession = useCallback((name: string) => {
    deleteSavedSession(name)
    setSavedSessions(getSavedSessions())
  }, [deleteSavedSession, getSavedSessions])

  if (!isOpen) {
    return null
  }

  return (
    <div className="split-view-settings-overlay">
      <div className="split-view-settings-modal">
        <div className="settings-header">
          <h2>Split View Settings</h2>
          <button 
            className="close-button"
            onClick={onClose}
            aria-label="Close settings"
          >
            ×
          </button>
        </div>

        <div className="settings-tabs">
          <button
            className={`tab-button ${activeTab === 'general' ? 'active' : ''}`}
            onClick={() => setActiveTab('general')}
          >
            General
          </button>
          <button
            className={`tab-button ${activeTab === 'editor' ? 'active' : ''}`}
            onClick={() => setActiveTab('editor')}
          >
            Editor
          </button>
          <button
            className={`tab-button ${activeTab === 'sessions' ? 'active' : ''}`}
            onClick={() => setActiveTab('sessions')}
          >
            Sessions
          </button>
        </div>

        <div className="settings-content">
          {activeTab === 'general' && (
            <div className="settings-section">
              <h3>General Settings</h3>
              
              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableKeyboardShortcuts}
                    onChange={(e) => handleSettingChange('enableKeyboardShortcuts', e.target.checked)}
                  />
                  Enable keyboard shortcuts
                </label>
                <p className="setting-description">
                  Enable global keyboard shortcuts for split view operations
                </p>
              </div>

              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.persistLayout}
                    onChange={(e) => handleSettingChange('persistLayout', e.target.checked)}
                  />
                  Persist layout
                </label>
                <p className="setting-description">
                  Save and restore split view configuration between sessions
                </p>
              </div>

              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.autoSave}
                    onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                  />
                  Auto-save files
                </label>
                <p className="setting-description">
                  Automatically save file changes after a delay
                </p>
              </div>

              {settings.autoSave && (
                <div className="setting-item">
                  <label>
                    Auto-save delay (ms):
                    <input
                      type="number"
                      min="500"
                      max="10000"
                      step="500"
                      value={settings.autoSaveDelay}
                      onChange={(e) => handleSettingChange('autoSaveDelay', parseInt(e.target.value))}
                    />
                  </label>
                </div>
              )}

              <div className="setting-item">
                <label>
                  Theme:
                  <select
                    value={settings.theme}
                    onChange={(e) => handleSettingChange('theme', e.target.value as 'light' | 'dark' | 'auto')}
                  >
                    <option value="auto">Auto</option>
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                  </select>
                </label>
              </div>

              <div className="setting-item">
                <label>
                  Resizer size (px):
                  <input
                    type="range"
                    min="2"
                    max="10"
                    value={settings.resizerSize}
                    onChange={(e) => handleSettingChange('resizerSize', parseInt(e.target.value))}
                  />
                  <span className="range-value">{settings.resizerSize}px</span>
                </label>
              </div>

              <div className="setting-item">
                <label>
                  Snap distance (px):
                  <input
                    type="range"
                    min="5"
                    max="50"
                    value={settings.snapDistance}
                    onChange={(e) => handleSettingChange('snapDistance', parseInt(e.target.value))}
                  />
                  <span className="range-value">{settings.snapDistance}px</span>
                </label>
              </div>
            </div>
          )}

          {activeTab === 'editor' && (
            <div className="settings-section">
              <h3>Editor Settings</h3>

              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.showMinimap}
                    onChange={(e) => handleSettingChange('showMinimap', e.target.checked)}
                  />
                  Show minimap
                </label>
              </div>

              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.wordWrap}
                    onChange={(e) => handleSettingChange('wordWrap', e.target.checked)}
                  />
                  Word wrap
                </label>
              </div>

              <div className="setting-item">
                <label>
                  Font size (px):
                  <input
                    type="range"
                    min="10"
                    max="24"
                    value={settings.fontSize}
                    onChange={(e) => handleSettingChange('fontSize', parseInt(e.target.value))}
                  />
                  <span className="range-value">{settings.fontSize}px</span>
                </label>
              </div>

              <div className="setting-item">
                <label>
                  Font family:
                  <select
                    value={settings.fontFamily}
                    onChange={(e) => handleSettingChange('fontFamily', e.target.value)}
                  >
                    <option value="'JetBrains Mono', 'Fira Code', Consolas, monospace">JetBrains Mono</option>
                    <option value="'Fira Code', Consolas, monospace">Fira Code</option>
                    <option value="Consolas, monospace">Consolas</option>
                    <option value="'Monaco', monospace">Monaco</option>
                    <option value="'Source Code Pro', monospace">Source Code Pro</option>
                  </select>
                </label>
              </div>

              <div className="setting-item">
                <label>
                  Tab size:
                  <select
                    value={settings.tabSize}
                    onChange={(e) => handleSettingChange('tabSize', parseInt(e.target.value))}
                  >
                    <option value={2}>2 spaces</option>
                    <option value={4}>4 spaces</option>
                    <option value={8}>8 spaces</option>
                  </select>
                </label>
              </div>

              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.insertSpaces}
                    onChange={(e) => handleSettingChange('insertSpaces', e.target.checked)}
                  />
                  Insert spaces (instead of tabs)
                </label>
              </div>
            </div>
          )}

          {activeTab === 'sessions' && (
            <div className="settings-section">
              <h3>Session Management</h3>

              <div className="session-save">
                <h4>Save Current Session</h4>
                <div className="session-input-group">
                  <input
                    type="text"
                    placeholder="Session name"
                    value={sessionName}
                    onChange={(e) => setSessionName(e.target.value)}
                  />
                  <button 
                    onClick={handleSaveSession}
                    disabled={!sessionName.trim()}
                  >
                    Save
                  </button>
                </div>
              </div>

              <div className="session-list">
                <h4>Saved Sessions</h4>
                {savedSessions.length === 0 ? (
                  <p className="no-sessions">No saved sessions</p>
                ) : (
                  <div className="sessions">
                    {savedSessions.map((session) => (
                      <div key={session} className="session-item">
                        <span className="session-name">{session}</span>
                        <div className="session-actions">
                          <button
                            className="load-button"
                            onClick={() => handleLoadSession(session)}
                          >
                            Load
                          </button>
                          <button
                            className="delete-button"
                            onClick={() => handleDeleteSession(session)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="settings-footer">
          <button 
            className="apply-button"
            onClick={onClose}
          >
            Apply & Close
          </button>
        </div>
      </div>

      <style jsx>{`
        .split-view-settings-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 2000;
          backdrop-filter: blur(4px);
        }

        .split-view-settings-modal {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
          width: 90vw;
          max-width: 600px;
          max-height: 80vh;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .settings-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid #e0e0e0;
          background-color: #f8f9fa;
        }

        .settings-header h2 {
          margin: 0;
          font-size: 1.5rem;
          font-weight: 600;
          color: #333;
        }

        .close-button {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #666;
          padding: 4px;
          border-radius: 4px;
          transition: background-color 0.2s ease;
        }

        .close-button:hover {
          background-color: #e0e0e0;
        }

        .settings-tabs {
          display: flex;
          border-bottom: 1px solid #e0e0e0;
          background-color: #f8f9fa;
        }

        .tab-button {
          flex: 1;
          padding: 12px 16px;
          background: none;
          border: none;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          color: #666;
          transition: all 0.2s ease;
          border-bottom: 2px solid transparent;
        }

        .tab-button:hover {
          background-color: #e0e0e0;
        }

        .tab-button.active {
          color: #007acc;
          border-bottom-color: #007acc;
          background-color: white;
        }

        .settings-content {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
        }

        .settings-section h3 {
          margin: 0 0 20px 0;
          font-size: 1.25rem;
          font-weight: 600;
          color: #333;
        }

        .setting-item {
          margin-bottom: 20px;
        }

        .setting-item label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 500;
          color: #333;
          cursor: pointer;
        }

        .setting-item input[type="checkbox"] {
          width: 18px;
          height: 18px;
          accent-color: #007acc;
        }

        .setting-item input[type="number"],
        .setting-item input[type="range"],
        .setting-item select {
          margin-left: auto;
          padding: 6px 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .setting-item input[type="range"] {
          width: 120px;
        }

        .range-value {
          margin-left: 8px;
          font-weight: 600;
          color: #007acc;
          min-width: 40px;
        }

        .setting-description {
          margin: 4px 0 0 26px;
          font-size: 13px;
          color: #666;
          line-height: 1.4;
        }

        .session-save,
        .session-list {
          margin-bottom: 24px;
        }

        .session-save h4,
        .session-list h4 {
          margin: 0 0 12px 0;
          font-size: 1rem;
          font-weight: 600;
          color: #333;
        }

        .session-input-group {
          display: flex;
          gap: 8px;
        }

        .session-input-group input {
          flex: 1;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .session-input-group button {
          padding: 8px 16px;
          background-color: #007acc;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 14px;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }

        .session-input-group button:hover:not(:disabled) {
          background-color: #0056b3;
        }

        .session-input-group button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }

        .no-sessions {
          color: #666;
          font-style: italic;
          text-align: center;
          padding: 20px;
        }

        .sessions {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .session-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background-color: #f8f9fa;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
        }

        .session-name {
          font-weight: 500;
          color: #333;
        }

        .session-actions {
          display: flex;
          gap: 8px;
        }

        .load-button,
        .delete-button {
          padding: 4px 12px;
          border: none;
          border-radius: 4px;
          font-size: 13px;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }

        .load-button {
          background-color: #28a745;
          color: white;
        }

        .load-button:hover {
          background-color: #218838;
        }

        .delete-button {
          background-color: #dc3545;
          color: white;
        }

        .delete-button:hover {
          background-color: #c82333;
        }

        .settings-footer {
          padding: 16px 20px;
          border-top: 1px solid #e0e0e0;
          background-color: #f8f9fa;
          display: flex;
          justify-content: flex-end;
        }

        .apply-button {
          padding: 10px 24px;
          background-color: #007acc;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }

        .apply-button:hover {
          background-color: #0056b3;
        }

        /* Dark theme support */
        @media (prefers-color-scheme: dark) {
          .split-view-settings-modal {
            background-color: #2d2d2d;
            color: white;
          }

          .settings-header,
          .settings-tabs,
          .settings-footer {
            background-color: #1a1a1a;
            border-color: #404040;
          }

          .settings-header h2,
          .settings-section h3,
          .session-save h4,
          .session-list h4,
          .setting-item label,
          .session-name {
            color: white;
          }

          .close-button,
          .tab-button {
            color: #ccc;
          }

          .close-button:hover {
            background-color: #404040;
          }

          .tab-button:hover {
            background-color: #404040;
          }

          .tab-button.active {
            background-color: #2d2d2d;
          }

          .setting-item input,
          .setting-item select,
          .session-input-group input {
            background-color: #404040;
            border-color: #555;
            color: white;
          }

          .session-item {
            background-color: #404040;
            border-color: #555;
          }
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
          .split-view-settings-modal {
            width: 95vw;
            max-height: 90vh;
          }

          .settings-header {
            padding: 16px;
          }

          .settings-content {
            padding: 16px;
          }

          .tab-button {
            padding: 10px 12px;
            font-size: 13px;
          }

          .setting-item label {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
          }

          .setting-item input[type="number"],
          .setting-item input[type="range"],
          .setting-item select {
            margin-left: 0;
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}

export default SplitViewSettings