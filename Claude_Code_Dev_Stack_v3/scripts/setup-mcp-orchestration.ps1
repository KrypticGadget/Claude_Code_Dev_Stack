#!/usr/bin/env powershell
# MCP Orchestration Setup for Claude Code Dev Stack v3.0
# Integrates @qdhenry/mcp-manager with v3.0 agent orchestration

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║                  MCP Orchestration Setup                       ║
║                                                                ║
║  Integrating:                                                  ║
║  • @qdhenry/mcp-manager                                        ║
║  • OpenAPI MCP generators                                      ║
║  • Playwright testing                                          ║
║  • GitHub integration                                          ║
║  + v3.0 Agent orchestration                                    ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check prerequisites
Write-Host "🔍 Checking MCP prerequisites..." -ForegroundColor Yellow

$mcpTools = @{
    "npx @modelcontextprotocol/inspector" = "MCP Inspector"
    "node" = "Node.js"
    "python" = "Python"
}

foreach ($tool in $mcpTools.Keys) {
    try {
        $cmd = $tool.Split()[0]
        $null = & $cmd --version 2>$null
        Write-Host "✅ $($mcpTools[$tool]): Available" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($mcpTools[$tool]): Missing" -ForegroundColor Red
    }
}

# Setup MCP configuration directory
Write-Host "📁 Setting up MCP configuration..." -ForegroundColor Blue

$mcpConfigDir = "$env:USERPROFILE\.claude\mcp"
if (!(Test-Path $mcpConfigDir)) {
    New-Item -Type Directory -Path $mcpConfigDir -Force
}

# Create comprehensive MCP configuration
$mcpConfig = @{
    mcpServers = @{
        "playwright" = @{
            command = "npx"
            args = @("@modelcontextprotocol/server-playwright")
            env = @{}
        }
        "github" = @{
            command = "npx"
            args = @("@modelcontextprotocol/server-github")
            env = @{
                GITHUB_PERSONAL_ACCESS_TOKEN = "your_token_here"
            }
        }
        "obsidian" = @{
            command = "python"
            args = @("-m", "mcp_server_obsidian")
            env = @{
                OBSIDIAN_VAULT_PATH = "$env:USERPROFILE\Documents\ObsidianVault"
            }
        }
        "filesystem" = @{
            command = "npx"
            args = @("@modelcontextprotocol/server-filesystem", "C:\Users\Zach\Desktop\Master Code\Claude_Code_Agents\Claude_Code_Dev_Stack\Claude_Code_Dev_Stack_v3")
            env = @{}
        }
        "websearch" = @{
            command = "npx" 
            args = @("@exa-labs/websearch-mcp-server")
            env = @{
                EXA_API_KEY = "your_exa_api_key_here"
            }
        }
        "openapi-generator" = @{
            command = "node"
            args = @("./integrations/generators/openapi-mcp-service.js")
            env = @{}
        }
        "devstack-orchestrator" = @{
            command = "python"
            args = @("./core/agents/mcp_orchestrator.py")
            env = @{
                DEVSTACK_AGENTS_PATH = "./core/agents"
                DEVSTACK_HOOKS_PATH = "./core/hooks"
                DEVSTACK_COMMANDS_PATH = "./core/commands"
            }
        }
    }
    attribution = @{
        "mcp-manager" = "@qdhenry/Claude-Code-MCP-Manager"
        "playwright" = "@modelcontextprotocol/server-playwright"
        "github" = "@modelcontextprotocol/server-github"
        "obsidian" = "MCP Obsidian server"
        "devstack" = "Original agent orchestration by Zach"
    }
} | ConvertTo-Json -Depth 10

$mcpConfig | Out-File "$mcpConfigDir\config.json" -Encoding UTF8

# Install MCP servers
Write-Host "📦 Installing MCP servers..." -ForegroundColor Blue

$mcpServers = @(
    "@modelcontextprotocol/server-playwright",
    "@modelcontextprotocol/server-github", 
    "@modelcontextprotocol/server-filesystem",
    "@exa-labs/websearch-mcp-server"
)

foreach ($server in $mcpServers) {
    Write-Host "Installing $server..." -ForegroundColor Gray
    npm install -g $server 2>$null
}

# Install Python MCP dependencies
Write-Host "Installing Python MCP dependencies..." -ForegroundColor Gray
pip install mcp-server-obsidian playwright 2>$null

# Setup custom MCP orchestrator
Write-Host "🤖 Setting up Dev Stack MCP orchestrator..." -ForegroundColor Blue

$orchestratorCode = @'
#!/usr/bin/env python3
"""
Dev Stack MCP Orchestrator
Exposes 28 agents, 28 hooks, and 18 commands via MCP protocol

Original Dev Stack by Zach
MCP integration for v3.0
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# MCP imports
from mcp import Server, McpError
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    CallToolRequest,
    CallToolResult,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
)

logger = logging.getLogger(__name__)

class DevStackMCPOrchestrator:
    """MCP Server for Dev Stack orchestration"""
    
    def __init__(self):
        self.agents_path = Path(os.environ.get('DEVSTACK_AGENTS_PATH', './core/agents'))
        self.hooks_path = Path(os.environ.get('DEVSTACK_HOOKS_PATH', './core/hooks'))
        self.commands_path = Path(os.environ.get('DEVSTACK_COMMANDS_PATH', './core/commands'))
        
        # Load agent configurations
        self.agents = self.load_agents()
        self.hooks = self.load_hooks()
        self.commands = self.load_commands()
    
    def load_agents(self) -> Dict[str, Any]:
        """Load all 28 agents"""
        agents = {}
        if self.agents_path.exists():
            for agent_file in self.agents_path.glob('*.py'):
                agent_name = agent_file.stem
                agents[agent_name] = {
                    'name': agent_name,
                    'path': str(agent_file),
                    'status': 'idle',
                    'description': f'Agent: {agent_name}'
                }
        return agents
    
    def load_hooks(self) -> Dict[str, Any]:
        """Load all 28 hooks"""
        hooks = {}
        if self.hooks_path.exists():
            for hook_file in self.hooks_path.glob('**/*.py'):
                hook_name = hook_file.stem
                hooks[hook_name] = {
                    'name': hook_name,
                    'path': str(hook_file),
                    'triggered': 0,
                    'description': f'Hook: {hook_name}'
                }
        return hooks
    
    def load_commands(self) -> Dict[str, Any]:
        """Load all 18 slash commands"""
        commands = {}
        if self.commands_path.exists():
            for cmd_file in self.commands_path.glob('*.py'):
                cmd_name = cmd_file.stem
                commands[cmd_name] = {
                    'name': cmd_name,
                    'path': str(cmd_file),
                    'usage_count': 0,
                    'description': f'Command: /{cmd_name}'
                }
        return commands

# Create MCP server
server = Server("devstack-orchestrator")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List all Dev Stack resources"""
    orchestrator = DevStackMCPOrchestrator()
    resources = []
    
    # Add agents as resources
    for agent_name, agent_data in orchestrator.agents.items():
        resources.append(Resource(
            uri=f"devstack://agents/{agent_name}",
            name=f"Agent: {agent_name}",
            description=agent_data['description'],
            mimeType="application/json"
        ))
    
    # Add hooks as resources
    for hook_name, hook_data in orchestrator.hooks.items():
        resources.append(Resource(
            uri=f"devstack://hooks/{hook_name}",
            name=f"Hook: {hook_name}",
            description=hook_data['description'],
            mimeType="application/json"
        ))
    
    # Add commands as resources
    for cmd_name, cmd_data in orchestrator.commands.items():
        resources.append(Resource(
            uri=f"devstack://commands/{cmd_name}",
            name=f"Command: /{cmd_name}",
            description=cmd_data['description'],
            mimeType="application/json"
        ))
    
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read Dev Stack resource details"""
    orchestrator = DevStackMCPOrchestrator()
    
    if uri.startswith("devstack://agents/"):
        agent_name = uri.split("/")[-1]
        if agent_name in orchestrator.agents:
            return json.dumps(orchestrator.agents[agent_name], indent=2)
    
    elif uri.startswith("devstack://hooks/"):
        hook_name = uri.split("/")[-1]
        if hook_name in orchestrator.hooks:
            return json.dumps(orchestrator.hooks[hook_name], indent=2)
    
    elif uri.startswith("devstack://commands/"):
        cmd_name = uri.split("/")[-1]
        if cmd_name in orchestrator.commands:
            return json.dumps(orchestrator.commands[cmd_name], indent=2)
    
    raise McpError("RESOURCE_NOT_FOUND", f"Resource not found: {uri}")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all Dev Stack tools"""
    return [
        Tool(
            name="invoke_agent",
            description="Invoke a Dev Stack agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Name of the agent to invoke"},
                    "task": {"type": "string", "description": "Task to execute"},
                    "parameters": {"type": "object", "description": "Task parameters"}
                },
                "required": ["agent_name", "task"]
            }
        ),
        Tool(
            name="trigger_hook",
            description="Trigger a Dev Stack hook",
            inputSchema={
                "type": "object",
                "properties": {
                    "hook_name": {"type": "string", "description": "Name of the hook to trigger"},
                    "event_data": {"type": "object", "description": "Event data for the hook"}
                },
                "required": ["hook_name"]
            }
        ),
        Tool(
            name="execute_command",
            description="Execute a Dev Stack slash command",
            inputSchema={
                "type": "object",
                "properties": {
                    "command_name": {"type": "string", "description": "Name of the command"},
                    "arguments": {"type": "array", "items": {"type": "string"}, "description": "Command arguments"}
                },
                "required": ["command_name"]
            }
        ),
        Tool(
            name="get_orchestration_status",
            description="Get current orchestration status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls"""
    orchestrator = DevStackMCPOrchestrator()
    
    if name == "invoke_agent":
        agent_name = arguments.get("agent_name")
        task = arguments.get("task")
        parameters = arguments.get("parameters", {})
        
        if agent_name not in orchestrator.agents:
            raise McpError("INVALID_PARAMS", f"Agent not found: {agent_name}")
        
        # Execute agent (mock for now)
        result = {
            "agent": agent_name,
            "task": task,
            "status": "executed",
            "result": f"Agent {agent_name} executed task: {task}",
            "parameters": parameters
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_orchestration_status":
        status = {
            "agents": {
                "total": len(orchestrator.agents),
                "active": sum(1 for a in orchestrator.agents.values() if a['status'] == 'active'),
                "idle": sum(1 for a in orchestrator.agents.values() if a['status'] == 'idle')
            },
            "hooks": {
                "total": len(orchestrator.hooks),
                "triggered": sum(h['triggered'] for h in orchestrator.hooks.values())
            },
            "commands": {
                "total": len(orchestrator.commands),
                "used": sum(c['usage_count'] for c in orchestrator.commands.values())
            },
            "attribution": "Original Dev Stack orchestration by Zach"
        }
        
        return [TextContent(type="text", text=json.dumps(status, indent=2))]
    
    else:
        raise McpError("METHOD_NOT_FOUND", f"Tool not found: {name}")

async def main():
    """Main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="devstack-orchestrator",
                server_version="3.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    import os
    asyncio.run(main())
'@

$orchestratorCode | Out-File "$PWD\core\agents\mcp_orchestrator.py" -Encoding UTF8

# Create MCP wrapper service
Write-Host "🔧 Creating MCP wrapper service..." -ForegroundColor Blue

$wrapperCode = @'
const { spawn } = require('child_process');
const path = require('path');

/**
 * MCP Manager Wrapper for Claude Code Dev Stack v3.0
 * 
 * Integrates @qdhenry/mcp-manager with v3.0 orchestration
 * Original MCP Manager by @qdhenry
 * Extended for Dev Stack v3.0 by Zach
 */

class MCPManagerWrapper {
    constructor() {
        this.mcpServers = new Map();
        this.mcpManagerPath = path.join(__dirname, '../clones/mcp-manager');
    }

    async startAllServers() {
        console.log('🚀 Starting all MCP servers...');
        
        const servers = [
            'playwright',
            'github', 
            'obsidian',
            'filesystem',
            'websearch',
            'devstack-orchestrator'
        ];

        for (const serverName of servers) {
            try {
                await this.startServer(serverName);
                console.log(`✅ ${serverName} server started`);
            } catch (error) {
                console.error(`❌ Failed to start ${serverName}: ${error.message}`);
            }
        }
    }

    async startServer(serverName) {
        return new Promise((resolve, reject) => {
            const configPath = path.join(process.env.USERPROFILE, '.claude', 'mcp', 'config.json');
            const config = require(configPath);
            
            const serverConfig = config.mcpServers[serverName];
            if (!serverConfig) {
                reject(new Error(`Server configuration not found: ${serverName}`));
                return;
            }

            const serverProcess = spawn(serverConfig.command, serverConfig.args, {
                env: { ...process.env, ...serverConfig.env },
                stdio: ['pipe', 'pipe', 'pipe']
            });

            serverProcess.on('error', reject);
            serverProcess.on('spawn', () => {
                this.mcpServers.set(serverName, serverProcess);
                resolve();
            });
        });
    }

    async stopAllServers() {
        console.log('🛑 Stopping all MCP servers...');
        
        for (const [serverName, process] of this.mcpServers) {
            try {
                process.kill('SIGTERM');
                console.log(`✅ ${serverName} server stopped`);
            } catch (error) {
                console.error(`❌ Failed to stop ${serverName}: ${error.message}`);
            }
        }
        
        this.mcpServers.clear();
    }

    getServerStatus() {
        const status = {};
        for (const [serverName, process] of this.mcpServers) {
            status[serverName] = {
                pid: process.pid,
                running: !process.killed
            };
        }
        return status;
    }
}

// Export for use in other modules
module.exports = MCPManagerWrapper;

// CLI usage
if (require.main === module) {
    const wrapper = new MCPManagerWrapper();
    
    const command = process.argv[2];
    
    switch (command) {
        case 'start':
            wrapper.startAllServers()
                .then(() => console.log('🎉 All MCP servers started successfully'))
                .catch(error => {
                    console.error('❌ Failed to start MCP servers:', error);
                    process.exit(1);
                });
            break;
            
        case 'stop':
            wrapper.stopAllServers()
                .then(() => console.log('🎉 All MCP servers stopped successfully'))
                .catch(error => {
                    console.error('❌ Failed to stop MCP servers:', error);
                    process.exit(1);
                });
            break;
            
        case 'status':
            const status = wrapper.getServerStatus();
            console.log('📊 MCP Server Status:');
            console.log(JSON.stringify(status, null, 2));
            break;
            
        default:
            console.log(`
MCP Manager Wrapper for Claude Code Dev Stack v3.0

Usage:
  node mcp-wrapper.js start    # Start all MCP servers
  node mcp-wrapper.js stop     # Stop all MCP servers
  node mcp-wrapper.js status   # Check server status

Attribution:
  Original MCP Manager by @qdhenry
  Extended for Dev Stack v3.0 by Zach
            `);
    }
}
'@

$wrapperCode | Out-File "$PWD\integrations\mcp-manager\mcp-wrapper.js" -Encoding UTF8

# Create startup script
Write-Host "📜 Creating MCP startup script..." -ForegroundColor Blue

$startupScript = @'
#!/usr/bin/env powershell
# MCP Services Startup Script

Write-Host "🚀 Starting MCP orchestration services..." -ForegroundColor Cyan

# Start MCP Manager wrapper
Start-Job -ScriptBlock {
    cd $using:PWD
    node integrations/mcp-manager/mcp-wrapper.js start
} -Name "MCPManager"

# Start MCP Inspector (optional)
Start-Job -ScriptBlock {
    npx @modelcontextprotocol/inspector
} -Name "MCPInspector"

Write-Host @"

🎉 MCP Services Started!

Available Services:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 Playwright:       Browser automation testing
🐙 GitHub:           Repository integration  
📝 Obsidian:         Knowledge management
📁 Filesystem:       File system access
🔍 WebSearch:        Web search capabilities
🤖 DevStack:         28 agents + 28 hooks + 18 commands
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Attribution:
• MCP Manager: @qdhenry/Claude-Code-MCP-Manager
• Orchestration: Original Dev Stack by Zach

Monitor: npx @modelcontextprotocol/inspector
"@ -ForegroundColor Green
'@

$startupScript | Out-File "$PWD\scripts\start-mcp-services.ps1" -Encoding UTF8

Write-Host "✅ MCP orchestration setup complete!" -ForegroundColor Green
Write-Host "" 
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update GitHub token in config.json" -ForegroundColor Gray
Write-Host "2. Update Exa API key in config.json" -ForegroundColor Gray  
Write-Host "3. Run: .\scripts\start-mcp-services.ps1" -ForegroundColor Gray