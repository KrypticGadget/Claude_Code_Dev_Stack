import { Tab, TabSearchResult } from '../types/TabTypes'

export interface SearchOptions {
  keys: Array<{
    key: keyof Tab
    weight: number
  }>
  threshold: number
  caseSensitive?: boolean
  includeScore?: boolean
}

/**
 * Fuzzy search implementation for tabs
 */
export function fuzzySearch(
  query: string,
  tabs: Tab[],
  options: SearchOptions
): TabSearchResult[] {
  if (!query.trim()) return []

  const {
    keys,
    threshold = 0.3,
    caseSensitive = false,
    includeScore = true
  } = options

  const normalizedQuery = caseSensitive ? query : query.toLowerCase()
  const results: TabSearchResult[] = []

  for (const tab of tabs) {
    let totalScore = 0
    let totalWeight = 0
    const matchedFields: string[] = []

    for (const { key, weight } of keys) {
      const value = String(tab[key] || '')
      const normalizedValue = caseSensitive ? value : value.toLowerCase()
      
      const score = calculateMatchScore(normalizedQuery, normalizedValue)
      
      if (score > 0) {
        totalScore += score * weight
        totalWeight += weight
        matchedFields.push(key)
      }
    }

    if (totalWeight > 0) {
      const finalScore = totalScore / totalWeight
      
      if (finalScore >= threshold) {
        results.push({
          tab,
          score: finalScore,
          matchedFields
        })
      }
    }
  }

  return results.sort((a, b) => b.score - a.score)
}

/**
 * Calculate match score between query and text
 */
function calculateMatchScore(query: string, text: string): number {
  if (!query || !text) return 0

  // Exact match gets highest score
  if (text === query) return 1.0

  // Contains query gets high score
  if (text.includes(query)) {
    const ratio = query.length / text.length
    return 0.8 + (ratio * 0.2) // 0.8 to 1.0 based on length ratio
  }

  // Fuzzy matching
  const fuzzyScore = calculateFuzzyScore(query, text)
  if (fuzzyScore > 0.5) return fuzzyScore * 0.7 // Scale down fuzzy matches

  // Check if query matches beginning of words
  const words = text.split(/\s+/)
  for (const word of words) {
    if (word.startsWith(query)) {
      return 0.6 + (query.length / word.length) * 0.2
    }
  }

  return 0
}

/**
 * Calculate fuzzy match score using Levenshtein distance
 */
function calculateFuzzyScore(query: string, text: string): number {
  const distance = levenshteinDistance(query, text)
  const maxLength = Math.max(query.length, text.length)
  
  if (maxLength === 0) return 1
  
  return 1 - (distance / maxLength)
}

/**
 * Calculate Levenshtein distance between two strings
 */
function levenshteinDistance(str1: string, str2: string): number {
  const matrix = Array(str2.length + 1).fill(null).map(() => 
    Array(str1.length + 1).fill(null)
  )

  for (let i = 0; i <= str1.length; i++) {
    matrix[0][i] = i
  }

  for (let j = 0; j <= str2.length; j++) {
    matrix[j][0] = j
  }

  for (let j = 1; j <= str2.length; j++) {
    for (let i = 1; i <= str1.length; i++) {
      const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1, // deletion
        matrix[j - 1][i] + 1, // insertion
        matrix[j - 1][i - 1] + indicator // substitution
      )
    }
  }

  return matrix[str2.length][str1.length]
}

/**
 * Search tabs by content with highlighting
 */
export function searchTabContent(
  query: string,
  tabs: Tab[],
  options: {
    maxResults?: number
    contextLines?: number
    caseSensitive?: boolean
  } = {}
): Array<{
  tab: Tab
  matches: Array<{
    line: number
    content: string
    highlights: Array<{ start: number; end: number }>
  }>
}> {
  const {
    maxResults = 50,
    contextLines = 2,
    caseSensitive = false
  } = options

  if (!query.trim()) return []

  const normalizedQuery = caseSensitive ? query : query.toLowerCase()
  const results: Array<{
    tab: Tab
    matches: Array<{
      line: number
      content: string
      highlights: Array<{ start: number; end: number }>
    }>
  }> = []

  for (const tab of tabs) {
    const lines = tab.content.split('\n')
    const matches: Array<{
      line: number
      content: string
      highlights: Array<{ start: number; end: number }>
    }> = []

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const normalizedLine = caseSensitive ? line : line.toLowerCase()
      
      if (normalizedLine.includes(normalizedQuery)) {
        const highlights = findAllOccurrences(normalizedLine, normalizedQuery)
        matches.push({
          line: i + 1,
          content: line,
          highlights
        })
      }
    }

    if (matches.length > 0) {
      results.push({ tab, matches })
    }

    if (results.length >= maxResults) break
  }

  return results
}

/**
 * Find all occurrences of query in text
 */
function findAllOccurrences(text: string, query: string): Array<{ start: number; end: number }> {
  const occurrences: Array<{ start: number; end: number }> = []
  let index = 0

  while (true) {
    const foundIndex = text.indexOf(query, index)
    if (foundIndex === -1) break

    occurrences.push({
      start: foundIndex,
      end: foundIndex + query.length
    })

    index = foundIndex + 1
  }

  return occurrences
}

/**
 * Advanced tab filtering
 */
export function filterTabs(
  tabs: Tab[],
  filters: {
    language?: string[]
    hasUnsavedChanges?: boolean
    isPinned?: boolean
    groupId?: string[]
    modifiedAfter?: Date
    modifiedBefore?: Date
    contentIncludes?: string
    pathIncludes?: string
  }
): Tab[] {
  return tabs.filter(tab => {
    // Language filter
    if (filters.language && filters.language.length > 0) {
      if (!filters.language.includes(tab.language)) return false
    }

    // Unsaved changes filter
    if (filters.hasUnsavedChanges !== undefined) {
      if (tab.isDirty !== filters.hasUnsavedChanges) return false
    }

    // Pinned filter
    if (filters.isPinned !== undefined) {
      if (tab.isPinned !== filters.isPinned) return false
    }

    // Group filter
    if (filters.groupId && filters.groupId.length > 0) {
      if (!tab.groupId || !filters.groupId.includes(tab.groupId)) return false
    }

    // Modified after filter
    if (filters.modifiedAfter) {
      if (tab.lastModified < filters.modifiedAfter) return false
    }

    // Modified before filter
    if (filters.modifiedBefore) {
      if (tab.lastModified > filters.modifiedBefore) return false
    }

    // Content includes filter
    if (filters.contentIncludes) {
      if (!tab.content.toLowerCase().includes(filters.contentIncludes.toLowerCase())) return false
    }

    // Path includes filter
    if (filters.pathIncludes) {
      if (!tab.filePath.toLowerCase().includes(filters.pathIncludes.toLowerCase())) return false
    }

    return true
  })
}

/**
 * Sort tabs by various criteria
 */
export function sortTabs(
  tabs: Tab[],
  sortBy: 'name' | 'lastModified' | 'language' | 'size' | 'path',
  direction: 'asc' | 'desc' = 'asc'
): Tab[] {
  const sorted = [...tabs].sort((a, b) => {
    let comparison = 0

    switch (sortBy) {
      case 'name':
        comparison = a.title.localeCompare(b.title)
        break
      case 'lastModified':
        comparison = a.lastModified.getTime() - b.lastModified.getTime()
        break
      case 'language':
        comparison = a.language.localeCompare(b.language)
        break
      case 'size':
        comparison = a.content.length - b.content.length
        break
      case 'path':
        comparison = a.filePath.localeCompare(b.filePath)
        break
    }

    return direction === 'asc' ? comparison : -comparison
  })

  return sorted
}

/**
 * Group tabs by criteria
 */
export function groupTabs(
  tabs: Tab[],
  groupBy: 'language' | 'directory' | 'group' | 'modified'
): Record<string, Tab[]> {
  const groups: Record<string, Tab[]> = {}

  for (const tab of tabs) {
    let groupKey: string

    switch (groupBy) {
      case 'language':
        groupKey = tab.language || 'Unknown'
        break
      case 'directory':
        groupKey = tab.filePath ? tab.filePath.split('/').slice(0, -1).join('/') || 'Root' : 'No Path'
        break
      case 'group':
        groupKey = tab.groupId || 'Ungrouped'
        break
      case 'modified':
        const today = new Date()
        const modified = tab.lastModified
        const diffTime = today.getTime() - modified.getTime()
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        
        if (diffDays <= 1) groupKey = 'Today'
        else if (diffDays <= 7) groupKey = 'This Week'
        else if (diffDays <= 30) groupKey = 'This Month'
        else groupKey = 'Older'
        break
      default:
        groupKey = 'All'
    }

    if (!groups[groupKey]) {
      groups[groupKey] = []
    }
    groups[groupKey].push(tab)
  }

  return groups
}

/**
 * Get tab suggestions based on current context
 */
export function getTabSuggestions(
  currentTab: Tab | null,
  allTabs: Tab[],
  recentTabs: string[],
  maxSuggestions = 5
): Tab[] {
  if (!currentTab) {
    // Return recent tabs if no current tab
    return recentTabs
      .map(tabId => allTabs.find(tab => tab.fileId === tabId))
      .filter((tab): tab is Tab => tab !== undefined)
      .slice(0, maxSuggestions)
  }

  const suggestions: Array<{ tab: Tab; score: number }> = []

  for (const tab of allTabs) {
    if (tab.id === currentTab.id) continue

    let score = 0

    // Same language bonus
    if (tab.language === currentTab.language) score += 0.3

    // Same directory bonus
    const currentDir = currentTab.filePath.split('/').slice(0, -1).join('/')
    const tabDir = tab.filePath.split('/').slice(0, -1).join('/')
    if (currentDir === tabDir) score += 0.4

    // Recent file bonus
    const recentIndex = recentTabs.indexOf(tab.fileId)
    if (recentIndex !== -1) {
      score += 0.5 - (recentIndex / recentTabs.length) * 0.3
    }

    // Related name bonus (similar file names)
    const currentName = currentTab.title.replace(/\.[^/.]+$/, '') // Remove extension
    const tabName = tab.title.replace(/\.[^/.]+$/, '')
    if (tabName.includes(currentName) || currentName.includes(tabName)) {
      score += 0.2
    }

    if (score > 0) {
      suggestions.push({ tab, score })
    }
  }

  return suggestions
    .sort((a, b) => b.score - a.score)
    .slice(0, maxSuggestions)
    .map(s => s.tab)
}

export default {
  fuzzySearch,
  searchTabContent,
  filterTabs,
  sortTabs,
  groupTabs,
  getTabSuggestions
}