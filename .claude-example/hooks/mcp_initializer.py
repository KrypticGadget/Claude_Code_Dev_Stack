#!/usr/bin/env python3
"""Initialize and verify MCP servers at session start"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

class MCPInitializer:
    def __init__(self):
        self.mcp_servers = {
            "playwright": {
                "name": "Playwright MCP",
                "test_command": 'claude "Use playwright to navigate to about:blank"',
                "capabilities": ["Browser automation", "Web scraping", "Visual testing"],
                "status": "unknown"
            },
            "obsidian": {
                "name": "Obsidian MCP",
                "test_command": 'claude "Use obsidian to list files in vault"',
                "capabilities": ["Note management", "Knowledge base", "Documentation"],
                "status": "unknown"
            },
            "web-search": {
                "name": "Web-search MCP",
                "test_command": 'claude "Use web-search to find information about test"',
                "capabilities": ["Web search", "Research", "Information gathering"],
                "status": "unknown"
            }
        }
        
        self.state_dir = Path.home() / ".claude" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def check_mcp_status(self):
        """Check status of all MCP servers"""
        results = {}
        
        try:
            # Run claude mcp list command
            result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout
            
            # Check each server
            for server_id, server_info in self.mcp_servers.items():
                if server_id in output.lower():
                    server_info["status"] = "installed"
                    results[server_id] = "✅ Active"
                else:
                    server_info["status"] = "not_found"
                    results[server_id] = "❌ Not found"
            
        except subprocess.TimeoutExpired:
            for server_id in self.mcp_servers:
                self.mcp_servers[server_id]["status"] = "timeout"
                results[server_id] = "⚠️ Check timeout"
        except Exception as e:
            for server_id in self.mcp_servers:
                self.mcp_servers[server_id]["status"] = "error"
                results[server_id] = f"❌ Error: {e}"
        
        return results
    
    def generate_context(self):
        """Generate context information for Claude"""
        context = "# MCP Server Status\n\n"
        
        # Check status
        status_results = self.check_mcp_status()
        
        # Add status information
        context += "## Server Status\n"
        for server_id, status in status_results.items():
            server_info = self.mcp_servers[server_id]
            context += f"- **{server_info['name']}**: {status}\n"
        
        # Add capabilities for active servers
        active_servers = [sid for sid, info in self.mcp_servers.items() 
                         if info["status"] == "installed"]
        
        if active_servers:
            context += "\n## Available Capabilities\n"
            for server_id in active_servers:
                server_info = self.mcp_servers[server_id]
                context += f"\n### {server_info['name']}\n"
                for capability in server_info['capabilities']:
                    context += f"- {capability}\n"
        
        # Add usage instructions
        context += "\n## Usage Instructions\n"
        
        if "playwright" in active_servers:
            context += "\n### Playwright\n"
            context += "- Browser automation: `Use playwright to navigate to [URL]`\n"
            context += "- Extract content: `Use playwright to extract text from [URL]`\n"
            context += "- Take screenshot: `Use playwright to screenshot [URL]`\n"
        
        if "obsidian" in active_servers:
            context += "\n### Obsidian\n"
            context += "- List notes: `Use obsidian to list all files in vault`\n"
            context += "- Search notes: `Use obsidian to search for [query]`\n"
            context += "- Save content: `Use obsidian to save this as [filename]`\n"
        
        if "web-search" in active_servers:
            context += "\n### Web Search\n"
            context += "- Search web: `Use web-search to find [query]`\n"
            context += "- Research topic: `Use web-search to research [topic]`\n"
            context += "- Find latest: `Use web-search to find latest news about [topic]`\n"
        
        # Add troubleshooting for missing servers
        missing_servers = [sid for sid, info in self.mcp_servers.items() 
                          if info["status"] != "installed"]
        
        if missing_servers:
            context += "\n## ⚠️ Missing Servers\n"
            context += "The following MCP servers are not installed:\n"
            for server_id in missing_servers:
                server_info = self.mcp_servers[server_id]
                context += f"\n### {server_info['name']}\n"
                
                if server_id == "playwright":
                    context += "Install with: `claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless`\n"
                elif server_id == "obsidian":
                    context += "Install with: `claude mcp add obsidian --env OBSIDIAN_API_KEY=YOUR_KEY -- cmd /c uvx mcp-obsidian`\n"
                elif server_id == "web-search":
                    context += "Install with the web-search setup script\n"
        
        # Add integration tips
        context += "\n## 💡 Integration Tips\n"
        context += "- Combine MCP services for complex workflows\n"
        context += "- Example: Search web → Visit with Playwright → Save to Obsidian\n"
        context += "- MCP services work seamlessly with agents and slash commands\n"
        
        return context
    
    def save_state(self):
        """Save MCP state for session"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "servers": {}
        }
        
        for server_id, server_info in self.mcp_servers.items():
            state["servers"][server_id] = {
                "name": server_info["name"],
                "status": server_info["status"],
                "capabilities": server_info["capabilities"]
            }
        
        state_file = self.state_dir / "mcp_state.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except:
            pass
    
    def check_prerequisites(self):
        """Check if prerequisites are installed"""
        prereqs = []
        
        # Check Node.js for Playwright and web-search
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                prereqs.append("✅ Node.js installed")
            else:
                prereqs.append("❌ Node.js not found (required for Playwright/Web-search)")
        except:
            prereqs.append("❌ Node.js not found")
        
        # Check Python for Obsidian
        try:
            result = subprocess.run(["python", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                prereqs.append("✅ Python installed")
            else:
                prereqs.append("⚠️ Python not found (required for Obsidian MCP)")
        except:
            prereqs.append("⚠️ Python not found")
        
        return prereqs

def main():
    """Main execution"""
    try:
        # Read input from Claude Code
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "")
        
        # Initialize MCP checker
        initializer = MCPInitializer()
        
        # Generate context
        context = initializer.generate_context()
        
        # Check prerequisites
        prereqs = initializer.check_prerequisites()
        if prereqs:
            context += "\n## Prerequisites Check\n"
            for prereq in prereqs:
                context += f"{prereq}\n"
        
        # Save state
        initializer.save_state()
        
        # Output for Claude Code
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context
            }
        }
        
        print(json.dumps(output))
        sys.exit(0)
        
    except Exception as e:
        print(f"Error in MCP initializer: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()