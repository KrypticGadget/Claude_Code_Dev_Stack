#!/usr/bin/env python3
"""
Statusline Installation Script

Automated installation and setup script for the Claude Code terminal statusline.
Handles shell integration, configuration setup, and dependency management.
"""

import os
import sys
import shutil
import subprocess
import json
import platform
from pathlib import Path
from typing import Dict, List, Optional


class StatuslineInstaller:
    """Handles installation of the statusline system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.bin_dir = self.project_root / "bin"
        self.config_dir = self.project_root / "config"
        self.core_dir = self.project_root / "core"
        
        self.system = platform.system().lower()
        self.home = Path.home()
        
        # Installation paths
        self.install_paths = {
            'config': self.home / '.config' / 'claude-code',
            'bin': self.home / '.local' / 'bin',
            'cache': self.home / '.cache' / 'claude-code'
        }
        
        # Shell configuration files
        self.shell_configs = {
            'bash': [
                self.home / '.bashrc',
                self.home / '.bash_profile',
                self.home / '.profile'
            ],
            'zsh': [
                self.home / '.zshrc',
                self.home / '.zprofile'
            ],
            'fish': [
                self.home / '.config' / 'fish' / 'config.fish'
            ],
            'powershell': [
                self.home / 'Documents' / 'PowerShell' / 'Microsoft.PowerShell_profile.ps1',
                self.home / 'Documents' / 'WindowsPowerShell' / 'Microsoft.PowerShell_profile.ps1'
            ]
        }
    
    def install(self, options: Dict[str, any] = None):
        """Main installation process"""
        options = options or {}
        
        print("🚀 Installing Claude Code Terminal Statusline...")
        print(f"📁 Project root: {self.project_root}")
        print(f"🖥️  System: {platform.system()} {platform.release()}")
        
        try:
            # Check prerequisites
            self._check_prerequisites()
            
            # Create directories
            self._create_directories()
            
            # Install configuration
            self._install_configuration()
            
            # Install binaries
            self._install_binaries()
            
            # Install shell integration
            if options.get('shell_integration', True):
                self._install_shell_integration(options.get('shells', ['auto']))
            
            # Set up permissions
            self._setup_permissions()
            
            # Test installation
            if options.get('test_install', True):
                self._test_installation()
            
            print("\n✅ Installation completed successfully!")
            self._print_next_steps()
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            if options.get('debug', False):
                raise
            sys.exit(1)
    
    def _check_prerequisites(self):
        """Check system prerequisites"""
        print("\n📋 Checking prerequisites...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            raise Exception(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check required modules
        required_modules = ['json', 'yaml', 'subprocess', 'threading']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✓ {module}")
            except ImportError:
                missing_modules.append(module)
                print(f"⚠️  {module} (missing)")
        
        if missing_modules:
            print(f"Installing missing modules: {missing_modules}")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_modules, 
                             check=True, capture_output=True)
                print("✓ Missing modules installed")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Could not install modules automatically: {e}")
                print("Please install manually with: pip install " + " ".join(missing_modules))
        
        # Check terminal capabilities
        self._check_terminal_capabilities()
    
    def _check_terminal_capabilities(self):
        """Check terminal support for colors and Unicode"""
        print("\n🖥️  Checking terminal capabilities...")
        
        # Color support
        if os.getenv('TERM'):
            term = os.getenv('TERM').lower()
            if 'color' in term or term in ['xterm', 'xterm-256color', 'screen', 'tmux']:
                print("✓ Color support detected")
            else:
                print("⚠️  Limited color support")
        
        # Unicode support
        try:
            encoding = sys.stdout.encoding or 'ascii'
            if 'utf' in encoding.lower():
                print(f"✓ Unicode support ({encoding})")
            else:
                print(f"⚠️  Limited Unicode support ({encoding})")
        except:
            print("⚠️  Could not detect encoding")
        
        # Terminal size
        try:
            size = shutil.get_terminal_size()
            print(f"✓ Terminal size: {size.columns}x{size.lines}")
        except:
            print("⚠️  Could not detect terminal size")
    
    def _create_directories(self):
        """Create necessary directories"""
        print("\n📁 Creating directories...")
        
        for name, path in self.install_paths.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"✓ {name}: {path}")
            except Exception as e:
                print(f"⚠️  {name}: {path} ({e})")
    
    def _install_configuration(self):
        """Install configuration files"""
        print("\n⚙️  Installing configuration...")
        
        config_dest = self.install_paths['config']
        
        # Copy main configuration
        src_config = self.config_dir / 'statusline.yml'
        dest_config = config_dest / 'statusline.yml'
        
        if src_config.exists():
            if dest_config.exists():
                # Backup existing config
                backup_path = dest_config.with_suffix('.yml.backup')
                shutil.copy2(dest_config, backup_path)
                print(f"✓ Backed up existing config to {backup_path}")
            
            shutil.copy2(src_config, dest_config)
            print(f"✓ Installed configuration: {dest_config}")
        else:
            print("⚠️  Default configuration not found, creating minimal config...")
            self._create_minimal_config(dest_config)
        
        # Copy additional config files
        for config_file in ['themes.yml', 'segments.yml']:
            src_file = self.config_dir / config_file
            if src_file.exists():
                dest_file = config_dest / config_file
                shutil.copy2(src_file, dest_file)
                print(f"✓ Installed {config_file}")
    
    def _create_minimal_config(self, config_path: Path):
        """Create a minimal configuration file"""
        minimal_config = {
            'layout': 'left',
            'position': 'bottom',
            'theme': 'default',
            'segments': [
                {'type': 'directory', 'enabled': True, 'priority': 10},
                {'type': 'git', 'enabled': True, 'priority': 20},
                {'type': 'time', 'enabled': True, 'priority': 50}
            ]
        }
        
        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(minimal_config, f, default_flow_style=False)
        
        print(f"✓ Created minimal configuration: {config_path}")
    
    def _install_binaries(self):
        """Install executable binaries"""
        print("\n🔧 Installing binaries...")
        
        bin_dest = self.install_paths['bin']
        
        # Copy main statusline script
        src_statusline = self.bin_dir / 'statusline.py'
        dest_statusline = bin_dest / 'claude-statusline'
        
        if src_statusline.exists():
            shutil.copy2(src_statusline, dest_statusline)
            dest_statusline.chmod(0o755)  # Make executable
            print(f"✓ Installed statusline binary: {dest_statusline}")
            
            # Create symlinks for convenience
            symlinks = ['statusline', 'claude-status']
            for symlink_name in symlinks:
                symlink_path = bin_dest / symlink_name
                if symlink_path.exists():
                    symlink_path.unlink()
                try:
                    symlink_path.symlink_to(dest_statusline)
                    print(f"✓ Created symlink: {symlink_path}")
                except OSError:
                    # Fallback to copy on systems that don't support symlinks
                    shutil.copy2(dest_statusline, symlink_path)
                    print(f"✓ Created copy: {symlink_path}")
        else:
            raise Exception("Main statusline script not found")
        
        # Check if bin directory is in PATH
        bin_str = str(bin_dest)
        path_env = os.getenv('PATH', '')
        if bin_str not in path_env:
            print(f"⚠️  {bin_dest} not in PATH")
            print(f"   Add this to your shell configuration:")
            print(f"   export PATH=\"{bin_dest}:$PATH\"")
    
    def _install_shell_integration(self, shells: List[str]):
        """Install shell integration"""
        print("\n🐚 Installing shell integration...")
        
        if shells == ['auto']:
            shells = self._detect_shells()
        
        for shell in shells:
            if shell in self.shell_configs:
                try:
                    self._install_shell_config(shell)
                except Exception as e:
                    print(f"⚠️  Failed to install {shell} integration: {e}")
            else:
                print(f"⚠️  Unsupported shell: {shell}")
    
    def _detect_shells(self) -> List[str]:
        """Detect available shells"""
        shells = []
        
        # Check current shell
        current_shell = os.getenv('SHELL', '')
        if current_shell:
            shell_name = Path(current_shell).name
            if shell_name in self.shell_configs:
                shells.append(shell_name)
        
        # Check for other common shells
        for shell in ['bash', 'zsh', 'fish']:
            if shutil.which(shell):
                if shell not in shells:
                    shells.append(shell)
        
        # Windows PowerShell
        if self.system == 'windows':
            if shutil.which('powershell') or shutil.which('pwsh'):
                shells.append('powershell')
        
        return shells or ['bash']  # Default to bash
    
    def _install_shell_config(self, shell: str):
        """Install configuration for specific shell"""
        config_paths = self.shell_configs[shell]
        
        # Find existing config file
        config_file = None
        for path in config_paths:
            if path.exists():
                config_file = path
                break
        
        if not config_file:
            # Create the first option
            config_file = config_paths[0]
            config_file.parent.mkdir(parents=True, exist_ok=True)
            config_file.touch()
        
        # Generate integration script
        integration_script = self._generate_shell_integration(shell)
        
        # Check if already installed
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            if 'claude-statusline' in content or 'Claude Code Statusline' in content:
                print(f"✓ {shell} integration already installed in {config_file}")
                return
        except Exception:
            pass
        
        # Append integration script
        try:
            with open(config_file, 'a') as f:
                f.write('\n\n# Claude Code Statusline Integration\n')
                f.write(integration_script)
                f.write('\n')
            
            print(f"✓ Installed {shell} integration in {config_file}")
        except Exception as e:
            raise Exception(f"Failed to write {shell} config: {e}")
    
    def _generate_shell_integration(self, shell: str) -> str:
        """Generate shell-specific integration script"""
        statusline_cmd = str(self.install_paths['bin'] / 'claude-statusline')
        
        if shell == 'bash':
            return f'''
# Function to update statusline
function _claude_statusline_update() {{
    if [[ "$TERM" != "dumb" ]] && [[ -t 1 ]]; then
        local statusline_output
        statusline_output=$("{statusline_cmd}" render 2>/dev/null)
        if [[ $? -eq 0 ]] && [[ -n "$statusline_output" ]]; then
            echo -e "\\033[s\\033[1;1H$statusline_output\\033[K\\033[u"
        fi
    fi
}}

# Update statusline before each prompt
if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="_claude_statusline_update"
else
    PROMPT_COMMAND="$PROMPT_COMMAND; _claude_statusline_update"
fi
'''
        
        elif shell == 'zsh':
            return f'''
# Function to update statusline
function _claude_statusline_update() {{
    if [[ "$TERM" != "dumb" ]] && [[ -t 1 ]]; then
        local statusline_output
        statusline_output=$("{statusline_cmd}" render 2>/dev/null)
        if [[ $? -eq 0 ]] && [[ -n "$statusline_output" ]]; then
            echo -e "\\033[s\\033[1;1H$statusline_output\\033[K\\033[u"
        fi
    fi
}}

# Add to precmd hooks
autoload -Uz add-zsh-hook
add-zsh-hook precmd _claude_statusline_update
'''
        
        elif shell == 'fish':
            return f'''
# Function to update statusline
function _claude_statusline_update --on-event fish_prompt
    if test "$TERM" != "dumb"; and isatty stdout
        set statusline_output ("{statusline_cmd}" render 2>/dev/null)
        if test $status -eq 0; and test -n "$statusline_output"
            echo -e "\\033[s\\033[1;1H$statusline_output\\033[K\\033[u"
        end
    end
end
'''
        
        elif shell == 'powershell':
            return f'''
# Function to update statusline
function Update-ClaudeStatusline {{
    if ($Host.UI.RawUI.WindowSize) {{
        try {{
            $statuslineOutput = & python "{statusline_cmd}" render 2>$null
            if ($LASTEXITCODE -eq 0 -and $statuslineOutput) {{
                $position = $Host.UI.RawUI.CursorPosition
                $Host.UI.RawUI.CursorPosition = @{{X=0; Y=0}}
                Write-Host $statuslineOutput -NoNewline
                $Host.UI.RawUI.CursorPosition = $position
            }}
        }} catch {{
            # Silently ignore errors
        }}
    }}
}}

# Update statusline with each prompt
$function:prompt = {{
    Update-ClaudeStatusline
    "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
}}
'''
        
        return '# Unsupported shell'
    
    def _setup_permissions(self):
        """Set up file permissions"""
        print("\n🔐 Setting up permissions...")
        
        # Make scripts executable
        bin_dir = self.install_paths['bin']
        for script in bin_dir.glob('*'):
            if script.is_file():
                script.chmod(0o755)
        
        print("✓ Set executable permissions on scripts")
    
    def _test_installation(self):
        """Test the installation"""
        print("\n🧪 Testing installation...")
        
        statusline_cmd = self.install_paths['bin'] / 'claude-statusline'
        
        try:
            # Test basic execution
            result = subprocess.run(
                [str(statusline_cmd), 'config', '--validate'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Configuration validation passed")
            else:
                print(f"⚠️  Configuration validation issues: {result.stderr}")
            
            # Test rendering
            result = subprocess.run(
                [str(statusline_cmd), 'render'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Statusline rendering works")
                if result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()}")
            else:
                print(f"⚠️  Rendering test failed: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            print("⚠️  Test timed out")
        except Exception as e:
            print(f"⚠️  Test failed: {e}")
    
    def _print_next_steps(self):
        """Print next steps for user"""
        print("\n📝 Next Steps:")
        print("1. Restart your terminal or run: source ~/.bashrc (or appropriate shell config)")
        print("2. Test the statusline: claude-statusline render")
        print("3. Start live updates: claude-statusline render --live")
        print("4. Customize configuration: ~/.config/claude-code/statusline.yml")
        print("5. View available themes: claude-statusline theme list")
        print("6. Get help: claude-statusline --help")
        
        # Print shell-specific instructions
        detected_shells = self._detect_shells()
        if detected_shells:
            print(f"\n🐚 Detected shells: {', '.join(detected_shells)}")
            print("   The statusline will automatically appear in new terminal sessions.")
        
        print(f"\n📁 Configuration directory: {self.install_paths['config']}")
        print(f"🔧 Binary directory: {self.install_paths['bin']}")
    
    def uninstall(self):
        """Uninstall the statusline system"""
        print("🗑️  Uninstalling Claude Code Terminal Statusline...")
        
        try:
            # Remove binaries
            bin_dir = self.install_paths['bin']
            for binary in ['claude-statusline', 'statusline', 'claude-status']:
                binary_path = bin_dir / binary
                if binary_path.exists():
                    binary_path.unlink()
                    print(f"✓ Removed {binary_path}")
            
            # Remove configuration (with confirmation)
            config_dir = self.install_paths['config']
            if config_dir.exists():
                response = input(f"Remove configuration directory {config_dir}? [y/N]: ")
                if response.lower() in ['y', 'yes']:
                    shutil.rmtree(config_dir)
                    print(f"✓ Removed {config_dir}")
                else:
                    print(f"⚠️  Kept configuration directory: {config_dir}")
            
            # Remove shell integrations
            self._remove_shell_integrations()
            
            print("\n✅ Uninstallation completed!")
            print("Note: You may need to restart your terminal or source your shell config.")
            
        except Exception as e:
            print(f"❌ Uninstallation failed: {e}")
            sys.exit(1)
    
    def _remove_shell_integrations(self):
        """Remove shell integrations"""
        print("\n🐚 Removing shell integrations...")
        
        for shell, config_paths in self.shell_configs.items():
            for config_path in config_paths:
                if config_path.exists():
                    try:
                        self._remove_from_config_file(config_path)
                    except Exception as e:
                        print(f"⚠️  Failed to clean {config_path}: {e}")
    
    def _remove_from_config_file(self, config_path: Path):
        """Remove statusline integration from config file"""
        try:
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            # Remove lines related to statusline
            filtered_lines = []
            skip_block = False
            
            for line in lines:
                if 'Claude Code Statusline' in line:
                    skip_block = True
                    continue
                elif skip_block and line.strip() == '':
                    skip_block = False
                    continue
                elif skip_block and ('_claude_statusline' in line or 'Update-ClaudeStatusline' in line):
                    continue
                
                if not skip_block:
                    filtered_lines.append(line)
            
            # Write back if changes were made
            if len(filtered_lines) != len(lines):
                with open(config_path, 'w') as f:
                    f.writelines(filtered_lines)
                print(f"✓ Cleaned {config_path}")
                
        except Exception as e:
            raise Exception(f"Failed to clean {config_path}: {e}")


def main():
    """Main installation script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install Claude Code Terminal Statusline")
    parser.add_argument('--uninstall', action='store_true', help='Uninstall the statusline')
    parser.add_argument('--shells', nargs='+', default=['auto'], 
                       help='Shells to install integration for')
    parser.add_argument('--no-shell-integration', action='store_true',
                       help='Skip shell integration')
    parser.add_argument('--no-test', action='store_true',
                       help='Skip installation test')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    installer = StatuslineInstaller()
    
    if args.uninstall:
        installer.uninstall()
    else:
        options = {
            'shells': args.shells,
            'shell_integration': not args.no_shell_integration,
            'test_install': not args.no_test,
            'debug': args.debug
        }
        installer.install(options)


if __name__ == '__main__':
    main()