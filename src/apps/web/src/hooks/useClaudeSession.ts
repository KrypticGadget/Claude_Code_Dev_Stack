/**
 * Claude Session Hook
 * ===================
 * 
 * Provides real-time Claude session information including model details,
 * token usage, costs, performance metrics, and session quality indicators.
 */

import { useState, useEffect, useCallback } from 'react'

export interface TokenUsage {
  input: number
  output: number
  total: number
  limit: number
  percentage: number
  cost: number
  estimatedRemaining: number
}

export interface ModelInfo {
  id: string
  name: string
  displayName: string
  version: string
  provider: 'anthropic' | 'openai' | 'other'
  capabilities: string[]
  contextWindow: number
  pricing: {
    input: number  // per 1K tokens
    output: number // per 1K tokens
  }
}

export interface SessionMetrics {
  duration: number // in seconds
  messagesCount: number
  avgResponseTime: number
  quality: 'excellent' | 'good' | 'fair' | 'poor'
  satisfaction: number // 0-100
  errorRate: number // 0-1
  throughput: number // tokens per second
}

export interface ClaudeSession {
  id: string
  active: boolean
  startTime: Date
  lastActivity: Date
  
  // Model information
  model: ModelInfo
  
  // Token usage
  tokens: TokenUsage
  
  // Session metrics
  metrics: SessionMetrics
  
  // Billing information
  billing: {
    sessionCost: number
    dailyCost: number
    monthlyCost: number
    budget: {
      daily: number
      monthly: number
      remaining: number
    }
  }
  
  // Session state
  status: 'active' | 'idle' | 'thinking' | 'responding' | 'error'
  lastMessage?: {
    content: string
    timestamp: Date
    tokens: number
    responseTime: number
  }
  
  // Performance tracking
  performance: {
    avgLatency: number
    successRate: number
    uptime: number
    reliability: number
  }
}

interface UseClaudeSessionOptions {
  updateInterval?: number
  trackPerformance?: boolean
  enableCostTracking?: boolean
  sessionId?: string
}

interface UseClaudeSessionReturn {
  session: ClaudeSession | null
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
  updateTokenUsage: (tokens: Partial<TokenUsage>) => void
  logMessage: (message: string, tokens: number, responseTime: number) => void
  calculateCost: (inputTokens: number, outputTokens: number) => number
}

// Model definitions
const MODELS: Record<string, ModelInfo> = {
  'claude-3-opus-20240229': {
    id: 'claude-3-opus-20240229',
    name: 'Claude 3 Opus',
    displayName: 'Claude 3 Opus',
    version: '20240229',
    provider: 'anthropic',
    capabilities: ['reasoning', 'analysis', 'writing', 'math', 'coding'],
    contextWindow: 200000,
    pricing: {
      input: 15.00,   // $15 per 1M input tokens
      output: 75.00   // $75 per 1M output tokens
    }
  },
  'claude-3-sonnet-20240229': {
    id: 'claude-3-sonnet-20240229',
    name: 'Claude 3 Sonnet',
    displayName: 'Claude 3 Sonnet',
    version: '20240229',
    provider: 'anthropic',
    capabilities: ['reasoning', 'analysis', 'writing', 'coding'],
    contextWindow: 200000,
    pricing: {
      input: 3.00,    // $3 per 1M input tokens
      output: 15.00   // $15 per 1M output tokens
    }
  },
  'claude-3-haiku-20240307': {
    id: 'claude-3-haiku-20240307',
    name: 'Claude 3 Haiku',
    displayName: 'Claude 3 Haiku',
    version: '20240307',
    provider: 'anthropic',
    capabilities: ['writing', 'analysis', 'coding'],
    contextWindow: 200000,
    pricing: {
      input: 0.25,    // $0.25 per 1M input tokens
      output: 1.25    // $1.25 per 1M output tokens
    }
  }
}

export const useClaudeSession = (
  options: UseClaudeSessionOptions = {}
): UseClaudeSessionReturn => {
  const {
    updateInterval = 1000,
    trackPerformance = true,
    enableCostTracking = true,
    sessionId
  } = options

  const [session, setSession] = useState<ClaudeSession | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Get current model (this would come from actual Claude API)
  const getCurrentModel = useCallback((): ModelInfo => {
    // In a real implementation, this would come from the Claude session
    const modelIds = Object.keys(MODELS)
    const randomModel = modelIds[Math.floor(Math.random() * modelIds.length)]
    return MODELS[randomModel]
  }, [])

  // Generate mock session data
  const generateMockSession = useCallback((): ClaudeSession => {
    const now = new Date()
    const startTime = new Date(now.getTime() - (Math.random() * 3600000)) // Up to 1 hour ago
    const model = getCurrentModel()
    
    const inputTokens = Math.floor(Math.random() * 50000) + 10000
    const outputTokens = Math.floor(Math.random() * 20000) + 5000
    const totalTokens = inputTokens + outputTokens
    const percentage = (totalTokens / model.contextWindow) * 100
    
    const sessionDuration = (now.getTime() - startTime.getTime()) / 1000
    const messagesCount = Math.floor(sessionDuration / 120) + Math.floor(Math.random() * 10)
    
    return {
      id: sessionId || `session-${Date.now()}`,
      active: Math.random() > 0.3,
      startTime,
      lastActivity: new Date(now.getTime() - Math.random() * 300000), // Last 5 minutes
      
      model,
      
      tokens: {
        input: inputTokens,
        output: outputTokens,
        total: totalTokens,
        limit: model.contextWindow,
        percentage,
        cost: (inputTokens / 1000 * model.pricing.input / 1000) + 
              (outputTokens / 1000 * model.pricing.output / 1000),
        estimatedRemaining: Math.max(0, model.contextWindow - totalTokens)
      },
      
      metrics: {
        duration: sessionDuration,
        messagesCount,
        avgResponseTime: 1500 + Math.random() * 2000,
        quality: percentage < 50 ? 'excellent' : 
                percentage < 70 ? 'good' : 
                percentage < 85 ? 'fair' : 'poor',
        satisfaction: Math.max(60, 100 - (percentage * 0.5)),
        errorRate: Math.random() * 0.05, // 0-5% error rate
        throughput: 20 + Math.random() * 30 // tokens per second
      },
      
      billing: {
        sessionCost: (inputTokens / 1000 * model.pricing.input / 1000) + 
                    (outputTokens / 1000 * model.pricing.output / 1000),
        dailyCost: Math.random() * 15 + 5,
        monthlyCost: Math.random() * 200 + 100,
        budget: {
          daily: 25,
          monthly: 500,
          remaining: 350 - (Math.random() * 200 + 100)
        }
      },
      
      status: (['active', 'idle', 'thinking'] as const)[Math.floor(Math.random() * 3)],
      
      lastMessage: {
        content: 'Implementing enhanced statusline component with real-time updates...',
        timestamp: new Date(now.getTime() - Math.random() * 60000),
        tokens: Math.floor(Math.random() * 500) + 100,
        responseTime: Math.random() * 2000 + 500
      },
      
      performance: {
        avgLatency: 800 + Math.random() * 1000,
        successRate: 0.95 + Math.random() * 0.05,
        uptime: 0.98 + Math.random() * 0.02,
        reliability: 0.92 + Math.random() * 0.08
      }
    }
  }, [sessionId, getCurrentModel])

  // Calculate token cost
  const calculateCost = useCallback((inputTokens: number, outputTokens: number): number => {
    if (!session?.model) return 0
    
    const { pricing } = session.model
    return (inputTokens / 1000 * pricing.input / 1000) + 
           (outputTokens / 1000 * pricing.output / 1000)
  }, [session])

  // Update token usage
  const updateTokenUsage = useCallback((tokens: Partial<TokenUsage>) => {
    setSession(prev => {
      if (!prev) return null
      
      const newTokens = { ...prev.tokens, ...tokens }
      newTokens.total = newTokens.input + newTokens.output
      newTokens.percentage = (newTokens.total / prev.model.contextWindow) * 100
      newTokens.estimatedRemaining = Math.max(0, prev.model.contextWindow - newTokens.total)
      newTokens.cost = calculateCost(newTokens.input, newTokens.output)
      
      return {
        ...prev,
        tokens: newTokens,
        lastActivity: new Date()
      }
    })
  }, [calculateCost])

  // Log a message
  const logMessage = useCallback((content: string, tokens: number, responseTime: number) => {
    setSession(prev => {
      if (!prev) return null
      
      const newMetrics = { ...prev.metrics }
      newMetrics.messagesCount++
      newMetrics.avgResponseTime = (newMetrics.avgResponseTime + responseTime) / 2
      
      return {
        ...prev,
        metrics: newMetrics,
        lastMessage: {
          content,
          timestamp: new Date(),
          tokens,
          responseTime
        },
        lastActivity: new Date()
      }
    })
  }, [])

  // Fetch session data from Claude API (mock implementation)
  const fetchSessionData = useCallback(async (): Promise<ClaudeSession> => {
    try {
      setError(null)
      
      // In a real implementation, this would call the Claude API
      // For now, we'll generate mock data
      await new Promise(resolve => setTimeout(resolve, 100)) // Simulate API delay
      
      return generateMockSession()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch session data'
      setError(message)
      throw err
    }
  }, [generateMockSession])

  // Manual refresh
  const refresh = useCallback(async () => {
    try {
      setIsLoading(true)
      const newSession = await fetchSessionData()
      setSession(newSession)
    } catch (err) {
      console.error('Failed to refresh session:', err)
    } finally {
      setIsLoading(false)
    }
  }, [fetchSessionData])

  // Auto-refresh effect
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const newSession = await fetchSessionData()
        setSession(newSession)
        setIsLoading(false)
      } catch (err) {
        console.error('Failed to update session:', err)
        setIsLoading(false)
      }
    }, updateInterval)

    return () => clearInterval(interval)
  }, [updateInterval, fetchSessionData])

  // Performance tracking effect
  useEffect(() => {
    if (!trackPerformance || !session) return

    const interval = setInterval(() => {
      setSession(prev => {
        if (!prev) return null
        
        // Update performance metrics
        const performance = { ...prev.performance }
        performance.avgLatency = performance.avgLatency * 0.9 + (Math.random() * 1000 + 500) * 0.1
        performance.uptime = Math.min(1, performance.uptime + 0.001)
        
        return { ...prev, performance }
      })
    }, 5000) // Update every 5 seconds

    return () => clearInterval(interval)
  }, [trackPerformance, session])

  // Initial load
  useEffect(() => {
    refresh()
  }, [])

  return {
    session,
    isLoading,
    error,
    refresh,
    updateTokenUsage,
    logMessage,
    calculateCost
  }
}

// Utility functions for session formatting
export const formatTokenUsage = (tokens: TokenUsage): string => {
  const percentage = Math.round(tokens.percentage)
  return `${tokens.total.toLocaleString()}/${tokens.limit.toLocaleString()} (${percentage}%)`
}

export const formatCost = (cost: number): string => {
  if (cost < 0.01) return '<$0.01'
  return `$${cost.toFixed(cost < 1 ? 3 : 2)}`
}

export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) return `${hours}h ${minutes}m`
  if (minutes > 0) return `${minutes}m ${secs}s`
  return `${secs}s`
}

export const getSessionQualityColor = (quality: string): string => {
  switch (quality) {
    case 'excellent': return '#10b981'
    case 'good': return '#3b82f6'
    case 'fair': return '#f59e0b'
    case 'poor': return '#ef4444'
    default: return '#6b7280'
  }
}

export const getTokenUsageLevel = (percentage: number): 'low' | 'medium' | 'high' | 'critical' => {
  if (percentage < 50) return 'low'
  if (percentage < 75) return 'medium'
  if (percentage < 90) return 'high'
  return 'critical'
}

export const estimateRemainingTime = (tokens: TokenUsage, throughput: number): number => {
  if (throughput <= 0) return 0
  return tokens.estimatedRemaining / throughput
}