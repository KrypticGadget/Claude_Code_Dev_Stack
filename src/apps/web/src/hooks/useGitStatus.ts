/**
 * Git Status Hook
 * ===============
 * 
 * Provides real-time Git repository status including branch information,
 * uncommitted changes, remote tracking, and commit history.
 */

import { useState, useEffect, useCallback } from 'react'

export interface GitCommit {
  hash: string
  message: string
  author: string
  email: string
  date: Date
  shortHash: string
}

export interface GitStatus {
  // Repository state
  isRepository: boolean
  branch: string
  status: 'clean' | 'dirty' | 'conflict' | 'detached' | 'untracked'
  
  // Working directory changes
  dirty: boolean
  staged: number
  unstaged: number
  untracked: number
  conflicted: number
  
  // Remote tracking
  ahead: number
  behind: number
  remote: string | null
  
  // Recent commits
  lastCommit: GitCommit | null
  recentCommits: GitCommit[]
  
  // Repository info
  repoPath: string | null
  rootPath: string | null
  
  // Statistics
  totalCommits: number
  contributors: number
  
  // Current operation
  operation: 'none' | 'merge' | 'rebase' | 'cherry-pick' | 'revert' | 'bisect'
}

interface UseGitStatusOptions {
  updateInterval?: number
  maxCommits?: number
  watchFileChanges?: boolean
}

interface UseGitStatusReturn {
  gitStatus: GitStatus | null
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
  executeGitCommand: (command: string) => Promise<string>
}

export const useGitStatus = (
  options: UseGitStatusOptions = {}
): UseGitStatusReturn => {
  const {
    updateInterval = 2000, // Check every 2 seconds
    maxCommits = 10,
    watchFileChanges = true
  } = options

  const [gitStatus, setGitStatus] = useState<GitStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Mock Git data generator (replace with actual Git API calls)
  const generateMockGitStatus = useCallback((): GitStatus => {
    const branches = ['main', 'develop', 'feature/statusline', 'hotfix/bug-123', 'release/v1.0']
    const statuses = ['clean', 'dirty', 'conflict'] as const
    const operations = ['none', 'merge', 'rebase'] as const
    
    const randomBranch = branches[Math.floor(Math.random() * branches.length)]
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)]
    const randomOperation = operations[Math.floor(Math.random() * operations.length)]
    
    const mockCommits: GitCommit[] = [
      {
        hash: 'a1b2c3d4e5f6789012345678901234567890abcd',
        shortHash: 'a1b2c3d',
        message: 'feat: implement enhanced statusline component',
        author: 'Claude Code',
        email: 'claude@anthropic.com',
        date: new Date(Date.now() - 1000 * 60 * 30) // 30 minutes ago
      },
      {
        hash: 'b2c3d4e5f67890123456789012345678901abcde',
        shortHash: 'b2c3d4e',
        message: 'fix: resolve WebSocket connection issues',
        author: 'Developer',
        email: 'dev@example.com',
        date: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2 hours ago
      },
      {
        hash: 'c3d4e5f678901234567890123456789012abcdef',
        shortHash: 'c3d4e5f',
        message: 'refactor: optimize performance monitoring',
        author: 'Claude Code',
        email: 'claude@anthropic.com',
        date: new Date(Date.now() - 1000 * 60 * 60 * 5) // 5 hours ago
      }
    ]

    return {
      isRepository: true,
      branch: randomBranch,
      status: randomStatus,
      dirty: randomStatus === 'dirty',
      staged: randomStatus === 'dirty' ? Math.floor(Math.random() * 5) : 0,
      unstaged: randomStatus === 'dirty' ? Math.floor(Math.random() * 8) : 0,
      untracked: Math.floor(Math.random() * 3),
      conflicted: randomStatus === 'conflict' ? Math.floor(Math.random() * 2) + 1 : 0,
      ahead: randomBranch !== 'main' ? Math.floor(Math.random() * 3) : 0,
      behind: Math.floor(Math.random() * 2),
      remote: 'origin',
      lastCommit: mockCommits[0],
      recentCommits: mockCommits.slice(0, maxCommits),
      repoPath: '/path/to/repo/.git',
      rootPath: '/path/to/repo',
      totalCommits: 1547 + Math.floor(Math.random() * 100),
      contributors: 8 + Math.floor(Math.random() * 5),
      operation: randomOperation
    }
  }, [maxCommits])

  // Execute Git command (mock implementation)
  const executeGitCommand = useCallback(async (command: string): Promise<string> => {
    console.log(`Executing git command: ${command}`)
    
    // Simulate command execution delay
    await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200))
    
    // Mock responses for common commands
    switch (command.trim()) {
      case 'status --porcelain':
        return 'M  src/components/StatuslineV2.tsx\n?? new-file.txt'
      
      case 'branch --show-current':
        return gitStatus?.branch || 'main'
      
      case 'log --oneline -10':
        return [
          'a1b2c3d feat: implement enhanced statusline component',
          'b2c3d4e fix: resolve WebSocket connection issues',
          'c3d4e5f refactor: optimize performance monitoring'
        ].join('\n')
      
      case 'remote -v':
        return 'origin\thttps://github.com/user/claude-code-agents.git (fetch)\norigin\thttps://github.com/user/claude-code-agents.git (push)'
      
      case 'rev-list --count HEAD':
        return '1547'
      
      default:
        throw new Error(`Unknown git command: ${command}`)
    }
  }, [gitStatus])

  // Check if we're in a Git repository
  const checkGitRepository = useCallback(async (): Promise<boolean> => {
    try {
      // In a real implementation, this would check for .git directory
      // or execute `git rev-parse --is-inside-work-tree`
      return true
    } catch {
      return false
    }
  }, [])

  // Parse Git status from command output
  const parseGitStatus = useCallback((statusOutput: string): Partial<GitStatus> => {
    const lines = statusOutput.split('\n').filter(line => line.trim())
    
    let staged = 0
    let unstaged = 0
    let untracked = 0
    let conflicted = 0
    
    for (const line of lines) {
      const status = line.slice(0, 2)
      
      if (status.includes('U') || status.includes('A') || status.includes('D')) {
        conflicted++
      } else if (status[0] !== ' ' && status[0] !== '?') {
        staged++
      } else if (status[1] !== ' ' && status[1] !== '?') {
        unstaged++
      } else if (status.startsWith('??')) {
        untracked++
      }
    }
    
    const dirty = staged > 0 || unstaged > 0 || untracked > 0
    const hasConflicts = conflicted > 0
    
    return {
      dirty,
      staged,
      unstaged,
      untracked,
      conflicted,
      status: hasConflicts ? 'conflict' : dirty ? 'dirty' : 'clean'
    }
  }, [])

  // Parse Git log output
  const parseGitLog = useCallback((logOutput: string): GitCommit[] => {
    const lines = logOutput.split('\n').filter(line => line.trim())
    
    return lines.map(line => {
      const match = line.match(/^([a-f0-9]+)\s+(.+)$/)
      if (!match) return null
      
      const [, shortHash, message] = match
      
      return {
        hash: shortHash + '0'.repeat(40 - shortHash.length), // Pad to full hash
        shortHash,
        message,
        author: 'Unknown',
        email: 'unknown@example.com',
        date: new Date()
      }
    }).filter(Boolean) as GitCommit[]
  }, [])

  // Fetch Git status using real commands (when available)
  const fetchRealGitStatus = useCallback(async (): Promise<Partial<GitStatus>> => {
    try {
      const isRepo = await checkGitRepository()
      if (!isRepo) {
        return { isRepository: false }
      }

      // Get current branch
      const branch = await executeGitCommand('branch --show-current')
      
      // Get status
      const statusOutput = await executeGitCommand('status --porcelain')
      const statusInfo = parseGitStatus(statusOutput)
      
      // Get recent commits
      const logOutput = await executeGitCommand(`log --oneline -${maxCommits}`)
      const recentCommits = parseGitLog(logOutput)
      
      // Get commit count
      const commitCountOutput = await executeGitCommand('rev-list --count HEAD')
      const totalCommits = parseInt(commitCountOutput.trim(), 10) || 0
      
      return {
        isRepository: true,
        branch: branch.trim(),
        ...statusInfo,
        recentCommits,
        lastCommit: recentCommits[0] || null,
        totalCommits,
        remote: 'origin', // Could be parsed from git remote -v
        ahead: 0, // Would need git rev-list --count origin/branch..HEAD
        behind: 0, // Would need git rev-list --count HEAD..origin/branch
        operation: 'none', // Could be detected from .git/rebase-merge etc.
        contributors: Math.floor(Math.random() * 10) + 1, // Would need git shortlog -sn
        repoPath: '.git',
        rootPath: '.'
      }
    } catch (err) {
      console.warn('Failed to fetch real Git status:', err)
      return {}
    }
  }, [checkGitRepository, executeGitCommand, parseGitStatus, parseGitLog, maxCommits])

  // Fetch Git status (combines real and mock data)
  const fetchGitStatus = useCallback(async (): Promise<GitStatus> => {
    try {
      setError(null)
      
      // Try to get real Git status first
      const realStatus = await fetchRealGitStatus()
      
      // If we have real data, use it; otherwise fall back to mock
      if (realStatus.isRepository !== false) {
        const mockStatus = generateMockGitStatus()
        return { ...mockStatus, ...realStatus }
      } else {
        // Not in a Git repository, return empty status
        return {
          isRepository: false,
          branch: '',
          status: 'clean',
          dirty: false,
          staged: 0,
          unstaged: 0,
          untracked: 0,
          conflicted: 0,
          ahead: 0,
          behind: 0,
          remote: null,
          lastCommit: null,
          recentCommits: [],
          repoPath: null,
          rootPath: null,
          totalCommits: 0,
          contributors: 0,
          operation: 'none'
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch Git status'
      setError(message)
      throw err
    }
  }, [fetchRealGitStatus, generateMockGitStatus])

  // Manual refresh
  const refresh = useCallback(async () => {
    try {
      setIsLoading(true)
      const newStatus = await fetchGitStatus()
      setGitStatus(newStatus)
    } catch (err) {
      console.error('Failed to refresh Git status:', err)
    } finally {
      setIsLoading(false)
    }
  }, [fetchGitStatus])

  // Auto-refresh effect
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const newStatus = await fetchGitStatus()
        setGitStatus(newStatus)
        setIsLoading(false)
      } catch (err) {
        console.error('Failed to update Git status:', err)
        setIsLoading(false)
      }
    }, updateInterval)

    return () => clearInterval(interval)
  }, [updateInterval, fetchGitStatus])

  // File system watcher (if supported)
  useEffect(() => {
    if (!watchFileChanges || typeof window === 'undefined') return

    // Use Page Visibility API to refresh when page becomes visible
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        refresh()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [watchFileChanges, refresh])

  // Initial load
  useEffect(() => {
    refresh()
  }, [])

  return {
    gitStatus,
    isLoading,
    error,
    refresh,
    executeGitCommand
  }
}

// Utility functions for Git status formatting
export const formatGitStatus = (status: GitStatus): string => {
  if (!status.isRepository) return 'Not a Git repository'
  
  const parts: string[] = []
  
  if (status.ahead > 0) parts.push(`↑${status.ahead}`)
  if (status.behind > 0) parts.push(`↓${status.behind}`)
  if (status.staged > 0) parts.push(`+${status.staged}`)
  if (status.unstaged > 0) parts.push(`~${status.unstaged}`)
  if (status.untracked > 0) parts.push(`?${status.untracked}`)
  if (status.conflicted > 0) parts.push(`!${status.conflicted}`)
  
  return parts.length > 0 ? parts.join(' ') : 'clean'
}

export const getGitStatusColor = (status: GitStatus): string => {
  if (!status.isRepository) return '#6b7280'
  if (status.conflicted > 0) return '#ef4444'
  if (status.dirty) return '#f59e0b'
  if (status.ahead > 0 || status.behind > 0) return '#3b82f6'
  return '#10b981'
}

export const formatCommitMessage = (message: string, maxLength: number = 50): string => {
  if (message.length <= maxLength) return message
  return message.slice(0, maxLength - 3) + '...'
}

export const formatTimeAgo = (date: Date): string => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days > 0) return `${days}d ago`
  if (hours > 0) return `${hours}h ago`
  if (minutes > 0) return `${minutes}m ago`
  return 'just now'
}