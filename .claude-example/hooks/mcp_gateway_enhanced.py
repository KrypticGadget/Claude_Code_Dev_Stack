#!/usr/bin/env python3
"""Enhanced MCP Gateway - Manages and validates MCP server interactions"""

import json
import sys
import os
import re
import argparse
from datetime import datetime
from pathlib import Path

class MCPGateway:
    def __init__(self, service=None):
        self.service = service
        self.log_path = Path.home() / ".claude" / "logs" / "mcp_operations.jsonl"
        self.state_path = Path.home() / ".claude" / "state" / "mcp_state.json"
        
        # Service configurations
        self.service_configs = {
            "playwright": {
                "dangerous_patterns": ["file://", "chrome://", "about:", "javascript:"],
                "max_timeout": 30000,
                "allowed_domains": None,  # None means all domains allowed
                "rate_limit": 10  # Max requests per minute
            },
            "obsidian": {
                "protected_paths": [".obsidian/", "templates/", "archive/"],
                "max_file_size": 10485760,  # 10MB
                "allowed_extensions": [".md", ".txt", ".json", ".yml", ".yaml"],
                "rate_limit": 30  # Max operations per minute
            },
            "web-search": {
                "pii_patterns": [
                    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                    r'\b\d{16}\b',              # Credit card
                    r'password\s*[:=]',         # Passwords
                    r'\b[A-Za-z0-9+/]{40,}\b'  # API keys/tokens
                ],
                "max_results": 10,
                "rate_limit": 5  # Max searches per minute
            }
        }
        
        # Load state
        self.load_state()
    
    def load_state(self):
        """Load MCP state from disk"""
        try:
            if self.state_path.exists():
                with open(self.state_path) as f:
                    self.state = json.load(f)
            else:
                self.state = {
                    "usage": {},
                    "last_reset": datetime.now().isoformat()
                }
        except:
            self.state = {"usage": {}, "last_reset": datetime.now().isoformat()}
    
    def save_state(self):
        """Save MCP state to disk"""
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_path, 'w') as f:
                json.dump(self.state, f, indent=2)
        except:
            pass
    
    def check_rate_limit(self):
        """Check if rate limit is exceeded"""
        if self.service not in self.service_configs:
            return True, ""
        
        config = self.service_configs[self.service]
        rate_limit = config.get("rate_limit", float('inf'))
        
        # Reset usage if minute has passed
        now = datetime.now()
        last_reset = datetime.fromisoformat(self.state.get("last_reset", now.isoformat()))
        if (now - last_reset).total_seconds() > 60:
            self.state["usage"] = {}
            self.state["last_reset"] = now.isoformat()
        
        # Check current usage
        current_usage = self.state["usage"].get(self.service, 0)
        if current_usage >= rate_limit:
            return False, f"Rate limit exceeded: {current_usage}/{rate_limit} requests per minute"
        
        # Update usage
        self.state["usage"][self.service] = current_usage + 1
        self.save_state()
        
        return True, ""
    
    def validate_mcp_operation(self, tool_name, tool_input):
        """Validate MCP operations based on service"""
        # Check rate limit first
        allowed, reason = self.check_rate_limit()
        if not allowed:
            return False, reason
        
        # Service-specific validation
        validations = {
            "playwright": self.validate_playwright,
            "obsidian": self.validate_obsidian,
            "web-search": self.validate_websearch
        }
        
        if self.service in validations:
            return validations[self.service](tool_name, tool_input)
        
        return True, ""
    
    def validate_playwright(self, tool_name, tool_input):
        """Validate Playwright operations"""
        config = self.service_configs["playwright"]
        
        # Check for dangerous URLs
        url = tool_input.get("url", "")
        for pattern in config["dangerous_patterns"]:
            if pattern in url.lower():
                return False, f"Blocked dangerous URL pattern: {pattern}"
        
        # Check allowed domains if configured
        if config["allowed_domains"]:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if domain not in config["allowed_domains"]:
                return False, f"Domain not in allowed list: {domain}"
        
        # Check timeout
        timeout = tool_input.get("timeout", 0)
        if timeout > config["max_timeout"]:
            return False, f"Timeout exceeds maximum: {timeout} > {config['max_timeout']}"
        
        return True, ""
    
    def validate_obsidian(self, tool_name, tool_input):
        """Validate Obsidian operations"""
        config = self.service_configs["obsidian"]
        
        # Check protected paths
        file_path = tool_input.get("file_path", "")
        for protected in config["protected_paths"]:
            if protected in file_path:
                return False, f"Protected Obsidian path: {protected}"
        
        # Check file extension for write operations
        if tool_name in ["append_content", "patch_content"]:
            ext = Path(file_path).suffix
            if ext and ext not in config["allowed_extensions"]:
                return False, f"File type not allowed: {ext}"
        
        # Check content size
        content = tool_input.get("content", "")
        if len(content.encode('utf-8')) > config["max_file_size"]:
            return False, f"Content exceeds max size: {config['max_file_size']} bytes"
        
        return True, ""
    
    def validate_websearch(self, tool_name, tool_input):
        """Validate web search operations"""
        config = self.service_configs["web-search"]
        
        # Check for PII in search queries
        query = tool_input.get("query", "")
        for pattern in config["pii_patterns"]:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Search query contains potential sensitive data"
        
        # Check result limit
        limit = tool_input.get("limit", 5)
        if limit > config["max_results"]:
            tool_input["limit"] = config["max_results"]  # Auto-correct
        
        return True, ""
    
    def enhance_operation(self, tool_name, tool_input):
        """Enhance MCP operations with additional parameters"""
        if self.service == "playwright":
            # Add default wait strategies
            if "wait_until" not in tool_input:
                tool_input["wait_until"] = "networkidle"
            
            # Add viewport for consistency
            if "viewport" not in tool_input:
                tool_input["viewport"] = {"width": 1920, "height": 1080}
        
        elif self.service == "obsidian":
            # Add metadata to notes
            if tool_name == "append_content":
                timestamp = datetime.now().isoformat()
                tool_input["content"] = f"\n---\n*Added by Claude Code: {timestamp}*\n\n{tool_input.get('content', '')}"
        
        elif self.service == "web-search":
            # Add search refinements
            if "site:" not in tool_input.get("query", ""):
                # Could add site restrictions based on quality sources
                pass
        
        return tool_input
    
    def log_operation(self, operation_data):
        """Log MCP operations for audit and analysis"""
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a") as f:
                operation_data["timestamp"] = datetime.now().isoformat()
                operation_data["service"] = self.service
                f.write(json.dumps(operation_data) + "\n")
        except:
            pass
    
    def get_service_status(self):
        """Get current status of MCP service"""
        if self.service not in self.service_configs:
            return {"status": "unknown", "service": self.service}
        
        config = self.service_configs[self.service]
        usage = self.state["usage"].get(self.service, 0)
        rate_limit = config.get("rate_limit", float('inf'))
        
        return {
            "service": self.service,
            "status": "active",
            "usage": f"{usage}/{rate_limit} requests this minute",
            "capabilities": self.get_service_capabilities()
        }
    
    def get_service_capabilities(self):
        """Get capabilities of current MCP service"""
        capabilities = {
            "playwright": [
                "browser_automation",
                "web_scraping",
                "visual_testing",
                "form_interaction",
                "screenshot_capture"
            ],
            "obsidian": [
                "note_creation",
                "note_search",
                "content_patching",
                "file_management",
                "vault_organization"
            ],
            "web-search": [
                "web_search",
                "research",
                "information_gathering",
                "trend_analysis"
            ]
        }
        return capabilities.get(self.service, [])

def main():
    """Main execution"""
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", help="MCP service name")
    parser.add_argument("--status", action="store_true", help="Get service status")
    args, _ = parser.parse_known_args()
    
    # Initialize gateway
    gateway = MCPGateway(service=args.service)
    
    # Handle status request
    if args.status:
        status = gateway.get_service_status()
        print(json.dumps(status, indent=2))
        sys.exit(0)
    
    try:
        # Read input from Claude Code
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Skip if not an MCP tool
        if not tool_name.startswith("mcp__"):
            sys.exit(0)
        
        # Extract service name if not provided
        if not args.service:
            parts = tool_name.split("__")
            if len(parts) >= 2:
                gateway.service = parts[1]
        
        # Validate operation
        is_valid, reason = gateway.validate_mcp_operation(tool_name, tool_input)
        
        if not is_valid:
            # Block the operation
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason
                }
            }
            print(json.dumps(output))
            
            # Log denied operation
            gateway.log_operation({
                "tool": tool_name,
                "input": tool_input,
                "status": "denied",
                "reason": reason
            })
            
            sys.exit(0)
        
        # Enhance the operation
        enhanced_input = gateway.enhance_operation(tool_name, tool_input)
        
        # Log allowed operation
        gateway.log_operation({
            "tool": tool_name,
            "input": tool_input,
            "enhanced": enhanced_input != tool_input,
            "status": "allowed"
        })
        
        # Allow the operation (possibly with enhancements)
        if enhanced_input != tool_input:
            # We enhanced the input, pass it along
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": "Operation validated and enhanced",
                    "modifiedInput": enhanced_input
                }
            }
        else:
            # No modifications needed
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": "Operation validated"
                }
            }
        
        print(json.dumps(output))
        sys.exit(0)
        
    except Exception as e:
        print(f"Error in MCP gateway: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()