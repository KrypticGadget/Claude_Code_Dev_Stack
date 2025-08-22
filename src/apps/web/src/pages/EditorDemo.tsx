import React, { useState, useCallback, useMemo } from 'react'
import { TabManager } from '../components/TabManager'
import { EditorFile } from '../types/TabTypes'
import '../styles/tab-manager.css'
import '../styles/tab-bar.css'
import '../styles/tab-item.css'
import '../styles/split-view.css'
import '../styles/tab-search-dialog.css'
import '../styles/tab-context-menu.css'
import '../styles/tab-preview.css'
import '../styles/tab-group-bar.css'
import '../styles/tab-scroll-controls.css'
import '../styles/tab-overflow-menu.css'
import '../styles/split-handle.css'
import '../styles/panel-drop-zone.css'

const DEMO_CODE_SAMPLES = {
  typescript: `// TypeScript Demo - Advanced React Component with Hooks
import React, { useState, useEffect, useCallback } from 'react'
import { debounce } from 'lodash'

interface User {
  id: number
  name: string
  email: string
  avatar?: string
}

interface SearchProps {
  onUserSelect: (user: User) => void
  placeholder?: string
}

const UserSearch: React.FC<SearchProps> = ({ 
  onUserSelect, 
  placeholder = "Search users..." 
}) => {
  const [query, setQuery] = useState<string>('')
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce(async (searchQuery: string) => {
      if (!searchQuery.trim()) {
        setUsers([])
        return
      }

      setLoading(true)
      setError(null)

      try {
        const response = await fetch(\`/api/users?q=\${encodeURIComponent(searchQuery)}\`)
        if (!response.ok) {
          throw new Error('Failed to fetch users')
        }
        
        const data: User[] = await response.json()
        setUsers(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setUsers([])
      } finally {
        setLoading(false)
      }
    }, 300),
    []
  )

  useEffect(() => {
    debouncedSearch(query)
    return () => debouncedSearch.cancel()
  }, [query, debouncedSearch])

  const handleUserClick = useCallback((user: User) => {
    onUserSelect(user)
    setQuery('')
    setUsers([])
  }, [onUserSelect])

  return (
    <div className="user-search">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="search-input"
      />
      
      {loading && <div className="loading">Searching...</div>}
      {error && <div className="error">{error}</div>}
      
      {users.length > 0 && (
        <div className="search-results">
          {users.map((user) => (
            <div
              key={user.id}
              className="user-item"
              onClick={() => handleUserClick(user)}
            >
              {user.avatar && (
                <img src={user.avatar} alt={user.name} className="avatar" />
              )}
              <div className="user-info">
                <div className="user-name">{user.name}</div>
                <div className="user-email">{user.email}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default UserSearch`,

  python: `# Python Demo - Advanced Data Processing with Type Hints
from typing import List, Dict, Optional, Callable, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class DataPoint:
    """Represents a single data point with timestamp and value."""
    timestamp: datetime
    value: float
    metadata: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class DataProcessor(Generic[T]):
    """Generic data processor with filtering and aggregation capabilities."""
    
    def __init__(self, data_source: str):
        self.data_source = data_source
        self.data_points: List[DataPoint] = []
        self.processors: List[Callable[[List[DataPoint]], List[DataPoint]]] = []
    
    async def load_data(self, start_date: datetime, end_date: datetime) -> None:
        """Load data from the specified date range."""
        logger.info(f"Loading data from {start_date} to {end_date}")
        
        try:
            # Simulate async data loading
            await asyncio.sleep(0.1)
            
            # Generate sample data
            current_date = start_date
            while current_date <= end_date:
                data_point = DataPoint(
                    timestamp=current_date,
                    value=hash(current_date.isoformat()) % 100,
                    metadata={"source": self.data_source}
                )
                self.data_points.append(data_point)
                current_date += timedelta(hours=1)
                
            logger.info(f"Loaded {len(self.data_points)} data points")
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def add_processor(self, processor: Callable[[List[DataPoint]], List[DataPoint]]) -> 'DataProcessor[T]':
        """Add a data processor function."""
        self.processors.append(processor)
        return self
    
    def filter_by_value(self, min_value: float, max_value: float) -> 'DataProcessor[T]':
        """Filter data points by value range."""
        def value_filter(points: List[DataPoint]) -> List[DataPoint]:
            return [p for p in points if min_value <= p.value <= max_value]
        
        return self.add_processor(value_filter)
    
    def process(self) -> List[DataPoint]:
        """Apply all processors to the data."""
        result = self.data_points.copy()
        
        for processor in self.processors:
            result = processor(result)
            logger.info(f"Processor applied, {len(result)} points remaining")
        
        return result

# Usage example
async def main():
    """Demonstrate the data processor."""
    processor = DataProcessor[DataPoint]("sensor_data")
    
    # Load data for the last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
    await processor.load_data(start_time, end_time)
    
    # Process data with filters
    result = (processor
              .filter_by_value(20, 80)
              .process())
    
    print(f"Processed {len(result)} data points")

if __name__ == "__main__":
    asyncio.run(main())`,

  go: `// Go Demo - Advanced Web Server with Middleware and Context
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "strconv"
    "time"
    
    "github.com/gorilla/mux"
    "github.com/rs/cors"
)

// User represents a user in the system
type User struct {
    ID        int       \`json:"id"\`
    Name      string    \`json:"name"\`
    Email     string    \`json:"email"\`
    CreatedAt time.Time \`json:"created_at"\`
    UpdatedAt time.Time \`json:"updated_at"\`
}

// UserService defines the interface for user operations
type UserService interface {
    GetUser(ctx context.Context, id int) (*User, error)
    GetUsers(ctx context.Context, limit, offset int) ([]*User, error)
    CreateUser(ctx context.Context, user *User) error
    UpdateUser(ctx context.Context, user *User) error
    DeleteUser(ctx context.Context, id int) error
}

// InMemoryUserService implements UserService using in-memory storage
type InMemoryUserService struct {
    users   map[int]*User
    nextID  int
}

// NewInMemoryUserService creates a new in-memory user service
func NewInMemoryUserService() *InMemoryUserService {
    return &InMemoryUserService{
        users:  make(map[int]*User),
        nextID: 1,
    }
}

func (s *InMemoryUserService) GetUser(ctx context.Context, id int) (*User, error) {
    user, exists := s.users[id]
    if !exists {
        return nil, fmt.Errorf("user with id %d not found", id)
    }
    return user, nil
}

func (s *InMemoryUserService) CreateUser(ctx context.Context, user *User) error {
    user.ID = s.nextID
    user.CreatedAt = time.Now()
    user.UpdatedAt = time.Now()
    s.users[user.ID] = user
    s.nextID++
    return nil
}

// UserHandler handles HTTP requests for user operations
type UserHandler struct {
    userService UserService
}

// NewUserHandler creates a new user handler
func NewUserHandler(userService UserService) *UserHandler {
    return &UserHandler{userService: userService}
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    idStr := vars["id"]
    
    id, err := strconv.Atoi(idStr)
    if err != nil {
        http.Error(w, "Invalid user ID", http.StatusBadRequest)
        return
    }
    
    user, err := h.userService.GetUser(r.Context(), id)
    if err != nil {
        http.Error(w, err.Error(), http.StatusNotFound)
        return
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

// Middleware for logging requests
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %s %v", r.Method, r.RequestURI, r.RemoteAddr, time.Since(start))
    })
}

func main() {
    // Initialize services
    userService := NewInMemoryUserService()
    userHandler := NewUserHandler(userService)
    
    // Create some sample users
    sampleUsers := []*User{
        {Name: "John Doe", Email: "john@example.com"},
        {Name: "Jane Smith", Email: "jane@example.com"},
    }
    
    for _, user := range sampleUsers {
        userService.CreateUser(context.Background(), user)
    }
    
    // Setup routes
    r := mux.NewRouter()
    
    // API routes
    api := r.PathPrefix("/api/v1").Subrouter()
    api.HandleFunc("/users/{id:[0-9]+}", userHandler.GetUser).Methods("GET")
    
    // Apply middleware
    r.Use(LoggingMiddleware)
    
    // Setup CORS
    c := cors.New(cors.Options{
        AllowedOrigins: []string{"*"},
        AllowedMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
        AllowedHeaders: []string{"*"},
    })
    
    handler := c.Handler(r)
    
    // Start server
    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", handler))
}`,

  rust: `// Rust Demo - Advanced Async Web Service with Error Handling
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde::{Deserialize, Serialize};
use tokio::sync::RwLock;
use warp::{Filter, Rejection, Reply};

// Custom error types
#[derive(Debug)]
pub enum ServiceError {
    NotFound(String),
    InvalidInput(String),
    InternalError(String),
}

impl warp::reject::Reject for ServiceError {}

// User model
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: u64,
    pub name: String,
    pub email: String,
    pub created_at: u64,
    pub updated_at: u64,
}

#[derive(Debug, Deserialize)]
pub struct CreateUserRequest {
    pub name: String,
    pub email: String,
}

// User repository trait
#[async_trait::async_trait]
pub trait UserRepository: Send + Sync {
    async fn create_user(&self, request: CreateUserRequest) -> Result<User, ServiceError>;
    async fn get_user(&self, id: u64) -> Result<User, ServiceError>;
    async fn get_users(&self, limit: usize, offset: usize) -> Result<Vec<User>, ServiceError>;
}

// In-memory implementation
pub struct InMemoryUserRepository {
    users: Arc<RwLock<HashMap<u64, User>>>,
    next_id: Arc<RwLock<u64>>,
}

impl InMemoryUserRepository {
    pub fn new() -> Self {
        Self {
            users: Arc::new(RwLock::new(HashMap::new())),
            next_id: Arc::new(RwLock::new(1)),
        }
    }
    
    fn current_timestamp() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
    }
}

#[async_trait::async_trait]
impl UserRepository for InMemoryUserRepository {
    async fn create_user(&self, request: CreateUserRequest) -> Result<User, ServiceError> {
        if request.name.trim().is_empty() {
            return Err(ServiceError::InvalidInput("Name cannot be empty".to_string()));
        }
        
        let mut next_id = self.next_id.write().await;
        let id = *next_id;
        *next_id += 1;
        
        let now = Self::current_timestamp();
        let user = User {
            id,
            name: request.name,
            email: request.email,
            created_at: now,
            updated_at: now,
        };
        
        let mut users = self.users.write().await;
        users.insert(id, user.clone());
        
        Ok(user)
    }
    
    async fn get_user(&self, id: u64) -> Result<User, ServiceError> {
        let users = self.users.read().await;
        users
            .get(&id)
            .cloned()
            .ok_or_else(|| ServiceError::NotFound(format!("User with id {} not found", id)))
    }
    
    async fn get_users(&self, limit: usize, offset: usize) -> Result<Vec<User>, ServiceError> {
        let users = self.users.read().await;
        let mut user_list: Vec<User> = users.values().cloned().collect();
        
        // Sort by ID for consistent pagination
        user_list.sort_by_key(|u| u.id);
        
        let result = user_list
            .into_iter()
            .skip(offset)
            .take(limit)
            .collect();
        
        Ok(result)
    }
}

#[tokio::main]
async fn main() {
    // Initialize repository
    let repository = Arc::new(InMemoryUserRepository::new());
    
    // Create some sample users
    let sample_users = vec![
        CreateUserRequest {
            name: "Alice Johnson".to_string(),
            email: "alice@example.com".to_string(),
        },
        CreateUserRequest {
            name: "Bob Smith".to_string(),
            email: "bob@example.com".to_string(),
        },
    ];
    
    for user_request in sample_users {
        if let Err(e) = repository.create_user(user_request).await {
            eprintln!("Failed to create sample user: {:?}", e);
        }
    }
    
    println!("Server starting on http://localhost:3030");
    warp::serve(warp::any())
        .run(([127, 0, 0, 1], 3030))
        .await;
}`
}

export const EditorDemo: React.FC = () => {
  const [enableTabPersistence, setEnableTabPersistence] = useState(true)
  const [enableKeyboardNav, setEnableKeyboardNav] = useState(true)
  const [enableDragDrop, setEnableDragDrop] = useState(true)
  const [enableSplitView, setEnableSplitView] = useState(true)
  const [enableTabGroups, setEnableTabGroups] = useState(true)

  // Create initial demo files
  const initialFiles = useMemo((): EditorFile[] => [
    {
      id: 'demo-ts',
      name: 'UserSearch.tsx',
      path: '/demo/components/UserSearch.tsx',
      content: DEMO_CODE_SAMPLES.typescript,
      language: 'typescript'
    },
    {
      id: 'demo-py',
      name: 'data_processor.py',
      path: '/demo/scripts/data_processor.py',
      content: DEMO_CODE_SAMPLES.python,
      language: 'python'
    },
    {
      id: 'demo-go',
      name: 'main.go',
      path: '/demo/server/main.go',
      content: DEMO_CODE_SAMPLES.go,
      language: 'go'
    },
    {
      id: 'demo-rs',
      name: 'service.rs',
      path: '/demo/src/service.rs',
      content: DEMO_CODE_SAMPLES.rust,
      language: 'rust'
    },
    {
      id: 'demo-readme',
      name: 'README.md',
      path: '/demo/README.md',
      content: `# Advanced Tab Management Demo

This demo showcases a sophisticated tab management system with:

## Core Features

### 🗂️ Tab Management
- **Multiple file editing** with syntax highlighting
- **Unsaved changes tracking** with visual indicators
- **Tab pinning** for important files
- **Tab grouping** with color coding
- **Quick tab search** with fuzzy matching

### 🪟 Split View Support
- **Drag tabs** to create split panels
- **Horizontal and vertical splits**
- **Resizable panels** with handles
- **Cross-panel tab dragging**

### ⌨️ Keyboard Navigation
- **Ctrl+Tab** - Next tab
- **Ctrl+Shift+Tab** - Previous tab
- **Ctrl+T** - New tab
- **Ctrl+W** - Close tab
- **Ctrl+P** - Quick open
- **Ctrl+1-9** - Go to tab by index

### 🎨 Advanced Features
- **Tab thumbnails** on hover
- **Session persistence** across browser sessions
- **Tab overflow** handling with scrolling
- **Context menus** with rich actions
- **Performance optimized** for many tabs

## Try It Out!

1. Open multiple files using the demo buttons
2. Drag tabs between panels to create splits
3. Right-click tabs for context menus
4. Use Ctrl+P to search and navigate quickly
5. Pin important tabs by double-clicking

Enjoy the enhanced editing experience! 🚀`,
      language: 'markdown'
    }
  ], [])

  const handleFileChange = useCallback((file: EditorFile) => {
    console.log('File changed:', file.name, 'Content length:', file.content?.length)
    // In a real app, this would save to a file or send to a server
  }, [])

  const handleTabClose = useCallback((tabId: string) => {
    console.log('Tab closed:', tabId)
    // Handle tab cleanup
  }, [])

  return (
    <div className="editor-demo">
      <div className="demo-header">
        <h1>Advanced Tab Management Demo</h1>
        <p>Sophisticated multi-file editor with tabs, split views, drag & drop, and advanced navigation.</p>
        
        <div className="demo-controls">
          <div className="control-group">
            <label>
              <input 
                type="checkbox" 
                checked={enableTabPersistence}
                onChange={(e) => setEnableTabPersistence(e.target.checked)}
              />
              Tab Persistence
            </label>
          </div>
          
          <div className="control-group">
            <label>
              <input 
                type="checkbox" 
                checked={enableKeyboardNav}
                onChange={(e) => setEnableKeyboardNav(e.target.checked)}
              />
              Keyboard Navigation
            </label>
          </div>
          
          <div className="control-group">
            <label>
              <input 
                type="checkbox" 
                checked={enableDragDrop}
                onChange={(e) => setEnableDragDrop(e.target.checked)}
              />
              Drag & Drop
            </label>
          </div>
          
          <div className="control-group">
            <label>
              <input 
                type="checkbox" 
                checked={enableSplitView}
                onChange={(e) => setEnableSplitView(e.target.checked)}
              />
              Split View
            </label>
          </div>
          
          <div className="control-group">
            <label>
              <input 
                type="checkbox" 
                checked={enableTabGroups}
                onChange={(e) => setEnableTabGroups(e.target.checked)}
              />
              Tab Groups
            </label>
          </div>
        </div>
      </div>

      <div className="demo-editor">
        <TabManager
          initialFiles={initialFiles}
          onFileChange={handleFileChange}
          onTabClose={handleTabClose}
          maxTabs={50}
          enablePersistence={enableTabPersistence}
          enableKeyboardNavigation={enableKeyboardNav}
          enableDragAndDrop={enableDragDrop}
          enableSplitView={enableSplitView}
          enableTabGroups={enableTabGroups}
        />
      </div>

      <div className="demo-features">
        <h2>Tab Management Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>🗂️ Multi-File Editing</h3>
            <p>Open multiple files simultaneously with syntax highlighting and IntelliSense support.</p>
          </div>
          
          <div className="feature-card">
            <h3>🪟 Split View</h3>
            <p>Drag tabs to create horizontal or vertical split panels for side-by-side editing.</p>
          </div>
          
          <div className="feature-card">
            <h3>📌 Tab Pinning</h3>
            <p>Pin important tabs to keep them always visible and prevent accidental closure.</p>
          </div>
          
          <div className="feature-card">
            <h3>🎨 Tab Groups</h3>
            <p>Organize related tabs into color-coded groups for better project management.</p>
          </div>
          
          <div className="feature-card">
            <h3>🔍 Quick Search</h3>
            <p>Instantly find and open files with fuzzy search and recent file suggestions.</p>
          </div>
          
          <div className="feature-card">
            <h3>⌨️ Keyboard Shortcuts</h3>
            <p>Navigate efficiently with keyboard shortcuts for all tab operations.</p>
          </div>
          
          <div className="feature-card">
            <h3>💾 Session Persistence</h3>
            <p>Restore your open tabs and workspace layout when you return to the editor.</p>
          </div>
          
          <div className="feature-card">
            <h3>🎯 Unsaved Changes</h3>
            <p>Visual indicators show which files have unsaved changes with confirmation dialogs.</p>
          </div>
          
          <div className="feature-card">
            <h3>🖱️ Drag & Drop</h3>
            <p>Intuitive drag and drop interface for reordering tabs and creating split views.</p>
          </div>
          
          <div className="feature-card">
            <h3>📱 Responsive Design</h3>
            <p>Optimized for both desktop and mobile devices with touch-friendly controls.</p>
          </div>
          
          <div className="feature-card">
            <h3>🚀 Performance</h3>
            <p>Efficient virtual scrolling and lazy loading for handling hundreds of tabs.</p>
          </div>
          
          <div className="feature-card">
            <h3>♿ Accessibility</h3>
            <p>Full keyboard navigation, screen reader support, and high contrast mode.</p>
          </div>
        </div>
      </div>

      <div className="demo-instructions">
        <h2>Try These Features</h2>
        <div className="instructions-grid">
          <div className="instruction-card">
            <h4>🖱️ Basic Operations</h4>
            <ul>
              <li>Click tabs to switch between files</li>
              <li>Right-click tabs for context menu</li>
              <li>Double-click tabs to pin/unpin</li>
              <li>Middle-click to close tabs</li>
            </ul>
          </div>
          
          <div className="instruction-card">
            <h4>⌨️ Keyboard Shortcuts</h4>
            <ul>
              <li><kbd>Ctrl+P</kbd> - Quick open/search</li>
              <li><kbd>Ctrl+Tab</kbd> - Next tab</li>
              <li><kbd>Ctrl+W</kbd> - Close tab</li>
              <li><kbd>Ctrl+1-9</kbd> - Go to tab by index</li>
            </ul>
          </div>
          
          <div className="instruction-card">
            <h4>🪟 Split Views</h4>
            <ul>
              <li>Drag tabs to panel edges to split</li>
              <li>Drag tabs between existing panels</li>
              <li>Use resize handles to adjust panel sizes</li>
              <li>Right-click tabs → "Move to New Panel"</li>
            </ul>
          </div>
          
          <div className="instruction-card">
            <h4>🎨 Tab Groups</h4>
            <ul>
              <li>Right-click tabs → "Create Group"</li>
              <li>Click group colors to change them</li>
              <li>Collapse groups to save space</li>
              <li>Drag tabs into existing groups</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EditorDemo