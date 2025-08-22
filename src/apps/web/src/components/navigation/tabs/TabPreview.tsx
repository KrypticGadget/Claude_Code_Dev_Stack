import React, { useEffect, useRef, useState } from 'react'
import { Tab } from '../types/TabTypes'
import '../styles/tab-preview.css'

export interface TabPreviewProps {
  tab: Tab
  position: { x: number; y: number }
  onClose: () => void
}

export const TabPreview: React.FC<TabPreviewProps> = ({
  tab,
  position,
  onClose
}) => {
  const [isVisible, setIsVisible] = useState(false)
  const previewRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Show preview with slight delay for smooth animation
    const timer = setTimeout(() => setIsVisible(true), 50)
    return () => clearTimeout(timer)
  }, [])

  // Position preview within viewport
  const previewStyle = React.useMemo(() => {
    const style: React.CSSProperties = {
      position: 'fixed',
      left: position.x,
      top: position.y,
      zIndex: 9999,
      opacity: isVisible ? 1 : 0,
      transform: `translate(-50%, 0) scale(${isVisible ? 1 : 0.95})`,
      transition: 'opacity 0.2s ease, transform 0.2s ease'
    }

    // Adjust position if preview would go off-screen
    if (typeof window !== 'undefined') {
      const previewWidth = 320
      const previewHeight = 240

      if (position.x + previewWidth / 2 > window.innerWidth) {
        style.left = window.innerWidth - previewWidth / 2 - 10
      } else if (position.x - previewWidth / 2 < 0) {
        style.left = previewWidth / 2 + 10
      }

      if (position.y + previewHeight > window.innerHeight) {
        style.top = position.y - previewHeight - 20
        style.transform = `translate(-50%, 0) scale(${isVisible ? 1 : 0.95})`
      }
    }

    return style
  }, [position, isVisible])

  // Get preview content (first few lines)
  const previewContent = React.useMemo(() => {
    const lines = tab.content.split('\n').slice(0, 15)
    return lines.join('\n')
  }, [tab.content])

  // Get file stats
  const fileStats = React.useMemo(() => {
    const lines = tab.content.split('\n').length
    const characters = tab.content.length
    const words = tab.content.split(/\s+/).filter(word => word.length > 0).length

    return { lines, characters, words }
  }, [tab.content])

  return (
    <div
      ref={previewRef}
      className="tab-preview"
      style={previewStyle}
      onMouseLeave={onClose}
    >
      {/* Preview Header */}
      <div className="preview-header">
        <div className="preview-file-info">
          <div className="preview-icon">
            {tab.language === 'typescript' ? '📘' : 
             tab.language === 'javascript' ? '📙' :
             tab.language === 'python' ? '🐍' :
             tab.language === 'go' ? '🔷' :
             tab.language === 'rust' ? '🦀' : '📄'}
          </div>
          <div className="preview-details">
            <div className="preview-title" title={tab.title}>
              {tab.title}
              {tab.isDirty && <span className="preview-dirty">●</span>}
            </div>
            {tab.filePath && (
              <div className="preview-path" title={tab.filePath}>
                {tab.filePath}
              </div>
            )}
          </div>
        </div>
        <div className="preview-language-badge">
          {tab.language.toUpperCase()}
        </div>
      </div>

      {/* Preview Content */}
      <div className="preview-content">
        <pre className="preview-code">
          <code className={`language-${tab.language}`}>
            {previewContent}
            {tab.content.split('\n').length > 15 && (
              <div className="preview-truncated">
                ... {tab.content.split('\n').length - 15} more lines
              </div>
            )}
          </code>
        </pre>
      </div>

      {/* Preview Footer */}
      <div className="preview-footer">
        <div className="preview-stats">
          <span className="stat-item">
            <span className="stat-label">Lines:</span>
            <span className="stat-value">{fileStats.lines.toLocaleString()}</span>
          </span>
          <span className="stat-item">
            <span className="stat-label">Words:</span>
            <span className="stat-value">{fileStats.words.toLocaleString()}</span>
          </span>
          <span className="stat-item">
            <span className="stat-label">Chars:</span>
            <span className="stat-value">{fileStats.characters.toLocaleString()}</span>
          </span>
        </div>
        <div className="preview-modified">
          Modified: {tab.lastModified.toLocaleString()}
        </div>
      </div>

      {/* Preview Actions */}
      <div className="preview-actions">
        <button
          className="preview-action-button"
          onClick={(e) => {
            e.stopPropagation()
            // Copy content to clipboard
            navigator.clipboard.writeText(tab.content)
            onClose()
          }}
          title="Copy content to clipboard"
        >
          📋
        </button>
        <button
          className="preview-action-button"
          onClick={(e) => {
            e.stopPropagation()
            // Copy file path to clipboard
            navigator.clipboard.writeText(tab.filePath || tab.title)
            onClose()
          }}
          title="Copy file path"
        >
          📄
        </button>
        <button
          className="preview-action-button"
          onClick={(e) => {
            e.stopPropagation()
            onClose()
          }}
          title="Close preview"
        >
          ✕
        </button>
      </div>
    </div>
  )
}

export default TabPreview