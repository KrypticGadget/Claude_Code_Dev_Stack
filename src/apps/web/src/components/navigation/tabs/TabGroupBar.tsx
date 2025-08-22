import React, { useState, useCallback } from 'react'
import { TabGroup, Tab } from '../types/TabTypes'
import '../styles/tab-group-bar.css'

export interface TabGroupBarProps {
  groups: TabGroup[]
  tabs: Tab[]
  onGroupCollapse: (groupId: string) => void
  onGroupDelete: (groupId: string) => void
  onGroupRename?: (groupId: string, newName: string) => void
  onGroupColorChange?: (groupId: string, newColor: string) => void
}

const PRESET_COLORS = [
  '#007acc', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4',
  '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3',
  '#ff9f43', '#10ac84', '#ee5a24', '#0abde3', '#c44569'
]

export const TabGroupBar: React.FC<TabGroupBarProps> = ({
  groups,
  tabs,
  onGroupCollapse,
  onGroupDelete,
  onGroupRename,
  onGroupColorChange
}) => {
  const [editingGroupId, setEditingGroupId] = useState<string | null>(null)
  const [editingName, setEditingName] = useState('')
  const [showColorPicker, setShowColorPicker] = useState<string | null>(null)

  const getGroupTabCount = useCallback((groupId: string) => {
    return tabs.filter(tab => tab.groupId === groupId).length
  }, [tabs])

  const handleStartRename = useCallback((group: TabGroup) => {
    setEditingGroupId(group.id)
    setEditingName(group.name)
  }, [])

  const handleFinishRename = useCallback(() => {
    if (editingGroupId && editingName.trim() && onGroupRename) {
      onGroupRename(editingGroupId, editingName.trim())
    }
    setEditingGroupId(null)
    setEditingName('')
  }, [editingGroupId, editingName, onGroupRename])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleFinishRename()
    } else if (e.key === 'Escape') {
      setEditingGroupId(null)
      setEditingName('')
    }
  }, [handleFinishRename])

  const handleColorChange = useCallback((groupId: string, color: string) => {
    if (onGroupColorChange) {
      onGroupColorChange(groupId, color)
    }
    setShowColorPicker(null)
  }, [onGroupColorChange])

  if (groups.length === 0) {
    return null
  }

  return (
    <div className="tab-group-bar">
      <div className="tab-group-header">
        <span className="tab-group-title">Tab Groups</span>
        <div className="tab-group-stats">
          {groups.length} group{groups.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="tab-groups">
        {groups.map((group) => {
          const tabCount = getGroupTabCount(group.id)
          const isEditing = editingGroupId === group.id

          return (
            <div
              key={group.id}
              className={`tab-group ${group.isCollapsed ? 'collapsed' : ''}`}
              style={{ '--group-color': group.color } as React.CSSProperties}
            >
              <div className="tab-group-item">
                {/* Color Indicator */}
                <div
                  className="group-color-indicator"
                  style={{ backgroundColor: group.color }}
                  onClick={() => setShowColorPicker(showColorPicker === group.id ? null : group.id)}
                  title="Click to change color"
                />

                {/* Collapse Button */}
                <button
                  className="group-collapse-button"
                  onClick={() => onGroupCollapse(group.id)}
                  title={group.isCollapsed ? 'Expand group' : 'Collapse group'}
                  aria-label={group.isCollapsed ? 'Expand group' : 'Collapse group'}
                >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 12 12"
                    fill="currentColor"
                    style={{
                      transform: group.isCollapsed ? 'rotate(-90deg)' : 'rotate(0deg)',
                      transition: 'transform 0.2s ease'
                    }}
                  >
                    <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>

                {/* Group Name */}
                <div className="group-name-container">
                  {isEditing ? (
                    <input
                      type="text"
                      className="group-name-input"
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      onBlur={handleFinishRename}
                      onKeyDown={handleKeyDown}
                      autoFocus
                    />
                  ) : (
                    <span
                      className="group-name"
                      onDoubleClick={() => handleStartRename(group)}
                      title="Double-click to rename"
                    >
                      {group.name}
                    </span>
                  )}
                </div>

                {/* Tab Count */}
                <div className="group-tab-count">
                  {tabCount} tab{tabCount !== 1 ? 's' : ''}
                </div>

                {/* Group Actions */}
                <div className="group-actions">
                  {onGroupRename && (
                    <button
                      className="group-action-button"
                      onClick={() => handleStartRename(group)}
                      title="Rename group"
                      aria-label="Rename group"
                    >
                      ✏️
                    </button>
                  )}
                  
                  <button
                    className="group-action-button"
                    onClick={() => onGroupDelete(group.id)}
                    title="Delete group"
                    aria-label="Delete group"
                  >
                    🗑️
                  </button>
                </div>

                {/* Color Picker */}
                {showColorPicker === group.id && onGroupColorChange && (
                  <div className="color-picker">
                    <div className="color-picker-colors">
                      {PRESET_COLORS.map((color) => (
                        <button
                          key={color}
                          className={`color-picker-color ${group.color === color ? 'selected' : ''}`}
                          style={{ backgroundColor: color }}
                          onClick={() => handleColorChange(group.id, color)}
                          title={color}
                          aria-label={`Set color to ${color}`}
                        />
                      ))}
                    </div>
                    <div className="color-picker-actions">
                      <input
                        type="color"
                        value={group.color}
                        onChange={(e) => handleColorChange(group.id, e.target.value)}
                        title="Choose custom color"
                      />
                      <button
                        className="color-picker-close"
                        onClick={() => setShowColorPicker(null)}
                        title="Close color picker"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Group Tab Preview (when not collapsed) */}
              {!group.isCollapsed && tabCount > 0 && (
                <div className="group-tabs-preview">
                  {tabs
                    .filter(tab => tab.groupId === group.id)
                    .slice(0, 5)
                    .map((tab) => (
                      <div key={tab.id} className="group-tab-preview">
                        <div className="preview-icon">
                          {tab.language === 'typescript' ? '📘' : 
                           tab.language === 'javascript' ? '📙' :
                           tab.language === 'python' ? '🐍' :
                           tab.language === 'go' ? '🔷' :
                           tab.language === 'rust' ? '🦀' : '📄'}
                        </div>
                        <span className="preview-title">{tab.title}</span>
                        {tab.isDirty && <span className="preview-dirty">●</span>}
                      </div>
                    ))}
                  {tabCount > 5 && (
                    <div className="group-tab-preview more">
                      +{tabCount - 5} more
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default TabGroupBar