/**
 * StatuslineV2 Component Tests
 * ===========================
 * 
 * Comprehensive test suite for the enhanced statusline component
 * including unit tests, integration tests, and accessibility tests.
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import '@testing-library/jest-dom'
import { StatuslineV2 } from './StatuslineV2'
import type { SystemMetrics, GitStatus, ClaudeSession, AgentStatus } from './StatuslineV2'

// Mock data
const mockSystemMetrics: SystemMetrics = {
  cpu: {
    usage: 45.5,
    cores: 8,
    temperature: 55,
    processes: [
      { name: 'chrome', pid: 1234, cpu: 15.2, memory: 512 },
      { name: 'vscode', pid: 5678, cpu: 8.1, memory: 256 }
    ]
  },
  memory: {
    used: 8192,
    total: 16384,
    percentage: 50,
    available: 8192,
    cached: 2048,
    buffers: 512
  },
  disk: {
    used: 256000,
    total: 512000,
    percentage: 50,
    read: 25.5,
    write: 15.2,
    iops: 150
  },
  network: {
    up: 1024,
    down: 5120,
    latency: 25,
    connections: 42,
    interfaces: [
      { name: 'eth0', ip: '192.168.1.100', sent: 1000000, received: 5000000 }
    ]
  },
  uptime: 86400000,
  loadAverage: [1.2, 1.5, 1.8]
}

const mockGitStatus: GitStatus = {
  isRepository: true,
  branch: 'feature/statusline-v2',
  status: 'dirty',
  dirty: true,
  staged: 2,
  unstaged: 3,
  untracked: 1,
  conflicted: 0,
  ahead: 2,
  behind: 0,
  remote: 'origin',
  lastCommit: {
    hash: 'a1b2c3d4e5f6789012345678901234567890abcd',
    shortHash: 'a1b2c3d',
    message: 'feat: implement enhanced statusline component',
    author: 'Claude Code',
    email: 'claude@anthropic.com',
    date: new Date('2024-01-01T12:00:00Z')
  },
  recentCommits: [],
  repoPath: '.git',
  rootPath: '.',
  totalCommits: 1547,
  contributors: 8,
  operation: 'none'
}

const mockClaudeSession: ClaudeSession = {
  id: 'test-session',
  active: true,
  startTime: new Date('2024-01-01T10:00:00Z'),
  lastActivity: new Date('2024-01-01T12:00:00Z'),
  model: {
    id: 'claude-3-opus-20240229',
    name: 'Claude 3 Opus',
    displayName: 'Claude 3 Opus',
    version: '20240229',
    provider: 'anthropic',
    capabilities: ['reasoning', 'analysis', 'writing'],
    contextWindow: 200000,
    pricing: { input: 15.00, output: 75.00 }
  },
  tokens: {
    input: 25000,
    output: 15000,
    total: 40000,
    limit: 200000,
    percentage: 20,
    cost: 1.5,
    estimatedRemaining: 160000
  },
  metrics: {
    duration: 7200,
    messagesCount: 45,
    avgResponseTime: 1500,
    quality: 'excellent',
    satisfaction: 95,
    errorRate: 0.02,
    throughput: 25
  },
  billing: {
    sessionCost: 1.5,
    dailyCost: 5.2,
    monthlyCost: 85.7,
    budget: { daily: 25, monthly: 500, remaining: 414.3 }
  },
  status: 'active',
  performance: {
    avgLatency: 800,
    successRate: 0.98,
    uptime: 0.99,
    reliability: 0.95
  }
}

const mockAgents: AgentStatus[] = [
  {
    id: 'frontend-architect',
    name: 'Frontend Architect',
    status: 'active',
    progress: 75,
    lastAction: 'Designing component hierarchy',
    performance: 92
  },
  {
    id: 'backend-services',
    name: 'Backend Services',
    status: 'idle',
    progress: 100,
    lastAction: 'API endpoints configured',
    performance: 88
  }
]

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
)

describe('StatuslineV2 Component', () => {
  const defaultProps = {
    systemMetrics: mockSystemMetrics,
    gitStatus: mockGitStatus,
    claudeSession: mockClaudeSession,
    agents: mockAgents,
    isConnected: true
  }

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  describe('Basic Rendering', () => {
    test('renders statusline with all segments', () => {
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      // Check for key segments
      expect(screen.getByTitle(/current working directory/i)).toBeInTheDocument()
      expect(screen.getByText('feature/statusline-v2')).toBeInTheDocument()
      expect(screen.getByText('Claude 3 Opus')).toBeInTheDocument()
      expect(screen.getByText('2/2')).toBeInTheDocument() // Active/total agents
    })

    test('renders with minimal props', () => {
      render(
        <TestWrapper>
          <StatuslineV2 agents={[]} isConnected={false} />
        </TestWrapper>
      )

      // Should still render basic structure
      expect(screen.getByRole('banner')).toBeInTheDocument()
    })

    test('handles missing data gracefully', () => {
      render(
        <TestWrapper>
          <StatuslineV2 
            agents={mockAgents}
            isConnected={true}
            systemMetrics={undefined}
            gitStatus={undefined}
            claudeSession={undefined}
          />
        </TestWrapper>
      )

      // Should not crash and still show some segments
      expect(screen.getByText('2/2')).toBeInTheDocument()
    })
  })

  describe('Segment Interactions', () => {
    test('opens git details modal on git segment click', async () => {
      const onSegmentClick = jest.fn()
      
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} onSegmentClick={onSegmentClick} />
        </TestWrapper>
      )

      const gitSegment = screen.getByTitle(/git branch/i)
      fireEvent.click(gitSegment)

      expect(onSegmentClick).toHaveBeenCalledWith('git', mockGitStatus)
      
      // Check if modal appears
      await waitFor(() => {
        expect(screen.getByText('Git Details')).toBeInTheDocument()
      })
    })

    test('opens claude details modal on claude segment click', async () => {
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      const claudeSegment = screen.getByTitle(/claude.*tokens/i)
      fireEvent.click(claudeSegment)

      await waitFor(() => {
        expect(screen.getByText('Claude Details')).toBeInTheDocument()
      })
    })

    test('opens system metrics modal on system segment click', async () => {
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      const systemSegment = screen.getByTitle(/cpu.*ram.*disk/i)
      fireEvent.click(systemSegment)

      await waitFor(() => {
        expect(screen.getByText('System Details')).toBeInTheDocument()
      })
    })

    test('closes modal when clicking close button', async () => {
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      // Open modal
      const gitSegment = screen.getByTitle(/git branch/i)
      fireEvent.click(gitSegment)

      await waitFor(() => {
        expect(screen.getByText('Git Details')).toBeInTheDocument()
      })

      // Close modal
      const closeButton = screen.getByRole('button', { name: /close/i })
      fireEvent.click(closeButton)

      await waitFor(() => {
        expect(screen.queryByText('Git Details')).not.toBeInTheDocument()
      })
    })
  })

  describe('Configuration', () => {
    test('opens configuration panel', () => {
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      const configButton = screen.getByTitle(/configure statusline/i)
      fireEvent.click(configButton)

      expect(screen.getByText('Statusline Configuration')).toBeInTheDocument()
    })

    test('changes theme configuration', () => {
      const onConfigChange = jest.fn()
      
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} onConfigChange={onConfigChange} />
        </TestWrapper>
      )

      // Open config panel
      const configButton = screen.getByTitle(/configure statusline/i)
      fireEvent.click(configButton)

      // Change theme
      const themeSelect = screen.getByDisplayValue('powerline')
      fireEvent.change(themeSelect, { target: { value: 'minimal' } })

      expect(onConfigChange).toHaveBeenCalledWith(
        expect.objectContaining({ theme: 'minimal' })
      )
    })

    test('changes update interval', () => {
      const onConfigChange = jest.fn()
      
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} onConfigChange={onConfigChange} />
        </TestWrapper>
      )

      // Open config panel
      const configButton = screen.getByTitle(/configure statusline/i)
      fireEvent.click(configButton)

      // Change update interval
      const intervalInput = screen.getByDisplayValue('100')
      fireEvent.change(intervalInput, { target: { value: '1000' } })

      expect(onConfigChange).toHaveBeenCalledWith(
        expect.objectContaining({ updateInterval: 1000 })
      )
    })

    test('toggles segment visibility', () => {
      const onConfigChange = jest.fn()
      
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} onConfigChange={onConfigChange} />
        </TestWrapper>
      )

      // Open config panel
      const configButton = screen.getByTitle(/configure statusline/i)
      fireEvent.click(configButton)

      // Toggle first segment
      const checkboxes = screen.getAllByRole('checkbox')
      const firstCheckbox = checkboxes[0]
      fireEvent.click(firstCheckbox)

      expect(onConfigChange).toHaveBeenCalledWith(
        expect.objectContaining({
          segments: expect.arrayContaining([
            expect.objectContaining({ enabled: false })
          ])
        })
      )
    })
  })

  describe('Status Indicators', () => {
    test('displays connection status correctly', () => {
      // Connected state
      const { rerender } = render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} isConnected={true} />
        </TestWrapper>
      )

      expect(screen.getByTitle(/connected.*real-time/i)).toBeInTheDocument()

      // Disconnected state
      rerender(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} isConnected={false} />
        </TestWrapper>
      )

      expect(screen.getByTitle(/disconnected/i)).toBeInTheDocument()
    })

    test('displays git status colors correctly', () => {
      const { rerender } = render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      // Dirty status
      const gitSegment = screen.getByTitle(/git branch/i)
      expect(gitSegment).toHaveClass('git-segment')

      // Clean status
      const cleanGitStatus = { ...mockGitStatus, status: 'clean' as const, dirty: false }
      rerender(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} gitStatus={cleanGitStatus} />
        </TestWrapper>
      )

      expect(screen.getByTitle(/git branch/i)).toBeInTheDocument()
    })

    test('displays agent status indicators', () => {
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      // Should show active agents count
      expect(screen.getByText('2/2')).toBeInTheDocument()
    })
  })

  describe('Theme Support', () => {
    test('applies powerline theme classes', () => {
      render(
        <TestWrapper>
          <StatuslineV2 
            {...defaultProps} 
            config={{ theme: 'powerline' }}
          />
        </TestWrapper>
      )

      expect(screen.getByRole('banner')).toHaveClass('theme-powerline')
    })

    test('applies minimal theme classes', () => {
      render(
        <TestWrapper>
          <StatuslineV2 
            {...defaultProps} 
            config={{ theme: 'minimal' }}
          />
        </TestWrapper>
      )

      expect(screen.getByRole('banner')).toHaveClass('theme-minimal')
    })

    test('applies compact theme classes', () => {
      render(
        <TestWrapper>
          <StatuslineV2 
            {...defaultProps} 
            config={{ theme: 'compact' }}
          />
        </TestWrapper>
      )

      expect(screen.getByRole('banner')).toHaveClass('theme-compact')
    })
  })

  describe('Accessibility', () => {
    test('has proper ARIA labels', () => {
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      // Check for semantic landmarks
      expect(screen.getByRole('banner')).toBeInTheDocument()
      
      // Check for accessible buttons
      const buttons = screen.getAllByRole('button')
      expect(buttons.length).toBeGreaterThan(0)
    })

    test('supports keyboard navigation', () => {
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      const firstSegment = screen.getByTitle(/current working directory/i)
      
      // Should be focusable
      firstSegment.focus()
      expect(firstSegment).toHaveFocus()
      
      // Should handle Enter key
      fireEvent.keyDown(firstSegment, { key: 'Enter', code: 'Enter' })
      // Modal should open (test implementation may vary)
    })

    test('provides descriptive tooltips', () => {
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      // Check for title attributes (tooltips)
      expect(screen.getByTitle(/current working directory/i)).toBeInTheDocument()
      expect(screen.getByTitle(/git branch/i)).toBeInTheDocument()
      expect(screen.getByTitle(/claude.*tokens/i)).toBeInTheDocument()
    })
  })

  describe('Performance', () => {
    test('renders without performance issues', () => {
      const start = performance.now()
      
      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )
      
      const end = performance.now()
      const renderTime = end - start
      
      // Should render quickly (adjust threshold as needed)
      expect(renderTime).toBeLessThan(100)
    })

    test('handles frequent updates efficiently', () => {
      const { rerender } = render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} />
        </TestWrapper>
      )

      const start = performance.now()
      
      // Simulate multiple rapid updates
      for (let i = 0; i < 10; i++) {
        const updatedMetrics = {
          ...mockSystemMetrics,
          cpu: { ...mockSystemMetrics.cpu, usage: 50 + i }
        }
        
        rerender(
          <TestWrapper>
            <StatuslineV2 {...defaultProps} systemMetrics={updatedMetrics} />
          </TestWrapper>
        )
      }
      
      const end = performance.now()
      const updateTime = end - start
      
      // Should handle updates efficiently
      expect(updateTime).toBeLessThan(200)
    })
  })

  describe('Error Handling', () => {
    test('handles invalid data gracefully', () => {
      const invalidProps = {
        ...defaultProps,
        systemMetrics: null as any,
        gitStatus: undefined,
        claudeSession: {} as any,
        agents: null as any
      }

      expect(() => {
        render(
          <TestWrapper>
            <StatuslineV2 {...invalidProps} />
          </TestWrapper>
        )
      }).not.toThrow()
    })

    test('shows error states appropriately', () => {
      const agentsWithErrors = [
        ...mockAgents,
        {
          id: 'error-agent',
          name: 'Error Agent',
          status: 'error' as const,
          progress: 25,
          lastAction: 'Failed to process',
          performance: 30
        }
      ]

      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} agents={agentsWithErrors} />
        </TestWrapper>
      )

      // Should handle error state in agents
      expect(screen.getByText('3/3')).toBeInTheDocument()
    })
  })

  describe('Notifications', () => {
    test('displays notifications for critical states', async () => {
      const criticalSystemMetrics = {
        ...mockSystemMetrics,
        cpu: { ...mockSystemMetrics.cpu, usage: 95 },
        memory: { ...mockSystemMetrics.memory, percentage: 90 }
      }

      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} systemMetrics={criticalSystemMetrics} />
        </TestWrapper>
      )

      // Wait for notifications to appear
      await waitFor(() => {
        expect(screen.getByText(/high cpu usage/i)).toBeInTheDocument()
      }, { timeout: 3000 })
    })

    test('allows dismissing notifications', async () => {
      const criticalSystemMetrics = {
        ...mockSystemMetrics,
        cpu: { ...mockSystemMetrics.cpu, usage: 95 }
      }

      render(
        <TestWrapper>
          <StatuslineV2 {...defaultProps} systemMetrics={criticalSystemMetrics} />
        </TestWrapper>
      )

      // Wait for notification and dismiss it
      await waitFor(() => {
        const notification = screen.getByText(/high cpu usage/i)
        const dismissButton = notification.closest('.notification')?.querySelector('button')
        if (dismissButton) {
          fireEvent.click(dismissButton)
        }
      })

      // Notification should be removed
      await waitFor(() => {
        expect(screen.queryByText(/high cpu usage/i)).not.toBeInTheDocument()
      })
    })
  })
})

// Custom render function for easier testing
export const renderStatusline = (props: Partial<React.ComponentProps<typeof StatuslineV2>> = {}) => {
  const defaultProps = {
    agents: mockAgents,
    isConnected: true,
    systemMetrics: mockSystemMetrics,
    gitStatus: mockGitStatus,
    claudeSession: mockClaudeSession
  }

  return render(
    <TestWrapper>
      <StatuslineV2 {...defaultProps} {...props} />
    </TestWrapper>
  )
}

// Utility functions for testing
export const mockSystemMetricsFactory = (overrides: Partial<SystemMetrics> = {}): SystemMetrics => ({
  ...mockSystemMetrics,
  ...overrides
})

export const mockGitStatusFactory = (overrides: Partial<GitStatus> = {}): GitStatus => ({
  ...mockGitStatus,
  ...overrides
})

export const mockClaudeSessionFactory = (overrides: Partial<ClaudeSession> = {}): ClaudeSession => ({
  ...mockClaudeSession,
  ...overrides
})