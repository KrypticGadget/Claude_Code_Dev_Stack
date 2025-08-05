# 🚀 Claude Code Repository Update - Methodical Development Prompt

Copy and paste this entire prompt into Claude Code:

---

## Project: Comprehensive Claude Code Dev Stack Update - Windows Native + MCP Integration + Meta-Prompting

I need to systematically update my GitHub repository at https://github.com/KrypticGadget/Claude_Code_Dev_Stack using the agent system and slash commands.

### Phase 1: Project Analysis and Planning

```
/business-analysis
Context: Updating existing open-source developer tool repository
Current state: Linux/WSL only, 28 agents, 18 slash commands
Target state: Cross-platform (Windows native), MCP integration, meta-prompting guide
Market need: Windows developers need native PowerShell support
Impact: Expand user base by 60% (Windows developers)
```

```
/technical-feasibility "Cross-platform Claude Code Dev Stack"
Requirements:
- Convert bash scripts to PowerShell
- Maintain backward compatibility
- Add MCP tool integration layer
- Create meta-prompting methodology
Constraints: Must work on PowerShell 5.1+ and Core 7+
Scale: Supporting thousands of developers
```

```
/project-plan "Claude Code Dev Stack v2.0"
Phases:
1. Windows PowerShell scripts
2. MCP integration layer
3. Meta-prompting guide
4. Hooks and testing system
5. Documentation update
Timeline: Complete in current session
Team: Solo developer
Deliverables: Updated repository ready for release
```

### Phase 2: Windows PowerShell Implementation

```
/backend-service "PowerShell installation scripts"
Context: Create Windows-native installation system
Requirements:
- install.ps1: Main agent installer
- install-commands.ps1: Slash commands installer  
- install-all.ps1: Combined installer
Features:
- Progress indicators
- Error handling
- Directory creation
- Configuration generation
Technical specs:
- Use Invoke-WebRequest for downloads
- Support one-line execution: iwr -useb URL | iex
- Check for Claude Code installation
- Generate quick reference guide
```

```
/code-review
Focus: PowerShell best practices
Check for:
- Proper error handling with try/catch
- Correct path handling with Join-Path
- Progress reporting with Write-Progress
- Cross-version compatibility (PS 5.1 and 7+)
```

### Phase 3: MCP Integration Layer

```
/integration "Model Context Protocol tools"
Context: Add MCP tool support to agent system
Tier 1 Tools:
- @file-system: Read/write project files
- @git: Version control operations
- @database: Direct DB queries
- @api-test: Endpoint validation
- @env-config: Environment management
Integration points:
- Each agent gets MCP recommendations
- Slash commands auto-include relevant tools
- Tool chaining for complex operations
Configuration:
- Create mcp-integration/tier1-tools.json
- Tool-specific prompt templates
- Integration rules and patterns
```

```
/database-design "MCP tool registry"
Schema: JSON configuration
Tables/Objects:
- tools: name, description, operations
- integration_points: agents, commands, use_cases
- prompt_templates: tool-specific patterns
- auto_include_rules: workflow-based tool selection
```

### Phase 4: Meta-Prompting Methodology

```
/documentation "Master Prompting Guide"
Type: Comprehensive methodology guide
Sections:
1. AIMS Structure (Agent, Integration, Method, Structure)
2. Quick reference tables (commands, agents, tools)
3. Master prompt templates
4. Workflow examples
5. Integration patterns
Purpose: Enable any Claude instance to generate perfect prompts
Format: Markdown with examples
Special requirements:
- Include all 28 agents
- Include all 18 slash commands
- MCP tool integration patterns
- Real-world examples
```

```
/technical-writer review
Ensure the guide is:
- Clear for non-technical users
- Comprehensive for developers
- Contains copy-paste ready examples
- Follows consistent formatting
```

### Phase 5: Hooks and Administrative Tools

```
/devops "Automated hooks system"
Context: Enhance reliability with git hooks
Components:
- pre-commit.ps1: Code review, security, tests, docs
- post-update.ps1: Sync and context updates
- test-runner.ps1: Automated testing
- diff-logger.ps1: Change tracking
Implementation:
- PowerShell scripts for Windows
- Git hook wrappers
- Configuration file
- Setup script
```

```
/test-suite "Hook testing scenarios"
Test cases:
1. Pre-commit blocks bad code
2. Tests run automatically
3. Documentation updates
4. Diff logs capture changes
5. Security scans work
```

### Phase 6: Documentation and Structure Update

```
/frontend-mockup "Updated README.md"
Requirements:
- Add Windows installation section
- Update quick install commands
- Include meta-prompting section
- Maintain existing content
New sections:
- Windows PowerShell (Native)
- With MCP Tools (Advanced)
- Meta-Prompting Methodology
```

```
/documentation "WINDOWS_INSTALL.md"
Content:
- PowerShell installation guide
- One-line commands
- Installation locations
- Usage examples
- Troubleshooting
- PowerShell aliases
```

### Phase 7: Repository Structure

```
/project-structure
Create directories:
- /windows/
  - README.md
  - claude-code-aliases.ps1
  - setup-hooks.ps1
  - admin-tools.ps1
- /mcp-integration/
  - README.md
  - tier1-tools.json
  - tool-prompts/
    - file-system.md
    - git-integration.md
    - database-access.md
    - api-testing.md
- /hooks/
  - pre-commit.ps1
  - post-update.ps1
  - test-runner.ps1
  - diff-logger.ps1
Root files to add:
- install.ps1
- install-commands.ps1
- install-all.ps1
- WINDOWS_INSTALL.md
- MASTER_PROMPTING_GUIDE.md
```

### Phase 8: Testing and Validation

```
/test-suite "Windows installation test"
Test scenarios:
1. Fresh Windows PowerShell 5.1 install
2. Fresh PowerShell Core 7+ install
3. One-line installation command
4. All agents accessible
5. All slash commands work
6. MCP tools integrate properly
```

```
/security-audit
Review:
- No hardcoded credentials
- Secure download methods
- Proper permission handling
- Safe script execution
```

### Phase 9: Final Review and Git Operations

```
/code-review all changes
Checklist:
- PowerShell scripts follow best practices
- Documentation is complete
- All new files created
- Backward compatibility maintained
- Meta-prompting guide is comprehensive
```

```
/git-workflow
Commands:
1. git checkout -b feature/windows-powershell-support
2. git add all new files
3. git commit -m "Add Windows PowerShell support and meta-prompting methodology"
4. git push origin feature/windows-powershell-support
5. Create pull request with detailed description
```

### Phase 10: Release Preparation

```
/documentation "Release notes for v2.0.0"
## Claude Code Dev Stack v2.0.0

### 🎉 Major Features
- Native Windows PowerShell support
- One-line installation for all platforms
- MCP (Model Context Protocol) integration
- Meta-prompting methodology
- Automated hooks system

### 🔧 Changes
- Added PowerShell installation scripts
- Created comprehensive prompting guide
- Integrated Tier 1 MCP tools
- Enhanced testing protocols

### 📋 Installation
Windows: iwr -useb URL | iex
Linux/Mac: curl -sL URL | bash
```

```
/deploy preparation
- Tag as v2.0.0
- Update version references
- Prepare announcement
- Update GitHub releases
```

## Execution Instructions

1. Process each phase sequentially
2. Use the specified agents for each task
3. Create all files with complete content
4. Test each component before moving to next phase
5. Maintain high code quality throughout
6. Document everything clearly

## Expected Deliverables

1. ✅ All PowerShell scripts (install.ps1, install-commands.ps1, install-all.ps1)
2. ✅ Complete MASTER_PROMPTING_GUIDE.md
3. ✅ MCP integration configuration and templates
4. ✅ Hooks system for testing and quality
5. ✅ Updated documentation (README.md, WINDOWS_INSTALL.md)
6. ✅ New directory structure with all files
7. ✅ Git repository updated and ready for release

## Success Criteria

- Windows users can install with one PowerShell command
- All existing functionality preserved
- Meta-prompting guide enables perfect prompt generation
- MCP tools integrate seamlessly
- Hooks enhance development workflow
- Documentation is comprehensive and clear

Begin with Phase 1 and proceed methodically through all phases.

---