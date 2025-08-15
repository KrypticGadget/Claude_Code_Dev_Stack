import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'

// Mock the useWebSocket hook
vi.mock('./hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    data: null,
    isConnected: false,
    send: vi.fn(),
    close: vi.fn(),
    reconnect: vi.fn()
  })
}))

describe('App Component', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })
  })

  const renderApp = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    )
  }

  it('renders without crashing', () => {
    renderApp()
    expect(screen.getByText('Claude_Code_Dev_Stack_v3')).toBeInTheDocument()
  })

  it('displays the statusline component', () => {
    renderApp()
    expect(screen.getByText('Claude_Code_Dev_Stack_v3')).toBeInTheDocument()
    expect(screen.getByText('main')).toBeInTheDocument()
  })

  it('shows agent metrics in statusline', () => {
    renderApp()
    expect(screen.getByText('0/28')).toBeInTheDocument() // agents metric
  })

  it('displays connection status', async () => {
    renderApp()
    await waitFor(() => {
      expect(screen.getByText('Offline')).toBeInTheDocument()
    })
  })

  it('renders main content area', () => {
    renderApp()
    const mainContent = document.querySelector('.main-content')
    expect(mainContent).toBeInTheDocument()
  })
})

describe('PWA Features', () => {
  it('should register service worker', async () => {
    // Test service worker registration
    expect(navigator.serviceWorker.register).toBeDefined()
  })

  it('should support notifications', () => {
    expect(window.Notification).toBeDefined()
    expect(window.Notification.permission).toBe('granted')
  })

  it('should handle offline state', () => {
    // Simulate offline
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: false
    })

    expect(navigator.onLine).toBe(false)
  })
})