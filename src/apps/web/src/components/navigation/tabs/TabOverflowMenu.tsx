import React, { useState, useRef, useEffect } from 'react'
import { Tab } from '../types/TabTypes'
import '../styles/tab-overflow-menu.css'

export interface TabOverflowMenuProps {
  tabs: Tab[]
  activeTabId: string | null
  onTabSelect: (tabId: string) => void
}

export const TabOverflowMenu: React.FC<TabOverflowMenuProps> = ({
  tabs,
  activeTabId,
  onTabSelect
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node) &&
          buttonRef.current && !buttonRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      document.addEventListener('keydown', handleEscape)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen])

  const handleTabSelect = (tabId: string) => {
    onTabSelect(tabId)
    setIsOpen(false)
  }

  const overflowTabs = tabs.slice(15) // Show tabs beyond the first 15

  if (overflowTabs.length === 0) {
    return null
  }

  return (
    <div className="tab-overflow-menu">
      <button
        ref={buttonRef}
        className={`overflow-menu-button ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title={`${overflowTabs.length} more tabs`}
        aria-label={`Show ${overflowTabs.length} more tabs`}
        aria-expanded={isOpen}
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
          <circle cx="3" cy="7" r="1"/>
          <circle cx="7" cy="7" r="1"/>
          <circle cx="11" cy="7" r="1"/>
        </svg>
        <span className="overflow-count">{overflowTabs.length}</span>
      </button>

      {isOpen && (
        <div ref={menuRef} className="overflow-menu-dropdown">
          <div className="overflow-menu-header">
            <span className="overflow-menu-title">More Tabs</span>
            <span className="overflow-menu-count">{overflowTabs.length} tabs</span>
          </div>

          <div className="overflow-menu-items">
            {overflowTabs.map((tab) => (
              <div
                key={tab.id}
                className={`overflow-menu-item ${tab.id === activeTabId ? 'active' : ''}`}
                onClick={() => handleTabSelect(tab.id)}
                title={tab.filePath || tab.title}
              >
                <div className="overflow-item-icon">
                  {tab.language === 'typescript' ? '📘' : 
                   tab.language === 'javascript' ? '📙' :
                   tab.language === 'python' ? '🐍' :
                   tab.language === 'go' ? '🔷' :
                   tab.language === 'rust' ? '🦀' : '📄'}
                </div>

                <div className="overflow-item-content">
                  <div className="overflow-item-title">
                    {tab.title}
                    {tab.isDirty && <span className="overflow-item-dirty">●</span>}
                    {tab.isPinned && <span className="overflow-item-pinned">📌</span>}
                  </div>
                  {tab.filePath && (
                    <div className="overflow-item-path">{tab.filePath}</div>
                  )}
                </div>

                <div className="overflow-item-meta">
                  <span className="overflow-item-language">{tab.language}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="overflow-menu-footer">
            <button
              className="overflow-menu-close"
              onClick={() => setIsOpen(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default TabOverflowMenu