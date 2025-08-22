import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { Tab, TabSearchResult } from '../types/TabTypes'
import { fuzzySearch } from '../utils/searchUtils'
import '../styles/tab-search-dialog.css'

export interface TabSearchDialogProps {
  tabs: Tab[]
  recentFiles: string[]
  onTabSelect: (tabId: string) => void
  onClose: () => void
}

export const TabSearchDialog: React.FC<TabSearchDialogProps> = ({
  tabs,
  recentFiles,
  onTabSelect,
  onClose
}) => {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [showRecentOnly, setShowRecentOnly] = useState(false)
  
  const inputRef = useRef<HTMLInputElement>(null)
  const dialogRef = useRef<HTMLDivElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  // Close on escape or outside click
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    const handleClickOutside = (e: MouseEvent) => {
      if (dialogRef.current && !dialogRef.current.contains(e.target as Node)) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('mousedown', handleClickOutside)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [onClose])

  // Search results
  const searchResults = useMemo((): TabSearchResult[] => {
    if (!query.trim() && !showRecentOnly) {
      return tabs.map(tab => ({
        tab,
        score: 1,
        matchedFields: []
      })).sort((a, b) => b.tab.lastModified.getTime() - a.tab.lastModified.getTime())
    }

    if (showRecentOnly && !query.trim()) {
      const recentTabs = recentFiles
        .map(fileId => tabs.find(tab => tab.fileId === fileId))
        .filter((tab): tab is Tab => tab !== undefined)
        .map(tab => ({
          tab,
          score: 1,
          matchedFields: ['recent']
        }))
      
      return recentTabs.slice(0, 10)
    }

    if (!query.trim()) return []

    const results = fuzzySearch(query, tabs, {
      keys: [
        { key: 'title', weight: 0.7 },
        { key: 'filePath', weight: 0.5 },
        { key: 'content', weight: 0.3 },
        { key: 'language', weight: 0.2 }
      ],
      threshold: 0.3
    })

    // Boost recent files
    return results.map(result => {
      const isRecent = recentFiles.includes(result.tab.fileId)
      return {
        ...result,
        score: isRecent ? result.score * 1.2 : result.score
      }
    }).sort((a, b) => b.score - a.score)
  }, [query, tabs, recentFiles, showRecentOnly])

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => Math.min(prev + 1, searchResults.length - 1))
        break
      
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => Math.max(prev - 1, 0))
        break
      
      case 'Enter':
        e.preventDefault()
        if (searchResults[selectedIndex]) {
          onTabSelect(searchResults[selectedIndex].tab.id)
        }
        break
      
      case 'Tab':
        if (e.shiftKey) {
          e.preventDefault()
          setShowRecentOnly(prev => !prev)
        }
        break
    }
  }, [searchResults, selectedIndex, onTabSelect])

  // Reset selected index when results change
  useEffect(() => {
    setSelectedIndex(0)
  }, [searchResults])

  // Scroll selected item into view
  useEffect(() => {
    if (resultsRef.current) {
      const selectedElement = resultsRef.current.children[selectedIndex] as HTMLElement
      if (selectedElement) {
        selectedElement.scrollIntoView({
          block: 'nearest',
          behavior: 'smooth'
        })
      }
    }
  }, [selectedIndex])

  const handleResultClick = useCallback((tabId: string) => {
    onTabSelect(tabId)
  }, [onTabSelect])

  const highlightMatch = useCallback((text: string, query: string) => {
    if (!query.trim()) return text

    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
    const parts = text.split(regex)

    return (
      <>
        {parts.map((part, index) =>
          regex.test(part) ? (
            <mark key={index} className="search-highlight">{part}</mark>
          ) : (
            part
          )
        )}
      </>
    )
  }, [])

  return (
    <div className="tab-search-overlay">
      <div ref={dialogRef} className="tab-search-dialog" role="dialog" aria-label="Search tabs">
        {/* Header */}
        <div className="search-header">
          <div className="search-input-container">
            <svg className="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M7 2a5 5 0 1 0 3.5 8.5l4 4a.5.5 0 0 0 .7-.7l-4-4A5 5 0 0 0 7 2zm0 1a4 4 0 1 1 0 8 4 4 0 0 1 0-8z"/>
            </svg>
            <input
              ref={inputRef}
              type="text"
              className="search-input"
              placeholder={showRecentOnly ? "Search recent files..." : "Search all tabs..."}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              aria-label="Search tabs"
            />
            <button
              className={`recent-toggle ${showRecentOnly ? 'active' : ''}`}
              onClick={() => setShowRecentOnly(prev => !prev)}
              title="Toggle recent files only (Shift+Tab)"
              aria-label={showRecentOnly ? "Show all tabs" : "Show recent files only"}
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
                <path d="M7 1a6 6 0 1 0 0 12A6 6 0 0 0 7 1zM6 3h2v4l2.5 1.5-.8 1.3L7 8V3z"/>
              </svg>
            </button>
          </div>
          
          <div className="search-stats">
            {searchResults.length} of {tabs.length} tabs
          </div>
        </div>

        {/* Results */}
        <div ref={resultsRef} className="search-results" role="listbox">
          {searchResults.length === 0 ? (
            <div className="no-results">
              <div className="no-results-icon">🔍</div>
              <div className="no-results-text">
                {query ? `No tabs found for "${query}"` : 'No tabs to show'}
              </div>
              {query && (
                <div className="search-tips">
                  <p>Try searching by:</p>
                  <ul>
                    <li>File name or path</li>
                    <li>Programming language</li>
                    <li>File content</li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            searchResults.map((result, index) => {
              const { tab, matchedFields } = result
              const isSelected = index === selectedIndex
              const isRecent = recentFiles.includes(tab.fileId)

              return (
                <div
                  key={tab.id}
                  className={`search-result ${isSelected ? 'selected' : ''}`}
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => handleResultClick(tab.id)}
                  onMouseEnter={() => setSelectedIndex(index)}
                >
                  <div className="result-icon">
                    {tab.language === 'typescript' ? '📘' : 
                     tab.language === 'javascript' ? '📙' :
                     tab.language === 'python' ? '🐍' :
                     tab.language === 'go' ? '🔷' :
                     tab.language === 'rust' ? '🦀' : '📄'}
                  </div>

                  <div className="result-content">
                    <div className="result-title">
                      {highlightMatch(tab.title, query)}
                      {tab.isPinned && <span className="pin-indicator" title="Pinned">📌</span>}
                      {isRecent && <span className="recent-indicator" title="Recent">⏰</span>}
                    </div>
                    
                    {tab.filePath && (
                      <div className="result-path">
                        {highlightMatch(tab.filePath, query)}
                      </div>
                    )}

                    <div className="result-meta">
                      <span className="result-language">{tab.language}</span>
                      <span className="result-modified">
                        {tab.lastModified.toLocaleDateString()}
                      </span>
                      {matchedFields.length > 0 && (
                        <span className="result-matches">
                          Matched: {matchedFields.join(', ')}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="result-actions">
                    {tab.isDirty && (
                      <div className="unsaved-indicator" title="Unsaved changes">●</div>
                    )}
                    <div className="result-score" title={`Search score: ${result.score.toFixed(2)}`}>
                      {Math.round(result.score * 100)}%
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>

        {/* Footer */}
        <div className="search-footer">
          <div className="search-help">
            <kbd>↑↓</kbd> Navigate
            <kbd>Enter</kbd> Select
            <kbd>Shift+Tab</kbd> Recent
            <kbd>Esc</kbd> Close
          </div>
        </div>
      </div>
    </div>
  )
}

export default TabSearchDialog