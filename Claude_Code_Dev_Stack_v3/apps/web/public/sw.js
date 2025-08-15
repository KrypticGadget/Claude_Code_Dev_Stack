// Claude Code Dev Stack v3.0 - Service Worker
// Progressive Web App functionality with advanced caching strategies

const CACHE_NAME = 'claude-code-dev-stack-v3-1.0.0'
const STATIC_CACHE = 'static-cache-v1'
const DYNAMIC_CACHE = 'dynamic-cache-v1'
const API_CACHE = 'api-cache-v1'

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/pwa-192x192.png',
  '/pwa-512x512.png',
  '/apple-touch-icon.png',
  '/favicon.ico'
]

// API endpoints to cache with NetworkFirst strategy
const API_ENDPOINTS = [
  '/api/',
  '/ws/'
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...')
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('📦 Caching static assets')
        return cache.addAll(STATIC_ASSETS)
      }),
      
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker activating...')
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && 
                cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== API_CACHE) {
              console.log('🗑️ Deleting old cache:', cacheName)
              return caches.delete(cacheName)
            }
          })
        )
      }),
      
      // Claim all clients
      self.clients.claim()
    ])
  )
})

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Handle different types of requests with appropriate strategies
  if (request.method === 'GET') {
    if (isStaticAsset(request)) {
      // Static assets: Cache First
      event.respondWith(cacheFirst(request, STATIC_CACHE))
    } else if (isAPIRequest(request)) {
      // API requests: Network First with fallback
      event.respondWith(networkFirst(request, API_CACHE))
    } else if (isNavigationRequest(request)) {
      // Navigation requests: Network First with offline fallback
      event.respondWith(handleNavigation(request))
    } else {
      // Other requests: Stale While Revalidate
      event.respondWith(staleWhileRevalidate(request, DYNAMIC_CACHE))
    }
  }
})

// Cache First Strategy - for static assets
async function cacheFirst(request, cacheName) {
  try {
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    console.error('Cache First failed:', error)
    return new Response('Offline', { status: 503 })
  }
}

// Network First Strategy - for API requests
async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    console.log('Network failed, trying cache:', error)
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline response for API requests
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'Network unavailable',
        cached: false 
      }), 
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}

// Stale While Revalidate Strategy - for dynamic content
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName)
  const cachedResponse = await cache.match(request)
  
  // Fetch from network in background
  const networkResponsePromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  }).catch(() => null)
  
  // Return cached response immediately, or wait for network
  return cachedResponse || await networkResponsePromise || new Response('Offline', { status: 503 })
}

// Handle navigation requests with offline fallback
async function handleNavigation(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE)
      cache.put(request, networkResponse.clone())
      return networkResponse
    }
  } catch (error) {
    console.log('Navigation network failed, trying cache')
  }
  
  // Try cache
  const cachedResponse = await caches.match(request)
  if (cachedResponse) {
    return cachedResponse
  }
  
  // Fallback to cached root page
  const rootResponse = await caches.match('/')
  if (rootResponse) {
    return rootResponse
  }
  
  // Ultimate fallback - offline page
  return new Response(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Claude Code Dev Stack - Offline</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #1a1b26;
          color: #c0caf5;
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100vh;
          margin: 0;
          text-align: center;
        }
        .offline-content {
          max-width: 400px;
          padding: 2rem;
        }
        .offline-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }
        h1 {
          margin-bottom: 1rem;
          color: #7aa2f7;
        }
        button {
          background: #7aa2f7;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 0.5rem;
          cursor: pointer;
          margin-top: 1rem;
        }
        button:hover {
          background: #bb9af7;
        }
      </style>
    </head>
    <body>
      <div class="offline-content">
        <div class="offline-icon">📴</div>
        <h1>You're Offline</h1>
        <p>Claude Code Dev Stack is currently unavailable. Please check your internet connection and try again.</p>
        <button onclick="window.location.reload()">Try Again</button>
      </div>
    </body>
    </html>
  `, {
    headers: { 'Content-Type': 'text/html' }
  })
}

// Helper functions
function isStaticAsset(request) {
  const url = new URL(request.url)
  return url.pathname.match(/\.(js|css|png|jpg|jpeg|svg|ico|woff2|woff|ttf)$/)
}

function isAPIRequest(request) {
  const url = new URL(request.url)
  return API_ENDPOINTS.some(endpoint => url.pathname.startsWith(endpoint))
}

function isNavigationRequest(request) {
  return request.mode === 'navigate'
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('📬 Push notification received')
  
  const options = {
    body: 'You have new updates in Claude Code Dev Stack',
    icon: '/pwa-192x192.png',
    badge: '/pwa-192x192.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/'
    },
    actions: [
      {
        action: 'open',
        title: 'Open App',
        icon: '/pwa-192x192.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/pwa-192x192.png'
      }
    ]
  }
  
  if (event.data) {
    try {
      const data = event.data.json()
      options.body = data.body || options.body
      options.data = { ...options.data, ...data }
    } catch (error) {
      console.error('Failed to parse push data:', error)
    }
  }
  
  event.waitUntil(
    self.registration.showNotification('Claude Code Dev Stack', options)
  )
})

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Notification clicked')
  event.notification.close()
  
  const action = event.action
  const url = event.notification.data?.url || '/'
  
  if (action === 'close') {
    return
  }
  
  event.waitUntil(
    clients.matchAll().then((clientList) => {
      // If app is already open, focus it
      for (const client of clientList) {
        if (client.url === url && 'focus' in client) {
          return client.focus()
        }
      }
      
      // Otherwise open new window
      if (clients.openWindow) {
        return clients.openWindow(url)
      }
    })
  )
})

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync triggered:', event.tag)
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync())
  }
})

async function doBackgroundSync() {
  try {
    // Sync offline actions when connection is restored
    console.log('Syncing offline actions...')
    
    // Example: sync offline form submissions, queued API calls, etc.
    const cache = await caches.open('offline-actions')
    const requests = await cache.keys()
    
    for (const request of requests) {
      try {
        await fetch(request)
        await cache.delete(request)
        console.log('Synced offline action:', request.url)
      } catch (error) {
        console.error('Failed to sync action:', error)
      }
    }
  } catch (error) {
    console.error('Background sync failed:', error)
  }
}

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
  console.log('⏰ Periodic sync triggered:', event.tag)
  
  if (event.tag === 'update-data') {
    event.waitUntil(updateAppData())
  }
})

async function updateAppData() {
  try {
    console.log('Updating app data in background...')
    
    // Example: fetch latest data, update caches, etc.
    const response = await fetch('/api/update')
    if (response.ok) {
      const cache = await caches.open(API_CACHE)
      cache.put('/api/update', response.clone())
    }
  } catch (error) {
    console.error('Periodic sync failed:', error)
  }
}

// Share target handling
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)
  
  if (url.pathname === '/share' && event.request.method === 'POST') {
    event.respondWith(handleSharedContent(event.request))
  }
})

async function handleSharedContent(request) {
  try {
    const formData = await request.formData()
    const title = formData.get('title')
    const text = formData.get('text')
    const url = formData.get('url')
    
    console.log('Shared content received:', { title, text, url })
    
    // Store shared content for the app to handle
    const cache = await caches.open('shared-content')
    const response = new Response(JSON.stringify({ title, text, url }), {
      headers: { 'Content-Type': 'application/json' }
    })
    await cache.put('/shared-content', response)
    
    // Redirect to main app
    return Response.redirect('/', 303)
  } catch (error) {
    console.error('Failed to handle shared content:', error)
    return new Response('Error', { status: 500 })
  }
}

console.log('🚀 Claude Code Dev Stack Service Worker loaded successfully')