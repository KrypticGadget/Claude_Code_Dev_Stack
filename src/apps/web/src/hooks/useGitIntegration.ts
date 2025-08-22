import { useState, useCallback, useRef, useEffect } from 'react'
import { Monaco } from '@monaco-editor/react'
import { editor } from 'monaco-editor'

export interface GitStatus {
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

export interface GitDiff {
  filePath: string
  oldContent: string
  newContent: string
  hunks: GitHunk[]
}

export interface GitHunk {
  oldStart: number
  oldLines: number
  newStart: number
  newLines: number
  lines: GitDiffLine[]
}

export interface GitDiffLine {
  type: 'add' | 'remove' | 'context'
  content: string
  lineNumber: number
}

export interface GitCommit {
  hash: string
  author: string
  date: Date
  message: string
  files: string[]
}

export interface GitBranch {
  name: string
  current: boolean
  remote: boolean
  upstream?: string
}

export const useGitIntegration = (
  enabled: boolean = false,
  filePath?: string,
  workspaceRoot?: string
) => {
  const [gitStatus, setGitStatus] = useState<GitStatus | null>(null)
  const [currentDiff, setCurrentDiff] = useState<GitDiff | null>(null)
  const [branches, setBranches] = useState<GitBranch[]>([])
  const [commitHistory, setCommitHistory] = useState<GitCommit[]>([])
  const [isGitRepo, setIsGitRepo] = useState(false)

  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)
  const monacoRef = useRef<Monaco | null>(null)
  const gitServiceRef = useRef<Worker | null>(null)

  const setupGitIntegration = useCallback(async (
    editorInstance: editor.IStandaloneCodeEditor,
    monacoInstance: Monaco
  ) => {
    if (!enabled || !workspaceRoot) return

    editorRef.current = editorInstance
    monacoRef.current = monacoInstance

    // Initialize Git service worker
    initializeGitService()

    // Setup Git decorations
    setupGitDecorations(editorInstance, monacoInstance)

    // Setup Git-specific commands
    setupGitCommands(editorInstance, monacoInstance)

    // Initial Git status check
    await refreshGitStatus()

    // Watch for file changes
    watchFileChanges(editorInstance)

  }, [enabled, workspaceRoot])

  const initializeGitService = () => {
    gitServiceRef.current = new Worker(
      new URL('../workers/gitServiceWorker.ts', import.meta.url),
      { type: 'module' }
    )

    gitServiceRef.current.onmessage = (event) => {
      const { type, data } = event.data
      
      switch (type) {
        case 'git-status':
          setGitStatus(data)
          setIsGitRepo(true)
          break
        case 'git-diff':
          setCurrentDiff(data)
          updateDiffDecorations(data)
          break
        case 'git-branches':
          setBranches(data)
          break
        case 'git-commits':
          setCommitHistory(data)
          break
        case 'git-error':
          console.error('Git service error:', data)
          setIsGitRepo(false)
          break
      }
    }
  }

  const setupGitDecorations = (
    editorInstance: editor.IStandaloneCodeEditor,
    monacoInstance: Monaco
  ) => {
    // Add Git-related context menu items
    editorInstance.addAction({
      id: 'git-diff',
      label: 'Show Git Diff',
      contextMenuGroupId: 'git',
      contextMenuOrder: 1,
      run: () => showDiff()
    })

    editorInstance.addAction({
      id: 'git-blame',
      label: 'Git Blame',
      contextMenuGroupId: 'git',
      contextMenuOrder: 2,
      run: () => showBlame()
    })

    editorInstance.addAction({
      id: 'git-stage-file',
      label: 'Stage File',
      contextMenuGroupId: 'git',
      contextMenuOrder: 3,
      run: () => stageFile(filePath)
    })

    editorInstance.addAction({
      id: 'git-unstage-file',
      label: 'Unstage File',
      contextMenuGroupId: 'git',
      contextMenuOrder: 4,
      run: () => unstageFile(filePath)
    })

    // Add gutter decorations for Git changes
    editorInstance.onDidChangeModelContent(() => {
      if (filePath) {
        requestDiff(filePath)
      }
    })
  }

  const setupGitCommands = (
    editorInstance: editor.IStandaloneCodeEditor,
    monacoInstance: Monaco
  ) => {
    // Git commands palette
    editorInstance.addCommand(
      monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyMod.Shift | monacoInstance.KeyCode.KeyG,
      () => {
        // Open Git command palette
        showGitCommandPalette()
      }
    )

    // Quick diff toggle
    editorInstance.addCommand(
      monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyCode.KeyD,
      () => {
        toggleDiffView()
      }
    )
  }

  const watchFileChanges = (editorInstance: editor.IStandaloneCodeEditor) => {
    editorInstance.onDidChangeModelContent(() => {
      // Debounced Git status refresh
      debounceGitStatus()
    })
  }

  const refreshGitStatus = useCallback(async () => {
    if (!gitServiceRef.current || !workspaceRoot) return

    gitServiceRef.current.postMessage({
      type: 'get-status',
      workspaceRoot
    })
  }, [workspaceRoot])

  const requestDiff = useCallback((targetFilePath: string) => {
    if (!gitServiceRef.current || !workspaceRoot) return

    gitServiceRef.current.postMessage({
      type: 'get-diff',
      workspaceRoot,
      filePath: targetFilePath
    })
  }, [workspaceRoot])

  const showDiff = useCallback(() => {
    if (!filePath) return
    requestDiff(filePath)
  }, [filePath, requestDiff])

  const showBlame = useCallback(async () => {
    if (!gitServiceRef.current || !workspaceRoot || !filePath) return

    gitServiceRef.current.postMessage({
      type: 'get-blame',
      workspaceRoot,
      filePath
    })
  }, [workspaceRoot, filePath])

  const stageFile = useCallback(async (targetFilePath?: string) => {
    if (!gitServiceRef.current || !workspaceRoot) return

    const fileToStage = targetFilePath || filePath
    if (!fileToStage) return

    gitServiceRef.current.postMessage({
      type: 'stage-file',
      workspaceRoot,
      filePath: fileToStage
    })

    // Refresh status after staging
    setTimeout(refreshGitStatus, 100)
  }, [workspaceRoot, filePath, refreshGitStatus])

  const unstageFile = useCallback(async (targetFilePath?: string) => {
    if (!gitServiceRef.current || !workspaceRoot) return

    const fileToUnstage = targetFilePath || filePath
    if (!fileToUnstage) return

    gitServiceRef.current.postMessage({
      type: 'unstage-file',
      workspaceRoot,
      filePath: fileToUnstage
    })

    // Refresh status after unstaging
    setTimeout(refreshGitStatus, 100)
  }, [workspaceRoot, filePath, refreshGitStatus])

  const commitChanges = useCallback(async (message: string, files?: string[]) => {
    if (!gitServiceRef.current || !workspaceRoot) return

    gitServiceRef.current.postMessage({
      type: 'commit',
      workspaceRoot,
      message,
      files
    })

    // Refresh status after commit
    setTimeout(refreshGitStatus, 500)
  }, [workspaceRoot, refreshGitStatus])

  const switchBranch = useCallback(async (branchName: string) => {
    if (!gitServiceRef.current || !workspaceRoot) return

    gitServiceRef.current.postMessage({
      type: 'switch-branch',
      workspaceRoot,
      branchName
    })

    // Refresh status after branch switch
    setTimeout(refreshGitStatus, 500)
  }, [workspaceRoot, refreshGitStatus])

  const createBranch = useCallback(async (branchName: string, fromBranch?: string) => {
    if (!gitServiceRef.current || !workspaceRoot) return

    gitServiceRef.current.postMessage({
      type: 'create-branch',
      workspaceRoot,
      branchName,
      fromBranch
    })

    // Refresh branches after creation
    setTimeout(() => {
      gitServiceRef.current?.postMessage({
        type: 'get-branches',
        workspaceRoot
      })
    }, 100)
  }, [workspaceRoot])

  const updateDiffDecorations = useCallback((diff: GitDiff) => {
    if (!editorRef.current || !monacoRef.current) return

    const decorations: editor.IModelDeltaDecoration[] = []

    diff.hunks.forEach(hunk => {
      hunk.lines.forEach(line => {
        if (line.type !== 'context') {
          decorations.push({
            range: new monacoRef.current!.Range(
              line.lineNumber,
              1,
              line.lineNumber,
              1
            ),
            options: {
              isWholeLine: true,
              className: `git-diff-${line.type}`,
              glyphMarginClassName: `git-glyph-${line.type}`,
              overviewRuler: {
                color: line.type === 'add' ? '#28a745' : '#dc3545',
                position: monacoRef.current!.editor.OverviewRulerLane.Left
              }
            }
          })
        }
      })
    })

    // Clear existing Git decorations and apply new ones
    const existingDecorations = editorRef.current.getModel()?.getAllDecorations()
      ?.filter(d => 
        d.options.className?.includes('git-diff') ||
        d.options.glyphMarginClassName?.includes('git-glyph')
      )
      ?.map(d => d.id) || []

    editorRef.current.deltaDecorations(existingDecorations, decorations)
  }, [])

  const toggleDiffView = useCallback(() => {
    if (!editorRef.current || !monacoRef.current || !currentDiff) return

    // Create diff editor
    const diffEditor = monacoRef.current.editor.createDiffEditor(
      document.createElement('div'),
      {
        enableSplitViewResizing: true,
        renderSideBySide: true,
        ignoreTrimWhitespace: false,
        renderIndicators: true
      }
    )

    const originalModel = monacoRef.current.editor.createModel(
      currentDiff.oldContent,
      undefined,
      monacoRef.current.Uri.file(currentDiff.filePath + '.original')
    )

    const modifiedModel = monacoRef.current.editor.createModel(
      currentDiff.newContent,
      undefined,
      monacoRef.current.Uri.file(currentDiff.filePath)
    )

    diffEditor.setModel({
      original: originalModel,
      modified: modifiedModel
    })

    // This would typically open in a new panel or modal
    console.log('Diff view toggled', { diffEditor, currentDiff })
  }, [currentDiff])

  const showGitCommandPalette = useCallback(() => {
    // This would typically show a command palette with Git commands
    const commands = [
      'Git: Stage All Changes',
      'Git: Commit Staged Changes',
      'Git: Push',
      'Git: Pull',
      'Git: Fetch',
      'Git: Switch Branch',
      'Git: Create Branch',
      'Git: Merge Branch',
      'Git: Show Git Graph',
      'Git: View File History'
    ]

    console.log('Git command palette:', commands)
  }, [])

  // Debounced Git status refresh
  const debounceGitStatus = useCallback(
    debounce(() => refreshGitStatus(), 1000),
    [refreshGitStatus]
  )

  // Cleanup
  useEffect(() => {
    return () => {
      if (gitServiceRef.current) {
        gitServiceRef.current.terminate()
      }
    }
  }, [])

  // Get file status
  const getFileStatus = useCallback((targetFilePath: string): 'modified' | 'added' | 'deleted' | 'untracked' | 'staged' | 'clean' => {
    if (!gitStatus) return 'clean'

    if (gitStatus.staged.includes(targetFilePath)) return 'staged'
    if (gitStatus.modified.includes(targetFilePath)) return 'modified'
    if (gitStatus.added.includes(targetFilePath)) return 'added'
    if (gitStatus.deleted.includes(targetFilePath)) return 'deleted'
    if (gitStatus.untracked.includes(targetFilePath)) return 'untracked'
    
    return 'clean'
  }, [gitStatus])

  return {
    setupGitIntegration,
    gitStatus,
    currentDiff,
    branches,
    commitHistory,
    isGitRepo,
    refreshGitStatus,
    showDiff,
    showBlame,
    stageFile,
    unstageFile,
    commitChanges,
    switchBranch,
    createBranch,
    toggleDiffView,
    getFileStatus,
    isGitEnabled: enabled
  }
}

// Utility function for debouncing
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}