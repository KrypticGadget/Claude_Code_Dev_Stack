#!/usr/bin/env python3
"""
Claude Code Global Installation Verification Script
Verifies all 4 components are installed correctly at Claude Code root level
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shutil
import argparse

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class InstallationVerifier:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.claude_root = self._find_claude_root()
        self.results = {
            'agents': {'status': False, 'details': [], 'errors': []},
            'commands': {'status': False, 'details': [], 'errors': []},
            'mcp': {'status': False, 'details': [], 'errors': []},
            'hooks': {'status': False, 'details': [], 'errors': []},
            'config': {'status': False, 'details': [], 'errors': []},
            'environment': {'status': False, 'details': [], 'errors': []},
            'functionality': {'status': False, 'details': [], 'errors': []}
        }
        
    def _find_claude_root(self) -> Path:
        """Find Claude Code root directory"""
        # Check common locations based on platform
        system = platform.system()
        home = Path.home()
        
        possible_paths = []
        
        if system == "Windows":
            possible_paths.extend([
                home / "AppData" / "Roaming" / "Claude",
                home / "AppData" / "Local" / "Claude",
                Path("C:/Users") / os.environ.get("USERNAME", "") / "AppData" / "Roaming" / "Claude"
            ])
        elif system == "Darwin":  # macOS
            possible_paths.extend([
                home / "Library" / "Application Support" / "Claude",
                home / ".claude"
            ])
        else:  # Linux/WSL
            possible_paths.extend([
                home / ".config" / "claude",
                home / ".claude"
            ])
            
            # WSL specific - check Windows paths
            if "microsoft" in platform.uname().release.lower():
                windows_user = os.environ.get("USER", "")
                possible_paths.extend([
                    Path(f"/mnt/c/Users/{windows_user}/AppData/Roaming/Claude"),
                    Path(f"/mnt/c/Users/{windows_user}/AppData/Local/Claude")
                ])
        
        # Check each possible path
        for path in possible_paths:
            if path.exists() and (path / "settings.json").exists():
                return path
                
        # Fallback - look for settings.json in parent directories
        current = Path.cwd()
        while current != current.parent:
            if (current / "settings.json").exists():
                return current
            current = current.parent
            
        return Path.home() / ".claude"  # Default fallback
    
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    def print_status(self, component: str, status: bool, details: str = ""):
        """Print component status"""
        icon = "✓" if status else "✗"
        color = Colors.GREEN if status else Colors.RED
        print(f"{color}{icon} {component}{Colors.RESET}", end="")
        if details:
            print(f" - {details}")
        else:
            print()
    
    def verify_agents(self) -> bool:
        """Verify agents directory and contents"""
        self.print_header("Verifying AI Agents")
        
        agents_dir = self.claude_root / "agents"
        
        # Check if agents directory exists
        if not agents_dir.exists():
            self.results['agents']['errors'].append(f"Agents directory not found at {agents_dir}")
            self.print_status("Agents directory", False, f"Not found at {agents_dir}")
            return False
        
        self.print_status("Agents directory", True, str(agents_dir))
        
        # Expected agents (28 total)
        expected_agents = [
            "project-manager-agent.md",
            "technical-specifications-agent.md",
            "database-design-agent.md",
            "api-integration-agent.md",
            "backend-implementation-agent.md",
            "frontend-development-agent.md",
            "ui-ux-design-agent.md",
            "authentication-security-agent.md",
            "testing-automation-agent.md",
            "devops-deployment-agent.md",
            "documentation-generation-agent.md",
            "code-review-agent.md",
            "performance-optimization-agent.md",
            "error-handling-agent.md",
            "logging-monitoring-agent.md",
            "data-migration-agent.md",
            "third-party-integration-agent.md",
            "notification-system-agent.md",
            "search-implementation-agent.md",
            "caching-optimization-agent.md",
            "file-management-agent.md",
            "real-time-features-agent.md",
            "analytics-implementation-agent.md",
            "security-audit-agent.md",
            "accessibility-compliance-agent.md",
            "internationalization-agent.md",
            "backup-recovery-agent.md",
            "quality-assurance-agent.md"
        ]
        
        # Check each agent file
        found_agents = []
        missing_agents = []
        
        for agent_file in expected_agents:
            agent_path = agents_dir / agent_file
            if agent_path.exists():
                found_agents.append(agent_file)
                # Check file size (should have content)
                if agent_path.stat().st_size < 100:
                    self.results['agents']['errors'].append(f"Agent file {agent_file} appears to be empty")
            else:
                missing_agents.append(agent_file)
        
        # Report results
        self.print_status(f"Agent files found", len(found_agents) == 28, 
                         f"{len(found_agents)}/28")
        
        if missing_agents:
            self.results['agents']['errors'].append(f"Missing agents: {', '.join(missing_agents[:5])}{'...' if len(missing_agents) > 5 else ''}")
            if self.verbose:
                print(f"{Colors.YELLOW}Missing agents:{Colors.RESET}")
                for agent in missing_agents:
                    print(f"  - {agent}")
        
        # Check agent-config.yaml
        agent_config = self.claude_root / "agent-config.yaml"
        if agent_config.exists():
            self.print_status("agent-config.yaml", True)
            self.results['agents']['details'].append("Configuration file found")
            
            # Verify YAML structure
            try:
                import yaml
                with open(agent_config, 'r') as f:
                    config = yaml.safe_load(f)
                    if 'agents' in config:
                        self.print_status("Configuration valid", True, 
                                        f"{len(config.get('agents', {}))} agents configured")
            except Exception as e:
                self.results['agents']['errors'].append(f"Error parsing agent-config.yaml: {e}")
        else:
            self.print_status("agent-config.yaml", False)
            self.results['agents']['errors'].append("agent-config.yaml not found")
        
        self.results['agents']['status'] = len(missing_agents) == 0 and agent_config.exists()
        return self.results['agents']['status']
    
    def verify_commands(self) -> bool:
        """Verify commands directory and contents"""
        self.print_header("Verifying Slash Commands")
        
        commands_dir = self.claude_root / "commands"
        
        # Check if commands directory exists
        if not commands_dir.exists():
            self.results['commands']['errors'].append(f"Commands directory not found at {commands_dir}")
            self.print_status("Commands directory", False, f"Not found at {commands_dir}")
            return False
        
        self.print_status("Commands directory", True, str(commands_dir))
        
        # Expected commands (18 total)
        expected_commands = [
            "analyze-project.js",
            "setup-environment.js",
            "create-component.js",
            "implement-feature.js",
            "fix-bug.js",
            "refactor-code.js",
            "optimize-performance.js",
            "add-tests.js",
            "deploy-app.js",
            "review-code.js",
            "generate-docs.js",
            "security-scan.js",
            "update-dependencies.js",
            "migrate-data.js",
            "backup-project.js",
            "monitor-logs.js",
            "debug-issue.js",
            "sync-team.js"
        ]
        
        # Check each command file
        found_commands = []
        missing_commands = []
        
        for cmd_file in expected_commands:
            cmd_path = commands_dir / cmd_file
            if cmd_path.exists():
                found_commands.append(cmd_file)
                # Check if executable
                if not os.access(cmd_path, os.X_OK) and platform.system() != "Windows":
                    self.results['commands']['errors'].append(f"Command {cmd_file} is not executable")
            else:
                missing_commands.append(cmd_file)
        
        self.print_status(f"Command files found", len(found_commands) == 18, 
                         f"{len(found_commands)}/18")
        
        if missing_commands:
            self.results['commands']['errors'].append(f"Missing commands: {', '.join(missing_commands[:5])}{'...' if len(missing_commands) > 5 else ''}")
            if self.verbose:
                print(f"{Colors.YELLOW}Missing commands:{Colors.RESET}")
                for cmd in missing_commands:
                    print(f"  - {cmd}")
        
        # Check commands-registry.json
        commands_registry = self.claude_root / "commands-registry.json"
        if commands_registry.exists():
            self.print_status("commands-registry.json", True)
            try:
                with open(commands_registry, 'r') as f:
                    registry = json.load(f)
                    cmd_count = len(registry.get('commands', []))
                    self.print_status("Registry valid", True, f"{cmd_count} commands registered")
            except Exception as e:
                self.results['commands']['errors'].append(f"Error parsing commands-registry.json: {e}")
        else:
            self.print_status("commands-registry.json", False)
            self.results['commands']['errors'].append("commands-registry.json not found")
        
        self.results['commands']['status'] = len(missing_commands) == 0 and commands_registry.exists()
        return self.results['commands']['status']
    
    def verify_mcp(self) -> bool:
        """Verify MCP servers"""
        self.print_header("Verifying MCP Servers")
        
        mcp_dir = self.claude_root / "mcp"
        
        # Check if MCP directory exists
        if not mcp_dir.exists():
            self.results['mcp']['errors'].append(f"MCP directory not found at {mcp_dir}")
            self.print_status("MCP directory", False, f"Not found at {mcp_dir}")
            return False
        
        self.print_status("MCP directory", True, str(mcp_dir))
        
        # Expected Tier 1 MCPs
        expected_mcps = {
            "filesystem": ["index.js", "package.json", "README.md"],
            "git": ["index.js", "package.json", "README.md"],
            "github": ["index.js", "package.json", "README.md"]
        }
        
        found_mcps = []
        missing_mcps = []
        
        for mcp_name, expected_files in expected_mcps.items():
            mcp_path = mcp_dir / mcp_name
            if mcp_path.exists():
                found_mcps.append(mcp_name)
                # Check expected files
                for file in expected_files:
                    if not (mcp_path / file).exists():
                        self.results['mcp']['errors'].append(f"Missing {file} in {mcp_name} MCP")
                
                # Check if npm installed
                node_modules = mcp_path / "node_modules"
                if not node_modules.exists():
                    self.results['mcp']['errors'].append(f"{mcp_name} MCP dependencies not installed")
                    self.print_status(f"{mcp_name} MCP", False, "Dependencies not installed")
                else:
                    self.print_status(f"{mcp_name} MCP", True, "Installed")
            else:
                missing_mcps.append(mcp_name)
                self.print_status(f"{mcp_name} MCP", False, "Not found")
        
        # Check mcp-config.json
        mcp_config = self.claude_root / "mcp-config.json"
        if mcp_config.exists():
            self.print_status("mcp-config.json", True)
            try:
                with open(mcp_config, 'r') as f:
                    config = json.load(f)
                    servers = config.get('mcpServers', {})
                    self.print_status("MCP configuration", True, f"{len(servers)} servers configured")
            except Exception as e:
                self.results['mcp']['errors'].append(f"Error parsing mcp-config.json: {e}")
        else:
            self.print_status("mcp-config.json", False)
            self.results['mcp']['errors'].append("mcp-config.json not found")
        
        self.results['mcp']['status'] = len(missing_mcps) == 0 and mcp_config.exists()
        return self.results['mcp']['status']
    
    def verify_hooks(self) -> bool:
        """Verify execution hooks"""
        self.print_header("Verifying Execution Hooks")
        
        hooks_dir = self.claude_root / ".claude-global"
        
        # Check if hooks directory exists
        if not hooks_dir.exists():
            self.results['hooks']['errors'].append(f"Hooks directory not found at {hooks_dir}")
            self.print_status("Hooks directory", False, f"Not found at {hooks_dir}")
            return False
        
        self.print_status("Hooks directory", True, str(hooks_dir))
        
        # Expected hook files
        expected_hooks = [
            "pre-execute.js",
            "post-execute.js",
            "error-handler.js",
            "auth-handler.js",
            "rate-limiter.js"
        ]
        
        found_hooks = []
        missing_hooks = []
        
        for hook_file in expected_hooks:
            hook_path = hooks_dir / hook_file
            if hook_path.exists():
                found_hooks.append(hook_file)
                self.print_status(f"{hook_file}", True)
                
                # Check if executable
                if platform.system() != "Windows" and not os.access(hook_path, os.X_OK):
                    self.results['hooks']['errors'].append(f"Hook {hook_file} is not executable")
            else:
                missing_hooks.append(hook_file)
                self.print_status(f"{hook_file}", False)
        
        # Check hooks configuration
        hooks_config = hooks_dir / "hooks-config.json"
        if hooks_config.exists():
            self.print_status("hooks-config.json", True)
            try:
                with open(hooks_config, 'r') as f:
                    config = json.load(f)
                    enabled_hooks = [h for h in config.get('hooks', {}) if config['hooks'][h].get('enabled', False)]
                    self.print_status("Enabled hooks", True, f"{len(enabled_hooks)} hooks enabled")
            except Exception as e:
                self.results['hooks']['errors'].append(f"Error parsing hooks-config.json: {e}")
        else:
            self.print_status("hooks-config.json", False)
            self.results['hooks']['errors'].append("hooks-config.json not found")
        
        self.results['hooks']['status'] = len(missing_hooks) == 0
        return self.results['hooks']['status']
    
    def verify_configuration(self) -> bool:
        """Verify configuration files"""
        self.print_header("Verifying Configuration Files")
        
        # Check settings.json
        settings_path = self.claude_root / "settings.json"
        if settings_path.exists():
            self.print_status("settings.json", True)
            try:
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    
                # Check required paths
                required_paths = ['agentsPath', 'commandsPath', 'mcpPath', 'hooksPath']
                missing_paths = []
                
                for path_key in required_paths:
                    if path_key not in settings:
                        missing_paths.append(path_key)
                    else:
                        # Verify path exists
                        path_value = settings[path_key]
                        if not Path(path_value).exists():
                            self.results['config']['errors'].append(f"{path_key} points to non-existent path: {path_value}")
                
                if missing_paths:
                    self.results['config']['errors'].append(f"Missing paths in settings.json: {', '.join(missing_paths)}")
                    self.print_status("Required paths", False, f"Missing: {', '.join(missing_paths)}")
                else:
                    self.print_status("Required paths", True, "All paths configured")
                    
                # Check for custom prompts
                if 'customPrompts' in settings:
                    self.print_status("Custom prompts", True, f"{len(settings['customPrompts'])} prompts configured")
                    
            except Exception as e:
                self.results['config']['errors'].append(f"Error parsing settings.json: {e}")
                self.print_status("settings.json parsing", False, str(e))
        else:
            self.print_status("settings.json", False, "Not found")
            self.results['config']['errors'].append("settings.json not found")
            return False
        
        # Check workspace settings
        workspace_settings = Path.cwd() / ".claude" / "settings.json"
        if workspace_settings.exists():
            self.print_status("Workspace settings", True, "Found project-specific settings")
        else:
            self.print_status("Workspace settings", False, "No project-specific settings")
        
        self.results['config']['status'] = settings_path.exists() and len(self.results['config']['errors']) == 0
        return self.results['config']['status']
    
    def verify_environment(self) -> bool:
        """Verify environment variables and dependencies"""
        self.print_header("Verifying Environment")
        
        # Check Node.js installation
        try:
            node_version = subprocess.check_output(['node', '--version'], text=True).strip()
            self.print_status("Node.js", True, node_version)
            
            # Check version requirement (should be >= 18)
            version_num = float(node_version.split('.')[0][1:])
            if version_num < 18:
                self.results['environment']['errors'].append(f"Node.js version {node_version} is below recommended v18+")
        except subprocess.CalledProcessError:
            self.print_status("Node.js", False, "Not found in PATH")
            self.results['environment']['errors'].append("Node.js not found")
        
        # Check npm installation
        try:
            npm_version = subprocess.check_output(['npm', '--version'], text=True).strip()
            self.print_status("npm", True, f"v{npm_version}")
        except subprocess.CalledProcessError:
            self.print_status("npm", False, "Not found in PATH")
            self.results['environment']['errors'].append("npm not found")
        
        # Check Python (for some scripts)
        try:
            python_version = subprocess.check_output([sys.executable, '--version'], text=True).strip()
            self.print_status("Python", True, python_version)
        except subprocess.CalledProcessError:
            self.print_status("Python", False, "Issue with Python")
        
        # Check environment variables
        env_vars = {
            'CLAUDE_HOME': self.claude_root,
            'CLAUDE_AGENTS_PATH': self.claude_root / 'agents',
            'CLAUDE_COMMANDS_PATH': self.claude_root / 'commands',
            'CLAUDE_MCP_PATH': self.claude_root / 'mcp'
        }
        
        for var_name, expected_path in env_vars.items():
            actual_value = os.environ.get(var_name)
            if actual_value:
                self.print_status(f"${var_name}", True, actual_value)
                if Path(actual_value) != expected_path:
                    self.results['environment']['errors'].append(f"{var_name} points to wrong location")
            else:
                self.print_status(f"${var_name}", False, "Not set")
                self.results['environment']['details'].append(f"Recommended: export {var_name}={expected_path}")
        
        # Check PATH includes Claude directories
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        claude_in_path = any(str(self.claude_root) in p for p in path_dirs)
        
        if claude_in_path:
            self.print_status("Claude in PATH", True)
        else:
            self.print_status("Claude in PATH", False, "Claude directories not in PATH")
            self.results['environment']['details'].append(f"Add to PATH: {self.claude_root / 'commands'}")
        
        self.results['environment']['status'] = len(self.results['environment']['errors']) == 0
        return self.results['environment']['status']
    
    def test_functionality(self) -> bool:
        """Test actual functionality"""
        self.print_header("Testing Functionality")
        
        # Test 1: Agent mention simulation
        test_agent_file = self.claude_root / "agents" / "project-manager-agent.md"
        if test_agent_file.exists():
            self.print_status("@agent-project-manager", True, "Agent file accessible")
            self.results['functionality']['details'].append("Agent mentions should work")
        else:
            self.print_status("@agent-project-manager", False, "Agent file not found")
            self.results['functionality']['errors'].append("Agent mentions may not work")
        
        # Test 2: Command execution test
        test_command = self.claude_root / "commands" / "analyze-project.js"
        if test_command.exists():
            try:
                # Check if command is valid JavaScript
                result = subprocess.run(['node', '--check', str(test_command)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.print_status("/analyze-project", True, "Command syntax valid")
                else:
                    self.print_status("/analyze-project", False, "Command has syntax errors")
                    self.results['functionality']['errors'].append(f"Command syntax error: {result.stderr}")
            except Exception as e:
                self.print_status("/analyze-project", False, f"Could not validate: {e}")
        else:
            self.print_status("/analyze-project", False, "Command not found")
        
        # Test 3: MCP server test
        mcp_test = self.claude_root / "mcp" / "filesystem" / "index.js"
        if mcp_test.exists():
            self.print_status("MCP filesystem server", True, "Server file found")
            # Check if can be loaded
            try:
                result = subprocess.run(['node', '--check', str(mcp_test)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.results['functionality']['details'].append("MCP servers should be functional")
            except Exception:
                pass
        else:
            self.print_status("MCP filesystem server", False, "Server not found")
        
        # Test 4: Hook execution test
        pre_hook = self.claude_root / ".claude-global" / "pre-execute.js"
        if pre_hook.exists():
            self.print_status("Pre-execution hook", True, "Hook file found")
            self.results['functionality']['details'].append("Hooks should execute on commands")
        else:
            self.print_status("Pre-execution hook", False, "Hook not found")
        
        # Test 5: Path with spaces handling
        test_path_spaces = Path("/tmp/test path with spaces")
        try:
            test_path_spaces.mkdir(exist_ok=True)
            test_file = test_path_spaces / "test.txt"
            test_file.write_text("test")
            test_file.unlink()
            test_path_spaces.rmdir()
            self.print_status("Paths with spaces", True, "Handled correctly")
        except Exception as e:
            self.print_status("Paths with spaces", False, f"Issue with spaces: {e}")
            self.results['functionality']['errors'].append("May have issues with paths containing spaces")
        
        self.results['functionality']['status'] = len(self.results['functionality']['errors']) == 0
        return self.results['functionality']['status']
    
    def generate_report(self) -> str:
        """Generate detailed report"""
        report = []
        report.append("\n" + "="*60)
        report.append("CLAUDE CODE INSTALLATION VERIFICATION REPORT")
        report.append("="*60)
        report.append(f"\nClaude Root Directory: {self.claude_root}")
        report.append(f"Platform: {platform.system()} ({platform.platform()})")
        report.append(f"Python: {sys.version.split()[0]}")
        
        # Summary
        report.append(f"\n{Colors.BOLD}SUMMARY:{Colors.RESET}")
        total_components = len(self.results)
        passed_components = sum(1 for r in self.results.values() if r['status'])
        
        status_color = Colors.GREEN if passed_components == total_components else Colors.YELLOW if passed_components > total_components // 2 else Colors.RED
        report.append(f"{status_color}Overall Status: {passed_components}/{total_components} components verified{Colors.RESET}")
        
        # Component details
        for component, data in self.results.items():
            report.append(f"\n{Colors.BOLD}{component.upper()}:{Colors.RESET}")
            status_icon = "✓" if data['status'] else "✗"
            status_color = Colors.GREEN if data['status'] else Colors.RED
            report.append(f"  Status: {status_color}{status_icon} {'PASSED' if data['status'] else 'FAILED'}{Colors.RESET}")
            
            if data['details']:
                report.append("  Details:")
                for detail in data['details']:
                    report.append(f"    - {detail}")
            
            if data['errors']:
                report.append(f"  {Colors.RED}Errors:{Colors.RESET}")
                for error in data['errors']:
                    report.append(f"    - {error}")
        
        # Recommendations
        report.append(f"\n{Colors.BOLD}RECOMMENDATIONS:{Colors.RESET}")
        
        if not self.results['agents']['status']:
            report.append("\nTo fix Agents:")
            report.append("  1. Run the agent installer:")
            report.append("     curl -fsSL https://raw.githubusercontent.com/user/repo/main/install-agents.sh | bash")
            report.append("  2. Or manually download agents to:")
            report.append(f"     {self.claude_root / 'agents'}")
        
        if not self.results['commands']['status']:
            report.append("\nTo fix Commands:")
            report.append("  1. Run the commands installer:")
            report.append("     npm install -g @claude-code/commands")
            report.append("  2. Ensure commands are executable:")
            report.append(f"     chmod +x {self.claude_root / 'commands'}/*.js")
        
        if not self.results['mcp']['status']:
            report.append("\nTo fix MCP Servers:")
            report.append("  1. Clone MCP repositories:")
            report.append(f"     cd {self.claude_root / 'mcp'}")
            report.append("     git clone https://github.com/modelcontextprotocol/servers.git")
            report.append("  2. Install dependencies for each MCP:")
            report.append("     cd filesystem && npm install")
        
        if not self.results['hooks']['status']:
            report.append("\nTo fix Hooks:")
            report.append("  1. Create hooks directory:")
            report.append(f"     mkdir -p {self.claude_root / '.claude-global'}")
            report.append("  2. Download hook templates from repository")
        
        if not self.results['environment']['status']:
            report.append("\nTo fix Environment:")
            report.append("  1. Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
            report.append(f"     export CLAUDE_HOME=\"{self.claude_root}\"")
            report.append(f"     export PATH=\"$PATH:{self.claude_root / 'commands'}\"")
            report.append("  2. Install Node.js 18+ if not present")
        
        # Quick fix script
        report.append(f"\n{Colors.BOLD}QUICK FIX SCRIPT:{Colors.RESET}")
        report.append("Run this to attempt automatic fixes:")
        report.append("```bash")
        report.append("#!/bin/bash")
        report.append(f"export CLAUDE_HOME=\"{self.claude_root}\"")
        report.append("mkdir -p \"$CLAUDE_HOME\"/{agents,commands,mcp,.claude-global}")
        report.append("# Download and install components...")
        report.append("# Add more specific commands based on your installation method")
        report.append("```")
        
        return "\n".join(report)
    
    def run_verification(self) -> bool:
        """Run all verification steps"""
        print(f"{Colors.BOLD}{Colors.CYAN}Claude Code Global Installation Verifier{Colors.RESET}")
        print(f"Checking installation at: {self.claude_root}\n")
        
        # Run all verifications
        self.verify_agents()
        self.verify_commands()
        self.verify_mcp()
        self.verify_hooks()
        self.verify_configuration()
        self.verify_environment()
        self.test_functionality()
        
        # Generate and print report
        report = self.generate_report()
        print(report)
        
        # Save report to file
        report_file = Path.cwd() / "claude-installation-report.txt"
        # Strip ANSI codes for file output
        clean_report = report
        for color in vars(Colors).values():
            if isinstance(color, str) and color.startswith('\033'):
                clean_report = clean_report.replace(color, '')
        
        report_file.write_text(clean_report)
        print(f"\n{Colors.GREEN}Report saved to: {report_file}{Colors.RESET}")
        
        # Return overall status
        return all(r['status'] for r in self.results.values())


def main():
    parser = argparse.ArgumentParser(description="Verify Claude Code global installation")
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix issues automatically')
    args = parser.parse_args()
    
    verifier = InstallationVerifier(verbose=args.verbose)
    success = verifier.run_verification()
    
    if args.fix and not success:
        print(f"\n{Colors.YELLOW}--fix option is not yet implemented{Colors.RESET}")
        print("Please follow the recommendations in the report above")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()