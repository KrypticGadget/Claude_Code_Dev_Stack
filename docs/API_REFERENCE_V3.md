# Claude Code Dev Stack v3.0 - Complete API Reference

**Comprehensive API Documentation for All Components**

---

## 📋 Table of Contents

1. [Core API Overview](#core-api-overview)
2. [Agent Management API](#agent-management-api)
3. [Hook Automation API](#hook-automation-api)
4. [Command Execution API](#command-execution-api)
5. [MCP Integration API](#mcp-integration-api)
6. [Status & Monitoring API](#status--monitoring-api)
7. [Audio System API](#audio-system-api)
8. [Mobile Control API](#mobile-control-api)
9. [Real-time WebSocket API](#real-time-websocket-api)
10. [Authentication & Security](#authentication--security)
11. [SDK Examples](#sdk-examples)

---

## Core API Overview

### Base Configuration
```yaml
Base URL: http://localhost:8080/api/v3
Protocol: HTTP/HTTPS + WebSocket
Authentication: JWT Bearer Token
Rate Limiting: 1000 requests/minute per token
Content-Type: application/json
```

### Standard Response Format
```json
{
  "success": true,
  "data": {},
  "meta": {
    "timestamp": "2025-01-16T10:30:00Z",
    "version": "3.0.0",
    "request_id": "uuid"
  },
  "error": null
}
```

### Error Response Format
```json
{
  "success": false,
  "data": null,
  "meta": {
    "timestamp": "2025-01-16T10:30:00Z",
    "version": "3.0.0",
    "request_id": "uuid"
  },
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent '@agent-nonexistent' not found",
    "details": {
      "available_agents": ["@agent-master-orchestrator", "..."]
    }
  }
}
```

---

## Agent Management API

### List All Agents
```http
GET /api/v3/agents
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_agents": 28,
    "agents": [
      {
        "name": "@agent-master-orchestrator",
        "tier": 1,
        "category": "orchestration",
        "status": "active",
        "capabilities": [
          "project_coordination",
          "agent_routing",
          "lifecycle_management"
        ],
        "current_tasks": 2,
        "success_rate": 98.5,
        "average_response_time": 1200,
        "last_activity": "2025-01-16T10:29:45Z"
      }
    ]
  }
}
```

### Get Specific Agent Details
```http
GET /api/v3/agents/{agent_name}
```

**Example:**
```http
GET /api/v3/agents/@agent-backend-services
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "@agent-backend-services",
    "tier": 4,
    "category": "development",
    "description": "Backend API and service development specialist",
    "status": "idle",
    "capabilities": [
      "api_development",
      "business_logic",
      "service_architecture",
      "database_operations"
    ],
    "dependencies": [
      "@agent-database-architecture",
      "@agent-technical-specifications"
    ],
    "performance_metrics": {
      "total_executions": 1247,
      "success_rate": 96.2,
      "average_duration": 180000,
      "error_count": 47
    },
    "current_workload": {
      "active_tasks": 0,
      "queued_tasks": 3,
      "estimated_availability": "2025-01-16T10:45:00Z"
    }
  }
}
```

### Execute Agent Task
```http
POST /api/v3/agents/{agent_name}/execute
```

**Request Body:**
```json
{
  "task": "Create REST API for user management",
  "context": {
    "project_id": "proj_123",
    "technology_stack": "Node.js, Express, MongoDB",
    "requirements": [
      "CRUD operations",
      "JWT authentication", 
      "Input validation"
    ]
  },
  "priority": "high",
  "timeout": 300,
  "parallel_execution": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_456",
    "agent": "@agent-backend-services",
    "status": "queued",
    "estimated_start": "2025-01-16T10:31:00Z",
    "estimated_completion": "2025-01-16T10:36:00Z",
    "queue_position": 1
  }
}
```

### Get Agent Execution Status
```http
GET /api/v3/agents/executions/{execution_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_456",
    "agent": "@agent-backend-services",
    "status": "running",
    "progress": 65,
    "current_step": "Implementing authentication middleware",
    "steps_completed": 13,
    "steps_total": 20,
    "started_at": "2025-01-16T10:31:00Z",
    "estimated_completion": "2025-01-16T10:35:30Z",
    "output": {
      "files_created": ["src/middleware/auth.js", "src/routes/users.js"],
      "tests_generated": 8,
      "documentation_updated": true
    }
  }
}
```

### Agent Collaboration
```http
POST /api/v3/agents/collaborate
```

**Request Body:**
```json
{
  "primary_agent": "@agent-master-orchestrator",
  "task": "Build full-stack e-commerce platform",
  "context": {
    "project_type": "e-commerce",
    "scale": "medium",
    "timeline": "4 weeks"
  },
  "collaboration_mode": "sequential",
  "max_parallel_agents": 5
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "collaboration_id": "collab_789",
    "execution_plan": {
      "phase_1": {
        "agents": ["@agent-business-analyst", "@agent-technical-cto"],
        "estimated_duration": 3600,
        "dependencies": []
      },
      "phase_2": {
        "agents": ["@agent-frontend-architecture", "@agent-database-architecture"],
        "estimated_duration": 7200,
        "dependencies": ["phase_1"]
      }
    },
    "total_estimated_duration": 43200,
    "status": "initialized"
  }
}
```

---

## Hook Automation API

### List All Hooks
```http
GET /api/v3/hooks
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_hooks": 28,
    "hooks": [
      {
        "name": "session_loader.py",
        "category": "session_management",
        "trigger_events": ["SessionStart"],
        "status": "active",
        "execution_count": 1247,
        "last_execution": "2025-01-16T09:00:00Z",
        "average_execution_time": 45,
        "success_rate": 99.8
      },
      {
        "name": "agent_orchestrator.py", 
        "category": "agent_orchestration",
        "trigger_events": ["AgentMention", "TaskStart"],
        "status": "active",
        "execution_count": 5892,
        "last_execution": "2025-01-16T10:29:30Z",
        "average_execution_time": 120,
        "success_rate": 97.3
      }
    ]
  }
}
```

### Get Hook Details
```http
GET /api/v3/hooks/{hook_name}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "audio_player.py",
    "category": "integration",
    "description": "Context-aware audio notification system",
    "trigger_events": [
      "PreToolUse",
      "PostToolUse", 
      "SessionStart",
      "Stop"
    ],
    "configuration": {
      "timeout": 1,
      "enabled": true,
      "priority": "low",
      "retry_count": 3
    },
    "performance": {
      "total_executions": 3421,
      "success_rate": 98.9,
      "average_duration": 287,
      "last_24h_executions": 145
    },
    "dependencies": [
      "audio_config.json",
      "~/.claude/audio/*.mp3"
    ]
  }
}
```

### Trigger Hook Manually
```http
POST /api/v3/hooks/{hook_name}/trigger
```

**Request Body:**
```json
{
  "event_data": {
    "hook_event_name": "SessionStart",
    "context": {
      "user_id": "user_123",
      "session_id": "session_456"
    }
  },
  "force_execution": false,
  "timeout_override": 5
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "hook_exec_789",
    "hook": "session_loader.py",
    "status": "completed",
    "duration": 423,
    "output": "Session restored successfully",
    "triggered_at": "2025-01-16T10:30:00Z"
  }
}
```

### Hook Chain Execution
```http
POST /api/v3/hooks/chain
```

**Request Body:**
```json
{
  "event": "TaskCompletion",
  "context": {
    "task_id": "task_123",
    "agent": "@agent-backend-services",
    "success": true
  },
  "dry_run": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "chain_id": "chain_456",
    "triggered_hooks": [
      {
        "hook": "post_command.py",
        "order": 1,
        "status": "completed",
        "duration": 156
      },
      {
        "hook": "audio_player.py", 
        "order": 2,
        "status": "completed",
        "duration": 287
      },
      {
        "hook": "github_integrator.py",
        "order": 3,
        "status": "running",
        "estimated_completion": "2025-01-16T10:30:45Z"
      }
    ],
    "total_estimated_duration": 2340
  }
}
```

---

## Command Execution API

### List All Commands
```http
GET /api/v3/commands
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_commands": 18,
    "commands": [
      {
        "name": "/new-project",
        "category": "project_management",
        "description": "Start comprehensive project with full orchestration",
        "parameters": [
          {
            "name": "description",
            "type": "string",
            "required": true,
            "description": "Project description"
          }
        ],
        "usage_count": 847,
        "success_rate": 96.8,
        "average_duration": 12000
      }
    ]
  }
}
```

### Execute Command
```http
POST /api/v3/commands/execute
```

**Request Body:**
```json
{
  "command": "/new-project",
  "parameters": {
    "description": "E-commerce platform with mobile app",
    "technology": "React, Node.js, MongoDB",
    "timeline": "6 weeks"
  },
  "context": {
    "user_id": "user_123",
    "workspace": "/path/to/workspace"
  },
  "async": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "cmd_exec_123",
    "command": "/new-project",
    "status": "initiated",
    "agents_involved": [
      "@agent-master-orchestrator",
      "@agent-business-analyst", 
      "@agent-technical-cto"
    ],
    "estimated_duration": 14400,
    "started_at": "2025-01-16T10:30:00Z"
  }
}
```

### Get Command Execution Status
```http
GET /api/v3/commands/executions/{execution_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "cmd_exec_123",
    "command": "/new-project",
    "status": "running",
    "progress": {
      "current_phase": "business_analysis",
      "completed_phases": ["initialization"],
      "total_phases": 8,
      "percentage": 25
    },
    "active_agents": [
      {
        "agent": "@agent-business-analyst",
        "status": "running",
        "current_task": "Market opportunity analysis"
      }
    ],
    "results": {
      "project_id": "proj_456",
      "workspace_created": true,
      "initial_structure": {
        "files_created": 15,
        "directories_created": 8
      }
    }
  }
}
```

### Command History
```http
GET /api/v3/commands/history
```

**Query Parameters:**
- `limit`: Number of records (default: 50)
- `offset`: Pagination offset (default: 0)
- `user_id`: Filter by user ID
- `status`: Filter by status (completed, running, failed)
- `command`: Filter by command name

**Response:**
```json
{
  "success": true,
  "data": {
    "total_count": 1247,
    "executions": [
      {
        "execution_id": "cmd_exec_123",
        "command": "/new-project",
        "status": "completed",
        "duration": 13847,
        "started_at": "2025-01-16T09:45:00Z",
        "completed_at": "2025-01-16T10:15:47Z",
        "user_id": "user_123",
        "success": true
      }
    ],
    "pagination": {
      "limit": 50,
      "offset": 0,
      "has_more": true
    }
  }
}
```

---

## MCP Integration API

### List MCP Servers
```http
GET /api/v3/mcp/servers
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_servers": 3,
    "servers": [
      {
        "name": "playwright",
        "status": "connected",
        "version": "0.0.32",
        "capabilities": [
          "browser_automation",
          "web_scraping",
          "visual_testing"
        ],
        "connection": {
          "protocol": "stdio",
          "last_ping": "2025-01-16T10:29:55Z",
          "uptime": 3600,
          "error_count": 2
        },
        "usage_stats": {
          "tools_called": 1847,
          "success_rate": 98.2,
          "average_response_time": 2340
        }
      },
      {
        "name": "obsidian",
        "status": "connected", 
        "version": "latest",
        "capabilities": [
          "note_management",
          "vault_operations", 
          "search"
        ],
        "connection": {
          "protocol": "stdio",
          "last_ping": "2025-01-16T10:29:58Z",
          "uptime": 3598,
          "error_count": 0
        },
        "configuration": {
          "api_key": "***hidden***",
          "host": "127.0.0.1",
          "port": 27124
        }
      }
    ]
  }
}
```

### Execute MCP Tool
```http
POST /api/v3/mcp/{server_name}/tools/{tool_name}
```

**Example - Playwright Navigation:**
```http
POST /api/v3/mcp/playwright/tools/navigate
```

**Request Body:**
```json
{
  "parameters": {
    "url": "https://example.com",
    "wait_for": "load",
    "timeout": 30000
  },
  "context": {
    "session_id": "browser_session_123"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "mcp_exec_789",
    "server": "playwright",
    "tool": "navigate",
    "status": "completed",
    "duration": 2847,
    "result": {
      "url": "https://example.com",
      "title": "Example Domain",
      "status_code": 200,
      "screenshot_available": true
    }
  }
}
```

### MCP Server Health Check
```http
GET /api/v3/mcp/{server_name}/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "server": "playwright",
    "status": "healthy",
    "checks": {
      "connection": "pass",
      "response_time": "pass",
      "tool_availability": "pass",
      "resource_usage": "warning"
    },
    "metrics": {
      "response_time": 1200,
      "memory_usage": "256MB",
      "cpu_usage": "15%",
      "active_sessions": 3
    },
    "last_check": "2025-01-16T10:30:00Z"
  }
}
```

### List Available MCP Tools
```http
GET /api/v3/mcp/{server_name}/tools
```

**Response:**
```json
{
  "success": true,
  "data": {
    "server": "obsidian",
    "tools": [
      {
        "name": "list_files_in_vault",
        "description": "List all files in vault root",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      },
      {
        "name": "search",
        "description": "Search across all files",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "Search query"
            }
          },
          "required": ["query"]
        }
      }
    ]
  }
}
```

---

## Status & Monitoring API

### Current System Status
```http
GET /api/v3/status/current
```

**Response:**
```json
{
  "success": true,
  "data": {
    "system": {
      "version": "3.0.0",
      "uptime": 7200,
      "status": "optimal",
      "last_restart": "2025-01-16T08:30:00Z"
    },
    "agents": {
      "total": 28,
      "active": 5,
      "idle": 23,
      "error": 0,
      "utilization": 17.9
    },
    "hooks": {
      "total": 28,
      "active": 8,
      "triggered_last_hour": 247,
      "success_rate": 98.7
    },
    "commands": {
      "executed_today": 45,
      "success_rate": 96.2,
      "average_duration": 8400
    },
    "mcps": {
      "total": 3,
      "connected": 3,
      "health": "good"
    },
    "performance": {
      "cpu_usage": 45.2,
      "memory_usage": 2048,
      "response_time": 187,
      "error_rate": 1.3
    }
  }
}
```

### Detailed Component Status
```http
GET /api/v3/status/components
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status_line": {
      "status": "active",
      "update_frequency": 100,
      "last_update": "2025-01-16T10:29:58Z",
      "subscribers": 12,
      "data_points": 1847
    },
    "orchestrator": {
      "status": "active",
      "parallel_executions": 3,
      "queue_depth": 8,
      "resource_usage": {
        "cpu": 23.4,
        "memory": 512
      }
    },
    "audio_system": {
      "status": "active",
      "sounds_played_today": 89,
      "last_sound": "task_complete.mp3",
      "enabled": true
    },
    "mobile_interface": {
      "status": "active",
      "connected_devices": 2,
      "port": 8080,
      "tunnel_active": true
    }
  }
}
```

### Performance Metrics
```http
GET /api/v3/status/metrics
```

**Query Parameters:**
- `timeframe`: "1h", "24h", "7d", "30d" (default: "1h")
- `component`: Filter by component name
- `metric_type`: "performance", "usage", "errors"

**Response:**
```json
{
  "success": true,
  "data": {
    "timeframe": "1h",
    "metrics": {
      "response_times": {
        "agent_executions": [
          {"timestamp": "2025-01-16T10:00:00Z", "value": 1200},
          {"timestamp": "2025-01-16T10:15:00Z", "value": 1450}
        ],
        "command_executions": [
          {"timestamp": "2025-01-16T10:00:00Z", "value": 8400},
          {"timestamp": "2025-01-16T10:15:00Z", "value": 7200}
        ]
      },
      "resource_usage": {
        "cpu": [
          {"timestamp": "2025-01-16T10:00:00Z", "value": 42.3},
          {"timestamp": "2025-01-16T10:15:00Z", "value": 45.2}
        ],
        "memory": [
          {"timestamp": "2025-01-16T10:00:00Z", "value": 1956},
          {"timestamp": "2025-01-16T10:15:00Z", "value": 2048}
        ]
      },
      "success_rates": {
        "agents": 96.8,
        "hooks": 98.7,
        "commands": 96.2,
        "mcps": 98.9
      }
    }
  }
}
```

---

## Audio System API

### Audio Configuration
```http
GET /api/v3/audio/config
```

**Response:**
```json
{
  "success": true,
  "data": {
    "enabled": true,
    "version": "3.0",
    "audio_mappings": {
      "task_complete": "task_complete.mp3",
      "build_complete": "build_complete.mp3", 
      "error_fixed": "error_fixed.mp3",
      "ready": "ready.mp3",
      "awaiting_instructions": "awaiting_instructions.mp3"
    },
    "model_specific_sounds": {
      "claude-3-opus": {
        "activation": "complex_chord.wav",
        "completion": "sophisticated_chime.wav"
      },
      "claude-3-haiku": {
        "activation": "simple_beep.wav",
        "completion": "quick_ding.wav"
      }
    },
    "platform_support": {
      "windows": "powershell_soundplayer",
      "macos": "afplay",
      "linux": "aplay"
    }
  }
}
```

### Play Audio
```http
POST /api/v3/audio/play
```

**Request Body:**
```json
{
  "event": "task_complete",
  "context": {
    "agent": "@agent-backend-services",
    "task": "API implementation completed",
    "model": "claude-3-opus"
  },
  "override_sound": null,
  "volume": 0.8
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "played": true,
    "sound_file": "sophisticated_chime.wav",
    "duration": 2.5,
    "volume": 0.8,
    "platform": "windows",
    "played_at": "2025-01-16T10:30:00Z"
  }
}
```

### Audio History
```http
GET /api/v3/audio/history
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_sounds_played": 3421,
    "recent_sounds": [
      {
        "timestamp": "2025-01-16T10:29:45Z",
        "event": "task_complete",
        "sound_file": "sophisticated_chime.wav",
        "context": {
          "agent": "@agent-backend-services"
        }
      }
    ],
    "statistics": {
      "sounds_today": 89,
      "most_played": "ready.mp3",
      "success_rate": 98.9
    }
  }
}
```

### Update Audio Configuration
```http
PUT /api/v3/audio/config
```

**Request Body:**
```json
{
  "enabled": true,
  "volume": 0.7,
  "audio_mappings": {
    "custom_event": "custom_sound.mp3"
  },
  "model_preferences": {
    "claude-3-opus": "sophisticated"
  }
}
```

---

## Mobile Control API

### Mobile Device Registration
```http
POST /api/v3/mobile/register
```

**Request Body:**
```json
{
  "device_info": {
    "device_id": "mobile_123",
    "platform": "ios",
    "app_version": "3.0.0",
    "device_name": "iPhone 15 Pro"
  },
  "user_id": "user_123",
  "capabilities": [
    "notifications",
    "remote_control",
    "status_viewing"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "device_token": "jwt_token_here",
    "tunnel_endpoint": "wss://localhost:8080/mobile/tunnel",
    "session_id": "mobile_session_456",
    "expires_at": "2025-01-17T10:30:00Z"
  }
}
```

### Send Command from Mobile
```http
POST /api/v3/mobile/command
```

**Request Body:**
```json
{
  "device_token": "jwt_token_here",
  "command": {
    "type": "execute_slash_command",
    "command": "/new-project",
    "parameters": {
      "description": "Mobile-initiated project"
    }
  },
  "priority": "normal"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "command_id": "mobile_cmd_789",
    "status": "queued",
    "queue_position": 2,
    "estimated_execution": "2025-01-16T10:31:30Z"
  }
}
```

### Get Mobile Command Status
```http
GET /api/v3/mobile/commands/{command_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "command_id": "mobile_cmd_789",
    "status": "completed",
    "execution_time": 8400,
    "result": {
      "success": true,
      "project_created": "proj_789",
      "files_created": 15
    },
    "completed_at": "2025-01-16T10:35:00Z"
  }
}
```

### Mobile Sync Status
```http
GET /api/v3/mobile/sync
```

**Response:**
```json
{
  "success": true,
  "data": {
    "connected_devices": [
      {
        "device_id": "mobile_123",
        "platform": "ios",
        "last_seen": "2025-01-16T10:29:58Z",
        "status": "connected",
        "latency": 45
      }
    ],
    "sync_statistics": {
      "commands_sent": 247,
      "status_updates": 1847,
      "average_latency": 52
    }
  }
}
```

---

## Real-time WebSocket API

### WebSocket Connection
```javascript
// Connect to real-time status updates
const ws = new WebSocket('ws://localhost:8080/api/v3/status/stream');

// Authentication (send immediately after connection)
ws.send(JSON.stringify({
  type: 'auth',
  token: 'jwt_token_here'
}));
```

### Status Update Events
```javascript
// Receive real-time status updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'status_update':
      handleStatusUpdate(data);
      break;
    case 'agent_activity':
      handleAgentActivity(data);
      break;
    case 'command_progress':
      handleCommandProgress(data);
      break;
  }
};
```

### Event Types

#### Status Update Event
```json
{
  "type": "status_update",
  "timestamp": "2025-01-16T10:30:00Z",
  "data": {
    "agents": {
      "active": 5,
      "total": 28
    },
    "system": {
      "cpu": 45.2,
      "memory": 2048
    }
  }
}
```

#### Agent Activity Event
```json
{
  "type": "agent_activity",
  "timestamp": "2025-01-16T10:30:00Z",
  "data": {
    "agent": "@agent-backend-services",
    "action": "started",
    "task": "API implementation",
    "estimated_duration": 300
  }
}
```

#### Command Progress Event
```json
{
  "type": "command_progress",
  "timestamp": "2025-01-16T10:30:00Z",
  "data": {
    "execution_id": "cmd_exec_123",
    "command": "/new-project",
    "progress": 65,
    "current_step": "Database design phase"
  }
}
```

#### Hook Execution Event
```json
{
  "type": "hook_execution",
  "timestamp": "2025-01-16T10:30:00Z",
  "data": {
    "hook": "audio_player.py",
    "event": "task_complete",
    "status": "completed",
    "duration": 287
  }
}
```

### WebSocket Subscription Management
```javascript
// Subscribe to specific events
ws.send(JSON.stringify({
  type: 'subscribe',
  events: ['agent_activity', 'command_progress'],
  filters: {
    agent: '@agent-backend-services'
  }
}));

// Unsubscribe from events
ws.send(JSON.stringify({
  type: 'unsubscribe',
  events: ['status_update']
}));
```

---

## Authentication & Security

### JWT Token Authentication
```http
POST /api/v3/auth/token
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "device_info": {
    "platform": "web",
    "user_agent": "Mozilla/5.0..."
  },
  "scope": ["agents", "commands", "status"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token_here",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "refresh_token_here",
    "scope": ["agents", "commands", "status"]
  }
}
```

### Rate Limiting
- **Standard Endpoints**: 1000 requests/minute per token
- **Real-time WebSocket**: No limit (connection-based)
- **Heavy Operations**: 100 requests/minute per token
- **Mobile Endpoints**: 500 requests/minute per device

### Security Headers
All API responses include:
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

---

## SDK Examples

### Python SDK Example
```python
import asyncio
from claude_code_sdk import ClaudeCodeClient

# Initialize client
client = ClaudeCodeClient(
    base_url="http://localhost:8080/api/v3",
    auth_token="your_jwt_token"
)

# Execute agent task
async def execute_backend_task():
    result = await client.agents.execute(
        agent="@agent-backend-services",
        task="Create user management API",
        context={
            "technology": "Node.js",
            "database": "MongoDB"
        }
    )
    
    # Monitor execution
    while result.status != "completed":
        await asyncio.sleep(5)
        result = await client.agents.get_execution(result.execution_id)
        print(f"Progress: {result.progress}%")
    
    return result

# Run the task
result = asyncio.run(execute_backend_task())
```

### JavaScript SDK Example
```javascript
import { ClaudeCodeClient } from '@claude-code/sdk';

// Initialize client
const client = new ClaudeCodeClient({
  baseURL: 'http://localhost:8080/api/v3',
  authToken: 'your_jwt_token'
});

// Execute slash command
async function createProject() {
  const execution = await client.commands.execute({
    command: '/new-project',
    parameters: {
      description: 'E-commerce platform',
      technology: 'React, Node.js'
    }
  });
  
  // Subscribe to real-time updates
  const ws = client.status.subscribe(['command_progress']);
  ws.on('command_progress', (data) => {
    if (data.execution_id === execution.execution_id) {
      console.log(`Progress: ${data.progress}%`);
    }
  });
  
  return execution;
}
```

### Mobile SDK Example (React Native)
```javascript
import { ClaudeCodeMobile } from '@claude-code/mobile-sdk';

// Initialize mobile client
const client = new ClaudeCodeMobile({
  baseURL: 'http://your-desktop-ip:8080/api/v3',
  deviceInfo: {
    platform: 'ios',
    deviceName: 'iPhone 15 Pro'
  }
});

// Register device and execute commands
async function setupMobileControl() {
  // Register device
  await client.register({
    userId: 'user_123',
    capabilities: ['notifications', 'remote_control']
  });
  
  // Send command to desktop
  const command = await client.sendCommand({
    type: 'execute_slash_command',
    command: '/project-status'
  });
  
  // Listen for notifications
  client.onNotification((notification) => {
    console.log('Desktop notification:', notification);
  });
}
```

---

## Error Codes Reference

### Common Error Codes
- `AGENT_NOT_FOUND` - Specified agent does not exist
- `AGENT_BUSY` - Agent is currently executing another task
- `INVALID_COMMAND` - Command syntax or parameters invalid
- `HOOK_EXECUTION_FAILED` - Hook execution encountered an error
- `MCP_CONNECTION_FAILED` - MCP server connection issue
- `RATE_LIMIT_EXCEEDED` - Too many requests per time period
- `AUTHENTICATION_FAILED` - Invalid or expired token
- `INSUFFICIENT_PERMISSIONS` - Token lacks required scope
- `SYSTEM_OVERLOADED` - System resource limits exceeded
- `WEBSOCKET_CONNECTION_FAILED` - Real-time connection issue

### Error Response Example
```json
{
  "success": false,
  "error": {
    "code": "AGENT_BUSY",
    "message": "Agent '@agent-backend-services' is currently executing another task",
    "details": {
      "current_task": "API implementation for project_456",
      "estimated_completion": "2025-01-16T10:35:00Z",
      "queue_position": 3
    },
    "retry_after": 300
  }
}
```

---

*Claude Code Dev Stack v3.0 API Reference - Complete and Ready for Integration*

Last Updated: January 16, 2025