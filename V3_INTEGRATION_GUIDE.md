# Claude Code Dev Stack V3 - Complete Integration Guide

## 🚀 Quick Installation

### Option 1: Direct GitHub Installation (Recommended)
```bash
npm install -g github:KrypticGadget/Claude_Code_Dev_Stack#feature/v3-dev
claude-code-setup
```

### Option 2: Local Installation
```bash
git clone -b feature/v3-dev https://github.com/KrypticGadget/Claude_Code_Dev_Stack.git
cd Claude_Code_Dev_Stack
npm install -g .
claude-code-setup
```

## 🎯 What Gets Installed

### Core Components
- ✅ **28 AI Agents** - Specialized development agents
- ✅ **37 Intelligent Hooks** - Claude Code integration points  
- ✅ **90+ Audio Files** - Rich feedback system
- ✅ **Smart Orchestration** - Context-aware agent selection
- ✅ **Status Line Manager** - Real-time development context
- ✅ **Agent Router** - @mentions processing system

### Available Commands After Installation
```bash
claude-code-setup           # Run initial setup
claude-code-agents list     # List all available agents  
claude-code-hooks list      # List all registered hooks
claude-code-router          # Test agent routing
claude-code-integrate       # Manage hook integration
claude-code-test            # Run integration tests
```

## 💡 Using @mentions for Agent Routing

### Basic Usage
```bash
claude "@agent-master-orchestrator create a new web application"
claude "@agent-business-analyst analyze the market opportunity"  
claude "@agent-technical-cto review this architecture"
```

### Model Selection
```bash
claude "@agent-master-orchestrator[opus] complex enterprise project"
claude "@agent-business-analyst[haiku] quick market analysis"
claude "@agent-technical-cto[sonnet] code review"
```

### Available Agents
- `@agent-master-orchestrator` - Project coordination and workflow management
- `@agent-prompt-engineer` - Prompt optimization and enhancement  
- `@agent-business-analyst` - Market analysis and ROI calculations
- `@agent-technical-cto` - Technical feasibility and architecture
- `@agent-project-manager` - Timeline and resource management
- `@agent-technical-specifications` - Requirements and documentation
- `@agent-business-tech-alignment` - Strategic technology decisions
- `@agent-frontend-architecture` - UI/UX and information architecture
- `@agent-backend-services` - Server-side logic and APIs
- `@agent-database-architecture` - Data modeling and persistence
- `@agent-testing-automation` - Quality assurance and testing
- `@agent-security-architecture` - Security and compliance
- `@agent-devops-engineer` - Infrastructure and deployment
- *...and 15 more specialized agents*

## 🔧 Advanced Configuration

### Hook Management
```bash
# List integrated hooks
claude-code-integrate list

# Validate hook configuration  
claude-code-integrate validate

# Remove specific hook
claude-code-integrate remove hook-name
```

### Status Line Monitoring
```bash
# Show current status
python3 ~/.claude/hooks/status_line_manager.py

# Monitor in real-time
python3 ~/.claude/hooks/status_line_manager.py --monitor

# JSON output
python3 ~/.claude/hooks/status_line_manager.py --json
```

### Smart Orchestration Testing
```bash
# Test orchestration with sample prompt
python3 ~/.claude/hooks/smart_orchestrator.py "create a mobile app"

# Direct agent routing test
node ~/.claude/hooks/agent-router.js "@agent-master-orchestrator help"
```

## 🧪 Testing Your Installation

### Quick Test
```bash
claude-code-test
```

### Specific Component Tests
```bash
claude-code-test testAgentRouter
claude-code-test testSmartOrchestrator  
claude-code-test testStatusLineManager
claude-code-test testCompleteWorkflow
```

### Manual Verification
```bash
# Verify agents are available
claude-code-agents list

# Verify hooks are registered
claude-code-hooks list

# Test @mention parsing
claude "@agent-master-orchestrator test the system"

# Check status line
python3 ~/.claude/hooks/status_line_manager.py
```

## 📊 Status Line Information

The status line provides real-time context about your development environment:

```
[opus] git:main (clean) | exploration | 3 agents | 45.2% tokens | good
```

**Format breakdown:**
- `[opus]` - Current Claude model
- `git:main (clean)` - Git branch and status
- `exploration` - Current development phase
- `3 agents` - Active agents count
- `45.2% tokens` - Token usage percentage
- `good` - Chat health status

## 🎛️ Phase Management

The system automatically detects your development phase:

- **exploration** - Initial planning and research
- **design** - Architecture and design phase  
- **implementation** - Active development
- **testing** - Quality assurance phase
- **debugging** - Issue resolution
- **production** - Deployment and maintenance

### Manual Phase Control
```bash
# Set current phase
echo "implementation" > ~/.claude/current_phase

# Check active agents for phase
claude-code-router --status
```

## 🔄 Workflow Examples

### New Project Creation
```bash
claude "@agent-master-orchestrator I need to create a new e-commerce platform with React frontend and Node.js backend"
```

**Expected flow:**
1. Master Orchestrator coordinates the request
2. Business Analyst evaluates market opportunity
3. Technical CTO assesses architecture
4. Project Manager creates timeline
5. Frontend/Backend agents begin implementation

### Bug Investigation  
```bash
claude "@agent-testing-automation investigate this failing test @agent-security-architecture check for vulnerabilities"
```

**Expected flow:**
1. Testing Automation agent analyzes test failures
2. Security Architecture agent performs security scan
3. Results coordinated through smart orchestration
4. Recommendations provided with priority

### Performance Optimization
```bash
claude "@agent-performance-optimization analyze slow database queries @agent-database-architecture suggest optimizations"
```

## 🛠️ Troubleshooting

### Common Issues

**Hooks not executing:**
```bash
# Re-register hooks
claude-code-integrate

# Validate configuration
claude-code-integrate validate
```

**@mentions not working:**
```bash
# Test agent mention parser
echo '{"prompt":"@agent-test"}' | python3 ~/.claude/hooks/agent_mention_parser.py

# Check agent router
claude-code-router --list-agents
```

**Status line not updating:**
```bash
# Test status manager
python3 ~/.claude/hooks/status_line_manager.py

# Check permissions
ls -la ~/.claude/hooks/
```

### Reinstallation
```bash
# Clean uninstall
npm uninstall -g @claude-code/dev-stack
rm -rf ~/.claude/

# Fresh install
npm install -g github:KrypticGadget/Claude_Code_Dev_Stack#feature/v3-dev
claude-code-setup
```

## 📈 Performance Metrics

The system tracks various performance metrics:

- **Agent Selection Time** - How quickly agents are selected
- **Hook Execution Time** - Performance of hook processing  
- **Context Switch Efficiency** - Status line update performance
- **Token Usage Optimization** - Smart context management

View metrics with:
```bash
claude-code-test testPerformance
```

## 🔐 Security Considerations

- All scripts are sandboxed within the Claude environment
- No external network calls without explicit MCP server configuration
- Agent routing is deterministic and logged for audit
- Sensitive information is filtered from logs automatically

## 🆘 Support

### Debug Mode
```bash
export CLAUDE_CODE_DEBUG=1
claude "@agent-master-orchestrator debug test"
```

### Log Files
- Hook execution: `~/.claude/logs/hooks.log`
- Agent routing: `~/.claude/state/routing_history.jsonl`  
- Status updates: `~/.claude/status_history.db`

### Community
- GitHub Issues: [Report bugs and feature requests](https://github.com/KrypticGadget/Claude_Code_Dev_Stack/issues)
- Discussions: [Community discussions and support](https://github.com/KrypticGadget/Claude_Code_Dev_Stack/discussions)

---

**🎉 You're ready to use Claude Code Dev Stack V3!**

Start with: `claude "@agent-master-orchestrator help me create my first project"`