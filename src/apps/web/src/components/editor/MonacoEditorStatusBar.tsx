import React from 'react'
import { GitStatus } from '../hooks/useGitIntegration'
import { 
  FileText, 
  Users, 
  GitBranch, 
  Wifi, 
  WifiOff, 
  Check, 
  X, 
  AlertCircle,
  Info
} from 'lucide-react'

export interface MonacoEditorStatusBarProps {
  cursorPosition: { line: number; column: number }
  selection: { selected: number; total: number }
  language: string
  readOnly: boolean
  gitStatus?: GitStatus | null
  isConnected?: boolean
  collaborators?: number
  errors?: number
  warnings?: number
  encoding?: string
  lineEnding?: 'LF' | 'CRLF'
  indentation?: { type: 'spaces' | 'tabs'; size: number }
}

export const MonacoEditorStatusBar: React.FC<MonacoEditorStatusBarProps> = ({
  cursorPosition,
  selection,
  language,
  readOnly,
  gitStatus,
  isConnected = false,
  collaborators = 0,
  errors = 0,
  warnings = 0,
  encoding = 'UTF-8',
  lineEnding = 'LF',
  indentation = { type: 'spaces', size: 2 }
}) => {
  return (
    <div className="monaco-status-bar">
      <div className="status-section status-left">
        {/* Git Status */}
        {gitStatus && (
          <div className="status-item git-status">
            <GitBranch size={14} />
            <span className="git-branch">{gitStatus.branch}</span>
            {!gitStatus.clean && (
              <span className="git-changes">
                {gitStatus.modified.length + gitStatus.added.length + gitStatus.deleted.length}
              </span>
            )}
            {gitStatus.ahead > 0 && (
              <span className="git-ahead">↑{gitStatus.ahead}</span>
            )}
            {gitStatus.behind > 0 && (
              <span className="git-behind">↓{gitStatus.behind}</span>
            )}
          </div>
        )}

        {/* Connection Status */}
        <div className={`status-item connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? <Wifi size={14} /> : <WifiOff size={14} />}
          <span>{isConnected ? 'Connected' : 'Offline'}</span>
        </div>

        {/* Collaboration Status */}
        {collaborators > 0 && (
          <div className="status-item collaboration-status">
            <Users size={14} />
            <span>{collaborators} online</span>
          </div>
        )}

        {/* Errors and Warnings */}
        {errors > 0 && (
          <div className="status-item error-status">
            <X size={14} />
            <span>{errors}</span>
          </div>
        )}
        
        {warnings > 0 && (
          <div className="status-item warning-status">
            <AlertCircle size={14} />
            <span>{warnings}</span>
          </div>
        )}
      </div>

      <div className="status-section status-center">
        {/* Read-only indicator */}
        {readOnly && (
          <div className="status-item readonly-status">
            <Info size={14} />
            <span>Read Only</span>
          </div>
        )}
      </div>

      <div className="status-section status-right">
        {/* Selection info */}
        {selection.selected > 0 && (
          <div className="status-item selection-info">
            <span>({selection.selected} selected)</span>
          </div>
        )}

        {/* Cursor position */}
        <div className="status-item cursor-position">
          <span>Ln {cursorPosition.line}, Col {cursorPosition.column}</span>
        </div>

        {/* Language */}
        <div className="status-item language-indicator">
          <FileText size={14} />
          <span className="language-name">{language.toUpperCase()}</span>
        </div>

        {/* Indentation */}
        <div className="status-item indentation-info">
          <span>
            {indentation.type === 'spaces' ? 'Spaces' : 'Tabs'}: {indentation.size}
          </span>
        </div>

        {/* Line ending */}
        <div className="status-item line-ending">
          <span>{lineEnding}</span>
        </div>

        {/* Encoding */}
        <div className="status-item encoding">
          <span>{encoding}</span>
        </div>
      </div>
    </div>
  )
}

export default MonacoEditorStatusBar