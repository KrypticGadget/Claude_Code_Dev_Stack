// Git Service Worker for Monaco Editor
// Provides Git integration functionality

interface GitRequest {
  type: 'get-status' | 'get-diff' | 'get-branches' | 'get-commits' | 'get-blame' | 
        'stage-file' | 'unstage-file' | 'commit' | 'switch-branch' | 'create-branch'
  workspaceRoot: string
  filePath?: string
  message?: string
  files?: string[]
  branchName?: string
  fromBranch?: string
}

interface GitStatus {
  modified: string[]
  added: string[]
  deleted: string[]
  untracked: string[]
  staged: string[]
  conflicted: string[]
  branch: string
  remoteUrl?: string
  ahead: number
  behind: number
  clean: boolean
}

interface GitDiff {
  filePath: string
  oldContent: string
  newContent: string
  hunks: GitHunk[]
}

interface GitHunk {
  oldStart: number
  oldLines: number
  newStart: number
  newLines: number
  lines: GitDiffLine[]
}

interface GitDiffLine {
  type: 'add' | 'remove' | 'context'
  content: string
  lineNumber: number
}

interface GitCommit {
  hash: string
  author: string
  date: Date
  message: string
  files: string[]
}

interface GitBranch {
  name: string
  current: boolean
  remote: boolean
  upstream?: string
}

// Mock Git service - In a real implementation, this would interface with actual Git
class GitService {
  private mockRepos = new Map<string, any>()

  async getStatus(workspaceRoot: string): Promise<GitStatus> {
    // Simulate Git status
    const mockStatus: GitStatus = {
      modified: ['src/components/MonacoEditor.tsx', 'src/hooks/useLanguageSupport.ts'],
      added: ['src/components/CommandPalette.tsx'],
      deleted: [],
      untracked: ['temp.js'],
      staged: ['src/components/MonacoEditorToolbar.tsx'],
      conflicted: [],
      branch: 'feature/monaco-integration',
      remoteUrl: 'https://github.com/user/repo.git',
      ahead: 2,
      behind: 0,
      clean: false
    }

    return mockStatus
  }

  async getDiff(workspaceRoot: string, filePath: string): Promise<GitDiff> {
    // Simulate Git diff
    const mockDiff: GitDiff = {
      filePath,
      oldContent: `// Old version of the file
import React from 'react'

const Component = () => {
  return <div>Hello</div>
}

export default Component`,
      newContent: `// New version of the file
import React, { useState } from 'react'

const Component = () => {
  const [count, setCount] = useState(0)
  
  return (
    <div>
      <p>Hello {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  )
}

export default Component`,
      hunks: [
        {
          oldStart: 1,
          oldLines: 7,
          newStart: 1,
          newLines: 15,
          lines: [
            { type: 'context', content: '// Old version of the file', lineNumber: 1 },
            { type: 'remove', content: 'import React from \'react\'', lineNumber: 2 },
            { type: 'add', content: 'import React, { useState } from \'react\'', lineNumber: 2 },
            { type: 'context', content: '', lineNumber: 3 },
            { type: 'context', content: 'const Component = () => {', lineNumber: 4 },
            { type: 'add', content: '  const [count, setCount] = useState(0)', lineNumber: 5 },
            { type: 'add', content: '  ', lineNumber: 6 },
            { type: 'remove', content: '  return <div>Hello</div>', lineNumber: 5 },
            { type: 'add', content: '  return (', lineNumber: 7 },
            { type: 'add', content: '    <div>', lineNumber: 8 },
            { type: 'add', content: '      <p>Hello {count}</p>', lineNumber: 9 },
            { type: 'add', content: '      <button onClick={() => setCount(count + 1)}>', lineNumber: 10 },
            { type: 'add', content: '        Increment', lineNumber: 11 },
            { type: 'add', content: '      </button>', lineNumber: 12 },
            { type: 'add', content: '    </div>', lineNumber: 13 },
            { type: 'add', content: '  )', lineNumber: 14 },
            { type: 'context', content: '}', lineNumber: 6 },
            { type: 'context', content: '', lineNumber: 7 },
            { type: 'context', content: 'export default Component', lineNumber: 8 }
          ]
        }
      ]
    }

    return mockDiff
  }

  async getBranches(workspaceRoot: string): Promise<GitBranch[]> {
    // Simulate Git branches
    const mockBranches: GitBranch[] = [
      { name: 'main', current: false, remote: false, upstream: 'origin/main' },
      { name: 'feature/monaco-integration', current: true, remote: false },
      { name: 'develop', current: false, remote: false, upstream: 'origin/develop' },
      { name: 'origin/main', current: false, remote: true },
      { name: 'origin/develop', current: false, remote: true }
    ]

    return mockBranches
  }

  async getCommits(workspaceRoot: string, limit = 20): Promise<GitCommit[]> {
    // Simulate Git commit history
    const mockCommits: GitCommit[] = [
      {
        hash: 'abc123def456',
        author: 'Developer <dev@example.com>',
        date: new Date('2024-01-20T10:30:00Z'),
        message: 'Add Monaco Editor integration with full IntelliSense',
        files: ['src/components/MonacoEditor.tsx', 'package.json']
      },
      {
        hash: 'def456ghi789',
        author: 'Developer <dev@example.com>',
        date: new Date('2024-01-19T15:45:00Z'),
        message: 'Implement collaborative editing features',
        files: ['src/hooks/useCollaborativeEditing.ts']
      },
      {
        hash: 'ghi789jkl012',
        author: 'Developer <dev@example.com>',
        date: new Date('2024-01-18T09:15:00Z'),
        message: 'Add debugging capabilities to editor',
        files: ['src/hooks/useDebugger.ts', 'src/components/DebugPanel.tsx']
      }
    ].slice(0, limit)

    return mockCommits
  }

  async getBlame(workspaceRoot: string, filePath: string): Promise<any> {
    // Simulate Git blame
    return {
      lines: [
        { lineNumber: 1, commit: 'abc123', author: 'Developer', date: '2024-01-20', content: 'import React from \'react\'' },
        { lineNumber: 2, commit: 'def456', author: 'Developer', date: '2024-01-19', content: '' },
        { lineNumber: 3, commit: 'abc123', author: 'Developer', date: '2024-01-20', content: 'const Component = () => {' }
      ]
    }
  }

  async stageFile(workspaceRoot: string, filePath: string): Promise<void> {
    // Simulate staging file
    console.log(`Staging file: ${filePath}`)
    // In real implementation: git add ${filePath}
  }

  async unstageFile(workspaceRoot: string, filePath: string): Promise<void> {
    // Simulate unstaging file
    console.log(`Unstaging file: ${filePath}`)
    // In real implementation: git reset HEAD ${filePath}
  }

  async commit(workspaceRoot: string, message: string, files?: string[]): Promise<void> {
    // Simulate commit
    console.log(`Committing with message: ${message}`)
    if (files) {
      console.log(`Files: ${files.join(', ')}`)
    }
    // In real implementation: git commit -m "${message}" ${files?.join(' ') || ''}
  }

  async switchBranch(workspaceRoot: string, branchName: string): Promise<void> {
    // Simulate branch switch
    console.log(`Switching to branch: ${branchName}`)
    // In real implementation: git checkout ${branchName}
  }

  async createBranch(workspaceRoot: string, branchName: string, fromBranch?: string): Promise<void> {
    // Simulate branch creation
    console.log(`Creating branch: ${branchName}${fromBranch ? ` from ${fromBranch}` : ''}`)
    // In real implementation: git checkout -b ${branchName} ${fromBranch || ''}
  }
}

const gitService = new GitService()

self.onmessage = async (event: MessageEvent<GitRequest>) => {
  const { type, workspaceRoot, filePath, message, files, branchName, fromBranch } = event.data

  try {
    switch (type) {
      case 'get-status':
        const status = await gitService.getStatus(workspaceRoot)
        self.postMessage({ type: 'git-status', data: status })
        break

      case 'get-diff':
        if (filePath) {
          const diff = await gitService.getDiff(workspaceRoot, filePath)
          self.postMessage({ type: 'git-diff', data: diff })
        }
        break

      case 'get-branches':
        const branches = await gitService.getBranches(workspaceRoot)
        self.postMessage({ type: 'git-branches', data: branches })
        break

      case 'get-commits':
        const commits = await gitService.getCommits(workspaceRoot)
        self.postMessage({ type: 'git-commits', data: commits })
        break

      case 'get-blame':
        if (filePath) {
          const blame = await gitService.getBlame(workspaceRoot, filePath)
          self.postMessage({ type: 'git-blame', data: blame })
        }
        break

      case 'stage-file':
        if (filePath) {
          await gitService.stageFile(workspaceRoot, filePath)
          self.postMessage({ type: 'git-stage-complete', data: { filePath } })
        }
        break

      case 'unstage-file':
        if (filePath) {
          await gitService.unstageFile(workspaceRoot, filePath)
          self.postMessage({ type: 'git-unstage-complete', data: { filePath } })
        }
        break

      case 'commit':
        if (message) {
          await gitService.commit(workspaceRoot, message, files)
          self.postMessage({ type: 'git-commit-complete', data: { message } })
        }
        break

      case 'switch-branch':
        if (branchName) {
          await gitService.switchBranch(workspaceRoot, branchName)
          self.postMessage({ type: 'git-branch-switched', data: { branchName } })
        }
        break

      case 'create-branch':
        if (branchName) {
          await gitService.createBranch(workspaceRoot, branchName, fromBranch)
          self.postMessage({ type: 'git-branch-created', data: { branchName } })
        }
        break

      default:
        self.postMessage({ type: 'git-error', data: `Unknown command: ${type}` })
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    self.postMessage({ type: 'git-error', data: errorMessage })
  }
}

export {}