import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { registerSW } from 'virtual:pwa-register'
import './index.css'

// Claude Code Dev Stack v3.0 - PWA Bootstrap
// Service Worker Registration with Auto-Update

// Register service worker for PWA functionality
const updateSW = registerSW({
  onNeedRefresh() {
    console.log('🔄 New content available, refreshing...')
    // Auto-refresh for seamless updates
    updateSW(true)
  },
  onOfflineReady() {
    console.log('✅ App ready to work offline')
    // Show offline ready notification
    showOfflineNotification()
  },
  onRegistered(r) {
    console.log('✅ Service Worker registered:', r)
  },
  onRegisterError(error) {
    console.error('❌ Service Worker registration error:', error)
  }
})

// Offline notification
function showOfflineNotification() {
  const notification = document.createElement('div')
  notification.innerHTML = `
    <div style="position: fixed; bottom: 20px; left: 20px; background: #10b981; color: white; padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1002; font-size: 14px;">
      ✅ App is ready to work offline!
    </div>
  `
  document.body.appendChild(notification)
  
  // Auto-remove after 3 seconds
  setTimeout(() => {
    notification.remove()
  }, 3000)
}

// Network status monitoring
window.addEventListener('online', () => {
  console.log('🌐 Back online')
  showNetworkStatus('online')
})

window.addEventListener('offline', () => {
  console.log('📴 Gone offline')
  showNetworkStatus('offline')
})

function showNetworkStatus(status: 'online' | 'offline') {
  const notification = document.createElement('div')
  const isOnline = status === 'online'
  
  notification.innerHTML = `
    <div style="position: fixed; top: 20px; left: 20px; background: ${isOnline ? '#10b981' : '#ef4444'}; color: white; padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1002; font-size: 14px;">
      ${isOnline ? '🌐 Back online' : '📴 You are offline'}
    </div>
  `
  document.body.appendChild(notification)
  
  // Auto-remove after 2 seconds
  setTimeout(() => {
    notification.remove()
  }, 2000)
}

// Performance monitoring
if ('performance' in window) {
  window.addEventListener('load', () => {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    console.log('📊 Page Load Performance:', {
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
      firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime,
      firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime
    })
  })
}

// Error boundary for PWA
class PWAErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('PWA Error Boundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          padding: '20px',
          textAlign: 'center',
          backgroundColor: '#1a1b26',
          color: 'white'
        }}>
          <h1 style={{ marginBottom: '20px' }}>Something went wrong</h1>
          <p style={{ marginBottom: '20px', opacity: 0.7 }}>
            The application encountered an error. Please try refreshing the page.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: '#007acc',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Refresh App
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// Render application with error boundary
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <PWAErrorBoundary>
      <App />
    </PWAErrorBoundary>
  </React.StrictMode>
)