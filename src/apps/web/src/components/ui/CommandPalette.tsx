import React, { useState, useEffect, useRef, useMemo } from 'react'
import { Monaco } from '@monaco-editor/react'
import { editor } from 'monaco-editor'
import { Search, Command, Zap, Settings, GitBranch, Bug, FileText } from 'lucide-react'

export interface CommandPaletteProps {
  editor: editor.IStandaloneCodeEditor | null
  monaco: Monaco | null
  onClose: () => void
}

interface Command {
  id: string
  label: string
  description?: string
  category: 'file' | 'edit' | 'selection' | 'view' | 'debug' | 'git' | 'settings'
  icon?: React.ReactNode
  keybinding?: string
  action: () => void
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  editor,
  monaco,
  onClose
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const commands: Command[] = useMemo(() => [
    // File Commands
    {
      id: 'file.new',
      label: 'New File',
      description: 'Create a new file',
      category: 'file',
      icon: <FileText size={16} />,
      keybinding: 'Ctrl+N',
      action: () => {
        // New file action
        console.log('New file')
        onClose()
      }
    },
    {
      id: 'file.save',
      label: 'Save',
      description: 'Save the current file',
      category: 'file',
      icon: <FileText size={16} />,
      keybinding: 'Ctrl+S',
      action: () => {
        if (editor) {
          const model = editor.getModel()
          if (model) {
            const saveEvent = new CustomEvent('monaco-save', {
              detail: { content: model.getValue() }
            })
            window.dispatchEvent(saveEvent)
          }
        }
        onClose()
      }
    },

    // Edit Commands
    {
      id: 'edit.format',
      label: 'Format Document',
      description: 'Format the entire document',
      category: 'edit',
      icon: <Zap size={16} />,
      keybinding: 'Shift+Alt+F',
      action: () => {
        editor?.getAction('editor.action.formatDocument')?.run()
        onClose()
      }
    },
    {
      id: 'edit.find',
      label: 'Find',
      description: 'Find in current file',
      category: 'edit',
      icon: <Search size={16} />,
      keybinding: 'Ctrl+F',
      action: () => {
        editor?.getAction('actions.find')?.run()
        onClose()
      }
    },
    {
      id: 'edit.replace',
      label: 'Replace',
      description: 'Find and replace in current file',
      category: 'edit',
      icon: <Search size={16} />,
      keybinding: 'Ctrl+H',
      action: () => {
        editor?.getAction('editor.action.startFindReplaceAction')?.run()
        onClose()
      }
    },
    {
      id: 'edit.comment',
      label: 'Toggle Line Comment',
      description: 'Comment or uncomment current line',
      category: 'edit',
      keybinding: 'Ctrl+/',
      action: () => {
        editor?.getAction('editor.action.commentLine')?.run()
        onClose()
      }
    },
    {
      id: 'edit.blockComment',
      label: 'Toggle Block Comment',
      description: 'Comment or uncomment selected block',
      category: 'edit',
      keybinding: 'Shift+Alt+A',
      action: () => {
        editor?.getAction('editor.action.blockComment')?.run()
        onClose()
      }
    },

    // Selection Commands
    {
      id: 'selection.selectAll',
      label: 'Select All',
      description: 'Select all content',
      category: 'selection',
      keybinding: 'Ctrl+A',
      action: () => {
        editor?.getAction('editor.action.selectAll')?.run()
        onClose()
      }
    },
    {
      id: 'selection.expandSelection',
      label: 'Expand Selection',
      description: 'Expand selection to next logical boundary',
      category: 'selection',
      keybinding: 'Shift+Alt+Right',
      action: () => {
        editor?.getAction('editor.action.smartSelect.expand')?.run()
        onClose()
      }
    },
    {
      id: 'selection.shrinkSelection',
      label: 'Shrink Selection',
      description: 'Shrink selection to previous logical boundary',
      category: 'selection',
      keybinding: 'Shift+Alt+Left',
      action: () => {
        editor?.getAction('editor.action.smartSelect.shrink')?.run()
        onClose()
      }
    },
    {
      id: 'selection.addCursorAbove',
      label: 'Add Cursor Above',
      description: 'Add a cursor above current line',
      category: 'selection',
      keybinding: 'Ctrl+Alt+Up',
      action: () => {
        editor?.getAction('editor.action.insertCursorAbove')?.run()
        onClose()
      }
    },
    {
      id: 'selection.addCursorBelow',
      label: 'Add Cursor Below',
      description: 'Add a cursor below current line',
      category: 'selection',
      keybinding: 'Ctrl+Alt+Down',
      action: () => {
        editor?.getAction('editor.action.insertCursorBelow')?.run()
        onClose()
      }
    },

    // View Commands
    {
      id: 'view.toggleMinimap',
      label: 'Toggle Minimap',
      description: 'Show or hide the minimap',
      category: 'view',
      action: () => {
        if (editor) {
          const currentOptions = editor.getOptions()
          const minimapEnabled = currentOptions.get(monaco?.editor.EditorOption.minimap)?.enabled
          editor.updateOptions({
            minimap: { enabled: !minimapEnabled }
          })
        }
        onClose()
      }
    },
    {
      id: 'view.toggleWordWrap',
      label: 'Toggle Word Wrap',
      description: 'Enable or disable word wrapping',
      category: 'view',
      keybinding: 'Alt+Z',
      action: () => {
        editor?.getAction('editor.action.toggleWordWrap')?.run()
        onClose()
      }
    },
    {
      id: 'view.toggleWhitespace',
      label: 'Toggle Whitespace',
      description: 'Show or hide whitespace characters',
      category: 'view',
      action: () => {
        if (editor) {
          const currentOptions = editor.getOptions()
          const renderWhitespace = currentOptions.get(monaco?.editor.EditorOption.renderWhitespace)
          editor.updateOptions({
            renderWhitespace: renderWhitespace === 'all' ? 'none' : 'all'
          })
        }
        onClose()
      }
    },
    {
      id: 'view.foldAll',
      label: 'Fold All',
      description: 'Fold all regions',
      category: 'view',
      keybinding: 'Ctrl+K Ctrl+0',
      action: () => {
        editor?.getAction('editor.foldAll')?.run()
        onClose()
      }
    },
    {
      id: 'view.unfoldAll',
      label: 'Unfold All',
      description: 'Unfold all regions',
      category: 'view',
      keybinding: 'Ctrl+K Ctrl+J',
      action: () => {
        editor?.getAction('editor.unfoldAll')?.run()
        onClose()
      }
    },

    // Navigation Commands
    {
      id: 'nav.goToLine',
      label: 'Go to Line',
      description: 'Go to a specific line number',
      category: 'edit',
      keybinding: 'Ctrl+G',
      action: () => {
        editor?.getAction('editor.action.gotoLine')?.run()
        onClose()
      }
    },
    {
      id: 'nav.goToDefinition',
      label: 'Go to Definition',
      description: 'Navigate to symbol definition',
      category: 'edit',
      keybinding: 'F12',
      action: () => {
        editor?.getAction('editor.action.revealDefinition')?.run()
        onClose()
      }
    },
    {
      id: 'nav.goToReferences',
      label: 'Go to References',
      description: 'Find all references',
      category: 'edit',
      keybinding: 'Shift+F12',
      action: () => {
        editor?.getAction('editor.action.goToReferences')?.run()
        onClose()
      }
    },

    // Debug Commands
    {
      id: 'debug.toggleBreakpoint',
      label: 'Toggle Breakpoint',
      description: 'Add or remove breakpoint on current line',
      category: 'debug',
      icon: <Bug size={16} />,
      keybinding: 'F9',
      action: () => {
        const position = editor?.getPosition()
        if (position) {
          const breakpointEvent = new CustomEvent('monaco-toggle-breakpoint', {
            detail: { line: position.lineNumber }
          })
          window.dispatchEvent(breakpointEvent)
        }
        onClose()
      }
    },
    {
      id: 'debug.start',
      label: 'Start Debugging',
      description: 'Start debugging session',
      category: 'debug',
      icon: <Bug size={16} />,
      keybinding: 'F5',
      action: () => {
        const debugEvent = new CustomEvent('monaco-debug-start')
        window.dispatchEvent(debugEvent)
        onClose()
      }
    },

    // Git Commands
    {
      id: 'git.showDiff',
      label: 'Show Git Diff',
      description: 'Show changes in current file',
      category: 'git',
      icon: <GitBranch size={16} />,
      action: () => {
        const gitEvent = new CustomEvent('monaco-git-diff')
        window.dispatchEvent(gitEvent)
        onClose()
      }
    },
    {
      id: 'git.stageFile',
      label: 'Stage File',
      description: 'Stage current file for commit',
      category: 'git',
      icon: <GitBranch size={16} />,
      action: () => {
        const gitEvent = new CustomEvent('monaco-git-stage')
        window.dispatchEvent(gitEvent)
        onClose()
      }
    },

    // Settings Commands
    {
      id: 'settings.preferences',
      label: 'Open Settings',
      description: 'Open editor preferences',
      category: 'settings',
      icon: <Settings size={16} />,
      action: () => {
        const settingsEvent = new CustomEvent('monaco-open-settings')
        window.dispatchEvent(settingsEvent)
        onClose()
      }
    }
  ], [editor, monaco, onClose])

  const filteredCommands = useMemo(() => {
    if (!searchQuery.trim()) return commands

    const query = searchQuery.toLowerCase()
    return commands.filter(command =>
      command.label.toLowerCase().includes(query) ||
      command.description?.toLowerCase().includes(query) ||
      command.category.toLowerCase().includes(query)
    )
  }, [commands, searchQuery])

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus()

    // Handle keyboard navigation
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(prev => 
            prev < filteredCommands.length - 1 ? prev + 1 : 0
          )
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(prev => 
            prev > 0 ? prev - 1 : filteredCommands.length - 1
          )
          break
        case 'Enter':
          e.preventDefault()
          if (filteredCommands[selectedIndex]) {
            filteredCommands[selectedIndex].action()
          }
          break
        case 'Escape':
          e.preventDefault()
          onClose()
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [filteredCommands, selectedIndex, onClose])

  useEffect(() => {
    // Reset selection when search changes
    setSelectedIndex(0)
  }, [searchQuery])

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'file': return <FileText size={14} />
      case 'edit': return <Zap size={14} />
      case 'debug': return <Bug size={14} />
      case 'git': return <GitBranch size={14} />
      case 'settings': return <Settings size={14} />
      default: return <Command size={14} />
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'file': return '#007acc'
      case 'edit': return '#f39c12'
      case 'selection': return '#e74c3c'
      case 'view': return '#9b59b6'
      case 'debug': return '#e67e22'
      case 'git': return '#27ae60'
      case 'settings': return '#95a5a6'
      default: return '#34495e'
    }
  }

  return (
    <div className="command-palette-overlay">
      <div className="command-palette">
        <div className="command-palette-header">
          <div className="search-container">
            <Search size={16} className="search-icon" />
            <input
              ref={inputRef}
              type="text"
              placeholder="Type a command or search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="command-search"
            />
          </div>
        </div>

        <div className="command-palette-body">
          {filteredCommands.length > 0 ? (
            <div className="command-list">
              {filteredCommands.map((command, index) => (
                <div
                  key={command.id}
                  className={`command-item ${index === selectedIndex ? 'selected' : ''}`}
                  onClick={() => command.action()}
                  onMouseEnter={() => setSelectedIndex(index)}
                >
                  <div className="command-icon-container">
                    <div 
                      className="command-category-indicator"
                      style={{ backgroundColor: getCategoryColor(command.category) }}
                    />
                    {command.icon || getCategoryIcon(command.category)}
                  </div>
                  
                  <div className="command-content">
                    <div className="command-label">{command.label}</div>
                    {command.description && (
                      <div className="command-description">{command.description}</div>
                    )}
                  </div>

                  {command.keybinding && (
                    <div className="command-keybinding">
                      {command.keybinding.split(' ').map((key, i) => (
                        <kbd key={i} className="keybinding-key">
                          {key}
                        </kbd>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="no-commands">
              <p>No commands found</p>
            </div>
          )}
        </div>

        <div className="command-palette-footer">
          <div className="footer-hint">
            <kbd>↑</kbd><kbd>↓</kbd> to navigate • <kbd>Enter</kbd> to select • <kbd>Esc</kbd> to close
          </div>
        </div>
      </div>
    </div>
  )
}

export default CommandPalette